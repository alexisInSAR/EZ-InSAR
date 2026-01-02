#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to process coregistration with SNAP processor 

The module allows to process coregistration with SNAP processor from an ``ezinsar.coregistration`` job. 
    
    (From `ezinsar` package)

Note: 
        RAM memory optimisation needs to be done!

Changelog:
        * 1.1.0: Several changes, Feb. 2025, Alexis Hrysiewicz
                * Start the support of RADARSAT-2 FQ and SQ imagery
                * Start the support of CSK HIMAGE imagery
                * Start the support of TSX/PAZ imagery (SM) imagery
                * Start the support of SAOCOM SM imagery
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
from typing import Optional
from shapely.wkt import loads
import shutil
import sys
import pandas as pd 
import json
import copy
import random
import string
import matplotlib.pyplot as plt

from ezinsar import usermessage
from ezinsar import constants
from ezinsar.eicomponents.processor.snapmodule import snaptools
from ezinsar.eicomponents.sensor.s1module import s1slctools, s1stacktools
from ezinsar.eicomponents.sensor.cskmodule import cskslctools, cskstacktools
from ezinsar.eicomponents.sensor.tsxmodule import tsxslctools, tsxstacktools
from ezinsar.eicomponents.sensor.rsat2module import rsat2slctools, rsat2stacktools
try: 
        from ezinsarsaocommodule import saocomslctools, saocomstacktools
except: 
        a = 'dummy' 

from ezinsar.eicomponents.processor.snapmodule import snapgpttools

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
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()
        if not 'coregistration' in str(type(jobcoreg)):
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
                if jobcoreg.satellite == 'RSAT2':
                        filelist = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'RS2*'))
                elif jobcoreg.satellite == 'CSK':
                        filelist = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'CSK*'))
                elif jobcoreg.satellite in ['TSX','PAZ']:
                        filelist = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'TSX*') + glob.glob(jobcoreg.pathSLC+os.sep+'TDM*') + glob.glob(jobcoreg.pathSLC+os.sep+'PAZ*'))
                elif jobcoreg.satellite == 'SAOCOM':
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

        #We re-write the list with sorted dates
        usermessage.ezprint('Write the dates file in %s' %(jobcoreg.workdirectory+os.sep+'dates'),jobcoreg.log,verbose) 
        fibis = open(jobcoreg.workdirectory+os.sep+'dates','w')
        for di in date:
            datestr = di.strftime("%Y%m%d")
            fibis.write(datestr+'\n')
        fibis.close()
        
        # Display 
        usermessage.ezprint('There are %d files for %d unique dates.\n' %(len(filelist),len(date)),jobcoreg.log,verbose) 

        os.chdir(cur_dir)
        jobcoreg.checkSLC['done']['value'] = True

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
        
        if not 'coregistration' in str(type(jobcoreg)):
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

        if jobcoreg.checkSLC['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,coarserefdate.__name__,__file__,__copyright__,
                                'The previous step (checkSLC) is not done.',None))

        if jobcoreg.satellite == 'S1': 

                date_ref, dates_SLC, Btempnorm, Bperpnorm = s1stacktools.commputecoarsenetwork(jobcoreg.pathSLC,jobcoreg.roi,jobcoreg.polarisation[0],
                        pathorbit = jobcoreg.pathorbit,
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
## importSLC FUNCTION
################################################################################
def importSLC(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Import the SLCs into a SNAP format

        The function will import the SLC files into a SNAP format, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        
        if not 'coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,importSLC.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,importSLC.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))
        
        usermessage.openingmsg(__name__,importSLC.__name__,__file__,__copyright__,'coregistration Step: importSLC',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.coarserefdate['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,importSLC.__name__,__file__,__copyright__,
                                'The previous step (coarserefdate) is not done.',None))
        
        cur_dir = os.getcwd()
        os.chdir(jobcoreg.workdirectory)

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)

        if not os.path.isdir('input_prep'): 
                os.mkdir('input_prep')

        listdate = snaptools.readdatefile('dates')

        ## Processing loop
        for dslc in listdate: 
                usermessage.ezprint('For the date %s' %(dslc),jobcoreg.log,verbose) 

                if (not glob.glob('input_prep'+os.sep+dslc+'.dim')) or modeforce == True:

                        ## Import the Product (in case of Sentinel-1 IW)
                        if jobcoreg.satellite == 'S1':

                                usermessage.ezprint('\tDetection of Sentinel-1 SM image(s)',jobcoreg.log,verbose) 

                                ## Detection of the different slices
                                pathslctmp = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'*'+dslc+'*'))
                                nb_slice = len(pathslctmp)

                        elif jobcoreg.satellite == 'CSK':
                                usermessage.ezprint('\tDetection of CSK image(s)',jobcoreg.log,verbose) 
                                pathslctmp = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'CSK*'+dslc+'*'+os.sep+'*.h5'))
                                nb_slice = len(pathslctmp)          

                        elif jobcoreg.satellite == 'RSAT2':
                                usermessage.ezprint('\tDetection of RSAT2 image(s)',jobcoreg.log,verbose) 
                                pathslctmp = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'RS2*'+dslc+'*'))
                                nb_slice = len(pathslctmp)    

                        elif jobcoreg.satellite == 'SAOCOM':
                                usermessage.ezprint('\tDetection of SAOCOM image(s)',jobcoreg.log,verbose) 
                                filelist = np.sort(glob.glob(jobcoreg.pathSLC+os.sep+'*SAR*'))
                                SLCfile = None
                                for fi in filelist: 
                                        SAOCOMannoresults = saocomslctools.detectSAOCOMannotation(fi,jobcoreg.polarisation[0])
                                        dates1 = datetime.datetime.strptime(SAOCOMannoresults['data_xmli1']['startTime'].split('T')[0].replace('-',''), '%Y%m%d').strftime("%Y%m%d")

                                        if dates1 == dslc:
                                                SLCfile = fi         

                                pathslctmp = np.sort(glob.glob(SLCfile+os.sep+'*.xemt'))
                                nb_slice = len(pathslctmp)    

                        ## Read the SLCs
                        usermessage.ezprint('\tRead the images',jobcoreg.log,verbose) 

                        gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                nbthread=jobcoreg.computernbthread,
                                cleancache = constants.__SNAPcacheclean__,
                                debugmode = constants.__SNAPloggingmode__)
                        gptdata.xmlinit()
                        gptdata.Read(pathslctmp[0])

                        # Cropping
                        sourceBands = []
                        for poly in jobcoreg.polarisation:
                                sourceBands.append('i_%s' % (poly.upper()))
                                sourceBands.append('q_%s' % (poly.upper()))
                                sourceBands.append('Intensity_%s' % (poly.upper()))

                        if jobcoreg.modecropping == 'auto':
                                usermessage.ezprint('\tCropping',jobcoreg.log,verbose) 
                                gptdata.generic('Subset',
                                        {'copyMetadata': True,
                                        'geoRegion': loads(jobcoreg.roi).wkt,
                                        'sourceBands': ','.join(sourceBands),
                                        })

                        ## Write 
                        gptdata.Write(os.path.abspath('input_prep'+os.sep+dslc+'.dim'))
                        gptdata.xmlclose()
                        gptdata.run(verbose=verbose,log=jobcoreg.log)
                        gptdata.clean()
                                
                else: 
                        usermessage.warningmsg(__name__,importSLC.__name__,__file__,'The file %s is already processed.' % (dslc),jobcoreg.log,verbose)

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)

        if jobcoreg.importSLC['createbmp']['value']:

                usermessage.ezprint('Creation of .bmp images',jobcoreg.log,verbose) 
                for dslc in listdate: 
                        usermessage.ezprint('\tFor the date %s' %(dslc),jobcoreg.log,verbose) 

                        if (not os.path.isfile('input_prep'+os.sep+dslc+'.'+jobcoreg.polarisation[0].lower()+'.mli.bmp')) or modeforce == True: 
                                listfile = glob.glob('input_prep'+os.sep+dslc+'.data'+os.sep+'*'+jobcoreg.polarisation[0].upper()+'*.img')
                                snaptools.createintensitybmp(listfile,
                                        'input_prep'+os.sep+dslc+'.'+jobcoreg.polarisation[0].lower()+'.mli.bmp',
                                        jobcoreg.mlrandisplay, 
                                        jobcoreg.mlazidisplay,
                                        verbose = False,
                                        log = jobcoreg.log)
                                        
                                usermessage.ezprint('\t\tdone',jobcoreg.log,verbose) 

        jobcoreg.importSLC['done']['value'] = True
        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)
        os.chdir(cur_dir)

        return jobcoreg 

################################################################################
## refinerefdate FUNCTION
################################################################################
def refinerefdate(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Refine the reference date

        The function will refine the reference date, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        
        if not 'coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,refinerefdate.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,refinerefdate.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,refinerefdate.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))
        
        usermessage.openingmsg(__name__,refinerefdate.__name__,__file__,__copyright__,'Coregistration Step: refinerefdate',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.importSLC['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,refinerefdate.__name__,__file__,__copyright__,
                                'The previous step (importSLC) is not done.',None))
        
        cur_dir = os.getcwd()
        os.chdir(jobcoreg.workdirectory+os.sep+'input_prep')

        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)

        if jobcoreg.refinerefdate['process']['value'] == True:    
                listdate = snaptools.readdatefile('..'+os.sep+'dates')
                stackproduct = []

                ## Processing
                for dslc in listdate: 
                        stackproduct.append(os.path.abspath(dslc+'.dim'))

                gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                                nbthread=jobcoreg.computernbthread,
                                cleancache = constants.__SNAPcacheclean__,
                                debugmode = constants.__SNAPloggingmode__)
                gptdata.xmlinit()
                gptdata.ProductSetReader(stackproduct)
                gptdata.InSAROverview(jobcoreg.workdirectory+os.sep+'masterselection.json')
                gptdata.xmlclose()
                gptdata.run(verbose=verbose,log=jobcoreg.log)
                gptdata.clean()
                gptdata = None 
   
                # Read the results
                with open(jobcoreg.workdirectory+os.sep+'masterselection.json') as fi:
                        data = json.load(fi)

                if os.path.isfile(jobcoreg.workdirectory+os.sep+'masterselection.json'):
                        os.remove(jobcoreg.workdirectory+os.sep+'masterselection.json')

                dfmaster = pd.json_normalize(data['reference'])
                dfsec = pd.json_normalize(data['secondary'])
                dateref = datetime.datetime.strptime(dfmaster['start_time'][0].split(' ')[0],"%d-%b-%Y").strftime("%Y%m%d")

                usermessage.ezprint('The best potential date should be %s' % (dateref),jobcoreg.log,verbose)

                if not jobcoreg.refdate == dateref: 
                        usermessage.warningmsg(__name__,refinerefdate.__name__,__file__,'The reference date is not the same used previously. We will modify the value.',jobcoreg.log,verbose)

                jobcoreg.refdate = dateref 

                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)

        else: 
                usermessage.warningmsg(__name__,refinerefdate.__name__,__file__,'This step is not enabled',jobcoreg.log,verbose)

        jobcoreg.refinerefdate['done']['value'] = True
        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)
        os.chdir(cur_dir)

        return jobcoreg

################################################################################
## coreg FUNCTION
################################################################################
def coreg(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Coregistration of the stack

        The function will coregistre the stack, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'coregistration' in str(type(jobcoreg)):
                raise ValueError(usermessage.errormsg(__name__,coreg.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = jobcoreg.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,coreg.__name__,__file__,__copyright__,
                        'verbose','True or False',jobcoreg.log))

        if modeforce == None:
                modeforce = jobcoreg.modeforce
        if not isinstance(modeforce,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,coreg.__name__,__file__,__copyright__,
                        'modeforce','True or False',jobcoreg.log))
        
        usermessage.openingmsg(__name__,coreg.__name__,__file__,__copyright__,'Coregistration Step: coreg',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.importSLC['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,coreg.__name__,__file__,__copyright__,
                                'The previous step (importSLC) is not done.',None))
        
        if not os.path.isdir(jobcoreg.workdirectory+os.sep+'stack'): 
                os.mkdir(jobcoreg.workdirectory+os.sep+'stack')

        os.chdir(jobcoreg.workdirectory+os.sep+'stack')
        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)

        listdate = snaptools.readdatefile('..'+os.sep+'dates')
        listdate.reverse()

        usermessage.ezprint('Run the coregistration of the stack',jobcoreg.log,verbose)
                        
        stackproduct = []

        for dslc in listdate: 
                if not dslc == jobcoreg.refdate:
                        usermessage.ezprint('\tAdd the date %s' %(dslc),jobcoreg.log,verbose)
                        stackproduct.append(os.path.abspath(jobcoreg.workdirectory+os.sep+'input_prep'+os.sep+dslc+'.dim'))

        usermessage.ezprint('\tAdd the reference date %s' %(jobcoreg.refdate),jobcoreg.log,verbose) 
        if len(listdate) > 2: 
                stackproduct.insert(0,os.path.abspath(jobcoreg.workdirectory+os.sep+'input_prep'+os.sep+jobcoreg.refdate+'.dim'))

        else: 
                stackproduct.insert(0,os.path.abspath(jobcoreg.workdirectory+os.sep+'input_prep'+os.sep+jobcoreg.refdate+'.dim'))
        
        gptdata = snapgpttools.snapgpt(cachesize= constants.__SNAPcachemax__,
                        nbthread=jobcoreg.computernbthread,
                        cleancache = constants.__SNAPcacheclean__,
                        debugmode = constants.__SNAPloggingmode__)
        gptdata.xmlinit()
        gptdata.ProductSetReader(stackproduct)

        ## Create the stack 
        gptdata.generic('CreateStack',{'initialOffsetMethod': jobcoreg.coreg['initoffset']['value']})

        ## Demodulation
        if jobcoreg.coreg['demodulate']['value']:
                gptdata.generic('Demodulate',{})

        ## Cross-correlation
        gptdata.generic('Cross-Correlation',
                {'numGCPtoGenerate': jobcoreg.coreg['numGCPtoGenerate']['value'],
                'coarseRegistrationWindowWidth': jobcoreg.coreg['coarseRegistrationWindowWidth']['value'],
                'coarseRegistrationWindowHeight': jobcoreg.coreg['coarseRegistrationWindowWidth']['value'],
                'rowInterpFactor': jobcoreg.coreg['rowInterpFactor']['value'],
                'columnInterpFactor': jobcoreg.coreg['columnInterpFactor']['value'],
                'maxIteration': jobcoreg.coreg['maxIteration']['value'],
                'gcpTolerance': jobcoreg.coreg['gcpTolerance']['value'],
                'applyFineRegistration': jobcoreg.coreg['applyFineRegistration']['value'],
                'inSAROptimized': jobcoreg.coreg['inSAROptimized']['value'],
                'fineRegistrationWindowWidth': jobcoreg.coreg['fineRegistrationWindowWidth']['value'],
                'fineRegistrationWindowHeight': jobcoreg.coreg['fineRegistrationWindowHeight']['value'],
                'fineRegistrationWindowAccAzimuth': jobcoreg.coreg['fineRegistrationWindowAccAzimuth']['value'],
                'fineRegistrationWindowAccRange': jobcoreg.coreg['fineRegistrationWindowAccRange']['value'],
                'fineRegistrationOversampling': jobcoreg.coreg['fineRegistrationOversampling']['value'],
                'coherenceWindowSize': jobcoreg.coreg['coherenceWindowSize']['value'],
                'coherenceThreshold': jobcoreg.coreg['coherenceThreshold']['value'],
                'useSlidingWindow': jobcoreg.coreg['useSlidingWindow']['value'],
                'computeOffset': jobcoreg.coreg['computeOffset']['value'],
                'onlyGCPsOnLand': jobcoreg.coreg['onlyGCPsOnLand']['value'],
                })

        ## Warp
        gptdata.generic('Warp',
                {'rmsThreshold': jobcoreg.coreg['rmsThreshold']['value'],
                'warpPolynomialOrder': jobcoreg.coreg['warpPolynomialOrder']['value'],
                'interpolationMethod': jobcoreg.coreg['interpolationMethod']['value'],
                'demRefinement': jobcoreg.coreg['demRefinement']['value'],
                'excludeMaster': jobcoreg.coreg['excludeMaster']['value'],
                })

        ## Remodulate
        if jobcoreg.coreg['remodulate']['value']:
                gptdata.generic('Remodulate',{})

        ## Run and write
        gptdata.Write(os.path.abspath(jobcoreg.pathstack+os.sep+'stack'))
        gptdata.xmlclose()

        if not os.path.isdir(jobcoreg.pathstack):
                os.mkdir(jobcoreg.pathstack)

        if (not os.path.isfile(os.path.abspath(jobcoreg.pathstack+os.sep+'stack.dim'))) or modeforce == True:
                gptdata.run(verbose=verbose,log=jobcoreg.log)
        else:
                usermessage.warningmsg(__name__,coreg.__name__,__file__,'The file %s is already computed.' % ('stack.dim'),jobcoreg.log,verbose)
        gptdata.clean()
                      
        if jobcoreg.coreg['createbmpifg']['value']:

                usermessage.ezprint('Creation of .bmp images for the interferograms',jobcoreg.log,verbose) 
                listdate = snaptools.readdatefile('..'+os.sep+'dates')

                for dslc in listdate: 
                        if not dslc == jobcoreg.refdate:

                                usermessage.ezprint('\tFor the interferogram %s - %s' % (jobcoreg.refdate,dslc),jobcoreg.log,verbose)

                                a = datetime.datetime.strptime(jobcoreg.refdate, "%Y%m%d").strftime('%d%b%Y')
                                b = datetime.datetime.strptime(dslc, "%Y%m%d").strftime('%d%b%Y')
                                
                                realfilemaster = glob.glob(jobcoreg.pathstack+os.sep+'stack.data'+os.sep+'q*'+jobcoreg.polarisation[0].upper()+'*mst*'+a+'*.img')[0]
                                imagfilemaster = glob.glob(jobcoreg.pathstack+os.sep+'stack.data'+os.sep+'i*'+jobcoreg.polarisation[0].upper()+'*mst*'+a+'*.img')[0]    

                                realfileslave = glob.glob(jobcoreg.pathstack+os.sep+'stack.data'+os.sep+'q*'+jobcoreg.polarisation[0].upper()+'*slv*'+b+'*.img')[0]
                                imagfileslave = glob.glob(jobcoreg.pathstack+os.sep+'stack.data'+os.sep+'i*'+jobcoreg.polarisation[0].upper()+'*slv*'+b+'*.img')[0] 

                                snaptools.createifgbmpnocorrection([realfilemaster, imagfilemaster],[realfileslave, imagfileslave],
                                        jobcoreg.refdate+'_'+jobcoreg.polarisation[0].lower()+'_'+dslc+'_'+jobcoreg.polarisation[0].lower()+'.int.bmp',
                                        jobcoreg.mlrandisplay, 
                                        jobcoreg.mlazidisplay,
                                        colormap = 'sar',
                                        verbose= False,
                                        log = jobcoreg.log,
                                        ) 
                                                        
                usermessage.ezprint('\t\tdone',jobcoreg.log,verbose) 

        
        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)
        os.chdir(cur_dir)
        jobcoreg.coreg['done']['value'] = True

        return jobcoreg

################################################################################
## cleanstack FUNCTION
################################################################################
def cleanstack(jobcoreg, verbose: Optional[bool] = None, modeforce: Optional[bool] = None):
        """Clean the work directory

        The function will clean the work directory, from an ``ezinsar.coregistration``.   

        Args:
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                modeforce (bool): Forcing mode [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.coregistration``: Return an EZ-InSAR coregistration class
        
        """
        cur_dir = os.getcwd()

        if not 'coregistration' in str(type(jobcoreg)):
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
        
        usermessage.openingmsg(__name__,coreg.__name__,__file__,__copyright__,'Coregistration Step: cleanstack',jobcoreg.log,verbose)

        jobcoreg.check(verbose=False,mode='high')

        if jobcoreg.coreg['done']['value'] == False:
                raise ValueError(usermessage.errormsg(__name__,cleanstack.__name__,__file__,__copyright__,
                                'The previous step (coreg) is not done.',None))
        
        os.chdir(jobcoreg.workdirectory)
        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)

        if jobcoreg.cleanstack['process']['value']: 
                
                if jobcoreg.cleanstack['keepinputfiles']['value'] == False:
                        if os.path.isdir(jobcoreg.workdirectory+os.sep+'input_prep'):
                                shutil.rmtree(jobcoreg.workdirectory+os.sep+'input_prep')
                
                if os.path.isdir(jobcoreg.workdirectory+os.sep+'stack'):
                        shutil.rmtree(jobcoreg.workdirectory+os.sep+'stack')

                if os.path.isfile(jobcoreg.workdirectory+os.sep+'coarse_ifg_network.jpg'):
                        os.remove(jobcoreg.workdirectory+os.sep+'coarse_ifg_network.jpg')

                if os.path.isfile(jobcoreg.workdirectory+os.sep+'dates'):
                        os.remove(jobcoreg.workdirectory+os.sep+'dates')

        jobcoreg.cleanstack['done']['value'] = True
        if constants.__SNAPcacheclean__:
                snaptools.snapclearcache(verbose=False,log=jobcoreg.log)
        os.chdir(cur_dir)

        return jobcoreg
