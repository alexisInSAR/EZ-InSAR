#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to process Intensity data with SNAP processor 

The module allows to process Intensity data with SNAP processor 
from an ``ezinsar.intstack`` job. 
    
    (From `ezinsar` package)

Note: 
        RAM memory optimisation needs to be done!

Changelog:
        * 1.2.1: Change the import line, Dec. 2025, Alexis Hrysiewicz
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
from osgeo import gdal
import sys

from ezinsar import usermessage
from ezinsar import constants
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""
from ezinsar.eicomponents.processor.snapmodule import snaptools
from ezinsar.eicomponents.sensor.s1module import s1slctools

# # Import snappy
# try: 
#         sys.path.append(constants.__requirement_SNAP__)
#         from esa_snappy import Engine
#         configSNAP = Engine.getInstance().getConfig()
#         # configSNAP.logLevel(constants.__loggingmode__)
#         configSNAP.logLevel('OFF')
#         from esa_snappy import jpy
#         from esa_snappy import ProductIO, WKTReader
#         from esa_snappy import GPF
#         from esa_snappy import HashMap
#         import dateutil.parser as parser
# except: 
#         usermessage.warningmsg(__name__,__name__,__file__,'Impossible to import the SNAPPY python package. Please see if your installation is correct. This message will not be visible in the log.',None,True)

################################################################################
## checkSLC FUNCTION
################################################################################
def checkSLC(jobint, verbose: Optional[bool] = None):
        """Check the SLC files 

        The function checks the SLC files, from an ``ezinsar.intstack``.   

        Args:
                jobint (``ezinsar.intstack``): EZ-InSAR intstack job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.intstack``: Return an EZ-InSAR intstack class
        
        """
        cur_dir = os.getcwd()
        if not 'snapintstack.intstack' in str(type(jobint)):
                raise ValueError(usermessage.errormsg(__name__,checkSLC.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobint.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,checkSLC.__name__,__file__,__copyright__,
                        'verbose','True or False',jobint.log))
        
        usermessage.openingmsg(__name__,checkSLC.__name__,__file__,__copyright__,'intstack Step: checkSLC',jobint.log,verbose)

        jobint.check(verbose=False,mode='high')

        ## Create the work directory
        if not os.path.isdir(jobint.workdirectory):
                os.mkdir(jobint.workdirectory)
        os.chdir(jobint.workdirectory)

        if jobint.satellite == 'S1':
                
                ## List the .zip or SAFE
                filelist = np.sort(glob.glob(jobint.pathSLC+os.sep+'*.zip') + glob.glob(jobint.pathSLC+os.sep+'*.SAFE'))
                date = []
                for slci in filelist:
                        datestr = slci.split(os.sep)[-1].split('.')[0].split('_')[5].split('T')[0] #We convert the name of files to date string.
                        usermessage.ezprint('For the file: %s.' %(slci),jobint.log,verbose)   

                        # Check the polarisation (not required because job can check this value)
                        check_sum_pol = 0
                        for poli in jobint.polarisation:
                                try: 
                                        S1annoresults = s1slctools.detectS1annoatationfromxml(slci,poli.upper())
                                        check_sum_pol = check_sum_pol + 1 
                                except:
                                        check_sum_pol = check_sum_pol + 0

                        if check_sum_pol == len(jobint.polarisation):
                                date.append(datetime.datetime.strptime(datestr, '%Y%m%d')) #We add the date in string to our list of date.
                                usermessage.ezprint('\tOkay',jobint.log,verbose)   
                        else:
                                usermessage.warningmsg(__name__,checkSLC.__name__,__file__,'Not required polarisation(s).',jobint.log,verbose)

        #We sort the dates
        # Add the previous images (two ways for updating)
        predates = []
        if os.path.isdir(jobint.workdirectory+os.sep+'geotiff'):
                listgeotiff = glob.glob(jobint.workdirectory+os.sep+'geotiff'+os.sep+'*.tif')
                for di in listgeotiff:
                        predates.append(datetime.datetime.strptime(di.split(os.sep)[-1].split('.')[0], '%Y%m%d'))

        date = sorted(date + predates)
        date = np.unique(date)

        #We re-write the list with sorted dates
        usermessage.ezprint('Write the dates files in %s' %(jobint.workdirectory+os.sep+'dates'),jobint.log,verbose) 
        fibis = open(jobint.workdirectory+os.sep+'dates','w')
        for di in date:
            datestr = di.strftime("%Y%m%d")
            fibis.write(datestr+'\n')
        fibis.close()
        
        # Display 
        usermessage.ezprint('There are %d .zip files for %d unique dates (can be already processed).\n' %(len(filelist),len(date)),jobint.log,verbose) 

        os.chdir(cur_dir)
        jobint.checkSLC['done']['value'] = True

        return jobint

################################################################################
## importSLC FUNCTION
################################################################################
def importSLC(jobint, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Import the SLCs into a SNAP format (and calibration)

        The function will import the SLC files into a SNAP format, from an ``ezinsar.intstack``.   

        Args:
                jobint (``ezinsar.intstack``): EZ-InSAR intstack job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.intstack``: Return an EZ-InSAR intstack class
        
        """
        
        if not 'snapintstack.intstack' in str(type(jobint)):
                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobint.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,importSLC.__name__,__file__,__copyright__,
                        'verbose','True or False',jobint.log))

        if modeforce == None:
                modeforce = jobint.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,importSLC.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobint.log))
        
        usermessage.openingmsg(__name__,importSLC.__name__,__file__,__copyright__,'intstack Step: importSLC',jobint.log,verbose)

        jobint.check(verbose=False,mode='high')

        if jobint.checkSLC['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,
                                'The previous step (checkSLC) is not done.',None))
        
        cur_dir = os.getcwd()
        os.chdir(jobint.workdirectory)
        snaptools.snapclearcache(verbose=False,log=jobint.log)

        if not os.path.isdir('input_prep'): 
                os.mkdir('input_prep')

        listdate = snaptools.readdatefile('dates')

        ## Processing loop
        for dslc in listdate: 
                usermessage.ezprint('For the date %s' %(dslc),jobint.log,verbose) 

                if ((not os.path.isfile('input_prep'+os.sep+dslc+'.dim')) and (not glob.glob('geotiff'+os.sep+dslc+'*.tif'))) or modeforce == True:

                        ## Import the Product (in case of Sentinel-1 IW)
                        if jobint.satellite == 'S1' and jobint.satmode == 'IW':

                                usermessage.ezprint('\tDetection of Sentinel-1 IW image(s)',jobint.log,verbose) 

                                # Impossible to use the reader...
                                ## Import the reader
                                # reader = ProductIO.getProductReader("SENTINEL-1")
                                # listproducts[nbslice] = reader.readProductNodes(str(slicei), None)

                                ## Detection of the different slices
                                pathslctmp = np.sort(glob.glob(jobint.pathSLC+os.sep+'*'+dslc+'*'))
                                nb_slice = len(pathslctmp)

                                ##Assembly the slices
                                usermessage.ezprint('\t\tAssembly the slices (if required)',jobint.log,verbose) 
                                listproducts = jpy.array('org.esa.snap.core.datamodel.Product', nb_slice)

                                for nbslice, slicei in enumerate(pathslctmp): 
                                        try: 
                                                listproducts[nbslice] = ProductIO.readProduct(str(slicei))
                                        except: 
                                                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: reader.readProductNodes',jobint.log))

                                operator = 'SliceAssembly'
                                parameters = HashMap()
                                # parameters.put('selectedPolarisations', None)
                                if len(listproducts) > 1:
                                        try: 
                                                imageSLC_ass = GPF.createProduct(operator,
                                                                        parameters, 
                                                                        listproducts)
                                        except: 
                                                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: SliceAssembly',jobint.log))
                                else: 
                                        imageSLC_ass = listproducts[0]

                                ## Thermal noise
                                if jobint.importSLC['removenoise']['value'] == True:
                                        usermessage.ezprint('\t\tRemove the thermal noise for Sentinel-1',jobint.log,verbose) 

                                        operator = 'ThermalNoiseRemoval'

                                        parameters = HashMap()
                                        # parameters.put('selectedPolarisations',  pol)
                                        # parameters.put('outputNoise', 'false')
                                        # parameters.put('removeThermalNoise', 'true')
                                        # parameters.put('reIntroduceThermalNoise', 'false')

                                        try: 
                                                imageSLC_noiserev = GPF.createProduct(operator,
                                                        parameters, 
                                                        imageSLC_ass)
                                        except: 
                                                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: ThermalNoiseRemoval',jobint.log))

                                        usermessage.ezprint('\t\t\tdone',jobint.log,verbose) 
                                        imageSLC = imageSLC_noiserev # Modification for consistency

                                ## Split
                                usermessage.ezprint('\tDetection of the subwaths and bursts required',jobint.log,verbose) 

                                IW1 = []
                                IW2 = []
                                IW3 = []
                                nbbIW1 = 0
                                nbbIW2 = 0
                                nbbIW3 = 0

                                for nbslice, slicei in enumerate(pathslctmp):
                                        S1annoresults = s1slctools.detectS1annoatationfromxml(slicei,'vv')
                                        burst_roi = s1slctools.detection_S1burst_fromROI(loads(jobint.roi),S1annoresults)

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

                                        usermessage.ezprint('\t\tdone',jobint.log,verbose) 

                                pol = ''
                                for poli in jobint.polarisation:
                                        pol = pol + poli.lower()+','

                                for idx in [1,2,3]:
                                        IW = eval('IW%s' % idx)
                                        if IW: 
                                                list_processing = []
                                                usermessage.ezprint('\t\tProcessing of the IW%s' % (idx),jobint.log,verbose) 

                                                usermessage.ezprint('\t\t\tTOPSAR-Split',jobint.log,verbose) 
                                                operator = 'TOPSAR-Split'

                                                parameters = HashMap()
                                                parameters.put('subswath',  'IW%s' % (idx))
                                                parameters.put('selectedPolarisations', pol)
                                                parameters.put('firstBurstIndex', str(np.min(IW)))
                                                parameters.put('lastBurstIndex', str(np.max(IW)))

                                                try: 
                                                        imageSLC_split = GPF.createProduct(operator,
                                                                parameters, 
                                                                imageSLC)
                                                except: 
                                                        raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: TOPSAR-Split',jobint.log))

                                                list_processing.append('imageSLC_split')
                                                usermessage.ezprint('\t\t\t\tdone',jobint.log,verbose) 

                                                ## Apply the orbits
                                                if jobint.importSLC['applyorbit']['value'] == True:
                                                        usermessage.ezprint('\t\t\tApply the orbit files (for Sentinel-1):',jobint.log,verbose) 

                                                        operator = 'Apply-Orbit-File'

                                                        parameters = HashMap()
                                                        parameters.put('orbitType', 'Sentinel Precise (Auto Download)')
                                                        parameters.put('polyDegree', '3')
                                                        parameters.put('continueOnFail', False)

                                                        usermessage.ezprint('\t\t\t\tTry the precise orbit files...',jobint.log,verbose)  
                                                        precise_orbit=False
                                                        last_image = eval('%s' % (list_processing[-1]))
                                                        try: 
                                                                imageSLC_orbit = GPF.createProduct(operator,
                                                                        parameters, 
                                                                        last_image)
                                                                precise_orbit = True 
                                                        except: 
                                                                precise_orbit = False

                                                        if precise_orbit == False:
                                                                precise_restitued = False
                                                                usermessage.ezprint('\t\t\t\tTry the restitued orbit files...',jobint.log,verbose)  
                                                                last_image = eval('%s' % (list_processing[-1]))

                                                                parameters = HashMap()
                                                                parameters.put('orbitType', 'Sentinel Restitued (Auto Download)')
                                                                parameters.put('polyDegree', '3')
                                                                parameters.put('continueOnFail', False)

                                                                try: 
                                                                        imageSLC_orbit = GPF.createProduct(operator,
                                                                                parameters, 
                                                                                last_image)
                                                                        precise_restitued = True 
                                                                except: 
                                                                        precise_restitued = False

                                                        if precise_orbit == True: 
                                                                usermessage.ezprint('\t\t\t\tApplication of precise orbits: done',jobint.log,verbose) 
                                                        elif precise_restitued == True: 
                                                                usermessage.ezprint('\t\t\t\tApplication of restitued orbits: done',jobint.log,verbose)  
                                                        else:
                                                                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'No orbit file found...',jobint.log)) 

                                                        list_processing.append('imageSLC_orbit')
                                                        usermessage.ezprint('\t\t\t\tdone',jobint.log,verbose) 

                                                ## Calibration 
                                                usermessage.ezprint('\t\t\tCalibration',jobint.log,verbose) 

                                                operator = 'Calibration'
                                                last_image = eval('%s' % (list_processing[-1]))

                                                parameters = HashMap()
                                                parameters.put('outputSigmaBand', str(jobint.importSLC['sigma0']['value']))
                                                parameters.put('outputGammaBand', str(jobint.importSLC['gamma0']['value']))
                                                parameters.put('outputBetaBand', 'true')
                                                parameters.put('selectedPolarisations', pol)

                                                try: 
                                                        imageSLC_cal = GPF.createProduct(operator,
                                                                                parameters, 
                                                                                last_image)
                                                except: 
                                                        raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: Calibration',jobint.log))

                                                list_processing.append('imageSLC_cal')
                                                usermessage.ezprint('\t\t\tdone',jobint.log,verbose) 

                                                ##De-burst 
                                                usermessage.ezprint('\t\t\tDe-burst the SLC',jobint.log,verbose) 

                                                operator = 'TOPSAR-Deburst'
                                                last_image = eval('%s' % (list_processing[-1]))

                                                parameters = HashMap()
                                                parameters.put('selectedPolarisations', None)

                                                try: 
                                                        imageSLC_deburst = GPF.createProduct(operator,
                                                                                parameters, 
                                                                                last_image)
                                                except: 
                                                        raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: TOPSAR-Deburst',jobint.log))

                                                list_processing.append('imageSLC_deburst')
                                                usermessage.ezprint('\t\t\tdone',jobint.log,verbose) 

                                                # Writting 
                                                try: 
                                                        usermessage.ezprint('\t\tWrite the file',jobint.log,verbose)
                                                        last_image = eval('%s' % (list_processing[-1]))
                                                        ProductIO.writeProduct(last_image, 'input_prep'+os.sep+dslc+'_IW'+str(idx), 'BEAM-DIMAP')
                                                        usermessage.ezprint('\t\t\tdone',jobint.log,verbose) 
                                                except:
                                                        raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: writeProduct',jobint.log))

                                                # imageSLC = None 
                                                # imageSLC_deburst = None 
                                                # imageSLC_orbit = None 
                                                # imageSLC_split = None 
                                                # imageSLC_ass = None 
                                                # imageSLC_noiserev = None 

                                ## Merge the subwaths
                                usermessage.ezprint('\t\tMerge the subswaths',jobint.log,verbose) 

                                listiw = glob.glob('input_prep'+os.sep+dslc+'_IW*.dim')

                                listproducts = []
                                for li in listiw: 
                                        try: 
                                                listproducts.append(ProductIO.readProduct(li))
                                        except: 
                                                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: reader.readProductNodes',jobint.log))
                                
                                operator = 'TOPSAR-Merge'
                                parameters = HashMap()
                                # parameters.put('selectedPolarisations', None)

                                if len(listiw)>1: 
                                        try: 
                                                imageSLC_merged = GPF.createProduct(operator,
                                                                        parameters, 
                                                                        listproducts)
                                        except: 
                                                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: TOPSAR-Merge',jobint.log))
                                else: 
                                        imageSLC_merged = listproducts[0]

                                try: 
                                        usermessage.ezprint('\t\tWrite the file',jobint.log,verbose)
                                        ProductIO.writeProduct(imageSLC_merged, 'input_prep'+os.sep+dslc+'_full', 'BEAM-DIMAP')
                                        usermessage.ezprint('\t\t\tdone',jobint.log,verbose)
                                except:
                                        raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: writeProduct',jobint.log))

                                imageSLC_merged = None 
                                listproducts = None 
                                

                        ## Cropping or not
                        usermessage.ezprint('\tCropping based on the ROI (not available for S1 IW images):',jobint.log,verbose)

                        imageSLC = ProductIO.readProduct('input_prep'+os.sep+dslc+'_full.dim')
                        
                        operator = 'Subset'
                        GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
                        parameters = HashMap()
                        parameters.put('copyMetadata', True)
                        geom = WKTReader().read(jobint.roi)

                        if jobint.modecropping == 'auto' and (not jobint.satmode == 'IW'): 
                                parameters.put('geoRegion', geom)
                        
                        else: 
                                parameters.put('fullSwath', True)
                        
                        try: 
                                imageSLC_subset = GPF.createProduct('Subset',
                                                                parameters,
                                                                imageSLC)
                        except: 
                                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: Subset',jobint.log))
                        
                        try: 
                                usermessage.ezprint('\tWrite the file',jobint.log,verbose)
                                ProductIO.writeProduct(imageSLC_subset, 'input_prep'+os.sep+dslc, 'BEAM-DIMAP')
                                usermessage.ezprint('\t\tdone',jobint.log,verbose)
                        except:
                                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,'Error in the SNAP processing: writeProduct',jobint.log))
                        
                        imageSLC = None 
                        imageSLC_subset = None 

                        ## Cleaning 
                        listfile = np.unique(glob.glob('input_prep'+os.sep+dslc+'_full*') + glob.glob('input_prep'+os.sep+dslc+'*IW*'))
                        for li in listfile: 
                                if os.path.isfile(li):
                                        os.remove(li)
                                elif os.path.isdir(li):
                                        shutil.rmtree(li)
                          
                else: 
                        usermessage.warningmsg(__name__,importSLC.__name__,__file__,'The file %s is already processed.' % (dslc),jobint.log,verbose)

                snaptools.snapclearcache(verbose=False,log=jobint.log)

        jobint.importSLC['done']['value'] = True
        snaptools.snapclearcache(verbose=False,log=jobint.log)
        os.chdir(cur_dir)

        return jobint 

################################################################################
## multilook FUNCTION
################################################################################
def multilook(jobint, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Multilook the SLCs

        The function will multilook the SLC files, from an ``ezinsar.intstack``.   

        Args:
                jobint (``ezinsar.intstack``): EZ-InSAR intstack job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.intstack``: Return an EZ-InSAR intstack class
        
        """
        
        if not 'snapintstack.intstack' in str(type(jobint)):
                raise ValueError(usermessage.errormsg(__name__,multilook.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobint.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,multilook.__name__,__file__,__copyright__,
                        'verbose','True or False',jobint.log))

        if modeforce == None:
                modeforce = jobint.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,multilook.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobint.log))
        
        usermessage.openingmsg(__name__,multilook.__name__,__file__,__copyright__,'intstack Step: multilook',jobint.log,verbose)

        jobint.check(verbose=False,mode='high')

        if jobint.importSLC['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,multilook.__name__,__file__,__copyright__,
                                'The previous step (importSLC) is not done.',None))
        
        cur_dir = os.getcwd()
        os.chdir(jobint.workdirectory)
        snaptools.snapclearcache(verbose=False,log=jobint.log)

        if not os.path.isdir('mli'): 
                os.mkdir('mli')

        listdate = snaptools.readdatefile('dates')

        ## Processing loop
        for dslc in listdate: 
                usermessage.ezprint('For the date %s' %(dslc),jobint.log,verbose) 

                if ((not os.path.isfile('mli'+os.sep+dslc+'.dim')) and (not glob.glob('geotiff'+os.sep+dslc+'*.tif'))) or modeforce == True:

                        imageSLC = ProductIO.readProduct('input_prep'+os.sep+dslc+'.dim')

                        operator = 'Multilook'
                        parameters = HashMap()
                        parameters.put('nRgLooks', str(jobint.mlran))
                        parameters.put('nAzLooks', str(jobint.mlazi))
                        parameters.put('outputIntensity', 'false')
                        parameters.put('grSquarePixel', 'false')

                        usermessage.ezprint('\tParameters: %s' % parameters,jobint.log,verbose)

                        try: 
                                imageSLC_ml = GPF.createProduct(operator,
                                                                parameters,
                                                                imageSLC)
                        except: 
                                raise ValueError(usermessage.errormsg(__name__,multilook.__name__,__file__,__copyright__,'Error in the SNAP processing: Multilook',jobint.log))
                        
                        try:
                                usermessage.ezprint('\tWrite the file',jobint.log,verbose)
                                ProductIO.writeProduct(imageSLC_ml, 'mli'+os.sep+dslc, 'BEAM-DIMAP')
                                usermessage.ezprint('\t\tdone',jobint.log,verbose)
                        except: 
                                raise ValueError(usermessage.errormsg(__name__,multilook.__name__,__file__,__copyright__,'Error in the SNAP processing: writeProduct',jobint.log))
                        
                        imageSLC = None 
                        imageSLC_ml = None  

                else: 
                        usermessage.warningmsg(__name__,multilook.__name__,__file__,'The file %s is already processed.' % (dslc),jobint.log,verbose)

                snaptools.snapclearcache(verbose=False,log=jobint.log)

        jobint.multilook['done']['value'] = True
        snaptools.snapclearcache(verbose=False,log=jobint.log)
        os.chdir(cur_dir)

        return jobint

################################################################################
## filter FUNCTION
################################################################################
def filter(jobint, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Filter the SLCs

        The function will filter the SLC files, from an ``ezinsar.intstack``.   

        Args:
                jobint (``ezinsar.intstack``): EZ-InSAR intstack job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.intstack``: Return an EZ-InSAR intstack class
        
        """
        
        if not 'snapintstack.intstack' in str(type(jobint)):
                raise ValueError(usermessage.errormsg(__name__,filter.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobint.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,filter.__name__,__file__,__copyright__,
                        'verbose','True or False',jobint.log))

        if modeforce == None:
                modeforce = jobint.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,filter.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobint.log))
        
        usermessage.openingmsg(__name__,filter.__name__,__file__,__copyright__,'intstack Step: filter',jobint.log,verbose)

        jobint.check(verbose=False,mode='high')

        if jobint.multilook['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,filter.__name__,__file__,__copyright__,
                                'The previous step (multilook) is not done.',None))
        
        cur_dir = os.getcwd()
        os.chdir(jobint.workdirectory)
        snaptools.snapclearcache(verbose=False,log=jobint.log)

        if jobint.filter['process']['value'] == True:

                if not os.path.isdir('filt'): 
                        os.mkdir('filt')

                listdate = snaptools.readdatefile('dates')
                
                ## Processing loop
                for dslc in listdate: 
                        usermessage.ezprint('For the date %s' %(dslc),jobint.log,verbose) 
                                
                        if ((not os.path.isfile('filt'+os.sep+dslc+'.dim')) and (not glob.glob('geotiff'+os.sep+dslc+'*.tif'))) or modeforce == True:
                                
                                imageSLC = ProductIO.readProduct('mli'+os.sep+dslc+'.dim')

                                operator = 'Speckle-Filter'

                                parameters = HashMap()
                                # parameters.put('sourceBandNames', None)
                                parameters.put('filter', jobint.filter['filter']['value'])
                                parameters.put('filterSizeX', str(jobint.filter['filterSizeX']['value']))
                                parameters.put('filterSizeY', str(jobint.filter['filterSizeX']['value']))
                                parameters.put('dampingFactor', str(jobint.filter['dampingFactor']['value']))
                                parameters.put('estimateENL', str(jobint.filter['estimateENL']['value']))
                                parameters.put('enl', str(jobint.filter['enl']['value']))
                                parameters.put('numLooksStr', str(jobint.filter['numLooksStr']['value']))
                                parameters.put('windowSize', jobint.filter['windowSize']['value'])
                                parameters.put('targetWindowSizeStr', jobint.filter['targetWindowSizeStr']['value'])
                                parameters.put('sigmaStr', str(jobint.filter['sigmaStr']['value']))
                                parameters.put('anSize', str(jobint.filter['anSize']['value']))

                                usermessage.ezprint('\tParameters: %s' % parameters,jobint.log,verbose)

                                try: 
                                        imageSLC_filt = GPF.createProduct(operator,
                                                                        parameters,
                                                                        imageSLC)
                                except: 
                                        raise ValueError(usermessage.errormsg(__name__,filter.__name__,__file__,__copyright__,'Error in the SNAP processing: Speckle-Filter',jobint.log))
                                
                                try: 
                                        usermessage.ezprint('\t\tWrite the file',jobint.log,verbose)
                                        ProductIO.writeProduct(imageSLC_filt, 'filt'+os.sep+dslc, 'BEAM-DIMAP')
                                        usermessage.ezprint('\t\tdone',jobint.log,verbose)
                                except: 
                                        raise ValueError(usermessage.errormsg(__name__,filter.__name__,__file__,__copyright__,'Error in the SNAP processing: writeProduct',jobint.log))
                                
                                imageSLC_filt = None 
                                imageSLC= None 

                        else: 
                                usermessage.warningmsg(__name__,filter.__name__,__file__,'The file %s is already processed.' % (dslc),jobint.log,verbose)

                snaptools.snapclearcache(verbose=False,log=jobint.log)

        else:
                usermessage.ezprint('The processing is not activated',jobint.log,verbose)

        jobint.filter['done']['value'] = True
        snaptools.snapclearcache(verbose=False,log=jobint.log)
        os.chdir(cur_dir)

        return jobint

################################################################################
## terraincal FUNCTION
################################################################################
def terraincal(jobint, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Terrain calibration (flattening) for the SLCs

        The function will calibrate the SLC files, from an ``ezinsar.intstack``.   

        Args:
                jobint (``ezinsar.intstack``): EZ-InSAR intstack job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.


        Returns:
                ``ezinsar.intstack``: Return an EZ-InSAR intstack class
        
        """
        
        if not 'snapintstack.intstack' in str(type(jobint)):
                raise ValueError(usermessage.errormsg(__name__,terraincal.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobint.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,terraincal.__name__,__file__,__copyright__,
                        'verbose','True or False',jobint.log))

        if modeforce == None:
                modeforce = jobint.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,terraincal.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobint.log))
        
        usermessage.openingmsg(__name__,terraincal.__name__,__file__,__copyright__,'intstack Step: terraincal',jobint.log,verbose)

        jobint.check(verbose=False,mode='high')

        if jobint.multilook['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,terraincal.__name__,__file__,__copyright__,
                                'The previous step (multilook) is not done.',None))
        
        cur_dir = os.getcwd()
        os.chdir(jobint.workdirectory)
        snaptools.snapclearcache(verbose=False,log=jobint.log)

        if jobint.terraincal['process']['value'] == True:

                if not os.path.isdir('cal'): 
                        os.mkdir('cal')

                listdate = snaptools.readdatefile('dates')
                
                ## Processing loop
                for dslc in listdate: 
                        usermessage.ezprint('For the date %s' %(dslc),jobint.log,verbose) 
                                
                        if ((not os.path.isfile('cal'+os.sep+dslc+'.dim')) and (not glob.glob('geotiff'+os.sep+dslc+'*.tif'))) or modeforce == True:

                                if jobint.filter['process']['value'] == True:
                                        imageSLC = ProductIO.readProduct('filt'+os.sep+dslc+'.dim')
                                else: 
                                        imageSLC = ProductIO.readProduct('mli'+os.sep+dslc+'.dim')

                                operator = 'Terrain-Flattening'

                                parameters = HashMap()
                                parameters.put('sourceBandNames', None)
                                parameters.put('demName', 'External DEM')
                                parameters.put('externalDEMFile',jobint.pathDEM+os.sep+jobint.nameDEM)

                                parameters.put('demResamplingMethod', jobint.terraincal['demResamplingMethod']['value'])
                                parameters.put('externalDEMNoDataValue', '0')
                                parameters.put('externalDEMApplyEGM', 'false') 
                                parameters.put('outputSimulatedImage', 'false')
                                parameters.put('outputSigma0', str(jobint.importSLC['sigma0']['value']))
                                parameters.put('nodataValueAtSea', 'true')
                                parameters.put('additionalOverlap', str(jobint.terraincal['additionalOverlap']['value']))
                                parameters.put('oversamplingMultiple', str(jobint.terraincal['oversamplingMultiple']['value']))

                                usermessage.ezprint('\tParameters: %s' % parameters,jobint.log,verbose)

                                try: 
                                        imageSLC_cal = GPF.createProduct(operator,
                                                                        parameters,
                                                                        imageSLC)
                                except: 
                                        raise ValueError(usermessage.errormsg(__name__,terraincal.__name__,__file__,__copyright__,'Error in the SNAP processing: Terrain-Flattening',jobint.log))
                                
                                try: 
                                        usermessage.ezprint('\t\tWrite the file',jobint.log,verbose)
                                        ProductIO.writeProduct(imageSLC_cal, 'cal'+os.sep+dslc, 'BEAM-DIMAP')
                                        usermessage.ezprint('\t\tdone',jobint.log,verbose)
                                except: 
                                        raise ValueError(usermessage.errormsg(__name__,terraincal.__name__,__file__,__copyright__,'Error in the SNAP processing: writeProduct',jobint.log))
                                
                                imageSLC_cal = None 
                                imageSLC = None 

                        else: 
                                usermessage.warningmsg(__name__,terraincal.__name__,__file__,'The file %s is already processed.' % (dslc),jobint.log,verbose)

                        snaptools.snapclearcache(verbose=False,log=jobint.log)
        else:
                usermessage.ezprint('The processing is not activated',jobint.log,verbose)

        jobint.terraincal['done']['value'] = True
        snaptools.snapclearcache(verbose=False,log=jobint.log)
        os.chdir(cur_dir)

        return jobint

################################################################################
## geocode FUNCTION
################################################################################
def geocode(jobint, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Geocoding for the results

        The function will geocode the SLC files, from an ``ezinsar.intstack``.   

        Args:
                jobint (``ezinsar.intstack``): EZ-InSAR intstack job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.intstack``: Return an EZ-InSAR intstack class
        
        """
        
        if not 'snapintstack.intstack' in str(type(jobint)):
                raise ValueError(usermessage.errormsg(__name__,geocode.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobint.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,geocode.__name__,__file__,__copyright__,
                        'verbose','True or False',jobint.log))

        if modeforce == None:
                modeforce = jobint.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,geocode.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobint.log))
        
        usermessage.openingmsg(__name__,geocode.__name__,__file__,__copyright__,'intstack Step: geocode',jobint.log,verbose)

        jobint.check(verbose=False,mode='high')

        if jobint.multilook['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,geocode.__name__,__file__,__copyright__,
                                'The previous step (multilook) is not done.',None))
        
        cur_dir = os.getcwd()
        os.chdir(jobint.workdirectory)
        snaptools.snapclearcache(verbose=False,log=jobint.log)

        if not os.path.isdir('geo'): 
                os.mkdir('geo')
        
        if not os.path.isdir('geotiff'): 
                os.mkdir('geotiff')

        listdate = snaptools.readdatefile('dates')
                
        ## Processing loop
        for dslc in listdate: 
                usermessage.ezprint('For the date %s' %(dslc),jobint.log,verbose) 
                        
                if (not glob.glob('geotiff'+os.sep+dslc+'*.tif')) or modeforce == True:                        
                
                        ## Preparation of the DEM
                        src_ds = gdal.Open(jobint.pathDEM+os.sep+jobint.nameDEM)
                        options = '-of GTiff -a_nodata 0 -tr %s %s' % (abs(src_ds.GetGeoTransform()[1]*jobint.geocode['Xdem_overfactor']['value']),abs(src_ds.GetGeoTransform()[5]*jobint.geocode['Ydem_overfactor']['value']))

                        dst_ds = gdal.Translate('tmpDEM.tif', src_ds, options = options)
                        src_ds = None
                        dst_ds = None

                        ## Import the last results
                        if jobint.terraincal['process']['value'] == True:
                                imageSLC = ProductIO.readProduct('cal'+os.sep+dslc+'.dim')
                        elif jobint.filter['process']['value'] == True:
                                imageSLC = ProductIO.readProduct('filt'+os.sep+dslc+'.dim')
                        else: 
                                imageSLC = ProductIO.readProduct('mli'+os.sep+dslc+'.dim')

                        operator = 'Terrain-Correction'

                        parameters = HashMap()
                        parameters.put('demName', 'External DEM')
                        parameters.put('externalDEMFile','tmpDEM.tif')
                        parameters.put('externalDEMNoDataValue', '0')
                        parameters.put('externalDEMApplyEGM', 'false')

                        parameters.put('demResamplingMethod', jobint.geocode['demResamplingMethod']['value'])
                        parameters.put('imgResamplingMethod', jobint.geocode['imgResamplingMethod']['value'])
                        parameters.put('alignToStandardGrid', 'True')

                        # parameters.put('pixelSpacingInMeter', '100')
                        # pixelSpacingInDegree 0
                        # mapProjection WGS84(DD)
                        # standardGridOriginX 0
                        # standardGridOriginY 0
                        # nodataValueAtSea true
                        # saveDEM false
                        # saveLatLon false
                        # saveIncidenceAngleFromEllipsoid false
                        # saveLocalIncidenceAngle false
                        # saveProjectedLocalIncidenceAngle false
                        # saveSelectedSourceBand true
                        # saveLayoverShadowMask false
                        # outputComplex false
                        # applyRadiometricNormalization false
                        # saveSigmaNought false
                        # saveGammaNought false
                        # saveBetaNought false
                        # incidenceAngleForSigma0 Use projected local incidence angle from DEM
                        # incidenceAngleForGamma0 Use projected local incidence angle from DEM
                        # auxFile Latest Auxiliary File
                        # externalAuxFile None

                        usermessage.ezprint('\tParameters: %s' % parameters,jobint.log,verbose)

                        try: 
                                imageSLC_geo = GPF.createProduct(operator,
                                        parameters,
                                        imageSLC)
                        except: 
                                raise ValueError(usermessage.errormsg(__name__,terraincal.__name__,__file__,__copyright__,'Error in the SNAP processing: Terrain-Correction',jobint.log))
                        
                        try: 
                                usermessage.ezprint('\t\tWrite the file',jobint.log,verbose)
                                ProductIO.writeProduct(imageSLC_geo, 'geo'+os.sep+dslc, 'BEAM-DIMAP')
                                usermessage.ezprint('\t\tdone',jobint.log,verbose)
                        except: 
                                raise ValueError(usermessage.errormsg(__name__,terraincal.__name__,__file__,__copyright__,'Error in the SNAP processing: writeProduct',jobint.log))
                        
                        imageSLC = None 
                        imageSLC_geo = None 

                        ## Creation of the geotiff
                        usermessage.ezprint('\tCreate the geotiff images:...',jobint.log,verbose)

                        listfile = glob.glob('geo'+os.sep+dslc+'.data'+os.sep+'*.img')
                        
                        for fi in listfile: 

                                ## Detection of the names
                                nameinput = fi
                                if 'Gamma0_' in nameinput: 
                                        ext1 = 'g0'
                                elif 'Sigma0' in nameinput: 
                                        ext1 = 's0'
                                else: 
                                        ext1 = 'b0'

                                ext2 = nameinput.split(os.sep)[-1].split('.')[0].split('_')[-1].lower()

                                if jobint.geocode['dB']['value'] == True:
                                        ext3 = '.db'
                                else:
                                        ext3 = ''

                                nameoutput = 'geotiff'+os.sep+dslc+'.'+ext2+'.'+ext1+'.geo'+ext3+'.tif'

                                ## Cropping the results regarding the ROI
                                src_ds = gdal.Open(jobint.pathDEM+os.sep+jobint.nameDEM)
                                options = '-of GTiff -a_nodata %s' % (jobint.geocode['nondata']['value'])
                                if jobint.modecropping == 'auto':
                                        bboxclip = loads(jobint.roi).exterior.xy
                                        options = options + ' -projwin %f %f %f %f -projwin_srs EPSG:4326' % (np.min(bboxclip[0]),np.max(bboxclip[1]),np.max(bboxclip[0]),np.min(bboxclip[1]))

                                src_ds = gdal.Open(nameinput)
                                dst_ds = gdal.Translate('tmp.tif', src_ds, options = options)
                                src_ds = None
                                dst_ds = None

                                lastname = 'tmp.tif'

                                ## Convert to dB scale
                                if jobint.geocode['dB']['value'] == True:
                                        src_ds = gdal.Open('tmp.tif')
                                        band = src_ds.GetRasterBand(1).ReadAsArray()
                                        band[band == jobint.geocode['nondata']['value']] = np.nan
                                        band = 10*np.log10(band)
                                        band[band == np.nan] = jobint.geocode['nondata']['value']

                                        dst_ds = gdal.GetDriverByName("GTiff").Create('tmp2.tif', src_ds.RasterXSize, src_ds.RasterYSize, 1, gdal.GDT_Float32)
                                        dst_ds.SetGeoTransform(src_ds.GetGeoTransform()) 
                                        dst_ds.SetProjection(src_ds.GetProjection())
                                        dst_ds.GetRasterBand(1).WriteArray(band)   
                                        dst_ds.GetRasterBand(1).SetNoDataValue(jobint.geocode['nondata']['value'])
                                        dst_ds.FlushCache()

                                        lastname = 'tmp2.tif'

                                os.rename(lastname,nameoutput)

                        usermessage.ezprint('\t\tdone',jobint.log,verbose)

                        ## Cleaning 
                        for li in ['tmpDEM.tif','tmp.tif','tmp2.tif']:
                                if os.path.isfile(li):
                                        os.remove(li)

                else: 
                        usermessage.warningmsg(__name__,geocode.__name__,__file__,'The file %s is already processed.' % (dslc),jobint.log,verbose)

                snaptools.snapclearcache(verbose=False,log=jobint.log)

        jobint.geocode['done']['value'] = True
        snaptools.snapclearcache(verbose=False,log=jobint.log)
        os.chdir(cur_dir)

        return jobint

################################################################################
## clean FUNCTION
################################################################################
def clean(jobint, verbose: Optional[bool] = None):
        """Clean for the results

        The function will clean the work directory, from an ``ezinsar.intstack``.   

        Args:
                jobint (``ezinsar.intstack``): EZ-InSAR intstack job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.intstack``: Return an EZ-InSAR intstack class
        
        """
        
        if not 'snapintstack.intstack' in str(type(jobint)):
                raise ValueError(usermessage.errormsg(__name__,clean.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobint.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,clean.__name__,__file__,__copyright__,
                        'verbose','True or False',jobint.log))
        
        usermessage.openingmsg(__name__,clean.__name__,__file__,__copyright__,'intstack Step: clean',jobint.log,verbose)

        jobint.check(verbose=False,mode='high')

        cur_dir = os.getcwd()
        os.chdir(jobint.workdirectory)

        if jobint.clean['process']['value'] == True:
                snaptools.snapclearcache(verbose=False,log=jobint.log)

                if jobint.clean['keepdirectory']['value'] == True:
                        listdate = snaptools.readdatefile('dates')

                        for dslc in listdate:
                                jobint.deletedate(dslc)

                else:
                        for directoryi in ['cal','filt','geo','input_prep','mli']:
                                if os.path.isdir(directoryi):
                                        shutil.rmtree(directoryi)

        jobint.clean['done']['value'] = True
        os.chdir(cur_dir)

        return jobint
                                
################################################################################
## update FUNCTION
################################################################################
def update(jobint, verbose: Optional[bool] = None):
        """Update for the stack

        The function will update the stack based on the new files, from an ``ezinsar.intstack``.   

        Args:
                jobint (``ezinsar.intstack``): EZ-InSAR intstack job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.intstack``: Return an EZ-InSAR intstack class
        
        """
        
        if not 'snapintstack.intstack' in str(type(jobint)):
                raise ValueError(usermessage.errormsg(__name__,update.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobint.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,update.__name__,__file__,__copyright__,
                        'verbose','True or False',jobint.log))
        
        usermessage.openingmsg(__name__,update.__name__,__file__,__copyright__,'intstack Step: update',jobint.log,verbose)

        jobint.check(verbose=False,mode='high')

        cur_dir = os.getcwd()
        os.chdir(jobint.workdirectory)
        snaptools.snapclearcache(verbose=False,log=jobint.log)

        ## Create the new date files
        jobint.run(step=['checkSLC'],verbose=False)

        ## Run the processing 
        importSLC(jobint,verbose=verbose,modeforce=jobint.update['modeforce']['value'])
        multilook(jobint,verbose=verbose,modeforce=jobint.update['modeforce']['value'])
        filter(jobint,verbose=verbose,modeforce=jobint.update['modeforce']['value'])
        terraincal(jobint,verbose=verbose,modeforce=jobint.update['modeforce']['value'])
        geocode(jobint,verbose=verbose,modeforce=jobint.update['modeforce']['value'])
        clean(jobint,verbose=verbose)

        jobint.update['done']['value'] = True
        os.chdir(cur_dir)

        return jobint
                       