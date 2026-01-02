#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage an EZ-InSAR job 

The module allows to add some tools to manage an `EIjob`: i.e., checking.
    
    (From `ezinsar` package)

Changelog:
        * 3.3.1: Several changes, Dec. 2025, Alexis Hrysiewicz
                * Check the check method (if EIjob in string)
                * Delete the link to the EZ-InSAR GAMMA module
        * 3.3.0: Bug fixes, Oct. 2025, Alexis Hrysiewicz
        * 3.2.0: Several changes, Jul. 2025, Alexis Hrysiewicz
                * Force the used of the \ symbol for Windows paths
                * changepath new function
        * 3.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import platform
import sys
import os
from typing import Optional
import re
import copy

from ezinsar import constants
from ezinsar import usermessage

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Function to check the attributes of the EZ-InSAR job 
################################################################################
def check(job, verbose: Optional[bool] = None, modelog: Optional[bool] = True, mode: Optional[str] = 'low'):
        """Check a EZ-InSAR job 

        The function checks the value inside an `EIjob`.  

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modelog (bool): Mode of the log. [Default: `True`]
                mode (str): mode of checking [Default: ``low``]. Can be ``low``or ``high``.

        Returns:
                `EIjob`: Return an EZ-InSAR class

        """  
        if not isinstance(modelog,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'modelog','True or False',None))
        if modelog == True:
                log = job.log
        else:
                log = None 

        if not log == None: 
                log = constants.__cachedir__+os.sep+log.split(os.sep)[-1]
                job.log = log
                usermessage.warningmsg(__name__,check.__name__,__file__,'the log file has been modified: %s' % (log),log,verbose)


        if not 'EIjob' in str(type(job)):
                raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,
                        'The job parameter is not a EZ-InSAR job.',log))
        
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if not (isinstance(mode,str) and mode in ['low','high']):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'mode','"low" or "high"',log))
        
        usermessage.openingmsg(__name__,check.__name__,__file__,__copyright__,'Check the EZ-InSAR-job attributes',log,verbose)

        # For the name of the job information
        if not (isinstance(job.nameJob,str) or job.nameJob == None):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'nameJob','str or None',log))

        usermessage.ezprint('The name of the EZ-InSAR job is: %s.' % (job.nameJob),log,verbose)
        
        # For the user information
        usermessage.ezprint('Check the user information:',log,verbose)

        if not (isinstance(job.user,str) or job.user == None):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'user','str or None',log))
        usermessage.ezprint('\tThe user is %s.' % job.user,log,verbose)
        if job.user == None: 
                usermessage.warningmsg(__name__,check.__name__,__file__,'The username is not defined.',log,verbose)
                
        usermessage.ezprint('\tThe computer system is %s.' % job.computer,log,verbose)

        if not job.computer == platform.system():
                usermessage.warningmsg(__name__,check.__name__,__file__,'The computer system is not the same. Please check the compatibility.',log,verbose)

        if not (isinstance(job.user,str) or job.user == None):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'token','str or None',log))
        
        usermessage.ezprint('\tThe user token is %s.' % job.token,log,verbose)
        if job.token == None:
                usermessage.warningmsg(__name__,check.__name__,__file__,'The user token is not defined.',log,verbose)

        # For the path information
        usermessage.ezprint('Check the path/file information:',log,verbose)

        listpath = ['workdirectory','pathSLC','pathorbit','pathaux','pathDEM']

        if not job.workdirectory == None:
                job.workdirectory = job.workdirectory.replace('/',os.sep).replace('\\',os.sep)
        if not job.pathSLC == None:
                job.pathSLC = job.pathSLC.replace('/',os.sep).replace('\\',os.sep)
        if not job.pathorbit == None:
                job.pathorbit = job.pathorbit.replace('/',os.sep).replace('\\',os.sep)
        if not job.pathaux == None:
                job.pathaux = job.pathaux.replace('/',os.sep).replace('\\',os.sep)
        if not job.pathDEM == None:
                job.pathDEM = job.pathDEM.replace('/',os.sep).replace('\\',os.sep)

        for pathi in listpath: 
                tmppath = eval("job."+pathi)

                if not (isinstance(job.user,str) or job.user == None):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                pathi,'str or None'))

                usermessage.ezprint('\tThe %s is %s.' % (pathi,tmppath),log,verbose)

                if tmppath == None:
                        strmess = 'The %s is not defined' % (pathi)
                        if mode == 'low':
                                usermessage.warningmsg(__name__,check.__name__,__file__,strmess,log,verbose)

                        elif mode == 'high':
                                if job.satellite == 'S1' and pathi == 'pathaux':
                                        raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,strmess,log))
                                else:
                                        usermessage.warningmsg(__name__,check.__name__,__file__,strmess,log,verbose)

        usermessage.ezprint('Check the DEM information:',log,verbose)
        
        # For the DEM information
        if not (isinstance(job.nameDEM,str) or job.nameDEM == None):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'nameDEM','str or None',log))
        
        usermessage.ezprint('\tThe DEM name is %s.' % (job.nameDEM),log,verbose)
        if job.nameDEM == None: 
                usermessage.warningmsg(__name__,check.__name__,__file__,'The DEM name is not defined.',log,verbose)

        if not (isinstance(job.typeDEM,str) or job.typeDEM == None):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'typeDEM','str or None',log))

        usermessage.ezprint('\tThe DEM type is %s.' % (job.typeDEM),log,verbose)
        if job.typeDEM == None: 
                usermessage.warningmsg(__name__,check.__name__,__file__,' The DEM type is not defined.',log,verbose)
        else: 
                if not job.typeDEM in constants.__DEMlist__: 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                pathi,'%s' % constants.__DEMlist__,log))

        # Temporal information
        if not 'datetime.datetime' in str(type(job.date1)):
                raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                pathi,'datetime.date',log))
        if not 'datetime.datetime' in str(type(job.date2)):
                raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                pathi,'datetime.date',log))
        usermessage.ezprint('For the temporal information:',log,verbose)
        usermessage.ezprint('\tThe date 1 is %s' % (job.date1),log,verbose)
        usermessage.ezprint('\tThe date 2 is %s' % (job.date2),log,verbose)

        # Spatial information
        try:
                job.roi.geom_type == 'Polygon'
        except: 
                if not (job.roi == None):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'roi','Polygon or None',log))
        
        usermessage.ezprint('Check the spatial information:',log,verbose)
        
        usermessage.ezprint('\tThe ROI is %s.' % (job.roi),log,verbose)
        if job.roi == None: 
                if mode == 'low':
                        usermessage.warningmsg(__name__,check.__name__,__file__,'The ROI is not defined.',log,verbose)
                elif mode == 'high':
                        raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,'The ROI is not defined.',log))

        # Satellite information
        if not isinstance(job.satellite,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'satellite','str'))
        usermessage.ezprint('Check the satellite information:',log,verbose)
        usermessage.ezprint('\tThe satellite is %s.' % (job.satellite),log,verbose)

        if not isinstance(job.satmode,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'satmode','str',log))
        checksat = False

        if job.satellite in list(constants.__sensors__.keys()): 
                if job.satmode in list(constants.__sensors__[job.satellite].keys()): 
                        checksat = True 
        if checksat == True:
                usermessage.ezprint('\tThe acquisition mode is %s.' % (job.satmode),log,verbose)
        else:
                raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,usermessage.createmsgsensors(),log))

        if not (isinstance(job.relorbit,int) or job.relorbit == None):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'relorbit','int or None',log))

        usermessage.ezprint('\tThe relative orbit is %s.' % (job.relorbit),log,verbose)
        if not job.relorbit == None:
                if not isinstance(job.relorbit,int):
                        sys.exit('\t\tERROR in EZ-InSAR processing (ezinsar.check - ezinsar.eicomponents.job.jobtools.check): The relative orbite must be an integer')
        else:
                usermessage.warningmsg(__name__,check.__name__,__file__,'The relative orbit is not defined.',log,verbose)

        if not isinstance(job.polarisation,list):
                job.polarisation = job.polarisation.split(',')
        job.polarisation = list(map(lambda x: x.upper(), job.polarisation))
        job.polarisation = list(set(job.polarisation))
        if 'VV' in job.polarisation:
                job.polarisation.sort(reverse=True)
        else:
                job.polarisation.sort()

        usermessage.ezprint('\tThe selected polarisation(s) is/are:' ,log,verbose)
        for pi in job.polarisation: 
                if pi.upper() in ['VV','VH','HV','HH']:
                        usermessage.ezprint('\t\t %s' % (pi.upper()) ,log,verbose)
                else: 
                        raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,'The selected polarisation (%s) is not correct' %(pi.upper()),log))

        if not (isinstance(job.relorbit,int) or job.relorbit == None):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'Relative orbit','int or None',log))

        usermessage.ezprint('\tThe pass direction is %s.' % (job.satpass),log,verbose)
        if not job.satpass == None:
                job.satpass = job.satpass.upper() 
                if not (job.satpass == 'ASCENDING' or job.satpass == 'DESCENDING'):
                        raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,'The pass direction must be ASCENDING or DESCENDING',log))
        else: 
                usermessage.warningmsg(__name__,check.__name__,__file__,'The pass direction is not defined.',log,verbose)

        # Integration information
        if not isinstance(job.verbose,bool): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        if not isinstance(job.gui,bool): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'gui','True or False',log))
        
        if not (isinstance(log,str) or log == None):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'log','str or None',log))
        
        return job

################################################################################
## Function to create the directories for the EZ-InSAR job 
################################################################################
def mkdir(job,verbose: Optional[bool] = None):
        """Create the directories required by a EZ-InSAR job 

        The function creates the differents directories for an `EIjob`.  

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                `EIjob`: Return an EZ-InSAR class

        """ 

        if not 'EIjob' in str(type(job)):
                raise ValueError(usermessage.errormsg(__name__,mkdir.__name__,__file__,__copyright__,
                        'The job parameter is not a EZ-InSAR job.'),job.log,verbose)

        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,mkdir.__name__,__file__,__copyright__,
                        'verbose','True or False'),job.log,verbose)
        
        usermessage.openingmsg(__name__,mkdir.__name__,__file__,__copyright__,'Create the directories for the EZ-InSAR job',job.log,verbose)

        job.check(mode='high',verbose=False)

        listpath = ['workdirectory','pathSLC','pathorbit','pathaux','pathDEM']
        for pathi in listpath: 
                tmppath = eval("job."+pathi)

                # if not os.path.isabs(tmppath):
                #         raise ValueError(usermessage.errormsg(__name__,mkdir.__name__,__file__,__copyright__,
                #                 'The path of %s is not an absolute path: %s' % (pathi,tmppath),job.log,verbose))

                usermessage.ezprint('For %s' % (pathi),job.log,verbose)
                if (not tmppath == None) and os.path.isdir(tmppath) == False:
                        usermessage.ezprint('\tCreate the %s directory for %s.' % (tmppath,pathi),job.log,verbose)
                        os.mkdir(tmppath)
                elif (not tmppath == None) and os.path.isdir(tmppath) == True:
                        usermessage.ezprint('\tThe %s directory for %s is already created.' % (tmppath,pathi),job.log,verbose)
                else:
                        usermessage.ezprint('\tNothing to do.',job.log,verbose)

        return job

################################################################################
## Function to change/list the paths inside the EZ-InSAR job
################################################################################
def changepath(job,
               newroot: Optional[str] = '/mnt/Data', 
               locklog : Optional[bool] = False,
               verbose: Optional[bool] = True,
               log: Optional[bool] = None):
        """List (and change) the paths required by a EZ-InSAR job 

        The function will change/list the paths for an `EIjob`.  

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                `EIjob`: Return the original EZ-InSAR class
                `EIjob`: Return the modified EZ-InSAR class

        """ 

        def looks_like_path(s):
                pattern = r'[/\\]'
                if bool(re.search(pattern, s)):
                        if '.' in pattern.split(os.sep)[-1]:
                                return 'file'
                        else:
                                return 'dir'
                else:
                        return 'None'
                
        def createnewpath(origpath,rootdir,newrootdir,namevariable,log,verbose):
                usermessage.ezprint('Path detected in %s' % (namevariable),log,verbose)

                if rootdir in origpath: 
                        newpath = origpath.replace(rootdir,newrootdir).replace(os.sep,'/')
                else:
                        newpath = os.path.dirname(newrootdir)+'/'+origpath.split(os.sep)[-1]

                usermessage.ezprint('\tOrignal path: %s' % (origpath),log,verbose)
                usermessage.ezprint('\tNew path: %s' % (newpath),log,verbose)

                return origpath, newpath
                                
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,mkdir.__name__,__file__,__copyright__,
                        'verbose','True or False'),log,verbose)
        
        usermessage.openingmsg(__name__,mkdir.__name__,__file__,__copyright__,'List (and change) the paths inside the EZ-InSAR job',log,verbose)

        usermessage.warningmsg(__name__,changepath.__name__,__file__,'EZ-InSAR requires that the work directory contains all job directories (i.e., coregistration, ifgstack, etc.).',log,verbose)

        oldpathdir = []
        newpathdir = []
        oldpathfile = []
        newpathfile = []

        # Duplicate the job 
        jobsecondary = copy.deepcopy(job)

        ## Detection of the root paths
        usermessage.ezprint('Detection of the root path (based on the work directory)',log,verbose)
        if not 'EIjob' in str(type(job)):
                rootdir = os.path.dirname(job.workdirectory)  
        else:
                rootdir = job.workdirectory
        newrootdir = newroot+'/'+rootdir.split(os.sep)[-1]

        jobsecondary.workdirectory = newrootdir

        usermessage.ezprint('\tRoot directory: %s' % (rootdir),log,verbose)
        usermessage.ezprint('\tNew root directory: %s' % (newrootdir),log,verbose)

        oldpathdir.append(os.path.dirname(job.workdirectory))
        newpathdir.append(os.path.dirname(jobsecondary.workdirectory))

        ## For the other directories
        for li in list(vars(job)):
                origpath = eval('job.%s' % (li))

                if li == 'log' and locklog == True:
                        origpath = 126

                if isinstance(origpath,dict):
                        for li2 in list(origpath.keys()):
                                origpath = eval('job.%s["%s"]["value"]' % (li,li2))

                                if isinstance(origpath,str) and (not looks_like_path(origpath) == 'None'):   
                                        origpath, newpath = createnewpath(origpath,rootdir,newrootdir,'job.%s["%s"]["value"]' % (li,li2),log,verbose)
                                        if looks_like_path(origpath) == 'dir':
                                                oldpathdir.append(origpath)
                                                newpathdir.append(newpath)

                                        elif looks_like_path(origpath) == 'file':
                                                oldpathfile.append(origpath)
                                                newpathfile.append(newpath)

                                        exec('jobsecondary.%s["%s"]["value"] = newpath' % (li,li2))
                        
                else:
                        if isinstance(origpath,str) and (not looks_like_path(origpath) == 'None'):   
                                origpath, newpath = createnewpath(origpath,rootdir,newrootdir,'job.%s' % (li),log,verbose)
                                if looks_like_path(origpath) == 'dir':
                                        oldpathdir.append(origpath)
                                        newpathdir.append(newpath)

                                elif looks_like_path(origpath) == 'file':
                                        oldpathfile.append(origpath)
                                        newpathfile.append(newpath)

                                exec('jobsecondary.%s = newpath' % (li))

        ## For Docker (detection of the mounted points)
        oldpathtmp = oldpathdir + oldpathfile
        newpathtmp = newpathdir + newpathfile
        idx = [oldpathtmp.index(x) for x in sorted(set(oldpathtmp))]

        oldpathmounted = [rootdir]
        newpathmounted = [newrootdir]

        for x in idx:
                if os.path.isdir(oldpathtmp[x]):
                        if not rootdir in oldpathtmp[x]:
                                oldpathmounted.append(oldpathtmp[x])
                                newpathmounted.append(newpathtmp[x])
                elif os.path.isfile(oldpathtmp[x]):
                        oldpathmounted.append(oldpathtmp[x])
                        newpathmounted.append(newpathtmp[x])

        return jobsecondary, job, oldpathmounted, newpathmounted, rootdir, newrootdir
