#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to process StripMap data with Doris processor 

The module allows to process StripMap data with Doris processor from an ``ezinsar.coregistration`` job. 
    
    (From `ezinsar` package)


Changelog:
        * 1.2.0: New checking of S1 orbit, Aug. 2025, Alexis Hrysiewicz
        * 1.1.0: Several changes, Feb. 2025, Alexis Hrysiewicz
                * Add the support of Sentinel-1 C and D
                * Start the support of RADARSAT-2 FQ and SQ imagery
                * Start the support of CSK HIMAGE imagery
                * Start the support of TSX/PAZ imagery (SM and SPT) imagery
                * Start the support of SAOCOM imagery (SM)
                * Fix the bug with format in extractimage
        * 1.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
from datetime import datetime
import os
import numpy as np
import glob
import datetime
from typing import Optional, Union
from matplotlib import path
import shutil
import jdcal
import copy
import subprocess
from scipy.interpolate import LinearNDInterpolator
from shapely.wkt import loads

from ezinsar import usermessage
from ezinsar import constants
from ezinsar.eicomponents.sensor.s1module import s1slctools, s1stacktools, s1orbits
from ezinsar.eicomponents.sensor.rsat2module import rsat2slctools, rsat2stacktools
from ezinsar.eicomponents.sensor.cskmodule import cskslctools, cskstacktools
from ezinsar.eicomponents.sensor.tsxmodule import tsxslctools, tsxstacktools

try: 
        from ezinsarsaocommodule import saocomslctools, saocomstacktools, importsaocom
except ImportError:  
        a = 'dummy'

from ezinsar.eicomponents.processor.dorismodule.sensors import S1stripmap
from ezinsar.eicomponents.processor.dorismodule import doristools

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Env variable 
################################################################################
createifg = True # can be [True, False]
"""bool: Create the interferograms for checking (can be True or False)
"""

################################################################################
## checkSLC FUNCTION
################################################################################
def checkSLC(jobcoreg, verbose: Optional[bool] = None):
        """Check the SLC files 

        The function checks the SLC files, from an ``ezinsar.coregistration`` job.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,checkSLC.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,checkSLC.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        usermessage.openingmsg(__name__,checkSLC.__name__,__file__,__copyright__,'Coregistration Step: checkSLC',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        ## Create the work directory
        if not os.path.isdir(jobcoreg.workdirectory):
                os.mkdir(jobcoreg.workdirectory)
        # os.chdir(jobcoreg.workdirectory)

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
                if jobcoreg.satellite == 'RSAT2':
                        filelist = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'RS2*'))
                elif jobcoreg.satellite == 'CSK':
                        filelist = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'CSK*'))
                elif jobcoreg.satellite in ['TSX','PAZ']:
                        filelist = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'TSX*') + glob.glob(jobcoreg.pathSLC+os.sep+'TDM*') + glob.glob(jobcoreg.pathSLC+os.sep+'PAZ*'))
                elif jobcoreg.satellite in ['SAOCOM']:
                        filelist = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'*SAR*'))

                for fi in filelist: 
                        if jobcoreg.satellite == 'RSAT2':
                                annot = rsat2slctools.detectRSAT2annotation(fi,jobcoreg.polarisation[0].upper())
                        elif jobcoreg.satellite == 'CSK':
                                annot = cskslctools.detectCSKannotation(fi,jobcoreg.polarisation[0].upper())
                        elif jobcoreg.satellite in ['TSX','PAZ']:
                                annot = tsxslctools.detectTSXannotationfromxml(fi,jobcoreg.polarisation[0].upper())
                        elif jobcoreg.satellite in ['SAOCOM']:
                                annot = saocomslctools.detectSAOCOMannotation(fi,jobcoreg.polarisation[0].upper())

                        for poli in jobcoreg.polarisation: 
                                if not poli.upper() in annot['data_xmli1']['polarisation']:
                                        raise ValueError(usermessage.errormsg(__name__,checkSLC.__name__,__file__,__copyright__,
                                                'The selected polarisation %s is not available in the SLC file.' % (poli.upper()),jobcoreg.log))
                                date.append(datetime.datetime.strptime(annot['data_xmli1']['startTime'].split('T')[0].replace('-',''), '%Y%m%d'))

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
        usermessage.ezprint('There are %d files for %d unique dates.\n' %(len(filelist),len(date)),jobcoreg.log,verbose) 

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
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,checkOrbit.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,checkOrbit.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        usermessage.openingmsg(__name__,checkOrbit.__name__,__file__,__copyright__,'Coregistration Step: checkOrbit',jobcoreg.log,verbose)

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
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,coarserefdate.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,coarserefdate.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        usermessage.openingmsg(__name__,coarserefdate.__name__,__file__,__copyright__,'Coregistration Step: coarserefdate',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.checkOrbit['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,coarserefdate.__name__,__file__,__copyright__,
                                'The previous step (checkOrbit) is not done.',None))

        if jobcoreg.satellite == 'S1': 

                date_ref, dates_SLC, Btempnorm, Bperpnorm = s1stacktools.commputecoarsenetwork(jobcoreg.pathSLC,jobcoreg.roi,jobcoreg.polarisation[0],
                        # pathorbit = jobcoreg.pathorbit,
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
                
        elif jobcoreg.satellite in ['TSX','PAZ']: 

                date_ref, dates_SLC, Btempnorm, Bperpnorm = tsxstacktools.commputecoarsenetworkSM(jobcoreg.pathSLC,jobcoreg.roi,
                        jobcoreg.polarisation[0],
                        DEM = jobcoreg.pathDEM+os.sep+jobcoreg.nameDEM,
                        figure = jobcoreg.workdirectory+os.sep+'coarse_ifg_network',
                        preref = None,
                        verbose = jobcoreg.verbose, 
                        log = jobcoreg.log, 
                        ) 
                
        elif jobcoreg.satellite in ['SAOCOM']: 

                date_ref, dates_SLC, Btempnorm, Bperpnorm = saocomstacktools.commputecoarsenetworkSM(jobcoreg.pathSLC,jobcoreg.roi,
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
## extractimage FUNCTION
################################################################################
def extractimage(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Extract the images from the original files

        The function extracts the images and converts them to the Doris format, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,extractimage.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,extractimage.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,extractimage.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = None

        usermessage.openingmsg(__name__,extractimage.__name__,__file__,__copyright__,'Coregistration Step: extractimage',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.coarserefdate['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,extractimage.__name__,__file__,__copyright__,
                        'The previous step (coarserefdate) is not done.',None))
        
        # Directory
        if not os.path.isdir(jobcoreg.workdirectory+os.sep+'slc'):
                os.mkdir(jobcoreg.workdirectory+os.sep+os.sep+'slc')
        os.chdir(jobcoreg.workdirectory+os.sep+'slc')

        # Create the zip list per date
        for di in doristools.readdatefile('..'+os.sep+'dates'):
                
                if (not os.path.isfile(jobcoreg.workdirectory+os.sep+'slc'+os.sep+'%s' % (di+'.'+jobcoreg.polarisation[0]+'.slc'))) or modeforce == True:
                        ## FOR SENTINEL-1
                        if jobcoreg.satellite == 'S1': 

                                SLCfile=np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'*'+di+'*.zip') + glob.glob(jobcoreg.pathSLC+os.sep+'*'+di+'*.SAFE'))[0] 

                                if di == jobcoreg.refdate: 
                                        mode = 'master'
                                else: 
                                        mode = 'slave'

                                S1stripmap.importS1SM(SLCfile,
                                        mode,
                                        jobcoreg.extractimage['applyorbit']['value'], 
                                        jobcoreg.pathorbit,
                                        di, 
                                        jobcoreg.workdirectory+os.sep+'slc', 
                                        jobcoreg.polarisation, 
                                        jobcoreg.modecropping, 
                                        jobcoreg.extractimage['calibration']['value'], 
                                        jobcoreg.roi,
                                        log,
                                        verbose)
                                
                        ## FOR SAOCOM
                        elif jobcoreg.satellite == 'SAOCOM': 

                                ## FILE named by using PROCESSING DATE...
                                filelist = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'*SAR*'))
                                SLCfile = None
                                for fi in filelist: 
                                        SAOCOMannoresults = saocomslctools.detectSAOCOMannotation(fi,jobcoreg.polarisation[0])
                                        dates1 = datetime.datetime.strptime(SAOCOMannoresults['data_xmli1']['startTime'].split('T')[0].replace('-',''), '%Y%m%d').strftime("%Y%m%d")

                                        if dates1 == di.split()[0]:
                                                SLCfile = fi 

                                print(SLCfile)

                                if di == jobcoreg.refdate: 
                                        mode = 'master'
                                else: 
                                        mode = 'slave'

                                for poli in jobcoreg.polarisation:
                                        importsaocom.importdoris(SLCfile,
                                                mode,
                                                di, 
                                                jobcoreg.workdirectory+os.sep+'slc', 
                                                poli, 
                                                jobcoreg.modecropping, 
                                                jobcoreg.roi,
                                                log,
                                                verbose)
                                
                        else: 
                                for poli in jobcoreg.polarisation: 

                                        if jobcoreg.satellite == 'RSAT2':
                                                annfile = glob.glob(jobcoreg.pathSLC+os.sep+'*'+di.split()[0]+'*'+os.sep+'product.xml')[0]
                                                lut_XML = glob.glob(jobcoreg.pathSLC+os.sep+'*'+di.split()[0]+'*'+os.sep+'lutSigma*')[0]
                                                rasterfile = glob.glob(jobcoreg.pathSLC+os.sep+'*'+di.split()[0]+'*'+os.sep+'imagery*'+poli.upper()+'*')[0]

                                        if jobcoreg.satellite == 'CSK':
                                                rasterfile = glob.glob(jobcoreg.pathSLC+os.sep+'*'+di.split()[0]+'*'+os.sep+'CSK*'+poli.upper()+'*.h5')[0]

                                        if jobcoreg.satellite in ['TSX','PAZ']:
                                                rasterfile = glob.glob(jobcoreg.pathSLC+os.sep+'*'+di.split()[0]+'*'+os.sep+'IMAGEDATA'+os.sep+'*'+poli.upper()+'*.cos')[0]
                                                annfile = glob.glob(jobcoreg.pathSLC+os.sep+'*'+di.split()[0]+'*'+os.sep+'*.xml')[0]

                                                # Change for PAZ
                                                if ('PAZ' in annfile.split(os.sep)[-1]) or (not jobcoreg.satmode == 'SM'): 
                                                        

                                                        shutil.copy(annfile,di+'.'+poli.lower()+'.leader.xml')
                                                        os.system("xmlstarlet edit -L -u '//level1Product/generalHeader/mission' -v 'TSX-1' %s" % (di+'.'+poli.lower()+'.leader.xml'))
                                                        os.system("xmlstarlet edit -L -u '//level1Product/productInfo/missionInfo/mission' -v 'TSX-1' %s" % (di+'.'+poli.lower()+'.leader.xml'))

                                                        annfile = di+'.'+poli.lower()+'.leader.xml'

                                        # Computation of cropping parameters
                                        if isinstance(jobcoreg.modecropping,list):
                                                                roff = jobcoreg.modecropping[0]
                                                                nr = jobcoreg.modecropping[1]
                                                                loff = jobcoreg.modecropping[2]
                                                                nl = jobcoreg.modecropping[3]

                                        elif jobcoreg.modecropping == 'auto': 
                                                             
                                                if jobcoreg.satellite == 'RSAT2':
                                                        tmpannot, tmporbit = rsat2slctools.read_RSAT2annotation_xml(annfile)
                                                elif jobcoreg.satellite == 'CSK':
                                                        tmpannot, tmporbit = cskslctools.read_CSKannotation(annfile)
                                                elif jobcoreg.satellite in ['TSX','PAZ']:
                                                        tmpannot, tmporbit = tsxslctools.read_TSXannotation_xml(annfile)

                                                interpline = LinearNDInterpolator(list(zip(tmpannot['longitude'], tmpannot['latitude'])), tmpannot['line'])
                                                interppixel = LinearNDInterpolator(list(zip(tmpannot['longitude'], tmpannot['latitude'])), tmpannot['pixel'])
                                                        
                                                coords = loads(jobcoreg.roi).exterior.xy
                                                lines = [interpline(np.min(coords[0]),np.min(coords[1])), 
                                                        interpline(np.max(coords[0]),np.min(coords[1])),
                                                        interpline(np.max(coords[0]),np.max(coords[1])),
                                                        interpline(np.min(coords[0]),np.max(coords[1]))]
                                                
                                                pixels = [interppixel(np.min(coords[0]),np.min(coords[1])), 
                                                        interppixel(np.max(coords[0]),np.min(coords[1])),
                                                        interppixel(np.max(coords[0]),np.max(coords[1])),
                                                        interppixel(np.min(coords[0]),np.max(coords[1]))]
                                                
                                                roff = int(np.min(pixels))
                                                nr = int(np.max(pixels) - np.min(pixels) + 1 )
                                                loff = int(np.min(lines))
                                                nl = int(np.max(lines) - np.min(lines) + 1 )

                                        dict_cmd = {}
                                        with open(jobcoreg.workdirectory+os.sep+'slc'+os.sep+'config_card_0.tmp','w') as fout: 

                                                fout.write('cc **********************************************************************\n')
                                                fout.write('c ***  Doris \inputfile *****\n')
                                                fout.write('c **********************************************************************\n')
                                                fout.write(' c\n')
                                                fout.write(' c\n')
                                                fout.write(' comment  ___general options___\n')
                                                fout.write(' c\n')
                                                fout.write('c SCREEN          debug                           // level of output to standard out\n')
                                                fout.write('SCREEN          info                           // level of output to standard out\n')
                                                fout.write('MEMORY          %s                             // MB\n' %(jobcoreg.computerRAM))
                                                fout.write('BEEP            error                            // level of beeping\n')
                                                fout.write('OVERWRITE                                       // overwrite existing files\n')
                                                fout.write('BATCH                                           // non-interactive\n')
                                                fout.write('c LISTINPUT OFF                                 // prevents copy of this file to log\n')
                                                fout.write('c\n')

                                                if di == jobcoreg.refdate: 
                                                        fout.write('PROCESS          m_readfiles\n')
                                                        fout.write('PROCESS          m_crop\n')
                                                else:
                                                        fout.write('PROCESS          s_readfiles\n')
                                                        fout.write('PROCESS          s_crop\n')

                                                fout.write('c                                              //\n')
                                                fout.write(' c                                              //\n')
                                                fout.write(' comment  ___the general io files___            //\n')
                                                fout.write(' c                                              //\n')
                                                if not jobcoreg.log == None:
                                                        fout.write('LOGFILE         %s                         // log file\n' % (log))
                                                if di == jobcoreg.refdate: 
                                                        fout.write('M_RESFILE       %s  // parameter file\n' % (di+'.'+poli.lower()+'.slc.res'))
                                                else: 
                                                        fout.write('S_RESFILE       %s                     // parameter file\n' % (di+'.'+poli.lower()+'.slc.res'))
                                                fout.write(' c                                              //\n')

                                                if di == jobcoreg.refdate: 
                                                        keymode = 'M'
                                                else: 
                                                        keymode = 'S'

                                                if jobcoreg.satellite == 'RSAT2':
                                                        fout.write('%s_IN_METHOD    RS2                                      \n' % (keymode))
                                                        fout.write('%s_IN_DAT       %s        // name of datafile\n' % (keymode,rasterfile))
                                                        fout.write('%s_IN_LEA       %s        // name of datafile   \n' % (keymode,annfile))  
                                                elif jobcoreg.satellite == 'CSK':
                                                        fout.write('%s_IN_METHOD    CSK                                      \n' % (keymode))
                                                        fout.write('%s_IN_DAT       %s        // name of datafile\n' % (keymode,rasterfile))
                                                elif jobcoreg.satellite in ['TSX','PAZ']:
                                                        fout.write('%s_IN_METHOD    TSX                                      \n' % (keymode))
                                                        fout.write('%s_IN_DAT       %s        // name of datafile\n' % (keymode,rasterfile))
                                                        fout.write('%s_IN_LEA       %s        // name of datafile   \n' % (keymode,annfile))  

                                                
                                                fout.write('%s_CROP_IN     %s        // name of datafile   \n' % (keymode,rasterfile))
                                                if not jobcoreg.modecropping == None: 
                                                        fout.write('%s_DBOW  %s %s %s %s  \n' % (keymode,loff,loff+nl,roff,roff+nr))
                                                fout.write('%s_CROP_OUT     %s        // name of datafile   \n' % (keymode,di+'.'+poli.lower()+'.slc'))

                                                fout.write('STOP\n')

                                        dict_cmd['cmd0'] = [ ['doris',jobcoreg.workdirectory+os.sep+'slc'+os.sep+'config_card_0.tmp'],
                                        jobcoreg.workdirectory+os.sep+'slc'+os.sep+'config_card_0.tmp']
                                        
                                        ## Run Doris
                                        doristools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                                        for keyi in list(dict_cmd.keys()):
                                                if os.path.isfile(dict_cmd[keyi][1]):
                                                        os.remove(dict_cmd[keyi][1])

                else:
                        usermessage.warningmsg(__name__,extractimage.__name__,__file__,'The files exist.',jobcoreg.log,verbose)

        ## Generate low-resolution images for checking
        paraimage = []
        listimage = []
        check_run = False
        for di in doristools.readdatefile('..'+os.sep+'dates'):
                for poli in jobcoreg.polarisation:
                        
                        if (not os.path.isfile(jobcoreg.workdirectory+os.sep+os.sep+'slc'+os.sep+di+'.'+poli.lower()+'.slc.ras')) or modeforce == True:
                                paraimage.append(doristools.readimagepara(jobcoreg.workdirectory+os.sep+os.sep+'slc'+os.sep+di+'.'+poli.lower()+'.slc.res'))
                                listimage.append(jobcoreg.workdirectory+os.sep+os.sep+'slc'+os.sep+di+'.'+poli.lower()+'.slc')
                                check_run = True 

        if check_run == True:  
                
                # For the format (same format for the whole of the stack) 
                if paraimage[0]['Data_output_format'] == 'complex_real4':
                        format = '-fcr4'
                else:
                        format = '-fci2'

                doristools.multilookimage(listimage,
                        'mag',
                        paraimage,
                        format,
                        jobcoreg.mlrandisplay,
                        jobcoreg.mlazidisplay,
                        log = log,
                        verbose = verbose)
                
                usermessage.warningmsg(__name__,extractimage.__name__,__file__,'The .ras images have been created in the slc directory. Please check them.',log,verbose)
                                
        os.chdir(cur_dir)

        jobcoreg.extractimage['done']['value'] = True

        return jobcoreg 

################################################################################
## refinerefdate FUNCTION
################################################################################
def refinerefdate(jobcoreg, verbose: Optional[bool] = None, modifyfiles: Optional[bool] = True):
        """Refine the best reference date

        The function recomputes the potential best reference image based on the files extracted by Doris, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modifyfiles (bool): modifyfiles [Default: `True`].

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class

        Notes: 
                If not similar, the ``refdat`` attributes will be modified.
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,refinerefdate.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,refinerefdate.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = 'log.out'

        if jobcoreg.refinerefdate['process']['value'] == True:  

                usermessage.openingmsg(__name__,refinerefdate.__name__,__file__,__copyright__,'Coregistration Step: refinerefdate',log,verbose)

                jobcoreg.check(verbose=False,mode='high')

                if jobcoreg.extractimage['done']['value'] == False:
                        raise ValueError(usermessage.errormsg(__name__,refinerefdate.__name__,__file__,__copyright__,
                                'The previous step (extractimage) is not done.',None))
        
                usermessage.ezprint('\tRun the doris programs to compute the InSAR network the reference image:...',jobcoreg.log,verbose)

                os.chdir(jobcoreg.workdirectory+os.sep+'slc')
                
                ## Create the input cards and the job
                h = 0
                dict_cmd = {}
                for di in doristools.readdatefile('..'+os.sep+'dates'):
                        dslc = di
                        if not dslc == jobcoreg.refdate:
                                if os.path.isfile(jobcoreg.refdate+'_'+dslc+'.tmpbase'):
                                        usermessage.warningmsg(__name__,refinerefdate.__name__,__file__,'EZ-InSAR will delete the previous file (%s).' % (jobcoreg.refdate+'_'+dslc+'.tmpbase'),jobcoreg.log,verbose)
                                        os.remove(jobcoreg.refdate+'_'+dslc+'.tmpbase')

                                with open(jobcoreg.workdirectory+os.sep+'slc'+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 

                                        fout.write('cc **********************************************************************\n')
                                        fout.write('c ***  Doris \inputfile *****\n')
                                        fout.write('c **********************************************************************\n')
                                        fout.write(' c\n')
                                        fout.write(' c\n')
                                        fout.write(' comment  ___general options___\n')
                                        fout.write(' c\n')
                                        fout.write('c SCREEN          debug                           // level of output to standard out\n')
                                        fout.write('SCREEN          info                           // level of output to standard out\n')
                                        fout.write('MEMORY          %s                             // MB\n' %(jobcoreg.computerRAM))
                                        fout.write('BEEP            error                            // level of beeping\n')
                                        fout.write('OVERWRITE                                       // overwrite existing files\n')
                                        fout.write('BATCH                                           // non-interactive\n')
                                        fout.write('c LISTINPUT OFF                                 // prevents copy of this file to log\n')
                                        fout.write('c\n')
                                        fout.write('PROCESS          COARSEORB\n')
                                
                                        fout.write('c                                              //\n')
                                        fout.write(' c                                              //\n')
                                        fout.write(' comment  ___the general io files___            //\n')
                                        fout.write(' c                                              //\n')
                                        fout.write('LOGFILE         %s                         // log file\n' % (log))
                                        fout.write('M_RESFILE       %s  // parameter file\n' % (jobcoreg.refdate+'.'+jobcoreg.polarisation[0].lower()+'.slc.res'))
                                        fout.write('S_RESFILE       %s                     // parameter file\n' % (dslc+'.'+jobcoreg.polarisation[0].lower()+'.slc.res'))
                                        fout.write('I_RESFILE       %s               // parameter file\n' % (jobcoreg.refdate+'_'+dslc+'.tmpbase'))
                                        fout.write('DUMPBASELINE    50 50\n')
                                        fout.write(' c                                              //\n')
                                        fout.write('STOP\n')
                                
                                dict_cmd['cmd%s' % (h)] = [ ['doris',jobcoreg.workdirectory+os.sep+'slc'+os.sep+'config_card_%s.tmp' % (h)],
                                        jobcoreg.workdirectory+os.sep+'slc'+os.sep+'config_card_%s.tmp' % (h)]
                                        
                                h = h + 1

                ## Run Doris
                doristools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                for keyi in list(dict_cmd.keys()):
                        if os.path.isfile(dict_cmd[keyi][1]):
                                os.remove(dict_cmd[keyi][1])
                        
                btemp = []
                bperp = []
                dates = []
                for dslc in doristools.readdatefile('..'+os.sep+'dates'):
                        if not dslc == jobcoreg.refdate: 
                                val = float(subprocess.check_output('grep "Bperp" '+jobcoreg.refdate+'_'+dslc+'.tmpbase'+" | awk 'END {print $3}'", shell=True, encoding="utf-8").strip())
                        else: 
                                val = 0

                        dates.append(dslc)
                        a = datetime.datetime.strptime(dslc, "%Y%m%d")
                        btemp.append(int(sum(jdcal.gcal2jd(a.year, a.month, a.day))))
                        bperp.append(val)

                bperp = (bperp - np.min(bperp)) / np.std(bperp)
                btemp = (btemp - np.min(btemp)) / np.std(btemp)

                baselines = np.array(bperp)
                datedays = np.array(btemp)
                meanbase = np.mean(bperp)
                meandays = np.mean(btemp)

                normdist = np.sqrt((baselines-meanbase)**2 + (datedays-meandays)**2)
                idxref = np.argmin(normdist)

                dateref = dates[idxref]

                usermessage.ezprint('The best potential date should be %s' % (dateref),jobcoreg.log,verbose)

                if (not jobcoreg.refdate == dateref) and (not jobcoreg.refdate == None): 
                        usermessage.warningmsg(__name__,refinerefdate.__name__,__file__,'The reference date is not the same used previously. We will modify the value.',jobcoreg.log,verbose)
                        
                        mod_ref = False
                        if jobcoreg.refinerefdate['bypassuser']['value'] == False: 
                                rep = input('Please confirm the modification of the reference date? [yes or no] => ')
                                
                                if rep in ['yes','y','1',1]: 
                                        mod_ref = True
                        else: 
                                mod_ref = True

                        if mod_ref == True: 

                                if modifyfiles == True:
                                        for poli in jobcoreg.polarisation[0]: 
                                                with open(jobcoreg.refdate+'.'+jobcoreg.polarisation[0].lower()+'.slc.res','r') as fi: 
                                                        lines = fi.readlines()
                                                for idx, li in enumerate(lines):
                                                        lines[idx] = li.replace('MASTER','SLAVE')
                                                for idx, li in enumerate(lines):
                                                        lines[idx] = li.replace('master','slave')
                                                for idx, li in enumerate(lines):
                                                        lines[idx] = li.replace('slave_timing','master_timing')
                                                with open(jobcoreg.refdate+'.'+jobcoreg.polarisation[0].lower()+'.slc.res','r') as fi: 
                                                        fi.write('%s' % (lines))

                                        jobcoreg.refdate = dateref
                                        for poli in jobcoreg.polarisation[0]: 
                                                with open(jobcoreg.refdate+'.'+jobcoreg.polarisation[0].lower()+'.slc.res','r') as fi: 
                                                        lines = fi.readlines()
                                                for idx, li in enumerate(lines):
                                                        lines[idx] = li.replace('SLAVE','MASTER')
                                                for idx, li in enumerate(lines):
                                                        lines[idx] = li.replace('slave','master')
                                                with open(jobcoreg.refdate+'.'+jobcoreg.polarisation[0].lower()+'.slc.res','r') as fi: 
                                                        fi.write('%s' % (lines))

                                else:
                                        jobcoreg.refdate = dateref

                for fi in glob.glob('*.tmpbase'):
                        os.remove(fi)

                jobcoreg.refinerefdate['done']['value'] = True

        else:
                usermessage.warningmsg(__name__,refinerefdate.__name__,__file__,'The processing is not activated.',log,verbose)
        
        jobcoreg.refinerefdate['done']['value'] = True
        os.chdir(cur_dir)

        return jobcoreg

################################################################################
## mastertiming FUNCTION
################################################################################
def mastertiming(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Master timing processing

        The function computes the master timing with Doris, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class

        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,mastertiming.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,mastertiming.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,mastertiming.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = 'log.out'

        if jobcoreg.mastertiming['process']['value'] == True:  

                usermessage.openingmsg(__name__,mastertiming.__name__,__file__,__copyright__,'Coregistration Step: mastertiming',log,verbose)

                jobcoreg.check(verbose=False,mode='high')

                if jobcoreg.extractimage['done']['value'] == False:
                        raise ValueError(usermessage.errormsg(__name__,mastertiming.__name__,__file__,__copyright__,
                                'The previous step (extractimage) is not done.',None))
        
                # Directory
                if not os.path.isdir(jobcoreg.workdirectory+os.sep+'sim'):
                        os.mkdir(jobcoreg.workdirectory+os.sep+os.sep+'sim')
                if not os.path.isdir(jobcoreg.workdirectory+os.sep+'dem'):
                        os.mkdir(jobcoreg.workdirectory+os.sep+os.sep+'dem')

                os.chdir(jobcoreg.workdirectory+os.sep+'slc')

                if doristools.checkprocess(jobcoreg.workdirectory+os.sep+'slc'+os.sep+jobcoreg.refdate+'.'+jobcoreg.polarisation[0].lower()+'.slc.res',
                        'sim_amplitude') == True or doristools.checkprocess(jobcoreg.workdirectory+os.sep+'slc'+os.sep+jobcoreg.refdate+'.'+jobcoreg.polarisation[0].lower()+'.slc.res',
                        'master_timing') == True:
                        if  modeforce == False:
                                usermessage.warningmsg(__name__,mastertiming.__name__,__file__,'The processing is already done (modeforce == False). Nothing can be done.',log,verbose)
                                return jobcoreg
                                ##### END OF THE PROCESS
                        else:
                                dict_tmp = dict()
                                dict_tmp['cmd%s' % (0)] = [ ['doris.rmstep.sh','master_timing','%s' % (jobcoreg.workdirectory+os.sep+'slc'+os.sep+jobcoreg.refdate+'.'+jobcoreg.polarisation[0].lower()+'.slc.res')],
                                None]
                                dict_tmp['cmd%s' % (1)] = [ ['doris.rmstep.sh','sim_amplitude','%s' % (jobcoreg.workdirectory+os.sep+'slc'+os.sep+jobcoreg.refdate+'.'+jobcoreg.polarisation[0].lower()+'.slc.res')],
                                None]
                                
                                doristools.wrappersubprocess(dict_tmp,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)

                ## Run Doris
                usermessage.ezprint('\tRun the doris programs to compute master timing:...',jobcoreg.log,verbose)

                dict_cmd = dict()
                with open('config_card_%s.tmp' % (0),'w') as f_temp: 
                        f_temp.write('c **********************************************************************\n')
                        f_temp.write('c ***  Doris \inputfile *****\n')
                        f_temp.write('c **********************************************************************\n')
                        f_temp.write('c\n')
                        f_temp.write('c\n')
                        f_temp.write('comment  ___general options___\n')
                        f_temp.write('c\n')
                        f_temp.write('c SCREEN          debug                         // level of output to standard out\n')
                        f_temp.write('SCREEN          info                          // level of output to standard out\n')
                        f_temp.write('MEMORY          %s                             // MB\n' %(jobcoreg.computerRAM))
                        f_temp.write('BEEP            error                		 // level of beeping\n')
                        f_temp.write('OVERWRITE                                       // overwrite existing files\n')
                        f_temp.write('BATCH                                           // non-interactive\n')
                        f_temp.write('PREVIEW ON                                 // prevents copy of this file to log\n')
                        f_temp.write('c\n')
                        f_temp.write('PROCESS          M_SIMAMP\n')
                        f_temp.write('PROCESS          M_TIMING\n')
                        f_temp.write('c                                               //\n')
                        f_temp.write('c                                              //\n')
                        f_temp.write('comment  ___the general io files___            //\n')
                        f_temp.write('c                                              //\n')
                        f_temp.write('LOGFILE         %s                      // log file\n' % (log))
                        f_temp.write('M_RESFILE       %s                     // parameter file\n' % (jobcoreg.workdirectory+os.sep+'slc'+os.sep+jobcoreg.refdate+'.'+jobcoreg.polarisation[0].lower()+'.slc.res'))
                        f_temp.write('c\n')
                        f_temp.write('comment ___SIMAMP___\n')
                        f_temp.write('c\n')

                        # Read the DEM parameters
                        paradem = doristools.readDEMpara(jobcoreg.pathDEM+os.sep+jobcoreg.nameDEM)

                        f_temp.write('SAM_IN_FORMAT   real4\n')
                        f_temp.write('SAM_IN_DEM      %s \n' % (jobcoreg.pathDEM+os.sep+jobcoreg.nameDEM))
                        f_temp.write('SAM_IN_SIZE     %d %d              // rows cols\n' % (paradem['lines'],paradem['samples']))
                        f_temp.write('SAM_IN_DELTA    %f %f    // in degrees       \n'  % (np.abs(paradem['deltalat']),np.abs(paradem['deltalon'])))
                        f_temp.write('SAM_IN_UL       %f %f     // lat and lon of upper left\n'% (paradem['lat'],paradem['lon']))
                        f_temp.write('SAM_IN_NODATA   %d\n' % (paradem['nodata']))
                        f_temp.write('SAM_OUT_FILE    ../sim/master_sam.raw // synthetic amplitude\n')
                        f_temp.write('SAM_OUT_DEM     ../dem/dem_radar.raw    // cropped DEM fo\n')
                        f_temp.write('c       ___                           ___\n')
                        f_temp.write('comment ___COMPUTE MASTER TIMING ERROR___\n')
                        f_temp.write('c\n')

                        if (jobcoreg.satmode in ['SL','HS','ST']) and (jobcoreg.mastertiming['MTE_METHOD']['value'] == 'magfft'):
                                raise ValueError(usermessage.errormsg(__name__,mastertiming.__name__,__file__,__copyright__,
                                'magfft is only compatible with StripMap-like data.',None))

                        f_temp.write('MTE_METHOD      %s         // computes faster than magspace\n' % (jobcoreg.mastertiming['MTE_METHOD']['value']))
                        f_temp.write('MTE_ACC        %s %s         // only for magspace\n' % (
                                jobcoreg.mastertiming['MTE_ACC_1']['value'],
                                jobcoreg.mastertiming['MTE_ACC_2']['value']))

                        f_temp.write('MTE_NWIN        %d             // number of large windows\n' % (jobcoreg.mastertiming['MTE_NWIN']['value']))
                        f_temp.write('MTE_INITOFF     %d %d            // initial offset\n' % (jobcoreg.mastertiming['MTE_INITOFF_1']['value'],
                                jobcoreg.mastertiming['MTE_INITOFF_2']['value']))
                        f_temp.write('MTE_WINSIZE     %d %d     // rectangular window\n' % (jobcoreg.mastertiming['MTE_WINSIZE_1']['value'],
                                jobcoreg.mastertiming['MTE_WINSIZE_2']['value']))
                        f_temp.write('c\n')
                        f_temp.write('STOP\n')  
                                        
                        dict_cmd['cmd%s' % (0)] = [ ['doris','config_card_%s.tmp' % (0)],
                                                'config_card_%s.tmp' % (0)]
                                                
                ## Run Doris
                doristools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                for keyi in list(dict_cmd.keys()):
                        if os.path.isfile(dict_cmd[keyi][1]):
                                os.remove(dict_cmd[keyi][1])

        else:
                usermessage.warningmsg(__name__,mastertiming.__name__,__file__,'The processing is not activated.',log,verbose)

        os.chdir(cur_dir)
        jobcoreg.mastertiming['done']['value'] = True

        return jobcoreg

################################################################################
## oversample FUNCTION
################################################################################
def oversample(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Oversample the SLCs

        The function will oversample the SLCs, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,oversample.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,oversample.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,oversample.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = 'log.out'

        if jobcoreg.oversample['process']['value'] == True:  

                usermessage.openingmsg(__name__,oversample.__name__,__file__,__copyright__,'Coregistration Step: oversample',log,verbose)

                jobcoreg.check(verbose=False,mode='high')

                if jobcoreg.extractimage['done']['value'] == False:
                        raise ValueError(usermessage.errormsg(__name__,oversample.__name__,__file__,__copyright__,
                                'The previous step (extractimage) is not done.',None))
        
                # Directory
                os.chdir(jobcoreg.workdirectory+os.sep+'slc')


                 ## Create the input cards and the job
                h = 0
                dict_cmd = {}
                for dslc in doristools.readdatefile('..'+os.sep+'dates'):
                        for poli in jobcoreg.polarisation:
                                check_process = True 

                                if doristools.checkprocess(jobcoreg.workdirectory+os.sep+'slc'+os.sep+dslc+'.'+poli.lower()+'.slc.res','oversample'): 
                                        if  modeforce == False:
                                                check_process = False

                                                ##### END OF THE PROCESS
                                        else:
                                                dict_tmp = dict()
                                                dict_tmp['cmd%s' % (0)] = [ ['doris.rmstep.sh','oversample','%s' % (jobcoreg.workdirectory+os.sep+'slc'+os.sep+dslc+'.'+poli.lower()+'.slc.res')],
                                                None]                                         
                                                doristools.wrappersubprocess(dict_tmp,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)

                                if check_process == True:
                                        if dslc == jobcoreg.refdate:
                                                mode = 'master'
                                                ext = 'M'
                                        else: 
                                                mode = 'slave'
                                                ext = 'S'

                                        with open(jobcoreg.workdirectory+os.sep+'slc'+os.sep+'config_card_%s.tmp' % (h),'w') as fout: 

                                                fout.write('cc **********************************************************************\n')
                                                fout.write('c ***  Doris \inputfile *****\n')
                                                fout.write('c **********************************************************************\n')
                                                fout.write(' c\n')
                                                fout.write(' c\n')
                                                fout.write(' comment  ___general options___\n')
                                                fout.write(' c\n')
                                                fout.write('c SCREEN          debug                           // level of output to standard out\n')
                                                fout.write('SCREEN          info                           // level of output to standard out\n')
                                                fout.write('MEMORY          %s                             // MB\n' %(jobcoreg.computerRAM))
                                                fout.write('BEEP            error                            // level of beeping\n')
                                                fout.write('OVERWRITE                                       // overwrite existing files\n')
                                                fout.write('BATCH                                           // non-interactive\n')
                                                fout.write('c LISTINPUT OFF                                 // prevents copy of this file to log\n')
                                                fout.write('c\n')

                                                if mode == 'master': 
                                                        fout.write('PROCESS          m_ovs\n')
                                                else: 
                                                        fout.write('PROCESS          s_ovs\n')
                                        
                                                fout.write('c                                              //\n')
                                                fout.write(' c                                              //\n')
                                                fout.write(' comment  ___the general io files___            //\n')
                                                fout.write(' c                                              //\n')
                                                fout.write('LOGFILE         %s                         // log file\n' % (log))

                                                if  mode == 'master': 
                                                        fout.write('M_RESFILE       %s  // parameter file\n' % (dslc+'.'+poli.lower()+'.slc.res'))
                                                else: 
                                                        fout.write('S_RESFILE       %s  // parameter file\n' % (dslc+'.'+poli.lower()+'.slc.res'))

                                                fout.write('c                                              //\n')
                                                fout.write('c\n')
                                                fout.write('c\n')
                                                fout.write('comment ___OVERSAMPLE___\n')
                                                fout.write('c\n')
                                                fout.write('%s_OVS_FACT_RNG      %d                       // range oversampling ratio\n' % (ext,jobcoreg.oversample['OVS_FACT_RNG']['value']))
                                                fout.write('%s_OVS_FACT_AZI      %d                        // azimuth oversampling ratio\n' % (ext,jobcoreg.oversample['OVS_FACT_AZI']['value']))
                                                fout.write('%s_OVS_KERNELSIZE    %d                       // interpolation kernel\n' % (ext,jobcoreg.oversample['OVS_KERNELSIZE']['value']))
                                                fout.write('%s_OVS_OUT_FORMAT    %s                      // image ci2 | cr4\n' % (ext,jobcoreg.oversample['OVS_OUT_FORMAT']['value']))
                                                fout.write('%s_OVS_OUT           %s                         // output filename \n' % (ext,dslc+'.'+poli.lower()+'.over.slc'))
                                                fout.write(' c                                              //\n')
                                                fout.write('STOP\n')
                                        
                                        dict_cmd['cmd%s' % (h)] = [ ['doris',jobcoreg.workdirectory+os.sep+'slc'+os.sep+'config_card_%s.tmp' % (h)],
                                                jobcoreg.workdirectory+os.sep+'slc'+os.sep+'config_card_%s.tmp' % (h)]
                                                
                                        h = h + 1

                                else: 
                                        usermessage.warningmsg(__name__,oversample.__name__,__file__,'The processing is already done for the date %s and polarisation %s (modeforce == False). Nothing can be done.' % (dslc,poli),log,verbose)

                ## Run Doris
                doristools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                for keyi in list(dict_cmd.keys()):
                        if os.path.isfile(dict_cmd[keyi][1]):
                                os.remove(dict_cmd[keyi][1])

                ## Generate low-resolution images for checking
                paraimage = []
                listimage = []
                check_run = False
                for di in doristools.readdatefile('..'+os.sep+'dates'):
                        for poli in jobcoreg.polarisation:

                                if (not os.path.isfile(jobcoreg.workdirectory+os.sep+os.sep+'slc'+os.sep+di+'.'+poli.lower()+'.over.slc.ras')) or modeforce == True:
                                        paraimage.append(doristools.readimagepara(jobcoreg.workdirectory+os.sep+os.sep+'slc'+os.sep+di+'.'+poli.lower()+'.slc.res'))
                                        listimage.append(jobcoreg.workdirectory+os.sep+os.sep+'slc'+os.sep+di+'.'+poli.lower()+'.over.slc')
                                        check_run = True 

                if check_run == True:                                 
                        doristools.multilookimage(listimage,
                                'mag',
                                paraimage,
                                '-fci2',
                                jobcoreg.mlrandisplay,
                                jobcoreg.mlazidisplay,
                                log = log,
                                verbose = verbose)
                        
                        usermessage.warningmsg(__name__,extractimage.__name__,__file__,'The .ras images have been created in the slc directory. Please check them.',log,verbose)

        else:
                usermessage.warningmsg(__name__,oversample.__name__,__file__,'The processing is not activated.',log,verbose)

        os.chdir(cur_dir)
        jobcoreg.oversample['done']['value'] = True

        return jobcoreg

################################################################################
## coarseoffset FUNCTION
################################################################################
def coarseoffset(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Compute the coarse offsets

        The function computes the coarse offsets, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,coarseoffset.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,coarseoffset.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,coarseoffset.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = 'log.out'

        usermessage.openingmsg(__name__,coarseoffset.__name__,__file__,__copyright__,'Coregistration Step: coarseoffset',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.extractimage['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,coarseoffset.__name__,__file__,__copyright__,
                        'The previous step (extractimage) is not done.',jobcoreg.log))
        
        # Directory
        os.chdir(jobcoreg.workdirectory+os.sep+'slc')

        if not os.path.isdir(jobcoreg.workdirectory+os.sep+'offset'):
                os.mkdir(jobcoreg.workdirectory+os.sep+os.sep+'offset')

        usermessage.warningmsg(__name__,coarseoffset.__name__,__file__,'Only the first polarisation will be used (i.e., %s)' % (jobcoreg.polarisation[0]),jobcoreg.log,verbose)

        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        for dslc in doristools.readdatefile('..'+os.sep+'dates'):
                if not dslc == jobcoreg.refdate:
                        if (not os.path.isfile('..'+os.sep+'offset'+os.sep+jobcoreg.refdate+'_'+jobcoreg.polarisation[0].lower()+'_'+dslc+'_'+jobcoreg.polarisation[0].lower()+'.ifg')) or modeforce == True:
                                usermessage.warningmsg(__name__,coarseoffset.__name__,__file__,'EZ-InSAR will try to delete the previous file (%s).' % ('..'+os.sep+'offset'+os.sep+jobcoreg.refdate+'_'+jobcoreg.polarisation[0].lower()+'_'+dslc+'_'+jobcoreg.polarisation[0].lower()+'.ifg'),jobcoreg.log,verbose)
                                if os.path.isfile('..'+os.sep+'offset'+os.sep+jobcoreg.refdate+'_'+jobcoreg.polarisation[0].lower()+'_'+dslc+'_'+jobcoreg.polarisation[0].lower()+'.ifg'):
                                        os.remove('..'+os.sep+'offset'+os.sep+jobcoreg.refdate+'_'+jobcoreg.polarisation[0].lower()+'_'+dslc+'_'+jobcoreg.polarisation[0].lower()+'.ifg')

                                with open(jobcoreg.workdirectory+os.sep+'slc'+os.sep+'config_card_%s.tmp' % (h),'w') as f_temp: 

                                        f_temp.write('cc **********************************************************************\n')
                                        f_temp.write('c ***  Doris \inputfile *****\n')
                                        f_temp.write('c **********************************************************************\n')
                                        f_temp.write(' c\n')
                                        f_temp.write(' c\n')
                                        f_temp.write(' comment  ___general options___\n')
                                        f_temp.write(' c\n')
                                        f_temp.write('c SCREEN          debug                           // level of output to standard out\n')
                                        f_temp.write('SCREEN          info                           // level of output to standard out\n')
                                        f_temp.write('MEMORY          %s                             // MB\n' %(jobcoreg.computerRAM))
                                        f_temp.write('BEEP            error                            // level of beeping\n')
                                        f_temp.write('OVERWRITE                                       // overwrite existing files\n')
                                        f_temp.write('BATCH                                           // non-interactive\n')
                                        f_temp.write('c LISTINPUT OFF                                 // prevents copy of this file to log\n')
                                        f_temp.write('c\n')

                                        if jobcoreg.coarseoffset['useorbit']['value'] == True: 
                                                f_temp.write('PROCESS          COARSEORB\n')

                                        f_temp.write('PROCESS          COARSECORR\n')
                                        f_temp.write('c                                              //\n')
                                        f_temp.write(' c                                              //\n')
                                        f_temp.write(' comment  ___the general io files___            //\n')
                                        f_temp.write(' c                                              //\n')
                                        f_temp.write('LOGFILE         %s                         // log file\n' % (log))

                                        f_temp.write('M_RESFILE       %s  // parameter file\n' % (jobcoreg.refdate+'.'+jobcoreg.polarisation[0].lower()+'.slc.res'))
                                        f_temp.write('S_RESFILE       %s  // parameter file\n' % (dslc+'.'+jobcoreg.polarisation[0].lower()+'.slc.res'))
                                        f_temp.write('I_RESFILE       %s  // parameter file\n' % ('..'+os.sep+'offset'+os.sep+jobcoreg.refdate+'_'+jobcoreg.polarisation[0].lower()+'_'+dslc+'_'+jobcoreg.polarisation[0].lower()+'.ifg'))

                                        f_temp.write('DUMPBASELINE    50 50\n')
                                        f_temp.write(' c                                              //\n')
                                        f_temp.write(' c\n')
                                        f_temp.write(' comment ___COARSE CORR (COREGISTRATION)___\n')
                                        f_temp.write(' c\n')

                                        if jobcoreg.satmode in ['ST','HS','ST'] and jobcoreg.coarseoffset['CC_METHOD']['value'] == 'magfft':
                                                raise ValueError(usermessage.errormsg(__name__,coarseoffset.__name__,__file__,__copyright__,
                                                        'The coarse coregistration method should be magspace for the Spotligh mode. ',jobcoreg.log))

                                        f_temp.write('CC_METHOD       %s                      // (no veclib)\n' % (jobcoreg.coarseoffset['CC_METHOD']['value']))
                                        f_temp.write('CC_ACC          %s %s                   // (only for magspace)\n' %(jobcoreg.coarseoffset['CC_ACC_1']['value'],jobcoreg.coarseoffset['CC_ACC_2']['value']))
                                        f_temp.write('CC_NWIN         %s                              // number of windows\n'%(jobcoreg.coarseoffset['CC_NWIN']['value']))
                                        f_temp.write('CC_WINSIZE      %s %s                     // size of windows\n' % (jobcoreg.coarseoffset['CC_WINSIZE_1']['value'],jobcoreg.coarseoffset['CC_WINSIZE_2']['value']))

                                        if jobcoreg.coarseoffset['useorbit']['value'] == True: 
                                                f_temp.write('CC_INITOFF      %s // use result of orbits for initial offset\n' % ('orbit'))
                                        else: 
                                                f_temp.write('CC_INITOFF      %s %s // use result of orbits for initial offset\n' % (jobcoreg.coarseoffset['CC_INITOFF_1']['value'],jobcoreg.coarseoffset['CC_INITOFF_2']['value']))

                                        f_temp.write('STOP\n')


                                dict_cmd['cmd%s' % (h)] = [ ['doris',jobcoreg.workdirectory+os.sep+'slc'+os.sep+'config_card_%s.tmp' % (h)],
                                        jobcoreg.workdirectory+os.sep+'slc'+os.sep+'config_card_%s.tmp' % (h)]

                                h = h + 1

                                
        if h > 0:
                ## Run Doris
                doristools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                for keyi in list(dict_cmd.keys()):
                        if os.path.isfile(dict_cmd[keyi][1]):
                                os.remove(dict_cmd[keyi][1])

        jobcoreg.coarseoffset['done']['value'] = True
        os.chdir(cur_dir)

        return jobcoreg

################################################################################
## filtazi FUNCTION
################################################################################
def filtazi(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Apply a filter in azimuth

        The function will apply a filter in azimuth (for the master and slaves), from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,filtazi.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,filtazi.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,filtazi.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = 'log.out'

        usermessage.openingmsg(__name__,filtazi.__name__,__file__,__copyright__,'Coregistration Step: filtazi',log,verbose)

        if jobcoreg.mastertiming['process']['value'] == True:  
                usermessage.warningmsg(__name__,filtazi.__name__,__file__,'This step is not implemented.',jobcoreg.log,verbose)
        else:
                usermessage.warningmsg(__name__,filtazi.__name__,__file__,'The processing is not activated.',log,verbose)

        jobcoreg.filtazi['process']['value'] == True
        os.chdir(cur_dir)

        return jobcoreg

################################################################################
## finecoreg FUNCTION
################################################################################
def finecoreg(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Compute the fine coregistration

        The function will the fine coregistration, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,finecoreg.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,finecoreg.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,finecoreg.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = 'log.out'

        usermessage.openingmsg(__name__,finecoreg.__name__,__file__,__copyright__,'Coregistration Step: finecoreg',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.coarseoffset['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,finecoreg.__name__,__file__,__copyright__,
                        'The previous step (coarseoffset) is not done.',jobcoreg.log))
        
        ## Run Doris
        usermessage.ezprint('\tRun the doris programs to apply a filtering in azimuth:...',jobcoreg.log,verbose)

        # Directory
        os.chdir(jobcoreg.workdirectory+os.sep+'slc')
        
        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        launch_doris = False

        usermessage.warningmsg(__name__,finecoreg.__name__,__file__,'Only the first polarisation will be used (i.e., %s)' % (jobcoreg.polarisation[0]),jobcoreg.log,verbose)

        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        for dslc in doristools.readdatefile('..'+os.sep+'dates'):
                if not dslc == jobcoreg.refdate:

                        offsetfile = '..'+os.sep+'offset'+os.sep+jobcoreg.refdate+'_'+jobcoreg.polarisation[0].lower()+'_'+dslc+'_'+jobcoreg.polarisation[0].lower()+'.ifg'
                        
                        if doristools.checkprocess(offsetfile,'fine_coreg') == True: 
                                if  modeforce == True :
                                        usermessage.warningmsg(__name__,finecoreg.__name__,__file__,'EZ-InSAR will try to delete the processing in the previous file (%s).' % (offsetfile),jobcoreg.log,verbose)

                                        dict_tmp = dict()
                                        dict_tmp['cmd%s' % (0)] = [ ['doris.rmstep.sh','fine_coreg','%s' % (offsetfile)],
                                                None]                                         
                                        doristools.wrappersubprocess(dict_tmp,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                                
                                        check_process = True 
                        else:
                                check_process = True 

                        # Create the cards
                        if check_process == True:
                                launch_doris = True
                                
                                with open('config_card_%s.tmp' % (h),'w') as f_temp: 
                                        f_temp.write('c **********************************************************************\n')
                                        f_temp.write('c ***  Doris \inputfile *****\n')
                                        f_temp.write('c **********************************************************************\n')
                                        f_temp.write('c\n')
                                        f_temp.write('c\n')
                                        f_temp.write('comment  ___general options___\n')
                                        f_temp.write('c\n')
                                        f_temp.write('c SCREEN          debug                         // level of output to standard out\n')
                                        f_temp.write('SCREEN          info                          // level of output to standard out\n')
                                        f_temp.write('MEMORY          %s                             // MB\n' %(jobcoreg.computerRAM))
                                        f_temp.write('BEEP            error                		 // level of beeping\n')
                                        f_temp.write('OVERWRITE                                       // overwrite existing files\n')
                                        f_temp.write('BATCH                                           // non-interactive\n')
                                        f_temp.write('PREVIEW ON                                 // prevents copy of this file to log\n')
                                        f_temp.write('c\n')

                                        f_temp.write('PROCESS          FINE\n')

                                        f_temp.write('c                                               //\n')
                                        f_temp.write('c                                              //\n')
                                        f_temp.write('comment  ___the general io files___            //\n')
                                        f_temp.write('c                                              //\n')
                                        f_temp.write('LOGFILE         %s                      // log file\n' % (log))
                                        f_temp.write('M_RESFILE       %s                     // parameter file\n' % (jobcoreg.workdirectory+os.sep+'slc'+os.sep+jobcoreg.refdate+'.'+jobcoreg.polarisation[0].lower()+'.slc.res'))
                                        f_temp.write('S_RESFILE       %s                     // parameter file\n' % (jobcoreg.workdirectory+os.sep+'slc'+os.sep+dslc+'.'+jobcoreg.polarisation[0].lower()+'.slc.res'))
                                        f_temp.write('I_RESFILE       %s                     // parameter file\n' % (offsetfile))
                                        f_temp.write('c\n')
                                        f_temp.write('comment ___FINE COREGISTRATION___\n')
                                        f_temp.write('c\n')

                                        f_temp.write(' c\n')
                                        if jobcoreg.satmode in ['ST','SL','ST'] and (not jobcoreg.finecoreg['FC_METHOD']['value'] == 'magspace'):
                                                raise ValueError(usermessage.errormsg(__name__,coarseoffset.__name__,__file__,__copyright__,
                                                        'The coarse coregistration method should be magspace for the Spotligh mode. ',jobcoreg.log))
                                        
                                        f_temp.write('FC_METHOD       %s                          //\n' % (jobcoreg.finecoreg['FC_METHOD']['value']))
                                        f_temp.write('FC_NWIN         %s                             // number of windows\n' % (jobcoreg.finecoreg['FC_NWIN']['value']))
                                        # f_temp.write('c FC_IN_POS       fc_pos.in                // file containing position of windows\n')
                                        f_temp.write('FC_WINSIZE      %s %s                           // size of windows\n' % (jobcoreg.finecoreg['FC_WINSIZE_1']['value'],jobcoreg.finecoreg['FC_WINSIZE_2']['value']))
                                        f_temp.write('FC_ACC          %s %s                             // search window, 2^n\n' % (jobcoreg.finecoreg['FC_ACC_1']['value'],jobcoreg.finecoreg['FC_ACC_2']['value']))

                                        if jobcoreg.finecoreg['usecoarseoff']['value'] == True: 
                                                f_temp.write('FC_INITOFF      coarsecorr                      // use result of coarse to compute first\n')
                                        else:
                                                f_temp.write('FC_INITOFF      %s %s                      // use result of coarse to compute first\n'% (jobcoreg.finecoreg['FC_INITOFF_1']['value'],jobcoreg.finecoreg['FC_INITOFF_2']['value']))

                                        f_temp.write('FC_OSFACTOR     %s                              // oversampling factor\n '% (jobcoreg.finecoreg['FC_OSFACTOR']['value']))
                                        
                                        # f_temp.write('c FC_PLOT         0.65 BG\n')
                                        f_temp.write('c\n')
                                        f_temp.write('STOP\n')  
                                                        
                                        dict_cmd['cmd%s' % (h)] = [ ['doris','config_card_%s.tmp' % (h)],
                                                                'config_card_%s.tmp' % (h)]

                                h = h + 1

                        else: 
                                usermessage.warningmsg(__name__,finecoreg.__name__,__file__,'The processing is already done for the date %s (modeforce == False). Nothing can be done.' % (dslc),log,verbose)
                
        ## Run Doris
        if launch_doris == True:
                doristools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                for keyi in list(dict_cmd.keys()):
                        if os.path.isfile(dict_cmd[keyi][1]):
                                os.remove(dict_cmd[keyi][1])

        os.chdir(cur_dir)

        jobcoreg.finecoreg['done']['value'] = True

        return jobcoreg

################################################################################
## reltiming FUNCTION
################################################################################
def reltiming(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Compute the timing error for the slaves

        The function will compute the timing errors for the slaves, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,reltiming.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,reltiming.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,reltiming.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = 'log.out'

        usermessage.openingmsg(__name__,reltiming.__name__,__file__,__copyright__,'Coregistration Step: reltiming',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.finecoreg['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,reltiming.__name__,__file__,__copyright__,
                        'The previous step (finecoreg) is not done.',jobcoreg.log))
        
        if jobcoreg.reltiming['process']['value'] == True:

                ## Run Doris
                usermessage.ezprint('\tRun the doris programs to compute the timing errors:...',jobcoreg.log,verbose)

                # Directory
                os.chdir(jobcoreg.workdirectory+os.sep+'slc')
                
                ## Create the input cards and the job
                h = 0
                dict_cmd = {}
                launch_doris = False

                usermessage.warningmsg(__name__,finecoreg.__name__,__file__,'Only the first polarisation will be used (i.e., %s)' % (jobcoreg.polarisation[0]),jobcoreg.log,verbose)

                ## Create the input cards and the job
                h = 0
                dict_cmd = {}
                for dslc in doristools.readdatefile('..'+os.sep+'dates'):
                        if not dslc == jobcoreg.refdate:

                                offsetfile = '..'+os.sep+'offset'+os.sep+jobcoreg.refdate+'_'+jobcoreg.polarisation[0].lower()+'_'+dslc+'_'+jobcoreg.polarisation[0].lower()+'.ifg'
                                
                                if doristools.checkprocess(offsetfile,'timing_error') == True: 
                                        if  modeforce == True :
                                                usermessage.warningmsg(__name__,finecoreg.__name__,__file__,'EZ-InSAR will try to delete the processing in the previous file (%s).' % (offsetfile),jobcoreg.log,verbose)

                                                dict_tmp = dict()
                                                dict_tmp['cmd%s' % (0)] = [ ['doris.rmstep.sh','timing_error','%s' % (offsetfile)],
                                                        None]                                         
                                                doristools.wrappersubprocess(dict_tmp,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                                
                                                check_process = True 
                                else:
                                        check_process = True 

                                # Create the cards
                                if check_process == True:
                                        launch_doris = True
                                        
                                        with open('config_card_%s.tmp' % (h),'w') as f_temp: 
                                                f_temp.write('c **********************************************************************\n')
                                                f_temp.write('c ***  Doris \inputfile *****\n')
                                                f_temp.write('c **********************************************************************\n')
                                                f_temp.write('c\n')
                                                f_temp.write('c\n')
                                                f_temp.write('comment  ___general options___\n')
                                                f_temp.write('c\n')
                                                f_temp.write('c SCREEN          debug                         // level of output to standard out\n')
                                                f_temp.write('SCREEN          info                          // level of output to standard out\n')
                                                f_temp.write('MEMORY          %s                             // MB\n' %(jobcoreg.computerRAM))
                                                f_temp.write('BEEP            error                		 // level of beeping\n')
                                                f_temp.write('OVERWRITE                                       // overwrite existing files\n')
                                                f_temp.write('BATCH                                           // non-interactive\n')
                                                f_temp.write('PREVIEW ON                                 // prevents copy of this file to log\n')
                                                f_temp.write('c\n')

                                                f_temp.write('PROCESS          RELTIMING\n')

                                                f_temp.write('c                                               //\n')
                                                f_temp.write('c                                              //\n')
                                                f_temp.write('comment  ___the general io files___            //\n')
                                                f_temp.write('c                                              //\n')
                                                f_temp.write('LOGFILE         %s                      // log file\n' % (log))
                                                f_temp.write('M_RESFILE       %s                     // parameter file\n' % (jobcoreg.workdirectory+os.sep+'slc'+os.sep+jobcoreg.refdate+'.'+jobcoreg.polarisation[0].lower()+'.slc.res'))
                                                f_temp.write('S_RESFILE       %s                     // parameter file\n' % (jobcoreg.workdirectory+os.sep+'slc'+os.sep+dslc+'.'+jobcoreg.polarisation[0].lower()+'.slc.res'))
                                                f_temp.write('I_RESFILE       %s                     // parameter file\n' % (offsetfile))
                                                f_temp.write('c\n')
                                                f_temp.write('comment ___RELATIVE TIMING ERROR___\n')
                                                f_temp.write('c\n')

                                                f_temp.write('RTE_THRESHOLD     %s                              // oversampling factor\n '% (jobcoreg.reltiming['RTE_THRESHOLD']['value']))
                                                f_temp.write('RTE_MAXITER     %s                              // oversampling factor\n '% (jobcoreg.reltiming['RTE_MAXITER']['value']))
                                                f_temp.write('RTE_K_ALPHA     %s                              // oversampling factor\n '% (jobcoreg.reltiming['RTE_K_ALPHA']['value']))
                                                
                                                f_temp.write('c\n')
                                                f_temp.write('STOP\n')  
                                                                
                                                dict_cmd['cmd%s' % (h)] = [ ['doris','config_card_%s.tmp' % (h)],
                                                                        'config_card_%s.tmp' % (h)]

                                        h = h + 1

                                else: 
                                        usermessage.warningmsg(__name__,finecoreg.__name__,__file__,'The processing is already done for the date %s (modeforce == False). Nothing can be done.' % (dslc),log,verbose)
                                
                ## Run Doris
                if launch_doris == True:
                        doristools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                        for keyi in list(dict_cmd.keys()):
                                if os.path.isfile(dict_cmd[keyi][1]):
                                        os.remove(dict_cmd[keyi][1])

        else: 
                usermessage.warningmsg(__name__,reltiming.__name__,__file__,'The processing is not activated.',log,verbose)

        os.chdir(cur_dir)

        jobcoreg.reltiming['done']['value'] = True        

        return jobcoreg

################################################################################
## demassist FUNCTION
################################################################################
def demassist(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Refine the offsets based on a DEM

        The function will refine the offsets based on a DEM, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,demassist.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,demassist.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,demassist.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = 'log.out'

        usermessage.openingmsg(__name__,demassist.__name__,__file__,__copyright__,'Coregistration Step: demassist',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.finecoreg['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,demassist.__name__,__file__,__copyright__,
                        'The previous step (finecoreg) is not done.',jobcoreg.log))
        
        if jobcoreg.demassist['process']['value'] == True:

                ## Run Doris
                usermessage.ezprint('\tRun the doris programs to refine the offsets based on a DEM:...',jobcoreg.log,verbose)

                # Directory
                os.chdir(jobcoreg.workdirectory+os.sep+'slc')
                
                ## Create the input cards and the job
                h = 0
                dict_cmd = {}
                launch_doris = False

                usermessage.warningmsg(__name__,finecoreg.__name__,__file__,'Only the first polarisation will be used (i.e., %s)' % (jobcoreg.polarisation[0]),jobcoreg.log,verbose)

                ## Create the input cards and the job
                h = 0
                dict_cmd = {}
                for dslc in doristools.readdatefile('..'+os.sep+'dates'):
                        if not dslc == jobcoreg.refdate:

                                offsetfile = '..'+os.sep+'offset'+os.sep+jobcoreg.refdate+'_'+jobcoreg.polarisation[0].lower()+'_'+dslc+'_'+jobcoreg.polarisation[0].lower()+'.ifg'
                                
                                if doristools.checkprocess(offsetfile,'dem_assist') == True: 
                                        if  modeforce == True :
                                                usermessage.warningmsg(__name__,finecoreg.__name__,__file__,'EZ-InSAR will try to delete the processing in the previous file (%s).' % (offsetfile),jobcoreg.log,verbose)

                                                dict_tmp = dict()
                                                dict_tmp['cmd%s' % (0)] = [ ['doris.rmstep.sh','dem_assist','%s' % (offsetfile)],
                                                        None]                                         
                                                doristools.wrappersubprocess(dict_tmp,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                                
                                                check_process = True 
                                else:
                                        check_process = True 

                                # Create the cards
                                if check_process == True:
                                        launch_doris = True
                                        
                                        with open('config_card_%s.tmp' % (h),'w') as f_temp: 
                                                f_temp.write('c **********************************************************************\n')
                                                f_temp.write('c ***  Doris \inputfile *****\n')
                                                f_temp.write('c **********************************************************************\n')
                                                f_temp.write('c\n')
                                                f_temp.write('c\n')
                                                f_temp.write('comment  ___general options___\n')
                                                f_temp.write('c\n')
                                                f_temp.write('c SCREEN          debug                         // level of output to standard out\n')
                                                f_temp.write('SCREEN          info                          // level of output to standard out\n')
                                                f_temp.write('MEMORY          %s                             // MB\n' %(jobcoreg.computerRAM))
                                                f_temp.write('BEEP            error                		 // level of beeping\n')
                                                f_temp.write('OVERWRITE       on                                // overwrite existing files\n')
                                                f_temp.write('BATCH                                           // non-interactive\n')
                                                f_temp.write('PREVIEW ON                                 // prevents copy of this file to log\n')
                                                f_temp.write('c\n')

                                                f_temp.write('PROCESS          DEMASSIST\n')

                                                f_temp.write('c                                               //\n')
                                                f_temp.write('c                                              //\n')
                                                f_temp.write('comment  ___the general io files___            //\n')
                                                f_temp.write('c                                              //\n')
                                                f_temp.write('LOGFILE         %s                      // log file\n' % (log))
                                                f_temp.write('M_RESFILE       %s                     // parameter file\n' % (jobcoreg.workdirectory+os.sep+'slc'+os.sep+jobcoreg.refdate+'.'+jobcoreg.polarisation[0].lower()+'.slc.res'))
                                                f_temp.write('S_RESFILE       %s                     // parameter file\n' % (jobcoreg.workdirectory+os.sep+'slc'+os.sep+dslc+'.'+jobcoreg.polarisation[0].lower()+'.slc.res'))
                                                f_temp.write('I_RESFILE       %s                     // parameter file\n' % (offsetfile))
                                                f_temp.write('c\n')
                                                f_temp.write('comment ___step demassist__\n')
                                                f_temp.write('c\n')

                                                # Read the DEM parameters
                                                paradem = doristools.readDEMpara(jobcoreg.pathDEM+os.sep+jobcoreg.nameDEM)

                                                f_temp.write('DAC_IN_FORMAT   R4\n')
                                                f_temp.write('DAC_IN_DEM      %s \n' % (jobcoreg.pathDEM+os.sep+jobcoreg.nameDEM))
                                                f_temp.write('DAC_IN_SIZE     %d %d              // rows cols\n' % (paradem['lines'],paradem['samples']))
                                                f_temp.write('DAC_IN_DELTA    %f %f    // in degrees       \n'  % (np.abs(paradem['deltalat']),np.abs(paradem['deltalon'])))
                                                f_temp.write('DAC_IN_UL       %f %f     // lat and lon of upper left\n'% (paradem['lat'],paradem['lon']))
                                                f_temp.write('DAC_IN_NODATA   %d\n' % (paradem['nodata']))
                                                f_temp.write('DAC_OUT_DEM    ../dem/dem_dac.raw \n')
                                                f_temp.write('DAC_OUT_DEMI    ../dem/demi_dac.raw \n')
                                                f_temp.write('DAC_OUT_DEM_LP    ../dem/demLP_dac.raw \n')

                                                f_temp.write('c\n')
                                                f_temp.write('STOP\n')  
                                                                
                                                dict_cmd['cmd%s' % (h)] = [ ['doris','config_card_%s.tmp' % (h)],
                                                                        'config_card_%s.tmp' % (h)]

                                        h = h + 1

                                else: 
                                        usermessage.warningmsg(__name__,demassist.__name__,__file__,'The processing is already done for the date %s (modeforce == False). Nothing can be done.' % (dslc),log,verbose)
                        
                ## Run Doris
                if launch_doris == True:
                        doristools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                        for keyi in list(dict_cmd.keys()):
                                if os.path.isfile(dict_cmd[keyi][1]):
                                        os.remove(dict_cmd[keyi][1])

        else: 
                usermessage.warningmsg(__name__,demassist.__name__,__file__,'The processing is not activated.',log,verbose)

        os.chdir(cur_dir)
        jobcoreg.demassist['done']['value'] = True

        return jobcoreg

################################################################################
## coregpm FUNCTION
################################################################################
def coregpm(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Compute the offset model

        The function will compute the offset model, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,coregpm.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,coregpm.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,coregpm.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = 'log.out'

        usermessage.openingmsg(__name__,coregpm.__name__,__file__,__copyright__,'Coregistration Step: coregpm',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.finecoreg['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,coregpm.__name__,__file__,__copyright__,
                        'The previous step (finecoreg) is not done.',jobcoreg.log))
        
        ## Run Doris
        usermessage.ezprint('\tRun the doris programs to compute the offset model:...',jobcoreg.log,verbose)

        # Directory
        os.chdir(jobcoreg.workdirectory+os.sep+'slc')
        
        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        launch_doris = False

        usermessage.warningmsg(__name__,finecoreg.__name__,__file__,'Only the first polarisation will be used (i.e., %s)' % (jobcoreg.polarisation[0]),jobcoreg.log,verbose)

        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        for dslc in doristools.readdatefile('..'+os.sep+'dates'):
                if not dslc == jobcoreg.refdate:

                        offsetfile = '..'+os.sep+'offset'+os.sep+jobcoreg.refdate+'_'+jobcoreg.polarisation[0].lower()+'_'+dslc+'_'+jobcoreg.polarisation[0].lower()+'.ifg'
                        
                        if doristools.checkprocess(offsetfile,'comp_coregpm') == True: 
                                if  modeforce == True :
                                        usermessage.warningmsg(__name__,finecoreg.__name__,__file__,'EZ-InSAR will try to delete the processing in the previous file (%s).' % (offsetfile),jobcoreg.log,verbose)

                                        dict_tmp = dict()
                                        dict_tmp['cmd%s' % (0)] = [ ['doris.rmstep.sh','comp_coregpm','%s' % (offsetfile)],
                                                None]                                         
                                        doristools.wrappersubprocess(dict_tmp,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                        
                                        check_process = True 
                        else:
                                check_process = True 

                        # Create the cards
                        if check_process == True:
                                launch_doris = True
                                
                                with open('config_card_%s.tmp' % (h),'w') as f_temp: 
                                        f_temp.write('c **********************************************************************\n')
                                        f_temp.write('c ***  Doris \inputfile *****\n')
                                        f_temp.write('c **********************************************************************\n')
                                        f_temp.write('c\n')
                                        f_temp.write('c\n')
                                        f_temp.write('comment  ___general options___\n')
                                        f_temp.write('c\n')
                                        f_temp.write('c SCREEN          debug                         // level of output to standard out\n')
                                        f_temp.write('SCREEN          info                          // level of output to standard out\n')
                                        f_temp.write('MEMORY          %s                             // MB\n' %(jobcoreg.computerRAM))
                                        f_temp.write('BEEP            error                		 // level of beeping\n')
                                        f_temp.write('OVERWRITE                                       // overwrite existing files\n')
                                        f_temp.write('BATCH                                           // non-interactive\n')
                                        f_temp.write('PREVIEW ON                                 // prevents copy of this file to log\n')
                                        f_temp.write('c\n')

                                        f_temp.write('PROCESS          COREGPM\n')

                                        f_temp.write('c                                               //\n')
                                        f_temp.write('c                                              //\n')
                                        f_temp.write('comment  ___the general io files___            //\n')
                                        f_temp.write('c                                              //\n')
                                        f_temp.write('LOGFILE         %s                      // log file\n' % (log))
                                        f_temp.write('M_RESFILE       %s                     // parameter file\n' % (jobcoreg.workdirectory+os.sep+'slc'+os.sep+jobcoreg.refdate+'.'+jobcoreg.polarisation[0].lower()+'.slc.res'))
                                        f_temp.write('S_RESFILE       %s                     // parameter file\n' % (jobcoreg.workdirectory+os.sep+'slc'+os.sep+dslc+'.'+jobcoreg.polarisation[0].lower()+'.slc.res'))
                                        f_temp.write('I_RESFILE       %s                     // parameter file\n' % (offsetfile))
                                        f_temp.write('c\n')
                                        f_temp.write('comment ___COMPUTE COREGISTRATION PARAMETERS___\n')
                                        f_temp.write('c\n')

                                        f_temp.write('CPM_THRESHOLD      %s \n' % (jobcoreg.coregpm['CPM_THRESHOLD']['value']))
                                        f_temp.write('CPM_DEGREE      %s \n' % (jobcoreg.coregpm['CPM_DEGREE']['value']))
                                        f_temp.write('CPM_WEIGHT      %s \n' % (jobcoreg.coregpm['CPM_WEIGHT']['value']))
                                        f_temp.write('CPM_MAXITER      %s \n' % (jobcoreg.coregpm['CPM_MAXITER']['value']))

                                        f_temp.write('c\n')
                                        f_temp.write('STOP\n')  
                                                        
                                        dict_cmd['cmd%s' % (h)] = [ ['doris','config_card_%s.tmp' % (h)],
                                                                'config_card_%s.tmp' % (h)]

                                h = h + 1

                        else: 
                                usermessage.warningmsg(__name__,coregpm.__name__,__file__,'The processing is already done for the date %s (modeforce == False). Nothing can be done.' % (dslc),log,verbose)
                        
        ## Run Doris
        if launch_doris == True:
                doristools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                for keyi in list(dict_cmd.keys()):
                        if os.path.isfile(dict_cmd[keyi][1]):
                                os.remove(dict_cmd[keyi][1])

        os.chdir(cur_dir)
        jobcoreg.coregpm['done']['value'] = True

        return jobcoreg

################################################################################
## resample FUNCTION
################################################################################
def resample(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Resample the slaves

        The function will resample the slaves, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,resample.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,resample.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,resample.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = 'log.out'

        usermessage.openingmsg(__name__,resample.__name__,__file__,__copyright__,'Coregistration Step: resample',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.coregpm['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,resample.__name__,__file__,__copyright__,
                        'The previous step (coregpm) is not done.',jobcoreg.log))

        # Directory
        os.chdir(jobcoreg.workdirectory+os.sep+'slc')

        if not os.path.isdir(jobcoreg.workdirectory+os.sep+'rslc'): 
              os.mkdir(jobcoreg.workdirectory+os.sep+'rslc')
        
        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        launch_doris = False

        ## Copy the offset file for the secondary polarisation(s)
        usermessage.ezprint('\tCreate the offset files for the secondary polarisation(s) based on the first polarisation (%s):...' % (jobcoreg.polarisation[0]),jobcoreg.log,verbose)

        for dslc in doristools.readdatefile('..'+os.sep+'dates'):
                if not dslc == jobcoreg.refdate:
                        for idx, poli in enumerate(jobcoreg.polarisation): 
                                if not idx == 0: 
                                        usermessage.ezprint('\t\tProcess the date %s in %s polarisation' % (dslc,poli),jobcoreg.log,verbose)

                                        offsetfileinput = '..'+os.sep+'offset'+os.sep+jobcoreg.refdate+'_'+jobcoreg.polarisation[0].lower()+'_'+dslc+'_'+jobcoreg.polarisation[0].lower()+'.ifg'
                                        offsetfileoutput = '..'+os.sep+'offset'+os.sep+jobcoreg.refdate+'_'+poli.lower()+'_'+dslc+'_'+poli.lower()+'.ifg'

                                        with open(offsetfileinput,'r') as fin: 
                                                input = fin.readlines()
                                                output = []

                                                with open(offsetfileoutput,'w') as fout:
                                                        for li in input: 
                                                                a = li.replace(jobcoreg.polarisation[0],poli)
                                                                a = a.replace(jobcoreg.polarisation[0].lower(),poli.lower())
                                                                fout.write('%s' % (a)) 

        usermessage.ezprint('\t\tdone',jobcoreg.log,verbose)

        ## Run Doris
        usermessage.ezprint('\tRun the doris programs to resample the slaves:...',jobcoreg.log,verbose)

        ## Create the input cards and the job
        h = 0
        dict_cmd = {}
        listcopyin = []
        listcopyout = []
        check_process = False
        listprocess = {'master': [], 'slave': [],'offset': []}

        for dslc in doristools.readdatefile('..'+os.sep+'dates'):
        
                for poli in jobcoreg.polarisation: 

                        info_offsetfile = '..'+os.sep+'offset'+os.sep+jobcoreg.refdate+'_'+poli.lower()+'_'+dslc+'_'+poli.lower()+'.ifg'
                        info_masterfile = jobcoreg.refdate+'.'+poli.lower()+'.slc.res'
                        info_slavefile = dslc+'.'+poli.lower()+'.slc.res'

                        masterfile = jobcoreg.refdate+'.'+poli.lower()+'.slc'
                        slavefile = dslc+'.'+poli.lower()+'.slc'

                        masterfile_res = '..'+os.sep+'rslc'+os.sep+jobcoreg.refdate+'.'+poli.lower()+'.rslc'
                        slavefile_res = '..'+os.sep+'rslc'+os.sep+dslc+'.'+poli.lower()+'.rslc'

                        info_masterfile_res = '..'+os.sep+'rslc'+os.sep+jobcoreg.refdate+'.'+poli.lower()+'.rslc.res'
                        info_slavefile_res = '..'+os.sep+'rslc'+os.sep+dslc+'.'+poli.lower()+'.rslc.res'
                                
                        if not dslc == jobcoreg.refdate:
                                if doristools.checkprocess(info_slavefile,'resample') == True: 
                                        if  modeforce == True :
                                                usermessage.warningmsg(__name__,resample.__name__,__file__,'EZ-InSAR will try to delete the processing in the previous file (%s).' % (info_slavefile),jobcoreg.log,verbose)

                                                dict_tmp = dict()
                                                dict_tmp['cmd%s' % (0)] = [ ['doris.rmstep.sh','resample','%s' % (info_slavefile)],
                                                        None]                                         
                                                doristools.wrappersubprocess(dict_tmp,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                                
                                                check_process = True 
                                else:
                                        check_process = True 

                                # Create the cards
                                if check_process == True:
                                        launch_doris = True

                                        listcopyin.append(info_slavefile)
                                        listcopyout.append(info_slavefile_res)

                                        listprocess['master'].append(info_masterfile_res.split(os.sep)[-1])
                                        listprocess['slave'].append(info_slavefile_res.split(os.sep)[-1])
                                        listprocess['offset'].append(info_offsetfile)

                                        # Computatation of the frequency matrix for SPT-like imagery 
                                        if (jobcoreg.satmode in ['ST','SL','HS']) and (jobcoreg.satellite in ['TSX','PAZ']): 
                                                from ezinsar.eicomponents.processor.dorismodule.sensors import TSXspt

                                                tmp = doristools.readimagepara(dslc+'.'+poli.lower()+'.slc.res')
                                                nb_lines = tmp['Last_line (w.r.t. original_image)'] - tmp['First_line (w.r.t. original_image)']  + 1 
                                                nb_pixels = tmp['Last_pixel (w.r.t. original_image)'] - tmp['First_pixel (w.r.t. original_image)']  + 1 
                                                TSXspt.computefrqmatrixTSXSPT(dslc+'.'+poli.lower()+'.leader.xml',
                                                                        '..'+os.sep+'rslc'+os.sep+dslc+'.'+poli.lower()+'.frq.raw',
                                                                        nb_lines,
                                                                        nb_pixels,
                                                                        log=jobcoreg.log,
                                                                        verbose=verbose)
                                        
                                        with open('config_card_%s.tmp' % (h),'w') as f_temp: 
                                                f_temp.write('c **********************************************************************\n')
                                                f_temp.write('c ***  Doris \inputfile *****\n')
                                                f_temp.write('c **********************************************************************\n')
                                                f_temp.write('c\n')
                                                f_temp.write('c\n')
                                                f_temp.write('comment  ___general options___\n')
                                                f_temp.write('c\n')
                                                f_temp.write('c SCREEN          debug                         // level of output to standard out\n')
                                                f_temp.write('SCREEN          info                          // level of output to standard out\n')
                                                f_temp.write('MEMORY          %s                             // MB\n' %(jobcoreg.computerRAM))
                                                f_temp.write('BEEP            error                		 // level of beeping\n')
                                                f_temp.write('OVERWRITE                                       // overwrite existing files\n')
                                                f_temp.write('BATCH                                           // non-interactive\n')
                                                f_temp.write('PREVIEW ON                                 // prevents copy of this file to log\n')
                                                f_temp.write('c\n')

                                                f_temp.write('PROCESS          RESAMPLE\n')

                                                f_temp.write('c                                               //\n')
                                                f_temp.write('c                                              //\n')
                                                f_temp.write('comment  ___the general io files___            //\n')
                                                f_temp.write('c                                              //\n')
                                                f_temp.write('LOGFILE         %s                      // log file\n' % (log))
                                                f_temp.write('M_RESFILE       %s                     // parameter file\n' % (info_masterfile))
                                                f_temp.write('S_RESFILE       %s                     // parameter file\n' % (info_slavefile))
                                                f_temp.write('I_RESFILE       %s                     // parameter file\n' % (info_offsetfile))
                                                f_temp.write('c\n')
                                                f_temp.write('comment ___RESAMPLING SLAVE___\n')
                                                f_temp.write('c\n')

                                                if jobcoreg.satmode in ['ST','SL','HS'] and (not jobcoreg.resample['RS_METHOD']['value'] == 'cc6p_SP'):
                                                        raise ValueError(usermessage.errormsg(__name__,resample.__name__,__file__,__copyright__,
                                                        'The resample method should be cc6p_SP for the Spotligh mode. ',jobcoreg.log))
                                                
                                                if not jobcoreg.computerworkers == 1: 
                                                        raise ValueError(usermessage.errormsg(__name__,resample.__name__,__file__,__copyright__,
                                                        'The resample processing ins only compatible with 1 worker.',jobcoreg.log))
                                        
                                                f_temp.write('RS_METHOD      %s \n' % (jobcoreg.resample['RS_METHOD']['value']))
                                                f_temp.write('RS_OUT_FILE        %s \n' % (slavefile_res))
                                                f_temp.write('RS_OUT_FORMAT      %s \n' % (jobcoreg.resample['RS_OUT_FORMAT']['value']))
                                                f_temp.write('RS_SHIFTAZI      %s \n' % (jobcoreg.resample['RS_SHIFTAZI']['value']))

                                                f_temp.write('c\n')
                                                f_temp.write('STOP\n')  

                                        if (jobcoreg.satmode in ['ST','SL','HS']) and (jobcoreg.satellite in ['TSX','PAZ']):
                                                tmp = ['cp','../slc/%s.%s.leader.xml' % (dslc,poli.lower()),'leader_slave.xml',';',
                                                        'cp','../rslc/%s.%s.frq.raw' % (dslc,poli.lower()),'test.raw',';',
                                                        'doris','config_card_%s.tmp' % (h)]
                                        else:
                                                tmp = ['doris','config_card_%s.tmp' % (h)]

                                        dict_cmd['cmd%s' % (h)] = [ tmp,
                                                        'config_card_%s.tmp' % (h)]

                                        h = h + 1

                                else: 
                                        usermessage.warningmsg(__name__,resample.__name__,__file__,'The processing is already done for the date %s (modeforce == False). Nothing can be done.' % (dslc),log,verbose)

                        else: 
                                ## Copy the master files
                                shutil.copy(slavefile,slavefile_res)
                                ## Modification of the master naming
                                with open(info_slavefile,'r') as fin: 
                                                input = fin.readlines()
                                                output = []

                                                with open(info_slavefile_res,'w') as fout:
                                                        for li in input: 
                                                                a = li.replace('.slc','.rslc')
                                                                fout.write('%s' % (a)) 

        # Run Doris
        if launch_doris == True:
                doristools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                for keyi in list(dict_cmd.keys()):
                        if os.path.isfile(dict_cmd[keyi][1]):
                                os.remove(dict_cmd[keyi][1])

                # ## Copy the files 
                for a,b in zip(listcopyin,listcopyout):
                        shutil.copy(a,b)

                ## Create the inteferograms for checking 
                if createifg == True:
                        usermessage.ezprint('\tEZ-InSAR will quickly compute interferograms for checking. Only the .ras images will be saved. No corrections to topography and flat Earth will be processed.',jobcoreg.log,verbose)

                        os.chdir(jobcoreg.workdirectory+os.sep+'rslc')

                        dict_cmd = dict()
                        h = 0
                        for idx, master in enumerate(listprocess['master']):

                                with open('config_card_%s.tmp' % (h),'w') as f_temp: 
                                        f_temp.write('c **********************************************************************\n')
                                        f_temp.write('c ***  Doris \inputfile *****\n')
                                        f_temp.write('c **********************************************************************\n')
                                        f_temp.write('c\n')
                                        f_temp.write('c\n')
                                        f_temp.write('comment  ___general options___\n')
                                        f_temp.write('c\n')
                                        f_temp.write('c SCREEN          debug                         // level of output to standard out\n')
                                        f_temp.write('SCREEN          info                          // level of output to standard out\n')
                                        f_temp.write('MEMORY          %s                             // MB\n' %(jobcoreg.computerRAM))
                                        f_temp.write('BEEP            error                		 // level of beeping\n')
                                        f_temp.write('OVERWRITE                                       // overwrite existing files\n')
                                        f_temp.write('BATCH                                           // non-interactive\n')
                                        f_temp.write('PREVIEW ON                                 // prevents copy of this file to log\n')
                                        f_temp.write('c\n')

                                        f_temp.write('PROCESS          INTERFERO\n')

                                        f_temp.write('c                                               //\n')
                                        f_temp.write('c                                              //\n')
                                        f_temp.write('comment  ___the general io files___            //\n')
                                        f_temp.write('c                                              //\n')
                                        f_temp.write('LOGFILE         %s                      // log file\n' % (log))
                                        f_temp.write('M_RESFILE       %s                     // parameter file\n' % (listprocess['master'][idx]))
                                        f_temp.write('S_RESFILE       %s                     // parameter file\n' % (listprocess['slave'][idx]))
                                        f_temp.write('I_RESFILE       %s                     // parameter file\n' % (listprocess['offset'][idx]))
                                        f_temp.write('c\n')
                                        f_temp.write('comment ___interferogram generation___\n')
                                        f_temp.write('c\n')
                                
                                        f_temp.write('INT_OUT_CINT      %s\n' % (listprocess['offset'][idx].replace('.ifg','.cint')))
                                        f_temp.write('INT_MULTILOOK      1 1 \n')

                                        f_temp.write('c\n')
                                        f_temp.write('STOP\n')  
                                                        
                                dict_cmd['cmd%s' % (h)] = [ ['doris','config_card_%s.tmp' % (h)],
                                                                'config_card_%s.tmp' % (h)]

                                h = h + 1

                        # Run Doris 
                        if h > 0:                                
                                doristools.wrappersubprocess(dict_cmd,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)
                                for keyi in list(dict_cmd.keys()):
                                        if os.path.isfile(dict_cmd[keyi][1]):
                                                os.remove(dict_cmd[keyi][1])

                                ## Delete the unused files
                                for fi in glob.glob('interferogram*'):
                                        os.remove(fi)
                                
                                ## Create the multilooked images for checking
                                paraimage = []
                                listimage = []
                                listfout = []
                                for idx, master in enumerate(listprocess['master']):
                                        paraimage.append(doristools.readimagepara(listprocess['offset'][idx],mode='ifg'))
                                        listimage.append(listprocess['offset'][idx].replace('.ifg','.cint'))
                                        listfout.append(listprocess['offset'][idx].replace('.ifg','.cint.ras').replace('offset','rslc'))

                                doristools.multilookimage(listimage,
                                        'mixed',
                                        paraimage,
                                        '-fcr4',
                                        jobcoreg.mlrandisplay,
                                        jobcoreg.mlazidisplay,
                                        colormap = constants.__file__.replace('constants.py','tools%scolormap%scmap_sar.csv' % (os.sep,os.sep)),
                                        fout = listfout,
                                        log = log,
                                        verbose = verbose)

                                ## Modification of offset files
                                dict_tmp = dict()
                                hbis = 0
                                for idx, master in enumerate(listprocess['master']):
                                        dict_tmp['cmd%s' % (hbis)] = [ ['doris.rmstep.sh','interfero','%s' % (listprocess['offset'][idx])],
                                                None]                                         
                                        doristools.wrappersubprocess(dict_tmp,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)

                                ## Delete the unused files
                                for fi in glob.glob('../offset/*.cint'):
                                        os.remove(fi)

        os.chdir(cur_dir)
        jobcoreg.resample['done']['value'] = True

        return jobcoreg

################################################################################
## finalstack FUNCTION
################################################################################
def finalstack(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Finalise the coregistration stack

        The function will finalise the coregistration stakcs, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,finalstack.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,finalstack.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,finalstack.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = 'log.out'

        usermessage.openingmsg(__name__,finalstack.__name__,__file__,__copyright__,'Coregistration Step: finalstack',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.resample['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,finalstack.__name__,__file__,__copyright__,
                        'The previous step (resample) is not done.',jobcoreg.log))

        # Create the directories
        usermessage.ezprint('\tCreate the directories:...',jobcoreg.log,verbose)

        if not os.path.isdir(jobcoreg.pathstack):
                os.mkdir(jobcoreg.pathstack)

        for poli in jobcoreg.polarisation:
                if not os.path.isdir(jobcoreg.pathstack+os.sep+'rslc_'+poli.lower()):
                        os.mkdir(jobcoreg.pathstack+os.sep+'rslc_'+poli.lower())

        usermessage.ezprint('\t\tdone',jobcoreg.log,verbose)

        # Create the directories
        usermessage.ezprint('\tCopy the resampled slcs:...',jobcoreg.log,verbose)

        usermessage.warningmsg(__name__,finalstack.__name__,__file__,'The .res files for the master will be keept as original. This can create bugs if the user creates their own ifgstack job.',log,verbose)
        
        os.chdir(jobcoreg.workdirectory+os.sep+'rslc')

        for dslc in doristools.readdatefile('..'+os.sep+'dates'):

                for poli in jobcoreg.polarisation:

                        if (not os.path.isfile(jobcoreg.pathstack+os.sep+'rslc_'+poli.lower()+os.sep+dslc+'.'+poli.lower()+'.rslc.res')) or modeforce == True:

                                # copy the image
                                shutil.copy(dslc+'.'+poli.lower()+'.rslc',jobcoreg.pathstack+os.sep+'rslc_'+poli.lower()+os.sep+dslc+'.'+poli.lower()+'.rslc')
                                
                                # copy the res
                                shutil.copy(dslc+'.'+poli.lower()+'.rslc.res',jobcoreg.pathstack+os.sep+'rslc_'+poli.lower()+os.sep+dslc+'.'+poli.lower()+'.rslc.res')

        # Modification of the paths in the slave .res files
        for dslc in doristools.readdatefile('..'+os.sep+'dates'):
                if not dslc == jobcoreg.refdate:
                        for poli in jobcoreg.polarisation:

                                with open(jobcoreg.pathstack+os.sep+'rslc_'+poli.lower()+os.sep+dslc+'.'+poli.lower()+'.rslc.res','r') as fi:
                                        input = fi.readlines()

                                with open(jobcoreg.pathstack+os.sep+'rslc_'+poli.lower()+os.sep+dslc+'.'+poli.lower()+'.rslc.res','w') as fout:
                                        for li in input:
                                                a = li.replace('../rslc/','')
                                                fout.write('%s' % (a))
                                                
        ## Write the date files (based on the file in the pathstack directory, for conviency)
        list = glob.glob(jobcoreg.pathstack+os.sep+'rslc_'+jobcoreg.polarisation[0].lower()+os.sep+'*.rslc.res')
        date = []
        for di in list:
                date.append(di.split(os.sep)[-1].split('.')[0])
        date = np.sort(date)
        with open(jobcoreg.pathstack+os.sep+'rslc_'+jobcoreg.polarisation[0].lower()+os.sep+'dates','w') as fdate:
                for di in date:
                        fdate.write('%s\n' % (di))

        for idx, poli in enumerate(jobcoreg.polarisation):
                if not idx == 0:
                        shutil.copy(jobcoreg.pathstack+os.sep+'rslc_'+jobcoreg.polarisation[0].lower()+os.sep+'dates',
                                jobcoreg.pathstack+os.sep+'rslc_'+poli.lower()+os.sep+'dates')

        os.chdir(cur_dir)
        jobcoreg.finalstack['done']['value'] = True

        return jobcoreg

################################################################################
## cleanstack FUNCTION
################################################################################
def cleanstack(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Clean the coregistration stack

        The function will clean the coregistration stakcs, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,cleanstack.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,cleanstack.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,cleanstack.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = 'log.out'

        usermessage.openingmsg(__name__,cleanstack.__name__,__file__,__copyright__,'Coregistration Step: cleanstack',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.finalstack['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,cleanstack.__name__,__file__,__copyright__,
                        'The previous step (finalstack) is not done.',jobcoreg.log))

        usermessage.ezprint('\tClean the directories using the mode %s:...' % (jobcoreg.cleanstack['mode']['value']),jobcoreg.log,verbose)

        if jobcoreg.cleanstack['mode']['value']== 'all':
                shutil.rmtree(jobcoreg.workdirectory)

        elif jobcoreg.cleanstack['mode']['value']== 'update':

                for fi in glob.glob(jobcoreg.workdirectory+os.sep+'offset'+os.sep+'*.ifg'):
                        os.remove(fi)

                for fi in glob.glob(jobcoreg.workdirectory+os.sep+'slc'+os.sep+'*'):       
                        if not jobcoreg.refdate in fi:
                                os.remove(fi)

                for fi in glob.glob(jobcoreg.workdirectory+os.sep+'rslc'+os.sep+'*'):   
                        if (not jobcoreg.refdate in fi) or ('.cint' in fi):
                                os.remove(fi)

        elif jobcoreg.cleanstack['mode']['value']== False:

                usermessage.ezprint('\t\tNothing to do.',jobcoreg.log,verbose)

        usermessage.ezprint('\t\tdone.',jobcoreg.log,verbose)

        os.chdir(cur_dir)
        jobcoreg.cleanstack['done']['value'] = True

        return jobcoreg

################################################################################
## updatestack FUNCTION
################################################################################
def updatestack(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[Union[None,bool]] = None):
        """Update the coregistration stack

        The function will update the coregistration stack, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for Doris processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): modeforce [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'doriscoregistration.coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,updatestack.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,updatestack.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))
        
        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,updatestack.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))

        if not jobcoreg.log == None: 
                log = os.path.abspath(jobcoreg.log)
        else: 
                log = 'log.out'

        usermessage.openingmsg(__name__,updatestack.__name__,__file__,__copyright__,'Coregistration Step: updatestack',log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.finalstack['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,updatestack.__name__,__file__,__copyright__,
                        'The previous step (finalstack) is not done.',jobcoreg.log))

        ## Check the new dates
        usermessage.ezprint('\tCheck the new SAR available acquitions:...',jobcoreg.log,verbose)

        olddates = []
        with open(jobcoreg.pathstack+os.sep+'rslc_'+jobcoreg.polarisation[0].lower()+os.sep+'dates','r') as fi:
                for di in fi: 
                        olddates.append(di.strip())

        jobcoreg.run(step=['checkSLC'],verbose=False)

        newpotentialdates = []
        with open(jobcoreg.workdirectory+os.sep+'dates','r') as fi:
                for di in fi: 
                        newpotentialdates.append(di.strip()) 

        newdates = []
        for di in newpotentialdates:
                if not di in olddates:
                      newdates.append(di)

        usermessage.ezprint('\t\tThe new potential dates are %s.' % (newdates),jobcoreg.log,verbose)

        # Check the orbit files (for Sentinel-1)
        check_orbits = []

        for dslc in newdates:

                if jobcoreg.satellite == 'S1':
                        orbitlist=glob.glob(jobcoreg.pathorbit+os.sep+'*POEORB*.EOF')

                        # List of .zip
                        ziplist=np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'*'+dslc+'*.zip') + glob.glob(jobcoreg.pathSLC+os.sep+'*'+dslc+'*.SAFE'))

                        dateslcorbits1 = []
                        dateslcorbits2 = []
                        sat_list = []
                        for slci in ziplist:
                                datestr = slci.split('/')[-1].split('.')[0].split('_')[5].split('T')[0] #We convert the name of files to date string.
                                hourstr = slci.split('/')[-1].split('.')[0].split('_')[5].split('T')[1]
                                datestr1 = datestr +' '+hourstr[0]+hourstr[1]+':'+hourstr[2]+hourstr[3]+':'+hourstr[4]+hourstr[5]

                                datestr = slci.split('/')[-1].split('.')[0].split('_')[6].split('T')[0] #We convert the name of files to date string.
                                hourstr = slci.split('/')[-1].split('.')[0].split('_')[6].split('T')[1]
                                datestr2 = datestr +' '+hourstr[0]+hourstr[1]+':'+hourstr[2]+hourstr[3]+':'+hourstr[4]+hourstr[5]

                                dateslcorbits1.append(datetime.datetime.strptime(datestr1, '%Y%m%d %H:%M:%S')) #We add the date in string to our list of date.
                                dateslcorbits2.append(datetime.datetime.strptime(datestr2, '%Y%m%d %H:%M:%S')) #We add the date in string to our list of date.

                                if 'S1A' in slci:
                                        sat_list.append("S1A")
                                elif 'S1B' in slci:
                                        sat_list.append("S1B")

                        total_check = False
                        for i in range(len(dateslcorbits1)):
                                dslc1 = dateslcorbits1[i]
                                dslc2 = dateslcorbits2[i]
                                sati = sat_list[i]

                                for pi in orbitlist:
                                        if sati in pi: 
                                                orb_test = pi.split('V')[1].split('.')[0]
                                                d1 = datetime.datetime.strptime(orb_test.split('_')[0], "%Y%m%dT%H%M%S")
                                                d2 = datetime.datetime.strptime(orb_test.split('_')[1], "%Y%m%dT%H%M%S")
                                                if d1 <= dslc1 <= d2 and d1 <= dslc2 <= d2:
                                                        total_check = True

                        if total_check == True:
                                check_orbits.append(True)
                        else:
                                check_orbits.append(False)                    

                else: 
                        check_orbits.append(True)             

        if jobcoreg.updatestack['bypass_POD']['value'] == True:
                newdateschecked = newdates
        else:

                usermessage.ezprint('\t\tThe new dates will be checked regarding the availability of POD files',jobcoreg.log,verbose)

                newdateschecked = []

                for idx, ni in enumerate(newdates):
                        if check_orbits[idx] == True:
                                newdateschecked.append(ni)

        usermessage.ezprint('\t\tThe new dates are %s. They will be processed.' % (newdateschecked),jobcoreg.log,verbose)
        usermessage.ezprint('\t\tdone',jobcoreg.log,verbose)

        with open(jobcoreg.workdirectory+os.sep+'dates','w') as fout:
                for di in newdateschecked:
                        fout.write('%s\n' % (di))

        if len(newdateschecked) > 0: 

                ## Extraction of the new SLCs
                # jobcoreg = extractimage(jobcoreg, modeforce = jobcoreg.updatestack['force']['value'])

                ## Update the reference dates
                updateref = False
                if jobcoreg.updatestack['update_ref']['value'] == True:
                        os.rename(jobcoreg.workdirectory+os.sep+'dates',jobcoreg.workdirectory+os.sep+'datessave')

                        datesfull = np.sort(olddates+newdateschecked)
                        with open(jobcoreg.workdirectory+os.sep+'dates','w') as fout:
                                for dslc in datesfull:
                                        fout.write('%s\n' % (dslc))

                        for dslc in olddates:
                                if not dslc == jobcoreg.refdate:
                                        shutil.copy(jobcoreg.pathstack+os.sep+'rslc_'+jobcoreg.polarisation[0].lower()+os.sep+dslc+'.'+jobcoreg.polarisation[0].lower()+'.rslc.res',
                                        jobcoreg.workdirectory+os.sep+'slc'+os.sep+dslc+'.'+jobcoreg.polarisation[0].lower()+'.slc.res')

                        # Copy the job
                        jobbis = copy.deepcopy(jobcoreg)
                        jobbis.refinerefdate['bypassuser']['value'] = True
                        # Run the detection
                        jobbis = refinerefdate(jobbis, modifyfiles=False)

                        for dslc in olddates:
                                if not dslc == jobcoreg.refdate:
                                        os.remove(jobcoreg.workdirectory+os.sep+'slc'+os.sep+dslc+'.'+jobcoreg.polarisation[0].lower()+'.slc.res')

                        os.rename(jobcoreg.workdirectory+os.sep+'datessave',jobcoreg.workdirectory+os.sep+'dates')

                        if not jobcoreg.refdate == jobbis.refdate:
                                updateref = True 

                                oldref = jobcoreg.refdate 
                                newref = jobbis.refdate 

                                if not newref in newdateschecked: 

                                        usermessage.ezprint('\tThe new reference date will be %s (the old reference date was %s).' % (newref,oldref),jobcoreg.log,verbose)
                                        usermessage.ezprint('\tEZ-InSAR will import the slaves files as master files.', jobcoreg.log,verbose)

                                        for fi in glob.glob(jobcoreg.workdirectory+os.sep+'sim'+os.sep+'*.raw'): 
                                                os.remove(fi)

                                        for fi in glob.glob(jobcoreg.workdirectory+os.sep+'dem'+os.sep+'*.raw'): 
                                                os.remove(fi)     

                                        if not oldref in newdateschecked: 
                                                for fi in glob.glob(jobcoreg.workdirectory+os.sep+'slc'+os.sep+'*'+oldref+'*'): 
                                                        os.remove(fi) 

                                                for fi in glob.glob(jobcoreg.workdirectory+os.sep+'rslc'+os.sep+'*'+oldref+'*'): 
                                                        os.remove(fi)                

                                        # Modify the master file as slave
                                        for poli in jobcoreg.polarisation: 
                                                masterfile = jobcoreg.pathstack+os.sep+'rslc_'+poli.lower()+os.sep+oldref+'.'+poli.lower()+'.rslc.res'
                                        
                                                if doristools.checkprocess(masterfile,'sim_amplitude') or doristools.checkprocess(masterfile,'master_timing'): 
                                                        dict_tmp = dict()
                                        
                                                        dict_tmp['cmd%s' % (0)] = [ ['doris.rmstep.sh','master_timing','%s' % (masterfile)],
                                                                None]          
                                                        dict_tmp['cmd%s' % (1)] = [ ['doris.rmstep.sh','sim_amplitude','%s' % (masterfile)],
                                                                None]                                
                                                        doristools.wrappersubprocess(dict_tmp,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)

                                                with open(masterfile,'r') as fi: 
                                                        master = fi.readlines()

                                                slave = []
                                                for li in master:
                                                        a = li.replace('MASTER','SLAVE') 
                                                        a = a.replace('master','slave') 
                                                        slave.append(a)

                                                with open(masterfile,'w') as fout: 
                                                        for li in slave: 
                                                                fout.write('%s' % (li))

                                                para = doristools.readimagepara(masterfile,mode='slc')
                                                
                                                with open(masterfile,'a') as fout: 
                                                        fout.write(' \n')
                                                        fout.write(' \n')
                                                        fout.write(' \n')
                                                        fout.write('*******************************************************************\n')
                                                        fout.write('*_Start_resample:\n')
                                                        fout.write('*******************************************************************\n')

                                                        if jobcoreg.resample['RS_SHIFTAZI']['value'] == 'ON': 
                                                                fout.write(' azimuth spectrum:                       1\n')
                                                        else:
                                                                fout.write(' azimuth spectrum:                       0\n')
                                                        fout.write('Data_output_file:                               %s.%s.rslc\n' % (oldref,poli.lower()))

                                                        if jobcoreg.resample['RS_OUT_FORMAT']['value'] == 'ci2': 
                                                                fout.write('Data_output_format:                             complex_short\n')
                                                        else: 
                                                                fout.write('Data_output_format:                             complex_long\n')

                                                        # if jobcoreg.resample['RS_METHOD']['value'] == 'rc12p':

                                                        fout.write('Interpolation kernel:                           12 point raised cosine kernel\n') # SHOULD BE MODIFY

                                                        fout.write('First_line (w.r.t. original_master):            %s\n' % (para['First_line (w.r.t. original_image)']))
                                                        fout.write('Last_line (w.r.t. original_master):             %s\n' % (para['Last_line (w.r.t. original_image)']))
                                                        fout.write('First_pixel (w.r.t. original_master):           %s\n' % (para['First_pixel (w.r.t. original_image)']))
                                                        fout.write('Last_pixel (w.r.t. original_master):            %s\n' % (para['Last_pixel (w.r.t. original_image)']))

                                                        fout.write('*******************************************************************\n')
                                                        fout.write('* End_resample:_NORMAL\n')
                                                        fout.write('*******************************************************************\n')
                                
                                        # Import the new refdate from the old dates
                                        for poli in jobcoreg.polarisation: 
                                                oldmastefile = jobcoreg.pathstack+os.sep+'rslc_'+poli.lower()+os.sep+newref+'.'+poli.lower()+'.rslc.res'
                                                newmastefile = jobcoreg.workdirectory+os.sep+'slc'+os.sep+newref+'.'+poli.lower()+'.slc.res'
                                                shutil.copy(oldmastefile,newmastefile)
                                                shutil.copy(oldmastefile.replace('.res',''),newmastefile.replace('.res',''))

                                                para = doristools.readimagepara(newmastefile,mode='slc')

                                                dict_tmp = dict()
                                                dict_tmp['cmd%s' % (0)] = [ ['doris.rmstep.sh','resample','%s' % (newmastefile)],
                                                        None]           
                                                dict_tmp['cmd%s' % (0)] = [ ['doris.rmstep.sh','crop','%s' % (newmastefile)],
                                                        None]                             
                                                doristools.wrappersubprocess(dict_tmp,jobcoreg.computercores,jobcoreg.computerworkers,verbose,log)

                                                slave = []
                                                with open(newmastefile,'r') as fi: 
                                                        slave = fi.readlines()

                                                master = []
                                                for li in slave:
                                                        a = li.replace('SLAVE','MASTER') 
                                                        a = a.replace('slave','master') 
                                                        master.append(a)

                                                with open(newmastefile,'w') as fout: 
                                                        for li in master:
                                                                fout.write('%s' % (li))

                                                with open(newmastefile,'a') as fout: 
                                                                
                                                        fout.write('\n')
                                                        fout.write('\n')
                                                        fout.write('\n')
                                                        fout.write('*******************************************************************\n')
                                                        fout.write('*_Start_crop:			master step01\n')
                                                        fout.write('*******************************************************************\n')
                                                        fout.write('Data_output_file: 				        %s.%s.slc\n' % (newref,poli.lower()))
                                                        fout.write('Data_output_format: 				%s\n' % (para['Data_output_format']))
                                                        fout.write('First_line (w.r.t. original_image): 		%s\n' % (para['First_line (w.r.t. original_image)']))
                                                        fout.write('Last_line (w.r.t. original_image): 		        %s\n' % (para['Last_line (w.r.t. original_image)']))
                                                        fout.write('First_pixel (w.r.t. original_image): 	        %s\n' % (para['First_pixel (w.r.t. original_image)']))
                                                        fout.write('Last_pixel (w.r.t. original_image): 		%s\n' % (para['Last_pixel (w.r.t. original_image)']))
                                                        fout.write('Number of lines (non-multilooked): 		        %s\n' % (para['Last_line (w.r.t. original_image)']-para['First_line (w.r.t. original_image)']+1))
                                                        fout.write('Number of pixels (non-multilooked): 		%s\n' % (para['Last_pixel (w.r.t. original_image)']-para['First_pixel (w.r.t. original_image)']+1))
                                                        fout.write('*******************************************************************\n')
                                                        fout.write('* End_crop:_NORMAL\n')
                                                        fout.write('*******************************************************************\n')
                                                
                                                # Final saving 
                                                jobcoreg.refdate = newref
                                else: 
                                        raise ValueError(usermessage.errormsg(__name__,updatestack.__name__,__file__,__copyright__,
                                                'The new reference cannot be in the new date. Please turn off the option which updates the reference date.',jobcoreg.log))

                else:
                        usermessage.ezprint('\tThe reference date will be NOT updated.',jobcoreg.log,verbose)
                        updateref = False

                ## Modification of the dates files in order to contain the reference dates
                dates = []
                with open(jobcoreg.workdirectory+os.sep+'dates','r') as fi:
                        for di in fi: 
                                dates.append(di.strip()) 

                dates.append(jobcoreg.refdate)
                dates = np.sort(dates)

                with open(jobcoreg.workdirectory+os.sep+'dates','w') as fout:
                        for di in dates:
                                fout.write('%s\n' % (di))

                ## Continue the process
                if updateref == True and jobcoreg.mastertiming['process']['value'] == True:
                        mastertiming(jobcoreg,modeforce=jobcoreg.updatestack['force']['value'])

                oversample(jobcoreg,modeforce=jobcoreg.updatestack['force']['value'])
                coarseoffset(jobcoreg,modeforce=jobcoreg.updatestack['force']['value'])
                finecoreg(jobcoreg,modeforce=jobcoreg.updatestack['force']['value'])
                reltiming(jobcoreg,modeforce=jobcoreg.updatestack['force']['value'])
                demassist(jobcoreg,modeforce=jobcoreg.updatestack['force']['value'])
                coregpm(jobcoreg,modeforce=jobcoreg.updatestack['force']['value'])
                resample(jobcoreg,jobcoreg.updatestack['force']['value'])
                finalstack(jobcoreg,modeforce=jobcoreg.updatestack['force']['value'])
                cleanstack(jobcoreg)

        else: 
                raise ValueError(usermessage.errormsg(__name__,updatestack.__name__,__file__,__copyright__,
                        'No new dates are available. Stop here.',jobcoreg.log))

        os.chdir(cur_dir)
        jobcoreg.updatestack['done']['value'] = True

        return jobcoreg


