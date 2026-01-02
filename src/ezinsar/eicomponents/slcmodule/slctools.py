#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage the SLCs for EZ-InSAR. 

The module allows to manage the SLCs from an `EIjob`. 
    
    (From `ezinsar` package)

Example: 
        Each function can directly used in Python scripts or/and a Python terminal::

                >>> # Import the EZ-InSAR packages
                >>> import ezinsar.job as ez
                >>> from ezinsar.eicomponents import slctools
                >>> # Create the job by defining the polarisation and the satellite mode
                >>> job = ez.EIjob(verbose=True,polarisation=['VV','VH'],satmode='IW',roi='ROI.shp')
                >>> # Create a Sentinel-1 list of SLCs from the Copernicus server
                >>> job = slctools.initiateSLC(job)

Changelog: 
        * 3.2.1: Various changes, Aug. 2025, Alexis Hrysiewicz 
                * New functions
                * New implementation of S1 orbit files
                * Download of ETAD files for Sentinel-1 
                * Add the option to check the availability for GEODES
        * 3.1.0: Various changes, Feb. 2024, Alexis Hrysiewicz 
                * Start the migration of scripts into the APIs. 
                * Fixes for the writeSLClisttokmz function
                * Add the yearly and 2yearly options for SLC donwloading
                * Add the compatibility between the SLC lists
                * Add the support of RADARSAT-2
                * Start the support of RADARSAT-1
                * Add the support of COSMO-SkyMed
                * Add the support of COSMO-SkyMed Second Generation
                * Add the support of SAOCOM SM data
                * New function: unzipSLC (method for EZInSAR job)
                * Add the quicklook in the KMZ files
                * Finalise the checking function
        * 3.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import os
import numpy as np
import pandas as pd 
from shapely.wkt import loads
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import requests
from zipfile import ZipFile
from clint.textui import progress
from datetime import datetime, timedelta
import multiprocessing
import copy 
from shapely import ops

import simplekml
import shutil
import glob
import zipfile
from typing import Optional, Union
import time

## From EZ-InSAR
from ezinsar import constants
from ezinsar import usermessage
from ezinsar.eicomponents.sensor.s1module import s1slctools, s1orbits, s1ETAD
from ezinsar.eicomponents.sensor.tsxmodule import tsxslctools
from ezinsar.eicomponents.sensor.alos2module import alos2slctools
from ezinsar.eicomponents.sensor.rsat2module import rsat2slctools
from ezinsar.eicomponents.sensor.rsatmodule import rsatslctools
from ezinsar.eicomponents.sensor.cskmodule import cskslctools
from ezinsar.eicomponents.sensor.csksgmodule import csksgslctools
from ezinsar.eicomponents.templatevar import listSLCempty

try: 
        from ezinsarnisarmodule import nisarslctools
except: 
        a = 'dummy'
        # usermessage.warningmsg(__name__,__name__,__file__,'The used EZ-InSAR version does not contain the module for NISAR processor. This message will not be visible in the log.',None,True)
try: 
        from ezinsarsaocommodule import saocomslctools
except: 
        a = 'dummy'
        # usermessage.warningmsg(__name__,__name__,__file__,'The used EZ-InSAR version does not contain the module for NISAR processor. This message will not be visible in the log.',None,True)

from ezinsar.api import ASFapi, Copernicusapi, GEODESapi, EarthDATAapi

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""
################################################################################
## Function to unzip the SLC
################################################################################
def unzipSLC(job,
        rename: Optional[bool] = True, 
        worker: Optional[int] = 1, 
        modeforce: Optional[bool] = False, 
        clean: Optional[bool] = False, 
        verbose: Optional[bool] = None, 
        log: Optional[bool] = None, 
        ):
        """Unzip SLC files for an EZ-InSAR job. 

        The function will unzip the SLC files, for an `EIjob`. 

        Args:
                job (`EIjob`): EZ-InSAR job
                rename (bool): Remaning the directory
                worker (int): Number of parallel unzipping
                modeforce (bool): Force the unzipping if it exists
                clean (bool): Delete the .zip file after inflating
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (bool): log [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                `EIjob`: Return an EZ-InSAR class
        
        """
        
        ## Check the input paramaters
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,unzipfile.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if log == None:
                log = job.log
        if not log == None: 
                if not isinstance(log,str):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,unzipfile.__name__,__file__,__copyright__,
                                'log','str',log))
        
        if (not isinstance(rename,bool)):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,unzipfile.__name__,__file__,__copyright__,
                        'morenamede','bool',job.log))

        if (not isinstance(clean,bool)):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,unzipfile.__name__,__file__,__copyright__,
                        'clean','bool',job.log))

        if (not isinstance(worker,int)):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,unzipfile.__name__,__file__,__copyright__,
                        'worker','int',job.log))
        
        usermessage.openingmsg(__name__,unzipSLC.__name__,__file__,__copyright__,'Unzip the SLC files',log,verbose)

        ## Detect the list of file(s)
        usermessage.ezprint('Detect the .zip file(s) in %s:' %(job.pathSLC),log,verbose)
        listzip = glob.glob(job.pathSLC+os.sep+'*')
        for li in listzip:
                usermessage.ezprint('\t%s' %(li.split(os.sep)[-1]),log,verbose)
        usermessage.ezprint('\tdone',log,verbose)

        ## Create the directory name(s) and check if required
        usermessage.ezprint('Create the name directory(ies):',log,verbose)

        listname = []
        checkunzip = []
        listzipneeded = []
        for li in listzip:

                if li.split(os.sep)[-1].endswith('.zip'): 
                        if li.split(os.sep)[-1].startswith('S1') and 'SLC' in li.split(os.sep)[-1]:
                                usermessage.warningmsg(__name__,unzipSLC.__name__,__file__,'Sentinel-1 .zip file has been detected. EZ-InSAR works better with the .zip: unzipping is not required',log,verbose)
                                checkunzip.append(False)
                                listname.append(None)

                        else:
                                with ZipFile(li, 'r') as zipObj:
                                        check = False
                                        h = 0
                                        while check == False and h < len(list(zipObj.namelist())):

                                                if ('CSKS' in list(zipObj.namelist())[h]) and list(zipObj.namelist())[h].endswith('.h5'):
                                                        check = True
                                                        nametmp = list(zipObj.namelist())[h].split(os.sep)[-1].split('.')[0]
                                                        usermessage.ezprint('\tCSK data detected for %s: new name => %s' % (li.split(os.sep)[-1], nametmp),log,verbose)

                                                elif ('CSG' in list(zipObj.namelist())[h]) and list(zipObj.namelist())[h].endswith('.h5'):
                                                        check = True
                                                        nametmp = list(zipObj.namelist())[h].split(os.sep)[-1].split('.')[0]
                                                        usermessage.ezprint('\tCSK Second Generation data detected for %s: new name => %s' % (li.split(os.sep)[-1], nametmp),log,verbose)

                                                elif ('CSG' in list(zipObj.namelist())[h]) and list(zipObj.namelist())[h].endswith('.h5'):
                                                        check = True
                                                        nametmp = list(zipObj.namelist())[h].split(os.sep)[-1].split('.')[0]
                                                        usermessage.ezprint('\tCSK Second Generation data detected for %s: new name => %s' % (li.split(os.sep)[-1], nametmp),log,verbose)
                                                        
                                                h = h + 1
                                        
                                        if check == False:
                                                nametmp = li.split(os.sep)[-1].split('.')[0]
                                                usermessage.ezprint('\tNo satellite detected for %s: new name => %s' % (li.split(os.sep)[-1], nametmp),log,verbose)

                                listname.append(job.pathSLC+os.sep+nametmp)
                                if not os.path.isdir(job.pathSLC+os.sep+nametmp):
                                        checkunzip.append(True)
                                        listzipneeded.append(li)
                                else:   
                                        if modeforce == False:
                                                checkunzip.append(False)
                                        else:   
                                                listzipneeded.append(li)
                                                checkunzip.append(True)

                else: 
                        if 'EOL1ASARSAO' in li.split(os.sep)[-1]: 
                                usermessage.ezprint('\tSAOCOM directory %s' % (li.split(os.sep)[-1]),log,verbose)
                                listzipsec = glob.glob(li+os.sep+'*.zip')

                                for lisec in listzipsec:
                                        with ZipFile(lisec, 'r') as zipObj:
                                                if ('S1' in lisec) and ('L1A' in lisec):
                                                        check = True
                                                        nametmp = lisec.split(os.sep)[-1].replace('.zip','')
                                                        usermessage.ezprint('\t\tSAOCOM zip file detected for %s: new name => %s' % (lisec.split(os.sep)[-1], nametmp),log,verbose)


                                        if check == False:
                                                nametmp = lisec.split(os.sep)[-1].split('.')[0]
                                                usermessage.ezprint('\tNo satellite detected for %s: new name => %s' % (lisec.split(os.sep)[-1], nametmp),log,verbose)

                                        listname.append(li+os.sep+nametmp)
                                        listzipneeded.append(lisec)
                                        if not os.path.isdir(li+os.sep+nametmp):
                                                checkunzip.append(True)
                                        else:   
                                                if modeforce == False:
                                                        checkunzip.append(False)
                                                else:
                                                        listzipneeded.append(lisec)
                                                        checkunzip.append(True)

                        elif 'AL1_' in li.split(os.sep)[-1]: 
                                usermessage.ezprint('\tALOS dataset from ESA: %s' % (li.split(os.sep)[-1]),log,verbose)
                                with ZipFile(li, 'r') as zipObj:
                                        check = True
                                        nametmp = li.split(os.sep)[-1].replace('.ZIP','')
                                        usermessage.ezprint('\t\tALOS zip file detected for %s: new name => %s' % (li.split(os.sep)[-1], nametmp),log,verbose)

                        
                                listname.append(os.path.dirname(li)+os.sep+nametmp)
                                listzipneeded.append(li)
                                if not os.path.isdir(li+os.sep+nametmp):
                                        checkunzip.append(True)
                                else:   
                                        if modeforce == False:
                                                checkunzip.append(False)
                                        else:
                                                listzipneeded.append(lisec)
                                                checkunzip.append(True)
        usermessage.ezprint('\tdone',log,verbose)       

        ## Create the directory name(s) and check if required
        usermessage.ezprint('Unzip the files with %s worker(s):' % (worker),log,verbose)

        def unzipfile(fi,dirout,check,clean,verbose,log):
                if check == True:
                        usermessage.ezprint('\tUnzip %s in %s: in progress' % (fi,dirout),log,verbose)
                        with ZipFile(fi, 'r') as zipObj:
                                zipObj.extractall(path=dirout)

                        if clean:
                                os.remove(fi)

                else:
                        usermessage.ezprint('\tUnzip %s in %s: NO REQUIRED' % (fi,dirout),log,verbose)

        maxjob = len(checkunzip) - 1
        i = 0
        while i <= maxjob:
                for it in np.arange(i,i+worker,1):
                        if it <= maxjob:
                                exec("p%s = multiprocessing.Process(target=unzipfile, args=(listzipneeded[%s], listname[%s], checkunzip[%s], clean, verbose, log))" % (it,it,it,it) )
                                exec('p%s.start()' % (it))

                for it in np.arange(i,i+worker,1):
                        if it <= maxjob:
                                exec('p%s.join()' % (it))
                        i = i + 1

        ## Fix regarding unzip in directory 
        for li in listname:
                entry = glob.glob(li+os.sep+'*')
                if (len(entry) == 1) and (os.path.isdir(entry[0])):
                        subentry = glob.glob(entry[0]+os.sep+'*')
                        for subentryi in subentry:
                                os.rename(subentryi,li+os.sep+subentryi.split(os.sep)[-1])
                        shutil.rmtree(entry[0])
        
        usermessage.ezprint('\tdone',log,verbose)

        return job
  
################################################################################
## Function to create the SLC list for EZ-InSAR
################################################################################
def initiateSLC(job,
        verbose: Optional[bool] = None, 
        mode: Optional[str] = 'online', 
        beam: Optional[str] = None,
        frame: Optional[int] = None,
        server: Optional[str] = constants.__S1server__, 
        satellite: Optional[str] = 'S1', 
        file: Optional[Union[str,None]] = None, 
        ):
        """Initialise the SLC list for an EZ-InSAR job. 

        The function initialises the SLC list, for an `EIjob`, from the data online available or stored in the disks. 

        Note: 
                The log paramater will be extracted from the job. 

        Args:
                job (`EIjob`): EZ-InSAR job
                mode (str, Optional): mode of the SLC detection [Default: online]. Can be ``online``, ``list``, ``onfile``. 
                server (str, Optional): Server for the ``online`` mode [Default: ``Copernicus``]. Can be ``Copernicus`` or ``ASF``. 
                satellite (str): Name of the satellite for the ``onfile`` mode. [Default: ``S1``].
                file (str): Fullpath of the file for the ``list`` mode
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                `EIjob`: Return an EZ-InSAR class
        
        """
        
        ## Check the input paramaters
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,initiateSLC.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        
        if not (isinstance(mode,str) and mode in ['online','list','onfile']):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,initiateSLC.__name__,__file__,__copyright__,
                        'mode','"online" or "list" or "onfile"',job.log))
        
        usermessage.openingmsg(__name__,initiateSLC.__name__,__file__,__copyright__,'Create the SLC list for EZ-InSAR',job.log,verbose)

        ## Run the initialisation regarding the satellites
        if not job.satellite == None:
                if mode == 'online': 
                        if job.satellite == 'S1':
                                s1slctools.initiateSLC(job,verbose=verbose,mode=mode,satellite=satellite,server=server)
                        elif job.satellite in 'RSAT':
                                rsatslctools.initiateSLC(job,beam=beam,verbose=verbose,mode=mode,server=server,frame=frame)
                        elif job.satellite in ['ALOS2','ALOS']:
                                alos2slctools.initiateSLC(job,beam=beam,verbose=verbose,mode=mode,server=server,frame=frame)
                        elif job.satellite in ['NISAR']:
                                nisarslctools.initiateSLC(job,verbose=verbose,mode=mode,server=server)
                elif mode == 'list': 
                        job = loadSLClist(job,verbose=verbose,file=file)
                elif mode == 'onfile': 
                        if job.satellite == 'S1':
                                s1slctools.initiateSLC(job,verbose=verbose,mode=mode,satellite=satellite,server=server)
                        elif job.satellite in ['TSX','PAZ']:
                                tsxslctools.initiateSLC(job,verbose=verbose,mode=mode)
                        elif job.satellite in ['ALOS2','ALOS']:
                                alos2slctools.initiateSLC(job,verbose=verbose,mode=mode)
                        elif job.satellite in ['NISAR']:
                                nisarslctools.initiateSLC(job,verbose=verbose,mode=mode)
                        elif job.satellite in ['RSAT2']:
                                rsat2slctools.initiateSLC(job,verbose=verbose,mode=mode)
                        elif job.satellite in ['RSAT']:
                                rsatslctools.initiateSLC(job,verbose=verbose,mode=mode)
                        elif job.satellite in ['CSK']:
                                cskslctools.initiateSLC(job,verbose=verbose,mode=mode)
                        elif job.satellite in ['CSKSG']:
                                csksgslctools.initiateSLC(job,verbose=verbose,mode=mode)
                        elif job.satellite in ['SAOCOM']:
                                saocomslctools.initiateSLC(job,verbose=verbose,mode=mode)
                        else:
                                raise ValueError(usermessage.errormsg(__name__,initiateSLC.__name__,__file__,__copyright__,'The satellite is not defined.',job.log))
        else:
                raise ValueError(usermessage.errormsg(__name__,initiateSLC.__name__,__file__,__copyright__,'The satellite is not defined.',job.log))

        ## Fast check of the SLC list 
        job.checkSLClist(verbose=False)

        return job

################################################################################
## Function to print the SLC list for EZ-InSAR
################################################################################
def printSLClist(job,
        verbose: Optional[bool] = True, 
        ):
        """Print the SLC list from an EZ-InSAR job. 

        The function prints the SLC list, from an `EIjob`. 

        Note: 
                The log paramater will be extracted from the job.

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `True`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                `EIjob`: Return an EZ-InSAR class
        
        """
        # Check the input paramaters
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,printSLClist.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))

        usermessage.openingmsg(__name__,printSLClist.__name__,__file__,__copyright__,'Print the SLC list for EZ-InSAR',job.log,verbose)

        # Print the SLC lists
        keys = list(job.SLClist.keys())
        for idx, value in enumerate(job.SLClist['Name']):
                usermessage.ezprint('For the SLC: %s' % (job.SLClist['Name'][idx]),job.log,verbose)
                for keyi in keys: 
                        usermessage.ezprint('\t%s: %s' %(keyi,job.SLClist[keyi][idx]),job.log,verbose)

        # Extract the unique dates
        listdate = []
        for datei in job.SLClist['Date1']:
                listdate.append(datei.split('T')[0])
        
        listdate = np.unique(listdate)
        usermessage.ezprint('\nSummary of dates:',job.log,verbose)
        for datei in listdate:
                usermessage.ezprint('\t%s' % (datei),job.log,verbose)

        # Print the final message
        usermessage.ezprint('\nThere are %d slices/frames/files for %d unique dates.' %(len(job.SLClist['Name']),len(listdate)),job.log,verbose)    

        return job

################################################################################
## Function to save the SLC list for EZ-InSAR into a .csv file
################################################################################
def saveSLClist(job,
        verbose: Optional[bool] = None, 
        file: Optional[str] = 'SLClist', 
        ):
        """Save the SLC list from an EZ-InSAR job. 

        The function saves the SLC list, from an `EIjob`.   

        Note: 
                The log paramater will be extracted from the job.

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                file (str): Fullpath of the .csv file [Default: ``SLClist``]

        Returns:
                `EIjob`: Return an EZ-InSAR class

        """
        # Check the input parameters
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,saveSLClist.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        
        if not isinstance(file,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,saveSLClist.__name__,__file__,__copyright__,
                        'file','str',job.log))
        
        usermessage.openingmsg(__name__,saveSLClist.__name__,__file__,__copyright__,'Save the SLC list for EZ-InSAR',job.log,verbose)

        # Save the list 
        if not file.endswith('.csv'): 
                file = file + '.csv'
        job.SLClist.to_csv(file,index=False)

        usermessage.ezprint('The SLC list has been saved into %s' % (file),job.log,verbose)

        return job

################################################################################
## Function to load the SLC list for EZ-InSAR from a .csv file
################################################################################
def loadSLClist(job,
        verbose: Optional[bool] = None, 
        file: Optional[str] = 'SLC.list.csv', 
        ):
        """Load a SLC list into an EZ-InSAR job. 

        The function loads the SLC list into an `EIjob`.  

        Note: 
                The log paramater will be extracted from the job. 

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                file (str): Fullpath of the .csv file [Default: ``SLClist``]

        Returns:
                `EIjob`: Return an EZ-InSAR class

        """
        # Check the input parameters
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,loadSLClist.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        
        if not isinstance(file,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,loadSLClist.__name__,__file__,__copyright__,
                        'file','str',job.log))
        
        usermessage.openingmsg(__name__,loadSLClist.__name__,__file__,__copyright__,'Load a SLC list for EZ-InSAR',job.log,verbose)

        # Load the list 
        if os.path.isfile(file): 
                datatmp = pd.read_csv(file)
        else:
                raise ValueError(usermessage.errormsg(__name__,loadSLClist.__name__,__file__,__copyright__,'Impossible to find the file: %s.' % (file),job.log))

        types = list(datatmp.dtypes)
        for idx, value in enumerate(list(datatmp.keys())):
                if types[idx] == 'float64' and value != 'SizeMB': 
                        posnan = np.where(np.isnan(datatmp[value]))[0]
                        datatmp[value] = datatmp[value].astype('object')
                        datatmp[value][posnan] = None

        job.SLClist = datatmp

        # Check the list 
        job = checkSLClist(job,verbose=False)

        return job 

################################################################################
## Function to check the SLC list for EZ-InSAR
################################################################################
def checkSLClist(job,
        verbose: Optional[bool] = None, 
        mode: Optional[Union[str,None]] = 'low', 
        checkOnline: Optional[bool] = False,  
        ):
        """Check the SLC list for an EZ-InSAR job. 

        The function checks the SLC list for an `EIjob`.  

        Note: 
                The log paramater will be extracted from the job. 

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                mode (str, Optional): mode of checking [Default: ``low``]. Can be ``low`` or ``high``. The ``low`` mode only displays errors while the ``high`` can induce errors, if the variables are not correct.
                checkOnline (bool): verbose [Default: `False`]. For the GEODES server, EZ-InSAR will check if the data is online

        Returns:
                `EIjob`: Return an EZ-InSAR class

        Todo:
                - Check the SLC extent and polarisations

        """
        ## Check the input parameters
        job.check(mode='high',verbose=False)

        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,checkSLClist.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        if mode == None:
                mode = 'high'
        if not (isinstance(mode,str) and mode in ['high','low']):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,checkSLClist.__name__,__file__,__copyright__,
                        'mode','high, low or None',job.log))
        
        usermessage.openingmsg(__name__,checkSLClist.__name__,__file__,__copyright__,'Check a SLC list for EZ-InSAR',job.log,verbose)

        ##################################################
        ## Check if the SLC list is consistent with the last listSLC keys
        keys1 = list(job.SLClist.keys())

        listSLCtemplate = copy.deepcopy(listSLCempty)

        keys2 = list(listSLCtemplate.keys())
 
        # Add the keys not available in the job SLC list
        template_empty = []
        for idx, imgi in enumerate(job.SLClist['Name']):
                template_empty.append(None)

        for ki in keys2:
                if not ki in keys1: 
                        usermessage.warningmsg(__name__,checkSLClist.__name__,__file__,'The SLC parameter %s is not available in the SLC list. It will be added by None values' % (ki),job.log,job.verbose)
                        job.SLClist[ki] = template_empty

        # Delete the keys not available in the job SLC list
        for ki in keys1:
                if not ki in keys2: 
                        usermessage.warningmsg(__name__,checkSLClist.__name__,__file__,'The SLC parameter %s is out-of-date in the SLC list. It will be deleted' % (ki),job.log,job.verbose)
                        job.SLClist.drop(columns=[ki], inplace=True)

        ##################################################
        ## Check if the SLC list is here
        satpass_tmp = None
        relorbit_tmp = None
        try: 
                len(np.unique(job.SLClist['RelativeOrbit'])) 
        except: 
                usermessage.warningmsg(__name__,checkSLClist.__name__,__file__,'No SLC list inside the EZ-InSAR',job.log,verbose)
                return job
        
        ##################################################
        ## Dates duplications
        if not len(np.unique(job.SLClist['Date1'])) == len(job.SLClist['Date1']):
                if mode == 'high':
                        raise ValueError(usermessage.errormsg(__name__,checkSLClist.__name__,__file__,__copyright__,'Some files are duplicated. It can be due to several re-processing (i.e., SAR processing, etc.) of Sentine-1 data. Please keep the files because this will cause a error during the SAR/InSAR processing.',job.log))
                else:
                        usermessage.warningmsg(__name__,checkSLClist.__name__,__file__,'Some files are duplicated. It can be due to several re-processing (i.e., SAR processing, etc.) of Sentine-1 data. Please keep the files because this will cause a error during the SAR/InSAR processing.',job.log,verbose)
        ##################################################
        ## For the satellite 
        usermessage.ezprint('Check the satellite:',job.log,verbose)
        if len(np.unique(job.SLClist['Platform'])) == 1:
                usermessage.ezprint('\tDetection of a single platform: %s' % (job.SLClist['Platform'][0]),job.log,verbose)
        else:   
                if ('TSX' in np.unique(job.SLClist['Platform'])) or ('PAZ' in np.unique(job.SLClist['Platform'])) or ('TDM' in np.unique(job.SLClist['Platform'])):
                        usermessage.ezprint('\tDetection of several platforms: TSX / TDM / PAZ. EZ-InSAR is compatible with this.',job.log,verbose)

        if (not job.satellite == 'TSX') and (not job.satellite == 'PAZ'):
                # Check the local files
                listele = []
                for li in glob.glob(job.pathSLC+os.sep+'*'):
                        listele.append(len(li.split('_')))
                        
                if listele: 
                        if not len(np.unique(listele))==1:
                                usermessage.warningmsg(__name__,checkSLClist.__name__,__file__,'EZ-InSAR has detected several types of filenames in %s. This can be a problem (i.e., several satellite files). Please check the directory.' % (job.pathSLC),job.log,verbose)

        ##################################################
        ## For the relative orbit
        usermessage.ezprint('\nCheck the relative orbit:',job.log,verbose)
        if len(np.unique(job.SLClist['RelativeOrbit'])) == 1: 
                usermessage.ezprint('\tDetection of a single relative orbit',job.log,verbose)
                if np.unique(job.SLClist['RelativeOrbit'])[0] == job.relorbit: 
                        usermessage.ezprint('\tThe number is consistent with the EZ-InSAR job: %s' % (job.SLClist['RelativeOrbit'][0]),job.log,verbose)
                else:
                        if mode == 'high':
                                raise ValueError(usermessage.errormsg(__name__,checkSLClist.__name__,__file__,__copyright__,'The relative orbit is not consistent with the EZ-InSAR job.',job.log))
                        else:
                                usermessage.warningmsg(__name__,checkSLClist.__name__,__file__,'The relative orbit is not consistent with the EZ-InSAR job.',job.log,verbose)
                                relorbit_tmp = np.unique(job.SLClist['RelativeOrbit'])[0]
        else:                   
                if mode == 'high':
                        raise ValueError(usermessage.errormsg(__name__,checkSLClist.__name__,__file__,__copyright__,'Several relative orbits have been detected.',job.log))
                else:
                        usermessage.warningmsg(__name__,checkSLClist.__name__,__file__,'Several relative orbits have been detected.',job.log,verbose)

        ##################################################
        # For the satellite pass
        usermessage.ezprint('\nCheck the orbit direction:',job.log,verbose)
        if len(np.unique(job.SLClist['OrbitDirection'])) == 1: 
                usermessage.ezprint('\tDetection of a single orbit direction',job.log,verbose)
                if np.unique(job.SLClist['OrbitDirection'])[0] == job.satpass: 
                        usermessage.ezprint('\tThe direction is consistent with the EZ-InSAR job: %s' % (job.SLClist['OrbitDirection'][0]),job.log,verbose)
                else:
                        if mode == 'high':
                                raise ValueError(usermessage.errormsg(__name__,checkSLClist.__name__,__file__,__copyright__,'The orbit direction is not consistent with the EZ-InSAR job.',job.log))
                        else:
                                usermessage.warningmsg(__name__,checkSLClist.__name__,__file__,'The orbit direction is not consistent with the EZ-InSAR job.',job.log,verbose)
                                satpass_tmp = np.unique(job.SLClist['OrbitDirection'])[0]
        else:                   
                if mode == 'high':
                        raise ValueError(usermessage.errormsg(__name__,checkSLClist.__name__,__file__,__copyright__,'Several orbit directions have been detected.',job.log))
                else:
                        usermessage.warningmsg(__name__,checkSLClist.__name__,__file__,'Several orbit directions have been detected.',job.log,verbose)
        
        ##################################################
        # For the levels
        usermessage.ezprint('\nCheck the processing levels:',job.log,verbose)
        if not len(np.unique(job.SLClist['ProcessingLevel'])) == 1:
                if mode == 'high':
                        raise ValueError(usermessage.errormsg(__name__,checkSLClist.__name__,__file__,__copyright__,'Several processing levels have been detected.',job.log))
                else:
                        usermessage.warningmsg(__name__,checkSLClist.__name__,__file__,'Several processing levels have been detected.',job.log,verbose)
        else:
                usermessage.ezprint('\t%s' % (job.SLClist['ProcessingLevel'][0]),job.log,verbose)

        ##################################################
        # Polarisation
        usermessage.ezprint('\nCheck the polarisations:',job.log,verbose)
        pol1 = []
        pol2 = []
        pol3 = []
        pol4 = []
        nbpol = []
        check = True
        for idx, namei in enumerate(job.SLClist['Name']):
                pol1.append(job.SLClist['Polarisation1'][idx])
                pol2.append(job.SLClist['Polarisation2'][idx])
                pol3.append(job.SLClist['Polarisation3'][idx])
                pol4.append(job.SLClist['Polarisation4'][idx])

                tmp =[job.SLClist['Polarisation1'][idx], job.SLClist['Polarisation2'][idx], job.SLClist['Polarisation3'][idx], job.SLClist['Polarisation4'][idx]]
                tmp = list(filter(lambda a: a != 'None', tmp))
                tmp = list(filter(lambda a: a != None, tmp))
                nbpol.append(len(tmp))
                
                for poli in job.polarisation: 
                        if not poli in tmp: 
                                usermessage.warningmsg(__name__,checkSLClist.__name__,__file__,'The SLC file %s has not the polarisation %s required by the EZ-InSAR job (%s)' % (namei,poli,job.polarisation),job.log,verbose)
                                check = False

        if not len(np.unique(nbpol)) == 1: 
                usermessage.warningmsg(__name__,checkSLClist.__name__,__file__,'The number of polarisations is not constant for all files. This can be the use of different acquisition mode.',job.log,verbose)
                check = False
        if check == True: 
              usermessage.ezprint('\tOkay',job.log,verbose)  

        ##################################################
        # Extent
        usermessage.ezprint('\nCheck the SLC extents:',job.log,verbose)
        check = True
        for idx, poly in enumerate(job.SLClist['PolyFrame']):
                if loads(poly).intersection(job.roi).area/job.roi.area*100 == 0:
                        usermessage.warningmsg(__name__,checkSLClist.__name__,__file__,'The SLC %s does not intersect the Region of Interest. It can be a problem.' % (job.SLClist['Name'][idx]),job.log,verbose)
                        check = False
        if check == True: 
              usermessage.ezprint('\tOkay',job.log,verbose)  

        ##################################################
        # If stored 
        pd.options.mode.chained_assignment = None               
        usermessage.ezprint('\nCheck the images have been stored:...',job.log,verbose)
        for idx, imgi in enumerate(job.SLClist['Name']):
                if os.path.isfile(job.pathSLC+os.sep+job.SLClist['Name'][idx]) or os.path.isdir(job.pathSLC+os.sep+job.SLClist['Name'][idx]) or os.path.isdir(job.pathSLC+os.sep+job.SLClist['Name'][idx].replace('.zip','.SAFE')):
                        job.SLClist.loc[idx, 'Stored'] = True  
                else:
                        job.SLClist.loc[idx, 'Stored'] = False  

        ## Check if the data is online 
        if job.SLClist['Server'][0] == 'GEODES' and checkOnline == True: 
                usermessage.ezprint('\nDetection of the GEODES server, EZ-InSAR can check if the data is online (or on tape):...',job.log,verbose)
                for idx, imgi in job.SLClist.iterrows():
                        if imgi['Stored'] == False: 
                                job.SLClist.loc[idx, 'IsOnline'] = GEODESapi.checkavailabity(imgi, 
                                                                        password = 'dummy',
                                                                        verbose = verbose,
                                                                        log = job.log, 
                                                                        )

        ##################################################
        # If processed
        if not job.coregistration == None:
                usermessage.ezprint('\tCheck the images have been processed for the coregistration:...',job.log,verbose)

                for idx, imgi in enumerate(job.SLClist['Date1']):
                        dslci = imgi.split('T')[0].replace('-','')
                        
                        testcheck = False
                        if job.coregistration.processor == 'isce2':
                                if os.path.isdir(job.coregistration.pathstack+os.sep+'SLC'+os.sep+dslci):
                                        testcheck = True
                        elif job.coregistration.processor == 'gamma':
                                if os.path.isfile(job.coregistration.pathstack+os.sep+'rslc_'+job.coregistration.polarisation[0].lower()+os.sep+dslci+'.'+job.coregistration.polarisation[0].lower()+'.rslc.par'):
                                        testcheck = True
                        elif job.coregistration.processor == 'doris':
                                if os.path.isfile(job.coregistration.pathstack+os.sep+'rslc_'+job.coregistration.polarisation[0].lower()+os.sep+dslci+'.'+job.coregistration.polarisation[0].lower()+'.rslc.res'):
                                        testcheck = True
                        
                        if testcheck == True:
                                job.SLClist.loc[idx, 'Processed'] = True 
                        else:
                                job.SLClist.loc[idx, 'Processed'] = False 

        ##################################################
        if not job.intstack == None:
                usermessage.ezprint('\tCheck the images have been processed for the intstack:...',job.log,verbose)
                
                for idx, imgi in enumerate(job.SLClist['Date1']):
                        dslci = imgi.split('T')[0].replace('-','')

                        testcheck = False
                        if job.coregistration.processor == 'snap':
                                if glob.glob(job.intstack.workdirectory+os.sep+'geotiff'+os.sep+dslci+'*.tif'):
                                        testcheck = True

                        if testcheck == True:
                                job.SLClist.loc[idx, 'Processed'] = True 
                        else:
                                job.SLClist.loc[idx, 'Processed'] = False 
                
        pd.options.mode.chained_assignment = 'warn'
        usermessage.ezprint('\tDone',job.log,verbose)

        ##################################################
        ## Modification of the job
        if (not relorbit_tmp == None): 
                usermessage.warningmsg(__name__,checkSLClist.__name__,__file__,'EZ-InSAR will modify the relorbit parameter: %s.' % (relorbit_tmp),job.log,verbose)
                job.relorbit = int(relorbit_tmp)

        if (not satpass_tmp == None): 
                usermessage.warningmsg(__name__,checkSLClist.__name__,__file__,'EZ-InSAR will modify the satpass parameter: %s.' % (satpass_tmp),job.log,verbose)
                job.satpass = satpass_tmp

        return job

################################################################################
## Function to display the SLC list on a map
################################################################################
def displaySLClist(job,
        verbose: Optional[bool] = None, 
        basemap: Optional[str] = 'World_Imagery', 
        mode: Optional[str] = 'Extent',
        figure: Optional[Union[str,None]] = None, 
        ):
        """Display the SLC list with a map from an EZ-InSAR job. 

        The function displays the SLC list via a map, from an `EIjob`. 

        Note: 
                The log paramater will be extracted from the job. 

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                basemap (str): mode of the display [Default: ``World_Imagery``]. Can be ``NatGeo_World_Map``,``USA_Topo_Maps``,``World_Imagery``,``World_Physical_Map``,``World_Shaded_Relief``,``World_Street_Map``,``World_Terrain_Base``,``World_Topo_Map``
                mode (str, Optional): mode of the display [Default: ``Extent``]. Can be ``Extent`` or ``Burst``.  
                figure (str): Path of the figure to save the figure [Default: ``None``]. If ``None``, the figure will be displayed.

        Returns:
                `EIjob`: Return an EZ-InSAR class
        
        """
        ## Check the input parameters
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,displaySLClist.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        
        if not (isinstance(basemap,str) and basemap in ['NatGeo_World_Map','USA_Topo_Maps','World_Imagery','World_Physical_Map','World_Shaded_Relief','World_Street_Map','World_Terrain_Base','World_Topo_Map']):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,displaySLClist.__name__,__file__,__copyright__,
                        'basemap',"'NatGeo_World_Map','USA_Topo_Maps','World_Imagery','World_Physical_Map','World_Shaded_Relief','World_Street_Map','World_Terrain_Base','World_Topo_Map'",job.log))
        
        if not (isinstance(mode,str) and mode in ['Extent','Burst']):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,displaySLClist.__name__,__file__,__copyright__,
                        'mode',"'Extent','Burst'",job.log))
 
        usermessage.openingmsg(__name__,displaySLClist.__name__,__file__,__copyright__,'Display a map with the SLC extents of the EZ-InSAR job',job.log,verbose)

        ## Extract the extent of the map
        lonall = []
        latall = []
        for polyi in job.SLClist['PolyFrame']: 
                lon,lat = loads(polyi).exterior.xy
                lonall = lonall + list(lon)
                latall = latall + list(lat)
                
        fig = plt.figure(figsize=(8, 8))
        m = Basemap(projection='merc', resolution='f',epsg=4326, 
                        llcrnrlon = np.min(lonall)-(np.max(lonall)-np.min(lonall))*0.25,
                        llcrnrlat = np.min(latall)-(np.max(latall)-np.min(latall))*0.25,
                        urcrnrlon = np.max(lonall)+(np.max(lonall)-np.min(lonall))*0.25,
                        urcrnrlat = np.max(latall)+(np.max(latall)-np.min(latall))*0.25)       
        
        ## Plot the ROIs
        lon, lat = job.roi.exterior.xy
        m.plot(lon,lat,'-',linewidth=2,color='red',latlon=True,label='User ROI')
        m.plot([np.min(lon),np.max(lon),np.max(lon),np.min(lon),np.min(lon)],[np.min(lat),np.min(lat),np.max(lat),np.max(lat),np.min(lat)],'--',linewidth=1,color='red',latlon=True,label='ROI for EZ-InSAR')

        ## Plot the images
        if mode == 'Extent':
                for polyi in job.SLClist['PolyFrame']: 
                        lon,lat = loads(polyi).exterior.xy
                        m.plot(lon,lat,'--',linewidth=1,color='white',latlon=True)
                        
        elif mode == 'Burst':
                for idxrow, row in job.SLClist.iterrows():
                        if row['Stored'] == True: 
                                S1annoresults = s1slctools.detectS1annoatationfromxml(job.pathSLC+os.sep+row['Name'],job.polarisation[0])

                                for idx_iw, iwi in enumerate(['data_xmli1','data_xmli2','data_xmli3']): 
                                        if not S1annoresults[iwi] == None: 
                                                for idx, polyi in enumerate(S1annoresults[iwi]['burst_loc']['Polygon']): 
                                                        m.plot(polyi.exterior.xy[0],polyi.exterior.xy[1],'--',linewidth=0.5,color='white',latlon=True)

                                burst_roi = s1slctools.detection_S1burst_fromROI(job.roi,S1annoresults)
                                for polyi in burst_roi['Polygon']: 
                                        if polyi: 
                                                m.plot(polyi.exterior.xy[0],polyi.exterior.xy[1],'-',linewidth=1,color='white',latlon=True)

        ## Finalise the map 
        m.arcgisimage(service=basemap, xpixels = 2000, ypixels = 2000, verbose = verbose)
        m.drawparallels(np.linspace(np.fix(np.min(lat))-1,np.fix(np.max(lat))+1,3),labels=[1,0,0,0])
        m.drawmeridians(np.linspace(np.fix(np.min(lon))-1,np.fix(np.max(lon))+1,3),labels=[0,0,0,1])
        plt.legend()
        plt.title('Map of the EZ-InSAR SLC list for "%s"' %(job.nameJob))

        ## Export the figure
        if figure == None:
                usermessage.ezprint('\tDisplay the figure...',job.log,verbose)
                plt.show()
        else:
                plt.savefig(figure, dpi=450)
                usermessage.ezprint('\tThe figure has been saved to %s' % (figure),job.log,verbose)

        return job

################################################################################
## Function to write the SLC list into a .kmz file
################################################################################
def writeSLClisttokmz(job,
        verbose: Optional[bool] = None, 
        file: Optional[str] = 'SLClist.kmz',  
        mode: Optional[str] = 'Extent',
        ):
        """Write the SLC list into a .kmz file from an EZ-InSAR job. 

        The function writes the SLC list into a .kmz file, from an `EIjob`.

        Note: 
                The log paramater will be extracted from the job.    

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                file (str): Fullpath of the .kmz file [Default: ``SLClist.kmz``]. 
                mode (str, Optional): mode of the display [Default: ``Extent``]. Can be ``Extent`` or ``Burst``.  

        """

        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,writeSLClisttokmz.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        
        if not isinstance(file,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,writeSLClisttokmz.__name__,__file__,__copyright__,
                        'file','str',job.log))

        usermessage.openingmsg(__name__,writeSLClisttokmz.__name__,__file__,__copyright__,'Write the SLC list into a .kmz file',job.log,verbose)

        job = checkSLClist(job,verbose=False)

        if os.path.isdir(file.replace('.kmz','')):
                shutil.rmtree(file.replace('.kmz',''))
        os.mkdir(file.replace('.kmz',''))
        os.mkdir(file.replace('.kmz','')+os.sep+'SLC')

        usermessage.ezprint('Write the .kml file(s)',job.log,verbose)

        with open(file.replace('.kmz','')+os.sep+'doc.kml','w') as fout:

                fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                fout.write('<kml xmlns="http://earth.google.com/kml/2.0">\n')
                fout.write('<Document>\n')
                fout.write('<name>SLC list for EZ-InSAR job: %s></name>\n' % (job.nameJob))

                for idxrow, row in job.SLClist.iterrows():

                        if verbose:
                                print('\tfor %s' % (row['Name']))

                        kml = simplekml.Kml()
                        namei = row['Name'].split('.')[0]

                        strtext = ''
                        for keyi in row.keys():
                                if not keyi == 'Quicklook':
                                        strtext = strtext + '<p><b>%s:</b> %s</p>' % (keyi, row[keyi])
                                else:    
                                        if (not row[keyi] == None): 
                                                strtext = strtext + '<p><b>Quicklook:</b></p>'
                                                strtext = strtext + '<img src="%s" alt="%s" width="300">' % (row[keyi],row[keyi])   

                        if mode == 'Extent':

                                pol = kml.newpolygon(name='%s' % (namei),
                                        description=strtext, 
                                        outerboundaryis=zip(loads(row['PolyFrame']).exterior.xy[0],loads(row['PolyFrame']).exterior.xy[1]))
                                pol.style.linestyle.color = simplekml.Color.black
                                pol.style.linestyle.width = 2
                                pol.style.polystyle.fill = 0   

                        elif mode == 'Burst':
                                if row['Stored'] == True:
                                        S1annoresults = s1slctools.detectS1annoatationfromxml(job.pathSLC+os.sep+row['Name'],job.polarisation[0])

                                        lon = []
                                        lat = []
                                        for idx_iw, iwi in enumerate(['data_xmli1','data_xmli2','data_xmli3']): 
                                                for idx, polyi in enumerate(S1annoresults[iwi]['burst_loc']['Polygon']): 
                                                        pol = kml.newpolygon(name='IW00%s Burst %s for %s' % (idx_iw+1,idx+1,namei),
                                                                description=strtext, 
                                                                outerboundaryis=zip(polyi.exterior.xy[0],polyi.exterior.xy[1]))
                                                        pol.style.linestyle.color = simplekml.Color.black
                                                        pol.style.linestyle.width = 2
                                                        pol.style.polystyle.fill = 0   
                                else: 
                                        raise ValueError(usermessage.errormsg(__name__,writeSLClisttokmz.__name__,__file__,__copyright__,'The SLC file needs to be stored.',job.log))

                        kml.save(file.replace('.kmz','')+os.sep+'SLC'+os.sep+row['Name'].split('.')[0]+'.kml')
                
                        fout.write('<NetworkLink>\n')
                        fout.write('<name>%s</name>\n' % (row['Name']))
                        fout.write('<Link><href>%s</href></Link>\n' % ('SLC'+os.sep+row['Name'].split('.')[0]+'.kml'))
                        fout.write('</NetworkLink>\n')

                fout.write('</Document>\n') 
                fout.write('</kml>\n')

        usermessage.ezprint('Write the .kmz from the .kml file(s)',job.log,verbose)

        with zipfile.ZipFile(file.replace('.kmz','.kmz'), 'w') as zip_ref:
                for folder_name, subfolders, filenames in os.walk(file.replace('.kmz','')):
                        for filename in filenames:
                                file_path = os.path.join(folder_name, filename)
                                zip_ref.write(file_path, arcname=os.path.relpath(file_path, file.replace('.kmz','')))

        usermessage.ezprint('Delete the temporary directory',job.log,verbose)
        shutil.rmtree(file.replace('.kmz',''))

        usermessage.ezprint('The .kmz file has been written: %s' % (file),job.log,verbose)

        return job
        
################################################################################
## Function to download the SLCs
################################################################################
def downloadSLC(job,
        verbose: Optional[bool] = None, 
        index: Optional[list] = None,  
        username: Optional[str] = constants.__username__,  
        password: Optional[str] = constants.__password__, 
        burstonly: Optional[bool] = False,
        partialdownloading: Optional[Union[list,None]] = None,
        modepartial: Optional[str] = 'exclude', 
        zipping: Optional[bool] = True, 
        ):
        """Download the SLC files from the SLC list in an EZ-InSAR job. 

        The function downloads the SLC files from a SLC list in an `EIjob`.  

        Note: 
                The log paramater will be extracted from the job. 

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                index (list of int or None or str, Optional): Indices of the selected SLCs for downloading. If ``None``, all the SLCs will be downloaded. The string input can be monthly, bimonthly trimontly, 4monthly, 5monthly, and 6monthly.  
                username (str, Optional): Username of the server [Default: `constants.__username__`]. 
                password (str, Optional): password of the server [Default: `constants.__password__`].
                burstonly (bool, Optional): Download only the required bursts (only compatible with ASF server).
                partialdownloading (list, Optional): Download only selected part of the .zip file (only compatible with the Copernicus server)
                modepartial (str, Optional): Mode of the selection of the partial downloading. Can be include or exclude. (only compatible with the Copernicus server) [default: exclude]
                zipping (bool, Optional): Force the zipping of .SAFE file
        Returns:
                `EIjob`: Return an EZ-InSAR class
        
        """
        ## Check the job
        job.check(mode='high',verbose=False)
        
        ## The the SLClist 
        job = checkSLClist(job,verbose=False)

        ## Check the input parameters
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,downloadSLC.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        
        if not isinstance(burstonly,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,downloadSLC.__name__,__file__,__copyright__,
                        'burstonly','True or False',job.log))
        
        if not index == None:
                if (not isinstance(index,str)) and (not isinstance(index,list)):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,downloadSLC.__name__,__file__,__copyright__,
                                'index','list or None or str',job.log))
        
        if isinstance(index,str): 
                if not index in ['monthly','bimonthly','trimonthly','4monthly','5monthly','6monthly','yearly','2yearly']: 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,downloadSLC.__name__,__file__,__copyright__,
                                'index',"'monthly','bimonthly','trimonthly','4monthly','5monthly','6monthly','yearly','2yearly'",job.log))

        usermessage.openingmsg(__name__,downloadSLC.__name__,__file__,__copyright__,'Download the SLCs',job.log,verbose)

        access_token = None
        session = None

        listdate = []
        for datei in job.SLClist['Date1']:
                listdate.append(datei.split('T')[0])
        listdate = np.unique(listdate)

        ## Modification of the indexes
        if index in ['monthly','bimonthly','trimonthly','4monthly','5monthly','6monthly','yearly','2yearly']:
                listdatef = []
                listdateftimestamp = []
                for di in listdate:
                        a = datetime.strptime(di,'%Y-%m-%d')
                        listdatef.append(a)
                        listdateftimestamp.append(a.timestamp())
                
                newindex = []
                di = listdatef[0]
                while di <= listdatef[-1]: 
                        idx = np.argmin(np.abs(di.timestamp() - np.array(listdateftimestamp)))
                        newindex.append(idx)
                        if index == 'monthly': 
                                di = di + timedelta(days=30)
                        elif index == 'bimonthly': 
                                di = di + timedelta(days=2*30)
                        elif index == 'trimonthly': 
                                di = di + timedelta(days=3*30)
                        elif index == '4monthly': 
                                di = di + timedelta(days=4*30)
                        elif index == '5monthly': 
                                di = di + timedelta(days=5*30)
                        elif index == '6monthly': 
                                di = di + timedelta(days=6*30)
                        elif index == 'yearly': 
                                di = di + timedelta(days=365.25*1)
                        elif index == '2yearly': 
                                di = di + timedelta(days=365.25*2)
                index = []
                for idx in np.sort(np.unique(newindex)): 
                        index.append(idx)

        ## Ask the token from the Copernicus server
        if job.SLClist['Server'][0] == 'Copernicus':
                if access_token == None:
                        access_token = Copernicusapi.get_access_token(username, password)

                headers = {"Authorization": f"Bearer {access_token}"}
                session = requests.Session()
                session.headers.update(headers)

        ## Run the downloading
        for idxrow, row in job.SLClist.iterrows():
                dwrequired = False
                if (not (row['Stored'] == True or row['Processed'] == True)) and row['Status'] == 'ONLINE': 
                        if index == None: 
                                dwrequired = True 
                        else: 
                                for idxdatei, datei in enumerate(listdate): 
                                        if idxdatei in index: 
                                                if row['Date1'].split('T')[0] == datei: 
                                                        dwrequired = True

                if dwrequired == True:
                        usermessage.ezprint('The file %s is ongoing to be downloaded:...' % (row['Name']),job.log,verbose)
                else:
                        usermessage.ezprint('The file %s will not be downloaded (can be already downloaded).' % (row['Name']),job.log,verbose)

                if dwrequired == True:    
                        
                        ## For the ASF server 
                        if row['Server'] == 'ASF':
                                ASFapi.download(row,job.pathSLC,
                                        username = username, 
                                        password = password,       
                                        burstonly=burstonly,
                                        roi=job.roi,
                                        polarisation=job.polarisation,
                                        verbose=False,
                                        log=job.log,
                                        verboseprogress=True)

                        ## For the Copernicus
                        elif row['Server'] == 'Copernicus':
                                Copernicusapi.download(row,job.pathSLC,
                                        username = username, 
                                        password = password,  
                                        partialdownloading = partialdownloading, 
                                        modepartial = modepartial, 
                                        zipping = zipping,
                                        access_token = access_token, 
                                        session = session, 
                                        headers = headers, 
                                        log = job.log, 
                                        verbose = True, 
                                        verboseprogress = True,
                                        )
                                
                        ## For the GEODES
                        elif row['Server'] == 'GEODES':
                                GEODESapi.download(row,job.pathSLC,
                                        password = password,  
                                        log = job.log, 
                                        verbose = True, 
                                        verboseprogress = True,
                                        )
                        
                        ## For the EarthDATA
                        elif row['Server'] == 'EarthDATA':
                                EarthDATAapi.download(row,job.pathSLC,
                                        username = username, 
                                        password = password,  
                                        log = job.log, 
                                        verbose = True, 
                                        )
                                
                        time.sleep(constants.__sleepSLCdownload__)

        ## Modification of the SLC list because of the burstonly option
        if burstonly == True and job.satmode == 'IW':
                usermessage.warningmsg(__name__,downloadSLC.__name__,__file__,'The only-burst option requires to modify the SLC list. The modification will be made based on the donwloaded files...',job.log,verbose)
                job.initiateSLC(mode='onfile',verbose=False)

        job = checkSLClist(job,verbose=False)

        return job

################################################################################
## Function to download orbit file 
################################################################################
def downloadorbit(job,
        verbose: Optional[bool] = None, 
        server: Optional[str] = constants.__S1server__,  
        username: Optional[str] = constants.__username__,  
        password: Optional[str] = constants.__password__, 
        filebased: Optional[Union[bool,None]] = None,
        ):
        """Download the SLC orbit files from the SLC list in an EZ-InSAR job. 

        The function downloads the SLC orbit files from a SLC list in an `EIjob`.  

        Note: 
                The log paramater will be extracted from the job. 

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                server (str, Optional): Server for the ``online`` mode [Default: ``ASF``]. Can be ``ASF``.
                username (str, Optional): Username of the server [Default: `constants.__username__`]. 
                password (str, Optional): password of the server [Default: `constants.__password__`].

        Returns:
                `EIjob`: Return an EZ-InSAR class
        
        """
        ## Check the input parameters
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,downloadorbit.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        
        if not (isinstance(server,str) and server in ['ASF','Copernicus']):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,downloadorbit.__name__,__file__,__copyright__,
                        'server','"ASF" or "Copernicus"',job.log))
        
        usermessage.openingmsg(__name__,downloadorbit.__name__,__file__,__copyright__,'Download the orbits',job.log,verbose)

        ## Check the SLC list
        job.checkSLClist(verbose=False)

        ## Launch the downloading regarding the sensor
        if not job.satellite == None:
                if job.satellite in ['S1']: 
                        s1orbits.s1orbits(job=job,server=server,filebased=filebased).retrieve().download(username,password)
                else:
                        usermessage.ezprint('The selected satellite is not implemented for orbit downloading ',job.log,verbose)
        else:
                raise ValueError(usermessage.errormsg(__name__,checkSLClist.__name__,__file__,__copyright__,'The satellite is not defined.',job.log))

        return job

################################################################################
## Function to download ETAD files 
################################################################################
def downloadETAD(job,
        verbose: Optional[bool] = None, 
        username: Optional[str] = constants.__username__,  
        password: Optional[str] = constants.__password__, 
        filebased: Optional[Union[bool,None]] = None,
        ):
        """Download the ETAD Sentinel-1 files from the SLC list in an EZ-InSAR job. 

        The function downloads the ETAD Sentinel-1 files from a SLC list in an `EIjob`.  

        Note: 
                The log paramater will be extracted from the job. 

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                username (str, Optional): Username of the server [Default: `constants.__username__`]. 
                password (str, Optional): password of the server [Default: `constants.__password__`].

        Returns:
                `EIjob`: Return an EZ-InSAR class
        
        """
        ## Check the input parameters
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,downloadorbit.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        
        usermessage.openingmsg(__name__,downloadorbit.__name__,__file__,__copyright__,'Download the Sentinel-1 ETAD',job.log,verbose)

        ## Check the SLC list
        job.checkSLClist(verbose=False)

        ## Launch the downloading regarding the sensor
        if not job.satellite == None:
                if job.satellite == 'S1': 
                        s1ETAD.s1ETAD(job=job,filebased=filebased,verbose=verbose).retrieve(verbose=verbose).check(verbose=verbose).download(username,password,verbose=verbose)
                else:
                        usermessage.ezprint('The selected satellite is not compatible with ETAD downloading ',job.log,verbose)
        else:
                raise ValueError(usermessage.errormsg(__name__,checkSLClist.__name__,__file__,__copyright__,'The satellite is not defined.',job.log))

        return job

################################################################################################################################################################
################################################################################################################################################################
## Sub-Functions
################################################################################################################################################################
################################################################################################################################################################
def get_access_token(username: str, password: str) -> str:
        """Function to generate the token for the Copernicus server 

        The function will generate a token regarding the Copernicus server access.  

        Note: 
                See https://documentation.dataspace.copernicus.eu/APIs.html

        Args:
                username (str, Optional): Username of the server [Default: `constants.__username__`]. 
                password (str, Optional): password of the server [Default: `constants.__password__`].

        Returns:
                str: Token

        """
        data = {
                "client_id": "cdse-public",
                "username": username,
                "password": password,
                "grant_type": "password",
                }
        try:
                r = requests.post("https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
                data=data,
                )
                r.raise_for_status()
        except Exception as e:
                raise Exception(
                f"Access token creation failed. Reponse from the server was: {r.json()}"
                )
        return r.json()["access_token"]
         
def checklistconsistency(list,verbose=False,log=None):
        """Function to check the consistency of the SLC list with the template

        The function will check the consistency of the SLC list with the template

        Args:
                list (dict): Dictionary of SLC parameters
                verbose (bool, Optional): verbose
                log (str, Optional): log

        Returns:
                dict: Modified dictionary of SLC parameters

        """
        
        if not list['Name']: 
                raise ValueError(usermessage.errormsg(__name__,checklistconsistency.__name__,__file__,__copyright__,'The SLC list is empty.',log))
        else:
                listSLCtemplate = copy.deepcopy(listSLCempty)
                template_empty = []
                for idx, imgi in enumerate(list['Name']):
                        template_empty.append(None)

                for keyi in listSLCtemplate.keys(): 
                        if not list[keyi]:
                                usermessage.warningmsg(__name__,checklistconsistency.__name__,__file__,'The SLC parameter %s is not available in the SLC list. It will be added by None values' % (keyi),log,verbose)
                                list[keyi] = template_empty

        return list

def getextentfromSLC(job,
                verbose=True,
                log=None):
        """Estimate the extent from the list of SLCs

        The function will estimate the extent from the list of SLCs

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool, Optional): verbose
                log (str, Optional): log

        Returns:
                Polygon: New polygon. Region of interest from the job is No SLClist. 

        """
        if isinstance(job.SLClist, pd.DataFrame):
                job.checkSLClist(verbose=False)
                
                checkslc = np.unique(job.SLClist['Stored'].tolist())
                
                if True in checkslc and job.satellite == 'S1' and job.satmode == 'IW': 
                        usermessage.ezprint('\tThe bbox will be extracted from the bursts regarding the job roi (only of S1 IW).',log,verbose) 

                        polymerged = None

                        for idxrow, row in job.SLClist.iterrows():
                                if row['Stored'] == True: 
                                        usermessage.ezprint('\tRead the S1 annotations from %s' % (row['Name']),log,verbose) 
                                        S1annoresults = s1slctools.detectS1annoatationfromxml(job.pathSLC+os.sep+row['Name'],job.polarisation[0])
                                        burst_roi = s1slctools.detection_S1burst_fromROI(job.roi,S1annoresults)
                                        for polyi in burst_roi['Polygon']: 
                                                if polyi: 
                                                        if polymerged == None: 
                                                                polymerged = polyi
                                                        else: 
                                                                polymerged = polymerged.union(polyi) 
                                        
                        if polymerged == None: 
                                raise ValueError(usermessage.errormsg(__name__,getextentfromSLC.__name__,__file__,__copyright__,'Impossible to find burts from the given ROI.',log))
                        else:
                                if polymerged.intersection(job.roi).area/job.roi.area*100 < 95:
                                        usermessage.warningmsg(__name__,getextentfromSLC.__name__,__file__,'The ROI is not fuly covered by S1 bursts.',log,verbose)  

                else: 
                        usermessage.ezprint('\tThe bbox will be extracted from the full extents of slices.',log,verbose)   
                        polymerged = ops.unary_union([loads(x) for x in job.SLClist['PolyFrame']])

        else: 
                usermessage.warningmsg(__name__,getextentfromSLC.__name__,__file__,'No SLClist is the EZ-InSAR job. The ROI from the job will be returned.',log,verbose)
                polymerged = job.roi

        return polymerged