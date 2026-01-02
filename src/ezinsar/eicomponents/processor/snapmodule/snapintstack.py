#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage the class for intensity-stack processing using SNAP

The module allows to create the EZ-InSAR intensity-stack class using SNAP. 
    
    (From `ezinsar` package)

Note: 
        Each function can directly used in Python script(s) or/and a Python terminal

Changelog:
        * 1.0.0: Initial version, Jul. 2024

"""

################################################################################
## Python packages
################################################################################
import os
from typing import Optional, Union
import logging 
import glob
import shutil

from ezinsar import constants
from ezinsar import usermessage
from ezinsar.eicomponents.roimodule import roitools
from ezinsar.eicomponents.processor.snapmodule import snaptools
from ezinsar.eicomponents.jobmodule import jobrun, jobproctools
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Class to manage the EZ-InSAR job
##      (part of EZ-InSAR)
################################################################################
class intstack:

        '''EZ-InSAR intstack class for snap 
        
        Attributes:
                title (str): Name/Definition of the user [Default: `None`]
                workdirectory (str): Work directory of the coregistration processin. [Default: `None`]
                pathSLC (str): Path of the SLC directory. [Default: `None`]
                pathorbit (str): Path of the orbit directory. [Default: `None`]
                pathaux (str): Path of the aux-file directory. [Default: `None`]
                pathDEM (str): Path of the DEM directory. [Default: `None`]
                nameDEM (str): Name of the DEM file. [Default: `None`]
                typeDEM (str): Type of the DEM. [Default: `None`]
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
                polarisation: Optional[Union[str, list]] = ['VV','VH'],
                roi: Optional[Union[any, None]] = None,
                satellite: Optional[str] = 'S1',
                satmode: Optional[str] = 'IW',

                relorbit: Optional[Union[int, None]] = None,
                satpass: Optional[Union[str, None]] = None,

                email: Optional[Union[dict, None]] = None,
                computercores: Optional[Union[int, None]] = 1, # Number of processes in parallel
                processor: Optional[str] = 'snap',

                modecropping: Optional[Union[any, None]] = 'auto',
                modeforce:  Optional[bool] = True,

                mlazi: Optional[Union[int, None]] = None,
                mlran: Optional[Union[int, None]] = None,

                verbose: Optional[bool] = True,
                log: Optional[Union[str, None]] = None,
                gui: Optional[bool] = False,
                ):
                
                """Initilisation of the job for EZ-InSAR
                
                Args:
                        job (``ezinsar.job``): EZ-InSAR job
                        title (str): Name/Definition of the user [Default: `None`]
                        workdirectory (str): Work directory of the coregistration processin. [Default: `None`]
                        pathSLC (str): Path of the SLC directory. [Default: `None`]
                        pathorbit (str): Path of the orbit directory. [Default: `None`]
                        pathaux (str): Path of the aux-file directory. [Default: `None`]
                        pathDEM (str): Path of the DEM directory. [Default: `None`]
                        nameDEM (str): Name of the DEM file. [Default: `None`]
                        typeDEM (str): Type of the DEM. [Default: `None`]
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
                        verbose (bool): Verbose mode. [Default: `True`]
                        log (str): Log file
                        gui (bool): GUI mode (not used). [Default: `False`]

                Returns: 
                        ``esinsar.job``: EZ-InSAR Doris intstack class

                Note: 
                        If a ``job`` input is given, EZ-InSAR will build the class based on its values. 

                """                

                # User information
                if not job == None: 
                        self.title = 'Intensity processing for %s' % (job.nameJob) 
                        self.workdirectory = job.workdirectory+os.sep+'intensity'
                        self.pathSLC = job.pathSLC
                        self.pathorbit = job.pathorbit
                        self.pathaux = job.pathaux
                        self.pathDEM = job.pathDEM
                        self.nameDEM = job.nameDEM
                        self.typeDEM = job.typeDEM

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

                self.computercores = computercores
                self.processor = 'snap'
                self.modecropping = modecropping
                self.modeforce = modeforce

                self.mlazi = mlazi
                self.mlran = mlran
                if self.mlazi == None: 
                        if self.satmode == 'IW':
                                self.mlazi = 1
                        else: 
                                self.mlazi = 2
                if self.mlran == None: 
                        if self.satmode == 'IW':
                                self.mlran = 5
                        else: 
                                self.mlran = 2

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
                
                # # For the Step 2: Import the SLCs
                self.importSLC = dict()
                self.importSLC['name'] = {'value': 'Step 2: Import the SLCs', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.importSLC['applyorbit'] = {'value': True, 
                                        'description': 'Enable the use of precise orbits. Only for Sentinel-1', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.importSLC['removenoise'] = {'value': True, 
                                        'description': 'Enable the removal of thermal noise. Only for Sentinel-1', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.importSLC['sigma0'] = {'value': True, 
                                        'description': 'Enable the computation of sigma0', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.importSLC['gamma0'] = {'value': True, 
                                        'description': 'Enable the computation of gamma0', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.importSLC['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
                
                # For the Step 3: Multilooking
                self.multilook = dict()
                self.multilook['name'] = {'value': 'Step 3: Multilooking', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.multilook['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}

                # For the Step 4: Filter
                self.filter = dict()
                self.filter['name'] = {'value': 'Step 4: Filter', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.filter['process'] = {'value': True, 
                                        'description': 'Enable the processing', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.filter['filter'] = {'value': 'Lee', 
                                        'description': 'Name of the use filter', 
                                        'format': 'list',
                                        'valuelist': ['Boxcar','Median','Frost','Gamma Mag','Lee','Refined Lee','Lee Sigma','IDAN']}
                self.filter['filterSizeX'] = {'value': 3, 
                                        'description': 'Size in X of the kernel', 
                                        'format': 'int',
                                        'valuelist': None}
                self.filter['filterSizeY'] = {'value': 3, 
                                        'description': 'Size in Y of the kernl', 
                                        'format': 'int',
                                        'valuelist': None}
                self.filter['dampingFactor'] = {'value': 2, 
                                        'description': 'Damping Factor', 
                                        'format': 'int',
                                        'valuelist': None}
                self.filter['estimateENL'] = {'value': False, 
                                        'description': 'to do', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.filter['enl'] = {'value': 1.0, 
                                        'description': 'to do', 
                                        'format': 'float',
                                        'valuelist': None}
                self.filter['numLooksStr'] = {'value': 1, 
                                        'description': 'to do', 
                                        'format': 'list',
                                        'valuelist': [1,2,3,4]}
                self.filter['numLooksStr'] = {'value': 2, 
                                        'description': 'to do', 
                                        'format': 'list',
                                        'valuelist': [1,2,3,4]}
                self.filter['windowSize'] = {'value': '5x5', 
                                        'description': 'Window size', 
                                        'format': 'list',
                                        'valuelist': ['5x5','7x7','9x9','11x11','13x13','15x15','17x17']}
                self.filter['targetWindowSizeStr'] = {'value': '3x3', 
                                        'description': 'Targeted window size', 
                                        'format': 'list',
                                        'valuelist': ['3x3','5x5']}
                self.filter['sigmaStr'] = {'value': 0.9, 
                                        'description': 'Simga factor', 
                                        'format': 'list',
                                        'valuelist': [0.5,0.6,0.7,0.8,0.9]}
                self.filter['anSize'] = {'value': 50, 
                                        'description': 'to do', 
                                        'format': 'int',
                                        'valuelist': None}
                self.filter['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
                
                # For the Step 5: Terraincal
                self.terraincal = dict()
                self.terraincal['name'] = {'value': 'Step 5: Terrain Calibration', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.terraincal['process'] = {'value': True, 
                                        'description': 'Enable the processing', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.terraincal['demResamplingMethod'] = {'value': 'BILINEAR_INTERPOLATION', 
                                        'description': 'Resampling method', 
                                        'format': 'list',
                                        'valuelist': ['NEAREST_NEIGHBOUR',
                                                      'BILINEAR_INTERPOLATION',
                                                      'CUBIC_CONVOLUTION',
                                                      'BISINC_5_POINT_INTERPOLATION',
                                                      'BISINC_11_POINT_INTERPOLATION',
                                                      'BISINC_21_POINT_INTERPOLATION',
                                                      'BICUBIC_CONVOLUTION']}
                self.terraincal['additionalOverlap'] = {'value': 0.1, 
                                        'description': 'Additional overlap value', 
                                        'format': 'float',
                                        'valuelist': None}
                self.terraincal['oversamplingMultiple'] = {'value': 2.0, 
                                        'description': 'Oversampling factor', 
                                        'format': 'float',
                                        'valuelist': None}
                self.terraincal['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}

                # For the Step 6: geocode
                self.geocode = dict()
                self.geocode['name'] = {'value': 'Step 6: Geocode', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.geocode['Xdem_overfactor'] = {'value': 1.0, 
                                        'description': 'DEM oversampling in X', 
                                        'format': 'float',
                                        'valuelist': None}
                self.geocode['Ydem_overfactor'] = {'value': 1.0, 
                                        'description': 'DEM oversampling in Y', 
                                        'format': 'float',
                                        'valuelist': None}
                self.geocode['demResamplingMethod'] = {'value': 'BILINEAR_INTERPOLATION', 
                                        'description': 'Resampling method for the DEM', 
                                        'format': 'list',
                                        'valuelist': ['NEAREST_NEIGHBOUR',
                                                      'BILINEAR_INTERPOLATION',
                                                      'CUBIC_CONVOLUTION',
                                                      'BISINC_5_POINT_INTERPOLATION',
                                                      'BISINC_11_POINT_INTERPOLATION',
                                                      'BISINC_21_POINT_INTERPOLATION',
                                                      'BICUBIC_CONVOLUTION']}
                self.geocode['imgResamplingMethod'] = {'value': 'BILINEAR_INTERPOLATION', 
                                        'description': 'Resampling method for the image', 
                                        'format': 'list',
                                        'valuelist': ['NEAREST_NEIGHBOUR',
                                                      'BILINEAR_INTERPOLATION',
                                                      'CUBIC_CONVOLUTION',
                                                      'BISINC_5_POINT_INTERPOLATION',
                                                      'BISINC_11_POINT_INTERPOLATION',
                                                      'BISINC_21_POINT_INTERPOLATION',
                                                      'BICUBIC_CONVOLUTION']}
                self.geocode['dB'] = {'value': True, 
                                        'description': 'Enable the conversion into dB', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.geocode['nondata'] = {'value': 0.0, 
                                        'description': 'Value for NaN values', 
                                        'format': 'float',
                                        'valuelist': None}
                self.geocode['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}

                # For the Step 7: clean
                self.clean = dict()
                self.clean['name'] = {'value': 'Step 7: Cleaning', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.clean['process'] = {'value': True, 
                                        'description': 'Enable the processing', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.clean['keepdirectory'] = {'value': False, 
                                        'description': 'Keep the directories', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.clean['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}

                # For the Step 8: update
                self.update = dict()
                self.update['name'] = {'value': 'Step 8: Update', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.update['modeforce'] = {'value': False, 
                                        'description': 'Forcing mode', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.update['done'] = {'value': False, 
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
                        logger.info('Creation of a EZ-InSAR intstack processing')

                # Initilisation by the user
                jobproctools.check(self,verbose=False,mode='low')
                
        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def print(self):
                """Print the intstack-processing attributes for EZ-InSAR"""

                attrs = vars(self)
                print(', '.join("%s: %s" % item for item in attrs.items()))

                return self

        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def check(self,**kwargs):
                """check and display the intstack-processing attributes for EZ-InSAR"""

                self = jobproctools.check(self,**kwargs)

                return self
        
        ################################################################################
        ## Run the coregistration
        ################################################################################
        def run(self,**kwargs):
                """Run the intstack using SNAP processor"""
 
                self = jobrun.run(self,**kwargs)

                return self
                
        ################################################################################
        ## Delete a date within the coregistration stack
        ################################################################################
        def deletedate(self,date,modifydatefile = False):
                """Delete a date within the intstack stack"""
                
                listfile = glob.glob(self.workdirectory+os.sep+'*'+os.sep+date+'*')
                
                for li in listfile:
                        if not (os.sep+'geotiff'+os.sep) in li:
                                if os.path.isfile(li):
                                        os.remove(li)
                                elif os.path.isdir(li):
                                        shutil.rmtree(li)

                if modifydatefile == True:
                        listdate = snaptools.readdatefile(self.workdirectory+os.sep+'dates')       
                        with open(self.workdirectory+os.sep+'dates','w') as fout:
                                for di in listdate:
                                        if not di == date:
                                                fout.write('%s\n' % (di))

                return self
                
        