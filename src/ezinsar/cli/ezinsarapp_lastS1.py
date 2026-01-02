#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Compute the latest Sentinel-1 interferogram for a given ROI

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 

        $ ezinsar lastS1 --help

Changelog:
    * 3.3.1: Several changes, Dec. 2025, Alexis Hrysiewicz
        * Change the import line
        * Delete the link to the EZ-InSAR GAMMA module
    * 3.2.0: No cleaning by default, Alexis Hrysiewicz, Aug. 2025
    * 3.0.0: Initial version, Dec. 2024

"""

__docstringapp__ = """EZ-InSAR application: Compute the latest Sentinel-1 IW interferogram for a given ROI

usage: ezinsar lastS1 -w <path_wk> -b <bbox> [options]

Arguments:
    -w, --path_wk <str>             Path of the work directory
    -b, --bbox <W,S,E,N>            Bbox of the Region of Interest (W,S,E,N) in EPGS:4326, or shapefile path, or volcano name

Satellite-options:
    -o, --relative_orbit <int>      Relative orbit, O value for automatic mode  [default: None]
    -f, --flight_direction <str>    Orbit direction (a for ascending, or d for descending), None value for automatic mode [default: None]
    --polarisation <str>            Polarisation [default: VV]
    --daykernel <int>               Number of days for SLC query [default: 30]
    --satmode <str>                 Acquisition mode of Sentinel-1 [default: IW]
    --dateslave <str>               End date for the search in 2014-01-01T00:00:00 format (default today)

Server-options:
    -u, --username <str>    Username of the Sentinel-1 server 
    -p, --password <str>    Password of the Sentinel-1 server
    --server <str>          Server (ASF or Copernicus) [default: Copernicus]
    --onlyburst             Download only the required S1 IW bursts 
    
Processor-options:
    --processor <str>       InSAR processor [default: isce2]
    --mlran <int>           Range multilooking factor (if None, automatic)
    --mlazi <int>           Azimuth multilooking factor (if None, automatic)
    --filter                Filtre the interferograms
    --unwrap                Unwrap the interferograms
    --dem <str>             DEM [default: Copernicus-ell]
    --nomaskifg             Block the masking of interferograms

Other-options:
    --savemapburst          Save a map of S1 IW bursts
    --noselect              Bypass the selection of S1 bursts by the user
    --nolog                 No logging
    --clean                 Clean the directories
    -h, --help
    -q, --quiet             Suppress verbose

"""

from docopt import docopt
from datetime import datetime, timedelta
import os
import numpy as np
import shutil

import ezinsar.job as ez
from ezinsar.eicomponents.sensor.s1module import s1iwburstIDapp
from ezinsar import usermessage
from ezinsar import constants

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

    if args['--onlyburst']: 
        onlyburst = True
    else:
        onlyburst = False

    jobezinsar = ez.EIjob(verbose=verbose,polarisation=args['--polarisation'].split(','),satmode=args['--satmode'],log=log)

    jobezinsar.workdirectory = os.path.abspath(args['--path_wk'])

    if not os.path.isdir(jobezinsar.workdirectory):
        os.mkdir(jobezinsar.workdirectory)

    jobezinsar.pathSLC = jobezinsar.workdirectory+os.sep+'Data_slc'
    jobezinsar.pathorbit = jobezinsar.workdirectory+os.sep+'Data_orbit'
    jobezinsar.pathaux = jobezinsar.workdirectory+os.sep+'Data_aux'

    jobezinsar.pathDEM = jobezinsar.workdirectory+os.sep+'DEM'
    jobezinsar.nameDEM = 'dem_EZInSAR'
    jobezinsar.typeDEM = args['--dem']

    if args['--dateslave'] == None:
        jobezinsar.date2 = datetime.today()
    else: 
        jobezinsar.date2 = datetime.strptime(args['--dateslave']+'.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')
    jobezinsar.date1 = jobezinsar.date2 - timedelta(days=int(args['--daykernel']))
    
    jobezinsar.importroi(input=args['--bbox'])

    if args['--satmode'] == 'SM' and (args['--relative_orbit'] == 'None' or args['--flight_direction'] == 'None'):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,constants.__copyright__,
            'The relative orbit and satellite pass are required for SM mode.',None))

    if not args['--relative_orbit'] == 'None': 
        jobezinsar.relorbit = int(args['--relative_orbit'])
    else:
        jobezinsar.relorbit = None

    if args['--flight_direction'] == 'a': 
        jobezinsar.satpass = 'ASCENDING'
    elif args['--flight_direction'] == 'd':
        jobezinsar.satpass = 'DESCENDING'
    else:
        jobezinsar.satpass = None
    
    if jobezinsar.satpass == None or jobezinsar.relorbit == None:

        jobdetect = s1iwburstIDapp.S1burstIDmap().checkfile().downloadfile().detectfromIDmap(jobezinsar)
        if args['--savemapburst'] == True:
            jobdetect.display(jobezinsar,figure=jobezinsar.workdirectory+os.sep+'figure_S1ID.jpg')

        a, b , res = jobdetect.analyse(jobezinsar)

        date1 = []
        date2 = []
        hourapprox = []

        if args['--noselect'] == True:
            jobezinsar.satpass = b 
            jobezinsar.relorbit = a
        else:
            for idx, namei in enumerate(res['name']):
                jobezinsar.satpass = namei.split('_')[0]
                jobezinsar.relorbit = int(namei.split('_')[1])

                try: # requires if no acquisitions have been done. 
                    jobezinsar.initiateSLC(mode='online',server=args['--server'])

                    listdate = []
                    hourdate = []
                    for datei in jobezinsar.SLClist['Date1']:
                        listdate.append(datei.split('T')[0])
                        hourdate.append(datei.split('T')[1])
                    
                    listdate = np.unique(listdate)
                    date1.append(listdate[-2])
                    date2.append(listdate[-1])
                    hourapprox.append(hourdate[0])
                
                except:
                    date1.append(None)
                    date2.append(None)
                    hourapprox.append(None)

            usermessage.ezprint('------------------------------------------------------------------',None,True)
            usermessage.ezprint('------------------------------------------------------------------',None,True)
            usermessage.ezprint('The potential interferogram can be computed using the following satellite parameters:',log,verbose)
            usermessage.ezprint('------------------------------------------------------------------',None,True)
            for idx, namei in enumerate(res['name']):
                usermessage.ezprint('\t%s with a overlap of %d with the ROI' % (namei,res['overlap'][idx]),log,verbose)
                usermessage.ezprint('\t\tBetween %s and %s (approx. %s)' % (date1[idx],date2[idx],hourapprox[idx]),log,verbose)

            usermessage.ezprint('------------------------------------------------------------------',None,True)
            usermessage.ezprint('Please select an option:',log,verbose)
            for idx, namei in enumerate(res['name']):
                usermessage.ezprint('\t%d for %s' % (idx,namei),log,verbose)
            
            rep = None
            while not rep in np.arange(0,len(res['name'])):
                rep = input('What is your selection?\n')   
                try:
                    rep = int(rep)
                except:
                    rep = None

            jobezinsar.satpass = res['name'][rep].split('_')[0]
            jobezinsar.relorbit = int(res['name'][rep].split('_')[1])
        
    jobezinsar.initiateSLC(mode='online',server=args['--server'])

    listdate = []
    for datei in jobezinsar.SLClist['Date1']:
        listdate.append(datei.split('T')[0])
        
    listdate = np.unique(listdate)
    refdate = listdate[-2].replace('-','')
    idxslc = [len(listdate)-2,len(listdate)-1]

    # Download the data
    jobezinsar.mkdir()
    if args['--username'] == None and args['--password'] == None:
        jobezinsar.downloadSLC(index=idxslc,burstonly=onlyburst)
        jobezinsar.downloadorbit()
    if args['--username'] == None and not (args['--password'] == None):
        jobezinsar.downloadSLC(index=idxslc,password=args['--password'],burstonly=onlyburst)
        jobezinsar.downloadorbit(server=args['--server'],password=args['--password'])
    if not (args['--username'] == None) and  args['--password'] == None:
        jobezinsar.downloadSLC(index=idxslc,username=args['--username'],burstonly=onlyburst)
        jobezinsar.downloadorbit(server=args['--server'],username=args['--username'])
    if not (args['--username'] == None) and  not (args['--password'] == None):
        jobezinsar.downloadSLC(index=idxslc,username=args['--username'],password=args['--password'],burstonly=onlyburst)
        jobezinsar.downloadorbit(server=args['--server'],username=args['--username'],password=args['--password'])

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
    # jobezinsar.ifgstack.merge_burst_igram['done']['value'] = True
    # jobezinsar.ifgstack.run(step=['ifggeocoding'])

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