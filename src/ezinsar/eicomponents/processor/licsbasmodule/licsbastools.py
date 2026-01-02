#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to add some tools for the StaMPS processing class

The module adds some tools for the StaMPS processing class. 
    
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
import subprocess

from ezinsar import usermessage
from ezinsar import constants
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""
################################################################################
## Run a subprocess for StaMPS
################################################################################
def subprocessrun(cmd,
                verbose,
                log):
        """Run a subprocess for LiCSBAS 

        The function will run a subprocess for LiCSBAS 

        Args:
                cmd (list) : command
                verbose (bool): verbose
                log (str or None): log file from the job

        """

        os.environ['PATH'] = os.environ['PATH']+':'+constants.__requirement_LiCSBAS__+':.' 
        os.environ['PYTHONPATH'] = os.environ['PYTHONPATH']+':'+constants.__requirement_LiCSBAS__+':.' 

        my_env = os.environ.copy()
        my_env["PATH"] = f"/usr/local/bin:{my_env['PATH']}"
        my_env["PYTHONPATH"] = f"/usr/local/bin:{my_env['PYTHONPATH']}"

        usermessage.ezprint('Run LiCSBAS:',log,verbose)
        usermessage.ezprint('\tCommand: %s' % (cmd),log,verbose)

        os.system(cmd)

        # pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, env=my_env)

        # try: 
        #         while (line := pr.stdout.readline()) != "":
        #                 usermessage.ezprint(line.replace('\n',' '),log,verbose)

        #         if not len("".join(pr.stderr.readline().strip().split())) == 0:
        #                 while (line := pr.stderr.readline()):
        #                         usermessage.ezprint(line.replace('\n',' '),log,verbose)  
        #                 raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the LiCSBAS processing',log))
                
        # except KeyboardInterrupt:
        #         pr.terminate()
        #         raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the StaLiCSBASMPS processing: user terminate',log))

        usermessage.ezprint('\tdone',log,verbose)

################################################################################
## Check the parameters of a dict
################################################################################
def checklicsbasparafromdict(paradict,jobts,verbose):
        """Check the parameters of a dict for an ``ezinsar`` job using LiCSBAS

        The function checks the parameters of a dict for an job with the LiCSBAS processor.

        Args:
                paradict (dict): parameter
                jobts (``ezinsar.job``): EZ-InSAR job for LiCSBAS processor
                verbose (bool): verbose. 

        Returns:
                ``ezinsar.job`` job: Return an EZ-InSAR processing job class
        
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

                if infopara['modepara'][idx] == 'bool':
                        if not isinstance(paradict[namepara]['value'],bool):
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checklicsbasparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'True or False',jobts.log))

                elif infopara['modepara'][idx] == 'list':
                        if not paradict[namepara]['value'] in infopara['valuelist'][idx]: 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checklicsbasparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'%s' % (infopara['valuelist'][idx]),jobts.log))
                        
                elif infopara['modepara'][idx] == 'email':
                        if not isinstance(paradict[namepara]['value'],str): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checklicsbasparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'str',jobts.log))
                        
                elif infopara['modepara'][idx] == 'int':
                        if not isinstance(paradict[namepara]['value'],int): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checklicsbasparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'int',jobts.log))

                elif infopara['modepara'][idx] == 'int-':
                        if isinstance(paradict[namepara]['value'],str): 
                                if not paradict[namepara]['value'] == '-': 
                                        raise TypeError(usermessage.typeerrormsg(
                                        __name__,checklicsbasparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),"int or '-'",jobts.log))
                        else: 
                                if not isinstance(paradict[namepara]['value'],int): 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,checklicsbasparafromdict.__name__,__file__,__copyright__,
                                                "parameter %s in %s" % (namepara,namestep),"int or '-'",jobts.log))

                elif infopara['modepara'][idx] == 'float':
                        if not isinstance(paradict[namepara]['value'],float): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checklicsbasparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'float',jobts.log))
                        
                elif infopara['modepara'][idx] == 'float-':
                        if isinstance(paradict[namepara]['value'],str): 
                                if not paradict[namepara]['value'] == '-': 
                                        raise TypeError(usermessage.typeerrormsg(
                                        __name__,checklicsbasparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),"float or '-'",jobts.log))
                        else: 
                                if not isinstance(paradict[namepara]['value'],float): 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,checklicsbasparafromdict.__name__,__file__,__copyright__,
                                                "parameter %s in %s" % (namepara,namestep),"float or '-'",jobts.log))
                        
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
                                        __name__,checklicsbasparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),"None, user or a file",jobts.log))

        return jobts