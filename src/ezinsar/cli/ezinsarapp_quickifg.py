#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Compute a single interferogram from two SLC files

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 

        $ ezinsar quickifg --help

Changelog:
    * 3.3.1: Several changes, Dec. 2025, Alexis Hrysiewicz
        * Change the import line
        * Delete the link to the EZ-InSAR GAMMA module
    * 3.2.0: No cleaning by default, Alexis Hrysiewicz, Aug. 2025
    * 3.0.0: Initial version, Dec. 2024

"""

__docstringapp__ = """EZ-InSAR application: Compute a single interferogram from two SLC files

usage: ezinsar quickifg -m <path-of-the-reference-image> -s <path-of-the-secondary-image> [options]

Arguments:
    -m, --master <str>      Path of the reference image 
    -s, --slave <str>       Path of the secondary image 

ROI-options:
    -b, --bbox <W,S,E,N>    Bbox of the Region of Interest (W,S,E,N) in EPGS:4326. Default: all image coverage

Path-options: 
    -w, --path_wk <str>     Path of the work directory [default: ./WKprocessing]
    -o, --path_orbit <str>  Path of the orbit directory [default: ./WKprocessing/Orbits]
    
Satellite-options:
    --polarisation <str>    Polarisation [default: VV]

Processing-options:
    --processor <str>       InSAR processor [default: isce2]
    --useorbitfile          Use the orbit file
    --mlran <int>           Range multilooking factor. If None, automatic
    --mlazi <int>           Azimuth multilooking factor. If None, automatic
    --filter                Filtre the interferograms
    --unwrap                Unwrap the interferograms
    --dem <str>             DEM [default: dem_EZInSAR]
    --typeDEM <str>         Type of the DEM [default: Copernicus-ell]
    --nomaskifg             Block the masking of interferograms

Other-options:
    --nolog                 No logging
    --clean                 Clean the directories
    -h, --help
    -q, --quiet             Suppress verbose

"""

from docopt import docopt
import os
import numpy as np
import shutil
import glob
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon

import ezinsar.job as ez
from ezinsar.eicomponents.sensor.s1module import s1slctools

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

    jobezinsar = ez.EIjob(verbose=verbose,polarisation=args['--polarisation'].split(','),satmode='IW',log=log)

    # Create the directories
    jobezinsar.workdirectory = os.path.abspath(args['--path_wk'])
    if not os.path.isdir(jobezinsar.workdirectory):
        os.mkdir(jobezinsar.workdirectory)

    jobezinsar.pathSLC = jobezinsar.workdirectory+os.sep+'Data_slc'
    if os.path.isdir(jobezinsar.pathSLC):
        shutil.rmtree(jobezinsar.pathSLC)
    os.mkdir(jobezinsar.pathSLC)
    jobezinsar.pathorbit = os.path.abspath(args['--path_orbit'])
    jobezinsar.pathaux = jobezinsar.workdirectory+os.sep+'Data_aux'
    jobezinsar.pathDEM = jobezinsar.workdirectory+os.sep+'DEM'
    jobezinsar.nameDEM = 'dem_EZInSAR'
    jobezinsar.typeDEM = args['--typeDEM']

    # Detect the files
    masterfile = glob.glob(args['--master'])
    slavefile = glob.glob(args['--slave'])

    # Detection of the mode
    if 'S1' in masterfile[0].split(os.sep)[-1]:
        S1annoresultsi = s1slctools.detectS1annoatationfromxml(masterfile[0],jobezinsar.polarisation[0])
        if not 'IW' in S1annoresultsi['data_xmli1']['mode']: 
            jobezinsar.satmode = 'SM'
        else: 
            jobezinsar.satmode = 'IW'

    # Update the ROI
    modecropping = True
    if not args['--bbox'] == None: 
        jobezinsar.importroi(input=args['--bbox'])
    else: 
        lat = []
        lon = []
        if 'S1' in masterfile[0].split(os.sep)[-1]: 
            for filei in masterfile: 
                S1annoresultsi = s1slctools.detectS1annoatationfromxml(filei,jobezinsar.polarisation[0])
                try: 
                    lat = lat + S1annoresultsi['data_xmli1']['latitude'] + S1annoresultsi['data_xmli2']['latitude'] + S1annoresultsi['data_xmli3']['latitude'] 
                    lon = lon + S1annoresultsi['data_xmli1']['longitude'] + S1annoresultsi['data_xmli2']['longitude'] + S1annoresultsi['data_xmli3']['longitude'] 
                except: 
                    lat = lat + S1annoresultsi['data_xmli1']['latitude']
                    lon = lon + S1annoresultsi['data_xmli1']['longitude']
            pts = np.array([np.array(lon), np.array(lat)]).T
            hull = ConvexHull(pts)
            jobezinsar.roi = Polygon(list(zip(pts[hull.vertices,0], pts[hull.vertices,1])))
        
        modecropping = False 
            
    # Create dummy variables
    jobezinsar.relorbit = 1
    jobezinsar.satpass = 'ASCENDING'
    jobezinsar.check(verbose=False)

    # Create the directories 
    jobezinsar.mkdir()
    
    # Link the SLC file into the good directory and initialise the SLC list
    for filei in masterfile:
        os.symlink(os.path.abspath(filei),jobezinsar.pathSLC+os.sep+filei.split(os.sep)[-1])
    for filei in slavefile:
        os.symlink(os.path.abspath(filei),jobezinsar.pathSLC+os.sep+filei.split(os.sep)[-1])

    jobezinsar.initiateSLC(mode='onfile')

    # Detect the reference date
    listdate = []
    for datei in jobezinsar.SLClist['Date1']:
        listdate.append(datei.split('T')[0])
    refdate = listdate[-1].replace('-','')

    # Download the DEM
    jobezinsar.downloaddem(processor=args['--processor'])
    
    # Initialisation of the jobs
    jobezinsar.initiatecoreg(processor=args['--processor'])
    jobezinsar.coregistration.check()

    ## Commun processing 
    jobezinsar.coregistration.refdate = refdate
    if  jobezinsar.satmode == 'IW':
        jobezinsar.coregistration.modecropping = None
    else: 
        jobezinsar.coregistration.modecropping = 'auto'
        jobezinsar.coregistration.extractimage['cropping']['value'] = True
    if not args['--mlran'] == None: 
        jobezinsar.coregistration.mlran = int(args['--mlran'])
    if not args['--mlazi'] == None: 
        jobezinsar.coregistration.mlazi = int(args['--mlazi'])
    if not args['--processor'] == 'snap':
        jobezinsar.coregistration.run(step=['checkSLC','checkOrbit'])
    else: 
        jobezinsar.coregistration.run(step=['checkSLC'])
    jobezinsar.coregistration.coarserefdate['done']['value'] = True

    ## Coregistration
    if args['--processor'] == 'isce2':
        if jobezinsar.satmode == 'IW':
            jobezinsar.coregistration.run(step=['unpack_topo_reference','unpack_secondary_slc','average_baseline','extract_burst_overlaps','overlap_geo2rdr','overlap_resample','pairs_misreg','timeseries_misreg','fullBurst_geo2rdr','fullBurst_resample','extract_stack_valid_region','merge_reference_secondary_slc','grid_baseline'])
        else: 
            jobezinsar.coregistration.run(step=['unpack_slc','crop_slc','reference','focus_split','geo2rdr_coarseResamp','refineSecondaryTiming','invertMisreg','fineResamp','grid_baseline'])
    elif args['--processor'] == 'doris':
        jobezinsar.coregistration.refinerefdate['done']['value'] = True
        jobezinsar.coregistration.run(step=['extractimage','mastertiming','oversample','coarseoffset','finecoreg','reltiming','demassist','coregpm','resample','finalstack','cleanstack'])
    elif args['--processor'] == 'snap':
        jobezinsar.coregistration.refinerefdate['done']['value'] = True
        jobezinsar.coregistration.run(step=['importSLC','coreg','cleanstack'])
    elif args['--processor'] == 'gamma': 
        jobezinsar = ez.parseparamter(jobezinsar,args,'coregistration')

    ## Interferogram generation 
    jobezinsar.initiateifg(processor=args['--processor'])
    jobezinsar.ifgstack.refdate = refdate
    if not args['--mlran'] == None: 
        jobezinsar.ifgstack.mlran = int(args['--mlran'])
    if not args['--mlazi'] == None: 
        jobezinsar.ifgstack.mlazi = int(args['--mlazi'])

    if args['--processor'] == 'isce2': 
        jobezinsar.ifgstack.filter_coherence['process']['value'] = args['--filter']
        jobezinsar.ifgstack.unwrap['process']['value'] = args['--unwrap']
        jobezinsar.ifgstack.finalstack['keepgeotiff']['value'] = (args['--clean']==True)
    elif args['--processor'] == 'doris':
        jobezinsar.ifgstack.refinerefdate['process']['value'] = False 
        jobezinsar.ifgstack.ifgfilter['process']['value'] = args['--filter']
        jobezinsar.ifgstack.ifgunwrapping['process']['value'] = args['--unwrap']
        jobezinsar.ifgstack.ifggeocoding['maskifg']['value'] = (args['--nomaskifg']==False)
        jobezinsar.ifgstack.finalstack['keepgeotiff']['value'] = (args['--clean']==True)
    elif args['--processor'] == 'snap':
        jobezinsar.ifgstack.ifgfilter['process']['value'] = args['--filter']
        jobezinsar.ifgstack.ifgunwrapping['process']['value'] = args['--unwrap']
        jobezinsar.ifgstack.ifggeocoding['maskifg']['value'] = (args['--nomaskifg']==False)
        jobezinsar.ifgstack.finalstack['keepgeotiff']['value'] = (args['--clean']==True)
    elif args['--processor'] == 'gamma': 
        jobezinsar = ez.parseparamter(jobezinsar,args,'ifgstack')
    
    jobezinsar.ifgstack.run(step=['all'])

    # Cleaning
    if args['--clean'] == True:
        listpath = [jobezinsar.pathSLC,
            jobezinsar.pathorbit, 
            jobezinsar.pathDEM, 
            jobezinsar.pathaux, 
            jobezinsar.coregistration.workdirectory, 
            jobezinsar.coregistration.pathstack]
        for pathi in listpath: 
            if os.path.isdir(pathi):
                shutil.rmtree(pathi)

if __name__=='__main__':
    main()