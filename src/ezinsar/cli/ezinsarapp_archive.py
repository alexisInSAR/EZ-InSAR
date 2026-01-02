#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Create an EZ-InSAR archive

This application allows to create an EZ-InSAR archive for long-term storage

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 

        $ ezinsar archive --help

Changelog:
    * 3.3.1: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 3.0.0: Initial version, Dec. 2024

"""

__docstringapp__ =  """EZ-InSAR application: Create an EZ-InSAR archive

usage: ezinsar archive -f <file> [options]

Arguments:
    -f, --file <str>    EZ-InSAR job file 

Optional-arguments:
    --description <str>     Description of the project [default: None]
    --project <str>         Project description [default: None]
    --imageill <str>        Path of an image of illustration [default: None]
    --suppfile <str>        Path of supplementary files [default: ]
    --blockreport           Block the creation of the report
    --logo <str>            Path of the logo [default: None]
    --unmasksensible        Block the masking of sensible information
    --compression <str>     Compression algorithm for the .tar file [default: gz]
    --encryption            Encrypte the archive
    --key <str>             Path of the user public key [default: None]
    --bypassuser            Bypass the user confirmation
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

    # Input parameters
    for keyi in list(args.keys()):
        if args[keyi] == 'None': 
            args[keyi] = None
    
    if args['--quiet']: 
        verbose = False
    else:
        verbose = True

    if args['--blockreport']: 
        report = False
    else:
        report = True

    if args['--unmasksensible']: 
        masksensible = False
    else:
        masksensible = True

    if args['--noclean']: 
        clean = False
    else:
        clean = True

    listfile = args['--suppfile'].split(',')
    if listfile[0]=='':
        listfile = []

    # Read the job file
    job = ez.load(args['--file'])

    # Create the archive
    ez.archive(job, 
        description=args['--description'],       
        project=args['--project'],  
        imageill=args['--imageill'],  
        report=report,
        suppfile=listfile,
        logo=args['--logo'],  
        masksensible=masksensible,
        compression=args['--compression'],
        encryption=args['--encryption'],
        key=args['--key'],
        bypassuser=args['--bypassuser'],
        clean=clean,
        verbose = verbose)

if __name__=='__main__':
    main()