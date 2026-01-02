#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Decrypt an encrypted EZ-InSAR archive 

This application allows to decrypt an encrypted EZ-InSAR archive

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 

        $ ezinsar archive_decrypt --help

Changelog:
    * 3.3.1: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 3.0.0: Initial version, Dec. 2024

"""

__docstringapp__ =  """EZ-InSAR application: Decrypt an encrypted EZ-InSAR archive 

usage: ezinsar archive_decrypt -f <file> -k <key> [options]

Arguments:
    -f, --file <str>        EZ-InSAR encrypted archive
    -k, --key <str>         Path of the private key

Optional-arguments:
    --noclean               Block the cleaning 
    
Other-options:
    -h, --help
    -q, --quiet             Suppress verbose

"""

from docopt import docopt
import ezinsar.job as ez

def main():
    """Main function"""
    args = docopt(__docstringapp__)
   
    if args['--quiet']: 
        verbose = False
    else:
        verbose = True
    if args['--noclean']: 
        clean = False
    else:
        clean = True
        
    # Decrypt the encrypted archive
    ez.decrypt_archive(args['--file'], 
        args['--key'], 
        clean = clean,  
        verbose = verbose)

if __name__=='__main__':
    main()