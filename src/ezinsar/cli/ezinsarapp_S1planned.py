#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Find the next acquisitions of Sentinel-1

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 

        $ ezinsar S1planned --help

Changelog:
    * 3.3.1: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 3.2.1: Initial version, Aug. 2025, Alexis Hrysiewicz

"""

__docstringapp__ = """EZ-InSAR application: Find the next acquisitions of Sentinel-1

usage: ezinsar S1planned -b <bbox> [--ezinsarjob <job_file>] [options]

Arguments:
    -b, --bbox <W,S,E,N>    Bbox of the Region of Interest (W,S,E,N) in EPGS:4326

Job-options:
    --ezinsarjob <str>      EZ-InSAR job [default: None]

Satellite-options:
    -o, --relative_orbit <int>      Relative orbit, [default: 0]
    -f, --flight_direction <str>    Orbit direction (ascending, or descending) [default: ASCENDING]
    -m, --acquisition_mode <str>    Acquisition mode (IW or SM) [default: IW] 

Other-options:
    --savelist      Save the list
    --savemap       Save a map of SLC extents
    --savekmz       Save a .kmz files
    --nolog         No logging
    -h, --help
    -q, --quiet     Suppress verbose

"""

from docopt import docopt
from datetime import datetime 
import os

import ezinsar.job as ez
from ezinsar.eicomponents.sensor.s1module import s1slctools
from ezinsar import usermessage

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

    if args['--ezinsarjob'] == 'None':
        jobezinsar = ez.EIjob(verbose=False,satmode=args['--acquisition_mode'],log=log,satellite='S1',satpass=args['--flight_direction'],relorbit=int(args['--relative_orbit']))
        jobezinsar.workdirectory = '.'
        jobezinsar.pathSLC = '.'
        jobezinsar.pathorbit = '.'
        jobezinsar.pathaux = '.'
        jobezinsar.date1 = datetime.strptime('2025-01-01T00:00:00'+'.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')
        jobezinsar.date2 = datetime.strptime('2025-01-02T00:00:00'+'.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')
        jobezinsar.importroi(input=args['--bbox'])
        jobezinsar.mkdir()
    else: 
        usermessage.ezprint('Directories, dates and ROI parameters will be bypassed because the user has given an EZ-InSAR job.',log,verbose)
        jobezinsar = ez.load(args['--ezinsarjob'],verbose=False)

    jobezinsar.SLClist = s1slctools.listnewS1acquisition(jobezinsar,verbose=verbose)
    jobezinsar.checkSLClist()
    jobezinsar.printSLClist()

    if args['--savelist']: 
        jobezinsar.saveSLClist(file='S1planned.list')
        
    if args['--savemap']:
        jobezinsar.displaySLClist(figure='S1plannedmap.jpg')

    if args['--savekmz']:
        jobezinsar.writeSLClisttokmz(file='S1planned.kmz')

    os.chdir(cur_dir)


if __name__=='__main__':
    main()
         