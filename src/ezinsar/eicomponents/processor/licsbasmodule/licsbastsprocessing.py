#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage the class for TS processing using LiCSBAS

The module allows to create the EZ-InSAR processing class using LiCSBAS. 
    
    (From `ezinsar` package)

Note: 
        Each function can directly used in Python scripts or/and a Python terminal

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
from ezinsar.eicomponents.processor.licsbasmodule import licsartools
from ezinsar.eicomponents.jobmodule import jobrun, jobproctools

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""
################################################################################
## Class for SBAS processing
################################################################################
class sbas:
        '''Attributes:
                title (str): Name/Definition of the user [Default: `None`]
                workdirectory (str): Work directory of the processing. [Default: `None`]
                polarisation (list): List of polarisation. [Default: ``['VV']``]
                roi (str): Polygon of the Region of Interest. [Default: `None`]
                satellite (str): Satellite name. [Default: ``S1``]
                satmode (str): Satellite mode. [Default: ``SM``]
                relorbit (int): Relative orbit number. [Default: `None`]
                satpass (str): Satellite direction. [Default: `None`]
                email (dict): Dictionary of the email parameters
                n_para (int): Number of workers. [Default: ``1``]
                mem_size (int): RAM used by Doris. [Default: ``25%``]
                processor (str): Processor. Here LiCSBAS
                frame (str): Frame of the Sentinel-1
                date1 (str): First date in YYYYMMDD format
                date2 (str): Last date in YYYYMMDD format
                get_geotiff (dict): EZ-InSAR parameter dictionary
                prep_ifg (dict): EZ-InSAR parameter dictionary
                check_unw (dict): EZ-InSAR parameter dictionary
                loop_closure (dict): EZ-InSAR parameter dictionary
                sb_inv (dict): EZ-InSAR parameter dictionary
                vel_std (dict): EZ-InSAR parameter dictionary
                mask_ts (dict): EZ-InSAR parameter dictionary
                filt_ts (dict): EZ-InSAR parameter dictionary
                extract_res (dict): EZ-InSAR parameter dictionary
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
                polarisation: Optional[Union[str]] = 'VV',
                roi: Optional[Union[any, None]] = None,
                satellite: Optional[str] = 'S1',
                satmode: Optional[str] = 'IW',
                satpass: Optional[Union[str, None]] = None,
                relorbit: Optional[Union[int, None]] = None,
                frame: Optional[Union[str, None]] = None,
                processor: Optional[Union[str, None]] = 'licsbas',
                mode: Optional[Union[str, None]] = 'sbas',
                date1 = '20140101',
                date2 = '20260101',
                refdate: Optional[Union[str, None]] = None,
                email: Optional[Union[dict, None]] = None,
                get_geotiff: Optional[Union[any, None]] = None,
                prep_ifg: Optional[Union[any, None]] = None,
                check_unw: Optional[Union[any, None]] = None,
                loop_closure: Optional[Union[any, None]] = None,
                sb_inv: Optional[Union[any, None]] = None,
                vel_std: Optional[Union[any, None]] = None,
                mask_ts: Optional[Union[any, None]] = None,
                filt_ts: Optional[Union[any, None]] = None,
                extract_res: Optional[Union[any, None]] = None,

                verbose: Optional[bool] = True,
                log: Optional[Union[str, None]] = None,
                gui: Optional[bool] = False,
                ):
                
                """Initilisation of the job for EZ-InSAR
                
                Args:
                        job (``ezinsar.job``): EZ-InSAR job
                        title (str): Name/Definition of the user [Default: `None`]
                        workdirectory (str): Work directory of the processing. [Default: `None`]
                        polarisation (list): List of polarisation. [Default: ``['VV']``]
                        roi (str): Polygon of the Region of Interest. [Default: `None`]
                        satellite (str): Satellite name. [Default: ``S1``]
                        satmode (str): Satellite mode. [Default: ``SM``]
                        relorbit (int): Relative orbit number. [Default: `None`]
                        satpass (str): Satellite direction. [Default: `None`]
                        email (dict): Dictionary of the email parameters
                        frame (str): Frame of the Sentinel-1
                        date1 (str): First date in YYYYMMDD format
                        date2 (str): Last date in YYYYMMDD format
                        get_geotiff (dict): EZ-InSAR parameter dictionary
                        prep_ifg (dict): EZ-InSAR parameter dictionary
                        check_unw (dict): EZ-InSAR parameter dictionary
                        loop_closure (dict): EZ-InSAR parameter dictionary
                        sb_inv (dict): EZ-InSAR parameter dictionary
                        vel_std (dict): EZ-InSAR parameter dictionary
                        mask_ts (dict): EZ-InSAR parameter dictionary
                        filt_ts (dict): EZ-InSAR parameter dictionary
                        extract_res (dict): EZ-InSAR parameter dictionary
                        verbose (bool): Verbose mode. [Default: `True`]
                        log (str): Log file
                        gui (bool): GUI mode (not used). [Default: `False`]

                Returns: 
                        ``esinsar.job``: EZ-InSAR Doris coregistration class

                """

                # User information
                if not job == None: 
                
                        self.title = 'SBAS-LiSBAS processing for %s' % (job.nameJob) 
                        self.polarisation = polarisation
                        self.satellite = job.satellite
                        self.satmode = job.satmode
                        self.relorbit = job.relorbit
                        self.satpass = job.satpass
                        self.roi = str(job.roi)
                        self.date1 = job.date1.strftime("%Y%m%d")
                        self.date2 = job.date2.strftime("%Y%m%d")
                        self.workdirectory = job.workdirectory+os.sep+'stack_licsbas_vv'

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
                        self.roi = str(self.roi)
                        self.date1 = date1
                        self.date2 = date2


                self.ifgprocessor = 'licsar'
                self.processor = 'licsbas'
                self.mode = 'sbas'
                self.frame = frame
                self.n_para = 3
                self.mem_size = 10000

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

                # For the Step 1: get_geotiff
                if get_geotiff == None:
                        self.get_geotiff = dict()
                        self.get_geotiff['name'] = {'value': 'Step 1: get_geotiff', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.get_geotiff['function'] = {'value': 'licsbas', 
                                                'description': 'Function for data downloadind', 
                                                'format': 'list',
                                                'valuelist': ['licsbas']}
                        self.get_geotiff['get_gacos'] = {'value': False, 
                                                'description': 'Enable the GACOS-data downloading', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.get_geotiff['get_mli'] = {'value': True, 
                                                'description': 'Enable the intensity downloading', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.get_geotiff['get_pha'] = {'value': False, 
                                                'description': 'Enable the wrapped phase downloading', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.get_geotiff['n_para'] = {'value': 10, 
                                                'description': 'Number of parallel donwloading', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.get_geotiff['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.get_geotiff = get_geotiff

                # For the Step 2: prep_ifg
                if prep_ifg == None:
                        self.prep_ifg = dict()
                        self.prep_ifg['name'] = {'value': 'Step 2: prep_ifg', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.prep_ifg['reunwrap'] = {'value': False, 
                                                'description': 'Re-unwrap the ifgs', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.prep_ifg['nb_look'] = {'value': 1, 
                                                'description': 'Number of looks', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.prep_ifg['clipping'] = {'value': True, 
                                                'description': 'Clip the data regarding the ROI', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.prep_ifg['filter'] = {'value': 'gold', 
                                                'description': 'Clip the data regarding the ROI', 
                                                'format': 'list',
                                                'valuelist': ['none','gold','gauss','adf']}
                        self.prep_ifg['gacos'] = {'value': False, 
                                                'description': 'Enable the GACOS correction', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.prep_ifg['fillholegacos'] = {'value': False, 
                                                'description': 'Enable the GACOS inpaint interpolation', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.prep_ifg['height_corr'] = {'value': False, 
                                                'description': 'Enable the height correlation correction', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.prep_ifg['cascade'] = {'value': 'cascade', 
                                                'description': 'Enable the cascade unwrapping', 
                                                'format': 'list',
                                                'valuelist': ['none','cascade','cascade_full']}
                        self.prep_ifg['thres'] = {'value': 0.3, 
                                                'description': 'Masking threshold', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.prep_ifg['landmask'] = {'value': True, 
                                                'description': 'Enable the landmask application', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.prep_ifg['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.prep_ifg = prep_ifg

                # For the Step 3: check_unw
                if check_unw == None:
                        self.check_unw = dict()
                        self.check_unw['name'] = {'value': 'Step 3: check_unw', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.check_unw['coherence_thres'] = {'value': 0.05, 
                                                'description': 'Threshold of average coherence', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.check_unw['unw_thres'] = {'value': 0.3, 
                                                'description': 'Threshold of average unw', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.check_unw['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.check_unw = check_unw

                # For the Step 4: loop_closure
                if loop_closure == None:
                        self.loop_closure = dict()
                        self.loop_closure['name'] = {'value': 'Step 4: loop_closure', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.loop_closure['loop_thres'] = {'value': 1.5, 
                                                'description': 'Loop threshold in rad', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.loop_closure['multi_prime'] = {'value': True, 
                                                'description': 'Enable the multi prime mode', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.loop_closure['rm_ifg_list'] = {'value': 'none', 
                                                'description': 'List of removed ifgs', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.loop_closure['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.loop_closure = loop_closure

                # For the Step 5: sb_inv
                if sb_inv == None:
                        self.sb_inv = dict()
                        self.sb_inv['name'] = {'value': 'Step 5: sb_inv', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.sb_inv['inv_alg'] = {'value': 'LS', 
                                                'description': 'Algorithm', 
                                                'format': 'list',
                                                'valuelist': ['LS','WLS']}
                        
                        self.sb_inv['mem_size'] = {'value': 10000, 
                                                'description': 'Max. RAM memory', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.sb_inv['gamma'] = {'value': 0.0, 
                                                'description': 'Gamma value for inversion', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.sb_inv['n_unw_r_thre'] = {'value': 1.0, 
                                                'description': 'Theshold of the number of unwrapped ifgs', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.sb_inv['keep_incfile'] = {'value': False, 
                                                'description': 'Keep the inc. and residue files', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.sb_inv['gpu'] = {'value': False, 
                                                'description': 'Use the GPU (need cupy)', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.sb_inv['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.sb_inv = sb_inv

                # For the Step 6: vel_std
                if vel_std == None:
                        self.vel_std = dict()
                        self.vel_std['name'] = {'value': 'Step 6: vel_std', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.vel_std['ransac'] = {'value': False, 
                                                'description': 'Enable the ransac processing', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.vel_std['gpu'] = {'value': False, 
                                                'description': 'Use the GPU (need cupy)', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.vel_std['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.vel_std = vel_std

                # For the Step 7: mask_ts
                if mask_ts == None:
                        self.mask_ts = dict()
                        self.mask_ts['name'] = {'value': 'Step 7: mask_ts', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.mask_ts['coh_avg_thres'] = {'value': 0.05, 
                                                'description': 'Average coherence threshold', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.mask_ts['unw_r_thres'] = {'value': 1.5, 
                                                'description': 'Unwrapped interferogram threshold', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.mask_ts['vstd_thres'] = {'value': 100.0, 
                                                'description': 'Velocity STD threshold', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.mask_ts['maxTlen'] = {'value': 10.0, 
                                                'description': 'Max time lenght', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.mask_ts['n_gap_thres'] = {'value': 10, 
                                                'description': 'Gap threshold', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.mask_ts['stc_thres'] = {'value': 5.0, 
                                                'description': 'Spatial-temporal consistency', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.mask_ts['n_ifg_noloop'] = {'value': 50, 
                                                'description': 'No-loop threshold', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.mask_ts['n_loop_err'] = {'value': 5, 
                                                'description': 'No-loop error threshold', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.mask_ts['resid_rms_err'] = {'value': 2.0, 
                                                'description': 'Residue RMS threshold', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.mask_ts['avg_phase_bias'] = {'value': False, 
                                                'description': 'Use the average absolute pahse loop closure error', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.mask_ts['keep_isolated'] = {'value': False, 
                                                'description': 'Keep the isolated pixels', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.mask_ts['noautoadjust'] = {'value': True, 
                                                'description': 'Block the auto adjust threshold when all pixels are masked', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.mask_ts['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None} 
                else:
                        self.mask_ts = mask_ts

                # For the Step 8: filt_ts
                if filt_ts == None:
                        self.filt_ts = dict()
                        self.filt_ts['name'] = {'value': 'Step 8: filt_ts', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.filt_ts['sfilter'] = {'value': 2.0, 
                                                'description': 'Width of spatial filter [km]', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.filt_ts['tfilter'] = {'value': 'auto', 
                                                'description': 'Width of temporal filter [km] in str format', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.filt_ts['deramppoly'] = {'value': 0, 
                                                'description': 'Degree of deramp', 
                                                'format': 'list',
                                                'valuelist': [0,1,2]}
                        self.filt_ts['demerr'] = {'value': False, 
                                                'description': 'Enable the DEM error estimation', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.filt_ts['hgt_linear'] = {'value': False, 
                                                'description': 'Enable the topo-correlated phase estimation and substration', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.filt_ts['hgt_min'] = {'value': 200, 
                                                'description': 'Minumum hgt to take into account [m]', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.filt_ts['hgt_max'] = {'value': 10000, 
                                                'description': 'Maximun hgt to take into account [m]', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.filt_ts['nomask'] = {'value': False, 
                                                'description': 'Enable the filter to unmasked data', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.filt_ts['nofilter'] = {'value': True, 
                                                'description': 'Block the temporal and spatial filter', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.filt_ts['range_geo'] = {'value': 'none', 
                                                'description': 'Geo range used by the deramp and hgt estimations. ie. lon1/lon2/lat1/lat2,', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.filt_ts['ex_range_geo'] = {'value': 'none', 
                                                'description': 'Geo exclusion range used by the deramp and hgt estimations. ie. lon1/lon2/lat1/lat2,', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.filt_ts['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None} 
                else:
                        self.filt_ts = filt_ts

                # For the Step 9: extract_res
                if extract_res == None:
                        self.extract_res = dict()
                        self.extract_res['name'] = {'value': 'Step 9: extract_res', 
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
                        logger.info('Creation of a EZ-InSAR LiCSBAS SBAS processing')

                # Initilisation by the user
                self = jobproctools.check(self,verbose=False,mode='low')
                
        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def print(self):
                """Print the LiCSBAS-processing attributes for EZ-InSAR"""

                attrs = vars(self)
                print(', '.join("%s: %s" % item for item in attrs.items()))

                return self

        ################################################################################
        ## Method to check the attributes
        ################################################################################
        def check(self,**kwargs):
                """check and display the LiCSBAS-processing attributes for EZ-InSAR"""

                self = jobproctools.check(self,**kwargs)

                return self
        
        ################################################################################
        ## Run the processing
        ################################################################################
        def run(self,**kwargs):
                """Run the TS processing using LiCSBAS processor"""

                self = jobrun.run(self,**kwargs)

                return self

        ################################################################################
        ## Detect the frame
        ################################################################################
        def detectframe(self,**kwargs):
                """Detect the frame for the LiCSBAS processor"""

                self.frame = licsartools.detectframe(job=self,**kwargs)['frame']

                return self
