#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to run an EZ-InSAR processing job

The module allows to run a EZ-InSAR processing job from an `ezinsar` job. 
    
    (From `ezinsar` package)

Changelog:
        * 3.3.1: Several changes, Dec. 2025, Alexis Hrysiewicz
                * Check the check method (if EIjob in string)
                * Delete the link to the EZ-InSAR GAMMA module
        * 3.3.0: Bug fixes, Oct. 2025, Alexis Hrysiewicz
        * 3.2.0: Several changes, Jun. 2025, Alexis Hrysiewicz
                * Add the new processing
                * Modify the docker running
        * 3.1.0: Add the Offset-Tracking processing for GAMMA, Feb. 2025, Alexis Hrysiewicz
        * 3.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
from timeit import default_timer as timer
from datetime import timedelta
from typing import Optional
import copy 
import os
import shutil
import glob 
from pathlib import Path
import platform

from ezinsar import ezinsarprocessor
from ezinsar import usermessage
from ezinsar import constants
from ezinsar.eicomponents.jobmodule import useremail, jobtools
from ezinsar.eicomponents.processor.dorismodule import dorisStripMapfunction, dorisifgStripMapfunction
from ezinsar.eicomponents.processor.snapmodule import snapStripMapfunction, snapintfunction, snapIWfunction, snapifgfunction
from ezinsar.eicomponents.processor.isce2module import isce2IWfunction, isce2StripMapfunction
from ezinsar.eicomponents.processor.mintpymodule import mintpytools 
from ezinsar.eicomponents.processor.miaplpymodule import miaplpytools 
from ezinsar.eicomponents.processor.sarveymodule import sarveytools 
from ezinsar.eicomponents.processor.stampsmodule import stampsfunctions, stampstools
from ezinsar.eicomponents.processor.licsbasmodule import licsbasfunctions, licsbastools

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Function to run the coregistration
################################################################################
def run(job, step: Optional[bool] = 'all', verbose: Optional[bool] = None, docker: Optional[bool] = False):
        """Run the processing steps 

        The function runs the different processing steps, from an ``ezinsar.coregistration``.   

        Args:
                job (``ezinsar.job``): EZ-InSAR processing job
                step (str): name of the coregistration step [Default: 'all'].
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                docker (bool): dockerisation of the processing step(s) [Default: `False`].

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
       
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,run.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        
        if not isinstance(docker,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,run.__name__,__file__,__copyright__,
                        'docker','True or False',job.log))

        ## Check the job type
        processing = None
        processor = None 

        if 'doris' in str(type(job)):
                processor= 'doris'
                if 'coregistration' in str(type(job)): 
                        processing = 'coregistration'
                else: 
                        processing = 'ifgstack'

        elif 'snap' in str(type(job)):
                processor= 'snap'
                if 'coregistration' in str(type(job)): 
                        processing = 'coregistration'
                elif 'ifgstack' in str(type(job)):
                        processing = 'ifgstack'
                else: 
                        processing = 'intstack'

        elif 'isce2' in str(type(job)):
                processor= 'isce2'
                if 'coregistration' in str(type(job)): 
                        processing = 'coregistration'
                else: 
                        processing = 'ifgstack'
        
        elif 'stamps' in str(type(job)):
                processor= 'stamps'
                processing = 'tsprocessing'

        elif 'mintpy' in str(type(job)):
                processor= 'mintpy'
                processing = 'tsprocessing'

        elif 'miaplpy' in str(type(job)):
                processor= 'miaplpy'
                processing = 'tsprocessing'

        elif 'sarvey' in str(type(job)):
                processor= 'sarvey'
                processing = 'tsprocessing'

        elif 'licsbas' in str(type(job)):
                processor= 'licsbas'
                processing = 'tsprocessing'

        elif 'EIjob' in str(type(job)):
                raise ValueError(usermessage.errormsg(__name__,run.__name__,__file__,__copyright__,
                                'An EZ-InSAR processing job is required.',job.log))

        else: 
                raise ValueError(usermessage.errormsg(__name__,run.__name__,__file__,__copyright__,
                                'Unknown processing job.',job.log))

        usermessage.openingmsg(__name__,run.__name__,__file__,__copyright__,'Run the %s using %s processor' % (processing,processor),job.log,verbose)

        # Detection of the steps 
        stepdetect = usermessage.getprocessingstep(job,mode='normal')
        if isinstance(step,str): 
                if step == 'all':
                        step = stepdetect
                else:
                        step = step.split(',')
        elif isinstance(step,list):
                if 'all' in step: 
                        step = stepdetect

        for stepi in step:
                if not stepi in stepdetect+['all']:
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,run.__name__,__file__,__copyright__,
                                'step',"in %s" % (stepdetect+['all']) ,job.log))

        ## Run the coregistration 
        for stepi in step:
                modeerror = False
                if  eval("job.%s['done']['value']" % (stepi)) == True:
                        usermessage.warningmsg(__name__,run.__name__,__file__,'The selected step has already done.',job.log,verbose)

                ## NORMAL MODE
                if docker == False: 
                        starttime = timer()

                        # For ISCE-2
                        if processor == 'isce2':
                                if (job.satmode == 'IW' and job.satellite == 'S1'):
                                        exec("job = isce2IWfunction.%s(job,verbose = verbose)" % (stepi))
                                else:
                                        exec("job = isce2StripMapfunction.%s(job,verbose = verbose)" % (stepi))

                        # For Doris
                        elif processor == 'doris':
                                if not (job.satmode == 'IW' and job.satellite == 'S1'):
                                        if processing == 'coregistration':
                                                exec("job = dorisStripMapfunction.%s(job,verbose = verbose)" % (stepi))
                                        else:
                                                exec("job = dorisifgStripMapfunction.%s(job,verbose = verbose)" % (stepi))

                        # For Snap
                        elif processor == 'snap':
                                if processing == 'coregistration':
                                        if (job.satmode == 'IW' and job.satellite == 'S1'):
                                                exec("job = snapIWfunction.%s(job,verbose = verbose)" % (stepi))
                                        else:
                                                exec("job = snapStripMapfunction.%s(job,verbose = verbose)" % (stepi))

                                elif processing == 'ifgstack':
                                        exec("job = snapifgfunction.%s(job,verbose = verbose)" % (stepi))
                                else:
                                        exec("job = snapintfunction.%s(job,verbose = verbose)" % (stepi))

                        # For StaMPS
                        elif processor == 'stamps':
                                exec("job = stampsfunctions.%s(job,verbose = verbose)" % (stepi))

                        # For MintPY
                        elif processor == 'mintpy':
                                job = mintpytools.wrappermintpy(job,stepi,verbose,job.log)

                        # For MiaplPy
                        elif processor == 'miaplpy':
                                job = miaplpytools.wrappermiaplpy(job,stepi,verbose,job.log)

                        # For SARvey
                        elif processor == 'sarvey':
                                job = sarveytools.wrappersarvey(job,stepi,verbose,job.log)

                        # For LiCSBAS
                        elif processor == 'licsbas':
                                exec("job = licsbasfunctions.%s(job,verbose = verbose)" % (stepi))
                                
                        ## End of the processing 
                        usermessage.ezprint('NORMAL TERMINATION in %s' % (timedelta(seconds=timer()-starttime)),job.log,verbose)

                        if processor in ['doris','isce2','snap']:
                                usermessage.warningmsg(__name__,run.__name__,__file__,'EZ-InSAR is not able to know if the process was correctly finished for the ISCE-2, SNAP-GPT and Doris processors.',job.log,verbose)

                        # except:
                        #         modeerror = True 
                        #         usermessage.ezprint('ERROR: ABNORMAL TERMINATION in %s seconds' % (timedelta(seconds=timer()-starttime)),job.log,verbose)

                        # ## Emai information
                        # if job.email['send']['value'] == True and job.email['mode']['value'] == 'all':
                        #         usermessage.ezprint('Send the user email.',job.log,verbose)
                        #         useremail.send_email(job,stepi,error = modeerror)
                        # if modeerror == True:
                        #         raise ValueError(usermessage.errormsg(__name__,run.__name__,__file__,__copyright__,
                        #                 'ERROR in the EZ-InSAR processing...',None))

                ## FOR DOCKER
                else:
                        usermessage.openingmsg(__name__,run.__name__,__file__,__copyright__,'Start the EZ-InSAR processing in Docker container',job.log,verbose)
                        usermessage.ezprint('The container will be created and deleted after processing',job.log,verbose)

                        jobdocker, _, oldpath, newpath, rootdir, newrootdir = jobtools.changepath(job,locklog=False,verbose=job.verbose,log=job.log)
                        usermessage.warningmsg(__name__,run.__name__,__file__,'The next lines will disappear in the next version of the log file.',job.log,verbose)

                        # Write the EZ-InSAR file
                        ezinsarprocessor.save(jobdocker,rootdir+'/jobdockertmp.ei',log=job.log,verbose=False)

                        # Create the command                       
                        cmdmt = ''
                        for idx, vi in enumerate(oldpath): 
                                cmdmt = cmdmt + '-v %s:%s ' % (oldpath[idx],newpath[idx])
                                        
                        cmd = 'docker run --rm --name ezinsar0 %s -it %s /bin/bash -c "cd /root; source .bashrc; %s; ezinsar run -f %s -s %s --nolicensecheck"' % (cmdmt,constants.__nameDockerImage__,constants.create_docker_string(),newrootdir+'/jobdockertmp.ei',stepi)
                        usermessage.ezprint('The Docker command is: \n\t%s' % (cmd),job.log,verbose)

                        usermessage.warningmsg(__name__,run.__name__,__file__,'EZ-InSAR is not able to retrieve the processing log with the current version of EZ-InSAR. Please wait...',job.log,verbose)

                        # Run the processing 
                        status = os.system(cmd)

                        ## Extract the reference date if modified
                        if status == 0: 
                                job2 = ezinsarprocessor.load(rootdir+'/jobdockertmp.ei',verbose=False,modelog=False,bypasscheck=True)
                                try: 
                                        job.refdate = job2.refdate
                                except:
                                        a = 'dummy'

                        os.remove(rootdir+os.sep+'jobdockertmp.ei')

                        # Messages
                        if status == 0: 
                                usermessage.ezprint('Successfull processing in the Docker container',job.log,verbose)
                                exec('job.%s["done"]["value"] = bool(1)' % (stepi))
                        else: 
                                raise ValueError(usermessage.errormsg(__name__,run.__name__,__file__,__copyright__,
                                        'Error during the processing in the Docker container',None))

        return job

