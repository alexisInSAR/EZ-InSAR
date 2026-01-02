#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage the class for coregistration processing using ISCE-2

The module allows to create the EZ-InSAR coregistration class using ISCE-2. 
    
    (From `ezinsar` package)

Note: 
        Each function can directly used in Python script(s) or/and a Python terminal

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

        '''EZ-InSAR coregistration class for ISCE-2 
        
        Attributes:
                title (str): Name/Definition of the user [Default: `None`]
                workdirectory (str): Work directory of the coregistration processin. [Default: `None`]
                pathSLC (str): Path of the SLC directory. [Default: `None`]
                pathorbit (str): Path of the orbit directory. [Default: `None`]
                pathaux (str): Path of the aux-file directory. [Default: `None`]
                pathDEM (str): Path of the DEM directory. [Default: `None`]
                nameDEM (str): Name of the DEM file. [Default: `None`]
                typeDEM (str): Type of the DEM. [Default: `None`]
                pathstack (str): Path of the directory for the coregistred SLCs. [Default: `None`]
                refdate (str): Reference date (YYYYMMDD). [Default: `None`]
                dates (list): List of dates. Not used. [Default: `None`]
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
                mlazi (int): Multilook factor in azimuth
                mlran (int): Multilook factor in range 
                mlazidisplay (int): Multilook factor in azimuth for displaying
                mlrandisplay (int): Multilook factor in range for displaying
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
                computercores: Optional[Union[int, None]] = 1, # Number of processes in parallel
                processor: Optional[str] = 'isce2',

                modecropping: Optional[Union[any, None]] = 'auto',

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
                        job (``ezinsar.job``): EZ-InSAR job
                        title (str): Name/Definition of the user [Default: `None`]
                        workdirectory (str): Work directory of the coregistration processin. [Default: `None`]
                        pathSLC (str): Path of the SLC directory. [Default: `None`]
                        pathorbit (str): Path of the orbit directory. [Default: `None`]
                        pathaux (str): Path of the aux-file directory. [Default: `None`]
                        pathDEM (str): Path of the DEM directory. [Default: `None`]
                        nameDEM (str): Name of the DEM file. [Default: `None`]
                        typeDEM (str): Type of the DEM. [Default: `None`]
                        pathstack (str): Path of the directory for the coregistred SLCs. [Default: `None`]
                        refdate (str): Reference date (YYYYMMDD). [Default: `None`]
                        dates (list): List of dates. Not used. [Default: `None`]
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
                        mlazi (int): Multilook factor in azimuth
                        mlran (int): Multilook factor in range 
                        mlazidisplay (int): Multilook factor in azimuth for displaying
                        mlrandisplay (int): Multilook factor in range for displaying
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
                        self.pathstack = job.workdirectory+os.sep+'merged'
                        
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
                        self.roi = job.roi
                        self.relorbit = job.relorbit
                        self.satpass = job.satpass

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

                self.computercores = computercores
                self.processor = 'isce2'
                self.modecropping = modecropping

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

                # For the Step 2: Check the Orbit files
                self.checkOrbit = dict()
                self.checkOrbit['name'] = {'value': 'Step 2: Check the orbit files', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.checkOrbit['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
        
                # For the Step 3: Detect the coarse reference date
                self.coarserefdate = dict()
                self.coarserefdate['name'] = {'value': 'Step 3: Detect the coarse reference date', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.coarserefdate['useorbit'] = {'value': False, 
                                        'description': 'Enable the use of precise orbits', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.coarserefdate['useDEM'] = {'value': True, 
                                        'description': 'Enable the use of DEM', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.coarserefdate['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
                
                if self.satmode == 'IW': 
                        # For the Step 4: Unpack the reference image
                        self.unpack_topo_reference = dict()
                        self.unpack_topo_reference['name'] = {'value': 'Step 4: Unpack the reference image', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.unpack_topo_reference['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                
                        # For the Step 5: Unpack the secondary images
                        self.unpack_secondary_slc = dict()
                        self.unpack_secondary_slc['name'] = {'value': 'Step 5: Unpack the secondary images', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.unpack_secondary_slc['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For the Step 6: Compute the average baselines
                        self.average_baseline = dict()
                        self.average_baseline['name'] = {'value': 'Step 6: Compute the average baselines', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.average_baseline['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For the Step 7: Extract the burst overlaps
                        self.extract_burst_overlaps = dict()
                        self.extract_burst_overlaps['name'] = {'value': 'Step 7: Extract the burst overlaps', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.extract_burst_overlaps['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For the Step 8: Convert the overlaps to radar geometry
                        self.overlap_geo2rdr = dict()
                        self.overlap_geo2rdr['name'] = {'value': 'Step 8: Convert the overlaps to radar geometry', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.overlap_geo2rdr['useGPU'] = {'value': False, 
                                                'description': 'Enable the GPU use', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.overlap_geo2rdr['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                
                        # For the Step 9: Overlap resampling 
                        self.overlap_resample = dict()
                        self.overlap_resample['name'] = {'value': 'Step 9: Overlap resampling', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.overlap_resample['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}

                        # For the Step 10: Compute the pair misregistration
                        self.pairs_misreg = dict()
                        self.pairs_misreg['name'] = {'value': 'Step 10: Compute the pair misregistration', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.pairs_misreg['maxconn'] = {'value': 3, 
                                                'description': 'Max. connection of interferometric network', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.pairs_misreg['coh_threshold'] = {'value': 0.85, 
                                                'description': 'Coherence threshold', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.pairs_misreg['plot'] = {'value': False, 
                                                'description': 'Enable the plotting', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.pairs_misreg['snr_threshold'] = {'value': 10.0, 
                                                'description': 'SNR threshold', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.pairs_misreg['done'] = {'value': False, 
                                                'description': 'Name of the processing step', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For the Step 11: Compute the TS misregistration
                        self.timeseries_misreg = dict()
                        self.timeseries_misreg['name'] = {'value': 'Step 11: Compute the TS misregistration', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.timeseries_misreg['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For the Step 12: Compute the full burst to radar geometry
                        self.fullBurst_geo2rdr = dict()
                        self.fullBurst_geo2rdr['name'] = {'value': 'Step 12: Compute the full burst to radar geometry', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.fullBurst_geo2rdr['useGPU'] = {'value': False, 
                                                'description': 'Enable the GPU use', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.fullBurst_geo2rdr['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For the Step 13: Compute the full-burst resampling
                        self.fullBurst_resample = dict()
                        self.fullBurst_resample['name'] = {'value': 'Step 13: Compute the full-burst resampling', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.fullBurst_resample['useGPU'] = {'value': False, 
                                                'description': 'Enable the GPU use', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.fullBurst_resample['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For the Step 14: Extract the stack valid region
                        self.extract_stack_valid_region = dict()
                        self.extract_stack_valid_region['name'] = {'value': 'Step 14: Extract the stack valid region', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.extract_stack_valid_region['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For the Step 15: Merge the images
                        self.merge_reference_secondary_slc = dict()
                        self.merge_reference_secondary_slc['name'] = {'value': 'Step 15: Merge the images', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.merge_reference_secondary_slc['use_virtual_files'] = {'value': False, 
                                                'description': 'Enable the use of virtual files', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.merge_reference_secondary_slc['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}

                        # For the Step 16: Compute the baseline grids
                        self.grid_baseline = dict()
                        self.grid_baseline['name'] = {'value': 'Step 16: Compute the baseline grids', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.grid_baseline['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                else:
                        # For the Step 4: Unpack the SLC files
                        self.unpack_slc = dict()
                        self.unpack_slc['name'] = {'value': 'Step 4: Unpack the SLC files', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.unpack_slc['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For the Step 5: Crop the SLC files
                        self.crop_slc = dict()
                        self.crop_slc['name'] = {'value': 'Step 5: Crop the SLC files', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.crop_slc['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For the Step 6: Initialise the reference image
                        self.reference = dict()
                        self.reference['name'] = {'value': 'Step 6: Initialise the reference image', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.reference['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For the Step 7: Focus split
                        self.focus_split = dict()
                        self.focus_split['name'] = {'value': 'Step 7: Focus split', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.focus_split['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For the Step 8: geo2rdr_coarseResamp
                        self.geo2rdr_coarseResamp = dict()
                        self.geo2rdr_coarseResamp['name'] = {'value': 'Step 8: geo2rdr_coarseResamp', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.geo2rdr_coarseResamp['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For the Step 9: refineSecondaryTiming
                        self.refineSecondaryTiming = dict()
                        self.refineSecondaryTiming['name'] = {'value': 'Step 9: refineSecondaryTiming', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.refineSecondaryTiming['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For the Step 10: invertMisreg
                        self.invertMisreg = dict()
                        self.invertMisreg['name'] = {'value': 'Step 10: invertMisreg', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.invertMisreg['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}

                        # For the Step 11: fineResamp
                        self.fineResamp = dict()
                        self.fineResamp['name'] = {'value': 'Step 11: fineResamp', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.fineResamp['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                        # For the Step 12: Compute the baseline grids
                        self.grid_baseline = dict()
                        self.grid_baseline['name'] = {'value': 'Step 12: Compute the baseline grids', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.grid_baseline['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                # For the Step: Update the stack
                self.updatestack = dict()
                self.updatestack['name'] = {'value': 'Step: Update the stack', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.updatestack['bypass_POD'] = {'value': False, 
                                        'description': 'Enable the bypassing of precise orbits', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.updatestack['done'] = {'value': False, 
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
                """Run the coregsitration using ISCE-2 processor"""
 
                self = jobrun.run(self,**kwargs)

                return self
                
                
        