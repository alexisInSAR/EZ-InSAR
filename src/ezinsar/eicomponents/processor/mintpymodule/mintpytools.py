#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to add some tools for the MintPy processing class

The module adds some tools for the MintPy processing class. 
    
    (From `ezinsar` package)

Changelog:
        * 1.1.1: Change the import line, Dec. 2025, Alexis Hrysiewicz
        * 1.1.0: Add the possibility to run MintPy in a different conda env, Oct. 2025, Alexis Hrysiewicz
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
## Wrapper for MintPy allowing logging of processing 
################################################################################
def wrappermintpy(job,
                stepi,
                verbose,
                log):
        """Run a subprocess for MintPy 

        The function will run a subprocess for MintPy 

        Args:   
                job (``ezinsar.job``): EZ-InSAR tsprocessing job with MintPy
                stepi (str): Processing step
                verbose (bool): verbose
                log (str): Log file

        Returns 
                ``ezinsar.job``: EZ-InSAR tsprocessing job with MintPy

        """

        ##Write the config file 
        writecfg(job, 
                file = job.pathmintpyconfig,
                verbose = False,
                log = job.log)

        # Old version without the logging 
        # argsmintpy = Namespace(argv = [job.pathmintpyconfig, '--dir', job.workdirectory, '--dostep', stepi],
        #         customTemplateFile=job.pathmintpyconfig, 
        #         doStep= stepi, 
        #         endStep= stepi, 
        #         generate_template=False, 
        #         plot=False, 
        #         print_template=False, 
        #         runSteps= [stepi], 
        #         startStep= stepi, 
        #         version=False, 
        #         workDir= job.workdirectory)
        # usermessage.ezprint('Minpty input parameters:\n\t%s' % (argsmintpy),job.log,verbose)
        # usermessage.ezprint('Run the MintPy step: %s with the command mintpy.smallbaselineApp.run_smallbaselineApp(argsmintpy)' % (stepi),job.log,verbose)
        # mintpy.smallbaselineApp.run_smallbaselineApp(argsmintpy)
        # exec("job.%s['done']['value'] = True" % (stepi))

        if not stepi == 'extract_res': 
                my_env = os.environ.copy()
                my_env["PATH"] = f"/usr/local/bin:{my_env['PATH']}"

                usermessage.ezprint('Run MintPy:',log,verbose)

                ## Creation of the command        
                cmd = 'smallbaselineApp.py --dir %s --dostep %s %s' % (job.workdirectory,
                                                                stepi,
                                                                job.pathmintpyconfig)
                
                if not constants.__mintpycondaenv__ == 'default': 
                        cmd = 'conda run -n %s %s' % (constants.__mintpycondaenv__,cmd)
                
                usermessage.ezprint('\tCommand: %s' % (cmd),log,verbose)

                pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, env=my_env)
                
                try: 
                        while (line := pr.stdout.readline()) != "":
                                usermessage.ezprint(line.replace('\n',' '),log,verbose)

                        if not len("".join(pr.stderr.readline().strip().split())) == 0:
                                while (line := pr.stderr.readline()):
                                        usermessage.ezprint(line.replace('\n',' '),log,verbose)  
                                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the MintPy processing',log))
                        
                except KeyboardInterrupt:
                        pr.terminate()
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the MintPy processing: user terminate',log))
                
                usermessage.ezprint('\tdone',log,verbose)

                exec("job.%s['done']['value'] = True" % (stepi))

        else: 
                ## Extraction of displacements
                data = importmintpyresults(job.workdirectory, 
                        applymask = job.extract_res['applymask']['value'],
                        job = job,
                        verbose = verbose,
                        log = job.log)

                name = 'TS_LOS_%s_%s_%s_%s_%s_%s_%s' % (job.satellite,
                                                job.satmode,
                                                job.relorbit,
                                                job.satpass,
                                                job.ifgprocessor,
                                                job.processor,
                                                job.mode.replace(os.sep,''))

                if job.extract_res['ecraseprevious']['value'] == True: 
                        usermessage.warningmsg(__name__,__name__,__file__,'The previous file will be replaced.',job.log,verbose)
                        name = job.workdirectory + os.sep + name + '.eidata'
                else: 
                        name = job.workdirectory + os.sep + '%s_%s.eidata' % (name,len(glob.glob(name+'*')))

                ezinsardata.saveEZdata(data,name,verbose = verbose,log = job.log)

        return job 

################################################################################
## Extraction of displacements for MintPy FUNCTION
################################################################################
def importmintpyresults(workdirectory, 
        job = None, 
        dataset = None, 
        applymask = True,
        nodata = np.nan,
        meter_mode = 'UTM',
        verbose: Optional[bool] = True,
        log: Optional[bool] = None):
        """Import the MintPy results into an EZ-InSAR data file

        The function will import the MintPy results into a format for EZ-InSAR.

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

        if not 'mintpytsprocessing' in str(type(job)):
                raise ValueError(usermessage.errormsg(__name__,importmintpyresults.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-StaMPS processing.',None))

        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,importmintpyresults.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if not log == None: 
                if not isinstance(log,str): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,importmintpyresults.__name__,__file__,__copyright__,
                                'log','str',log))

        if not os.path.isdir(workdirectory):
                raise ValueError(usermessage.errormsg(__name__,importmintpyresults.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        
        usermessage.openingmsg(__name__,importmintpyresults.__name__,__file__,__copyright__,'Import the MintPy results',log,verbose)

        os.chdir(workdirectory)

        ## Initialisation of the dataset
        usermessage.ezprint('Initialisation of the dataset...',log,verbose)
        data = ezinsardata.displacement()
        usermessage.ezprint('\tdone',log,verbose)

        ## Detection of the dataset
        if dataset == None: 
                listfile = glob.glob(workdirectory+os.sep+'geo'+os.sep+'geo_timeseries_*.h5')
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

        data.datainformation['TS_Processor'] = 'mintpy'
        data.datainformation['Approach'] = 'SBAS'
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
                data.date_ref['value'] = datetime.strptime(job.reference_date['reference.date']['value'],"%Y%m%d")

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
                data.dispLOS['value'] = f['timeseries'][()]
        
        for a in range(data.dispLOS['value'].shape[0]):
                data.dispLOS['value'][a,:,:][data.dispLOS['value'][a,:,:] == 0] = np.nan
                data.dispLOS['value'][a,:,:][data.dispLOS['value'][a,:,:] != np.nan] = data.dispLOS['value'][a,:,:][data.dispLOS['value'][a,:,:] != np.nan]*1000

                if applymask == True: 
                        data.dispLOS['value'][a,:,:][mask==False] = np.nan

                data.dispLOS['value'][a,:,:][np.isnan(data.dispLOS['value'][a,:,:])] = nodata
                        
        with h5py.File(os.path.dirname(dataset)+os.sep+'geo_velocity.h5', "r") as f:
                data.rateLOS['value'] = f['velocity'][()]
                data.sigmarateLOS['value'] = f['velocityStd'][()]

        data.rateLOS['value'][data.rateLOS['value']==0] = np.nan
        data.sigmarateLOS['value'][data.sigmarateLOS['value']==0] = np.nan

        data.rateLOS['value'][data.rateLOS['value'] != np.nan] = data.rateLOS['value'][data.rateLOS['value'] != np.nan]*1000
        data.sigmarateLOS['value'][data.sigmarateLOS['value'] != np.nan] = data.sigmarateLOS['value'][data.sigmarateLOS['value'] != np.nan]*1000

        if applymask == True: 
                data.rateLOS['value'][mask==False] = np.nan
                data.sigmarateLOS['value'][mask==False] = np.nan

        data.rateLOS['value'][np.isnan(data.rateLOS['value'])] = nodata
        data.sigmarateLOS['value'][np.isnan(data.sigmarateLOS['value'])] = nodata

        usermessage.ezprint('\tdone',log,verbose)

        ## For the reference point
        usermessage.ezprint('Extract the reference-point information...',log,verbose)

        data.referencepoint['value']['index'] = 0
        if not job == None: 
                try: 
                        data.referencepoint['value']['lat_pt_ref'] = float(job.reference_point['reference.lalo']['value'].split(',')[1])
                        data.referencepoint['value']['lon_pt_ref'] = float(job.reference_point['reference.lalo']['value'].split(',')[0])
                except: 
                        data.referencepoint['value']['lat_pt_ref'] = 0.0
                        data.referencepoint['value']['lon_pt_ref'] = 0.0

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
                fcfg.write('##------------------------ %s ------------------------##\n' % (file.split(os.sep)[-1]))
                fcfg.write('########## computing resource configuration\n')
                fcfg.write('mintpy.compute.maxMemory = %s #[float > 0.0], auto for 4, max memory to allocate in GB\n' % (jobmintpy.computer['compute.maxMemory']['value']))
                fcfg.write('## parallel processing with dask\n')
                fcfg.write('## currently apply to steps: invert_network, correct_topography\n')
                fcfg.write('## cluster   = none to turn off the parallel computing\n')
                fcfg.write('## numWorker = all  to use all of locally available cores (for cluster = local only)\n')
                fcfg.write('## numWorker = 80%  to use 80% of locally available cores (for cluster = local only)\n')
                fcfg.write('## config    = none to rollback to the default name (same as the cluster type; for cluster != local)\n')
                fcfg.write('mintpy.compute.cluster   = %s #[local / slurm / pbs / lsf / none], auto for none, cluster type\n' % (jobmintpy.computer['compute.cluster']['value']))
                fcfg.write('mintpy.compute.numWorker = %s #[int > 1 / all / num%%], auto for 4 (local) or 40 (slurm / pbs / lsf), num of workers\n' % (jobmintpy.computer['compute.numWorker']['value']))
                fcfg.write('mintpy.compute.config    = %s #[none / slurm / pbs / lsf ], auto for none (same as cluster), config name\n' % (jobmintpy.computer['compute.config']['value']))
                fcfg.write('\n')
                fcfg.write('\n')
                fcfg.write('########## 1. load_data\n')
                fcfg.write('##---------add attributes manually\n')
                fcfg.write('## MintPy requires attributes listed at: https://mintpy.readthedocs.io/en/latest/api/attributes/\n')
                fcfg.write('## Missing attributes can be added below manually (uncomment #), e.g.\n')

                fcfg.write('ORBIT_DIRECTION = %s\n' % (jobmintpy.satpass.lower()))
                fcfg.write('PLATFORM = %s\n' % (jobmintpy.satellite))

                fcfg.write('# ...\n')
                fcfg.write('## a. autoPath - automatic path pattern defined in mintpy.defaults.auto_path.AUTO_PATH_*\n')
                fcfg.write('## b. load_data.py -H to check more details and example inputs.\n')
                fcfg.write('## c. compression to save disk usage for ifgramStack.h5 file:\n')
                fcfg.write('## no   - save   0% disk usage, fast [default]\n')
                fcfg.write('## lzf  - save ~57% disk usage, relative slow\n')
                fcfg.write('## gzip - save ~62% disk usage, very slow [not recommend]\n')
                fcfg.write('mintpy.load.processor      = %s  #[isce, aria, hyp3, gmtsar, snap, gamma, roipac], auto for isce\n' % (jobmintpy.load_data['load.processor']['value']))
                fcfg.write('mintpy.load.autoPath       = %s  #[yes / no], auto for no, use pre-defined auto path\n' % (jobmintpy.load_data['load.autoPath']['value']))
                fcfg.write('mintpy.load.updateMode     = %s  #[yes / no], auto for yes, skip re-loading if HDF5 files are complete\n' % (jobmintpy.load_data['load.updateMode']['value']))
                fcfg.write('mintpy.load.compression    = %s  #[gzip / lzf / no], auto for no.\n' % (jobmintpy.load_data['load.compression']['value']))
                fcfg.write('##---------for ISCE only:\n')
                fcfg.write('mintpy.load.metaFile       = %s  #[path of common metadata file for the stack], i.e.: ./reference/IW1.xml, ./referenceShelve/data.dat\n' % (jobmintpy.load_data['load.metaFile']['value']))
                fcfg.write('mintpy.load.baselineDir    = %s  #[path of the baseline dir], i.e.: ./baselines\n' % (jobmintpy.load_data['load.baselineDir']['value']))
                fcfg.write('##---------interferogram datasets:\n')
                fcfg.write('mintpy.load.unwFile        = %s  #[path pattern of unwrapped interferogram files]\n' % (jobmintpy.load_data['load.unwFile']['value']))
                fcfg.write('mintpy.load.corFile        = %s  #[path pattern of spatial coherence       files]\n' % (jobmintpy.load_data['load.corFile']['value']))
                fcfg.write('mintpy.load.connCompFile   = %s  #[path pattern of connected components    files], optional but recommended\n' % (jobmintpy.load_data['load.connCompFile']['value']))
                fcfg.write('mintpy.load.intFile        = %s  #[path pattern of wrapped interferogram   files], optional\n' % (jobmintpy.load_data['load.intFile']['value']))
                fcfg.write('mintpy.load.ionoFile       = %s  #[path pattern of ionospheric delay       files], optional\n' % (jobmintpy.load_data['load.ionoFile']['value']))
                fcfg.write('mintpy.load.magFile        = %s  #[path pattern of interferogram magnitude files], optional\n' % (jobmintpy.load_data['load.magFile']['value']))
                fcfg.write('##---------offset datasets (optional):\n')
                fcfg.write('mintpy.load.azOffFile      = %s  #[path pattern of azimuth offset file], optional\n' % (jobmintpy.load_data['load.azOffFile']['value']))
                fcfg.write('mintpy.load.rgOffFile      = %s  #[path pattern of range   offset file], optional\n' % (jobmintpy.load_data['load.rgOffFile']['value']))
                fcfg.write('mintpy.load.azOffStdFile   = %s  #[path pattern of azimuth offset variance file], optional\n' % (jobmintpy.load_data['load.azOffStdFile']['value']))
                fcfg.write('mintpy.load.rgOffStdFile   = %s  #[path pattern of range   offset variance file], optional\n' % (jobmintpy.load_data['load.rgOffStdFile']['value']))
                fcfg.write('mintpy.load.offSnrFile     = %s  #[path pattern of offset signal-to-noise ratio file], optional\n' % (jobmintpy.load_data['load.offSnrFile']['value']))
                fcfg.write('##---------geometry datasets:\n')
                fcfg.write('mintpy.load.demFile        = %s  #[path of DEM file]\n' % (jobmintpy.load_data['load.demFile']['value']))
                fcfg.write('mintpy.load.lookupYFile    = %s  #[path of latitude /row   /y coordinate file], not required for geocoded data\n' % (jobmintpy.load_data['load.lookupYFile']['value']))
                fcfg.write('mintpy.load.lookupXFile    = %s  #[path of longitude/column/x coordinate file], not required for geocoded data\n' % (jobmintpy.load_data['load.lookupXFile']['value']))
                fcfg.write('mintpy.load.incAngleFile   = %s  #[path of incidence angle file], optional but recommended\n' % (jobmintpy.load_data['load.incAngleFile']['value']))
                fcfg.write('mintpy.load.azAngleFile    = %s  #[path of azimuth   angle file], optional\n' % (jobmintpy.load_data['load.azAngleFile']['value']))
                fcfg.write('mintpy.load.shadowMaskFile = %s  #[path of shadow mask file], optional but recommended\n' % (jobmintpy.load_data['load.shadowMaskFile']['value']))
                fcfg.write('mintpy.load.waterMaskFile  = %s  #[path of water  mask file], optional but recommended\n' % (jobmintpy.load_data['load.waterMaskFile']['value']))
                fcfg.write('mintpy.load.bperpFile      = %s  #[path pattern of 2D perpendicular baseline file], optional\n' % (jobmintpy.load_data['load.bperpFile']['value']))
                fcfg.write('##---------multilook (optional):\n')
                fcfg.write('## multilook while loading data with nearest interpolation, to reduce dataset size\n')
                fcfg.write('mintpy.load.ystep          = %s    #[int >= 1], auto for 1 - no multilooking\n' % (jobmintpy.load_data['load.ystep']['value']))
                fcfg.write('mintpy.load.xstep          = %s    #[int >= 1], auto for 1 - no multilooking\n' % (jobmintpy.load_data['load.xstep']['value']))
                fcfg.write('##---------subset (optional):\n')
                fcfg.write('## if both yx and lalo are specified, use lalo option unless a) no lookup file AND b) dataset is in radar coord\n')
                fcfg.write('mintpy.subset.yx           = %s    #[y0:y1,x0:x1 / no], auto for no\n' % (jobmintpy.load_data['subset.yx']['value']))
                fcfg.write('mintpy.subset.lalo         = %s    #[S:N,W:E / no], auto for no\n' % (jobmintpy.load_data['subset.lalo']['value']))
                fcfg.write('\n')
                fcfg.write('\n')
                fcfg.write('########## 2. modify_network\n')
                fcfg.write('## 1) Network modification based on temporal/perpendicular baselines, date, num of connections etc.\n')
                fcfg.write('mintpy.network.tempBaseMax     = %s  #[1-inf, no], auto for no, max temporal baseline in days\n' % (jobmintpy.modify_network['network.tempBaseMax']['value']))
                fcfg.write('mintpy.network.perpBaseMax     = %s  #[1-inf, no], auto for no, max perpendicular spatial baseline in meter\n' % (jobmintpy.modify_network['network.perpBaseMax']['value']))
                fcfg.write('mintpy.network.connNumMax      = %s  #[1-inf, no], auto for no, max number of neighbors for each acquisition\n' % (jobmintpy.modify_network['network.connNumMax']['value']))
                fcfg.write('mintpy.network.startDate       = %s  #[20090101 / no], auto for no\n' % (jobmintpy.modify_network['network.startDate']['value']))
                fcfg.write('mintpy.network.endDate         = %s  #[20110101 / no], auto for no\n' % (jobmintpy.modify_network['network.endDate']['value']))
                fcfg.write('mintpy.network.excludeDate     = %s  #[20080520,20090817 / no], auto for no\n' % (jobmintpy.modify_network['network.excludeDate']['value']))
                fcfg.write('mintpy.network.excludeIfgIndex = %s  #[1:5,25 / no], auto for no, list of ifg index (start from 0)\n' % (jobmintpy.modify_network['network.excludeIfgIndex']['value']))
                fcfg.write('mintpy.network.referenceFile   = %s  #[date12_list.txt / ifgramStack.h5 / no], auto for no\n' % (jobmintpy.modify_network['network.referenceFile']['value']))
                fcfg.write('\n')
                fcfg.write('## 2) Data-driven network modification\n')
                fcfg.write('## a - Coherence-based network modification = (threshold + MST) by default\n')
                fcfg.write('## reference: Yunjun et al. (2019, section 4.2 and 5.3.1); Chaussard et al. (2015, GRL)\n')
                fcfg.write('## It calculates a average coherence for each interferogram using spatial coherence based on input mask (with AOI)\n')
                fcfg.write('## Then it finds a minimum spanning tree (MST) network with inverse of average coherence as weight (keepMinSpanTree)\n')
                fcfg.write('## Next it excludes interferograms if a) the average coherence < minCoherence AND b) not in the MST network.\n')
                fcfg.write('mintpy.network.coherenceBased  = %s  #[yes / no], auto for no, exclude interferograms with coherence < minCoherence\n' % (jobmintpy.modify_network['network.coherenceBased']['value']))
                fcfg.write('mintpy.network.minCoherence    = %s  #[0.0-1.0], auto for 0.7\n' % (jobmintpy.modify_network['network.minCoherence']['value']))
                fcfg.write('\n')
                fcfg.write('## b - Effective Coherence Ratio network modification = (threshold + MST) by default\n')
                fcfg.write('## reference: Kang et al. (2021, RSE)\n')
                fcfg.write('## It calculates the area ratio of each interferogram that is above a spatial coherence threshold.\n')
                fcfg.write('## This threshold is defined as the spatial coherence of the interferograms within the input mask.\n')
                fcfg.write('## It then finds a minimum spanning tree (MST) network with inverse of the area ratio as weight (keepMinSpanTree)\n')
                fcfg.write('## Next it excludes interferograms if a) the area ratio < minAreaRatio AND b) not in the MST network.\n')
                fcfg.write('mintpy.network.areaRatioBased  = %s  #[yes / no], auto for no, exclude interferograms with area ratio < minAreaRatio\n' % (jobmintpy.modify_network['network.areaRatioBased']['value']))
                fcfg.write('mintpy.network.minAreaRatio    = %s  #[0.0-1.0], auto for 0.75\n' % (jobmintpy.modify_network['network.minAreaRatio']['value']))
                fcfg.write('\n')
                fcfg.write('## Additional common parameters for the 2) data-driven network modification\n')
                fcfg.write('mintpy.network.keepMinSpanTree = %s  #[yes / no], auto for yes, keep interferograms in Min Span Tree network\n' % (jobmintpy.modify_network['network.keepMinSpanTree']['value']))
                fcfg.write('mintpy.network.maskFile        = %s  #[file name, no], auto for waterMask.h5 or no [if no waterMask.h5 found]\n' % (jobmintpy.modify_network['network.maskFile']['value']))
                fcfg.write('mintpy.network.aoiYX           = %s  #[y0:y1,x0:x1 / no], auto for no, area of interest for coherence calculation\n' % (jobmintpy.modify_network['network.aoiYX']['value']))
                fcfg.write('mintpy.network.aoiLALO         = %s  #[S:N,W:E / no], auto for no - use the whole area\n' % (jobmintpy.modify_network['network.aoiLALO']['value']))
                fcfg.write('\n')
                fcfg.write('\n')
                fcfg.write('########## 3. reference_point\n')
                fcfg.write('## Reference all interferograms to one common point in space\n')
                fcfg.write('## auto - randomly select a pixel with coherence > minCoherence\n')
                fcfg.write('## however, manually specify using prior knowledge of the study area is highly recommended\n')
                fcfg.write('##   with the following guideline (section 4.3 in Yunjun et al., 2019):\n')
                fcfg.write('## 1) located in a coherence area, to minimize the decorrelation effect.\n')
                fcfg.write('## 2) not affected by strong atmospheric turbulence, i.e. ionospheric streaks\n')
                fcfg.write('## 3) close to and with similar elevation as the AOI, to minimize the impact of spatially correlated atmospheric delay\n')
                fcfg.write('mintpy.reference.yx            = %s   #[257,151 / auto]\n' % (jobmintpy.reference_point['reference.yx']['value']))
                fcfg.write('mintpy.reference.lalo          = %s   #[31.8,130.8 / auto]\n' % (jobmintpy.reference_point['reference.lalo']['value']))
                fcfg.write('mintpy.reference.maskFile      = %s   #[filename / no], auto for maskConnComp.h5\n' % (jobmintpy.reference_point['reference.maskFile']['value']))
                fcfg.write('mintpy.reference.coherenceFile = %s   #[filename], auto for avgSpatialCoh.h5\n' % (jobmintpy.reference_point['reference.coherenceFile']['value']))
                fcfg.write('mintpy.reference.minCoherence  = %s   #[0.0-1.0], auto for 0.85, minimum coherence for auto method\n' % (jobmintpy.reference_point['reference.minCoherence']['value']))
                fcfg.write('\n')
                fcfg.write('\n')
                fcfg.write('########## quick_overview\n')
                fcfg.write('## A quick assessment of:\n')
                fcfg.write('## 1) possible groud deformation\n')
                fcfg.write('##    using the velocity from the traditional interferogram stacking\n')
                fcfg.write('##    reference: Zebker et al. (1997, JGR)\n')
                fcfg.write('## 2) distribution of phase unwrapping error\n')
                fcfg.write('##    from the number of interferogram triplets with non-zero integer ambiguity of closue phase\n')
                fcfg.write('##    reference: T_int in Yunjun et al. (2019, CAGEO). Related to section 3.2, equation (8-9) and Fig. 3d-e.\n')
                fcfg.write('\n')
                fcfg.write('\n')
                fcfg.write('########## 4. correct_unwrap_error (optional)\n')
                fcfg.write('## connected components (mintpy.load.connCompFile) are required for this step.\n')
                fcfg.write('## SNAPHU (Chem & Zebker,2001) is currently the only unwrapper that provides connected components as far as we know.\n')
                fcfg.write('## reference: Yunjun et al. (2019, section 3)\n')
                fcfg.write('## supported methods:\n')
                fcfg.write('## a. phase_closure          - suitable for highly redundant network\n')
                fcfg.write('## b. bridging               - suitable for regions separated by narrow decorrelated features, e.g. rivers, narrow water bodies\n')
                fcfg.write('## c. bridging+phase_closure - recommended when there is a small percentage of errors left after bridging\n')
                fcfg.write('mintpy.unwrapError.method          = %s  #[bridging / phase_closure / bridging+phase_closure / no], auto for no\n' % (jobmintpy.correct_unwrap_error['unwrapError.method']['value']))
                fcfg.write('mintpy.unwrapError.waterMaskFile   = %s  #[waterMask.h5 / no], auto for waterMask.h5 or no [if not found]\n' % (jobmintpy.correct_unwrap_error['unwrapError.waterMaskFile']['value']))
                fcfg.write('mintpy.unwrapError.connCompMinArea = %s  #[1-inf], auto for 2.5e3, discard regions smaller than the min size in pixels\n' % (jobmintpy.correct_unwrap_error['unwrapError.connCompMinArea']['value']))
                fcfg.write('\n')
                fcfg.write('## phase_closure options:\n')
                fcfg.write('## numSample - a region-based strategy is implemented to speedup L1-norm regularized least squares inversion.\n')
                fcfg.write('##     Instead of inverting every pixel for the integer ambiguity, a common connected component mask is generated,\n')
                fcfg.write('##     for each common conn. comp., numSample pixels are radomly selected for inversion, and the median value of the results\n')
                fcfg.write('##     are used for all pixels within this common conn. comp.\n')
                fcfg.write('mintpy.unwrapError.numSample       = %s  #[int>1], auto for 100, number of samples to invert for common conn. comp.\n' % (jobmintpy.correct_unwrap_error['unwrapError.numSample']['value']))
                fcfg.write('\n')
                fcfg.write('## briding options:\n')
                fcfg.write('## ramp - a phase ramp could be estimated based on the largest reliable region, removed from the entire interferogram\n')
                fcfg.write('##     before estimating the phase difference between reliable regions and added back after the correction.\n')
                fcfg.write('## bridgePtsRadius - half size of the window used to calculate the median value of phase difference\n')
                fcfg.write('mintpy.unwrapError.ramp            = %s  #[linear / quadratic], auto for no; recommend linear for L-band data\n' % (jobmintpy.correct_unwrap_error['unwrapError.ramp']['value']))
                fcfg.write('mintpy.unwrapError.bridgePtsRadius = %s  #[1-inf], auto for 50, half size of the window around end points\n' % (jobmintpy.correct_unwrap_error['unwrapError.bridgePtsRadius']['value']))
                fcfg.write('\n')
                fcfg.write('\n')
                fcfg.write('########## 5. invert_network\n')
                fcfg.write('## Invert network of interferograms into time-series using weighted least sqaure (WLS) estimator.\n')
                fcfg.write('## weighting options for least square inversion [fast option available but not best]:\n')
                fcfg.write('## a. var - use inverse of covariance as weight (Tough et al., 1995; Guarnieri & Tebaldini, 2008) [recommended]\n')
                fcfg.write('## b. fim - use Fisher Information Matrix as weight (Seymour & Cumming, 1994; Samiei-Esfahany et al., 2016).\n')
                fcfg.write('## c. coh - use coherence as weight (Perissin & Wang, 2012)\n')
                fcfg.write('## d. no  - uniform weight (Berardino et al., 2002) [fast]\n')
                fcfg.write('## SBAS (Berardino et al., 2002) = minNormVelocity (yes) + weightFunc (no)\n')
                fcfg.write('mintpy.networkInversion.weightFunc      = %s #[var / fim / coh / no], auto for var\n' % (jobmintpy.invert_network['networkInversion.weightFunc']['value']))
                fcfg.write('mintpy.networkInversion.waterMaskFile   = %s #[filename / no], auto for waterMask.h5 or no [if not found]\n' % (jobmintpy.invert_network['networkInversion.waterMaskFile']['value']))
                fcfg.write('mintpy.networkInversion.minNormVelocity = %s #[yes / no], auto for yes, min-norm deformation velocity / phase\n' % (jobmintpy.invert_network['networkInversion.minNormVelocity']['value']))
                fcfg.write('mintpy.networkInversion.residualNorm    = %s #[L2 ], auto for L2, norm minimization solution\n' % (jobmintpy.invert_network['networkInversion.residualNorm']['value']))
                fcfg.write('\n')
                fcfg.write('## mask options for unwrapPhase of each interferogram before inversion (recommed if weightFunct=no):\n')
                fcfg.write('## a. coherence              - mask out pixels with spatial coherence < maskThreshold\n')
                fcfg.write('## b. connectComponent       - mask out pixels with False/0 value\n')
                fcfg.write('## c. no                     - no masking [recommended].\n')
                fcfg.write('## d. range/azimuthOffsetStd - mask out pixels with offset std. dev. > maskThreshold [for offset]\n')
                fcfg.write('mintpy.networkInversion.maskDataset   = %s #[coherence / connectComponent / rangeOffsetStd / azimuthOffsetStd / no], auto for no\n' % (jobmintpy.invert_network['networkInversion.maskDataset']['value']))
                fcfg.write('mintpy.networkInversion.maskThreshold = %s #[0-inf], auto for 0.4\n' % (jobmintpy.invert_network['networkInversion.maskThreshold']['value']))
                fcfg.write('mintpy.networkInversion.minRedundancy = %s #[1-inf], auto for 1.0, min num_ifgram for every SAR acquisition\n' % (jobmintpy.invert_network['networkInversion.minRedundancy']['value']))
                fcfg.write('\n')
                fcfg.write('## Temporal coherence is calculated and used to generate the mask as the reliability measure\n')
                fcfg.write('## reference: Pepe & Lanari (2006, IEEE-TGRS)\n')
                fcfg.write('mintpy.networkInversion.minTempCoh  = %s #[0.0-1.0], auto for 0.7, min temporal coherence for mask\n' % (jobmintpy.invert_network['networkInversion.minNumPixel']['value']))
                fcfg.write('mintpy.networkInversion.minNumPixel = %s #[int > 1], auto for 100, min number of pixels in mask above\n' % (jobmintpy.invert_network['networkInversion.minNumPixel']['value']))
                fcfg.write('mintpy.networkInversion.shadowMask  = %s #[yes / no], auto for yes [if shadowMask is in geometry file] or no.\n' % (jobmintpy.invert_network['networkInversion.shadowMask']['value']))
                fcfg.write('\n')
                fcfg.write('\n')
                fcfg.write('########## correct_LOD\n')
                fcfg.write('## Local Oscillator Drift (LOD) correction (for Envisat only)\n')
                fcfg.write('## reference: Marinkovic and Larsen (2013, Proc. LPS)\n')
                fcfg.write('## automatically applied to Envisat data (identified via PLATFORM attribute)\n')
                fcfg.write('## and skipped for all the other satellites.\n')
                fcfg.write('\n')
                fcfg.write('\n')
                fcfg.write('########## correct_SET\n')
                fcfg.write('## Solid Earth tides (SET) correction [need to install insarlab/PySolid]\n')
                fcfg.write('## reference: Milbert (2018); Fattahi et al. (2020, AGU)\n')
                fcfg.write('mintpy.solidEarthTides = %s #[yes / no], auto for no\n' % (jobmintpy.correct_SET['solidEarthTides']['value']))
                fcfg.write('\n')
                fcfg.write('\n')
                fcfg.write('########## 6. correct_troposphere (optional but recommended)\n')
                fcfg.write('## correct tropospheric delay using the following methods:\n')
                fcfg.write('## a. height_correlation - correct stratified tropospheric delay (Doin et al., 2009, J Applied Geop)\n')
                fcfg.write('## b. pyaps - use Global Atmospheric Models (GAMs) data (Jolivet et al., 2011; 2014)\n')
                fcfg.write('##      ERA5  - ERA5    from ECMWF [need to install PyAPS from GitHub; recommended and turn ON by default]\n')
                fcfg.write('##      MERRA - MERRA-2 from NASA  [need to install PyAPS from Caltech/EarthDef]\n')
                fcfg.write('##      NARR  - NARR    from NOAA  [need to install PyAPS from Caltech/EarthDef; recommended for N America]\n')
                fcfg.write('## c. gacos - use GACOS with the iterative tropospheric decomposition model (Yu et al., 2018a, RSE; 2018b, JGR)\n')
                fcfg.write('##      need to manually download GACOS products at http://www.gacos.net for all acquisitions before running this step\n')
                fcfg.write('mintpy.troposphericDelay.method = %s  #[pyaps / height_correlation / gacos / no], auto for pyaps\n' % (jobmintpy.correct_troposphere['troposphericDelay.method']['value']))
                fcfg.write('\n')
                fcfg.write('## Notes for pyaps:\n')
                fcfg.write('## a. GAM data latency: with the most recent SAR data, there will be GAM data missing, the correction\n')
                fcfg.write('##    will be applied to dates with GAM data available and skipped for the others.\n')
                fcfg.write('## b. WEATHER_DIR: if you define an environment variable named WEATHER_DIR to contain the path to a\n')
                fcfg.write('##    directory, then MintPy applications will download the GAM files into the indicated directory.\n')
                fcfg.write('##    MintPy application will look for the GAM files in the directory before downloading a new one to\n')
                fcfg.write('##    prevent downloading multiple copies if you work with different dataset that cover the same date/time.\n')
                fcfg.write('mintpy.troposphericDelay.weatherModel = %s  #[ERA5 / MERRA / NARR], auto for ERA5\n' % (jobmintpy.correct_troposphere['troposphericDelay.weatherModel']['value']))
                fcfg.write('mintpy.troposphericDelay.weatherDir   = %s  #[path2directory], auto for WEATHER_DIR or "./"\n' % (jobmintpy.correct_troposphere['troposphericDelay.weatherDir']['value']))
                fcfg.write('\n')
                fcfg.write('## Notes for height_correlation:\n')
                fcfg.write('## Extra multilooking is applied to estimate the empirical phase/elevation ratio ONLY.\n')
                fcfg.write('## For an dataset with 5 by 15 looks, looks=8 will generate phase with (5*8) by (15*8) looks\n')
                fcfg.write('## to estimate the empirical parameter; then apply the correction to original phase (with 5 by 15 looks),\n')
                fcfg.write('## if the phase/elevation correlation is larger than minCorrelation.\n')
                fcfg.write('mintpy.troposphericDelay.polyOrder      = %s  #[1 / 2 / 3], auto for 1\n' % (jobmintpy.correct_troposphere['troposphericDelay.polyOrder']['value']))
                fcfg.write('mintpy.troposphericDelay.looks          = %s  #[1-inf], auto for 8, extra multilooking num\n' % (jobmintpy.correct_troposphere['troposphericDelay.looks']['value']))
                fcfg.write('mintpy.troposphericDelay.minCorrelation = %s  #[0.0-1.0], auto for 0\n' % (jobmintpy.correct_troposphere['troposphericDelay.minCorrelation']['value']))
                fcfg.write('\n')
                fcfg.write('## Notes for gacos:\n')
                fcfg.write('## Set the path below to directory that contains the downloaded *.ztd* files\n')
                fcfg.write('mintpy.troposphericDelay.gacosDir = %s # [path2directory], auto for "./GACOS"\n' % (jobmintpy.correct_troposphere['troposphericDelay.gacosDir']['value']))
                fcfg.write('\n')
                fcfg.write('\n')
                fcfg.write('########## 7. deramp (optional)\n')
                fcfg.write('## Estimate and remove a phase ramp for each acquisition based on the reliable pixels.\n')
                fcfg.write('## Recommended for localized deformation signals, i.e. volcanic deformation, landslide and land subsidence, etc.\n')
                fcfg.write('## NOT recommended for long spatial wavelength deformation signals, i.e. co-, post- and inter-seimic deformation.\n')
                fcfg.write('mintpy.deramp          = %s  #[no / linear / quadratic], auto for no - no ramp will be removed\n' % (jobmintpy.deramp['deramp']['value']))
                fcfg.write('mintpy.deramp.maskFile = %s  #[filename / no], auto for maskTempCoh.h5, mask file for ramp estimation\n' % (jobmintpy.deramp['deramp.maskFile']['value']))
                fcfg.write('\n')
                fcfg.write('\n')
                fcfg.write('########## 8. correct_topography (optional but recommended)\n')
                fcfg.write('## Topographic residual (DEM error) correction\n')
                fcfg.write('## reference: Fattahi and Amelung (2013, IEEE-TGRS)\n')
                fcfg.write('## stepFuncDate      - specify stepFuncDate option if you know there are sudden displacement jump in your area,\n')
                fcfg.write('##                     e.g. volcanic eruption, or earthquake\n')
                fcfg.write('## excludeDate       - dates excluded for the error estimation\n')
                fcfg.write('## pixelwiseGeometry - use pixel-wise geometry (incidence angle & slant range distance)\n')
                fcfg.write('##                     yes - use pixel-wise geometry if they are available [slow; used by default]\n')
                fcfg.write('##                     no  - use the mean   geometry [fast]\n')
                fcfg.write('mintpy.topographicResidual                   = %s  #[yes / no], auto for yes\n' % (jobmintpy.correct_topography['topographicResidual']['value']))
                fcfg.write('mintpy.topographicResidual.polyOrder         = %s  #[1-inf], auto for 2, poly order of temporal deformation model\n' % (jobmintpy.correct_topography['topographicResidual.polyOrder']['value']))
                fcfg.write('mintpy.topographicResidual.phaseVelocity     = %s  #[yes / no], auto for no - phase, use phase velocity for minimization\n' % (jobmintpy.correct_topography['topographicResidual.phaseVelocity']['value']))
                fcfg.write('mintpy.topographicResidual.stepFuncDate      = %s  #[20080529,20190704T1733 / no], auto for no, date of step jump\n' % (jobmintpy.correct_topography['topographicResidual.stepFuncDate']['value']))
                fcfg.write('mintpy.topographicResidual.excludeDate       = %s  #[20070321 / txtFile / no], auto for exclude_date.txt\n' % (jobmintpy.correct_topography['topographicResidual.excludeDate']['value']))
                fcfg.write('mintpy.topographicResidual.pixelwiseGeometry = %s  #[yes / no], auto for yes, use pixel-wise geometry info\n' % (jobmintpy.correct_topography['topographicResidual.pixelwiseGeometry']['value']))
                fcfg.write('\n')
                fcfg.write('\n')
                fcfg.write('########## 9.1 residual_RMS (root mean squares for noise evaluation)\n')
                fcfg.write('## Calculate the Root Mean Square (RMS) of residual phase time-series for each acquisition\n')
                fcfg.write('## reference: Yunjun et al. (2019, section 4.9 and 5.4)\n')
                fcfg.write('## To get rid of long wavelength component in space, a ramp is removed for each acquisition\n')
                fcfg.write('## Set optimal reference date to date with min RMS\n')
                fcfg.write('## Set exclude dates (outliers) to dates with RMS > cutoff * median RMS (Median Absolute Deviation)\n')
                fcfg.write('mintpy.residualRMS.maskFile = %s  #[file name / no], auto for maskTempCoh.h5, mask for ramp estimation\n' % (jobmintpy.residual_RMS['residualRMS.maskFile']['value']))
                fcfg.write('mintpy.residualRMS.deramp   = %s  #[quadratic / linear / no], auto for quadratic\n' % (jobmintpy.residual_RMS['residualRMS.deramp']['value']))
                fcfg.write('mintpy.residualRMS.cutoff   = %s  #[0.0-inf], auto for 3\n' % (jobmintpy.residual_RMS['residualRMS.cutoff']['value']))
                fcfg.write('\n')
                fcfg.write('########## 9.2 reference_date\n')
                fcfg.write('## Reference all time-series to one date in time\n')
                fcfg.write('## reference: Yunjun et al. (2019, section 4.9)\n')
                fcfg.write('## no     - do not change the default reference date (1st date)\n')
                fcfg.write('mintpy.reference.date = %s   #[reference_date.txt / 20090214 / no], auto for reference_date.txt\n' % (jobmintpy.reference_date['reference.date']['value']))
                fcfg.write('\n')
                fcfg.write('\n')
                fcfg.write('########## 10. velocity\n')
                fcfg.write('## Estimate linear velocity and its standard deviation from time-series\n')
                fcfg.write('## and from tropospheric delay file if exists.\n')
                fcfg.write('## reference: Fattahi and Amelung (2015, JGR)\n')
                fcfg.write('mintpy.velocity.excludeDate    = %s   #[exclude_date.txt / 20080520,20090817 / no], auto for exclude_date.txt\n' % (jobmintpy.velocity['velocity.excludeDate']['value']))
                fcfg.write('mintpy.velocity.startDate      = %s   #[20070101 / no], auto for no\n' % (jobmintpy.velocity['velocity.startDate']['value']))
                fcfg.write('mintpy.velocity.endDate        = %s   #[20101230 / no], auto for no\n' % (jobmintpy.velocity['velocity.endDate']['value']))
                fcfg.write('\n')
                fcfg.write('## Bootstrapping\n')
                fcfg.write('## refernce: Efron and Tibshirani (1986, Stat. Sci.)\n')
                fcfg.write('mintpy.velocity.bootstrap      = %s   #[yes / no], auto for no, use bootstrap\n' % (jobmintpy.velocity['velocity.bootstrap']['value']))
                fcfg.write('mintpy.velocity.bootstrapCount = %s   #[int>1], auto for 400, number of iterations for bootstrapping\n' % (jobmintpy.velocity['velocity.bootstrapCount']['value']))
                fcfg.write('\n')
                fcfg.write('\n')
                fcfg.write('########## 11.1 geocode (post-processing)\n')
                fcfg.write('# for input dataset in radar coordinates only\n')
                fcfg.write('# commonly used resolution in meters and in degrees (on equator)\n')
                fcfg.write('# 100,         60,          50,          30,          20,          10\n')
                fcfg.write('# 0.000925926, 0.000555556, 0.000462963, 0.000277778, 0.000185185, 0.000092593\n')
                fcfg.write('mintpy.geocode              = %s  #[yes / no], auto for yes\n' % (jobmintpy.geocode['geocode']['value']))
                fcfg.write('mintpy.geocode.SNWE         = %s  #[-1.2,0.5,-92,-91 / none ], auto for none, output extent in degree\n' % (jobmintpy.geocode['geocode.SNWE']['value']))
                fcfg.write('mintpy.geocode.laloStep     = %s  #[-0.000555556,0.000555556 / None], auto for None, output resolution in degree\n' % (jobmintpy.geocode['geocode.laloStep']['value']))
                fcfg.write('mintpy.geocode.interpMethod = %s  #[nearest], auto for nearest, interpolation method\n' % (jobmintpy.geocode['geocode.interpMethod']['value']))
                fcfg.write('mintpy.geocode.fillValue    = %s  #[np.nan, 0, ...], auto for np.nan, fill value for outliers.\n' % (jobmintpy.geocode['geocode.fillValue']['value']))
                fcfg.write('\n')
                fcfg.write('########## 11.2 google_earth (post-processing)\n')
                fcfg.write('mintpy.save.kmz             = %s   #[yes / no], auto for yes, save geocoded velocity to Google Earth KMZ file\n' % (jobmintpy.google_earth['save.kmz']['value']))
                fcfg.write('\n')
                fcfg.write('########## 11.3 hdfeos5 (post-processing)\n')
                fcfg.write('mintpy.save.hdfEos5         = %s   #[yes / no], auto for no, save time-series to HDF-EOS5 format\n' % (jobmintpy.hdfeos5['save.hdfEos5']['value']))
                fcfg.write('mintpy.save.hdfEos5.update  = %s   #[yes / no], auto for no, put XXXXXXXX as endDate in output filename\n' % (jobmintpy.hdfeos5['save.hdfEos5.update']['value']))
                fcfg.write('mintpy.save.hdfEos5.subset  = %s   #[yes / no], auto for no, put subset range info   in output filename\n' % (jobmintpy.hdfeos5['save.hdfEos5.subset']['value']))
                fcfg.write('\n')
                fcfg.write('########## 11.4 plot\n')
                fcfg.write('# for high-resolution plotting, increase mintpy.plot.maxMemory\n')
                fcfg.write('# for fast plotting with more parallelization, decrease mintpy.plot.maxMemory\n')
                fcfg.write('mintpy.plot           = %s  #[yes / no], auto for yes, plot files generated by default processing to pic folder\n' % (jobmintpy.plotoptions['plot']['value']))
                fcfg.write('mintpy.plot.dpi       = %s  #[int], auto for 150, number of dots per inch (DPI)\n' % (jobmintpy.plotoptions['plot.dpi']['value']))
                
                fcfg.write('mintpy.plot.maxMemory = %s  #[float], auto for 4, max memory used by one call of view.py for plotting.\n' % (jobmintpy.plotoptions['plot.maxMemory']['value']))

        usermessage.ezprint('Configuration file written in %s' % (file),log,verbose)

################################################################################
## Function to read a MintPy configuration file and update the job
################################################################################
def readcfg(jobmintpy, 
        file: Optional[str] = '.'+os.sep+'MintPy.cfg',
        verbose: Optional[bool] = None, 
        log: Optional[bool] = None):
        """Read the MintPy configuration file and update an ``ezinsar.tsprocessing`` using MintPy

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

        usermessage.openingmsg(__name__,writecfg.__name__,__file__,__copyright__,'Read the MintPy configuration file',log,verbose)

        if not os.path.isfile(file):
                raise ValueError(usermessage.errormsg(__name__,'tsmintpy'.__name__,__file__,__copyright__,
                        'Impossible to find the .cfg file.',None))

        with open(file,'r') as fcfg: 
                for line in fcfg:
                        parameter = None
                        value = None
                        line = line.split()
                        
                        if line and 'mintpy.' in line[0]: 
                                parameter = line[0].replace('mintpy.','')
                                idxi = 0
                                for li in line: 
                                        if li == '=':
                                                idx = idxi + 1 
                                        else: 
                                                idxi = idxi +1
                                value = line[idx]        
                        if not parameter == None: 
                                attrs = vars(jobmintpy)
                                for item in attrs.keys():
                                        tmp = eval("jobmintpy.%s" % (item))                                         
                                        if isinstance(tmp,dict):
                                                if parameter in list(tmp.keys()):
                                                        usermessage.ezprint('The parameter mintpy.%s will be modified by %s' % (parameter,value),log,verbose)
                                                        exec("jobmintpy.%s['%s']['value']=value" % (item,parameter))
        
        jobmintpy.pathmintpyconfig = file
        jobmintpy.check(verbose=False)

        return jobmintpy

################################################################################
## Check the parameters of a dict
################################################################################
def checkmintpyparafromdict(paradict,jobcoreg,verbose):
        """Check the parameters of a dict for an ``ezinsar`` job using MintPy

        The function checks the parameters of a dict for an ``ezinsar.tsprocessing`` with the MintPy processor.

        Args:
                paradict (dict): parameter
                jobcoreg (``ezinsar.job``): EZ-InSAR job for MintPy processor
                verbose (bool): verbose. 

        Returns:
                ``ezinsar.job`` job: Return an EZ-InSAR processing job class
        
        """

        try: 
                namestep = paradict['name']['value']
        except:
                namestep = 'Email information'

        usermessage.ezprint('\tCheck the %s:' % (namestep),jobcoreg.log,verbose)

        listpara = list(paradict.keys())
        modepara = []
        for parai in listpara:
               modepara.append(paradict[parai]['format'])
        valuelist = []
        for parai in listpara:
               valuelist.append(paradict[parai]['valuelist']) 
        valuepara = []
        for parai in listpara:
               valuepara.append(paradict[parai]['value']) 

        infopara = {'listpara':     listpara,
                'modepara':     modepara,
                'valuelist':    valuelist,
                'valuepara':    valuepara}
        
        for idx, namepara in enumerate(infopara['listpara']): 

                if paradict[namepara]['format'] == 'list': 
                        exttext='\n\t\t\t<Format: %s>\n\t\t\t<Possible values: %s>' % ('predefined',paradict[namepara]['valuelist'])
                else: 
                        exttext = '\n\t\t\t<Format: %s>' % (paradict[namepara]['format']) 

                usermessage.ezprint('\t\t%s: %s\n\t\t\t<Description: %s>%s' % (namepara,paradict[namepara]['value'],paradict[namepara]['description'],exttext),jobcoreg.log,verbose)

                if infopara['modepara'][idx] == 'bool':
                        if not isinstance(paradict[namepara]['value'],bool):
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkmintpyparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'True or False',jobcoreg.log))

                elif infopara['modepara'][idx] == 'list':
                        if not paradict[namepara]['value'] in infopara['valuelist'][idx]: 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkmintpyparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'%s' % (infopara['valuelist'][idx]),jobcoreg.log))
                        
                elif infopara['modepara'][idx] == 'email':
                        if not isinstance(paradict[namepara]['value'],str): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkmintpyparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'str',jobcoreg.log))
                        
                elif infopara['modepara'][idx] == 'str':
                        if not isinstance(paradict[namepara]['value'],str): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkmintpyparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'str',jobcoreg.log))

        return jobcoreg