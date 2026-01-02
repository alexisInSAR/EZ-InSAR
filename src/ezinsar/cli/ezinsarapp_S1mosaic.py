#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Download Sentinel-1 IW mosaics

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 
        
        $ ezinsar S1mosaic --help

Changelog:
    * 3.3.1: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 3.0.0: Initial version, Dec. 2024

"""
from docopt import docopt
from datetime import datetime 
import random
import string 
import os 

__docstringapp__ =  """EZ-InSAR application: Download Sentinel-1 IW mosaics

usage: 
    ezinsar S1mosaic -b <bbox> [options]

Arguments:
    -b, --bbox <W,S,E,N>            Region of Interests respecting the EZ-InSAR format. Can be an EZ-InSAR job file
    
Options:
    --output_file <str>             Directory of the results [default: auto]
    --year <int>                    Year [default: %s]
    --month <str>                   Month [default: latest]
    --saveobservation <bool>        Save the observation GTiff [default: False]
    --epsg <int>                    Wrap the image(s) [default: None]
    --temporary_dir <str>           Temporary direction [default: %s]
    --resolution <float>            Resolution [default: None]

Account-Options: 
    -u, --username <str>            Username [default: None]
    -p, --password <str>            Password [default: None]

Other-options:
    --printonly                     Print the list without processing
    --no_clean                      Block the cleaning
    --modefull                      Full downloading
    --nolog                         No logging
    -h, --help
    -q, --quiet                     Suppress verbose

""" % (datetime.now().year,
    '.'+os.sep+'tmp_'+''.join(random.choice(string.ascii_lowercase) for i in range(5)))

import ezinsar.job as ez
from ezinsar.eicomponents.sensor.s1module import s1grdtools
import numpy as np

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
        log = 'ezinsar.log'

    if args['--bbox'].endswith('.ei'): 
        roipoly = ez.load(args['--bbox'],verbose=False).roi
    else: 
        roipoly = ez.EIjob(verbose=False).importroi(input=args['--bbox']).roi

    if not args['--modefull']: 
        yearlist = [int(args['--year'])]
        monthlist = [args['--month']]

    else: 
        yearlist = []
        monthlist = []

        for idx in np.arange(2014,datetime.now().year+1):
            for idx2 in np.arange(1,13):
                yearlist.append(int(idx))
                monthlist.append('M%02.0f' % (idx2))

    for yi, mi in zip(yearlist,monthlist):
        try:
            s1grdtools.runS1IWbasemap(roipoly,
                    args['--output_file'],
                    year = yi,
                    month = mi, 
                    epsg = args['--epsg'],
                    resolution = args['--resolution'],
                    temp_dir = args['--temporary_dir'],
                    username = args['--username'],
                    password = args['--password'],
                    cleaning=(args['--no_clean']==False),
                    printonly = args['--printonly'],
                    verbose = verbose,
                    log = log, 
                    )
        except: 
            a = 'dummy'
    


if __name__=='__main__':
    main()