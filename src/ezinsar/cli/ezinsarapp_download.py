#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Download SLCs 

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 

        $ ezinsar download --help

Changelog:
    * 3.3.1: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 3.2.1: The function becomes generic, Aug. 2025, Alexis Hrysiewicz
    * 3.0.0: Initial version, Jan. 2024

"""

__docstringapp__ = """EZ-InSAR application: Download SLCs

usage: ezinsar download -s <path_SLC> -b <bbox> [--ezinsarjob <job_file>] [-i <date_start>] [-j <date_end>] [-r <path>] [options]

Arguments:
    -s, --path_SLC <str>    Path of the .zip/.safe files
    -b, --bbox <W,S,E,N>    Bbox of the Region of Interest (W,S,E,N) in EPGS:4326

Job-options:
    --ezinsarjob <str>      EZ-InSAR job [default: None]

Optional-arguments:
    -i, --date_start <date in YYYY-MM-DDThh:mm:SS format>   First date [default: 2014-01-01T00:00:00]
    -j, --date_end <date in YYYY-MM-DDThh:mm:SS format>     Second date [default: 2025-01-01T00:00:00]
    -r, --path_RSLC <str>                                   Path of the processed images [defaut: '.']

Satellite-options:
    --satellite <str>               Satellite name [default: S1]
    -o, --relative_orbit <int>      Relative orbit, O value for automatic mode  [default: 0]
    -f, --flight_direction <str>    Orbit direction (a for ascending, or d for descending), None value for automatic mode [default: None]
    -m, --acquisition_mode <str>    Acquisition mode (IW or SM) [default: IW] 
    --polarisation <str>            Polarisation [default: VV,VH]

Server-options:
    -u, --username <str>    Username of the server 
    -p, --password <str>    Password of the server
    --server <str>          Server [default: Copernicus]
    --onlyburst             Download only the required S1 IW bursts (for ASF server)

Other-options:
    --savemap       Save a map of SLC extents
    --savekmz       Save a .kmz files
    --download      Download the images
    --cleanlist     Delete the SLC list
    --nolog         No logging
    -h, --help
    -q, --quiet     Suppress verbose

"""

from docopt import docopt
from datetime import datetime 
import os

import ezinsar.job as ez
from ezinsar.eicomponents.sensor.s1module import s1iwburstIDapp
from ezinsar import usermessage
from ezinsar import constants

def main():
    """Main function"""
    args = docopt(__docstringapp__)
    cur_dir = os.getcwd()
    
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

    if args['--ezinsarjob'] == 'None':
        jobezinsar = ez.EIjob(verbose=verbose,polarisation=args['--polarisation'].split(','),satmode=args['--acquisition_mode'],log=log,satellite=args['--satellite'])
        jobezinsar.workdirectory = '.'
        jobezinsar.pathSLC = args['--path_SLC']
        jobezinsar.pathorbit = '.'
        jobezinsar.pathaux = '.'
        jobezinsar.date1 = datetime.strptime(args['--date_start']+'.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')
        jobezinsar.date2 = datetime.strptime(args['--date_end']+'.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')
        jobezinsar.importroi(input=args['--bbox'])
        jobezinsar.mkdir()

    else: 
        usermessage.ezprint('Directories, dates and ROI parameters will be bypassed because the user has given an EZ-InSAR job.',log,verbose)
        jobezinsar = ez.load(args['--ezinsarjob'])

    if isinstance(jobezinsar.SLClist, type(None)):
        if args['--relative_orbit'] == '0': 
            if args['--satellite'] == 'S1': 
                jobezinsar.relorbit, jobezinsar.satpass, res = s1iwburstIDapp.S1burstIDmap().detectfromIDmap(jobezinsar,verbose=True).analyse(jobezinsar)
            else: 
                raise ValueError(usermessage.errormsg(__name__,main.__name__,__file__,constants.__copyright__,'The relative_orbit optional is required for other satellites than Sentinel-1.',log))
        else:
            jobezinsar.relorbit = int(args['--relative_orbit'])
            if args['--flight_direction'] == 'a': 
                jobezinsar.satpass = 'ASCENDING'
            elif args['--flight_direction'] == 'd':
                jobezinsar.satpass = 'DESCENDING'

    jobezinsar.initiateSLC(mode='online',server=args['--server'])
    jobezinsar.check()

    if not args['--cleanlist']:
        jobezinsar.saveSLClist(file='SLC.list')
    jobezinsar.checkSLClist()
    jobezinsar.printSLClist()

    if args['--savemap']:
        jobezinsar.displaySLClist(figure='SLCmap.jpg')

    if args['--savekmz']:
        jobezinsar.writeSLClisttokmz(file='SLClist.kmz')
   
    if args['--download']:
        if args['--username'] == None and args['--password'] == None:
            jobezinsar.downloadSLC(burstonly=onlyburst)
        if args['--username'] == None and not (args['--password'] == None):
            jobezinsar.downloadSLC(password=args['--password'],burstonly=onlyburst)
        if not (args['--username'] == None) and  args['--password'] == None:
            jobezinsar.downloadSLC(username=args['--username'],burstonly=onlyburst)
        if not (args['--username'] == None) and  not (args['--password'] == None):
            jobezinsar.downloadSLC(username=args['--username'],password=args['--password'],burstonly=onlyburst)

    os.chdir(cur_dir)
    if not args['--ezinsarjob'] == 'None':
        ez.save(jobezinsar,args['--ezinsarjob'])

if __name__=='__main__':
    main()