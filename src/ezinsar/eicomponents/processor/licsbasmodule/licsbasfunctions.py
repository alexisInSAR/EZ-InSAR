#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to process the Time-Series analaysis data with LiCSBAS processor 

The module allows to process Time-Series analaysis data with LiCSBAS processor 
from an ``ezinsar.tsprocessing`` job. 
    
    (From `ezinsar` package)

Note: 
        Each function can directly used in Python scripts or/and a Python terminal

Changelog:
        * 1.0.1: Change the import line, Dec. 2025, Alexis Hrysiewicz
        * 1.0.0: Initial version, Feb. 2024

Todo: 
        * Write the part to send an email
        * Optimisation for orbit detection

"""

################################################################################
## Python packages
################################################################################
from datetime import datetime
import os
import numpy as np
import glob
import h5py
import string
import random
from shapely.wkt import loads
import pyproj

from typing import Optional
from ezinsar import usermessage
from ezinsar import constants
from ezinsar.eicomponents.processor.licsbasmodule import licsbastools 
from ezinsar.tools import ezinsardata 

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Env variable 
################################################################################
os.environ['PATH'] = os.environ['PATH']+':'+constants.__requirement_LiCSBAS__+':.' 
os.environ['PYTHONPATH'] = os.environ['PYTHONPATH']+':'+constants.__requirement_LiCSBAS__+':.' 

# usermessage.warningmsg(__name__,__name__,__file__,'LiCSBAS implementation is experimental.',None,True)

################################################################################
## get_geotiff FUNCTION
################################################################################
def get_geotiff(jobts, verbose: Optional[bool] = None, log: Optional[bool] = None):
        """Downlaod the data from the LiCSAR server

        The function will download the data from the LiCSAR server, for an ``ezinsar.tsprocessing``.   

        Args:
                jobts (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for LiCSBAS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'licsbastsprocessing' in str(type(jobts)):
                raise ValueError(usermessage.errormsg(__name__,get_geotiff.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-LiCSBAS processing.',None))
        
        if verbose == None:
                verbose = jobts.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,get_geotiff.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if log == None:
                log = jobts.log
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,get_geotiff.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        usermessage.openingmsg(__name__,get_geotiff.__name__,__file__,__copyright__,'LiCSBAS Step: get_geotiff',log,verbose)

        # Check the job 
        jobts.check(verbose=False,mode='high')

        ## Work directory
        if not os.path.isdir(jobts.workdirectory):
                os.mkdir(jobts.workdirectory)
        os.chdir(jobts.workdirectory)

        ## Create the function 
        cmd = 'LiCSBAS01_get_geotiff.py -f %s -s %s -e %s ' % (jobts.frame,jobts.date1,jobts.date2)
        if jobts.get_geotiff['get_gacos']['value'] == True: 
                cmd = cmd + ' --get_gacos'
        if jobts.get_geotiff['get_mli']['value'] == True: 
                cmd = cmd + ' --get_mli'
        if jobts.get_geotiff['get_pha']['value'] == True: 
                cmd = cmd + ' --get_pha'
        cmd = cmd + ' --n_para %s' % (jobts.get_geotiff['n_para']['value'])

        licsbastools.subprocessrun(cmd,verbose,log)

        os.chdir(cur_dir)
        jobts.get_geotiff['done']['value'] = True

        return jobts

################################################################################
## prep_ifg FUNCTION
################################################################################
def prep_ifg(jobts, verbose: Optional[bool] = None, log: Optional[bool] = None):
        """Prepare the interferograms with several options 

        The function will prepare the interferograms with several options , for an ``ezinsar.tsprocessing``.   

        Args:
                jobts (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for LiCSBAS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'licsbastsprocessing' in str(type(jobts)):
                raise ValueError(usermessage.errormsg(__name__,prep_ifg.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-LiCSBAS processing.',None))
        
        if verbose == None:
                verbose = jobts.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,prep_ifg.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if log == None:
                log = jobts.log
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,prep_ifg.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        usermessage.openingmsg(__name__,prep_ifg.__name__,__file__,__copyright__,'LiCSBAS Step: prep_ifg',log,verbose)

        if jobts.get_geotiff['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,prep_ifg.__name__,__file__,__copyright__,
                        'The previous step (get_geotiff) is not done.',None))

        # Check the job 
        jobts.check(verbose=False,mode='high')

        ## Work directory
        if not os.path.isdir(jobts.workdirectory):
                os.mkdir(jobts.workdirectory)
        os.chdir(jobts.workdirectory)

        ## Create the function 
        if jobts.prep_ifg['reunwrap']['value']:
                cmd = 'LiCSBAS02to05_unwrap.py -i %s -M %s' % (os.path.abspath(jobts.workdirectory),
                                                                jobts.prep_ifg['nb_look']['value'])
                
                if jobts.prep_ifg['clipping']['value']: 
                        lon,lat = loads(jobts.roi).exterior.xy
                        cmd = cmd + ' -g %s/%s/%s/%s' % (np.min(lon),np.max(lon),np.min(lat),np.max(lat))

                if not jobts.prep_ifg['filter']['value'] == 'none': 
                        cmd = cmd + ' --filter %s' % (jobts.prep_ifg['filter']['value'])

                if jobts.prep_ifg['gacos']['value']: 
                        cmd = cmd + ' --gacos'

                if jobts.prep_ifg['height_corr']['value']: 
                        cmd = cmd + ' --hgtcorr'

                if not jobts.prep_ifg['cascade']['value'] == 'none': 
                        cmd = cmd + ' --%s' % (jobts.prep_ifg['cascade']['value'])

                cmd = cmd + ' --thres %s' % (jobts.prep_ifg['thres']['value'])

                cmd = cmd + ' --n_para %s' % (jobts.n_para)

                if jobts.prep_ifg['landmask']['value'] == False: 
                        cmd = cmd + ' --nolandmask'

                licsbastools.subprocessrun(cmd,verbose,log)

        else: 
                cmd = 'LiCSBAS02_ml_prep.py -i %s -o %s -n %s --n_para %s' % (os.path.abspath(jobts.workdirectory)+os.sep+'GEOC',
                                os.path.abspath(jobts.workdirectory)+os.sep+'GEOCml'+str(jobts.prep_ifg['nb_look']['value']), 
                                jobts.prep_ifg['nb_look']['value'],
                                jobts.n_para)
                licsbastools.subprocessrun(cmd,verbose,log)

                inputdir = os.path.abspath(jobts.workdirectory)+os.sep+'GEOCml'+str(jobts.prep_ifg['nb_look']['value'])

                if jobts.prep_ifg['gacos']['value']: 
                        cmd = 'LiCSBAS03op_GACOS.py -i %s -o %s -g %s -n %s --n_para %s' % (inputdir,
                                inputdir+'GACOS',
                                os.path.abspath(jobts.workdirectory), 
                                jobts.prep_ifg['nb_look']['value'],
                                jobts.n_para)
                        
                        if jobts.prep_ifg['fillholegacos']['value']: 
                                cmd = cmd + ' --fillhole'
                        
                        inputdir = inputdir+'GACOS'
                        licsbastools.subprocessrun(cmd,verbose,log)
                        
                cmd = 'LiCSBAS04op_mask_unw.py -i %s -o %s -c %s -s %s --n_para %s' % (inputdir,
                                inputdir+'masked', 
                                jobts.prep_ifg['thres']['value'],
                                jobts.prep_ifg['thres']['value'],
                                jobts.n_para)
                
                inputdir = inputdir+'masked'
                licsbastools.subprocessrun(cmd,verbose,log)

                if jobts.prep_ifg['clipping']['value']: 
                        lon,lat = loads(jobts.roi).exterior.xy
                        cmd = 'LiCSBAS05op_clip_unw.py -i %s -o %s  -g %s/%s/%s/%s --n_para %s' % (inputdir,
                                        inputdir+'clip', 
                                        np.min(lon),np.max(lon),np.min(lat),np.max(lat),
                                        jobts.n_para)
                
                        inputdir = inputdir+'clip'
                        licsbastools.subprocessrun(cmd,verbose,log)
                
        os.chdir(cur_dir)
        jobts.prep_ifg['done']['value'] = True

        return jobts

################################################################################
## check_unw FUNCTION
################################################################################
def check_unw(jobts, verbose: Optional[bool] = None, log: Optional[bool] = None):
        """Check the unwrapped interferograms with several options 

        The function will check the unwrapped interferograms with several options , for an ``ezinsar.tsprocessing``.   

        Args:
                jobts (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for LiCSBAS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'licsbastsprocessing' in str(type(jobts)):
                raise ValueError(usermessage.errormsg(__name__,check_unw.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-LiCSBAS processing.',None))
        
        if verbose == None:
                verbose = jobts.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check_unw.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if log == None:
                log = jobts.log
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check_unw.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        usermessage.openingmsg(__name__,check_unw.__name__,__file__,__copyright__,'LiCSBAS Step: check_unw',log,verbose)

        if jobts.prep_ifg['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,check_unw.__name__,__file__,__copyright__,
                        'The previous step (prep_ifg) is not done.',None))

        # Check the job 
        jobts.check(verbose=False,mode='high')

        ## Work directory
        if not os.path.isdir(jobts.workdirectory):
                os.mkdir(jobts.workdirectory)
        os.chdir(jobts.workdirectory)

        ## Create the function 
        input_dir = np.sort(glob.glob(os.path.abspath(jobts.workdirectory)+os.sep+'GEOCml*'))[-1]

        cmd = 'LiCSBAS11_check_unw.py -d %s -c %s -u %s' % (input_dir,
                                                        jobts.check_unw['coherence_thres']['value'],
                                                        jobts.check_unw['unw_thres']['value'])
        licsbastools.subprocessrun(cmd,verbose,log)

        os.chdir(cur_dir)
        jobts.check_unw['done']['value'] = True

        return jobts

################################################################################
## loop_closure FUNCTION
################################################################################
def loop_closure(jobts, verbose: Optional[bool] = None, log: Optional[bool] = None):
        """Compute the loop closure 

        The function will compute the loop closure with several options , for an ``ezinsar.tsprocessing``.   

        Args:
                jobts (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for LiCSBAS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'licsbastsprocessing' in str(type(jobts)):
                raise ValueError(usermessage.errormsg(__name__,loop_closure.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-LiCSBAS processing.',None))
        
        if verbose == None:
                verbose = jobts.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,loop_closure.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if log == None:
                log = jobts.log
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,loop_closure.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        usermessage.openingmsg(__name__,loop_closure.__name__,__file__,__copyright__,'LiCSBAS Step: loop_closure',log,verbose)

        if jobts.check_unw['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,loop_closure.__name__,__file__,__copyright__,
                        'The previous step (check_unw) is not done.',None))

        # Check the job 
        jobts.check(verbose=False,mode='high')

        ## Work directory
        if not os.path.isdir(jobts.workdirectory):
                os.mkdir(jobts.workdirectory)
        os.chdir(jobts.workdirectory)

        ## Create the function 
        input_dir = np.sort(glob.glob(os.path.abspath(jobts.workdirectory)+os.sep+'GEOCml*'))[-1]

        cmd = 'LiCSBAS12_loop_closure.py -d %s -l %s' % (input_dir,
                                                        jobts.loop_closure['loop_thres']['value'])
        
        if jobts.loop_closure['multi_prime']['value']:
                cmd = cmd + ' --multi_prime'
        
        if not jobts.loop_closure['rm_ifg_list']['value'] == 'none':
                cmd = cmd + ' --rm_ifg_list %s' % (jobts.loop_closure['rm_ifg_list']['value'])

        cmd = cmd + ' --n_para %s' % (jobts.n_para)

        licsbastools.subprocessrun(cmd,verbose,log)

        os.chdir(cur_dir)
        jobts.loop_closure['done']['value'] = True

        return jobts

################################################################################
## sb_inv FUNCTION
################################################################################
def sb_inv(jobts, verbose: Optional[bool] = None, log: Optional[bool] = None):
        """Compute the inversion

        The function will inverse the time series, for an ``ezinsar.tsprocessing``.   

        Args:
                jobts (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for LiCSBAS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'licsbastsprocessing' in str(type(jobts)):
                raise ValueError(usermessage.errormsg(__name__,sb_inv.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-LiCSBAS processing.',None))
        
        if verbose == None:
                verbose = jobts.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,sb_inv.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if log == None:
                log = jobts.log
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,sb_inv.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        usermessage.openingmsg(__name__,sb_inv.__name__,__file__,__copyright__,'LiCSBAS Step: sb_inv',log,verbose)

        if jobts.loop_closure['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,sb_inv.__name__,__file__,__copyright__,
                        'The previous step (loop_closure) is not done.',None))

        # Check the job 
        jobts.check(verbose=False,mode='high')

        ## Work directory
        if not os.path.isdir(jobts.workdirectory):
                os.mkdir(jobts.workdirectory)
        os.chdir(jobts.workdirectory)

        ## Create the function 
        input_dir = np.sort(glob.glob(os.path.abspath(jobts.workdirectory)+os.sep+'GEOCml*'))[-1]

        cmd = 'LiCSBAS13_sb_inv.py -d %s --inv_alg %s --mem_size %s --gamma %s --n_para %s --n_unw_r_thre %s' % (input_dir,
                                                        jobts.sb_inv['inv_alg']['value'],
                                                        jobts.mem_size,
                                                        jobts.sb_inv['gamma']['value'],
                                                        jobts.n_para,
                                                        jobts.sb_inv['n_unw_r_thre']['value'],
                                                        )
        if jobts.sb_inv['keep_incfile']['value']:
                cmd = cmd + ' --keep_incfile'
        if jobts.sb_inv['gpu']['value']:
                cmd = cmd + ' --gpu'

        licsbastools.subprocessrun(cmd,verbose,log)

        os.chdir(cur_dir)
        jobts.sb_inv['done']['value'] = True

        return jobts

################################################################################
## vel_std FUNCTION
################################################################################
def vel_std(jobts, verbose: Optional[bool] = None, log: Optional[bool] = None):
        """Compute the velocity uncertainties by bootstrapping

        The function will compute the velocity uncertainties by bootstrapping, for an ``ezinsar.tsprocessing``.   

        Args:
                jobts (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for LiCSBAS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'licsbastsprocessing' in str(type(jobts)):
                raise ValueError(usermessage.errormsg(__name__,vel_std.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-LiCSBAS processing.',None))
        
        if verbose == None:
                verbose = jobts.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,vel_std.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if log == None:
                log = jobts.log
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,vel_std.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        usermessage.openingmsg(__name__,vel_std.__name__,__file__,__copyright__,'LiCSBAS Step: vel_std',log,verbose)

        if jobts.sb_inv['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,vel_std.__name__,__file__,__copyright__,
                        'The previous step (sb_inv) is not done.',None))

        # Check the job 
        jobts.check(verbose=False,mode='high')

        ## Work directory
        if not os.path.isdir(jobts.workdirectory):
                os.mkdir(jobts.workdirectory)
        os.chdir(jobts.workdirectory)

        ## Create the function 
        input_dir = np.sort(glob.glob(os.path.abspath(jobts.workdirectory)+os.sep+'TS_GEOCml*'))[-1]

        cmd = 'LiCSBAS14_vel_std.py -t %s --mem_size %s' % (input_dir,
                                                        jobts.mem_size,
                                                        )
        if jobts.vel_std['ransac']['value']:
                cmd = cmd + ' --ransac'

        if jobts.vel_std['gpu']['value']:
                cmd = cmd + ' --gpu'

        licsbastools.subprocessrun(cmd,verbose,log)

        os.chdir(cur_dir)
        jobts.vel_std['done']['value'] = True

        return jobts

################################################################################
## mask_ts FUNCTION
################################################################################
def mask_ts(jobts, verbose: Optional[bool] = None, log: Optional[bool] = None):
        """Mask the time series results

        The function will mask the time series results, for an ``ezinsar.tsprocessing``.   

        Args:
                jobts (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for LiCSBAS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'licsbastsprocessing' in str(type(jobts)):
                raise ValueError(usermessage.errormsg(__name__,mask_ts.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-LiCSBAS processing.',None))
        
        if verbose == None:
                verbose = jobts.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,mask_ts.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if log == None:
                log = jobts.log
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,mask_ts.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        usermessage.openingmsg(__name__,mask_ts.__name__,__file__,__copyright__,'LiCSBAS Step: mask_ts',log,verbose)

        if jobts.vel_std['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,mask_ts.__name__,__file__,__copyright__,
                        'The previous step (vel_std) is not done.',None))

        # Check the job 
        jobts.check(verbose=False,mode='high')

        ## Work directory
        if not os.path.isdir(jobts.workdirectory):
                os.mkdir(jobts.workdirectory)
        os.chdir(jobts.workdirectory)

        ## Create the function 
        input_dir = np.sort(glob.glob(os.path.abspath(jobts.workdirectory)+os.sep+'TS_GEOCml*'))[-1]

        cmd = 'LiCSBAS15_mask_ts.py -t %s -c %s -u %s -v %s -T %s -g %s -s %s -i %s -l %s -r %s' % (input_dir,
                                jobts.mask_ts['coh_avg_thres']['value'],
                                jobts.mask_ts['unw_r_thres']['value'],
                                jobts.mask_ts['vstd_thres']['value'],
                                jobts.mask_ts['maxTlen']['value'],
                                jobts.mask_ts['n_gap_thres']['value'],
                                jobts.mask_ts['stc_thres']['value'],
                                jobts.mask_ts['n_ifg_noloop']['value'],
                                jobts.mask_ts['n_loop_err']['value'],
                                jobts.mask_ts['resid_rms_err']['value'])
        
        if jobts.mask_ts['keep_isolated']['value']:
                cmd = cmd + ' --keep_isolated'
        
        if jobts.mask_ts['noautoadjust']['value']:
                cmd = cmd + ' --noautoadjust'

        if jobts.mask_ts['avg_phase_bias']['value']:
                cmd = cmd + ' --avg_phase_bias'

        licsbastools.subprocessrun(cmd,verbose,log)

        os.chdir(cur_dir)
        jobts.mask_ts['done']['value'] = True

        return jobts

################################################################################
## filt_ts FUNCTION
################################################################################
def filt_ts(jobts, verbose: Optional[bool] = None, log: Optional[bool] = None):
        """Filter for the time series results

        The function will apply a filter to the time series results, for an ``ezinsar.tsprocessing``.   

        Args:
                jobts (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for LiCSBAS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'licsbastsprocessing' in str(type(jobts)):
                raise ValueError(usermessage.errormsg(__name__,filt_ts.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-LiCSBAS processing.',None))
        
        if verbose == None:
                verbose = jobts.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,filt_ts.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if log == None:
                log = jobts.log
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,filt_ts.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        usermessage.openingmsg(__name__,filt_ts.__name__,__file__,__copyright__,'LiCSBAS Step: filt_ts',log,verbose)

        if jobts.mask_ts['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,filt_ts.__name__,__file__,__copyright__,
                        'The previous step (mask_ts) is not done.',None))

        # Check the job 
        jobts.check(verbose=False,mode='high')

        ## Work directory
        if not os.path.isdir(jobts.workdirectory):
                os.mkdir(jobts.workdirectory)
        os.chdir(jobts.workdirectory)

        ## Create the function 
        input_dir = np.sort(glob.glob(os.path.abspath(jobts.workdirectory)+os.sep+'TS_GEOCml*'))[-1]

        cmd = 'LiCSBAS16_filt_ts.py -t %s -s %s --n_para %s' % (input_dir,
                                jobts.filt_ts['sfilter']['value'],
                                jobts.n_para,
                                )
        
        if not jobts.filt_ts['tfilter']['value'] == 'auto':
                cmd = cmd + ' -y %s' % (jobts.filt_ts['tfilter']['value'])

        if not jobts.filt_ts['deramppoly']['value'] == 0: 
                cmd = cmd + ' -r %s' % (jobts.filt_ts['deramppoly']['value'])

        if jobts.filt_ts['demerr']['value']:
                cmd = cmd + ' --demerr'

        if jobts.filt_ts['hgt_linear']['value']:
                cmd = cmd + ' --hgt_linear'

        if (not jobts.filt_ts['deramppoly']['value'] == 0) or (jobts.filt_ts['hgt_linear']['value']): 
                cmd = cmd + ' --hgt_min %s' % (jobts.filt_ts['hgt_min']['value'])
                cmd = cmd + ' --hgt_max %s' % (jobts.filt_ts['hgt_max']['value'])

        if jobts.filt_ts['nomask']['value']:
                cmd = cmd + ' --nomask'
        
        if not jobts.filt_ts['range_geo']['value'] == 'none':
                cmd = cmd + ' --range_geo %s' % (jobts.filt_ts['range_geo']['value'])
        
        if not jobts.filt_ts['ex_range_geo']['value'] == 'none':
                cmd = cmd + ' --ex_range_geo %s' % (jobts.filt_ts['ex_range_geo']['value'])

        licsbastools.subprocessrun(cmd,verbose,log)

        # os.system('LiCSBAS_plot_ts.py -i %s/cum_filt.h5' % (input_dir))

        os.chdir(cur_dir)
        jobts.mask_ts['done']['value'] = True

        return jobts

################################################################################
## extract_res FUNCTION
################################################################################
def extract_res(jobts, verbose: Optional[bool] = None, log: Optional[bool] = None):
        """Extract the time series displacement results

        The function will extract the results from the time series results, for an ``ezinsar.tsprocessing``.   

        Args:
                jobts (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for LiCSBAS processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if not 'licsbastsprocessing' in str(type(jobts)):
                raise ValueError(usermessage.errormsg(__name__,extract_res.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-LiCSBAS processing.',None))
        
        if verbose == None:
                verbose = jobts.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,extract_res.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if log == None:
                log = jobts.log
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,extract_res.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        ## Work directory
        if not os.path.isdir(jobts.workdirectory):
                os.mkdir(jobts.workdirectory)
        os.chdir(jobts.workdirectory)
        
        usermessage.openingmsg(__name__,extract_res.__name__,__file__,__copyright__,'LiCSBAS Step: extract_res',log,verbose)

        ## Extraction of displacements
        input_dir = np.sort(glob.glob(os.path.abspath(jobts.workdirectory)+os.sep+'TS_GEOCml*'))[-1]

        data = importlibsbasresults(input_dir, 
                job = jobts,
                verbose = verbose,
                log = log)

        name = 'TS_LOS_%s_%s_%s_%s_%s_%s_%s' % (jobts.satellite,
                                                jobts.satmode,
                                                jobts.relorbit,
                                                jobts.satpass,
                                                jobts.ifgprocessor,
                                                jobts.processor,
                                                jobts.mode.replace('/',''))

        if jobts.extract_res['ecraseprevious']['value'] == True: 
                usermessage.warningmsg(__name__,__name__,__file__,'The previous file will be replaced.',jobts.log,verbose)
                name = name + '.eidata'
        else: 
                name = '%s_%s.eidata' % (name,len(glob.glob(name+'*')))

        ezinsardata.saveEZdata(data,name,verbose = verbose, log = log)

        os.chdir(cur_dir)
        jobts.extract_res['done']['value'] = True

        return jobts

################################################################################
## Extraction of displacements for LiCSBAS FUNCTION
################################################################################
def importlibsbasresults(workdirectory, 
        job = None, 
        dataset = None, 
        nodata = np.nan,
        meter_mode = 'UTM',
        verbose: Optional[bool] = True,
        log: Optional[bool] = None):
        """Import the MintPy results into an EZ-InSAR data file

        The function will import the MintPy results into a format for EZ-InSAR.

        Args:
                workdirectory (str): Work directory
                job (``ezinsar.job``): EZ-InSAR tsprocessing job. [Default: `None`]
                dataset (str): Selected dataset. [Default: `None`]
                nodata (float): No data value [Default: ``np.nan``]
                meter_mode (str): UTM grid [Default: ``UTM``]
                verbose: (bool): Verbose. [Default: `True`]
                log (str): Log file. [Default: `None`]

        Returns:
                ``ezinsar.data``: EZ-InSAR data class
        
        """
        cur_dir = os.getcwd()

        if not 'licsbastsprocessing' in str(type(job)):
                raise ValueError(usermessage.errormsg(__name__,importlibsbasresults.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-LiCSBAS processing.',None))

        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,importlibsbasresults.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if not log == None: 
                if not isinstance(log,str): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,importlibsbasresults.__name__,__file__,__copyright__,
                                'log','str',log))

        if not os.path.isdir(workdirectory):
                raise ValueError(usermessage.errormsg(__name__,importlibsbasresults.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        
        usermessage.openingmsg(__name__,importlibsbasresults.__name__,__file__,__copyright__,'Import the LiCSBAS results',log,verbose)

        os.chdir(workdirectory)

        ## Initialisation of the dataset
        usermessage.ezprint('Initialisation of the dataset...',log,verbose)
        data = ezinsardata.displacement()
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

        data.datainformation['TS_Processor'] = 'licsbas'
        data.datainformation['Approach'] = 'SBAS'
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

        data.datainformation['Path'] = str(workdirectory)

        usermessage.ezprint('\tdone',log,verbose)

        ## For the temporal data
        usermessage.ezprint('Extract the temporal information...',log,verbose)

        with h5py.File(workdirectory+os.sep+'cum_filt.h5',"r") as f:
                tmp = f['imdates'][()].astype(str).tolist()

        data.dates['value'] = []
        for di in tmp:
                data.dates['value'].append(datetime.strptime(di,"%Y%m%d"))
        data.dates['value'] = np.array(data.dates['value'])

        data.n_image['value'] = int(len(data.dates['value']))

        data.n_ifg['value'] = int(0)

        if not job == None: 
                data.date_ref['value'] = data.dates['value'][0]

        # data.ifg_date['value'] = np.array(0)

        usermessage.ezprint('\tdone',log,verbose)

        ## For the spatial data
        usermessage.ezprint('Extract the spatial information...',log,verbose)

        with h5py.File(workdirectory+os.sep+'cum_filt.h5',"r") as f:
                n_im, length, width = f['cum'].shape

                yc = float(f['corner_lat'][()])
                xc = float(f['corner_lon'][()])
                dy = float(f['post_lat'][()])
                dx = float(f['post_lon'][()])
 
                xmin = xc
                xmax = xc + dx * width

                ymin = yc + dy * length
                ymax = yc
                
                a, b = np.meshgrid(
                        np.linspace(xmin,xmax,width),
                        np.linspace(ymin,ymax,length),
                        )               

                data.lon_grid['value'] = a 
                data.lat_grid['value'] = b

        if meter_mode == 'UTM': 
                utm_crs_list = pyproj.database.query_utm_crs_info(
                        datum_name="WGS 84",
                        area_of_interest=pyproj.aoi.AreaOfInterest(
                                west_lon_degree=np.nanmin(data.lon_grid['value']),
                                south_lat_degree=np.nanmin(data.lat_grid['value']),
                                east_lon_degree=np.nanmax(data.lon_grid['value']),
                                north_lat_degree=np.nanmax(data.lat_grid['value']),
                                ),
                        )
                meter_mode = utm_crs_list[0].code

        latlon_to_meter = pyproj.Transformer.from_crs('epsg:4326','epsg:%s' % (meter_mode))
        data.x_utm['value'], data.y_utm['value'] = latlon_to_meter.transform(data.lat_grid['value'],data.lon_grid['value'])
        data.code_meter['value'] = 'epsg:%s' % (meter_mode)

        usermessage.ezprint('\tdone',log,verbose)

        ## For the ground data
        usermessage.ezprint('Extract the ground information...',log,verbose)

        with h5py.File(workdirectory+os.sep+'cum_filt.h5', "r") as f:
                data.radlkU['value'] = f['U.geo'][()]
                data.radlkE['value'] = f['E.geo'][()]
                data.radlkN['value'] = f['N.geo'][()]
        
        usermessage.ezprint('\tdone',log,verbose)

        ## For the displacement data
        usermessage.ezprint('Extract the displacement data...',log,verbose)

        with h5py.File(workdirectory+os.sep+'cum_filt.h5', "r") as f:
                data.dispLOS['value'] = f['cum'][()]
        
        for a in range(data.dispLOS['value'].shape[0]):
                data.dispLOS['value'][a,:,:][data.dispLOS['value'][a,:,:] == 0] = np.nan
                data.dispLOS['value'][a,:,:][data.dispLOS['value'][a,:,:] != np.nan] = data.dispLOS['value'][a,:,:][data.dispLOS['value'][a,:,:] != np.nan]

                # if applymask == True: 
                #         data.dispLOS['value'][a,:,:][mask==False] = np.nan

                data.dispLOS['value'][a,:,:][np.isnan(data.dispLOS['value'][a,:,:])] = nodata
                        
        with h5py.File(workdirectory+os.sep+'cum_filt.h5', "r") as f:
                data.rateLOS['value'] = f['vel'][()]
                data.sigmarateLOS['value'] = f['vstd'][()]

        data.rateLOS['value'][data.rateLOS['value']==0] = np.nan
        data.sigmarateLOS['value'][data.sigmarateLOS['value']==0] = np.nan

        data.rateLOS['value'][data.rateLOS['value'] != np.nan] = data.rateLOS['value'][data.rateLOS['value'] != np.nan]
        data.sigmarateLOS['value'][data.sigmarateLOS['value'] != np.nan] = data.sigmarateLOS['value'][data.sigmarateLOS['value'] != np.nan]
        print( data.rateLOS['value'].shape)
        # if applymask == True: 
        #         data.rateLOS['value'][mask==False] = np.nan
        #         data.sigmarateLOS['value'][mask==False] = np.nan

        data.rateLOS['value'][np.isnan(data.rateLOS['value'])] = nodata
        data.sigmarateLOS['value'][np.isnan(data.sigmarateLOS['value'])] = nodata

        usermessage.ezprint('\tdone',log,verbose)

        ## For the reference point
        usermessage.ezprint('Extract the reference-point information...',log,verbose)

        data.referencepoint['value']['index'] = 0
        data.referencepoint['value']['lat_pt_ref'] = 0
        data.referencepoint['value']['lon_pt_ref'] = 0
        data.referencepoint['value']['lon_pt_refarea'] = 0
        data.referencepoint['value']['lat_pt_refarea'] = 0
        data.referencepoint['value']['radius'] = 0
        data.referencepoint['value']['rateLOS'] = 0

        usermessage.ezprint('\tdone',log,verbose)

        ## For the baselines
        # usermessage.ezprint('Extract the perpendicular baselines...',log,verbose)

        # with h5py.File(dataset, "r") as f:
        #         data.bperp['value'] = f['bperp'][()]
                
        os.chdir(cur_dir)

        return data