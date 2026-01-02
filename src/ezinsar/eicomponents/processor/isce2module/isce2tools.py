#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to add some tool functions for ISCE-2 processor

The module allows to add some sub-functions for ISCE-2 processor.
    
    (From `ezinsar` package)

Note: 
        Each function can directly used in Python scripts or/and a Python terminal

Changelog:
        * 1.0.0: Initial version, May. 2024

"""

################################################################################
## Python packages
################################################################################
import os
import platform
from typing import Optional
import subprocess
import multiprocessing
import numpy as np

from ezinsar import usermessage
from ezinsar import constants
__copyright__ = constants.__copyright__

################################################################################
## check the path variable to be consistent with the contrib functions
################################################################################
def isce2checkenv(mode='IW',verbose=True):
        """Check and modify the path enviroment variable for ISCE2

        The function will check and modify the path enviroment variable for ISCE2.

        Args:
                mode (str): Acquisition mode to switch the path variables
                verbose (bool)

        """
        usermessage.openingmsg(__name__,isce2checkenv.__name__,__file__,__copyright__,'Check the path env variable for ISCE2',None,verbose)
        
        # Checking 
        for vi in constants.__requirement_ISCE2__:
                if vi in os.environ['PATH']:
                        usermessage.ezprint('The variable %s has been found.' % (vi),None,verbose)
                else:
                        os.environ['PATH'] = os.environ['PATH']+':'+vi+':.' 
        
        for vi in constants.__requirement_ISCE2_Python__: 
                if vi in os.environ['PYTHONPATH']:
                        usermessage.ezprint('The variable %s has been found.' % (vi),None,verbose)
                else:
                        os.environ['PYTHONPATH'] = os.environ['PYTHONPATH']+':'+vi+':.' 

        # Checking of the consistent with the sensor mode
        if (mode == 'IW') and ('/stack/topsStack' in os.environ['PATH']): 
                usermessage.ezprint('The contrib directories are consistent with the IW mode.',None,verbose)
        elif (mode == 'IW') and (not '/stack/topsStack' in os.environ['PATH']): 
                usermessage.ezprint('The contrib directories are not consistent with the IW mode.',None,verbose)
                usermessage.warningmsg(__name__,isce2checkenv.__name__,__file__,'The path will be changed.',None,verbose)
                os.environ['PATH'] = os.environ['PATH'].replace('/stack/stripmapStack','/stack/topsStack')
        elif (mode == 'SM') and ('/stack/stripmapStack' in os.environ['PATH']): 
                usermessage.ezprint('The contrib directories are consistent with the SM mode.',None,verbose)
        elif (mode == 'SM') and ('/stack/topsStack' in os.environ['PATH']):
                usermessage.ezprint('The contrib directories are not consistent with the SM mode.',None,verbose)
                usermessage.warningmsg(__name__,isce2checkenv.__name__,__file__,'The path will be changed.',None,verbose)
                os.environ['PATH'] = os.environ['PATH'].replace('/stack/topsStack','/stack/stripmapStack')

        return os.environ['PATH'], os.environ['PYTHONPATH']

################################################################################
## Check the parameters of a dict
################################################################################
def checkisce2parafromdict(paradict,jobcoreg,verbose):
        """Check the parameters of a dict for an ``ezinsar`` job using ISCE-2

        The function checks the parameters of a dict for an ``ezinsar.coregistration`` or ``ezinsar.ifgstack``.   

        Args:
                paradict (dict): parameter
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar`` processing job: Return an EZ-InSAR coregistration class
        
        """

        try: 
                namestep = paradict['name']['value']
        except:
                namestep = 'Email information'

        usermessage.ezprint('\tCheck the %s:' % (namestep),jobcoreg.log,verbose)

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

                usermessage.ezprint('\t\t%s: %s\n\t\t\t<Description: %s>%s' % (namepara,paradict[namepara]['value'],paradict[namepara]['description'],exttext),jobcoreg.log,verbose)

                if infopara['modepara'][idx] == 'bool':
                        if not isinstance(paradict[namepara]['value'],bool):
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkisce2parafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'True or False',jobcoreg.log))

                elif infopara['modepara'][idx] == 'list':
                        if not paradict[namepara]['value'] in infopara['valuelist'][idx]: 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkisce2parafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'%s' % (infopara['valuelist'][idx]),jobcoreg.log))
                        
                elif infopara['modepara'][idx] == 'email':
                        if not isinstance(paradict[namepara]['value'],str): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkisce2parafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'str',jobcoreg.log))
                        
                elif infopara['modepara'][idx] == 'int':
                        if not isinstance(paradict[namepara]['value'],int): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkisce2parafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'int',jobcoreg.log))

                elif infopara['modepara'][idx] == 'int-':
                        if isinstance(paradict[namepara]['value'],str): 
                                if not paradict[namepara]['value'] == '-': 
                                        raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkisce2parafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),"int or '-'",jobcoreg.log))
                        else: 
                                if not isinstance(paradict[namepara]['value'],int): 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,checkisce2parafromdict.__name__,__file__,__copyright__,
                                                "parameter %s in %s" % (namepara,namestep),"int or '-'",jobcoreg.log))

                elif infopara['modepara'][idx] == 'float':
                        if not isinstance(paradict[namepara]['value'],float): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkisce2parafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'float',jobcoreg.log))
                        
                elif infopara['modepara'][idx] == 'float-':
                        if isinstance(paradict[namepara]['value'],str): 
                                if not paradict[namepara]['value'] == '-': 
                                        raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkisce2parafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),"float or '-'",jobcoreg.log))
                        else: 
                                if not isinstance(paradict[namepara]['value'],float): 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,checkisce2parafromdict.__name__,__file__,__copyright__,
                                                "parameter %s in %s" % (namepara,namestep),"float or '-'",jobcoreg.log))
                        
                elif infopara['modepara'][idx] == 'pathuser':
                        check_error = False
                        if not paradict[namepara]['value'] == None: 
                                if not paradict[namepara]['value'] == 'user': 
                                        check_error = True
                                else: 
                                        if not os.path.isfile(paradict[namepara]['value']):
                                                check_error = True
                        if check_error: 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkisce2parafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),"None, user or a file",jobcoreg.log))

        return jobcoreg

################################################################################
## Create a log file name for the ISCE-2 step
################################################################################
def createisce2log(log,cur_dir,step,gui=False):
        """Create the name of the log for ISCE-2 

        The function creates the name of the log for ISCE-2.   

        Args:
                log (str or None): log file from the job
                cur_dir (str) : current directory
                step (str) : step name
        
        Returns:
                (str or None): isce2 log file name

        """

        if not log == None: 
                if gui == True: 
                        isce2log = os.path.abspath(log)
                else:
                        isce2log = os.path.abspath(log).split('.')[0] + '_isce2_'+ step +'.log'
        else:
                if not platform.system() == 'Windows':
                        isce2log = '/dev/null'
                else:
                        isce2log = cur_dir+os.sep+'isce2_'+ step +'.log'

        return isce2log

################################################################################
## Run a subprocess for ISCE-2
################################################################################
def subprocessrun(cmd,
                input_card,
                job,
                isce2log,
                modeSAT):
        """Run a subprocess for ISCE-2 

        The function will run a subprocess for ISCE-2  

        Args:
                cmd (list) : command
                input_card (str) : input card 
                job (ezinsar job) : ezinsar job
                isce2log (str or None): log file from the job
                modeSAT (str): can be IW or SM

        """
        os.environ['PATH'], os.environ['PYTHONPATH'] = isce2checkenv(mode=modeSAT,verbose=False) 
        my_env = os.environ.copy()
        my_env["PATH"] = f"/usr/local/bin:{my_env['PATH']}"
        my_env["PYTHONPATH"] = f"/usr/local/bin:{my_env['PYTHONPATH']}"

        usermessage.ezprint('Run ISCE-2:',job.log,job.verbose)
        usermessage.ezprint('\tCommand: %s' % (cmd),job.log,job.verbose)

        if not input_card == None:
                param = []
                with open(input_card,'r') as fi:
                        for li in fi:
                                param.append(li)
                usermessage.ezprint('\tParameters: %s' % (cmd),job.log,job.verbose)
                usermessage.ezprint('%s' % ('\t\t'+'\t\t'.join(param)),job.log,job.verbose)

        # # Modification for consisntency of PATHs
        # if 'make_single_reference_stack_isce' in cmd[0] or 'make_small_baselines_isce' in cmd[0] or 'croppingstack_ISCE' in cmd[0]:
        #         cmd.insert(0, 'PYTHONPATH=%s' % (my_env["PYTHONPATH"]))
        #         cmd.insert(0, 'PATH=%s' % (my_env["PATH"]))

        pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env = my_env)

        try: 
                if not len("".join(pr.stdout.readline().strip().split())) == 0:
                        while (line := pr.stdout.readline()) != "":
                                usermessage.ezprint(line.replace('\n',' '),isce2log,job.verbose)     

                if not len("".join(pr.stderr.readline().strip().split())) == 0:
                        while (line := pr.stderr.readline()):
                                usermessage.ezprint(line.replace('\n',' '),isce2log,job.verbose)   
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the ISCE2 processing',job.log))
                
        except KeyboardInterrupt:
                pr.terminate()
                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'User terminate',job.log))

        usermessage.ezprint('\tdone',job.log,job.verbose)

################################################################################
## Wrapper of the subprocess of ISCE-2
################################################################################
def wrappersubprocess(list_cmd,
                nb_worker,
                job,
                isce2log,
                modeSAT):
        """Wrapper for ISCE-2 subprocesses 

        The function will run several subprocesses for ISCE-2 regarding the number of workers  

        Args:
                list_cmd (dict) : commands
                nb_worker (str) : number of workers
                job (ezinsar): ezinsar job
                isce2log (str or None): log file from the job
                modeSAT (str): can be IW or SM

        """
        
        maxidx_job = len(list(list_cmd.keys())) - 1
        i = 0
        while i <= maxidx_job:
                for it in np.arange(i,i+nb_worker,1):

                        if it <= maxidx_job:
                                exec("p%s = multiprocessing.Process(target=subprocessrun, args=(list_cmd['cmd%s'][0], list_cmd['cmd%s'][1], job, isce2log, modeSAT))" % (it,it,it) )
                                exec('p%s.start()' % (it))

                for it in np.arange(i,i+nb_worker,1):
                        if it <= maxidx_job:
                                exec('p%s.join()' % (it))
                        i = i + 1
