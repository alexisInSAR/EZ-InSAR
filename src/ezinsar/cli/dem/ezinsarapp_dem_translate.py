#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZ-InSAR DEM application**

EZ-InSAR DEM application to translate the DEM

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
        The help can be launched by using the following command:: 

                $ ezinsar dem translate --help

Changelog:
        * 3.3.0: Initial version, Sep. 2025

"""
from docopt import docopt
from ezinsar import constants

__docstringapp__ = """EZ-InSAR DEM application

Translate the DEM

usage: 
        ezinsarapp_dem translate -f <str> -o <str> [options]

Arguments: 
        -f, --input <str>       Input file
        -o, --output <str>      Output file

Account-Options: 
        --roi <str>             Region of Interest for cropping. Can be an EZ-InSAR job
        --nodata <bool>         If True, the nodata values will be masked [default: True]
        --format <str>          Output format. [default: GTiff]
        --byteswap <bool>       Byte Swap. [default: False]
        --areaorpoint <str>     Area or Point [default: Point]
        --xmlISCE               Create the auxiliary for ISCE        

Other-Options:
        --noSLCuse      Block the use of the SLC list
        --quiet         Block the verbose
        --nolog         Block the log 
        -h, --help

"""

from ezinsar.eicomponents.demmodule import demfunctions
from ezinsar import ezinsarprocessor as ez 
from ezinsar.eicomponents.slcmodule import slctools

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

        if not args['--roi'] in ['None',None]:
                if args['--roi'].endswith('.ei'): 
                        if args['--noSLCuse']:
                                roipoly = ez.load(args['--bbox'],verbose=False).roi
                        else: 
                                roipoly = slctools.getextentfromSLC(ez.load(args['--bbox'],verbose=False),verbose=verbose,log=log)
                else: 
                        roipoly = ez.EIjob(verbose=False).importroi(input=args['--bbox']).roi
        else: 
                roipoly = None

        demfunctions.translate(args['--input'],
                args['--output'],
                roi = roipoly,
                format = args['--format'],
                nodata = args['--nodata'],
                byteswap = args['--byteswap'],
                areaorpoint=args['--areaorpoint'],
                xmlISCE = args['--xmlISCE'],
                verbose=verbose,
                log=log)

if __name__=='__main__':
    main()

        