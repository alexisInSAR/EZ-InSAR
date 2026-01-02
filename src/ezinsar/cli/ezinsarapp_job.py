#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Advanced tools for the EZ-InSAR job 

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 
        
        $ ezinsar job --help

Changelog:
    * 3.3.1: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 3.2.0: Initial version, Jul., 2025

"""


__docstringapp__ = """EZ-InSAR application: Advanced tools for the EZ-InSAR job

usage: ezinsar job -f <EZ-InSARfile> -t <selected_tool> [options]

Arguments:
    -f, --file <str>        Path of the EZ-InSAR file
    -t, --tool <str>        Selected tools

Changepaths-related options
    --rootname <str>        New path of the root. For 'changepaths tool'. [Default: None]

Clearprocess-related options
    --process <str>         List of processing which will be removed. Comma-separated. [Default: None]

Other-options:
    --nolog         No logging
    -h, --help
    -q, --quiet     Suppress verbose

The available tools are as follows:
    - 'changepaths': smart modifications of directory/file paths inside an EZ-InSAR job
    - 'clearprocess': remove the processing available for the EZ-InSAR job
"""
 
from docopt import docopt

import ezinsar.job as ez
from ezinsar import usermessage
from ezinsar import constants
__copyright__ = constants.__copyright__

listtools = ['changepaths','clearprocess']
listprocessing = ['coregistration','ifgstack','tsprocessing','intstack','offsetprocessing']

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

    if not args['--tool'] in listtools:
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
            'The available tools are %s' % (listtools),log))

    #########################
    ## changepaths
    #########################
    if args['--tool'] == 'changepaths':
        if args['--rootname'] == 'None': 
            raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
            '--rootname is required for this tools',log))
        else:
            job = ez.load(args['--file'].split('.')[0]+'.ei')
            job.changedir(args['--rootname'],verbose=verbose,log=log)
            ez.save(job,args['--file'].split('.')[0],verbose=False)

    #########################
    ## clearprocess
    #########################
    if args['--tool'] == 'clearprocess':
        if args['--process'] == 'None': 
            raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
            '--process is required for this tools',log))
        else:
            if args['--process'] == 'all':
                args['--process'] = listprocessing
            else:
                args['--process'] = args['--process'].split(',')

            for proci in args['--process']:
                if proci in listprocessing:
                    usermessage.ezprint('Delete the processing %s in %s' % (proci,args['--file']),log,verbose)  
                    job = ez.load(args['--file'].split('.')[0]+'.ei',bypasscheck=True,verbose=False)
                    exec('job.%s = None' % (proci))
                    ez.save(job,args['--file'].split('.')[0],verbose=False)
                    usermessage.ezprint('\tdone',log,verbose) 
                else:
                    raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                        '%s is not an EZ-InSAR processing' % (proci),log))

        
if __name__=='__main__':
    main()