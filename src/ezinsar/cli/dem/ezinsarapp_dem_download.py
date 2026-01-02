#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZ-InSAR DEM application**

EZ-InSAR DEM application to download the DEM tiles

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
        The help can be launched by using the following command:: 

                $ ezinsar dem download --help

Changelog:
        * 3.3.0: Initial version, Sep. 2025

"""

__docstringapp__ = """EZ-InSAR DEM application

Download the DEM tiles

usage: 
        ezinsarapp_dem download -b <str> -d <str> [options]

Arguments: 
        -b, --bbox <str>        Region of Interest in EZ-InSAR format
        -d, --dem <str>         Key code of the DEM

Options: 
        --directory <str>       Directory where the final file(s) will be stored [default: demtiles]
        --nameDEM <str>         Name of the DEM file [default: EZInSARDEM]
        --tiles <str>           Name of tiles which have to be downloaded, comma-separeted [default: None]

Account-Options: 
        -u, --username <str>    Username [default: None]
        -p, --password <str>    Password [default: None]

Other-Options: 
        --noSLCuse      Block the use of the SLC list
        --quiet         Block the verbose
        --nolog         Block the log 
        -h, --help

"""
from docopt import docopt
from ezinsar import constants

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
        
        ## Download
        if (not args['--tiles'] == None) and (not args['--tiles'] == 'None'): 
                args['--tiles'] = args['--tiles'].split(',')
        else: 
                args['--tiles'] = None

        demfunctions.downloadtiles(roipoly,
                args['--dem'],
                outdir = args['--directory'],
                username = constants.__username__,
                password = constants.__password__,
                nameDEM = args['--nameDEM'],
                tiles = args['--tiles'],
                verbose=verbose,
                log=log)

if __name__=='__main__':
    main()

        