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
from typing import Optional
import numpy as np
import subprocess
from datetime import datetime
import random
import string 
import geopandas as gpd
import glob
import pyproj

from ezinsar import usermessage
from ezinsar import constants
from ezinsar.tools import ezinsardata 
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Wrapper for SARvey allowing logging of processing 
################################################################################
def wrappersarvey(job,
                stepi,
                verbose,
                log):
        """Run a subprocess for SARvey 

        The function will run a subprocess for SARvey 

        Args:   
                job (``ezinsar.job``): EZ-InSAR tsprocessing job with SARvey
                stepi (str): Processing step
                verbose (bool): verbose
                log (str): Log file

        Returns 
                ``ezinsar.job``: EZ-InSAR tsprocessing job with SARvey

        """
        
        ## Check if the workdirectory exists
        if not os.path.isdir(job.workdirectory):
                os.makedirs(job.workdirectory)

        ## Extraction of dates for the first steps
        if job.preparation['start_date']['value'] == 'null' or job.preparation['end_date']['value'] == 'null':
                d1 = 'null'
                d2 = 'null'
                fileslc = glob.glob(job.computer['input_path']['value']+os.sep+'slcStack.h5')
                if fileslc: 
                        out = os.system('info.py %s > %s' % (fileslc[0],constants.__cachedir__+os.sep+'out.tmp'))
                        with open(constants.__cachedir__+os.sep+'out.tmp','r') as fi: 
                                for line in fi.readlines():
                                        if line.startswith('Start Date:'):
                                                d1 = line.split(':')[-1].strip()
                                                d1 = '%s-%s-%s' % (d1[0:4],d1[4:6],d1[6:8])
                                        if line.startswith('End   Date:'):
                                                d2 = line.split(':')[-1].strip()
                                                d2 = '%s-%s-%s' % (d2[0:4],d2[4:6],d2[6:8])
                        
                if job.preparation['start_date']['value'] == 'null': 
                        job.preparation['start_date']['value'] = d1
                if job.preparation['end_date']['value'] == 'null': 
                        job.preparation['end_date']['value'] = d2

        ##Write the config file 
        writecfg(job, 
                file = job.pathsarveyconfig,
                verbose = False,
                log = job.log)

        if not stepi == 'extract_res': 

                my_env = os.environ.copy()
                my_env["PATH"] = f"/usr/local/bin:{my_env['PATH']}"

                usermessage.ezprint('Run SARvey:',log,verbose)

                liststep = usermessage.getprocessingstep(job)
                idx = liststep.index(stepi)

                ## Creation of the command        
                cmd = 'sarvey -w %s -f %s %s %s' % (job.workdirectory,
                                                        job.pathsarveyconfig,
                                                        idx,
                                                        idx,
                                                        )

                usermessage.ezprint('\tCommand: %s' % (cmd),log,verbose)

                pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, env=my_env)
                
                try: 
                        while (line := pr.stdout.readline()) != "":
                                usermessage.ezprint(line.replace('\n',' '),log,verbose)

                        if not len("".join(pr.stderr.readline().strip().split())) == 0:
                                while (line := pr.stderr.readline()):
                                        usermessage.ezprint(line.replace('\n',' '),log,verbose)  
                                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the SARvey processing',log))
                                # usermessage.warningmsg(__name__,__name__,__file__,'Potential error in the SARvey processing',job,True)

                except KeyboardInterrupt:
                        pr.terminate()
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the SARvey processing: user terminate',log))

                usermessage.ezprint('\tdone',log,verbose)

                exec("job.%s['done']['value'] = True" % (stepi))

        else: 
                ## Extraction of displacements
                data = importsarveyresults(job.workdirectory, 
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
## Function to write the SARvey configuration file
################################################################################
def writecfg(jobsarvey, 
        file: Optional[str] = '.'+os.sep+'config.json',
        verbose: Optional[bool] = None, 
        log: Optional[bool] = None):
        """Write the MintPy configuration file from an ``ezinsar.tsprocessing`` using SARvey

        The function writes the MintPy configuration file from an ``ezinsar.tsprocessing``.   

        Args:
                jobsarvey (``ezinsar.tsprocessing``): EZ-InSAR tsprocessing job for SARvey processor
                file (str, Optional): Path and name of the SARvey configuration file [Default: SARvey.cfg]
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (bool): log [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar.tsprocessing``: Return an EZ-InSAR tsprocessing class
        
        """

        if log == None:
                log = jobsarvey.log

        if verbose == None:
                verbose = jobsarvey.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,writecfg.__name__,__file__,__copyright__,
                        'verbose','True or False',log))

        usermessage.openingmsg(__name__,writecfg.__name__,__file__,__copyright__,'Write the SARvey configuration file',log,verbose)

        jobsarvey.check(verbose=False)

        with open(file,'w') as fcfg: 
                fcfg.write('{\n')

                fcfg.write('\tgeneral: {\n')
                fcfg.write('\t\tinput_path: "%s",\n' % (jobsarvey.computer['input_path']['value'].replace('None','')))
                fcfg.write('\t\toutput_path: "%s",\n' % (jobsarvey.computer['output_path']['value'].replace('None','')))
                fcfg.write('\t\tnum_cores: %s,\n' % (jobsarvey.computer['num_cores']['value']))
                fcfg.write('\t\tnum_patches: %s,\n' % (jobsarvey.computer['num_patches']['value']))
                fcfg.write('\t\tapply_temporal_unwrapping: %s,\n' % (str(jobsarvey.computer['apply_temporal_unwrapping']['value']).lower()))
                fcfg.write('\t\tspatial_unwrapping_method: "%s",\n' % (jobsarvey.computer['spatial_unwrapping_method']['value'].replace('None','')))
                fcfg.write('\t\tlogging_level: "%s",\n' % (jobsarvey.computer['logging_level']['value'].replace('None','')))
                fcfg.write('\t\tlogfile_path: "%s",\n' % (jobsarvey.computer['logfile_path']['value'].replace('None','')))
                fcfg.write('\t},\n')

                fcfg.write('\tphase_linking: {\n')
                fcfg.write('\t\tuse_phase_linking_results: %s,\n' % (str(jobsarvey.computer['use_phase_linking_results']['value']).lower()))
                fcfg.write('\t\tinverted_path: "%s",\n' % (jobsarvey.computer['inverted_path']['value'].replace('None','')))
                fcfg.write('\t\tnum_siblings: %s,\n' % (jobsarvey.computer['num_siblings']['value']))
                fcfg.write('\t\tmask_phase_linking_file: "%s",\n' % (jobsarvey.computer['mask_phase_linking_file']['value'].replace('None','')))
                fcfg.write('\t\tuse_ps: %s,\n' % (str(jobsarvey.computer['use_ps']['value']).lower()))
                fcfg.write('\t\tmask_ps_file: "%s",\n' % (jobsarvey.computer['mask_ps_file']['value'].replace('None','')))
                fcfg.write('\t},\n')

                fcfg.write('\tpreparation: {\n')
                fcfg.write('\t\tstart_date: "%s",\n' % (jobsarvey.preparation['start_date']['value'].replace('None','')))
                fcfg.write('\t\tend_date: "%s",\n' % (jobsarvey.preparation['end_date']['value'].replace('None','')))
                fcfg.write('\t\tifg_network_type: "%s",\n' % (jobsarvey.preparation['ifg_network_type']['value'].replace('None','')))
                fcfg.write('\t\tnum_ifgs: %s,\n' % (jobsarvey.preparation['num_ifgs']['value']))
                fcfg.write('\t\tmax_tbase: %s,\n' % (jobsarvey.preparation['max_tbase']['value']))
                fcfg.write('\t\tfilter_window_size: %s,\n' % (jobsarvey.preparation['filter_window_size']['value']))
                fcfg.write('\t},\n')

                fcfg.write('\tconsistency_check: {\n')
                fcfg.write('\t\tcoherence_p1: %s,\n' % (jobsarvey.consistency_check['coherence_p1']['value']))
                fcfg.write('\t\tgrid_size: %s,\n' % (jobsarvey.consistency_check['grid_size']['value']))
                fcfg.write('\t\tmask_p1_file: "%s",\n' % (jobsarvey.consistency_check['mask_p1_file']['value'].replace('None','')))
                fcfg.write('\t\tnum_nearest_neighbours: %s,\n' % (jobsarvey.consistency_check['num_nearest_neighbours']['value']))
                fcfg.write('\t\tmax_arc_length: %s,\n' % (jobsarvey.consistency_check['max_arc_length']['value']))
                fcfg.write('\t\tvelocity_bound: %s,\n' % (jobsarvey.consistency_check['velocity_bound']['value']))
                fcfg.write('\t\tdem_error_bound: %s,\n' % (jobsarvey.consistency_check['dem_error_bound']['value']))
                fcfg.write('\t\tnum_optimization_samples: %s,\n' % (jobsarvey.consistency_check['num_optimization_samples']['value']))
                fcfg.write('\t\tarc_unwrapping_coherence: %s,\n' % (jobsarvey.consistency_check['arc_unwrapping_coherence']['value']))
                fcfg.write('\t\tmin_num_arc: %s,\n' % (jobsarvey.consistency_check['min_num_arc']['value']))
                fcfg.write('\t},\n')

                fcfg.write('\tunwrapping: {\n')
                fcfg.write('\t\tuse_arcs_from_temporal_unwrapping: %s,\n' % (str(jobsarvey.unwrapping['use_arcs_from_temporal_unwrapping']['value'])).lower())
                fcfg.write('\t},\n')

                fcfg.write('\tfiltering: {\n')
                fcfg.write('\t\tcoherence_p2: %s,\n' % (jobsarvey.filtering['coherence_p2']['value']))
                fcfg.write('\t\tapply_aps_filtering: %s,\n' % (str(jobsarvey.filtering['apply_aps_filtering']['value'])).lower())
                fcfg.write('\t\tinterpolation_method: "%s",\n' % (jobsarvey.filtering['interpolation_method']['value'].replace('None','')))
                fcfg.write('\t\tgrid_size: %s,\n' % (jobsarvey.filtering['grid_size']['value']))
                fcfg.write('\t\tmask_p2_file: "%s",\n' % (jobsarvey.filtering['mask_p2_file']['value'].replace('None','')))
                fcfg.write('\t\tuse_moving_points: %s,\n' % (str(jobsarvey.filtering['use_moving_points']['value'])).lower())
                fcfg.write('\t\tmax_temporal_autocorrelation: %s,\n' % (jobsarvey.filtering['max_temporal_autocorrelation']['value']))
                fcfg.write('\t},\n')

                fcfg.write('\tdensification: {\n')
                fcfg.write('\t\tnum_connections_to_p1: %s,\n' % (jobsarvey.densification['num_connections_to_p1']['value']))
                fcfg.write('\t\tmax_distance_to_p1: %s,\n' % (jobsarvey.densification['max_distance_to_p1']['value']))
                fcfg.write('\t\tvelocity_bound: %s,\n' % (jobsarvey.densification['velocity_bound']['value']))
                fcfg.write('\t\tdem_error_bound: %s,\n' % (jobsarvey.densification['dem_error_bound']['value']))
                fcfg.write('\t\tnum_optimization_samples: %s,\n' % (jobsarvey.densification['num_optimization_samples']['value']))
                fcfg.write('\t\tarc_unwrapping_coherence: %s,\n' % (jobsarvey.densification['arc_unwrapping_coherence']['value']))
                fcfg.write('\t},\n')

                fcfg.write('}\n')
                
        usermessage.ezprint('Configuration file written in %s' % (file),log,verbose)

################################################################################
## Extraction of displacements for SARvey FUNCTION
################################################################################
def importsarveyresults(workdirectory, 
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

        if not 'sarveytsprocessing' in str(type(job)):
                raise ValueError(usermessage.errormsg(__name__,importsarveyresults.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR-MiaplPy processing.',None))

        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,importsarveyresults.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if not log == None: 
                if not isinstance(log,str): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,importsarveyresults.__name__,__file__,__copyright__,
                                'log','str',log))

        if not os.path.isdir(workdirectory):
                raise ValueError(usermessage.errormsg(__name__,importsarveyresults.__name__,__file__,__copyright__,
                                'The work directory does not exist.',None))       
        
        usermessage.openingmsg(__name__,importsarveyresults.__name__,__file__,__copyright__,'Import the SARvey results',log,verbose)

        os.chdir(workdirectory)

        ## Convert the dataset to gpkg
        cmd = 'sarvey_export '
        intfile = glob.glob(job.computer['output_path']['value']+os.sep+'p2_coh%0.0d_ts.h5' % (job.filtering['coherence_p2']['value']*100))[0]
        outfile = 'tmp.gpkg'
        logfile = job.computer['logfile_path']['value']

        if job.extract_res['correct_geo']: 
                cmd = cmd + '-g '
        cmd = cmd + '-o %s %s' % (outfile,intfile)
        # os.system(cmd)

        ## Initialisation of the dataset
        usermessage.ezprint('Initialisation of the dataset...',log,verbose)
        data = ezinsardata.displacement()
        usermessage.ezprint('\tdone',log,verbose)

        ## Detection of the dataset
        usermessage.ezprint('Read the dataset...',log,verbose)
        dataset = workdirectory+os.sep+'tmp.gpkg'
        dataimport = gpd.read_file(dataset)
        usermessage.ezprint('\tdone',log,verbose)


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

        data.datainformation['TS_Processor'] = 'sarvey'
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
        
        tmp = [x.replace('D','') for x in list(dataimport.keys())[7:-1]] 

        data.dates['value'] = []
        for di in tmp:
                data.dates['value'].append(datetime.strptime(di,"%Y%m%d"))
        data.dates['value'] = np.array(data.dates['value'])

        data.n_image['value'] = int(len(data.dates['value']))

        # data.n_ifg['value'] = int(tmp['n_ifg'][0][0])

        if not job == None: 
                data.date_ref['value'] = datetime.strptime(tmp[0],"%Y%m%d")

        # data.ifg_date['value'] = np.array(tmp)

        usermessage.ezprint('\tdone',log,verbose)

        ## For the spatial data
        usermessage.ezprint('Extract the spatial information...',log,verbose)
        
        a = []
        b = []
        for pti in dataimport['geometry']:
                a.append(pti.xy[0][0])
                b.append(pti.xy[1][0])
        meter_to_latlon = pyproj.Transformer.from_crs('%s' % (str(dataimport.crs).lower()),'epsg:4326',always_xy=True)
        data.lon['value'], data.lat['value'] = meter_to_latlon.transform(a,b)

        if meter_mode == 'UTM': 
                utm_crs_list = pyproj.database.query_utm_crs_info(
                        datum_name="WGS 84",
                        area_of_interest=pyproj.aoi.AreaOfInterest(
                                west_lon_degree=np.nanmin(data.lon['value']),
                                south_lat_degree=np.nanmin(data.lat['value']),
                                east_lon_degree=np.nanmax(data.lon['value']),
                                north_lat_degree=np.nanmax(data.lat['value']),
                                ),
                        )
                meter_mode = utm_crs_list[0].code

        latlon_to_meter = pyproj.Transformer.from_crs('epsg:4326','epsg:%s' % (meter_mode))
        data.x_utm['value'], data.y_utm['value'] = latlon_to_meter.transform(data.lat['value'],data.lon['value'])
        data.code_meter['value'] = 'epsg:%s' % (meter_mode)

        usermessage.ezprint('\tdone',log,verbose)

        ## For the ground data
        usermessage.ezprint('Extract the ground information...',log,verbose)

        ## For the displacement data
        usermessage.ezprint('Extract the displacement data...',log,verbose)

        tmpdisp = np.empty((len(data.x_utm['value']),len(data.dates['value'])))
        h = 0
        for di in [x for x in list(dataimport.keys())[7:-1]]: 
                tmpdisp[:,h] = dataimport[di].to_list()
                h = h + 1
        data.dispLOS['value'] = tmpdisp

        data.rateLOS['value'] = np.array(dataimport['velocity'].to_list())
        data.sigmarateLOS['value'] = np.zeros_like(data.rateLOS['value'])

        usermessage.ezprint('\tdone',log,verbose)

        ## For the reference point
        usermessage.ezprint('Extract the reference-point information...',log,verbose)

        data.referencepoint['value']['index'] = 0
        if not job == None: 
                data.referencepoint['value']['lat_pt_ref'] = float(0)
                data.referencepoint['value']['lon_pt_ref'] = float(0)
                data.referencepoint['value']['lon_pt_refarea'] = 0
                data.referencepoint['value']['lat_pt_refarea'] = 0
                data.referencepoint['value']['radius'] = 0
                data.referencepoint['value']['rateLOS'] = 0

        usermessage.ezprint('\tdone',log,verbose)
                
        os.chdir(cur_dir)

        return data

################################################################################
## Check the parameters of a dict
################################################################################
def checksarveyparafromdict(paradict,jobcoreg,verbose):
        """Check the parameters of a dict for an ``ezinsar`` job using SARvey

        The function checks the parameters of a dict for an ``ezinsar.coregistration`` or ``ezinsar.ifgstack``.   

        Args:
                paradict (dict): parameter
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for SARvey processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar`` processing job: Return an EZ-InSAR tsprocessing class
        
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
                                        __name__,checksarveyparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'True or False',jobcoreg.log))

                elif infopara['modepara'][idx] == 'list':
                        if not paradict[namepara]['value'] in infopara['valuelist'][idx]: 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checksarveyparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'%s' % (infopara['valuelist'][idx]),jobcoreg.log))
                        
                elif infopara['modepara'][idx] == 'email':
                        if not isinstance(paradict[namepara]['value'],str): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checksarveyparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'str',jobcoreg.log))
                        
                elif infopara['modepara'][idx] == 'int':
                        if not isinstance(paradict[namepara]['value'],int): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checksarveyparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'int',jobcoreg.log))

                elif infopara['modepara'][idx] == 'float':
                        if not isinstance(paradict[namepara]['value'],float): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checksarveyparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'float',jobcoreg.log))
                               
        return jobcoreg