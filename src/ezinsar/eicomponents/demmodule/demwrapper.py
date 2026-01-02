#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to add the wrapper for the DEM module

The module allows to add wrapper to the DEM modules
    
    (From `ezinsar` package)

Changelog:
        * 3.3.1: Check the check method, Dec. 2025, Alexis Hrysiewicz
        * 3.2.1: Initial version, Sep. 2025

"""

from ezinsar import usermessage
from ezinsar import constants
from ezinsar.eicomponents.demmodule import demconstants, demfunctions
from ezinsar.tools import formattools
from ezinsar.eicomponents.slcmodule import slctools
from typing import Optional, Union
import platform
import os 
import glob
import shutil
import numpy as np

################################################################################
## run
################################################################################
def run(job: Optional[Union[any,None]] = None, 
        pathDEM: Optional[Union[str,None]] = None, 
        nameDEM: Optional[Union[str,None]] = None, 
        typeDEM: Optional[Union[str,None]] = None,
        bbox: Optional[Union[str,None]] = None,
        ell: Optional[Union[str,None]] = None,
        ellcorrection: Optional[bool] = True,
        processor: Optional[Union[str,None]] = None,
        clip: Optional[bool] = True,
        useSLClist: Optional[bool] = True,
        nodata: Optional[Union[int,float]] = 0,
        waterbody_mask: Optional[bool] = True,
        verbose: Optional[Union[bool,None]] = None,
        log: Optional[Union[str,None]] = None,
        username: Optional[Union[str,None]] = None,
        password: Optional[Union[str,None]] = None,
        EPSG: Optional[str] = '4326',
        docker: Optional[bool] = False,
        cleaning: Optional[bool] = True,
        ):
        """Download and prepare a DEM for InSAR computations

        The function downloads or import a DEM from a ``EIjob`` and from user inputs.  

        Args:
                job (`EIjob`): EZ-InSAR job
                pathDEM (str): Path of the DEM directory [Default: `None`]. See Notes. 
                nameDEM (str): Name of the DEM file [Default: `None`]. See Notes. 
                typeDEM (str): Type of the DEM [Default: `None`]. See Notes. 
                bbox (str): Bbox to define the ROI, in 'W,S,E,N' format[Default: `None`]. In EPGS:4326. See Notes. 
                ell (str): Fullpath of the ellipsoid file format[Default: `None`]. See Notes. 
                ellcorrection (bool, Optional): Ellipsoid correction [Default: `True`]. See Notes. 
                processor (str): Name of the InSAR processor [Default: `None`]. See Notes.
                clip (bool, Optional): Clipping of the DEM [Default: `True`]. See Notes.
                useSLClist (bool, Optional): If job, use the SLC list to create the bbox. 
                nodata (int or float, Optional): No-data value in the DEM [Default: 0]. See Notes.
                waterbody_mask (bool, Optional): Generate two DEMs with and without no-data values. [Default: True]
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (str): logging [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                username (str): Username [Default: `None`]. Used for AW3D30.
                password (str): Username [Default: `None`]. Used for AW3D30.
                EPSG (str, Optional): Coordinate system. Another EPSG than 4326 can be used by GAMMA and SNAP. [Default: ``4326``] 
                docker (bool, Optional): Run the processing in the docker container [Default: `True`] 
                cleaning (bool, Optional): Cleaning [Default: `True`] 
        Returns:
                `EIjob`: EZ-InSAR class if given
                str: path of the DEM directory 
                str: type of the DEM
                str: Name of the DEM file

        """

        ## Detection of parameters regarding the job
        if not job == None: 
                if not 'EIjob' in str(type(job)):
                        raise ValueError(usermessage.errormsg(__name__,run.__name__,__file__,constants.__copyright__,
                                'The job parameter is not a EZ-InSAR job.',None))
                
        # For pathDEM
        if pathDEM == None:
                if not job == None: 
                        pathDEM = job.pathDEM
        # For nameDEM
        if nameDEM == None:
                if not job == None: 
                        nameDEM = job.nameDEM
        # For typeDEM
        if typeDEM == None:
                if not job == None: 
                        typeDEM = job.typeDEM
        # For processor
        if processor == None:
                if not job == None: 
                        if not job.coregistration == None: 
                                processor = job.coregistration.processor
        # For log
        if log == None:
                if not job == None: 
                        log = job.log
        # For verbose
        if verbose == None:
                if not job == None: 
                        verbose = job.verbose
        else: 
                if not isinstance(verbose,bool): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,run.__name__,__file__,constants.__copyright__,
                                'verbose','True or False',log))

        if not isinstance(clip,bool): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,run.__name__,__file__,constants.__copyright__,
                                'clip','True or False',log)) 
        
        if not isinstance(docker,bool): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,run.__name__,__file__,constants.__copyright__,
                                'docker','True or False',log)) 
        
        if (platform.system() == 'Windows') and (processor=='isce2') and (docker==False):
                raise ValueError(usermessage.errormsg(__name__,run.__name__,__file__,constants.__copyright__,'On Windows, docker must be True for isce2 processor.',log))  
        
        usermessage.openingmsg(__name__,run.__name__,__file__,constants.__copyright__,'Download the DEM',log,verbose)

        ## Check the parameters
        # For pathDEM
        if isinstance(pathDEM,str): 
                if not os.path.isdir(pathDEM): 
                        raise ValueError(usermessage.errormsg(__name__,run.__name__,__file__,constants.__copyright__,'The path does not exist.',log))  
        else: 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,run.__name__,__file__,constants.__copyright__,
                        'pathDEM','a path or given by the job.',log))
        
        # For nameDEM
        if not isinstance(nameDEM,str): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,run.__name__,__file__,constants.__copyright__,
                        'nameDEM','a str or given by the job.',log))
        
        # For typeDEM
        if '-ell' in typeDEM:
                typeDEM = typeDEM.replace('-ell','')
                ellcorrection = True

        if not typeDEM in list(demconstants.__DEMinformation__.keys()): 
                raise TypeError(usermessage.typeerrormsg(
                                __name__,run.__name__,__file__,constants.__copyright__,
                                'typeDEM',list(demconstants.__DEMinformation__.keys()),log))
        
        # Check the username and password
        if typeDEM in ["AW3D30","COPDEM30","COPDEM90",]:
                if username == None or password == None: 
                        raise ValueError(usermessage.errormsg(__name__,run.__name__,__file__,constants.__copyright__,'An username and a password are required for %s.' % (typeDEM),log))
                
        # For ellcorrection
        if not isinstance(ellcorrection,bool): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,run.__name__,__file__,constants.__copyright__,
                                'ellcorrection','True or False',log))
        
        usermessage.ezprint('The ell. correction for the DEM is: %s' % (ellcorrection),log,verbose) 

        # For ell
        if typeDEM == 'perso' and ell == None and ellcorrection == True: 
                raise ValueError(usermessage.errormsg(__name__,run.__name__,__file__,constants.__copyright__,'The ell. file is required.',log))     

        # For processor
        if processor == None:
                usermessage.warningmsg(__name__,run.__name__,__file__,'The InSAR processor is not defined, the DEM will be saved in .tif format.',log,verbose)

        if clip == True and processor == 'snap': 
                raise ValueError(usermessage.errormsg(__name__,run.__name__,__file__,constants.__copyright__,'The clip parameter should be False for snap processor.',log))
        
        ## For the non-data value
        if not processor in [None,'gamma']: 
                if not nodata == 0: 
                        raise ValueError(usermessage.errormsg(__name__,run.__name__,__file__,constants.__copyright__,'The No-data value must be 0.',log))
        else: 
                if (not isinstance(nodata,int)) and (not isinstance(nodata,float)):
                        raise ValueError(usermessage.errormsg(__name__,run.__name__,__file__,constants.__copyright__,'the No-data value must be int or float.',log))

        # For the EPSG
        if not isinstance(EPSG,str): 
                raise TypeError(usermessage.typeerrormsg(
                                __name__,run.__name__,__file__,constants.__copyright__,
                                'EPSG','str',log))

        if (not EPSG == '4326') and (not processor in ['gamma','snap']):
                raise ValueError(usermessage.errormsg(__name__,run.__name__,__file__,constants.__copyright__,
                                'Another EPSG code than 4326 is only possible with the gamma processor.',log)) 
        
        if job == None: 
                roipoly = bbox
        else: 
                if useSLClist == True: 
                        roipoly = slctools.getextentfromSLC(job,verbose=verbose,log=log)
                else: 
                        roipoly = job.roi

        ########################################################################################################
        ## For Windows
        ########################################################################################################
        if docker:
                usermessage.warningmsg(__name__,run.__name__,__file__,'On Windows, the creation of a DEM for ISCE-2 is easier inside a Docker container. EZ-InSAR will run the next steps in a Docker container. No logging will not be perfomed.',log,verbose)

                oldpath = os.path.abspath(pathDEM)
                newpath = '/mnt/Data/DEM' 

                usermessage.ezprint('Current DEM path: %s' % (oldpath),log,verbose) 
                usermessage.ezprint('Docker DEM path: %s' % (newpath),log,verbose) 
                
                lon, lat = roipoly.exterior.xy 
                lonmin = np.min(lon)
                lonmax = np.max(lon)
                latmin = np.min(lat)
                latmax = np.max(lat)

                cmd = 'docker run --rm --name ezinsar0 -v %s:%s -it %s /bin/bash -c "cd /root; source .bashrc; %s; ezinsar dem run -s %s -b %s --nameDEM %s --typeDEM %s --processor %s' % (oldpath,newpath,constants.__nameDockerImage__,
                                constants.create_docker_string(),
                                newpath,
                                '%s,%s,%s,%s' % (lonmin,latmin,lonmax,latmax),
                                nameDEM,
                                typeDEM, 
                                processor)
                if not ell == None: 
                        cmd = cmd + ' --ell %s' % (ell)
                if ellcorrection == False: 
                        cmd = cmd + ' --no_ellcorrection'
                if clip == False:
                        cmd = cmd + ' --no_clip'
                if not username == None:
                        cmd = cmd + ' --username %s --password %s' % (username,password)
                cmd = cmd + ' --nolicensecheck"'

                usermessage.ezprint('The Docker command is: \n\t%s' % (cmd),log,verbose)

                # Run the processing 
                status = os.system(cmd)
                if status == 0: 
                        usermessage.ezprint('Successfull processing in the Docker container',log,verbose)
                else: 
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,constants.__copyright__,
                                        'Error during the processing in the Docker container',None))
                
                # Naming of files
                if typeDEM == 'perso':
                        output_dem = nameDEM.split('.')[0]+'_EZ_InSAR'
                else:
                        output_dem = nameDEM.split('.')[0]

                if ellcorrection == True:
                        output_dem = output_dem+'.wgs84'

                if processor == 'gamma':
                        format = "GTiff"
                        output_dembis = output_dem+'.masked.gamma.tif'
                        output_dem = output_dem+'.gamma.tif'
                elif processor == 'doris':
                        format = "ENVI"
                        output_dembis = output_dem+'.masked.doris.r4'
                        output_dem = output_dem+'.doris.r4'
                elif processor == 'snap':
                        format = "GTiff"
                        output_dembis = output_dem+'.masked.snap.tif'
                        output_dem = output_dem+'.snap.tif'
                elif processor == 'isce2' or processor == 'isce3':
                        format = "ISCE"
                        output_dembis = output_dem+'.masked.isce'
                        output_dem = output_dem+'.isce'
                else: 
                        format = "GTiff"
                        output_dembis = output_dem+'.masked.tif'
                        output_dem = output_dem+'.tif'

                if (not typeDEM == 'perso') and (not 'ell' in typeDEM) and (ellcorrection == True): 
                        usermessage.warningmsg(__name__,run.__name__,__file__,'Modification of typeDEM',log,verbose)
                        typeDEM = typeDEM + '-ell'

                if not job == None:
                        usermessage.ezprint('Update the EZ-InSAR job: ...',log,verbose) 
                        usermessage.warningmsg(__name__,run.__name__,__file__,'The EZ-InSAR job will be updated.',log,verbose)
                        job.pathDEM = pathDEM
                        job.typeDEM = typeDEM
                        job.nameDEM = output_dem
                        usermessage.ezprint('\t done.',log,verbose) 

                usermessage.ezprint('Quick summary of outputs: ...',log,verbose) 
                usermessage.ezprint('\tpathDEM is %s' % (pathDEM),log,verbose) 
                usermessage.ezprint('\ttypeDEM is %s' % (typeDEM),log,verbose) 
                usermessage.ezprint('\tnameDEM is %s' % (output_dem),log,verbose) 

                return job, pathDEM, typeDEM, output_dem

        ################################################
        ## Display the input parameters
        ################################################
        usermessage.ezprint('User input:',log,verbose)
        usermessage.ezprint('\tJob file: %s' % (job),log,verbose) 
        usermessage.ezprint('\tThe path of the DEM is: %s' % (pathDEM),log,verbose)
        usermessage.ezprint('\tThe name of the DEM is: %s' % (nameDEM),log,verbose)
        usermessage.ezprint('\tThe type of the DEM is: %s' % (typeDEM),log,verbose)
        usermessage.ezprint('\tThe Region of Interest is: %s' % (roipoly),log,verbose)

        usermessage.ezprint('\tThe ellipsoid correction is: %s' % (ellcorrection),log,verbose)
        usermessage.ezprint('\tThe ellipsoid file is: %s' % (ell),log,verbose)

        usermessage.ezprint('\tThe InSAR processor will be: %s' % (processor),log,verbose)
        usermessage.ezprint('\tThe cropping option is: %s' % (clip),log,verbose)
        usermessage.ezprint('\tThe nodata value will be: %s' % (nodata),log,verbose)
        usermessage.ezprint('\tThe creation of the masked (water bodies) file is: %s' % (waterbody_mask),log,verbose)

        usermessage.ezprint('\tThe EPSG code is: %s' % (EPSG),log,verbose)

        usermessage.ezprint('\tThe docker mode is: %s' % (docker),log,verbose)

        usermessage.ezprint('\tThe cleaning mode is: %s' % (cleaning),log,verbose)

        ## Download the DEM tiles 
        demfunctions.downloadtiles(roipoly,
                typeDEM,
                outdir = pathDEM+os.sep+'dem_tiles_tmp',
                username = username,
                password = password,
                nameDEM = 'dem_tmp',
                verbose=verbose,
                log=log)

        ## Merge the tiles
        demfunctions.mergetiles(pathDEM+os.sep+'dem_tiles_tmp'+os.sep+'*.tif',
                pathDEM+os.sep+'demtmp0.tif',
                format='GTiff',
                verbose=verbose,
                log=log)

        ## Detection of the nodata values 
        orignodata = formattools.readnodata(pathDEM+os.sep+'demtmp0.tif')

        if waterbody_mask: 
                ## Create the mask 
                demfunctions.extractmask(pathDEM+os.sep+'demtmp0.tif',
                        pathDEM+os.sep+'masktmp.tif',
                        orignodata,
                        format='GTiff',
                        verbose=verbose,
                        log=log)
                               
        ## Replace the nodatavalue
        demfunctions.replace(pathDEM+os.sep+'demtmp0.tif',
                pathDEM+os.sep+'demtmp1.tif',
                orignodata,
                nodata,
                nodata=False,
                format = 'GTiff',
                verbose=verbose,
                log=log)
        lastdem = pathDEM+os.sep+'demtmp1.tif'

        if ell == None:
                geoidecode = demconstants.__DEMinformation__[typeDEM]['vertical ref.'].split('Geoid')[0].split('/')[-1].strip()
        else:
                geoidecode = ell

        if ellcorrection:
                demfunctions.ellcorrection(lastdem,
                        pathDEM+os.sep+'demtmp2.tif',
                        geoidecode,
                        format='GTiff',
                        nodata = False,
                        verbose=verbose,
                        log=log)
                lastdem = pathDEM+os.sep+'demtmp2.tif'

        ## Remask the DEM
        if waterbody_mask:
                demfunctions.applymask(lastdem,
                        lastdem.replace('.tif','.masked.tif'),
                        pathDEM+os.sep+'masktmp.tif',
                        format='GTiff',
                        verbose=verbose,
                        log=log)

        ## Create the new name / parameters
        if clip:
                roi = roipoly
        else:
                roi = None

        if processor == 'Doris' and platform.system() == 'Windows':
                byteswap = True
        else:
                byteswap = False

        if typeDEM == 'perso':
                output_dem = pathDEM+os.sep+nameDEM.split('.')[0]+'_EZ_InSAR'
        else:
                output_dem = pathDEM+os.sep+nameDEM.split('.')[0]

        if ellcorrection == True:
                output_dem = output_dem+'.wgs84'

        if processor == 'gamma':
                format = "GTiff"
                output_dembis = output_dem+'.masked.gamma.tif'
                output_dem = output_dem+'.gamma.tif'
                areaorpoint = 'Point'
                xmlISCE = False
        elif processor == 'doris':
                format = "ENVI"
                output_dembis = output_dem+'.masked.doris.r4'
                output_dem = output_dem+'.doris.r4'
                areaorpoint = 'Point'
                xmlISCE = False
        elif processor == 'snap':
                format = "GTiff"
                output_dembis = output_dem+'.masked.snap.tif'
                output_dem = output_dem+'.snap.tif'
                areaorpoint = 'Point'
                xmlISCE = False
        elif processor == 'isce2' or processor == 'isce3':
                format = "ISCE"
                output_dembis = output_dem+'.masked.isce'
                output_dem = output_dem+'.isce'
                areaorpoint = 'Area'
                xmlISCE = True
        else: 
                format = "GTiff"
                output_dembis = output_dem+'.masked.tif'
                output_dem = output_dem+'.tif'
                areaorpoint = 'Point'
                xmlISCE = False

        ## Format the DEM file
        demfunctions.translate(lastdem,
                output_dem,
                roi = roi,
                format=format,
                nodata=True,
                byteswap = byteswap,
                areaorpoint = areaorpoint, 
                xmlISCE = xmlISCE,
                verbose=verbose,
                log=log)

        if waterbody_mask:
                demfunctions.translate(lastdem.replace('.tif','.masked.tif'),
                output_dembis,
                roi = roi,
                format=format,
                nodata=True,
                byteswap = byteswap,
                areaorpoint = areaorpoint, 
                xmlISCE = xmlISCE,
                verbose=verbose,
                log=log)

        ## Cleaning 
        if cleaning:
                listfile = glob.glob(pathDEM+os.sep+'demtmp*') + [pathDEM+os.sep+'masktmp.tif',pathDEM+os.sep+'dem_tiles_tmp']
                for li in listfile:
                        if os.path.isfile(li):
                                os.remove(li)
                        elif os.path.isdir(li):
                                shutil.rmtree(li)

        ## Modification of typeDEM 
        usermessage.ezprint('\n------------------------------',log,verbose) 
        if (not typeDEM == 'perso') and (not 'ell' in typeDEM) and (ellcorrection == True): 
                usermessage.warningmsg(__name__,run.__name__,__file__,'Modification of typeDEM',log,verbose)
                typeDEM = typeDEM + '-ell'

        ## Update the EZ-InSAR job
        if not job == None:
                usermessage.ezprint('Update the EZ-InSAR job: ...',log,verbose) 

                usermessage.warningmsg(__name__,run.__name__,__file__,'The EZ-InSAR job will be updated.',log,verbose)

                job.pathDEM = pathDEM
                job.typeDEM = typeDEM
                job.nameDEM = output_dem.split(os.sep)[-1]

                usermessage.ezprint('\t done.',log,verbose) 

        usermessage.ezprint('Quick summary of outputs: ...',log,verbose) 
        usermessage.ezprint('\tpathDEM is %s' % (pathDEM),log,verbose) 
        usermessage.ezprint('\ttypeDEM is %s' % (typeDEM),log,verbose) 
        usermessage.ezprint('\tnameDEM is %s' % (output_dem.split(os.sep)[-1]),log,verbose) 

        return job, pathDEM, typeDEM, output_dem                