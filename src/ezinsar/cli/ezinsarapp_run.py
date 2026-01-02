#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Run an EZ-InSAR processing job

This application allows to run an EZ-InSAR processing job (i.e., coregistration, ifgstack, etc.). 

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 

        $ ezinsar run --help

Changelog:
    * 3.3.1: Several changes, Dec. 2025, Alexis Hrysiewicz
        * Change the import line
        * Check the check method (if EIjob in string)
        * Delete the link to the EZ-InSAR GAMMA module
    * 3.2.0: Several changes, Jun. 2025, Alexis Hrysiewicz
        * Bug fix and add the tsprocessing for GAMMA
        * Add the possitibility to run - in parallel - several jobs
    * 3.1.0: Add the Offset-tacking processing and the docker options, Feb. 2025, Alexis Hrysiewicz
    * 3.0.0: Initial version, Dec. 2024

"""

from docopt import docopt
import numpy as np
import os
from joblib import Parallel, delayed
import glob 

import ezinsar.job as ez
from ezinsar import usermessage 

__docstringapp__ =  """EZ-InSAR application: Run an EZ-InSAR processing job

usage: ezinsar run -f <file> -s <str> [options]

Arguments:
    -f, --file <str>    EZ-InSAR job file 
    -s, --step <str>    Step names regarding the InSAR processor and the SAR/InSAR processing

Other-options:
    --processing <str>  Type of the processing 
    --parallel <int>    Number of works for parallel computation. Please see the end of the help for further information. [Default: 1] 
    --docker            Enable the processing in a Docker container
    --displaystep       Display the processing steps
    --nolog             No logging
    -h, --help
    -q, --quiet         Suppress verbose

Information:
    For an example of an EZ-InSAR processing job, the processing step can be given by using a single str: i.e., 'extractimage'. 
    Several steps can be given by using several step name and commas: i.e., 'initref,extractimage'. 
    All the steps can be done by using the full name or a number: i.e., 1-3, in this case, all the steps from checkSLC to coarserefdate will be processed.   
    The use of 'all' for the step name will process all the different steps
    %s
    For the ISCE-2 processor: 

        WARNING: The steps are different regarding the acquisition mode.

        The coregistration steps are: 1 => checkSLC; 2 => checkOrbit; 3 => coarserefdate for all modes. 

            - The steps for Sentinel-1 IW are: 4 => unpack_topo_reference; 5 => unpack_secondary_slc; 6 => average_baseline; 7 => extract_burst_overlaps; 8 => overlap_geo2rdr; 9 => overlap_resample; 10 => pairs_misreg; 11 => timeseries_misreg; 12 => fullBurst_geo2rdr; 13 => fullBurst_resample; 14 => extract_stack_valid_region; 15 => merge_reference_secondary_slc; 16 => grid_baseline; 17 => updatestack.
            - The steps for any other modes are: 4 => unpack_slc; 5 => crop_slc; 6 => reference; 7 => focus_split; 8 => geo2rdr_coarseResamp; 9 => refineSecondaryTiming; 10 => invertMisreg; 11 => fineResamp; 12 => grid_baseline; 13 => updatestack

        The ifgstack steps are: 1 => ifgnetwork for all modes. 

            - The steps for Sentinel-1 IW are: 2 => generate_burst_igram; 3 => merge_burst_igram; 4 => filter_coherence; 5 => unwrap; 6 => ifggeocoding; 7 => finalstack.
            - The steps for any other modes are: 2 => generate_igram; 3 => filter_coherence; 4 => unwrap; 5 => ifggeocoding; 6 => finalstack.

    For the Doris processor: 

        WARNING: Only StripMap-like data are supported. 

        - The coregistration steps are: 1 => checkSLC; 2 => checkOrbit; 3 => coarserefdate; 4 => extractimage; 5 => refinerefdate; 6 => mastertiming; 7 => oversample; 8 => coarseoffset; 9 => finecoreg; 10 => reltiming; 11 => demassist; 12 => coregpm; 13 => resample; 14 => finalstack; 15 => cleanstack; 16 => updatestack.
        - The ifgstack steps are: 1 => importrslc; 2 => refinerefdate; 3 => ifgnetwork; 4 => ifgcompute; 5 => ifgfilter; 6 => ifgunwrapping; 7 => ifggeocoding; 8 => finalstack.
    
    For the SNAP processor: 

        - The intensity stack steps are: 1 => checkSLC; 2 => importSLC; 3 => multilook; 4 => filter; 5 => terraincal; 6 => geocode; 7 => clean; 8 => update. 
        - The coregistration steps are: 1 => checkSLC; 2 => coarserefdate; 3 => importSLC; 4 => refinerefdate; 5 => coreg; 6 = > cleanstack.
        - The ifgstack steps are: 1 => ifgnetwork; 2 => ifgcompute; 3 => ifgfilter; 4 => multilook; 5 => ifgunwrapping; 6 = > ifggeocoding; 7 => finalstack.

    For the MintPy processor: 

        - The sbas steps are: 1 => load_data; 2 => modify_network; 3 => reference_point; 4 => quick_overview; 5 => correct_unwrap_error; 6 => invert_network; 7 => correct_LOD; 8 => correct_SET; 9 => correct_troposphere; 10 => deramp; 11 => correct_topography; 12 => residual_RMS; 13 => reference_date; 14 => velocity; 15 => geocode; 16 => google_earth; 17 => hdfeos5; 17 => extract_res.

    For the StaMPS processor:

        - The ps and sbas are: 1 => mt_prep; 2 => load_data; 3 => phase_noise; 4 => ps_selection; 5 => ps_weeding; 6 => phase_correction; 7 => phase_unwrapping; 8 => corr_lkerror 9 => corr_noise; 10 => extract_res. 
        - The merged steps are: 1 => merging; 2 => phase_unwrapping; 3 => corr_lkerror 4 => corr_noise; 5 => extract_res.

    For the MiaplPy processor: 
        - The steps are: 1 => load_data; 2 => phase_linking; 3 => concatenate_patches; 4 => generate_ifgram; 5 => unwrap_ifgram; 6 => load_ifgram; 7 => ifgram_correction; 8 => invert_network; 9 => timeseries_correction; 10 => extract_res.

    For the SARvey processor: 
        - The steps are: 1 => preparation; 2 => consistency_check; 3 => unwrapping; 4 => filtering; 5 => densification; 6 => extract_res.

Parallelisation: 
    It is possible to run, in parallel, several EZ-InSAR jobs. 
    All jobs need to be similar in terms of processing. 
    The list can be in quote or double quote: e.g., 'job_*.ei'. 
    Only the first job is the list will be used to detect the processing, processor and steps. 
         
""" % (ez.__help_CLIrun__)

def main():
    """Main function"""
    args = docopt(__docstringapp__)
    args['--parallel'] = int(args['--parallel'])
    
    if args['--quiet']: 
        verbose = False
    else:
        verbose = True

    cur_dir = os.getcwd()

    ################################################################################
    ## Create the job list
    ################################################################################
    listjob = glob.glob(args['--file'])

    ################################################################################
    ## Detect and verification of the job 
    ################################################################################
    job = ez.load(listjob[0],verbose=False)

    if args['--nolog']: 
        log = None
    else: 
        log = 'ezinsar.log'

    # Detect the job type
    if 'coregistration' in str(type(job)):
        mode = 'coregistration'    
    elif 'intstack' in str(type(job)):
        mode = 'intstack'        
    elif 'ifgstack' in str(type(job)):
        mode = 'ifgstack'
    elif 'offsetprocessing' in str(type(job)):
        mode = 'offsetprocessing'
    elif 'mintpytsprocessing.sbas' in str(type(job)) or 'stampstsprocessing' in str(type(job)) or 'tsprocessing' in str(type(job)):
        mode = 'tsprocessing'
    elif 'EIjob' in str(type(job)):
        mode = []
        if not job.coregistration == None:
            mode.append('coregistration')
        if not job.intstack == None:
            mode.append('intstack')
        if not job.ifgstack == None:
            mode.append('ifgstack')
        if not job.tsprocessing == None:
            mode.append('tsprocessing')
        if not job.offsetprocessing == None:
            mode.append('offsetprocessing')
        
        if not len(mode) == 0:
            if len(mode) == 1:
                mode = mode[0]
        else: 
            raise ValueError('None processing job detected.')

    if isinstance(mode,list):
        if args['--processing'] == None:
            rep = None
            while not rep in mode:
                rep = input('Several EZ-InSAR processing jobs have been detected. Please select one: %s\n\t==>' % (mode))   
            mode = rep
        else: 
            if args['--processing'] in mode: 
                mode = args['--processing']
            else: 
                raise ValueError('The processing %s is not stored in the job. There is/are %s.' % (args['--processing'],mode))

    # Detection of steps
    if 'EIjob' in str(type(job)):
        namestep = eval('usermessage.getprocessingstep(job.%s)' % (mode))
    else: 
        namestep = eval('usermessage.getprocessingstep(job)')  

    # Detect the steps
    stepstring = [str(x+1) for x in np.arange(0,len(namestep),1)]
    try: 
        if args['--step'] in stepstring:
            step = namestep[int(args['--step'])-1]
        elif '-' in args['--step']: 
            stepidx = np.arange(int(args['--step'].split('-')[0])-1,int(args['--step'].split('-')[1]),1) + 1
            step = []
            for idx in stepidx:
                if idx > 0 and idx <= len(namestep): 
                    step.append(namestep[idx-1])
                else:
                    raise ValueError('The step indexes should be between 1 and %s.' % (len(namestep)))
        else:             
            step = args['--step'].split(',')
        # The step will be checked in the processor...
    except: 
        raise ValueError('Incorrect processing step name or number.')

    os.chdir(cur_dir)

    if args['--displaystep'] == True:
        usermessage.ezprint('The steps are: %s' % (namestep),None,True)
    else: 
        ################################################################################
        ## Run the processing 
        ################################################################################
        def subrun(jobpath,mode,step,verbose,log,docker):
            try: 
                job = ez.load(jobpath,verbose=False) 
                if 'EIjob' in str(type(job)):
                    exec('job.%s.verbose = verbose' % (mode))
                    tmplog = eval('job.%s.log' % (mode))
                    if (tmplog == None) and (not log == None):
                        exec('job.%s.log = log' % (mode))
                    exec('job.%s.run(step=step,docker=docker)' % (mode))

                else:
                    job.verbose = verbose
                    if (job.log == None) and (not log == None):
                        job.log = log
                    job.run(step=step,docker=docker)

                # Save the job file
                ez.save(job,jobpath,verbose=False)

                return 'Performed'
            
            except Exception as e: 
                return e

        ## Running 
        if len(listjob) > 1: 
            output = Parallel(n_jobs=args['--parallel'])(delayed(subrun)(jobi,mode,step,verbose,log,args["--docker"]) for jobi in listjob)

            usermessage.ezprint('\n\n----------------------------------------------',None,True)
            usermessage.ezprint('Summary of processing',None,True)
            usermessage.ezprint('----------------------------------------------',None,True)

            for idx, jobi in enumerate(listjob): 
                usermessage.ezprint('\nFor the job: %s' % (jobi),None,True)
                usermessage.ezprint('\tMode: %s' % (mode),None,True)
                usermessage.ezprint('\tStep(s): %s' % (step),None,True)
                usermessage.ezprint('\tVerbose: %s' % (verbose),None,True)
                usermessage.ezprint('\tLog: %s' % (log),None,True)
                usermessage.ezprint('\tDocker: %s' % (args["--docker"]),None,True)
                usermessage.ezprint('\tOutput: %s' % (output[idx]),None,True)

        else: 
            output = subrun(listjob[0],mode,step,verbose,log,args["--docker"])
            if not output == 'Performed':
                raise ValueError(output)

if __name__=='__main__':
    main()