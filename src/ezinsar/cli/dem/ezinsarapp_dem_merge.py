#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZ-InSAR DEM application**

EZ-InSAR DEM application to merge the DEM tiles

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
        The help can be launched by using the following command:: 

                $ ezinsar dem merge --help

Changelog:
        * 3.3.0: Initial version, Sep. 2025

"""
from docopt import docopt
from ezinsar import constants
import random
import string 
import os

__docstringapp__ = """EZ-InSAR DEM application

Merge the DEM tiles

usage: 
        ezinsarapp_dem merge -f <str> -o <str> [options]

Arguments: 
        -f, --pathfile <str>            Path of the file, i.e., ./DEMfile/*.tif
        -o, --output <str>              Output file

Processing--Options: 
        --format <str>                  Output format. [default: GTiff]

Other-Options: 
        --quiet         Block the verbose
        --nolog         Block the log 
        -h, --help

"""

from ezinsar.eicomponents.demmodule import demfunctions

def main():
        """Main function"""
        args = docopt(__docstringapp__)
        
        # Input parameters
        if args['--quiet']: 
                verbose = False
        else:
                verbose = True
        
        if args['--nolog']: 
                log = None
        else: 
                log = 'ezinsarDEM.log'

        demfunctions.mergetiles(args['--pathfile'],
                args['--output'],
                format=args['--format'],
                verbose=verbose,
                log=log)

if __name__=='__main__':
    main()

        