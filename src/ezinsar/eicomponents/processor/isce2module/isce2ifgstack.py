#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage the class for interferometric processing using ISCE-2

The module allows to create the EZ-InSAR interferogram-stack class using ISCE-2. 
    
    (From `ezinsar` package)

Changelog:
        * 1.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import os
import psutil
from typing import Optional, Union
import logging 

from ezinsar import constants
__copyright__ = constants.__copyright__
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
class ifgstack:

        '''EZ-InSAR coregistration class for ISCE-2 
        
        Attributes:
                title (str): Name/Definition of the user [Default: `None`]
                workdirectory (str): Work directory of the coregistration processin. [Default: `None`]
                coregdirectory (str): Previous coreg directory of the coregistration processing. [Default: `None`]
                modestack (str): Mode of the ifg stack 
                pathstack (str): Path of the directory for the coregistred SLCs. [Default: `None`]
                pathDEM (str): Path of the DEM directory. [Default: `None`]
                nameDEM (str): Name of the DEM file. [Default: `None`]
                typeDEM (str): Type of the DEM. [Default: `None`]
                modeDEM (str): Type of the DEM. [Default: `None`]
                satellite (str): Satellite name. [Default: ``S1``]
                satmode (str): Satellite mode. [Default: ``SM``]
                relorbit (int): Relative orbit number. [Default: `None`]
                satpass (str): Satellite direction. [Default: `None`]
                refdate (str): Reference date (YYYYMMDD). [Default: `None`]
                polarisation (list): List of polarisation. [Default: ``['VV']``]
                roi (str): Polygon of the Region of Interest. [Default: `None`]
                modeacq (str): Mode of the acquisition
                email (dict): Dictionary of the emal parameters
                computercores (int): Number of threads. [Default: ``1``]
                processor (str): Processor. Here isce2. 
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
                coregdirectory: Optional[Union[str, None]] = None,
                modestack: Optional[str] = 'normal', # Can be normal, StaMPS_PS, StaMPS_SBAS, StaMPS_PSSBAS, MintPy

                modeforce: Optional[bool] = True,

                pathstack: Optional[Union[str, None]] = None,
                pathDEM: Optional[Union[str, None]] = None, 
                nameDEM: Optional[Union[str, None]] = None,
                typeDEM: Optional[Union[str, None]] = None,
                modeDEM: Optional[Union[str, None]] = 'exact',

                satellite: Optional[str] = 'S1',
                satmode: Optional[str] = 'IW',

                relorbit: Optional[Union[int, None]] = None,
                satpass: Optional[Union[str, None]] = None,

                refdate: Optional[Union[str, None]] = None,
                polarisation: Optional[Union[str, list]] = ['VV'],
                roi: Optional[Union[any, None]] = None,
                modeacq: Optional[str] = 'monostatic',

                email: Optional[Union[dict, None]] = None,
                computercores: Optional[Union[int, None]] = 1, 
                processor: Optional[str] = 'isce2',

                mlazi: Optional[Union[int, None]] = None,
                mlran: Optional[Union[int, None]] = None,

                verbose: Optional[bool] = True,
                log: Optional[Union[str, None]] = None,
                gui: Optional[bool] = False,

                ):
                
                """Initilisation of the ifgstack job for EZ-InSAR

                Args:
                        job (``ezinsar.job``): EZ-InSAR job
                        title (str): Name/Definition of the user [Default: `None`]
                        workdirectory (str): Work directory of the coregistration processin. [Default: `None`]
                        modestack (str): Mode of the ifg stack 
                        pathstack (str): Path of the directory for the coregistred SLCs. [Default: `None`]
                        pathDEM (str): Path of the DEM directory. [Default: `None`]
                        nameDEM (str): Name of the DEM file. [Default: `None`]
                        typeDEM (str): Type of the DEM. [Default: `None`]
                        modeDEM (str): Type of the DEM. [Default: `None`]
                        satellite (str): Satellite name. [Default: ``S1``]
                        satmode (str): Satellite mode. [Default: ``SM``]
                        relorbit (int): Relative orbit number. [Default: `None`]
                        satpass (str): Satellite direction. [Default: `None`]
                        refdate (str): Reference date (YYYYMMDD). [Default: `None`]
                        polarisation (list): List of polarisation. [Default: ``['VV']``]
                        roi (str): Polygon of the Region of Interest. [Default: `None`]
                        modeacq (str): Mode of the acquisition
                        email (dict): Dictionary of the emal parameters
                        computercores (int): Number of threads. [Default: ``1``]
                        processor (str): Processor. Here isce2. 
                        mlazi (int): Multilook factor in azimuth
                        mlran (int): Multilook factor in range 
                        verbose (bool): Verbose mode. [Default: `True`]
                        log (str): Log file
                        gui (bool): GUI mode (not used). [Default: `False`]

                Returns: 
                        ``esinsar.job``: EZ-InSAR Doris ifgstack class

                Note: 
                        If a ``job`` input is given, EZ-InSAR will build the class based on its values. 

                """                 

                # User information
                if not job == None: 
                        self.title = 'Interferometric stack for %s' % (job.title) 

                        if os.sep+'coreg' in job.workdirectory: 
                                self.workdirectory = job.workdirectory.replace(os.sep+'coreg',os.sep)+'ifgstack'
                                self.coregdirectory = job.workdirectory
                                self.pathSLCdirectory = job.pathSLC
                                self.pathorbitdirectory = job.pathorbit
                                self.pathauxdirectory = job.pathaux
                        else:
                                self.workdirectory = job.workdirectory+os.sep+'ifgstack'

                                # required by Docker
                                self.coregdirectory = None
                                self.pathSLCdirectory = None
                                self.pathorbitdirectory = None
                                self.pathauxdirectory = None
    
                        self.pathDEM = job.pathDEM
                        self.nameDEM = job.nameDEM
                        self.typeDEM = job.typeDEM

                        self.pathstack = job.pathstack

                        try:
                                self.refdate = job.refdate
                        except:
                                self.refdate = None

                        self.polarisation = job.polarisation
                        self.satellite = job.satellite
                        self.satmode = job.satmode
                        self.roi = job.roi
                        self.relorbit = job.relorbit
                        self.satpass = job.satpass

                        self.email = job.email
                        self.computercores = job.computercores
                        self.processor = job.processor

                        self.mlazi = job.mlazi
                        self.mlran = job.mlran

                else: 
                        self.title = title
                        self.workdirectory = workdirectory
                        self.coregdirectory = coregdirectory
                        self.pathSLCdirectory = None
                        self.pathorbitdirectory = None
                        self.pathauxdirectory = None

                        self.pathDEM = pathDEM
                        self.nameDEM = nameDEM
                        self.typeDEM = typeDEM

                        self.pathstack = pathstack

                        self.refdate = refdate
                        self.polarisation = polarisation
                        self.satellite = satellite
                        self.satmode = satmode     
                        self.relorbit = relorbit
                        self.satpass = satpass                  
                        
                        if not roi == None: 
                                self.roi = roitools.importroi(self, roi)
                        else: 
                                self.roi = None

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

                        self.processor = 'isce2'

                        self.mlazi = mlazi
                        self.mlran = mlran
                        
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

                self.modestack = modestack

                if self.modestack in ['StaMPS_PS','StaMPS_SBAS','StaMPS_PSSBAS']:
                        self.mlran = 1
                        self.mlazi = 1

                if not self.roi == None:
                        self.roi = str(self.roi)        

                self.modeforce = modeforce 
                self.modeDEM = modeDEM

                self.modeacq = modeacq
                self.processor = processor

                # For the Step 1: Build the interferogram network
                self.ifgnetwork = dict()
                self.ifgnetwork['name'] = {'value': 'Step 1: Build the interferogram network', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.ifgnetwork['bperp_min'] = {'value': '-', 
                                        'description': 'Min. threshold of perpendicular baselines [m]', 
                                        'format': 'int-',
                                        'valuelist': None}
                self.ifgnetwork['bperp_max'] = {'value': '-', 
                                        'description': 'Max. threshold of perpendicular baselines [m]', 
                                        'format': 'int-',
                                        'valuelist': None}
                self.ifgnetwork['delta_T_min'] = {'value': '-', 
                                        'description': 'Min. threshold of temporal baselines [day]', 
                                        'format': 'int-',
                                        'valuelist': None}
                self.ifgnetwork['delta_T_max'] = {'value': '-', 
                                        'description': 'Max. threshold of temporal baselines [day]', 
                                        'format': 'int-',
                                        'valuelist': None}
                self.ifgnetwork['delta_n_max'] = {'value': 1, 
                                        'description': 'Max. number of interferometric connections', 
                                        'format': 'int-',
                                        'valuelist': None}
                self.ifgnetwork['delta_difg'] = {'value': 6, 
                                        'description': 'Average temporal sampling in day', 
                                        'format': 'int-',
                                        'valuelist': None}
                self.ifgnetwork['SBAS_opti'] = {'value': False, 
                                        'description': 'Enable the use of optimised interferometruic network', 
                                        'format': 'list',
                                        'valuelist': [False,'delaunay','long-term']}
                self.ifgnetwork['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
                
                 
                # For the Step 2: Compute the interferogram images
                if self.satmode == 'IW':
                        self.generate_burst_igram = dict()
                        self.generate_burst_igram['name'] = {'value': 'Step 2: Compute the interferogram images', 
                                                'description': 'Name fo the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.generate_burst_igram['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.generate_igram = dict()
                        self.generate_igram['name'] = {'value': 'Step 2: Compute the interferogram images', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.generate_igram['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                if self.satmode == 'IW':
                        # For the Step 3: Merge the interferogram images
                        self.merge_burst_igram = dict()
                        self.merge_burst_igram['name'] = {'value': 'Step 3: Merge the interferogram images', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.merge_burst_igram['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                if self.satmode == 'IW':
                        idx = 4
                else: 
                        idx = 3

                # For the Step: Filtering and coherence computation
                self.filter_coherence = dict()
                self.filter_coherence['name'] = {'value': 'Step %s: Filtering and coherence computation' % (idx), 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.filter_coherence['process'] = {'value': True, 
                                        'description': 'Enable the processing', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.filter_coherence['strength'] = {'value': 0.25, 
                                        'description': 'Strength of the filter', 
                                        'format': 'float',
                                        'valuelist': None}
                self.filter_coherence['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
                idx = idx + 1

                # For the Step: Unwrap the interferograms
                self.unwrap = dict()
                self.unwrap['name'] = {'value': 'Step %s: Unwrap the interferograms' % (idx), 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.unwrap['process'] = {'value': True, 
                                        'description': 'Enable the processing', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.unwrap['nomcf'] = {'value': False, 
                                        'description': 'Initialisation method', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.unwrap['method'] = {'value': 'snaphu', 
                                        'description': 'Unwrapping method/software', 
                                        'format': 'list',
                                        'valuelist': ['snaphu']}
                self.unwrap['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
                idx = idx + 1

                # For the Step: Geocode the results
                self.ifggeocoding = dict()
                self.ifggeocoding['name'] = {'value': 'Step %s: Geocode the results' % (idx), 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.ifggeocoding['process'] = {'value': True, 
                                        'description': 'Enable the processing', 
                                        'format': 'bool',
                                        'valuelist': None} 
                self.ifggeocoding['DEMoverlon'] = {'value': 1.0, 
                                        'description': 'Oversampling factor for the DEM grid in longitude', 
                                        'format': 'float',
                                        'valuelist': None} 
                self.ifggeocoding['DEMoverlat'] = {'value': 1.0, 
                                        'description': 'Oversampling factor for the DEM grid in longitude', 
                                        'format': 'float',
                                        'valuelist': None} 
                self.ifggeocoding['uchargeotiff'] = {'value': True, 
                                        'description': 'Enable the saving in uchar', 
                                        'format': 'bool',
                                        'valuelist': None} 
                self.ifggeocoding['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None} 

                # For the Step: Finalise the stack
                self.finalstack = dict()
                self.finalstack['name'] = {'value': 'Step %s: Finalise the stack'  % (idx+1), 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None} 
                if self.modestack == 'normal':
                        self.finalstack['keepgeotiff'] = {'value': True, 
                                        'description': 'Keep only the goetiff files', 
                                        'format': 'bool',
                                        'valuelist': None}  
                else:
                        self.finalstack['keepgeotiff'] = {'value': False, 
                                        'description': 'Keep only the goetiff files', 
                                        'format': 'bool',
                                        'valuelist': None} 
                self.finalstack['croppingforStaMPS'] = {'value': True,
                                        'description': 'Enable the cropping for StaMPS', 
                                        'format': 'bool',
                                        'valuelist': None} 
                self.finalstack['parentdirStaMPS'] = {'value': self.workdirectory, 
                                        'description': 'Path of the parent dictory of StaMPS', 
                                        'format': 'str',
                                        'valuelist': None} 
                self.finalstack['parentdirMintPy'] = {'value': self.workdirectory,
                                        'description': 'Path of the parent dictory of MintPy', 
                                        'format': 'str',
                                        'valuelist': None} 
                self.finalstack['done'] = {'value': False, 
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
                        logger.info('Creation of a EZ-InSAR InSAR stack processing')

                # Initilisation by the user
                jobproctools.check(self,verbose=False,mode='low')
                
        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def print(self):
                """Print the attributes of an ``ezinsar.ifgstack`` using ISCE-2

                The method prints the attributes of an ``ezinsar.ifgstack``.   

                Returns:
                        ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
                
                """

                attrs = vars(self)
                print(', '.join("%s: %s" % item for item in attrs.items()))

                return self

        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def check(self,**kwargs):
                """Check the attributes of an ``ezinsar.ifgstack`` using ISCE-2

                The method checks the attributes of an ``ezinsar.ifgstack``.   

                Returns:
                        ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
                
                """

                self = jobproctools.check(self,**kwargs)

                return self
        
        ################################################################################
        ## Run the interferometric processing
        ################################################################################
        def run(self,**kwargs):
                """Run an ``ezinsar.ifgstack`` using ISCE-2

                The method runs an ``ezinsar.ifgstack``.   

                Returns:
                        ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
                
                """

                self = jobrun.run(self,**kwargs)

                return self
                
                
        