#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage the class for interferometric processing using Doris

The module allows to create the EZ-InSAR interferogram-stack class using Doris. 
    
    (From `ezinsar` package)

Note: 
        Worflow 1: EZ-InSAR will respect the workflow defined by StaMPS: i.e., computation of the single-master-network interfegrams, then expanding of interferograms by cpxsum. This method is less accurate but allows to respect the outputs of the single-master processing. 

Changelog:
        * 1.0.1: Add the masking based on a masked DEM in DEM geometry, for water bodies, Jun. 2025, Alexis Hrysiewicz
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

################################################################################
## Class to manage the EZ-InSAR job
##      (part of EZ-InSAR)
################################################################################
class ifgstack:
        """Attributes:
                title (str): Name/Definition of the user [Default: `None`]
                workdirectory (str): Work directory of the ifgstack processing. [Default: `None`]
                modestack (str): Mode of the stack: can be ``normal``, ``StaMPS_PS``, ``StaMPS_SBAS``, ``StaMPS_PSSBAS``. [Default: ``normal``]
                modeforce (bool): Forcing mode [Default: `True`]
                pathstack (str): Path of the directory for the coregistred SLCs. [Default: `None`]
                pathDEM (str): Path of the DEM directory. [Default: `None`]
                nameDEM (str): Name of the DEM file. [Default: `None`]
                typeDEM (str): Type of the DEM. [Default: `None`]
                modeDEM (str): Mode of the DEM for cropping. [Default: ``exact``]
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
                computerworkers: Optional[Union[int, None]] = 1, # Number of workers
                computerRAM: Optional[Union[int, None]] = int((psutil.virtual_memory().total*0.1)/1e6),
                processor: Optional[str] = 'doris',
                mlazi (int): Multilook factor in azimuth
                mlran (int): Multilook factor in range   
                importrslc (dict): EZ-InSAR parameter dictionary
                refinerefdate (dict): EZ-InSAR parameter dictionary
                ifgnetwork (dict): EZ-InSAR parameter dictionary
                ifgcompute (dict): EZ-InSAR parameter dictionary
                ifgfilter (dict): EZ-InSAR parameter dictionary
                ifgunwrapping (dict): EZ-InSAR parameter dictionary
                ifggeocoding (dict): EZ-InSAR parameter dictionary
                finalstack (dict): EZ-InSAR parameter dictionary
                verbose (bool): Verbose mode. [Default: `True`]
                log (str): Log file
                gui (bool): GUI mode (not used). [Default: `False`]
        """
        ################################################################################
        ## Initialistion of the class
        ################################################################################
        def __init__(self, 
                job: Optional[Union[any, None]] = None,
                title: Optional[Union[str, None]] = None,
                workdirectory: Optional[Union[str, None]] = None,
                modestack: Optional[str] = 'normal', # Can be normal, StaMPS_PS, StaMPS_SBAS, StaMPS_PSSBAS

                modeforce: Optional[bool] = True,

                pathstack: Optional[Union[str, None]] = None,
                pathDEM: Optional[Union[str, None]] = None, 
                nameDEM: Optional[Union[str, None]] = None,
                typeDEM: Optional[Union[str, None]] = None,
                modeDEM: Optional[Union[str, None]] = 'exact',

                satellite: Optional[str] = 'S1',
                satmode: Optional[str] = 'SM',

                relorbit: Optional[Union[int, None]] = None,
                satpass: Optional[Union[str, None]] = None,

                refdate: Optional[Union[str, None]] = None,
                polarisation: Optional[Union[str, list]] = ['VV'],
                roi: Optional[Union[any, None]] = None,
                modeacq: Optional[str] = 'monostatic',

                email: Optional[Union[dict, None]] = None,
                computercores: Optional[Union[int, None]] = 0, # Number of threads
                computerworkers: Optional[Union[int, None]] = 1, # Number of workers
                computerRAM: Optional[Union[int, None]] = int((psutil.virtual_memory().total*0.1)/1e6),
                processor: Optional[str] = 'doris',

                mlazi: Optional[Union[int, None]] = None,
                mlran: Optional[Union[int, None]] = None,

                importrslc: Optional[Union[any, None]] = None,
                refinerefdate: Optional[Union[any, None]] = None,
                ifgnetwork: Optional[Union[any, None]] = None,
                ifgcompute: Optional[Union[any, None]] = None,
                ifgfilter: Optional[Union[any, None]] = None,
                ifgunwrapping: Optional[Union[any, None]] = None,
                ifggeocoding: Optional[Union[any, None]] = None,
                finalstack: Optional[Union[any, None]] = None,

                verbose: Optional[bool] = True,
                log: Optional[Union[str, None]] = None,
                gui: Optional[bool] = False,

                ):
                
                """Initilisation of the ifgstack job for EZ-InSAR

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
                        modeDEM (str): Mode of the DEM for cropping. [Default: ``exact``]
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
                        computerworkers: Optional[Union[int, None]] = 1, # Number of workers
                        computerRAM: Optional[Union[int, None]] = int((psutil.virtual_memory().total*0.1)/1e6),
                        processor: Optional[str] = 'doris',
                        mlazi (int): Multilook factor in azimuth
                        mlran (int): Multilook factor in range   
                        importrslc (dict): EZ-InSAR parameter dictionary
                        refinerefdate (dict): EZ-InSAR parameter dictionary
                        ifgnetwork (dict): EZ-InSAR parameter dictionary
                        ifgcompute (dict): EZ-InSAR parameter dictionary
                        ifgfilter (dict): EZ-InSAR parameter dictionary
                        ifgunwrapping (dict): EZ-InSAR parameter dictionary
                        ifggeocoding (dict): EZ-InSAR parameter dictionary
                        finalstack (dict): EZ-InSAR parameter dictionary
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
                        self.computercores = job.computercores
                        self.computerworkers = job.computerworkers
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

                        self.computercores = computercores
                        self.computerworkers = computerworkers
                        self.processor = 'doris'

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

                self.workflow = 'single'
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
                self.computerRAM = computerRAM

                # For the Step 1: Import the rslc files
                if importrslc == None:
                        self.importrslc = dict()
                        self.importrslc['name'] = {'value': 'Step 1: Import the rslc files', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.importrslc['excludedate'] = {'value': "''", 
                                                'description': 'Dates will be excluded (YYYYMMDD,YYYYMMDD format)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.importrslc['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None} 
                else:
                        self.importrslc = importrslc

                # For the Step 2: Refine the reference date
                if refinerefdate == None:
                        self.refinerefdate = dict()
                        self.refinerefdate['name'] = {'value': 'Step 2: Refine the reference date', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None} 
                        self.refinerefdate['process'] = {'value': False, 
                                                'description': 'Enable the processing', 
                                                'format': 'bool',
                                                'valuelist': None} 
                        self.refinerefdate['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None} 
                else:
                        self.refinerefdate = refinerefdate

                # For the Step 3: Build the interferogram network
                if ifgnetwork == None:
                        self.ifgnetwork = dict()
                        self.ifgnetwork['name'] = {'value': 'Step 3: Build the interferogram network', 
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

                # For the Step 4: Compute the interferogram images
                if ifgcompute == None:
                        self.ifgcompute = dict()
                        self.ifgcompute['name'] = {'value': 'Step 4: Compute the interferogram images', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        
                        # COARSEORB
                        #NONE

                        # FILTAZI
                        self.ifgcompute['FILTAZI'] = {'value': False, 
                                                'description': 'Enable the azimuth filtering (AF)', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifgcompute['AF_BLOCKSIZE'] = {'value': 4096, 
                                                'description': 'AF blocksize', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgcompute['AF_OVERLAP'] = {'value': 64, 
                                                'description': 'AF overlapping', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgcompute['AF_HAMMING'] = {'value': 0.75, 
                                                'description': 'AF Hamming', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ifgcompute['AF_OUT_FORMAT'] = {'value': 'ci2', 
                                                'description': 'Format of the ouput file', 
                                                'format': 'list',
                                                'valuelist': ['cr4','ci2']}
                        
                        # FILTRANGE
                        self.ifgcompute['FILTRANGE'] = {'value': False, 
                                                'description': 'enable the range filtering (RF)', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifgcompute['RF_METHOD'] = {'value': 'adaptive', 
                                                'description': 'RF method', 
                                                'format': 'list',
                                                'valuelist': ['adaptive','porbits']}
                        self.ifgcompute['RF_FFTLENGTH'] = {'value': '64', 
                                                'description': 'FFT length of the RF', 
                                                'format': 'list',
                                                'valuelist': ['64','512','1024']}
                        self.ifgcompute['RF_OVERLAP'] = {'value': 0, 
                                                'description': 'RF overlapping', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgcompute['RF_HAMMING'] = {'value': 0.75, 
                                                'description': 'RF hamming', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ifgcompute['RF_SLOPE'] = {'value': 0.0,
                                                'description': 'RF slope', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ifgcompute['RF_NLMEAN'] = {'value': 15.0,
                                                'description': 'to do', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ifgcompute['RF_THRESHOLD'] = {'value': 15.0,
                                                'description': 'RF threshold', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ifgcompute['RF_OVERSAMPLE'] = {'value': 2,
                                                'description': 'RF oversampling', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgcompute['RF_WEIGHTCORR'] = {'value': 'OFF',
                                                'description': 'RF weight correlation', 
                                                'format': 'list',
                                                'valuelist': ['ON','OFF']}
                        self.ifgcompute['RF_OUT_FORMAT'] = {'value': 'ci2', 
                                                'description': 'Format of the output file', 
                                                'format': 'list',
                                                'valuelist': ['cr4','ci2']}

                        # INTERFERO
                        #NONE

                        # COMPREFPHA
                        self.ifgcompute['Remove_FE'] = {'value': True,
                                                'description': 'Enable the removal of the flat Earth', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        self.ifgcompute['FE_METHOD'] = {'value': 'porbits',
                                                'description': 'Method for flat-Earth computation', 
                                                'format': 'list',
                                                'valuelist': ['porbits']}
                        self.ifgcompute['FE_DEGREE'] = {'value': 5,
                                                'description': 'Polymomial degree for the interpolation of orbits', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgcompute['FE_NPOINTS'] = {'value': 501,
                                                'description': 'Number of estimated points', 
                                                'format': 'int',
                                                'valuelist': None}

                        # SUBTRREFPHA
                        self.ifgcompute['SRP_METHOD'] = {'value': 'polynomial',
                                                'description': 'Method of the flat-Earth removal', 
                                                'format': 'list',
                                                'valuelist': ['polynomial','exact']}
                        # COMPREFDEM
                        self.ifgcompute['Remove_TOPO'] = {'value': True,
                                                'description': 'Enable the removal of the topo. phase', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # SUBTRREFDEM 
                        self.ifgcompute['SRD_OFFSET_1'] = {'value': 0,
                                                'description': 'Additional offset 1 between the interfogram and the DEM (radarcoded)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgcompute['SRD_OFFSET_2'] = {'value': 0,
                                                'description': 'Additional offset 2 between the interfogram and the DEM (radarcoded)',
                                                'format': 'int',
                                                'valuelist': None}
                        
                        # COHERENCE
                        self.ifgcompute['Coherence'] = {'value': True,
                                                'description': 'Enable the computation of coherence', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifgcompute['COH_METHOD'] = {'value': 'include_refdem',
                                                'description': 'Method of the coherence computation', 
                                                'format': 'list',
                                                'valuelist': ['include_refdem','refphase_only']}
                        self.ifgcompute['COH_WINSIZE_1'] = {'value': 3,
                                                'description': 'Kernel size 1 for coherence computation', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgcompute['COH_WINSIZE_2'] = {'value': 3,
                                                'description': 'Kernel size 2 for coherence computation', 
                                                'format': 'int',
                                                'valuelist': None}

                        self.ifgcompute['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.ifgcompute = ifgcompute

                # For the Step 5: Filter the interferogram images
                if ifgfilter == None:
                        self.ifgfilter = dict()
                        self.ifgfilter['name'] = {'value': 'Step 5: Filter the interferogram images', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.ifgfilter['process'] = {'value': True, 
                                                'description': 'Enable the processing', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        self.ifgfilter['PF_METHOD'] = {'value': 'goldstein', 
                                                'description': 'Method of phase filtrering', 
                                                'format': 'list',
                                                'valuelist': ['goldstein']}#,'spatialconv','spectra']}           
                        self.ifgfilter['PF_ALPHA'] = {'value': 0.125, 
                                                'description': 'For goldstein: alpha value', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ifgfilter['PF_OVERLAP'] = {'value': 16, 
                                                'description': 'For goldstein: overlap value', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgfilter['PF_BLOCKSIZE'] = {'value': 64, 
                                                'description': 'For goldstein: block-size value', 
                                                'format': 'int',
                                                'valuelist': None}
                        
                        self.ifgfilter['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}

                else:
                        self.ifgfilter = ifgfilter

                # For the Step 6: Unwrap the interferograms
                if ifgunwrapping == None:
                        self.ifgunwrapping = dict()
                        self.ifgunwrapping['name'] = {'value': 'Step 6: Unwrap the interferograms', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.ifgunwrapping['process'] = {'value': False, 
                                                'description': 'Enable the processing', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifgunwrapping['usecohweight'] = {'value': True, 
                                                'description': 'Use the coherence for weighting', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifgunwrapping['mode'] = {'value': 'DEFO', 
                                                'description': 'Mode of unwrapping (see snaphu)', 
                                                'format': 'list',
                                                'valuelist': ['DEFO','TOPO','SMOOTH','NOSTATCOSTS']}
                        self.ifgunwrapping['init'] = {'value': 'MST', 
                                                'description': 'Mode of the unwrapping initialisation (see snaphu)', 
                                                'format': 'list',
                                                'valuelist': ['MST','MCF']}
                        self.ifgunwrapping['tiles'] = {'value': False, 
                                                'description': 'Parallelisation of the unwrapping (see snaphu)', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifgunwrapping['NTILEROW'] = {'value': 5, 
                                                'description': 'Number of tile rows (see snaphu)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgunwrapping['NTILECOL'] = {'value': 5, 
                                                'description': 'tNumber of tile columns (see snaphu)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgunwrapping['ROWOVRLP'] = {'value': 250, 
                                                'description': 'Row overlapping (see snaphu)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgunwrapping['COLOVRLP'] = {'value': 250, 
                                                'description': 'Column overlapping (see snaphu)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ifgunwrapping['CONNmode'] = {'value': False, 
                                                'description': 'Computation of the connectivity map', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.ifgunwrapping['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None} 
                else:
                        self.ifgunwrapping = ifgunwrapping

                # For the Step 7: Geocode the results
                if ifggeocoding == None:
                        self.ifggeocoding = dict()
                        self.ifggeocoding['name'] = {'value': 'Step 7: Geocode the results', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.ifggeocoding['process'] = {'value': True, 
                                                'description': 'Enable the processing', 
                                                'format': 'bool',
                                                'valuelist': None} 
                        self.ifggeocoding['maskifg'] = {'value': True, 
                                                'description': 'Mask the interferograms', 
                                                'format': 'bool',
                                                'valuelist': None} 
                        self.ifggeocoding['maskWaterBody'] = {'value': True, 
                                                'description': 'Mask the water bodies based on the masked DEM', 
                                                'format': 'bool',
                                                'valuelist': None} 
                        self.ifggeocoding['overlat'] = {'value': 1.0, 
                                                'description': 'Oversampling for the latitude DEM grid', 
                                                'format': 'float',
                                                'valuelist': None} 
                        self.ifggeocoding['overlon'] = {'value': 1.0, 
                                                'description': 'Oversampling for the longitude DEM grid', 
                                                'format': 'float',
                                                'valuelist': None} 
                        self.ifggeocoding['uchargeotiff'] = {'value': True, 
                                                'description': 'uchar format used', 
                                                'format': 'bool',
                                                'valuelist': None} 
                        self.ifggeocoding['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None} 
                else:
                        self.ifggeocoding = ifggeocoding

                # For the Step 8: Finalise the stack
                if finalstack == None:
                        self.finalstack = dict()
                        self.finalstack['name'] = {'value': 'Step 8: Finalise the stack', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None} 
                        self.finalstack['keepgeotiff'] = {'value': False, 
                                                'description': 'Only keep the geotiff (final results) files', 
                                                'format': 'bool',
                                                'valuelist': None}  
                        self.finalstack['parentdirStaMPS'] = {'value': self.workdirectory, 
                                                'description': 'Path of the parent directory for StaMPS-stack directory', 
                                                'format': 'str',
                                                'valuelist': None} 
                        self.finalstack['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None} 
                else:
                        self.finalstack = finalstack

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
                """Print the attributes of an ``ezinsar.ifgstack`` using Doris

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
                """Check the attributes of an ``ezinsar.ifgstack`` using Doris

                The method checks the attributes of an ``ezinsar.ifgstack``.   

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `slctools.displaySLClist` for more information.

                Returns:
                        ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
                
                """

                self = jobproctools.check(self,**kwargs)

                return self
        
        ################################################################################
        ## Run the interferometric processing
        ################################################################################
        def run(self,**kwargs):
                """Run an ``ezinsar.ifgstack`` using Doris

                The method runs an ``ezinsar.ifgstack``.   

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `slctools.displaySLClist` for more information.

                Returns:
                        ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
                
                """

                self = jobrun.run(self,**kwargs)

                return self
                
                
        