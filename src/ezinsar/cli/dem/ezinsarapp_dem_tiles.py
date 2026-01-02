#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZ-InSAR DEM application**

EZ-InSAR DEM application to list the tiles available for the DEM

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
        The help can be launched by using the following command:: 

                $ ezinsar dem tiles --help

Changelog:
        * 3.3.0: Initial version, Sep. 2025

"""

__docstringapp__ = """EZ-InSAR DEM application

List the tiles available for the DEM

usage: 
        ezinsarapp_dem tiles -b <str> -d <str> [options]

Arguments: 
        -b, --bbox <str>        Region of Interest in EZ-InSAR format
        -d, --dem <str>         Key code of the DEM

Options: 
        --noSLCuse      Block the use of the SLC list
        --quiet         Block the verbose
        --nolog         Block the log 
        -h, --help

"""

from docopt import docopt
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

        if args['--bbox'].endswith('.ei'): 
                if args['--noSLCuse']:
                        roipoly = ez.load(args['--bbox'],verbose=False).roi
                else: 
                        roipoly = slctools.getextentfromSLC(ez.load(args['--bbox'],verbose=False),verbose=verbose,log=log)
        else: 
                roipoly = ez.EIjob(verbose=False).importroi(input=args['--bbox']).roi
        
        demfunctions.listtiles(roipoly,
                        args['--dem'],
                        verbose=verbose,
                        log=log)

if __name__=='__main__':
    main()

        