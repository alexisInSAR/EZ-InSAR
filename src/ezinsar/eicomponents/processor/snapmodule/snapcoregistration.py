#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage the class for coregistration processing using SNAP

The module allows to create the EZ-InSAR coregistration class using SNAP. 
    
    (From `ezinsar` package)

Note: 
        Each function can directly used in Python script(s) or/and a Python terminal

Changelog:
        * 1.0.1: Bug fixes, Jan. 2025, Alexis Hrysiewicz 
        * 1.0.0: Initial version, Jul. 2024

"""

################################################################################
## Python packages
################################################################################
import os
import psutil
from typing import Optional, Union
import logging 

from ezinsar import constants
from ezinsar import usermessage
from ezinsar.eicomponents.roimodule import roitools
from ezinsar.eicomponents.jobmodule import jobrun, jobproctools
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Class to manage the EZ-InSAR job
##      (part of EZ-InSAR)
################################################################################
class coregistration:

        '''EZ-InSAR coregistration class for snap 
        
        Attributes:
                title (str): Name/Definition of the user [Default: `None`]
                workdirectory (str): Work directory of the coregistration processin. [Default: `None`]
                pathSLC (str): Path of the SLC directory. [Default: `None`]
                pathorbit (str): Path of the orbit directory. [Default: `None`]
                pathaux (str): Path of the aux-file directory. [Default: `None`]
                pathDEM (str): Path of the DEM directory. [Default: `None`]
                nameDEM (str): Name of the DEM file. [Default: `None`]
                typeDEM (str): Type of the DEM. [Default: `None`]
                pathstack (str): Path of the coregistration stack
                refdate (str): Reference date
                polarisation (list): List of polarisation. [Default: ``['VV']``]
                roi (str): Polygon of the Region of Interest. [Default: `None`]
                satellite (str): Satellite name. [Default: ``S1``]
                satmode (str): Satellite mode. [Default: ``SM``]
                relorbit (int): Relative orbit number. [Default: `None`]
                satpass (str): Satellite direction. [Default: `None`]
                email (dict): Dictionary of the emal parameters
                computercores (int): Number of threads. [Default: ``1``]
                processor (str): Processor. Here isce2. 
                modecropping (str): Mode of the cropping. [Default: ``auto``]
                modeforce (str): Forcing mode. [Default: `True`]
                mlazi (int): Multilook factor in azimuth
                mlran (int): Multilook factor in range 
                mlazidisplay (int): Multilook factor in azimuth
                mlrandisplay (int): Multilook factor in range 
                verbose (bool): Verbose mode. [Default: `True`]
                log (str): Log file
                gui (bool): GUI mode (not used). [Default: `False`]

        '''

        ################################################################################
        ## Initialistion of the class
        ################################################################################
        def __init__(self, 
                job: Optional[Union[any, None]] = None,
                title: Optional[Union[str, None]] = None,
                workdirectory: Optional[Union[str, None]] = None,
                pathSLC: Optional[Union[str, None]] = None,
                pathorbit: Optional[Union[str, None]] = None,
                pathaux: Optional[Union[str, None]] = None,
                pathDEM: Optional[Union[str, None]] = None, 
                nameDEM: Optional[Union[str, None]] = None,
                typeDEM: Optional[Union[str, None]] = None,
                pathstack: Optional[Union[str, None]] = None,
                refdate: Optional[Union[str, None]] = None,
                dates: Optional[Union[list, None]] = None,
                polarisation: Optional[Union[str, list]] = ['VV'],
                roi: Optional[Union[any, None]] = None,
                satellite: Optional[str] = 'S1',
                satmode: Optional[str] = 'IW',
                relorbit: Optional[Union[int, None]] = None,
                satpass: Optional[Union[str, None]] = None,
                email: Optional[Union[dict, None]] = None,
                computernbthread: Optional[Union[int, None]] = 4,
                processor: Optional[str] = 'snap',
                modecropping: Optional[Union[any, None]] = 'auto',
                modeforce:  Optional[bool] = True,
                mlazi: Optional[Union[int, None]] = None,
                mlran: Optional[Union[int, None]] = None,
                mlazidisplay: Optional[Union[int, None]] = None,
                mlrandisplay: Optional[Union[int, None]] = None,
                verbose: Optional[bool] = True,
                log: Optional[Union[str, None]] = None,
                gui: Optional[bool] = False,
                ):
                
                """Initilisation of the job for EZ-InSAR

                Args:
                        title (str): Name/Definition of the user [Default: `None`]
                        workdirectory (str): Work directory of the coregistration processin. [Default: `None`]
                        pathSLC (str): Path of the SLC directory. [Default: `None`]
                        pathorbit (str): Path of the orbit directory. [Default: `None`]
                        pathaux (str): Path of the aux-file directory. [Default: `None`]
                        pathDEM (str): Path of the DEM directory. [Default: `None`]
                        nameDEM (str): Name of the DEM file. [Default: `None`]
                        typeDEM (str): Type of the DEM. [Default: `None`]
                        pathstack (str): Path of the coregistration stack
                        refdate (str): Reference date
                        polarisation (list): List of polarisation. [Default: ``['VV']``]
                        roi (str): Polygon of the Region of Interest. [Default: `None`]
                        satellite (str): Satellite name. [Default: ``S1``]
                        satmode (str): Satellite mode. [Default: ``SM``]
                        relorbit (int): Relative orbit number. [Default: `None`]
                        satpass (str): Satellite direction. [Default: `None`]
                        email (dict): Dictionary of the emal parameters
                        computernbthread (int): Number of threads. [Default: ``4``]
                        processor (str): Processor. Here isce2. 
                        modecropping (str): Mode of the cropping. [Default: ``auto``]
                        modeforce (str): Forcing mode. [Default: `True`]
                        mlazi (int): Multilook factor in azimuth
                        mlran (int): Multilook factor in range 
                        mlazidisplay (int): Multilook factor in azimuth
                        mlrandisplay (int): Multilook factor in range 
                        verbose (bool): Verbose mode. [Default: `True`]
                        log (str): Log file
                        gui (bool): GUI mode (not used). [Default: `False`]

                Returns: 
                        ``esinsar.job``: EZ-InSAR Doris coregistration class

                Note: 
                        If a ``job`` input is given, EZ-InSAR will build the class based on its values. 

                """                 

                # User information
                if not job == None: 
                        self.title = 'Coregistration for %s' % (job.nameJob) 
                        self.workdirectory = job.workdirectory+os.sep+'coreg'
                        self.pathSLC = job.pathSLC
                        self.pathorbit = job.pathorbit
                        self.pathaux = job.pathaux
                        self.pathDEM = job.pathDEM
                        self.nameDEM = job.nameDEM
                        self.typeDEM = job.typeDEM
                        self.pathstack = job.workdirectory+os.sep+'input_files'
                        
                        if not dates == None:
                                self.dates = []
                                for di in job.SLClist['Date1']: 
                                        self.dates.append(di.split('T')[0].replace('-',''))
                                self.dates = self.dates
                                self.dates.sort()
                                self.refdate = self.dates[0]
                        else: 
                                self.dates = None
                                self.refdate = None

                        self.polarisation = job.polarisation
                        self.satellite = job.satellite
                        self.satmode = job.satmode
                        self.relorbit = job.relorbit
                        self.satpass = job.satpass
                        self.roi = job.roi

                else: 
                        self.title = title
                        self.workdirectory = workdirectory
                        self.pathSLC = pathSLC
                        self.pathorbit = pathorbit
                        self.pathaux = pathaux
                        self.pathDEM = pathDEM
                        self.nameDEM = nameDEM
                        self.typeDEM = typeDEM
                        self.pathstack = pathstack
                        self.refdate = refdate
                        self.dates = dates
                        if not dates == None:
                                self.dates.sort()

                        self.satellite = satellite
                        self.satmode = satmode
                        self.relorbit = relorbit
                        self.satpass = satpass
                        self.polarisation = polarisation
                        if not roi == None: 
                                self.roi = roitools.importroi(self, roi)
                        else: 
                                self.roi = None
                
                if not self.roi == None:
                        self.roi = str(self.roi)

                if email == None:
                        self.email = dict()
                        self.email['send'] = {'value': False, 
                                                'description': 'Enable the email sending', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.email['mode'] = {'value': 'all', 
                                                'description': 'Define when emails will be send.', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.email['sender'] = {'value': 'test.test@gmail.com', 
                                                'description': 'Sender email', 
                                                'format': 'email',
                                                'valuelist': None}
                        self.email['receiver'] = {'value': 'test.test@gmail.com', 
                                                'description': 'Receiver email', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.email['password'] = {'value': 'xxxxx', 
                                                'description': 'Password', 
                                                'format': 'password',
                                                'valuelist': None}
                        self.email['SMTPserver'] = {'value': 'smtp.gmail.com', 
                                                'description': 'SMTP server', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.email['SMTPport'] = {'value': 465, 
                                                'description': 'SMTP port', 
                                                'format': 'int',
                                                'valuelist': None}
                else:
                        self.email = email

                self.computernbthread = computernbthread
                self.processor = 'snap'
                self.modecropping = modecropping
                self.modeforce = modeforce

                self.mlazi = mlazi
                self.mlran = mlran
                self.mlazidisplay = mlazidisplay
                self.mlrandisplay = mlrandisplay
                if self.mlazi == None: 
                        if self.satmode == 'IW':
                                self.mlazi = 3
                        else: 
                                self.mlazi = 2
                if self.mlran == None: 
                        if self.satmode == 'IW':
                                self.mlran = 15
                        else: 
                                self.mlran = 2
                if self.mlazidisplay == None: 
                        if self.satmode == 'IW':
                                self.mlazidisplay = 3*3
                        else: 
                                self.mlazidisplay = 2
                if self.mlrandisplay == None: 
                        if self.satmode == 'IW':
                                self.mlrandisplay = 15*3
                        else: 
                                self.mlrandisplay = 2

                # For the Step 1: Check the SLC files
                self.checkSLC = dict()
                self.checkSLC['name'] = {'value': 'Step 1: Check the SLC files', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.checkSLC['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
   
                # For the Step 2: Detect the coarse reference date
                self.coarserefdate = dict()
                self.coarserefdate['name'] = {'value': 'Step 2: Detect the coarse reference date', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.coarserefdate['useorbit'] = {'value': False, 
                                        'description': 'to do', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.coarserefdate['useDEM'] = {'value': True, 
                                        'description': 'to do', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.coarserefdate['done'] = {'value': False, 
                                        'description': 'to do', 
                                        'format': 'bool',
                                        'valuelist': None}
                
                # For the Step 3: Import the SLCs
                self.importSLC = dict()
                self.importSLC['name'] = {'value': 'Step 3: Import the SLCs', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.importSLC['applyorbit'] = {'value': True, 
                                        'description': 'Enable the use of precise orbit files. Only for Sentinel-1', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.importSLC['createbmp'] = {'value': True, 
                                        'description': 'Enable the creation of .bmp images for visualisation', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.importSLC['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
                
                # For the Step 4: Refine the reference date
                self.refinerefdate = dict()
                self.refinerefdate['name'] = {'value': 'Step 4: Refine the reference date', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.refinerefdate['process'] = {'value': True, 
                                        'description': 'Enable the processing', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.refinerefdate['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
                
                # For the Step 5: Coregistration of the SLCs
                self.coreg = dict()
                self.coreg['name'] = {'value': 'Step 5: Coregistration', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                
                if not self.satmode == 'IW':

                        self.coreg['initoffset'] = {'value': 'Orbit', 
                                                'description': 'to do', 
                                                'format': 'list',
                                                'valuelist': ['Orbit','Product Geolocation']}
                        self.coreg['demodulate'] = {'value': False, 
                                                'description': 'to do', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.coreg['numGCPtoGenerate'] = {'value': 300, 
                                                'description': 'to do', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.coreg['coarseRegistrationWindowWidth'] = {'value': 128, 
                                                'description': 'to do', 
                                                'format': 'list',
                                                'valuelist': [32, 64, 128, 256, 512, 1024, 2048]}
                        self.coreg['coarseRegistrationWindowHeight'] = {'value': 128, 
                                                'description': 'to do', 
                                                'format': 'list',
                                                'valuelist': [32, 64, 128, 256, 512, 1024, 2048]}
                        self.coreg['rowInterpFactor'] = {'value': 4, 
                                                'description': 'to do', 
                                                'format': 'list',
                                                'valuelist': [2, 4, 8, 16]}
                        self.coreg['columnInterpFactor'] = {'value': 4, 
                                                'description': 'to do', 
                                                'format': 'list',
                                                'valuelist': [2, 4, 8, 16]}
                        self.coreg['maxIteration'] = {'value': 10, 
                                                'description': 'to do', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.coreg['gcpTolerance'] = {'value': 0.25, 
                                                'description': 'to do', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.coreg['applyFineRegistration'] = {'value': True, 
                                                'description': 'to do', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.coreg['inSAROptimized'] = {'value': True, 
                                                'description': 'to do', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.coreg['fineRegistrationWindowWidth'] = {'value': 32, 
                                                'description': 'to do', 
                                                'format': 'list',
                                                'valuelist': [32, 64, 128, 256, 512]}
                        self.coreg['fineRegistrationWindowHeight'] = {'value': 32, 
                                                'description': 'to do', 
                                                'format': 'list',
                                                'valuelist': [32, 64, 128, 256, 512]}
                        self.coreg['fineRegistrationWindowAccAzimuth'] = {'value': 8, 
                                                'description': 'to do', 
                                                'format': 'list',
                                                'valuelist': [2, 4, 8, 16, 64]}
                        self.coreg['fineRegistrationWindowAccRange'] = {'value': 8, 
                                                'description': 'to do', 
                                                'format': 'list',
                                                'valuelist': [2, 4, 8, 16, 64]}
                        self.coreg['fineRegistrationOversampling'] = {'value': 32, 
                                                'description': 'to do', 
                                                'format': 'list',
                                                'valuelist': [2, 4, 8, 16, 32, 64]}
                        self.coreg['coherenceWindowSize'] = {'value': 3, 
                                                'description': 'to do', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.coreg['coherenceThreshold'] = {'value': 0.3, 
                                                'description': 'to do', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.coreg['useSlidingWindow'] = {'value': False, 
                                                'description': 'to do', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.coreg['computeOffset'] = {'value': False, 
                                                'description': 'to do', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.coreg['onlyGCPsOnLand'] = {'value': True, 
                                                'description': 'to do', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.coreg['rmsThreshold'] = {'value': 0.05, 
                                                'description': 'to do', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.coreg['warpPolynomialOrder'] = {'value': 2, 
                                                'description': 'to do', 
                                                'format': 'list',
                                                'valuelist': [1,2,3]}
                        self.coreg['interpolationMethod'] = {'value': 'Cubic convolution (6 points)', 
                                                'description': 'to do', 
                                                'format': 'list',
                                                'valuelist': ['Nearest-neighboor interpolation',
                                                        'Bilinear interpolation',
                                                        'Bicubic interpolation',
                                                        'bicubic2 interpolation',
                                                        'Linear interpolation',
                                                        'Cubic convolution (4 points)',
                                                        'Cubic convolution (6 points)',
                                                        'Truncated sinc (6 points)',
                                                        'Truncated sinc (8 points)',
                                                        'Truncated sinc (16 points)']}
                        self.coreg['demRefinement'] = {'value': False, 
                                                'description': 'to do', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.coreg['excludeMaster'] = {'value': False, 
                                                'description': 'to do', 
                                                'format': 'bool',
                                                'valuelist': None}
                        # demName SRTM 3Sec
                        # openResidualsFile false

                        self.coreg['remodulate'] = {'value': False, 
                                                'description': 'to do', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                else: 
                        self.coreg['demResamplingMethod'] = {'value': 'BILINEAR_INTERPOLATION', 
                                        'description': 'Resampling method', 
                                        'format': 'list',
                                        'valuelist': ['NEAREST_NEIGHBOUR',
                                                      'BILINEAR_INTERPOLATION',
                                                      'CUBIC_CONVOLUTION',
                                                      'BISINC_5_POINT_INTERPOLATION',
                                                      'BISINC_11_POINT_INTERPOLATION',
                                                      'BISINC_21_POINT_INTERPOLATION',
                                                      'BICUBIC_CONVOLUTION']}
                        self.coreg['resamplingType'] = {'value': 'BISINC_5_POINT_INTERPOLATION',
                                                'description': 'Resampling algorithm', 
                                                'format': 'list',
                                                'valuelist': ['BISINC_5_POINT_INTERPOLATION']}
                        self.coreg['externalDEMNoDataValue'] = {'value': '0',
                                                'description': 'Value of NaN values', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.coreg['maskOutAreaWithoutElevation'] = {'value': True, 
                                        'description': 'Mask the area without elevation', 
                                        'format': 'bool',
                                        'valuelist': None}
                        self.coreg['disableReramp'] = {'value': False, 
                                        'description': 'Disable the reramping', 
                                        'format': 'bool',
                                        'valuelist': None}
                        
                        self.coreg['ESDcomputation'] = {'value': True, 
                                        'description': 'Enable the ESD computation', 
                                        'format': 'bool',
                                        'valuelist': None}
                        
                        self.coreg['fineWinWidthStr'] = {'value': 512, 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'int',
                                        'valuelist': None}
                        self.coreg['fineWinHeightStr'] = {'value': 512, 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'int',
                                        'valuelist': None}
                        self.coreg['fineWinAccAzimuth'] = {'value': 16, 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'int',
                                        'valuelist': None}
                        self.coreg['fineWinAccRange'] = {'value': 16, 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'int',
                                        'valuelist': None}
                        self.coreg['fineWinOversampling'] = {'value': 128, 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'int',
                                        'valuelist': None}
                        self.coreg['xCorrThreshold'] = {'value': 0.1, 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'float',
                                        'valuelist': None}
                        self.coreg['cohThreshold'] = {'value': 0.3, 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'float',
                                        'valuelist': None}
                        self.coreg['numBlocksPerOverlap'] = {'value': 10, 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'int',
                                        'valuelist': None}
                        self.coreg['esdEstimator'] = {'value': 'Periodogram', 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'list',
                                        'valuelist': ['Periodogram','Average']}
                        self.coreg['weightFunc'] = {'value': 'Inv Quadratic', 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'list',
                                        'valuelist': ['Inv Quadratic','None','Linear','Quadratic']}
                        self.coreg['temporalBaselineType'] = {'value': 'Number of images', 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'list',
                                        'valuelist': ['Number of images','Number of days']}
                        self.coreg['maxTemporalBaseline'] = {'value': 4, 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'int',
                                        'valuelist': None}
                        self.coreg['integrationMethod'] = {'value': 'L1 and L2', 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'list',
                                        'valuelist': ['L1','L2','L1 and L2']}
                        self.coreg['doNotWriteTargetBands'] = {'value': False, 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'bool',
                                        'valuelist': None}
                        self.coreg['useSuppliedRangeShift'] = {'value': False, 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'bool',
                                        'valuelist': None}
                        self.coreg['overallRangeShift'] = {'value': 0.0, 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'float',
                                        'valuelist': None}
                        self.coreg['useSuppliedAzimuthShift'] = {'value': False, 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'bool',
                                        'valuelist': None}
                        self.coreg['overallAzimuthShift'] = {'value': 0.0, 
                                        'description': 'Parameter for the ESD computation', 
                                        'format': 'float',
                                        'valuelist': None}

                self.coreg['createbmpifg'] = {'value': True, 
                                        'description': 'Create .bmp images of interferograms wihtout any correction', 
                                        'format': 'bool',
                                        'valuelist': None}        
                self.coreg['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
                
                # For the Step 6: Cleaning  
                self.cleanstack = dict()
                self.cleanstack['name'] = {'value': 'Step 6: Cleaning', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.cleanstack['process'] = {'value': True, 
                                        'description': 'Enable the processing', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.cleanstack['keepinputfiles'] = {'value': False, 
                                        'description': 'Keep the input files', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.cleanstack['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}

                if not job == None: 
                        self.verbose = job.verbose
                        self.log = job.log
                        self.gui = job.gui
                else: 
                        self.verbose = verbose
                        self.log = log
                        self.gui = gui
                
                if not self.log == None: 
                        logging.basicConfig(filename=self.log, filemode='a', 
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                        logger=logging.getLogger() 
                        logger.setLevel(usermessage.definelevel(constants.__loggingmode__)) 
                        logger.info('Creation of a EZ-InSAR Coregistration processing')

                # Initilisation by the user
                jobproctools.check(self,verbose=False,mode='low')
                
        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def print(self):
                """Print the Coregistration-processing attributes for EZ-InSAR"""

                attrs = vars(self)
                print(', '.join("%s: %s" % item for item in attrs.items()))

                return self

        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def check(self,**kwargs):
                """check and display the Coregistration-processing attributes for EZ-InSAR"""

                self = jobproctools.check(self,**kwargs)

                return self
        
        ################################################################################
        ## Run the coregistration
        ################################################################################
        def run(self,**kwargs):
                """Run the coregsitration using SNAP processor"""
 
                self = jobrun.run(self,**kwargs)

                return self
                
                
        