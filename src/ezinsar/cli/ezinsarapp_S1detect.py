#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Detect the Sentinel-1 IW track and orbits

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 
        
        $ ezinsar S1detect --help

Changelog:
    * 3.3.1: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 3.2.2: Initial version, Sep. 2025

"""

__docstringapp__ =  """EZ-InSAR application: Detect the Sentinel-1 IW track and orbits

usage: 
    ezinsar S1detect -b <file>  [options]

Arguments:
    -b, --bbox <str>            Bbox or EZ-InSAR job file (.ei for extension) 

Options: 
    --savemapburst              Save a map of bursts
    --server <str>              Server for time checking [default: Copernicus]
    
Other-options:
    --nolog                     No logging
    -h, --help
    -q, --quiet                 Suppress verbose

"""

from docopt import docopt
import ezinsar.job as ez
from ezinsar.eicomponents.sensor.s1module import s1iwburstIDapp
from ezinsar import usermessage, constants
import numpy as np
import datetime

def main():
    """Main function"""
    args = docopt(__docstringapp__)
        
    if args['--bbox'].endswith('.ei'):
        jobezinsar = ez.load(args['--bbox'],verbose=False)
    else:
        jobezinsar = ez.EIjob(verbose=False)
        jobezinsar.importroi(input=args['--bbox'])

    jobezinsar.relorbit = None
    jobezinsar.satpass = None

    jobezinsar.date2 = datetime.datetime.today()
    jobezinsar.date1 = jobezinsar.date2 - datetime.timedelta(days=int(30))

    if args['--nolog']: 
        log = None
    else:
        log = 'EZInSAR.log'

    usermessage.openingmsg(__name__,__name__,__file__,constants.__copyright__,'Detect the Sentinel-1 IW track and orbits based on a Region of Interest',log,verbose=(args['--quiet']==False))
        
    usermessage.ezprint('Region of Interest: %s' % (jobezinsar.roi),log,verbose=(args['--quiet']==False))

    jobdetect = s1iwburstIDapp.S1burstIDmap(verbose=(args['--quiet']==False)).checkfile(verbose=(args['--quiet']==False)).downloadfile(verbose=(args['--quiet']==False)).detectfromIDmap(jobezinsar,verbose=(args['--quiet']==False))

    if args['--savemapburst'] == True:
        jobdetect.display(jobezinsar,figure='figure_S1ID.jpg',verbose=(args['--quiet']==False))

    a, b , res = jobdetect.analyse(jobezinsar,verbose=(args['--quiet']==False))

    date1 = []
    date2 = []
    hourapprox = []

    for idx, namei in enumerate(res['name']):
        jobezinsar.satpass = namei.split('_')[0]
        jobezinsar.relorbit = int(namei.split('_')[1])

        try:
            jobezinsar.initiateSLC(mode='online',server=args['--server'],verbose=(args['--quiet']==False))

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

    usermessage.ezprint('------------------------------------------------------------------',None,verbose=(args['--quiet']==False))
    usermessage.ezprint('------------------------------------------------------------------',None,verbose=(args['--quiet']==False))
    usermessage.ezprint('The potential interferogram can be computed using the following satellite parameters:',log,verbose=(args['--quiet']==False))
    usermessage.ezprint('------------------------------------------------------------------',None,verbose=(args['--quiet']==False))
    for idx, namei in enumerate(res['name']):
        usermessage.ezprint('\t%s with a overlap of %d with the ROI' % (namei,res['overlap'][idx]),log,verbose=(args['--quiet']==False))
        usermessage.ezprint('\t\tBetween %s and %s (approx. %s)' % (date1[idx],date2[idx],hourapprox[idx]),log,verbose=(args['--quiet']==False))

if __name__=='__main__':
    main()