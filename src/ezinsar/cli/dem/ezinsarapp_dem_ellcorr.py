#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZ-InSAR DEM application**

EZ-InSAR DEM application to apply the ellipsoid correction for a DEM

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
        The help can be launched by using the following command:: 

                $ ezinsar dem ellcorr --help

Changelog:
        * 3.3.0: Initial version, Sep. 2025

"""
from docopt import docopt
from ezinsar import constants

__docstringapp__ = """EZ-InSAR DEM application

Apply the ellipsoid correction for a DEM

usage: 
        ezinsarapp_dem ellcorr -f <str> -o <str> -e <str> [options]

Arguments: 
        -f, --input <str>       Input file
        -o, --output <str>      Output file
        -e, --ellpisoid <str>   Ellipsoid code or file

Account-Options: 
        --nodata <bool>        If True, the nodata values will be masked [default: True]
        --format <str>         Output format. [default: GTiff]


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

        demfunctions.ellcorrection(args['--input'],
                args['--output'],
                args['--ellpisoid'],
                format = args['--format'],
                nodata = args['--nodata'],
                verbose=verbose,
                log=log)

if __name__=='__main__':
    main()

        