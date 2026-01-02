#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Update an EZ-InSAR processing job

This application allows to update an EZ-InSAR processing job (i.e., coregistration, ifgstack, etc.). 

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 

        $ ezinsar update --help

Changelog:
    * 3.3.1: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 3.0.0: Initial version, Dec. 2024

"""

__docstringapp__ =  """EZ-InSAR application: Update an EZ-InSAR processing job

usage: ezinsar update -f <file> [options]

Arguments:
    -f, --file <str>        EZ-InSAR job file 

Other-options:
    -u, --username <str>    Username of the Sentinel-1 server 
    -p, --password <str>    Password of the Sentinel-1 server
    -h, --help
    -q, --quiet         Suppress verbose

"""

from docopt import docopt
import numpy as np
from datetime import datetime

import ezinsar.job as ez

def main():
    """Main function"""
    args = docopt(__docstringapp__)
    
    if args['--quiet']: 
        verbose = False
    else:
        verbose = True

    # Load the EZ-InSAR job
    job = ez.load(args['--file'])
    job.date2 = datetime.today()

    # Check the SLC list
    job.checkSLClist()

    # Check the new images
    if not job.satellite == 'S1':
        job.initiateSLC(mode='onfile')
    else:
        job.initiateSLC(server=job.SLClist['Server'][0])
        job.downloadSLC(username=args['--username'],password=args['--password'])
        job.downloadorbit(server=job.SLClist['Server'][0],username=args['--username'],password=args['--password'])
        job.checkSLClist(verbose=verbose)
        job.printSLClist(verbose=verbose)

    ## For the coregistration 
    if not job.coregistration == None:
        job.coregistration.run(step=['updatestack'],verbose=verbose)
    # ## For the ifgstack     
    # if not job.ifgstack == None:
    #     job.ifgstack.run(step=['all'],verbose=verbose)
    # ## For the intstack     
    # if not job.intstack == None:
    #     if job.intstack.processor == 'snap':
    #         step = ['update']
    #     else:
    #         step = ['all']
        # job.intstack.run(step=step,verbose=verbose)
    
    ## Save the job file
    ez.save(job,args['--file'],verbose=verbose)
       
if __name__=='__main__':
    main()