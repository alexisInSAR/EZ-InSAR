#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage an EZ-InSAR processing job

The module allows to add some tools to manage an EZ-InSAR processing job: i.e., checking.
    
    (From `ezinsar` package)

Changelog:
        * 3.3.1: Several changes, Dec. 2025, Alexis Hrysiewicz
                * Check the check method (if EIjob in string)
                * Delete the link to the EZ-InSAR GAMMA module
        * 3.2.0: Add the MiaplPy processing, Jul. 2025, Alexis Hrysiewicz
        * 3.1.0: Add the GAMMA processing, Feb. 2025, Alexis Hrysiewicz
        * 3.0.1: Add the parameter checking for StaMPS processing, Jan. 2025, Alexis Hrysiewicz 
        * 3.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import os
import psutil
from typing import Optional

from ezinsar import constants
from ezinsar import usermessage

from ezinsar.eicomponents.processor.dorismodule import doristools
from ezinsar.eicomponents.processor.mintpymodule import mintpytools
from ezinsar.eicomponents.processor.miaplpymodule import miaplpytools
from ezinsar.eicomponents.processor.licsbasmodule import licsbastools
from ezinsar.eicomponents.processor.isce2module import isce2tools
from ezinsar.eicomponents.processor.snapmodule import snaptools
from ezinsar.eicomponents.processor.stampsmodule import stampstools

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Function to check the attributes of the EZ-InSAR job 
################################################################################
def check(job, verbose: Optional[bool] = None, mode: Optional[str] = 'low'):
        """Check a EZ-InSAR processing job 

        The function checks the parameters of an EZ-InSAR processing job.  

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                mode (str): mode of checking [Default: ``low``]. Can be ``low``or ``high``.

        Returns:
                `EIjob`: Return an EZ-InSAR class

        """   

        if not 'ezinsar' in str(type(job)):
                raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,
                        'The job parameter is not a EZ-InSAR job.',job.log))
        
        if not job.log == None: 
                job.log = constants.__cachedir__+os.sep+job.log.split(os.sep)[-1]
                usermessage.warningmsg(__name__,check.__name__,__file__,'the log file has been modified: %s' % (job.log),job.log,verbose)
        
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        
        if not mode in ['low','high']:
                raise TypeError(usermessage.typeerrormsg(
                        __name__,check.__name__,__file__,__copyright__,
                        'mode','low or high',job.log))
        
        usermessage.openingmsg(__name__,check.__name__,__file__,__copyright__,'Check the EZ-InSAR processing parameters: %s' % (str(type(job))),job.log,verbose)
        usermessage.warningmsg(__name__,check.__name__,__file__,'The script does not check if the values of the parameters are valid for the used processor.',job.log,verbose)

        listsuperpara = []
        for parai in list(vars(job)):
                tmppara = eval("job."+parai) 
                if not isinstance(tmppara,dict):
                     listsuperpara.append(parai)

        ## Check the directories             
        listpath = ['workdirectory','pathSLC','pathorbit','pathaux','pathDEM']
        for pathi in listpath: 
                if pathi in listsuperpara:
                        tmppath = eval("job."+pathi)
                        usermessage.ezprint('\tThe %s is %s.' % (pathi,tmppath),job.log,verbose)
                        if tmppath == None:
                                strmess = 'The %s is not defined' % (pathi)
                                if mode == 'low':
                                        usermessage.warningmsg(__name__,check.__name__,__file__,strmess,job.log,verbose)
                                elif mode == 'high':
                                        if job.satellite == 'S1' and pathi == 'pathaux':
                                                raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,strmess,job.log))
                                        else:
                                                usermessage.warningmsg(__name__,check.__name__,__file__,strmess,job.log,verbose)

        ## For the DEM 
        if 'typeDEM' in listsuperpara:
                usermessage.ezprint('\tThe typeDEM is %s.' % (job.typeDEM),job.log,verbose)
                if job.typeDEM == None: 
                        if mode == 'low':
                                usermessage.warningmsg(__name__,check.__name__,__file__,'The typeDEM is not defined.',job.log,verbose)
                        elif mode == 'high':
                                raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,'The typeDEM is not defined.',job.log))
                else: 
                        if not job.typeDEM in ['SRTM','SRTM-ell','NASADEM','NASADEM-ell','Copernicus','Copernicus-ell','perso']: 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,check.__name__,__file__,__copyright__,
                                        pathi,'["SRTM","SRTM-ell","NASADEM","NASADEM-ell","Copernicus","Copernicus-ell","perso"]"',job.log)) 

        if 'nameDEM' in listsuperpara:
                usermessage.ezprint('\tThe nameDEM is %s.' % (job.nameDEM),job.log,verbose)
                if job.nameDEM == None: 
                        if mode == 'low':
                                usermessage.warningmsg(__name__,check.__name__,__file__,'The nameDEM is not defined.',job.log,verbose)
                        elif mode == 'high':
                                raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,'The nameDEM is not defined.',job.log))
                # else:     
                        # if not os.path.isfile(job.pathDEM+os.sep+job.nameDEM):
                                # raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,'The nameDEM is not a file.',job.log))           

        if 'pathstack' in listsuperpara:
                usermessage.ezprint('\tThe pathstack is %s.' % (job.pathstack),job.log,verbose)
                if job.pathstack == None: 
                        if mode == 'low':
                                usermessage.warningmsg(__name__,check.__name__,__file__,'The pathstack is not defined.',job.log,verbose)
                        elif mode == 'high':
                                raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,'The pathstack is not defined.',job.log))
        
        ## For the reference date
        if 'refdate' in listsuperpara:
                if (not isinstance(job.refdate,str)) and (not job.refdate == None) :
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'refdate','str',job.log))
                usermessage.ezprint('\tThe refdate is %s.' % (job.refdate),job.log,verbose)

        ## For the satellite parameters
        if 'satellite' in listsuperpara:
                if not isinstance(job.satellite,str):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'satellite','str',job.log))
                usermessage.ezprint('\tThe satellite is %s.' % (job.satellite),job.log,verbose)

        if 'satmode' in listsuperpara:
                if not isinstance(job.satmode,str):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'satmode','str',job.log))
                usermessage.ezprint('\tThe acquisition mode is %s.' % (job.satmode),job.log,verbose)

        if  (not 'intstack' in str(type(job))) and (not 'tsprocessing' in str(type(job))):
                if not constants.__sensors__[job.satellite][job.satmode] == None:
                        if not job.processor in constants.__sensors__[job.satellite][job.satmode]: 
                                raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,usermessage.createmsgsensors(),job.log))
                else: 
                        raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,usermessage.createmsgsensors(),job.log))
                
        elif not 'tsprocessing' in str(type(job)):
                if not constants.__sensorsintensity__[job.satellite][job.satmode] == None:
                        if not job.processor in constants.__sensorsintensity__[job.satellite][job.satmode]: 
                                raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,usermessage.createmsgsensors(mode='int'),job.log))
                else: 
                        raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,usermessage.createmsgsensors(mode='int'),job.log))

        if 'polarisation' in listsuperpara:
                usermessage.ezprint('\tThe selected polarisation(s) is/are:' ,job.log,verbose)
                if isinstance(job.polarisation,list):
                        polarisation = job.polarisation
                else: 
                        polarisation = [job.polarisation]
                for pi in polarisation: 
                        if pi.upper() in ['VV','VH','HV','HH']:
                                usermessage.ezprint('\t\t %s' % (pi.upper()) ,job.log,verbose)
                        else: 
                                raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,'The selected polarisation (%s) is not correct' %(pi.upper()),job.log))

                if isinstance(job.polarisation,list):
                        if len(job.polarisation)>1 and job.processor == 'snap': 
                                raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,'Only one polarisation is authorised with SNAP.',job.log))


        ## For the Region of Interest
        if 'roi' in listsuperpara:
                usermessage.ezprint('\tThe ROI is: %s' % (str(job.roi)),job.log,verbose)
                if job.roi == None: 
                        if mode == 'low':
                                usermessage.warningmsg(__name__,check.__name__,__file__,'The ROI is not defined.',job.log,verbose)
                        else: 
                                raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,'The ROI is not defined.',job.log)) 
        
        ## For the processor 
        if 'computercores' in listsuperpara:
                usermessage.ezprint('\tThe computercores is %s.' % (job.computercores),job.log,verbose)
                if not isinstance(job.computercores,int):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'computercores','int',job.log))
                
        if 'computerworkers' in listsuperpara:
                usermessage.ezprint('\tThe computerworkers is %s.' % (job.computerworkers),job.log,verbose)
                if not isinstance(job.computerworkers,int):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'computerworkers','int',job.log))
        
        if 'computerRAM' in listsuperpara:
                usermessage.ezprint('\tThe computerRAM is %s.' % (job.computerRAM),job.log,verbose)
                if not isinstance(job.computerRAM,int):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'computerRAM','int',job.log))
                else: 
                        if not job.computerRAM <= int((psutil.virtual_memory().total)/1e6):
                                raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,'The computerRAM is higher to the available RAM.',psutil.log)) 
        
        if 'processor' in listsuperpara:
                usermessage.ezprint('\tThe processor is %s.' % (job.processor),job.log,verbose)    
                if (not job.processor == 'doris') and 'doris' in str(type(job)): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'processor','doris',job.log)) 
                elif (not job.processor == 'isce2') and 'isce2' in str(type(job)): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'processor','isce2',job.log)) 
                elif (not job.processor == 'mintpy') and 'mintpy' in str(type(job)): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'processor','mintpy',job.log)) 
                elif (not job.processor == 'stamps') and 'stamps' in str(type(job)): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'processor','stamps',job.log)) 
                elif (not job.processor == 'snap') and 'snap' in str(type(job)): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'processor','snap',job.log)) 

        if 'modecropping' in listsuperpara:
                usermessage.ezprint('\tThe modecropping is %s.' % (job.modecropping),job.log,verbose)    
                if not job.modecropping == None:
                        if isinstance(job.modecropping,str) and (not job.modecropping in ['auto','precise']):  
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,check.__name__,__file__,__copyright__,
                                        'modecropping','auto or a list (4 elements)',job.log)) 
                        elif isinstance(job.modecropping,list) and (not len(job.modecropping) == 4): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,check.__name__,__file__,__copyright__,
                                        'modecropping','auto or a list (4 elements)',job.log)) 

        ## For the processing 
        if 'mlazi' in listsuperpara:
                usermessage.ezprint('\tThe mlazi is %s.' % (job.mlazi),job.log,verbose)
                if not isinstance(job.mlazi,int):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'mlazi','int',job.log))
        
        if 'mlran' in listsuperpara:
                usermessage.ezprint('\tThe mlran is %s.' % (job.mlran),job.log,verbose)
                if not isinstance(job.mlran,int):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'mlran','int',job.log))
        
        if 'mlazidisplay' in listsuperpara:
                usermessage.ezprint('\tThe mlazidisplay is %s.' % (job.mlazidisplay),job.log,verbose)
                if not isinstance(job.mlazidisplay,int):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'mlazidisplay','int',job.log))
        
        if 'mlrandisplay' in listsuperpara:
                usermessage.ezprint('\tThe mlrandisplay is %s.' % (job.mlrandisplay),job.log,verbose)
                if not isinstance(job.mlrandisplay,int):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'mlrandisplay','int',job.log))
                
        if 'modestack' in listsuperpara:
                usermessage.ezprint('\tThe modestack is %s.' % (job.modestack),job.log,verbose)
                if 'doris' in str(type(job)):
                        tmp = constants.__dorisTScompatibility__
                elif 'snap' in str(type(job)):
                        tmp = constants.__SNAPTScompatibility__
                else: 
                        tmp = ['normal','StaMPS_PS','StaMPS_SBAS','StaMPS_PSSBAS','MintPy']

                if not job.modestack in tmp:
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'modestack',"%s" % tmp,job.log))

        if 'modeforce' in listsuperpara:
                usermessage.ezprint('\tThe force mode is %s.' % (job.modeforce),job.log,verbose)
                if not isinstance(job.modeforce,bool):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'modeforce','bool',job.log))
        
        if 'modeDEM' in listsuperpara:
                usermessage.ezprint('\tThe modeDEM is %s.' % (job.modeDEM),job.log,verbose)
                if not job.modeDEM in ['exact','import']:
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'modeDEM',"in ['exact','import']",job.log))

        if 'modeacq' in listsuperpara:
                usermessage.ezprint('\tThe modeacq is %s.' % (job.modeacq),job.log,verbose)
                if not job.modeacq in ['monostatic','bistatic']:
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,check.__name__,__file__,__copyright__,
                                'modeacq',"in ['monostatic','bistatic']",job.log))

        if 'pathmintpyconfig' in listsuperpara:
                usermessage.ezprint('\tThe pathmintpyconfig is %s.' % (job.pathmintpyconfig),job.log,verbose)
                if not job.pathmintpyconfig == None: 
                        if not os.path.isfile(job.pathmintpyconfig):
                                if mode == 'low':
                                        usermessage.warningmsg(__name__,check.__name__,__file__,'The pathmintpyconfig is not defined.',job.log,verbose)
                                else: 
                                        raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,'The pathmintpyconfig is not defined.',job.log)) 
                else:
                        if mode == 'low':
                                usermessage.warningmsg(__name__,check.__name__,__file__,'The pathmintpyconfig is not defined.',job.log,verbose)
                        else: 
                                raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,'The pathmintpyconfig is not defined.',job.log)) 

        if 'ifgprocessor' in listsuperpara:
                usermessage.ezprint('\tThe ifgprocessor is %s.' % (job.ifgprocessor),job.log,verbose)

        if 'mode' in listsuperpara:
                usermessage.ezprint('\tThe mode is %s.' % (job.mode),job.log,verbose)        

        if 'mintpy' in str(type(job)):
                usermessage.warningmsg(__name__,check.__name__,__file__,'All parameter for MintPy must be given in str. Please see the MintPy documentation for further information on processing parameters.',job.log,verbose)

        ## (ONLY FOR LICSBAS)
        if 'frame' in listsuperpara:
                usermessage.ezprint('\tThe frame is: %s' % (job.frame),job.log,verbose)
                if job.frame == None: 
                        if mode == 'low':
                                usermessage.warningmsg(__name__,check.__name__,__file__,'The frame is not defined.',job.log,verbose)
                        else: 
                                raise ValueError(usermessage.errormsg(__name__,check.__name__,__file__,__copyright__,'The frame is not defined.',job.log)) 
                        
        ## Check the processing parameters
        for parai in vars(job).items():
                tmp = eval('job.%s' % (parai[0]))
                if isinstance(tmp,dict):
                        if 'doris' in str(type(job)):
                                doristools.checkdorisparafromdict(tmp,job,verbose)

                        elif 'mintpy' in str(type(job)):
                                mintpytools.checkmintpyparafromdict(tmp,job,verbose)

                        elif 'miaplpy' in str(type(job)):
                                mintpytools.checkmintpyparafromdict(tmp,job,verbose)
                        
                        elif 'licsbas' in str(type(job)):
                                licsbastools.checklicsbasparafromdict(tmp,job,verbose)
                        
                        elif 'isce2' in str(type(job)):
                                isce2tools.checkisce2parafromdict(tmp,job,verbose)
                        
                        elif 'snap' in str(type(job)):
                                snaptools.checksnapparafromdict(tmp,job,verbose)

                        elif 'stamps' in str(type(job)):
                                stampstools.checkstampsparafromdict(tmp,job,verbose)
        
        if 'mintpy' in str(type(job)) or 'miaplpy' in str(type(job)):
                usermessage.warningmsg(__name__,check.__name__,__file__,'All parameter for MintPy and MiaplPy must be given in str. Please see the MintPy and MiaplPy documentations for further information on processing parameters.',job.log,verbose)

        return job