#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to process StripMap data with Doris processor for ifgstack

The module allows to process StripMap data with Doris processor for ifgstack from an ``ezinsar.ifgstack`` job. 
    
    (From `ezinsar` package)

Changelog:
        * 1.0.1: Add the masking based on a masked DEM in DEM geometry, Jun. 2025, Alexis Hrysiewicz
        * 1.0.1: Fix regarding the maskifg parameters, Feb. 2025, Alexis Hrysiewicz
        * 1.0.0: Initial version, Dec. 2024

Todo: 
        * Optimisation for orbit detection

"""

################################################################################
## Python packages
################################################################################
import os
import numpy as np
import glob
from typing import Optional, Union
from matplotlib import path
from shapely.wkt import loads
import shutil
import copy

from ezinsar import usermessage
from ezinsar import constants
from ezinsar.eicomponents.processor.dorismodule import doristools
from ezinsar.eicomponents.processor.dorismodule import dorisstack
from ezinsar.tools import geocoding

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## importrslc FUNCTION
################################################################################
def importrslc(jobifg, verbose: Optional[bool] = None):
        """Import the RSLC files 

        The function checks the SLC files, from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()
        
        if not 'dorisifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,importrslc.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,importrslc.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))
        
        usermessage.openingmsg(__name__,importrslc.__name__,__file__,__copyright__,'ifgstack Step: importrslc',jobifg.log,verbose)

        jobifg.check(verbose=False,mode='high')

        ## Create the work directory
        if not os.path.isdir(jobifg.workdirectory):
                os.mkdir(jobifg.workdirectory)
        os.chdir(jobifg.workdirectory)

        ## Create the new date file
        with open(jobifg.pathstack+os.sep+'rslc_'+jobifg.polarisation[0].lower()+os.sep+'dates','r') as fi:
                with open(jobifg.workdirectory+os.sep+'dates','w') as fout:
                        for di in fi:
                                dslc = di.strip()
                                if not dslc in jobifg.importrslc['excludedate']['value'].split(','):
                                        fout.write('%s\n' % (dslc))

        ## Copy the RSLC
        if not os.path.isdir(jobifg.workdirectory+os.sep+'rslc'):
                os.mkdir(jobifg.workdirectory+os.sep+'rslc')

        for dslc in doristools.readdatefile(jobifg.workdirectory+os.sep+'dates'):
                for poli in jobifg.polarisation:
                        usermessage.ezprint('\tCopy the data for %s %s' % (dslc,poli.lower()),jobifg.log,verbose) 

                        shutil.copy(jobifg.pathstack+os.sep+'rslc_'+poli.lower()+os.sep+dslc+'.'+poli.lower()+'.rslc', 
                                'rslc'+os.sep+dslc+'.'+poli.lower()+'.rslc') 
                        shutil.copy(jobifg.pathstack+os.sep+'rslc_'+poli.lower()+os.sep+dslc+'.'+poli.lower()+'.rslc.res', 
                                'rslc'+os.sep+dslc+'.'+poli.lower()+'.rslc.res') 

        os.chdir(cur_dir)

        jobifg.importrslc['done']['value'] = True

        return jobifg

################################################################################
## refinerefdate FUNCTION
################################################################################
def refinerefdate(jobifg, verbose: Optional[bool] = None):
        """Refine the reference dates

        The function refines the reference dates, from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()
        if not 'dorisifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,refinerefdate.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,refinerefdate.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))
        
        usermessage.openingmsg(__name__,refinerefdate.__name__,__file__,__copyright__,'ifgstack Step: refinerefdate',jobifg.log,verbose)

        if jobifg.refinerefdate['process']['value'] == True:
                usermessage.warningmsg(__name__,refinerefdate.__name__,__file__,'This option is not implemented.',jobifg.log,verbose)

        os.chdir(cur_dir)
        jobifg.refinerefdate['done']['value'] = True

        return jobifg

################################################################################
## ifgnetwork FUNCTION
################################################################################
def ifgnetwork(jobifg, verbose: Optional[bool] = None):
        """Create the interfermetric network

        The function will compute the inteferometric network, from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()
        if not 'dorisifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,ifgnetwork.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ifgnetwork.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))
        
        usermessage.openingmsg(__name__,ifgnetwork.__name__,__file__,__copyright__,'ifgstack Step: ifgnetwork',jobifg.log,verbose)

        jobifg.check(verbose=False,mode='high')

        if jobifg.importrslc['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,ifgnetwork.__name__,__file__,__copyright__,
                                'The previous step (importrslc) is not done.',None))
        
        if jobifg.modestack in ['StaMPS_PS', 'StaMPS_PSSBAS']:
                modePS = True
                if jobifg.modestack == 'StaMPS_PS': 
                        modeSBAS = False
        else: 
                modePS = False

        if jobifg.modestack in ['normal','StaMPS_SBAS','StaMPS_PSSBAS']: 
                if jobifg.ifgnetwork['SBAS_opti']['value'] == False: 
                        modeSBAS = 'normal'  
                else: 
                        modeSBAS = jobifg.ifgnetwork['SBAS_opti']['value']
                
        dorisstack.computeifgnetwork(jobifg.workdirectory+os.sep+'rslc', 
                                jobifg.workdirectory+os.sep+'dates',
                                jobifg.workdirectory+os.sep+'rslc'+os.sep+jobifg.refdate+'.'+jobifg.polarisation[0].lower()+'.rslc.res',
                                modePS = modePS ,
                                modeSBAS = modeSBAS,
                                bperp_mm = [jobifg.ifgnetwork['bperp_min']['value'], jobifg.ifgnetwork['bperp_max']['value']], 
                                delta_T = [jobifg.ifgnetwork['delta_T_min']['value'], jobifg.ifgnetwork['delta_T_max']['value']], 
                                delta_n_max = jobifg.ifgnetwork['delta_n_max']['value'],
                                bperp_th=50, 
                                pol=jobifg.polarisation[0].lower(),
                                orbit_sampling=6,
                                verbose = verbose,
                                log = jobifg.log)

        
        ## Finalisation fo the baseline files 
        if os.path.isfile(jobifg.workdirectory+os.sep+'rslc'+os.sep+'bperp_file_Single.txt'):
                os.rename(jobifg.workdirectory+os.sep+'rslc'+os.sep+'bperp_file_Single.txt',jobifg.workdirectory+os.sep+'bperp_file_Single.txt')
                dorisstack.baselinefigure(jobifg.workdirectory+os.sep+'bperp_file_Single.txt')

        if os.path.isfile(jobifg.workdirectory+os.sep+'rslc'+os.sep+'bperp_file_MR.txt'):
                os.rename(jobifg.workdirectory+os.sep+'rslc'+os.sep+'bperp_file_MR.txt',jobifg.workdirectory+os.sep+'bperp_file_MR.txt')
                dorisstack.baselinefigure(jobifg.workdirectory+os.sep+'bperp_file_MR.txt')        

        if os.path.isfile(jobifg.workdirectory+os.sep+'rslc'+os.sep+'bperp_file.txt'):
                os.rename(jobifg.workdirectory+os.sep+'rslc'+os.sep+'bperp_file.txt',jobifg.workdirectory+os.sep+'bperp_file.txt')
                dorisstack.baselinefigure(jobifg.workdirectory+os.sep+'bperp_file.txt')   

        os.chdir(cur_dir)
        jobifg.ifgnetwork['done']['value'] = True

        return jobifg 

################################################################################
## ifgcompute FUNCTION
################################################################################
def ifgcompute(jobifg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Compute the interferograms

        The function will compute the interferograms, from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()

        if not 'dorisifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,ifgcompute.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ifgcompute.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))
        
        if modeforce == None:
                modeforce = jobifg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ifgcompute.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobifg.log))

        if not jobifg.log == None: 
                log = os.path.abspath(jobifg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,ifgcompute.__name__,__file__,__copyright__,'ifgstack Step: ifgcompute',log,verbose)

        jobifg.check(verbose=False,mode='high')

        if jobifg.ifgnetwork['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,ifgcompute.__name__,__file__,__copyright__,
                        'The previous step (ifgnetwork) is not done.',None))
        

        if jobifg.workflow == 'single':
                # Directory
                if not os.path.isdir(jobifg.workdirectory+os.sep+'single_diff'):
                        os.mkdir(jobifg.workdirectory+os.sep+os.sep+'single_diff')
                os.chdir(jobifg.workdirectory+os.sep+'single_diff')

                baselines = dorisstack.readbaselinefile('..'+os.sep+'bperp_file_Single.txt')
                
                ## Loop of processing (parallellisation possible????)
                idx = 0 
                while idx <= len(baselines['Idx'])-1:
                        if baselines['Check'][idx] == 1:
                                for poli in jobifg.polarisation:
                                        ncore = 1
                                        h = 0
                                        dict_cmd = {}

                                        prefix_ifg = baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()

                                        while ncore <= jobifg.computerworkers:
                                                if (not os.path.isfile(jobifg.workdirectory+os.sep+'single_diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.ifg')) or modeforce == True:

                                                        ## Creation of the tmp directories
                                                        if not os.path.isdir(baselines['Slave'][idx]+'_'+poli.lower()):
                                                                os.mkdir(baselines['Slave'][idx]+'_'+poli.lower())

                                                        ## Copy the RSLCs
                                                        shutil.copy('..'+os.sep+'rslc'+os.sep+baselines['Master'][idx]+'.'+poli.lower()+'.rslc',
                                                                baselines['Slave'][idx]+'_'+poli.lower()+os.sep+baselines['Master'][idx]+'.'+poli.lower()+'.rslc')
                                                        shutil.copy('..'+os.sep+'rslc'+os.sep+baselines['Master'][idx]+'.'+poli.lower()+'.rslc.res',
                                                                baselines['Slave'][idx]+'_'+poli.lower()+os.sep+baselines['Master'][idx]+'.'+poli.lower()+'.rslc.res')
                                                        
                                                        shutil.copy('..'+os.sep+'rslc'+os.sep+baselines['Slave'][idx]+'.'+poli.lower()+'.rslc',
                                                                baselines['Slave'][idx]+'_'+poli.lower()+os.sep+baselines['Slave'][idx]+'.'+poli.lower()+'.rslc')
                                                        shutil.copy('..'+os.sep+'rslc'+os.sep+baselines['Slave'][idx]+'.'+poli.lower()+'.rslc.res',
                                                                baselines['Slave'][idx]+'_'+poli.lower()+os.sep+baselines['Slave'][idx]+'.'+poli.lower()+'.rslc.res')
                                                        
                                                        ## Copy the DEM
                                                        listDEM = glob.glob(jobifg.pathDEM+os.sep+'*r4') + glob.glob(jobifg.pathDEM+os.sep+'*hdr')
                                                        for fi in listDEM:
                                                                shutil.copy(fi,baselines['Slave'][idx]+'_'+poli.lower()+os.sep+fi.split(os.sep)[-1])

                                                        ## Input card creation
                                                        with open(baselines['Slave'][idx]+'_'+poli.lower()+os.sep+'config_card.tmp','w') as fout: 

                                                                fout.write('cc **********************************************************************\n')
                                                                fout.write('c ***  Doris \inputfile *****\n')
                                                                fout.write('c **********************************************************************\n')
                                                                fout.write(' c\n')
                                                                fout.write(' c\n')
                                                                fout.write(' comment  ___general options___\n')
                                                                fout.write(' c\n')
                                                                fout.write('c SCREEN          debug                           // level of output to standard out\n')
                                                                fout.write('SCREEN          info                           // level of output to standard out\n')
                                                                fout.write('MEMORY          %s                             // MB\n' %(jobifg.computerRAM))
                                                                fout.write('BEEP            error                            // level of beeping\n')
                                                                fout.write('OVERWRITE                                       // overwrite existing files\n')
                                                                fout.write('BATCH                                           // non-interactive\n')
                                                                fout.write('c LISTINPUT OFF                                 // prevents copy of this file to log\n')
                                                                fout.write('c\n')

                                                                fout.write('PROCESS          COARSEORB\n')
                                                                
                                                                if jobifg.ifgcompute['FILTAZI']['value'] == True:
                                                                        fout.write('PROCESS          m_filtazi\n')
                                                                        fout.write('PROCESS          s_filtazi\n')

                                                                if jobifg.ifgcompute['FILTRANGE']['value'] == True:
                                                                        fout.write('PROCESS          FILTRANGE\n')

                                                                fout.write('PROCESS          INTERFERO\n')
                                                                
                                                                if jobifg.ifgcompute['Remove_FE']['value'] == True:
                                                                        fout.write('PROCESS          COMPREFPHA\n')
                                                                        fout.write('PROCESS          SUBTRREFPHA\n')
                                                                        
                                                                if jobifg.ifgcompute['Remove_TOPO']['value'] == True:
                                                                        fout.write('PROCESS          COMPREFDEM\n')
                                                                        fout.write('PROCESS          SUBTRREFDEM\n')

                                                                if jobifg.ifgcompute['Coherence']['value'] == True:
                                                                        fout.write('PROCESS          COHERENCE\n')

                                                                fout.write('c                                              //\n')
                                                                fout.write(' c                                              //\n')
                                                                fout.write(' comment  ___the general io files___            //\n')
                                                                fout.write(' c                                              //\n')
                                                                fout.write('LOGFILE         %s                         // log file\n' % (log))
                                                                fout.write('M_RESFILE       %s  // parameter file\n' % (baselines['Master'][idx]+'.'+poli.lower()+'.rslc.res'))
                                                                fout.write('S_RESFILE       %s                     // parameter file\n' % (baselines['Slave'][idx]+'.'+poli.lower()+'.rslc.res'))
                                                                fout.write('I_RESFILE       %s               // parameter file\n' % (prefix_ifg+'.ifg'))
                                                                fout.write('HEIGHT              	0                	 // average WGS84 height\n')
                                                                fout.write('ORB_INTERP          	POLYFIT             	 // orbit interpolation method\n')
                                                                fout.write('ELLIPSOID           	WGS84               	 // WGS84, GRS80, BESSEL or define major and minor axis\n')
                                                                fout.write('c                             \n')
                                                                fout.write('DUMPBASELINE    50 50\n')
                                                                fout.write(' c                                              //\n')

                                                                if jobifg.ifgcompute['FILTAZI']['value'] == True:
                                                                        fout.write(' c                                              //\n')
                                                                        fout.write(' comment ___AZIMUTH FILTERING___                //\n')
                                                                        fout.write(' c                                              //\n')
                                                                        fout.write('AF_BLOCKSIZE    %s                            // fftlength each column\n' % (jobifg.ifgcompute['AF_BLOCKSIZE']['value']))
                                                                        fout.write('AF_OVERLAP      %s                              // hbs\n' % (jobifg.ifgcompute['AF_OVERLAP']['value']))
                                                                        fout.write('c AF_HAMMING    %s                                  \n' % (jobifg.ifgcompute['AF_HAMMING']['value']))
                                                                        fout.write('AF_OUT_MASTER   master_azifilt.rslc                  \n')
                                                                        fout.write('AF_OUT_SLAVE    slave_azifilt.rslc                   \n')
                                                                        fout.write('AF_OUT_FORMAT   %s                                 \n' % (jobifg.ifgcompute['AF_OUT_FORMAT']['value']))
                                                                        fout.write('c                           \n')

                                                                if jobifg.ifgcompute['FILTRANGE']['value'] == True:
                                                                        fout.write(' c                                              //          \n')
                                                                        fout.write(' comment   ___ ADAPTIVE RANGE FILTERING ___                 \n')
                                                                        fout.write(' c                                                          \n')
                                                                        fout.write('RF_METHOD       %s                                          \n' % (jobifg.ifgcompute['RF_METHOD']['value']))
                                                                        fout.write('RF_FFTLENGTH    %s                               // 5 km    \n' % (jobifg.ifgcompute['RF_FFTLENGTH']['value']))
                                                                        fout.write('RF_OVERLAP      %s                                          \n' % (jobifg.ifgcompute['RF_OVERLAP']['value']))
                                                                        fout.write('RF_SLOPE        %s                                          \n' % (jobifg.ifgcompute['RF_SLOPE']['value']))
                                                                        fout.write('RF_NLMEAN       %s                              // odd      \n' % (jobifg.ifgcompute['RF_NLMEAN']['value']))
                                                                        fout.write('RF_THRESHOLD    %s                               // SNR     \n' % (jobifg.ifgcompute['RF_THRESHOLD']['value']))
                                                                        fout.write('RF_HAMMING      %s                            // alpha      \n' % (jobifg.ifgcompute['RF_HAMMING']['value']))
                                                                        fout.write('RF_OVERSAMPLE   %s                                          \n' % (jobifg.ifgcompute['RF_OVERSAMPLE']['value']))
                                                                        fout.write('RF_WEIGHTCORR   %s                                          \n' % (jobifg.ifgcompute['RF_WEIGHTCORR']['value']))
                                                                        fout.write('RF_OUT_MASTER   master_filtrg.rslc                          \n')
                                                                        fout.write('RF_OUT_SLAVE    slave_filtrg.rslc                           \n')
                                                                        fout.write('RF_OUT_FORMAT   %s                                          \n' % (jobifg.ifgcompute['RF_OUT_FORMAT']['value']))          

                                                                fout.write(' c                                              //          \n')
                                                                fout.write(' comment ___interferogram generation___                     \n')
                                                                fout.write(' c                                                          \n')
                                                                fout.write(' c\n')
                                                                fout.write('INT_OUT_CINT    %s.cint.raw                 // optional        \n' % (prefix_ifg))
                                                                fout.write('INT_MULTILOOK   1 1                            // line, pixel\n')

                                                                if jobifg.ifgcompute['Remove_FE']['value'] == True:
                                                                        fout.write(' c                                              //          \n')
                                                                        fout.write(' comment   ___ COMPREFPHA ___                               \n')
                                                                        fout.write(' c                                                          \n')
                                                                        fout.write('FE_METHOD       %s                                          \n' % (jobifg.ifgcompute['FE_METHOD']['value']))
                                                                        fout.write('FE_DEGREE       %s                                          \n' % (jobifg.ifgcompute['FE_DEGREE']['value']))
                                                                        fout.write('FE_NPOINTS      %s                                          \n' % (jobifg.ifgcompute['FE_NPOINTS']['value'])) 
                                                                        fout.write(' c                                              //          \n')
                                                                        fout.write(' comment   ___ COMPREFPHA ___                               \n')
                                                                        fout.write(' c                                                          \n')
                                                                        fout.write('SRP_METHOD      %s                                          \n' % (jobifg.ifgcompute['SRP_METHOD']['value']))
                                                                        fout.write('SRP_OUT_CINT    %s.cint.minrefpha.raw                       \n' % (prefix_ifg))

                                                                if jobifg.ifgcompute['Remove_TOPO']['value'] == True:

                                                                        paradem = doristools.readDEMpara(baselines['Slave'][idx]+'_'+poli.lower()+os.sep+jobifg.nameDEM)

                                                                        fout.write(' c                                              //          \n')
                                                                        fout.write(' comment   ___ comprefdem ___                               \n')
                                                                        fout.write(' c                                                          \n')
                                                                        fout.write('CRD_INCLUDE_FE       OFF                                    \n')
                                                                        fout.write('CRD_IN_FORMAT        real4                                  \n')
                                                                        fout.write('CRD_IN_DEM      %s                                          \n' % (jobifg.nameDEM))
                                                                        fout.write('CRD_IN_SIZE          %d %d                                  // rows cols\n' % (paradem['lines'],paradem['samples']))
                                                                        fout.write('CRD_IN_DELTA    %f %f                                       // in degrees       \n'  % (np.abs(paradem['deltalat']),np.abs(paradem['deltalon'])))
                                                                        fout.write('CRD_IN_UL       %f %f                                       // lat and lon of upper left\n'% (paradem['lat'],paradem['lon']))
                                                                        fout.write('CRD_IN_NODATA   %d                                          \n' % (paradem['nodata']))
                                                                        fout.write('CRD_OUT_FILE    refdem_1l.raw                               // synthetic amplitude\n')
                                                                        fout.write('CRD_OUT_DEM_LP  dem_radar.raw                               \n')

                                                                        fout.write(' c                                              //          \n')
                                                                        fout.write(' comment   ___ subrefdem ___                                \n')
                                                                        fout.write(' c                                                          \n')
                                                                        fout.write('SRD_OUT_CINT        	%s.cint.minrefdem.raw           \n' % (prefix_ifg))
                                                                        fout.write('SRD_OFFSET          	%d %d                           \n' % (jobifg.ifgcompute['SRD_OFFSET_1']['value'],jobifg.ifgcompute['SRD_OFFSET_2']['value']))

                                                                if jobifg.ifgcompute['Coherence']['value'] == True:

                                                                        fout.write(' c                                              //          \n')
                                                                        fout.write(' comment   ___ coherence ___                                \n')
                                                                        fout.write(' c                                                          \n')
                                                                        fout.write('COH_METHOD                %s                                \n' % (jobifg.ifgcompute['COH_METHOD']['value']))
                                                                        fout.write('COH_WINSIZE               %d %d                             \n' % (jobifg.ifgcompute['COH_WINSIZE_1']['value'],jobifg.ifgcompute['COH_WINSIZE_2']['value']))
                                                                        fout.write('COH_MULTILOOK             %d %d                             \n' % (jobifg.mlran,jobifg.mlazi))
                                                                        fout.write('COH_OUT_COH               %s.cc                              \n' % (prefix_ifg))
                                                                
                                                                fout.write('STOP\n')
                                                
                                                        dict_cmd['cmd%s' % (h)] = [ ['cd',baselines['Slave'][idx]+'_'+poli.lower(),';','doris','config_card.tmp'],
                                                                baselines['Slave'][idx]+'_'+poli.lower()+os.sep+'config_card.tmp']
                                                        
                                                        ncore = ncore + 1
                                                        h = h + 1

                                        # Run
                                        if h > 0:
                                                doristools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg.computerworkers,verbose,log)
                                        
                        idx = idx + 1

                ## Display the interferograms
                listifg1 = glob.glob('*'+os.sep+'*.cint.raw')
                listifg2 = glob.glob('*'+os.sep+'*.cint.minrefpha.raw') 
                listifg3 = glob.glob('*'+os.sep+'*.cint.minrefdem.raw')

                if listifg3:
                        listifg = listifg3
                elif listifg2:
                        listifg = listifg2
                elif listifg1:
                        listifg = listifg1

                paraimage = []
                listimage = []
                check_run = False
                for fi in listifg:
                        if (not os.path.isfile(fi+'.ras')) or modeforce == True:
                                paraimage.append(doristools.readimagepara(os.path.dirname(fi)+os.sep+fi.split(os.sep)[-1].split('.')[0]+'.ifg',mode = 'ifg'))
                                listimage.append(fi)
                                check_run = True 

                if check_run == True:                                 
                        doristools.multilookimage(listimage,
                                'mixed',
                                paraimage,
                                '-fcr4',
                                jobifg.mlran,
                                jobifg.mlazi,
                                colormap = constants.__file__.replace('constants.py','tools%scolormap%scmap_sar.csv' % (os.sep,os.sep)),
                                log = log,
                                verbose = verbose)
                                
                ## Display the coherences
                if jobifg.ifgcompute['Coherence']['value'] == True:
                        listifg = glob.glob('*'+os.sep+'*.cc')
                        
                        paraimage = []
                        listimage = []
                        check_run = False
                        for fi in listifg:
                                if (not os.path.isfile(fi+'.ras')) or modeforce == True:
                                        paraimage.append(doristools.readimagepara(os.path.dirname(fi)+os.sep+fi.split(os.sep)[-1].split('.')[0]+'.ifg',mode = 'coh'))
                                        listimage.append(fi)
                                        check_run = True 

                        if check_run == True:                                 
                                doristools.multilookimage(listimage,
                                        'coh',
                                        paraimage,
                                        '-fr4',
                                        1,
                                        1,
                                        colormap = constants.__file__.replace('constants.py','tools%scolormap%scmap_gray.csv' % (os.sep,os.sep)),
                                        log = log,
                                        verbose = verbose)

                ## Propagation of the network
                if not os.path.isdir(jobifg.workdirectory+os.sep+'diff'):
                        os.mkdir(jobifg.workdirectory+os.sep+os.sep+'diff')
                os.chdir(jobifg.workdirectory+os.sep+'diff')

                baselines = dorisstack.readbaselinefile('..'+os.sep+'bperp_file.txt')
                
                ## Loop of processing (parallellisation possible????)
                idx = 0
                
                while idx <= len(baselines['Idx'])-1:
                        if baselines['Check'][idx] == 1:
                                for poli in jobifg.polarisation:
                                        if (not os.path.isfile(baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.ifg')) or modeforce == True:
                                                
                                                if os.path.isfile(baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.ifg'):
                                                        os.remove(baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.ifg')
                                                h = 0
                                                dict_cmd = {}

                                                prefix_ifg = baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()

                                                ## Copy the RSLCs
                                                shutil.copy('..'+os.sep+'rslc'+os.sep+baselines['Master'][idx]+'.'+poli.lower()+'.rslc',
                                                        baselines['Master'][idx]+'.'+poli.lower()+'.rslc')
                                                shutil.copy('..'+os.sep+'rslc'+os.sep+baselines['Master'][idx]+'.'+poli.lower()+'.rslc.res',
                                                        prefix_ifg+'.master.rslc.res')
                                                
                                                shutil.copy('..'+os.sep+'rslc'+os.sep+baselines['Slave'][idx]+'.'+poli.lower()+'.rslc',
                                                        baselines['Slave'][idx]+'.'+poli.lower()+'.rslc')
                                                shutil.copy('..'+os.sep+'rslc'+os.sep+baselines['Slave'][idx]+'.'+poli.lower()+'.rslc.res',
                                                        prefix_ifg+'.slave.rslc.res')

                                                ## Modification of the master res file
                                                if not baselines['Master'][idx] == jobifg.refdate:
                                                        paraimage = doristools.readimagepara(prefix_ifg+'.master.rslc.res')

                                                        dict_tmp = dict()
                                                        dict_tmp['cmd%s' % (0)] = [ ['doris.rmstep.sh','resample',prefix_ifg+'.master.rslc.res'],
                                                                None]                                         
                                                        doristools.wrappersubprocess(dict_tmp,jobifg.computercores,jobifg.computerworkers,verbose,log)

                                                        with open(prefix_ifg+'.master.rslc.res') as fi:
                                                                lines = fi.readlines()

                                                        with open(prefix_ifg+'.master.rslc.res','w') as fout:
                                                                for li in lines:
                                                                        li = li.replace('SLAVE','MASTER')
                                                                        li = li.replace('.slc','.rslc')
                                                                        if '*_Start_crop:' in li:
                                                                                break
                                                                        fout.write('%s' % (li))

                                                                fout.write('*_Start_crop:                   master step01\n')
                                                                fout.write('*******************************************************************\n')
                                                                fout.write('Data_output_file:                               %s\n' % (baselines['Master'][idx]+'.'+poli.lower()+'.rslc'))
                                                                fout.write('Data_output_format:                             complex_short\n')
                                                                fout.write('First_line (w.r.t. original_image):             %s\n' % (paraimage['First_line (w.r.t. original_image)']))
                                                                fout.write('Last_line (w.r.t. original_image):              %s\n' % (paraimage['Last_line (w.r.t. original_image)']))
                                                                fout.write('First_pixel (w.r.t. original_image):            %s\n' % (paraimage['First_pixel (w.r.t. original_image)']))
                                                                fout.write('Last_pixel (w.r.t. original_image):             %s\n' % (paraimage['Last_pixel (w.r.t. original_image)']))
                                                                fout.write('Number of lines (non-multilooked):              %s\n' % (paraimage['Last_line (w.r.t. original_image)']-paraimage['First_line (w.r.t. original_image)']+1))
                                                                fout.write('Number of pixels (non-multilooked):             %s\n'  % (paraimage['Last_pixel (w.r.t. original_image)']-paraimage['First_pixel (w.r.t. original_image)']+1))
                                                                fout.write('*******************************************************************\n')
                                                                fout.write('* End_crop:_NORMAL\n')
                                                                fout.write('*******************************************************************\n')
                                                
                                                ## Modification of the slave res file
                                                if baselines['Slave'][idx] == jobifg.refdate:
                                                        paraimage = doristools.readimagepara(prefix_ifg+'.slave.rslc.res')

                                                        with open(prefix_ifg+'.slave.rslc.res') as fi:
                                                                lines = fi.readlines()

                                                        with open(prefix_ifg+'.slave.rslc.res','w') as fout:
                                                                for li in lines:
                                                                        li = li.replace('MASTER ','SLAVE ')
                                                                        li = li.replace('master ','slave ')
                                                                        li = li.replace('.slc','.rslc')
                                                                        if 'resample:' in li:
                                                                                fout.write('resample:               1\n')
                                                                        fout.write('%s' % (li))

                                                                fout.write('*******************************************************************\n')
                                                                fout.write('*_Start_resample:                   \n')
                                                                fout.write('*******************************************************************\n')
                                                                fout.write('Shifted azimuth spectrum:                       1\n')
                                                                fout.write('Data_output_file:                               %s\n' % (baselines['Slave'][idx]+'.'+poli.lower()+'.rslc'))
                                                                fout.write('Data_output_format:                             complex_short\n')
                                                                fout.write('Interpolation kernel:                           12 point raised cosine kernel\n')
                                                                fout.write('First_line (w.r.t. original_master):             %s\n' % (paraimage['First_line (w.r.t. original_image)']))
                                                                fout.write('Last_line (w.r.t. original_master):              %s\n' % (paraimage['Last_line (w.r.t. original_image)']))
                                                                fout.write('First_pixel (w.r.t. original_master):            %s\n' % (paraimage['First_pixel (w.r.t. original_image)']))
                                                                fout.write('Last_pixel (w.r.t. original_master):             %s\n' % (paraimage['Last_pixel (w.r.t. original_image)']))
                                                                fout.write('*******************************************************************\n')
                                                                fout.write('* End_resample:_NORMAL\n')
                                                                fout.write('*******************************************************************\n')

                                                # Input card creation
                                                with open('config_card.tmp','w') as fout: 

                                                        fout.write('cc **********************************************************************\n')
                                                        fout.write('c ***  Doris \inputfile *****\n')
                                                        fout.write('c **********************************************************************\n')
                                                        fout.write(' c\n')
                                                        fout.write(' c\n')
                                                        fout.write(' comment  ___general options___\n')
                                                        fout.write(' c\n')
                                                        fout.write('c SCREEN          debug                           // level of output to standard out\n')
                                                        fout.write('SCREEN          info                           // level of output to standard out\n')
                                                        fout.write('MEMORY          %s                             // MB\n' %(jobifg.computerRAM))
                                                        fout.write('BEEP            error                            // level of beeping\n')
                                                        fout.write('OVERWRITE                                       // overwrite existing files\n')
                                                        fout.write('BATCH                                           // non-interactive\n')
                                                        fout.write('c LISTINPUT OFF                                 // prevents copy of this file to log\n')
                                                        fout.write('c\n')

                                                        fout.write('PROCESS          COARSEORB\n')
                                                        
                                                        # if jobifg.ifgcompute['FILTAZI']['value'] == True:
                                                        #         fout.write('PROCESS          m_filtazi\n')
                                                        #         fout.write('PROCESS          s_filtazi\n')

                                                        # if jobifg.ifgcompute['FILTRANGE']['value'] == True:
                                                        #         fout.write('PROCESS          FILTRANGE\n')

                                                        fout.write('PROCESS          INTERFERO\n')
                                                        
                                                        if jobifg.ifgcompute['Coherence']['value'] == True:
                                                                fout.write('PROCESS          COHERENCE\n')

                                                        fout.write('c                                              //\n')
                                                        fout.write(' c                                              //\n')
                                                        fout.write(' comment  ___the general io files___            //\n')
                                                        fout.write(' c                                              //\n')
                                                        fout.write('LOGFILE         %s                         // log file\n' % (log))
                                                        fout.write('M_RESFILE       %s  // parameter file\n' % (prefix_ifg+'.master.rslc.res'))
                                                        fout.write('S_RESFILE       %s                     // parameter file\n' % (prefix_ifg+'.slave.rslc.res'))
                                                        fout.write('I_RESFILE       %s               // parameter file\n' % (prefix_ifg+'.ifg'))
                                                        fout.write('HEIGHT              	0                	 // average WGS84 height\n')
                                                        fout.write('ORB_INTERP          	POLYFIT             	 // orbit interpolation method\n')
                                                        fout.write('ELLIPSOID           	WGS84               	 // WGS84, GRS80, BESSEL or define major and minor axis\n')
                                                        fout.write('c                             \n')
                                                        fout.write('DUMPBASELINE    50 50\n')
                                                        fout.write(' c                                              //\n')

                                                        # if jobifg.ifgcompute['FILTAZI']['value'] == True:
                                                        #         fout.write(' c                                              //\n')
                                                        #         fout.write(' comment ___AZIMUTH FILTERING___                //\n')
                                                        #         fout.write(' c                                              //\n')
                                                        #         fout.write('AF_BLOCKSIZE    %s                            // fftlength each column\n' % (jobifg.ifgcompute['AF_BLOCKSIZE']['value']))
                                                        #         fout.write('AF_OVERLAP      %s                              // hbs\n' % (jobifg.ifgcompute['AF_OVERLAP']['value']))
                                                        #         fout.write('c AF_HAMMING    %s                                  \n' % (jobifg.ifgcompute['AF_HAMMING']['value']))
                                                        #         fout.write('AF_OUT_MASTER   master_azifilt.rslc                  \n')
                                                        #         fout.write('AF_OUT_SLAVE    slave_azifilt.rslc                   \n')
                                                        #         fout.write('AF_OUT_FORMAT   %s                                 \n' % (jobifg.ifgcompute['AF_OUT_FORMAT']['value']))
                                                        #         fout.write('c                           \n')

                                                        # if jobifg.ifgcompute['FILTRANGE']['value'] == True:
                                                        #         fout.write(' c                                              //          \n')
                                                        #         fout.write(' comment   ___ ADAPTIVE RANGE FILTERING ___                 \n')
                                                        #         fout.write(' c                                                          \n')
                                                        #         fout.write('RF_METHOD       %s                                          \n' % (jobifg.ifgcompute['RF_METHOD']['value']))
                                                        #         fout.write('RF_FFTLENGTH    %s                               // 5 km    \n' % (jobifg.ifgcompute['RF_FFTLENGTH']['value']))
                                                        #         fout.write('RF_OVERLAP      %s                                          \n' % (jobifg.ifgcompute['RF_OVERLAP']['value']))
                                                        #         fout.write('RF_SLOPE        %s                                          \n' % (jobifg.ifgcompute['RF_SLOPE']['value']))
                                                        #         fout.write('RF_NLMEAN       %s                              // odd      \n' % (jobifg.ifgcompute['RF_NLMEAN']['value']))
                                                        #         fout.write('RF_THRESHOLD    %s                               // SNR     \n' % (jobifg.ifgcompute['RF_THRESHOLD']['value']))
                                                        #         fout.write('RF_HAMMING      %s                            // alpha      \n' % (jobifg.ifgcompute['RF_HAMMING']['value']))
                                                        #         fout.write('RF_OVERSAMPLE   %s                                          \n' % (jobifg.ifgcompute['RF_OVERSAMPLE']['value']))
                                                        #         fout.write('RF_WEIGHTCORR   %s                                          \n' % (jobifg.ifgcompute['RF_WEIGHTCORR']['value']))
                                                        #         fout.write('RF_OUT_MASTER   master_filtrg.rslc                          \n')
                                                        #         fout.write('RF_OUT_SLAVE    slave_filtrg.rslc                           \n')
                                                        #         fout.write('RF_OUT_FORMAT   %s                                          \n' % (jobifg.ifgcompute['RF_OUT_FORMAT']['value']))          

                                                        fout.write(' c                                              //          \n')
                                                        fout.write(' comment ___interferogram generation___                     \n')
                                                        fout.write(' c                                                          \n')
                                                        fout.write(' c\n')
                                                        fout.write('INT_OUT_CINT    %s.cint.raw                 // optional        \n' % (prefix_ifg))
                                                        fout.write('INT_MULTILOOK   1 1                            // line, pixel\n')

                                                        if jobifg.ifgcompute['Coherence']['value'] == True:

                                                                fout.write(' c                                              //          \n')
                                                                fout.write(' comment   ___ coherence ___                                \n')
                                                                fout.write(' c                                                          \n')
                                                                fout.write('COH_METHOD                refphase_only                     \n')
                                                                fout.write('COH_WINSIZE               %d %d                             \n' % (jobifg.ifgcompute['COH_WINSIZE_1']['value'],jobifg.ifgcompute['COH_WINSIZE_2']['value']))
                                                                fout.write('COH_MULTILOOK             %d %d                             \n' % (jobifg.mlran,jobifg.mlazi))
                                                                fout.write('COH_OUT_COH               %s.cc                              \n' % (prefix_ifg))

                                                        fout.write('STOP\n')
                                        
                                                dict_cmd['cmd%s' % (0)] = [ ['doris','config_card.tmp'],
                                                        'config_card.tmp']

                                                paraimage = doristools.readimagepara(prefix_ifg+'.master.rslc.res')

                                                if baselines['Master'][idx] == jobifg.refdate: 
                                                        cmd = "cpxsum %s %s %s %s cr4 -1 1" % (
                                                                prefix_ifg+'.cint.raw', 
                                                                '..'+os.sep+'single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+jobifg.refdate+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.cint.raw',
                                                                'tmp_cint3.raw',
                                                                paraimage['Number of pixels (non-multilooked)'])
                                                        dict_cmd['cmd%s' % (1)] = [ cmd.split(' '),
                                                                None]

                                                        cmd = "cpxsum %s %s %s %s cr4 1 1" % (
                                                                'tmp_cint3.raw',
                                                                '..'+os.sep+'single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+jobifg.refdate+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.cint.minrefdem.raw',
                                                                prefix_ifg+'.minrefdem.raw',
                                                                paraimage['Number of pixels (non-multilooked)'])
                                                        dict_cmd['cmd%s' % (2)] = [ cmd.split(' '),
                                                                None]

                                                elif baselines['Slave'][idx] == jobifg.refdate: 
                                                        cmd = "cpxsum %s %s %s %s cr4 -1 1" % (
                                                                '..'+os.sep+'single_diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+os.sep+jobifg.refdate+'_'+poli.lower()+'_'+baselines['Master'][idx]+'_'+poli.lower()+'.cint.raw',
                                                                prefix_ifg+'.cint.raw',
                                                                'tmp_cint3.raw',
                                                                paraimage['Number of pixels (non-multilooked)'])
                                                        dict_cmd['cmd%s' % (1)] = [ cmd.split(' '),
                                                                None]

                                                        cmd = "cpxsum %s %s %s %s cr4 -1 1" % (
                                                                'tmp_cint3.raw',
                                                                '..'+os.sep+'single_diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+os.sep+jobifg.refdate+'_'+poli.lower()+'_'+baselines['Master'][idx]+'_'+poli.lower()+'.cint.minrefdem.raw',
                                                                prefix_ifg+'.minrefdem.raw',
                                                                paraimage['Number of pixels (non-multilooked)'])
                                                        dict_cmd['cmd%s' % (2)] = [ cmd.split(' '),
                                                                None]

                                                else:
                                                        cmd = "cpxsum %s %s %s %s cr4 1 1" % (
                                                                prefix_ifg+'.cint.raw',
                                                                '..'+os.sep+'single_diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+os.sep+jobifg.refdate+'_'+poli.lower()+'_'+baselines['Master'][idx]+'_'+poli.lower()+'.cint.raw',
                                                                'tmp_cint.raw',
                                                                paraimage['Number of pixels (non-multilooked)'])
                                                        dict_cmd['cmd%s' % (1)] = [ cmd.split(' '),
                                                                None]
                                                        
                                                        cmd = "cpxsum %s %s %s %s cr4 -1 1" % (
                                                                'tmp_cint.raw',
                                                                '..'+os.sep+'single_diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+os.sep+jobifg.refdate+'_'+poli.lower()+'_'+baselines['Master'][idx]+'_'+poli.lower()+'.cint.minrefdem.raw',
                                                                'tmp_cint2.raw',
                                                                paraimage['Number of pixels (non-multilooked)'])
                                                        dict_cmd['cmd%s' % (2)] = [ cmd.split(' '),
                                                                None]

                                                        cmd = "cpxsum %s %s %s %s cr4 -1 1" % (
                                                                'tmp_cint2.raw',
                                                                '..'+os.sep+'single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+jobifg.refdate+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.cint.raw',
                                                                'tmp_cint3.raw',
                                                                paraimage['Number of pixels (non-multilooked)'])
                                                        dict_cmd['cmd%s' % (3)] = [ cmd.split(' '),
                                                                None]

                                                        cmd = "cpxsum %s %s %s %s cr4 1 1" % (
                                                                'tmp_cint3.raw',
                                                                '..'+os.sep+'single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+jobifg.refdate+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.cint.minrefdem.raw',
                                                                prefix_ifg+'.minrefdem.raw',
                                                                paraimage['Number of pixels (non-multilooked)'])
                                                        dict_cmd['cmd%s' % (4)] = [ cmd.split(' '),
                                                                None]

                                                # Multilook
                                                cmd = "cpxfiddle -w%d -fcr4 -qnormal -M%d/%d -ofloat %s > %s" % (
                                                        paraimage['Number of pixels (non-multilooked)'],
                                                        jobifg.mlran,
                                                        jobifg.mlazi,
                                                        prefix_ifg+'.minrefdem.raw',
                                                        prefix_ifg+'.diff')
                                                
                                                hh = len(dict_cmd.keys())
                                                dict_cmd['cmd%s' % (hh)] = [ cmd.split(' '),
                                                                None]

                                                doristools.wrappersubprocess(dict_cmd,jobifg.computercores,1,verbose,log)

                                                # Clean 
                                                listfi = glob.glob('*.raw') + glob.glob('*.rslc') + glob.glob('*.tmp')
                                                for fi in listfi:
                                                        os.remove(fi)

                                                ## Modification of the .ifg information file for consistency 
                                                with open(prefix_ifg+'.ifg','r') as fi: 
                                                        input = fi.readlines()

                                                for itt, li in enumerate(input):
                                                        if ('comp_refphase:' in li.split() and '0' in li.split()) or \
                                                                ('subtr_refphase:' in li.split() and '0' in li.split()) or \
                                                                ('comp_refdem:' in li.split() and '0' in li.split()) or \
                                                                ('subtr_refdem:' in li.split() and '0' in li.split()): 
                                                                input[itt] = li.replace('0','1')

                                                with open(prefix_ifg+'.ifg','w') as fi: 
                                                        for li in input: 
                                                                fi.write('%s' % (li))

                                                        fi.write('\n')
                                                        fi.write('\n')
                                                   
                                                        fi.write('*******************************************************************\n')
                                                        fi.write('*_Start_comp_refphase:\n')
                                                        fi.write('*******************************************************************\n')
                                                        fi.write('Degree_flat:	%s\n' % (jobifg.ifgcompute['FE_DEGREE']['value']))
                                                        fi.write('Estimated_coefficients_flatearth:\n')

                                                        co1 = 0
                                                        while co1 <= jobifg.ifgcompute['FE_DEGREE']['value']: 
                                                                co2 = 0
                                                                while co2 <= jobifg.ifgcompute['FE_DEGREE']['value']: 
                                                                        fi.write('1\t\t %s %s\n' % (co1,co2))
                                                                        co2 = co2 + 1
                                                                co1 = co1 + 1
                                                        
                                                        fi.write('\n')
                                                        fi.write('\n')
                                                        fi.write('Degree_h2ph:	%s\n' % (jobifg.ifgcompute['FE_DEGREE']['value']))
                                                        fi.write('Estimated_coefficients_h2ph:\n')

                                                        co1 = 0
                                                        while co1 <= jobifg.ifgcompute['FE_DEGREE']['value']: 
                                                                co2 = 0
                                                                while co2 <= jobifg.ifgcompute['FE_DEGREE']['value']: 
                                                                        fi.write('1\t\t %s %s\n' % (co1,co2))
                                                                        co2 = co2 + 1
                                                                co1 = co1 + 1

                                                        fi.write('*******************************************************************\n')
                                                        fi.write('* End_comp_refphase:_NORMAL\n')
                                                        fi.write('*******************************************************************\n')

                                                        fi.write('\n')
                                                        fi.write('   Current time: Sun Sep  8 09:50:09 2024\n')
                                                        fi.write('\n')
                                                        fi.write('\n')

                                                        fi.write('*******************************************************************\n')
                                                        fi.write('*_Start_subtr_refphase:\n')
                                                        fi.write('*******************************************************************\n')
                                                        fi.write('Method: 				        %s\n' % (jobifg.ifgcompute['FE_METHOD']['value']))
                                                        fi.write('Data_output_file: 			        %s.cint.minrefpha.raw\n' % (prefix_ifg))
                                                        fi.write('Data_output_format: 			        complex_real4\n')
                                                        fi.write('First_line (w.r.t. original_master): 	        %s\n' % (paraimage['First_line (w.r.t. original_image)']))
                                                        fi.write('Last_line (w.r.t. original_master): 	        %s\n' % (paraimage['Last_line (w.r.t. original_image)']))
                                                        fi.write('First_pixel (w.r.t. original_master): 	%s\n' % (paraimage['First_pixel (w.r.t. original_image)']))
                                                        fi.write('Last_pixel (w.r.t. original_master): 	        %s\n' % (paraimage['Last_pixel (w.r.t. original_image)']))
                                                        fi.write('Multilookfactor_azimuth_direction: 	        1\n')
                                                        fi.write('Multilookfactor_range_direction: 	        1\n')
                                                        fi.write('Number of lines (multilooked): 		%s\n' % (paraimage['Number of lines (non-multilooked)']))
                                                        fi.write('Number of pixels (multilooked): 	        %s\n' % (paraimage['Number of pixels (non-multilooked)']))
                                                        fi.write('*******************************************************************\n')
                                                        fi.write('* End_subtr_refphase:_NORMAL\n')
                                                        fi.write('*******************************************************************\n')

                                                        fi.write('\n')
                                                        fi.write('   Current time: Sun Sep  8 09:50:11 2024\n')
                                                        fi.write('\n')
                                                        fi.write('\n')

                                                        fi.write('*******************************************************************\n')
                                                        fi.write('*_Start_comp_refdem:\n')
                                                        fi.write('*******************************************************************\n')
                                                        fi.write('Include_flatearth:                 	        No\n')
                                                        fi.write('DEM source file:                      	%s\n' % (jobifg.nameDEM))
                                                        fi.write('Min. of input DEM:                    	1\n')
                                                        fi.write('Max. of input DEM:                    	5000\n')
                                                        fi.write('Data_output_file:                     	refdem_1l.raw\n')
                                                        fi.write('Data_output_format:                   	real4\n')
                                                        fi.write('First_line (w.r.t. original_master): 	        %s\n' % (paraimage['First_line (w.r.t. original_image)']))
                                                        fi.write('Last_line (w.r.t. original_master): 	        %s\n' % (paraimage['Last_line (w.r.t. original_image)']))
                                                        fi.write('First_pixel (w.r.t. original_master): 	%s\n' % (paraimage['First_pixel (w.r.t. original_image)']))
                                                        fi.write('Last_pixel (w.r.t. original_master): 	        %s\n' % (paraimage['Last_pixel (w.r.t. original_image)']))
                                                        fi.write('Multilookfactor_azimuth_direction: 	        1\n')
                                                        fi.write('Multilookfactor_range_direction: 	        1\n')
                                                        fi.write('Number of lines (multilooked): 		%s\n' % (paraimage['Number of lines (non-multilooked)']))
                                                        fi.write('Number of pixels (multilooked): 	        %s\n' % (paraimage['Number of pixels (non-multilooked)']))
                                                        fi.write('*******************************************************************\n')
                                                        fi.write('* End_comp_refdem:_NORMAL\n')
                                                        fi.write('*******************************************************************\n')

                                                        fi.write('\n')
                                                        fi.write('   Current time: Sun Sep  8 09:51:01 2024\n')
                                                        fi.write('\n')
                                                        fi.write('\n')

                                                        fi.write('*******************************************************************\n')
                                                        fi.write('*_Start_subtr_refdem:\n')
                                                        fi.write('*******************************************************************\n')
                                                        fi.write('Method:                               	NOT_USED\n')
                                                        fi.write('Additional_azimuth_shift:             	0\n')
                                                        fi.write('Additional_range_shift:               	0\n')
                                                        fi.write('Data_output_file:                     	%s\n' % (prefix_ifg+'.diff'))
                                                        fi.write('Data_output_format:                   	complex_real4\n')
                                                        fi.write('First_line (w.r.t. original_master): 	        %s\n' % (paraimage['First_line (w.r.t. original_image)']))
                                                        fi.write('Last_line (w.r.t. original_master): 	        %s\n' % (paraimage['Last_line (w.r.t. original_image)']))
                                                        fi.write('First_pixel (w.r.t. original_master): 	%s\n' % (paraimage['First_pixel (w.r.t. original_image)']))
                                                        fi.write('Last_pixel (w.r.t. original_master): 	        %s\n' % (paraimage['Last_pixel (w.r.t. original_image)']))
                                                        fi.write('Multilookfactor_azimuth_direction: 	        %s\n' % (jobifg.mlazi))
                                                        fi.write('Multilookfactor_range_direction: 	        %s\n' % (jobifg.mlran))
                                                        fi.write('Number of lines (multilooked): 		%s\n' % (int((paraimage['Last_line (w.r.t. original_image)'] - paraimage['First_line (w.r.t. original_image)'] + 1)/jobifg.mlazi)))
                                                        fi.write('Number of pixels (multilooked): 	        %s\n' % (int((paraimage['Last_pixel (w.r.t. original_image)'] - paraimage['First_pixel (w.r.t. original_image)'] + 1)/jobifg.mlran)))
                                                        fi.write('*******************************************************************\n')
                                                        fi.write('* End_subtr_refdem:_NORMAL\n')
                                                        fi.write('*******************************************************************\n')

                                                        fi.write('\n')
                                                        fi.write('   Current time: Sun Sep  8 09:51:01 2024\n')
                                                        fi.write('\n')
                                                        fi.write('\n')

                        idx = idx + 1
                
                paraimage = []
                listimage = []
                check_run = False
                for fi in glob.glob('*.diff'):
                        if (not os.path.isfile(fi+'.ras')) or modeforce == True:
                                tmp = doristools.readimagepara(fi.replace('.diff','.ifg'),mode = 'ifg') 
                                tmp['Number of pixels (non-multilooked)'] = int(tmp['Number of pixels (non-multilooked)']/jobifg.mlran)
                                paraimage.append(tmp)
                                listimage.append(fi)
                                check_run = True 

                if check_run == True:                                 
                        doristools.multilookimage(listimage,
                                'mixed',
                                paraimage,
                                '-fcr4',
                                1,
                                1,
                                colormap = constants.__file__.replace('constants.py','tools%scolormap%scmap_sar.csv' % (os.sep,os.sep)),
                                log = log,
                                verbose = verbose)

                paraimage = []
                listimage = []
                check_run = False
                for fi in glob.glob('*.cc'):
                        if (not os.path.isfile(fi+'.ras')) or modeforce == True:
                                tmp = doristools.readimagepara(fi.replace('.cc','.ifg'),mode = 'ifg') 
                                tmp['Number of pixels (non-multilooked)'] = int(tmp['Number of pixels (non-multilooked)']/jobifg.mlran)
                                paraimage.append(tmp)
                                listimage.append(fi)
                                check_run = True 

                if check_run == True:                                 
                        doristools.multilookimage(listimage,
                                'coh',
                                paraimage,
                                '-fr4',
                                1,
                                1,
                                colormap = constants.__file__.replace('constants.py','tools%scolormap%scmap_gray.csv' % (os.sep,os.sep)),
                                log = log,
                                verbose = verbose)

        else:
                raise ValueError(usermessage.errormsg(__name__,ifgcompute.__name__,__file__,__copyright__,
                        'The value of the workflow parameter is not correct.',log))
                                
        os.chdir(cur_dir)

        jobifg.ifgcompute['done']['value'] = True

        return jobifg 

################################################################################
## ifgfilter FUNCTION
################################################################################
def ifgfilter(jobifg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Filtre the interferograms

        The function applies filtering on the interferograms, from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()

        if not 'dorisifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,ifgfilter.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ifgfilter.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))

        if modeforce == None:
                modeforce = jobifg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ifgfilter.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobifg.log))

        if not jobifg.log == None: 
                log = os.path.abspath(jobifg.log)
        else: 
                log = 'log.out'

        if jobifg.ifgfilter['process']['value'] == True:  

                usermessage.openingmsg(__name__,ifgfilter.__name__,__file__,__copyright__,'ifgstack Step: ifgfilter',log,verbose)

                jobifg.check(verbose=False,mode='high')

                if jobifg.ifgcompute['done']['value'] == False:
                        raise ValueError(usermessage.errormsg(__name__,ifgfilter.__name__,__file__,__copyright__,
                                'The previous step (ifgcompute) is not done.',None))
        
                os.chdir(jobifg.workdirectory+os.sep+'diff')
                
                ## Create the input cards and the job
                baselines = dorisstack.readbaselinefile('..'+os.sep+'bperp_file.txt')
                
                ## Loop of processing
                idx = 0 
                h = 0
                dict_cmd = {}

                while idx <= len(baselines['Idx'])-1:
                        if baselines['Check'][idx] == 1:
                                for poli in jobifg.polarisation:
                                        
                                        prefix_ifg = baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()

                                        if (not os.path.isfile(prefix_ifg+'.ifg.filt')) or modeforce == True:

                                                if doristools.checkprocess(prefix_ifg+'.ifg','filtphase') == True: 
                                                        dict_tmp = dict()
                                                        dict_tmp['cmd%s' % (0)] = [ ['doris.rmstep.sh','filtphase','%s' % (prefix_ifg+'.ifg')],
                                                                None]                                         
                                                        doristools.wrappersubprocess(dict_tmp,jobifg.computercores,jobifg.computerworkers,verbose,log)
                        
                                                # Input card creation
                                                with open('config_card_%s.tmp' % (h),'w') as fout: 

                                                        fout.write('cc **********************************************************************\n')
                                                        fout.write('c ***  Doris \inputfile *****\n')
                                                        fout.write('c **********************************************************************\n')
                                                        fout.write(' c\n')
                                                        fout.write(' c\n')
                                                        fout.write(' comment  ___general options___\n')
                                                        fout.write(' c\n')
                                                        fout.write('c SCREEN          debug                           // level of output to standard out\n')
                                                        fout.write('SCREEN          info                           // level of output to standard out\n')
                                                        fout.write('MEMORY          %s                             // MB\n' %(jobifg.computerRAM))
                                                        fout.write('BEEP            error                            // level of beeping\n')
                                                        fout.write('OVERWRITE                                       // overwrite existing files\n')
                                                        fout.write('BATCH                                           // non-interactive\n')
                                                        fout.write('c LISTINPUT OFF                                 // prevents copy of this file to log\n')
                                                        fout.write('c\n')

                                                        fout.write('PROCESS          filtphase\n')

                                                        fout.write('c                                              //\n')
                                                        fout.write(' c                                              //\n')
                                                        fout.write(' comment  ___the general io files___            //\n')
                                                        fout.write(' c                                              //\n')
                                                        fout.write('LOGFILE         %s                          // log file\n' % (log))
                                                        fout.write('M_RESFILE       %s                          // parameter file\n' % (prefix_ifg+'.master.rslc.res'))
                                                        fout.write('S_RESFILE       %s                          // parameter file\n' % (prefix_ifg+'.slave.rslc.res'))
                                                        fout.write('I_RESFILE       %s                          // parameter file\n' % (prefix_ifg+'.ifg'))
                                                        fout.write(' c                                              //\n')
                                                        fout.write(' c                                              //\n')
                                                        fout.write(' comment PHASEFILT\n')
                                                        fout.write(' c\n')
                                                        fout.write('PF_METHOD      %s\n' %( jobifg.ifgfilter['PF_METHOD']['value']))
                                                        fout.write('PF_OUT_FILE    %s\n' % (prefix_ifg+'.diff.filt'))
                                                        fout.write('PF_ALPHA       %s\n' %( jobifg.ifgfilter['PF_ALPHA']['value']))
                                                        fout.write('PF_BLOCKSIZE   %s\n' %( jobifg.ifgfilter['PF_BLOCKSIZE']['value']))
                                                        fout.write('PF_OVERLAP     %s\n' %( jobifg.ifgfilter['PF_OVERLAP']['value']))
                                                        fout.write('STOP\n')

                                                dict_cmd['cmd%s' % (h)] = [ ['doris','config_card_%s.tmp' % (h)],
                                                                'config_card_%s.tmp' % (h)]
                                             
                                                h = h + 1

                        idx = idx + 1

                if h > 0: 
                # Run Doris
                        doristools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg.computerworkers,verbose,log)
                        for keyi in list(dict_cmd.keys()):
                                if os.path.isfile(dict_cmd[keyi][1]):
                                        os.remove(dict_cmd[keyi][1])

                ## Multilooking 
                paraimage = []
                listimage = []
                check_run = False
                for fi in glob.glob('*.diff.filt'):
                        if (not os.path.isfile(fi+'.ras')) or modeforce == True:
                                tmp = doristools.readimagepara(fi.replace('.diff.filt','.ifg'),mode = 'ifg') 
                                tmp['Number of pixels (non-multilooked)'] = int(tmp['Number of pixels (non-multilooked)']/jobifg.mlran)
                                paraimage.append(tmp)
                                listimage.append(fi)
                                check_run = True 

                if check_run == True:                                 
                        doristools.multilookimage(listimage,
                                'mixed',
                                paraimage,
                                '-fcr4',
                                1,
                                1,
                                colormap = constants.__file__.replace('constants.py','tools%scolormap%scmap_sar.csv' % (os.sep,os.sep)),
                                log = log,
                                verbose = verbose)
                
                os.chdir(cur_dir)

        else:
                usermessage.warningmsg(__name__,ifgfilter.__name__,__file__,'The processing is not activated.',log,verbose)

        jobifg.ifgfilter['done']['value'] = True

        os.chdir(cur_dir)
        return jobifg

################################################################################
## ifgunwrapping FUNCTION
################################################################################
def ifgunwrapping(jobifg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Unwrap the interferograms

        The function will unwrap the interferograms, from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class

        Notes: 
                If not similar, the ``refdat`` attributes will be modified.
        
        """
        cur_dir = os.getcwd()

        if not 'dorisifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,ifgunwrapping.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ifgunwrapping.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))

        if modeforce == None:
                modeforce = jobifg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ifgunwrapping.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobifg.log))

        if not jobifg.log == None: 
                log = os.path.abspath(jobifg.log)
        else: 
                log = 'log.out'

        if jobifg.ifgunwrapping['process']['value'] == True:  

                usermessage.openingmsg(__name__,ifgunwrapping.__name__,__file__,__copyright__,'ifgstack Step: ifgunwrapping',log,verbose)

                jobifg.check(verbose=False,mode='high')

                if jobifg.ifgfilter['process']['value']: 
                        if jobifg.ifgfilter['done']['value'] == False:
                                raise ValueError(usermessage.errormsg(__name__,ifgunwrapping.__name__,__file__,__copyright__,
                                        'The previous step (ifgfilter) is not done.',None))
                else: 
                        if jobifg.ifgcompute['done']['value'] == False:
                                raise ValueError(usermessage.errormsg(__name__,ifgunwrapping.__name__,__file__,__copyright__,
                                        'The previous step (ifgcompute) is not done.',None))

                if not os.path.isdir(jobifg.workdirectory+os.sep+'unw'):
                        os.mkdir(jobifg.workdirectory+os.sep+'unw')
                os.chdir(jobifg.workdirectory+os.sep+'unw')
                
                ## Create the input cards and the job
                baselines = dorisstack.readbaselinefile('..'+os.sep+'bperp_file.txt')
                
                ## Loop of processing
                idx = 0 
                h = 0
                dict_cmd = {}

                while idx <= len(baselines['Idx'])-1:
                        if baselines['Check'][idx] == 1:
                                for poli in jobifg.polarisation:
                                        
                                        prefix_ifg = baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()

                                        if (not os.path.isfile(prefix_ifg+'.unw')) or modeforce == True:

                                                usermessage.warningmsg(__name__,ifgunwrapping.__name__,__file__,'The interferogram .res file will not modified because Doris is not used here.',log,verbose)

                                                # Input card creation
                                                with open('snaphu_%s.conf' % (h),'w') as fout: 

                                                        paraimage = doristools.readimagepara('..'+os.sep+'diff'+os.sep+prefix_ifg+'.ifg',mode = 'ifg') 
                                                        nbl = int(paraimage['Number of lines (non-multilooked)']/jobifg.mlazi)
                                                        nbc = int(paraimage['Number of pixels (non-multilooked)']/jobifg.mlran)

                                                        fout.write('# snaphu configuration file\n\n')

                                                        if jobifg.ifgfilter['process']['value']: 
                                                                fileincpx = '..'+os.sep+'diff'+os.sep+prefix_ifg+'.diff.filt'
                                                        else: 
                                                                fileincpx = '..'+os.sep+'diff'+os.sep+prefix_ifg+'.diff'

                                                        fileinfloat = fileincpx.split(os.sep)[-1] + '.float'

                                                        # fout.write('INFILE	%s \n\n' % (fileinfloat))
                                                        
                                                        # fout.write('LINELENGTH	        %d \n\n' % (int(paraimage['Number of lines (non-multilooked)']/jobifg.mlazi)))

                                                        fout.write('OUTFILE	        %s \n\n' % (prefix_ifg+'.unw'))

                                                        if jobifg.ifgunwrapping['usecohweight']['value'] == True: 
                                                                fout.write('CORRFILE	        %s \n\n' % (prefix_ifg+'.cc'))

                                                                usermessage.warningmsg(__name__,ifgunwrapping.__name__,__file__,'The coherence %s will be mofified in order to avoid NaN values.' % (prefix_ifg+'.cc'),log,verbose)
                                                                
                                                                with open('..'+os.sep+'diff'+os.sep+prefix_ifg+'.cc', "rb") as fcoh: 
                                                                      coh = np.reshape(np.fromfile(fcoh, np.float32),(nbl,nbc))
                                                                coh[coh==np.nan] = 0.00001
                                                                coh.tofile(prefix_ifg+'.cc')

                                                        else: 
                                                                fout.write('#CORRFILE	        \n\n')

                                                        ## Prepare the ifg in float (on-the-fly)
                                                        ifgdata = np.angle(np.reshape(np.fromfile(fileincpx, np.complex64),(nbl,nbc)))
                                                        ifgdata.tofile(fileinfloat)

                                                        fout.write('#LOGFILE            snaph.logfile\n\n')

                                                        fout.write('STATCOSTMODE	%s \n\n' % (jobifg.ifgunwrapping['mode']['value']))
                                                        
                                                        fout.write('INITMETHOD	        %s \n\n' % (jobifg.ifgunwrapping['init']['value']))
                                                        fout.write('VERBOSE	        TRUE\n\n')

                                                        fout.write('INFILEFORMAT	FLOAT_DATA\n\n')
                                                        fout.write('OUTFILEFORMAT	FLOAT_DATA\n\n')
                                                        fout.write('CORRFILEFORMAT	FLOAT_DATA\n\n')
                                                        # fout.write('ORBITRADIUS		7153000.0\n\n')
                                                        # fout.write('EARTHRADIUS		6378000.0\n\n')
                                                        # fout.write('TRANSMITMODE	REPEATPASS\n\n')

                                                        if jobifg.ifgunwrapping['mode']['value'] == 'DEFO':
                                                                fout.write('DEFOAZDZFACTOR	1.0\n\n')
                                                                fout.write('DEFOTHRESHFACTOR 1.2\n\n')
                                                                fout.write('DEFOMAX_CYCLE	1.2\n\n')
                                                                fout.write('DEFOMAX_RAD	7.5398\n\n')
                                                                fout.write('DEFOCONST	0.9\n\n')

                                                        if jobifg.ifgunwrapping['tiles']['value'] == True:
                                                                fout.write('NTILEROW		%s \n\n' % (jobifg.ifgunwrapping['NTILEROW']['value']))
                                                                fout.write('NTILECOL		%s \n\n' % (jobifg.ifgunwrapping['NTILECOL']['value']))
                                                                fout.write('ROWOVRLP		%s \n\n' % (jobifg.ifgunwrapping['ROWOVRLP']['value']))
                                                                fout.write('COLOVRLP		%s \n\n' % (jobifg.ifgunwrapping['COLOVRLP']['value']))
                                                                fout.write('NPROC		%s \n\n' % (jobifg.computercores))

                                                        if jobifg.ifgunwrapping['CONNmode']['value'] == True: 
                                                                fout.write('CONNCOMPFILE            %s \n\n' % (prefix_ifg+'unw.conn'))

                                                        fout.write('# End of snaphu configuration file\n\n')

                                                dict_cmd['cmd%s' % (h)] = [ ['snaphu',fileinfloat,str(int(paraimage['Number of pixels (non-multilooked)']/jobifg.mlazi)),'-f','snaphu_%s.conf' % (h)],
                                                                'snaphu_%s.conf' % (h)]     

                                                h = h + 1

                        idx = idx + 1

                if h > 0: 
                # Run Doris
                        doristools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg.computerworkers,verbose,log)
                        for keyi in list(dict_cmd.keys()):
                                if os.path.isfile(dict_cmd[keyi][1]):
                                        os.remove(dict_cmd[keyi][1])

                for li in glob.glob('*.cc'): 
                        os.remove(li)
                for li in glob.glob('*.float'): 
                        os.remove(li)

        else:
                usermessage.warningmsg(__name__,ifgunwrapping.__name__,__file__,'The processing is not activated.',log,verbose)
        
        
        jobifg.ifgunwrapping['done']['value'] = True
        os.chdir(cur_dir)
        return jobifg

################################################################################
## ifggeocoding FUNCTION
################################################################################
def ifggeocoding(jobifg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Geocode the interferograms

        The function will geocode the interferograms, from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class

        """
        cur_dir = os.getcwd()

        if not 'dorisifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,ifggeocoding.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ifggeocoding.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))

        if modeforce == None:
                modeforce = jobifg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ifggeocoding.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobifg.log))

        if not jobifg.log == None: 
                log = os.path.abspath(jobifg.log)
        else: 
                log = 'log.out'

        if jobifg.ifggeocoding['process']['value'] == True:  

                usermessage.openingmsg(__name__,ifggeocoding.__name__,__file__,__copyright__,'ifgstack Step: ifggeocoding',log,verbose)

                jobifg.check(verbose=False,mode='high')

             
                if jobifg.ifgcompute['done']['value'] == False:
                        raise ValueError(usermessage.errormsg(__name__,ifggeocoding.__name__,__file__,__copyright__,
                                        'The previous step (ifgcompute) is not done.',None))

                if not os.path.isdir(jobifg.workdirectory+os.sep+'geo'):
                        os.mkdir(jobifg.workdirectory+os.sep+'geo')
                os.chdir(jobifg.workdirectory+os.sep+'geo')
                
                ## Create the input cards and the job
                baselines = dorisstack.readbaselinefile('..'+os.sep+'bperp_file_Single.txt')

                idx = 0
                while baselines['Master'][idx] == baselines['Slave'][idx]:
                        idx = idx + 1
                
                shutil.copy('..'+os.sep+'single_diff'+os.sep+baselines['Slave'][idx]+'_'+jobifg.polarisation[0].lower()+os.sep+'dem_radar.raw','dem_radar.raw')
                shutil.copy('..'+os.sep+'single_diff'+os.sep+baselines['Slave'][idx]+'_'+jobifg.polarisation[0].lower()+os.sep+jobifg.refdate+'.'+jobifg.polarisation[0].lower()+'.rslc.res',jobifg.refdate+'.'+jobifg.polarisation[0].lower()+'.rslc.res')
                shutil.copy('..'+os.sep+'single_diff'+os.sep+baselines['Slave'][idx]+'_'+jobifg.polarisation[0].lower()+os.sep+baselines['Slave'][idx]+'.'+jobifg.polarisation[0].lower()+'.rslc.res',baselines['Slave'][idx]+'.'+jobifg.polarisation[0].lower()+'.rslc.res')

                paraimage = doristools.readimagepara(jobifg.refdate+'.'+jobifg.polarisation[0].lower()+'.rslc.res') 

                with open('..'+os.sep+'single_diff'+os.sep+baselines['Slave'][idx]+'_'+jobifg.polarisation[0].lower()+os.sep+jobifg.refdate+'_'+jobifg.polarisation[0].lower()+'_'+baselines['Slave'][idx]+'_'+jobifg.polarisation[0].lower()+'.ifg','r') as fi: 
                        input = fi.readlines()
                output = []
                for li in input:
                        if ('slant2h:' in li.split()) and ('0' in li.split()):
                                output.append(li.replace('0','1'))
                        else: 
                                output.append(li)
                with open(jobifg.refdate+'_'+jobifg.polarisation[0].lower()+'_'+baselines['Slave'][idx]+'_'+jobifg.polarisation[0].lower()+'.ifg','w') as fi: 
                        for li in output:
                                fi.write('%s' % (li))

                ## Multilooking at the END
                with open(jobifg.refdate+'_'+jobifg.polarisation[0].lower()+'_'+baselines['Slave'][idx]+'_'+jobifg.polarisation[0].lower()+'.ifg','a') as fout: 
                        fout.write(' \n')
                        fout.write('*****************************************************\n')
                        fout.write('*_Start_slant2h:\n')
                        fout.write('*****************************************************\n')
                        fout.write('Method:                                 schwabisch\n')
                        fout.write('Data_output_file:                       dem_radar.raw\n')
                        fout.write('Data_output_format:                     real4\n')
                        fout.write('First_line (w.r.t. original_master):   '+str(paraimage['First_line (w.r.t. original_image)'])+'\n')
                        fout.write('Last_line (w.r.t. original_master):    '+str(paraimage['Last_line (w.r.t. original_image)'])+'\n')
                        fout.write('First_pixel (w.r.t. original_master):  '+str(paraimage['First_pixel (w.r.t. original_image)'])+'\n')
                        fout.write('Last_pixel (w.r.t. original_master):   '+str(paraimage['Last_pixel (w.r.t. original_image)'])+'\n')
                        fout.write('Multilookfactor_azimuth_direction:      1\n')
                        fout.write('Multilookfactor_range_direction:        1\n')
                        fout.write('Ellipsoid (name,a,b):                   WGS84 6.37814e+06 6.35675e+06\n')
                        fout.write('*****************************************************\n')
                        fout.write('* End_slant2h:_NORMAL\n')
                        fout.write('*****************************************************\n')    

                # Input card creation
                with open('config_card.tmp','w') as fout: 

                        fout.write('cc **********************************************************************\n')
                        fout.write('c ***  Doris \inputfile *****\n')
                        fout.write('c **********************************************************************\n')
                        fout.write(' c\n')
                        fout.write(' c\n')
                        fout.write(' comment  ___general options___\n')
                        fout.write(' c\n')
                        fout.write('c SCREEN          debug                           // level of output to standard out\n')
                        fout.write('SCREEN          info                           // level of output to standard out\n')
                        fout.write('MEMORY          %s                             // MB\n' %(jobifg.computerRAM))
                        fout.write('BEEP            error                            // level of beeping\n')
                        fout.write('OVERWRITE                                       // overwrite existing files\n')
                        fout.write('BATCH                                           // non-interactive\n')
                        fout.write('c LISTINPUT OFF                                 // prevents copy of this file to log\n')
                        fout.write('c\n')

                        fout.write('PROCESS          GEOCODE\n')

                        fout.write('c                                              //\n')
                        fout.write(' c                                              //\n')
                        fout.write(' comment  ___the general io files___            //\n')
                        fout.write(' c                                              //\n')
                        fout.write('LOGFILE         %s                          // log file\n' % (log))
                        fout.write('M_RESFILE       %s                          // parameter file\n' % (jobifg.refdate+'.'+jobifg.polarisation[0].lower()+'.rslc.res'))
                        fout.write('S_RESFILE       %s                          // parameter file\n' % (baselines['Slave'][idx]+'.'+jobifg.polarisation[0].lower()+'.rslc.res'))
                        fout.write('I_RESFILE       %s                          // parameter file\n' % (jobifg.refdate+'_'+jobifg.polarisation[0].lower()+'_'+baselines['Slave'][idx]+'_'+jobifg.polarisation[0].lower()+'.ifg'))
                        fout.write(' c                                              //\n')
                        fout.write(' c\n')
                        fout.write('HEIGHT              	0.0                 	 // average WGS84 height\n')
                        fout.write('ORB_INTERP          	POLYFIT             	 // orbit interpolation method\n')
                        fout.write('ELLIPSOID           	WGS84               	 // WGS84, GRS80, BESSEL or define major and minor axis\n')
                        fout.write('c                             \n')
                        fout.write('GEO_OUT_LAM         	lon_full.raw             	 // longitude coordinates\n')
                        fout.write('GEO_OUT_PHI         	lat_full.raw             	 // latitude coordinates\n')
                        fout.write('STOP                          \n')
                        fout.close()
                
                dict_cmd = {}
                dict_cmd['cmd%s' % (0)] = [ ['doris','config_card.tmp'],
                                'config_card.tmp']
                
                # Run Doris
                doristools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg.computerworkers,verbose,log)
                for keyi in list(dict_cmd.keys()):
                        if os.path.isfile(dict_cmd[keyi][1]):
                                os.remove(dict_cmd[keyi][1])

                ## Multilooking 
                paraimage = []
                listimage = []

                paraimage.append(doristools.readimagepara(jobifg.refdate+'.'+jobifg.polarisation[0].lower()+'.rslc.res') )
                paraimage.append(doristools.readimagepara(jobifg.refdate+'.'+jobifg.polarisation[0].lower()+'.rslc.res') )
                paraimage.append(doristools.readimagepara(jobifg.refdate+'.'+jobifg.polarisation[0].lower()+'.rslc.res') )

                listimage = ['lon_full.raw','lat_full.raw','dem_radar.raw']
                outimage = ['lon.raw','lat.raw','dem_radar_ml.raw']
                doristools.multilookimage(listimage,
                        'normal',
                        paraimage,
                        '-fr4',
                        jobifg.mlran,
                        jobifg.mlazi,
                        log = log,
                        fout=outimage,
                        verbose = verbose)

                ## Geocoding 
                if not os.path.isdir(jobifg.workdirectory+os.sep+'geotiff'):
                        os.mkdir(jobifg.workdirectory+os.sep+'geotiff')
                os.chdir(jobifg.workdirectory+os.sep+'geotiff')
                
                ## Create the input cards and the job
                baselines = dorisstack.readbaselinefile('..'+os.sep+'bperp_file.txt')
                
                ## Loop of processing
                idx = 0 
                h = 0
                dict_cmd = {}

                # Generation of the file list S1_IW_20240223_VV_20240306_VV.diff.geo.pha.tif
                usermessage.ezprint('Generation of the file list',jobifg.log,verbose)
                list_file = []
                list_cc = []
                list_outfile = []

                while idx <= len(baselines['Idx'])-1:
                        if baselines['Check'][idx] == 1:
                                for poli in jobifg.polarisation:
                                        outname = '%s_%s_%s_%s_%s_%s' % (jobifg.satellite,jobifg.satmode,baselines['Master'][idx],poli.upper(),baselines['Slave'][idx],poli.upper())
                                        prefix_ifg = baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()

                                        if jobifg.ifgunwrapping['process']['value'] == True:
                                                if (not os.path.isfile(outname+'.unw.geo.tif')) or modeforce == True:
                                                        list_file.append('..'+os.sep+'unw'+os.sep+prefix_ifg+'.unw')
                                                        list_cc.append('..'+os.sep+'diff'+os.sep+prefix_ifg+'.cc')
                                                        list_outfile.append(outname+'.unw.geo.tif')

                                        if (not os.path.isfile(outname+'.diff.geo.pha.tif')) or modeforce == True:
                                                list_file.append('..'+os.sep+'diff'+os.sep+prefix_ifg+'.diff')
                                                list_cc.append('..'+os.sep+'diff'+os.sep+prefix_ifg+'.cc')
                                                list_outfile.append(outname+'.diff.geo.pha.tif')

                                        if jobifg.ifgfilter['process']['value'] == True:
                                                if (not os.path.isfile(outname+'.diff.filt.geo.pha.tif')) or modeforce == True:
                                                        list_file.append('..'+os.sep+'diff'+os.sep+prefix_ifg+'.diff.filt')
                                                        list_cc.append('..'+os.sep+'diff'+os.sep+prefix_ifg+'.cc')
                                                        list_outfile.append(outname+'.diff.filt.geo.pha.tif')

                                        if jobifg.ifgcompute['Coherence']['value'] == True:
                                                if (not os.path.isfile(outname+'.cc.geo.tif')) or modeforce == True:
                                                        list_file.append('..'+os.sep+'diff'+os.sep+prefix_ifg+'.cc')
                                                        list_cc.append(None)
                                                        list_outfile.append(outname+'.cc.geo.tif')

                        idx = idx + 1     
                                
                ## Read the DEM information
                paradem = doristools.readDEMpara(jobifg.pathDEM+os.sep+jobifg.nameDEM)
                deltaLon = np.abs(paradem['deltalon'])
                deltaLat = np.abs(paradem['deltalat'])

                latin = '%s' % (jobifg.workdirectory+os.sep+'geo'+os.sep+'lat.raw')
                lonin = '%s' % (jobifg.workdirectory+os.sep+'geo'+os.sep+'lon.raw')
                demin = '%s' % (jobifg.workdirectory+os.sep+'geo'+os.sep+'dem_radar_ml.raw')
                
                ## Read the DEM information
                if jobifg.ifggeocoding['maskWaterBody']['value']:
                        if 'masked' in jobifg.nameDEM: 
                                usermessage.warningmsg(__name__,ifggeocoding.__name__,__file__,'The radarcoded DEM is already masked.',log,verbose)
                                demgeofile = None
                        else:
                                listtmp = glob.glob(jobifg.pathDEM+os.sep+jobifg.nameDEM.split('.')[0]+'*masked*.r4')
                                if listtmp == None:
                                        usermessage.warningmsg(__name__,ifggeocoding.__name__,__file__,'No masked DEM found.',log,verbose)
                                        demgeofile = None
                                else:
                                        demgeofile = listtmp[0]

                poly = loads(jobifg.roi)

                paraimage = doristools.readimagepara('..'+os.sep+'diff'+os.sep+baselines['Master'][0]+'_'+poli.lower()+'_'+baselines['Slave'][0]+'_'+poli.lower()+'.ifg',mode = 'ifg') 

                for fi, fout, cc in zip(list_file,list_outfile,list_cc):

                        nbl = int(paraimage['Number of lines (non-multilooked)']/jobifg.mlazi)
                        nbc = int(paraimage['Number of pixels (non-multilooked)']/jobifg.mlran)

                        if jobifg.ifggeocoding['maskifg']['value'] == False:
                                cc = None

                        geocoding.rdr2geotiff(fi, 
                                latin,
                                lonin, 
                                fout, 
                                deltaLon/jobifg.ifggeocoding['overlon']['value'], 
                                deltaLat/jobifg.ifggeocoding['overlat']['value'],  
                                processor = 'doris',
                                ROIpoly = poly, 
                                uchar = jobifg.ifggeocoding['uchargeotiff']['value'], 
                                coherencefile = cc,
                                demradarfile = demin,
                                demgeofile = demgeofile, 
                                coherenceth = 0.2,
                                nblineinput = nbl,
                                nbcolinput = nbc,
                                verbose = verbose, 
                                log = log,
                                )

        else:
                usermessage.warningmsg(__name__,ifggeocoding.__name__,__file__,'The processing is not activated.',log,verbose)

        os.chdir(cur_dir)
        jobifg.ifggeocoding['done']['value'] = True
        
        return jobifg

################################################################################
## finalstack FUNCTION
################################################################################
def finalstack(jobifg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Finalise the interferometric stack

        The function will finalise the stack, from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()

        if not 'dorisifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,finalstack.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,finalstack.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))

        if modeforce == None:
                modeforce = jobifg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,finalstack.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobifg.log))

        if not jobifg.log == None: 
                log = os.path.abspath(jobifg.log)
        else: 
                log = 'log.out'

        usermessage.openingmsg(__name__,ifggeocoding.__name__,__file__,__copyright__,'ifgstack Step: finalstack',log,verbose)

        jobifg.check(verbose=False,mode='high')

        if jobifg.ifgcompute['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,finalstack.__name__,__file__,__copyright__,
                                'The previous step (ifgcompute) is not done.',None))

        os.chdir(jobifg.workdirectory)

        ## For StaMPS in PS mode
        if 'StaMPS' in jobifg.modestack: 
                usermessage.ezprint('Preparation of the files for StaMPS:',log,verbose)
     
                # Creation of the directory 
                usermessage.ezprint('\tCreate the directories:',log,verbose)
                for poli in jobifg.polarisation:
                        if not os.path.isdir(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate):
                                os.makedirs(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate, exist_ok=True)

                baselines = dorisstack.readbaselinefile(jobifg.workdirectory+os.sep+'bperp_file_Single.txt')
        
                idx = 0 
                while idx <= len(baselines['Idx'])-1:
                        if baselines['Check'][idx] == 1:
                                for poli in jobifg.polarisation:
                                        if not os.path.isdir(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+baselines['Slave'][idx]):
                                                os.mkdir(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+baselines['Slave'][idx])
                        idx = idx + 1
                
                usermessage.ezprint('\t\tdone',log,verbose)

                # Copy the master files 
                usermessage.ezprint('\tCopy the master files:',log,verbose)
                for poli in jobifg.polarisation:
                        if doristools.checkprocess('single_diff'+os.sep+baselines['Slave'][0]+'_'+poli.lower()+os.sep+jobifg.refdate+'.'+poli.lower()+'.rslc.res','oversample') == True: 
                                masterout = jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+jobifg.refdate+'_crop_ovs.slc'
                        else: 
                                masterout = jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+jobifg.refdate+'_crop.slc'

                        shutil.copy('single_diff'+os.sep+baselines['Slave'][0]+'_'+poli.lower()+os.sep+jobifg.refdate+'.'+poli.lower()+'.rslc',
                                masterout)
                        
                        # Not needed to modify the files name
                        shutil.copy('single_diff'+os.sep+baselines['Slave'][0]+'_'+poli.lower()+os.sep+jobifg.refdate+'.'+poli.lower()+'.rslc.res',
                                jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+'master.res')

                usermessage.ezprint('\t\tdone',log,verbose)        

                # Copy the slave files 
                usermessage.ezprint('\tCopy the slave files:',log,verbose)
        
                idx = 0 
                while idx <= len(baselines['Idx'])-1:
                        if baselines['Check'][idx] == 1:
                                for poli in jobifg.polarisation:

                                        paraimage = doristools.readimagepara('single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+baselines['Slave'][idx]+'.'+poli.lower()+'.rslc.res')
                                        width = int(paraimage['Last_pixel (w.r.t. original_image)'] - paraimage['First_pixel (w.r.t. original_image)'] + 1)
                                        if paraimage['Data_output_format'] == 'complex_short': 
                                                cmd = 'cpxfiddle -w %s -fci2 -ofloat -qnormal %s > %s' % (width,'single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+baselines['Slave'][idx]+'.'+poli.lower()+'.rslc', 
                                                jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+baselines['Slave'][idx]+os.sep+'slave_res.slc')
                                                os.system(cmd)
                                        else:
                                                shutil.copy('single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+baselines['Slave'][idx]+'.'+poli.lower()+'.rslc',
                                                        jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+baselines['Slave'][idx]+os.sep+'slave_res.slc')
                                        
                                        shutil.copy('single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+baselines['Slave'][idx]+'.'+poli.lower()+'.rslc.res',
                                                jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+baselines['Slave'][idx]+os.sep+'slave_res.slc.res')

                                        # In diff for the filtered images
                                        if jobifg.modestack == 'StaMPS_SBAS':
                                                usermessage.warningmsg(__name__,__name__,__file__,'The single-master interferograms will be copied (not filtered) and should not be used.',log,verbose)
                                                infile = 'single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+jobifg.refdate+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.cint.minrefdem.raw'
                                                infileres = 'single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+jobifg.refdate+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.ifg'
                                        else: 
                                                if jobifg.ifgfilter['process']['value'] == True: 
                                                        infile = 'diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.diff.filt'
                                                else: 
                                                        infile = 'diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.diff'

                                                infileres = 'diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.ifg'

                                        shutil.copy(infile,
                                                jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+baselines['Slave'][idx]+os.sep+'cint.minrefdem.raw')
                                        
                                        shutil.copy(infileres,
                                                jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+baselines['Slave'][idx]+os.sep+'interferogram.out')
                        
                        idx = idx + 1

                usermessage.ezprint('\t\tdone',log,verbose) 

                # Copy the supplementary files 
                usermessage.ezprint('\tCopy the supplementary files:',log,verbose)
                for poli in jobifg.polarisation:
                        shutil.copy('geo'+os.sep+'lat_full.raw',
                                jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+'lat.raw')
                        shutil.copy('geo'+os.sep+'lon_full.raw',
                                jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+'lon.raw')
                        shutil.copy('geo'+os.sep+'dem_radar.raw',
                                jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+'dem_radar_i.raw')

                        paradem = doristools.readDEMpara('single_diff'+os.sep+baselines['Slave'][0]+'_'+poli.lower()+os.sep+jobifg.nameDEM)

                        with open(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+'dem.dorisin','w') as fout: 
                                fout.write(' c                                              //          \n')
                                fout.write(' comment   ___ comprefdem ___                               \n')
                                fout.write(' c                                                          \n')
                                fout.write('CRD_INCLUDE_FE       OFF                                    \n')
                                fout.write('CRD_IN_FORMAT        real4                                  \n')
                                fout.write('CRD_IN_DEM      %s                                          \n' % (jobifg.nameDEM))
                                fout.write('CRD_IN_SIZE          %d %d                                  // rows cols\n' % (paradem['lines'],paradem['samples']))
                                fout.write('CRD_IN_DELTA    %f %f                                       // in degrees       \n'  % (np.abs(paradem['deltalat']),np.abs(paradem['deltalon'])))
                                fout.write('CRD_IN_UL       %f %f                                       // lat and lon of upper left\n'% (paradem['lat'],paradem['lon']))
                                fout.write('CRD_IN_NODATA   %d                                          \n' % (paradem['nodata']))
                                fout.write('CRD_OUT_FILE    refdem_1l.raw                               // synthetic amplitude\n')
                                fout.write('CRD_OUT_DEM_LP  dem_radar_i.raw                               \n')
                        
                usermessage.ezprint('\t\tdone',log,verbose) 

                # Compute the heading of the master
                usermessage.ezprint('\tExtract the heading of the master:',log,verbose)
                if jobifg.satellite == 'S1': 
                        with open(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+jobifg.polarisation[0].lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+'master.res','r') as fi: 
                                for li in fi:
                                        if 'Scene_center_heading:' in  li: 
                                                heading = li.split()[-1]
                        for poli in jobifg.polarisation: 
                                with open(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+jobifg.refdate+'.slc.rsc','w') as fout:
                                        fout.write('HEADING %s' % (heading))

                usermessage.ezprint('\t\tdone',log,verbose) 

                # Regeneration of the log of the coarse correlation
                usermessage.ezprint('\tRegeneration of the log of the coarse correlation:',log,verbose)

                idx = 0 
                while idx <= len(baselines['Idx'])-1:
                        if baselines['Check'][idx] == 1:
                                for poli in jobifg.polarisation:

                                        os.chdir(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+baselines['Slave'][idx])

                                        with open('config_card.tmp','w') as fout: 
                                                fout.write('cc **********************************************************************\n')
                                                fout.write('c ***  Doris \inputfile *****\n')
                                                fout.write('c **********************************************************************\n')
                                                fout.write(' c\n')
                                                fout.write(' c\n')
                                                fout.write(' comment  ___general options___\n')
                                                fout.write(' c\n')
                                                fout.write('c SCREEN          debug                           // level of output to standard out\n')
                                                fout.write('SCREEN          info                           // level of output to standard out\n')
                                                fout.write('MEMORY          %s                             // MB\n' %(jobifg.computerRAM))
                                                fout.write('BEEP            error                            // level of beeping\n')
                                                fout.write('OVERWRITE                                       // overwrite existing files\n')
                                                fout.write('BATCH                                           // non-interactive\n')
                                                fout.write('c LISTINPUT OFF                                 // prevents copy of this file to log\n')
                                                fout.write('c\n')
                                                fout.write('PROCESS          COARSEORB\n')
                                                fout.write('c                                              //\n')
                                                fout.write(' c                                              //\n')
                                                fout.write(' comment  ___the general io files___            //\n')
                                                fout.write(' c                                              //\n')
                                                fout.write('LOGFILE         tmp.log                         // log file\n')
                                                fout.write('M_RESFILE       ../master.res  // parameter file\n')
                                                fout.write('S_RESFILE       slave_res.slc.res                     // parameter file\n')
                                                fout.write('I_RESFILE       ifg.tmp               // parameter file\n')
                                                fout.write('HEIGHT              	0                	 // average WGS84 height\n')
                                                fout.write('ORB_INTERP          	POLYFIT             	 // orbit interpolation method\n')
                                                fout.write('ELLIPSOID           	WGS84               	 // WGS84, GRS80, BESSEL or define major and minor axis\n')
                                                fout.write('c                             \n')
                                                fout.write('DUMPBASELINE    50 50\n')
                                                fout.write(' c                                              //\n')
                                                fout.write('STOP                                              //\n')

                                        dict_cmd = {}
                                        dict_cmd['cmd%s' % (0)] = [ ['doris','config_card.tmp'],
                                                        'config_card.tmp']
                
                                        # Run Doris
                                        os.system('doris config_card.tmp > step_coarse.log')

                                        if os.path.isfile('ifg.tmp'): 
                                                os.remove('ifg.tmp')
                                        if os.path.isfile('tmp.log'): 
                                                os.remove('tmp.log')

                                        os.chdir(cur_dir)

                        idx = idx + 1

                usermessage.ezprint('\t\tdone',log,verbose) 

                if 'SBAS' in jobifg.modestack: 
                        usermessage.ezprint('Preparation of the StaMPS files for the SMALL_BASELINES processing',log,verbose)
                        
                        if jobifg.modestack == 'StaMPS_SBAS':
                                baselines = dorisstack.readbaselinefile(jobifg.workdirectory+os.sep+'bperp_file.txt')
                        else:
                                baselines = dorisstack.readbaselinefile(jobifg.workdirectory+os.sep+'bperp_file_MR.txt')

                        for poli in jobifg.polarisation:
                                if not os.path.isdir(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+'SMALL_BASELINES'):
                                        os.mkdir(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+'SMALL_BASELINES')

                        idx = 0 
                        while idx <= len(baselines['Idx'])-1:
                                if baselines['Check'][idx] == 1:
                                        for poli in jobifg.polarisation:
                                                pathdir = jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+'SMALL_BASELINES'+os.sep+baselines['Master'][idx]+'_'+baselines['Slave'][idx]
                                                if not os.path.isdir(pathdir):
                                                        os.mkdir(pathdir)

                                                ## Need to be modified for filtered slcs
                                                if baselines['Master'][idx] == jobifg.refdate: 
                                                        pathmaster = 'single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+baselines['Master'][idx]+'.'+poli.lower()+'.rslc' 
                                                        pathmasterres = 'single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+baselines['Master'][idx]+'.'+poli.lower()+'.rslc.res'

                                                        pathslave = 'single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+baselines['Slave'][idx]+'.'+poli.lower()+'.rslc' 
                                                        pathslaveres = 'single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+baselines['Slave'][idx]+'.'+poli.lower()+'.rslc.res'

                                                elif baselines['Slave'][idx] == jobifg.refdate: 
                                                        pathmaster = 'single_diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+os.sep+baselines['Master'][idx]+'.'+poli.lower()+'.rslc' 
                                                        pathmasterres = 'single_diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+os.sep+baselines['Master'][idx]+'.'+poli.lower()+'.rslc.res'

                                                        pathslave = 'single_diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+os.sep+jobifg.refdate+'.'+poli.lower()+'.rslc' 
                                                        pathslaveres = 'single_diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+os.sep+jobifg.refdate+'.'+poli.lower()+'.rslc.res'
                                                
                                                else:
                                                        pathmaster = 'single_diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+os.sep+baselines['Master'][idx]+'.'+poli.lower()+'.rslc' 
                                                        pathmasterres = 'single_diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+os.sep+baselines['Master'][idx]+'.'+poli.lower()+'.rslc.res'

                                                        pathslave = 'single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+jobifg.refdate+'.'+poli.lower()+'.rslc' 
                                                        pathslaveres = 'single_diff'+os.sep+baselines['Slave'][idx]+'_'+poli.lower()+os.sep+jobifg.refdate+'.'+poli.lower()+'.rslc.res'

                                                # for the master
                                                paraimage = doristools.readimagepara(pathmasterres)
                                                width = int(paraimage['Last_pixel (w.r.t. original_image)'] - paraimage['First_pixel (w.r.t. original_image)'] + 1)
 
                                                if paraimage['Data_output_format'] == 'complex_short': 
                                                        cmd = 'cpxfiddle -w %s -fci2 -ofloat -qnormal %s > %s' % (width,pathmaster, 
                                                        pathdir+os.sep+'master.filtrg.slc')
                                                        os.system(cmd)
                                                else:
                                                        shutil.copy(pathmaster,
                                                                pathdir+os.sep+'master.filtrg.slc')

                                                # for the slave
                                                paraimage = doristools.readimagepara(pathslaveres)
                                                width = int(paraimage['Last_pixel (w.r.t. original_image)'] - paraimage['First_pixel (w.r.t. original_image)'] + 1)
 
                                                if paraimage['Data_output_format'] == 'complex_short': 
                                                        cmd = 'cpxfiddle -w %s -fci2 -ofloat -qnormal %s > %s' % (width,pathslave, 
                                                        pathdir+os.sep+'slave.filtrg.slc')
                                                        os.system(cmd)
                                                else:
                                                        shutil.copy(pathslave,
                                                                pathdir+os.sep+'slave.filtrg.slc')

                                                # For the res files
                                                shutil.copy('diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.master.rslc.res',pathdir+os.sep+'master.res')
                                                shutil.copy('diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.slave.rslc.res',pathdir+os.sep+'slave.res')

                                                # For the interferograms
                                                if jobifg.ifgfilter['process']['value'] == True: 
                                                        infile = 'diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.diff.filt'
                                                else: 
                                                        infile = 'diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.diff'

                                                infileres = 'diff'+os.sep+baselines['Master'][idx]+'_'+poli.lower()+'_'+baselines['Slave'][idx]+'_'+poli.lower()+'.ifg'

                                                shutil.copy(infile,pathdir+os.sep+'cint.minrefdem.raw')
                                                shutil.copy(infileres,pathdir+os.sep+'interferogram.out')
                                                
                                idx = idx + 1

                        for poli in jobifg.polarisation:
                                idx = 0 
                                with open(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+poli.lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+'SMALL_BASELINES'+os.sep+'SMALL_BASELINES.list','w') as fout: 
                                        while idx <= len(baselines['Idx'])-1:
                                                if baselines['Check'][idx] == 1:
                                                        fout.write('%s %s\n' % (baselines['Master'][idx],baselines['Slave'][idx]))
                                                idx = idx + 1                       

                        usermessage.ezprint('\tdone',log,verbose) 

        if jobifg.finalstack['keepgeotiff']['value'] == True: 
                for li in ['diff','geo','rslc','single_diff']:
                        if os.path.isdir(li): 
                                shutil.rmtree(li)                                

        os.chdir(cur_dir)
        jobifg.finalstack['done']['value'] = True
        
        return jobifg