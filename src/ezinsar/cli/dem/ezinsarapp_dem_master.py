#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZ-InSAR DEM application**

EZ-InSAR wrapper to running the DEM command-line interface.

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
        Please see the different command to have a full description:: 

                $ ezinsar dem --help

Changelog:
        * 3.3.0: Initial version, Sep. 2025

"""

__docstringapp__ = """EZ-InSAR DEM application

This interface includes all programs to manipulate DEMs. 

usage:  
        ezinsar dem <command> [<args>...] [options]
        ezinsar dem -h | --help

The commands are:
        list                    List the DEMs available with EZ-InSAR
        checkext                Check if the DEM covers the Region of Interest
        tiles                   List the tiles
        download                Download the tiles
        merge                   Merge the tiles
        mask                    Extract or apply a mask to the raster 
        replace                 Replace values within the DEM 
        ellcorr                 Apply the ellipsoid correction
        translate               Translate the DEM in the correct format  
        run                     Download and prepare the DEM regarding the InSAR purposes

Options: 
        --nolog         No logging
        -h, --help
        -q, --quiet     Suppress verbose

See 'ezinsar dem2 <command> --help' for more information on a specific command.
"""

from subprocess import call
from docopt import docopt
from ezinsar import constants

__copyright__ = constants.__copyright__

def main():
        """Main function"""
        args = docopt(__docstringapp__,options_first=True)
        argv = [args['<command>']] + args['<args>']
        
        #################################
        ## Run the Desktop application by default 
        if args['<command>'] in ['list','checkext','tiles','download','merge','mask','replace','ellcorr','translate','run']:
                exit(call(['ezinsarapp_dem_%s' % (args['<command>'])] + argv))
                
        # For the help 
        elif args['<command>'] in ['-h','help', None]:
                exit(call(['ezinsarapp_dem_master', '--help']))

        # For nothing
        else:
                exit("%r is not a EZ-InSAR dem command. See 'ezinsar dem --help'." % args['<command>'])