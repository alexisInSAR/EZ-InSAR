#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Compute a super-single network to find the best potential reference date

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 
        
        $ ezinsar bestref -s <path_SLC> -b <bbox> [options]

Changelog:
    * 3.3.1: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 3.0.0: Initial version, Dec. 2024

"""

__docstringapp__ =  """EZInSAR application: Compute a super-single network to find the best potential reference date

usage: ezinsar bestref -s <path_SLC> -b <bbox> [options]

Arguments:
    -s, --path_SLC <str>                    Path of the SLC files
    -b, --bbox <W,S,E,N>                    Bbox of the Region of Interest (W,S,E,N) in EPGS:4326

Optional-arguments:
    -r, --satellite <str>                   Satellite [default: S1] 
    -p, --polarisation <str>                Polarisation [default: VV] 
    -o, --path_orbit <str>                  Path of the orbit directiry   [default: None]
    -d, --dem <str,int,float>               DEM information (file or number) [default: 500]
    -f, --figure <str>                      Path of the figure [default: coarse_ifg_network.jpg]
    -a, --preref <str>                      Preselected reference date (YYYYMMDD format) [defaut: None]

Other-options:
    --displayfigure     Save a map of SLC extents
    --nolog             No logging
    -h, --help
    -q, --quiet         Suppress verbose

"""

from docopt import docopt
from shapely.geometry import Polygon
from PIL import Image

import ezinsar.job as ez
from ezinsar.eicomponents.sensor.s1module import s1stacktools
from ezinsar.eicomponents.sensor.tsxmodule import tsxstacktools

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

    bboxstr = args['--bbox'].split(',')

    bbox = Polygon(
            [
                [float(bboxstr[0]),float(bboxstr[1])],
                [float(bboxstr[2]),float(bboxstr[1])],
                [float(bboxstr[2]),float(bboxstr[3])],
                [float(bboxstr[0]),float(bboxstr[3])],
            ]
        )
    
    if args['--path_orbit'] == 'None':
        args['--path_orbit'] = None
    if args['--figure'] == 'None':
        args['--figure'] = None
    if args['--preref'] == 'None':
        args['--preref'] = None

    try: 
        args['--dem'] = float(args['--dem'])
    except: 
        dummy = []

    # Compute the network and find the best potential reference date (barycentre method)
    if args['--satellite'] == 'S1':
        s1stacktools.commputecoarsenetwork(args['--path_SLC'],bbox,args['--polarisation'].upper(),
            pathorbit = args['--path_orbit'],
            DEM = args['--dem'],
            figure = args['--figure'],
            preref = args['--preref'],
            verbose = verbose, 
            log = log, 
            )
    elif args['--satellite'] == 'PAZ' or args['--satellite'] == 'TSX':
        tsxstacktools.commputecoarsenetworkSM(args['--path_SLC'],bbox,args['--polarisation'].upper(),
            pathorbit = args['--path_orbit'],
            DEM = args['--dem'],
            figure = args['--figure'],
            preref = args['--preref'],
            verbose = verbose, 
            log = log, 
            )
        
    if args['--displayfigure'] == True and args['--figure'] != None: 
        image = Image.open(args['--figure'])
        image.show()

if __name__=='__main__':
    main()