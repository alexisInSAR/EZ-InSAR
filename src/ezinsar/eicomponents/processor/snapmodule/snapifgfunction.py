#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to process ifgstack with SNAP processor 

The module allows to process ifgstack with SNAP processor from an ``ezinsar.coregistration`` job. 
    
    (From `ezinsar` package)

Note: 
        RAM memory optimisation needs to be done!

Changelog:
        * 1.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
from datetime import datetime
import os
import numpy as np
import glob
import datetime
from typing import Optional
from shapely.wkt import loads
from shapely import Polygon
import shutil
from osgeo import gdal, osr
import sys
import pandas as pd 
import json
import jdcal

from ezinsar import usermessage
from ezinsar import constants
from ezinsar.eicomponents.processor.snapmodule import snaptools, snapstack, snapgpttools
from ezinsar import tools

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

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
        if not 'snapifgstack.ifgstack' in str(type(jobifg)):
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

        if not os.path.isdir(jobifg.workdirectory): 
                os.mkdir(jobifg.workdirectory)

        os.chdir(jobifg.workdirectory)
        
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
        
        if jobifg.satmode == 'IW': 
                if os.path.isfile(jobifg.pathstack+os.sep+'stack_IW1.dim'): 
                        iwi = '1'
                elif os.path.isfile(jobifg.pathstack+os.sep+'stack_IW2.dim'): 
                        iwi = '2'
                else:
                        iwi = '3'
                stackfile = jobifg.pathstack+os.sep+'stack_IW'+iwi+'.dim'
                usermessage.warningmsg(__name__,ifgnetwork.__name__,__file__,'Because of Sentinel-1 IW data, the baselines will be computeed according to the sub-swath %s.' % (iwi),jobifg.log,verbose)
                
        else: 
                stackfile = jobifg.pathstack+os.sep+'stack.dim'       

        snapstack.computeifgnetwork(stackfile, 
                                jobifg.refdate,
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
        if os.path.isfile('bperp_file_Single.txt'):
                snapstack.baselinefigure('bperp_file_Single.txt')

        if os.path.isfile('bperp_file_MR.txt'):
                snapstack.baselinefigure('bperp_file_MR.txt')        

        if os.path.isfile('bperp_file.txt'):
                snapstack.baselinefigure('bperp_file.txt')   

        os.chdir(cur_dir)
        jobifg.ifgnetwork['done']['value'] = True

        return jobifg 

################################################################################
## ifgcompute FUNCTION
################################################################################
def ifgcompute(jobifg, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Create the interferograms

        The function will compute the inteferograms, from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()
        if not 'snapifgstack.ifgstack' in str(type(jobifg)):
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
        
        usermessage.openingmsg(__name__,ifgcompute.__name__,__file__,__copyright__,'ifgstack Step: ifgcompute',jobifg.log,verbose)

        jobifg.check(verbose=False,mode='high')

        if jobifg.ifgnetwork['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,ifgcompute.__name__,__file__,__copyright__,
                                'The previous step (ifgnetwork) is not done.',None))

        if not os.path.isdir(jobifg.workdirectory): 
                os.mkdir(jobifg.workdirectory)
        os.chdir(jobifg.workdirectory)

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobifg.log)
        
        list_stack = glob.glob(jobifg.pathstack+os.sep+'stack*.dim')
        for stack in list_stack: 

                usermessage.ezprint('Processing for %s:' % (stack),jobifg.log,verbose)

                prefixstack = stack.split('.')[0].replace(os.path.dirname(stack)+os.sep,'')

                usermessage.ezprint('\tImport the coregistration stack and add the elevation band (if required)',jobifg.log,verbose)
                listifg = snapstack.createsnaplistifg(snapstack.readbaselinefile('bperp_file.txt'))

                # Create the duplication of the stack to avoid any problems 
                if not jobifg.ifgcompute['symlinkstack']['value'] == False: 
                        if not os.path.isfile(prefixstack+'_coreg.dim'): 
                                os.symlink(stack,prefixstack+'_coreg.dim')
                        if not os.path.isdir(prefixstack+'_coreg.data'): 
                                os.symlink(stack,prefixstack+'_coreg.data')

                        usermessage.warningmsg(__name__,__name__,__file__,'EZ-InSAR assumes that the coregistration files can contain elevation band',jobifg.log,True)

                else: 
                        if not os.path.isfile(prefixstack+'_coreg.dim'):
                                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                        nbthread=jobifg.computernbthread,
                                        cleancache = constants.__SNAPcacheclean__,
                                        debugmode = constants.__SNAPloggingmode__)
                                gptdata.xmlinit()
                                gptdata.Read(os.path.abspath(stack))
                                
                                if (jobifg.modestack ==  'normal') and len(listifg)>1:
                                        para = {'demName': 'External DEM',
                                        'demResamplingMethod': jobifg.ifgcompute['demResamplingMethod']['value'],
                                        'externalDEMFile': os.path.abspath(jobifg.pathDEM+os.sep+jobifg.nameDEM),
                                        'externalDEMNoDataValue': jobifg.ifgcompute['externalDEMNoDataValue']['value']}
                                        gptdata.generic('AddElevation',
                                                para)
                                
                                gptdata.Write(os.path.abspath(prefixstack+'_coreg.dim'))
                                gptdata.xmlclose()
                                gptdata.run(verbose=verbose,log=jobifg.log)
                                gptdata.clean()

                        else: 
                               usermessage.warningmsg(__name__,__name__,__file__,'The coregistration file has been imported previously. This step was bypassed.',jobifg.log,True) 

                usermessage.ezprint('\t\tdone',jobifg.log,verbose)

                ## Compute the interferograms
                usermessage.ezprint('\tRun the computation of interferograms',jobifg.log,verbose)

                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                        nbthread=jobifg.computernbthread,
                        cleancache = constants.__SNAPcacheclean__,
                        debugmode = constants.__SNAPloggingmode__)
                gptdata.xmlinit()
                gptdata.Read(os.path.abspath(prefixstack+'_coreg.dim'))

                if jobifg.modestack ==  'normal':

                        # Add the MultiMasterInSAR
                        listifg = snapstack.createsnaplistifg(snapstack.readbaselinefile('bperp_file.txt'))

                        if not len(listifg) == 1: 

                                para = {'orbitDegree': '4',
                                        'includeWavenumber': jobifg.ifgcompute['includeWavenumber']['value'],
                                        'includeIncidenceAngle': jobifg.ifgcompute['includeIncidenceAngle']['value'],
                                        'includeLatLon': jobifg.ifgcompute['includeLatLon']['value'],
                                        'cohWindowAz': jobifg.ifgcompute['cohWindowAz']['value'],
                                        'cohWindowRg': jobifg.ifgcompute['cohWindowRg']['value'],
                                        'pairs': ','.join(listifg)}
                                gptdata.generic('MultiMasterInSAR',
                                                para)
                                
                        else:
                                para = {'orbitDegree': '4',
                                        'includeCoherence': True,
                                        'squarePixel': False,
                                        'cohWinAz': jobifg.ifgcompute['cohWindowAz']['value'],
                                        'cohWinRg': jobifg.ifgcompute['cohWindowRg']['value'],
                                        'outputElevation': True,
                                        'outputLatLon': True,
                                        'subtractTopographicPhase': jobifg.ifgcompute['subtractTopographicPhase']['value'], 
                                        'demName': 'External DEM',
                                        'externalDEMFile': os.path.abspath(jobifg.pathDEM+os.sep+jobifg.nameDEM),
                                        'externalDEMNoDataValue': jobifg.ifgcompute['externalDEMNoDataValue']['value'],
                                        'externalDEMApplyEGM': False,
                                        }
                                gptdata.generic('Interferogram',
                                                para)
                        
                elif jobifg.modestack ==  'StaMPS_PS':
                        para = {'orbitDegree': '4',
                                'includeCoherence': False,
                                'squarePixel': False,
                                'cohWinAz': jobifg.ifgcompute['cohWindowAz']['value'],
                                'cohWinRg': jobifg.ifgcompute['cohWindowRg']['value'],
                                'outputElevation': True,
                                'outputLatLon': True,
                                'subtractTopographicPhase': jobifg.ifgcompute['subtractTopographicPhase']['value'], 
                                'demName': 'External DEM',
                                'externalDEMFile': os.path.abspath(jobifg.pathDEM+os.sep+jobifg.nameDEM),
                                'externalDEMNoDataValue': jobifg.ifgcompute['externalDEMNoDataValue']['value'],
                                'externalDEMApplyEGM': False,
                                }
                        gptdata.generic('Interferogram',
                                        para)
                
                gptdata.Write(os.path.abspath(prefixstack+'_ifg.dim'))
                gptdata.xmlclose()
                if (not os.path.isfile(os.path.abspath(prefixstack+'_ifg.dim'))) or modeforce == True: 
                        gptdata.run(verbose=verbose,log=jobifg.log)
                else: 
                        usermessage.warningmsg(__name__,__name__,__file__,'The inteferogram computation has been done for %s.' % (prefixstack+'_ifg.dim'),jobifg.log,True) 
                gptdata.clean()

                ## Debursting if required
                if jobifg.satmode == 'IW':
                        gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                nbthread=jobifg.computernbthread,
                                cleancache = constants.__SNAPcacheclean__,
                                debugmode = constants.__SNAPloggingmode__)
                        gptdata.xmlinit()
                        gptdata.Read(os.path.abspath(prefixstack+'_ifg.dim'))
                        gptdata.generic('TOPSAR-Deburst',{})
                        gptdata.Write(os.path.abspath(prefixstack+'_ifg_deb.dim'))
                        gptdata.xmlclose()
                        if (not os.path.isfile(os.path.abspath(prefixstack+'_ifg_deb.dim'))) or modeforce == True: 
                                gptdata.run(verbose=verbose,log=jobifg.log)
                        else: 
                                usermessage.warningmsg(__name__,__name__,__file__,'The inteferogram computation has been done for %s.' % (prefixstack+'_ifg_deb.dim'),jobifg.log,True) 
                        gptdata.clean()

                usermessage.ezprint('\t\tdone',jobifg.log,verbose)

        ## Merging if required
        usermessage.ezprint('\tHarmonise of the InSAR stack (for Sentinel-1 IW, the merging of IW will be done)',jobifg.log,verbose)

        if jobifg.satmode == 'IW':
                list_stack = glob.glob(jobifg.workdirectory+os.sep+'stack_IW*_ifg_deb.dim')

                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                        nbthread=jobifg.computernbthread,
                                        cleancache = constants.__SNAPcacheclean__,
                                        debugmode = constants.__SNAPloggingmode__)
                gptdata.xmlinit()
                for idx, stacki in enumerate(list_stack):
                        gptdata.Read(os.path.abspath(stacki),idx=idx+1)
                
                if len(list_stack) > 1:
                        gptdata.TOPSARMerge()

                gptdata.Write(os.path.abspath(jobifg.workdirectory+os.sep+'stack_ifg_full.dim'))
                gptdata.xmlclose()
                
                if (not os.path.isfile(os.path.abspath('stack_ifg_full.dim'))) or modeforce == True: 
                        gptdata.run(verbose=verbose,log=jobifg.log)
                else: 
                        usermessage.warningmsg(__name__,__name__,__file__,'The inteferogram computation has been done for %s.' % ('stack_ifg_full.dim'),jobifg.log,True) 

                gptdata.clean()

                ## Crop the dataset if required
                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                        nbthread=jobifg.computernbthread,
                        cleancache = constants.__SNAPcacheclean__,
                        debugmode = constants.__SNAPloggingmode__)
                gptdata.xmlinit()
                gptdata.Read(os.path.abspath(jobifg.workdirectory+os.sep+'stack_ifg_full.dim'))

                if 'StaMPS_PS' in jobifg.modestack: 

                        para = {'outputElevationBand': False,
                                'outputLatLonBands': True,
                                'outputTopoPhaseBand': True, 
                                'demName': 'External DEM',
                                'externalDEMFile': os.path.abspath(jobifg.pathDEM+os.sep+jobifg.nameDEM),
                                'externalDEMNoDataValue': jobifg.ifgcompute['externalDEMNoDataValue']['value'],
                                }
                        gptdata.generic('TopoPhaseRemoval',
                                        para)

                if jobifg.ifgcompute['cropping']['value']:
                        gptdata.generic('Subset',
                                {'copyMetadata': True,
                                'geoRegion': loads(jobifg.roi).wkt})
                        
                gptdata.Write(os.path.abspath(jobifg.workdirectory+os.sep+'stack_diff.dim'))
                gptdata.xmlclose()
                if (not os.path.isfile(os.path.abspath('stack_diff.dim'))) or modeforce == True: 
                        gptdata.run(verbose=verbose,log=jobifg.log)
                else: 
                        usermessage.warningmsg(__name__,__name__,__file__,'The inteferogram computation has been done for %s.' % ('stack_diff.dim'),jobifg.log,True) 
                gptdata.clean()

        else: 
                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                nbthread=jobifg.computernbthread,
                                cleancache = constants.__SNAPcacheclean__,
                                debugmode = constants.__SNAPloggingmode__)
                gptdata.xmlinit()
                gptdata.Read(os.path.abspath(jobifg.workdirectory+os.sep+'stack_ifg.dim'))
                gptdata.Write(os.path.abspath(jobifg.workdirectory+os.sep+'stack_diff.dim'))
                gptdata.xmlclose()
                if (not os.path.isfile(os.path.abspath('stack_diff.dim'))) or modeforce == True: 
                        gptdata.run(verbose=verbose,log=jobifg.log)
                else: 
                        usermessage.warningmsg(__name__,__name__,__file__,'The inteferogram computation has been done for %s.' % ('stack_diff.dim'),jobifg.log,True) 
                gptdata.clean()

        usermessage.ezprint('\t\tdone',jobifg.log,verbose)

        ## Image creation of verification
        if jobifg.ifgcompute['createbmp']['value']:
                usermessage.ezprint('Creation of the .bmp for checking',jobifg.log,verbose)

                network = snapstack.readbaselinefile('bperp_file.txt')

                for idx, li in enumerate(snapstack.createsnaplistifg(network)):
                        if network['Check'][idx]==1:

                                li = li.replace('-','_')

                                # For the interferogram
                                output = network['Master'][idx]+'.'+jobifg.polarisation[0].lower()+'.'+network['Slave'][idx]+'.'+jobifg.polarisation[0].lower()+'.diff.bmp'
                                
                                realpart = glob.glob(jobifg.workdirectory+os.sep+'stack_diff.data'+os.sep+'q_ifg*'+jobifg.polarisation[0].upper()+'*'+li+'*'+'img')
                                imgpart = glob.glob(jobifg.workdirectory+os.sep+'stack_diff.data'+os.sep+'i_ifg*'+jobifg.polarisation[0].upper()+'*'+li+'*'+'img')
                                if realpart: 
                                        realpart = realpart[0]
                                        imgpart = imgpart[0]
                                        if (not os.path.isfile(output)) or modeforce == True: 

                                                usermessage.ezprint('\tCreate the file %s' % (output),jobifg.log,verbose)
                                                snaptools.createifgbmp([realpart, imgpart],
                                                        output,
                                                        jobifg.mlran, 
                                                        jobifg.mlazi,
                                                        colormap = 'sar',
                                                        verbose = True,
                                                        log = jobifg.log,
                                                        )
                                                usermessage.ezprint('\t\tdone',jobifg.log,verbose)

                                # For the coherence
                                imagecoh = glob.glob(jobifg.workdirectory+os.sep+'stack_diff.data'+os.sep+'coh*'+jobifg.polarisation[0].upper()+'*'+li+'*'+'img')
                                output = network['Master'][idx]+'.'+jobifg.polarisation[0].lower()+'.'+network['Slave'][idx]+'.'+jobifg.polarisation[0].lower()+'.cc.bmp'
                                
                                if imagecoh: 
                                        imagecoh = imagecoh[0]
                                        if (not os.path.isfile(output)) or modeforce == True: 

                                                usermessage.ezprint('\tCreate the file %s' % (output),jobifg.log,verbose)
                                                snaptools.createcohbmp(imagecoh,
                                                        output,
                                                        jobifg.mlran, 
                                                        jobifg.mlazi,
                                                        colormap = 'gray',
                                                        verbose = False,
                                                        log = jobifg.log,
                                                        )
                                                usermessage.ezprint('\t\tdone',jobifg.log,verbose)

                usermessage.ezprint('\tdone',jobifg.log,verbose)

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobifg.log)
        os.chdir(cur_dir)
        jobifg.ifgcompute['done']['value'] = True

        return jobifg 

################################################################################
## ifgfilter FUNCTION
################################################################################
def ifgfilter(jobifg, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Create the interferograms

        The function will compute the inteferograms, from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()
        if not 'snapifgstack.ifgstack' in str(type(jobifg)):
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
        
        usermessage.openingmsg(__name__,ifgfilter.__name__,__file__,__copyright__,'ifgstack Step: ifgfilter',jobifg.log,verbose)

        jobifg.check(verbose=False,mode='high')

        if jobifg.ifgcompute['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,ifgfilter.__name__,__file__,__copyright__,
                                'The previous step (ifgcompute) is not done.',None))

        # Exit if not required
        if 'StaMPS' in jobifg.modestack: 
                usermessage.warningmsg(__name__,__name__,__file__,'This step is not required for the stack mode %s.' % (jobifg.modestack),jobifg.log,verbose) 
                os.chdir(cur_dir)
                jobifg.ifgfilter['done']['value'] = True
                return jobifg 
        
        os.chdir(jobifg.workdirectory)

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobifg.log)
        
        if jobifg.ifgfilter['process']['value']: 
                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                                nbthread=jobifg.computernbthread,
                                                cleancache = constants.__SNAPcacheclean__,
                                                debugmode = constants.__SNAPloggingmode__)
                gptdata.xmlinit()
                gptdata.Read(os.path.abspath('stack_diff.dim'))
                
                para = {'alpha': jobifg.ifgfilter['alpha']['value'],
                        'FFTSizeString': jobifg.ifgfilter['FFTSizeString']['value'],
                        'useCoherenceMask': jobifg.ifgfilter['useCoherenceMask']['value'],
                        'coherenceThreshold': jobifg.ifgfilter['coherenceThreshold']['value'],
                        'windowSizeString': jobifg.ifgfilter['windowSizeString']['value']}
                
                gptdata.generic('GoldsteinPhaseFiltering',
                        para)

                gptdata.Write(os.path.abspath('stack_diff_filt.dim'))
                gptdata.xmlclose()
                if (not os.path.isfile(os.path.abspath('stack_diff_filt.dim'))) or modeforce == True: 
                        gptdata.run(verbose=verbose,log=jobifg.log)
                else: 
                        usermessage.warningmsg(__name__,__name__,__file__,'The inteferogram computation has been done for %s.' % ('stack_diff_filt.dim'),jobifg.log,True) 
                gptdata.clean()

                if jobifg.ifgfilter['createbmp']['value']:
                        network = snapstack.readbaselinefile('bperp_file.txt')
                        
                        for idx, li in enumerate(snapstack.createsnaplistifg(network)):
                                if network['Check'][idx]==1:
                                        li = li.replace('-','_')
                                        realpart = glob.glob(jobifg.workdirectory+os.sep+'stack_diff_filt.data'+os.sep+'q_ifg*'+jobifg.polarisation[0].upper()+'*'+li+'*'+'img')
                                        imgpart = glob.glob(jobifg.workdirectory+os.sep+'stack_diff_filt.data'+os.sep+'i_ifg*'+jobifg.polarisation[0].upper()+'*'+li+'*'+'img')
                                        output = network['Master'][idx]+'.'+jobifg.polarisation[0].lower()+'.'+network['Slave'][idx]+'.'+jobifg.polarisation[0].lower()+'.diff.filt.bmp'

                                        if realpart: 
                                                realpart = realpart[0]
                                                imgpart = imgpart[0]
                                                if (not os.path.isfile(output)) or modeforce == True: 
                                                        usermessage.ezprint('\tCreate the file %s' % (output),jobifg.log,verbose)
                                                        snaptools.createifgbmp([realpart, imgpart],
                                                                output,
                                                                jobifg.mlran, 
                                                                jobifg.mlazi,
                                                                colormap = 'sar',
                                                                verbose = False,
                                                                log = jobifg.log,
                                                                )

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobifg.log)
        os.chdir(cur_dir)
        jobifg.ifgfilter['done']['value'] = True

        return jobifg 

################################################################################
## multilook FUNCTION
################################################################################
def multilook(jobifg, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Multilook the InSAR products

        The function will multilook the InSAR products, from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()
        if not 'snapifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,multilook.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,multilook.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))
        
        if modeforce == None:
                modeforce = jobifg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ifgfilter.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobifg.log))
        
        usermessage.openingmsg(__name__,multilook.__name__,__file__,__copyright__,'ifgstack Step: multilook',jobifg.log,verbose)

        jobifg.check(verbose=False,mode='high')

        if jobifg.ifgcompute['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,multilook.__name__,__file__,__copyright__,
                                'The previous step (ifgcompute) is not done.',None))

        # Exit if not required
        if 'StaMPS' in jobifg.modestack: 
                usermessage.warningmsg(__name__,__name__,__file__,'This step is not required for the stack mode %s.' % (jobifg.modestack),jobifg.log,verbose) 
                # os.chdir(cur_dir)
                # jobifg.multilook['done']['value'] = True
                # return jobifg 
        
        os.chdir(jobifg.workdirectory)

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobifg.log)
        
        if jobifg.multilook['process']['value']: 
                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                                nbthread=jobifg.computernbthread,
                                                cleancache = constants.__SNAPcacheclean__,
                                                debugmode = constants.__SNAPloggingmode__)
                gptdata.xmlinit()

                if jobifg.ifgfilter['process']['value']:
                        gptdata.Read(os.path.abspath('stack_diff_filt.dim'))
                        output = os.path.abspath('stack_diff_filt_ml.dim')
                else: 
                        gptdata.Read(os.path.abspath('stack_diff.dim'))
                        output = os.path.abspath('stack_diff_ml.dim')
                
                gptdata.generic('Multilook',
                        {'nRgLooks': jobifg.mlran,
                        'nAzLooks': jobifg.mlazi,
                        'grSquarePixel': False})

                gptdata.Write(output)
                gptdata.xmlclose()
                if (not os.path.isfile(output)) or modeforce == True: 
                        gptdata.run(verbose=verbose,log=jobifg.log)
                else: 
                        usermessage.warningmsg(__name__,__name__,__file__,'The inteferogram computation has been done for %s.' % (output),jobifg.log,True) 
                gptdata.clean()

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobifg.log)
        os.chdir(cur_dir)
        jobifg.ifgfilter['done']['value'] = True

        return jobifg 

################################################################################
## ifgunwrapping FUNCTION
################################################################################
def ifgunwrapping(jobifg, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Unwrap the interferograms

        The function will unwrap the interferograms, from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()
        if not 'snapifgstack.ifgstack' in str(type(jobifg)):
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
                        __name__,ifgfilter.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobifg.log))
        
        usermessage.openingmsg(__name__,ifgunwrapping.__name__,__file__,__copyright__,'ifgstack Step: ifgunwrapping',jobifg.log,verbose)

        jobifg.check(verbose=False,mode='high')

        if jobifg.ifgcompute['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,ifgunwrapping.__name__,__file__,__copyright__,
                                'The previous step (ifgcompute) is not done.',None))

        # Exit if not required
        if 'StaMPS' in jobifg.modestack: 
                usermessage.warningmsg(__name__,__name__,__file__,'This step is not required for the stack mode %s.' % (jobifg.modestack),jobifg.log,verbose) 
                os.chdir(cur_dir)
                jobifg.ifgunwrapping['done']['value'] = True
                return jobifg 
        
        os.chdir(jobifg.workdirectory)

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobifg.log)
        
        if jobifg.ifgunwrapping['process']['value']: 

                # Export 
                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                                nbthread=jobifg.computernbthread,
                                                cleancache = constants.__SNAPcacheclean__,
                                                debugmode = constants.__SNAPloggingmode__)
                gptdata.xmlinit()

                if os.path.isfile(os.path.abspath('stack_diff_filt_ml.dim')): 
                        input = os.path.abspath('stack_diff_filt_ml.dim')
                elif os.path.isfile(os.path.abspath('stack_diff_ml.dim')): 
                        input = os.path.abspath('stack_diff_ml.dim')
                elif os.path.isfile(os.path.abspath('stack_diff_filt.dim')): 
                        input = os.path.abspath('stack_diff_filt.dim')
                else:
                        input = os.path.abspath('stack_diff.dim')

                if jobifg.ifgunwrapping['targetFolder']['value'] == 'auto':
                        output = jobifg.workdirectory + os.sep + 'tmp_unwrap'
                else:
                        output = jobifg.ifgunwrapping['targetFolder']['value']

                if (not os.path.isfile(input.replace('.dim','')+'_unw.dim')) or modeforce == True:

                        gptdata.Read(input)
                        gptdata.generic('SnaphuExport',
                                {'targetFolder': output,
                                'statCostMode': jobifg.ifgunwrapping['statCostMode']['value'],
                                'initMethod': jobifg.ifgunwrapping['initMethod']['value'],
                                'numberOfTileRows': jobifg.ifgunwrapping['numberOfTileRows']['value'],
                                'numberOfTileCols': jobifg.ifgunwrapping['numberOfTileCols']['value'],
                                'numberOfProcessors': jobifg.ifgunwrapping['numberOfProcessors']['value'],
                                'rowOverlap': jobifg.ifgunwrapping['rowOverlap']['value'],
                                'colOverlap': jobifg.ifgunwrapping['colOverlap']['value'],
                                'tileCostThreshold': jobifg.ifgunwrapping['tileCostThreshold']['value']})

                        gptdata.xmlclose()
                        gptdata.run(verbose=verbose,log=jobifg.log)
                        gptdata.clean()

                        ## Run the unwrapping 
                        listconf = glob.glob(output+os.sep+'*'+os.sep+'*.conf')
                        
                        # Modification to delete the corr files
                        cmds = []
                        for confi in listconf: 
                                with open(confi) as fi:
                                        lines = fi.readlines()

                                for idx, li in enumerate(lines): 
                                        if 'CORRFILE' in li: 
                                                lines[idx] = ''
                                        if 'snaphu -f' in li: 
                                                cmds.append(li)

                                with open(confi,'w') as fi:
                                        for li in lines:
                                                fi.write('%s' % (li))            

                        # run
                        os.chdir(os.path.dirname(listconf[0]))
                        for cmdi in cmds: 
                                os.system(cmdi.replace('#','').strip())
                        os.chdir(jobifg.workdirectory)

                        ## Import the unwrapped phase
                        listunwrapfile = glob.glob(os.path.dirname(listconf[0])+os.sep+'UnwPhase*.hdr')
                        inputtmp = input
                        output = input.replace('.dim','')+'_unw.dim'
                        
                        for li in listunwrapfile: 
                                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                                        nbthread=jobifg.computernbthread,
                                                        cleancache = constants.__SNAPcacheclean__,
                                                        debugmode = constants.__SNAPloggingmode__)
                                gptdata.xmlinit()
                                gptdata.Read(inputtmp)
                                gptdata.Read(li,idx=2)
                                gptdata.SnaphuImport()
                                gptdata.Write(output)
                                gptdata.xmlclose()
                                gptdata.run(verbose=verbose,log=jobifg.log)
                                gptdata.clean()

                                inputtmp = output

                        if os.path.isdir(output): 
                                shutil.rmtree(output)

                else: 
                        usermessage.warningmsg(__name__,__name__,__file__,'The inteferogram computation has been done', jobifg.log,True)

                if jobifg.ifgunwrapping['createbmp']['value']:
                        network = snapstack.readbaselinefile('bperp_file.txt')

                        for idx, li in enumerate(snapstack.createsnaplistifg(network)):
                                li = li.replace('-','_')
                                fi = glob.glob(input.replace('.dim','')+'_unw.data'+os.sep+'UnwPhase_ifg_*'+jobifg.polarisation[0].upper()+'*'+li+'*'+'img')
                                output = network['Master'][idx]+'.'+jobifg.polarisation[0].lower()+'.'+network['Slave'][idx]+'.'+jobifg.polarisation[0].lower()+'.diff.unw.bmp'

                                if fi: 
                                        fi = fi[0]
                                        if (not os.path.isfile(output)) or modeforce == True: 
                                                snaptools.createunwbmp(fi,
                                                        output,
                                                        1, 
                                                        1,
                                                        colormap = 'jet',
                                                        verbose = verbose,
                                                        log = jobifg.log,
                                                        )
                                
        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobifg.log)
        os.chdir(cur_dir)
        jobifg.ifgunwrapping['done']['value'] = True

        return jobifg 

################################################################################
## ifggeocoding FUNCTION
################################################################################
def ifggeocoding(jobifg, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Geocode the InSAR products

        The function will geocode the InSAR products, from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()
        if not 'snapifgstack.ifgstack' in str(type(jobifg)):
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
        
        usermessage.openingmsg(__name__,ifggeocoding.__name__,__file__,__copyright__,'ifgstack Step: ifggeocoding',jobifg.log,verbose)

        jobifg.check(verbose=False,mode='high')

        if jobifg.ifgcompute['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,ifggeocoding.__name__,__file__,__copyright__,
                                'The previous step (ifgcompute) is not done.',None))
        
        # Exit if not required
        if 'StaMPS' in jobifg.modestack: 
                usermessage.warningmsg(__name__,__name__,__file__,'This step is not required for the stack mode %s.' % (jobifg.modestack),jobifg.log,verbose) 
                # os.chdir(cur_dir)
                # jobifg.ifggeocoding['done']['value'] = True
                # return jobifg 

        os.chdir(jobifg.workdirectory)

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobifg.log)
        
        if jobifg.ifggeocoding['process']['value']: 

                ## Preparation of the DEM
                src_ds = gdal.Open(jobifg.pathDEM+os.sep+jobifg.nameDEM)
                options = '-of GTiff -a_nodata %s -tr %s %s' % (jobifg.ifggeocoding['externalDEMNoDataValue']['value'],abs(src_ds.GetGeoTransform()[1]*jobifg.ifggeocoding['Xdem_overfactor']['value']),abs(src_ds.GetGeoTransform()[5]*jobifg.ifggeocoding['Ydem_overfactor']['value']))
                dst_ds = gdal.Translate('tmpDEM.tif', src_ds, options = options)
                src_ds = None
                dst_ds = None

                inputstack = sorted(glob.glob('stack_diff_*.dim'), key=len)[-1]
                outputstack = 'stack_diff_geo.dim'
        
                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                        nbthread=jobifg.computernbthread,
                                        cleancache = constants.__SNAPcacheclean__,
                                        debugmode = constants.__SNAPloggingmode__)
                gptdata.xmlinit()
                gptdata.Read(inputstack)

                para = {'demName': 'External DEM',
                        'demResamplingMethod': jobifg.ifggeocoding['demResamplingMethod']['value'],
                        'imgResamplingMethod': jobifg.ifggeocoding['imgResamplingMethod']['value'],
                        'externalDEMFile': 'tmpDEM.tif',
                        'externalDEMApplyEGM': jobifg.ifggeocoding['demResamplingMethod']['value'],
                        'externalDEMNoDataValue': jobifg.ifggeocoding['externalDEMNoDataValue']['value'],
                        'nodataValueAtSea': jobifg.ifggeocoding['nodataValueAtSea']['value'],
                        'saveDEM': jobifg.ifggeocoding['saveDEM']['value'],
                        'saveLatLon': jobifg.ifggeocoding['saveLatLon']['value'],
                        'saveIncidenceAngleFromEllipsoid': jobifg.ifggeocoding['saveIncidenceAngleFromEllipsoid']['value'],
                        'saveLocalIncidenceAngle': jobifg.ifggeocoding['saveLocalIncidenceAngle']['value'],
                        'saveProjectedLocalIncidenceAngle': jobifg.ifggeocoding['saveProjectedLocalIncidenceAngle']['value'],
                        'saveLayoverShadowMask': jobifg.ifggeocoding['saveLayoverShadowMask']['value'],
                        'outputComplex': jobifg.ifggeocoding['outputComplex']['value'],
                        'outputComplex': jobifg.ifggeocoding['outputComplex']['value'],
                        'alignToStandardGrid': 'True'}

                gptdata.generic('Terrain-Correction',para)
                gptdata.Write(os.path.abspath(outputstack))
                gptdata.xmlclose()
                if (not os.path.isfile(outputstack)) or modeforce == True: 
                        gptdata.run(verbose=verbose,log=jobifg.log)
                else: 
                        usermessage.warningmsg(__name__,__name__,__file__,'The inteferogram computation has been done for %s.' % (outputstack),jobifg.log,True) 
                gptdata.clean()

                if os.path.isfile('tmpDEM.tif'):
                        os.remove('tmpDEM.tif')

                if jobifg.ifggeocoding['geotiff']['value']:

                        usermessage.ezprint('Creation of the GTiff images',jobifg.log,verbose)

                        if not os.path.isdir('geotiff'):
                                os.mkdir('geotiff')

                        network = snapstack.readbaselinefile('bperp_file.txt')

                        for idx, li in enumerate(snapstack.createsnaplistifg(network)):
                                if network['Check'][idx]==1:
                                        li = li.replace('-','_')

                                        shadowfile = jobifg.workdirectory+os.sep+'stack_diff_geo.data'+os.sep+'layoverShadowMask.img'
                                        if not os.path.isfile(shadowfile):
                                                shadowfile = None

                                        coherencefile = None
                                        coherencefileunw = None
                                        cleantmpfile = False
                                        if jobifg.ifggeocoding['maskifg']['value']:
                                                coherencefile = glob.glob(jobifg.workdirectory+os.sep+'stack_diff_geo.data'+os.sep+'coh_*'+jobifg.polarisation[0].upper()+'*'+li+'*'+'img')[0]
                                                coherencefileunw = glob.glob(jobifg.workdirectory+os.sep+'stack_diff_geo.data'+os.sep+'coh_*'+jobifg.polarisation[0].upper()+'*'+li+'*'+'img')[0]

                                        # For the ifgs
                                        input = glob.glob(jobifg.workdirectory+os.sep+'stack_diff_geo.data'+os.sep+'Phase_ifg_*'+jobifg.polarisation[0].upper()+'*'+li+'*'+'img')

                                        # for StaMPS_PS processing
                                        if not input: 
                                                inputcpx = glob.glob(jobifg.workdirectory+os.sep+'stack_diff_geo.data'+os.sep+'q_ifg_*'+jobifg.polarisation[0].upper()+'*'+li+'*'+'img')

                                                for filei in inputcpx: 
                                                        realpart = filei
                                                        imagpart = os.path.dirname(filei)+os.sep+filei.split(os.sep)[-1].replace('q_ifg','i_ifg')
                                                        floatfile = os.path.dirname(filei)+os.sep+filei.split(os.sep)[-1].replace('q_ifg','Phase_ifg')

                                                        with gdal.Open(realpart) as fimag:
                                                                realpart_s = fimag.GetRasterBand(1).ReadAsArray().astype(float)

                                                                nx = realpart_s.shape[0]
                                                                ny = realpart_s.shape[1]
                                                                dst_ds = gdal.GetDriverByName('ENVI').Create(floatfile, ny, nx, 1, gdal.GDT_Float32)
                                                                dst_ds.SetGeoTransform(list(fimag.GetGeoTransform()))
                                                                srs = osr.SpatialReference()
                                                                srs.ImportFromEPSG(4326)
                                                                dst_ds.SetProjection(srs.ExportToWkt())  

                                                        with gdal.Open(imagpart) as fimag:
                                                                imagfile_s = fimag.GetRasterBand(1).ReadAsArray().astype(float)
                                                        ifg_s = realpart_s + imagfile_s * 1j

                                                        dst_ds.GetRasterBand(1).WriteArray(np.angle(ifg_s))   
                                                        dst_ds.GetRasterBand(1).SetNoDataValue(0)                 
                                                        dst_ds.FlushCache()                                             
                                                        dst_ds = None       

                                                # Re-detection 
                                                input = glob.glob(jobifg.workdirectory+os.sep+'stack_diff_geo.data'+os.sep+'Phase_ifg_*'+jobifg.polarisation[0].upper()+'*'+li+'*'+'img') 
                                                cleantmpfile = True


                                        output = 'geotiff'+os.sep+network['Master'][idx]+'.'+jobifg.polarisation[0].lower()+'.'+network['Slave'][idx]+'.'+jobifg.polarisation[0].lower()+'.diff.geo.tif'

                                        if input:
                                                input = input[0] 
                                                if (not os.path.isfile(output)) or modeforce == True: 
                                                        snaptools.ENVI2geotiff(input,
                                                                output,
                                                                coherencefile = coherencefile,
                                                                cohthreshold = jobifg.ifggeocoding['coherencethresholdmask']['value'],
                                                                shadowfile = shadowfile,
                                                                nodata = 0,
                                                                verbose = verbose,
                                                                log = jobifg.log,
                                                                )
                                                        if jobifg.ifggeocoding['uchargeotiff']['value']:
                                                                tools.geocoding.geotifffloat2uchar(output,
                                                                        nodata = 0,
                                                                        colormap = 'sar',
                                                                        AREA_OR_POINT = 'Area',
                                                                        verbose = verbose,
                                                                        log = jobifg.log,
                                                                        )
                                                if cleantmpfile: 
                                                        listfile = glob.glob(input.replace('.img','.*'))
                                                        for filei in listfile: 
                                                                if os.path.isfile(filei): 
                                                                        os.remove(filei)

                                        # For the coherence
                                        input = glob.glob(jobifg.workdirectory+os.sep+'stack_diff_geo.data'+os.sep+'coh_*'+jobifg.polarisation[0].upper()+'*'+li+'*'+'img')
                                        output = 'geotiff'+os.sep+network['Master'][idx]+'.'+jobifg.polarisation[0].lower()+'.'+network['Slave'][idx]+'.'+jobifg.polarisation[0].lower()+'.coh.geo.tif'
                                        
                                        if input: 
                                                input = input[0]
                                                if (not os.path.isfile(output)) or modeforce == True: 
                                                        snaptools.ENVI2geotiff(input,
                                                                output,
                                                                coherencefile = None,
                                                                cohthreshold = jobifg.ifggeocoding['coherencethresholdmask']['value'],
                                                                shadowfile = shadowfile,
                                                                nodata = 0,
                                                                verbose = verbose,
                                                                log = jobifg.log,
                                                                )
                                        
                                                        if jobifg.ifggeocoding['uchargeotiff']['value']:
                                                                tools.geocoding.geotifffloat2uchar(output,
                                                                        nodata = 0,
                                                                        colormap = 'gray',
                                                                        AREA_OR_POINT = 'Area',
                                                                        verbose = verbose,
                                                                        log = jobifg.log,
                                                                        )

                                        # For the unwraping
                                        input = glob.glob(jobifg.workdirectory+os.sep+'stack_diff_geo.data'+os.sep+'UnwPhase_ifg_*'+jobifg.polarisation[0].upper()+'*'+li+'*'+'img')
                                        output = 'geotiff'+os.sep+network['Master'][idx]+'.'+jobifg.polarisation[0].lower()+'.'+network['Slave'][idx]+'.'+jobifg.polarisation[0].lower()+'.unw.geo.tif'
                                        
                                        if input: 
                                                input = [0]
                                                if (not os.path.isfile(output)) or modeforce == True: 
                                                        snaptools.ENVI2geotiff(input,
                                                                output,
                                                                coherencefile = coherencefileunw,
                                                                cohthreshold = jobifg.ifggeocoding['coherencethresholdmask']['value'],
                                                                shadowfile = shadowfile,
                                                                nodata = 0,
                                                                verbose = verbose,
                                                                log = jobifg.log,
                                                                )

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobifg.log)
        os.chdir(cur_dir)
        jobifg.ifggeocoding['done']['value'] = True

        return jobifg 

################################################################################
## finalstack FUNCTION
################################################################################
def finalstack(jobifg, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Finalise the stack

        The function will finalse the InSAR stack, from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()
        if not 'snapifgstack.ifgstack' in str(type(jobifg)):
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
                        __name__,ifgcompute.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobifg.log))
        
        usermessage.openingmsg(__name__,finalstack.__name__,__file__,__copyright__,'ifgstack Step: finalstack',jobifg.log,verbose)

        jobifg.check(verbose=False,mode='high')

        if jobifg.ifgcompute['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,finalstack.__name__,__file__,__copyright__,
                                'The previous step (ifgcompute) is not done.',None))

        os.chdir(jobifg.workdirectory)

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobifg.log)

        ## For the export of StaMPS for PS
        if jobifg.modestack == 'StaMPS_PS': 

                usermessage.ezprint('Creation of the StaMPS directory for StaMPS in case of PSI computation',jobifg.log,verbose)

                stampsdir = jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+jobifg.polarisation[0].lower()+os.sep+'INSAR_'+jobifg.refdate

                if not os.path.isdir(stampsdir): 
                        os.makedirs(stampsdir)
                else: 
                        raise ValueError(usermessage.errormsg(__name__,finalstack.__name__,__file__,__copyright__,
                                'A previous StaMPS directory has been detected. Please delete it.',None))

                usermessage.ezprint('\tCreation of the tmp directory',jobifg.log,verbose)
                if os.path.isdir('tmp_stamps'): 
                    shutil.rmtree('tmp_stamps')
                os.mkdir('tmp_stamps')
                usermessage.ezprint('\t\tdone',jobifg.log,verbose)

                # For the coregistration stack
                usermessage.ezprint('\tProcessing of the coregistration stack (add the elevation band)',jobifg.log,verbose)

                list_stack = glob.glob(jobifg.workdirectory+os.sep+'stack*coreg.dim')

                for idx, stacki in enumerate(list_stack): 
                        if jobifg.satmode == 'IW':
                                usermessage.ezprint('\t\tDebursting required:',jobifg.log,verbose)
                                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                        nbthread=jobifg.computernbthread,
                                        cleancache = constants.__SNAPcacheclean__,
                                        debugmode = constants.__SNAPloggingmode__)
                                gptdata.xmlinit()
                                gptdata.Read(os.path.abspath(stacki))
                                gptdata.generic('TOPSAR-Deburst',{})
                                gptdata.Write(os.path.abspath('tmp_stamps'+os.sep+'stack_coreg_tmp_%s.dim' % (idx+1)))
                                gptdata.xmlclose()
                                gptdata.run(verbose=verbose,log=jobifg.log)
                                gptdata.clean()
                                usermessage.ezprint('\t\t\tdone',jobifg.log,verbose)

                list_stack = glob.glob('tmp_stamps'+os.sep+'stack_coreg_tmp_*.dim')
                usermessage.ezprint('\t\tRenaming of the stack:',jobifg.log,verbose)
                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                        nbthread=jobifg.computernbthread,
                                        cleancache = constants.__SNAPcacheclean__,
                                        debugmode = constants.__SNAPloggingmode__)
                gptdata.xmlinit()
                for idx, stacki in enumerate(list_stack):
                        gptdata.Read(os.path.abspath(stacki),idx=idx+1)
                if len(list_stack) > 1:
                        usermessage.ezprint('\t\t\tS1-IW merging is required:',jobifg.log,verbose)
                        gptdata.TOPSARMerge()
                gptdata.Write(os.path.abspath('tmp_stamps'+os.sep+'stack_coreg_tmp_full.dim'))
                gptdata.xmlclose()
                gptdata.run(verbose=verbose,log=jobifg.log)
                gptdata.clean()
                usermessage.ezprint('\t\t\tdone',jobifg.log,verbose)

                usermessage.ezprint('\t\tFinalisation of the coregistration stack (cropping if IW):',jobifg.log,verbose)
                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                        nbthread=jobifg.computernbthread,
                        cleancache = constants.__SNAPcacheclean__,
                        debugmode = constants.__SNAPloggingmode__)
                gptdata.xmlinit()
                gptdata.Read(os.path.abspath('tmp_stamps'+os.sep+'stack_coreg_tmp_full.dim'))

                if jobifg.ifgcompute['cropping']['value'] and jobifg.satmode == 'IW':
                        gptdata.generic('Subset',
                                {'copyMetadata': True,
                                'geoRegion': loads(jobifg.roi).wkt})
                        
                para = {'demName': 'External DEM',
                'demResamplingMethod': jobifg.ifgcompute['demResamplingMethod']['value'],
                'externalDEMFile': os.path.abspath(jobifg.pathDEM+os.sep+jobifg.nameDEM),
                'externalDEMNoDataValue': jobifg.ifgcompute['externalDEMNoDataValue']['value']}
                gptdata.generic('AddElevation',
                        para)
                        
                gptdata.Write(os.path.abspath('tmp_stamps'+os.sep+'stack_coreg_stamps.dim'))
                gptdata.xmlclose()
                gptdata.run(verbose=verbose,log=jobifg.log)
                gptdata.clean()
                usermessage.ezprint('\t\t\tdone',jobifg.log,verbose)

                # For the interferogram stack
                usermessage.ezprint('\tProcessing of the interferometric stack (add the elevation band)',jobifg.log,verbose)
                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                        nbthread=jobifg.computernbthread,
                                        cleancache = constants.__SNAPcacheclean__,
                                        debugmode = constants.__SNAPloggingmode__)
                gptdata.xmlinit()
                gptdata.Read(os.path.abspath('stack_diff.dim'))
                gptdata.Write(os.path.abspath('tmp_stamps'+os.sep+'stack_ifg_stamps.dim'))
                gptdata.xmlclose()
                gptdata.run(verbose=verbose,log=jobifg.log)
                gptdata.clean()
                usermessage.ezprint('\t\tdone',jobifg.log,verbose)

                ## Export to StaMPS 
                usermessage.ezprint('Export the datasets to StaMPS in %s:' % (stampsdir),jobifg.log,verbose)
                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                        nbthread=jobifg.computernbthread,
                                        cleancache = constants.__SNAPcacheclean__,
                                        debugmode = constants.__SNAPloggingmode__)
                gptdata.xmlinit()
                gptdata.Read(os.path.abspath('tmp_stamps'+os.sep+'stack_coreg_stamps.dim'),idx=1)
                gptdata.Read(os.path.abspath('tmp_stamps'+os.sep+'stack_ifg_stamps.dim'),idx=2)
                gptdata.StampsExport(stampsdir,True)
                gptdata.xmlclose()
                gptdata.run(verbose=verbose,log=jobifg.log)
                gptdata.clean()
                usermessage.ezprint('\tdone',jobifg.log,verbose)

                if os.path.isdir('tmp_stamps'): 
                        shutil.rmtree('tmp_stamps')


        ## Delete everything
        if jobifg.finalstack['keepgeotiff']['value']:
                listdata = glob.glob('*.bmp') + glob.glob('*.dim') + glob.glob('*.data') + glob.glob('tmp_*')
                for li in listdata:
                        if os.path.isdir(li):
                                shutil.rmtree(li)
                        else:
                                os.remove(li)

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobifg.log)
        os.chdir(cur_dir)
        jobifg.finalstack['done']['value'] = True

        return jobifg 


