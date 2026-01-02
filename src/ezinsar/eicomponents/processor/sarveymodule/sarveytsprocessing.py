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
from ezinsar.eicomponents.processor.sarveymodule import sarveytools
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
                pathsarveyconfig: Optional[Union[str, None]] = None,
                polarisation: Optional[Union[str]] = 'VV',
                roi: Optional[Union[any, None]] = None,
                satellite: Optional[str] = 'S1',
                satmode: Optional[str] = 'IW',

                relorbit: Optional[Union[int, None]] = None,
                satpass: Optional[Union[str, None]] = None,

                email: Optional[Union[dict, None]] = None,
                processor: Optional[str] = 'sarvey',
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
                                raise ValueError(usermessage.errormsg(__name__,'tssarvey'.__name__,__file__,__copyright__,
                                        'The job input must be a coregistration job.',None))

                        self.title = 'SARvey processing for %s' % (job.title) 
                        self.polarisation = polarisation
                        self.satellite = job.satellite
                        self.satmode = job.satmode
                        self.relorbit = job.relorbit
                        self.satpass = job.satpass
                        self.roi = job.roi
                        self.workdirectory = os.path.dirname(job.workdirectory)+os.sep+'stack_sarvey_'+self.polarisation.lower()
                        self.mlazi = 1
                        self.mlran = 1

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

                        self.mlazi = 1
                        self.mlran = 1

                        tmpprocessor = ifgprocessor

                if tmpprocessor == 'isce2': 
                        tmpprocessor = 'isce' 

                self.ifgprocessor = ifgprocessor
                
                self.processor = processor
                self.mode = mode

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

                self.processor = 'sarvey'
                if (not job == None) and (not self.workdirectory == None):
                        self.pathsarveyconfig = self.workdirectory+os.sep+'config.json'
                else:
                        self.pathsarveyconfig = None

                # For the Step 0: Computing resource configuration
                self.computer = dict()
                self.computer['name'] = {'value': 'Step 0: General information for SARvey', 
                                        'description': 'Dummy step', 
                                        'format': 'str',
                                        'valuelist': None}
                if not job == None:
                        a = self.workdirectory
                else:
                        a = '.'
                self.computer['input_path'] = {'value': a+os.sep+'inputs'+os.sep, 
                                        'description': 'To do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.computer['output_path'] = {'value': a+os.sep+'outputs'+os.sep, 
                                        'description': 'To do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.computer['logfile_path'] = {'value': a+os.sep+'logfiles'+os.sep, 
                                        'description': 'To do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.computer['inverted_path'] = {'value': a+os.sep+'inverted'+os.sep, 
                                        'description': 'To do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.computer['num_cores'] = {'value': 4, 
                                        'description': 'To do', 
                                        'format': 'int',
                                        'valuelist': None}
                self.computer['num_patches'] = {'value': 1, 
                                        'description': 'To do', 
                                        'format': 'int',
                                        'valuelist': None}
                self.computer['apply_temporal_unwrapping'] = {'value': True, 
                                        'description': 'To do', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.computer['spatial_unwrapping_method'] = {'value': 'puma', 
                                        'description': 'To do', 
                                        'format': 'list',
                                        'valuelist': ['puma']}
                self.computer['logging_level'] = {'value': 'INFO', 
                                        'description': 'To do', 
                                        'format': 'list',
                                        'valuelist': ['INFO']}
                self.computer['use_phase_linking_results'] = {'value': False,
                                        'description': 'To do', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.computer['num_siblings'] = {'value': 20,
                                        'description': 'To do', 
                                        'format': 'int',
                                        'valuelist': None}
                self.computer['mask_phase_linking_file'] = {'value': 'None',
                                        'description': 'To do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.computer['use_ps'] = {'value': False,
                                        'description': 'To do', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.computer['mask_ps_file'] = {'value': 'maskPS.h5',
                                        'description': 'To do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.computer['done'] = {'value': True, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
                
                # For the Step 0: preparation
                self.preparation = dict()
                self.preparation['name'] = {'value': 'Step 1: preparation', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                
                self.preparation['start_date'] = {'value': 'null', 
                                        'description': 'To do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.preparation['end_date'] = {'value': 'null', 
                                        'description': 'To do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.preparation['ifg_network_type'] = {'value': 'sb', 
                                        'description': 'To do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.preparation['num_ifgs'] = {'value': 3, 
                                        'description': 'To do', 
                                        'format': 'int',
                                        'valuelist': None}
                self.preparation['max_tbase'] = {'value': 100, 
                                        'description': 'To do', 
                                        'format': 'int',
                                        'valuelist': None}
                self.preparation['filter_window_size'] = {'value': 9, 
                                        'description': 'To do', 
                                        'format': 'int',
                                        'valuelist': None}
                self.preparation['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
            
                # For the Step 2: consistency_check
                self.consistency_check = dict()
                self.consistency_check['name'] = {'value': 'Step 2: consistency_check', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.consistency_check['coherence_p1'] = {'value': 0.9, 
                                        'description': 'To do', 
                                        'format': 'float',
                                        'valuelist': None}
                self.consistency_check['grid_size'] = {'value': 200, 
                                        'description': 'To do', 
                                        'format': 'float',
                                        'valuelist': None}
                self.consistency_check['mask_p1_file'] = {'value': 'None', 
                                        'description': 'To do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.consistency_check['num_nearest_neighbours'] = {'value': 30, 
                                        'description': 'To do', 
                                        'format': 'int',
                                        'valuelist': None}
                self.consistency_check['max_arc_length'] = {'value': 'null', 
                                        'description': 'To do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.consistency_check['velocity_bound'] = {'value': 0.1, 
                                        'description': 'To do', 
                                        'format': 'float',
                                        'valuelist': None}
                self.consistency_check['dem_error_bound'] = {'value': 100.0, 
                                        'description': 'To do', 
                                        'format': 'float',
                                        'valuelist': None}
                self.consistency_check['num_optimization_samples'] = {'value': 100, 
                                        'description': 'To do', 
                                        'format': 'int',
                                        'valuelist': None}
                self.consistency_check['arc_unwrapping_coherence'] = {'value': 0.6, 
                                        'description': 'To do', 
                                        'format': 'float',
                                        'valuelist': None}
                self.consistency_check['min_num_arc'] = {'value': 3, 
                                        'description': 'To do', 
                                        'format': 'int',
                                        'valuelist': None}
                self.consistency_check['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}

                # For the Step 3: unwrapping
                self.unwrapping = dict()
                self.unwrapping['name'] = {'value': 'Step 3: unwrapping', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.unwrapping['use_arcs_from_temporal_unwrapping'] = {'value': True, 
                                        'description': 'To do', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.unwrapping['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
                
                # For the Step 4: unwrapping
                self.filtering = dict()
                self.filtering['name'] = {'value': 'Step 4: filtering', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.filtering['coherence_p2'] = {'value': 0.8, 
                                        'description': 'To do', 
                                        'format': 'float',
                                        'valuelist': None}
                self.filtering['apply_aps_filtering'] = {'value': True, 
                                        'description': 'To do', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.filtering['interpolation_method'] = {'value': 'kriging', 
                                        'description': 'To do', 
                                        'format': 'list',
                                        'valuelist': ['kriging']}
                self.filtering['grid_size'] = {'value': 1000, 
                                        'description': 'To do', 
                                        'format': 'int',
                                        'valuelist': None}
                self.filtering['mask_p2_file'] = {'value': 'None', 
                                        'description': 'To do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.filtering['use_moving_points'] = {'value': True, 
                                        'description': 'To do', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.filtering['max_temporal_autocorrelation'] = {'value': 0.3, 
                                        'description': 'To do', 
                                        'format': 'float',
                                        'valuelist': None}
                self.filtering['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}

                # For the Step 5: densification
                self.densification = dict()
                self.densification['name'] = {'value': 'Step 4: filtering', 
                                        'description': 'Name of the processing step', 
                                        'format': 'str',
                                        'valuelist': None}
                self.densification['num_connections_to_p1'] = {'value': 5, 
                                        'description': 'To do', 
                                        'format': 'int',
                                        'valuelist': None}
                self.densification['max_distance_to_p1'] = {'value': 2000, 
                                        'description': 'To do', 
                                        'format': 'int',
                                        'valuelist': None}
                self.densification['velocity_bound'] = {'value': 0.15, 
                                        'description': 'To do', 
                                        'format': 'float',
                                        'valuelist': None}
                self.densification['dem_error_bound'] = {'value': 100.0, 
                                        'description': 'To do', 
                                        'format': 'float',
                                        'valuelist': None}
                self.densification['num_optimization_samples'] = {'value': 100, 
                                        'description': 'To do', 
                                        'format': 'int',
                                        'valuelist': None}
                self.densification['arc_unwrapping_coherence'] = {'value': 0.5, 
                                        'description': 'To do', 
                                        'format': 'float',
                                        'valuelist': None}
                self.densification['done'] = {'value': False, 
                                        'description': 'Processing completed', 
                                        'format': 'bool',
                                        'valuelist': None}
        
                # For the Step 6: extract_res
                self.extract_res = dict()
                self.extract_res['name'] = {'value': 'Step 10: extract_res', 
                                        'description': 'to do', 
                                        'format': 'str',
                                        'valuelist': None}
                self.extract_res['ecraseprevious'] = {'value': True, 
                                        'description': 'Ecrase the previous file', 
                                        'format': 'bool',
                                        'valuelist': None}
                self.extract_res['correct_geo'] = {'value': True, 
                                        'description': 'to do', 
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
                        logger.info('Creation of a EZ-InSAR SARvey processing')

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
        ## Run the processing
        ################################################################################
        def run(self,**kwargs):
                """Run the coregsitration using SARvey processor

                Args:
                        ``kwargs``: Arbitrary keyword arguments.

                Returns:
                        ``ezinsar.job``: Return the ``ezinsar.job`` used
                """

                self = jobrun.run(self,**kwargs)

                return self
                
                
