#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZ-InSAR DEM application**

EZ-InSAR DEM application to replace values within the DEM raster

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
        The help can be launched by using the following command:: 

                $ ezinsar replace download --help

Changelog:
        * 3.3.0: Initial version, Sep. 2025

"""
from docopt import docopt

__docstringapp__ = """EZ-InSAR DEM application

Replace values within the DEM raster

usage: 
        ezinsarapp_dem replace [extract | apply] -f <str> -o <str> [options]

Arguments: 
        -f, --input <str>       Input file
        -o, --output <str>      Output file
        --value_int <float>     Input value
        --value_out <float>     Output value

Options: 
        --NOTnodata             Define the new value as a no-data value
        --format <str>          Output format. [default: GTiff]

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

        demfunctions.replace(args['--input'],
                args['--output'],
                args['--value_int'],
                args['--value_out'],
                nodata=(args['--NOTnodata']==False),
                format = args['--format'],
                verbose=verbose,
                log=log)
                
if __name__=='__main__':
    main()

        