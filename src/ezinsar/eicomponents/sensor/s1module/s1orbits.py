#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage the S1 orbit files

The module allows to manage Sentinel-1 orbits
    
    (From `ezinsar` package)

Changelog:
        * 1.2.1: Bug fix, Oct. 2025, Alexis Hrysiewicz
        * 1.2.0: Initial version, Aug. 2025

"""

################################################################################
## Python packages
################################################################################
import glob
import os 
import datetime 
import numpy as np

from ezinsar import constants
from ezinsar import usermessage
from ezinsar.api import ASFapi, Copernicusapi

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Class
################################################################################
class s1orbits:
        """`s1orbits` class.

        Attributes:
                SLClist (any): EZ-InSAR SLC list
                pathorbit (str): Path of the orbit directory
                satellite (str): Satellite
                server (str): Server
                mode (str): Mode / Not used
                filebased (bool): File-based mode
                error_felching (list): List of errors for Copernicus server
                listfile (list): List of urls
                listfilename (list): List of orbit-file names        
        """

        def __init__(self,
                job=None,
                SLClist=None,
                pathorbit=None,
                server = 'Copernicus',
                satellite = 'S1',
                mode = 'auto',
                filebased=False,
                verbose = True, 
                log = None,
                ):
                """Initialise the class 

                The function initialise the class

                Args:
                        job (`EIjob`): EZ-InSAR job / Optional
                        SLClist: EZ-InSAR SLC list 
                        pathorbit: path of the orbit directory
                        server (str): Server for the 'online' mode [Default: 'Copernicus']. Can be 'Copernicus' or 'ASF'. 
                        satellite (str): Satellite [Default: 'S1'].
                        mode (str): Mode for the list creation [Default: 'auto']. Not used. 
                        filebased (bool): Download the files regarding the SLC stored [Default: False].
                        verbose (bool): verbose [Default: `True`].
                        log (str): log [Default: `None`].
                        
                Returns:
                        `s1orbits`: Return the class

                Note:
                        Please give <an EZ-InSAR job> or <a SLClist AND a pathorbit>. 

                """   

                usermessage.ezprint('Initialise the S1 orbit class',log,verbose)

                if not job == None: 
                        job.check(mode='high',verbose=False)
                        self.SLClist = job.SLClist
                        self.pathorbit = job.pathorbit
                        self.satellite = job.satellite
                else: 
                        self.SLClist = SLClist
                        self.pathorbit = pathorbit
                        self.satellite = satellite
                        
                self.server = server
                self.mode = mode

                if filebased == None: 
                        if True in self.SLClist['Stored'].tolist():
                                filebased = True
                        else: 
                                filebased = False                
                self.filebased = filebased
                
                usermessage.ezprint('\tThe SLC list contains %s frames/slices.' % (len(self.SLClist)),log,verbose)
                usermessage.ezprint('\tThe directory is %s.' % (self.pathorbit),log,verbose)
                usermessage.ezprint('\tThe satellite is %s.' % (self.satellite),log,verbose)
                usermessage.ezprint('\tThe server is %s.' % (self.server),log,verbose)
                usermessage.ezprint('\tThe mode is %s.' % (self.mode),log,verbose)
                usermessage.ezprint('\tThe filebased is %s.' % (self.filebased),log,verbose)

                self.error_felching = []

                self.listfile = []
                self.listfilename = []

        def retrieve(self,verbose=True,log=None):
                """Retrieve the orbit files

                The function will retrieve the orbit files

                Args:
                        verbose (bool): verbose [Default: `True`].
                        log (str): log [Default: `None`].
                        
                Returns:
                        `s1orbits`: Return the class

                """   

                if self.server == 'ASF': 
                        self = ASFapi.retrieveorbit(self,verbose=verbose,log=log)
                elif self.server == 'Copernicus': 
                        self = Copernicusapi.retrieveorbit(self,verbose=verbose,log=log)
                else: 
                        raise ValueError(usermessage.errormsg(__name__,s1orbits.__name__,__file__,__copyright__,
                                'The selected server is not available.',log,verbose))

                return self

        def download(self,username,password,verbose=True,log=None):
                """Download the orbit files

                The function will download the orbit files.

                Args:
                        username (str): Username 
                        password (str): Password
                        verbose (bool): verbose [Default: `True`].
                        log (str): log [Default: `None`].
                        
                Returns:
                        `s1orbits`: Return the class

                """  
                if self.server == 'ASF': 
                        self = ASFapi.downloadorbit(self,username,password,verbose=verbose,log=log)
                elif self.server == 'Copernicus': 
                        self = Copernicusapi.downloadorbit(self,username,password,verbose=verbose,log=log)
                else: 
                        raise ValueError(usermessage.errormsg(__name__,s1orbits.__name__,__file__,__copyright__,
                                'The selected server is not available.',log,verbose))

                return self

def checkorbitfile(pathSLC,pathorbit,
        verbose = True, 
        log = None,
        ): 
        """Check the orbit files 

        The function checks the orbit files.   

        Args:
                pathSLC (str): Directory of Sentinel-1 files
                pathorbit (str): Directory of Sentinel-1 orbit files
                verbose (bool): verbose [Default: `True`].
                log (str): log [Default: `None`].

        Returns:
                check (bool)
        
        """
        orbitlist=glob.glob(pathorbit+os.sep+'*.EOF')
        ziplist=np.sort(glob.glob(pathSLC+os.sep+'*.zip') + glob.glob(pathSLC+os.sep+'*.SAFE'))

        dateslcorbits1 = []
        dateslcorbits2 = []
        sat_list = []
        for slci in ziplist:
                datestr = slci.split(os.sep)[-1].split('.')[0].split('_')[5].split('T')[0] #We convert the name of files to date string.
                hourstr = slci.split(os.sep)[-1].split('.')[0].split('_')[5].split('T')[1]
                datestr1 = datestr +' '+hourstr[0]+hourstr[1]+':'+hourstr[2]+hourstr[3]+':'+hourstr[4]+hourstr[5]

                datestr = slci.split(os.sep)[-1].split('.')[0].split('_')[6].split('T')[0] #We convert the name of files to date string.
                hourstr = slci.split(os.sep)[-1].split('.')[0].split('_')[6].split('T')[1]
                datestr2 = datestr +' '+hourstr[0]+hourstr[1]+':'+hourstr[2]+hourstr[3]+':'+hourstr[4]+hourstr[5]

                dateslcorbits1.append(datetime.datetime.strptime(datestr1, '%Y%m%d %H:%M:%S')) #We add the date in string to our list of date.
                dateslcorbits2.append(datetime.datetime.strptime(datestr2, '%Y%m%d %H:%M:%S')) #We add the date in string to our list of date.

                if 'S1A' in slci:
                        sat_list.append("S1A")
                elif 'S1B' in slci:
                        sat_list.append("S1B")
                elif 'S1C' in slci:
                        sat_list.append("S1C")
                elif 'S1D' in slci:
                        sat_list.append("S1D")

        # Check the orbits
        total_check = True
        for i in range(len(dateslcorbits1)):
                dslc1 = dateslcorbits1[i]
                dslc2 = dateslcorbits2[i]
                sati = sat_list[i]

                usermessage.ezprint('Check the orbit files for %s SLC acquired by %s' % (dslc1,sati),log,verbose) 

                check_sum = False
                for pi in orbitlist:
                        if sati in pi: 
                                orb_test = os.path.abspath(pi).split(os.sep)[-1].split('V')[1].split('.')[0]
                                d1 = datetime.datetime.strptime(orb_test.split('_')[0], "%Y%m%dT%H%M%S")
                                d2 = datetime.datetime.strptime(orb_test.split('_')[1], "%Y%m%dT%H%M%S")
                                if d1 <= dslc1 <= d2 and d1 <= dslc2 <= d2:
                                        check_sum = True

                if check_sum == True: 
                        usermessage.ezprint('\tOrbit file: found.',log,verbose)
                else: 
                        total_check = False
                        usermessage.warningmsg(__name__,checkorbitfile.__name__,__file__,'Orbit file: not found.',log,verbose)

        if total_check == False: 
                usermessage.warningmsg(__name__,checkorbitfile.__name__,__file__,'Some orbit files are missing.',log,verbose)

        return total_check