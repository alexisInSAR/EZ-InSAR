#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to add some tools for the StaMPS processing class

The module adds some tools for the StaMPS processing class. 
    
    (From `ezinsar` package)

Note: 
        Each function can directly used in Python scripts or/and a Python terminal

Changelog:
        * 1.0.1: Add the parameter checking for StaMPS processing, Jan. 2025, Alexis Hrysiewicz 
        * 1.0.0: Initial version, Feb. 2024

"""

################################################################################
## Python packages
################################################################################
import os
import psutil
from typing import Optional, Union
import numpy as np
import scipy.io
import shutil
import subprocess

from ezinsar import usermessage
from ezinsar import constants
__copyright__ = constants.__copyright__

try: 
        import matlab.engine
except: 
        usermessage.warningmsg(__name__,__name__,__file__,'Impossible to import the MATLAB engine. Please see if your installation is correct! This message will not be visible in the log.',None,True)

################################################################################
## Run a subprocess for StaMPS
################################################################################
def subprocessrun(cmd,
                verbose,
                log):
        """Run a subprocess for StaMPS 

        The function will run a subprocess for StaMPS 

        Args:
                cmd (list) : command
                verbose (bool): verbose
                log (str or None): log file from the job

        """

        os.environ['PATH'] = os.environ['PATH']+':'+constants.__requirement_StaMPS__[0]+':.' 
        os.environ['PATH'] = os.environ['PATH']+':'+constants.__requirement_StaMPS__[1]+':.' 
        os.environ['STAMPS'] = constants.__requirement_StaMPS__[0].replace('/bin','')

        if not 'MATLABPATH' in list(os.environ.keys()):  
                os.environ['MATLABPATH'] = constants.__requirement_StaMPS__[1]
        else: 
                os.environ['MATLABPATH'] = os.environ['MATLABPATH'] + ':' + constants.__requirement_StaMPS__[1]

        if 'isce' in cmd:
                from ezinsar.eicomponents.processor.isce2module import isce2tools
                os.environ['PATH'], os.environ['PYTHONPATH'] = isce2tools.isce2checkenv(mode='IW',verbose=False) 
                # os.environ['PATH'] =  os.environ['PATH'] + ':' + A
                # os.environ['PYTHONPATH'] =  os.environ['PYTHONPATH'] + ':' + B

        my_env = os.environ.copy()
        my_env["PATH"] = f"/usr/local/bin:{my_env['PATH']}"

        usermessage.ezprint('Run StaMPS:',log,verbose)
        usermessage.ezprint('\tCommand: %s' % (cmd),log,verbose)

        pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, env=my_env)
        
        try: 
                while (line := pr.stdout.readline()) != "":
                        usermessage.ezprint(line.replace('\n',' '),log,verbose)

                if not len("".join(pr.stderr.readline().strip().split())) == 0:
                        while (line := pr.stderr.readline()):
                                usermessage.ezprint(line.replace('\n',' '),log,verbose)  
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the StaMPS processing',log))
                
        except KeyboardInterrupt:
                pr.terminate()
                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the StaMPS processing: user terminate',log))

        usermessage.ezprint('\tdone',log,verbose)

################################################################################
## Function to write the StaMPS-parameter file
################################################################################
def writeparameters(jobstamps, 
        file: Optional[Union[str,None]] = None,
        verbose: Optional[bool] = None, 
        log: Optional[bool] = None):
        """Write the StaMPS-parameter file from an ``ezinsar.tsprocessing`` using StaMPS

        The function writes the StaMPS-parameter file from an ``ezinsar.tsprocessing``.   

        Args:
                jobstamps (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for StaMPS processor
                file (str, Optional): Path and name of the StaMPS configuration file [Default: `None`]
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (bool): log [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        cur_dir = os.getcwd()

        if log == None:
                log = jobstamps.log

        if verbose == None:
                verbose = jobstamps.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,writeparameters.__name__,__file__,__copyright__,
                        'verbose','True or False',log))

        usermessage.openingmsg(__name__,writeparameters.__name__,__file__,__copyright__,'Write the StaMPS-parameter file',log,verbose)

        if file == None: 
                file = jobstamps.pathstampsparms
        else:
                if not file.split(os.sep)[-1] == 'parms.mat': 
                        raise ValueError(usermessage.errormsg(__name__,writeparameters.__name__,__file__,__copyright__,
                                'The file must be named parms.mat',None))

        ## Change the directory
        dir_path = os.path.dirname(os.path.abspath(file))
        os.chdir(dir_path)

        if (not os.path.isfile(file)) and (not os.path.isfile(dir_path.replace(os.sep+'SMALL_BASELINES','')+os.sep+'parms.mat')):
                usermessage.ezprint('Initialisation of the parms.mat file:',log,verbose)
                usermessage.ezprint('\tStart the MATLAB engine...',log,verbose)
                eng = matlab.engine.start_matlab()
                eng.addpath(constants.__requirement_StaMPS__[1],nargout=0)
                eng.getparm(nargout=0)
                usermessage.ezprint('\tStop the MATLAB engine.',log,verbose)
                eng.quit()
        elif (not os.path.isfile(file)) and (os.path.isfile(dir_path.replace(os.sep+'SMALL_BASELINES','')+os.sep+'parms.mat')):
                shutil.copy(dir_path.replace(os.sep+'SMALL_BASELINES','')+os.sep+'parms.mat','parms.mat')

        jobstamps.check(verbose=False)

        usermessage.ezprint('Start the MATLAB engine...',log,verbose)
        eng = matlab.engine.start_matlab()
        LASTN = eng.maxNumCompThreads(jobstamps.communpara['n_cores']['value'])
        eng.addpath(constants.__requirement_StaMPS__[1],nargout=0)
        parastamps = eng.load(file,nargout=1)
        paralist = list(parastamps.keys())

        attrs = vars(jobstamps)
        for item in attrs.keys():
                tmp = eval("jobstamps.%s" % (item))  
                if isinstance(tmp,dict):
                        for parai in list(tmp.keys()):

                                valuei = eval("jobstamps.%s['%s']['value']" % (item,parai))  

                                # Fix for StaMPS (must be temporally because of ISCE-3)
                                if valuei == 'isce2':
                                        valuei = 'isce'

                                if parai in paralist:
                                        if not valuei == None:
                                                usermessage.ezprint('\tModification of the parameter %s: %s' % (parai,valuei),log,verbose)
                                                
                                                if isinstance(valuei,list):
                                                        # if not 'inf' in valuei:
                                                        eng.setparm(parai,eng.double(eng.cell2mat(valuei)),nargout=0)
                                                        # else: 
                                                        #         listvaluei = []
                                                        #         for vi in valuei:
                                                        #                 if vi == '-inf':
                                                        #                         listvaluei.append(-eng.inf(1,1))
                                                        #                 elif vi == 'inf':
                                                        #                         listvaluei.append(eng.inf(1,1))
                                                        #                 else:
                                                        #                         .append(eng.double(vi)) 
                                                                # eng.setparm(parai,eng.double(eng.cell2mat(listvaluei)),nargout=0)                    
                                                
                                                elif not isinstance(valuei,str):
                                                        eng.setparm(parai,eng.double(valuei),nargout=0)
                                                else: 
                                                        eng.setparm(parai,valuei,nargout=0)
                                                
        usermessage.ezprint('Stop the MATLAB engine.',log,verbose)
        eng.quit()

        usermessage.ezprint('Write the %s file: done' % (file),log,verbose)

        return jobstamps

################################################################################
## Function to read a MintPy configuration file and update the job
################################################################################
def readparameters(jobstamps, 
        file: Optional[Union[str,None]] = None,
        verbose: Optional[bool] = None, 
        log: Optional[bool] = None):
        """Read the StaMPS-parameter file and update an ``ezinsar.tsprocessing`` using StaMPS

        The function writes the StaMPS-parameter file from an ``ezinsar.tsprocessing``.   

        Args:
                jobstamps (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for StaMPS processor
                file (str, Optional): Path and name of the StaMPS-parameter file [Default: `None`]
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (bool): log [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        if log == None:
                log = jobstamps.log

        if verbose == None:
                verbose = jobstamps.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,writeparameters.__name__,__file__,__copyright__,
                        'verbose','True or False',log))

        if file == None: 
                file = jobstamps.pathstampsparms
        else: 
                if not file.split(os.sep)[-1] == 'parms.mat': 
                        raise ValueError(usermessage.errormsg(__name__,writeparameters.__name__,__file__,__copyright__,
                                'The file must be named parms.mat',None))

        usermessage.openingmsg(__name__,writeparameters.__name__,__file__,__copyright__,'Read the StaMPS-parameter configuration file',log,verbose)

        if not os.path.isfile(file):
                raise ValueError(usermessage.errormsg(__name__,writeparameters.__name__,__file__,__copyright__,
                        'Impossible to find the parms.mat file.',None))

        usermessage.ezprint('Read the %s file:' % (file),log,verbose)

        parastamps = scipy.io.loadmat(file)
        paralist = list(parastamps.keys())

        attrs = vars(jobstamps)
        for item in attrs.keys():
                tmp = eval("jobstamps.%s" % (item))  
                if isinstance(tmp,dict):
                        for parai in list(tmp.keys()):  
                                if parai in paralist:
                                        try:
                                                valuei = parastamps[parai][0]
                                        except:
                                                valuei = None

                                        if isinstance(valuei,np.ndarray):
                                                valuei = list(valuei)
                                        if isinstance(valuei,list):
                                                if len(valuei) == 1:
                                                        valuei = valuei[0]

                                        # Fix for StaMPS (must be temporally because of ISCE-3))
                                        if valuei == 'isce':
                                                valuei = 'isce2'

                                        if not valuei == None: 
                                                if 'float' == eval("jobstamps.%s['%s']['format']" % (item,parai)): 
                                                        valuei = float(valuei)
                                                if 'int' == eval("jobstamps.%s['%s']['format']" % (item,parai)): 
                                                        valuei = int(valuei)
                                                if 'floatmat' == eval("jobstamps.%s['%s']['format']" % (item,parai)): 
                                                        valuei = [float(i) for i in valuei]
                                                if 'intmat' == eval("jobstamps.%s['%s']['format']" % (item,parai)): 
                                                        valuei = [int(i) for i in valuei]
                                                                        
                                        cmdi = "jobstamps.%s['%s']['value'] = valuei" % (item,parai)
                                        exec(cmdi)

        usermessage.ezprint('\tdone.',log,verbose)

        jobstamps.check(verbose=False)

        return jobstamps

################################################################################
## Check the parameters of a dict
################################################################################
def checkstampsparafromdict(paradict,jobts,verbose):
        """Check the parameters of a dict for an ``ezinsar`` job using StaMPS

        The function checks the parameters of a dict for an ``ezinsar.coregistration`` or ``ezinsar.ifgstack``.   

        Args:
                paradict (dict): parameter
                jobts (``ezinsar.coregistration``): EZ-InSAR coregistration job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar`` processing job: Return an EZ-InSAR coregistration class
        
        """

        try: 
                namestep = paradict['name']['value']
        except:
                namestep = 'Email information'

        usermessage.ezprint('\tCheck the %s:' % (namestep),jobts.log,verbose)

        listpara = list(paradict.keys())
        modepara = []
        for parai in listpara:
               modepara.append(paradict[parai]['format'])
        valuelist = []
        for parai in listpara:
               valuelist.append(paradict[parai]['valuelist']) 
        valuepara = []
        for parai in listpara:
               valuepara.append(paradict[parai]['value']) 

        infopara = {'listpara':     listpara,
                'modepara':     modepara,
                'valuelist':    valuelist,
                'valuepara':    valuepara}
        
        for idx, namepara in enumerate(infopara['listpara']): 

                if paradict[namepara]['format'] == 'list': 
                        exttext='\n\t\t\t<Format: %s>\n\t\t\t<Possible values: %s>' % ('predefined',paradict[namepara]['valuelist'])
                else: 
                        exttext = '\n\t\t\t<Format: %s>' % (paradict[namepara]['format']) 

                usermessage.ezprint('\t\t%s: %s\n\t\t\t<Description: %s>%s' % (namepara,paradict[namepara]['value'],paradict[namepara]['description'],exttext),jobts.log,verbose)

                if not paradict[namepara]['value'] == None: 

                        if infopara['modepara'][idx] == 'bool':
                                if not isinstance(paradict[namepara]['value'],bool):
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,checkstampsparafromdict.__name__,__file__,__copyright__,
                                                "parameter %s in %s" % (namepara,namestep),'True or False',jobts.log))

                        elif infopara['modepara'][idx] == 'list':
                                if not paradict[namepara]['value'] in infopara['valuelist'][idx]: 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,checkstampsparafromdict.__name__,__file__,__copyright__,
                                                "parameter %s in %s" % (namepara,namestep),'%s' % (infopara['valuelist'][idx]),jobts.log))
                                
                        elif infopara['modepara'][idx] == 'email':
                                if not isinstance(paradict[namepara]['value'],str): 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,checkstampsparafromdict.__name__,__file__,__copyright__,
                                                "parameter %s in %s" % (namepara,namestep),'str',jobts.log))
                                
                        # elif infopara['modepara'][idx] == 'int':
                        #         if not isinstance(paradict[namepara]['value'],int): 
                        #                 raise TypeError(usermessage.typeerrormsg(
                        #                         __name__,checkstampsparafromdict.__name__,__file__,__copyright__,
                        #                         "parameter %s in %s" % (namepara,namestep),'int',jobts.log))

                        # elif infopara['modepara'][idx] == 'float':
                        #         if not isinstance(paradict[namepara]['value'],float): 
                        #                 raise TypeError(usermessage.typeerrormsg(
                        #                         __name__,checkstampsparafromdict.__name__,__file__,__copyright__,
                        #                         "parameter %s in %s" % (namepara,namestep),'float',jobts.log))
                                
                        elif infopara['modepara'][idx] == 'floatmat':
                                if isinstance(paradict[namepara]['value'],list): 
                                        for vi in paradict[namepara]['value']: 
                                                if not isinstance(vi,float): 
                                                        raise TypeError(usermessage.typeerrormsg(
                                                                __name__,checkstampsparafromdict.__name__,__file__,__copyright__,
                                                                "parameter %s in %s" % (namepara,namestep),'list of float values',jobts.log))
                                else: 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,checkstampsparafromdict.__name__,__file__,__copyright__,
                                                "parameter %s in %s" % (namepara,namestep),'list of float values',jobts.log))
                                
                        elif infopara['modepara'][idx] == 'intmat':
                                if isinstance(paradict[namepara]['value'],list): 
                                        for vi in paradict[namepara]['value']: 
                                                if not isinstance(vi,int): 
                                                        raise TypeError(usermessage.typeerrormsg(
                                                                __name__,checkstampsparafromdict.__name__,__file__,__copyright__,
                                                                "parameter %s in %s" % (namepara,namestep),'list of int values',jobts.log))
                                else: 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,checkstampsparafromdict.__name__,__file__,__copyright__,
                                                "parameter %s in %s" % (namepara,namestep),'list of int values',jobts.log))
                                
                else: 
                        usermessage.warningmsg(__name__,checkstampsparafromdict.__name__,__file__,'This parameter is defined as None. It will be replaced by a default value.',jobts.log,verbose)

        return jobts