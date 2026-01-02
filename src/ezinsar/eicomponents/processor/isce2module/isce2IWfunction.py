#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to process ScanSAR data with ISCE-2 processor 

The module allows to process ScanSAR data with ISCE-2 processor 
from an ``ezinsar.coregistration`` job. 
    
    (From `ezinsar` package)

Changelog:
        * 1.2.0: New checking of S1 orbit, Aug. 2025, Alexis Hrysiewicz
        * 1.1.0: Add the support of Sentinel-1 C and D, Feb. 2025, Alexis Hrysiewicz
        * 1.0.0: Initial version, Dec. 2024

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
from matplotlib import path
import matplotlib.pyplot as plt
from shapely.wkt import loads
import shutil
import jdcal
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
from osgeo import gdal

from ezinsar import usermessage
from ezinsar import constants
from ezinsar.eicomponents.processor.isce2module import isce2tools
from ezinsar.eicomponents.processor.mintpymodule import mintpytsprocessing
from ezinsar.eicomponents.sensor.s1module import s1slctools, s1orbits
from ezinsar.eicomponents.sensor.s1module import s1stacktools
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
        
        usermessage.openingmsg(__name__,coarserefdate.__name__,__file__,__copyright__,'Coregistration Step: coarserefdate (ScanSAR)',jobcoreg.log,verbose)

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
## unpack_topo_reference FUNCTION
################################################################################
def unpack_topo_reference(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
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
                raise ValueError(usermessage.errormsg(__name__,unpack_topo_reference.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,unpack_topo_reference.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        usermessage.openingmsg(__name__,unpack_topo_reference.__name__,__file__,__copyright__,'Coregistration Step: unpack_topo_reference (Sentinel-1)',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.coarserefdate['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,unpack_topo_reference.__name__,__file__,__copyright__,
                        'The previous step (coarserefdate) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'unpack_topo_reference',gui=jobcoreg.gui)

        ## Create the input card
        usermessage.ezprint('Create the input card for ISCE-2:...',jobcoreg.log,verbose)

        listslc = ' '.join(glob.glob(jobcoreg.pathSLC+os.sep+'*'+jobcoreg.refdate+'*'))

        with open(jobcoreg.workdirectory+os.sep+'config_card.tmp','w') as fout: 
                fout.write('[Common]\n')
                fout.write('##########################\n')
                fout.write('##########################\n')
                fout.write('[Function-1]\n')
                fout.write('Sentinel1_TOPS : \n')
                fout.write('dirname : %s\n' % (listslc))
                fout.write('swaths : 1 2 3\n')
                fout.write('orbitdir : %s\n' % (jobcoreg.pathorbit))
                fout.write('outdir : %s/reference\n' % (jobcoreg.workdirectory))
                fout.write('auxdir : /%s\n' % (jobcoreg.pathaux))
                fout.write('bbox : %s %s %s %s\n' % (np.min(loads(jobcoreg.roi).exterior.xy[1]),
                                                     np.max(loads(jobcoreg.roi).exterior.xy[1]),
                                                     np.min(loads(jobcoreg.roi).exterior.xy[0]),
                                                     np.max(loads(jobcoreg.roi).exterior.xy[0]),
                                                ))
                fout.write('pol : %s\n' % (jobcoreg.polarisation[0].lower()))
                fout.write('##########################\n')
                fout.write('##########################\n')
                fout.write('#Call topo to produce reference geometry files\n')
                fout.write('[Function-2]\n')
                fout.write('topo : \n')
                fout.write('reference : %s/reference\n' % (jobcoreg.workdirectory))
                fout.write('dem : %s/%s\n' % (jobcoreg.pathDEM,jobcoreg.nameDEM))
                fout.write('geom_referenceDir : %s/geom_reference\n' % (jobcoreg.workdirectory))
                fout.write('numProcess : %d\n' % (jobcoreg.computercores))
                fout.write('##########################')

        usermessage.ezprint('\tdone',jobcoreg.log,verbose)

        ## Run ISCE
        cmd = ['SentinelWrapper.py','-c','%s' % (jobcoreg.workdirectory+os.sep+'config_card.tmp')]
        isce2tools.subprocessrun(cmd,jobcoreg.workdirectory+os.sep+'config_card.tmp',jobcoreg,isce2log,'IW')

        if os.path.isfile(jobcoreg.workdirectory+os.sep+'config_card.tmp'):
                os.remove(jobcoreg.workdirectory+os.sep+'config_card.tmp')

        os.chdir(cur_dir)
        jobcoreg.unpack_topo_reference['done']['value'] = True

        return jobcoreg 

################################################################################
## unpack_secondary_slc FUNCTION
################################################################################
def unpack_secondary_slc(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """Extract the images from the original files

        The function extracts the images and converts them to the ISCE-2 format, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,unpack_secondary_slc.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,unpack_secondary_slc.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,unpack_secondary_slc.__name__,__file__,__copyright__,'Coregistration Step: unpack_secondary_slc (Sentinel-1)',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.coarserefdate['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,unpack_secondary_slc.__name__,__file__,__copyright__,
                        'The previous step (unpack_topo_reference) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'unpack_secondary_slc',gui=jobcoreg.gui)
        os.chdir(jobcoreg.workdirectory)
        
        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        with open('dates','r') as fi: 
                for line in fi:
                        dslc = line.strip()
                        if not dslc == jobcoreg.refdate:
                                if (not os.path.isdir('%s/secondarys/%s' % (jobcoreg.workdirectory,dslc))) or modeforce == True:
                                        usermessage.ezprint('Create the input card for ISCE-2: %s...' % (dslc),jobcoreg.log,verbose)

                                        listslc = ' '.join(glob.glob(jobcoreg.pathSLC+os.sep+'*'+dslc+'*'))
                                        with open(jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                                fout.write('[Common]\n')
                                                fout.write('##########################\n')
                                                fout.write('##########################\n')
                                                fout.write('[Function-1]\n')
                                                fout.write('Sentinel1_TOPS : \n')
                                                fout.write('dirname : %s\n' % (listslc))
                                                fout.write('swaths : 1 2 3\n')
                                                fout.write('orbitdir : %s\n' % (jobcoreg.pathorbit))
                                                fout.write('outdir : %s/secondarys/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('auxdir : /%s\n' % (jobcoreg.pathaux))
                                                fout.write('bbox : %s %s %s %s\n' % (np.min(loads(jobcoreg.roi).exterior.xy[1]),
                                                                                np.max(loads(jobcoreg.roi).exterior.xy[1]),
                                                                                np.min(loads(jobcoreg.roi).exterior.xy[0]),
                                                                                np.max(loads(jobcoreg.roi).exterior.xy[0]),
                                                                                ))
                                                fout.write('pol : %s\n' % (jobcoreg.polarisation[0].lower()))
                                                fout.write('##########################\n')

                                        dict_cmd['cmd%s' % (h)] = [ ['SentinelWrapper.py','-c',jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                                jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                        h = h + 1
                                else:
                                        usermessage.warningmsg(__name__,unpack_secondary_slc.__name__,__file__,'The directory %s exists.' % ('%s/secondarys/%s' % (jobcoreg.workdirectory,dslc)),jobcoreg.log,verbose)

        ## Run ISCE-2
        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'IW')        
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])
              
        os.chdir(cur_dir)

        jobcoreg.unpack_secondary_slc['done']['value'] = True

        return jobcoreg 

################################################################################
## average_baseline FUNCTION
################################################################################
def average_baseline(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """Compute the average baselines

        The function will compute the average baselines, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,average_baseline.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,average_baseline.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,average_baseline.__name__,__file__,__copyright__,'Coregistration Step: average_baseline (Sentinel-1)',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.unpack_secondary_slc['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,average_baseline.__name__,__file__,__copyright__,
                        'The previous step (unpack_secondary_slc) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'average_baseline',gui=jobcoreg.gui)
        os.chdir(jobcoreg.workdirectory)
        
        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        with open('dates','r') as fi: 
                for line in fi:
                        dslc = line.strip()
                        if not dslc == jobcoreg.refdate:
                                if (not os.path.isfile('%s/baselines/%s_%s/%s_%s.txt' % (jobcoreg.workdirectory,jobcoreg.refdate,dslc,jobcoreg.refdate,dslc))) or modeforce == True:
                                        usermessage.ezprint('Create the input card for ISCE-2: %s...' % (dslc),jobcoreg.log,verbose)

                                        with open(jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                                fout.write('[Common]\n')
                                                fout.write('##########################\n')
                                                fout.write('##########################\n')
                                                fout.write('[Function-1]\n')
                                                fout.write('computeBaseline : \n')
                                                fout.write('reference : %s/reference/\n' % (jobcoreg.workdirectory))
                                                fout.write('secondary : %s/secondarys/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('baseline_file : %s/baselines/%s_%s/%s_%s.txt\n' % (jobcoreg.workdirectory,jobcoreg.refdate,dslc,jobcoreg.refdate,dslc))

                                        dict_cmd['cmd%s' % (h)] = [ ['SentinelWrapper.py','-c',jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                                jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                        h = h + 1
                                else:
                                        usermessage.warningmsg(__name__,average_baseline.__name__,__file__,'The directory %s exists.' % ('%s/baselines/%s_%s/%s_%s.txt\n' % (jobcoreg.workdirectory,jobcoreg.refdate,dslc,jobcoreg.refdate,dslc)),jobcoreg.log,verbose)

        ## Run ISCE-2
        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'IW')        
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])
              
        os.chdir(cur_dir)

        jobcoreg.average_baseline['done']['value'] = True

        return jobcoreg 

################################################################################
## extract_burst_overlaps FUNCTION
################################################################################
def extract_burst_overlaps(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """Extract the burst overlaps for the reference images

        The function will extract the burst overlaps, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,extract_burst_overlaps.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,extract_burst_overlaps.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,extract_burst_overlaps.__name__,__file__,__copyright__,'Coregistration Step: extract_burst_overlaps (Sentinel-1)',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.average_baseline['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,extract_burst_overlaps.__name__,__file__,__copyright__,
                        'The previous step (average_baseline) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'extract_burst_overlaps',gui=jobcoreg.gui)
        os.chdir(jobcoreg.workdirectory)
        
        ## Run ISCE
        cmd = ['subsetReference.py','-m','%s/reference' % (jobcoreg.workdirectory),'-g','%s/geom_reference' % (jobcoreg.workdirectory)]
        isce2tools.subprocessrun(cmd,None,jobcoreg,isce2log,'IW')

        os.chdir(cur_dir)

        jobcoreg.extract_burst_overlaps['done']['value'] = True

        return jobcoreg 

################################################################################
## overlap_geo2rdr FUNCTION
################################################################################
def overlap_geo2rdr(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """Compute the overlaps 

        The function will ..., from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,overlap_geo2rdr.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,overlap_geo2rdr.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,overlap_geo2rdr.__name__,__file__,__copyright__,'Coregistration Step: overlap_geo2rdr (Sentinel-1)',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.extract_burst_overlaps['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,overlap_geo2rdr.__name__,__file__,__copyright__,
                        'The previous step (extract_burst_overlaps) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'overlap_geo2rdr',gui=jobcoreg.gui)
        os.chdir(jobcoreg.workdirectory)
        
        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        with open('dates','r') as fi: 
                for line in fi:
                        dslc = line.strip()
                        if not dslc == jobcoreg.refdate:
                                if (not os.path.isdir('%s/coreg_secondarys/%s/overlap' % (jobcoreg.workdirectory,dslc))) or modeforce == True:
                                        usermessage.ezprint('Create the input card for ISCE-2: %s...' % (dslc),jobcoreg.log,verbose)

                                        with open(jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                                fout.write('[Common]\n')
                                                fout.write('##########################\n')
                                                fout.write('##########################\n')
                                                fout.write('[Function-1]\n')
                                                fout.write('geo2rdr :\n')
                                                fout.write('secondary : %s/secondarys/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('reference : %s/reference\n' % (jobcoreg.workdirectory))
                                                fout.write('geom_referenceDir : %s/geom_reference\n' % (jobcoreg.workdirectory))
                                                fout.write('coregSLCdir : %s/coreg_secondarys/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('overlap : True\n')
                                                fout.write('useGPU : %s\n' % (jobcoreg.overlap_geo2rdr['useGPU']['value']))

                                        dict_cmd['cmd%s' % (h)] = [ ['SentinelWrapper.py','-c',jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                                jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                        h = h + 1
                                else:
                                        usermessage.warningmsg(__name__,overlap_geo2rdr.__name__,__file__,'The directory %s exists.' % ('%s/coreg_secondarys/%s/overlap' % (jobcoreg.workdirectory,dslc)),jobcoreg.log,verbose)

        ## Run ISCE-2
        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'IW')
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])

        os.chdir(cur_dir)

        jobcoreg.overlap_geo2rdr['done']['value'] = True

        return jobcoreg 

################################################################################
## overlap_resample FUNCTION
################################################################################
def overlap_resample(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """Resample the overlaps 

        The function will ..., from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,overlap_resample.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,overlap_resample.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,overlap_resample.__name__,__file__,__copyright__,'Coregistration Step: overlap_resample (Sentinel-1)',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.overlap_geo2rdr['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,overlap_resample.__name__,__file__,__copyright__,
                        'The previous step (overlap_geo2rdr) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'overlap_resample',gui=jobcoreg.gui)
        os.chdir(jobcoreg.workdirectory)
        
        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        with open('dates','r') as fi: 
                for line in fi:
                        dslc = line.strip()
                        if not dslc == jobcoreg.refdate:
                                if (not glob.glob('%s/coreg_secondarys/%s/overlap/*xml*' % (jobcoreg.workdirectory,dslc))) or modeforce == True:
                                        usermessage.ezprint('Create the input card for ISCE-2: %s...' % (dslc),jobcoreg.log,verbose)

                                        with open(jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                                fout.write('[Common]\n')
                                                fout.write('##########################\n')
                                                fout.write('##########################\n')
                                                fout.write('[Function-1]\n')
                                                fout.write('resamp_withCarrier :\n')
                                                fout.write('secondary : %s/secondarys/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('reference : %s/reference\n' % (jobcoreg.workdirectory))
                                                fout.write('coregdir : %s/coreg_secondarys/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('overlap : True\n')

                                        dict_cmd['cmd%s' % (h)] = [ ['SentinelWrapper.py','-c',jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                                jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                        h = h + 1
                                else:
                                        usermessage.warningmsg(__name__,overlap_resample.__name__,__file__,'The files exist.',jobcoreg.log,verbose)

        ## Run ISCE-2
        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'IW')
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])

        os.chdir(cur_dir)

        jobcoreg.overlap_resample['done']['value'] = True

        return jobcoreg 

################################################################################
## pairs_misreg FUNCTION
################################################################################
def pairs_misreg(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """pairs_misreg

        The function will ..., from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,pairs_misreg.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,pairs_misreg.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,pairs_misreg.__name__,__file__,__copyright__,'Coregistration Step: pairs_misreg (Sentinel-1)',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.overlap_resample['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,overlap_resample.__name__,__file__,__copyright__,
                        'The previous step (overlap_resample) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'pairs_misreg',gui=jobcoreg.gui)
        os.chdir(jobcoreg.workdirectory)

        # Read the date file
        dates = []
        with open('dates','r') as fi: 
                for line in fi:
                        dates.append(line.strip())

        ## Create the pairs
        ifg = []
        for i in range(len(dates)):
                h = 1
                for j in range(i + 1, len(dates)):
                        if h <= jobcoreg.pairs_misreg['maxconn']['value']:
                                ifg.append((dates[i], dates[j]))
                                h = h + 1

        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        for master, slave in ifg:
                        if master == jobcoreg.refdate:
                                pathmaster = '%s/reference' % (jobcoreg.workdirectory)
                        else:
                                pathmaster = '%s/coreg_secondarys/%s' % (jobcoreg.workdirectory,master)
                        if slave == jobcoreg.refdate:
                                pathslave = '%s/reference' % (jobcoreg.workdirectory)
                        else:
                                pathslave = '%s/coreg_secondarys/%s' % (jobcoreg.workdirectory,slave)

                        if (not os.path.isfile('%s/misreg/range/pairs/%s_%s/%s_%s.txt' % (jobcoreg.workdirectory,master,slave,master,slave))) or modeforce == True:
                                usermessage.ezprint('Create the input card for ISCE-2: %s - %s...' % (master,slave),jobcoreg.log,verbose)

                                with open(jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                        fout.write('[Common]\n')
                                        fout.write('##########################\n')
                                        fout.write('###################################\n')
                                        fout.write('[Function-1]\n')
                                        fout.write('generateIgram : \n')
                                        fout.write('reference : %s\n' % (pathmaster))
                                        fout.write('secondary : %s\n' % (pathslave))
                                        fout.write('interferogram : %s/coarse_interferograms/%s_%s\n' % (jobcoreg.workdirectory,master,slave))
                                        fout.write('flatten : False\n')
                                        fout.write('interferogram_prefix : int\n')
                                        fout.write('overlap : True\n')
                                        fout.write('###################################\n')
                                        fout.write('###################################\n')
                                        fout.write('[Function-2]\n')
                                        fout.write('overlap_withDEM : \n')
                                        fout.write('interferogram : %s/coarse_interferograms/%s_%s\n' % (jobcoreg.workdirectory,master,slave))
                                        fout.write('reference_dir : %s\n' % (pathmaster))
                                        fout.write('secondary_dir : %s\n' % (pathslave))
                                        fout.write('overlap_dir : %s/ESD/%s_%s\n' % (jobcoreg.workdirectory,master,slave))
                                        fout.write('###################################\n')
                                        fout.write('[Function-3]\n')
                                        fout.write('estimateAzimuthMisreg : \n')
                                        fout.write('overlap_dir : %s/ESD/%s_%s\n' % (jobcoreg.workdirectory,master,slave))
                                        fout.write('out_azimuth : %s/misreg/azimuth/pairs/%s_%s/%s_%s.txt\n' % (jobcoreg.workdirectory,master,slave,master,slave))
                                        fout.write('coh_threshold : %s\n' % (jobcoreg.pairs_misreg['coh_threshold']['value']))
                                        fout.write('plot : %s\n' % (jobcoreg.pairs_misreg['plot']['value']))
                                        fout.write('###################################\n')
                                        fout.write('[Function-4]\n')
                                        fout.write('estimateRangeMisreg : \n')
                                        fout.write('reference : %s\n' % (pathmaster))
                                        fout.write('secondary : %s\n' % (pathslave))
                                        fout.write('out_range : %s/misreg/range/pairs/%s_%s/%s_%s.txt\n' % (jobcoreg.workdirectory,master,slave,master,slave))
                                        fout.write('snr_threshold : %s\n' % (jobcoreg.pairs_misreg['snr_threshold']['value']))

                                dict_cmd['cmd%s' % (h)] = [ ['SentinelWrapper.py','-c',jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                        jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                h = h + 1
                        else:
                                usermessage.warningmsg(__name__,pairs_misreg.__name__,__file__,'The files exist.',jobcoreg.log,verbose)

        ## Run ISCE-2
        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'IW')
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])

        os.chdir(cur_dir)

        jobcoreg.pairs_misreg['done']['value'] = True

        return jobcoreg 

################################################################################
## timeseries_misreg FUNCTION
################################################################################
def timeseries_misreg(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """timeseries_misreg

        The function will ..., from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,timeseries_misreg.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,timeseries_misreg.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,timeseries_misreg.__name__,__file__,__copyright__,'Coregistration Step: timeseries_misreg (Sentinel-1)',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.pairs_misreg['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,overlap_resample.__name__,__file__,__copyright__,
                        'The previous step (pairs_misreg) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'timeseries_misreg',gui=jobcoreg.gui)
        os.chdir(jobcoreg.workdirectory)

        ## Run ISCE-2
        dict_cmd = {
                'cmd0' : [
                        ['invertMisreg.py','-i','%s/misreg/azimuth/pairs/' % (jobcoreg.workdirectory),'-o','%s/misreg/azimuth/dates/' % (jobcoreg.workdirectory)],
                        None,
                        ],
                'cmd1' : [
                        ['invertMisreg.py','-i','%s/misreg/azimuth/pairs/' % (jobcoreg.workdirectory),'-o','%s/misreg/azimuth/dates/' % (jobcoreg.workdirectory)],
                        None,
                        ],
                }

        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'IW')
        
        os.chdir(cur_dir)

        jobcoreg.timeseries_misreg['done']['value'] = True

        return jobcoreg 

################################################################################
## fullBurst_geo2rdr FUNCTION
################################################################################
def fullBurst_geo2rdr(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """fullBurst_geo2rdr

        The function will ..., from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,fullBurst_geo2rdr.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,fullBurst_geo2rdr.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,fullBurst_geo2rdr.__name__,__file__,__copyright__,'Coregistration Step: fullBurst_geo2rdr (Sentinel-1)',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.timeseries_misreg['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,overlap_resample.__name__,__file__,__copyright__,
                        'The previous step (timeseries_misreg) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'fullBurst_geo2rdr',gui=jobcoreg.gui)
        os.chdir(jobcoreg.workdirectory)

        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        with open('dates','r') as fi: 
                for line in fi:
                        dslc = line.strip()
                        if not dslc == jobcoreg.refdate:
                                if (not glob.glob('%s/coreg_secondarys/%s/IW*' % (jobcoreg.workdirectory,dslc))) or modeforce == True:
                                        usermessage.ezprint('Create the input card for ISCE-2: %s...' % (dslc),jobcoreg.log,verbose)

                                        with open(jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                                fout.write('[Common]\n')
                                                fout.write('##########################\n')
                                                fout.write('##########################\n')
                                                fout.write('[Function-1]\n')
                                                fout.write('geo2rdr :\n')
                                                fout.write('secondary : %s/secondarys/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('reference : %s/reference\n' % (jobcoreg.workdirectory))
                                                fout.write('geom_referenceDir : %s/geom_reference\n' % (jobcoreg.workdirectory))
                                                fout.write('coregSLCdir : %s/coreg_secondarys/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('overlap : False\n')
                                                fout.write('useGPU : %s\n' % (jobcoreg.fullBurst_geo2rdr['useGPU']['value']))
                                                fout.write('azimuth_misreg : %s/misreg/azimuth/dates/%s.txt\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('range_misreg : %s/misreg/range/dates/%s.txt\n' % (jobcoreg.workdirectory,dslc))

                                        dict_cmd['cmd%s' % (h)] = [ ['SentinelWrapper.py','-c',jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                                jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                        h = h + 1
                                else:
                                        usermessage.warningmsg(__name__,overlap_resample.__name__,__file__,'The files exist.',jobcoreg.log,verbose)

        ## Run ISCE-2
        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'IW')
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])
        
        os.chdir(cur_dir)

        jobcoreg.fullBurst_geo2rdr['done']['value'] = True

        return jobcoreg 

################################################################################
## fullBurst_resample FUNCTION
################################################################################
def fullBurst_resample(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """fullBurst_resample

        The function will ..., from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,fullBurst_resample.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,fullBurst_resample.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,fullBurst_resample.__name__,__file__,__copyright__,'Coregistration Step: fullBurst_resample (Sentinel-1)',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.fullBurst_geo2rdr['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,overlap_resample.__name__,__file__,__copyright__,
                        'The previous step (fullBurst_geo2rdr) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'fullBurst_resample',gui=jobcoreg.gui)
        os.chdir(jobcoreg.workdirectory)

        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        with open('dates','r') as fi: 
                for line in fi:
                        dslc = line.strip()
                        if not dslc == jobcoreg.refdate:
                                if (not glob.glob('%s/coreg_secondarys/%s/IW*/burst_*' % (jobcoreg.workdirectory,dslc))) or modeforce == True:
                                        usermessage.ezprint('Create the input card for ISCE-2: %s...' % (dslc),jobcoreg.log,verbose)

                                        with open(jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                                fout.write('[Common]\n')
                                                fout.write('##########################\n')
                                                fout.write('##########################\n')
                                                fout.write('[Function-1]\n')
                                                fout.write('resamp_withCarrier : \n')
                                                fout.write('secondary : %s/secondarys/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('reference : %s/reference\n' % (jobcoreg.workdirectory))
                                                fout.write('coregdir : %s/coreg_secondarys/%s\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('overlap : False\n')
                                                fout.write('azimuth_misreg : %s/misreg/azimuth/dates/%s.txt\n' % (jobcoreg.workdirectory,dslc))
                                                fout.write('range_misreg : %s/misreg/range/dates/%s.txt\n' % (jobcoreg.workdirectory,dslc))

                                        dict_cmd['cmd%s' % (h)] = [ ['SentinelWrapper.py','-c',jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                                jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                        h = h + 1
                                else:
                                        usermessage.warningmsg(__name__,fullBurst_resample.__name__,__file__,'The files exist.',jobcoreg.log,verbose)

        ## Run ISCE-2
        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'IW')
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])
        
        os.chdir(cur_dir)

        jobcoreg.fullBurst_resample['done']['value'] = True

        return jobcoreg 

################################################################################
## extract_stack_valid_region FUNCTION
################################################################################
def extract_stack_valid_region(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """extract_stack_valid_region

        The function will ..., from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,extract_stack_valid_region.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,extract_stack_valid_region.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,extract_stack_valid_region.__name__,__file__,__copyright__,'Coregistration Step: extract_stack_valid_region (Sentinel-1)',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.fullBurst_resample['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,overlap_resample.__name__,__file__,__copyright__,
                        'The previous step (fullBurst_resample) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'extract_stack_valid_region',gui=jobcoreg.gui)
        os.chdir(jobcoreg.workdirectory)

        ## Run ISCE-2
        dict_cmd = {
                'cmd0' : [
                        ['extractCommonValidRegion.py','-m','%s/reference' % (jobcoreg.workdirectory),'-s','%s/coreg_secondarys' % (jobcoreg.workdirectory)],
                        None,
                        ],
                }

        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'IW')
        
        os.chdir(cur_dir)

        jobcoreg.extract_stack_valid_region['done']['value'] = True

        return jobcoreg 

################################################################################
## merge_reference_secondary_slc FUNCTION
################################################################################
def merge_reference_secondary_slc(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """merge_reference_secondary_slc

        The function will ..., from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2coregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,merge_reference_secondary_slc.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,merge_reference_secondary_slc.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,merge_reference_secondary_slc.__name__,__file__,__copyright__,'Coregistration Step: merge_reference_secondary_slc (Sentinel-1)',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.extract_stack_valid_region['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,extract_stack_valid_region.__name__,__file__,__copyright__,
                        'The previous step (extract_stack_valid_region) is not done.',None))
        
        isce2log = isce2tools.createisce2log(jobcoreg.log,cur_dir,'merge_reference_secondary_slc',gui=jobcoreg.gui)
        os.chdir(jobcoreg.workdirectory)

        ## Create the input cards and the job
        list_file = []
        with open('dates','r') as fi: 
                for line in fi:
                        list_file.append(line.strip())
        list_file = list_file + ['lat','lon','los','hgt','shadowMask','incLocal']

        h = 0
        dict_cmd = {}
        for li in list_file:

                if (li in ['lat','lon','los','hgt','shadowMask','incLocal']):
                        testpath = '%s/geom_reference/%s.rdr' % (jobcoreg.pathstack,li)
                else:
                        testpath = '%s/SLC/%s/%s.slc.hdr' % (jobcoreg.pathstack,li,li)

                if (not os.path.isfile(testpath)) or (modeforce == True):
                        usermessage.ezprint('Create the input card for ISCE-2: %s...' % (li),jobcoreg.log,verbose)

                        with open(jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                fout.write('[Common]\n')
                                fout.write('##########################\n')
                                fout.write('###################################\n')
                                fout.write('[Function-1]\n')
                                fout.write('mergeBursts : \n')
                                fout.write('stack : %s/stack\n' % (jobcoreg.workdirectory))

                                if li in ['lat','lon','los','hgt','shadowMask','incLocal']:
                                        fout.write('inp_reference : %s/reference\n' % (jobcoreg.workdirectory))
                                        fout.write('dirname : %s/geom_reference\n' % (jobcoreg.workdirectory))
                                        fout.write('name_pattern : %s*rdr\n' % (li))
                                        fout.write('outfile : %s/geom_reference/%s.rdr\n' % (jobcoreg.pathstack,li))
                                        fout.write('method : top\n')
                                        fout.write('aligned : False\n')
                                        fout.write('valid_only : False\n')
                                        fout.write('use_virtual_files : %s\n' % (jobcoreg.merge_reference_secondary_slc['use_virtual_files']['value']))
                                        fout.write('multilook : True\n')
                                        fout.write('range_looks : %s\n' % (jobcoreg.mlran))
                                        fout.write('azimuth_looks : %s\n' % (jobcoreg.mlazi))
                                        fout.write('multilook_tool : gdal\n')
                                        fout.write('no_data_value : 0\n')

                                elif li == jobcoreg.refdate:
                                        fout.write('inp_reference : %s/reference\n' % (jobcoreg.workdirectory))
                                        fout.write('dirname :%s/reference\n' % (jobcoreg.workdirectory))
                                        fout.write('name_pattern : burst*slc\n')
                                        fout.write('outfile : %s/SLC/%s/%s.slc\n' % (jobcoreg.pathstack,li,li))
                                        fout.write('method : top\n')
                                        fout.write('aligned : False\n')
                                        fout.write('valid_only : True\n')
                                        fout.write('use_virtual_files : %s\n' % (jobcoreg.merge_reference_secondary_slc['use_virtual_files']['value']))
                                        fout.write('multilook : False\n')
                                        fout.write('range_looks : %s\n' % (jobcoreg.mlran))
                                        fout.write('azimuth_looks : %s\n' % (jobcoreg.mlazi))

                                else:
                                        fout.write('inp_reference : %s/coreg_secondarys/%s\n' % (jobcoreg.workdirectory,li))
                                        fout.write('dirname : %s/coreg_secondarys/%s\n' % (jobcoreg.workdirectory,li))
                                        fout.write('name_pattern : burst*slc\n')
                                        fout.write('outfile : %s/SLC/%s/%s.slc\n' % (jobcoreg.pathstack,li,li))
                                        fout.write('method : top\n')
                                        fout.write('aligned : True\n')
                                        fout.write('valid_only : True\n')
                                        fout.write('use_virtual_files : %s\n' % (jobcoreg.merge_reference_secondary_slc['use_virtual_files']['value']))
                                        fout.write('multilook : False\n')
                                        fout.write('range_looks : %s\n' % (jobcoreg.mlran))
                                        fout.write('azimuth_looks : %s\n' % (jobcoreg.mlazi))
                        
                                dict_cmd['cmd%s' % (h)] = [ ['SentinelWrapper.py','-c',jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                        jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                
                                h = h + 1
                else:
                        usermessage.warningmsg(__name__,fullBurst_resample.__name__,__file__,'The file %s exist.' % (testpath),jobcoreg.log,verbose)

        ## Run ISCE-2
        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'IW')
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])

        os.chdir(cur_dir)

        jobcoreg.merge_reference_secondary_slc['done']['value'] = True

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

        if jobcoreg.merge_reference_secondary_slc['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,extract_stack_valid_region.__name__,__file__,__copyright__,
                        'The previous step (merge_reference_secondary_slc) is not done.',None))
        
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
                                        fout.write('reference : %s/reference/\n' % (jobcoreg.workdirectory))
                                        if not dslc == jobcoreg.refdate:
                                                fout.write('secondary : %s/secondarys/%s\n' % (jobcoreg.workdirectory,dslc))
                                        else:
                                                fout.write('secondary : %s/reference/\n' % (jobcoreg.workdirectory))
                                        fout.write('baseline_file : %s/baselines/%s/%s\n' % (jobcoreg.pathstack,dslc,dslc))

                                dict_cmd['cmd%s' % (h)] = [ ['SentinelWrapper.py','-c',jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                        jobcoreg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                
                                h = h + 1
                        else:
                                usermessage.warningmsg(__name__,grid_baseline.__name__,__file__,'The files exist.',jobcoreg.log,verbose)

        ## Run ISCE-2
        isce2tools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg,isce2log,'IW')
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])

        ## Create a link for consistency
        if constants.__ISCE2_modesymlink__ == True:
                try:
                        os.symlink(jobcoreg.workdirectory,
                                jobcoreg.pathstack+os.sep+'coreg',
                                target_is_directory = True)
                except:
                        usermessage.warningmsg(__name__,grid_baseline.__name__,__file__,'Impossible to create the symlink.',jobcoreg.log,verbose)
        else:
                # os.rename(jobcoreg.workdirectory,jobcoreg.pathstack+os.sep+'coreg')
                raise ValueError(usermessage.errormsg(__name__,grid_baseline.__name__,__file__,__copyright__,
                                'The symbolic links are required by ISCE-2 in the current version of EZ-InSAR.',jobcoreg.log))


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

        usermessage.openingmsg(__name__,grid_baseline.__name__,__file__,__copyright__,'Ifgstack Step: ifgnetwork (Sentinel-1)',log,verbose)

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
                                        with open('%s/baselines/%s_%s/%s_%s.txt' % (jobifg.pathstack+os.sep+'coreg',jobifg.refdate,dslci,jobifg.refdate,dslci),'r') as fi: 
                                                tmp = []
                                                for line in fi:
                                                        if 'Bperp (average):' in line.strip(): 
                                                                bperpi = float(line.strip().split(':')[-1]) 
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
## generate_burst_igram FUNCTION
################################################################################
def generate_burst_igram(jobifg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """generate_burst_igram

        The function will ..., from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2ifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,generate_burst_igram.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,generate_burst_igram.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))

        if not jobifg.log == None: 
                log = os.path.abspath(jobifg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,generate_burst_igram.__name__,__file__,__copyright__,'Ifgstack Step: generate_burst_igram (Sentinel-1)',log,verbose)

        if jobifg.ifgnetwork['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,generate_burst_igram.__name__,__file__,__copyright__,
                        'The previous step (ifgnetwork) is not done.',None))
        
        jobifg.check(verbose=False,mode='high')

        isce2log = isce2tools.createisce2log(jobifg.log,cur_dir,'generate_burst_igram',gui=jobifg.gui)
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
                                                fout.write('##########################\n')
                                                fout.write('###################################\n')
                                                fout.write('[Function-1]\n')
                                                fout.write('generateIgram : \n')
                                                if master == jobifg.refdate: 
                                                        fout.write('reference : %s/reference\n' % (jobifg.pathstack+os.sep+'coreg'))         
                                                else:
                                                        fout.write('reference : %s/coreg_secondarys/%s\n' % (jobifg.pathstack+os.sep+'coreg',master))
                                                if slave == jobifg.refdate: 
                                                        fout.write('secondary : %s/reference\n' % (jobifg.pathstack+os.sep+'coreg'))         
                                                else:
                                                        fout.write('secondary : %s/coreg_secondarys/%s\n' % (jobifg.pathstack+os.sep+'coreg',slave))
                                                fout.write('interferogram : %s/interferograms/%s_%s\n' % (jobifg.workdirectory,master,slave))
                                                fout.write('flatten : False\n')
                                                fout.write('interferogram_prefix : fine\n')
                                                fout.write('overlap : False\n')
                                                fout.write('###################################\n')

                                        dict_cmd['cmd%s' % (h)] = [ ['SentinelWrapper.py','-c',jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                                jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                        h = h + 1
                                else:
                                        usermessage.warningmsg(__name__,fullBurst_resample.__name__,__file__,'The files exist.',jobifg.log,verbose)

                ## Run ISCE-2
                isce2tools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg,isce2log,'IW')
                for keyi in list(dict_cmd.keys()):
                        if os.path.isfile(dict_cmd[keyi][1]):
                                os.remove(dict_cmd[keyi][1])

        else: 
                usermessage.ezprint('This step is not required for StaMPS.',jobifg.log,verbose)

        os.chdir(cur_dir)

        jobifg.generate_burst_igram['done']['value'] = True

        return jobifg 

################################################################################
## merge_burst_igram FUNCTION
################################################################################
def merge_burst_igram(jobifg, verbose: Optional[bool] = None, modeforce: Optional[bool] = True):
        """merge_burst_igram

        The function will ..., from an ``ezinsar.ifgstack``.   

        Args:
                jobifg (``ezinsar.ifgstack``): EZ-InSAR ifgstack job for ISCE-2 processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.ifgstack``: Return an EZ-InSAR ifgstack class
        
        """
        cur_dir = os.getcwd()

        if not 'isce2ifgstack.ifgstack' in str(type(jobifg)):
                raise ValueError(usermessage.errormsg(__name__,merge_burst_igram.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobifg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,merge_burst_igram.__name__,__file__,__copyright__,
                        'verbose','True or False',jobifg.log))

        if not jobifg.log == None: 
                log = os.path.abspath(jobifg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,merge_burst_igram.__name__,__file__,__copyright__,'Ifgstack Step: merge_burst_igram (Sentinel-1)',log,verbose)

        if jobifg.generate_burst_igram['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,merge_burst_igram.__name__,__file__,__copyright__,
                        'The previous step (generate_burst_igram) is not done.',None))
        
        jobifg.check(verbose=False,mode='high')

        isce2log = isce2tools.createisce2log(jobifg.log,cur_dir,'merge_burst_igram',gui=jobifg.gui)
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
                                                fout.write('##########################\n')
                                                fout.write('###################################\n')
                                                fout.write('[Function-1]\n')
                                                fout.write('mergeBursts : \n')
                                                fout.write('stack : %s/stack\n' % (jobifg.pathstack+os.sep+'coreg'))
                                                fout.write('inp_reference : %s/interferograms/%s_%s\n'  % (jobifg.workdirectory,master,slave))
                                                fout.write('dirname : %s/interferograms/%s_%s\n' % (jobifg.workdirectory,master,slave))
                                                fout.write('name_pattern : fine*int\n')
                                                fout.write('outfile : %s/interferograms/%s_%s/fine.int\n' % (jobifg.pathstack,master,slave))
                                                fout.write('method : top\n')
                                                fout.write('aligned : True\n')
                                                fout.write('valid_only : True\n')
                                                fout.write('use_virtual_files : True\n')
                                                fout.write('multilook : True\n')
                                                fout.write('range_looks : %s\n' % (jobifg.mlran))
                                                fout.write('azimuth_looks : %s\n' % (jobifg.mlazi))

                                        dict_cmd['cmd%s' % (h)] = [ ['SentinelWrapper.py','-c',jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                                jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                        h = h + 1
                                else:
                                        usermessage.warningmsg(__name__,fullBurst_resample.__name__,__file__,'The files exist.',jobifg.log,verbose)

                ## Run ISCE-2
                isce2tools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg,isce2log,'IW')
                for keyi in list(dict_cmd.keys()):
                        if os.path.isfile(dict_cmd[keyi][1]):
                                os.remove(dict_cmd[keyi][1])

        else: 
                usermessage.ezprint('This step is not required for StaMPS.',jobifg.log,verbose)

        os.chdir(cur_dir)

        jobifg.merge_burst_igram['done']['value'] = True

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

        usermessage.openingmsg(__name__,filter_coherence.__name__,__file__,__copyright__,'Ifgstack Step: filter_coherence (Sentinel-1)',log,verbose)

        if jobifg.merge_burst_igram['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,filter_coherence.__name__,__file__,__copyright__,
                        'The previous step (merge_burst_igram) is not done.',None))
        
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

                                if (not os.path.isfile('%s/interferograms/%s_%s/filt_fine.cor' % (jobifg.pathstack,master,slave))) or modeforce == True:
                                        usermessage.ezprint('Create the input card for ISCE-2: %s - %s...' % (master,slave),jobifg.log,verbose)

                                        with open(jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                                fout.write('[Common]\n')
                                                fout.write('##########################\n')
                                                fout.write('###################################\n')
                                                fout.write('[Function-1]\n')
                                                fout.write('FilterAndCoherence : \n')
                                                fout.write('input : %s/interferograms/%s_%s/fine.int\n' % (jobifg.pathstack,master,slave))
                                                fout.write('filt : %s/interferograms/%s_%s/filt_fine.int\n' % (jobifg.pathstack,master,slave))
                                                fout.write('coh : %s/interferograms/%s_%s/filt_fine.cor\n' % (jobifg.pathstack,master,slave))
                                                fout.write('strength : %s\n' % (jobifg.filter_coherence['strength']['value']))
                                                fout.write('slc1 : %s/SLC/%s/%s.slc.full\n' % (jobifg.pathstack,master,master))
                                                fout.write('slc2 : %s/SLC/%s/%s.slc.full\n' % (jobifg.pathstack,slave,slave))
                                                fout.write('complex_coh : %s/interferograms/%s_%s/fine.cor\n' % (jobifg.pathstack,master,slave))
                                                fout.write('range_looks : %s\n' % (jobifg.mlran))
                                                fout.write('azimuth_looks : %s\n' % (jobifg.mlazi))

                                        dict_cmd['cmd%s' % (h)] = [ ['SentinelWrapper.py','-c',jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                                jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                        h = h + 1
                                else:
                                        usermessage.warningmsg(__name__,filter_coherence.__name__,__file__,'The files exist.',jobifg.log,verbose)

                ## Run ISCE-2
                isce2tools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg,isce2log,'IW')
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

        usermessage.openingmsg(__name__,unwrap.__name__,__file__,__copyright__,'Ifgstack Step: unwrap (Sentinel-1)',log,verbose)

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

                                if (not os.path.isfile('%s/interferograms/%s_%s/filt_fine.cor' % (jobifg.pathstack,master,slave))) or modeforce == True:
                                        usermessage.ezprint('Create the input card for ISCE-2: %s - %s...' % (master,slave),jobifg.log,verbose)

                                        with open(jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 
                                                fout.write('[Common]\n')
                                                fout.write('##########################\n')
                                                fout.write('###################################\n')
                                                fout.write('[Function-1]\n')
                                                fout.write('unwrap : \n')
                                                fout.write('ifg : %s/interferograms/%s_%s/filt_fine.int\n' % (jobifg.pathstack,master,slave))
                                                fout.write('unw : %s/interferograms/%s_%s/filt_fine.unw\n' % (jobifg.pathstack,master,slave))
                                                fout.write('coh : %s/interferograms/%s_%s/filt_fine.cor\n' % (jobifg.pathstack,master,slave))
                                                fout.write('nomcf : %s\n' % (jobifg.unwrap['nomcf']['value']))
                                                fout.write('reference : %s/reference\n' % (jobifg.pathstack+os.sep+'coreg'))
                                                fout.write('defomax : 2\n')
                                                fout.write('rlks : %s\n' % (jobifg.mlran))
                                                fout.write('alks : %s\n' % (jobifg.mlazi))
                                                fout.write('rmfilter : False\n')
                                                fout.write('method : %s\n' % (jobifg.unwrap['method']['value']))

                                        dict_cmd['cmd%s' % (h)] = [ ['SentinelWrapper.py','-c',jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h)],
                                                jobifg.workdirectory+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                        h = h + 1
                                else:
                                        usermessage.warningmsg(__name__,unwrap.__name__,__file__,'The files exist.',jobifg.log,verbose)

                ## Run ISCE-2
                isce2tools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg,isce2log,'IW')
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

        usermessage.openingmsg(__name__,ifggeocoding.__name__,__file__,__copyright__,'Ifgstack Step: ifggeocoding (Sentinel-1)',log,verbose)

        if jobifg.merge_burst_igram['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,ifggeocoding.__name__,__file__,__copyright__,
                        'A previous step (merge_burst_igram) is not done.',None))
        
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
                                if os.path.isfile('%s/interferograms/%s_%s/filt_fine.int' % (jobifg.pathstack,master,slave)):
                                        list_file.append('%s/interferograms/%s_%s/filt_fine.int' % (jobifg.pathstack,master,slave))
                                        list_outfile.append(nametmp+'.diff.filt.geo.pha.tif')
                                elif os.path.isfile('%s/interferograms/%s_%s/fine.int' % (jobifg.pathstack,master,slave)):
                                        list_file.append('%s/interferograms/%s_%s/fine.int' % (jobifg.pathstack,master,slave))
                                        list_outfile.append(nametmp+'.diff.geo.pha.tif')

                                if os.path.isfile('%s/interferograms/%s_%s/filt_fine.unw' % (jobifg.pathstack,master,slave)):
                                        list_file.append('%s/interferograms/%s_%s/filt_fine.unw' % (jobifg.pathstack,master,slave))
                                        list_outfile.append(nametmp+'.unw.filt.geo.tif')
                                elif os.path.isfile('%s/interferograms/%s_%s/fine.unw' % (jobifg.pathstack,master,slave)):
                                        list_file.append('%s/interferograms/%s_%s/fine.unw' % (jobifg.pathstack,master,slave))
                                        list_outfile.append(nametmp+'.unw.geo.tif')

                                if os.path.isfile('%s/interferograms/%s_%s/filt_fine.cor' % (jobifg.pathstack,master,slave)):
                                        list_file.append('%s/interferograms/%s_%s/filt_fine.cor' % (jobifg.pathstack,master,slave))
                                        list_outfile.append(nametmp+'.cc.geo.tif')
                                elif os.path.isfile('%s/interferograms/%s_%s/fine.cor' % (jobifg.pathstack,master,slave)):
                                        list_file.append('%s/interferograms/%s_%s/fine.cor' % (jobifg.pathstack,master,slave))
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

                                geocoding.rdr2geotiff(
                                        fi,
                                        '%s/geom_reference/lat.rdr' % (jobifg.pathstack),
                                        '%s/geom_reference/lon.rdr' % (jobifg.pathstack),
                                        jobifg.workdirectory+os.sep+'geotiff'+os.sep+fout, 
                                        deltaLon,
                                        deltaLat,
                                        ROIpoly = poly,
                                        demradarfile = '%s/geom_reference/hgt.rdr' % (jobifg.pathstack),
                                        # shadowfile = '%s/geom_reference/shadowMask.rdr' % (jobifg.pathstack),
                                        uchar=jobifg.ifggeocoding['uchargeotiff']['value'],
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

        usermessage.openingmsg(__name__,finalstack.__name__,__file__,__copyright__,'Ifgstack Step: finalstack (Sentinel-1)',log,verbose)
        
        jobifg.check(verbose=False,mode='high')

        isce2log = isce2tools.createisce2log(jobifg.log,cur_dir,'finalstack',gui=jobifg.gui)

        ## For StaMPS
        if 'StaMPS' in jobifg.modestack: 
                usermessage.ezprint('Preparation of the StaMPS directory in %s' % (jobifg.finalstack['parentdirStaMPS']['value']+os.sep+'stack_stamps_'+jobifg.polarisation[0].lower()),jobifg.log,verbose)

                ## Cropping 
                if jobifg.finalstack['croppingforStaMPS']['value'] == True: 
                        os.chdir(jobifg.pathstack)

                        usermessage.ezprint('Cropping of the images:',jobifg.log,verbose)
                        usermessage.ezprint('Preparation of the command:',jobifg.log,verbose)

                        
                        if jobifg.pathstack.endswith("_cropped"):
                                jobifg.pathstack = jobifg.pathstack.replace('_cropped','')
                                newpathstack = jobifg.pathstack+'_cropped'
                        else:
                                newpathstack = jobifg.pathstack+'_cropped'

                        if os.path.isdir(newpathstack):
                                usermessage.warningmsg(__name__,finalstack.__name__,__file__,'The previous cropped stack will be deleted.',jobifg.log,verbose)
                                shutil.rmtree(newpathstack)
                        
                        if not os.path.isdir(newpathstack):
                                os.mkdir(newpathstack)

                        dict_cmd = {}
                        # cmdpath = [__file__.replace('eicomponents/processor/isce2module/isce2IWfunction.py','3rdparty/croppingstack_ISCE.csh')]
                        cmdpath = ['croppingstack_ISCE.csh']
                        cmdpath.append('1')
                        cmdpath.append(jobifg.pathstack)
                        cmdpath.append(newpathstack)
                        cmdpath.append(str(np.min(loads(jobifg.roi).exterior.xy[1])))
                        cmdpath.append(str(np.max(loads(jobifg.roi).exterior.xy[1])))
                        cmdpath.append(str(np.min(loads(jobifg.roi).exterior.xy[0])))
                        cmdpath.append(str(np.max(loads(jobifg.roi).exterior.xy[0])))
                        cmdpath.append('0')
                        dict_cmd['cmd0'] = [ cmdpath, None]
                                                
                        isce2tools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg,isce2log,'IW')

                        jobifg.pathstack = newpathstack

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

                if constants.__ISCE2_modesymlink__ == True:
                        dict_cmd['cmd0'] = [ ['make_single_reference_stack_isce','input_file'], 'input_file']                  
                else:
                        dict_cmd['cmd0'] = [ ['make_single_reference_stack_isce_cp','input_file'], 'input_file']    

                isce2tools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg,isce2log,'IW')

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

                        isce2tools.wrappersubprocess(dict_cmd,jobifg.computercores,jobifg,isce2log,'IW')


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

                if jobifg.satmode == 'IW':
                        jobtmp.load_data['load.metaFile']['value'] = jobifg.pathstack+os.sep+'coreg'+os.sep+'reference'+os.sep+'IW*.xml'
                else:
                        jobtmp.load_data['load.metaFile']['value'] = jobifg.pathstack+os.sep+'coreg'+os.sep+'slc_unpacked_crop'+os.sep+jobifg.refdate+os.sep+'*.xml'

                jobtmp.load_data['load.baselineDir']['value'] = jobifg.pathstack+os.sep+'coreg'+os.sep+'baselines'
                jobtmp.load_data['load.unwFile']['value'] = jobifg.pathstack+os.sep+'interferograms'+os.sep+'*'+os.sep+'filt*.unw'
                jobtmp.load_data['load.corFile']['value'] = jobifg.pathstack+os.sep+'interferograms'+os.sep+'*'+os.sep+'filt*.cor'
                jobtmp.load_data['load.connCompFile']['value'] = jobifg.pathstack+os.sep+'interferograms'+os.sep+'*'+os.sep+'filt*.unw.conncomp'
                
                jobtmp.load_data['load.ionoFile']['value'] = 'None'
                jobtmp.load_data['load.intFile']['value'] = 'None'

                jobtmp.load_data['load.demFile']['value'] = jobifg.pathstack+os.sep+'geom_reference'+os.sep+'hgt.rdr'
                jobtmp.load_data['load.lookupYFile']['value'] = jobifg.pathstack+os.sep+'geom_reference'+os.sep+'lat.rdr'
                jobtmp.load_data['load.lookupXFile']['value'] = jobifg.pathstack+os.sep+'geom_reference'+os.sep+'lon.rdr'
                jobtmp.load_data['load.incAngleFile']['value'] = jobifg.pathstack+os.sep+'geom_reference'+os.sep+'los.rdr'
                jobtmp.load_data['load.azAngleFile']['value'] = jobifg.pathstack+os.sep+'geom_reference'+os.sep+'los.rdr'
                jobtmp.load_data['load.shadowMaskFile']['value'] = jobifg.pathstack+os.sep+'geom_reference'+os.sep+'shadowMask.rdr'

                if jobifg.satmode == 'IW':
                        jobtmp.load_data['load.waterMaskFile']['value'] = jobifg.pathstack+os.sep+'geom_reference'+os.sep+'waterMask.rdr'
                else:
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
                jobtmp.correct_unwrap_error['unwrapError.numSample']['value'] = '20'

                jobtmp.invert_network['networkInversion.weightFunc']['value'] = 'var'
                jobtmp.invert_network['networkInversion.maskDataset']['value'] = 'coherence'
                jobtmp.invert_network['networkInversion.maskThreshold']['value'] = '0.2'
                jobtmp.invert_network['networkInversion.minTempCoh']['value'] = '0.4'

                jobtmp.correct_troposphere['troposphericDelay.method']['value' ]= 'height_correlation'

                jobtmp.deramp['deramp']['value'] = 'linear'

                jobtmp.hdfeos5['save.hdfEos5']['value'] = 'yes'

                jobtmp.writecfg(file=jobifg.finalstack['parentdirMintPy']['value']+os.sep+'stack_mintpy_'+jobifg.polarisation[0].lower()+os.sep+'mintpy'+os.sep+'TSmintpyprocessing.cfg')
  
        os.chdir(cur_dir)

        jobifg.finalstack['done']['value'] = True

        return jobifg 