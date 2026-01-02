#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage Sentinel-1 SLC for EZ-InSAR

The module allows to manage Sentinel-1 SLC in .zip and .SAFE format for an `EIjob`
    
    (From `ezinsar` package)

Changelog:
        * 3.3.1: Bug fix with SM data, Dec. 2025, Alexis Hrysiewicz
        * 3.2.2: Delete the support of wget, Alexis Hrysiewicz, Sep. 2025
        * 1.2.0: Various changes, Aug. 2025, Alexis Hrysiewicz
                * Delete the orbit managemenent for harmonisation
                * Server name in lowercase
        * 1.1.0: Various changes, Feb. 2025, Alexis Hrysiewicz
                * Start the migration of scripts into the APIs
                * Start the implementation of Sentinel-1 C and D
                * Some optimisations
        * 1.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import os
import numpy as np
import pandas as pd
from shapely.geometry import Polygon
import glob
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import shutil
from scipy.spatial import ConvexHull
import datetime
from typing import Optional
import random
import string 
import copy 
import urllib
import re
import fiona 
from alive_progress import alive_bar
from shapely.wkt import loads

from ezinsar import constants
from ezinsar import usermessage
from ezinsar.eicomponents.slcmodule import slctools
from ezinsar.api import ASFapi, Copernicusapi, GEODESapi, EarthDATAapi
from ezinsar.eicomponents.templatevar import listSLCempty
from ezinsar.tools import miscellaneous

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Env variable 
################################################################################
__timeout_ASF__ = 5000
"""int: Time out in seconds for feching orbit files from the ASF server
"""

################################################################################
## Initialise the SLC list
################################################################################
def initiateSLC(job,
        verbose: Optional[bool] = None, 
        mode: Optional[str] = 'online', 
        server: Optional[str] = constants.__S1server__, 
        satellite: Optional[str] = 'S1', 
        ):
        """Initialise the S1 SLC list 

        The function initialise the S1 SLC for an ``EIjob``. 

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                mode (str): Mode for the list creation [Default: 'online']. Can be 'online' or 'list' or 'onfile' 
                server (str): Server for the 'online' mode [Default: 'Copernicus']. Can be 'Copernicus' or 'ASF'. 
                satellite (str): Satellite [Default: 'S1']. Can be 'S1', 'Sentinel-1A' or 'Sentinel-1B'. 

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
        
        if not (isinstance(server,str) and server.lower() in ['asf','copernicus','geodes','earthdata']):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,initiateSLC.__name__,__file__,__copyright__,
                        'mode','"ASF" or "Copernicus" or "GEODES" or "EarthDATA"',job.log))
        
        if not (isinstance(satellite,str) and satellite in ['S1','Sentinel-1A','Sentinel-1B']):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,initiateSLC.__name__,__file__,__copyright__,
                        'mode','"S1" or "Sentinel-1A" or "Sentinel-1B"',job.log))
        
        usermessage.openingmsg(__name__,initiateSLC.__name__,__file__,__copyright__,'Create the SLC list for EZ-InSAR for Sentinel-1',job.log,verbose)

        if not job.satellite == None:
                if job.satellite == 'S1': 
                        if mode == 'online':
                                if (not job.relorbit == None) and (not job.satpass == None):
                                        usermessage.ezprint('Mode: online - the S1 SLC list will be created based on the job information:',job.log,verbose)
                                        usermessage.ezprint('Acquisition mode: %s' %(job.satmode),job.log,verbose)
                                        usermessage.ezprint('Relative orbite: %s' %(job.relorbit),job.log,verbose)
                                        usermessage.ezprint('Pass direction: %s' %(job.satpass),job.log,verbose)
                                        usermessage.ezprint('Polarisation: %s' %(job.polarisation),job.log,verbose)
                                        usermessage.ezprint('Request for %s' % (satellite),job.log,verbose)
                                        job = createS1listonline(job,verbose,server,satellite)
                                else:
                                        raise ValueError(usermessage.errormsg(__name__,initiateSLC.__name__,__file__,__copyright__,'The relative orbit and/or the pass direction is/are not defined.',job.log))
                        elif mode == 'onfile':
                                usermessage.ezprint('Mode: base on files - the S1 SLC list will be created based on available files:',job.log,verbose)
                                job = createS1listonfile(job,verbose)
        else:
                raise ValueError(usermessage.errormsg(__name__,initiateSLC.__name__,__file__,__copyright__,'The satellite is not defined.',job.log))
                
        return job

################################################################################
################################################################################
## Sub-functions
################################################################################
################################################################################
def createS1listonline(job,verbose,server,satellite):
        """Create the S1 SLC list with the **online** mode

        The function initialise the S1 SLC for an ``EIjob``. 

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose 
                server (str): Server for the 'online' mode 
                satellite (str): Satellite

        Returns:
                `EIjob`: Return an EZ-InSAR class

        """ 
        lon,lat = job.roi.exterior.xy

        listSLC = copy.deepcopy(listSLCempty)

        if server.lower() == 'asf': 
                listSLCpd = ASFapi.retrieve(job.satellite, 
                        job.roi, 
                        job.date1,
                        job.date2,
                        level = 'SLC',
                        satmode = job.satmode, 
                        relorbit = job.relorbit, 
                        satpass = job.satpass,
                        log = job.log, 
                        verbose = verbose,
                )

        elif server.lower() == 'copernicus': 
                listSLCpd = Copernicusapi.retrieve(job.satellite, 
                        job.roi, 
                        job.date1,
                        job.date2,
                        level = 'SLC',
                        satmode = job.satmode, 
                        relorbit = job.relorbit, 
                        satpass = job.satpass,
                        log = job.log, 
                        verbose = verbose,
                )

        elif server.lower() == 'geodes': 
                listSLCpd = GEODESapi.retrieve(job.satellite, 
                        job.roi, 
                        job.date1,
                        job.date2,
                        level = 'SLC',
                        satmode = job.satmode, 
                        relorbit = job.relorbit, 
                        satpass = job.satpass,
                        log = job.log, 
                        verbose = verbose,
                )

        elif server.lower() == 'earthdata': 
                listSLCpd = EarthDATAapi.retrieve(job.satellite, 
                        job.roi, 
                        job.date1,
                        job.date2,
                        level = 'SLC',
                        satmode = job.satmode, 
                        relorbit = job.relorbit, 
                        satpass = job.satpass,
                        log = job.log, 
                        verbose = verbose,
                )

        # Save the list
        if listSLCpd.empty == False:
                job.SLClist = listSLCpd
        else:
                raise ValueError(usermessage.errormsg(__name__,createS1listonline.__name__,__file__,__copyright__,'The list is empty.',job.log))

        return job

def createS1listonfile(job,verbose):
        """Create the S1 SLC list with the **onfile** mode

        The function initialise the S1 SLC for an ``EIjob``, with the **onfile** mode.  

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose

        Returns:
                `EIjob`: Return an EZ-InSAR class

        """ 
        lon,lat = job.roi.exterior.xy

        listSLC = copy.deepcopy(listSLCempty)

        listfile = glob.glob(job.pathSLC+os.sep+'*.zip') + glob.glob(job.pathSLC+os.sep+'*.SAFE')
        listfile = sorted(listfile, key=lambda x: x.split(os.sep)[-1].split('_')[5])[::-1]

        for filei in listfile:
                usermessage.ezprint('Process the file %s' % (filei),job.log,verbose)

                pol = job.polarisation[0]

                S1annoresults = detectS1annoatationfromxml(filei,pol)
                
                if not S1annoresults['data_xmli1'] == None: 
                        resanno = S1annoresults['data_xmli1']
                if not S1annoresults['data_xmli2'] == None: 
                        resanno = S1annoresults['data_xmli2']
                if not S1annoresults['data_xmli3'] == None: 
                        resanno = S1annoresults['data_xmli3']

                listSLC['Name'].append(filei.split(os.sep)[-1])

                listSLC['Date1'].append(resanno['startTime']+'Z')
                if resanno['mode'] == 'IW': 
                        listSLC['Date2'].append(resanno['stopTime']+'Z')
                else: 
                        listSLC['Date2'].append(resanno['stopTime']+'Z')

                listSLC['Platform'].append(resanno['missionId'])

                if resanno['mode'] == 'IW': 
                        listSLC['Mode'].append(resanno['mode'])
                else: 
                        listSLC['Mode'].append('SM')

                listSLC['Orbit'].append(int(resanno['absoluteOrbitNumber']))

                if resanno['missionId'] == 'S1A': 
                        listSLC['RelativeOrbit'].append(np.mod(int(resanno['absoluteOrbitNumber']) - 73, 175) + 1)
                elif resanno['missionId'] == 'S1B': 
                        listSLC['RelativeOrbit'].append(np.mod(int(resanno['absoluteOrbitNumber']) - 27, 175) + 1)
                elif resanno['missionId'] == 'S1C': 
                        listSLC['RelativeOrbit'].append(np.mod(int(resanno['absoluteOrbitNumber']) - 4, 175) + 1) # 4 or 179
                        # raise ValueError(usermessage.errormsg(__name__,initiateSLC.__name__,__file__,__copyright__,'The Sentinel-1 C is not implemented.',job.log))
                elif resanno['missionId'] == 'S1D': 
                        raise ValueError(usermessage.errormsg(__name__,initiateSLC.__name__,__file__,__copyright__,'The Sentinel-1 D is not implemented.',job.log))

                listSLC['OrbitDirection'].append(resanno['Pass'].upper())
                listSLC['Looking'].append(resanno['Looking']) 
                listSLC['Wavelength'].append(resanno['Wavelength'])        
                listSLC['Frequency'].append(resanno['Frequency'])
                listSLC['ProcessingLevel'].append(resanno['productType'])

                listSLC['Server'].append('DISK')
                listSLC['Url'].append(filei)
                listSLC['Status'].append('DISK')

                if '.zip' in filei: 
                        listSLC['SizeMB'].append(os.path.getsize(filei)/1e6)
                else: 
                        listSLC['SizeMB'].append(float(0))

                listSLC['Stored'].append(False)
                listSLC['Processed'].append(False)

                if 'SSV_' in filei.split(os.sep)[-1] or 'SVV_' in filei.split(os.sep)[-1]:  
                        listSLC['Polarisation1'].append('VV')
                        listSLC['Polarisation2'].append(None)
                elif 'SSH_' in filei.split(os.sep)[-1] or 'SHH_' in filei.split(os.sep)[-1]: 
                        listSLC['Polarisation1'].append('HH')
                        listSLC['Polarisation2'].append(None)
                elif 'SDH_' in filei.split(os.sep)[-1]: 
                        listSLC['Polarisation1'].append('HH')
                        listSLC['Polarisation2'].append('HV')
                elif 'SDV_' in filei.split(os.sep)[-1]: 
                        listSLC['Polarisation1'].append('VV')
                        listSLC['Polarisation2'].append('VH')
                elif 'SHV_' in filei.split(os.sep)[-1]: 
                        listSLC['Polarisation1'].append('HV')
                        listSLC['Polarisation2'].append(None)
                elif 'SVH_' in filei.split(os.sep)[-1]: 
                        listSLC['Polarisation1'].append('VH')
                        listSLC['Polarisation2'].append(None)

                listSLC['Polarisation3'].append(None)
                listSLC['Polarisation4'].append(None)

                lonpts = []
                latpts = []
                
                if not S1annoresults['data_xmli1'] == None: 
                        lonpts = lonpts + S1annoresults['data_xmli1']['longitude']
                        latpts = latpts + S1annoresults['data_xmli1']['latitude'] 
                if not S1annoresults['data_xmli2'] == None: 
                        lonpts = lonpts + S1annoresults['data_xmli2']['longitude']
                        latpts = latpts + S1annoresults['data_xmli2']['latitude'] 
                if not S1annoresults['data_xmli3'] == None: 
                        lonpts = lonpts + S1annoresults['data_xmli3']['longitude']
                        latpts = latpts + S1annoresults['data_xmli3']['latitude'] 

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
                raise ValueError(usermessage.errormsg(__name__,createS1listonfile.__name__,__file__,__copyright__,'The list is empty.',job.log))

        return job 

def detectS1annoatationfromxml(file,pol):
        """Detect and read the annonation files from S1 .zip and .SAFE file

        The function detects and reads the annonation files from S1 .zip and .SAFE file

        Args:
                file (str): Fullpath of the S1 file
                pol (str): Selected polarisation (e.g., 'VV')

        Returns:
                dict: Dict of Sentinel-1 annotations

        """ 
        data_xmli1 = None
        data_xmli2 = None
        data_xmli3 = None
        data_orbitsi1 = None
        data_orbitsi2 = None
        data_orbitsi3 = None

        path_xml_IW1 = None
        path_xml_IW2 = None
        path_xml_IW3 = None 

        if not os.path.isfile(file): 
                file = file.replace('.zip','.SAFE')

        if 'IW' in file.split(os.sep)[-1]:
                check_IW1, check_IW2, check_IW3 = detectionS1IW(file)

        ## Tmp directory 
        tmpintdir = constants.__cachedir__+os.sep+'tmpsafe_'+''.join(random.choice(string.ascii_lowercase) for i in range(16))
        tmpdir = constants.__cachedir__+os.sep+'tmp_'+''.join(random.choice(string.ascii_lowercase) for i in range(16))
        os.mkdir(tmpdir)

        if '.zip' in file:  
                with ZipFile(file, 'r') as zipObj:
                        listOfFileNames = zipObj.namelist()
                        for entry in listOfFileNames: 
                                if "annotation" in entry:
                                        if 'IW' in file.split(os.sep)[-1]:
                                                if (pol.lower() in entry) and ('iw1' in entry) and (not 'calibration' in entry) and (not 'noise' in entry) and (not 'rfi' in entry) and (check_IW1 == True):
                                                        path_xml_IW1 = entry
                                                if (pol.lower() in entry) and ('iw2' in entry) and (not 'calibration' in entry) and (not 'noise' in entry) and (not 'rfi' in entry) and (check_IW2 == True):
                                                        path_xml_IW2 = entry
                                                if (pol.lower() in entry) and ('iw3' in entry) and (not 'calibration' in entry) and (not 'noise' in entry) and (not 'rfi' in entry) and (check_IW3 == True):
                                                        path_xml_IW3 = entry
                                        else:
                                                if (pol.lower() in entry) and (not 'calibration' in entry) and (not 'noise' in entry):
                                                        path_xml = entry
                                                
                        if 'IW' in file.split(os.sep)[-1]:
                                if not path_xml_IW1 == None:
                                        zipObj.extract(path_xml_IW1, path=tmpintdir, pwd=None)   
                                        shutil.copy2(tmpintdir+os.sep+path_xml_IW1,tmpdir+os.sep+'tmp_IW1.xml')
                                if not path_xml_IW2 == None:        
                                        zipObj.extract(path_xml_IW2, path=tmpintdir, pwd=None)    
                                        shutil.copy2(tmpintdir+os.sep+path_xml_IW2,tmpdir+os.sep+'tmp_IW2.xml')
                                if not path_xml_IW3 == None: 
                                        zipObj.extract(path_xml_IW3, path=tmpintdir, pwd=None)  
                                        shutil.copy2(tmpintdir+os.sep+path_xml_IW3,tmpdir+os.sep+'tmp_IW3.xml')
                        else:
                                zipObj.extract(path_xml, path=tmpintdir, pwd=None) 
                                shutil.copy2(tmpintdir+os.sep+path_xml,tmpdir+os.sep+'tmp.xml') 

                shutil.rmtree(tmpintdir)
        else:
                listOfFiles = os.listdir(file+os.sep+"annotation") 
                for entry in listOfFiles:
                        if 'IW' in file.split(os.sep)[-1]:
                                if (pol.lower() in entry) and ('iw1' in entry) and (not 'calibration' in entry) and (not 'noise' in entry) and (not 'rfi' in entry) and (check_IW1 == True):
                                        path_xml_IW1 = file+os.sep+"annotation"+os.sep+entry
                                if (pol.lower() in entry) and ('iw2' in entry) and (not 'calibration' in entry) and (not 'noise' in entry) and (not 'rfi' in entry) and (check_IW2 == True):
                                        path_xml_IW2 = file+os.sep+"annotation"+os.sep+entry
                                if (pol.lower() in entry) and ('iw3' in entry) and (not 'calibration' in entry) and (not 'noise' in entry) and (not 'rfi' in entry) and (check_IW3 == True):
                                        path_xml_IW3 = file+os.sep+"annotation"+os.sep+entry
                        else:
                                if (pol.lower() in entry) and (not 'calibration' in entry) and (not 'noise' in entry):
                                        path_xml = file+os.sep+"annotation"+os.sep+entry
        
                if 'IW' in file.split(os.sep)[-1]:
                        if not path_xml_IW1 == None: 
                                shutil.copy2(path_xml_IW1,tmpdir+os.sep+'tmp_IW1.xml')
                        if not path_xml_IW2 == None: 
                                shutil.copy2(path_xml_IW2,tmpdir+os.sep+'tmp_IW2.xml')
                        if not path_xml_IW3 == None: 
                                shutil.copy2(path_xml_IW3,tmpdir+os.sep+'tmp_IW3.xml')
                else:
                        shutil.copy2(path_xml,tmpdir+os.sep+'tmp.xml')

        if 'IW' in file.split(os.sep)[-1]:
                if not path_xml_IW1 == None:
                        data_xmli1, data_orbitsi1  = read_S1annotation_xml(tmpdir+os.sep+'tmp_IW1.xml') 
                if not path_xml_IW2 == None:
                        data_xmli2, data_orbitsi2  = read_S1annotation_xml(tmpdir+os.sep+'tmp_IW2.xml') 
                if not path_xml_IW3 == None:
                        data_xmli3, data_orbitsi3  = read_S1annotation_xml(tmpdir+os.sep+'tmp_IW3.xml') 
        else: 
                data_xmli1, data_orbitsi1  = read_S1annotation_xml(tmpdir+os.sep+'tmp.xml') 

        if os.path.isdir(tmpdir): 
                shutil.rmtree(tmpdir)

        S1annoresults = dict()
        S1annoresults['data_xmli1'] = data_xmli1
        S1annoresults['data_xmli2'] = data_xmli2
        S1annoresults['data_xmli3'] = data_xmli3
        S1annoresults['data_orbitsi1'] = data_orbitsi1
        S1annoresults['data_orbitsi2'] = data_orbitsi2
        S1annoresults['data_orbitsi3'] = data_orbitsi3

        return S1annoresults

def read_S1annotation_xml(path_xml): 
        """Read the annonation files from the S1 .xml files

        The function reads the annonation files from S1 .xml files

        Args:
                path_xml (str): Fullpath of the .xml files

        Returns:
                dict: Dict of Sentinel-1 annotations per subswath
                dict: Dict of S1 orbit per subswath

        """ 

        xmlfileslc = ET.parse(path_xml)

        data_xml = dict()

        data_xml['missionId'] = xmlfileslc.find('.//adsHeader/missionId').text
        data_xml['startTime'] = xmlfileslc.find('.//adsHeader/startTime').text
        data_xml['stopTime'] = xmlfileslc.find('.//adsHeader/stopTime').text
        data_xml['polarisation'] = xmlfileslc.find('.//adsHeader/polarisation').text
        data_xml['mode'] = xmlfileslc.find('.//adsHeader/mode').text   
        data_xml['absoluteOrbitNumber'] = xmlfileslc.find('.//adsHeader/absoluteOrbitNumber').text       
        data_xml['Pass'] = xmlfileslc.find('.//generalAnnotation/productInformation/pass').text
        data_xml['Looking'] = 'Right' 
        data_xml['Wavelength'] = ['C']
        data_xml['Frequency'] = [0]
        data_xml['productType'] = xmlfileslc.find('.//adsHeader/productType').text

        data_xml['azimuthTime'] = []
        data_xml['slantRangeTime'] = []
        data_xml['line'] = []
        data_xml['pixel'] = []
        data_xml['latitude'] = []
        data_xml['longitude'] = []
        data_xml['height'] = []
        data_xml['incidenceAngle'] = []
        data_xml['elevationAngle'] = []
        data_xml['Xtrack_f_DC'] = []
        data_xml['burst_loc'] = dict()

        data_xml['burst_loc']['id'] = []
        data_xml['burst_loc']['idx'] = []
        data_xml['burst_loc']['Polygon'] = []

        for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/azimuthTime'):
                data_xml['azimuthTime'].append(nodes.text)
        for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/slantRangeTime'):
                data_xml['slantRangeTime'].append(nodes.text)
        for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/line'):
                data_xml['line'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/pixel'):
                data_xml['pixel'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/latitude'):
                data_xml['latitude'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/longitude'):
                data_xml['longitude'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/height'):
                data_xml['height'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/incidenceAngle'):
                data_xml['incidenceAngle'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/elevationAngle'):
                data_xml['elevationAngle'].append(float(nodes.text))

        # azimuthTimestamp = []     
        # for di in data_xml['azimuthTime']:
        #         azimuthTimestamp.append(datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S.%f").timestamp())

        data_orbits = dict()
        data_orbits['time'] = []
        data_orbits['orb_X_int'] = []
        data_orbits['orb_Y_int'] = []
        data_orbits['orb_Z_int'] = []
        data_orbits['orb_VX_int'] = []
        data_orbits['orb_VY_int'] = []
        data_orbits['orb_VZ_int'] = []

        for nodes in xmlfileslc.findall('.//generalAnnotation/orbitList/orbit/time'): 
                data_orbits['time'].append(nodes.text)
        for nodes in xmlfileslc.findall('.//generalAnnotation/orbitList/orbit/position/x'): 
                data_orbits['orb_X_int'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//generalAnnotation/orbitList/orbit/position/y'): 
                data_orbits['orb_Y_int'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//generalAnnotation/orbitList/orbit/position/z'): 
                data_orbits['orb_Z_int'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//generalAnnotation/orbitList/orbit/velocity/x'): 
                data_orbits['orb_VX_int'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//generalAnnotation/orbitList/orbit/velocity/y'): 
                data_orbits['orb_VY_int'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//generalAnnotation/orbitList/orbit/velocity/z'): 
                data_orbits['orb_VZ_int'].append(float(nodes.text))

        # For the burst locations
        if data_xml['mode'] == 'IW': 

                burst_lines = int(xmlfileslc.find('.//swathTiming/linesPerBurst').text)
                burst_pixels = int(xmlfileslc.find('.//swathTiming/samplesPerBurst').text)

                burst_id = []
                for nodes in xmlfileslc.findall('.//swathTiming/burstList/burst/burstId'): 
                        burst_id.append(int(nodes.text))

                burst_Azitime = []
                for nodes in xmlfileslc.findall('.//swathTiming/burstList/burst/azimuthTime'): 
                        burst_Azitime.append(nodes.text)

                # burst_AzitimeTimestamp = []     
                # for di in burst_Azitime:
                #         burst_AzitimeTimestamp.append(datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S.%f").timestamp())

                # burst_firstValidSample = []
                # for nodes in xmlfileslc.findall('.//swathTiming/burstList/burst/firstValidSample'): 
                #         burst_firstValidSample.append([int(ele) for ele in nodes.text.split(' ')])

                # burst_lastValidSample = []
                # for nodes in xmlfileslc.findall('.//swathTiming/burstList/burst/lastValidSample'): 
                #         burst_lastValidSample.append([int(ele) for ele in nodes.text.split(' ')])

                top_right_idx = 0
                top_left_idx = 20
                bottom_left_idx = 41
                bottom_right_idx = 21
                for idx, id in enumerate(burst_Azitime):

                        poly_burst = Polygon(
                                [
                                        [data_xml['longitude'][top_right_idx], data_xml['latitude'][top_right_idx]],
                                        [data_xml['longitude'][top_left_idx], data_xml['latitude'][top_left_idx]],
                                        [data_xml['longitude'][bottom_left_idx], data_xml['latitude'][bottom_left_idx]],
                                        [data_xml['longitude'][bottom_right_idx], data_xml['latitude'][bottom_right_idx]],
                                ]
                        )

                        top_right_idx = top_right_idx + 21
                        top_left_idx = top_left_idx + 21
                        bottom_left_idx = bottom_left_idx + 21
                        bottom_right_idx = bottom_right_idx + 21

                        try: 
                                data_xml['burst_loc']['id'].append(burst_id[idx])
                        except: 
                                data_xml['burst_loc']['id'].append(None)

                        data_xml['burst_loc']['idx'].append(idx)
                        data_xml['burst_loc']['Polygon'].append(poly_burst)

        else:
                data_xml['burst_loc'] = None

        return data_xml, data_orbits

def read_precise_restitued_xml(path_xml): 
        """Read the S1 precise and restitued orbit files

        The function reads the S1 precise and restitued orbit files

        Args:
                path_xml (str): Fullpath of the .EOF files

        Returns:
                dict: Dict of Sentinel-1 annotations per subswath
                dict: Dict of S1 orbit per subswath

        """ 
        print(path_xml)
        xmlfileslc = ET.parse(path_xml)

        data_orbits = dict()
        data_orbits['time'] = []
        data_orbits['orb_X_int'] = []
        data_orbits['orb_Y_int'] = []
        data_orbits['orb_Z_int'] = []
        data_orbits['orb_VX_int'] = []
        data_orbits['orb_VY_int'] = []
        data_orbits['orb_VZ_int'] = []

        for nodes in xmlfileslc.findall('.//Data_Block/List_of_OSVs/OSV/UTC'): 
                data_orbits['time'].append(nodes.text.split('=')[1])
        for nodes in xmlfileslc.findall('.//Data_Block/List_of_OSVs/OSV/X'): 
                data_orbits['orb_X_int'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//Data_Block/List_of_OSVs/OSV/Y'): 
                data_orbits['orb_Y_int'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//Data_Block/List_of_OSVs/OSV/Z'): 
                data_orbits['orb_Z_int'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//Data_Block/List_of_OSVs/OSV/VX'): 
                data_orbits['orb_VX_int'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//Data_Block/List_of_OSVs/OSV/VY'): 
                data_orbits['orb_VY_int'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//Data_Block/List_of_OSVs/OSV/VZ'): 
                data_orbits['orb_VZ_int'].append(float(nodes.text))

        return data_orbits

def detection_S1burst_fromROI(roi,S1annoresults): 
        """Detect the burst from a ROI

        The function detects the cooresponding bursts from a ROI

        Args:
                roi (any): ROI
                S1annoresults (dict): Dict of S1 annotations

        Returns:
                dict: Dict of Sentinel-1 bursts
                
        """ 

        polyROI = Polygon(
                [
                        [np.min(roi.exterior.xy[0]), np.min(roi.exterior.xy[1])],
                        [np.max(roi.exterior.xy[0]), np.min(roi.exterior.xy[1])],
                        [np.max(roi.exterior.xy[0]), np.max(roi.exterior.xy[1])],
                        [np.min(roi.exterior.xy[0]), np.max(roi.exterior.xy[1])],
                ]
        )
        
        burst_roi = dict()
        burst_roi['idx'] = []
        burst_roi['id'] = []
        burst_roi['Polygon'] = [] 
        burst_roi['iw'] = [] 

        for idx_iw, iwi in enumerate(['data_xmli1','data_xmli2','data_xmli3']): 
                if not S1annoresults[iwi] == None: 
                        for idx, polyi in enumerate(S1annoresults[iwi]['burst_loc']['Polygon']): 
                                if polyROI.intersects(polyi) == True:
                                        burst_roi['idx'].append(S1annoresults[iwi]['burst_loc']['idx'][idx])
                                        burst_roi['id'].append(S1annoresults[iwi]['burst_loc']['id'][idx])
                                        burst_roi['Polygon'].append(polyi)
                                        burst_roi['iw'].append(idx_iw)
        return burst_roi

def detectionS1IW(file): 
        """Detect the IW file available in .zip or .SAFE file

        The function detects the IW. 

        Args:
                file (str): Path of the file

        Returns:
                IW1, IW2, IW3 (bool)
                
        """ 

        IW1 = None
        IW2 = None
        IW3 = None

        if '.zip' in file:  
                with ZipFile(file, 'r') as zipObj:
                        listOfFileNames = zipObj.namelist()
                        for entry in listOfFileNames: 
                                if ("annotation" in entry) and ('-iw1-' in entry):
                                        IW1 = True 
                                if ("annotation" in entry) and ('-iw2-' in entry):
                                        IW2 = True 
                                if ("annotation" in entry) and ('-iw3-' in entry):
                                        IW3 = True 
        else:
                listOfFiles = os.listdir(file+os.sep+"annotation") 
                for entry in listOfFiles:
                        if ('-iw1-' in entry):
                                IW1 = True 
                        if ('-iw2-' in entry):
                                IW2 = True 
                        if ('-iw3-' in entry):
                                IW3 = True 

        return IW1, IW2, IW3

def listnewS1acquisition(job,verbose=True):
        """List the next and planned acquisitions of Sentinel-1 from an EZ-InSAR job

        The function lists the next and planned acquisitions of Sentinel-1 from an EZ-InSAR job

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose

        Returns:
                list: List of data in EZ-InSAR format

        """ 

        usermessage.openingmsg(__name__,listnewS1acquisition.__name__,__file__,__copyright__,'List the new Sentinel-1 acquisitions',job.log,verbose)

        ## Detection of the files
        usermessage.ezprint('Detection of the files provided by ESA',job.log,verbose)
        url = "https://sentinels.copernicus.eu/web/sentinel/copernicus/sentinel-1/acquisition-plans"
        html = urllib.request.urlopen(url)        
        text = html.read()
        plaintext = text.decode('utf8')
        links = re.findall("href=[\"\'](.*?)[\"\']", plaintext)
        listfile = []
        for li in links:
                if "_mp_" in li.lower():
                        if li.startswith('/documents'):
                                li = 'https://sentinels.copernicus.eu'+li
                        listfile.append(li)

        ## Create the dummy list 
        
        listSLC = copy.deepcopy(listSLCempty)

        def drop_z(coords):
                return [(x, y) for x, y, *rest in coords]

        ## Detection 
        usermessage.ezprint('Detection in progress...',job.log,verbose)

        ## For safety
        if os.path.isfile(constants.__cachedir__+os.sep+'plannedS1.kml'):
                os.remove(constants.__cachedir__+os.sep+'plannedS1.kml')
        if os.path.isdir(constants.__cachedir__+os.sep+'plannedS1'):
                shutil.rmtree(constants.__cachedir__+os.sep+'plannedS1')
        
        for idx, file in enumerate(listfile): 

                usermessage.ezprint('\tFor the file %s of %s' % (idx+1,len(listfile)),job.log,verbose)

                miscellaneous.download_file(file,
                                        output_file=constants.__cachedir__+os.sep+'plannedS1.kml',
                                        verbose=verbose)
        
                os.system("ogr2ogr -f CSV %s %s -lco GEOMETRY=AS_WKT" % (constants.__cachedir__+os.sep+'plannedS1',
                                                       constants.__cachedir__+os.sep+'plannedS1.kml'))

                listcsv = glob.glob(constants.__cachedir__+os.sep+'plannedS1'+os.sep+'S1*.csv')

                for csvifile in listcsv: 
                        data = pd.read_csv(csvifile)

                        for idx, rowi in data.iterrows(): 
                                polyi3d = Polygon(loads(rowi['WKT']))
                                polyi = Polygon(
                                        drop_z(polyi3d.exterior.coords),
                                        [drop_z(interior.coords) for interior in polyi3d.interiors]
                                        )

                                if job.roi.intersects(polyi):
                                        if (rowi['OrbitRelative'] == job.relorbit) and (rowi['Mode'] == job.satmode) and (datetime.datetime.strptime(rowi['ObservationTimeStart']+'.000000Z',"%Y-%m-%dT%H:%M:%S.%fZ") >= datetime.datetime.today()):
                                                                                                                
                                                name = '%s_%s_%s_%s_%s_%s_%s_%s_%s.zip' % (
                                                        rowi['SatelliteId'], 
                                                        rowi['Mode'], 
                                                        'SLC_', 
                                                        '1S'+rowi['Polarisation'], 
                                                        rowi['ObservationTimeStart'].replace('-','').replace(':',''),
                                                        rowi['ObservationTimeStop'].replace('-','').replace(':',''),
                                                        rowi['OrbitAbsolute'],
                                                        rowi['DatatakeId'],
                                                        'XXXX',
                                                )

                                                listSLC['Name'].append(name)

                                                listSLC['Date1'].append(rowi['ObservationTimeStart']+'.000000Z')
                                                listSLC['Date2'].append(rowi['ObservationTimeStop']+'.000000Z')
                                                listSLC['Platform'].append(rowi['SatelliteId'])
                                                listSLC['Mode'].append(job.satmode)
                                                listSLC['Orbit'].append(int(rowi['OrbitAbsolute']))
                                                listSLC['RelativeOrbit'].append(int(rowi['OrbitRelative']))
                                                listSLC['PolyFrame'].append(str(polyi))
                                                listSLC['OrbitDirection'].append(job.satpass)
                                                listSLC['ProcessingLevel'].append('SLC')

                                                if rowi['Polarisation'] == 'SH': 
                                                        listSLC['Polarisation1'].append('HH')
                                                        listSLC['Polarisation2'].append(None)
                                                        listSLC['Polarisation3'].append(None)
                                                        listSLC['Polarisation4'].append(None)
                                                elif rowi['Polarisation'] == 'SV': 
                                                        listSLC['Polarisation1'].append('VV')
                                                        listSLC['Polarisation2'].append(None)
                                                        listSLC['Polarisation3'].append(None)
                                                        listSLC['Polarisation4'].append(None)
                                                elif rowi['Polarisation'] == 'DH': 
                                                        listSLC['Polarisation1'].append('HH')
                                                        listSLC['Polarisation2'].append('HV')
                                                        listSLC['Polarisation3'].append(None)
                                                        listSLC['Polarisation4'].append(None)
                                                elif rowi['Polarisation'] == 'DV': 
                                                        listSLC['Polarisation1'].append('VV')
                                                        listSLC['Polarisation2'].append('VH')
                                                        listSLC['Polarisation3'].append(None)
                                                        listSLC['Polarisation4'].append(None)

                                                listSLC['Status'].append('PLANNED')

                if os.path.isfile(constants.__cachedir__+os.sep+'plannedS1.kml'):
                        os.remove(constants.__cachedir__+os.sep+'plannedS1.kml')
                if os.path.isdir(constants.__cachedir__+os.sep+'plannedS1'):
                        shutil.rmtree(constants.__cachedir__+os.sep+'plannedS1')

                usermessage.ezprint('\t\tdone',job.log,verbose)

        print(listSLC)
        
        listSLC = slctools.checklistconsistency(listSLC,log=job.log,verbose=verbose) 
        listSLC = pd.DataFrame.from_dict(listSLC)
        
        ## Cleaning 
        date1save = listSLC['Date1']
        listSLC['Date1'] = pd.to_datetime(listSLC['Date1'],format='%Y-%m-%dT%H:%M:%S.%fZ')
        listSLC = listSLC.drop_duplicates(subset=['Date1']) 
        listSLC = listSLC.sort_values(by='Date1', ascending=True)
        listSLC['Date1'] = date1save
        listSLC = listSLC.reset_index(drop=True)
        
        return listSLC


        
