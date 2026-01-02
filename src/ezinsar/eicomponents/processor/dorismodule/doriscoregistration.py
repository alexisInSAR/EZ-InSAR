#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage the class for coregistration processing using Doris

The module allows to create the EZ-InSAR coregistration class using Doris. 
    
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
from ezinsar import usermessage
from ezinsar.eicomponents.roimodule import roitools
from ezinsar.eicomponents.processor.dorismodule import doristools
from ezinsar.eicomponents.jobmodule import jobrun, jobproctools
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Class to manage the EZ-InSAR job
##      (part of EZ-InSAR)
################################################################################
class coregistration:
        '''EZ-InSAR coregistration class for Doris 
        
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
                nisarwavelength (str): NISAR wavelenght. [Default: ``L``]
                relorbit (int): Relative orbit number. [Default: `None`]
                satpass (str): Satellite direction. [Default: `None`]
                email (dict): Dictionary of the emal parameters
                computercores (int): Number of threads. [Default: ``0``]
                computerworkers (int): Number of workers. [Default: ``1``]
                computerRAM (int): RAM used by Doris. [Default: ``25%``]
                processor (str): Processor. Here Doris. 
                modeforce (bool): Forcing mode. [Default: `True`]
                modecropping (str): Mode of the cropping. [Default: ``auto``]
                mlazi (int): Multilook factor in azimuth
                mlran (int): Multilook factor in range 
                mlazidisplay (int): Multilook factor in azimuth for displaying
                mlrandisplay (int): Multilook factor in range for displaying
                checkSLC (dict): EZ-InSAR parameter dictionary
                checkOrbit (dict): EZ-InSAR parameter dictionary
                coarserefdate (dict): EZ-InSAR parameter dictionary
                extractimage (dict): EZ-InSAR parameter dictionary
                refinerefdate (dict): EZ-InSAR parameter dictionary
                mastertiming (dict): EZ-InSAR parameter dictionary
                oversample (dict): EZ-InSAR parameter dictionary
                coarseoffset (dict): EZ-InSAR parameter dictionary
                filtazi (dict): EZ-InSAR parameter dictionary
                finecoreg (dict): EZ-InSAR parameter dictionary
                reltiming (dict): EZ-InSAR parameter dictionary
                demassist (dict): EZ-InSAR parameter dictionary
                coregpm (dict): EZ-InSAR parameter dictionary
                resample (dict): EZ-InSAR parameter dictionary
                finalstack (dict): EZ-InSAR parameter dictionary
                cleanstack (dict): EZ-InSAR parameter dictionary
                updatestack (dict): EZ-InSAR parameter dictionary
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
                satmode: Optional[str] = 'SM',
                nisarwavelength: Optional[str] = 'L',

                relorbit: Optional[Union[int, None]] = None,
                satpass: Optional[Union[str, None]] = None,

                email: Optional[Union[dict, None]] = None,
                computercores: Optional[Union[int, None]] = 0, # Number of threads
                computerworkers: Optional[Union[int, None]] = 1, # Number of processes in parallel
                computerRAM: Optional[Union[int, None]] = int((psutil.virtual_memory().total*0.25)/1e6),
                processor: Optional[str] = 'doris',
                modeforce: Optional[bool] = True,

                modecropping: Optional[Union[any, None]] = 'auto',

                mlazi: Optional[Union[int, None]] = None,
                mlran: Optional[Union[int, None]] = None,

                mlazidisplay: Optional[Union[int, None]] = None,
                mlrandisplay: Optional[Union[int, None]] = None,

                checkSLC: Optional[Union[any, None]] = None,
                checkOrbit: Optional[Union[any, None]] = None,
                coarserefdate: Optional[Union[any, None]] = None,
                extractimage: Optional[Union[any, None]] = None,
                refinerefdate: Optional[Union[any, None]] = None,
                mastertiming: Optional[Union[any, None]] = None,
                oversample: Optional[Union[any, None]] = None,
                coarseoffset: Optional[Union[any, None]] = None,
                filtazi: Optional[Union[any, None]] = None,
                finecoreg: Optional[Union[any, None]] = None,
                reltiming: Optional[Union[any, None]] = None,
                demassist: Optional[Union[any, None]] = None, 
                coregpm: Optional[Union[any, None]] = None, 
                resample: Optional[Union[any, None]] = None, 
                finalstack: Optional[Union[any, None]] = None,
                cleanstack: Optional[Union[any, None]] = None,
                updatestack: Optional[Union[any, None]] = None,

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
                        nisarwavelength (str): NISAR wavelenght. [Default: ``L``]
                        relorbit (int): Relative orbit number. [Default: `None`]
                        satpass (str): Satellite direction. [Default: `None`]
                        email (dict): Dictionary of the emal parameters
                        computercores (int): Number of threads. [Default: ``0``]
                        computerworkers (int): Number of workers. [Default: ``1``]
                        computerRAM (int): RAM used by Doris. [Default: ``25%``]
                        processor (str): Processor. Here Doris. 
                        modeforce (bool): Forcing mode. [Default: `True`]
                        modecropping (str): Mode of the cropping. [Default: ``auto``]
                        mlazi (int): Multilook factor in azimuth
                        mlran (int): Multilook factor in range 
                        mlazidisplay (int): Multilook factor in azimuth for displaying
                        mlrandisplay (int): Multilook factor in range for displaying
                        checkSLC (dict): EZ-InSAR parameter dictionary
                        checkOrbit (dict): EZ-InSAR parameter dictionary
                        coarserefdate (dict): EZ-InSAR parameter dictionary
                        extractimage (dict): EZ-InSAR parameter dictionary
                        refinerefdate (dict): EZ-InSAR parameter dictionary
                        mastertiming (dict): EZ-InSAR parameter dictionary
                        oversample (dict): EZ-InSAR parameter dictionary
                        coarseoffset (dict): EZ-InSAR parameter dictionary
                        filtazi (dict): EZ-InSAR parameter dictionary
                        finecoreg (dict): EZ-InSAR parameter dictionary
                        reltiming (dict): EZ-InSAR parameter dictionary
                        demassist (dict): EZ-InSAR parameter dictionary
                        coregpm (dict): EZ-InSAR parameter dictionary
                        resample (dict): EZ-InSAR parameter dictionary
                        finalstack (dict): EZ-InSAR parameter dictionary
                        cleanstack (dict): EZ-InSAR parameter dictionary
                        updatestack (dict): EZ-InSAR parameter dictionary
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
                        self.pathstack = job.workdirectory+os.sep+'input_files'
                        
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
                self.computerworkers = computerworkers
                self.computerRAM = computerRAM
                self.processor = 'doris'
                self.modecropping = modecropping
                self.modeforce = modeforce
                self.nisarwavelength = nisarwavelength

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
                if checkSLC == None:
                        self.checkSLC = dict()
                        self.checkSLC['name'] = {'value': 'Step 1: Check the SLC files', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.checkSLC['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.checkSLC = checkSLC

                # For the Step 2: Check the orbit files
                if checkOrbit == None:
                        self.checkOrbit = dict()
                        self.checkOrbit['name'] = {'value': 'Step 2: Check the orbit files', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.checkOrbit['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.checkOrbit = checkOrbit

                # For the Step 3: Detect the coarse reference date
                if coarserefdate == None:
                        self.coarserefdate = dict()
                        self.coarserefdate['name'] = {'value': 'Step 3: Detect the coarse reference date', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.coarserefdate['useorbit'] = {'value': False, 
                                                'description': 'Use of the orbit file to compute the best potential reference date.', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.coarserefdate['useDEM'] = {'value': True, 
                                                'description': 'Use the DEM to estimate the distance between the satellite and the ground.', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.coarserefdate['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.coarserefdate = coarserefdate

                # For the Step 4: Extraction of the images
                if extractimage == None:
                        self.extractimage = dict()
                        self.extractimage['name'] = {'value': 'Step 4: Extraction of the images', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.extractimage['calibration'] = {'value': None, 
                                                'description': 'Calibration mode', 
                                                'format': 'list',
                                                'valuelist': [None, 
                                                              'beta0',
                                                              'beta0+noise',
                                                              'sigma0',
                                                              'sigma0+noise',
                                                              'dn',
                                                              'dn+noise',
                                                              'gamma',
                                                              'gamma+noise'] 
                                                }
                        self.extractimage['applyorbit'] = {'value': False, 
                                                'description': 'Apply the orbit found inside the orbit files', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.extractimage['cropping'] = {'value': False, 
                                                'description': 'Cropping (is bypassed by the cropping mode)', 
                                                'format': 'bool',
                                                'valuelist': None}
                        if (not self.satmode == 'IW') and (not self.modecropping == None): 
                                self.extractimage['cropping']['value'] = True
                        
                        self.extractimage['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.extractimage = extractimage

                # For the Step 5: Refine the reference date
                if refinerefdate == None:
                        self.refinerefdate = dict()
                        self.refinerefdate['name'] = {'value': 'Step 5: Refine the reference date', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.refinerefdate['process'] = {'value': False, 
                                                'description': 'Enable the processing step', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.refinerefdate['bypassuser'] = {'value': False, 
                                                'description': 'Bypass interactive user input', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.refinerefdate['done'] = {'value': False, 
                                                'description': 'Processing done', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.refinerefdate = refinerefdate
                
                # For the Step 6: Compute the master timing
                if mastertiming == None:
                        self.mastertiming = dict()
                        self.mastertiming['name'] = {'value': 'Step 6: Compute the master timing', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.mastertiming['process'] = {'value': False, 
                                                'description': 'Enable the processing', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.mastertiming['MTE_METHOD'] = {'value': 'magfft', 
                                                'description': 'Correlation method', 
                                                'format': 'list',
                                                'valuelist': ['magspace','magfft']}
                        self.mastertiming['MTE_ACC_1'] = {'value': 128, 
                                                'description': 'Accuracy first value. (only for magspace)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.mastertiming['MTE_ACC_2'] = {'value': 32, 
                                                'description': 'Accuracy second value. (only for magspace)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.mastertiming['MTE_NWIN'] = {'value': 30, 
                                                'description': 'Number of correlation windows', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.mastertiming['MTE_INITOFF_1'] = {'value': 0, 
                                                'description': 'Initial offset 1', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.mastertiming['MTE_INITOFF_2'] = {'value': 0, 
                                                'description': 'Initial offset 2', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.mastertiming['MTE_WINSIZE_1'] = {'value': 1024, 
                                                'description': 'Correlation window size 1', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.mastertiming['MTE_WINSIZE_2'] = {'value': 512, 
                                                'description': 'Correlation window size 2', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.mastertiming['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.mastertiming = mastertiming

                # For the Step 7: Oversample the SLCs
                if oversample == None:
                        self.oversample = dict()
                        self.oversample['name'] = {'value': 'Step 7: Oversample the SLCs', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.oversample['process'] = {'value': False, 
                                                'description': 'Enable the processing', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.oversample['OVS_FACT_RNG'] = {'value': 2, 
                                                'description': 'Oversampling factor in range', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.oversample['OVS_FACT_AZI'] = {'value': 2, 
                                                'description': 'Oversampling factor in azimuth', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.oversample['OVS_KERNELSIZE'] = {'value': 16, 
                                                'description': 'Oversampling kernel size', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.oversample['OVS_OUT_FORMAT'] = {'value': 'ci2', 
                                                'description': 'Format of the ouput file', 
                                                'format': 'list',
                                                'valuelist': ['ci2','cr4']}
                        self.oversample['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.oversample = oversample

                # For the Step 8: Compute the coarse offsets
                if coarseoffset == None:
                        self.coarseoffset = dict()
                        self.coarseoffset['name'] = {'value': 'Step 8: Compute the coarse offsets', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.coarseoffset['useorbit'] = {'value': True, 
                                                'description': 'Use the orbit to define the initial offset', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.coarseoffset['CC_METHOD'] = {'value': 'magfft', 
                                                'description': 'Correlation method', 
                                                'format': 'list',
                                                'valuelist': ['magfft','magspace']}
                        self.coarseoffset['CC_NWIN'] = {'value': 21, 
                                                'description': 'Number of correlation windows', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.coarseoffset['CC_WINSIZE_1'] = {'value': 1024, 
                                                'description': 'Correlation window size 1', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.coarseoffset['CC_WINSIZE_2'] = {'value': 256, 
                                                'description': 'Correlation window size 2', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.coarseoffset['CC_ACC_1'] = {'value': 30, 
                                                'description': 'Correlation accuracy 1 (only for magspace)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.coarseoffset['CC_ACC_2'] = {'value': 30, 
                                                'description': 'Correlation accuracy 2 (only for magspace)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.coarseoffset['CC_INITOFF_1'] = {'value': 0, 
                                                'description': 'Initial offset 1 if orbits are not used', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.coarseoffset['CC_INITOFF_2'] = {'value': 0, 
                                                'description': 'Initial offset 2 if orbits are not used', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.coarseoffset['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.coarseoffset = coarseoffset

                # For the Step 9: Fine coregistration
                if finecoreg == None:
                        self.finecoreg = dict()
                        self.finecoreg['name'] = {'value': 'Step 9: Fine coregistration', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.finecoreg['FC_METHOD'] = {'value': 'oversample', 
                                                'description': 'Correlation method', 
                                                'format': 'list',
                                                'valuelist': ['oversample','magfft','magspace']}
                        self.finecoreg['FC_NWIN'] = {'value': 2000, 
                                                'description': 'Number of correlation windows', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.finecoreg['FC_WINSIZE_1'] = {'value': 64, 
                                                'description': 'Correlation window size 1', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.finecoreg['FC_WINSIZE_2'] = {'value': 64, 
                                                'description': 'Correlation window size 2', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.finecoreg['FC_ACC_1'] = {'value': 8, 
                                                'description': 'Correlation accuracy 1 (only for magspace)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.finecoreg['FC_ACC_2'] = {'value': 8, 
                                                'description': 'Correlation accuracy 2 (only for magspace)', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.finecoreg['usecoarseoff'] = {'value': True, 
                                                'description': 'Use of the offsets computed by the coarse correlation', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.finecoreg['FC_INITOFF_1'] = {'value': 0, 
                                                'description': 'Initial offset 1 if the results from the coarse correlation are not used', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.finecoreg['FC_INITOFF_2'] = {'value': 0, 
                                                'description': 'Initial offset 1 if the results from the coarse correlation are not used', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.finecoreg['FC_OSFACTOR'] = {'value': 32, 
                                                'description': 'Oversampling factor', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.finecoreg['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.finecoreg = finecoreg
                        
                # For the Step 10: Compute the timing for the slaves
                if reltiming == None:
                        self.reltiming = dict()
                        self.reltiming['name'] = {'value': 'Step 10: Compute the timing for the slaves', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.reltiming['process'] = {'value': False, 
                                                'description': 'Enable the processing', 
                                                'format': 'bool',
                                                'valuelist': None}

                        self.reltiming['RTE_THRESHOLD'] = {'value': 0.4, 
                                                'description': 'Threshold value', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.reltiming['RTE_MAXITER'] = {'value': 1000, 
                                                'description': 'Max number of iterations', 
                                                'format': 'int',
                                                'valuelist': None}
                        self.reltiming['RTE_K_ALPHA'] = {'value': 1.97, 
                                                'description': 'K alpha valye', 
                                                'format': 'float',
                                                'valuelist': None}   
                        self.reltiming['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.reltiming = reltiming

                # For the Step 11: Refine the offsets using the DEM
                if demassist == None:
                        self.demassist = dict()
                        self.demassist['name'] = {'value': 'Step 11: Refine the offsets using the DEM', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.demassist['process'] = {'value': False, 
                                                'description': 'Enable the processing', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.demassist['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.demassist = demassist

                # For the Step 12: Compute the offset model
                if coregpm == None:
                        self.coregpm = dict()
                        self.coregpm['name'] = {'value': 'Step 12: Compute the offset model', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.coregpm['CPM_THRESHOLD'] = {'value': 0.4, 
                                                'description': 'Threshold of valid offsets', 
                                                'format': 'float',
                                                'valuelist': None}
                        self.coregpm['CPM_DEGREE'] = {'value': 2, 
                                                'description': 'Degre of the model', 
                                                'format': 'int',
                                                'valuelist': None}
                        # self.coregpm['CPM_DUMP'] = {'value': 'OFF', 
                        #                         'description': 'to do', 
                        #                         'format': 'list',
                        #                         'valuelist': ['OFF','ON']}
                        self.coregpm['CPM_WEIGHT'] = {'value': 'quadratic', 
                                                'description': 'Model of the model weight', 
                                                'format': 'list',
                                                'valuelist': ['quadratic','linear','bamler','none']}
                        self.coregpm['CPM_MAXITER'] = {'value': 8000, 
                                                'description': 'Max numer of iterations', 
                                                'format': 'int',
                                                'valuelist': None}
                        # self.coregpm['CPM_K ALPHA'] = {'value': 1.97, 
                        #                         'description': 'to do', 
                        #                         'format': 'float',
                        #                         'valuelist': None}
                        self.coregpm['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.coregpm = coregpm

                # For the Step 13: Resample the slaves
                if resample == None:
                        self.resample = dict()
                        self.resample['name'] = {'value': 'Step 13: Resample the slaves', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.resample['RS_METHOD'] = {'value': 'rc12p', 
                                                'description': 'Resampling algorithm', 
                                                'format': 'list',
                                                'valuelist': ['cc4p','cc6p','ts6p','ts8p','ts16p','cc6p_SP','rc6p','rc12p','rect','tri','knab6','knab8','knab10','knab16']}
                        self.resample['RS_OUT_FORMAT'] = {'value': 'ci2', 
                                                'description': 'Format of the output image', 
                                                'format': 'list',
                                                'valuelist': ['cr4','ci2']}
                        self.resample['RS_SHIFTAZI'] = {'value': 'ON', 
                                                'description': 'Shifting the doppler in azimuth', 
                                                'format': 'list',
                                                'valuelist': ['ON','OFF']}
                        
                        # self.resample['RS_DBOW'] = {'value': None, 
                        #                         'description': 'to do', 
                        #                         'format': 'None',
                        #                         'valuelist': None}
                        # self.resample['RS_DBOW GEO'] = {'value': None, 
                        #                         'description': 'to do', 
                        #                         'format': 'None',
                        #                         'valuelist': None}

                        self.resample['done'] = {'value': False, 
                                                'description': 'Procesisng completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.resample = resample

                # For the Step 14: Finalise the stack
                if finalstack == None:
                        self.finalstack = dict()
                        self.finalstack['name'] = {'value': 'Step 14: Finalise the stack', 
                                                'description': 'Name of the processing', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.finalstack['done'] = {'value': False, 
                                                'description': 'Processing completeds', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.finalstack = finalstack

                # For the Step 15: Clean the stack
                if cleanstack == None:
                        self.cleanstack = dict()
                        self.cleanstack['name'] = {'value': 'Step 15: Clean the stack', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}
                        self.cleanstack['mode'] = {'value': 'update', 
                                                'description': 'Mode of the cleaning', 
                                                'format': 'list',
                                                'valuelist': [False, 'all','update']}
                        self.cleanstack['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.cleanstack = cleanstack

                # For the Step 16: Update the stack
                if updatestack == None:
                        self.updatestack = dict()
                        self.updatestack['name'] = {'value': 'Step 16: Update the stack', 
                                                'description': 'Name of the processing step', 
                                                'format': 'str',
                                                'valuelist': None}

                        self.updatestack['update_ref'] = {'value': False, 
                                                'description': 'Update the reference date. VERY DANGEROUS OPTION', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.updatestack['bypass_POD'] = {'value': False, 
                                                'description': 'If False, only the dates with precise orbits will be updated (for Sentinel-1)', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.updatestack['force'] = {'value': False, 
                                                'description': 'Forcing mode', 
                                                'format': 'bool',
                                                'valuelist': None}
                        self.updatestack['done'] = {'value': False, 
                                                'description': 'Processing completed', 
                                                'format': 'bool',
                                                'valuelist': None}
                else:
                        self.updatestack = updatestack

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
                """Print the coregistration-processing attributes of the EZ-InSAR class

                Returns:
                        ``ezinsar.job``: Return the ``ezinsar.job`` used
                """

                attrs = vars(self)
                print(', '.join("%s: %s" % item for item in attrs.items()))

                return self

        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def check(self,**kwargs):
                """Check and display the coregistration-processing attributes of the EZ-InSAR class

                Args:
                        ``kwargs``: Arbitrary keyword arguments.

                Returns:
                        ``ezinsar.job``: Return the ``ezinsar.job`` used
                """

                self = jobproctools.check(self,**kwargs)

                return self
        
        ################################################################################
        ## Run the coregistration
        ################################################################################
        def run(self,**kwargs):
                """Run the coregsitration using Doris processor

                Args:
                        ``kwargs``: Arbitrary keyword arguments.

                Returns:
                        ``ezinsar.job``: Return the ``ezinsar.job`` used
                """

                self = jobrun.run(self,**kwargs)

                return self

        ################################################################################
        ## Delete a date within the coregistration stack
        ################################################################################
        def deletedate(self,**kwargs):
                """Delete a date within the coregistration stack

                Args:
                        ``kwargs``: Arbitrary keyword arguments.

                Returns:
                        ``ezinsar.job``: Return the ``ezinsar.job`` used
                """

                self = doristools.deletedate(self,**kwargs)
                
                return self
                
                
        