#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZ-InSAR DEM application**

EZ-InSAR DEM application to mask the DEM raster

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
        The help can be launched by using the following command:: 

                $ ezinsar dem mask --help

Changelog:
        * 3.3.0: Initial version, Sep. 2025

"""
from docopt import docopt
from ezinsar import constants
import random
import string 
import os

__docstringapp__ = """EZ-InSAR DEM application

Mask the DEM tiles

usage: 
        ezinsarapp_dem mask [extract | apply | toshp] -f <str> -o <str> [options]

Arguments: 
        -f, --input <str>       Input file
        -o, --output <str>      Output file

Options: 
        --mask <str>            Mask file (required for apply command)
        --value <str>           Value used to create a mask. Default is the nodata value [default: None]
        --format <str>          Output format. [default: GTiff]

toshp-Options: 
        --dilate <int>          Dilatation factor [default: 0]
        --fillholes             Fill the holes based on the same structuring element

Other-Options: 
        --quiet         Block the verbose
        --nolog         Block the log 
        -h, --help

"""

from ezinsar.eicomponents.demmodule import demfunctions

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
                log = 'ezinsarDEM.log'

        if args['extract']: 
                demfunctions.extractmask(args['--input'],
                        args['--output'],
                        args['--value'],
                        format=args['--format'],
                        verbose=verbose,
                        log=log)
                
        if args['apply']: 
               demfunctions.applymask(args['--input'],
                        args['--output'],
                        args['--mask'],
                        format=args['--format'],
                        verbose=verbose,
                        log=log)
               
        if args['toshp']: 
               demfunctions.masktoshp(args['--input'],
                        args['--output'],
                        dilatefactor = int(args['--dilate']),
                        fillholes = args['--fillholes'],
                        verbose=verbose,
                        log=log)
      
if __name__=='__main__':
    main()

        