#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage the class for MintPy processing using MintPy

The module allows to create the EZ-InSAR processing class using MintPy. 
    
    (From `ezinsar` package)

Changelog:
        * 1.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import os
from typing import Optional, Union
import logging 

from ezinsar import constants
from ezinsar import usermessage
from ezinsar.eicomponents.roimodule import roitools
from ezinsar.eicomponents.processor.miaplpymodule import miaplpytools
from ezinsar.eicomponents.jobmodule import jobrun, jobproctools
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Class to manage the EZ-InSAR job
##      (part of EZ-InSAR)
################################################################################
class ps:

        '''Attributes:
                title (str): Name/Definition of the user [Default: `None`]
                workdirectory (str): Work directory of the coregistration processin. [Default: `None`]
                pathmintpyconfig (str): Path of the MintPy configuration file. [Default: `None`]
                polarisation (str):  Polarisation. [Default: ``VV``]
                roi (str): Polygon of the Region of Interest. [Default: `None`]
                satellite (str): Satellite name. [Default: ``S1``]
                satmode (str): Satellite mode. [Default: ``SM``]
                relorbit (int): Relative orbit number. [Default: `None`]
                satpass (str): Satellite direction. [Default: `None`]
                email (dict): Dictionary of the emal parameters
                processor (str): Processor. [Default: ``mintpy``] 
                ifgprocessor (str): Interferometric processor. [Default: ``gamma``] 
                mode (str): Mode of the time series processing. [Default: ``sbas``] 
                mlazi (int): Multilook factor in azimuth
                mlran (int): Multilook factor in range 
                computer (dict): EZ-InSAR parameter dictionary

                load_data (dict): EZ-InSAR parameter dictionary
                modify_network (dict): EZ-InSAR parameter dictionary
                reference_point (dict): EZ-InSAR parameter dictionary
                quick_overview (dict): EZ-InSAR parameter dictionary
                correct_unwrap_error (dict): EZ-InSAR parameter dictionary
                invert_network (dict): EZ-InSAR parameter dictionary
                correct_LOD (dict): EZ-InSAR parameter dictionary
                correct_SET (dict): EZ-InSAR parameter dictionary
                correct_troposphere (dict): EZ-InSAR parameter dictionary
                deramp (dict): EZ-InSAR parameter dictionary
                correct_topography (dict): EZ-InSAR parameter dictionary
                residual_RMS (dict): EZ-InSAR parameter dictionary
                reference_date (dict): EZ-InSAR parameter dictionary
                velocity (dict): EZ-InSAR parameter dictionary
                geocode (dict): EZ-InSAR parameter dictionary
                google_earth (dict): EZ-InSAR parameter dictionary
                hdfeos5 (dict): EZ-InSAR parameter dictionary
                extract_res (dict): EZ-InSAR parameter dictionary
                plotoptions (dict): EZ-InSAR parameter dictionary
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
                pathmiaplpyconfig: Optional[Union[str, None]] = None,
                polarisation: Optional[Union[str]] = 'VV',
                roi: Optional[Union[any, None]] = None,
                satellite: Optional[str] = 'S1',
                satmode: Optional[str] = 'IW',

                relorbit: Optional[Union[int, None]] = None,
                satpass: Optional[Union[str, None]] = None,

                email: Optional[Union[dict, None]] = None,
                processor: Optional[str] = 'miaplpy',
                ifgprocessor: Optional[str] = 'isce2',
                mode: Optional[str] = 'ps',

                mlazi: Optional[Union[int]] = 1,
                mlran: Optional[Union[int]] = 1,

                verbose: Optional[bool] = True,
                log: Optional[Union[str, None]] = None,
                gui: Optional[bool] = False,

                ):
                """Initilisation of the job for EZ-InSAR

                Args:
                        job (``ezinsar.job``): EZ-InSAR interferometric job
                        title (str): Name/Definition of the user [Default: `None`]
                        workdirectory (str): Work directory of the coregistration processin. [Default: `None`]
                        pathmintpyconfig (str): Path of the MintPy configuration file. [Default: `None`]
                        polarisation (str):  Polarisation. [Default: ``VV``]
                        roi (str): Polygon of the Region of Interest. [Default: `None`]
                        satellite (str): Satellite name. [Default: ``S1``]
                        satmode (str): Satellite mode. [Default: ``SM``]
                        relorbit (int): Relative orbit number. [Default: `None`]
                        satpass (str): Satellite direction. [Default: `None`]
                        email (dict): Dictionary of the emal parameters
                        processor (str): Processor. [Default: ``mintpy``] 
                        ifgprocessor (str): Interferometric processor. [Default: ``gamma``] 
                        mode (str): Mode of the time series processing. [Default: ``sbas``] 
                        mlazi (int): Multilook factor in azimuth
                        mlran (int): Multilook factor in range 
                        verbose (bool): Verbose mode. [Default: `True`]
                        log (str): Log file
                        gui (bool): GUI mode (not used). [Default: `False`]

                """                 

                # User information
                if not job == None: 
                        
                        if not 'coregistration' in str(type(job)):
                                raise ValueError(usermessage.errormsg(__name__,'tsmiaplpy'.__name__,__file__,__copyright__,
                                        'The job input must be a coregistration job.',None))

                        self.title = 'MiaplPy processing for %s' % (job.title) 
                        self.polarisation = polarisation
                        self.satellite = job.satellite
                        self.satmode = job.satmode
                        self.relorbit = job.relorbit
                        self.satpass = job.satpass
                        self.roi = job.roi
                        self.workdirectory = os.path.dirname(job.workdirectory)+os.sep+'stack_miaplpy_'+self.polarisation.lower()
                        self.mlazi = job.mlazi
                        self.mlran = job.mlran

                        tmpprocessor = job.processor

                else: 
                        self.title = title
                        self.workdirectory = workdirectory
                        self.satellite = satellite
                        self.satmode = satmode
                        self.relorbit = relorbit
                        self.satpass = satpass
                        self.polarisation = polarisation
                        if not roi == None: 
                                self.roi = roitools.importroi(self, roi)
                        else: 
                                self.roi = None

                        self.mlazi = mlazi
                        self.mlran = mlran

                        tmpprocessor = ifgprocessor

                if tmpprocessor == 'isce2': 
                        tmpprocessor = 'isce' 

                self.ifgprocessor = ifgprocessor
                
                self.processor = processor
                self.mode = mode
                self.pathmiaplpyconfig = None

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

                self.processor = 'miaplpy'

                # For the Step 0: Computing resource configuration
                self.computer = dict()
                self.computer['name'] = {'value': 'Step 0: Computing resource configuration (for MintPy)', 
                                        'description': 'Dummy step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.computer['compute.maxMemory'] = {'value': 'auto', 
                                        'description': 'Float (given in str) for the max memory allocated in GB', 
                                        'format': 'str',
                                        'valuelist': None}
                self.computer['compute.cluster'] = {'value': 'auto', 
                                        'description': 'Type of the cluster (auto for none)', 
                                        'format': 'list',
                                        'valuelist': ['local','slurm','pbs','lsf','none','auto']}
                self.computer['compute.numWorker'] = {'value': 'auto', 
                                        'description': 'Number of workers', 
                                        'format': 'str',
                                        'valuelist': None}
                self.computer['compute.config'] = {'value': 'auto', 
                                        'description': 'Configuration of the computer', 
                                        'format': 'list',
                                        'valuelist': ['slurm','pbs','lsf','none','auto']}
                self.computer['multiprocessing.numProcessor'] = {'value': 'auto', 
                                        'description': 'None', 
                                        'format': 'str',
                                        'valuelist': None}
                self.computer['done'] = {'value': True, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
                
                # For the Step 1: load
                self.load_data = dict()
                self.load_data['name'] = {'value': 'Step 1: load', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.processor'] = {'value': tmpprocessor, 
                                        'description': 'Interferometric processing', 
                                        'format': 'list',
                                        'valuelist': ['isce','gamma','auto']}
                self.load_data['load.updateMode'] = {'value': 'auto', 
                                        'description': 'Update the TS stack (auto for no)', 
                                        'format': 'list',
                                        'valuelist': ['yes','no','auto']}
                self.load_data['load.compression'] = {'value': 'auto', 
                                        'description': 'Mode of compression (auto for no)', 
                                        'format': 'list',
                                        'valuelist': ['gzip','lzf','no','auto']}
                self.load_data['load.autoPath'] = {'value': 'auto', 
                                        'description': 'Automatic detection of pathes (auto for isce)', 
                                        'format': 'list',
                                        'valuelist': ['yes','no','auto']}
                self.load_data['load.slcFile'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.startDate'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.endDate'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}                
                self.load_data['load.metaFile'] = {'value': 'auto', 
                                        'description': 'For ISCE only. Metadata files', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.baselineDir'] = {'value': 'auto', 
                                        'description': 'For ISCE only. Baseline directory', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.demFile'] = {'value': 'auto', 
                                        'description': 'DEM file', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.lookupYFile'] = {'value': 'auto', 
                                        'description': 'X lookup table file', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.lookupXFile'] = {'value': 'auto', 
                                        'description': 'Y lookup table file', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.incAngleFile'] = {'value': 'auto', 
                                        'description': 'Incidence angle file', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.azAngleFile'] = {'value': 'auto', 
                                        'description': 'Azimuth angle file', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.shadowMaskFile'] = {'value': 'auto', 
                                        'description': 'Shadow mask file', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.waterMaskFile'] = {'value': 'auto', 
                                        'description': 'Water mask file', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.bperpFile'] = {'value': 'auto', 
                                        'description': 'Perpendicular files', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.unwFile'] = {'value': 'auto', 
                                        'description': 'Unwrapped interferograms', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.corFile'] = {'value': 'auto', 
                                        'description': 'Coherence files', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.connCompFile'] = {'value': 'auto', 
                                        'description': 'Connectivity maps', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.intFile'] = {'value': 'auto', 
                                        'description': 'Wrapped interferogams', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['load.ionoFile'] = {'value': 'auto', 
                                        'description': 'Ionospheric delays', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['subset.yx'] = {'value': 'auto', 
                                        'description': 'Subset in XY (auto for no)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['subset.lalo'] = {'value': 'auto', 
                                        'description': 'Subset in lat/lon (auto for no)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_data['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
            
                # For the Step 2: phase_linking
                self.phase_linking = dict()
                self.phase_linking['name'] = {'value': 'Step 2: phase_linking', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.phase_linking['inversion.patchSize'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.phase_linking['inversion.ministackSize'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.phase_linking['inversion.rangeWindow'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.phase_linking['inversion.azimuthWindow'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.phase_linking['inversion.shpTest'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'list',
                                        'valuelist': ['ks','ad','ttest','auto']}
                self.phase_linking['inversion.phaseLinkingMethod'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'list',
                                        'valuelist': ['EVD','EMI','PTA','sequential_EVD','sequential_EMI','sequential_PTA','StBAS','auto']}
                self.phase_linking['inversion.sbw_connNum'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.phase_linking['inversion.PsNumShp'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.phase_linking['inversion.mask'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.phase_linking['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
                
                # For the Step 3: concatenate_patches
                self.concatenate_patches = dict()
                self.concatenate_patches['name'] = {'value': 'Step 3: concatenate_patches', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.concatenate_patches['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
                
                # For the Step 4: generate_ifgram
                self.generate_ifgram = dict()
                self.generate_ifgram['name'] = {'value': 'Step 4: generate_ifgram', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.generate_ifgram['interferograms.networkType'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'list',
                                        'valuelist': ['mini_stacks', 'single_reference', 'sequential', 'delaunay', 'auto']}
                self.generate_ifgram['interferograms.list'] = {'value': 'auto',
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.generate_ifgram['interferograms.referenceDate'] = {'value': 'auto',
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.generate_ifgram['interferograms.filterStrength'] = {'value': 'auto',
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.generate_ifgram['interferograms.ministackRefMonth'] = {'value': 'auto',
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.generate_ifgram['interferograms.connNum'] = {'value': 'auto',
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.generate_ifgram['interferograms.delaunayBaselineRatio'] = {'value': 'auto',
                                        'description': 'to do', 
                                        'format': 'list',
                                        'valuelist': ['1','4','9','auto']}
                self.generate_ifgram['interferograms.delaunayTempThresh'] = {'value': 'auto',
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.generate_ifgram['interferograms.delaunayPerpThresh'] = {'value': 'auto',
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.generate_ifgram['interferograms.oneYear'] = {'value': 'auto',
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.generate_ifgram['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}

                # For the Step 5: unwrap_ifgram
                self.unwrap_ifgram = dict()
                self.unwrap_ifgram['name'] = {'value': 'Step 5: unwrap_ifgram', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.unwrap_ifgram['unwrap.twostage'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'list',
                                        'valuelist': ['yes','no','auto']}
                self.unwrap_ifgram['unwrap.removeFilter'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'list',
                                        'valuelist': ['yes','no','auto']}
                self.unwrap_ifgram['unwrap.snaphu.maxDiscontinuity'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.unwrap_ifgram['unwrap.snaphu.initMethod'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'list',
                                        'valuelist': ['MCF', 'MST', 'auto']}
                self.unwrap_ifgram['unwrap.snaphu.tileNumPixels'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.unwrap_ifgram['unwrap.mask'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.unwrap_ifgram['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}

                # For the Step 6: load_ifgram
                self.load_ifgram = dict()
                self.load_ifgram['name'] = {'value': 'Step 6: load_ifgram', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.load_ifgram['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}

                # For the Step 7: ifgram_correction
                self.ifgram_correction = dict()
                self.ifgram_correction['name'] = {'value': 'Step 7: ifgram_correction', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.ifgram_correction['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}

                # For the Step 8: invert_network
                self.invert_network = dict()
                self.invert_network['name'] = {'value': 'Step 8: invert_network', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.invert_network['timeseries.tempCohType'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.invert_network['timeseries.minTempCoh'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.invert_network['timeseries.waterMask'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.invert_network['timeseries.shadowMask'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.invert_network['timeseries.residualNorm'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.invert_network['timeseries.L1smoothingFactor'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.invert_network['timeseries.L2weightFunc'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.invert_network['timeseries.minNormVelocity'] = {'value': 'auto', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.invert_network['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}

                # For the Step 9: timeseries_correction
                self.timeseries_correction = dict()
                self.timeseries_correction['name'] = {'value': 'Step 9: timeseries_correction', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.timeseries_correction['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
                
                # For the Step 0: MintPy parameters
                self.mintpyparameter = dict()
                self.mintpyparameter['name'] = {'value': 'Dummy step for MintPy parameter', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}

                self.mintpyparameter['compute.maxMemory'] = {'value': 'auto', 
                                                'description': 'Float (given in str) for the max memory allocated in GB', 
                                                'format': 'str',
                                                'valuelist': None}
                self.mintpyparameter['compute.cluster'] = {'value': 'auto', 
                                        'description': 'Type of the cluster (auto for none)', 
                                        'format': 'list',
                                        'valuelist': ['local','slurm','pbs','lsf','none','auto']}
                self.mintpyparameter['compute.numWorker'] = {'value': 'auto', 
                                        'description': 'Number of workers', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['compute.config'] = {'value': 'auto', 
                                        'description': 'Configuration of the computer', 
                                        'format': 'list',
                                        'valuelist': ['slurm','pbs','lsf','none','auto']}
                self.mintpyparameter['reference.yx'] = {'value': 'auto', 
                                        'description': 'Reference point in YX (can be auto)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['reference.lalo'] = {'value': 'auto', 
                                        'description': 'str', 
                                        'format': 'Reference point in lat/lon (can be auto)',
                                        'valuelist': None}
                self.mintpyparameter['reference.maskFile'] = {'value': 'auto', 
                                        'description': 'Mask file for the reference point (auto for maskConnComp.h5)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['reference.coherenceFile'] = {'value': 'auto', 
                                        'description': 'Coherence map for the reference point (auto for avgSpatialCoh.h5)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['reference.minCoherence'] = {'value': 'auto', 
                                        'description': 'Min coherence for the reference point (auto for 0.85)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['unwrapError.method'] = {'value': 'auto', 
                                        'description': 'Method for error estimation (auto for no)', 
                                        'format': 'list',
                                        'valuelist': ['bridging','phase_closure','bridging+phase_closure','no','auto']}
                self.mintpyparameter['unwrapError.waterMaskFile'] = {'value': 'auto', 
                                        'description': 'Water mask file (auto for waterMask.h5 or no)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['unwrapError.numSample'] = {'value': 'auto', 
                                        'description': 'Number of samples (auto for 100)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['unwrapError.ramp'] = {'value': 'auto', 
                                        'description': 'Ramp estimation method (auto for no)', 
                                        'format': 'list',
                                        'valuelist': ['linear','quadratic','no','auto']}
                self.mintpyparameter['unwrapError.bridgePtsRadius'] = {'value': 'auto', 
                                        'description': 'Point-radius bridging (auto for 50)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['solidEarthTides'] = {'value': 'auto', 
                                        'description': 'SET correction (auto for no)', 
                                        'format': 'list',
                                        'valuelist': ['yes','no','auto']}
                self.mintpyparameter['troposphericDelay.method'] = {'value': 'height_correlation', 
                                        'description': 'Tropo. delay method (auto for pyaps)', 
                                        'format': 'list',
                                        'valuelist': ['pyaps','height_correlation','gacos','no','auto']}
                self.mintpyparameter['troposphericDelay.weatherModel'] = {'value': 'auto', 
                                        'description': 'Used weather mode (auto for ERA5)', 
                                        'format': 'list',
                                        'valuelist': ['ERA5','MERRA','NARR','auto']}
                self.mintpyparameter['troposphericDelay.weatherDir'] = {'value': 'auto', 
                                        'description': 'Weather data directory (auto for WEATHER_DIR or "./")', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['troposphericDelay.polyOrder'] = {'value': 'auto', 
                                        'description': 'Poly. order (auto for 1)', 
                                        'format': 'list',
                                        'valuelist': ['1','2','3','auto']}
                self.mintpyparameter['troposphericDelay.looks'] = {'value': 'auto', 
                                        'description': 'Number of looks (auto for 8)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['troposphericDelay.minCorrelation'] = {'value': 'auto', 
                                        'description': 'Min. correlation (auto for 0)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['troposphericDelay.gacosDir'] = {'value': 'auto', 
                                        'description': 'GACOS directory (auto for ./GACOS)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['deramp'] = {'value': 'auto', 
                                        'description': 'Deramping (auto for no)', 
                                        'format': 'list',
                                        'valuelist': ['no','linear','quadratic','auto']}
                self.mintpyparameter['deramp.maskFile'] = {'value': 'auto', 
                                        'description': 'Mask file (auto for maskTempCoh.h5)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['topographicResidual'] = {'value': 'auto', 
                                        'description': 'Topographic correction (auto for yes)', 
                                        'format': 'list',
                                        'valuelist': ['no','yes','auto']}
                self.mintpyparameter['topographicResidual.polyOrder'] = {'value': 'auto', 
                                        'description': 'Poly order (auto for 2)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['topographicResidual.phaseVelocity'] = {'value': 'auto', 
                                        'description': 'Phase-based minimisation (auto for no)', 
                                        'format': 'list',
                                        'valuelist': ['yes','no','auto']}
                self.mintpyparameter['topographicResidual.stepFuncDate'] = {'value': 'auto', 
                                        'description': 'Date for the step function (can be YYYYMMDD, YYYYMMDDTHHMM or no) (auto for no)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['topographicResidual.excludeDate'] = {'value': 'auto', 
                                        'description': 'Date(s) exluced (YYYYMMDD, .txt file or no) (auto for exclude_date.txt)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['topographicResidual.pixelwiseGeometry'] = {'value': 'auto', 
                                        'description': 'Use pixe-geometry information (auto for yes)', 
                                        'format': 'list',
                                        'valuelist': ['no','yes','auto']}
                self.mintpyparameter['residualRMS.maskFile'] = {'value': 'auto', 
                                        'description': 'Mask file (auto for maskTempCoh.h5)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['residualRMS.deramp'] = {'value': 'auto', 
                                        'description': 'Deramping (auto for quadratic)', 
                                        'format': 'list',
                                        'valuelist': ['linear','quadratic','no','auto']}
                self.mintpyparameter['residualRMS.cutoff'] = {'value': 'auto', 
                                        'description': 'Cutoff value (auto for 3)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['reference.date'] = {'value': 'auto', 
                                        'description': 'Reference date (YYYYMMDD, reference_date.txt) (auto for reference_date.txt)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['velocity.excludeDate'] = {'value': 'auto', 
                                        'description': 'Exluced dates (exclude_date.txt, YYYYMMDD,YYYYMMDD or no) (auto for exclude_date.txt)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['velocity.startDate'] = {'value': 'auto', 
                                        'description': 'Start date in YYYYMMDD format (auto for no)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['velocity.endDate'] = {'value': 'auto', 
                                        'description': 'Start date in YYYYMMDD format (auto for no)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['velocity.bootstrap'] = {'value': 'auto', 
                                        'description': 'Velocity bootstrapping (auto for no)', 
                                        'format': 'list',
                                        'valuelist': ['yes','no','auto']}
                self.mintpyparameter['velocity.bootstrapCount'] = {'value': 'auto', 
                                        'description': 'Number of iterations (auto for 400)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['geocode'] = {'value': 'auto', 
                                        'description': 'Geocoding of the results (auto for yes)', 
                                        'format': 'list',
                                        'valuelist': ['no','yes','auto']}
                self.mintpyparameter['geocode.SNWE'] = {'value': 'auto', 
                                        'description': 'Region of Interest for geocoding (auto for none)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['geocode.laloStep'] = {'value': 'auto', 
                                        'description': 'Lat/lon step for geocoding (auto for none)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['geocode.interpMethod'] = {'value': 'auto', 
                                        'description': 'Interpolation method (auto for nearest)', 
                                        'format': 'list',
                                        'valuelist': ['nearest','auto']}
                self.mintpyparameter['geocode.fillValue'] = {'value': 'auto', 
                                        'description': 'Fill value (auto for np.nan)', 
                                        'format': 'str',
                                        'valuelist': None}
                self.mintpyparameter['save.kmz'] = {'value': 'auto', 
                                        'description': 'Save the results in kmz (auto for yes)', 
                                        'format': 'list',
                                        'valuelist': ['yes','no','auto']}
                self.mintpyparameter['save.hdfEos5'] = {'value': 'auto', 
                                        'description': 'Save the time series in HDF-EOS5 format (auto for no)', 
                                        'format': 'list',
                                        'valuelist': ['yes','no','auto']}
                self.mintpyparameter['save.hdfEos5.update'] = {'value': 'auto', 
                                        'description': 'Update the HDF-EOS5 file (auto for no)', 
                                        'format': 'list',
                                        'valuelist': ['yes','no','auto']}
                self.mintpyparameter['save.hdfEos5.subset'] = {'value': 'auto', 
                                        'description': 'Subset the HDF-EOS5 file (auto for no)', 
                                        'format': 'list',
                                        'valuelist': ['yes','no','auto']}
                self.mintpyparameter['plot'] = {'value': 'auto', 
                                        'description': 'Plotting file in .pic directory (auto for yes)', 
                                        'format': 'list',
                                        'valuelist': ['yes','no','auto']}
                self.mintpyparameter['done'] = {'value': True, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}

                # For the Step 10: extract_res
                self.extract_res = dict()
                self.extract_res['name'] = {'value': 'Step 10: extract_res', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.extract_res['ecraseprevious'] = {'value': True, 
                                        'description': 'Ecrase the previous file', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.extract_res['done'] = {'value': False, 
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
                        logger.info('Creation of a EZ-InSAR MiaplPy processing')

                ## Update based on the coregistration job 
                if not job == None:

                        ## For ISCE2
                        if job.processor == 'isce2':
                                self.pathmiaplpyconfig = self.workdirectory+os.sep+'miaplpy'+os.sep+'TSmiaplpyprocessing.cfg' 
                                self.load_data['load.processor']['value'] = 'isce'
                                self.load_data['load.autoPath']['value'] = 'yes'
                                self.load_data['load.slcFile']['value'] = job.pathstack + '/SLC/*/*.slc.full'
                                self.load_data['load.metaFile']['value'] = job.workdirectory + '/reference/IW*.xml'
                                self.load_data['load.baselineDir']['value'] = job.workdirectory + '/baselines'

                                self.load_data['load.demFile']['value'] = job.pathstack + '/geom_reference/hgt.rdr.full'
                                self.load_data['load.lookupYFile']['value'] = job.pathstack + '/geom_reference/lat.rdr.full'
                                self.load_data['load.lookupXFile']['value'] = job.pathstack + '/geom_reference/lon.rdr.full'
                                self.load_data['load.incAngleFile']['value'] = job.pathstack + '/geom_reference/los.rdr.full'
                                self.load_data['load.azAngleFile']['value'] = job.pathstack + '/geom_reference/los.rdr.full'
                                self.load_data['load.shadowMaskFile']['value'] = job.pathstack + '/geom_reference/shadowMask.rdr.full'
                                self.load_data['load.waterMaskFile']['value'] = 'None'

                                self.load_data['load.unwFile']['value'] = self.workdirectory+'/inverted/interferograms_single_reference/*/*fine*.unw'
                                self.load_data['load.corFile']['value'] = self.workdirectory+'/inverted/interferograms_single_reference/*/*fine*.cor'
                                self.load_data['load.connCompFile']['value'] = self.workdirectory+'/inverted/interferograms_single_reference/*/*unw*.conncomp'

                                from shapely.wkt import loads
                                import numpy as np
                                roitmp = loads(job.roi)
                                self.load_data['subset.lalo']['value'] = '%s:%s:%s:%s' % (
                                        np.min(roitmp.exterior.xy[1]),
                                        np.max(roitmp.exterior.xy[1]),
                                        np.min(roitmp.exterior.xy[0]),
                                        np.max(roitmp.exterior.xy[0]),
                                )

                                if not job.refdate == None:
                                        self.mintpyparameter['reference.date']['value'] = job.refdate
                                else:
                                        self.mintpyparameter['reference.date']['value'] = 'auto'
                
                # Initilisation by the user
                jobproctools.check(self,verbose=False,mode='low')
                
        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def print(self):
                """Print the tsprocessing-processing attributes of the EZ-InSAR class

                Returns:
                        ``ezinsar.job``: Return the ``ezinsar.job`` used
                """

                attrs = vars(self)
                print(', '.join("%s: %s" % item for item in attrs.items()))

                return self

        ################################################################################
        ## Method to check the attributes
        ################################################################################
        def check(self,**kwargs):
                """Check and display the tsprocessing-processing attributes of the EZ-InSAR class

                Args:
                        ``kwargs``: Arbitrary keyword arguments.

                Returns:
                        ``ezinsar.job``: Return the ``ezinsar.job`` used
                """

                self = jobproctools.check(self,**kwargs)

                return self

        ################################################################################
        ## Method to write the MiaplPy configuration file 
        ################################################################################
        def writecfg(self,**kwargs):
                """Write the MiaplPy configuration file from an EZ-InSAR job
                
                Args:
                        ``kwargs``: Arbitrary keyword arguments.
                        
                Returns:
                        ``ezinsar.job``: Return the ``ezinsar.job`` used
                """

                self = miaplpytools.writecfg(self,**kwargs)

                return self

        # ################################################################################
        # ## Method to write the MintPy configuration file 
        # ################################################################################
        # def readcfg(self,**kwargs):
        #         """Read the MintPy configuration file and update an EZ-InSAR job
                
        #         Args:
        #                 ``kwargs``: Arbitrary keyword arguments.
                        
        #         Returns:
        #                 ``ezinsar.job``: Return the ``ezinsar.job`` used
        #         """

        #         self = mintpytools.readcfg(self,**kwargs)

        #         return self
        
        ################################################################################
        ## Run the processing
        ################################################################################
        def run(self,**kwargs):
                """Run the coregsitration using MiaplPy processor

                Args:
                        ``kwargs``: Arbitrary keyword arguments.

                Returns:
                        ``ezinsar.job``: Return the ``ezinsar.job`` used
                """

                self = jobrun.run(self,**kwargs)

                return self
                
                
