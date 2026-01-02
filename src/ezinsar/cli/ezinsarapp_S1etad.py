#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Download Sentinel-1 ETAD files

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 
        
        $ ezinsar S1etad --help

Changelog:
    * 3.3.1: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 3.2.1: Initial version, Aug. 2025

"""

__docstringapp__ =  """EZ-InSAR application: Download Sentinel-1 ETAD files

usage: 
    ezinsar S1etad -f <file>  [options]

Arguments:
    -f, --file <str>            EZ-InSAR job file (.ei for extension) 
    
Directory-options:
    -o, --path_aux <str>        Path of the orbit files

Server-options:
    -u, --username <str>        Username of the Sentinel-1 server 
    -p, --password <str>        Password of the Sentinel-1 server

Other-options:
    --nolog                     No logging
    -h, --help
    -q, --quiet                 Suppress verbose

"""

from docopt import docopt
import ezinsar.job as ez

def main():
    """Main function"""
    args = docopt(__docstringapp__)
            
    jobezinsar = ez.load(args['--file'],verbose=(args['--quiet']==False))
    if args['--nolog']: 
        jobezinsar.log = None
    if args['--quiet']: 
        jobezinsar.verbose = False
    else: 
        jobezinsar.verbose = True

    if not args['--path_aux'] == None: 
        jobezinsar.pathaux = args['--path_aux']

    if args['--username'] == None and args['--password'] == None:
        jobezinsar.downloadETAD()
    if args['--username'] == None and not (args['--password'] == None):
        jobezinsar.downloadETAD(password=args['--password'])
    if not (args['--username'] == None) and  args['--password'] == None:
        jobezinsar.downloadETAD(username=args['--username'])
    if not (args['--username'] == None) and  not (args['--password'] == None):
        jobezinsar.downloadETAD(username=args['--username'],password=args['--password'])

if __name__=='__main__':
    main()