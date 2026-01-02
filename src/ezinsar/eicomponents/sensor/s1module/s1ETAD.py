#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage the S1 ETAD files

The module allows to manage Sentinel-1 ETAD files
    
    (From `ezinsar` package)

Changelog:
        * 1.2.0: Initial version, Aug. 2025

"""

################################################################################
## Python packages
################################################################################
import os 
import requests
import time 

from ezinsar import constants
from ezinsar import usermessage
from ezinsar.api import Copernicusapi

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Class
################################################################################
class s1ETAD:
        """`s1ETAD` class.

        Attributes:
                job (any): EZ-InSAR job (duplicated for compliance)
                filebased (bool): File-based mode
                error_felching (list): List of errors for Copernicus server
                listfile (list): List of urls
                listfiledownload (list): List of urls which will be downloaded  
        """
            
        def __init__(self,
                job,
                filebased=False,
                verbose = True, 
                log = None,
                ):
                """Initialise the class 

                The function initialise the class

                Args:
                        job (`EIjob`): EZ-InSAR job 
                        filebased (bool): Download the files regarding the SLC stored [Default: False].
                        verbose (bool): verbose [Default: `True`].
                        lob (str): log [Default: `None`].
                        
                Returns:
                        `s1ETAD`: Return the class

                """   

                usermessage.ezprint('Initialise the S1 ETAD list class',log,verbose)
                job.check(mode='high',verbose=False)
                self.job = job
                        
                if filebased == None: 
                        if True in self.job.SLClist['Stored'].tolist():
                                filebased = True
                        else: 
                                filebased = False                
                self.filebased = filebased

                self.listfile = None

                self.listfiledownload = []
                
                usermessage.ezprint('\tThe SLC list contains %s frames/slices.' % (len(self.job.SLClist)),log,verbose)
                usermessage.ezprint('\tThe directory is %s.' % (self.job.pathaux),log,verbose)
                usermessage.ezprint('\tThe satellite is %s.' % (self.job.satellite),log,verbose)
                usermessage.ezprint('\tThe filebased is %s.' % (self.filebased),log,verbose)

        def retrieve(self,verbose=True):
                """Retrieve the files

                The function will retrieve the files

                Args:
                        verbose (bool): verbose [Default: `True`].
                        
                Returns:
                        `s1ETAD`: Return the class

                """   

                ## Detection of the BEAM for SM
                if self.job.satmode == 'SM': 
                        beam = self.job.SLClist['Name'][0].split('_')[1]
                else: 
                        beam = None

                self.listfile = Copernicusapi.retrieve(self.job.satellite, 
                        self.job.roi, 
                        self.job.date1,
                        self.job.date2,
                        level = 'ETAD',
                        satmode = self.job.satmode, 
                        relorbit = self.job.relorbit, 
                        satpass = self.job.satpass,
                        SMswath = beam,
                        log = self.job.log, 
                        verbose = verbose,
                )
                return self
        
        def check(self,verbose=True):
                """Check the files

                The function will check the files.

                Args:
                        verbose (bool): verbose [Default: `True`].
                        
                Returns:
                        `s1ETAD`: Return the class

                """  
             
                for idx, slci in self.job.SLClist.iterrows():
                        checkvalue = False
                        key = '_'.join(slci['Name'].split('_')[5:9])

                        if self.filebased == True and (slci['Stored'] == True): 
                                for idxbis, etadi in self.listfile.iterrows():
                                        if key in etadi['Name']: 
                                                self.listfiledownload.append(etadi)
                                                checkvalue = True
                        elif self.filebased == False: 
                                for idxbis, etadi in self.listfile.iterrows():
                                                if key in etadi['Name']: 
                                                        self.listfiledownload.append(etadi)
                                                        checkvalue = True

                        if checkvalue:
                                usermessage.ezprint('The file %s has a ETAD file' % (slci['Name']),self.job.log,verbose)
                        else: 
                                usermessage.warningmsg(__name__,s1ETAD.__name__,__file__,'The file %s has NOT a ETAD file' % (slci),self.job.log,verbose)

                return self

        def download(self,username,password,verbose=True):
                """Download the files

                The function will download the files.

                Args:
                        username (str): Username 
                        password (str): Password
                        verbose (bool): verbose [Default: `True`].
                        
                Returns:
                        `s1ETAD`: Return the class

                """  
                access_token = None 

                if self.job.SLClist['Server'][0] == 'Copernicus':
                        if access_token == None:
                                access_token = Copernicusapi.get_access_token(username, password)

                        headers = {"Authorization": f"Bearer {access_token}"}
                        session = requests.Session()
                        session.headers.update(headers)

                for row in self.listfiledownload:
                        dwrequired = False
                        if not os.path.isfile(self.job.pathaux + os.sep + row['Name']):
                                dwrequired = True

                        if dwrequired == True:
                                usermessage.ezprint('The file %s is ongoing to be downloaded:...' % (row['Name']),self.job.log,verbose)
                        else:
                                usermessage.ezprint('The file %s will not be downloaded (can be already downloaded).' % (row['Name']),self.job.log,verbose)

                        if dwrequired == True:    
                                if row['Server'] == 'Copernicus':
                                        Copernicusapi.download(row,self.job.pathaux,
                                                username = username, 
                                                password = password,  
                                                access_token = access_token, 
                                                session = session, 
                                                headers = headers, 
                                                log = self.job.log, 
                                                verbose = True, 
                                                verboseprogress = True,
                                                sizecheck = 1e6,
                                                )
                
                                time.sleep(constants.__sleepSLCdownload__)

                return self