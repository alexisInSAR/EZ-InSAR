#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage COSMO-SkyMed images for EZ-InSAR

The module allows to manage COSMO-SkyMed images for an `EIjob`
    
    (From `ezinsar` package)

Changelog:
        * 1.0.0: Initial version, Feb. 2025

"""

################################################################################
## Python packages
################################################################################
import os
import numpy as np
import pandas as pd
from shapely.geometry import Polygon
import glob
import xml.etree.ElementTree as ET
from scipy.spatial import ConvexHull
import datetime
from typing import Optional
import h5py
import copy 

from ezinsar import constants
from ezinsar.tools import miscellaneous
from ezinsar import usermessage
from ezinsar.eicomponents.slcmodule import slctools
from ezinsar.eicomponents.templatevar import listSLCempty

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Initialise the SLC list
################################################################################
def initiateSLC(job,
        verbose: Optional[bool] = None, 
        mode: Optional[str] = 'onfile', 
        server: Optional[str] = constants.__S1server__, 
        satellite: Optional[str] = 'S1', 
        ):
        """Initialise the COSMO-SkyMed SLC list 

        The function initialise the RSAT2 SLC for an ``EIjob``. 

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                mode (str): Mode for the list creation [Default: 'online']. Can be 'online' or 'list' or 'onfile' 

        Returns:
                `EIjob`: Return an EZ-InSAR class

        """   

        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,initiateSLC.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        
        if not (isinstance(mode,str) and mode in ['online','onfile']):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,initiateSLC.__name__,__file__,__copyright__,
                        'mode','"online" or "onfile"',job.log))
        
        usermessage.openingmsg(__name__,initiateSLC.__name__,__file__,__copyright__,'Create the SLC list for EZ-InSAR for COSMO-SkyMed',job.log,verbose)

        if not job.satellite == None:
                if job.satellite == 'CSK': 
                        if mode == 'onfile':
                                usermessage.ezprint('Mode: base on files - the CSK SLC list will be created based on available files:',job.log,verbose)
                                job = createCSKlistonfile(job,verbose)
        else:
                raise ValueError(usermessage.errormsg(__name__,initiateSLC.__name__,__file__,__copyright__,'The satellite is not defined.',job.log))
                
        return job

################################################################################
################################################################################
## Sub-functions
################################################################################
################################################################################
def createCSKlistonfile(job,verbose):
        """Create the COSMO-SkyMed SLC list with the **onfile** mode

        The function initialise the COSMO-SkyMed  SLC for an ``EIjob``, with the **onfile** mode.  

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose

        Returns:
                `EIjob`: Return an EZ-InSAR class

        """ 
        lon,lat = job.roi.exterior.xy

        listSLC = copy.deepcopy(listSLCempty)

        listfile = glob.glob(job.pathSLC+os.sep+'CSK*')
        try:
                listfile = sorted(listfile, key=lambda x: x.split(os.sep)[-1].split('_')[8])[::-1]
        except:
                a = dummy

        for filei in listfile:
                usermessage.ezprint('Process the file %s' % (filei),job.log,verbose)

                pol = job.polarisation[0]

                CSKannoresults = detectCSKannotation(filei,pol)
                resanno = CSKannoresults['data_xmli1']

                listSLC['Name'].append(filei.split(os.sep)[-1])

                listSLC['Date1'].append(resanno['startTime'])
                listSLC['Date2'].append(resanno['stopTime'])
                listSLC['Platform'].append(resanno['missionId'])

                if resanno['mode'] == 'HIMAGE':
                        listSLC['Mode'].append('HH')
                elif resanno['mode'] == 'PINGPONG':
                        listSLC['Mode'].append('PP')
                
                listSLC['Beam'].append(resanno['beam'])

                listSLC['Orbit'].append(int(resanno['absoluteOrbitNumber']))
                listSLC['RelativeOrbit'].append(int(resanno['beam']))

                listSLC['OrbitDirection'].append(resanno['Pass'].upper())
                listSLC['Looking'].append(resanno['Looking']) 
                listSLC['IncidenceAngle'].append(np.mean(resanno['incidenceAngle']))
                listSLC['Wavelength'].append(resanno['Wavelength'])        
                listSLC['Frequency'].append(resanno['Frequency'])
                listSLC['ProcessingLevel'].append(resanno['productType'])

                listSLC['Server'].append('DISK')
                listSLC['Url'].append(filei)
                listSLC['Status'].append('DISK')

                listSLC['SizeMB'].append(miscellaneous.get_dir_size(filei))

                listSLC['Stored'].append(True)
                listSLC['Processed'].append(False)

                tmp = [None, None, None, None]

                for idx, poli in enumerate(resanno['polarisation']):
                        tmp[idx] = poli

                for idx, poli in enumerate(tmp):
                        exec("listSLC['Polarisation%s'].append('%s')" % (idx+1,poli))

                lonpts = resanno['longitude']
                latpts = resanno['latitude']
  
                pts= [(x,y) for x in lonpts for y in latpts]

                pts=np.array([np.array(lonpts), np.array(latpts)]).T
                hull = ConvexHull(pts)
                listSLC['PolyFrame'].append(str(Polygon(list(zip(pts[hull.vertices,0], pts[hull.vertices,1])))))

                usermessage.ezprint('\tDone.',job.log,verbose)

        listSLC = slctools.checklistconsistency(listSLC,log=job.log,verbose=verbose)
        listSLCpd = pd.DataFrame.from_dict(listSLC)

        # Save the list
        if listSLCpd.empty == False:
                job.SLClist = listSLCpd
        else:
                raise ValueError(usermessage.errormsg(__name__,createCSKlistonfile.__name__,__file__,__copyright__,'The list is empty.',job.log))

        return job 

def detectCSKannotation(file,pol):
        """Detect and read the annonation files from COSMO-SkyMed file

        The function detects and reads the annonation files

        Args:
                file (str): Fullpath of the S1 file
                pol (str): Selected polarisation (e.g., 'VV')

        Returns:
                dict: Dict of RSAT2 annotations

        """ 
        data_xmli1 = None
        data_orbitsi1 = None

        path_file = glob.glob(file+os.sep+'*h5')

        if not path_file: 
                raise ValueError(usermessage.errormsg(__name__,detectCSKannotation.__name__,__file__,__copyright__,'Impossible to detect the product.xml in the directory %s' % (file),None))

        data_xmli1, data_orbitsi1  = read_CSKannotation(path_file[0]) 
      
        CSKannoresults = dict()
        CSKannoresults['data_xmli1'] = data_xmli1
        CSKannoresults['data_orbitsi1'] = data_orbitsi1

        return CSKannoresults

def read_CSKannotation(path_h5): 
        """Read the annonation files from the COSMO-SkyMed file

        The function reads the annonation files from COSMO-SkyMed file

        Args:
                path_h5 (str): Fullpath of the h5 file

        Returns:
                dict: Dict of annotations
                dict: Dict of orbits

        """ 

        data_xml = dict()
        data_orbits = dict()

        ## Detection of polarisation
        with h5py.File(path_h5, "r") as fslc:
                list = [key for key in fslc.attrs.keys()]
                # if len(list) > 1:
                #         usermessage.warningmsg(__name__,read_CSKannotation.__name__,__file__,'Several polarisations have been detected. Only the first one will be used as metadata.',None,True)

                data_xml['missionId'] = fslc['/'].attrs['Mission ID'].decode('utf-8')   
                data_xml['beam'] = fslc['S01'].attrs['Beam ID'].decode('utf-8').split('-')[-1]
                data_xml['startTime'] = fslc['/'].attrs['Scene Sensing Start UTC'].decode('utf-8').replace(' ','T')
                data_xml['stopTime'] = fslc['/'].attrs['Scene Sensing Stop UTC'].decode('utf-8').replace(' ','T')
                
                data_xml['polarisation'] = []
                for key in fslc.keys():
                        data_xml['polarisation'].append(fslc[key].attrs['Polarisation'].decode('utf-8').upper())

                data_xml['mode'] = fslc['/'].attrs['Acquisition Mode'].decode('utf-8')
                data_xml['absoluteOrbitNumber'] = int(fslc['/'].attrs['Orbit Number'])
                data_xml['Pass'] = fslc['/'].attrs['Orbit Direction'].decode('utf-8').upper()

                data_xml['Looking'] = fslc['/'].attrs['Look Side'].decode('utf-8').capitalize()

                data_xml['Wavelength'] = [float(fslc['/'].attrs['Radar Wavelength'])]
                data_xml['Frequency'] = [float(fslc['/'].attrs['Radar Frequency'])]

                data_xml['productType'] = fslc['/'].attrs['Product Type'].decode('utf-8')

                tmp = fslc['/'].attrs['Reference UTC'].decode('utf-8').replace(' ','T')
                tmpbis = str(round(float(tmp.split('.')[-1])/1e3)) # keep only milliseconds
                time_ref = datetime.datetime.strptime(tmp.split('.')[0]+'.'+tmpbis,'%Y-%m-%dT%H:%M:%S.%f')

                Zero_Doppler_Azimuth_First_Time = float(fslc['S01/SBI'].attrs['Zero Doppler Azimuth First Time'])
                Zero_Doppler_Azimuth_Last_Time = float(fslc['S01/SBI'].attrs['Zero Doppler Azimuth Last Time'])

                data_xml['azimuthTime'] = [
                        (time_ref + datetime.timedelta(seconds=Zero_Doppler_Azimuth_Last_Time)).strftime("%Y-%m-%dT%H:%M:%S.%f"),
                        (time_ref + datetime.timedelta(seconds=Zero_Doppler_Azimuth_Last_Time)).strftime("%Y-%m-%dT%H:%M:%S.%f"),
                        (time_ref + datetime.timedelta(seconds=Zero_Doppler_Azimuth_First_Time)).strftime("%Y-%m-%dT%H:%M:%S.%f"),
                        (time_ref + datetime.timedelta(seconds=Zero_Doppler_Azimuth_First_Time)).strftime("%Y-%m-%dT%H:%M:%S.%f"),
                        (time_ref + datetime.timedelta(seconds=Zero_Doppler_Azimuth_Last_Time)).strftime("%Y-%m-%dT%H:%M:%S.%f")]

                data_xml['slantRangeTime'] = []

                tmp = fslc['//S01/SBI'].shape
                nb_line = tmp[0]
                nb_pixel = tmp[1]

                tmp1 = fslc['/S01/SBI'].attrs['Bottom Left Geodetic Coordinates']
                tmp2 = fslc['/S01/SBI'].attrs['Bottom Right Geodetic Coordinates']
                tmp3 = fslc['/S01/SBI'].attrs['Top Right Geodetic Coordinates']
                tmp4 = fslc['/S01/SBI'].attrs['Top Left Geodetic Coordinates']

                data_xml['line'] = [nb_line-1, nb_line-1, 0, 0, nb_line-1]
                data_xml['pixel'] = [0, nb_pixel-1, nb_pixel-1, 0, 0]

                data_xml['longitude'] = [tmp1[1],tmp2[1], tmp3[1], tmp4[1], tmp1[1]]
                data_xml['latitude'] = [tmp1[0],tmp2[0], tmp3[0], tmp4[0], tmp1[0]]

                data_xml['height'] = []

                data_xml['incidenceAngle'] = [float(fslc['S01/SBI'].attrs['Near Incidence Angle']),
                                        float(fslc['S01/SBI'].attrs['Far Incidence Angle']),
                                        float(fslc['S01/SBI'].attrs['Far Incidence Angle']),
                                        float(fslc['S01/SBI'].attrs['Near Incidence Angle']),
                                        float(fslc['S01/SBI'].attrs['Near Incidence Angle']),
                                        ]

                data_xml['elevationAngle'] = []
                data_xml['Xtrack_f_DC'] = []

                data_orbits = dict()

                data_orbits['time'] = []
                for di in fslc['/'].attrs['State Vectors Times']: 
                        data_orbits['time'].append((time_ref + datetime.timedelta(seconds=di)).strftime("%Y-%m-%dT%H:%M:%S.%f"))

                tmp = fslc['/'].attrs['ECEF Satellite Position']
                data_orbits['orb_X_int'] = [i[0] for i in tmp]
                data_orbits['orb_Y_int'] = [i[1] for i in tmp]
                data_orbits['orb_Z_int'] = [i[2] for i in tmp]

                tmp = fslc['/'].attrs['ECEF Satellite Velocity']
                data_orbits['orb_VX_int'] = [i[0] for i in tmp]
                data_orbits['orb_VY_int'] = [i[1] for i in tmp]
                data_orbits['orb_VZ_int'] = [i[2] for i in tmp]

        return data_xml, data_orbits
