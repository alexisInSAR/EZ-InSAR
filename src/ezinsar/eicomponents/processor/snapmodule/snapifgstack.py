#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage the class for ifgstack processing using SNAP

The module allows to create the EZ-InSAR ifgstack class using SNAP. 
    
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
class ifgstack:

        '''EZ-InSAR ifgstack class for snap 
        
        Attributes:
                title (str): Name/Definition of the user [Default: `None`]
                workdirectory (str): Work directory of the ifgstack processing. [Default: `None`]
                modestack (str): Mode of the stack: can be ``normal``, ``StaMPS_PS``, ``StaMPS_SBAS``, ``StaMPS_PSSBAS``. [Default: ``normal``]
                modeforce (bool): Forcing mode [Default: `True`]
                pathstack (str): Path of the directory for the coregistred SLCs. [Default: `None`]
                pathDEM (str): Path of the DEM directory. [Default: `None`]
                nameDEM (str): Name of the DEM file. [Default: `None`]
                typeDEM (str): Type of the DEM. [Default: `None`]
                satellite (str): Satellite name. [Default: ``S1``]
                satmode (str): Satellite mode. [Default: ``SM``]
                relorbit (int): Relative orbit number. [Default: `None`]
                satpass (str): Satellite direction. [Default: `None`]
                refdate (str): Reference date (YYYYMMDD). [Default: `None`]
                polarisation (list): List of polarisation. [Default: ``['VV']``]
                modeacq (str): type of acquisition. Can be ``monostatic`` or ``bistatic``. [Default: ``monostatic``]
                roi (str): Polygon of the Region of Interest. [Default: `None`]
                email: Optional[Union[dict, None]] = None,
                computercores: Optional[Union[int, None]] = 0, # Number of threads
                processor: Optional[str] = 'snap'
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
                modestack: Optional[str] = 'normal',

                modeforce: Optional[bool] = True,

                pathstack: Optional[Union[str, None]] = None,
                pathDEM: Optional[Union[str, None]] = None, 
                nameDEM: Optional[Union[str, None]] = None,
                typeDEM: Optional[Union[str, None]] = None,

                satellite: Optional[str] = 'S1',
                satmode: Optional[str] = 'IW',

                relorbit: Optional[Union[int, None]] = None,
                satpass: Optional[Union[str, None]] = None,

                refdate: Optional[Union[str, None]] = None,
                polarisation: Optional[Union[str, list]] = ['VV'],
                roi: Optional[Union[any, None]] = None,
                modeacq: Optional[str] = 'monostatic',

                email: Optional[Union[dict, None]] = None,
                computernbthread: Optional[Union[int, None]] = 4, # Number of threads
                processor: Optional[str] = 'snap',

                mlazi: Optional[Union[int, None]] = None,
                mlran: Optional[Union[int, None]] = None,

                ifgnetwork: Optional[Union[any, None]] = None,
                ifgcompute: Optional[Union[any, None]] = None,
                ifgfilter: Optional[Union[any, None]] = None,
                multilook: Optional[Union[any, None]] = None,
                ifgunwrapping: Optional[Union[any, None]] = None,
                ifggeocoding: Optional[Union[any, None]] = None,
                finalstack: Optional[Union[any, None]] = None, 
               
                verbose: Optional[bool] = True,
                log: Optional[Union[str, None]] = None,
                gui: Optional[bool] = False,
                ):
                
                """Initilisation of the job for EZ-InSAR

                Args:
                        job (``ezinsar.job``): EZ-InSAR job
                        title (str): Name/Definition of the user [Default: `None`]
                        workdirectory (str): Work directory of the ifgstack processing. [Default: `None`]
                        modestack (str): Mode of the stack: can be ``normal``, ``StaMPS_PS``, ``StaMPS_SBAS``, ``StaMPS_PSSBAS``. [Default: ``normal``]
                        modeforce (bool): Forcing mode [Default: `True`]
                        pathstack (str): Path of the directory for the coregistred SLCs. [Default: `None`]
                        pathDEM (str): Path of the DEM directory. [Default: `None`]
                        nameDEM (str): Name of the DEM file. [Default: `None`]
                        typeDEM (str): Type of the DEM. [Default: `None`]
                        satellite (str): Satellite name. [Default: ``S1``]
                        satmode (str): Satellite mode. [Default: ``SM``]
                        relorbit (int): Relative orbit number. [Default: `None`]
                        satpass (str): Satellite direction. [Default: `None`]
                        refdate (str): Reference date (YYYYMMDD). [Default: `None`]
                        polarisation (list): List of polarisation. [Default: ``['VV']``]
                        modeacq (str): type of acquisition. Can be ``monostatic`` or ``bistatic``. [Default: ``monostatic``]
                        roi (str): Polygon of the Region of Interest. [Default: `None`]
                        email: Optional[Union[dict, None]] = None,
                        processor: Optional[str] = 'doris',
                        mlazi (int): Multilook factor in azimuth
                        mlran (int): Multilook factor in range   

                        log (str): Log file
                        gui (bool): GUI mode (not used). [Default: `False`]

                Returns: 
                        ``esinsar.job``: EZ-InSAR SNAP coregistration class

                Note: 
                        If a ``job`` input is given, EZ-InSAR will build the class based on its values. 

                """                 

                # User information
                if not job == None: 
                        self.title = 'Interferometric stack for %s' % (job.title) 

                        if os.sep+'coreg' in job.workdirectory: 
                                self.workdirectory = job.workdirectory.replace(os.sep+'coreg',os.sep)+'ifgstack'
                        else:
                                self.workdirectory = job.workdirectory+os.sep+'ifgstack'

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
                        self.processor = job.processor

                        self.mlazi = job.mlazi
                        self.mlran = job.mlran

                else: 
                        self.title = title
                        self.workdirectory = workdirectory

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

                        self.processor = 'snap'

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

                # if self.modestack in ['StaMPS_PS','StaMPS_SBAS','StaMPS_PSSBAS']:
                #         self.mlran = 1
                #         self.mlazi = 1

                if not self.roi == None:
                        self.roi = str(self.roi)        

                self.modeforce = modeforce 

                self.modeacq = modeacq
                self.processor = processor
                self.computernbthread = computernbthread

                # For the Step 1: Build the interferogram network
                if ifgnetwork == None:
                        self.ifgnetwork = dict()
                        self.ifgnetwork['name'] = {'value': 'Step 1: Build the interferogram network', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.ifgnetwork['bperp_min'] = {'value': -1e6, 
                                                'description': 'Min. perpendicular baseline in metres', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ifgnetwork['bperp_max'] = {'value': 1e6, 
                                                'description': 'Max. perpendicular baseline in metres', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ifgnetwork['delta_T_min'] = {'value': -1e6, 
                                                'description': 'Min. temporal baseline in days', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ifgnetwork['delta_T_max'] = {'value': 1e6, 
                                                'description': 'Max. temporal baseline in days', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ifgnetwork['delta_n_max'] = {'value': 1, 
                                                'description': 'Max. connectivity', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgnetwork['delta_difg'] = {'value': 6, 
                                                'description': 'Average temporal sampling for network optimisation (lt)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgnetwork['SBAS_opti'] = {'value': False, 
                                                'description': 'Enable the optimisation of the network', 
                                                'format': 'list',
                                                'valuelist': [False,'delaunay','lt']}
                        self.ifgnetwork['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.ifgnetwork = ifgnetwork

                # For the Step 2: Compute the InSAR products
                if ifgcompute == None:
                        self.ifgcompute = dict()
                        self.ifgcompute['name'] = {'value': 'Step 2: Compute the InSAR products', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.ifgcompute['symlinkstack'] = {'value': False, 
                                                'description': 'Enable the use of symlink for the coreg stack', 
                                                'format': 'bool',
                                                'valuelist': None}

                        self.ifgcompute['demResamplingMethod'] = {'value': 'BILINEAR_INTERPOLATION', 
                                        'description': 'Resampling method', 
                                        'format': 'list',
                                        'valuelist': ['NEAREST_NEIGHBOUR',
                                                      'BILINEAR_INTERPOLATION',
                                                      'CUBIC_CONVOLUTION',
                                                      'BISINC_5_POINT_INTERPOLATION',
                                                      'BISINC_11_POINT_INTERPOLATION',
                                                      'BISINC_21_POINT_INTERPOLATION',
                                                      'BICUBIC_CONVOLUTION']}
                        self.ifgcompute['externalDEMNoDataValue'] = {'value': '0',
                                                'description': 'Value of NaN values', 
                                                'format': 'str',
                                                'valuelist': None}

                        # For normal mode
                        # MultiMasterInSAR
                        self.ifgcompute['includeWavenumber'] = {'value': False, 
                                                'description': 'Enable the storage of the Wavenumber image', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifgcompute['includeIncidenceAngle'] = {'value': False, 
                                                'description': 'Enable the storage of the incidence-angle image', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifgcompute['includeLatLon'] = {'value': True, 
                                                'description': 'Enable the storage of the lat/lon images', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifgcompute['cohWindowAz'] = {'value': 3, 
                                                'description': 'Coherence kernel in azi.', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgcompute['cohWindowRg'] = {'value': 3, 
                                                'description': 'Coherence kernel in ran.', 
                                                'format': 'int',
                                                'valuelist': None}
        
                        self.ifgcompute['createbmp'] = {'value': True, 
                                                'description': 'Enable the creation of .bmp images', 
                                                'format': 'bool',
                                                'valuelist': None}

                        self.ifgcompute['cropping'] = {'value': True, 
                                                'description': 'Enable the cropping for IW data', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For STAMPS
                        self.ifgcompute['subtractTopographicPhase'] = {'value': (not self.satmode == 'IW'), 
                                                'description': 'Subtract topographic phase if StaMPS mode',
                                                'format': 'bool',
                                                'valuelist': None}

                        self.ifgcompute['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                # For the Step 3: Filter the interferograms
                if ifgfilter == None:
                        self.ifgfilter = dict()
                        self.ifgfilter['name'] = {'value': 'Step 3: Filter the interferograms', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.ifgfilter['process'] = {'value': True, 
                                                'description': 'Enable the processing', 
                                                'format': 'bool',
                                                'valuelist': None}
                         # GoldsteinPhaseFiltering
                        self.ifgfilter['alpha'] = {'value': 0.3, 
                                                'description': 'Alpha parameter for Goldstein filtering', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ifgfilter['FFTSizeString'] = {'value': '64', 
                                                'description': 'FFT parameter for Goldstein filtering', 
                                                'format': 'list',
                                                'valuelist': ['32', '64', '128', '256']}
                        self.ifgfilter['windowSizeString'] = {'value': '3', 
                                                'description': 'Window size for Goldstein filtering',  
                                                'format': 'list',
                                                'valuelist': ['3','7','5']}
                        self.ifgfilter['useCoherenceMask'] = {'value': False, 
                                                'description': 'Enable the use of the coherence mask for Goldstein filtering', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifgfilter['coherenceThreshold'] = {'value': 0.2, 
                                                'description': 'Coherence threshold for Goldstein filtering', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ifgfilter['createbmp'] = {'value': True, 
                                                'description': 'Enable the creation of .bmp images', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifgfilter['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                # For the Step 4: Multilooking
                if multilook == None:
                        self.multilook = dict()
                        self.multilook['name'] = {'value': 'Step 4: Multiloolking', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.multilook['process'] = {'value': True, 
                                                'description': 'Enable the processing', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.multilook['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                # For the Step 5: Unwrapping
                if ifgunwrapping == None:
                        self.ifgunwrapping = dict()
                        self.ifgunwrapping['name'] = {'value': 'Step 5: Unwrap the interferograms', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.ifgunwrapping['process'] = {'value': True, 
                                                'description': 'Enable the processing', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifgunwrapping['targetFolder'] = {'value': 'auto', 
                                                'description': 'Target directory', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.ifgunwrapping['statCostMode'] = {'value': 'DEFO', 
                                                'description': 'Mode of the unwrapping', 
                                                'format': 'list',
                                                'valuelist': ['TOPO', 'DEFO', 'SMOOTH', 'NOSTATCOSTS']}
                        self.ifgunwrapping['initMethod'] = {'value': 'MST', 
                                                'description': 'Initialisation method', 
                                                'format': 'list',
                                                'valuelist': ['MST','MCF']}
                        self.ifgunwrapping['numberOfTileRows'] = {'value': 1, 
                                                'description': 'Number of tile (rows)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgunwrapping['numberOfTileCols'] = {'value': 1, 
                                                'description': 'Number of tile (columns)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgunwrapping['numberOfProcessors'] = {'value': self.computernbthread, 
                                                'description': 'Number of used processors', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.ifgunwrapping['rowOverlap'] = {'value': 200, 
                                                'description': 'Overlap in rows', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgunwrapping['colOverlap'] = {'value': 200, 
                                                'description': 'Overlap in columns', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgunwrapping['tileCostThreshold'] = {'value': 500, 
                                                'description': 'tile threshold', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgunwrapping['createbmp'] = {'value': True, 
                                                'description': 'Enable the processing', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifgunwrapping['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}

                # For the Step 6: Geocode the InSAR products
                if ifggeocoding == None:
                        self.ifggeocoding = dict()
                        self.ifggeocoding['name'] = {'value': 'Step 6: Geocode the InSAR products', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.ifggeocoding['process'] = {'value': True, 
                                                'description': 'Enable the processing', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifggeocoding['demResamplingMethod'] = {'value': 'BILINEAR_INTERPOLATION', 
                                                'description': 'Interpolation method', 
                                                'format': 'list',
                                                'valuelist': ['NEAREST_NEIGHBOUR', 'BILINEAR_INTERPOLATION', 'CUBIC_CONVOLUTION', 'BISINC_5_POINT_INTERPOLATION', 'BISINC_11_POINT_INTERPOLATION', 'BISINC_21_POINT_INTERPOLATION', 'BICUBIC_INTERPOLATION', 'DELAUNAY_INTERPOLATION']}
                        self.ifggeocoding['imgResamplingMethod'] = {'value': 'NEAREST_NEIGHBOUR', 
                                                'description': 'Interpolation method', 
                                                'format': 'list',
                                                'valuelist': ['NEAREST_NEIGHBOUR', 'BILINEAR_INTERPOLATION', 'CUBIC_CONVOLUTION', 'BISINC_5_POINT_INTERPOLATION', 'BISINC_11_POINT_INTERPOLATION', 'BISINC_21_POINT_INTERPOLATION', 'BICUBIC_INTERPOLATION', 'DELAUNAY_INTERPOLATION']}
                        self.ifggeocoding['externalDEMApplyEGM'] = {'value': False, 
                                                'description': 'Apply a Ellip. correction', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifggeocoding['Xdem_overfactor'] = {'value': 1, 
                                                'description': 'Oversampling factor of the DEM in X', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifggeocoding['Ydem_overfactor'] = {'value': 1, 
                                                'description': 'Oversampling factor of the DEM in Y', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifggeocoding['externalDEMNoDataValue'] = {'value': '0',
                                                'description': 'Value of NaN values', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.ifggeocoding['nodataValueAtSea'] = {'value': True, 
                                                'description': 'Interpret the non-data as sea', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifggeocoding['saveDEM'] = {'value': False, 
                                                'description': 'Save the DEM', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifggeocoding['saveLatLon'] = {'value': False, 
                                                'description': 'Save the lat/lon image', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifggeocoding['saveIncidenceAngleFromEllipsoid'] = {'value': False, 
                                                'description': 'Save the incidence angle from the ellip.', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifggeocoding['saveLocalIncidenceAngle'] = {'value': False, 
                                                'description': 'Save the local incidence angle', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifggeocoding['saveProjectedLocalIncidenceAngle'] = {'value': False, 
                                                'description': 'Save the projected local incidence angle', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifggeocoding['saveLayoverShadowMask'] = {'value': True, 
                                                'description': 'Save the layover-shadow mask', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifggeocoding['outputComplex'] = {'value': True, 
                                                'description': 'Save the complex value of interferograms', 
                                                'format': 'bool',
                                                'valuelist': None}
                        # pixelSpacingInDegree 0
                        # mapProjection WGS84(DD)
                        # standardGridOriginX 0
                        # standardGridOriginY 0
                        # saveSelectedSourceBand true
                        # applyRadiometricNormalization false
                        # saveSigmaNought false
                        # saveGammaNought false
                        # saveBetaNought false
                        # incidenceAngleForSigma0 Use projected local incidence angle from DEM
                        # incidenceAngleForGamma0 Use projected local incidence angle from DEM
                        # auxFile Latest Auxiliary File
                        # externalAuxFile None
                        self.ifggeocoding['geotiff'] = {'value': True, 
                                                'description': 'Create the geotiff files', 
                                                'format': 'bool',
                                                'valuelist': None} 
                        self.ifggeocoding['maskifg'] = {'value': True, 
                                                'description': 'Mask the interferograms based on the coherence value', 
                                                'format': 'bool',
                                                'valuelist': None} 
                        self.ifggeocoding['coherencethresholdmask'] = {'value': 0.2, 
                                                'description': 'Coherence threshold for masking', 
                                                'format': 'float',
                                                'valuelist': None} 
                        self.ifggeocoding['uchargeotiff'] = {'value': True, 
                                                'description': 'Uchar format used', 
                                                'format': 'bool',
                                                'valuelist': None} 
                        self.ifggeocoding['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}

                        # For the Step 7: Finalise the stack
                        self.finalstack = dict()
                        self.finalstack['name'] = {'value': 'Step 7: Finalise the stack', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.finalstack['keepgeotiff'] = {'value': False, 
                                                'description': 'Keep only the goetiff files', 
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
                        logger.info('Creation of a EZ-InSAR ifgstack processing')

                # Initilisation by the user
                jobproctools.check(self,verbose=False,mode='low')
                
        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def print(self):
                """Print the ifgstack-processing attributes for EZ-InSAR"""

                attrs = vars(self)
                print(', '.join("%s: %s" % item for item in attrs.items()))

                return self

        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def check(self,**kwargs):
                """check and display the ifgstack-processing attributes for EZ-InSAR"""

                self = jobproctools.check(self,**kwargs)

                return self
        
        ################################################################################
        ## Run the coregistration
        ################################################################################
        def run(self,**kwargs):
                """Run the ifgstack using SNAP processor"""
 
                self = jobrun.run(self,**kwargs)

                return self
                
                
        