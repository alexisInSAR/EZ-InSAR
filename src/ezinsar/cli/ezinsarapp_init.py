#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Create a xml file which can be used as an EZ-InSAR job

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 
        
        $ ezinsar init --help

Changelog:
    * 3.3.1: Several changes, Dec. 2025, Alexis Hrysiewicz
        * Change the import line
        * Delete the link to the EZ-InSAR GAMMA module
    * 3.0.0: Initial version, Dec. 2024

"""

__docstringapp__ = """EZ-InSAR application: Create a xml file which can be used as an EZ-InSAR job

usage: ezinsar init [-p <processor>] [] [-f <file>] [-j <file>] [-m <string> ][options]

Optional-arguments:
    -p, --processor <str>   InSAR processor [default: isce2]
    -t, --template <str>    Template. Can be coreg, ifgstack, tsprocessing [default: None]
    -a, --approach <str>    InSAR Time Series Analysis approach [default: sbas]
    -f, --file <file>       .xml file for saving the template  [default: ezinsarjob]
    -j, --job <file>        EZ-InSAR job .xml file [default: None]
    -m, --modify <string>   Key string to modify a parameter
    --display               Display the job parameter

Other-options:
    --nolog         No logging
    -h, --help
    -q, --quiet     Suppress verbose

"""

from docopt import docopt

import ezinsar.job as ez
from ezinsar import usermessage
from ezinsar import constants
__copyright__ = constants.__copyright__

from ezinsar.eicomponents.processor.isce2module import isce2coregistration
from ezinsar.eicomponents.processor.isce2module import isce2ifgstack
from ezinsar.eicomponents.processor.snapmodule import snapcoregistration, snapintstack
from ezinsar.eicomponents.processor.mintpymodule import mintpytsprocessing
from ezinsar.eicomponents.processor.stampsmodule import stampstsprocessing

def main():
    """Main function"""
    args = docopt(__docstringapp__)
    
    if args['--quiet']: 
        verbose = False
    else:
        verbose = True
    
    if args['--nolog']: 
        log = None
    else: 
        log = 'ezinsar.log'

    if not args['--template'] in ['None','coreg','ifgstack','intstack','tsprocessing','offsetprocessing']: 
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
            'Wrong selected template.',None))

    if args['--display'] == False: 
        if args['--modify'] == None:
            # Creation of the new processing job
            usermessage.ezprint('Creation of the new processing job with the %s script: %s' % (__name__,args['--template']),log,verbose)

            if args['--job'] == 'None':
                job = ez.EIjob(satellite='S1',satmode='IW')
                job.importroi(input=[0,0,0,0],verbose=False)
            elif not args['--job'] == 'None':
                job = ez.load(args['--job'])
                if args['--template'] == 'coreg': 
                    job.initiatecoreg(processor=args['--processor'])
                    job.coregistration.check(verbose=verbose)
                elif args['--template'] == 'intstack': 
                    job.initiateint(processor=args['--processor'])
                    job.intstack.check(verbose=verbose)
                elif args['--template'] == 'ifgstack': 
                    job.initiateifg(processor=args['--processor'])
                    job.ifgstack.check(verbose=verbose)
                elif args['--template'] == 'tsprocessing': 
                    job.initiatets(processor=args['--processor'],mode=args['--approach'])
                    job.tsprocessing.check(verbose=verbose)
                elif args['--template'] == 'offsetprocessing': 
                    job.initiateoff(processor=args['--processor'])
                    job.offsetprocessing.check(verbose=verbose)

            else: 
                if args['--template'] == 'coreg':  
                    job = eval("%scoregistration.coregistration()" % (args['--processor']))
                elif args['--template'] == 'intstack': 
                    job = eval("%sintstack.intstack()" % (args['--processor']))
                elif args['--template'] == 'ifgstack': 
                    job = eval("%sifgstack.ifgstack()" % (args['--processor']))
                elif args['--template'] == 'offsetprocessing': 
                    job = eval("%soffsetprocessing.offsetprocessing()" % (args['--processor']))
                elif args['--template'] == 'tsprocessing': 
                    if args['--processor'] == 'mintpy' and args['--approach'] == 'sbas':
                        job = eval("%stsprocessing.sbas()" % (args['--processor']))  
                    elif args['--processor'] == 'stamps' and args['--approach'] == 'ps':
                        job = eval("%stsprocessing.ps()" % (args['--processor']))  
                    elif args['--processor'] == 'stamps' and args['--approach'] == 'sbas':
                        job = eval("%stsprocessing.sbas()" % (args['--processor']))  
                    elif args['--processor'] == 'stamps' and args['--approach'] == 'merged':
                        job = eval("%stsprocessing.merged()" % (args['--processor']))  
                    else:
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                        'The approach for the TS processing is not correct.',None))
                else:
                    raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                        'The processor is not correct.',None))
                
                job.check(verbose=verbose)

        else: 
            # Modification of a parameter
            usermessage.ezprint('Modification of the file: %s' % (args['--file'].split('.')[0]+'.ei'),log,verbose)

            job = ez.load(args['--file'].split('.')[0]+'.ei')
            para = args['--modify'].split('=')[0].split(':')
            if len(para) == 1: 
                textpara = para[0]
            else: 
                textpara = "%s['%s']['value']" % (para[0],para[-1])
            newvalue = args['--modify'].split('=')[-1]
            
            if args['--template'] == 'coreg': 
                cmdi = 'job.coregistration.'
            elif args['--template'] == 'intstack':
                cmdi = 'job.intstack.'
            elif args['--template'] == 'ifgstack':
                cmdi = 'job.ifgstack.'
            elif args['--template'] == 'tsprocessing':
                cmdi = 'job.tsprocessing.'
            elif args['--template'] == 'offsetprocessing':
                cmdi = 'job.offsetprocessing.'
            else:
                cmdi = 'job.'
                    
            cmdifull = cmdi + textpara + '=' + newvalue
            cmdidisplay = cmdi + textpara
            try:
                prevpara = eval('%s' % (cmdidisplay))
            except:
                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                    'The key string %s has not been found. Please check the used template.' % (cmdidisplay),None))

            usermessage.ezprint('Modification of a %s EZ-InSAR processing job:' % (str(type(job))),log,verbose)
            usermessage.ezprint('\tThe previous parameter for %s is %s.' % (cmdidisplay,prevpara),log,verbose)
            usermessage.ezprint('\tIt will be modify by %s.' % (newvalue),log,verbose)

            exec(cmdifull)
            job.check(verbose=False)

        # Modification of the logging mode
        if args['--nolog']:
            job.log = None

        # Save the new file
        ez.save(job,args['--file'].split('.')[0],verbose=False)

    else: 
        # Display the EZ-InSAR job
        job = ez.load(args['--file'].split('.')[0]+'.ei')
        job.check(verbose=True)

if __name__=='__main__':
    main()