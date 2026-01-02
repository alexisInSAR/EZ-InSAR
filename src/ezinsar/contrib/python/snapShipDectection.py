#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to process ship detection on Sentinel-1 GRD images with SNAP 

The module contains a set of class and functions to run a ship detection based on Sentinel-1 GRD images and the alogithms provided by SNAP. 

Restrictions: 
        * Only for Sentinel-1 GRD image
        * Use the SNAP GTP
        * Parameters (i.e., region of Interest must be provided by an EZ-InSAR job)

Changelog:
        * 1.0.0: Initial version, Sep. 2025

"""

__author__ = 'Alexis Hrysiewicz (UCD / iCRAG)'
__copyright__ = "Copyright 2025, EZ-InSAR / UCD / iCRAG"
__version__ = '1.0.0'

################################################################################
## Python packages
################################################################################
import os
from typing import Optional, Union
import numpy as np
import time
import datetime
from shapely.geometry import Point, mapping
import glob
import pandas as pd
import fiona 
from fiona.crs import from_epsg

################################################################################
## Import the EZ-InSAR package
################################################################################
from ezinsar import usermessage, constants
from ezinsar.eicomponents.processor.snapmodule import snaptools
from ezinsar.eicomponents.processor.snapmodule import snapgpttools

if not constants.__SNAP_wrapper__ == 'gpt':
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                'The SNAP mode must be gpt',None))

################################################################################
## Class to manage the EZ-InSAR job
################################################################################
class jobsnapSD:
        """Job SNAP Ship Detection (`jobsnapSD`) class.             
        """

        ################################################################################
        ## Initialistion of the class
        ################################################################################
        def __init__(self,
                        job,
                        verbose: Optional[bool] = True,
                        log: Optional[Union[str,None]] = None,
                        ):
                """Initialisation of the class   
                """
                start = time.time()

                if not isinstance(verbose,bool):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'verbose','True or False',log))

                usermessage.openingmsg(__name__,__name__,__file__,constants.__copyright__,'Ship detection based on Sentinel-1 GRD images with SNAP',log,verbose,contribauthor=__author__,contribcopyright=__copyright__,contribversion=__version__,contribfile=__file__)

                self.job = job
     
                usermessage.ezprint('\nPerformed in %0.3f seconds' % (time.time()-start),log,verbose)

        ################################################################################
        ## Processing steps
        ################################################################################
        def importGRD(self,
                applyorbit: Optional[bool] = True,
                cropping: Optional[bool] = True,
                modeforce: Optional[bool] = True,
                verbose: Optional[bool] = True,
                log: Optional[Union[str,None]] = None,
                ): 
                """Import the GRD images

                The method will import Sentinel-1 GRD images into the SNAP format. 

                Args: 
                        applyorbit (bool, Optional): Apply the orbits. [Default: `True`]
                        cropping (bool, Optional): Cropping. [Default: `True`]
                        modeforce (bool, Optional): Forcing mode. [Default: `True`]
                        verbose (bool, Optional): Verbose. [Default: `True`]
                        log (str, Optional): log. [Default: `None`]
                
                Returns:
                        `jobsnapSD` class
                """
                if not isinstance(verbose,bool):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'verbose','True or False',log))

                usermessage.openingmsg(__name__,__name__,__file__,__copyright__,'Ship detection based on Sentinel-1 GRD images with SNAP: Import GRD images',log,verbose,contribauthor=__author__,contribcopyright=__copyright__,contribversion=__version__,contribfile=__file__)

                ## Detection of the dates
                dates = []
                filelist = np.sort(glob.glob(self.job.pathSLC+os.sep+'*.zip') + glob.glob(self.job.pathSLC+os.sep+'*.SAFE'))
                for slci in filelist:
                        datestr = slci.split(os.sep)[-1].split('.')[0].split('_')[5].split('T')[0] 
                        dates.append(datestr)
                dates = sorted(dates)
                dates = np.unique(dates)

                usermessage.ezprint('The date(s) is/are %s' %(dates),log,verbose)

                cur_dir = os.getcwd()
                os.chdir(self.job.workdirectory)

                if constants.__SNAPcacheclean__:
                        snaptools.snapclearcache(verbose=False,log=log)

                if not os.path.isdir('input_prep'): 
                        os.mkdir('input_prep')

                for dslc in dates: 
                        usermessage.ezprint('For the date %s' %(dslc),log,verbose) 

                        if (not glob.glob('input_prep'+os.sep+'*'+dslc+'*.dim')) or modeforce == True:

                                usermessage.ezprint('\tDetection of Sentinel-1 GRD image(s)',log,verbose) 

                                ## Detection of the different slices
                                pathslctmp = np.sort(glob.glob(self.job.pathSLC+os.sep+'*'+dslc+'*'))
                                nb_slice = len(pathslctmp)

                                ## Read the Sentinel-1 slices
                                usermessage.ezprint('\t\tRead the Sentinel-1 slices',log,verbose) 

                                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                        cleancache = constants.__SNAPcacheclean__,
                                        debugmode = constants.__SNAPloggingmode__)
                                gptdata.xmlinit()
                                listproducts = []

                                for nbslice, slicei in enumerate(pathslctmp): 
                                        listproducts.append(str(slicei))

                                        gptdata.Read(slicei,idx=nbslice+1)

                                ## Assembly the Sentinel-1 slices (if required)
                                usermessage.ezprint('\t\tAssemble the Sentinel-1 slices (if required)',log,verbose)         
                                        
                                if len(listproducts) > 1:
                                        gptdata.SliceAssembly2(self.job.polarisation)                                        

                                # Apply the orbits
                                if applyorbit == True:
                                        usermessage.ezprint('\t\t\tApply the orbit files (for Sentinel-1):',log,verbose) 
                                        gptdata.ApplyOrbitFile()
                                        usermessage.ezprint('\t\t\t\tdone',log,verbose) 

                                # Subset 
                                if cropping: 
                                        sourceBands = []
                                        for poly in self.job.polarisation:
                                                sourceBands.append('Intensity_%s' % (poly.upper()))

                                                usermessage.ezprint('\tCropping', log,verbose) 
                                                gptdata.generic('Subset',
                                                        {'copyMetadata': True,
                                                        'geoRegion': self.job.roi.wkt,
                                                        'sourceBands': ','.join(sourceBands),
                                                        })

                                ## Write 
                                gptdata.Write(os.path.abspath('input_prep'+os.sep+dslc+'.dim'))
                                gptdata.xmlclose()
                                gptdata.run(verbose=verbose,log=log)
                                gptdata.clean()

                        else: 
                                usermessage.warningmsg(__name__,__name__,__file__,'The file %s is already processed.' % (dslc),log,verbose)

                if constants.__SNAPcacheclean__:
                        snaptools.snapclearcache(verbose=False,log=log)

                os.chdir(cur_dir)

                return self 
        
        ################################################################################
        def importVector(self,vectorfile,
                modeforce: Optional[bool] = True,
                verbose: Optional[bool] = True,
                log: Optional[Union[str,None]] = None,
                ): 
                """Import a vector file for masking based on a shoreline 

                The method will import a vector file (.shp) into the SNAP GRD image.

                Args: 
                        vectorfile (str): Vector file.
                        modeforce (bool, Optional): Forcing mode. [Default: `True`]
                        verbose (bool, Optional): Verbose. [Default: `True`]
                        log (str, Optional): log. [Default: `None`]
                
                Returns:
                        `jobsnapSD` class
                """

                if not isinstance(verbose,bool):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'verbose','True or False',log))

                usermessage.openingmsg(__name__,__name__,__file__,__copyright__,'Ship detection based on Sentinel-1 GRD images with SNAP: Import a vector file (for masking)',log,verbose,contribauthor=__author__,contribcopyright=__copyright__,contribversion=__version__,contribfile=__file__)

                ## Detection of the dates
                dates = [x.split(os.sep)[-1].split('.')[0] for x in np.sort(glob.glob(self.job.workdirectory+os.sep+'input_prep'+os.sep+'*.dim'))]
                usermessage.ezprint('The date(s) is/are %s' %(dates),log,verbose)

                cur_dir = os.getcwd()
                os.chdir(self.job.workdirectory)

                if constants.__SNAPcacheclean__:
                        snaptools.snapclearcache(verbose=False,log=log)

                ## Processing loop
                for dslc in dates: 
                        usermessage.ezprint('For the date %s' %(dslc),log,verbose) 

                        if (not glob.glob('input_prep'+os.sep+'*'+dslc+'*.dim')) or modeforce == True:

                                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                        cleancache = constants.__SNAPcacheclean__,
                                        debugmode = constants.__SNAPloggingmode__)
                                gptdata.xmlinit()
                                gptdata.Read(self.job.workdirectory+os.sep+'input_prep'+os.sep+dslc+'.dim')
                                gptdata.generic('Import-Vector',
                                                {'vectorFile': vectorfile,
                                                 'separateShapes': False, 
                                                })
                                gptdata.Write(os.path.abspath('input_prep'+os.sep+dslc+'.dim'))
                                gptdata.xmlclose()
                                gptdata.run(verbose=verbose,log=log)
                                gptdata.clean()
                        else: 
                                usermessage.warningmsg(__name__,__name__,__file__,'The file %s is already processed.' % (dslc),log,verbose)

                if constants.__SNAPcacheclean__:
                        snaptools.snapclearcache(verbose=False,log=log)

                os.chdir(cur_dir)

                return self 

        ################################################################################
        def detection(self,
                usevector: Optional[bool] = True, 
                shorelineExtension: Optional[int] = 50,   
                targetWindowSizeInMeter: Optional[int] = 50,   
                guardWindowSizeInMeter: Optional[float] = 500.0,   
                backgroundWindowSizeInMeter: Optional[float] = 800.0,   
                pfa: Optional[float] = 12.5,   
                estimateBackground: Optional[bool] = False,   
                minTargetSizeInMeter: Optional[int] = 30,   
                maxTargetSizeInMeter: Optional[int] = 600,   
                modeforce: Optional[bool] = True,
                verbose: Optional[bool] = True,
                log: Optional[Union[str,None]] = None,
                ): 
                """Ship detection based on the SNAP algorithm

                The method will apply the ship detection based on the SNAP algorithm

                Args: 
                        usevector (bool, Optional): Use the vector for masking [default: True]
                        shorelineExtension (bool, Optional): SNAP parameter (see SNAP documentation) [default: 50]
                        targetWindowSizeInMeter (bool, Optional): SNAP parameter (see SNAP documentation) [default: 50]
                        guardWindowSizeInMeter (float, Optional): SNAP parameter (see SNAP documentation) [default: 500.0]
                        backgroundWindowSizeInMeter (float, Optional): SNAP parameter (see SNAP documentation) [default: 800.0]
                        pfa (float, Optional): SNAP parameter (see SNAP documentation) [default: 13.5.0]
                        estimateBackground (bool, Optional): SNAP parameter (see SNAP documentation) [default: False]
                        minTargetSizeInMeter (bool, Optional): SNAP parameter (see SNAP documentation) [default: 30]
                        maxTargetSizeInMeter (bool, Optional): SNAP parameter (see SNAP documentation) [default: 600]
                        modeforce (bool, Optional): Forcing mode. [Default: `True`]
                        verbose (bool, Optional): Verbose. [Default: `True`]
                        log (str, Optional): log. [Default: `None`]
                
                Returns:
                        `jobsnapSD` class
                """

                if not isinstance(verbose,bool):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'verbose','True or False',log))

                usermessage.openingmsg(__name__,__name__,__file__,__copyright__,'Ship detection based on Sentinel-1 GRD images with SNAP: Ship detection',log,verbose,contribauthor=__author__,contribcopyright=__copyright__,contribversion=__version__,contribfile=__file__)

                dates = [x.split(os.sep)[-1].split('.')[0] for x in np.sort(glob.glob(self.job.workdirectory+os.sep+'input_prep'+os.sep+'*.dim'))]
                usermessage.ezprint('The date(s) is/are %s' %(dates),log,verbose)

                cur_dir = os.getcwd()
                os.chdir(self.job.workdirectory)

                if constants.__SNAPcacheclean__:
                        snaptools.snapclearcache(verbose=False,log=log)

                if not os.path.isdir('output'): 
                        os.mkdir('output')

                for dslc in dates: 
                        usermessage.ezprint('For the date %s' %(dslc),log,verbose) 

                        if (not glob.glob('input_prep'+os.sep+'*'+dslc+'*.dim')) or modeforce == True:

                                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                        cleancache = constants.__SNAPcacheclean__,
                                        debugmode = constants.__SNAPloggingmode__)
                                gptdata.xmlinit()
                                gptdata.Read(self.job.workdirectory+os.sep+'input_prep'+os.sep+dslc+'.dim')

                                if usevector: 
                                        listvec = [x.split(os.sep)[-1] for x in glob.glob(self.job.workdirectory+os.sep+'input_prep'+os.sep+dslc+'.data'+os.sep+'vector_data'+os.sep+'*.csv')]
                                        listvec.remove('ground_control_points.csv')
                                        listvec.remove('pins.csv')

                                        para = {'landMask': False,
                                        'useSRTM': False, 
                                        'geometry': listvec[0].split('.')[0],
                                        'shorelineExtension': shorelineExtension,
                                        'invertGeometry': True, 
                                        }
                                else: 
                                        para = {'landMask': True,
                                        'useSRTM': True, 
                                        'shorelineExtension': shorelineExtension,
                                        }
                                gptdata.generic('Land-Sea-Mask',para)

                                gptdata.generic('Calibration',
                                                {'outputImageInComplex': False,
                                                        'outputImageScaleInDb': False,
                                                        'createGammaBand': False,
                                                        'createBetaBand': False,
                                                        'selectedPolarisations': ','.join(self.job.polarisation),
                                                        'outputSigmaBand': True,
                                                        'outputGammaBand': False,
                                                        'outputBetaBand': False,
                                                })
                                
                                gptdata.generic('AdaptiveThresholding',
                                                {'targetWindowSizeInMeter': targetWindowSizeInMeter,
                                                'guardWindowSizeInMeter': guardWindowSizeInMeter,
                                                'backgroundWindowSizeInMeter': backgroundWindowSizeInMeter,
                                                'pfa': pfa,
                                                'estimateBackground': estimateBackground,
                                                })

                                gptdata.generic('Object-Discrimination',
                                                {'minTargetSizeInMeter': minTargetSizeInMeter,
                                                'maxTargetSizeInMeter': maxTargetSizeInMeter,
                                                })

                                gptdata.Write(os.path.abspath('output'+os.sep+dslc+'.dim'))
                                gptdata.xmlclose()
                                gptdata.run(verbose=verbose,log=log)
                                gptdata.clean()
                        else: 
                                usermessage.warningmsg(__name__,__name__,__file__,'The file %s is already processed.' % (dslc),log,verbose)

                if constants.__SNAPcacheclean__:
                        snaptools.snapclearcache(verbose=False,log=log)

                os.chdir(cur_dir)

                return self 
        
        ################################################################################
        def extractposition(self,
                output_directory,
                modeforce: Optional[bool] = True,
                verbose: Optional[bool] = True,
                log: Optional[Union[str,None]] = None,
                ): 
                """Extract ship locations from the SNAP vector file

                The method will extract ship locations from the SNAP vector file, and save a .shp file. 

                Args: 
                        output_directory (str): Directory for the output shp file
                        modeforce (bool, Optional): Forcing mode. [Default: `True`]
                        verbose (bool, Optional): Verbose. [Default: `True`]
                        log (str, Optional): log. [Default: `None`]
                
                Returns:
                        `jobsnapSD` class
                """
                
                if not isinstance(verbose,bool):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'verbose','True or False',log))

                usermessage.openingmsg(__name__,__name__,__file__,__copyright__,'Ship detection based on Sentinel-1 GRD images with SNAP: Extract the ship locations',log,verbose,contribauthor=__author__,contribcopyright=__copyright__,contribversion=__version__,contribfile=__file__)

                dates = [x.split(os.sep)[-1].split('.')[0] for x in np.sort(glob.glob(self.job.workdirectory+os.sep+'input_prep'+os.sep+'*.dim'))]
                usermessage.ezprint('The date(s) is/are %s' %(dates),log,verbose)

                if constants.__SNAPcacheclean__:
                        snaptools.snapclearcache(verbose=False,log=log)

                if not os.path.isdir(output_directory): 
                        os.mkdir(output_directory)

                for dslc in dates: 
                        usermessage.ezprint('For the date %s' %(dslc),log,verbose) 

                        outputshp = output_directory + os.sep + 'shipDetection_%s_%s_%s_%s_%s.shp' % ('S1',
                                self.job.satmode,
                                self.job.satpass,
                                self.job.relorbit,
                                dslc,
                                )

                        if (not glob.glob(outputshp)) or modeforce == True:
                                file = glob.glob(self.job.workdirectory+os.sep+'output'+os.sep+dslc+'.data'+os.sep+'vector_data'+os.sep+'ShipDetections.csv')[0]

                                date1 = None
                                date2 = None
                                with open(self.job.workdirectory+os.sep+'output'+os.sep+dslc+'.dim','r') as f_in:
                                        for line in f_in.readlines(): 
                                                if 'PRODUCT_SCENE_RASTER_START_TIME' in line: 
                                                        date1 = datetime.datetime.strptime(line.replace('<PRODUCT_SCENE_RASTER_START_TIME>','').replace('</PRODUCT_SCENE_RASTER_START_TIME>','').strip().lower(),
                                                        '%d-%b-%Y %H:%M:%S.%f').strftime('%Y-%m-%dT%H:%M:%S.%f')+'Z'
                                                        
                                                if 'PRODUCT_SCENE_RASTER_STOP_TIME' in line: 
                                                        date2 = datetime.datetime.strptime(line.replace('<PRODUCT_SCENE_RASTER_STOP_TIME>','').replace('</PRODUCT_SCENE_RASTER_STOP_TIME>','').strip().lower(),
                                                        '%d-%b-%Y %H:%M:%S.%f').strftime('%Y-%m-%dT%H:%M:%S.%f')+'Z'

                                shpdetectionCSVtoSHP(file,outputshp,
                                                date1 = date1,
                                                date2 = date2)

                                usermessage.ezprint('\tdone: %s' %(outputshp),log,verbose) 

                        else: 
                                usermessage.warningmsg(__name__,__name__,__file__,'The file %s is ' \
                                'already processed.' % (dslc),log,verbose)

                return self 


################################################################################
def shpdetectionCSVtoSHP(inputfile,outputfile,date1 = None,date2 = None): 
        """Convert the .csv SNAP vector file to .shp file

        The function will convert the .csv file to .shp file.

        Args: 
                inputfile (str): .csv file from SNAP
                outputfile (str): .shp file
                date1 (str, Optional): Start time of the detection. [Default: `None`]
                date2 (str, Optional): End time of the detection. [Default: `None`]
        
        """
        data = pd.read_csv(inputfile,delimiter='\t',header=1)
        schema =  {'geometry': 'Point',
                'properties': {
                        'Detected_width': 'int',
                        'Detected_length': 'int',
                        'Start_Time': 'str',
                        'End_Time': 'str'}}
        with fiona.open(outputfile,'w',crs=from_epsg(4326),driver='ESRI Shapefile', schema=schema) as output:
                for idx, rowi in data.iterrows():
                        point = Point(float(rowi['Detected_lon:Double']), float(rowi['Detected_lat:Double']))
                        prop = {'Detected_width': int(rowi['Detected_width:Double']),
                                'Detected_length': int(rowi['Detected_length:Double']),
                                'Start_Time': date1,
                                'End_Time': date2,                                                        
                                }
                        output.write({'geometry':mapping(point),'properties': prop})



