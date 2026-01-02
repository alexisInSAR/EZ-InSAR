#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage the class for StaMPS processing using StaMPS

The module allows to create the EZ-InSAR processing class using StaMPS. 
    
    (From `ezinsar` package)

Note: 
        Each function can directly used in Python scripts or/and a Python terminal

Changelog:
        * 1.0.1: Bug fixes and the descriptions and formats of each processing parameter have been added, Jan. 2025, Alexis Hrysiewicz 
        * 1.0.0: Initial version, Feb. 2024

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

from ezinsar.eicomponents.processor.stampsmodule import stampstools

from ezinsar.eicomponents.jobmodule import jobrun, jobproctools

################################################################################
## Class for PS processing
################################################################################
class ps:

        ################################################################################
        ## Initialistion of the class
        ################################################################################
        def __init__(self, 
                job: Optional[Union[any, None]] = None,
                title: Optional[Union[str, None]] = None,
                workdirectory: Optional[Union[str, None]] = None,
                pathstampsparms: Optional[Union[str, None]] = None,
                polarisation: Optional[Union[str]] = 'VV',
                roi: Optional[Union[any, None]] = None,
                satellite: Optional[str] = 'S1',
                satmode: Optional[str] = 'IW',
                satpass: Optional[Union[str, None]] = None,
                relorbit: Optional[Union[int, None]] = None,

                refdate: Optional[Union[str, None]] = None,

                email: Optional[Union[dict, None]] = None,
                processor: Optional[str] = 'stamps',
                ifgprocessor: Optional[str] = 'gamma',
                mode: Optional[str] = 'ps',

                communpara: Optional[Union[any, None]] = None,

                mt_prep: Optional[Union[any, None]] = None,

                load_data: Optional[Union[any, None]] = None,

                phase_noise: Optional[Union[any, None]] = None,

                ps_selection: Optional[Union[any, None]] = None,

                ps_weeding: Optional[Union[any, None]] = None,

                phase_correction: Optional[Union[any, None]] = None,

                phase_unwrapping: Optional[Union[any, None]] = None,

                corr_lkerror: Optional[Union[any, None]] = None,

                corr_noise: Optional[Union[any, None]] = None,

                extract_res: Optional[Union[any, None]] = None,
  
                verbose: Optional[bool] = True,
                log: Optional[Union[str, None]] = None,
                gui: Optional[bool] = False,

                ):
                
                """Initilisation of the job for EZ-InSAR
                """                 

                # User information
                if not job == None: 
                        
                        if not 'ifgstack' in str(type(job)):
                                raise ValueError(usermessage.errormsg(__name__,'stampstsprocessing'.__name__,__file__,__copyright__,
                                        'The job input must be a ifgstack job.',None))

                        self.title = 'PS-StaMPS processing for %s' % (job.title) 
                        self.polarisation = polarisation
                        self.satellite = job.satellite
                        self.satmode = job.satmode
                        self.refdate = job.refdate
                        self.relorbit = job.relorbit
                        self.satpass = job.satpass
                        self.roi = job.roi
                        if not self.refdate == None: 
                                self.workdirectory = job.workdirectory+os.sep+'stack_stamps_'+self.polarisation.lower()+os.sep+'INSAR_'+self.refdate
                        else: 
                               self.refdate = None
                        self.ifgprocessor = job.processor

                else: 
                        self.title = title
                        self.workdirectory = workdirectory
                        self.satellite = satellite
                        self.satmode = satmode
                        self.refdate = refdate
                        self.relorbit = relorbit
                        self.satpass = satpass
                        self.polarisation = polarisation
                        if not roi == None: 
                                self.roi = roitools.importroi(self, roi)
                        else: 
                                self.roi = None

                        self.ifgprocessor = ifgprocessor
                
                self.processor = processor
                self.mode = mode

                if pathstampsparms == None and (not self.workdirectory == None):
                        self.pathstampsparms = self.workdirectory+os.sep+'parms.mat'
                else:
                        self.pathstampsparms = pathstampsparms

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

                self.processor = 'stamps'

                # For the Step 0: Commun parameters
                if communpara == None:
                        self.communpara = dict()
                        self.communpara['name'] = {'value': 'Step 0: Commun parameters', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.communpara['insar_processor'] = {'value': self.ifgprocessor, 
                                                'description': 'InSAR processor used', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.communpara['lambda'] = {'value': None, 
                                                'description': 'Wavelength', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.communpara['heading'] = {'value': None, 
                                                'description': 'Heading angle', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.communpara['ref_centre_lonlat'] = {'value': None, 
                                                'description': 'Location of the reference point (lon/lat centre) in list format', 
                                                'format': 'floatmat',
                                                'valuelist': None}            
                        self.communpara['ref_lat'] = {'value': None, 
                                                'description': 'Location of the reference point (min and max latitudes) in list format', 
                                                'format': 'floatmat',
                                                'valuelist': None}                     
                        self.communpara['ref_lon'] = {'value': None, 
                                                'description': 'Location of the reference point (min and max longitudes) in list format', 
                                                'format': 'floatmat',
                                                'valuelist': None}
                        self.communpara['ref_radius'] = {'value': None, 
                                                'description': 'Reference point radius in meters', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['ref_velocity'] = {'value': None, 
                                                'description': 'Velocity of the reference point in mm/yr', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.communpara['small_baseline_flag'] = {'value': 'n', 
                                                'description': 'Flag for the SBAS computation', 
                                                'format': 'list',
                                                'valuelist': ['y','n']}
                        self.communpara['parallelstep'] = {'value': False, 
                                                'description': 'Parallelisation of the StaMPS processing steps', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.communpara['n_cores'] = {'value': int(psutil.cpu_count(logical=True)*0.25), 
                                                'description': 'Number of thread per worker', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['n_jobs'] = {'value': 10, 
                                                'description': 'Number of workers', 
                                                'format': 'int',
                                                'valuelist': None} 
                        self.communpara['lonlat_offset'] = {'value': None, 
                                                'description': 'Offsets for longitude and latitude grids in list format', 
                                                'format': 'floatmat',
                                                'valuelist': None}
                        self.communpara['drop_ifg_index'] = {'value': None, 
                                                'description': 'List of interferograms dropped in list format', 
                                                'format': 'intmat',
                                                'valuelist': None}
                        self.communpara['subtr_tropo'] = {'value': 'n', 
                                                'description': 'Substraction of tropographic delays', 
                                                'format': 'list',
                                                'valuelist': ['y','n']}
                        self.communpara['tropo_method'] = {'value': 'a_l', 
                                                'description': 'Method for subtracting tropographic delays', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.communpara['shade_rel_angle'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'intmat',
                                                'valuelist': None}
                        self.communpara['slc_osf'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['plot_color_scheme'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.communpara['plot_dem_posting'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['plot_pixels_scatterer'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['plot_scatterer_size'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['done'] = {'value': True, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.communpara = communpara

                # For the Step 1: Preparation of PS
                if mt_prep == None:
                        self.mt_prep = dict()
                        self.mt_prep['name'] = {'value': 'Step 1: Preparation of PS', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.mt_prep['da_thresh'] = {'value': 0.4, 
                                                'description': 'Amplitude-dispersion threshold', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.mt_prep['rg_patches'] = {'value': 2, 
                                                'description': 'Number of patches in range', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.mt_prep['az_patches'] = {'value': 2, 
                                                'description': 'Number of patches in azimut',
                                                'format': 'int',
                                                'valuelist': None}
                        self.mt_prep['rg_overlap'] = {'value': 100, 
                                                'description': 'Patch overlap in range', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.mt_prep['az_overlap'] = {'value': 100, 
                                                'description': 'Patch overlap in azimut', 
                                                'format': 'todo',
                                                'valuelist': None}
                        self.mt_prep['maskfile'] = {'value': None, 
                                                'description': 'Mask file', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.mt_prep['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.load_data = load_data

                # For the Step 2: load_data
                if load_data == None:
                        self.load_data = dict()
                        self.load_data['name'] = {'value': 'Step 2: load_data', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.load_data['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.load_data = load_data

                # For the Step 3: Estimate phase noise
                if phase_noise == None:
                        self.phase_noise = dict()
                        self.phase_noise['name'] = {'value': 'Step 3: Estimate phase noise', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.phase_noise['max_topo_err'] = {'value': 5, 
                                                'description': 'Maximum uncorrelated DEM error in metres', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_noise['filter_grid_size'] = {'value': 50, 
                                                'description': 'Pixel size of grid in metre for filtering', 
                                                'format': 'todo',
                                                'valuelist': None}
                        self.phase_noise['filter_weighting'] = {'value': 'P-square', 
                                                'description': 'Method for filter weighting', 
                                                'format': 'list',
                                                'valuelist': ['P-square','SNR']}
                        self.phase_noise['clap_win'] = {'value': 32, 
                                                'description': 'Filter window', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_noise['clap_low_pass_wavelength'] = {'value': 800, 
                                                'description': 'Cut-off spatial wavelength', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_noise['clap_alpha'] = {'value': 1.0, 
                                                'description': 'Filter alpha term', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.phase_noise['clap_beta'] = {'value': 0.3, 
                                                'description': 'Filter beta term', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.phase_noise['gamma_change_convergence'] = {'value': 0.005, 
                                                'description': 'Threshold for convergence', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.phase_noise['gamma_max_iterations'] = {'value': 3, 
                                                'description': 'Maximum number of iterations', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_noise['gamma_stdev_reject'] = {'value': 0.0, 
                                                'description': 'TBD', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.phase_noise['quick_est_gamma_flag'] = {'value': None, 
                                                'description': 'Flag for the quick gamma estimation', 
                                                'format': 'list',
                                                'valuelist': ['None','y','n']}
                        self.phase_noise['select_reest_gamma_flag'] = {'value': None, 
                                                'description': 'Flag for the re-estimation of gamma', 
                                                'format': 'list',
                                                'valuelist': ['None','y','n']}
                        self.phase_noise['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.phase_noise = phase_noise

                # For the Step 4: PS selection
                if ps_selection == None:
                        self.ps_selection = dict()
                        self.ps_selection['name'] = {'value': 'Step 4: PS selection', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.ps_selection['select_method'] = {'value': 'DENSITY', 
                                                'description': 'Selection method', 
                                                'format': 'list',
                                                'valuelist': ['DENSITY','PERCENT']}
                        self.ps_selection['percent_rand'] = {'value': 20, 
                                                'description': 'Threshold for the PERCENT method', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ps_selection['density_rand'] = {'value': 20, 
                                                'description': 'Threshold for the DENSITY method', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ps_selection['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.ps_selection = phase_noise

                # For the Step 5: PS weeding
                if ps_weeding == None:
                        self.ps_weeding = dict()
                        self.ps_weeding['name'] = {'value': 'Step 5: PS weeding', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.ps_weeding['weed_standard_dev'] = {'value': 1.0, 
                                                'description': 'Threshold standard deviation', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ps_weeding['weed_max_noise'] = {'value': float('inf'), 
                                                'description': 'Threshold for the maximum noise allowed for a pixel', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ps_weeding['weed_time_win'] = {'value': 730, 
                                                'description': 'Smoothing window (in days) for estimating phase noise distribution for each pair of neighbouring pixels.', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ps_weeding['weed_neighbours'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'y','n']}
                        self.ps_weeding['weed_zero_elevation'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'y','n']}
                        self.ps_weeding['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.ps_weeding = ps_weeding

                # For the Step 6: Phase correction
                if phase_correction == None:
                        self.phase_correction = dict()
                        self.phase_correction['name'] = {'value': 'Step 6: Phase correction', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.phase_correction['merge_resample_size'] = {'value': 0, 
                                                'description': 'Coarser posting (in m) to resample to. If set to 0 , no resampling is applied.', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_correction['merge_standard_dev'] = {'value': float('inf'), 
                                                'description': 'Threshold standard deviation', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.phase_correction['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.phase_correction = phase_correction
           
                # For the Step 7: Phase unwrapping
                if phase_unwrapping == None:
                        self.phase_unwrapping = dict()
                        self.phase_unwrapping['name'] = {'value': 'Step 7: Phase unwrapping', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_method'] = {'value': '3D', 
                                                'description': 'Unwrapping method', 
                                                'format': 'list',
                                                'valuelist': ['3D','3D_QUICK','2D']}
                        self.phase_unwrapping['unwrap_prefilter_flag'] = {'value': 'y', 
                                                'description': 'Phase filtering before unwrapping to reduce noise.', 
                                                'format': 'list',
                                                'valuelist': ['y','n']}
                        self.phase_unwrapping['unwrap_patch_phase'] = {'value': 'n', 
                                                'description': 'Use the patch phase from Step 3 as prefiltered phase.',
                                                'format': 'list',
                                                'valuelist': ['y','n']}
                        self.phase_unwrapping['unwrap_grid_size'] = {'value': 200, 
                                                'description': 'Resampling grid spacing for unwrapping', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_time_win'] = {'value': 730, 
                                                'description': 'Smoothing window (in days)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_gold_alpha'] = {'value': 0.8, 
                                                'description': 'Alpha term of the Goldstein filter', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_alpha'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_gold_n_win'] = {'value': None, 
                                                'description': 'Window size for Goldstein filter', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_hold_good_values'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'y','n']}
                        self.phase_unwrapping['unwrap_la_error_flag'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'y','n']}
                        self.phase_unwrapping['unwrap_spatial_cost_func_flag'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'y','n']}
                        self.phase_unwrapping['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.phase_unwrapping = phase_unwrapping

                # For the Step 8: Spatially correlated look angle (DEM) error
                if corr_lkerror == None:
                        self.corr_lkerror = dict()
                        self.corr_lkerror['name'] = {'value': 'Step 8: Spatially correlated look angle (DEM) error', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.corr_lkerror['scla_drop_index'] = {'value': None, 
                                                'description': 'List of interferograms dropped', 
                                                'format': 'intmat',
                                                'valuelist': None}
                        self.corr_lkerror['scla_deramp'] = {'value': 'y', 
                                                'description': 'Deramping of interferograms', 
                                                'format': 'list',
                                                'valuelist': ['y','n']}
                        self.corr_lkerror['scla_method'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.corr_lkerror['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.corr_lkerror = corr_lkerror

                # For the Step 9: Filter spatially correlated noise
                if corr_noise == None:
                        self.corr_noise = dict()
                        self.corr_noise['name'] = {'value': 'Step 9: Filter spatially correlated noise', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.corr_noise['scn_deramp_ifg'] = {'value': None, 
                                                'description': 'List of interferograms', 
                                                'format': 'intmat',
                                                'valuelist': None}          
                        self.corr_noise['scn_kriging_flag'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'n','y']}        
                        self.corr_noise['scn_time_win'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}      
                        self.corr_noise['scn_wavelength'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.corr_noise['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.corr_noise = corr_noise

                # For the Step 10: Save the results
                if extract_res == None:
                        self.extract_res = dict()
                        self.extract_res['name'] = {'value': 'Step 10: Save the results', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.extract_res['correction'] = {'value': 'd', 
                                                'description': 'String parameters for InSAR correction', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.extract_res['ecraseprevious'] = {'value': True, 
                                                'description': 'Ecrase the previous results', 
                                                'format': 'bool',
                                                'valuelist': None}           
                        self.extract_res['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.extract_res = extract_res
             
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
                        logger.info('Creation of a EZ-InSAR StaMPS PS processing')

                # Initilisation by the user
                self = jobproctools.check(self,verbose=False)
                
        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def print(self):
                """Print the StaMPS-processing attributes for EZ-InSAR"""

                attrs = vars(self)
                print(', '.join("%s: %s" % item for item in attrs.items()))

                return self

        ################################################################################
        ## Method to check the attributes
        ################################################################################
        def check(self,**kwargs):
                """check and display the StaMPS-processing attributes for EZ-InSAR"""

                self = jobproctools.check(self,**kwargs)

                return self

        ################################################################################
        ## Method to write the StaMPS parameter file 
        ################################################################################
        def writeparameters(self,**kwargs):
                """Write the StaMPS parameter file from an EZ-InSAR job"""

                self = stampstools.writeparameters(self,**kwargs)

                return self

        ################################################################################
        ## Method to write the StaMPS parameter file 
        ################################################################################
        def readparameters(self,**kwargs):
                """Read the StaMPS parameter file and update an EZ-InSAR job"""

                self = stampstools.readparameters(self,**kwargs)

                return self
        
        ################################################################################
        ## Run the processing
        ################################################################################
        def run(self,**kwargs):
                """Run the TS processing using StaMPS processor"""

                self = jobrun.run(self,**kwargs)

                return self

################################################################################
## Class for SBAS processing
################################################################################
class sbas:

        ################################################################################
        ## Initialistion of the class
        ################################################################################
        def __init__(self, 
                job: Optional[Union[any, None]] = None,
                title: Optional[Union[str, None]] = None,
                workdirectory: Optional[Union[str, None]] = None,
                pathstampsparms: Optional[Union[str, None]] = None,
                polarisation: Optional[Union[str]] = 'VV',
                roi: Optional[Union[any, None]] = None,
                satellite: Optional[str] = 'S1',
                satmode: Optional[str] = 'IW',
                satpass: Optional[Union[str, None]] = None,
                relorbit: Optional[Union[int, None]] = None,

                refdate: Optional[Union[str, None]] = None,

                email: Optional[Union[dict, None]] = None,
                processor: Optional[str] = 'stamps',
                ifgprocessor: Optional[str] = 'gamma',
                mode: Optional[str] = 'sbas',

                communpara: Optional[Union[any, None]] = None,

                mt_prep: Optional[Union[any, None]] = None,

                load_data: Optional[Union[any, None]] = None,

                phase_noise: Optional[Union[any, None]] = None,

                ps_selection: Optional[Union[any, None]] = None,

                ps_weeding: Optional[Union[any, None]] = None,

                phase_correction: Optional[Union[any, None]] = None,

                phase_unwrapping: Optional[Union[any, None]] = None,

                corr_lkerror: Optional[Union[any, None]] = None,

                corr_noise: Optional[Union[any, None]] = None,

                extract_res: Optional[Union[any, None]] = None,
  
                verbose: Optional[bool] = True,
                log: Optional[Union[str, None]] = None,
                gui: Optional[bool] = False,

                ):
                
                """Initilisation of the job for EZ-InSAR
                """                 

                # User information
                if not job == None: 
                        
                        if not 'ifgstack' in str(type(job)):
                                raise ValueError(usermessage.errormsg(__name__,'stampstsprocessing'.__name__,__file__,__copyright__,
                                        'The job input must be a ifgstack job.',None))

                        self.title = 'SBAS-StaMPS processing for %s' % (job.title) 
                        self.polarisation = polarisation
                        self.satellite = job.satellite
                        self.satmode = job.satmode
                        self.relorbit = job.relorbit
                        self.satpass = job.satpass
                        self.refdate = job.refdate
                        self.roi = job.roi
                        if not self.refdate == None: 
                                self.workdirectory = job.workdirectory+os.sep+'stack_stamps_'+self.polarisation[0].lower()+os.sep+'INSAR_'+self.refdate+os.sep+'SMALL_BASELINES'
                        else: 
                                self.workdirectory = None
                        self.ifgprocessor = job.processor

                else: 
                        self.title = title
                        self.workdirectory = workdirectory
                        self.satellite = satellite
                        self.satmode = satmode
                        self.relorbit = relorbit
                        self.satpass = satpass
                        self.refdate = refdate
                        self.polarisation = polarisation
                        if not roi == None: 
                                self.roi = roitools.importroi(self, roi)
                        else: 
                                self.roi = None

                        self.ifgprocessor = ifgprocessor
                
                self.processor = processor
                self.mode = mode
                
                if pathstampsparms == None and (not self.workdirectory == None):
                        self.pathstampsparms = self.workdirectory+os.sep+'parms.mat'
                else:
                        self.pathstampsparms = pathstampsparms

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

                self.processor = 'stamps'

                # For the Step 0: Commun parameters
                if communpara == None:
                        self.communpara = dict()
                        self.communpara['name'] = {'value': 'Step 0: Commun parameters', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.communpara['insar_processor'] = {'value': self.ifgprocessor, 
                                                'description': 'InSAR processor used', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.communpara['lambda'] = {'value': None, 
                                                'description': 'Wavelength', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.communpara['heading'] = {'value': None, 
                                                'description': 'Heading angle', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.communpara['ref_centre_lonlat'] = {'value': None, 
                                                'description': 'Location of the reference point (lon/lat centre) in list format', 
                                                'format': 'floatmat',
                                                'valuelist': None}            
                        self.communpara['ref_lat'] = {'value': None, 
                                                'description': 'Location of the reference point (min and max latitudes) in list format', 
                                                'format': 'floatmat',
                                                'valuelist': None}                     
                        self.communpara['ref_lon'] = {'value': None, 
                                                'description': 'Location of the reference point (min and max longitudes) in list format', 
                                                'format': 'floatmat',
                                                'valuelist': None}
                        self.communpara['ref_radius'] = {'value': None, 
                                                'description': 'Reference point radius in meters', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.communpara['ref_velocity'] = {'value': None, 
                                                'description': 'Velocity of the reference point in mm/yr', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.communpara['small_baseline_flag'] = {'value': 'y', 
                                                'description': 'Flag for the SBAS computation', 
                                                'format': 'list',
                                                'valuelist': ['y','n']}
                        self.communpara['parallelstep'] = {'value': False, 
                                                'description': 'Parallelisation of the StaMPS processing steps', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.communpara['n_cores'] = {'value': int(psutil.cpu_count(logical=True)*0.25), 
                                                'description': 'Number of thread per worker', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['n_jobs'] = {'value': 10, 
                                                'description': 'Number of workers', 
                                                'format': 'int',
                                                'valuelist': None} 
                        self.communpara['lonlat_offset'] = {'value': None, 
                                                'description': 'Offsets for longitude and latitude grids in list format', 
                                                'format': 'floatmat',
                                                'valuelist': None}
                        self.communpara['drop_ifg_index'] = {'value': None, 
                                                'description': 'List of interferograms dropped in list format', 
                                                'format': 'intmat',
                                                'valuelist': None}
                        self.communpara['subtr_tropo'] = {'value': 'n', 
                                                'description': 'Substraction of tropographic delays', 
                                                'format': 'list',
                                                'valuelist': ['y','n']}
                        self.communpara['tropo_method'] = {'value': 'a_l', 
                                                'description': 'Method for subtracting tropographic delays', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.communpara['shade_rel_angle'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'intmat',
                                                'valuelist': None}
                        self.communpara['slc_osf'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['plot_color_scheme'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.communpara['plot_dem_posting'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['plot_pixels_scatterer'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['plot_scatterer_size'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['done'] = {'value': True, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                        
                else:
                        self.communpara = communpara

                # For the Step 1: Preparation of PS
                if mt_prep == None:
                        self.mt_prep = dict()
                        self.mt_prep['name'] = {'value': 'Step 1: Preparation of PS', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.mt_prep['da_thresh'] = {'value': 0.6, 
                                                'description': 'Amplitude-dispersion threshold', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.mt_prep['rg_patches'] = {'value': 3, 
                                                'description': 'Number of patches in range', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.mt_prep['az_patches'] = {'value': 3, 
                                                'description': 'Number of patches in azimut',
                                                'format': 'int',
                                                'valuelist': None}
                        self.mt_prep['rg_overlap'] = {'value': 100, 
                                                'description': 'Patch overlap in range', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.mt_prep['az_overlap'] = {'value': 100, 
                                                'description': 'Patch overlap in azimut', 
                                                'format': 'todo',
                                                'valuelist': None}
                        self.mt_prep['maskfile'] = {'value': None, 
                                                'description': 'Mask file', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.mt_prep['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.load_data = load_data

                # For the Step 2: load_data
                if load_data == None:
                        self.load_data = dict()
                        self.load_data['name'] = {'value': 'Step 2: load_data', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.load_data['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.load_data = load_data

                # For the Step 3: Estimate phase noise
                if phase_noise == None:
                        self.phase_noise = dict()
                        self.phase_noise['name'] = {'value': 'Step 3: Estimate phase noise', 
                                               'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.phase_noise['max_topo_err'] = {'value': 5, 
                                                'description': 'Maximum uncorrelated DEM error in metres', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_noise['filter_grid_size'] = {'value': 50, 
                                                'description': 'Pixel size of grid in metre for filtering', 
                                                'format': 'todo',
                                                'valuelist': None}
                        self.phase_noise['filter_weighting'] = {'value': 'P-square', 
                                                'description': 'Method for filter weighting', 
                                                'format': 'list',
                                                'valuelist': ['P-square','SNR']}
                        self.phase_noise['clap_win'] = {'value': 32, 
                                                'description': 'Filter window', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_noise['clap_low_pass_wavelength'] = {'value': 800, 
                                                'description': 'Cut-off spatial wavelength', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_noise['clap_alpha'] = {'value': 1.0, 
                                                'description': 'Filter alpha term', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.phase_noise['clap_beta'] = {'value': 0.3, 
                                                'description': 'Filter beta term', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.phase_noise['gamma_change_convergence'] = {'value': 0.005, 
                                                'description': 'Threshold for convergence', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.phase_noise['gamma_max_iterations'] = {'value': 3, 
                                                'description': 'Maximum number of iterations', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_noise['gamma_stdev_reject'] = {'value': 0.0, 
                                                'description': 'TBD', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.phase_noise['quick_est_gamma_flag'] = {'value': None, 
                                                'description': 'Flag for the quick gamma estimation', 
                                                'format': 'list',
                                                'valuelist': ['None','y','n']}
                        self.phase_noise['select_reest_gamma_flag'] = {'value': None, 
                                                'description': 'Flag for the re-estimation of gamma', 
                                                'format': 'list',
                                                'valuelist': ['None','y','n']}
                        self.phase_noise['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.phase_noise = phase_noise

                # For the Step 4: PS selection
                if ps_selection == None:
                        self.ps_selection = dict()
                        self.ps_selection['name'] = {'value': 'Step 4: PS selection', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.ps_selection['select_method'] = {'value': 'DENSITY', 
                                                'description': 'Selection method', 
                                                'format': 'list',
                                                'valuelist': ['DENSITY','PERCENT']}
                        self.ps_selection['percent_rand'] = {'value': 1, 
                                                'description': 'Threshold for the PERCENT method', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ps_selection['density_rand'] = {'value': 2, 
                                                'description': 'Threshold for the DENSITY method', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ps_selection['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.ps_selection = phase_noise

                # For the Step 5: PS weeding
                if ps_weeding == None:
                        self.ps_weeding = dict()
                        self.ps_weeding['name'] = {'value': 'Step 5: PS weeding', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.ps_weeding['weed_standard_dev'] = {'value': float('inf'),
                                                'description': 'Threshold standard deviation', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ps_weeding['weed_max_noise'] = {'value': float('inf'), 
                                                'description': 'Threshold for the maximum noise allowed for a pixel', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.ps_weeding['weed_time_win'] = {'value': 730, 
                                                'description': 'Smoothing window (in days) for estimating phase noise distribution for each pair of neighbouring pixels.', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.ps_weeding['weed_neighbours'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'y','n']}
                        self.ps_weeding['weed_zero_elevation'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'y','n']}
                        self.ps_weeding['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.ps_weeding = ps_weeding

                # For the Step 6: Phase correction
                if phase_correction == None:
                        self.phase_correction = dict()
                        self.phase_correction['name'] = {'value': 'Step 6: Phase correction', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.phase_correction['merge_resample_size'] = {'value': 100, 
                                                'description': 'Coarser posting (in m) to resample to. If set to 0 , no resampling is applied.', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_correction['merge_standard_dev'] = {'value': float('inf'), 
                                                'description': 'Threshold standard deviation', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.phase_correction['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.phase_correction = phase_correction
           
                # For the Step 7: Phase unwrapping
                if phase_unwrapping == None:
                        self.phase_unwrapping = dict()
                        self.phase_unwrapping['name'] = {'value': 'Step 7: Phase unwrapping', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_method'] = {'value': '3D_QUICK', 
                                                'description': 'Unwrapping method', 
                                                'format': 'list',
                                                'valuelist': ['3D','3D_QUICK','2D']}
                        self.phase_unwrapping['unwrap_prefilter_flag'] = {'value': 'y', 
                                                'description': 'Phase filtering before unwrapping to reduce noise.', 
                                                'format': 'list',
                                                'valuelist': ['y','n']}
                        self.phase_unwrapping['unwrap_patch_phase'] = {'value': 'n', 
                                                'description': 'Use the patch phase from Step 3 as prefiltered phase.',
                                                'format': 'list',
                                                'valuelist': ['y','n']}
                        self.phase_unwrapping['unwrap_grid_size'] = {'value': 200, 
                                                'description': 'Resampling grid spacing for unwrapping', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_time_win'] = {'value': 730, 
                                                'description': 'Smoothing window (in days)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_gold_alpha'] = {'value': 0.8, 
                                                'description': 'Alpha term of the Goldstein filter', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_alpha'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_gold_n_win'] = {'value': None, 
                                                'description': 'Window size for Goldstein filter', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_hold_good_values'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'y','n']}
                        self.phase_unwrapping['unwrap_la_error_flag'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'y','n']}
                        self.phase_unwrapping['unwrap_spatial_cost_func_flag'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'y','n']}
                        self.phase_unwrapping['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.phase_unwrapping = phase_unwrapping

                # For the Step 8: Spatially correlated look angle (DEM) error
                if corr_lkerror == None:
                        self.corr_lkerror = dict()
                        self.corr_lkerror['name'] = {'value': 'Step 8: Spatially correlated look angle (DEM) error', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.corr_lkerror['scla_drop_index'] = {'value': None, 
                                                'description': 'List of interferograms dropped', 
                                                'format': 'intmat',
                                                'valuelist': None}
                        self.corr_lkerror['scla_deramp'] = {'value': 'n', 
                                                'description': 'Deramping of interferograms', 
                                                'format': 'list',
                                                'valuelist': ['y','n']}
                        self.corr_lkerror['scla_method'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.corr_lkerror['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.corr_lkerror = corr_lkerror

                # For the Step 9: Filter spatially correlated noise
                if corr_noise == None:
                        self.corr_noise = dict()
                        self.corr_noise['name'] = {'value': 'Step 9: Filter spatially correlated noise', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.corr_noise['scn_deramp_ifg'] = {'value': None, 
                                                'description': 'List of interferograms', 
                                                'format': 'intmat',
                                                'valuelist': None}          
                        self.corr_noise['scn_kriging_flag'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'n','y']}        
                        self.corr_noise['scn_time_win'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}      
                        self.corr_noise['scn_wavelength'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.corr_noise['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.corr_noise = corr_noise
                
                # For the Step 10: Save the results
                if extract_res == None:
                        self.extract_res = dict()
                        self.extract_res['name'] = {'value': 'Step 10: Save the results', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.extract_res['correction'] = {'value': 'd', 
                                                'description': 'String parameters for InSAR correction', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.extract_res['ecraseprevious'] = {'value': True, 
                                                'description': 'Ecrase the previous results', 
                                                'format': 'bool',
                                                'valuelist': None}           
                        self.extract_res['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.extract_res = extract_res
             
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
                        logger.info('Creation of a EZ-InSAR StaMPS SBAS processing')

                # Initilisation by the user
                self = jobproctools.check(self,verbose=False)
                
        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def print(self):
                """Print the StaMPS-processing attributes for EZ-InSAR"""

                attrs = vars(self)
                print(', '.join("%s: %s" % item for item in attrs.items()))

                return self

        ################################################################################
        ## Method to check the attributes
        ################################################################################
        def check(self,**kwargs):
                """check and display the StaMPS-processing attributes for EZ-InSAR"""

                self = jobproctools.check(self,**kwargs)

                return self

        ################################################################################
        ## Method to write the StaMPS parameter file 
        ################################################################################
        def writeparameters(self,**kwargs):
                """Write the StaMPS parameter file from an EZ-InSAR job"""

                self = stampstools.writeparameters(self,**kwargs)

                return self

        ################################################################################
        ## Method to write the StaMPS parameter file 
        ################################################################################
        def readparameters(self,**kwargs):
                """Read the StaMPS parameter file and update an EZ-InSAR job"""

                self = stampstools.readparameters(self,**kwargs)

                return self
        
        ################################################################################
        ## Run the processing
        ################################################################################
        def run(self,**kwargs):
                """Run the TS processing using StaMPS processor"""

                self = jobrun.run(self,**kwargs)

                return self
                
################################################################################
## Class for MERGED processing
################################################################################
class merged:

        ################################################################################
        ## Initialistion of the class
        ################################################################################
        def __init__(self, 
                job: Optional[Union[any, None]] = None,
                title: Optional[Union[str, None]] = None,
                workdirectory: Optional[Union[str, None]] = None,
                pathstampsparms: Optional[Union[str, None]] = None,
                polarisation: Optional[Union[str]] = 'VV',
                roi: Optional[Union[any, None]] = None,
                satellite: Optional[str] = 'S1',
                satmode: Optional[str] = 'IW',
                satpass: Optional[Union[str, None]] = None,
                relorbit: Optional[Union[int, None]] = None,

                refdate: Optional[Union[str, None]] = None,

                email: Optional[Union[dict, None]] = None,
                processor: Optional[str] = 'stamps',
                ifgprocessor: Optional[str] = 'gamma',
                mode: Optional[str] = 'merged',

                communpara: Optional[Union[any, None]] = None,

                merging: Optional[Union[any, None]] = None,

                phase_unwrapping: Optional[Union[any, None]] = None,

                corr_lkerror: Optional[Union[any, None]] = None,

                corr_noise: Optional[Union[any, None]] = None,

                extract_res: Optional[Union[any, None]] = None,
  
                verbose: Optional[bool] = True,
                log: Optional[Union[str, None]] = None,
                gui: Optional[bool] = False,

                ):
                
                """Initilisation of the job for EZ-InSAR
                """                 

                # User information
                if not job == None: 
                        
                        if not 'ifgstack' in str(type(job)):
                                raise ValueError(usermessage.errormsg(__name__,'stampstsprocessing'.__name__,__file__,__copyright__,
                                        'The job input must be a ifgstack job.',None))

                        self.title = 'SBAS-StaMPS processing for %s' % (job.title) 
                        self.polarisation = polarisation
                        self.satellite = job.satellite
                        self.satmode = job.satmode
                        self.relorbit = job.relorbit
                        self.satpass = job.satpass
                        self.refdate = job.refdate
                        self.roi = job.roi
                        if not self.refdate == None: 
                                self.workdirectory = job.workdirectory+os.sep+'stack_stamps_'+self.polarisation.lower()+os.sep+'INSAR_'+self.refdate+os.sep+'MERGED'
                        else: 
                                self.workdirectory =None 
                        self.ifgprocessor = job.processor

                else: 
                        self.title = title
                        self.workdirectory = workdirectory
                        self.satellite = satellite
                        self.satmode = satmode
                        self.relorbit = relorbit
                        self.satpass = satpass
                        self.refdate = refdate
                        self.polarisation = polarisation
                        if not roi == None: 
                                self.roi = roitools.importroi(self, roi)
                        else: 
                                self.roi = None

                        self.ifgprocessor = ifgprocessor
                
                self.processor = processor
                self.mode = mode
                
                if pathstampsparms == None and (not self.workdirectory == None):
                        self.pathstampsparms = self.workdirectory+os.sep+'parms.mat'
                else:
                        self.pathstampsparms = pathstampsparms

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

                self.processor = 'stamps'

                # For the Step 0: Commun parameters
                if communpara == None:
                        self.communpara = dict()
                        self.communpara['name'] = {'value': 'Step 0: Commun parameters', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.communpara['insar_processor'] = {'value': self.ifgprocessor, 
                                                'description': 'InSAR processor used', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.communpara['lambda'] = {'value': None, 
                                                'description': 'Wavelength', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.communpara['heading'] = {'value': None, 
                                                'description': 'Heading angle', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.communpara['ref_centre_lonlat'] = {'value': None, 
                                                'description': 'Location of the reference point (lon/lat centre) in list format', 
                                                'format': 'floatmat',
                                                'valuelist': None}            
                        self.communpara['ref_lat'] = {'value': None, 
                                                'description': 'Location of the reference point (min and max latitudes) in list format', 
                                                'format': 'floatmat',
                                                'valuelist': None}                     
                        self.communpara['ref_lon'] = {'value': None, 
                                                'description': 'Location of the reference point (min and max longitudes) in list format', 
                                                'format': 'floatmat',
                                                'valuelist': None}
                        self.communpara['ref_radius'] = {'value': None, 
                                                'description': 'Reference point radius in meters', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.communpara['ref_velocity'] = {'value': None, 
                                                'description': 'Velocity of the reference point in mm/yr', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.communpara['small_baseline_flag'] = {'value': 'y', 
                                                'description': 'Flag for the SBAS computation', 
                                                'format': 'list',
                                                'valuelist': ['y','n']}
                        self.communpara['parallelstep'] = {'value': False, 
                                                'description': 'Parallelisation of the StaMPS processing steps', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.communpara['n_cores'] = {'value': int(psutil.cpu_count(logical=True)*0.25), 
                                                'description': 'Number of thread per worker', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['n_jobs'] = {'value': 10, 
                                                'description': 'Number of workers', 
                                                'format': 'int',
                                                'valuelist': None} 
                        self.communpara['lonlat_offset'] = {'value': None, 
                                                'description': 'Offsets for longitude and latitude grids in list format', 
                                                'format': 'floatmat',
                                                'valuelist': None}
                        self.communpara['drop_ifg_index'] = {'value': None, 
                                                'description': 'List of interferograms dropped in list format', 
                                                'format': 'intmat',
                                                'valuelist': None}
                        self.communpara['subtr_tropo'] = {'value': 'n', 
                                                'description': 'Substraction of tropographic delays', 
                                                'format': 'list',
                                                'valuelist': ['y','n']}
                        self.communpara['tropo_method'] = {'value': 'a_l', 
                                                'description': 'Method for subtracting tropographic delays', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.communpara['shade_rel_angle'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'intmat',
                                                'valuelist': None}
                        self.communpara['slc_osf'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['plot_color_scheme'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.communpara['plot_dem_posting'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['plot_pixels_scatterer'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['plot_scatterer_size'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.communpara['done'] = {'value': True, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.communpara = communpara

                # For the Step 1: Merging 
                if merging == None:
                        self.merging = dict()
                        self.merging['name'] = {'value': 'Step 1: Merging', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None} 
                        self.merging['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.merging = merging
           
                # For the Step 2: Phase unwrapping
                if phase_unwrapping == None:
                        self.phase_unwrapping = dict()
                        self.phase_unwrapping['name'] = {'value': 'Step 2: Phase unwrapping', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_method'] = {'value': '3D_QUICK', 
                                                'description': 'Unwrapping method', 
                                                'format': 'list',
                                                'valuelist': ['3D','3D_QUICK','2D']}
                        self.phase_unwrapping['unwrap_prefilter_flag'] = {'value': 'y', 
                                                'description': 'Phase filtering before unwrapping to reduce noise.', 
                                                'format': 'list',
                                                'valuelist': ['y','n']}
                        self.phase_unwrapping['unwrap_patch_phase'] = {'value': 'n', 
                                                'description': 'Use the patch phase from Step 3 as prefiltered phase.',
                                                'format': 'list',
                                                'valuelist': ['y','n']}
                        self.phase_unwrapping['unwrap_grid_size'] = {'value': 200, 
                                                'description': 'Resampling grid spacing for unwrapping', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_time_win'] = {'value': 730, 
                                                'description': 'Smoothing window (in days)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_gold_alpha'] = {'value': 0.8, 
                                                'description': 'Alpha term of the Goldstein filter', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_alpha'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_gold_n_win'] = {'value': None, 
                                                'description': 'Window size for Goldstein filter', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.phase_unwrapping['unwrap_hold_good_values'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'y','n']}
                        self.phase_unwrapping['unwrap_la_error_flag'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'y','n']}
                        self.phase_unwrapping['unwrap_spatial_cost_func_flag'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'y','n']}
                        self.phase_unwrapping['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.phase_unwrapping = phase_unwrapping

                # For the Step 3: Spatially correlated look angle (DEM) error
                if corr_lkerror == None:
                        self.corr_lkerror = dict()
                        self.corr_lkerror['name'] = {'value': 'Step 3: Spatially correlated look angle (DEM) error', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.corr_lkerror['scla_drop_index'] = {'value': None, 
                                                'description': 'List of interferograms dropped', 
                                                'format': 'intmat',
                                                'valuelist': None}
                        self.corr_lkerror['scla_deramp'] = {'value': 'y', 
                                                'description': 'Deramping of interferograms', 
                                                'format': 'list',
                                                'valuelist': ['y','n']}
                        self.corr_lkerror['scla_method'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.corr_lkerror['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.corr_lkerror = corr_lkerror

                # For the Step 4: Filter spatially correlated noise
                if corr_noise == None:
                        self.corr_noise = dict()
                        self.corr_noise['name'] = {'value': 'Step 4: Filter spatially correlated noise', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.corr_noise['scn_deramp_ifg'] = {'value': None, 
                                                'description': 'List of interferograms', 
                                                'format': 'intmat',
                                                'valuelist': None}          
                        self.corr_noise['scn_kriging_flag'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'list',
                                                'valuelist': [None,'n','y']}        
                        self.corr_noise['scn_time_win'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}      
                        self.corr_noise['scn_wavelength'] = {'value': None, 
                                                'description': 'TBD', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.corr_noise['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.corr_noise = corr_noise

                # For the Step 5: Save the results
                if extract_res == None:
                        self.extract_res = dict()
                        self.extract_res['name'] = {'value': 'Step 5: Save the results', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.extract_res['correction'] = {'value': 'd', 
                                                'description': 'String parameters for InSAR correction', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.extract_res['ecraseprevious'] = {'value': True, 
                                                'description': 'Ecrase the previous results', 
                                                'format': 'bool',
                                                'valuelist': None}           
                        self.extract_res['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.extract_res = extract_res
             
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
                        logger.info('Creation of a EZ-InSAR StaMPS MERGED processing')

                # Initilisation by the user
                self = jobproctools.check(self,verbose=False)
                
        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def print(self):
                """Print the StaMPS-processing attributes for EZ-InSAR"""

                attrs = vars(self)
                print(', '.join("%s: %s" % item for item in attrs.items()))

                return self

        ################################################################################
        ## Method to check the attributes
        ################################################################################
        def check(self,**kwargs):
                """check and display the StaMPS-processing attributes for EZ-InSAR"""

                self = jobproctools.check(self,**kwargs)

                return self

        ################################################################################
        ## Method to write the StaMPS parameter file 
        ################################################################################
        def writeparameters(self,**kwargs):
                """Write the StaMPS parameter file from an EZ-InSAR job"""

                self = stampstools.writeparameters(self,**kwargs)

                return self

        ################################################################################
        ## Method to write the StaMPS parameter file 
        ################################################################################
        def readparameters(self,**kwargs):
                """Read the StaMPS parameter file and update an EZ-InSAR job"""

                self = stampstools.readparameters(self,**kwargs)

                return self
        
        ################################################################################
        ## Run the processing
        ################################################################################
        def run(self,**kwargs):
                """Run the TS processing using StaMPS processor"""

                self = jobrun.run(self,**kwargs)

                return self
