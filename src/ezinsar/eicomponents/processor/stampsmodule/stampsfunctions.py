#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to process the Time-Series analaysis data with StaMPS processor 

The module allows to process Time-Series analaysis data with StaMPS processor 
from an ``ezinsar.tsprocessing`` job. 
    
    (From `ezinsar` package)

Note: 
        Each function can directly used in Python scripts or/and a Python terminal

Changelog:
        * 1.0.2: Change the import line, Dec. 2025, Alexis Hrysiewicz
        * 1.0.0: Initial version, Feb. 2024

Todo: 
        * Write the part to send an email
        * Optimisation for orbit detection

"""

################################################################################
## Python packages
################################################################################
from datetime import datetime, timedelta
import os
import numpy as np
import glob
import subprocess
from typing import Optional
from zipfile import ZipFile
import random
from mpl_toolkits.basemap import Basemap
from matplotlib import path
import matplotlib.pyplot as plt
from shapely.wkt import loads
from shapely import Polygon
import shutil
import jdcal
from tqdm import tqdm
import scipy
from scipy.interpolate import LinearNDInterpolator
from joblib import Parallel, delayed
import time
import io
import pyproj
import string
import re

from ezinsar import usermessage
from ezinsar import constants
__copyright__ = constants.__copyright__

from ezinsar.eicomponents.processor.stampsmodule import stampstools 
from ezinsar.tools import ezinsardata 

try: 
        import matlab.engine
except: 
        usermessage.warningmsg(__name__,__name__,__file__,'Impossible to import the MATLAB engine. Please see if your installation is correct. This message will not be visible in the log.',None,True)

################################################################################
## Env variable 
################################################################################
use_matlabengine = False # can be [True or False]
"""str: Use of Python MATLAB engine. Can be True or False
"""

para_sleep_sec = 20
"""str: Sleep time in seconds for the parallel steps
"""

os.environ['PATH'] = os.environ['PATH']+':'+constants.__requirement_StaMPS__[0]+':.' 
os.environ['PATH'] = os.environ['PATH']+':'+constants.__requirement_StaMPS__[1]+':.' 
os.environ['STAMPS'] = constants.__requirement_StaMPS__[0].replace('/bin','')
if not 'MATLABPATH' in list(os.environ.keys()): 
        os.environ['MATLABPATH'] = constants.__requirement_StaMPS__[1]
else: 
        os.environ['MATLABPATH'] = os.environ['MATLABPATH'] + ':' + constants.__requirement_StaMPS__[1]

################################################################################
## Sub-functions
################################################################################
def runstampsparallel(pathdir,timedepl,step,log,verbose,nb_cores):
        curdir = os.getcwd()
        os.chdir(pathdir)
        time.sleep(timedepl)

        usermessage.ezprint('\tMove in %s' % (pathdir),log,verbose)
        usermessage.ezprint('\tSleep for %s seconds before to run the job: step %s...' % (para_sleep_sec,step),log,verbose)
        
        runstampsmatlabengine(step,verbose,log,nb_cores)

        os.chdir(curdir)

def runstampsmatlabengine(step,verbose,log,nb_cores):
        out = io.StringIO()
        err = io.StringIO()
        usermessage.ezprint('Start the MATLAB engine for the StaMPS step %s (processing will not be logged, errors will be logged)...' % (step),log,verbose)
        eng = matlab.engine.start_matlab()
        LASTN = eng.maxNumCompThreads(nb_cores)
        errormat = False
        try: 
                eng.stamps(step,step,stderr=err,nargout=0)
        except: 
                errormat = True
        usermessage.ezprint('Stop the MATLAB engine.',log,verbose)
        eng.quit()
        if errormat == True:
                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the StaMPS processing (step: %s): MATLAB engine\n\t%s' % (step,err.getvalue().replace('\n',' ')),log))

################################################################################
## mt_prep FUNCTION
################################################################################
def mt_prep(jobstamps, verbose: Optional[bool] = None):
        """Initiale selection of PS

        The function initialises the selection for PS points, from an ``ezinsar.tsprocessing``.   

        Args:
                jobstamps (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for StaMPS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'stampstsprocessing' in str(type(jobstamps)):
                raise ValueError(usermessage.errormsg(__name__,mt_prep.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-StaMPS processing.',None))
        
        if verbose == None:
                verbose = jobstamps.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,mt_prep.__name__,__file__,__copyright__,
                        'verbose','True or False',jobstamps.log))
        
        usermessage.openingmsg(__name__,mt_prep.__name__,__file__,__copyright__,'StaMPS Step: mt_prep',jobstamps.log,verbose)

        # Check the job 
        jobstamps.check(verbose=False,mode='high')

        # Write the parms file
        jobstamps.writeparameters(verbose=False)

        ## Work directory
        if not os.path.isdir(jobstamps.workdirectory):
                raise ValueError(usermessage.errormsg(__name__,mt_prep.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        os.chdir(jobstamps.workdirectory)
        wk = jobstamps.workdirectory

        # Fix for GAMMA regarding the work directory (1)
        if jobstamps.ifgprocessor == 'gamma':
                wk = wk.replace('/SMALL_BASELINES','')
                
                if not jobstamps.mode == 'sbas':
                        if os.path.isdir('SMALL_BASELINES'): 
                                os.rename('SMALL_BASELINES','__FIX_SMALL_BASELINES_FIX__')
                
        ## Create the command
        if jobstamps.ifgprocessor == 'gamma':
                cmdi = 'mt_prep_gamma'
        elif jobstamps.ifgprocessor =='isce2':
                cmdi = 'mt_prep_isce'
        elif jobstamps.ifgprocessor == 'snap':
                cmdi = 'mt_prep_snap'
        else:
                cmdi = 'mt_prep'    

        if jobstamps.ifgprocessor in ['gamma','snap']:
                cmdi = cmdi + ' %s %s %s %s %s %s %s' % (jobstamps.refdate, 
                        wk, 
                        jobstamps.mt_prep['da_thresh']['value'],
                        jobstamps.mt_prep['rg_patches']['value'],
                        jobstamps.mt_prep['az_patches']['value'],
                        jobstamps.mt_prep['rg_overlap']['value'],
                        jobstamps.mt_prep['az_overlap']['value'])
        else:
                cmdi = cmdi + ' %s %s %s %s %s' % (jobstamps.mt_prep['da_thresh']['value'],
                        jobstamps.mt_prep['rg_patches']['value'],
                        jobstamps.mt_prep['az_patches']['value'],
                        jobstamps.mt_prep['rg_overlap']['value'],
                        jobstamps.mt_prep['az_overlap']['value'])
                
        if (not jobstamps.ifgprocessor in ['doris','isce2']) and (not jobstamps.mt_prep['maskfile']['value'] == None):
                cmdi = cmdi + ' %s' % (jobstamps.mt_prep['maskfile']['value'])
        
        ## Run the command
        stampstools.subprocessrun(cmdi,verbose,jobstamps.log)

        # Fix for GAMMA regarding the work directory (2) 
        if os.path.isdir('__FIX_SMALL_BASELINES_FIX__'):
                os.rename('__FIX_SMALL_BASELINES_FIX__','SMALL_BASELINES')

        # Little fix for ISCE-2 (stupid renaming)
        if jobstamps.ifgprocessor =='isce2':
                if not os.path.isfile('master_day.1.in'):
                        usermessage.warningmsg(__name__,__name__,__file__,'The master_day.1.init file does not exist. It will be created from the reference_day.1.in file',jobstamps.log,True)

                        if os.path.isfile('reference_day.1.in'):
                                shutil.copy('reference_day.1.in','master_day.1.in')
                        else:
                                raise ValueError(usermessage.errormsg(__name__,merging.__name__,__file__,__copyright__,
                                        'Impossible to create the master_day.1.in.',jobstamps.log)) 

                if not os.path.isfile('calamp.out.orig'):
                        shutil.copy('calamp.out','calamp.out.orig')
                fout = open('calamp.out','w')
                with open('calamp.out.orig','r') as fi: 
                        for li in fi:
                                a = li.split()
                                if '/reference/reference.slc' in a[0]:
                                        a[0] = a[0].replace('/reference/','/master/')
                                
                                fout.write('%s %s\n' % (a[0],a[1]))
                fout.close()

                if os.path.isdir('reference') and (not os.path.isdir('master')):
                        try:
                                os.symlink('reference','master',target_is_directory = True)
                        except:
                                os.rename('reference','master')
                
        os.chdir(cur_dir)
        jobstamps.mt_prep['done']['value'] = True

        return jobstamps

################################################################################
## merging FUNCTION
################################################################################
def merging(jobstamps, verbose: Optional[bool] = None):
        """merging

        The function merging, from an ``ezinsar.tsprocessing``.   

        Args:
                jobstamps (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for StaMPS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'stampstsprocessing' in str(type(jobstamps)):
                raise ValueError(usermessage.errormsg(__name__,merging.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-StaMPS processing.',None))
        
        if verbose == None:
                verbose = jobstamps.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,merging.__name__,__file__,__copyright__,
                        'verbose','True or False',jobstamps.log))
        
        usermessage.openingmsg(__name__,merging.__name__,__file__,__copyright__,'StaMPS Step: merging',jobstamps.log,verbose)

        # Check the job 
        jobstamps.check(verbose=False,mode='high')

        # Write the parms file
        jobstamps.writeparameters(verbose=False)

        ## Work directory
        if not os.path.isdir(jobstamps.workdirectory):
                raise ValueError(usermessage.errormsg(__name__,merging.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        
        wk = jobstamps.workdirectory
        wk = wk.replace('/SMALL_BASELINES','')
        os.chdir(wk)                   
                
        ## Run the MATLAB
        if use_matlabengine:
                out = io.StringIO()
                err = io.StringIO()
                usermessage.ezprint('Start the MATLAB engine (processing will not be logged)...',jobstamps.log,verbose)
                eng = matlab.engine.start_matlab()
                LASTN = eng.maxNumCompThreads(jobstamps.communpara['n_cores']['value'])
                errormat = False
                try: 
                        eng.ps_sb_merge(stderr=err,nargout=0)
                except: 
                        errormat = True
                usermessage.ezprint('Stop the MATLAB engine.',jobstamps.log,verbose)
                eng.quit()
                if errormat == True:
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the StaMPS processing: MATLAB engine\n\t%s' % (err.getvalue().replace('\n',' ')),jobstamps.log))
        else:
                stampstools.subprocessrun('matlab -nodisplay -r "ps_sb_merge;quit()"',verbose,jobstamps.log)

        os.chdir(cur_dir)
        jobstamps.merging['done']['value'] = True

        return jobstamps

################################################################################
## load_data FUNCTION
################################################################################
def load_data(jobstamps, verbose: Optional[bool] = None):
        """Load the data

        The function loads the data, from an ``ezinsar.tsprocessing``.   

        Args:
                jobstamps (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for StaMPS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'stampstsprocessing' in str(type(jobstamps)):
                raise ValueError(usermessage.errormsg(__name__,load_data.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-StaMPS processing.',None))
        
        if verbose == None:
                verbose = jobstamps.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,load_data.__name__,__file__,__copyright__,
                        'verbose','True or False',jobstamps.log))
        
        usermessage.openingmsg(__name__,load_data.__name__,__file__,__copyright__,'StaMPS Step: load_data',jobstamps.log,verbose)

        # Check the job 
        jobstamps.check(verbose=False,mode='high')

        # Write the parms file
        jobstamps.writeparameters(verbose=False)

        if jobstamps.mt_prep['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,load_data.__name__,__file__,__copyright__,
                        'The previous step (mt_prep) is not done.',None))

        ## Work directory
        if not os.path.isdir(jobstamps.workdirectory):
                raise ValueError(usermessage.errormsg(__name__,load_data.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        os.chdir(jobstamps.workdirectory)

        ## Run the MATLAB
        if jobstamps.communpara['parallelstep']['value'] == False:
                if use_matlabengine:
                        runstampsmatlabengine(1,verbose,jobstamps.log,jobstamps.communpara['n_cores']['value'])
                else:
                        stampstools.subprocessrun('matlab -nodisplay -r "stamps(1,1);quit()"',verbose,jobstamps.log)
        else:
                patch_dir = glob.glob(jobstamps.workdirectory+os.sep+'PATCH*')
                time_deplayed = np.arange(0,len(patch_dir)) * para_sleep_sec
                step = 1

                usermessage.ezprint('Run StaMPS in parallel',jobstamps.log,verbose)
                Parallel(n_jobs=jobstamps.communpara['n_jobs']['value'])(delayed(runstampsparallel)(pathdir,timedepl,step,jobstamps.log,verbose,jobstamps.communpara['n_cores']['value']) for pathdir, timedepl in zip(patch_dir,time_deplayed))
       
        os.chdir(cur_dir)
        jobstamps.load_data['done']['value'] = True

        return jobstamps

################################################################################
## phase_noise FUNCTION
################################################################################
def phase_noise(jobstamps, verbose: Optional[bool] = None):
        """phase_noise

        The function: phase_noise, from an ``ezinsar.tsprocessing``.   

        Args:
                jobstamps (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for StaMPS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'stampstsprocessing' in str(type(jobstamps)):
                raise ValueError(usermessage.errormsg(__name__,phase_noise.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-StaMPS processing.',None))
        
        if verbose == None:
                verbose = jobstamps.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,phase_noise.__name__,__file__,__copyright__,
                        'verbose','True or False',jobstamps.log))
        
        usermessage.openingmsg(__name__,phase_noise.__name__,__file__,__copyright__,'StaMPS Step: phase_noise',jobstamps.log,verbose)

        # Check the job 
        jobstamps.check(verbose=False,mode='high')

        # Write the parms file
        jobstamps.writeparameters(verbose=False)

        if jobstamps.load_data['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,phase_noise.__name__,__file__,__copyright__,
                        'The previous step (load_data) is not done.',None))

        ## Work directory
        if not os.path.isdir(jobstamps.workdirectory):
                raise ValueError(usermessage.errormsg(__name__,phase_noise.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        os.chdir(jobstamps.workdirectory)

        ## Run the MATLAB
        if jobstamps.communpara['parallelstep']['value'] == False:
                if use_matlabengine:
                        runstampsmatlabengine(2,verbose,jobstamps.log,jobstamps.communpara['n_cores']['value'])
                else:
                        stampstools.subprocessrun('matlab -nodisplay -r "stamps(2,2);quit()"',verbose,jobstamps.log)

        else:
                patch_dir = glob.glob(jobstamps.workdirectory+os.sep+'PATCH*')
                time_deplayed = np.arange(0,len(patch_dir)) * para_sleep_sec
                step = 2

                usermessage.ezprint('Run StaMPS in parallel',jobstamps.log,verbose)
                Parallel(n_jobs=jobstamps.communpara['n_jobs']['value'])(delayed(runstampsparallel)(pathdir,timedepl,step,jobstamps.log,verbose,jobstamps.communpara['n_cores']['value']) for pathdir, timedepl in zip(patch_dir,time_deplayed))
       
        os.chdir(cur_dir)
        jobstamps.phase_noise['done']['value'] = True

        return jobstamps

################################################################################
## ps_selection FUNCTION
################################################################################
def ps_selection(jobstamps, verbose: Optional[bool] = None):
        """ps_selection

        The function: ps_selection, from an ``ezinsar.tsprocessing``.   

        Args:
                jobstamps (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for StaMPS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'stampstsprocessing' in str(type(jobstamps)):
                raise ValueError(usermessage.errormsg(__name__,ps_selection.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-StaMPS processing.',None))
        
        if verbose == None:
                verbose = jobstamps.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ps_selection.__name__,__file__,__copyright__,
                        'verbose','True or False',jobstamps.log))
        
        usermessage.openingmsg(__name__,ps_selection.__name__,__file__,__copyright__,'StaMPS Step: ps_selection',jobstamps.log,verbose)

        # Check the job 
        jobstamps.check(verbose=False,mode='high')

        # Write the parms file
        jobstamps.writeparameters(verbose=False)

        if jobstamps.phase_noise['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,ps_selection.__name__,__file__,__copyright__,
                        'The previous step (phase_noise) is not done.',None))

        ## Work directory
        if not os.path.isdir(jobstamps.workdirectory):
                raise ValueError(usermessage.errormsg(__name__,ps_selection.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        os.chdir(jobstamps.workdirectory)

        ## Run the MATLAB
        if jobstamps.communpara['parallelstep']['value'] == False:
                if use_matlabengine:
                        runstampsmatlabengine(3,verbose,jobstamps.log,jobstamps.communpara['n_cores']['value'])
                else:
                        stampstools.subprocessrun('matlab -nodisplay -r "stamps(3,3);quit()"',verbose,jobstamps.log)

        else:
                patch_dir = glob.glob(jobstamps.workdirectory+os.sep+'PATCH*')
                time_deplayed = np.arange(0,len(patch_dir)) * para_sleep_sec
                step = 3

                usermessage.ezprint('Run StaMPS in parallel',jobstamps.log,verbose)
                Parallel(n_jobs=jobstamps.communpara['n_jobs']['value'])(delayed(runstampsparallel)(pathdir,timedepl,step,jobstamps.log,verbose,jobstamps.communpara['n_cores']['value']) for pathdir, timedepl in zip(patch_dir,time_deplayed))
       
        os.chdir(cur_dir)
        jobstamps.ps_selection['done']['value'] = True

        return jobstamps

################################################################################
## ps_weeding FUNCTION
################################################################################
def ps_weeding(jobstamps, verbose: Optional[bool] = None):
        """ps_weeding

        The function: ps_weeding, from an ``ezinsar.tsprocessing``.   

        Args:
                jobstamps (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for StaMPS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'stampstsprocessing' in str(type(jobstamps)):
                raise ValueError(usermessage.errormsg(__name__,ps_weeding.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-StaMPS processing.',None))
        
        if verbose == None:
                verbose = jobstamps.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ps_weeding.__name__,__file__,__copyright__,
                        'verbose','True or False',jobstamps.log))
        
        usermessage.openingmsg(__name__,ps_weeding.__name__,__file__,__copyright__,'StaMPS Step: ps_weeding',jobstamps.log,verbose)

        # Check the job 
        jobstamps.check(verbose=False,mode='high')

        # Write the parms file
        jobstamps.writeparameters(verbose=False)

        if jobstamps.ps_selection['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,ps_weeding.__name__,__file__,__copyright__,
                        'The previous step (ps_selection) is not done.',None))

        ## Work directory
        if not os.path.isdir(jobstamps.workdirectory):
                raise ValueError(usermessage.errormsg(__name__,ps_weeding.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        os.chdir(jobstamps.workdirectory)

        ## Run the MATLAB
        if jobstamps.communpara['parallelstep']['value'] == False:
                if use_matlabengine:
                        runstampsmatlabengine(4,verbose,jobstamps.log,jobstamps.communpara['n_cores']['value'])
                else:
                        stampstools.subprocessrun('matlab -nodisplay -r "stamps(4,4);quit()"',verbose,jobstamps.log)

        else:
                patch_dir = glob.glob(jobstamps.workdirectory+os.sep+'PATCH*')
                time_deplayed = np.arange(0,len(patch_dir)) * para_sleep_sec
                step = 4

                usermessage.ezprint('Run StaMPS in parallel',jobstamps.log,verbose)
                Parallel(n_jobs=jobstamps.communpara['n_jobs']['value'])(delayed(runstampsparallel)(pathdir,timedepl,step,jobstamps.log,verbose,jobstamps.communpara['n_cores']['value']) for pathdir, timedepl in zip(patch_dir,time_deplayed))
       
        os.chdir(cur_dir)
        jobstamps.ps_weeding['done']['value'] = True

        return jobstamps

################################################################################
## phase_correction FUNCTION
################################################################################
def phase_correction(jobstamps, verbose: Optional[bool] = None):
        """phase_correction

        The function: phase_correction, from an ``ezinsar.tsprocessing``.   

        Args:
                jobstamps (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for StaMPS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'stampstsprocessing' in str(type(jobstamps)):
                raise ValueError(usermessage.errormsg(__name__,phase_correction.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-StaMPS processing.',None))
        
        if verbose == None:
                verbose = jobstamps.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,phase_correction.__name__,__file__,__copyright__,
                        'verbose','True or False',jobstamps.log))
        
        usermessage.openingmsg(__name__,phase_correction.__name__,__file__,__copyright__,'StaMPS Step: phase_correction',jobstamps.log,verbose)

        # Check the job 
        jobstamps.check(verbose=False,mode='high')

        # Write the parms file
        jobstamps.writeparameters(verbose=False)

        if jobstamps.ps_weeding['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,phase_correction.__name__,__file__,__copyright__,
                        'The previous step (ps_weeding) is not done.',None))

        ## Work directory
        if not os.path.isdir(jobstamps.workdirectory):
                raise ValueError(usermessage.errormsg(__name__,phase_correction.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        os.chdir(jobstamps.workdirectory)

        ## Run the MATLAB
        if use_matlabengine:
                runstampsmatlabengine(5,verbose,jobstamps.log,jobstamps.communpara['n_cores']['value'])
        else:
                stampstools.subprocessrun('matlab -nodisplay -r "stamps(5,5);quit()"',verbose,jobstamps.log)

       
        os.chdir(cur_dir)
        jobstamps.phase_correction['done']['value'] = True

        return jobstamps

################################################################################
## phase_unwrapping FUNCTION
################################################################################
def phase_unwrapping(jobstamps, verbose: Optional[bool] = None):
        """phase_unwrapping

        The function: phase_unwrapping, from an ``ezinsar.tsprocessing``.   

        Args:
                jobstamps (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for StaMPS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'stampstsprocessing' in str(type(jobstamps)):
                raise ValueError(usermessage.errormsg(__name__,phase_unwrapping.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-StaMPS processing.',None))
        
        if verbose == None:
                verbose = jobstamps.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,phase_unwrapping.__name__,__file__,__copyright__,
                        'verbose','True or False',jobstamps.log))
        
        usermessage.openingmsg(__name__,phase_unwrapping.__name__,__file__,__copyright__,'StaMPS Step: phase_unwrapping',jobstamps.log,verbose)

        # Check the job 
        jobstamps.check(verbose=False,mode='high')

        # Write the parms file
        jobstamps.writeparameters(verbose=False)

        if jobstamps.phase_correction['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,phase_unwrapping.__name__,__file__,__copyright__,
                        'The previous step (phase_correction) is not done.',None))

        ## Work directory
        if not os.path.isdir(jobstamps.workdirectory):
                raise ValueError(usermessage.errormsg(__name__,phase_unwrapping.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        os.chdir(jobstamps.workdirectory)

        ## Run the MATLAB
        if use_matlabengine:
                runstampsmatlabengine(6,verbose,jobstamps.log,jobstamps.communpara['n_cores']['value'])
        else:
                stampstools.subprocessrun('matlab -nodisplay -r "stamps(6,6);quit()"',verbose,jobstamps.log)
       
        os.chdir(cur_dir)
        jobstamps.phase_unwrapping['done']['value'] = True

        return jobstamps

################################################################################
## corr_lkerror FUNCTION
################################################################################
def corr_lkerror(jobstamps, verbose: Optional[bool] = None):
        """corr_lkerror

        The function: corr_lkerror, from an ``ezinsar.tsprocessing``.   

        Args:
                jobstamps (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for StaMPS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'stampstsprocessing' in str(type(jobstamps)):
                raise ValueError(usermessage.errormsg(__name__,corr_lkerror.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-StaMPS processing.',None))
        
        if verbose == None:
                verbose = jobstamps.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,corr_lkerror.__name__,__file__,__copyright__,
                        'verbose','True or False',jobstamps.log))
        
        usermessage.openingmsg(__name__,corr_lkerror.__name__,__file__,__copyright__,'StaMPS Step: corr_lkerror',jobstamps.log,verbose)

        # Check the job 
        jobstamps.check(verbose=False,mode='high')

        # Write the parms file
        jobstamps.writeparameters(verbose=False)

        if jobstamps.phase_unwrapping['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,corr_lkerror.__name__,__file__,__copyright__,
                        'The previous step (phase_unwrapping) is not done.',None))

        ## Work directory
        if not os.path.isdir(jobstamps.workdirectory):
                raise ValueError(usermessage.errormsg(__name__,corr_lkerror.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        os.chdir(jobstamps.workdirectory)

        ## Run the MATLAB
        if use_matlabengine:
                runstampsmatlabengine(7,verbose,jobstamps.log,jobstamps.communpara['n_cores']['value'])
        else:
                stampstools.subprocessrun('matlab -nodisplay -r "stamps(7,7);quit()"', verbose,jobstamps.log)

        os.chdir(cur_dir)
        jobstamps.corr_lkerror['done']['value'] = True

        return jobstamps

################################################################################
## corr_noise FUNCTION
################################################################################
def corr_noise(jobstamps, verbose: Optional[bool] = None):
        """corr_noise

        The function: corr_noise, from an ``ezinsar.tsprocessing``.   

        Args:
                jobstamps (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for StaMPS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'stampstsprocessing' in str(type(jobstamps)):
                raise ValueError(usermessage.errormsg(__name__,corr_noise.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-StaMPS processing.',None))
        
        if verbose == None:
                verbose = jobstamps.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,corr_noise.__name__,__file__,__copyright__,
                        'verbose','True or False',jobstamps.log))
        
        usermessage.openingmsg(__name__,corr_noise.__name__,__file__,__copyright__,'StaMPS Step: corr_noise',jobstamps.log,verbose)

        # Check the job 
        jobstamps.check(verbose=False,mode='high')

        # Write the parms file
        jobstamps.writeparameters(verbose=False)

        if jobstamps.corr_lkerror['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,corr_noise.__name__,__file__,__copyright__,
                        'The previous step (corr_lkerror) is not done.',None))

        ## Work directory
        if not os.path.isdir(jobstamps.workdirectory):
                raise ValueError(usermessage.errormsg(__name__,corr_noise.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        os.chdir(jobstamps.workdirectory)

        ## Run the MATLAB
        if use_matlabengine:
                runstampsmatlabengine(8,verbose,jobstamps.log,jobstamps.communpara['n_cores']['value'])
        else:
                stampstools.subprocessrun('matlab -nodisplay -r "stamps(8,8);quit()"', verbose,jobstamps.log)

        os.chdir(cur_dir)
        jobstamps.corr_noise['done']['value'] = True

        return jobstamps

################################################################################
## extract_res FUNCTION
################################################################################
def extract_res(jobstamps, verbose: Optional[bool] = None):
        """extract_res

        The function: extract_res, from an ``ezinsar.tsprocessing``.   

        Args:
                jobstamps (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for StaMPS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'stampstsprocessing' in str(type(jobstamps)):
                raise ValueError(usermessage.errormsg(__name__,extract_res.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-StaMPS processing.',None))
        
        if verbose == None:
                verbose = jobstamps.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,extract_res.__name__,__file__,__copyright__,
                        'verbose','True or False',jobstamps.log))
        
        usermessage.openingmsg(__name__,extract_res.__name__,__file__,__copyright__,'StaMPS Step: extract_res',jobstamps.log,verbose)

        # Check the job 
        jobstamps.check(verbose=False,mode='high')

        # Write the parms file 
        jobstamps.writeparameters(verbose=False)

        if jobstamps.corr_noise['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,extract_res.__name__,__file__,__copyright__,
                        'The previous step (corr_noise) is not done.',None))

        ## Work directory
        if not os.path.isdir(jobstamps.workdirectory):
                raise ValueError(usermessage.errormsg(__name__,extract_res.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        os.chdir(jobstamps.workdirectory)

        ## Extraction of displacements
        data = importstampsresults(jobstamps.workdirectory, 
                correction = jobstamps.extract_res['correction']['value'],
                job = jobstamps,
                use_matlabengine = use_matlabengine, 
                verbose = verbose,
                log = jobstamps.log)

        name = 'TS_LOS_%s_%s_%s_%s_%s_%s_%s' % (jobstamps.satellite,
                                                jobstamps.satmode,
                                                jobstamps.relorbit,
                                                jobstamps.satpass,
                                                jobstamps.ifgprocessor,
                                                jobstamps.processor,
                                                jobstamps.mode.replace('/',''))

        if jobstamps.extract_res['ecraseprevious']['value'] == True: 
                usermessage.warningmsg(__name__,__name__,__file__,'The previous file will be replaced.',jobstamps.log,verbose)
                name = name + '.eidata'
        else: 
                name = '%s_%s.eidata' % (name,len(glob.glob(name+'*')))

        ezinsardata.saveEZdata(data,name,verbose = verbose,log = jobstamps.log)

        os.chdir(cur_dir)
        jobstamps.extract_res['done']['value'] = True

        return jobstamps

################################################################################
## Extraction of displacements for StaMPS FUNCTION
################################################################################
def importstampsresults(workdirectory, 
        mode: Optional[str] = None,
        correction: Optional[str] = 'd',
        job: Optional = None, 
        meter_mode = 'UTM',
        use_matlabengine: Optional[bool] = True,
        verbose: Optional[bool] = True,
        log: Optional[bool] = None):
        """importstampsresults

        The function will import the StaMPS results into a format for EZ-InSAR.
        
        """
        cur_dir = os.getcwd()

        if not 'stampstsprocessing' in str(type(job)):
                raise ValueError(usermessage.errormsg(__name__,importstampsresults.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-StaMPS processing.',None))

        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,importstampsresults.__name__,__file__,__copyright__,
                        'verbose','True or False',log))

        if not correction == None: 
                if not isinstance(correction,str): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,importstampsresults.__name__,__file__,__copyright__,
                                'correction','str',log))
        
        if not log == None: 
                if not isinstance(log,str): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,importstampsresults.__name__,__file__,__copyright__,
                                'log','str',log))

        if not os.path.isdir(workdirectory):
                raise ValueError(usermessage.errormsg(__name__,extract_res.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        
        usermessage.openingmsg(__name__,importstampsresults.__name__,__file__,__copyright__,'Import the StaMPS results',log,verbose)

        os.chdir(workdirectory)

        ## Initialisation of the dataset
        usermessage.ezprint('Initialisation of the dataset...',log,verbose)
        data = ezinsardata.displacement()
        usermessage.ezprint('\tdone',log,verbose)

        ## Detection of the dataset mode
        usermessage.ezprint('Detection of the dataset mode...',log,verbose)
        if (not '/SMALL_BASELINES' in workdirectory) and (not '/MERGED' in workdirectory): 
                mode = 'PS'
        elif '/SMALL_BASELINES' in workdirectory: 
                mode = 'SBAS'
        else: 
                mode = 'PS/SBAS'
        usermessage.ezprint('\tThe mode is %s.' % (mode),log,verbose)
        usermessage.ezprint('\tdone',log,verbose)

        ## For the metadata
        usermessage.ezprint('Extract the metadata...',log,verbose)
        
        data.mode['value'] = 'LOS'
        
        if not job == None: 
                data.datainformation['Name'] = None
                data.datainformation['Target'] = job.title
                data.datainformation['InSAR_Processor'] = job.ifgprocessor
                data.datainformation['Satellite'] = job.satellite
                data.datainformation['Mode'] = job.satmode
                data.datainformation['Pass'] = job.relorbit
                data.datainformation['Track'] = job.satpass

                if job.satellite == 'S1': 
                        data.datainformation['Wavelength'] = 0.055
                elif job.satellite in ['TSX','PAZ','CSK']: 
                        data.datainformation['Wavelength'] = 0.031

        data.datainformation['TS_Processor'] = 'stamps'
        data.datainformation['Approach'] = mode
        data.datainformation['Date'] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        data.datainformation['Importation'] = 'regular'
        data.datainformation['Processing'] = 'raw'

        if not job == None:
                import ezinsar.job as ez
                tmpfile = constants.__cachedir__+os.sep+'jobtmp_'+''.join(random.choice(string.ascii_lowercase) for i in range(16))+'.ei'
                ez.save(job,tmpfile,verbose=False)

                with open(tmpfile,'r') as fi: 
                        content = fi.readlines()

                if os.path.isfile(tmpfile): 
                        os.remove(tmpfile)

                data.datainformation['Metadata_processing'] = content

        data.datainformation['Path'] = workdirectory

        usermessage.ezprint('\tdone',log,verbose)

        ## For the temporal data
        usermessage.ezprint('Extract the temporal information...',log,verbose)

        tmp = scipy.io.loadmat('ps2.mat',variable_names='day')
        data.dates['value'] = []
        for di in tmp['day']: 
                a = float(di[0])
                data.dates['value'].append(datetime.fromordinal(int(a)) + timedelta(days=a%1) - timedelta(days = 366))
        data.dates['value'] = np.array(data.dates['value'])

        tmp = scipy.io.loadmat('ps2.mat',variable_names='n_image')
        data.n_image['value'] = int(tmp['n_image'][0][0])

        tmp = scipy.io.loadmat('ps2.mat',variable_names='n_ifg')
        data.n_ifg['value'] = int(tmp['n_ifg'][0][0])

        tmp = scipy.io.loadmat('ps2.mat',variable_names='master_day')
        a = float(tmp['master_day'][0][0])
        data.date_ref['value'] = datetime.fromordinal(int(a)) + timedelta(days=a%1) - timedelta(days = 366)

        # if not mode == 'PS': 
                # tmp = scipy.io.loadmat('ps2.mat',variable_names='ifgday')
        # else: 
        tmp = None 

        if not tmp == None: 
                a = tmp['ifgday'][:,0]
                # a = datetime.fromordinal(int(a)) + timedelta(days=a%1) - timedelta(days = 366)
                # nposmaster = np.where(np.array(data.dates['value']) == data.date_ref['value'])[0][0]
        else: 
                tmp = [np.nan]
        data.ifg_date['value'] = np.array(tmp)

        usermessage.ezprint('\tdone',log,verbose)

        ## For the spatial data
        usermessage.ezprint('Extract the spatial information...',log,verbose)

        tmp = scipy.io.loadmat('ps2.mat',variable_names='lonlat')
        data.lon['value'] = tmp['lonlat'][:,0]
        data.lat['value'] = tmp['lonlat'][:,1]

        tmp = scipy.io.loadmat('ps2.mat',variable_names='ij')
        data.index_pts['value'] = None 

        if meter_mode == 'UTM': 
                utm_crs_list = pyproj.database.query_utm_crs_info(
                        datum_name="WGS 84",
                        area_of_interest=pyproj.aoi.AreaOfInterest(
                                west_lon_degree=np.min(data.lon['value']),
                                south_lat_degree=np.min(data.lat['value']),
                                east_lon_degree=np.max(data.lon['value']),
                                north_lat_degree=np.min(data.lat['value']),
                                ),
                        )
                meter_mode = utm_crs_list[0].code

        latlon_to_meter = pyproj.Transformer.from_crs('epsg:4326','epsg:%s' % (meter_mode))
        data.x_utm['value'], data.y_utm['value'] = latlon_to_meter.transform(data.lat['value'],data.lon['value'])
        data.code_meter['value'] = 'epsg:%s' % (meter_mode)

        usermessage.ezprint('\tdone',log,verbose)

        ## For the ground data
        usermessage.ezprint('Extract the ground information...',log,verbose)

        if os.path.isfile('amp_mean.mat'): 
                pathtmp = 'amp_mean.mat'
        elif os.path.isfile('..'+os.sep+'amp_mean.mat'): 
                pathtmp = '..'+os.sep+'amp_mean.mat'
        else:
                pathtmp = None
        
        if not pathtmp == None:
                tmp = scipy.io.loadmat(pathtmp,variable_names='amp_mean')

        tmp = scipy.io.loadmat('hgt2.mat',variable_names='hgt')
        data.hgt['value'] = tmp['hgt'].flatten()

        # For the elevation grid, incident angle and heading
        with open('len.txt','r') as fi:
                n_rows = int(fi.readlines()[0])
        with open('width.txt','r') as fi:
                n_cols = int(fi.readlines()[0])

        if os.path.isfile('dem.raw'):
                pathtmp = 'dem.raw'
        elif os.path.isfile('..'+os.sep+'dem.raw'):
                pathtmp = 'dem.raw'
        else:
                pathtmp = None 
        if not pathtmp == None: 
                with open(pathtmp,"rb") as fi:
                        tmp = np.reshape(np.fromfile(fi, np.float32),(n_rows,n_cols))
                data.hgt_grid['value'] = tmp

        if os.path.isfile('heading.raw'):
                pathtmp = 'heading.raw'
        elif os.path.isfile('..'+os.sep+'heading.raw'):
                pathtmp = 'heading.raw'
        else:
                pathtmp = None 
        if not pathtmp == None: 
                with open(pathtmp,"rb") as fi:
                        tmp = np.reshape(np.fromfile(fi, np.float32),(n_rows,n_cols))
                data.heading['value'] = tmp

        if os.path.isfile('inc_angle.raw'):
                pathtmp = 'inc_angle.raw'
        elif os.path.isfile('..'+os.sep+'heading.raw'):
                pathtmp = 'inc_angle.raw'
        else:
                pathtmp = None 
        if not pathtmp == None: 
                with open(pathtmp,"rb") as fi:
                        tmp = np.reshape(np.fromfile(fi, np.float32),(n_rows,n_cols))
                data.inc_angle['value'] = tmp

        usermessage.ezprint('\tdone',log,verbose)

        ## For the spatial data
        usermessage.ezprint('Extract the displacement data...',log,verbose)

        if correction == None: 
                namevel = 'v' 
                namevels = 'vs'
        else: 
                namevel = 'v-%s' % (correction)
                namevels = 'vs-%s' % (correction)

        if not mode == 'PS':
                namevel = namevel.replace('v','V')
                namevels = namevels.replace('v','V')

        if use_matlabengine:
                out = io.StringIO()
                err = io.StringIO()
                usermessage.ezprint('\tStart the MATLAB engine for displacement extraction (processing will not be logged)...',log,verbose)
                eng = matlab.engine.start_matlab()
                errormat = False
                try: 
                        eng.ps_plot(namevel,-1,stderr=err,nargout=0)
                        # eng.ps_plot(namevels,-1,stderr=err,nargout=0)
                        eng.ps_plot(namevel,'ts',stderr=err,nargout=0)
                        # eng.delete(gcf,stderr=err,nargout=0)
                except: 
                        errormat = True
                usermessage.ezprint('\tStop the MATLAB engine.',log,verbose)
                eng.quit()
                if errormat == True:
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the StaMPS processing: MATLAB engine\n\t%s' % (err.getvalue().replace('\n',' ')),log))
        else:
                stampstools.subprocessrun('matlab -nodisplay -r "ps_plot(%s,-1);ps_plot(%s,-1);ps_plot(%s,''ts'');delete(gcf);quit()"' % (namesvel,namevels),verbose,log)

        tmp1 = scipy.io.loadmat('ps_plot_%s.mat' % (namevel))
        # tmp2 = scipy.io.loadmat('ps_plot_%s.mat' % (namevels))
        data.rateLOS['value'] = tmp1['ph_disp'].flatten()
        data.sigmarateLOS['value'] = np.array([0])#tmp2['ph_disp'].flatten()

        tmp = scipy.io.loadmat('ps_plot_ts_%s.mat' % (namevel),variable_names=['ph_mm','ref_ps'])

        # Add the master displ
        usermessage.warningmsg(__name__,__name__,__file__,'For StaMPS, the master displacement will be added (linear interpolation considering homogenous temporal sampling)',log,verbose)
        nposmaster = np.where(np.array(data.dates['value']) == data.date_ref['value'])[0][0]
        # data.dispLOS['value'] = np.insert(tmp['ph_mm'],nposmaster,np.zeros(tmp['ph_mm'].shape[0]),1)
        if nposmaster in [0,tmp['ph_mm'].shape[1]]: 
                data.dispLOS['value'] = np.insert(tmp['ph_mm'],nposmaster,np.zeros(tmp['ph_mm'].shape[0]),1)
        else: 
                data.dispLOS['value'] = np.insert(tmp['ph_mm'],nposmaster,tmp['ph_mm'][:,nposmaster-1]+(tmp['ph_mm'][:,nposmaster]-tmp['ph_mm'][:,nposmaster-1])/2,1)             

        data.sigmadispLOS['value'] = None

        usermessage.ezprint('\tdone',log,verbose)

        ## For the reference point
        usermessage.ezprint('Extract the reference-point information...',log,verbose)

        data.referencepoint['value']['index'] = tmp['ref_ps'].flatten()

        tmp = scipy.io.loadmat('parms.mat')
        data.referencepoint['value']['lon_pt_ref'] = tmp['ref_centre_lonlat'].flatten()[0]
        data.referencepoint['value']['lat_pt_ref'] = tmp['ref_centre_lonlat'].flatten()[1]
        data.referencepoint['value']['lon_pt_refarea'] = tmp['ref_lon'].flatten()
        data.referencepoint['value']['lat_pt_refarea'] = tmp['ref_lat'].flatten()
        data.referencepoint['value']['radius'] = tmp['ref_radius'].flatten()[0]
        data.referencepoint['value']['rateLOS'] = tmp['ref_velocity'].flatten()[0]

        usermessage.ezprint('\tdone',log,verbose)

        ## For the reference point
        usermessage.ezprint('Extract the perpendicular baselines...',log,verbose)

        if mode == 'PS':
                data.bperp['value'] = scipy.io.loadmat('ps2.mat',variable_names='bperp')['bperp'].flatten()
        else:
                data.bperp['value'] = scipy.io.loadmat('..'+os.sep+'ps2.mat',variable_names='bperp')['bperp'].flatten()

        os.chdir(cur_dir)

        return data