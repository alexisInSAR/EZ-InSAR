#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to process coregistration with SNAP processor 

The module allows to process coregistration with SNAP processor from an ``ezinsar.coregistration`` job. 
    
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
import shutil
import sys
import pandas as pd 
import json
import copy
import random
import string
import matplotlib.pyplot as plt

from ezinsar import usermessage
from ezinsar import constants
from ezinsar.eicomponents.processor.snapmodule import snaptools
from ezinsar.eicomponents.sensor.s1module import s1slctools, s1stacktools
from ezinsar.eicomponents.processor.snapmodule import snapgpttools

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

if constants.__SNAP_wrapper__ == 'snappy':
        # Import snappy
        try: 
                sys.path.append(constants.__requirement_SNAP__)
                from esa_snappy import Engine
                configSNAP = Engine.getInstance().getConfig()
                # configSNAP.logLevel(constants.__loggingmode__)
                configSNAP.logLevel('OFF')
                from esa_snappy import jpy
                from esa_snappy import ProductIO, WKTReader
                from esa_snappy import GPF
                from esa_snappy import HashMap
                import dateutil.parser as parser
        except: 
                usermessage.warningmsg(__name__,__name__,__file__,'Impossible to import the SNAPPY python package. Please see if your installation is correct. This message will not be visible in the log.',None,True)

elif constants.__SNAP_wrapper__ == 'gpt':
        a = 'dummy'
        # usermessage.warningmsg(__name__,__name__,__file__,'SNAP will be parameterised with GPT.',None,True)

else:
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                'The SNAP mode must be gpt or snappy',None))

################################################################################
## checkSLC FUNCTION
################################################################################
def checkSLC(jobcoreg, verbose: Optional[bool] = None):
        """Check the SLC files 

        The function checks the SLC files, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()
        if not 'coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,checkSLC.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,checkSLC.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        usermessage.openingmsg(__name__,checkSLC.__name__,__file__,__copyright__,'Coregistration Step: checkSLC (ScanSAR)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        ## Create the work directory
        if not os.path.isdir(jobcoreg.workdirectory):
                os.mkdir(jobcoreg.workdirectory)
        os.chdir(jobcoreg.workdirectory)

        if jobcoreg.satellite == 'S1':
                
                ## List the .zip or SAFE
                filelist = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'*.zip') + glob.glob(jobcoreg.pathSLC+os.sep+'*.SAFE'))
                date = []
                for slci in filelist:
                        datestr = slci.split(os.sep)[-1].split('.')[0].split('_')[5].split('T')[0] #We convert the name of files to date string.
                        usermessage.ezprint('For the file: %s.' %(slci),jobcoreg.log,verbose)   

                        # Check the polarisation (not required because job can check this value)
                        check_sum_pol = 0
                        for poli in jobcoreg.polarisation:
                                try: 
                                        S1annoresults = s1slctools.detectS1annoatationfromxml(slci,poli.upper())
                                        check_sum_pol = check_sum_pol + 1 
                                except:
                                        check_sum_pol = check_sum_pol + 0

                        if check_sum_pol == len(jobcoreg.polarisation):
                                date.append(datetime.datetime.strptime(datestr, '%Y%m%d')) #We add the date in string to our list of date.
                                usermessage.ezprint('\tOkay',jobcoreg.log,verbose)   
                        else:
                                usermessage.warningmsg(__name__,checkSLC.__name__,__file__,'Not required polarisation(s).',jobcoreg.log,verbose)

        #We sort the dates
        date = sorted(date)
        date = np.unique(date)

        #We re-write the list with sorted dates
        usermessage.ezprint('Write the dates file in %s' %(jobcoreg.workdirectory+os.sep+'dates'),jobcoreg.log,verbose) 
        fibis = open(jobcoreg.workdirectory+os.sep+'dates','w')
        for di in date:
            datestr = di.strftime("%Y%m%d")
            fibis.write(datestr+'\n')
        fibis.close()
        
        # Display 
        usermessage.ezprint('There are %d .zip files for %d unique dates.\n' %(len(filelist),len(date)),jobcoreg.log,verbose) 

        os.chdir(cur_dir)
        jobcoreg.checkSLC['done']['value'] = True

        return jobcoreg

################################################################################
## coarserefdate FUNCTION
################################################################################
def coarserefdate(jobcoreg, verbose: Optional[bool] = None):
        """Detection of the best potential reference date

        The function defines the best potential reference date, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()
        
        if not 'coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,coarserefdate.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,coarserefdate.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        usermessage.openingmsg(__name__,coarserefdate.__name__,__file__,__copyright__,'Coregistration Step: coarserefdate (ScanSAR)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.checkSLC['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,coarserefdate.__name__,__file__,__copyright__,
                                'The previous step (checkSLC) is not done.',None))

        if jobcoreg.satellite == 'S1': 

                date_ref, dates_SLC, Btempnorm, Bperpnorm = s1stacktools.commputecoarsenetwork(jobcoreg.pathSLC,jobcoreg.roi,jobcoreg.polarisation[0],
                        pathorbit = jobcoreg.pathorbit,
                        DEM = jobcoreg.pathDEM+os.sep+jobcoreg.nameDEM,
                        figure = jobcoreg.workdirectory+os.sep+'coarse_ifg_network',
                        preref = None,
                        verbose = jobcoreg.verbose, 
                        log = jobcoreg.log, 
                        )     
        else:

                date_ref = None
                dates_SLC = None
                Btempnorm = None
                Bperpnorm = None 
        
        jobcoreg.refdate = datetime.datetime.strftime(date_ref,'%Y%m%d')

        os.chdir(cur_dir)
        jobcoreg.coarserefdate['done']['value'] = True

        return jobcoreg 

################################################################################
## importSLC FUNCTION
################################################################################
def importSLC(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Import the SLCs into a SNAP format

        The function will import the SLC files into a SNAP format, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        
        if not 'coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,importSLC.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,importSLC.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))
        
        usermessage.openingmsg(__name__,importSLC.__name__,__file__,__copyright__,'coregistration Step: importSLC',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.coarserefdate['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,
                                'The previous step (coarserefdate) is not done.',None))
        
        cur_dir = os.getcwd()
        os.chdir(jobcoreg.workdirectory)

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)

        if not os.path.isdir('input_prep'): 
                os.mkdir('input_prep')

        listdate = snaptools.readdatefile('dates')

        ## Processing loop
        for dslc in listdate: 
                usermessage.ezprint('For the date %s' %(dslc),jobcoreg.log,verbose) 

                if (not glob.glob('input_prep'+os.sep+'*'+dslc+'*.dim')) or modeforce == True:

                        ## Import the Product (in case of Sentinel-1 IW)
                        if jobcoreg.satellite == 'S1' and jobcoreg.satmode == 'IW':

                                usermessage.ezprint('\tDetection of Sentinel-1 IW image(s)',jobcoreg.log,verbose) 

                                ## Detection of the different slices
                                pathslctmp = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'*'+dslc+'*'))
                                nb_slice = len(pathslctmp)

                                ## Read the Sentinel-1 slices
                                usermessage.ezprint('\t\tRead the Sentinel-1 slices',jobcoreg.log,verbose) 

                                if constants.__SNAP_wrapper__ == 'snappy':
                                        listproducts = jpy.array('org.esa.snap.core.datamodel.Product', nb_slice)
                                else: 
                                        gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                                nbthread=jobcoreg.computernbthread,
                                                cleancache = constants.__SNAPcacheclean__,
                                                debugmode = constants.__SNAPloggingmode__)
                                        gptdata.xmlinit()
                                        listproducts = []

                                for nbslice, slicei in enumerate(pathslctmp): 

                                        if constants.__SNAP_wrapper__ == 'snappy':
                                                try: 
                                                        listproducts[nbslice] = ProductIO.readProduct(str(slicei))
                                                except: 
                                                        raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: reader.readProductNodes',jobcoreg.log))
                                        else: 
                                                listproducts.append(str(slicei))

                                if constants.__SNAP_wrapper__ == 'gpt':
                                        gptdata.ProductSetReader(listproducts)

                                ## Assemble the Sentinel-1 slices (if required)
                                usermessage.ezprint('\t\tAssemble the Sentinel-1 slices (if required)',jobcoreg.log,verbose)         
                                
                                if constants.__SNAP_wrapper__ == 'snappy':
                                
                                        if len(listproducts) > 1:
                                                operator = 'SliceAssembly'
                                                parameters = HashMap()
                                                parameters.put('selectedPolarisations', jobcoreg.polarisation[0])
                                                try: 
                                                        imageSLC_ass = GPF.createProduct(operator,
                                                                                parameters, 
                                                                                listproducts)
                                                except: 
                                                        raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: SliceAssembly',jobcoreg.log))
                                        else: 
                                                imageSLC_ass = listproducts[0]
                                        imageSLC = imageSLC_ass # For consistency

                                else: 
                                        if len(listproducts) > 1:
                                                gptdata.SliceAssembly(jobcoreg.polarisation)

                                ## Split
                                usermessage.ezprint('\tDetection of the subwaths and bursts required for splitting',jobcoreg.log,verbose) 
                                IW1 = []
                                IW2 = []
                                IW3 = []
                                nbbIW1 = 0
                                nbbIW2 = 0
                                nbbIW3 = 0

                                for nbslice, slicei in enumerate(pathslctmp):
                                        S1annoresults = s1slctools.detectS1annoatationfromxml(slicei,'vv')
                                        burst_roi = s1slctools.detection_S1burst_fromROI(loads(jobcoreg.roi),S1annoresults)
                                        for idx, a in enumerate(burst_roi['iw']):
                                                a = a + 1
                                                if a == 1:
                                                        IW1.append(nbbIW1 + burst_roi['idx'][idx]+1)
                                                elif a == 2:
                                                        IW2.append(nbbIW2 + burst_roi['idx'][idx]+1)   
                                                else:
                                                        IW3.append(nbbIW3 + burst_roi['idx'][idx]+1)
                                        try: 
                                                nbbIW1 = len(S1annoresults['data_xmli1']['burst_loc']['Polygon'])
                                        except: 
                                                nbbIW1 = 0
                                        try: 
                                                nbbIW2 = len(S1annoresults['data_xmli2']['burst_loc']['Polygon'])
                                        except: 
                                                nbbIW2 = 0
                                        try: 
                                                nbbIW3 = len(S1annoresults['data_xmli3']['burst_loc']['Polygon'])
                                        except: 
                                                nbbIW3 = 0
                                        usermessage.ezprint('\t\tdone',jobcoreg.log,verbose) 

                                for idx in [1,2,3]:
                                        gptdataiw = copy.deepcopy(gptdata)

                                        IW = eval('IW%s' % idx)
                                        if IW: 
                                                list_processing = []
                                                usermessage.ezprint('\t\tProcessing of the IW%s' % (idx),jobcoreg.log,verbose) 
                                                
                                                ## TOPSAR-Split
                                                usermessage.ezprint('\t\t\tTOPSAR-Split',jobcoreg.log,verbose) 

                                                if constants.__SNAP_wrapper__ == 'snappy':

                                                        operator = 'TOPSAR-Split'
                                                        parameters = HashMap()
                                                        parameters.put('subswath',  'IW%s' % (idx))
                                                        parameters.put('firstBurstIndex', str(np.min(IW)))
                                                        parameters.put('lastBurstIndex', str(np.max(IW)))
                                                        try: 
                                                                imageSLC_split = GPF.createProduct(operator,
                                                                        parameters, 
                                                                        imageSLC)
                                                        except: 
                                                                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: TOPSAR-Split',jobcoreg.log))
                                                        
                                                        list_processing.append('imageSLC_split')
                                                        usermessage.ezprint('\t\t\t\tdone',jobcoreg.log,verbose) 

                                                else: 
                                                        gptdataiw.TOPSARSplit(idx,np.min(IW),np.max(IW))
                                                
                                                usermessage.ezprint('\t\t\t\tdone',jobcoreg.log,verbose) 

                                                ## Apply the orbits
                                                if jobcoreg.importSLC['applyorbit']['value'] == True:
                                                        usermessage.ezprint('\t\t\tApply the orbit files (for Sentinel-1):',jobcoreg.log,verbose) 

                                                        if constants.__SNAP_wrapper__ == 'snappy':
                                                                operator = 'Apply-Orbit-File'

                                                                parameters = HashMap()
                                                                parameters.put('orbitType', 'Sentinel Precise (Auto Download)')
                                                                parameters.put('polyDegree', '3')
                                                                parameters.put('continueOnFail', True)

                                                                usermessage.ezprint('\t\t\t\tTry the precise orbit files...',jobcoreg.log,verbose)  
                                                                last_image = eval('%s' % (list_processing[-1]))
                                                                try: 
                                                                        imageSLC_orbit = GPF.createProduct(operator,
                                                                                parameters, 
                                                                                last_image)
                                                                except: 
                                                                        raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: SliceAssembly',jobcoreg.log))

                                                                list_processing.append('imageSLC_orbit')

                                                        else: 
                                                                gptdataiw.ApplyOrbitFile()

                                                        usermessage.ezprint('\t\t\t\tdone',jobcoreg.log,verbose) 

                                                # Writting 
                                                usermessage.ezprint('\t\tRun the processing',jobcoreg.log,verbose) 
                                                
                                                if constants.__SNAP_wrapper__ == 'snappy':
                                                        try: 
                                                                usermessage.ezprint('\t\tWrite the file',jobcoreg.log,verbose)
                                                                last_image = eval('%s' % (list_processing[-1]))
                                                                ProductIO.writeProduct(last_image, 'input_prep'+os.sep+dslc+'_IW'+str(idx), 'BEAM-DIMAP')
                                                                usermessage.ezprint('\t\t\tdone',jobcoreg.log,verbose) 
                                                        except:
                                                                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: writeProduct',jobcoreg.log))
                                                
                                                else: 
                                                        gptdataiw.Write(os.path.abspath('input_prep'+os.sep+dslc+'_IW'+str(idx)))
                                                        gptdataiw.xmlclose()
                                                        gptdataiw.run(verbose=verbose,log=jobcoreg.log)

                                                # Clean the variable 
                                                if constants.__SNAP_wrapper__ == 'snappy':
                                                        for producti in list_processing:
                                                                last_image = eval('%s' % (producti))
                                                                last_image.dispose()
                                                                last_image.closeIO()
                                                                del last_image
                                                else:
                                                        gptdataiw.clean()
                                                        gptdataiw = None 

                        if constants.__SNAP_wrapper__ == 'snappy':
                                imageSLC.dispose()
                                imageSLC.closeIO()
                                imageSLC_ass.dispose()
                                imageSLC_ass.closeIO()
                                del imageSLC
                                del imageSLC_ass

                                for li in listproducts: 
                                        li.dispose()
                                        li.closeIO()
                                del li
                        else: 
                                gptdata.clean()
                                gptdata = None 

                else: 
                        usermessage.warningmsg(__name__,importSLC.__name__,__file__,'The file %s is already processed.' % (dslc),jobcoreg.log,verbose)

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)

        if jobcoreg.importSLC['createbmp']['value']:

                usermessage.ezprint('Creation of .bmp images',jobcoreg.log,verbose) 
                for dslc in listdate: 
                        usermessage.ezprint('\tFor the date %s' %(dslc),jobcoreg.log,verbose) 

                        if (not os.path.isfile('input_prep'+os.sep+dslc+'.'+jobcoreg.polarisation[0].lower()+'.mli.bmp')) or modeforce == True: 

                                if jobcoreg.satellite == 'S1' and jobcoreg.satmode == 'IW':
                                        IW = snaptools.detectIW(jobcoreg.workdirectory+os.sep+'input_prep',date=jobcoreg.refdate)

                                        listfile = glob.glob('input_prep'+os.sep+'*'+dslc+'*.data')
                                        
                                        snaptools.createbmpmosaic(listfile,
                                                'input_prep'+os.sep+dslc+'.'+jobcoreg.polarisation[0].lower()+'.mli.bmp',
                                                jobcoreg.mlrandisplay, 
                                                jobcoreg.mlazidisplay,
                                                verbose = False,
                                                log = jobcoreg.log)
                                        
                                usermessage.ezprint('\t\tdone',jobcoreg.log,verbose) 

        jobcoreg.importSLC['done']['value'] = True
        snaptools.snapclearcache(verbose=False,log=jobcoreg.log)
        os.chdir(cur_dir)

        return jobcoreg 

################################################################################
## refinerefdate FUNCTION
################################################################################
def refinerefdate(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Refine the reference date

        The function will refine the reference date, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        
        if not 'coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,refinerefdate.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,refinerefdate.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,refinerefdate.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))
        
        usermessage.openingmsg(__name__,refinerefdate.__name__,__file__,__copyright__,'Coregistration Step: refinerefdate (ScanSAR)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.importSLC['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,refinerefdate.__name__,__file__,__copyright__,
                                'The previous step (importSLC) is not done.',None))
        
        cur_dir = os.getcwd()
        os.chdir(jobcoreg.workdirectory+os.sep+'input_prep')

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)

        IW = snaptools.detectIW(jobcoreg.workdirectory+os.sep+'input_prep',date=jobcoreg.refdate)

        if jobcoreg.refinerefdate['process']['value'] == True:

                usermessage.warningmsg(__name__,refinerefdate.__name__,__file__,'The %s will be used.' % (IW[0]),jobcoreg.log,verbose)
    
                listdate = snaptools.readdatefile('..'+os.sep+'dates')
                stackproduct = []

                try: 
                        ## Processing
                        for dslc in listdate: 
                                usermessage.ezprint('Add the date %s' %(dslc),jobcoreg.log,verbose) 
                                if constants.__SNAP_wrapper__ == 'snappy':
                                        stackproduct.append(ProductIO.readProduct(dslc+'_'+IW[0]+'.dim'))
                                else:
                                        stackproduct.append(os.path.abspath(dslc+'_'+IW[0]+'.dim'))

                        if constants.__SNAP_wrapper__ == 'snappy':
                                operator = 'InSAR-Overview'
                                parameters = HashMap()
                                parameters.put('overviewJSONFile',jobcoreg.workdirectory+os.sep+'masterselection.json')
                                stack = GPF.createProduct(operator,
                                        parameters,
                                        stackproduct)
                        else: 
                                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                                nbthread=jobcoreg.computernbthread,
                                                cleancache = constants.__SNAPcacheclean__,
                                                debugmode = constants.__SNAPloggingmode__)
                                gptdata.xmlinit()
                                gptdata.ProductSetReader(stackproduct)
                                gptdata.InSAROverview(jobcoreg.workdirectory+os.sep+'masterselection.json')
                                gptdata.xmlclose()
                                gptdata.run(verbose=verbose,log=jobcoreg.log)
                                gptdata.clean()
                                gptdata = None 
                
                except: 
                        raise ValueError(usermessage.errormsg(__name__,refinerefdate.__name__,__file__,__copyright__,'Error in the SNAP processing: InSAR-stack-overview',jobcoreg.log))
                
                # Memoery clean 
                if constants.__SNAP_wrapper__ == 'snappy':
                        for producti in stackproduct:
                                producti.dispose()
                                producti.closeIO()
                        del stackproduct

                        stack.dispose()
                        stack.closeIO()
                        del stack

                # Read the results
                with open(jobcoreg.workdirectory+os.sep+'masterselection.json') as fi:
                        data = json.load(fi)

                if os.path.isfile(jobcoreg.workdirectory+os.sep+'masterselection.json'):
                        os.remove(jobcoreg.workdirectory+os.sep+'masterselection.json')

                dfmaster = pd.json_normalize(data['reference'])
                dfsec = pd.json_normalize(data['secondary'])
                dateref = datetime.datetime.strptime(dfmaster['start_time'][0].split(' ')[0],"%d-%b-%Y").strftime("%Y%m%d")

                usermessage.ezprint('The best potential date should be %s' % (dateref),jobcoreg.log,verbose)

                if not jobcoreg.refdate == dateref: 
                        usermessage.warningmsg(__name__,refinerefdate.__name__,__file__,'The reference date is not the same used previously. We will modify the value.',jobcoreg.log,verbose)

                jobcoreg.refdate = dateref 

                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)

        else: 
                usermessage.warningmsg(__name__,refinerefdate.__name__,__file__,'This step is not enabled',jobcoreg.log,verbose)

        jobcoreg.refinerefdate['done']['value'] = True
        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)
        os.chdir(cur_dir)

        return jobcoreg

################################################################################
## coreg FUNCTION
################################################################################
def coreg(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Coregistration of the stack

        The function will coregistre the stack, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,coreg.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,coreg.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,coreg.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))
        
        usermessage.openingmsg(__name__,coreg.__name__,__file__,__copyright__,'Coregistration Step: coreg (ScanSAR)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.importSLC['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,coreg.__name__,__file__,__copyright__,
                                'The previous step (importSLC) is not done.',None))
        
        if not os.path.isdir(jobcoreg.workdirectory+os.sep+'stack'): 
                os.mkdir(jobcoreg.workdirectory+os.sep+'stack')

        os.chdir(jobcoreg.workdirectory+os.sep+'stack')
        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)

        IW = snaptools.detectIW(jobcoreg.workdirectory+os.sep+'input_prep',date=jobcoreg.refdate)
        listdate = snaptools.readdatefile('..'+os.sep+'dates')
        listdate.reverse()

        for iwi in IW: 

                if (not os.path.isfile('stack_'+iwi+'.dim')) or modeforce == True:

                        usermessage.ezprint('Run the coregistration of the %s stack' % (iwi),jobcoreg.log,verbose)
                        
                        stackproduct = []

                        for dslc in listdate: 
                                if not dslc == jobcoreg.refdate:
                                        usermessage.ezprint('\tAdd the date %s' %(dslc),jobcoreg.log,verbose)
                                        if constants.__SNAP_wrapper__ == 'snappy': 
                                                stackproduct.append(ProductIO.readProduct(jobcoreg.workdirectory+os.sep+'input_prep'+os.sep+dslc+'_'+iwi+'.dim'))
                                        else:
                                                stackproduct.append(os.path.abspath(jobcoreg.workdirectory+os.sep+'input_prep'+os.sep+dslc+'_'+iwi+'.dim'))

                        usermessage.ezprint('\tAdd the reference date %s' %(jobcoreg.refdate),jobcoreg.log,verbose) 
                        if len(listdate) > 2: 
                                if constants.__SNAP_wrapper__ == 'snappy':
                                        stackproduct.insert(-1,ProductIO.readProduct(jobcoreg.workdirectory+os.sep+'input_prep'+os.sep+jobcoreg.refdate+'_'+iwi+'.dim'))
                                else:
                                        stackproduct.insert(0,os.path.abspath(jobcoreg.workdirectory+os.sep+'input_prep'+os.sep+jobcoreg.refdate+'_'+iwi+'.dim'))

                        else: 
                                if constants.__SNAP_wrapper__ == 'snappy':
                                        stackproduct.insert(-1,ProductIO.readProduct(jobcoreg.workdirectory+os.sep+'input_prep'+os.sep+jobcoreg.refdate+'_'+iwi+'.dim'))
                                else:
                                        stackproduct.insert(0,os.path.abspath(jobcoreg.workdirectory+os.sep+'input_prep'+os.sep+jobcoreg.refdate+'_'+iwi+'.dim'))
                        
                        list_processing = []

                        if not constants.__SNAP_wrapper__ == 'snappy':
                                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                                nbthread=jobcoreg.computernbthread,
                                                cleancache = constants.__SNAPcacheclean__,
                                                debugmode = constants.__SNAPloggingmode__)
                                gptdata.xmlinit()
                                gptdata.ProductSetReader(stackproduct)
                                
                        ## Back-Geocoding
                        try: 
                                if constants.__SNAP_wrapper__ == 'snappy':
                                        operator = 'Back-Geocoding'
                                        parameters = HashMap()
                                        parameters.put('demName', 'External DEM')
                                        parameters.put('externalDEMFile',jobcoreg.pathDEM+os.sep+jobcoreg.nameDEM)
                                        parameters.put('externalDEMNoDataValue', jobcoreg.coreg['externalDEMNoDataValue']['value'])
                                        parameters.put('demResamplingMethod', jobcoreg.coreg['demResamplingMethod']['value'])
                                        parameters.put('imgResamplingMethod', jobcoreg.coreg['resamplingType']['value'])
                                        parameters.put('maskOutAreaWithoutElevation', str(jobcoreg.coreg['maskOutAreaWithoutElevation']['value']))
                                        parameters.put('disableReramp', str(jobcoreg.coreg['disableReramp']['value']))
                                
                                        stackcoreg = GPF.createProduct(operator,
                                                parameters,
                                                stackproduct)
                                else:
                                        para = {'demName': 'External DEM',
                                                'demResamplingMethod': jobcoreg.coreg['demResamplingMethod']['value'],
                                                'externalDEMFile': os.path.abspath(jobcoreg.pathDEM+os.sep+jobcoreg.nameDEM),
                                                'externalDEMNoDataValue': jobcoreg.coreg['externalDEMNoDataValue']['value'],
                                                'resamplingType': jobcoreg.coreg['resamplingType']['value'],
                                                'maskOutAreaWithoutElevation': jobcoreg.coreg['maskOutAreaWithoutElevation']['value'],
                                                'disableReramp': jobcoreg.coreg['disableReramp']['value']}
                                        gptdata.generic('Back-Geocoding',para)
                                
                                list_processing.append('stackcoreg')
                        
                        except: 
                                raise ValueError(usermessage.errormsg(__name__,coreg.__name__,__file__,__copyright__,'Error in the SNAP processing: Back-Geocoding',jobcoreg.log))
                        
                        # Enhanced-Spectral-Diversity
                        if jobcoreg.coreg['ESDcomputation']['value']:
                                try:
                                        if constants.__SNAP_wrapper__ == 'snappy':
                                                operator = 'Enhanced-Spectral-Diversity'
                                                parameters = HashMap()

                                                for parai in ['fineWinWidthStr',
                                                        'fineWinHeightStr',
                                                        'fineWinAccAzimuth',
                                                        'fineWinAccRange',
                                                        'fineWinOversampling',
                                                        'xCorrThreshold',
                                                        'cohThreshold',
                                                        'numBlocksPerOverlap',
                                                        'esdEstimator',
                                                        'weightFunc',
                                                        'temporalBaselineType',
                                                        'maxTemporalBaseline',
                                                        'integrationMethod',
                                                        'doNotWriteTargetBands', 
                                                        'useSuppliedRangeShift',
                                                        'overallRangeShift',
                                                        'useSuppliedAzimuthShift',
                                                        'overallAzimuthShift']:

                                                        if jobcoreg.coreg[parai]['format'] in ['int','float']: 
                                                                parameters.put(parai,str(jobcoreg.coreg[parai]['value']))
                                                        else:
                                                                parameters.put(parai,jobcoreg.coreg[parai]['value'])

                                                last_image = eval('%s' % (list_processing[-1]))

                                                stackcoregesd = GPF.createProduct(operator,
                                                        parameters,
                                                        last_image)
                                        else:
                                                para = {}
                                                for parai in ['fineWinWidthStr',
                                                        'fineWinHeightStr',
                                                        'fineWinAccAzimuth',
                                                        'fineWinAccRange',
                                                        'fineWinOversampling',
                                                        'xCorrThreshold',
                                                        'cohThreshold',
                                                        'numBlocksPerOverlap',
                                                        'esdEstimator',
                                                        'weightFunc',
                                                        'temporalBaselineType',
                                                        'maxTemporalBaseline',
                                                        'integrationMethod',
                                                        'doNotWriteTargetBands', 
                                                        'useSuppliedRangeShift',
                                                        'overallRangeShift',
                                                        'useSuppliedAzimuthShift',
                                                        'overallAzimuthShift']:
                                                        para[parai] = jobcoreg.coreg[parai]['value']

                                                gptdata.generic('Enhanced-Spectral-Diversity',para)

                                        list_processing.append('stackcoregesd')

                                except: 
                                        raise ValueError(usermessage.errormsg(__name__,coreg.__name__,__file__,__copyright__,'Error in the SNAP processing: Enhanced-Spectral-Diversity',jobcoreg.log))

                        # Writting 
                        try: 
                                if constants.__SNAP_wrapper__ == 'snappy':
                                        usermessage.ezprint('\t\tWrite the file',jobcoreg.log,verbose)
                                        last_image = eval('%s' % (list_processing[-1]))
                                        ProductIO.writeProduct(last_image, 'stack_'+iwi, 'BEAM-DIMAP')
                                        usermessage.ezprint('\t\t\tdone',jobcoreg.log,verbose) 
                                else:
                                        gptdata.Write(os.path.abspath(jobcoreg.pathstack+os.sep+'stack_'+iwi))
                                        gptdata.xmlclose()
                                        gptdata.run(verbose=verbose,log=jobcoreg.log)
                                        gptdata.clean()
                        except:
                                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: writeProduct',jobcoreg.log))

                        # Memory cleaning
                        if constants.__SNAP_wrapper__ == 'snappy':
                                for sti in stackproduct:
                                        sti.dispose()
                                        sti.closeIO()
                                del stackproduct

                                stackcoreg.dispose()
                                stackcoreg.closeIO()
                                del stackcoreg

                                if jobcoreg.coreg['ESDcomputation']['value']:
                                        stackcoregesd.dispose()
                                        stackcoregesd.closeIO()
                                        del stackcoregesd
                        else:
                                gptdata = None 
        
                else: 
                        usermessage.warningmsg(__name__,coreg.__name__,__file__,'The file %s is already computed.' % ('stack_'+iwi+'.dim'),jobcoreg.log,verbose)

        if jobcoreg.coreg['createbmpifg']['value']:

                usermessage.ezprint('Creation of .bmp images for the interferograms',jobcoreg.log,verbose) 
                IW = snaptools.detectIW(jobcoreg.pathstack)
                listdate = snaptools.readdatefile('..'+os.sep+'dates')

                for dslc in listdate: 
                        if not dslc == jobcoreg.refdate:

                                usermessage.ezprint('\tFor the interferogram %s - %s' % (jobcoreg.refdate,dslc),jobcoreg.log,verbose)

                                a = datetime.datetime.strptime(jobcoreg.refdate, "%Y%m%d").strftime('%d%b%Y')
                                b = datetime.datetime.strptime(dslc, "%Y%m%d").strftime('%d%b%Y')

                                listimage = []
                                for iwi in IW: 
                                
                                        realfilemaster = glob.glob(jobcoreg.pathstack+os.sep+'stack_'+iwi+'.data'+os.sep+'q*'+jobcoreg.polarisation[0].upper()+'*mst*'+a+'*.img')[0]
                                        imagfilemaster = glob.glob(jobcoreg.pathstack+os.sep+'stack_'+iwi+'.data'+os.sep+'i*'+jobcoreg.polarisation[0].upper()+'*mst*'+a+'*.img')[0]    

                                        realfileslave = glob.glob(jobcoreg.pathstack+os.sep+'stack_'+iwi+'.data'+os.sep+'q*'+jobcoreg.polarisation[0].upper()+'*slv*'+b+'*.img')[0]
                                        imagfileslave = glob.glob(jobcoreg.pathstack+os.sep+'stack_'+iwi+'.data'+os.sep+'i*'+jobcoreg.polarisation[0].upper()+'*slv*'+b+'*.img')[0] 

                                        tmpfile = constants.__cachedir__+os.sep+'tmp_'+''.join(random.choice(string.ascii_lowercase) for i in range(16))+'.bmp'

                                        snaptools.createifgbmpnocorrection([realfilemaster, imagfilemaster],[realfileslave, imagfileslave],
                                                tmpfile,
                                                jobcoreg.mlrandisplay, 
                                                jobcoreg.mlazidisplay,
                                                colormap = 'sar',
                                                verbose= False,
                                                log = jobcoreg.log,
                                                ) 
                                        
                                        listimage.append(tmpfile)

                                fig, axs = plt.subplots(1, len(listimage))    
                                h = 1   
                                for ax, li in zip(axs.flat,listimage): 
                                        im = plt.imread(li)
                                        ax.imshow(im)
                                        ax.set_title('IW%s' % (h))
                                        h = h + 1

                                fig.canvas._print_pil(jobcoreg.refdate+'_'+jobcoreg.polarisation[0].lower()+'_'+dslc+'_'+jobcoreg.polarisation[0].lower()+'.int.bmp', fmt = 'BMP', pil_kwargs={'dpi': [450,450]})

                                for li in listimage: 
                                        if os.path.isfile(li):
                                                os.remove(li)    
                        
                usermessage.ezprint('\t\tdone',jobcoreg.log,verbose) 

        jobcoreg.coreg['done']['value'] = True
        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)
        os.chdir(cur_dir)

        return jobcoreg

################################################################################
## cleanstack FUNCTION
################################################################################
def cleanstack(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Clean the work directory

        The function will clean the work directory, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,cleanstack.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,cleanstack.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,cleanstack.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))
        
        usermessage.openingmsg(__name__,coreg.__name__,__file__,__copyright__,'Coregistration Step: cleanstack (ScanSAR)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.coreg['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,cleanstack.__name__,__file__,__copyright__,
                                'The previous step (coreg) is not done.',None))
        
        os.chdir(jobcoreg.workdirectory)
        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)

        if jobcoreg.cleanstack['process']['value']: 
                
                if jobcoreg.cleanstack['keepinputfiles']['value'] == False:
                        if os.path.isdir(jobcoreg.workdirectory+os.sep+'input_prep'):
                                shutil.rmtree(jobcoreg.workdirectory+os.sep+'input_prep')
                
                if os.path.isdir(jobcoreg.workdirectory+os.sep+'stack'):
                        shutil.rmtree(jobcoreg.workdirectory+os.sep+'stack')

                if os.path.isfile(jobcoreg.workdirectory+os.sep+'coarse_ifg_network.jpg'):
                        os.remove(jobcoreg.workdirectory+os.sep+'coarse_ifg_network.jpg')

                if os.path.isfile(jobcoreg.workdirectory+os.sep+'dates'):
                        os.remove(jobcoreg.workdirectory+os.sep+'dates')

        jobcoreg.cleanstack['done']['value'] = True
        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)
        os.chdir(cur_dir)

        return jobcoreg
