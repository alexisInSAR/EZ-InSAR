#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZ-InSAR DEM application**

EZ-InSAR DEM application to list the DEMs available with EZ-InSAR

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
        The help can be launched by using the following command:: 

                $ ezinsar dem list --help

Changelog:
        * 3.3.0: Initial version, Sep. 2025

"""

__docstringapp__ = """EZ-InSAR DEM application

List the DEMs available with EZ-InSAR 

usage: 
        ezinsarapp_dem list [options]

Options: 
        --nofull        No full
        -h, --help

"""

from docopt import docopt
from ezinsar.eicomponents.demmodule import demfunctions

def main():
        """Main function"""
        args = docopt(__docstringapp__)
        demfunctions.printinfo(full=(args['--nofull']==False))

if __name__=='__main__':
    main()

        