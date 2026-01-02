#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZ-InSAR DEM application**

EZ-InSAR DEM application to download and prepare a DEM for InSAR computations

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
        The help can be launched by using the following command:: 

                $ ezinsar dem run --help

Changelog:
        * 3.3.0: Initial version, Sep. 2025

"""
from docopt import docopt
import os

__docstringapp__ =  """EZ-InSAR application: Download and prepare a DEM for InSAR computations

usage: ezinsarapp_dem run  -s <path_SLC> -b <bbox> [options]

Arguments:
    -s, --pathDEM <str>     Path of the DEM or EZ-InSAR job file (with .ei extension)
    -b, --bbox <W,S,E,N>    Bbox of the Region of Interest (W,S,E,N) in EPGS:4326

Optional-arguments:
    --nameDEM <str>         Name of the DEM                     [default: DEM_InSAR]
    --typeDEM <str>         Type of the DEM                     [default: Copernicus]
    --ell <str>             File of the ell. correction         [defaut: None]
    --processor <str>       InSAR processor                     [defaut: None]
    --username <str>        Username for DEMs with registration [defaut: None]
    --password <str>        Password for DEMs with registration [defaut: None]
    
Other-options:
    --no_4326               Block the used of 4326 CRS 
    --no_ellcorrection      Block the ell. correction
    --no_clip               Block the clippling of the DEM   
    --figure                Save a figure of the DEM (hillshade)
    --docker                Run the processing in a Docker container
    --noSLCuse              Block the use of the SLC list
    --nolog                 No logging
    --noclean               Block the cleaning of files
    -h, --help
    -q, --quiet             Suppress verbose

"""

from docopt import docopt

import ezinsar.job as ez
from ezinsar.eicomponents.demmodule import demwrapper, demtools

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

    if args['--no_ellcorrection']: 
        ellcorrection = False
    else:
        ellcorrection = True

    if args['--no_4326']: 
        codeCRS = 'None'
    else:
        codeCRS = '4326'

    if args['--no_clip']: 
        clip = False
    else:
        clip = True

    # If an EZ-InSAR is given
    if '.ei' in args['--pathDEM']:
        job = ez.load(args['--pathDEM'],verbose=verbose).check(mode='high',verbose=verbose)        
        job.downloaddem(nameDEM = args['--nameDEM'], 
            typeDEM = args['--typeDEM'], 
            ell = args['--ell'], 
            ellcorrection = ellcorrection,
            processor = args['--processor'],
            clip = clip,
            useSLClist = (args['--noSLCuse']==False),
            nodata = 0, 
            waterbody_mask = True, 
            username = args['--username'],
            password = args['--password'],
            EPSG = codeCRS,
            docker=args['--docker'],
            cleaning = (args['--noclean']==False), 
            verbose = verbose,
            log = log)
        ez.save(job,args['--pathDEM'])

        if args['--figure']: 
            job.displaydem(figure = 'hillshade_DEM.jpg', 
                verbose = verbose,
                log = log)

    # If an EZ-InSAR job is not given 
    else: 
        roipoly = ez.EIjob(verbose=False).importroi(input=args['--bbox']).roi

        job, pathDEM, typeDEM, output_dem = demwrapper.run(pathDEM=args['--pathDEM'], 
            nameDEM = args['--nameDEM'], 
            typeDEM = args['--typeDEM'], 
            bbox = roipoly,
            ell = args['--ell'], 
            ellcorrection = ellcorrection,
            processor = args['--processor'],
            clip = clip,
            nodata = 0, 
            waterbody_mask = True, 
            username = args['--username'],
            password = args['--password'],
            EPSG = codeCRS,
            docker=args['--docker'],
            cleaning = (args['--noclean']==False), 
            verbose = verbose,
            log = log)
    
        if args['--figure']: 
            demtools.display(pathDEM = pathDEM+os.sep+output_dem,
                figure = 'hillshade_DEM.jpg', 
                verbose = verbose,
                log = log)

if __name__=='__main__':
    main()

    
  