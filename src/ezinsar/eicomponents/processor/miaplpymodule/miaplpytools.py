#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to add some tools for the MintPy processing class

The module adds some tools for the MintPy processing class. 
    
    (From `ezinsar` package)

Changelog:
        * 1.0.1: Change the import line, Dec. 2025, Alexis Hrysiewicz
        * 1.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import os
import psutil
from typing import Optional
import numpy as np
import subprocess
from datetime import datetime
import random
import string 
import h5py
import glob
import pyproj

from ezinsar import usermessage
from ezinsar import constants
from ezinsar.tools import ezinsardata 
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Wrapper for MiaplPy allowing logging of processing 
################################################################################
def wrappermiaplpy(job,
                stepi,
                verbose,
                log):
        """Run a subprocess for MiaplPy 

        The function will run a subprocess for MiaplPy 

        Args:   
                job (``ezinsar.job``): EZ-InSAR tsprocessing job with MiaplPy
                stepi (str): Processing step
                verbose (bool): verbose
                log (str): Log file

        Returns 
                ``ezinsar.job``: EZ-InSAR tsprocessing job with MiaplPy

        """
        
        ## Check if the workdirectory exists
        if not os.path.isdir(job.workdirectory):
                os.makedirs(job.workdirectory)
        if not os.path.isdir(job.workdirectory+os.sep+'miaplpy'):
                os.makedirs(job.workdirectory+os.sep+'miaplpy')

        ##Write the config file 
        writecfg(job, 
                file = job.pathmiaplpyconfig,
                verbose = False,
                log = job.log)

        if not stepi == 'extract_res': 
                from ezinsar.eicomponents.processor.isce2module import isce2tools
                os.environ['PATH'], os.environ['PYTHONPATH'] = isce2tools.isce2checkenv(mode='IW',verbose=False) 
                my_env = os.environ.copy()
                my_env["PATH"] = f"/usr/local/bin:{my_env['PATH']}"
                my_env["PYTHONPATH"] = f"/usr/local/bin:{my_env['PYTHONPATH']}"

                usermessage.ezprint('Run MiaplPy:',log,verbose)

                ## Creation of the command        
                cmd = 'miaplpyApp --dir %s --dostep %s %s' % (job.workdirectory,
                                                                stepi,
                                                                job.pathmiaplpyconfig)

                usermessage.ezprint('\tCommand: %s' % (cmd),log,verbose)

                pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, env=my_env)
                
                try: 
                        while (line := pr.stdout.readline()) != "":
                                usermessage.ezprint(line.replace('\n',' '),log,verbose)

                        if not len("".join(pr.stderr.readline().strip().split())) == 0:
                                while (line := pr.stderr.readline()):
                                        usermessage.ezprint(line.replace('\n',' '),log,verbose)  
                                # raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the MiaplPy processing',log))
                                usermessage.warningmsg(__name__,__name__,__file__,'Potential error in the MiaplPy processing',job,True)

                except KeyboardInterrupt:
                        pr.terminate()
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the MiaplPy processing: user terminate',log))

                usermessage.ezprint('\tdone',log,verbose)

                exec("job.%s['done']['value'] = True" % (stepi))

        else: 
                ## Extraction of displacements
                data = importmiaplpyresults(job.workdirectory, 
                        job = job,
                        verbose = verbose,
                        log = job.log)

                name = 'TS_LOS_%s_%s_%s_%s_%s_%s_%s' % (job.satellite,
                                                job.satmode,
                                                job.relorbit,
                                                job.satpass,
                                                job.ifgprocessor,
                                                job.processor,
                                                job.mode.replace('/',''))

                if job.extract_res['ecraseprevious']['value'] == True: 
                        usermessage.warningmsg(__name__,__name__,__file__,'The previous file will be replaced.',job.log,verbose)
                        name = job.workdirectory + os.sep + name + '.eidata'
                else: 
                        name = job.workdirectory + os.sep + '%s_%s.eidata' % (name,len(glob.glob(name+'*')))

                ezinsardata.saveEZdata(data,name,verbose = verbose,log = job.log)

        return job 

################################################################################
## Function to write the MintPy configuration file
################################################################################
def writecfg(jobmintpy, 
        file: Optional[str] = '.'+os.sep+'MintPy.cfg',
        verbose: Optional[bool] = None, 
        log: Optional[bool] = None):
        """Write the MintPy configuration file from an ``ezinsar.tsprocessing`` using MintPy

        The function writes the MintPy configuration file from an ``ezinsar.tsprocessing``.   

        Args:
                jobmintpy (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for MintPy processor
                file (str, Optional): Path and name of the MintPy configuration file [Default: MintPy.cfg]
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (bool): log [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        if log == None:
                log = jobmintpy.log

        if verbose == None:
                verbose = jobmintpy.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,writecfg.__name__,__file__,__copyright__,
                        'verbose','True or False',log))

        usermessage.openingmsg(__name__,writecfg.__name__,__file__,__copyright__,'Write the MintPy configuration file',log,verbose)

        jobmintpy.check(verbose=False)

        with open(file,'w') as fcfg: 
                fcfg.write('# vim: set filetype=cfg:\n')
                fcfg.write('##------------------------ miaplpyApp.cfg ------------------------##\n')
                
                fcfg.write('\n')
                fcfg.write('########## text before script calls\n')
                fcfg.write('miaplpy.textCmd                        = auto    # [eg: source ~/.bashrc]\n')
                
                fcfg.write('\n')
                fcfg.write('########## parallel job setting\n')
                fcfg.write('miaplpy.multiprocessing.numProcessor              = %s    # auto for 4\n' % (jobmintpy.computer['multiprocessing.numProcessor']['value']))
                
                fcfg.write('\n')
                fcfg.write('########## 1. load data given the area of interest\n')
                fcfg.write('## auto - automatic path pattern for Univ of Miami file structure\n')
                fcfg.write('## crop_image.py -h to check more details and example inputs.\n')
                fcfg.write('## directories are to read from and the subsets will be saved under miaplpy directory\n')
                fcfg.write('## compression to save disk usage for ifgramStack.h5 file:\n')
                fcfg.write('## no   - save   0% disk usage, fast [default]\n')
                fcfg.write('## lzf  - save ~57% disk usage, relative slow\n')
                fcfg.write('## gzip - save ~62% disk usage, very slow [not recommend]\n')
                
                fcfg.write('\n')
                fcfg.write('miaplpy.load.processor      = %s  #[isce,snap,gamma,roipac], auto for isceTops\n' % (jobmintpy.load_data['load.processor']['value']))
                fcfg.write('miaplpy.load.updateMode     = %s  #[yes / no], auto for yes, skip re-loading if HDF5 files are complete\n' % (jobmintpy.load_data['load.updateMode']['value']))
                fcfg.write('miaplpy.load.compression    = %s  #[gzip / lzf / no], auto for no.\n' % (jobmintpy.load_data['load.compression']['value']))
                fcfg.write('miaplpy.load.autoPath       = %s    # [yes, no] auto for no\n' % (jobmintpy.load_data['load.autoPath']['value']))
                fcfg.write('##---------Coregistered SLC images:\n')
                fcfg.write('miaplpy.load.slcFile        = %s  #[path2slc_file]\n' % (jobmintpy.load_data['load.slcFile']['value']))
                fcfg.write('miaplpy.load.startDate      = %s  #auto for first date\n' % (jobmintpy.load_data['load.startDate']['value']))
                fcfg.write('miaplpy.load.endDate        = %s  #auto for last date\n' % (jobmintpy.load_data['load.endDate']['value']))
                fcfg.write('##---------for ISCE only:\n')
                fcfg.write('miaplpy.load.metaFile       = %s  #[path2metadata_file], i.e.: ./reference/IW1.xml, ./referenceShelve/data.dat\n' % (jobmintpy.load_data['load.metaFile']['value']))
                fcfg.write('miaplpy.load.baselineDir    = %s  #[path2baseline_dir], i.e.: ./baselines\n' % (jobmintpy.load_data['load.baselineDir']['value']))
                fcfg.write('##---------geometry datasets:\n')
                fcfg.write('miaplpy.load.demFile        = %s  #[path2hgt_file]\n' % (jobmintpy.load_data['load.demFile']['value']))
                fcfg.write('miaplpy.load.lookupYFile    = %s  #[path2lat_file], not required for geocoded data\n' % (jobmintpy.load_data['load.lookupYFile']['value']))
                fcfg.write('miaplpy.load.lookupXFile    = %s  #[path2lon_file], not required for geocoded data\n' % (jobmintpy.load_data['load.lookupXFile']['value']))
                fcfg.write('miaplpy.load.incAngleFile   = %s  #[path2los_file], optional\n' % (jobmintpy.load_data['load.incAngleFile']['value']))
                fcfg.write('miaplpy.load.azAngleFile    = %s  #[path2los_file], optional\n' % (jobmintpy.load_data['load.azAngleFile']['value']))
                fcfg.write('miaplpy.load.shadowMaskFile = %s  #[path2shadow_file], optional\n' % (jobmintpy.load_data['load.shadowMaskFile']['value']))
                fcfg.write('miaplpy.load.waterMaskFile  = %s  #[path2water_mask_file], optional\n' % (jobmintpy.load_data['load.waterMaskFile']['value']))
                fcfg.write('miaplpy.load.bperpFile      = %s  #[path2bperp_file], optional\n' % (jobmintpy.load_data['load.bperpFile']['value']))
                fcfg.write('##---------interferogram datasets:\n')
                fcfg.write('miaplpy.load.unwFile        = %s  #[path2unw_file]\n' % (jobmintpy.load_data['load.unwFile']['value']))
                fcfg.write('miaplpy.load.corFile        = %s  #[path2cor_file]\n' % (jobmintpy.load_data['load.corFile']['value']))
                fcfg.write('miaplpy.load.connCompFile   = %s  #[path2conn_file], optional\n' % (jobmintpy.load_data['load.connCompFile']['value']))
                fcfg.write('miaplpy.load.intFile        = %s  #[path2int_file], optional\n' % (jobmintpy.load_data['load.intFile']['value']))
                fcfg.write('miaplpy.load.ionoFile       = %s  #[path2iono_file], optional\n' % (jobmintpy.load_data['load.ionoFile']['value']))
                fcfg.write('##---------subset (optional):\n')
                fcfg.write('## if both yx and lalo are specified, use lalo option unless a) no lookup file AND b) dataset is in radar coord\n')
                fcfg.write('miaplpy.subset.yx           = %s    #[y0:y1,x0:x1 / no], auto for no\n' % (jobmintpy.load_data['subset.yx']['value']))
                fcfg.write('miaplpy.subset.lalo         = %s    #[S:N,W:E / no], auto for no\n' % (jobmintpy.load_data['subset.lalo']['value']))

                fcfg.write('\n')
                fcfg.write('########## 2,3. Perform patch wise phase linking and concatenate patches\n')
                fcfg.write('## window sizes are used in step 2, 3,\n')
                fcfg.write('miaplpy.inversion.patchSize                = %s   # patch size (n*n) to divide the image for parallel processing, auto for 200\n' % (jobmintpy.phase_linking['inversion.patchSize']['value']))
                fcfg.write('miaplpy.inversion.ministackSize            = %s   # number of images in each ministack, auto for 10\n' % (jobmintpy.phase_linking['inversion.ministackSize']['value']))
                fcfg.write('miaplpy.inversion.rangeWindow              = %s   # range window size for searching SHPs, auto for 15\n' % (jobmintpy.phase_linking['inversion.rangeWindow']['value']))
                fcfg.write('miaplpy.inversion.azimuthWindow            = %s   # azimuth window size for searching SHPs, auto for 15\n' % (jobmintpy.phase_linking['inversion.azimuthWindow']['value']))
                fcfg.write('miaplpy.inversion.shpTest                  = %s   # [ks, ad, ttest] auto for ks: kolmogorov-smirnov test\n' % (jobmintpy.phase_linking['inversion.shpTest']['value']))
                fcfg.write('miaplpy.inversion.phaseLinkingMethod       = %s   # [EVD, EMI, PTA, sequential_EVD, sequential_EMI, sequential_PTA, StBAS], auto for sequential_EMI\n' % (jobmintpy.phase_linking['inversion.phaseLinkingMethod']['value']))
                fcfg.write('miaplpy.inversion.sbw_connNum              = %s   # auto for 10, number of consecutive interferograms\n' % (jobmintpy.phase_linking['inversion.sbw_connNum']['value']))
                fcfg.write('miaplpy.inversion.PsNumShp                 = %s   # auto for 10, number of shps for ps candidates\n' % (jobmintpy.phase_linking['inversion.PsNumShp']['value']))
                fcfg.write('miaplpy.inversion.mask                     = %s   # mask file for phase inversion, auto for None\n' % (jobmintpy.phase_linking['inversion.mask']['value']))

                fcfg.write('\n')
                fcfg.write('########## 4. Select the network and generate interferograms\n')
                fcfg.write('## Different pairs of interferograms can be choosed for unwrapping.\n')
                fcfg.write('## Following is a short description of each type\n')
                fcfg.write('## 1. mini_stacks: It unwraps single reference interferograms in each ministack which is formed from images of each year\n')
                fcfg.write('## 2. single_reference: It unwraps the single reference interferograms of the whole stack using referenceDate.\n')
                fcfg.write('## 3. delaunay: delaunay triangles with temporal and spatial baseline threshold.\n')
                fcfg.write('## 4. sequential: sequential interferograms\n')
                fcfg.write('## You may also unwrap certain combination of pairs by giving them in a text file as miaplpy.interferograms.list\n')
                fcfg.write('miaplpy.interferograms.networkType             = %s      # [mini_stacks, single_reference, sequential, delaunay] default: single_reference\n' % (jobmintpy.generate_ifgram['interferograms.networkType']['value']))
                fcfg.write('miaplpy.interferograms.list                    = %s      # auto for None, list of interferograms to unwrap in a text file\n' % (jobmintpy.generate_ifgram['interferograms.list']['value']))
                fcfg.write('miaplpy.interferograms.referenceDate           = %s      # auto for the middle image\n' % (jobmintpy.generate_ifgram['interferograms.referenceDate']['value']))
                fcfg.write('miaplpy.interferograms.filterStrength          = %s      # [0-1], interferogram smoothing factor, auto for 0\n' % (jobmintpy.generate_ifgram['interferograms.filterStrength']['value']))
                fcfg.write('miaplpy.interferograms.ministackRefMonth       = %s      # The month of the year that coherence is high to choose reference from, default: 06\n' % (jobmintpy.generate_ifgram['interferograms.ministackRefMonth']['value']))
                fcfg.write('miaplpy.interferograms.connNum                 = %s      # Number of connections in sequential interferograms, auto for 3\n' % (jobmintpy.generate_ifgram['interferograms.connNum']['value']))
                fcfg.write('miaplpy.interferograms.delaunayBaselineRatio   = %s      # [1, 4, 9] Ratio between perpendiclar and temporal baselines, auto for 4\n' % (jobmintpy.generate_ifgram['interferograms.delaunayBaselineRatio']['value']))
                fcfg.write('miaplpy.interferograms.delaunayTempThresh      = %s      # [days] temporal threshold for delaunay triangles, auto for 120\n' % (jobmintpy.generate_ifgram['interferograms.delaunayTempThresh']['value']))
                fcfg.write('miaplpy.interferograms.delaunayPerpThresh      = %s      # [meters] Perp baseline threshold for delaunay triangles, auto for 200\n' % (jobmintpy.generate_ifgram['interferograms.delaunayPerpThresh']['value']))
                fcfg.write('miaplpy.interferograms.oneYear                 = %s      # [yes, no ] Add one year interferograms, auto for no\n' % (jobmintpy.generate_ifgram['interferograms.oneYear']['value']))

                fcfg.write('\n')
                fcfg.write('########## 5. Unwrap interferograms\n')
                fcfg.write('miaplpy.unwrap.two-stage                  = %s     # [yes, no], auto for yes, Do two stage unwrapping\n' % (jobmintpy.unwrap_ifgram['unwrap.twostage']['value']))
                fcfg.write('miaplpy.unwrap.removeFilter               = %s     # [yes, no], auto for yes, remove filter after unwrap\n' % (jobmintpy.unwrap_ifgram['unwrap.removeFilter']['value']))
                fcfg.write('miaplpy.unwrap.snaphu.maxDiscontinuity    = %s     # (snaphu parameter) max phase discontinuity in cycle, auto for 1.2\n' % (jobmintpy.unwrap_ifgram['unwrap.snaphu.maxDiscontinuity']['value']))
                fcfg.write('miaplpy.unwrap.snaphu.initMethod          = %s     # [MCF, MST] auto for MCF\n' % (jobmintpy.unwrap_ifgram['unwrap.snaphu.initMethod']['value']))
                fcfg.write('miaplpy.unwrap.snaphu.tileNumPixels       = %s     # number of pixels in a tile, auto for 10000000\n' % (jobmintpy.unwrap_ifgram['unwrap.snaphu.tileNumPixels']['value']))
                fcfg.write('miaplpy.unwrap.mask                       = %s     # auto for None\n' % (jobmintpy.unwrap_ifgram['unwrap.mask']['value']))

                fcfg.write('\n')
                fcfg.write('########## 6,7. Load interferograms\n')
                fcfg.write('# Set options in mintpy config file\n')

                fcfg.write('\n')
                fcfg.write('########## 8. Invert network of interferograms to timeseries\n')
                fcfg.write('miaplpy.timeseries.tempCohType            = %s     # [full, average], auto for full.\n' % (jobmintpy.invert_network['timeseries.tempCohType']['value']))
                fcfg.write('miaplpy.timeseries.minTempCoh             = %s     # auto for 0.5\n' % (jobmintpy.invert_network['timeseries.minTempCoh']['value']))
                fcfg.write('miaplpy.timeseries.waterMask              = %s     # auto for None, path to water mask\n' % (jobmintpy.invert_network['timeseries.waterMask']['value']))
                fcfg.write('miaplpy.timeseries.shadowMask             = %s     # [yes, no] auto for no, using shadow mask to mask final results\n' % (jobmintpy.invert_network['timeseries.shadowMask']['value']))
                fcfg.write('miaplpy.timeseries.residualNorm           = %s     #[L1, L2], auto for L2, norm minimization solution\n' % (jobmintpy.invert_network['timeseries.residualNorm']['value']))
                fcfg.write('miaplpy.timeseries.L1smoothingFactor      = %s     #[0-1] auto for 0.01\n' % (jobmintpy.invert_network['timeseries.L1smoothingFactor']['value']))
                fcfg.write('miaplpy.timeseries.L2weightFunc           = %s     #[var / fim / coh / no], auto for var\n' % (jobmintpy.invert_network['timeseries.L2weightFunc']['value']))
                fcfg.write('miaplpy.timeseries.minNormVelocity        = %s     #[yes / no], auto for yes, min-norm deformation velocity / phase\n' % (jobmintpy.invert_network['timeseries.minNormVelocity']['value']))

                fcfg.write('\n')
                fcfg.write('########## 9. Timeseries Correction\n')
                fcfg.write('# Set options in mintpy config file\n')

                fcfg.write('\n')
                fcfg.write('##------------------------ smallbaselineApp.cfg ------------------------##\n')
                fcfg.write('########## computing resource configuration\n')
                fcfg.write('mintpy.compute.maxMemory = auto #[float > 0.0], auto for 4, max memory to allocate in GB\n')
                fcfg.write('## parallel processing with dask\n')
                fcfg.write('## currently apply to steps: invert_network, correct_topography\n')
                fcfg.write('## cluster   = none to turn off the parallel computing\n')
                fcfg.write('## numWorker = all  to use all locally available cores (for cluster = local only)\n')
                fcfg.write('## config    = none to rollback to the default name (same as the cluster type; for cluster != local)\n')
                fcfg.write('mintpy.compute.cluster   = %s #[local / slurm / pbs / lsf / none], auto for none, cluster type\n' % (jobmintpy.mintpyparameter['compute.cluster']['value']))
                fcfg.write('mintpy.compute.numWorker = %s #[int > 1 / all], auto for 4 (local) or 40 (non-local), num of workers\n' % (jobmintpy.mintpyparameter['compute.numWorker']['value']))
                fcfg.write('mintpy.compute.config    = %s #[none / slurm / pbs / lsf ], auto for none (same as cluster), config name\n' % (jobmintpy.mintpyparameter['compute.numWorker']['value']))
                
                fcfg.write('\n')
                fcfg.write('########## reference_point\n')
                fcfg.write('## Reference all interferograms to one common point in space\n')
                fcfg.write('## auto - randomly select a pixel with coherence > minCoherence\n')
                fcfg.write('## however, manually specify using prior knowledge of the study area is highly recommended\n')
                fcfg.write('##   with the following guideline (section 4.3 in Yunjun et al., 2019):\n')
                fcfg.write('## 1) located in a coherence area, to minimize the decorrelation effect.\n')
                fcfg.write('## 2) not affected by strong atmospheric turbulence, i.e. ionospheric streaks\n')
                fcfg.write('## 3) close to and with similar elevation as the AOI, to minimize the impact of spatially correlated atmospheric delay\n')
                fcfg.write('mintpy.reference.yx            = %s   #[257,151 / auto]\n' % (jobmintpy.mintpyparameter['reference.yx']['value']))
                fcfg.write('mintpy.reference.lalo          = %s   #[31.8,130.8 / auto]\n' % (jobmintpy.mintpyparameter['reference.lalo']['value']))
                fcfg.write('mintpy.reference.maskFile      = %s   #[filename / no], auto for maskConnComp.h5\n' % (jobmintpy.mintpyparameter['reference.maskFile']['value']))
                fcfg.write('mintpy.reference.coherenceFile = %s   #[filename], auto for avgSpatialCoh.h5\n' % (jobmintpy.mintpyparameter['reference.coherenceFile']['value']))
                fcfg.write('mintpy.reference.minCoherence  = %s   #[0.0-1.0], auto for 0.85, minimum coherence for auto method\n' % (jobmintpy.mintpyparameter['reference.minCoherence']['value']))

                fcfg.write('\n')
                fcfg.write('########## quick_overview\n')
                fcfg.write('## A quick assessment of:\n')
                fcfg.write('## 1) possible ground deformation\n')
                fcfg.write('##    using the velocity from the traditional interferogram stacking\n')
                fcfg.write('##    reference: Zebker et al. (1997, JGR)\n')
                fcfg.write('## 2) distribution of phase unwrapping error\n')
                fcfg.write('##    from the number of interferogram triplets with non-zero integer ambiguity of closue phase\n')
                fcfg.write('##    reference: T_int in Yunjun et al. (2019, CAGEO). Related to section 3.2, equation (8-9) and Fig. 3d-e.\n')

                fcfg.write('\n')
                fcfg.write('########## correct_unwrap_error (optional)\n')
                fcfg.write('## connected components (mintpy.load.connCompFile) are required for this step.\n')
                fcfg.write('## reference: Yunjun et al. (2019, section 3)\n')
                fcfg.write('## supported methods:\n')
                fcfg.write('## a. phase_closure          - suitable for highly redundant network\n')
                fcfg.write('## b. bridging               - suitable for regions separated by narrow decorrelated features, e.g. rivers, narrow water bodies\n')
                fcfg.write('## c. bridging+phase_closure - recommended when there is a small percentage of errors left after bridging\n')
                fcfg.write('mintpy.unwrapError.method          = %s  #[bridging / phase_closure / bridging+phase_closure / no], auto for no\n' % (jobmintpy.mintpyparameter['unwrapError.method']['value']))
                fcfg.write('mintpy.unwrapError.waterMaskFile   = %s  #[waterMask.h5 / no], auto for waterMask.h5 or no [if not found]\n' % (jobmintpy.mintpyparameter['unwrapError.waterMaskFile']['value']))

                fcfg.write('\n')
                fcfg.write('## phase_closure options:\n')
                fcfg.write('## numSample - a region-based strategy is implemented to speedup L1-norm regularized least squares inversion.\n')
                fcfg.write('##     Instead of inverting every pixel for the integer ambiguity, a common connected component mask is generated,\n')
                fcfg.write('##     for each common conn. comp., numSample pixels are radomly selected for inversion, and the median value of the results\n')
                fcfg.write('##     are used for all pixels within this common conn. comp.\n')
                fcfg.write('mintpy.unwrapError.numSample       = %s  #[int>1], auto for 100, number of samples to invert for common conn. comp.\n' % (jobmintpy.mintpyparameter['unwrapError.numSample']['value']))

                fcfg.write('\n')
                fcfg.write('## briding options:\n')
                fcfg.write('## ramp - a phase ramp could be estimated based on the largest reliable region, removed from the entire interferogram\n')
                fcfg.write('##     before estimating the phase difference between reliable regions and added back after the correction.\n')
                fcfg.write('## bridgePtsRadius - half size of the window used to calculate the median value of phase difference\n')
                fcfg.write('mintpy.unwrapError.ramp            = %s  #[linear / quadratic], auto for no; recommend linear for L-band data\n' % (jobmintpy.mintpyparameter['unwrapError.ramp']['value']))
                fcfg.write('mintpy.unwrapError.bridgePtsRadius = %s  #[1-inf], auto for 50, half size of the window around end points\n' % (jobmintpy.mintpyparameter['unwrapError.bridgePtsRadius']['value']))

                fcfg.write('\n')
                fcfg.write('########## correct_LOD\n')
                fcfg.write('## Local Oscillator Drift (LOD) correction (for Envisat only)\n')
                fcfg.write('## reference: Marinkovic and Larsen (2013, Proc. LPS)\n')
                fcfg.write('## automatically applied to Envisat data (identified via PLATFORM attribute)\n')
                fcfg.write('## and skipped for all the other satellites.\n')

                fcfg.write('\n')
                fcfg.write('########## correct_SET\n')
                fcfg.write('## Solid Earth tides (SET) correction [need to install insarlab/PySolid]\n')
                fcfg.write('## reference: Milbert (2018); Fattahi et al. (2020, AGU)\n')
                fcfg.write('mintpy.solidEarthTides = %s #[yes / no], auto for no\n' % (jobmintpy.mintpyparameter['solidEarthTides']['value']))

                fcfg.write('\n')
                fcfg.write('########## correct_troposphere (optional but recommended)\n')
                fcfg.write('## correct tropospheric delay using the following methods:\n')
                fcfg.write('## a. height_correlation - correct stratified tropospheric delay (Doin et al., 2009, J Applied Geop)\n')
                fcfg.write('## b. pyaps - use Global Atmospheric Models (GAMs) data (Jolivet et al., 2011; 2014)\n')
                fcfg.write('##      ERA5  - ERA-5       from ECMWF [need to install PyAPS from GitHub; recommended and turn ON by default]\n')
                fcfg.write('##      MERRA - MERRA-2     from NASA  [need to install PyAPS from Caltech/EarthDef]\n')
                fcfg.write('##      NARR  - NARR        from NOAA  [need to install PyAPS from Caltech/EarthDef; recommended for N America]\n')
                fcfg.write('## c. gacos - use GACOS with the iterative tropospheric decomposition model (Yu et al., 2018a, RSE; 2018b, JGR)\n')
                fcfg.write('##      need to manually download GACOS products at http://www.gacos.net for all acquisitions before running this step\n')
                fcfg.write('mintpy.troposphericDelay.method = %s  #[pyaps / height_correlation / gacos / no], auto for pyaps\n' % (jobmintpy.mintpyparameter['troposphericDelay.method']['value']))

                fcfg.write('\n')
                fcfg.write('## Notes for pyaps:\n')
                fcfg.write('## a. GAM data latency: with the most recent SAR data, there will be GAM data missing, the correction\n')
                fcfg.write('##    will be applied to dates with GAM data available and skipped for the others.\n')
                fcfg.write('## b. WEATHER_DIR: if you define an environment variable named WEATHER_DIR to contain the path to a\n')
                fcfg.write('##    directory, then MintPy applications will download the GAM files into the indicated directory.\n')
                fcfg.write('##    MintPy application will look for the GAM files in the directory before downloading a new one to\n')
                fcfg.write('##    prevent downloading multiple copies if you work with different dataset that cover the same date/time.\n')
                fcfg.write('mintpy.troposphericDelay.weatherModel = %s  #[ERA5 / MERRA / NARR], auto for ERA5\n' % (jobmintpy.mintpyparameter['troposphericDelay.weatherModel']['value']))
                fcfg.write('mintpy.troposphericDelay.weatherDir   = %s  #[path2directory], auto for WEATHER_DIR or "./"\n' % (jobmintpy.mintpyparameter['troposphericDelay.weatherDir']['value']))

                fcfg.write('\n')
                fcfg.write('## Notes for height_correlation:\n')
                fcfg.write('## Extra multilooking is applied to estimate the empirical phase/elevation ratio ONLY.\n')
                fcfg.write('## For an dataset with 5 by 15 looks, looks=8 will generate phase with (5*8) by (15*8) looks\n')
                fcfg.write('## to estimate the empirical parameter; then apply the correction to original phase (with 5 by 15 looks),\n')
                fcfg.write('## if the phase/elevation correlation is larger than minCorrelation.\n')
                fcfg.write('mintpy.troposphericDelay.polyOrder      = %s  #[1 / 2 / 3], auto for 1\n' % (jobmintpy.mintpyparameter['troposphericDelay.polyOrder']['value']))
                fcfg.write('mintpy.troposphericDelay.looks          = %s  #[1-inf], auto for 8, extra multilooking num\n' % (jobmintpy.mintpyparameter['troposphericDelay.looks']['value']))
                fcfg.write('mintpy.troposphericDelay.minCorrelation = %s  #[0.0-1.0], auto for 0\n' % (jobmintpy.mintpyparameter['troposphericDelay.minCorrelation']['value']))

                fcfg.write('\n')
                fcfg.write('## Notes for gacos:\n')
                fcfg.write('## Set the path below to directory that contains the downloaded *.ztd* files\n')
                fcfg.write('mintpy.troposphericDelay.gacosDir = %s # [path2directory], auto for "./GACOS"\n' % (jobmintpy.mintpyparameter['troposphericDelay.gacosDir']['value']))

                fcfg.write('\n')
                fcfg.write('########## deramp (optional)\n')
                fcfg.write('## Estimate and remove a phase ramp for each acquisition based on the reliable pixels.\n')
                fcfg.write('## Recommended for localized deformation signals, i.e. volcanic deformation, landslide and land subsidence, etc.\n')
                fcfg.write('## NOT recommended for long spatial wavelength deformation signals, i.e. co-, post- and inter-seimic deformation.\n')
                fcfg.write('mintpy.deramp          = %s  #[no / linear / quadratic], auto for no - no ramp will be removed\n' % (jobmintpy.mintpyparameter['deramp']['value']))
                fcfg.write('mintpy.deramp.maskFile = %s  #[filename / no], auto for maskTempCoh.h5, mask file for ramp estimation\n' % (jobmintpy.mintpyparameter['deramp.maskFile']['value']))

                fcfg.write('\n')
                fcfg.write('########## correct_topography (optional but recommended)\n')
                fcfg.write('## Topographic residual (DEM error) correction\n')
                fcfg.write('## reference: Fattahi and Amelung (2013, IEEE-TGRS)\n')
                fcfg.write('## stepFuncDate      - specify stepFuncDate option if you know there are sudden displacement jump in your area,\n')
                fcfg.write('##                     e.g. volcanic eruption, or earthquake\n')
                fcfg.write('## excludeDate       - dates excluded for the error estimation\n')
                fcfg.write('## pixelwiseGeometry - use pixel-wise geometry (incidence angle & slant range distance)\n')
                fcfg.write('##                     yes - use pixel-wise geometry if they are available [slow; used by default]\n')
                fcfg.write('##                     no  - use the mean   geometry [fast]\n')
                fcfg.write('mintpy.topographicResidual                   = %s  #[yes / no], auto for yes\n' % (jobmintpy.mintpyparameter['topographicResidual']['value']))
                fcfg.write('mintpy.topographicResidual.polyOrder         = %s  #[1-inf], auto for 2, poly order of temporal deformation model\n' % (jobmintpy.mintpyparameter['topographicResidual.polyOrder']['value']))
                fcfg.write('mintpy.topographicResidual.phaseVelocity     = %s  #[yes / no], auto for no - phase, use phase velocity for minimization\n' % (jobmintpy.mintpyparameter['topographicResidual.phaseVelocity']['value']))
                fcfg.write('mintpy.topographicResidual.stepFuncDate      = %s  #[20080529,20100611 / no], auto for no, date of step jump\n' % (jobmintpy.mintpyparameter['topographicResidual.stepFuncDate']['value']))
                fcfg.write('mintpy.topographicResidual.excludeDate       = %s  #[20070321 / txtFile / no], auto for exclude_date.txt\n' % (jobmintpy.mintpyparameter['topographicResidual.excludeDate']['value']))
                fcfg.write('mintpy.topographicResidual.pixelwiseGeometry = %s  #[yes / no], auto for yes, use pixel-wise geometry info\n' % (jobmintpy.mintpyparameter['topographicResidual.pixelwiseGeometry']['value']))

                fcfg.write('\n')
                fcfg.write('########## residual_RMS (root mean squares for noise evaluation)\n')
                fcfg.write('## Calculate the Root Mean Square (RMS) of residual phase time-series for each acquisition\n')
                fcfg.write('## reference: Yunjun et al. (2019, section 4.9 and 5.4)\n')
                fcfg.write('## To get rid of long wavelength component in space, a ramp is removed for each acquisition\n')
                fcfg.write('## Set optimal reference date to date with min RMS\n')
                fcfg.write('## Set exclude dates (outliers) to dates with RMS > cutoff * median RMS (Median Absolute Deviation)\n')
                fcfg.write('mintpy.residualRMS.maskFile = %s  #[file name / no], auto for maskTempCoh.h5, mask for ramp estimation\n' % (jobmintpy.mintpyparameter['residualRMS.maskFile']['value']))
                fcfg.write('mintpy.residualRMS.deramp   = %s  #[quadratic / linear / no], auto for quadratic\n' % (jobmintpy.mintpyparameter['residualRMS.deramp']['value']))
                fcfg.write('mintpy.residualRMS.cutoff   = %s  #[0.0-inf], auto for 3\n' % (jobmintpy.mintpyparameter['residualRMS.cutoff']['value']))

                fcfg.write('\n')
                fcfg.write('########## reference_date\n')
                fcfg.write('## Reference all time-series to one date in time\n')
                fcfg.write('## reference: Yunjun et al. (2019, section 4.9)\n')
                fcfg.write('## no     - do not change the default reference date (1st date)\n')
                fcfg.write('mintpy.reference.date = %s   #[reference_date.txt / 20090214 / no], auto for reference_date.txt\n' % (jobmintpy.mintpyparameter['reference.date']['value']))

                fcfg.write('\n')
                fcfg.write('########## velocity\n')
                fcfg.write('## Estimate linear velocity and its standard deviation from time-series\n')
                fcfg.write('## and from tropospheric delay file if exists.\n')
                fcfg.write('## reference: Fattahi and Amelung (2015, JGR)\n')
                fcfg.write('mintpy.velocity.excludeDate    = %s   #[exclude_date.txt / 20080520,20090817 / no], auto for exclude_date.txt\n' % (jobmintpy.mintpyparameter['velocity.excludeDate']['value']))
                fcfg.write('mintpy.velocity.startDate      = %s   #[20070101 / no], auto for no\n' % (jobmintpy.mintpyparameter['velocity.startDate']['value']))
                fcfg.write('mintpy.velocity.endDate        = %s   #[20101230 / no], auto for no\n' % (jobmintpy.mintpyparameter['velocity.endDate']['value']))

                fcfg.write('\n')
                fcfg.write('## Bootstrapping\n')
                fcfg.write('## refernce: Efron and Tibshirani (1986, Stat. Sci.)\n')
                fcfg.write('mintpy.velocity.bootstrap      = %s   #[yes / no], auto for no, use bootstrap\n' % (jobmintpy.mintpyparameter['velocity.bootstrap']['value']))
                fcfg.write('mintpy.velocity.bootstrapCount = %s   #[int>1], auto for 400, number of iterations for bootstrapping\n' % (jobmintpy.mintpyparameter['velocity.bootstrap']['value']))

                fcfg.write('\n')
                fcfg.write('########## geocode (post-processing)\n')
                fcfg.write('# for input dataset in radar coordinates only\n')
                fcfg.write('# commonly used resolution in meters and in degrees (on equator)\n')
                fcfg.write('# 100,         60,          50,          30,          20,          10\n')
                fcfg.write('# 0.000925926, 0.000555556, 0.000462963, 0.000277778, 0.000185185, 0.000092593\n')
                fcfg.write('mintpy.geocode              = %s  #[yes / no], auto for yes\n' % (jobmintpy.mintpyparameter['geocode']['value']))
                fcfg.write('mintpy.geocode.SNWE         = %s  #[-1.2,0.5,-92,-91 / none ], auto for none, output extent in degree\n' % (jobmintpy.mintpyparameter['geocode.SNWE']['value']))
                fcfg.write('mintpy.geocode.laloStep     = %s  #[-0.000555556,0.000555556 / None], auto for None, output resolution in degree\n' % (jobmintpy.mintpyparameter['geocode.laloStep']['value']))
                fcfg.write('mintpy.geocode.interpMethod = %s  #[nearest], auto for nearest, interpolation method\n' % (jobmintpy.mintpyparameter['geocode.interpMethod']['value']))
                fcfg.write('mintpy.geocode.fillValue    = %s  #[np.nan, 0, ...], auto for np.nan, fill value for outliers.\n' % (jobmintpy.mintpyparameter['geocode.fillValue']['value']))

                fcfg.write('\n')
                fcfg.write('########## google_earth (post-processing)\n')
                fcfg.write('mintpy.save.kmz             = %s   #[yes / no], auto for yes, save geocoded velocity to Google Earth KMZ file\n' % (jobmintpy.mintpyparameter['save.kmz']['value']))

                fcfg.write('\n')
                fcfg.write('########## hdfeos5 (post-processing)\n')
                fcfg.write('mintpy.save.hdfEos5         = %s   #[yes / no], auto for no, save time-series to HDF-EOS5 format\n' % (jobmintpy.mintpyparameter['save.hdfEos5']['value']))
                fcfg.write('mintpy.save.hdfEos5.update  = %s   #[yes / no], auto for no, put XXXXXXXX as endDate in output filename\n' % (jobmintpy.mintpyparameter['save.hdfEos5.update']['value']))
                fcfg.write('mintpy.save.hdfEos5.subset  = %s   #[yes / no], auto for no, put subset range info   in output filename\n' % (jobmintpy.mintpyparameter['save.hdfEos5.subset']['value']))

                fcfg.write('\n')
                fcfg.write('########## plot\n')
                fcfg.write('mintpy.plot = %s   #[yes / no], auto for yes, plot files generated by default processing to pic folder\n' % (jobmintpy.mintpyparameter['plot']['value']))

        usermessage.ezprint('Configuration file written in %s' % (file),log,verbose)

################################################################################
## Extraction of displacements for MiaplPy FUNCTION
################################################################################
def importmiaplpyresults(workdirectory, 
        job = None, 
        dataset = None, 
        nodata = np.nan,
        meter_mode = 'UTM',
        verbose: Optional[bool] = True,
        log: Optional[bool] = None):
        """Import the MiaplPy results into an EZ-InSAR data file

        The function will import the MiaplPy results into a format for EZ-InSAR.

        Args:
                workdirectory (str): Work directory
                job (``ezinsar.job``): EZ-InSAR tsprocessing job. [Default: `None`]
                dataset (str): Selected dataset. [Default: `None`]
                applymask (bool): Apply the mask. [Default: `True`]
                nodata (float): No data value [Default: ``np.nan``]
                meter_mode (str): UTM grid [Default: ``UTM``]
                verbose: (bool): Verbose. [Default: `True`]
                log (str): Log file. [Default: `None`]

        Returns:
                ``ezinsar.data``: EZ-InSAR data class
        
        """
        cur_dir = os.getcwd()

        if not 'miaplpytsprocessing' in str(type(job)):
                raise ValueError(usermessage.errormsg(__name__,importmiaplpyresults.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-MiaplPy processing.',None))

        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,importmiaplpyresults.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if not log == None: 
                if not isinstance(log,str): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,importmiaplpyresults.__name__,__file__,__copyright__,
                                'log','str',log))

        if not os.path.isdir(workdirectory):
                raise ValueError(usermessage.errormsg(__name__,importmiaplpyresults.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        
        usermessage.openingmsg(__name__,importmiaplpyresults.__name__,__file__,__copyright__,'Import the MiaplPy results',log,verbose)

        os.chdir(workdirectory)

        ## Initialisation of the dataset
        usermessage.ezprint('Initialisation of the dataset...',log,verbose)
        data = ezinsardata.displacement()
        usermessage.ezprint('\tdone',log,verbose)

        ## Detection of the dataset
        if dataset == None: 
                listfile = glob.glob(workdirectory+os.sep+'network*'+os.sep+'geo'+os.sep+'geo_timeseries_*.h5')
                nb_process = []
                for li in listfile: 
                        nb_process.append(len(li.split(os.sep)[-1].split('_')))
                dataset = listfile[np.argmax(nb_process)]
                usermessage.ezprint('Import the dataset %s' % (dataset),log,verbose)
        else: 
                dataset = workdirectory+os.sep+'geo'+os.sep+dataset


        ## For the metadata
        usermessage.ezprint('Extract the metadata...',log,verbose)
        
        data.mode['value'] = 'LOS'
        
        if not job == None: 
                data.datainformation['Name'] = None
                data.datainformation['Target'] = job.title
                data.datainformation['InSAR_Processor'] = job.ifgprocessor
                data.datainformation['Satellite'] = job.satellite
                data.datainformation['Mode'] = job.satmode
                data.datainformation['Pass'] = job.relorbit
                data.datainformation['Track'] = job.satpass

                if job.satellite == 'S1': 
                        data.datainformation['Wavelength'] = 0.055
                elif job.satellite in ['TSX','PAZ','CSK']: 
                        data.datainformation['Wavelength'] = 0.031

        data.datainformation['TS_Processor'] = 'miaplpy'
        data.datainformation['Approach'] = 'Phase-Linking'
        data.datainformation['Date'] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        data.datainformation['Importation'] = 'regular'
        data.datainformation['Processing'] = 'raw'

        if not job == None:
                import ezinsar.job as ez
                tmpfile = constants.__cachedir__+os.sep+'jobtmp_'+''.join(random.choice(string.ascii_lowercase) for i in range(16))+'.ei'
                ez.save(job,tmpfile,verbose=False)

                with open(tmpfile,'r') as fi: 
                        content = fi.readlines()

                if os.path.isfile(tmpfile): 
                        os.remove(tmpfile)

                data.datainformation['Metadata_processing'] = content

        data.datainformation['Path'] = workdirectory

        usermessage.ezprint('\tdone',log,verbose)

        ## For the temporal data
        usermessage.ezprint('Extract the temporal information...',log,verbose)

        with h5py.File(dataset, "r") as f:
                tmp = f['date'][()]

        data.dates['value'] = []
        for di in tmp:
                a = di.decode('UTF-8') 
                data.dates['value'].append(datetime.strptime(a,"%Y%m%d"))
        data.dates['value'] = np.array(data.dates['value'])

        data.n_image['value'] = int(len(data.dates['value']))

        # data.n_ifg['value'] = int(tmp['n_ifg'][0][0])

        if not job == None: 
                data.date_ref['value'] = datetime.strptime(job.mintpyparameter['reference.date']['value'],"%Y%m%d")

        # data.ifg_date['value'] = np.array(tmp)

        usermessage.ezprint('\tdone',log,verbose)

        ## For the spatial data
        usermessage.ezprint('Extract the spatial information...',log,verbose)
        with h5py.File(os.path.dirname(dataset)+os.sep+'geo_geometryRadar.h5', "r") as f:
                # if 'latitude' in list(f.keys()): 
                #         data.lon_grid['value'] = f['latitude'][()]
                #         data.lat_grid['value'] = f['longitude'][()]

                # else: 
                xmin = float(f['/'].attrs['X_FIRST'])
                xmax = float(f['/'].attrs['X_FIRST']) + float(f['/'].attrs['X_STEP']) * float(f['/'].attrs['WIDTH'])

                ymin = float(f['/'].attrs['Y_FIRST']) + float(f['/'].attrs['Y_STEP']) * float(f['/'].attrs['LENGTH'])
                ymax = float(f['/'].attrs['Y_FIRST']) 
                
                a, b = np.meshgrid(
                        np.linspace(xmin,xmax,int(f['/'].attrs['WIDTH'])),
                        np.linspace(ymin,ymax,int(f['/'].attrs['LENGTH'])),
                        )               

                data.lon_grid['value'] = a 
                data.lat_grid['value'] = b

        if meter_mode == 'UTM': 
                utm_crs_list = pyproj.database.query_utm_crs_info(
                        datum_name="WGS 84",
                        area_of_interest=pyproj.aoi.AreaOfInterest(
                                west_lon_degree=np.nanmin(data.lon_grid['value']),
                                south_lat_degree=np.nanmin(data.lat_grid['value']),
                                east_lon_degree=np.nanmax(data.lon_grid['value']),
                                north_lat_degree=np.nanmax(data.lat_grid['value']),
                                ),
                        )
                meter_mode = utm_crs_list[0].code

        latlon_to_meter = pyproj.Transformer.from_crs('epsg:4326','epsg:%s' % (meter_mode))
        data.x_utm['value'], data.y_utm['value'] = latlon_to_meter.transform(data.lat_grid['value'],data.lon_grid['value'])
        data.code_meter['value'] = 'epsg:%s' % (meter_mode)

        usermessage.ezprint('\tdone',log,verbose)

        ## For the ground data
        usermessage.ezprint('Extract the ground information...',log,verbose)

        with h5py.File(os.path.dirname(dataset)+os.sep+'geo_geometryRadar.h5', "r") as f:
                data.hgt_grid['value'] = f['height'][()]
                data.inc_angle['value'] = f['incidenceAngle'][()]

                if 'azimuthAngle' in list(f.keys()): 
                        data.heading['value'] = f['azimuthAngle'][()]
        
        usermessage.ezprint('\tdone',log,verbose)

        ## Read the mask 
        with h5py.File(os.path.dirname(dataset)+os.sep+'geo_maskTempCoh.h5', "r") as f:
                mask = f['mask'][()]

        ## For the displacement data
        usermessage.ezprint('Extract the displacement data...',log,verbose)

        with h5py.File(dataset, "r") as f:
                tmpdisp = f['timeseries'][()]

        data.dispLOS['value'] = np.empty((len(data.lon_grid['value'][mask].flatten()),len(data.dates['value'])))
        for a in range(tmpdisp.shape[0]):
                data.dispLOS['value'][:,a] = tmpdisp[a,:,:][mask].flatten()*1000

        with h5py.File(os.path.dirname(dataset)+os.sep+'geo_velocity.h5', "r") as f:
                data.rateLOS['value'] = f['velocity'][()][mask].flatten()*1000
                data.sigmarateLOS['value'] = f['velocityStd'][()][mask].flatten()*1000

        usermessage.ezprint('\tdone',log,verbose)


        data.x_utm['value'] = data.x_utm['value'][mask].flatten()
        data.y_utm['value'] = data.y_utm['value'][mask].flatten()
        data.lon['value'] = data.lon_grid['value'][mask].flatten()
        data.lat['value'] = data.lat_grid['value'][mask].flatten()

        ## For the reference point
        usermessage.ezprint('Extract the reference-point information...',log,verbose)

        data.referencepoint['value']['index'] = 0
        if not job == None: 
                try: 
                        data.referencepoint['value']['lat_pt_ref'] = float(job.mintpyparameter['reference.lalo']['value'].split(',')[1])
                        data.referencepoint['value']['lon_pt_ref'] = float(job.mintpyparameter['reference.lalo']['value'].split(',')[0])
                except: 
                        data.referencepoint['value']['lat_pt_ref'] = float(0)
                        data.referencepoint['value']['lon_pt_ref'] = float(0)
                data.referencepoint['value']['lon_pt_refarea'] = 0
                data.referencepoint['value']['lat_pt_refarea'] = 0
                data.referencepoint['value']['radius'] = 0
                data.referencepoint['value']['rateLOS'] = 0

        usermessage.ezprint('\tdone',log,verbose)

        ## For the baselines
        usermessage.ezprint('Extract the perpendicular baselines...',log,verbose)

        with h5py.File(dataset, "r") as f:
                data.bperp['value'] = f['bperp'][()]
                
        os.chdir(cur_dir)

        return data