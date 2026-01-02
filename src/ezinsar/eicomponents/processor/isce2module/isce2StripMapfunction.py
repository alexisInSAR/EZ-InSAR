#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to process ScanSAR data with ISCE-2 processor 

The module allows to process ScanSAR data with ISCE-2 processor 
from an ``ezinsar.coregistration`` job. 
    
    (From `ezinsar` package)

Note: 
        Each function can directly used in Python scripts or/and a Python terminal

Changelog:
        * 1.2.0: New checking of S1 orbit, Aug. 2025, Alexis Hrysiewicz
        * 1.1.0: Several changes, Feb. 2025, Alexis Hrysiewicz
                * Add the support of Sentinel-1 C and D
                * Start the support of RADARSAT-2 FQ and SQ imagery
                * Start the support of CSK HIMAGE imagery
        * 1.0.0: Initial version, Jan. 2024

Todo: 
        * This module needs a huge optimisation.
        * Write the part to send an email

"""

################################################################################
## Python packages
################################################################################
from datetime import datetime
import os
import numpy as np
import glob
import datetime
from typing import Optional
from mpl_toolkits.basemap import Basemap
from matplotlib import path
import matplotlib.pyplot as plt
from shapely.wkt import loads
from shapely import Polygon
import shutil
import jdcal
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
from osgeo import gdal

from ezinsar import usermessage
from ezinsar import constants
from ezinsar.eicomponents.processor.isce2module import isce2tools
from ezinsar.eicomponents.processor.mintpymodule import mintpytsprocessing
from ezinsar.eicomponents.sensor.s1module import s1slctools, s1stacktools, s1orbits
from ezinsar.eicomponents.sensor.tsxmodule import tsxslctools, tsxstacktools
from ezinsar.eicomponents.sensor.alos2module import alos2slctools, alos2stacktools
from ezinsar.eicomponents.sensor.rsat2module import rsat2slctools, rsat2stacktools
from ezinsar.eicomponents.sensor.cskmodule import cskslctools, cskstacktools

from ezinsar.tools import geocoding
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## checkSLC FUNCTION
################################################################################
def checkSLC(jobcoreg, verbose: Optional[bool] = None):
        """Check the SLC files 

        The function checks the SLC files, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,checkSLC.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,checkSLC.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        usermessage.openingmsg(__name__,checkSLC.__name__,__file__,__copyright__,'Coregistration Step: checkSLC (Sentinel-1 IW)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        ## Create the work directory
        if not os.path.isdir(jobcoreg.workdirectory):
                os.mkdir(jobcoreg.workdirectory)
        os.chdir(jobcoreg.workdirectory)

        if jobcoreg.satellite == 'S1':
                
                ## List the .zip or SAFE
                filelist = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'*.zip') + glob.glob(jobcoreg.pathSLC+os.sep+'*.SAFE'))

                date = []
                for slci in filelist:
                        datestr = slci.split(os.sep)[-1].split('.')[0].split('_')[5].split('T')[0] #We convert the name of files to date string.

                        usermessage.ezprint('For the file: %s.' %(slci),jobcoreg.log,verbose)   
                        
                        # Check the polarisation (not required because job can check this value)
                        check_sum_pol = 0
                        for poli in jobcoreg.polarisation:
                                try: 
                                        S1annoresults = s1slctools.detectS1annoatationfromxml(slci,poli.upper())
                                        check_sum_pol = check_sum_pol + 1 
                                except:
                                        check_sum_pol = check_sum_pol + 0

                        if check_sum_pol == len(jobcoreg.polarisation):
                                date.append(datetime.datetime.strptime(datestr, '%Y%m%d')) #We add the date in string to our list of date.
                                usermessage.ezprint('\tOkay',jobcoreg.log,verbose)   
                        else:
                                usermessage.warningmsg(__name__,checkSLC.__name__,__file__,'Not required polarisation(s).',jobcoreg.log,verbose)
        
        else: 
                date = []
                if jobcoreg.satellite == 'PAZ' or jobcoreg.satellite == 'TSX':
                        filelist = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+jobcoreg.satellite+'*'))
                elif jobcoreg.satellite == 'ALOS2' or jobcoreg.satellite == 'ALOS':
                        filelist = []
                        for li in glob.glob(jobcoreg.pathSLC+os.sep+'*'+os.sep+'VOL*') + glob.glob(jobcoreg.pathSLC+os.sep+'*'+os.sep+'*.CEOS'): 
                                filelist.append(os.path.dirname(li))
                        filelist = np.sort(filelist)
                elif jobcoreg.satellite == 'RSAT2':
                        filelist = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'RS2*'))
                elif jobcoreg.satellite == 'CSK':
                        filelist = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'CSK*'))

                for fi in filelist: 
                        if jobcoreg.satellite == 'PAZ' or jobcoreg.satellite == 'TSX':
                                annoresults = tsxslctools.detectTSXannotationfromxml(fi,'VV')
                        elif jobcoreg.satellite == 'ALOS2' or jobcoreg.satellite == 'ALOS':
                                annoresults = alos2slctools.detectALOS2annotationfromxml(fi)
                        elif jobcoreg.satellite == 'RSAT2':
                                annoresults = rsat2slctools.detectRSAT2annotation(fi,jobcoreg.polarisation[0].upper())
                        elif jobcoreg.satellite == 'CSK':
                                annoresults = cskslctools.detectCSKannotation(fi,jobcoreg.polarisation[0].upper())

                        date.append(datetime.datetime.strptime(annoresults['data_xmli1']['startTime'].split('T')[0].replace('-',''), '%Y%m%d')) 

        #We sort the dates
        date = sorted(date)
        date = np.unique(date)

        #We rewritte the list with sorted dates
        usermessage.ezprint('Write the dates files in %s' %(jobcoreg.workdirectory+os.sep+'dates'),jobcoreg.log,verbose) 
        fibis = open(jobcoreg.workdirectory+os.sep+'dates','w')
        for di in date:
            datestr = di.strftime("%Y%m%d")
            fibis.write(datestr+'\n')
        fibis.close()

        jobcoreg.dates = date

        # Display 
        usermessage.ezprint('There are %d .zip files for %d unique dates.\n' %(len(filelist),len(date)),jobcoreg.log,verbose) 

        os.chdir(cur_dir)
        jobcoreg.checkSLC['done']['value'] = True

        return jobcoreg

################################################################################
## checkOrbit FUNCTION
################################################################################
def checkOrbit(jobcoreg, verbose: Optional[bool] = None):
        """Check the orbit files

        The function checks the orbit files, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,checkOrbit.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,checkOrbit.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        usermessage.openingmsg(__name__,checkOrbit.__name__,__file__,__copyright__,'Coregistration Step: checkOrbit (Sentinel-1 IW)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.checkSLC['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,checkOrbit.__name__,__file__,__copyright__,
                                'The previous step (checkSLC) is not done.',None))

        if jobcoreg.satellite == 'S1':
                s1orbits.checkorbitfile(jobcoreg.pathSLC,jobcoreg.pathorbit,verbose=verbose,log=jobcoreg.log)
        else: 
                usermessage.ezprint('This step is bypassed for %s %s.' % (jobcoreg.satellite,jobcoreg.satmode),jobcoreg.log,verbose) 

        os.chdir(cur_dir)
        jobcoreg.checkOrbit['done']['value'] = True

        return jobcoreg

################################################################################
## coarserefdate FUNCTION
################################################################################
def coarserefdate(jobcoreg, verbose: Optional[bool] = None):
        """Detection of the best potential reference date

        The function defines the best potential reference date, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,coarserefdate.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,coarserefdate.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        usermessage.openingmsg(__name__,coarserefdate.__name__,__file__,__copyright__,'Coregistration Step: coarserefdate (StripMap)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.checkOrbit['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,coarserefdate.__name__,__file__,__copyright__,
                                'The previous step (checkOrbit) is not done.',None))

        if jobcoreg.satellite == 'S1': 

                date_ref, dates_SLC, Btempnorm, Bperpnorm = s1stacktools.commputecoarsenetwork(jobcoreg.pathSLC,jobcoreg.roi,jobcoreg.polarisation[0],
                        pathorbit = jobcoreg.pathorbit,
                        DEM = jobcoreg.pathDEM+os.sep+jobcoreg.nameDEM,
                        figure = jobcoreg.workdirectory+os.sep+'coarse_ifg_network',
                        preref = None,
                        verbose = jobcoreg.verbose, 
                        log = jobcoreg.log, 
                        )     
                
        elif jobcoreg.satellite == 'TSX' or jobcoreg.satellite == 'PAZ': 

                date_ref, dates_SLC, Btempnorm, Bperpnorm = tsxstacktools.commputecoarsenetworkSM(jobcoreg.pathSLC,jobcoreg.roi,
                        jobcoreg.polarisation[0],
                        DEM = jobcoreg.pathDEM+os.sep+jobcoreg.nameDEM,
                        figure = jobcoreg.workdirectory+os.sep+'coarse_ifg_network',
                        preref = None,
                        verbose = jobcoreg.verbose, 
                        log = jobcoreg.log, 
                        )   
        
        elif jobcoreg.satellite == 'ALOS2' or jobcoreg.satellite == 'ALOS': 

                date_ref, dates_SLC, Btempnorm, Bperpnorm = alos2stacktools.commputecoarsenetworkSM(jobcoreg.pathSLC,jobcoreg.roi,
                        jobcoreg.polarisation[0],
                        DEM = jobcoreg.pathDEM+os.sep+jobcoreg.nameDEM,
                        figure = jobcoreg.workdirectory+os.sep+'coarse_ifg_network',
                        preref = None,
                        verbose = jobcoreg.verbose, 
                        log = jobcoreg.log, 
                        )   
        
        elif jobcoreg.satellite == 'RSAT2': 

                date_ref, dates_SLC, Btempnorm, Bperpnorm = rsat2stacktools.commputecoarsenetworkSM(jobcoreg.pathSLC,jobcoreg.roi,
                        jobcoreg.polarisation[0],
                        DEM = jobcoreg.pathDEM+os.sep+jobcoreg.nameDEM,
                        figure = jobcoreg.workdirectory+os.sep+'coarse_ifg_network',
                        preref = None,
                        verbose = jobcoreg.verbose, 
                        log = jobcoreg.log, 
                        )   
        
        elif jobcoreg.satellite == 'CSK': 

                date_ref, dates_SLC, Btempnorm, Bperpnorm = cskstacktools.commputecoarsenetworkSM(jobcoreg.pathSLC,jobcoreg.roi,
                        jobcoreg.polarisation[0],
                        DEM = jobcoreg.pathDEM+os.sep+jobcoreg.nameDEM,
                        figure = jobcoreg.workdirectory+os.sep+'coarse_ifg_network',
                        preref = None,
                        verbose = jobcoreg.verbose, 
                        log = jobcoreg.log, 
                        )   
                
        else:

                date_ref = None
                dates_SLC = None
                Btempnorm = None
                Bperpnorm = None 
        
        jobcoreg.refdate = datetime.datetime.strftime(date_ref,'%Y%m%d')

        os.chdir(cur_dir)
        jobcoreg.coarserefdate['done']['value'] = True

        return jobcoreg 

################################################################################
## unpack_slc FUNCTION
################################################################################
def unpack_slc(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """Unpack the SLC files

        The function unpacks the SLC files, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,unpack_slc.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,unpack_slc.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        usermessage.openingmsg(__name__,unpack_slc.__name__,__file__,__copyright__,'Coregistration Step: unpack_slc (StripMap)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.coarserefdate['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,unpack_slc.__name__,__file__,__copyright__,
                        'The previous step (coarserefdate) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'unpack_slc',gui=jobcoreg.gui)
        

        if not os.path.isdir(jobcoreg.workdirectory+os.sep+'Data_slc_unpacked'): 
                os.mkdir(jobcoreg.workdirectory+os.sep+'Data_slc_unpacked')

        ## Run ISCE2
        usermessage.ezprint('Detection of the images:...',jobcoreg.log,verbose)

        if jobcoreg.satellite == 'S1': 
                listslc = glob.glob(jobcoreg.pathSLC+os.sep+'*.zip') + glob.glob(jobcoreg.pathSLC+os.sep+'*.SAFE') 

        elif jobcoreg.satellite == 'TSX' or jobcoreg.satellite == 'PAZ':
                listslc = glob.glob(jobcoreg.pathSLC+os.sep+'PAZ*') + glob.glob(jobcoreg.pathSLC+os.sep+'TSX*') + glob.glob(jobcoreg.pathSLC+os.sep+'TDM*')

        elif jobcoreg.satellite == 'ALOS2' or jobcoreg.satellite == 'ALOS':
                listslc = []
                for li in glob.glob(jobcoreg.pathSLC+os.sep+'*'+os.sep+'VOL*') + glob.glob(jobcoreg.pathSLC+os.sep+'*'+os.sep+'*.CEOS'): 
                        listslc.append(os.path.dirname(li))

        elif jobcoreg.satellite == 'RSAT2': 
                listslc = glob.glob(jobcoreg.pathSLC+os.sep+'RS2*')

        elif jobcoreg.satellite == 'CSK': 
                listslc = glob.glob(jobcoreg.pathSLC+os.sep+'CSK*')
        
        dict_cmd = {}

        h = 0
        for idx, slci in enumerate(listslc): 

                if jobcoreg.satellite == 'S1':
                        di = slci.split(os.sep)[-1].split('.')[0].split('T')[0].split('_')[-1]
                elif jobcoreg.satellite == 'TSX' or jobcoreg.satellite == 'PAZ':
                        annoresults = tsxslctools.detectTSXannotationfromxml(slci,'VV')
                        di = datetime.datetime.strptime(annoresults['data_xmli1']['startTime'].split('T')[0].replace('-',''), '%Y%m%d').strftime('%Y%m%d')

                        if len(annoresults['data_xmli1']['polarisation']) > 1: 
                                usermessage.warningmsg(__name__,unpack_slc.__name__,__file__,'Several polarisations has been detected. The files will be splitted.',jobcoreg.log,verbose)

                                slci = tsxslctools.tsxsplitpol(jobcoreg, 
                                                                     slci, 
                                                                     jobcoreg.workdirectory+os.sep+'splittedSLC', 
                                                                     verbose=verbose)
                                
                elif jobcoreg.satellite == 'ALOS2' or jobcoreg.satellite == 'ALOS':
                        annoresults = alos2slctools.detectALOS2annotationfromxml(slci,'VV')
                        di = datetime.datetime.strptime(annoresults['data_xmli1']['startTime'].split('T')[0].replace('-',''), '%Y%m%d').strftime('%Y%m%d')

                        if (jobcoreg.satellite == 'ALOS') and (len(annoresults['data_xmli1']['polarisation']) > 1): 
                                usermessage.warningmsg(__name__,unpack_slc.__name__,__file__,'Several polarisations has been detected. The files will be splitted.',jobcoreg.log,verbose)

                                slci = alos2slctools.alossplitpol(jobcoreg, 
                                                                     slci, 
                                                                     jobcoreg.workdirectory+os.sep+'splittedSLC', 
                                                                     verbose=verbose)
                                
                elif jobcoreg.satellite == 'RSAT2':
                        annoresults = rsat2slctools.detectRSAT2annotation(slci,'VV')
                        di = datetime.datetime.strptime(annoresults['data_xmli1']['startTime'].split('T')[0].replace('-',''), '%Y%m%d').strftime('%Y%m%d')
                
                elif jobcoreg.satellite == 'CSK':
                        annoresults = cskslctools.detectCSKannotation(slci,'VV')
                        di = datetime.datetime.strptime(annoresults['data_xmli1']['startTime'].split('T')[0].replace('-',''), '%Y%m%d').strftime('%Y%m%d')

                if not os.path.isdir(jobcoreg.workdirectory+os.sep+'Data_slc_unpacked'+os.sep+di) or modeforce == True: 

                        # os.mkdir(jobcoreg.workdirectory+os.sep+'Data_slc_unpacked'+os.sep+di)

                        if jobcoreg.satellite == 'S1':
                                cmdpath = ['unpackFrame_S1.py']
                        elif jobcoreg.satellite == 'TSX': 
                                cmdpath = ['unpackFrame_TSX_ezinsar.py']
                        elif jobcoreg.satellite == 'PAZ': 
                                cmdpath = ['unpackFrame_PAZ_ezinsar.py']
                        elif jobcoreg.satellite == 'ALOS2': 
                                cmdpath = ['unpackFrame_ALOS2_ezinsar.py']
                        elif jobcoreg.satellite == 'ALOS': 
                                cmdpath = ['unpackFrame_ALOS.py']
                        elif jobcoreg.satellite == 'RSAT2': 
                                cmdpath = ['unpackFrame_RSAT2.py']
                        elif jobcoreg.satellite == 'CSK': 
                                cmdpath = ['unpackFrame_CSK.py']

                        cmdpath.append('-i')
                        cmdpath.append('%s' % (slci))
                        cmdpath.append('-o')
                        cmdpath.append('%s' % (jobcoreg.workdirectory+os.sep+'Data_slc_unpacked'+os.sep+di))

                        if jobcoreg.satellite == 'S1':
                                cmdpath.append('-p')
                                cmdpath.append('%s' % (jobcoreg.polarisation[0].lower()))
                                cmdpath.append('-b')
                                cmdpath.append('%s' % (jobcoreg.pathorbit))
                        elif jobcoreg.satellite == 'ALOS2':
                                cmdpath.append('-p')
                                cmdpath.append('%s' % (jobcoreg.polarisation[0].lower()))

                        dict_cmd['cmd%s' % (h)] = [ cmdpath, None]
                        h = h + 1
                
                else: 
                        usermessage.warningmsg(__name__,unpack_slc.__name__,__file__,'The files exist.',jobcoreg.log,verbose)

        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'SM')

        os.chdir(cur_dir)
        jobcoreg.unpack_slc['done']['value'] = True

        return jobcoreg 

################################################################################
## crop_slc FUNCTION
################################################################################
def crop_slc(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """Crop the SLC images based on the ROI

        The function crops the SLC images, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,crop_slc.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,crop_slc.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        usermessage.openingmsg(__name__,crop_slc.__name__,__file__,__copyright__,'Coregistration Step: crop_slc (StripMap)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.unpack_slc['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,crop_slc.__name__,__file__,__copyright__,
                        'The previous step (unpack_slc) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'crop_slc',gui=jobcoreg.gui)
        

        polyROI = loads(jobcoreg.roi)
        os.chdir(jobcoreg.workdirectory)

        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        with open('dates','r') as fi: 
                for line in fi:
                        dslc = line.strip()
                        if (not os.path.isdir('%s/Data_slc_unpacked_crop/%s' % (jobcoreg.workdirectory,dslc))) or modeforce == True:
                                usermessage.ezprint('Create the input card for ISCE-2: %s...' % (dslc),jobcoreg.log,verbose)

                                with open(jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                        fout.write('[Common]\n')
                                        fout.write('##########################\n')
                                        fout.write('##########################\n')
                                        fout.write('[Function-1]\n')
                                        fout.write('cropFrame : \n')
                                        fout.write('input : %s/Data_slc_unpacked/%s\n' % (jobcoreg.workdirectory,dslc))
                                        fout.write('box_str : %s %s %s %s\n' % (
                                                np.min(polyROI.exterior.xy[1]),
                                                np.max(polyROI.exterior.xy[1]),
                                                np.min(polyROI.exterior.xy[0]),
                                                np.max(polyROI.exterior.xy[0]),
                                        ))
                                        fout.write('output : %s/Data_slc_unpacked_crop/%s\n' % (jobcoreg.workdirectory,dslc))
                                        # fout.write('native : True \n')
                                        fout.write('##########################')

                                dict_cmd['cmd%s' % (h)] = [ ['stripmapWrapper.py','-c',jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                        jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                
                                h = h + 1
                        else:
                                usermessage.warningmsg(__name__,crop_slc.__name__,__file__,'The files exist.',jobcoreg.log,verbose)

        ## Run ISCE-2
        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'SM')
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])

        os.chdir(cur_dir)
        jobcoreg.crop_slc['done']['value'] = True

        return jobcoreg 

################################################################################
## reference FUNCTION
################################################################################
def reference(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """Initialisation of the reference image

        The function initialises the reference image, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,reference.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,reference.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        usermessage.openingmsg(__name__,reference.__name__,__file__,__copyright__,'Coregistration Step: reference (StripMap)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.crop_slc['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,reference.__name__,__file__,__copyright__,
                        'The previous step (crop_slc) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'reference',gui=jobcoreg.gui)
        
        os.chdir(jobcoreg.workdirectory)

        ## Create the input card
        usermessage.ezprint('Create the input card for ISCE-2:...',jobcoreg.log,verbose)

        with open(jobcoreg.workdirectory+os.sep+'config_card.tmp','w') as fout: 
                fout.write('[Common]\n')
                fout.write('##########################\n')
                fout.write('##########################\n')
                fout.write('[Function-1]\n')
                fout.write('topo : \n')
                fout.write('reference : %s/Data_slc_unpacked_crop/%s\n' % (jobcoreg.workdirectory,jobcoreg.refdate))
                fout.write('dem : %s/%s\n' % (jobcoreg.pathDEM,jobcoreg.nameDEM))
                fout.write('output : %s/geom_reference\n' % (jobcoreg.pathstack))
                fout.write('alks : %s\n' % (jobcoreg.mlazi))
                fout.write('rlks : %s\n' % (jobcoreg.mlran))
                # fout.write('native : True\n')
                fout.write('useGPU : False\n')
                fout.write('##########################\n')
                # fout.write('##########################\n')
                # fout.write('[Function-2]\n')
                # fout.write('createWaterMask : \n')
                # fout.write('dem_file : %s/%s\n' % (jobcoreg.pathDEM,jobcoreg.nameDEM))
                # fout.write('lat_file : %s/coreg/geom_reference/lat.rdr\n' % (jobcoreg.workdirectory))
                # fout.write('lon_file : %s/coreg/geom_reference/lon.rdr\n' % (jobcoreg.workdirectory)) 
                # fout.write('output : %s/geom_reference/waterMask.rdr\n' % (jobcoreg.workdirectory))
                # fout.write('##########################')

        usermessage.ezprint('\tdone',jobcoreg.log,verbose)

        # Run ISCE
        cmd = ['stripmapWrapper.py','-c','%s' % (jobcoreg.workdirectory+os.sep+'config_card.tmp')]
        isce2tools.subprocessrun(cmd,jobcoreg.workdirectory+os.sep+'config_card.tmp',jobcoreg,isce2log,'SM')

        if os.path.isfile(jobcoreg.workdirectory+os.sep+'config_card.tmp'):
                os.remove(jobcoreg.workdirectory+os.sep+'config_card.tmp')

        ## Multilook the geom files: requires to move the geom directory
        if os.path.isdir(jobcoreg.pathstack+'/../geom_reference'):
                os.rename(jobcoreg.pathstack+'/../geom_reference',jobcoreg.workdirectory+'/geom_reference')

                os.chdir(jobcoreg.workdirectory+'/geom_reference')

                for fi in ['hgt','incLocal','lat','lon','los','shadowMask']:
                        os.environ['PATH'], os.environ['PYTHONPATH'] = isce2tools.isce2checkenv(mode='SM',verbose=False)
                        os.system('fixImageXml.py -i %s.rdr -f' % (fi))

        os.chdir(cur_dir)
        jobcoreg.reference['done']['value'] = True

        return jobcoreg 

################################################################################
## focus_split FUNCTION
################################################################################
def focus_split(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """focus_split

        The function XX, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,focus_split.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,focus_split.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        usermessage.openingmsg(__name__,focus_split.__name__,__file__,__copyright__,'Coregistration Step: focus_split (StripMap)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.reference['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,focus_split.__name__,__file__,__copyright__,
                        'The previous step (reference) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'focus_split',gui=jobcoreg.gui)
        
        os.chdir(jobcoreg.workdirectory)

        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        with open('dates','r') as fi: 
                for line in fi:
                        dslc = line.strip()
                        usermessage.ezprint('Create the input card for ISCE-2: %s...' % (dslc),jobcoreg.log,verbose)

                        with open(jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                fout.write('[Common]\n')
                                fout.write('##########################\n')

                        dict_cmd['cmd%s' % (h)] = [ ['stripmapWrapper.py','-c',jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                        
                        h = h + 1

        ## Run ISCE-2
        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'SM')
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])

        os.chdir(cur_dir)
        jobcoreg.focus_split['done']['value'] = True

        return jobcoreg 

################################################################################
## geo2rdr_coarseResamp FUNCTION
################################################################################
def geo2rdr_coarseResamp(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """geo2rdr_coarseResamp

        The function XX, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,geo2rdr_coarseResamp.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,geo2rdr_coarseResamp.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        usermessage.openingmsg(__name__,geo2rdr_coarseResamp.__name__,__file__,__copyright__,'Coregistration Step: geo2rdr_coarseResamp (StripMap)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.focus_split['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,geo2rdr_coarseResamp.__name__,__file__,__copyright__,
                        'The previous step (focus_split) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'geo2rdr_coarseResamp',gui=jobcoreg.gui)
        
        os.chdir(jobcoreg.workdirectory)

        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        with open('dates','r') as fi: 
                for line in fi:
                        dslc = line.strip()

                        if not dslc == jobcoreg.refdate:
                                usermessage.ezprint('Create the input card for ISCE-2: %s...' % (dslc),jobcoreg.log,verbose)

                                if (not os.path.isdir('%s/coregSLC/Coarse/%s' % (jobcoreg.workdirectory,dslc))) or modeforce == True:
                                        with open(jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                        
                                                fout.write('[Common]\n')
                                                fout.write('##########################\n')
                                                fout.write('##########################\n')
                                                fout.write('[Function-1]\n')
                                                fout.write('geo2rdr : \n')
                                                fout.write('reference : %s/Data_slc_unpacked_crop/%s\n' % (jobcoreg.workdirectory,jobcoreg.refdate))
                                                fout.write('secondary : %s/Data_slc_unpacked_crop/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('geom : %s/geom_reference\n' % (jobcoreg.pathstack))
                                                # fout.write('native : True\n')
                                                fout.write('useGPU : False\n')
                                                fout.write('outdir : %s/offsets/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('##########################\n')
                                                fout.write('##########################\n')
                                                fout.write('[Function-2]\n')
                                                fout.write('resampleSlc : \n')
                                                fout.write('reference : %s/Data_slc_unpacked_crop/%s\n' % (jobcoreg.workdirectory,jobcoreg.refdate))
                                                fout.write('secondary : %s/Data_slc_unpacked_crop/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('coreg : %s/coregSLC/Coarse/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('offsets : %s/offsets/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('##########################')

                                        dict_cmd['cmd%s' % (h)] = [ ['stripmapWrapper.py','-c',jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                                jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                        h = h + 1
                                        
                                else:
                                        usermessage.warningmsg(__name__,geo2rdr_coarseResamp.__name__,__file__,'The files exist.',jobcoreg.log,verbose)

        ## Run ISCE-2
        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'SM')
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])

        os.chdir(cur_dir)
        jobcoreg.geo2rdr_coarseResamp['done']['value'] = True

        return jobcoreg 

################################################################################
## refineSecondaryTiming FUNCTION
################################################################################
def refineSecondaryTiming(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """refineSecondaryTiming

        The function XX, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,refineSecondaryTiming.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,refineSecondaryTiming.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        usermessage.openingmsg(__name__,refineSecondaryTiming.__name__,__file__,__copyright__,'Coregistration Step: refineSecondaryTiming (StripMap)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.geo2rdr_coarseResamp['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,refineSecondaryTiming.__name__,__file__,__copyright__,
                        'The previous step (geo2rdr_coarseResamp) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'refineSecondaryTiming',gui=jobcoreg.gui)
        
        os.chdir(jobcoreg.workdirectory)

        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        dates = []
        with open('dates','r') as fi: 
                for line in fi:
                        dates.append(line.strip())

        for i in range(len(dates)):
                for j in range(i + 1, len(dates)):
                        dmaster = dates[i]
                        dslave = dates[j]

                        usermessage.ezprint('Create the input card for ISCE-2: %s - %s...' % (dmaster,dslave),jobcoreg.log,verbose)

                        if (not os.path.isdir('%s/refineSecondaryTiming/pairs/%s_%s/misreg' % (jobcoreg.workdirectory,dmaster,dslave))) or modeforce == True:
                                with open(jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                
                                        fout.write('[Common]\n')
                                        fout.write('##########################\n')
                                        fout.write('##########################\n')
                                        fout.write('[Function-1]\n')
                                        fout.write('refineSecondaryTiming : \n')
                                        if dmaster == jobcoreg.refdate: 
                                                fout.write('reference : %s/Data_slc_unpacked_crop/%s/%s.slc\n' % (jobcoreg.workdirectory,dmaster,dmaster))
                                        else: 
                                                fout.write('reference : %s/coregSLC/Coarse/%s/%s.slc\n' % (jobcoreg.workdirectory,dmaster,dmaster))
                                        
                                        if dslave == jobcoreg.refdate: 
                                                fout.write('secondary : %s/Data_slc_unpacked_crop/%s/%s.slc\n' % (jobcoreg.workdirectory,dslave,dslave))
                                        else:
                                                fout.write('secondary : %s/coregSLC/Coarse/%s/%s.slc\n' % (jobcoreg.workdirectory,dslave,dslave))
                                        fout.write('mm : %s/Data_slc_unpacked_crop/%s\n' % (jobcoreg.workdirectory,dmaster))
                                        fout.write('ss : %s/Data_slc_unpacked_crop/%s\n' % (jobcoreg.workdirectory,dslave))
                                        fout.write('outfile : %s/refineSecondaryTiming/pairs/%s_%s/misreg' % (jobcoreg.workdirectory,dmaster,dslave))

                                dict_cmd['cmd%s' % (h)] = [ ['stripmapWrapper.py','-c',jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                        jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                
                                h = h + 1
                                
                        else:
                                usermessage.warningmsg(__name__,refineSecondaryTiming.__name__,__file__,'The files exist.',jobcoreg.log,verbose)

        ## Run ISCE-2
        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'SM')
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])

        os.chdir(cur_dir)
        jobcoreg.refineSecondaryTiming['done']['value'] = True

        return jobcoreg 

################################################################################
## invertMisreg FUNCTION
################################################################################
def invertMisreg(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """invertMisreg

        The function will ..., from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,invertMisreg.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,invertMisreg.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,invertMisreg.__name__,__file__,__copyright__,'Coregistration Step: invertMisreg (Sentinel-1)',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.refineSecondaryTiming['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,invertMisreg.__name__,__file__,__copyright__,
                        'The previous step (refineSecondaryTiming) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'invertMisreg',gui=jobcoreg.gui)
        
        os.chdir(jobcoreg.workdirectory)

        ## Run ISCE-2
        dict_cmd = {
                'cmd0' : [
                        ['invertMisreg.py','-i','%s/refineSecondaryTiming/pairs/' % (jobcoreg.workdirectory),'-o','%s/refineSecondaryTiming/dates' % (jobcoreg.workdirectory)],
                        None,
                        ],
                }

        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'SM')
        
        os.chdir(cur_dir)

        jobcoreg.invertMisreg['done']['value'] = True

        return jobcoreg 

################################################################################
## fineResamp FUNCTION
################################################################################
def fineResamp(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """fineResamp

        The function will ..., from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,fineResamp.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,fineResamp.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        usermessage.openingmsg(__name__,fineResamp.__name__,__file__,__copyright__,'Coregistration Step: fineResamp (StripMap)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.invertMisreg['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,crop_slc.__name__,__file__,__copyright__,
                        'The previous step (invertMisreg) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'fineResamp',gui=jobcoreg.gui)
        

        os.chdir(jobcoreg.workdirectory)

        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        with open('dates','r') as fi: 
                for line in fi:
                        dslc = line.strip()
                        if not dslc == jobcoreg.refdate:
                                if (not os.path.isdir('%s/SLC/%s' % (jobcoreg.pathstack,dslc))) or modeforce == True:
                                        usermessage.ezprint('Create the input card for ISCE-2: %s...' % (dslc),jobcoreg.log,verbose)

                                        with open(jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                              
                                                fout.write('[Common]\n')
                                                fout.write('##########################\n')
                                                fout.write('##########################\n')
                                                fout.write('[Function-1]\n')
                                                fout.write('resampleSlc : \n')
                                                fout.write('reference : %s/Data_slc_unpacked_crop/%s\n' % (jobcoreg.workdirectory,jobcoreg.refdate))
                                                fout.write('secondary : %s/Data_slc_unpacked_crop/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('coreg : %s/SLC/%s\n' % (jobcoreg.pathstack,dslc))
                                                fout.write('offsets : %s/offsets/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('poly : %s/refineSecondaryTiming/dates/%s/misreg\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('##########################\n')

                                        dict_cmd['cmd%s' % (h)] = [ ['stripmapWrapper.py','-c',jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                                jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                        h = h + 1
                                else:
                                        usermessage.warningmsg(__name__,fineResamp.__name__,__file__,'The files exist.',jobcoreg.log,verbose)

        ## Run ISCE-2
        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'SM')
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])

        ## Copy the reference image
        if (not os.path.isdir('%s/SLC/%s' % (jobcoreg.pathstack,jobcoreg.refdate))):
                usermessage.warningmsg(__name__,fineResamp.__name__,__file__,'It requires to copy the reference image into the stack directory.',jobcoreg.log,verbose)

                dict_cmd = {
                'cmd0' : [
                        ['referenceStackCopy.py','-i','%s/Data_slc_unpacked_crop/%s/%s.slc' % (jobcoreg.workdirectory,jobcoreg.refdate,jobcoreg.refdate),'-o','%s/SLC/%s/%s.slc' % (jobcoreg.pathstack,jobcoreg.refdate,jobcoreg.refdate)],
                        None,
                        ],
                }

                isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'SM')

                os.chdir('%s/SLC/%s' % (jobcoreg.pathstack,jobcoreg.refdate))

                # No xml file created (needs a fix)
                xmlfile = glob.glob('%s/SLC/*/*.xml' % (jobcoreg.pathstack))
                xmlfileinput = xmlfile[0]
                dixml = xmlfileinput.split(os.sep)[-1].split('.')[0]
                xmlfileoutput = xmlfileinput.replace(dixml,jobcoreg.refdate)
                shutil.copy(xmlfileinput,xmlfileoutput+'.orig')

                with open(xmlfileoutput+'.orig', 'r') as file:
                        filedata = file.read()
                filedata = filedata.replace(dixml, jobcoreg.refdate)

                with open(xmlfileoutput, 'w') as file:
                        file.write(filedata)

                if os.path.isfile(xmlfileoutput+'.orig'):
                        os.remove(xmlfileoutput+'.orig')

                os.environ['PATH'], os.environ['PYTHONPATH'] = isce2tools.isce2checkenv(mode='SM',verbose=False)
                os.system('fixImageXml.py -i %s.slc -f' % (jobcoreg.refdate))

        os.chdir(cur_dir)
        jobcoreg.fineResamp['done']['value'] = True

        return jobcoreg 

################################################################################
## grid_baseline FUNCTION
################################################################################
def grid_baseline(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """grid_baseline

        The function will ..., from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,grid_baseline.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,grid_baseline.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,grid_baseline.__name__,__file__,__copyright__,'Coregistration Step: grid_baseline (Sentinel-1)',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.fineResamp['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,grid_baseline.__name__,__file__,__copyright__,
                        'The previous step (fineResamp) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'grid_baseline',gui=jobcoreg.gui)
        
        os.chdir(jobcoreg.workdirectory)

        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        with open('dates','r') as fi: 
                for line in fi:
                        dslc = line.strip()
                        if (not os.path.isfile('%s/baselines/%s/%s' % (jobcoreg.pathstack,dslc,dslc))) or modeforce == True:
                                usermessage.ezprint('Create the input card for ISCE-2: %s...' % (dslc),jobcoreg.log,verbose)

                                with open(jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                
                                        fout.write('[Common]\n')
                                        fout.write('##########################\n')
                                        fout.write('##########################\n')
                                        fout.write('[Function-1]\n')
                                        fout.write('baselineGrid : \n')
                                        fout.write('reference : %s/SLC/%s/referenceShelve\n' % (jobcoreg.pathstack,dslc))
                                        fout.write('secondary : %s/SLC/%s/secondaryShelve\n' % (jobcoreg.pathstack,dslc))
                                        fout.write('baseline_file : %s/baselines/%s/%s' % (jobcoreg.pathstack,dslc,dslc))

                                dict_cmd['cmd%s' % (h)] = [ ['stripmapWrapper.py','-c',jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                        jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                
                                h = h + 1
                        else:
                                usermessage.warningmsg(__name__,grid_baseline.__name__,__file__,'The files exist.',jobcoreg.log,verbose)

        ## Run ISCE-2
        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'SM')
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])

        ## Create a link for consistency
        try:
                os.symlink(jobcoreg.workdirectory,
                        jobcoreg.pathstack+os.sep+'coreg',
                        target_is_directory = True)
        except:
                usermessage.warningmsg(__name__,grid_baseline.__name__,__file__,'Impossible to create the symlink.',jobcoreg.log,verbose)

        os.chdir(cur_dir)

        jobcoreg.grid_baseline['done']['value'] = True

        return jobcoreg 

################################################################################
## ifgnetwork FUNCTION
################################################################################
def ifgnetwork(jobifg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """ifgnetwork

        The function will ..., from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2ifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,grid_baseline.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,grid_baseline.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))

        if not jobifg.log == None: 
                log = os.path.abspath(jobifg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,grid_baseline.__name__,__file__,__copyright__,'Ifgstack Step: ifgnetwork (StripMap)',log,verbose)

        jobifg.check(verbose=False,mode='high')

        isce2log = isce2tools.createisce2log(jobifg.log,cur_dir,'grid_baseline',gui=jobifg.gui)
        
        if not os.path.isdir(jobifg.workdirectory):
                os.mkdir(jobifg.workdirectory)
        os.chdir(jobifg.workdirectory)

        if not jobifg.modestack == ['StaMPS_PS']: 

                ## Read the average baselines 
                usermessage.ezprint('Read the average baselines:...',jobifg.log,verbose)
                dates = []
                datesjj = []
                datesdatetime = []
                bperp = []
                with open(jobifg.pathstack+os.sep+'coreg'+os.sep+'dates','r') as fi: 
                        for dslc in fi:
                                dslci = dslc.strip()
                                dslci_date = datetime.datetime.strptime(dslci, '%Y%m%d')
                                
                                if not dslci == jobifg.refdate:
                                        fi = gdal.Open('%s/baselines/%s/%s' % (jobifg.pathstack,dslci,dslci))
                                        bperpi =np.mean(fi.ReadAsArray(0))
                                        fi = None

                                else:
                                        bperpi = 0.0  

                                dates.append(dslci)
                                datesjj.append(int(sum(jdcal.gcal2jd(dslci_date.year, dslci_date.month, dslci_date.day))))
                                datesdatetime.append(dslci_date)
                                bperp.append(np.mean(bperpi))
                usermessage.ezprint('\tdone',jobifg.log,verbose)

                # Read the parameters
                usermessage.ezprint('Read the network parameters:...',jobifg.log,verbose)

                if jobifg.ifgnetwork['bperp_min']['value'] == '-': 
                        bperp_min = -1e9
                else: 
                        bperp_min = jobifg.ifgnetwork['bperp_min']['value']

                if jobifg.ifgnetwork['bperp_max']['value'] == '-': 
                        bperp_max = 1e9
                else: 
                        bperp_max = jobifg.ifgnetwork['bperp_max']['value']

                if jobifg.ifgnetwork['delta_T_min']['value'] == '-': 
                        delta_T_min = -1e9
                else: 
                        delta_T_min = jobifg.ifgnetwork['delta_T_min']['value']

                if jobifg.ifgnetwork['delta_T_max']['value'] == '-': 
                        delta_T_max = 1e9
                else: 
                        delta_T_max = jobifg.ifgnetwork['delta_T_max']['value']

                if jobifg.ifgnetwork['delta_n_max']['value'] == '-': 
                        delta_n_max = 1e9
                else: 
                        delta_n_max = jobifg.ifgnetwork['delta_n_max']['value']

                modenetwork = jobifg.ifgnetwork['SBAS_opti']['value']

                usermessage.ezprint('\tbperp_min [m]: %s' % (bperp_min),jobifg.log,verbose)
                usermessage.ezprint('\tbperp_max [m]: %s' % (bperp_max),jobifg.log,verbose)
                usermessage.ezprint('\tdelta_T_min [day]: %s' % (delta_T_min),jobifg.log,verbose)
                usermessage.ezprint('\tdelta_T_max [day]: %s' % (delta_T_max),jobifg.log,verbose)
                usermessage.ezprint('\tdelta_n_max: %s' % (delta_n_max),jobifg.log,verbose)
                usermessage.ezprint('\tmodenetwork: %s' % (modenetwork),jobifg.log,verbose)
                usermessage.ezprint('\tdone',jobifg.log,verbose)

                # Build the interferogram network
                usermessage.ezprint('Build the interferogram network:...',jobifg.log,verbose)

                ifg = []
                ifgbperp = []
                ifgidx = []

                if modenetwork == False:
                        for i in range(len(dates)):
                                h = 1
                                for j in range(i + 1, len(dates)):
                                        d1 = datetime.datetime.strptime(dates[i], '%Y%m%d')
                                        d2 = datetime.datetime.strptime(dates[j], '%Y%m%d')
                                        DT = int(sum(jdcal.gcal2jd(d2.year, d2.month, d2.day))) - int(sum(jdcal.gcal2jd(d1.year, d1.month, d1.day)))
                                        berpi = bperp[j] - bperp[i]
                                        if (h <= delta_n_max) and (DT >= delta_T_min) and (DT <= delta_T_max) and (berpi >= bperp_min) and (berpi <= bperp_max):
                                                ifg.append((dates[i], dates[j]))
                                                ifgbperp.append(berpi)
                                                ifgidx.append((i,j))
                                                h = h + 1
                
                elif modenetwork == 'delaunay':
                        usermessage.warningmsg(__name__,ifgnetwork.__name__,__file__,'The given parameters will be bypassed.',jobifg.log,verbose)
                        points = np.array([ [x,y] for x,y in zip(datesjj,bperp)])
                        tri = Delaunay(points)

                        ifg = []
                        
                        for trii in tri.simplices: 
                                if trii[0] < trii[1]: 
                                        ifga = (dates[trii[0]],dates[trii[1]])
                                        berpa = -(bperp[trii[0]] - bperp[trii[1]])
                                        idxa = (trii[0],trii[1])
                                else:
                                        ifga = (dates[trii[1]],dates[trii[0]])
                                        berpa = -(bperp[trii[1]] - bperp[trii[0]])
                                        idxa = (trii[1],trii[0])
                                if trii[1] < trii[2]: 
                                        ifgb = (dates[trii[1]],dates[trii[2]])
                                        berpb = -(bperp[trii[1]] - bperp[trii[2]])
                                        idxb = (trii[1],trii[2])
                                else:
                                        ifgb = (dates[trii[2]],dates[trii[1]])
                                        berpb = -(bperp[trii[2]] - bperp[trii[1]])
                                        idxb = (trii[2],trii[1])
                                if trii[0] < trii[2]: 
                                        ifgc = (dates[trii[0]],dates[trii[2]])
                                        berpc = -(bperp[trii[0]] - bperp[trii[2]])
                                        idxc = (trii[0],trii[2])
                                else:
                                        ifgc = (dates[trii[2]],dates[trii[0]])
                                        berpc = -(bperp[trii[2]] - bperp[trii[0]])
                                        idxc = (trii[2],trii[0])

                                if not ifga in ifg: 
                                        ifg.append(ifga)
                                        ifgbperp.append(berpa)
                                        ifgidx.append(idxa)
                                if not ifgb in ifg: 
                                        ifg.append(ifgb)
                                        ifgbperp.append(berpb)
                                        ifgidx.append(idxb)
                                if not ifgc in ifg: 
                                        ifg.append(ifgc)
                                        ifgbperp.append(berpc)
                                        ifgidx.append(idxc)
                        
                # Plot the network
                usermessage.ezprint('\tPlot the interferometric network',jobifg.log,verbose)
                for ifgi in ifgidx:
                        plt.plot([datesdatetime[ifgi[0]],datesdatetime[ifgi[1]]],
                                [bperp[ifgi[0]],bperp[ifgi[1]]], '-k')  
                plt.plot(datesdatetime, bperp, 'o')
                plt.xlabel("Time")
                plt.ylabel("Perpendicular Baselines [m]")
                plt.savefig(jobifg.workdirectory+os.sep+'bperp_file.txt.png')

                # Write the file
                usermessage.ezprint('\tWrite the bperp_file',jobifg.log,verbose)
                with open(jobifg.workdirectory+os.sep+'bperp_file.txt','w') as fout: 
                        h = 0
                        for ifgi in ifgidx:
                                fout.write('%d\t%s\t%s\t%f\n' % (
                                h+1,
                                dates[ifgi[0]], 
                                dates[ifgi[1]], 
                                ifgbperp[h],
                                ))
                                h = h + 1

        else:
                usermessage.ezprint('This step is not required for StaMPS PS.',jobifg.log,verbose)

        os.chdir(cur_dir)

        jobifg.ifgnetwork['done']['value'] = True

        return jobifg 

################################################################################
## generate_igram FUNCTION
################################################################################
def generate_igram(jobifg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """generate_igram

        The function will ..., from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2ifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,generate_igram.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,generate_igram.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))

        if not jobifg.log == None: 
                log = os.path.abspath(jobifg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,generate_igram.__name__,__file__,__copyright__,'Ifgstack Step: generate_igram (StripMap)',log,verbose)

        if jobifg.ifgnetwork['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,generate_igram.__name__,__file__,__copyright__,
                        'The previous step (ifgnetwork) is not done.',None))
        
        jobifg.check(verbose=False,mode='high')

        isce2log = isce2tools.createisce2log(jobifg.log,cur_dir,'generate_igram',gui=jobifg.gui)
        
        os.chdir(jobifg.workdirectory)

        if not 'StaMPS' in jobifg.modestack: 

                ## Create the input cards and the job
                h = 0
                dict_cmd = {}
                with open('bperp_file.txt','r') as fi: 
                        for line in fi:
                                master = line.split()[1]
                                slave = line.split()[2]

                                if (not os.path.isdir('%s/interferograms/%s_%s' % (jobifg.workdirectory,master,slave))) or modeforce == True:
                                        usermessage.ezprint('Create the input card for ISCE-2: %s - %s...' % (master,slave),jobifg.log,verbose)

                                        with open(jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                                
                                                fout.write('[Common]\n')
                                                fout.write('#########################\n')
                                                fout.write('##########################\n')
                                                fout.write('[Function-1]\n')
                                                fout.write('crossmul : \n')
                                                fout.write('reference : %s/SLC/%s/%s.slc\n' % (jobifg.pathstack,master,master))
                                                fout.write('secondary : %s/SLC/%s/%s.slc\n' % (jobifg.pathstack,slave,slave))
                                                fout.write('outdir : %s/interferograms/%s_%s/%s_%s\n' % (jobifg.pathstack,master,slave,master,slave))
                                                fout.write('alks : %s\n' % (jobifg.mlazi))
                                                fout.write('rlks : %s\n' % (jobifg.mlran))
                                                fout.write('##########################\n')

                                        dict_cmd['cmd%s' % (h)] = [ ['stripmapWrapper.py','-c',jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                                jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                        h = h + 1
                                else:
                                        usermessage.warningmsg(__name__,generate_igram.__name__,__file__,'The files exist.',jobifg.log,verbose)

                ## Run ISCE-2
                isce2tools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg,isce2log,'SM')
                for keyi in list(dict_cmd.keys()):
                        if os.path.isfile(dict_cmd[keyi][1]):
                                os.remove(dict_cmd[keyi][1])

        else: 
                usermessage.ezprint('This step is not required for StaMPS.',jobifg.log,verbose)

        os.chdir(cur_dir)

        jobifg.generate_igram['done']['value'] = True

        return jobifg 

################################################################################
## filter_coherence FUNCTION
################################################################################
def filter_coherence(jobifg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """filter_coherence

        The function will ..., from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2ifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,filter_coherence.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,filter_coherence.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))

        if not jobifg.log == None: 
                log = os.path.abspath(jobifg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,filter_coherence.__name__,__file__,__copyright__,'Ifgstack Step: filter_coherence (StripMap)',log,verbose)

        if jobifg.generate_igram['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,filter_coherence.__name__,__file__,__copyright__,
                        'The previous step (generate_igram) is not done.',None))
        
        jobifg.check(verbose=False,mode='high')

        isce2log = isce2tools.createisce2log(jobifg.log,cur_dir,'filter_coherence',gui=jobifg.gui)
        
        os.chdir(jobifg.workdirectory)

        if (not 'StaMPS' in jobifg.modestack) and jobifg.filter_coherence['process']['value'] == True: 

                ## Create the input cards and the job
                h = 0
                dict_cmd = {}
                with open('bperp_file.txt','r') as fi: 
                        for line in fi:
                                master = line.split()[1]
                                slave = line.split()[2]

                                if (not os.path.isfile('%s/interferograms/%s_%s/filt_%s_%s.cor' % (jobifg.pathstack,master,slave,master,slave))) or modeforce == True:
                                        usermessage.ezprint('Create the input card for ISCE-2: %s - %s...' % (master,slave),jobifg.log,verbose)

                                        with open(jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                                fout.write('[Common]\n')
                                                fout.write('##########################\n')
                                                fout.write('###################################\n')
                                                fout.write('[Function-1]\n')
                                                fout.write('FilterAndCoherence : \n')
                                                fout.write('input : %s/interferograms/%s_%s/%s_%s.int\n' % (jobifg.pathstack,master,slave,master,slave))
                                                fout.write('filt : %s/interferograms/%s_%s/filt_%s_%s.int\n' % (jobifg.pathstack,master,slave,master,slave))
                                                fout.write('coh : %s/interferograms/%s_%s/filt_%s_%s.cor\n' % (jobifg.pathstack,master,slave,master,slave))
                                                fout.write('strength : %s\n' % (jobifg.filter_coherence['strength']['value']))

                                        dict_cmd['cmd%s' % (h)] = [ ['stripmapWrapper.py','-c',jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                                jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                        h = h + 1
                                else:
                                        usermessage.warningmsg(__name__,filter_coherence.__name__,__file__,'The files exist.',jobifg.log,verbose)

                ## Run ISCE-2
                isce2tools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg,isce2log,'SM')
                for keyi in list(dict_cmd.keys()):
                        if os.path.isfile(dict_cmd[keyi][1]):
                                os.remove(dict_cmd[keyi][1])

        else: 
                usermessage.ezprint('This step will be bypassed.',jobifg.log,verbose)

        os.chdir(cur_dir)

        jobifg.filter_coherence['done']['value'] = True

        return jobifg 

################################################################################
## unwrap FUNCTION
################################################################################
def unwrap(jobifg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """unwrap

        The function will ..., from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2ifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,unwrap.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,unwrap.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))

        if not jobifg.log == None: 
                log = os.path.abspath(jobifg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,unwrap.__name__,__file__,__copyright__,'Ifgstack Step: unwrap (StripMap)',log,verbose)

        if jobifg.filter_coherence['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,unwrap.__name__,__file__,__copyright__,
                        'The previous step (filter_coherence) is not done.',None))
        
        jobifg.check(verbose=False,mode='high')

        isce2log = isce2tools.createisce2log(jobifg.log,cur_dir,'unwrap',gui=jobifg.gui)
        
        os.chdir(jobifg.workdirectory)

        if (not 'StaMPS' in jobifg.modestack) and jobifg.unwrap['process']['value'] == True: 

                ## Create the input cards and the job
                h = 0
                dict_cmd = {}
                with open('bperp_file.txt','r') as fi: 
                        for line in fi:
                                master = line.split()[1]
                                slave = line.split()[2]

                                if (not os.path.isfile('%s/interferograms/%s_%s/filt_%s_%s.unw' % (jobifg.pathstack,master,slave,master,slave))) or modeforce == True:
                                        usermessage.ezprint('Create the input card for ISCE-2: %s - %s...' % (master,slave),jobifg.log,verbose)

                                        with open(jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                                fout.write('[Common]\n')
                                                fout.write('##########################\n')
                                                fout.write('###################################\n')
                                                fout.write('[Function-1]\n')
                                                fout.write('unwrap : \n')
                                                fout.write('ifg : %s/interferograms/%s_%s/filt_%s_%s.int\n' % (jobifg.pathstack,master,slave,master,slave))
                                                fout.write('coh : %s/interferograms/%s_%s/filt_%s_%s.cor\n' % (jobifg.pathstack,master,slave,master,slave))
                                                fout.write('unwprefix : %s/interferograms/%s_%s/filt_%s_%s\n' % (jobifg.pathstack,master,slave,master,slave))
                                                fout.write('nomcf : %s\n' % (jobifg.unwrap['nomcf']['value']))
                                                fout.write('reference : %s/Data_slc_unpacked_crop/%s/data\n' % (jobifg.pathstack+os.sep+'coreg',jobifg.refdate))
                                                fout.write('defomax : 2\n')
                                                fout.write('rlks : %s\n' % (jobifg.mlran))
                                                fout.write('alks : %s\n' % (jobifg.mlazi))
                                                fout.write('method : %s\n' % (jobifg.unwrap['method']['value']))

                                        dict_cmd['cmd%s' % (h)] = [ ['stripmapWrapper.py','-c',jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                                jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                        h = h + 1
                                else:
                                        usermessage.warningmsg(__name__,unwrap.__name__,__file__,'The files exist.',jobifg.log,verbose)

                ## Run ISCE-2
                isce2tools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg,isce2log,'SM')
                for keyi in list(dict_cmd.keys()):
                        if os.path.isfile(dict_cmd[keyi][1]):
                                os.remove(dict_cmd[keyi][1])

        else: 
                usermessage.ezprint('This step will be bypassed.',jobifg.log,verbose)

        os.chdir(cur_dir)

        jobifg.unwrap['done']['value'] = True

        return jobifg 

################################################################################
## ifggeocoding FUNCTION
################################################################################
def ifggeocoding(jobifg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """ifggeocoding

        The function will ..., from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2ifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,ifggeocoding.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ifggeocoding.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))

        if not jobifg.log == None: 
                log = os.path.abspath(jobifg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,ifggeocoding.__name__,__file__,__copyright__,'Ifgstack Step: ifggeocoding (StripMap)',log,verbose)

        if jobifg.generate_igram['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,ifggeocoding.__name__,__file__,__copyright__,
                        'A previous step (generate_igram) is not done.',None))
        
        jobifg.check(verbose=False,mode='high')

        isce2log = isce2tools.createisce2log(jobifg.log,cur_dir,'ifggeocoding',gui=jobifg.gui)
        os.chdir(jobifg.workdirectory)

        if not os.path.isdir('%s/geotiff' % (jobifg.workdirectory)):
                os.mkdir('%s/geotiff' % (jobifg.workdirectory))
        os.chdir('%s/geotiff' % (jobifg.workdirectory))

        if jobifg.ifggeocoding['process']['value'] == True: 

                # Generation of the file list S1_IW_20240223_VV_20240306_VV.diff.geo.pha.tif
                usermessage.ezprint('Generation of the file list',jobifg.log,verbose)
                list_file = []
                list_outfile = []
                list_check = []
                with open('../bperp_file.txt','r') as fi: 
                        for line in fi:
                                master = line.split()[1]
                                slave = line.split()[2]

                                nametmp = '%s_%s_%s_%s_%s_%s' % (jobifg.satellite,jobifg.satmode,master,jobifg.polarisation[0].upper(),slave,jobifg.polarisation[0].upper())
                                if os.path.isfile('%s/interferograms/%s_%s/filt_%s_%s.int' % (jobifg.pathstack,master,slave,master,slave)):
                                        list_file.append('%s/interferograms/%s_%s/filt_%s_%s.int' % (jobifg.pathstack,master,slave,master,slave))
                                        list_outfile.append(nametmp+'.diff.filt.geo.pha.tif')
                                elif os.path.isfile('%s/interferograms/%s_%s/%s_%s.int' % (jobifg.pathstack,master,slave,master,slave)):
                                        list_file.append('%s/interferograms/%s_%s/%s_%s.int' % (jobifg.pathstack,master,slave,master,slave))
                                        list_outfile.append(nametmp+'.diff.geo.pha.tif')

                                if os.path.isfile('%s/interferograms/%s_%s/filt_%s_%s_%s.unw' % (jobifg.pathstack,master,slave,master,slave,jobifg.unwrap['method']['value'])):
                                        list_file.append('%s/interferograms/%s_%s/filt_%s_%s_%s.unw' % (jobifg.pathstack,master,slave,master,slave,jobifg.unwrap['method']['value']))
                                        list_outfile.append(nametmp+'.unw.filt.geo.tif')
                                elif os.path.isfile('%s/interferograms/%s_%s/%s_%s_%s.unw' % (jobifg.pathstack,master,slave,master,slave,jobifg.unwrap['method']['value'])):
                                        list_file.append('%s/interferograms/%s_%s/%s_%s_%s.unw' % (jobifg.pathstack,master,slave,master,slave,jobifg.unwrap['method']['value']))
                                        list_outfile.append(nametmp+'.unw.geo.tif')

                                if os.path.isfile('%s/interferograms/%s_%s/filt_%s_%s.cor' % (jobifg.pathstack,master,slave,master,slave)):
                                        list_file.append('%s/interferograms/%s_%s/filt_%s_%s.cor' % (jobifg.pathstack,master,slave,master,slave))
                                        list_outfile.append(nametmp+'.cc.geo.tif')
                                elif os.path.isfile('%s/interferograms/%s_%s/%s_%s.cor' % (jobifg.pathstack,master,slave,master,slave)):
                                        list_file.append('%s/interferograms/%s_%s/%s_%s.cor' % (jobifg.pathstack,master,slave,master,slave))
                                        list_outfile.append(nametmp+'.cc.geo.tif')
        
                for li in list_outfile:
                        if not os.path.isfile(li):
                                list_check.append(False)
                        else:
                                list_check.append(True) 

                ## Read the DEM information
                ds=gdal.Open(jobifg.pathDEM+os.sep+jobifg.nameDEM)
                deltaLon = np.abs(ds.GetGeoTransform()[1])/jobifg.ifggeocoding['DEMoverlon']['value']
                deltaLat = np.abs(ds.GetGeoTransform()[5])/jobifg.ifggeocoding['DEMoverlat']['value']
                ds = None

                poly = loads(jobifg.roi)

                for fi, fout, check in zip(list_file,list_outfile,list_check):

                        if (check == False) or (modeforce == True):

                                os.chdir(os.path.dirname(fi))

                                if (jobifg.mlazi == 1) and (jobifg.mlran == 1):
                                        latin = '%s/geom_reference/lat.rdr' % (jobifg.pathstack)
                                        lonin = '%s/geom_reference/lon.rdr' % (jobifg.pathstack)
                                        shadowin = '%s/geom_reference/shadowMask.rdr' % (jobifg.pathstack)
                                else:
                                        latin = '%s/coreg/geom_reference/lat.rdr' % (jobifg.pathstack)
                                        lonin = '%s/coreg/geom_reference/lon.rdr' % (jobifg.pathstack)
                                        shadowin = '%s/coreg/geom_reference/shadowMask.rdr' % (jobifg.pathstack)

                                geocoding.rdr2geotiff(
                                        fi,
                                        latin, 
                                        lonin,
                                        jobifg.workdirectory+os.sep+'geotiff'+os.sep+fout, 
                                        deltaLon,
                                        deltaLat,
                                        ROIpoly = poly,
                                        uchar=jobifg.ifggeocoding['uchargeotiff']['value'],
                                        shadowfile=shadowin,
                                        verbose=verbose,
                                        log=jobifg.log)
                                
        else: 
                usermessage.ezprint('This step will be bypassed.',jobifg.log,verbose)
                
        os.chdir(cur_dir)

        jobifg.unwrap['done']['value'] = True

        return jobifg 

################################################################################
## finalstack FUNCTION
################################################################################
def finalstack(jobifg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """finalstack

        The function will ..., from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2ifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,finalstack.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,finalstack.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))

        if not jobifg.log == None: 
                log = os.path.abspath(jobifg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,finalstack.__name__,__file__,__copyright__,'Ifgstack Step: finalstack (StripMap)',log,verbose)
        
        jobifg.check(verbose=False,mode='high')

        isce2log = isce2tools.createisce2log(jobifg.log,cur_dir,'finalstack',gui=jobifg.gui)
        
        ## For StaMPS
        if 'StaMPS' in jobifg.modestack: 
                usermessage.ezprint('Preparation of the StaMPS directory in %s' % (jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+jobifg.polarisation[0].lower()),jobifg.log,verbose)

                ## Creation of the StaMPS stack
                if not os.path.isdir(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+jobifg.polarisation[0].lower()):
                        os.mkdir(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+jobifg.polarisation[0].lower())
                os.chdir(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+jobifg.polarisation[0].lower())

                with open(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+jobifg.polarisation[0].lower()+os.sep+'input_file','w') as fout: 
                        fout.write('source_data %s\n' % ('slc_stack'))
                        fout.write('slc_stack_path %s\n' % (jobifg.pathstack+os.sep+'SLC'))
                        fout.write('slc_stack_reference %s\n' % (jobifg.refdate))
                        fout.write('slc_stack_geom_path %s\n'% (jobifg.pathstack+os.sep+'geom_reference'))
                        fout.write('slc_stack_baseline_path %s\n'% (jobifg.pathstack+os.sep+'baselines'))
                        fout.write('range_looks %s\n'% (jobifg.mlran))
                        fout.write('azimuth_looks %s\n'% (jobifg.mlazi))
                        fout.write('aspect_ratio %s\n\n'% (jobifg.mlran/jobifg.mlazi))

                        if jobifg.satellite == 'S1': 
                                lw = 0.055465760
                        elif jobifg.satellite == 'TSX' or jobifg.satellite == 'PAZ' or jobifg.satellite == 'CSK': 
                                lw = 0.0311
                        elif jobifg.satellite == 'ALOS2': 
                                lw = 0.2424525
                        elif jobifg.satellite == 'ALOS': 
                                lw = 0.2360571
                        elif jobifg.satellite == 'SAOCOM': 
                                lw = 0.2351313
                        fout.write('lambda %s\n'% (lw))

                        if jobifg.satmode == 'IW':
                                fout.write('slc_suffix %s\n'% ('.full'))
                                fout.write('geom_suffix %s\n'% ('.full'))
                        else:
                                fout.write('slc_suffix %s\n'% (''))
                                fout.write('geom_suffix %s\n'% (''))

                # Run the command
                if os.path.isdir(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+jobifg.polarisation[0].lower()+os.sep+'INSAR_'+jobifg.refdate):
                        usermessage.warningmsg(__name__,finalstack.__name__,__file__,'The previous StaMPS stack will be deleted.',jobifg.log,verbose)
                        shutil.rmtree(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+jobifg.polarisation[0].lower()+os.sep+'INSAR_'+jobifg.refdate)

                dict_cmd = {}
                jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+jobifg.polarisation[0].lower()

                if constants.__ISCE2_modesymlink__ == True:
                        dict_cmd['cmd0'] = [ ['make_single_reference_stack_isce','input_file'], 'input_file']                  
                else:
                        dict_cmd['cmd0'] = [ ['make_single_reference_stack_isce_cp','input_file'], 'input_file']

                isce2tools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg,isce2log,'SM')

                if 'SBAS' in jobifg.modestack: 
                        usermessage.ezprint('Create the multi-reference stack:',jobifg.log,verbose)                

                        os.chdir(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+jobifg.polarisation[0].lower()+os.sep+'INSAR_'+jobifg.refdate)

                        fout = open(jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+jobifg.polarisation[0].lower()+os.sep+'INSAR_'+jobifg.refdate+os.sep+'small_baselines.list','w')
                        with open(jobifg.workdirectory+os.sep+'bperp_file.txt') as fi:
                                for line in fi: 
                                        master = line.split()[1]
                                        slave = line.split()[2]
                                        fout.write('%s %s\n' % (master,slave))
                        fout.close()

                        if constants.__ISCE2_modesymlink__ == True:
                                dict_cmd['cmd0'] = [ ['make_small_baselines_isce'], None] 
                        else:
                                dict_cmd['cmd0'] = [ ['make_small_baselines_isce_cp'], None] 

                        isce2tools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg,isce2log,'SM')

        ## For MintPy
        if jobifg.modestack == 'MintPy':
                usermessage.ezprint('Generation of the MintPy configuration file:...',jobifg.log,verbose)

                jobtmp = mintpytsprocessing.sbas(job=jobifg,polarisation=jobifg.polarisation[0].upper())

                if not os.path.isdir(jobifg.finalstack['parentdirMintPy']['value']+os.sep+'stack_mintpy_'+jobifg.polarisation[0].lower()):
                        os.mkdir(jobifg.finalstack['parentdirMintPy']['value']+os.sep+'stack_mintpy_'+jobifg.polarisation[0].lower())
                if not os.path.isdir(jobifg.finalstack['parentdirMintPy']['value']+os.sep+'stack_mintpy_'+jobifg.polarisation[0].lower()+os.sep+'mintpy'):
                        os.mkdir(jobifg.finalstack['parentdirMintPy']['value']+os.sep+'stack_mintpy_'+jobifg.polarisation[0].lower()+os.sep+'mintpy')

                jobtmp.pathmintpyconfig = jobifg.finalstack['parentdirMintPy']['value']+os.sep+'stack_mintpy_'+jobifg.polarisation[0].lower()+os.sep+'mintpy'+os.sep+'TSmintpyprocessing.cfg'

                jobtmp.computer['compute.cluster']['value']
                jobtmp.computer['compute.numWorker']['value']

                jobtmp.load_data['load.processor']['value'] = 'isce'
                jobtmp.load_data['load.autoPath']['value'] = 'no'

                jobtmp.load_data['load.metaFile']['value'] = jobifg.pathstack+os.sep+'coreg'+os.sep+'slc_unpacked_crop'+os.sep+jobifg.refdate+os.sep+'*.xml'

                jobtmp.load_data['load.baselineDir']['value'] = jobifg.pathstack+os.sep+'coreg'+os.sep+'baselines'
                jobtmp.load_data['load.unwFile']['value'] = jobifg.pathstack+os.sep+'interferograms'+os.sep+'*'+os.sep+'filt*.unw'
                jobtmp.load_data['load.corFile']['value'] = jobifg.pathstack+os.sep+'interferograms'+os.sep+'*'+os.sep+'filt*.cor'
                jobtmp.load_data['load.connCompFile']['value'] = jobifg.pathstack+os.sep+'interferograms'+os.sep+'*'+os.sep+'filt*.unw.conncomp'
                
                jobtmp.load_data['load.ionoFile']['value'] = 'None'
                jobtmp.load_data['load.intFile']['value'] = 'None'

                jobtmp.load_data['load.demFile']['value'] = jobifg.pathstack+os.sep+'coreg/geom_reference'+os.sep+'hgt.rdr'
                jobtmp.load_data['load.lookupYFile']['value'] = jobifg.pathstack+os.sep+'coreg/geom_reference'+os.sep+'lat.rdr'
                jobtmp.load_data['load.lookupXFile']['value'] = jobifg.pathstack+os.sep+'coreg/geom_reference'+os.sep+'lon.rdr'
                jobtmp.load_data['load.incAngleFile']['value'] = jobifg.pathstack+os.sep+'coreg/geom_reference'+os.sep+'los.rdr'
                jobtmp.load_data['load.azAngleFile']['value'] = jobifg.pathstack+os.sep+'coreg/geom_reference'+os.sep+'los.rdr'
                jobtmp.load_data['load.shadowMaskFile']['value'] = jobifg.pathstack+os.sep+'coreg/geom_reference'+os.sep+'shadowMask.rdr'

                jobtmp.load_data['load.waterMaskFile']['value'] = 'None'

                jobtmp.load_data['load.bperpFile']['value'] = 'None'

                poly = loads(jobifg.roi).exterior.xy
                jobtmp.load_data['subset.lalo']['value'] = '%f:%f:%f:%f' % (
                                                                np.min(poly[1]),
                                                                np.max(poly[1]),
                                                                np.min(poly[0]),
                                                                np.max(poly[0]),
                                                                )

                jobtmp.correct_unwrap_error['unwrapError.method']['value'] = 'auto'
                jobtmp.correct_unwrap_error['unwrapError.numSample']['value'] = 20

                jobtmp.invert_network['networkInversion.weightFunc']['value'] = 'var'
                jobtmp.invert_network['networkInversion.maskDataset']['value'] = 'coherence'
                jobtmp.invert_network['networkInversion.maskThreshold']['value'] = 0.2
                jobtmp.invert_network['networkInversion.minTempCoh']['value'] = 0.4

                jobtmp.correct_troposphere['troposphericDelay.method']['value' ]= 'height_correlation'

                jobtmp.deramp['deramp']['value'] = 'linear'

                jobtmp.hdfeos5['save.hdfEos5']['value'] = 'yes'

                jobtmp.writecfg(file=jobifg.finalstack['parentdirMintPy']['value']+os.sep+'stack_mintpy_'+jobifg.polarisation[0].lower()+os.sep+'mintpy'+os.sep+'TSmintpyprocessing.cfg')
  
        os.chdir(cur_dir)

        jobifg.finalstack['done']['value'] = True

        return jobifg 