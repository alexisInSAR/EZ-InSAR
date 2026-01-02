#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Download Sentinel-1 orbit files

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 
        
        $ ezinsar S1orbit --help

Changelog:
    * 3.3.1: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 3.0.0: Initial version, Dec. 2024

"""

__docstringapp__ =  """EZ-InSAR application: Download Sentinel-1 orbit files

usage: 
    ezinsar S1orbit -f <path_SLC> -o <path_orbit> [options]

Arguments:
    -f, --file <str>            List of SLCs or EZ-InSAR job file (.ei for extension) 
    -o, --path_orbit <str>      Path of the orbit files

SLC-options
    -s, --path_SLC <str>        Path of the .zip/.safe files
    
Server-options:
    -u, --username <str>        Username of the Sentinel-1 server 
    -p, --password <str>        Password of the Sentinel-1 server
    --server <str>              Server  [default: Copernicus]

Other-options:
    --nolog                     No logging
    -h, --help
    -q, --quiet                 Suppress verbose

"""

from docopt import docopt
from datetime import datetime 

import ezinsar.job as ez

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

    if '.ei' in args['--file']: 
        # If job is given
        jobezinsar = ez.load(args['--file'])

    else:
        # If job is not given 
        jobezinsar = ez.EIjob(verbose=verbose,log=log)

        jobezinsar.workdirectory = '.'
        
        if not args['--path_SLC'] == None:
            jobezinsar.pathSLC = args['--path_SLC']
        else:
            jobezinsar.pathSLC = '.'

        jobezinsar.pathorbit = args['--path_orbit']
        jobezinsar.pathaux = '.'
        jobezinsar.date1 = datetime.strptime('1999-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')
        jobezinsar.date2 = datetime.strptime('2030-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')
        jobezinsar.importroi(input=[-180,-90,180,90])
        jobezinsar.mkdir()
        jobezinsar.check()

        if not args['--path_SLC'] == None:
            jobezinsar.initiateSLC(mode='onfile')
        else:
            jobezinsar.initiateSLC(mode='list',file=args['--file'])

    # Download the orbit files
    if args['--username'] == None and args['--password'] == None:
        jobezinsar.downloadorbit(server=args['--server'])
    if args['--username'] == None and not (args['--password'] == None):
        jobezinsar.downloadorbit(password=args['--password'],server=args['--server'])
    if not (args['--username'] == None) and  args['--password'] == None:
        jobezinsar.downloadorbit(username=args['--username'],server=args['--server'])
    if not (args['--username'] == None) and  not (args['--password'] == None):
        jobezinsar.downloadorbit(username=args['--username'],password=args['--password'],server=args['--server'])

if __name__=='__main__':
    main()