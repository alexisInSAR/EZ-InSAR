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
import psutil
from typing import Optional, Union
import logging 
import glob 

from ezinsar import constants
from ezinsar import usermessage
from ezinsar.eicomponents.roimodule import roitools
from ezinsar.eicomponents.processor.mintpymodule import mintpytools
from ezinsar.eicomponents.jobmodule import jobrun, jobproctools
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Class to manage the EZ-InSAR job
##      (part of EZ-InSAR)
################################################################################
class sbas:

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
                pathmintpyconfig: Optional[Union[str, None]] = None,
                polarisation: Optional[Union[str]] = 'VV',
                roi: Optional[Union[any, None]] = None,
                satellite: Optional[str] = 'S1',
                satmode: Optional[str] = 'IW',

                relorbit: Optional[Union[int, None]] = None,
                satpass: Optional[Union[str, None]] = None,

                email: Optional[Union[dict, None]] = None,
                processor: Optional[str] = 'mintpy',
                ifgprocessor: Optional[str] = 'gamma',
                mode: Optional[str] = 'sbas',

                mlazi: Optional[Union[int]] = 1,
                mlran: Optional[Union[int]] = 1,

                computer: Optional[Union[any, None]] = None,
                load_data: Optional[Union[any, None]] = None,
                modify_network: Optional[Union[any, None]] = None,
                reference_point: Optional[Union[any, None]] = None,
                quick_overview: Optional[Union[any, None]] = None,
                correct_unwrap_error: Optional[Union[any, None]] = None,
                invert_network: Optional[Union[any, None]] = None,
                correct_LOD: Optional[Union[any, None]] = None,
                correct_SET: Optional[Union[any, None]] = None,
                correct_troposphere: Optional[Union[any, None]] = None,
                deramp: Optional[Union[any, None]] = None,
                correct_topography: Optional[Union[any, None]] = None,
                residual_RMS: Optional[Union[any, None]] = None,
                reference_date: Optional[Union[any, None]] = None,
                velocity: Optional[Union[any, None]] = None,
                geocode: Optional[Union[any, None]] = None,
                google_earth: Optional[Union[any, None]] = None,
                hdfeos5: Optional[Union[any, None]] = None,
                extract_res: Optional[Union[any, None]] = None,
                plotoptions: Optional[Union[any, None]] = None,
        
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

                """                 

                # User information
                if not job == None: 
                        
                        if not 'ifgstack' in str(type(job)):
                                raise ValueError(usermessage.errormsg(__name__,'tsmintpy'.__name__,__file__,__copyright__,
                                        'The job input must be a ifgstack job.',None))

                        self.title = 'MintPy processing for %s' % (job.title) 
                        self.polarisation = polarisation
                        self.satellite = job.satellite
                        self.satmode = job.satmode
                        self.relorbit = job.relorbit
                        self.satpass = job.satpass
                        self.roi = job.roi
                        self.workdirectory = job.workdirectory+os.sep+'stack_mintpy_'+self.polarisation.lower()
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
                self.pathmintpyconfig = None

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

                self.processor = 'mintpy'

                # For the Step 0: Computing resource configuration
                if computer == None:
                        self.computer = dict()
                        self.computer['name'] = {'value': 'Step 0: Computing resource configuration', 
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
                        self.computer['done'] = {'value': True, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.computer = computer

                # For the Step 1: load_data
                if load_data == None:
                        self.load_data = dict()
                        self.load_data['name'] = {'value': 'Step 1: load_data', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.load_data['load.processor'] = {'value': tmpprocessor, 
                                                'description': 'Interferometric processing', 
                                                'format': 'list',
                                                'valuelist': ['isce','aria','hyp3','gmtsar','snap','gamma','roipac','auto']}
                        self.load_data['load.autoPath'] = {'value': 'auto', 
                                                'description': 'Automatic detection of pathes (auto for isce)', 
                                                'format': 'list',
                                                'valuelist': ['yes','no','auto']}
                        self.load_data['load.updateMode'] = {'value': 'auto', 
                                                'description': 'Update the TS stack (auto for no)', 
                                                'format': 'list',
                                                'valuelist': ['yes','no','auto']}
                        self.load_data['load.compression'] = {'value': 'auto', 
                                                'description': 'Mode of compression (auto for no)', 
                                                'format': 'list',
                                                'valuelist': ['gzip','lzf','no','auto']}
                        self.load_data['load.metaFile'] = {'value': 'auto', 
                                                'description': 'For ISCE only. Metadata files', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.load_data['load.baselineDir'] = {'value': 'auto', 
                                                'description': 'For ISCE only. Baseline directory', 
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
                        self.load_data['load.magFile'] = {'value': 'auto', 
                                                'description': 'Interferometric magnitudes', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.load_data['load.azOffFile'] = {'value': 'auto', 
                                                'description': 'Azimuth offset files', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.load_data['load.rgOffFile'] = {'value': 'auto', 
                                                'description': 'Range offset files', 
                                                'format': 'todo',
                                                'valuelist': None}
                        self.load_data['load.azOffStdFile'] = {'value': 'auto', 
                                                'description': 'Azimuth offset varianc', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.load_data['load.rgOffStdFile'] = {'value': 'auto', 
                                                'description': 'Range offset varianc', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.load_data['load.offSnrFile'] = {'value': 'auto', 
                                                'description': 'Signal-noise files', 
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
                        self.load_data['load.ystep'] = {'value': 'auto', 
                                                'description': 'Multilooking factor in Y (auto for 1)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.load_data['load.xstep'] = {'value': 'auto', 
                                                'description': 'Multilooking factor in X (auto for 1)', 
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
                else:
                        self.load_data = load_data

                # For the Step 2: modify_network
                if modify_network == None:
                        self.modify_network = dict()
                        self.modify_network['name'] = {'value': 'Step 2: modify_network', 
                                                'description': 'to do', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.modify_network['network.tempBaseMax'] = {'value': 'auto', 
                                                'description': 'Max temporal baseline in days (auto for no)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.modify_network['network.perpBaseMax'] = {'value': 'auto', 
                                                'description': 'Max Bperp in metre (auto for no)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.modify_network['network.connNumMax'] = {'value': 'auto', 
                                                'description': 'Max connectivity (auto for no)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.modify_network['network.startDate'] = {'value': 'auto', 
                                                'description': 'Start data in YYYYMMDD (auto for no)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.modify_network['network.endDate'] = {'value': 'auto', 
                                                'description': 'End date in YYYYMMDD (auto for no)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.modify_network['network.excludeDate'] = {'value': 'auto', 
                                                'description': 'Excluded dates [YYYYMMDD,YYYYMMDD] (auto for no)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.modify_network['network.excludeIfgIndex'] = {'value': 'auto', 
                                                'description': 'Excluded interferogram indexes (auto for no)', 
                                                'format': 'todo',
                                                'valuelist': None}
                        self.modify_network['network.referenceFile'] = {'value': 'auto', 
                                                'description': 'Reference files (auto for no)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.modify_network['network.coherenceBased'] = {'value': 'auto', 
                                                'description': 'Coherence-based ifg exclusion (auto for no)', 
                                                'format': 'list',
                                                'valuelist': ['yes','no','auto']}
                        self.modify_network['network.minCoherence'] = {'value': 'auto', 
                                                'description': 'Coherence threshold (auto for 0.7)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.modify_network['network.areaRatioBased'] = {'value': 'auto', 
                                                'description': 'Area-ratio-based ifg exclusions (auto for no)', 
                                                'format': 'list',
                                                'valuelist': ['yes','no','auto']}
                        self.modify_network['network.minAreaRatio'] = {'value': 'auto', 
                                                'description': 'Min. area ratio (auto for 0.75)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.modify_network['network.keepMinSpanTree'] = {'value': 'auto', 
                                                'description': 'Min-span-tree-network-based ifg exclusion (only for yes)', 
                                                'format': 'list',
                                                'valuelist': ['yes','no','auto']}
                        self.modify_network['network.maskFile'] = {'value': 'auto', 
                                                'description': 'Mask file (auto for waterMask.h5 or no)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.modify_network['network.aoiYX'] = {'value': 'auto', 
                                                'description': 'Region of Interest (in XY) for coherence computing (auto for no)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.modify_network['network.aoiLALO'] = {'value': 'auto', 
                                                'description': 'Region of Interest (in lat/lon) for coherence computing (auto for no)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.modify_network['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.modify_network = modify_network

                # For the Step 3: reference_point
                if reference_point == None:
                        self.reference_point = dict()
                        self.reference_point['name'] = {'value': 'Step 3: reference_point', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.reference_point['reference.yx'] = {'value': 'auto', 
                                                'description': 'Reference point in YX (can be auto)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.reference_point['reference.lalo'] = {'value': 'auto', 
                                                'description': 'str', 
                                                'format': 'Reference point in lat/lon (can be auto)',
                                                'valuelist': None}
                        self.reference_point['reference.maskFile'] = {'value': 'auto', 
                                                'description': 'Mask file for the reference point (auto for maskConnComp.h5)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.reference_point['reference.coherenceFile'] = {'value': 'auto', 
                                                'description': 'Coherence map for the reference point (auto for avgSpatialCoh.h5)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.reference_point['reference.minCoherence'] = {'value': 'auto', 
                                                'description': 'Min coherence for the reference point (auto for 0.85)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.reference_point['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.reference_point = reference_point

                # For the Step 4: quick_overview
                if quick_overview == None:
                        self.quick_overview = dict()
                        self.quick_overview['name'] = {'value': 'Step 4: quick_overview', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.quick_overview['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else: 
                        self.quick_overview = quick_overview

                # For the Step 5: correct_unwrap_error
                if correct_unwrap_error == None:
                        self.correct_unwrap_error = dict()
                        self.correct_unwrap_error['name'] = {'value': 'Step 5: correct_unwrap_error', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_unwrap_error['unwrapError.method'] = {'value': 'auto', 
                                                'description': 'Method for error estimation (auto for no)', 
                                                'format': 'list',
                                                'valuelist': ['bridging','phase_closure','bridging+phase_closure','no','auto']}
                        self.correct_unwrap_error['unwrapError.waterMaskFile'] = {'value': 'auto', 
                                                'description': 'Water mask file (auto for waterMask.h5 or no)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_unwrap_error['unwrapError.connCompMinArea'] = {'value': 'auto', 
                                                'description': 'Threshold for smaller region (auto for 2.5e3)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_unwrap_error['unwrapError.numSample'] = {'value': 'auto', 
                                                'description': 'Number of samples (auto for 100)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_unwrap_error['unwrapError.ramp'] = {'value': 'auto', 
                                                'description': 'Ramp estimation method (auto for no)', 
                                                'format': 'list',
                                                'valuelist': ['linear','quadratic','no','auto']}
                        self.correct_unwrap_error['unwrapError.bridgePtsRadius'] = {'value': 'auto', 
                                                'description': 'Point-radius bridging (auto for 50)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_unwrap_error['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else: 
                        self.correct_unwrap_error = correct_unwrap_error

                # For the Step 6: invert_network
                if invert_network == None:
                        self.invert_network = dict()
                        self.invert_network['name'] = {'value': 'Step 6: invert_network', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.invert_network['networkInversion.weightFunc'] = {'value': 'auto', 
                                                'description': 'Weighting function (auto for var)', 
                                                'format': 'list',
                                                'valuelist': ['var','fim','coh','no','auto']}
                        self.invert_network['networkInversion.waterMaskFile'] = {'value': 'auto', 
                                                'description': 'Watermak file (auto for waterMask.h5 or no)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.invert_network['networkInversion.minNormVelocity'] = {'value': 'auto', 
                                                'description': 'Min-norm velocity estimation (auto for yes)', 
                                                'format': 'list',
                                                'valuelist': ['auto','yes','no']}
                        self.invert_network['networkInversion.residualNorm'] = {'value': 'auto', 
                                                'description': 'Norm minimisation (auto for L2)', 
                                                'format': 'list',
                                                'valuelist': ['L2','auto']}
                        self.invert_network['networkInversion.maskDataset'] = {'value': 'auto', 
                                                'description': 'Masking mode (auto for no)', 
                                                'format': 'list',
                                                'valuelist': ['coherence','connectComponent','rangeOffsetStd','azimuthOffsetStd','no','auto']}
                        self.invert_network['networkInversion.maskThreshold'] = {'value': 'auto', 
                                                'description': 'Masking threshold (auto for 0.4)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.invert_network['networkInversion.minRedundancy'] = {'value': 'auto', 
                                                'description': 'Min redundancy (auto for 1.0)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.invert_network['networkInversion.minTempCoh'] = {'value': 'auto', 
                                                'description': 'Min temporal coherence (auto for 0.7)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.invert_network['networkInversion.minNumPixel'] = {'value': 'auto', 
                                                'description': '????? (auto for 1000)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.invert_network['networkInversion.shadowMask'] = {'value': 'auto', 
                                                'description': 'Shadow mask file (auto for yes)', 
                                                'format': 'list',
                                                'valuelist': ['yes','no','auto']}
                        self.invert_network['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else: 
                        self.invert_network = invert_network

                # For the Step 7: correct_LOD
                if correct_LOD == None:
                        self.correct_LOD = dict()
                        self.correct_LOD['name'] = {'value': 'Step 7: correct_LOD', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_LOD['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else: 
                        self.correct_LOD = correct_LOD

                # For the Step 8: correct_SET
                if correct_SET == None:
                        self.correct_SET = dict()
                        self.correct_SET['name'] = {'value': 'Step 8: correct_SET', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_SET['solidEarthTides'] = {'value': 'auto', 
                                                'description': 'SET correction (auto for no)', 
                                                'format': 'list',
                                                'valuelist': ['yes','no','auto']}
                        self.correct_SET['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else: 
                        self.correct_SET = correct_SET

                # For the Step 9: correct_troposphere
                if correct_troposphere == None:
                        self.correct_troposphere = dict()
                        self.correct_troposphere['name'] = {'value': 'Step 9: correct_troposphere', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_troposphere['troposphericDelay.method'] = {'value': 'no', 
                                                'description': 'Tropo. delay method (auto for pyaps)', 
                                                'format': 'list',
                                                'valuelist': ['pyaps','height_correlation','gacos','no','auto']}
                        self.correct_troposphere['troposphericDelay.weatherModel'] = {'value': 'auto', 
                                                'description': 'Used weather mode (auto for ERA5)', 
                                                'format': 'list',
                                                'valuelist': ['ERA5','MERRA','NARR','auto']}
                        self.correct_troposphere['troposphericDelay.weatherDir'] = {'value': 'auto', 
                                                'description': 'Weather data directory (auto for WEATHER_DIR or "./")', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_troposphere['troposphericDelay.polyOrder'] = {'value': 'auto', 
                                                'description': 'Poly. order (auto for 1)', 
                                                'format': 'list',
                                                'valuelist': ['1','2','3','auto']}
                        self.correct_troposphere['troposphericDelay.looks'] = {'value': 'auto', 
                                                'description': 'Number of looks (auto for 8)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_troposphere['troposphericDelay.minCorrelation'] = {'value': 'auto', 
                                                'description': 'Min. correlation (auto for 0)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_troposphere['troposphericDelay.gacosDir'] = {'value': 'auto', 
                                                'description': 'GACOS directory (auto for ./GACOS)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_troposphere['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else: 
                        self.correct_troposphere = correct_troposphere

                # For the Step 10: deramp
                if deramp == None:
                        self.deramp = dict()
                        self.deramp['name'] = {'value': 'Step 10: deramp', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.deramp['deramp'] = {'value': 'auto', 
                                                'description': 'Deramping (auto for no)', 
                                                'format': 'list',
                                                'valuelist': ['no','linear','quadratic','auto']}
                        self.deramp['deramp.maskFile'] = {'value': 'auto', 
                                                'description': 'Mask file (auto for maskTempCoh.h5)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.deramp['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else: 
                        self.deramp = deramp

                # For the Step 11: correct_topography
                if correct_topography == None:
                        self.correct_topography = dict()
                        self.correct_topography['name'] = {'value': 'Step 11: correct_topography', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_topography['topographicResidual'] = {'value': 'auto', 
                                                'description': 'Topographic correction (auto for yes)', 
                                                'format': 'list',
                                                'valuelist': ['no','yes','auto']}
                        self.correct_topography['topographicResidual.polyOrder'] = {'value': 'auto', 
                                                'description': 'Poly order (auto for 2)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_topography['topographicResidual.phaseVelocity'] = {'value': 'auto', 
                                                'description': 'Phase-based minimisation (auto for no)', 
                                                'format': 'list',
                                                'valuelist': ['yes','no','auto']}
                        self.correct_topography['topographicResidual.stepFuncDate'] = {'value': 'auto', 
                                                'description': 'Date for the step function (can be YYYYMMDD, YYYYMMDDTHHMM or no) (auto for no)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_topography['topographicResidual.excludeDate'] = {'value': 'auto', 
                                                'description': 'Date(s) exluced (YYYYMMDD, .txt file or no) (auto for exclude_date.txt)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.correct_topography['topographicResidual.pixelwiseGeometry'] = {'value': 'auto', 
                                                'description': 'Use pixe-geometry information (auto for yes)', 
                                                'format': 'list',
                                                'valuelist': ['no','yes','auto']}
                        self.correct_topography['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else: 
                        self.correct_topography = correct_topography

                # For the Step 12: residual_RMS
                if residual_RMS == None:
                        self.residual_RMS = dict()
                        self.residual_RMS['name'] = {'value': 'Step 12: residual_RMS', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.residual_RMS['residualRMS.maskFile'] = {'value': 'auto', 
                                                'description': 'Mask file (auto for maskTempCoh.h5)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.residual_RMS['residualRMS.deramp'] = {'value': 'auto', 
                                                'description': 'Deramping (auto for quadratic)', 
                                                'format': 'list',
                                                'valuelist': ['linear','quadratic','no','auto']}
                        self.residual_RMS['residualRMS.cutoff'] = {'value': 'auto', 
                                                'description': 'Cutoff value (auto for 3)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.residual_RMS['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else: 
                        self.residual_RMS = residual_RMS

                # For the Step 13: reference_date
                if reference_date == None:
                        self.reference_date = dict()
                        self.reference_date['name'] = {'value': 'Step 13: reference_date', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.reference_date['reference.date'] = {'value': 'auto', 
                                                'description': 'Reference date (YYYYMMDD, reference_date.txt) (auto for reference_date.txt)', 
                                                'format': 'str',
                                                'valuelist': None}
                        if not job == None: 
                                self.reference_date['reference.date']['value'] = job.refdate
   
                        self.reference_date['done'] = {'value': False, 
                                                'description': 'Processing completeds', 
                                                'format': 'bool',
                                                'valuelist': None}
                else: 
                        self.reference_date = reference_date

                # For the Step 14: velocity
                if velocity == None:
                        self.velocity = dict()
                        self.velocity['name'] = {'value': 'Step 14: velocity', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.velocity['velocity.excludeDate'] = {'value': 'auto', 
                                                'description': 'Exluced dates (exclude_date.txt, YYYYMMDD,YYYYMMDD or no) (auto for exclude_date.txt)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.velocity['velocity.startDate'] = {'value': 'auto', 
                                                'description': 'Start date in YYYYMMDD format (auto for no)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.velocity['velocity.endDate'] = {'value': 'auto', 
                                                'description': 'Start date in YYYYMMDD format (auto for no)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.velocity['velocity.bootstrap'] = {'value': 'auto', 
                                                'description': 'Velocity bootstrapping (auto for no)', 
                                                'format': 'list',
                                                'valuelist': ['yes','no','auto']}
                        self.velocity['velocity.bootstrapCount'] = {'value': 'auto', 
                                                'description': 'Number of iterations (auto for 400)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.velocity['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else: 
                        self.velocity = velocity

                # For the Step 15: geocode
                if geocode == None:
                        self.geocode = dict()
                        self.geocode['name'] = {'value': 'Step 15: geocode', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.geocode['geocode'] = {'value': 'auto', 
                                                'description': 'Geocoding of the results (auto for yes)', 
                                                'format': 'list',
                                                'valuelist': ['no','yes','auto']}
                        self.geocode['geocode.SNWE'] = {'value': 'auto', 
                                                'description': 'Region of Interest for geocoding (auto for none)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.geocode['geocode.laloStep'] = {'value': 'auto', 
                                                'description': 'Lat/lon step for geocoding (auto for none)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.geocode['geocode.interpMethod'] = {'value': 'auto', 
                                                'description': 'Interpolation method (auto for nearest)', 
                                                'format': 'list',
                                                'valuelist': ['nearest','auto']}
                        self.geocode['geocode.fillValue'] = {'value': 'auto', 
                                                'description': 'Fill value (auto for np.nan)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.geocode['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else: 
                        self.geocode = geocode

                # For the Step 16: google_earth
                if google_earth == None:
                        self.google_earth = dict()
                        self.google_earth['name'] = {'value': 'Step 16: google_earth', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.google_earth['save.kmz'] = {'value': 'auto', 
                                                'description': 'Save the results in kmz (auto for yes)', 
                                                'format': 'list',
                                                'valuelist': ['yes','no','auto']}
                        self.google_earth['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else: 
                        self.google_earth = google_earth

                # For the Step 17: hdfeos5
                if hdfeos5 == None:
                        self.hdfeos5 = dict()
                        self.hdfeos5['name'] = {'value': 'Step 17: hdfeos5', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.hdfeos5['save.hdfEos5'] = {'value': 'auto', 
                                                'description': 'Save the time series in HDF-EOS5 format (auto for no)', 
                                                'format': 'list',
                                                'valuelist': ['yes','no','auto']}
                        self.hdfeos5['save.hdfEos5.update'] = {'value': 'auto', 
                                                'description': 'Update the HDF-EOS5 file (auto for no)', 
                                                'format': 'list',
                                                'valuelist': ['yes','no','auto']}
                        self.hdfeos5['save.hdfEos5.subset'] = {'value': 'auto', 
                                                'description': 'Subset the HDF-EOS5 file (auto for no)', 
                                                'format': 'list',
                                                'valuelist': ['yes','no','auto']}
                        self.hdfeos5['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                # For the Step 18: extract_res
                if extract_res == None:
                        self.extract_res = dict()
                        self.extract_res['name'] = {'value': 'Step 18: extract_res', 
                                                'description': 'to do', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.extract_res['ecraseprevious'] = {'value': True, 
                                                'description': 'Ecrase the previous file', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.extract_res['applymask'] = {'value': True, 
                                                'description': 'Apply the mask file', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.extract_res['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}

                else: 
                        self.hdfeos5 = hdfeos5

                # For plot options
                if plotoptions == None:
                        self.plotoptions = dict()
                        self.plotoptions['name'] = {'value': 'Plotting options', 
                                                'description': 'Dummy processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.plotoptions['plot'] = {'value': 'auto', 
                                                'description': 'Plotting file in .pic directory (auto for yes)', 
                                                'format': 'list',
                                                'valuelist': ['yes','no','auto']}
                        self.plotoptions['plot.dpi'] = {'value': 'auto', 
                                                'description': 'DPI of figures (auto for 150)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.plotoptions['plot.maxMemory'] = {'value': 'auto', 
                                                'description': 'Max RAM for plotting (view.py scripts) in GB (auto for 4)', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.plotoptions['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else: 
                        self.plotoptions = plotoptions

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
                        logger.info('Creation of a EZ-InSAR MintPy processing')
                
                ## Detection of the config file 
                if not job == None: 
                        listfile = glob.glob(job.workdirectory+os.sep+'stack_mintpy_'+self.polarisation.lower()+os.sep+'mintpy'+os.sep+'*.cfg')
                        if listfile: 
                                usermessage.ezprint('Detection of the MintPy configuration file: %s' % (listfile[0]),self.log,self.verbose)
                                usermessage.ezprint('\tImport the parameters into the EZ-InSAR job',self.log,self.verbose)
                                self = mintpytools.readcfg(self, file = listfile[0],verbose=False)
                                self.pathmintpyconfig = listfile[0]
                                usermessage.ezprint('\tdone',self.log,self.verbose)

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
                        ``kwargs``: Arbitrary keyword arguments. See `slctools.displaySLClist` for more information. 

                Returns:
                        ``ezinsar.job``: Return the ``ezinsar.job`` used
                """

                self = jobproctools.check(self,**kwargs)

                return self

        ################################################################################
        ## Method to write the MintPy configuration file 
        ################################################################################
        def writecfg(self,**kwargs):
                """Write the MintPy configuration file from an EZ-InSAR job
                
                Args:
                        ``kwargs``: Arbitrary keyword arguments.
                        
                Returns:
                        ``ezinsar.job``: Return the ``ezinsar.job`` used
                """

                self = mintpytools.writecfg(self,**kwargs)

                return self

        ################################################################################
        ## Method to write the MintPy configuration file 
        ################################################################################
        def readcfg(self,**kwargs):
                """Read the MintPy configuration file and update an EZ-InSAR job
                
                Args:
                        ``kwargs``: Arbitrary keyword arguments.
                        
                Returns:
                        ``ezinsar.job``: Return the ``ezinsar.job`` used
                """

                self = mintpytools.readcfg(self,**kwargs)

                return self
        
        ################################################################################
        ## Run the coregistration
        ################################################################################
        def run(self,**kwargs):
                """Run the coregsitration using MintPy processor

                Args:
                        ``kwargs``: Arbitrary keyword arguments.

                Returns:
                        ``ezinsar.job``: Return the ``ezinsar.job`` used
                """

                self = jobrun.run(self,**kwargs)

                return self
                
                
