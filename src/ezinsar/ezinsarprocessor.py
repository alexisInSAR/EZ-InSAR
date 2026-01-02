#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
**EZ-InSAR** module to create and control an **EZ-InSAR** job. 

The module contains the different methods, and low-level functions to run EZ-InSAR (`EIjob`). 

        (From `ezinsar` package)

Example:
        In a Python terminal, the `EIjob` can be created by using the 
        following commands::

                >>> # Import the EZ-InSAR package
                >>> import ezinsar.job as ez
                >>> # Create the job by defining the polarisation and the satellite mode
                >>> job = ez.EIjob(verbose=True,satellite='S1',polarisation=['VV','VH'],satmode='IW')
                >>> # Check the class attributes with the verbose False
                >>> job.check(verbose=False)

Changelog:
        * 3.3.1: Several changes, Dec. 2025, Alexis Hrysiewicz
                * Check the check method (if EIjob in string)
                * Delete the link to the EZ-InSAR GAMMA module
        * 3.2.2: Delele the support of wget, Sep. 2025, Alexis Hrysiewicz
        * 3.2.1: Add the ETAD download for Sentinel-1, Aug. 2025, Alexis Hrysiewicz
        * 3.2.0: Several changes, Jun. 2025, Alexis Hrysiewicz
                * Add the GAMMA tsprocessing
                * Add the MiaplPy tsprocessing
                * Add the Sarvey tsprocessing
                * Add a method for changing paths
                * Add the new method for DEM
        * 3.1.0: Several changes, Feb. 2025, Alexis Hrysiewicz
                * Add the offset-tracking processing
                * Fixes in load function (satellite key is required)
                * New method: unzipSLC
                * Remove the dicttoxml package for license compliance
        * 3.0.1: Bug fixes, Jan. 2025, Alexis Hrysiewicz 
        * 3.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
from datetime import datetime
import platform
import os
import xmltodict
from xml.dom.minidom import parseString
from shapely.wkt import loads
import pandas as pd
import copy
from typing import Optional, Union
import logging 
import shutil
import pylatex
import pylatex.utils
import numpy as np
import glob
from PIL import Image
from zipfile import ZipFile
import tarfile
import requests
import time

################################################################################
## Change the logging mode of dicttoxml
################################################################################
logging.getLogger('dicttoxml').setLevel(logging.WARNING)

################################################################################
## Import the EZ-InSAR package
################################################################################
# Import the common EZ-InSAR packages
from ezinsar.eicomponents.jobmodule import jobtools
from ezinsar.eicomponents.roimodule import roitools
from ezinsar.eicomponents.demmodule import demtools, demwrapper
from ezinsar.eicomponents.slcmodule import slctools 
from ezinsar import constants
__copyright__ = constants.__copyright__
from ezinsar import usermessage
from ezinsar.tools import miscellaneous

# Import the EZ-InSAR package for ISCE-2
from ezinsar.eicomponents.processor.isce2module import isce2coregistration
from ezinsar.eicomponents.processor.isce2module import isce2ifgstack

# Import the EZ-InSAR package for SNAP
from ezinsar.eicomponents.processor.snapmodule import snapcoregistration
from ezinsar.eicomponents.processor.snapmodule import snapifgstack
from ezinsar.eicomponents.processor.snapmodule import snapintstack

# Import the EZ-InSAR package for Doris
from ezinsar.eicomponents.processor.dorismodule import doriscoregistration
from ezinsar.eicomponents.processor.dorismodule import dorisifgstack

# Import the EZ-InSAR package for MintPy
from ezinsar.eicomponents.processor.mintpymodule import mintpytsprocessing

# Import the EZ-InSAR package for MiaplPy
from ezinsar.eicomponents.processor.miaplpymodule import miaplpytsprocessing

# Import the EZ-InSAR package for SARvey
from ezinsar.eicomponents.processor.sarveymodule import sarveytsprocessing

# Import the EZ-InSAR package for StaMPS
from ezinsar.eicomponents.processor.stampsmodule import stampstsprocessing

# Inport the EZ-InSAR package for LiCSBAS
from ezinsar.eicomponents.processor.licsbasmodule import licsbastsprocessing

################################################################################
## Class to manage the EZ-InSAR job
################################################################################
class EIjob:
        """EZ-InSAR job (`EIjob`) class.

        Attributes:
                user (str): Name/Definition of the user [Default: `None`]
                computer (str): Computer type. Automatically generated
                token (str): Token of the job [Default: `None`]
                nameJob (str): Name of the job [Default: Job for EZ-InSAR]
                workdirectory (str): Path of the work directory [Default: `None`]
                pathSLC (str): Path of the SLC directory [Default: `None`]
                pathorbit (str): Path of the orbit directory [Default: `None`]
                pathaux (str): Path of the aux.-file directory [Default: `None`]
                pathDEM (str): Path of the DEM directory [Default: `None`]
                nameDEM (str): Name of the DEM file [Default: `None`]
                typeDEM (str): Type of the DEM [Default: `None`]. See `demmodule.demtools` for more information.
                date1 (any): First date for the SLC checking in `datetime` format [Default: ``datetime.strptime('2015-01-01T00:00:00.000100Z','%Y-%m-%dT%H:%M:%S.%fZ')``]. This value is only used to check the SLCs from the Sentinel-1 servers. 
                date2 (any): Last date for the SLC checking in `datetime` format [Default: `datetime.now()`]. This value is only used to check the SLCs from the Sentinel-1 servers.
                roi (any): ROI of the job [Default: `None`]. This value must be a Polygon variable. See `roimodule.roitools` for more information.
                satellite (str): Used satellite [Default: ``S1``]. Can be ``S1``, ``ALOS``, ``ALOS2``, ``RST``, ``TSX``, ``PAZ`` or ``CSK``. 
                satmode (str): Used acquisition mode [Default: ``IW``]. Can be ``ScanSAR``, ``SM``, ``SPT``, ``ScanSAR``, ``SM``, ``SPT``, ``SM``, ``ScanSAR``, ``SM``, ``SPT``, ``HSSPT``, ``ST``, ``ScanSAR``, ``SM``, ``SPT``, ``HSSPT``, ``ST``, ``HI`` or ``SPT``. 
                relorbit (int): Relative orbit [Default: `None`]. 
                polarisation (list of str): Polarisation [Default: ``VV``]. Can be a list of string: i.e., ``['VV','VH']`` or a string as ``'VV,VH'``. 
                satpass (str): Satellite direction [Default: `None`]. Can be ``ASCENDING`` or ``DESCENDING``
                SLClist (any): List of the SLCs [Default: `None`]
                verbose (bool): Verbose [Default: `True`]
                gui (bool): GUI mode [Default: `False`].
                log (bool): Logging [Default: Fa`lse].
                coregistration (``EZ-InSAR class for coregistration``): Coregistration job [Default: `None`].
                intstack (``EZ-InSAR class for intensity computation``): Int stack job [Default: `None`].
                ifgstack (``EZ-InSAR class for interferometric computation``): Ifg stack job [Default: `None`].
                tsprocessing (``EZ-InSAR class for Time-Series-Analysis computation``): TS job [Default: `None`].
                offsetprocessing (``EZ-InSAR class for Offset-Tracking-Analysis computation``): TS job [Default: `None`].

        """

        ################################################################################
        ## Initialistion of the class
        ################################################################################
        def __init__(self,
                        user: Optional[Union[str, None]] = None,
                        token: Optional[Union[str, None]] = None,
                        nameJob: Optional[Union[str, None]] = 'Job for EZ-InSAR', 
                        workdirectory: Optional[Union[str, None]] = None,
                        pathSLC: Optional[Union[str, None]] = None,
                        pathorbit: Optional[Union[str, None]] = None,
                        pathaux: Optional[Union[str, None]] = None,
                        pathDEM: Optional[Union[str, None]] = None, 
                        nameDEM: Optional[Union[str, None]] = None,
                        typeDEM: Optional[Union[str, None]] = None,
                        date1: Optional[datetime.date] = datetime.strptime('2015-01-01T00:00:00.000100Z','%Y-%m-%dT%H:%M:%S.%fZ'), 
                        date2: Optional[datetime.date] = datetime.now(), 
                        roi: Optional[Union[any, None]] = None,
                        satellite: Optional[str] = 'S1',
                        satmode: Optional[str] = 'IW',
                        relorbit: Optional[Union[int, None]] = None,
                        polarisation: Optional[Union[str, list]] = 'VV',
                        satpass: Optional[Union[str, None]] = None,
                        SLClist: Optional[Union[str, None]] = None,
                        verbose: Optional[bool] = True,
                        gui: Optional[bool] = False,
                        log: Optional[Union[str, None]] = None,
                        coregistration: Optional[Union[any, None]] = None, 
                        intstack: Optional[Union[any, None]] = None, 
                        ifgstack: Optional[Union[any, None]] = None, 
                        tsprocessing: Optional[Union[any, None]] = None,
                        offsetprocessing: Optional[Union[any, None]] = None):

                """Initialisation of the `EIjob` class  

                Args: 
                        user (str): Name/Definition of the user [Default: `None`]
                        token (str): Token of the job [Default: `None`]
                        nameJob (str): Name of the job [Default: Job for EZ-InSAR]
                        workdirectory (str): Path of the work directory [Default: `None`]
                        pathSLC (str): Path of the SLC directory [Default: `None`]
                        pathorbit (str): Path of the orbit directory [Default: `None`]
                        pathaux (str): Path of the aux.-file directory [Default: `None`]
                        pathDEM (str): Path of the DEM directory [Default: `None`]
                        nameDEM (str): Name of the DEM file [Default: `None`]
                        typeDEM (str): Type of the DEM [Default: `None`]. See `demmodule.demtools` for more information.
                        date1 (any): First date for the SLC checking in `datetime` format [Default: ``datetime.strptime('2015-01-01T00:00:00.000100Z','%Y-%m-%dT%H:%M:%S.%fZ')``]. This value is only used to check the SLCs from the Sentinel-1 servers. 
                        date2 (any): Last date for the SLC checking in `datetime` format [Default: `datetime.now()`]. This value is only used to check the SLCs from the Sentinel-1 servers.
                        roi (any): ROI of the job [Default: `None`]. This value must be a Polygon variable. See `roimodule.roitools` for more information.
                        satellite (str): Used satellite [Default: ``S1``]. Can be ``S1``, ``ALOS``, ``ALOS2``, ``RST``, ``TSX``, ``PAZ`` or ``CSK``. 
                        satmode (str): Used acquisition mode [Default: ``IW``]. Can be ``ScanSAR``, ``SM``, ``SPT``, ``ScanSAR``, ``SM``, ``SPT``, ``SM``, ``ScanSAR``, ``SM``, ``SPT``, ``HSSPT``, ``ST``, ``ScanSAR``, ``SM``, ``SPT``, ``HSSPT``, ``ST``, ``HI`` or ``SPT``. 
                        relorbit (int): Relative orbit [Default: `None`]. 
                        polarisation (list of str): Polarisation [Default: ``VV``]. Can be a list of string: i.e., ``['VV','VH']`` or a string as ``'VV,VH'``. 
                        satpass (str): Satellite direction [Default: `None`]. Can be ``ASCENDING`` or ``DESCENDING``
                        SLClist (any): List of the SLCs [Default: `None`]
                        verbose (bool): Verbose [Default: `True`]
                        gui (bool): GUI mode [Default: `False`].
                        log (bool): Logging [Default: Fa`lse].
                        coregistration (``EZ-InSAR class for coregistration``): Coregistration job [Default: `None`].
                        intstack (``EZ-InSAR class for intensity computation``): Int stack job [Default: `None`].
                        ifgstack (``EZ-InSAR class for interferometric computation``): Ifg stack job [Default: `None`].
                        tsprocessing (``EZ-InSAR class for Time-Series-Anylaysis computation``): TS job [Default: `None`].
                        offsetprocessing (``EZ-InSAR class for Offset-Tracking-Analysis computation``): TS job [Default: `None`].

                """

                # User information
                self.user = user
                self.computer = platform.system()
                self.token = token

                # Name of the job
                self.nameJob = nameJob

                # Path information
                self.workdirectory = workdirectory
                self.pathSLC = pathSLC
                self.pathorbit = pathorbit
                self.pathaux = pathaux

                # DEM information 
                self.pathDEM = pathDEM
                self.nameDEM = nameDEM
                self.typeDEM = typeDEM

                # Temporal information
                self.date1 = date1
                self.date2 = date2

                # Spatial information
                self.roi = roi

                # Satellite information
                self.satellite = satellite
                self.satmode = satmode
                self.relorbit = relorbit
                self.polarisation = polarisation
                self.satpass = satpass
                self.SLClist = SLClist

                # Integration information
                self.verbose = verbose
                self.gui = gui
                self.log = log

                # Processing
                self.coregistration = coregistration
                self.intstack = intstack
                self.ifgstack = ifgstack
                self.tsprocessing = tsprocessing
                self.offsetprocessing = offsetprocessing

                # Logging
                if not self.log == None: 
                        logging.basicConfig(filename=self.log, filemode='w', 
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                        logger=logging.getLogger() 
                        logger.setLevel(usermessage.definelevel(constants.__loggingmode__)) 
                        logger.info('Creation of a EZ-InSAR job')

                # Checking (required if init by the user)
                self.check(verbose=False)

        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def print(self):
                """Print the attributes of an `EIjob` class

                The method display a unstructured text of the job attributes.

                Returns:

                        `EIjob`: Return the `EIjob` used

                """
                attrs = vars(self)
                print(', '.join("%s: %s" % item for item in attrs.items()))

                return self
        
        ################################################################################
        ## Method to check the attributes
        ################################################################################
        def check(self,**kwargs):
                """Check and display the attributes of an `EIjob` class

                The method checks and displays (if verbose is True) the job attributes. 

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `jobmodule.jobtools.check` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = jobtools.check(self,**kwargs)

                return self

        ################################################################################
        ## ROI management
        ################################################################################
        def importroi(self,**kwargs):
                """Import the ROI into an `EIjob` class

                The method imports the ROI. 

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `roimodule.roitools.importroi` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = roitools.importroi(self,**kwargs)

                return self

        def displayroi(self,**kwargs):
                """Display the ROI of an `EIjob` class

                The method displays the ROI (via a figure).

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `roimodule.roitools.display` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = roitools.display(self,**kwargs)

                return self

        ################################################################################
        ## Job management
        ################################################################################
        def mkdir(self,**kwargs):
                """Create the required directories for an `EIjob` class

                The method creates the required directories (i.e., directories of SLCs, orbit files, ...).

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `jobmodule.jobtools.mkdir` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = jobtools.mkdir(self,**kwargs)

                return self
        
        def changedir(self,newroot,verbose=None,log=None):
                """Change the required directories for an `EIjob` class

                The method changes the required directories (i.e., directories of SLCs, orbit files, ...).

                Args:
                        newroot: New path of the root 

                Returns:
                        `EIjob`: Return the new `EIjob`
                
                """

                if verbose == None:
                        verbose = self.verbose
                if log == None:
                        log = self.log

                self, _, _, _, _, _ = jobtools.changepath(self,newroot=newroot,locklog=True,verbose=verbose,log=log)
                
                if not self.coregistration == None:
                       self.coregistration, _, _, _, _, _ = jobtools.changepath(self.coregistration,newroot=newroot,locklog=True,verbose=verbose,log=log)
                 
                if not self.ifgstack == None:
                       self.ifgstack, _, _, _, _, _ = jobtools.changepath(self.ifgstack,newroot=newroot,locklog=True,verbose=verbose,log=log)
                 
                if not self.tsprocessing == None:
                        self.tsprocessing, _, _, _, _, _ = jobtools.changepath(self.tsprocessing,newroot=newroot,locklog=True,verbose=verbose,log=log)
                
                if not self.intstack == None:
                        self.intstack, _, _, _, _, _ = jobtools.changepath(self.intstack,newroot=newroot,locklog=True,verbose=verbose,log=log)
                
                if not self.offsetprocessing == None:
                        self.offsetprocessing, _, _, _, _, _ = jobtools.changepath(self.offsetprocessing,newroot=newroot,locklog=True,verbose=verbose,log=log)
                 
                return self 
        
        ################################################################################
        ## SLC management
        ################################################################################
        def unzipSLC(self,**kwargs):
                """Unzip the SLC files for an `EIjob` class

                The method unzippes the SLC list.

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `slctools.unzipSLC` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = slctools.unzipSLC(self,**kwargs)

                return self

        def initiateSLC(self,**kwargs):
                """Create the SLC list for an `EIjob` class

                The method creates the SLC list.

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `slctools.initiateSLC` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = slctools.initiateSLC(self,**kwargs)

                return self
        
        def printSLClist(self,**kwargs):
                """Print the SLC list of an `EIjob` class

                The method prints the SLC list.

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `slctools.printSLClist` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """

                self = slctools.printSLClist(self,**kwargs)

                return self

        def saveSLClist(self,**kwargs):
                """Save the SLC list of an `EIjob` class into a .csv file

                The method saves the SLC list.

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `slctools.saveSLClist` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = slctools.saveSLClist(self,**kwargs)

                return self

        def checkSLClist(self,**kwargs):
                """Check the SLC list of an `EIjob` class

                The method checks the SLC list.

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `slctools.checkSLClist` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = slctools.checkSLClist(self,**kwargs)

                return self

        def displaySLClist(self,**kwargs):
                """Display the SLC list of an `EIjob` class

                The method displays the SLC list via a figure.

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `slctools.displaySLClist` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = slctools.displaySLClist(self,**kwargs)

                return self

        def writeSLClisttokmz(self,**kwargs):
                """Write the SLC list of an `EIjob` class in .kmz format

                The method generates a .kmz files regarding the SLC list. 

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `slctools.writeSLClisttokmz` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = slctools.writeSLClisttokmz(self,**kwargs)

                return self

        def downloadSLC(self,**kwargs):
                """Download the SLC of an `EIjob` class

                The method downloads the SLCs regarding the SLC list. 

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `slctools.downloadSLC` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = slctools.downloadSLC(self,**kwargs)

                return self

        def downloadorbit(self,**kwargs):
                """Download the orbits of an `EIjob` class

                The method downloads the orbits regarding the SLC list. 

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `slctools.downloadorbit` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = slctools.downloadorbit(self,**kwargs)

                return self
        
        def downloadETAD(self,**kwargs):
                """Download the ETAD file for Sentinel-1 of an `EIjob` class

                The method downloads the ETAD file for Sentinel-1 regarding the SLC list. 

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `slctools.downloadorbit` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = slctools.downloadETAD(self,**kwargs)

                return self
        
        ################################################################################
        ## DEM management 
        ################################################################################
        def downloaddem(self,**kwargs):
                """Download the DEM for an `EIjob` class

                The method downloads the DEM. 

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `demmodule.demtools.download` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                # self, _, _, _ = demtools.download(job=self,**kwargs)
                self, _, _, _ = demwrapper.run(job=self,**kwargs)

                return self
                
        def displaydem(self,**kwargs):
                """Display the DEM of an `EIjob` class

                The method display the DEM. 

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See `demmodule.demtools.display` for more information. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = demtools.display(job=self,**kwargs)

                return self
        
        ################################################################################
        ## Coregistration 
        ################################################################################
        def initiatecoreg(self,**kwargs):
                """Initialise the coregistration class for an `EIjob` class

                The method initialise the coregistration class (with parameters) for an `EIjob`. 

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See the corresponding functions.

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                if 'processor' in kwargs: 
                                if kwargs['processor'] in ['isce2','snap','doris']: #['doris','snap','isce2','isce3']:
                                        processor = kwargs['processor']
                                else: 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,'initiatecoreg',__file__,__copyright__,
                                                'processor','doris, snap, isce2 or isce3',self.log))
                else: 
                        processor = constants.__defautprocessor__

                # Initialisation
                if processor == 'isce2':
                        self.coregistration = None
                        self.coregistration = isce2coregistration.coregistration(job=self,**kwargs)
                elif processor == 'snap':
                        self.coregistration = None
                        self.coregistration = snapcoregistration.coregistration(job=self,**kwargs)
                elif processor == 'doris':
                        self.coregistration = None
                        self.coregistration = doriscoregistration.coregistration(job=self,**kwargs)

                return self
        
        def runcoreg(self,**kwargs):
                """Run the coregistration processing of an `EIjob` class

                The method runs the coregistration processing of an `EIjob`. 

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See the corresponding functions. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = self.coregistration.run(self,**kwargs)

                return self
        
        ################################################################################
        ## Intensity stack 
        ################################################################################
        def initiateint(self,**kwargs):
                """Initialise the intensity-stack class for an `EIjob` class

                The method initialise the interferometric-stack class (with parameters) for an `EIjob`. 

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See the corresponding functions.

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                if 'processor' in kwargs: 
                                if kwargs['processor'] in ['snap']:
                                        processor = kwargs['processor']
                                else: 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,'initiatecoreg',__file__,__copyright__,
                                                'processor','snap',self.log))
                else: 
                        processor = constants.__defautprocessor__

                # Initialisation
                if processor == 'snap':
                        self.intstack = None
                        self.intstack = snapintstack.intstack(job=self,**kwargs)

                return self
        
        def runint(self,**kwargs):
                """Run the intensity processing of an `EIjob` class

                The method runs the intensity processing from an `EIjob`. self  

                Args:
                        ``kwargs``: Arbitrary keyword arguments.  

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = self.intstack.run(self,**kwargs)

                return self

        ################################################################################
        ## Interferometric stack 
        ################################################################################
        def initiateifg(self,**kwargs):
                """Initialise the interferometric-stack class for an `EIjob` class

                The method initialise the interferometric-stack class (with parameters) for an `EIjob`. 

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See the corresponding functions.

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                if 'processor' in kwargs: 
                                if kwargs['processor'] in ['isce2','doris','snap']: #['doris','snap','isce2','isce3']:
                                        processor = kwargs['processor']
                                else: 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,'initiatecoreg',__file__,__copyright__,
                                                'processor','doris, snap, isce2',self.log))
                else: 
                        processor = constants.__defautprocessor__

                # Initialisation
                if processor == 'isce2':
                        self.ifgstack = None
                        self.ifgstack = isce2ifgstack.ifgstack(job=self.coregistration,**kwargs)
                elif processor == 'doris':
                        self.ifgstack = None
                        self.ifgstack = dorisifgstack.ifgstack(job=self.coregistration,**kwargs)
                elif processor == 'snap':
                        self.ifgstack = None
                        self.ifgstack = snapifgstack.ifgstack(job=self.coregistration,**kwargs)

                return self
        
        def runifg(self,**kwargs):
                """Run the interferometric processing of an `EIjob` class

                The method runs the interferometric processing of an `EIjob`. 

                Args:
                        ``kwargs``: Arbitrary keyword arguments. See the corresponding functions. 

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                self = self.ifgstack.run(self,**kwargs)

                return self

        ################################################################################
        ## Time series analysis processing
        ################################################################################
        def initiatets(self,**kwargs):
                """Initialise the time-series-analysis class for an `EIjob` class

                The method initialise the time-series-analysis class (with parameters) for an `EIjob`. 

                Args:
                        ``kwargs``: Arbitrary keyword arguments.

                Returns:
                        `EIjob`: Return the `EIjob` used
                
                """
                if 'processor' in kwargs: 
                                if kwargs['processor'] in ['mintpy','stamps','licsbas','miaplpy','sarvey']:
                                        processor = kwargs['processor']
                                else: 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,'initiatets',__file__,__copyright__,
                                                'processor','mintpy/stamps/licsbas/miaplpy/sarvey',self.log))
                else: 
                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,'initiatets',__file__,__copyright__,
                                                'processor','mintpy/stamps/licsbas/miaplpy/sarvey',self.log))
                
                if 'mode' in kwargs: 
                        if kwargs['mode'] in ['ps','sbas','merged']:
                                        mode = kwargs['mode']
                        else: 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,'initiatets',__file__,__copyright__,
                                        'mode','mintpy',self.log))
                else: 
                        mode = 'sbas'

                # Initialisation
                if processor == 'mintpy' and mode == 'sbas':
                        self.tsprocessing = None
                        self.tsprocessing = mintpytsprocessing.sbas(job=self.ifgstack,**kwargs)
                elif processor == 'miaplpy' and mode == 'ps':
                        self.tsprocessing = None
                        self.tsprocessing = miaplpytsprocessing.ps(job=self.coregistration,**kwargs)
                elif processor == 'sarvey' and mode == 'ps':
                        self.tsprocessing = None
                        self.tsprocessing = sarveytsprocessing.ps(job=self.coregistration,**kwargs)
                elif processor == 'stamps' and mode == 'ps':
                        self.tsprocessing = None
                        self.tsprocessing = stampstsprocessing.ps(job=self.ifgstack,**kwargs)
                elif processor == 'stamps' and mode == 'sbas':
                        self.tsprocessing = None
                        self.tsprocessing = stampstsprocessing.sbas(job=self.ifgstack,**kwargs)
                elif processor == 'stamps' and mode == 'merged':
                        self.tsprocessing = None
                        self.tsprocessing = stampstsprocessing.merged(job=self.ifgstack,**kwargs)
                elif processor == 'licsbas' and mode == 'sbas':
                        self.tsprocessing = None
                        self.tsprocessing = licsbastsprocessing.sbas(job=self,**kwargs)

                else:
                        raise ValueError(usermessage.errormsg(__name__,'initiatets',__file__,__copyright__,
                                'The couple processor/approach is not correct.',self.log))
        
                return self
                
################################################################################################################################################################
################################################################################################################################################################
## Functions low-levels
################################################################################################################################################################
################################################################################################################################################################

################################################################################
## Save the job into a file
################################################################################
def save(job, file, log: Optional[bool] = None, verbose: Optional[bool] = None): 
        """Save an EZ-InSAR job/processing into a .xml file format

        The function saves the EZ-InSAR job/processing into a .xml file format. 

        Example:
                In a Python terminal::

                        >>> import ezinsar.job as ez
                        >>> ez.save(job,'jobezinsar.ei',verbose=True)

        Args:
                job (``ezinsar.job``): EZ-InSAR job/processing class.
                file (str): Full path of the .xml files
                log (bool): log [Default: `None`]. If None, the function will use the value from the class. 
                verbose (bool): verbose [Default: `None`]. If None, the function will use the value from the class. 

        """
        if (not 'EIjob' in str(type(job))) and (not 'coregistration' in str(type(job))) and (not 'ifgstack' in str(type(job))) and (not 'mintpytsprocessing' in str(type(job))) and (not 'stampstsprocessing' in str(type(job))) and (not 'intstack' in str(type(job))) and (not 'licsbastsprocessing' in str(type(job)) and (not 'offsetprocessing' in str(type(job)))) and (not 'tsprocessing' in str(type(job))):
                try: 
                        raise ValueError(usermessage.errormsg(__name__,save.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR job/processing.',job.log))
                except:
                        raise ValueError(usermessage.errormsg(__name__,save.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR job/processing.',None))
        
        if log == None:
                log = job.log

        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,save.__name__,__file__,__copyright__,
                        'verbose','True or False',log,verbose))

        usermessage.openingmsg(__name__,save.__name__,__file__,__copyright__,'Save the EZ-InSAR job/processing into a file',log,verbose)

        # Copy the variable
        jobtosave = copy.deepcopy(job)

        # For a full job 
        if 'EIjob' in str(type(job)):
                usermessage.ezprint('Save an EZ-InSAR job...',log,verbose)

                # Some modifications 
                jobtosave.roi = str(jobtosave.roi)
                if isinstance(jobtosave.SLClist,pd.DataFrame):
                        jobtosave.SLClist = jobtosave.SLClist.to_dict(orient='records')

                if not jobtosave.coregistration == None:
                        jobtosave.coregistration = jobtosave.coregistration.__dict__

                if not jobtosave.intstack == None:
                        jobtosave.intstack = jobtosave.intstack.__dict__

                if not jobtosave.ifgstack == None:
                        jobtosave.ifgstack = jobtosave.ifgstack.__dict__

                if not jobtosave.tsprocessing == None:
                        jobtosave.tsprocessing = jobtosave.tsprocessing.__dict__

                if not jobtosave.offsetprocessing == None:
                        jobtosave.offsetprocessing = jobtosave.offsetprocessing.__dict__
                        
                miscellaneous.writexmlfromdict(jobtosave.__dict__,file.replace('.ei','')+'.ei',rootname='EZ-InSAR-Job',log=None)

        # For partial jobs 
        elif 'coregistration' in str(type(job)):
                usermessage.ezprint('Save an EZ-InSAR Coregistration processing...',log,verbose) 
                miscellaneous.writexmlfromdict(jobtosave.__dict__,file.replace('.ei','')+'.ei',rootname='EZ-InSAR-Coregistration',log=None)
        elif 'intstack' in str(type(job)):
                usermessage.ezprint('Save an EZ-InSAR Intensity stack processing...',log,verbose) 
                miscellaneous.writexmlfromdict(jobtosave.__dict__,file.replace('.ei','')+'.ei',rootname='EZ-InSAR-intstack',log=None)
        elif 'ifgstack' in str(type(job)):
                usermessage.ezprint('Save an EZ-InSAR InSAR stack processing...',log,verbose) 
                miscellaneous.writexmlfromdict(jobtosave.__dict__,file.replace('.ei','')+'.ei',rootname='EZ-InSAR-ifgstack',log=None)
        elif 'tsprocessing' in str(type(job)):
                usermessage.ezprint('Save an EZ-InSAR Time series Analysis processing...',log,verbose) 
                miscellaneous.writexmlfromdict(jobtosave.__dict__,file.replace('.ei','')+'.ei',rootname='EZ-InSAR-tsprocessing',log=None)
        elif 'offsetprocessing' in str(type(job)):
                usermessage.ezprint('Save an EZ-InSAR Offset-tracking Analysis processing...',log,verbose) 
                miscellaneous.writexmlfromdict(jobtosave.__dict__,file.replace('.ei','')+'.ei',rootname='EZ-InSAR-offsetprocessing',log=None)

        usermessage.ezprint('Job/processing saved in %s' % (file.replace('.ei','')+'.ei'),log,verbose)

################################################################################
## Function to extract the parameters
################################################################################
def extractparam(tmp,item):
        """Extract the parameters from a generated dict

        The function is linked to the `load` function. 

        Args:
                tmp (any): First input
                item (any): Second input

        Returns:
                any: Output
                
        """
        out = None
        if tmp['@type'] == 'null':
                out = None
        elif tmp['@type'] == 'str':
                out = tmp['#text']  
        elif tmp['@type'] == 'bool':
                if tmp['#text'] == 'true': 
                        out = True
                else:
                        out = False
        elif tmp['@type'] == 'int':
                out = int(tmp['#text'])
        elif tmp['@type'] == 'float':
                out = float(tmp['#text'])
        elif tmp['@type'] == 'list':
                out = []
                ######## Little change
                if not isinstance(tmp['item'],list):
                        tmp['item'] = [tmp['item']]
                ########        
                for keyi, itemi  in enumerate(tmp['item']):
                        out.append(extractparam(itemi,'null'))
        elif tmp['@type'] == 'dict':
                out = dict()
                for keyi, itemi  in enumerate(tmp.keys()):
                        if not itemi == '@type':
                                if not itemi in out:
                                        out[itemi] = []
                                out[itemi] = extractparam(tmp[itemi],'null')

        if item == 'SLClist' and (not out == None): 
                out = pd.DataFrame.from_records(out)

        return out

################################################################################
## Function to create compatibility between different versions of EZ-InSAR
################################################################################
def comparedict(input,readinput,log,verbose):
        """Compare the dict value, between the EZ-InSAR job file and the EZ-InSAR class, for EZ-InSAR compability 

        The function will compare the job-parameter dict provided by EZ-InSAR and provided by a file in order to have a compability. The goal is to affect the value from the user file to the class. 
        
        
        Note: 
                If the parameter is not defined by the user, default value will be used. If th
                If the parameter is not available in the EZ-InSAR class, a warning message will be displayed.  

        Args:
                input (any): Input parameter from the EZ-InSAR class
                readinput (any): Input parameter from the user file
                log (str): Log value. If `None`, no log will be used. 
                verbose (bool): Verbose value 
                
        """
        if isinstance(readinput,dict): 
                for ki in readinput.keys():
                        if ki in list(input.keys()):
                                input[ki]['value'] = readinput[ki]['value']
                        else: 
                                usermessage.warningmsg(__name__,load.__name__,__file__,'The parameter %s has been depreciated in the given parameter dictionary. Please see the changelog.' % (ki),log,verbose)
        else:
                input = readinput

        return input

################################################################################
## Load a job from a file
################################################################################
def load(file, verbose=True, modelog=True, bypasscheck=False): 
        """Load an EZ-InSAR job/processing from a .ei file

        The function loads the EZ-InSAR job/processing from a .ei file. 

        Example:
                In a Python terminal::

                        >>> import ezinsar.job as ez
                        >>> job = ez.load('jobezinsar.ei', verbose = False)

        Args:
                file (str): Full path of the .ei file
                verbose (bool): verbose [Default: `None`]. If None, the function will use the value from the class. 
                modelog (bool): log [Default: `True`]. 
                bypasscheck (bool): Bypass the verification of the job [Default: `False`]. 

        Returns:
                `EIjob`: Return an EZ-InSAR class

        To-do:
                The function requires to be optimised.

        """
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,load.__name__,__file__,__copyright__,
                        'verbose','True or False',None,verbose))
        
        if not isinstance(modelog,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,load.__name__,__file__,__copyright__,
                        'modelog','True or False',None,verbose))

        usermessage.openingmsg(__name__,load.__name__,__file__,__copyright__,'Load a EZ-InSAR job/processing from a file',None,verbose)

        # Read the file
        if not os.path.isfile(file):
                raise ValueError(usermessage.errormsg(__name__,load.__name__,__file__,__copyright__,
                        '%s has not been found.' % (file),None))

        usermessage.ezprint('Read the file %s' % (file),None,verbose)

        with open(file,'r') as f_in:
                xmlfile = (f_in.read())
        dictfile = xmltodict.parse(xmlfile)
                
        ## Conversion to a EZ-InSAR job
        # If we have a full job 
        if 'EZ-InSAR-Job' in dictfile.keys():
                usermessage.ezprint('Load a EZ-InSAR Job...',None,verbose) 

                job = EIjob()
                for item in dictfile['EZ-InSAR-Job'].keys():

                        # For the coregistration
                        if item == 'coregistration' and (not dictfile['EZ-InSAR-Job'][item]['@type'] == 'null'):

                                if dictfile['EZ-InSAR-Job']['coregistration']['processor']['#text'] == 'isce2':
                                        job.coregistration = isce2coregistration.coregistration(satellite=dictfile['EZ-InSAR-Job']['satellite']['#text'],
                                                                                                satmode=dictfile['EZ-InSAR-Job']['satmode']['#text'])
                                elif dictfile['EZ-InSAR-Job']['coregistration']['processor']['#text'] == 'snap':
                                        job.coregistration = snapcoregistration.coregistration(satellite=dictfile['EZ-InSAR-Job']['satellite']['#text'],
                                                                                                satmode=dictfile['EZ-InSAR-Job']['satmode']['#text'])
                                elif dictfile['EZ-InSAR-Job']['coregistration']['processor']['#text'] == 'doris':
                                        job.coregistration = doriscoregistration.coregistration(satellite=dictfile['EZ-InSAR-Job']['satellite']['#text'],
                                                                                                satmode=dictfile['EZ-InSAR-Job']['satmode']['#text'])

                                for itemcoreg in dictfile['EZ-InSAR-Job']['coregistration'].keys():
                                        if not itemcoreg == '@type':
                                                tmp = eval("dictfile['EZ-InSAR-Job']['coregistration']['%s']" % (itemcoreg)) 
                                                out = extractparam(tmp,itemcoreg)  

                                                if itemcoreg in [attr for attr in dir(job.coregistration) if not callable(getattr(job.coregistration, attr)) and not attr.startswith("__")]:
                                                        out2 = comparedict(eval("job.coregistration.%s" % (itemcoreg)),out,None,verbose)
                                                        exec("job.coregistration.%s = out2" % (itemcoreg))
                                                else:
                                                        usermessage.warningmsg(__name__,load.__name__,__file__,'The parameter %s has been depreciated in job.coregistration with %s. Please see the changelog.' % (itemcoreg,dictfile['EZ-InSAR-Job']['coregistration']['processor']['#text']),None,verbose)

                        # For the intstack
                        elif item == 'intstack' and (not dictfile['EZ-InSAR-Job'][item]['@type'] == 'null'):

                                if dictfile['EZ-InSAR-Job']['intstack']['processor']['#text'] == 'snap':
                                        job.intstack = snapintstack.intstack(satellite=dictfile['EZ-InSAR-Job']['satellite']['#text'],
                                                                                                satmode=dictfile['EZ-InSAR-Job']['satmode']['#text'])

                                for itemcoreg in dictfile['EZ-InSAR-Job']['intstack'].keys():
                                        if not itemcoreg == '@type':
                                                tmp = eval("dictfile['EZ-InSAR-Job']['intstack']['%s']" % (itemcoreg)) 
                                                out = extractparam(tmp,itemcoreg)

                                                if itemcoreg in [attr for attr in dir(job.intstack) if not callable(getattr(job.intstack, attr)) and not attr.startswith("__")]:  
                                                        out2 = comparedict(eval("job.intstack.%s" % (itemcoreg)),out,None,verbose)
                                                        exec("job.intstack.%s = out2" % (itemcoreg))
                                                else:
                                                        usermessage.warningmsg(__name__,load.__name__,__file__,'The parameter %s has been depreciated in job.intstack with %s. Please see the changelog.' % (itemcoreg,dictfile['EZ-InSAR-Job']['intstack']['processor']['#text']),None,verbose)

                        # For the ifgstack
                        elif item == 'ifgstack' and (not dictfile['EZ-InSAR-Job'][item]['@type'] == 'null'):

                                if dictfile['EZ-InSAR-Job']['ifgstack']['processor']['#text'] == 'isce2':
                                        job.ifgstack = isce2ifgstack.ifgstack(satellite=dictfile['EZ-InSAR-Job']['satellite']['#text'],
                                                                                satmode=dictfile['EZ-InSAR-Job']['satmode']['#text'])
                                elif dictfile['EZ-InSAR-Job']['ifgstack']['processor']['#text'] == 'doris':
                                        job.ifgstack = dorisifgstack.ifgstack(satellite=dictfile['EZ-InSAR-Job']['satellite']['#text'],
                                                                                satmode=dictfile['EZ-InSAR-Job']['satmode']['#text'])
                                elif dictfile['EZ-InSAR-Job']['ifgstack']['processor']['#text'] == 'snap':
                                        job.ifgstack = snapifgstack.ifgstack(satellite=dictfile['EZ-InSAR-Job']['satellite']['#text'],
                                                                                satmode=dictfile['EZ-InSAR-Job']['satmode']['#text'])

                                for itemcoreg in dictfile['EZ-InSAR-Job']['ifgstack'].keys():
                                        if not itemcoreg == '@type':
                                                tmp = eval("dictfile['EZ-InSAR-Job']['ifgstack']['%s']" % (itemcoreg)) 
                                                out = extractparam(tmp,itemcoreg) 
                                                
                                                if itemcoreg in [attr for attr in dir(job.ifgstack) if not callable(getattr(job.ifgstack, attr)) and not attr.startswith("__")]:
                                                        out2 = comparedict(eval("job.ifgstack.%s" % (itemcoreg)),out,None,verbose)
                                                        exec("job.ifgstack.%s = out2" % (itemcoreg))
                                                else:
                                                        usermessage.warningmsg(__name__,load.__name__,__file__,'The parameter %s has been depreciated in job.ifgstack with %s. Please see the changelog.' % (itemcoreg,dictfile['EZ-InSAR-Job']['ifgstack']['processor']['#text']),None,verbose)
                                
                       # For the tsprocessing
                        elif item == 'tsprocessing' and (not dictfile['EZ-InSAR-Job'][item]['@type'] == 'null'):

                                if dictfile['EZ-InSAR-Job']['tsprocessing']['processor']['#text'] == 'mintpy':
                                        job.tsprocessing = mintpytsprocessing.sbas(satellite=dictfile['EZ-InSAR-Job']['satellite']['#text'],
                                                                                        satmode=dictfile['EZ-InSAR-Job']['satmode']['#text'])
                                elif dictfile['EZ-InSAR-Job']['tsprocessing']['processor']['#text'] == 'miaplpy':
                                        job.tsprocessing = miaplpytsprocessing.ps(satellite=dictfile['EZ-InSAR-Job']['satellite']['#text'],
                                                                                        satmode=dictfile['EZ-InSAR-Job']['satmode']['#text'])

                                elif dictfile['EZ-InSAR-Job']['tsprocessing']['processor']['#text'] == 'sarvey':
                                        job.tsprocessing = sarveytsprocessing.ps(satellite=dictfile['EZ-InSAR-Job']['satellite']['#text'],
                                                                                        satmode=dictfile['EZ-InSAR-Job']['satmode']['#text'])         
                                
                                elif dictfile['EZ-InSAR-Job']['tsprocessing']['processor']['#text'] == 'stamps':
                                        if dictfile['EZ-InSAR-Job']['tsprocessing']['mode']['#text'] == 'ps':
                                                job.tsprocessing = stampstsprocessing.ps(satellite=dictfile['EZ-InSAR-Job']['satellite']['#text'],
                                                                                        satmode=dictfile['EZ-InSAR-Job']['satmode']['#text'])
                                        elif dictfile['EZ-InSAR-Job']['tsprocessing']['mode']['#text'] == 'sbas':
                                                job.tsprocessing = stampstsprocessing.sbas(satellite=dictfile['EZ-InSAR-Job']['satellite']['#text'],
                                                                                        satmode=dictfile['EZ-InSAR-Job']['satmode']['#text'])
                                        elif dictfile['EZ-InSAR-Job']['tsprocessing']['mode']['#text'] == 'merged':
                                                job.tsprocessing = stampstsprocessing.merged(satellite=dictfile['EZ-InSAR-Job']['satellite']['#text'],
                                                                                        satmode=dictfile['EZ-InSAR-Job']['satmode']['#text'])
                                elif dictfile['EZ-InSAR-Job']['tsprocessing']['processor']['#text'] == 'licsbas':
                                        job.tsprocessing = licsbastsprocessing.sbas(satellite=dictfile['EZ-InSAR-Job']['satellite']['#text'],
                                                                                        satmode=dictfile['EZ-InSAR-Job']['satmode']['#text'])
                                
                                for itemcoreg in dictfile['EZ-InSAR-Job']['tsprocessing'].keys():
                                        if not itemcoreg == '@type':
                                                tmp = eval("dictfile['EZ-InSAR-Job']['tsprocessing']['%s']" % (itemcoreg)) 
                                                out = extractparam(tmp,itemcoreg)  
                                                
                                                if itemcoreg in [attr for attr in dir(job.tsprocessing) if not callable(getattr(job.tsprocessing, attr)) and not attr.startswith("__")]:
                                                        out2 = comparedict(eval("job.tsprocessing.%s" % (itemcoreg)),out,None,verbose)
                                                        exec("job.tsprocessing.%s = out2" % (itemcoreg))
                                                else:
                                                        usermessage.warningmsg(__name__,load.__name__,__file__,'The parameter %s has been depreciated in job.tsprocessing with %s. Please see the changelog.' % (itemcoreg,dictfile['EZ-InSAR-Job']['tsprocessing']['processor']['#text']),None,verbose)
                        
                        else:
                                tmp = eval("dictfile['EZ-InSAR-Job']['%s']" % (item))   
                                out = extractparam(tmp,item) 

                                if item in [attr for attr in dir(job) if not callable(getattr(job, attr)) and not attr.startswith("__")]:  
                                        out2 = comparedict(eval("job.%s" % (item)),out,None,verbose) 
                                        exec("job.%s = out2" % (item))
                                else:
                                        usermessage.warningmsg(__name__,load.__name__,__file__,'The parameter %s has been depreciated in job.' % (item),None,verbose)

                # Correction for the dates
                if job.date1.split('.')[-1] == job.date1:
                        job.date1 = datetime.strptime(job.date1+'.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')
                else: 
                        job.date1 = datetime.strptime(job.date1+'Z','%Y-%m-%dT%H:%M:%S.%fZ')
                if job.date2.split('.')[-1] == job.date2:
                        job.date2 = datetime.strptime(job.date2+'.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')
                else: 
                        job.date2 = datetime.strptime(job.date2+'Z','%Y-%m-%dT%H:%M:%S.%fZ')

                if not job.roi ==None:                  
                        job.roi = loads(job.roi)

        # For a single coregistration processing
        elif 'EZ-InSAR-Coregistration' in dictfile.keys():
                usermessage.ezprint('Load a EZ-InSAR Coregistration processing...',None,verbose) 
                
                if dictfile['EZ-InSAR-Coregistration']['processor']['#text'] == 'isce2':
                        job = isce2coregistration.coregistration(satellite=dictfile['EZ-InSAR-Coregistration']['satellite']['#text'],
                                                                satmode=dictfile['EZ-InSAR-Coregistration']['satmode']['#text'])
                elif dictfile['EZ-InSAR-Coregistration']['processor']['#text'] == 'snap':
                        job = snapcoregistration.coregistration(satellite=dictfile['EZ-InSAR-Coregistration']['satellite']['#text'],
                                                                satmode=dictfile['EZ-InSAR-Coregistration']['satmode']['#text'])
                elif dictfile['EZ-InSAR-Coregistration']['processor']['#text'] == 'doris':
                        job = doriscoregistration.coregistration(satellite=dictfile['EZ-InSAR-Coregistration']['satellite']['#text'],
                                                                satmode=dictfile['EZ-InSAR-Coregistration']['satmode']['#text'])

                for itemcoreg in dictfile['EZ-InSAR-Coregistration'].keys():
                        if not itemcoreg == '@type':
                                tmp = eval("dictfile['EZ-InSAR-Coregistration']['%s']" % (itemcoreg)) 
                                out = extractparam(tmp,itemcoreg) 
                                if itemcoreg in [attr for attr in dir(job) if not callable(getattr(job, attr)) and not attr.startswith("__")]:
                                        out2 = comparedict(eval("job.%s" % (itemcoreg)),out,None,verbose)
                                        exec("job.%s = out2" % (itemcoreg))
                                else:
                                        usermessage.warningmsg(__name__,load.__name__,__file__,'The parameter %s has been depreciated in job.coregistration with %s. Please see the changelog.' % (itemcoreg,dictfile['EZ-InSAR-Coregistration']['processor']['#text']),None,verbose)

        elif 'EZ-InSAR-intstack' in dictfile.keys():
                usermessage.ezprint('Load a EZ-InSAR intstack processing...',None,verbose) 

                if dictfile['EZ-InSAR-intstack']['processor']['#text'] == 'snap':
                        job = snapintstack.intstack(satellite=dictfile['EZ-InSAR-intstack']['satellite']['#text'],
                                                satmode=dictfile['EZ-InSAR-intstack']['satmode']['#text'])

                for itemcoreg in dictfile['EZ-InSAR-intstack'].keys():
                        if not itemcoreg == '@type':
                                tmp = eval("dictfile['EZ-InSAR-intstack']['%s']" % (itemcoreg)) 
                                out = extractparam(tmp,itemcoreg) 

                                if itemcoreg in [attr for attr in dir(job) if not callable(getattr(job, attr)) and not attr.startswith("__")]:
                                        out2 = comparedict(eval("job.%s" % (itemcoreg)),out,None,verbose)
                                        exec("job.%s = out2" % (itemcoreg))
                                else:
                                        usermessage.warningmsg(__name__,load.__name__,__file__,'The parameter %s has been depreciated in job.intstack with %s. Please see the changelog.' % (itemcoreg,dictfile['EZ-InSAR-intstack']['processor']['#text']),None,verbose)
                        
        elif 'EZ-InSAR-ifgstack' in dictfile.keys():
                usermessage.ezprint('Load a EZ-InSAR ifgstack processing...',None,verbose) 

                if dictfile['EZ-InSAR-ifgstack']['processor']['#text'] == 'isce2':
                        job = isce2ifgstack.ifgstack(satellite=dictfile['EZ-InSAR-ifgstack']['satellite']['#text'],
                                                        satmode=dictfile['EZ-InSAR-ifgstack']['satmode']['#text'])
                elif dictfile['EZ-InSAR-ifgstack']['processor']['#text'] == 'doris':
                        job = dorisifgstack.ifgstack(satellite=dictfile['EZ-InSAR-ifgstack']['satellite']['#text'],
                                                        satmode=dictfile['EZ-InSAR-ifgstack']['satmode']['#text'])
                elif dictfile['EZ-InSAR-ifgstack']['processor']['#text'] == 'snap':
                        job = snapifgstack.ifgstack(satellite=dictfile['EZ-InSAR-ifgstack']['satellite']['#text'],
                                                        satmode=dictfile['EZ-InSAR-ifgstack']['satmode']['#text'])

                for itemcoreg in dictfile['EZ-InSAR-ifgstack'].keys():
                        if not itemcoreg == '@type':
                                tmp = eval("dictfile['EZ-InSAR-ifgstack']['%s']" % (itemcoreg)) 
                                out = extractparam(tmp,itemcoreg) 

                                if itemcoreg in [attr for attr in dir(job) if not callable(getattr(job, attr)) and not attr.startswith("__")]:
                                        out2 = comparedict(eval("job.%s" % (itemcoreg)),out,None,verbose)
                                        exec("job.%s = out2" % (itemcoreg))
                                else:
                                        usermessage.warningmsg(__name__,load.__name__,__file__,'The parameter %s has been depreciated in job.ifgstack with %s. Please see the changelog.' % (itemcoreg,dictfile['EZ-InSAR-ifgstack']['processor']['#text']),None,verbose)

        elif 'EZ-InSAR-tsprocessing' in dictfile.keys():
                usermessage.ezprint('Load a EZ-InSAR tsprocessing processing...',None,verbose) 

                if dictfile['EZ-InSAR-tsprocessing']['processor']['#text'] == 'mintpy':
                        job = mintpytsprocessing.sbas(satellite=dictfile['EZ-InSAR-tsprocessing']['satellite']['#text'],
                                                        satmode=dictfile['EZ-InSAR-tsprocessing']['satmode']['#text'])
                elif dictfile['EZ-InSAR-tsprocessing']['processor']['#text'] == 'miaplpy':
                        job = miaplpytsprocessing.ps(satellite=dictfile['EZ-InSAR-tsprocessing']['satellite']['#text'],
                                                        satmode=dictfile['EZ-InSAR-tsprocessing']['satmode']['#text'])
                elif dictfile['EZ-InSAR-tsprocessing']['processor']['#text'] == 'sarvey':
                        job = sarveytsprocessing.ps(satellite=dictfile['EZ-InSAR-tsprocessing']['satellite']['#text'],
                                                        satmode=dictfile['EZ-InSAR-tsprocessing']['satmode']['#text'])
                elif dictfile['EZ-InSAR-tsprocessing']['processor']['#text'] == 'stamps':
                        if dictfile['EZ-InSAR-tsprocessing']['mode']['#text'] == 'ps':
                                job = stampstsprocessing.ps(satellite=dictfile['EZ-InSAR-tsprocessing']['satellite']['#text'],
                                                        satmode=dictfile['EZ-InSAR-tsprocessing']['satmode']['#text'])
                        elif dictfile['EZ-InSAR-tsprocessing']['mode']['#text'] == 'sbas':
                                job = stampstsprocessing.sbas(satellite=dictfile['EZ-InSAR-tsprocessing']['satellite']['#text'],
                                                        satmode=dictfile['EZ-InSAR-tsprocessing']['satmode']['#text'])
                        elif dictfile['EZ-InSAR-tsprocessing']['mode']['#text'] == 'merged':
                                job = stampstsprocessing.merged(satellite=dictfile['EZ-InSAR-tsprocessing']['satellite']['#text'],
                                                        satmode=dictfile['EZ-InSAR-tsprocessing']['satmode']['#text'])
                elif dictfile['EZ-InSAR-tsprocessing']['processor']['#text'] == 'licsbas':
                        job = licsbastsprocessing.sbas(satellite=dictfile['EZ-InSAR-tsprocessing']['satellite']['#text'],
                                                        satmode=dictfile['EZ-InSAR-tsprocessing']['satmode']['#text'])
                                        
                for itemcoreg in dictfile['EZ-InSAR-tsprocessing'].keys():
                        if not itemcoreg == '@type':
                                tmp = eval("dictfile['EZ-InSAR-tsprocessing']['%s']" % (itemcoreg)) 
                                out = extractparam(tmp,itemcoreg) 

                                if itemcoreg in [attr for attr in dir(job) if not callable(getattr(job, attr)) and not attr.startswith("__")]:
                                        out2 = comparedict(eval("job.%s" % (itemcoreg)),out,None,verbose)
                                        exec("job.%s = out2" % (itemcoreg))
                                else:
                                        usermessage.warningmsg(__name__,load.__name__,__file__,'The parameter %s has been depreciated in job.tsprocessing with %s. Please see the changelog.' % (itemcoreg,dictfile['EZ-InSAR-tsprocessing']['processor']['#text']),None,verbose)

        else: 
                raise ValueError(usermessage.errormsg(__name__,load.__name__,__file__,__copyright__,
                        'The file is not a EZ-InSAR job/processing.',None,verbose))

        # Check the new job  
        if bypasscheck == False:
                if 'EIjob' in str(type(job)):
                        job.check(verbose=False,modelog=modelog)

                        if not job.coregistration == None: 
                                job.coregistration.check(verbose=False)
                        if not job.ifgstack == None: 
                                job.ifgstack.check(verbose=False)
                        if not job.intstack == None: 
                                job.intstack.check(verbose=False)
                        if not job.tsprocessing == None: 
                                job.tsprocessing.check(verbose=False)
                else: 
                        job.check(verbose=False)

        return job  

################################################################################
## Creation of an archive for long-term storage
################################################################################
def archive(job, 
        file: Optional[Union[None, str]] = None, 
        description: Optional[Union[None, str]] = None,
        project: Optional[Union[None, str]] = None,
        imageill: Optional[Union[None, str]] = None,
        report: Optional[bool] = True,
        suppfile: Optional[list] = [],
        references: Optional[list] = [],
        logo: Optional[Union[None, str]] = None,
        masksensible: Optional[bool] = True,
        compression: Optional[Union[str]] = 'gz',
        encryption: Optional[bool] = False,
        key: Optional[Union[None, str]] = None,
        bypassuser: Optional[bool] = False,  
        comuse: Optional[bool] = False, 
        packageill: Optional[str] = 'matplotlib', 
        clean: Optional[bool] = True, 
        verbose: Optional[bool] = None): 
        """Create an archive from an EZ-InSAR processing . 

        The function creates an archive for long-term storage from an `EIjob`.  

        Args:
                job (`EIjob`): EZ-InSAR job
                file (str): Full path of the archive file
                description (str): Description of the archive (i.e., text will be added to the report)
                project (str): Project name
                imageill (str): Path of an image for illustration
                report (bool): Creation of the .pdf report (can be `True` or `False`)
                suppfile (list): `None`, 'description': `None`, 'newname': 'name'}): List of the supplementary files needed to be added to the archive
                references (list): List of DOI for the publications used this dataset (e.g., 10.1016/j.rse.2023.113516)
                logo (str): Path of the logo used to generate the report
                masksensible (bool): Masked the sensible information like paths
                compression (str): Method of compression
                encryption (bool): Encryption of the archive (can be `True` of `False`)
                key (str): Key used to encrypt the archive
                bypassuser (bool): Bypass the user for encryption (can be `True` of `False`)
                comuse (bool): Apply a license for commercial use (see Licensing of data in the EZ-InSAR documentation) (can be `True` or `False`)
                packageill (str): Package used to generate the map of illustration (can be matplotlib or pygmt)
                clean (bool): Clean the temporary files (can be `True` of `False`)
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.  

        """
        if (not 'EIjob' in str(type(job))): 
                raise ValueError(usermessage.errormsg(__name__,archive.__name__,__file__,__copyright__,
                                'The job parameter is not a EZ-InSAR job/processing.',job.log))
                
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,archive.__name__,__file__,__copyright__,
                        'verbose','True or False'),job.log,verbose)

        usermessage.openingmsg(__name__,archive.__name__,__file__,__copyright__,'Create a .tar archive for long-term storage',job.log,verbose)

        ## Copy the new job variable
        jobbackup = copy.deepcopy(job)

        ## Confirmation of the user
        # For bypassuser 
        if not isinstance(bypassuser,bool): 
                raise TypeError(usermessage.typeerrormsg(
                         __name__,archive.__name__,__file__,__copyright__,
                        'bypassuser','bool',None,verbose))
        
        if not bypassuser == True: 
                anwser = False
                while not anwser in ['yes','y','1','ok','okay',1,True,'True']:  
                        anwser = input("EZ-InSAR will create a .tar archive for long-term storage. However it will not be possible to update the arhived job. It is recommended keeping the files in order to maintain the update ability.\nCan you confimr it? [yes or no] ")
                        if anwser in ['no','n','0',0,'False',False]: 
                                raise ValueError(usermessage.errormsg(__name__,archive.__name__,__file__,__copyright__,
                                'Stopped by user.',job.log))
                        
        if not packageill in ['matplotlib','pygmt']:
                raise TypeError(usermessage.typeerrormsg(
                         __name__,archive.__name__,__file__,__copyright__,
                        'packageill','matplotlib or pygmt',None,verbose)) 
                        
        ## Check the different inputs 
        # For description
        if description == None: 
                usermessage.warningmsg(__name__,archive.__name__,__file__,'No description given.',job.log,verbose)
        else: 
                if not isinstance(description,str): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,archive.__name__,__file__,__copyright__,
                                'description','None or str',None,verbose))
        
        # For project
        if project == None: 
                usermessage.warningmsg(__name__,archive.__name__,__file__,'No project given.',job.log,verbose)
        else: 
                if not isinstance(project,str): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,archive.__name__,__file__,__copyright__,
                                'project','None or str',None,verbose))
                
        # For imageill
        if (not imageill == None):
                if os.path.isfile(imageill) == False:
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,archive.__name__,__file__,__copyright__,
                                'imageill','None or str',None,verbose))
        
        # For report 
        if not isinstance(report,bool): 
                raise TypeError(usermessage.typeerrormsg(
                         __name__,archive.__name__,__file__,__copyright__,
                        'report','bool',None,verbose))
                
        # For suppfile 
        if not isinstance(suppfile,list): 
                raise TypeError(usermessage.typeerrormsg(
                         __name__,archive.__name__,__file__,__copyright__,
                        'suppfile','list',None,verbose))
        for fi in suppfile:
                if (not 'scp' in fi['file']) and (not os.path.isfile(fi['file'])): 
                        raise ValueError(usermessage.errormsg(__name__,archive.__name__,__file__,__copyright__,
                                'The file %s does not exist.' % (fi['file']),job.log))
                
        # For references 
        if not isinstance(references,list):
                raise TypeError(usermessage.typeerrormsg(
                         __name__,archive.__name__,__file__,__copyright__,
                        'references','list',None,verbose)) 
        
        for fi in references:
                if not isinstance(fi,str):
                        raise ValueError(usermessage.errormsg(__name__,archive.__name__,__file__,__copyright__,
                                'The reference %s should be a str (DOI).' % (fi),job.log))
        
        # For logo
        if (not logo == None):
                if not isinstance(logo,str):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,archive.__name__,__file__,__copyright__,
                                'logo','None or str',None,verbose))
        
        # For maskpath 
        if not isinstance(masksensible,bool): 
                raise TypeError(usermessage.typeerrormsg(
                         __name__,archive.__name__,__file__,__copyright__,
                        'masksensible','bool',None,verbose))

        # For compression
        if not compression in ['','gz']: 
                raise TypeError(usermessage.typeerrormsg(
                         __name__,archive.__name__,__file__,__copyright__,
                        'compression',"'' or 'gz'",None,verbose))
        
        # For encryption 
        if not isinstance(encryption,bool): 
                raise TypeError(usermessage.typeerrormsg(
                         __name__,archive.__name__,__file__,__copyright__,
                        'encryption','bool',None,verbose))
        
        # For key
        if (not key == None):
                if not isinstance(key,str):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,archive.__name__,__file__,__copyright__,
                                'key','None or str',None,verbose))
        
        ## Check if the user have a web connection 
        response_web = False
        try: 
                response = requests.get(constants.__websitetestconn__, timeout=5)
                response_web = True
        except requests.ConnectionError:
                response_web = False

        if response_web == False: 
                raise ValueError(usermessage.errormsg(__name__,archive.__name__,__file__,__copyright__,
                                'No internet connection: a connection is required for a archive creation.',job.log))

        ## Detection of processing job
        jobbackupcoreg = None
        jobbackupifgstack = None
        jobbackuptsprocessing = None
        jobbackupintstack = None

        usermessage.ezprint('Detection of EZ-InSAR processing job',job.log,verbose)
        if not jobbackup.coregistration == None: 
                usermessage.ezprint('\tCoregistration job detected.',job.log,verbose)
                jobbackupcoreg = jobbackup.coregistration
                jobbackup.coregistration = None
        if not jobbackup.ifgstack == None: 
                usermessage.ezprint('\tInterferometric-stack job detected.',job.log,verbose)
                jobbackupifgstack = jobbackup.ifgstack
                jobbackup.ifgstack = None     
        if not jobbackup.tsprocessing == None: 
                usermessage.ezprint('\ttsprocessing job detected.',job.log,verbose)
                jobbackuptsprocessing = jobbackup.tsprocessing
                jobbackup.tsprocessing = None  
        if not jobbackup.intstack == None: 
                usermessage.ezprint('\tIntensity-stack job detected.',job.log,verbose)
                jobbackupintstack = jobbackup.intstack
                jobbackup.intstack = None  

        ## Detection of the license
        if comuse == False: 
                licenseimage = constants.__imagelicensencu__
                licensetext = constants.__licensetextncu__
                msglicense = constants.__msglicensencu__
        else: 
                licenseimage = constants.__imagelicense__
                licensetext = constants.__licensetext__
                msglicense = constants.__msglicensen__

        ## Detection of processing job
        usermessage.ezprint('Creation of the archive name...',job.log,verbose)
        if file == None:
                nametar = jobbackup.nameJob
                for symbol in ['-',' ','/','.']: 
                        nametar = nametar.replace(symbol,'_')
        elif isinstance(file,str):
                nametar = file
        else:
                raise TypeError(usermessage.typeerrormsg(
                        __name__,archive.__name__,__file__,__copyright__,
                        'file','None or str',None,verbose))
        usermessage.ezprint('\tdone',job.log,verbose)

        ## Creation of the temporal directory
        if os.path.isdir('tmparchive'): 
                raise ValueError(usermessage.errormsg(__name__,archive.__name__,__file__,__copyright__,
                        'A tmparchive directory seems be present. Please delete it.',job.log))
        else: 
                os.mkdir('tmparchive')

        ## Create the report (example from https://jeltef.github.io/PyLaTeX/current/examples/complex_report.html)
        if report == True:
                usermessage.ezprint('Creation of the report...',job.log,verbose)  

                geometry_options = {
                        "head": "150pt",
                        "margin": "0.5in",
                        "bottom": "100pt",
                        "includeheadfoot": True
                        }
                doc = pylatex.Document(geometry_options=geometry_options)

                # Generating first page style
                first_page = pylatex.PageStyle("firstpage")

                # Include the EZ-InSAR logo
                with first_page.create(pylatex.Head("L")) as header_left:
                        with header_left.create(pylatex.MiniPage(width=pylatex.utils.NoEscape(r"0.25\textwidth"),
                                                        pos='c')) as logo_wrapper:
                                logo_file = os.path.dirname(__file__)+os.sep+'..'+os.sep+'..'+os.sep+'private'+os.sep+'EZ_InSAR_logo.png'
                                logo_wrapper.append(pylatex.StandAloneGraphic(image_options="width=120px",
                                                        filename=logo_file))

                # Include the processing information
                with first_page.create(pylatex.Head("R")) as right_header:
                        with right_header.create(pylatex.MiniPage(width=pylatex.utils.NoEscape(r"0.75\textwidth"),
                                                        pos='c', align='r')) as title_wrapper:
                                title_wrapper.append(pylatex.LargeText(pylatex.utils.bold("Processing Report")))
                                title_wrapper.append(pylatex.LineBreak())
                                title_wrapper.append(pylatex.LargeText("%s" % (jobbackup.nameJob)))
                                title_wrapper.append(pylatex.LineBreak())
                                title_wrapper.append(pylatex.LineBreak())

                                title_wrapper.append(pylatex.MediumText(pylatex.utils.bold("Operator:")))
                                title_wrapper.append(pylatex.LineBreak())
                                title_wrapper.append(pylatex.MediumText("%s" % (jobbackup.user)))
                                title_wrapper.append(pylatex.LineBreak())
                                title_wrapper.append(pylatex.LineBreak())
                                title_wrapper.append(pylatex.MediumText(pylatex.utils.bold("Project:")))
                                title_wrapper.append(pylatex.LineBreak())
                                title_wrapper.append(pylatex.MediumText("%s" % (project)))
                                title_wrapper.append(pylatex.LineBreak())
                                title_wrapper.append(pylatex.LineBreak())

                                title_wrapper.append(pylatex.MediumText("Archive creation: %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
                                title_wrapper.append(pylatex.LineBreak())
                                title_wrapper.append(pylatex.LineBreak())
                                title_wrapper.append(pylatex.utils.NoEscape(r"\noindent\rule{\textwidth}{1pt}"))
                                title_wrapper.append(pylatex.LineBreak())

                # Add footer
                with first_page.create(pylatex.Foot("C")) as footer:
                        with footer.create(pylatex.Tabularx("X X X X",width_argument=pylatex.utils.NoEscape(r"\textwidth"))) as footer_table:
                                footer_table.add_row([pylatex.MultiColumn(4, align='l')])
                                footer_table.add_hline(color="black")
                                footer_table.add_empty_row()

                                # Add the license
                                miscellaneous.download_file(licenseimage,output_file='tmplicense.png')

                                licencetab = pylatex.MiniPage(
                                                width=pylatex.utils.NoEscape(r"0.25\textwidth"),
                                                pos='h')
                                licencetab.append(pylatex.StandAloneGraphic(image_options=r"width=0.5\textwidth",
                                        filename='tmplicense.png'))
                                
                                # Add the iCRAG logo
                                if logo == None: 
                                        try:
                                                logo = 'tmplogo.png'
                                                miscellaneous.download_file('https://www.icrag-centre.org/t4media/icrag-logo-new.png',output_file=logo)

                                        except Exception as e:
                                                print(f"An error occurred: {e}")
                                                logo = None
                                
                                logotab = pylatex.MiniPage(
                                        width=pylatex.utils.NoEscape(r"0.25\textwidth"),
                                        pos='h')
                                if not logo == None:
                                        logotab.append(pylatex.StandAloneGraphic(image_options=r"width=0.5\textwidth",
                                                filename=logo))
                                        
                                # EZ-InSAR info
                                ezinsarinfo = pylatex.MiniPage(
                                        width=pylatex.utils.NoEscape(r"0.25\textwidth"),
                                        pos='t')
                                ezinsarinfo.append("EZ-InSAR version %s" % (constants.__version__))
                                # ezinsarinfo.append("\n")
                                # ezinsarinfo.append("%s" % (constants.__copyright__))

                                # Document details
                                document_details = pylatex.MiniPage(width=pylatex.utils.NoEscape(r"0.25\textwidth"),
                                                                pos='h', align='r')
                                document_details.append(pylatex.simple_page_number())

                                # Fusion
                                footer_table.add_row([licencetab, logotab, ezinsarinfo, document_details])

                doc.preamble.append(first_page)
                # End first page style

                doc.change_document_style("firstpage")
                doc.add_color(name="lightgray", model="gray", description="0.80")

                # Add stuff to the document
                with doc.create(pylatex.Section('Summary')):
                        doc.append(description)

                # Job information table
                with doc.create(pylatex.LongTabu("X[l] X[l] X[l] X[l] X[l]",
                                        row_height=1.5)) as data_table:
                        data_table.add_row(["Satellite",
                                        "Mode",
                                        "Polarisation",
                                        "Pass",
                                        "Track"],
                                        mapper=pylatex.utils.bold,
                                        color="lightgray")
                        data_table.add_hline()
                        row = ["%s" % (jobbackup.satellite), 
                               "%s" % (jobbackup.satmode), 
                               "%s" % (jobbackup.polarisation),
                               "%s" % (jobbackup.satpass), 
                               "%s" % (jobbackup.relorbit)]
                        data_table.add_row(row)

                with doc.create(pylatex.LongTabu("X[l] X[l] X[l] X[l]",
                                        row_height=1.5)) as data_table:
                        data_table.add_row(["Coregistration",
                                        "Interferometric stack",
                                        "Time series analysis",
                                        "Intensity stack"],
                                        mapper=pylatex.utils.bold,
                                        color="lightgray")
                        data_table.add_hline()
                        row = []
                        if not jobbackupcoreg == None: 
                                row.append(pylatex.TextColor("green", 'True'))
                        else:
                                row.append(pylatex.TextColor("red", 'False'))
                        if not jobbackupifgstack == None: 
                                row.append(pylatex.TextColor("green", 'True'))
                        else:
                                row.append(pylatex.TextColor("red", 'False'))
                        if not jobbackuptsprocessing == None: 
                                row.append(pylatex.TextColor("green", 'True'))
                        else:
                                row.append(pylatex.TextColor("red", 'False'))
                        if not jobbackupintstack == None: 
                                row.append(pylatex.TextColor("green", 'True'))
                        else:
                                row.append(pylatex.TextColor("red", 'False'))
                        data_table.add_row(row)

                # Add an image for illustration 
                if imageill == None:  

                        if packageill == ' pygmt': 
                                import pygmt
                                fig = pygmt.Figure()
                                lon = jobbackup.roi.exterior.xy[0]
                                lat = jobbackup.roi.exterior.xy[1]
                                optical_basemap = False
                                try: 
                                        fig.tilemap(
                                                region=[np.min(lon), np.max(lon), np.min(lat), np.max(lat)],
                                        projection="M12c",zoom=14,
                                                source="http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                                                frame="afg",
                                        )
                                        optical_basemap = True
                                except:
                                        fig.basemap(
                                                region=[np.min(lon), np.max(lon), np.min(lat), np.max(lat)],
                                                projection="M12c", 
                                                frame="afg")
                                        fig.coast(resolution='f',land="#1d8348", water="#85c1e9", shorelines=True)
                                        optical_basemap = False

                                fig.plot(
                                        region=[np.min(lon), np.max(lon), np.min(lat), np.max(lat)],
                                        projection="M12c",
                                        x=lon,
                                        y=lat,
                                        pen="1p,black",
                                )

                                fig.savefig('tmpimageill.jpg')
                                imageill = 'tmpimageill.jpg'
                        else: 
                                import matplotlib.pyplot as plt
                                from mpl_toolkits.basemap import Basemap

                                lon,lat = jobbackup.roi.exterior.xy
                                fig = plt.figure(figsize=(8, 8))
                                m = Basemap(projection='merc', resolution='f',epsg=4326, 
                                                llcrnrlon = np.min(lon)-(np.max(lon)-np.min(lon))*0.25,
                                                llcrnrlat = np.min(lat)-(np.max(lat)-np.min(lat))*0.25,
                                                urcrnrlon = np.max(lon)+(np.max(lon)-np.min(lon))*0.25,
                                                urcrnrlat = np.max(lat)+(np.max(lat)-np.min(lat))*0.25)       
                                m.plot([np.min(lon),np.max(lon),np.max(lon),np.min(lon),np.min(lon)],[np.min(lat),np.min(lat),np.max(lat),np.max(lat),np.min(lat)],'-',linewidth=2,color='black',latlon=True)
                                m.arcgisimage(service='World_Imagery', xpixels = 1000, ypixels = 1000, verbose = verbose)
                                m.drawparallels(np.linspace(np.fix(np.min(lat))-1,np.fix(np.max(lat))+1,10),labels=[1,0,0,0])
                                m.drawmeridians(np.linspace(np.fix(np.min(lon))-1,np.fix(np.max(lon))+1,10),labels=[0,0,0,1])
                                
                                plt.legend()
                                plt.savefig('tmpimageill.jpg', dpi=450)
                                imageill = 'tmpimageill.jpg'
                                multispectral_basemap = True

                if not imageill == None:
                        with doc.create(pylatex.Figure(position='p')) as figure_ill:
                                figure_ill.add_image(imageill, width='300px')
                                if multispectral_basemap == True: 
                                        figure_ill.add_caption('Multispectral image of the Region of Interest. The black polygon corresponds to the EZ-InSAR Region of Interest. Basemap image: ArcGISOnline service.')
                                else: 
                                        figure_ill.add_caption('Region of Interest. The black polygon corresponds to the EZ-InSAR Region of Interest.')

                ## For the coregistration 
                if not jobbackupcoreg == None: 
                        ## Add the information about the coregistration processing
                        doc.append(pylatex.NewPage())

                        # Quick detection of dates
                        datescoreg = []
                        if jobbackupcoreg.processor == 'gamma':
                                with open(jobbackupcoreg.pathstack+os.sep+'rslc_'+jobbackupcoreg.polarisation[0].lower()+os.sep+'dates','r') as fi: 
                                        for di in fi:
                                                datescoreg.append(datetime.strptime(di.split()[0],'%Y%m%d'))
                        datescoreg = np.sort(datescoreg)

                        with doc.create(pylatex.Section('Coregistration processing')): 
                                with doc.create(pylatex.LongTabu("X[l] X[l] X[l] X[l] X[l]",
                                                row_height=1.5)) as data_table:
                                        data_table.add_row(["EZ-InSAR file",
                                                        "Processor",
                                                        "Polarisation",
                                                        "Dates",
                                                        "Reference date"],
                                                        mapper=pylatex.utils.bold,
                                                        color="lightgray")
                                        data_table.add_hline()
                                        row = ["%s" % ('ezinsarjob\ \ncoregistration.ei'), 
                                        "%s" % (jobbackupcoreg.processor), 
                                        "%s" % (jobbackupcoreg.polarisation), 
                                        "%s - %s (%s dates)" % (np.min(datescoreg).strftime('%Y%m%d'),np.max(datescoreg).strftime('%Y%m%d'),len(datescoreg)), 
                                        "%s" % (jobbackupcoreg.refdate)]
                                        data_table.add_row(row)

                                # Add the intensity images and baselines
                                if (not os.path.isfile(imagebpepcoreg)) and (not os.path.isfile(imageintcoreg)):
                                        # raise ValueError(usermessage.errormsg(__name__,archive.__name__,__file__,__copyright__,
                                        #         'The files %s and %s are required.' % (imagebpepcoreg,imageintcoreg),job.log))

                                        Image.open(imagebpepcoreg).save('imagebpepcoreg.png')
                                        Image.open(imageintcoreg).save('imageintcoreg.png')

                                        with doc.create(pylatex.Figure(position='p')) as coregfigure:
                                                with doc.create(pylatex.SubFigure(
                                                        position='b',
                                                        width=pylatex.utils.NoEscape(r'0.45\linewidth'))) as figure1:

                                                        figure1.add_image('imagebpepcoreg.png',
                                                                        width=pylatex.utils.NoEscape(r'\linewidth'))
                                                        figure1.add_caption('Super-single master network')
                                                with doc.create(pylatex.SubFigure(
                                                        position='b',
                                                        width=pylatex.utils.NoEscape(r'0.45\linewidth'))) as figure2:

                                                        figure2.add_image('imageintcoreg.png',
                                                                        width=pylatex.utils.NoEscape(r'\linewidth'))
                                                        figure2.add_caption('Intensity image of the reference date')
                                                coregfigure.add_caption("Coregistration figures")

                ## For the intensity stack 
                if not jobbackupintstack == None: 
                        ## Add the information about the intensity processing
                        doc.append(pylatex.NewPage())

                        # Quick detection of dates
                        datesint = []
                        if jobbackupintstack.processor == 'snap':
                                listfile = glob.glob(jobbackupintstack.workdirectory+os.sep+'geotiff'+os.sep+'*.tif')
                                for li in listfile: 
                                        a = li.split(os.sep)[-1].split('.')[0]
                                        datesint.append(datetime.strptime(a,'%Y%m%d'))
                                datesint = np.unique(datesint)

                        datesint = np.sort(datesint)

                        with doc.create(pylatex.Section('Intensity-stack processing')): 
                                with doc.create(pylatex.LongTabu("X[l] X[l] X[l] X[l]",
                                                row_height=1.5)) as data_table:
                                        data_table.add_row(["EZ-InSAR file",
                                                        "Processor",
                                                        "Polarisation",
                                                        "Dates"],
                                                        mapper=pylatex.utils.bold,
                                                        color="lightgray")
                                        data_table.add_hline()
                                        row = ["%s" % ('ezinsarjob\ \nintstack.ei'), 
                                        "%s" % (jobbackupintstack.processor), 
                                        "%s" % (jobbackupintstack.polarisation), 
                                        "%s - %s (%s dates)" % (np.min(datesint).strftime('%Y%m%d'),np.max(datesint).strftime('%Y%m%d'),len(datesint))]
                                        data_table.add_row(row)

                # Create the list of supp files
                with doc.create(pylatex.Section('Supplementary files')):
                        with doc.create(pylatex.Itemize()) as itemize:

                                for fi in suppfile: 
                                        if fi['newname'] == None: 
                                                name = fi['file'].split(os.sep)[-1]
                                        else: 
                                                name = fi['newname']
                                        itemize.add_item("File %s: %s" % (name,fi['description']))

                # Create the list of references
                with doc.create(pylatex.Section('References')):

                        if references:
                                for idx, refi in enumerate(references): 
                                        time.sleep(5)
                                        if refi.startswith("http://"):
                                                url = refi
                                        else:
                                                url = "http://dx.doi.org/" + refi
                                        r = requests.get(url, headers = {'accept': 'text/x-bibliography; style=apa'}, timeout=5).text
                                        doc.append('%s\n%s' % (' '.join(r.split(' ')[0:-1]),r.split(' ')[-1]))

                                        if not idx == len(references)-1:
                                                doc.append(pylatex.NewLine())

                        else: 
                                doc.append('No references.')

                # Create the list of supp files
                with doc.create(pylatex.Section('License')):
                        doc.append(msglicense)

                # Save
                doc.generate_pdf("report", clean_tex=False)
                shutil.move('report.pdf','tmparchive'+os.sep+'report.pdf')

                for fi in ['tmplogo.png','tmpimageill.jpg',"report.tex","imagebpepcoreg.png","imageintcoreg.png","tmplicense.png"]:
                        if os.path.isfile(fi):
                                os.remove(fi)

                usermessage.ezprint('\tdone',job.log,verbose)  

        ## Creation of zip archives for each processing   
        usermessage.ezprint('Creation of zip archives for each processing:...',job.log,verbose)  

        usermessage.ezprint('\tFor the coregistration:...',job.log,verbose)  
        if not jobbackupcoreg == None:
                with ZipFile('tmparchive'+os.sep+'coregdata.zip', 'w') as zipout:
                        for fi in listfile:
                                usermessage.ezprint('\t\tCompress the file: %s' % (fi),job.log,verbose)  
                                zipout.write(fi,os.path.basename(fi))
        usermessage.ezprint('\t\tdone',job.log,verbose)

        usermessage.ezprint('\tFor the intensity stack:...',job.log,verbose)  
        if not jobbackupintstack == None:
                if jobbackupintstack.processor == 'snap':
                        listfile = glob.glob(jobbackupintstack.workdirectory+os.sep+'geotiff'+os.sep+'*.tif')

                with ZipFile('tmparchive'+os.sep+'intdata.zip', 'w') as zipout:
                        for fi in listfile:
                                usermessage.ezprint('\t\tCompress the file: %s' % (fi),job.log,verbose)  
                                zipout.write(fi,os.path.basename(fi))
        usermessage.ezprint('\t\tdone',job.log,verbose)

        # FOR OTHERS

        ## Copy the supplementary files
        usermessage.ezprint('\tImport the supplementary files:...',job.log,verbose)
        for fi in suppfile:
                if 'scp' in fi['file']: 
                        cmd = fi['file'] + ' ' + 'tmparchive'+os.sep+fi['newname']
                        os.system(cmd)
                else: 
                        if fi['newname'] == None: 
                                shutil.copy(fi['file'],'tmparchive'+os.sep+os.path.basename(fi['file']))
                        else:
                                shutil.copy(fi['file'],'tmparchive'+os.sep+fi['newname'])
        usermessage.ezprint('\t\tdone',job.log,verbose)

        ## Creation of EZ-InSAR files
        usermessage.ezprint('Creation of EZ-InSAR files:...',job.log,verbose)
        if masksensible == True:
                
                def masksensible(jobtmp):
                        listvar = list(vars(jobtmp).keys())
                        for vari in listvar:
                                if 'path' in vari or 'token' in vari or 'workdirectory' in vari or 'email' in vari:
                                        exec('jobtmp.%s = "Masked"' % (vari))
                        return jobtmp
                
                jobbackup = masksensible(jobbackup)
                if not jobbackupcoreg == None:
                        jobbackupcoreg = masksensible(jobbackupcoreg)
                if not jobbackupifgstack == None:
                        jobbackupifgstack = masksensible(jobbackupifgstack)
                if not jobbackuptsprocessing == None:
                        jobbackuptsprocessing = masksensible(jobbackuptsprocessing)
                if not jobbackupintstack == None:
                        jobbackupintstack = masksensible(jobbackupintstack)

        save(jobbackup,'tmparchive'+os.sep+'ezinsarjob.ei',verbose=False)
        if not jobbackupcoreg == None:
                save(jobbackupcoreg,'tmparchive'+os.sep+'ezinsarjobcoregistration.ei',verbose=False)
        if not jobbackupifgstack == None:
                save(jobbackupifgstack,'tmparchive'+os.sep+'ezinsarjobifgstack.ei',verbose=False)
        if not jobbackuptsprocessing == None:
                save(jobbackuptsprocessing,'tmparchive'+os.sep+'ezinsarjobtsprocessing.ei',verbose=False)
        if not jobbackupintstack == None:
                save(jobbackupintstack,'tmparchive'+os.sep+'ezinsarjobintstack.ei',verbose=False)

        jobbackup.saveSLClist(verbose = False, file = 'tmparchive'+os.sep+'SLClist')
        usermessage.ezprint('\tdone.',job.log,verbose)

        ## Add the license file
        usermessage.ezprint('Creation of EZ-InSAR files:...',job.log,verbose)        
        miscellaneous.download_file(licensetext,output_file='tmparchive'+os.sep+'license.txt')

        os.system(cmd)
        usermessage.ezprint('\tdone.',job.log,verbose)

        # Create the final archive
        usermessage.ezprint('Create the final archive:...',job.log,verbose)        

        if not compression == '':
                nametar = nametar+'.tar.'+compression
                tar = tarfile.open(nametar, "w:"+compression)
        else:
                nametar = nametar+'.tar'
                tar = tarfile.open(nametar, "w:"+compression) 
        
        listfi = glob.glob('tmparchive'+os.sep+'*')
        for fi in listfi:
                usermessage.ezprint('\tArchive the file: %s' % (fi),job.log,verbose)    
                tar.add(fi, arcname=os.path.basename(fi))
        tar.close()

        usermessage.ezprint('\tdone.',job.log,verbose)

        if os.path.isdir('tmparchive'): 
                shutil.rmtree('tmparchive')

        ## Encrypting 
        if encryption == True:
                usermessage.ezprint('Encrypt the archive: ...',job.log,verbose)

                # Import some required packages
                import gnupg
                import getpass

                gpg = gnupg.GPG()

                if key == None: 
                        # generate key
                        usermessage.ezprint('\tNo key given - generation of the key: ...',job.log,verbose)

                        name_email = ''
                        while name_email == '':
                                name_email = input('User email [empty]: ')
                        
                        pswd = ''
                        while pswd == '':
                                pswd = getpass.getpass('Password [empty]: ')

                        input_data = gpg.gen_key_input(
                                name_email=name_email,
                                passphrase=pswd,
                                )
                        key = gpg.gen_key(input_data)
                
                        # create ascii-readable versions of pub / private keys
                        ascii_armored_public_keys = gpg.export_keys(key.fingerprint)
                        ascii_armored_private_keys = gpg.export_keys(
                                keyids=key.fingerprint,
                                secret=True,
                                passphrase=pswd,
                                )
                        
                        # export
                        usermessage.ezprint('\t\tExport the keys in the current directory',job.log,verbose)

                        with open('keyfilepublic.asc', 'w') as f:
                                f.write(ascii_armored_public_keys)
                        with open('keyfileprivate.asc', 'w') as f:
                                f.write(ascii_armored_private_keys)

                        # Delete keys
                        usermessage.ezprint('\t\tDelete the keys',job.log,verbose)
                        fp = key.fingerprint
                        gpg.delete_keys(fp, True, passphrase=pswd)
                        gpg.delete_keys(fp)

                        key = 'keyfilepublic.asc'

                # import
                if not os.path.isfile(key):
                        raise ValueError(usermessage.errormsg(__name__,archive.__name__,__file__,__copyright__,
                                'Impossible to find the public key.',job.log))
                
                try: 
                        with open(key) as f:
                                key_data = f.read()
                                import_result = gpg.import_keys(key_data)

                        # for k in import_result.results:
                        #         print(k)
                        keyimported = import_result.results[0]['fingerprint']

                        # encrypt file
                        with open(nametar, 'rb') as f:
                                status = gpg.encrypt_file(f,
                                        recipients = [keyimported],
                                        always_trust = True,
                                        output=nametar+'.gpg',
                                )

                        if verbose == True: 
                                print(status.ok)
                                print(status.status)
                                print(status.stderr)

                        gpg.delete_keys(keyimported)

                        # Delete the no-encrypted file
                        if clean == True and status.ok == True:
                                os.remove(nametar)
                except: 
                        raise ValueError(usermessage.errormsg(__name__,archive.__name__,__file__,__copyright__,
                                'FAILURE of the encryption. Please check the key file',job.log))
                
################################################################################
## Decrypt an EZ-InSAR archive
################################################################################
def decrypt_archive(input, 
        private_key, 
        output: Optional[Union[None, str]] = None, 
        clean: Optional[bool] = True, 
        verbose: Optional[bool] = True): 
        """Descrypt an EZ-InSAR encrypted archive

        The function allows to decrypt an encrypted EZ-InSAR archive.

        Args: 
                input (str): Path of the EZ-InSAR archive
                private_key (str): Private key used
                output (str): Output path 
                clean (bool): Clean the archive file
                verbose (bool): Verbose mode

        """
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,decrypt_archive.__name__,__file__,__copyright__,
                        'verbose','True or False',None,None))

        usermessage.openingmsg(__name__,decrypt_archive.__name__,__file__,__copyright__,'Create a .tar archive for long-term storage',None,verbose)

        import gnupg
        gpg = gnupg.GPG()
        import getpass

        # Check if the file is present
        if not os.path.isfile(input):
                raise ValueError(usermessage.errormsg(__name__,decrypt_archive.__name__,__file__,__copyright__,
                        'The encrypted file has not been found.',None))
        if not '.gpg' in input:
                raise ValueError(usermessage.errormsg(__name__,decrypt_archive.__name__,__file__,__copyright__,
                        'The input file is not encrypted.',None))

        # Ask the password
        pswd = ''
        while pswd == '':
                pswd = getpass.getpass('Password [empty]: ')

        # import the key
        if not os.path.isfile(private_key):
                raise ValueError(usermessage.errormsg(__name__,decrypt_archive.__name__,__file__,__copyright__,
                        'Impossible to find the private key.',None))
        
        # Decrypt the file
        try: 
                with open(private_key) as f:
                        key_data = f.read()
                        import_result = gpg.import_keys(key_data)
                keyimported = import_result.results[0]['fingerprint']

                if output == None:
                        output = input.replace('.gpg','')

                with open(input, 'rb') as f:
                        status = gpg.decrypt_file(f,
                                passphrase=pswd,
                                always_trust = True,
                                output=output,
                        )

                if verbose == True: 
                        print(status.ok)
                        print(status.status)
                        print(status.stderr)

                gpg.delete_keys(keyimported, True, passphrase=pswd)
                gpg.delete_keys(keyimported)

                if clean == True and status.ok == True: 
                        os.remove(input)
        
        except:
                raise ValueError(usermessage.errormsg(__name__,decrypt_archive.__name__,__file__,__copyright__,
                                'FAILURE of the decryption. Please check the key file',None))