#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage RADARSAT-2 images for EZ-InSAR

The module allows to manage RADARSAT-2 images for an `EIjob`
    
    (From `ezinsar` package)

Changelog:
        * 1.0.0: Initial version, Feb. 2024

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
        """Initialise the RSAT2 SLC list 

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
        
        usermessage.openingmsg(__name__,initiateSLC.__name__,__file__,__copyright__,'Create the SLC list for EZ-InSAR for RadarSAT-2',job.log,verbose)

        if not job.satellite == None:
                if job.satellite == 'RSAT2': 
                        if mode == 'onfile':
                                usermessage.ezprint('Mode: base on files - the RSAT2 SLC list will be created based on available files:',job.log,verbose)
                                job = createRSAT2listonfile(job,verbose)
        else:
                raise ValueError(usermessage.errormsg(__name__,initiateSLC.__name__,__file__,__copyright__,'The satellite is not defined.',job.log))
                
        return job

################################################################################
################################################################################
## Sub-functions
################################################################################
################################################################################
def createRSAT2listonfile(job,verbose):
        """Create the RadarSAT-2 SLC list with the **onfile** mode

        The function initialise the RadarSAT-2  SLC for an ``EIjob``, with the **onfile** mode.  

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose

        Returns:
                `EIjob`: Return an EZ-InSAR class

        """ 
        lon,lat = job.roi.exterior.xy

        listSLC = copy.deepcopy(listSLCempty)
        
        listfile = glob.glob(job.pathSLC+os.sep+'RS2*')
        listfile = sorted(listfile, key=lambda x: x.split(os.sep)[-1].split('_')[5])[::-1]

        for filei in listfile:
                usermessage.ezprint('Process the file %s' % (filei),job.log,verbose)

                pol = job.polarisation[0]

                RSAT2annoresults = detectRSAT2annotation(filei,pol)
                resanno = RSAT2annoresults['data_xmli1']

                listSLC['Name'].append(filei.split(os.sep)[-1])

                listSLC['Date1'].append(resanno['startTime'])
                listSLC['Date2'].append(resanno['stopTime'])
                listSLC['Platform'].append(resanno['missionId'])

                if resanno['mode'] == 'Standard Quad Polarization':
                        listSLC['Mode'].append('SQ')
                elif resanno['mode'] == 'Fine Quad Polarization':
                        listSLC['Mode'].append('FQ')
                
                listSLC['Beam'].append(resanno['beam'])

                listSLC['Orbit'].append(int(resanno['absoluteOrbitNumber']))
                listSLC['RelativeOrbit'].append(int(resanno['absoluteOrbitNumber']))

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
                raise ValueError(usermessage.errormsg(__name__,createRSAT2listonfile.__name__,__file__,__copyright__,'The list is empty.',job.log))

        return job 

def detectRSAT2annotation(file,pol):
        """Detect and read the annonation files from RSAT2 file

        The function detects and reads the annonation files

        Args:
                file (str): Fullpath of the S1 file
                pol (str): Selected polarisation (e.g., 'VV')

        Returns:
                dict: Dict of RSAT2 annotations

        """ 
        data_xmli1 = None
        data_orbitsi1 = None
        data_calibi1 = None

        path_annot = glob.glob(file+os.sep+'product.xml')
        path_tif = glob.glob(file+os.sep+'imagery*.tif')
        path_cal = glob.glob(file+os.sep+'lut*.xml')

        if not path_annot: 
                raise ValueError(usermessage.errormsg(__name__,initiateSLC.__name__,__file__,__copyright__,'Impossible to detect the product.xml in the directory %s' % (file),None))

        if not path_tif: 
                raise ValueError(usermessage.errormsg(__name__,initiateSLC.__name__,__file__,__copyright__,'Impossible to detect the imagery_PP.tif in the directory %s' % (file),None))

        if not path_cal: 
                raise ValueError(usermessage.errormsg(__name__,initiateSLC.__name__,__file__,__copyright__,'Impossible to detect the lutXXXX.xml in the directory %s' % (file),None))

        data_xmli1, data_orbitsi1  = read_RSAT2annotation_xml(path_annot[0]) 
      
        RSAT2annoresults = dict()
        RSAT2annoresults['data_xmli1'] = data_xmli1
        RSAT2annoresults['data_orbitsi1'] = data_orbitsi1

        return RSAT2annoresults

def read_RSAT2annotation_xml(path_xml): 
        """Read the annonation files from the RSAT2 .xml files

        The function reads the annonation files from RSAT2 .xml files

        Args:
                path_xml (str): Fullpath of the .xml files

        Returns:
                dict: Dict of Sentinel-1 annotations per subswath
                dict: Dict of S1 orbit per subswath

        """ 

        xmlfileslc = ET.parse(path_xml)

        data_xml = dict()
        data_orbits = dict() 

        if xmlfileslc.find('{http://www.rsi.ca/rs2/prod/xml/schemas}sourceAttributes').find('{http://www.rsi.ca/rs2/prod/xml/schemas}satellite').text == 'RADARSAT-2':
                data_xml['missionId'] = 'RSAT2'
        else:
               raise ValueError(usermessage.errormsg(__name__,initiateSLC.__name__,__file__,__copyright__,'No a RADARSAT-2 file.',None)) 
        
        data_xml['beam'] = xmlfileslc.find('{http://www.rsi.ca/rs2/prod/xml/schemas}sourceAttributes').find('{http://www.rsi.ca/rs2/prod/xml/schemas}beamModeMnemonic').text

        data_xml['startTime'] = xmlfileslc.find('{http://www.rsi.ca/rs2/prod/xml/schemas}imageGenerationParameters').find('{http://www.rsi.ca/rs2/prod/xml/schemas}sarProcessingInformation').find('{http://www.rsi.ca/rs2/prod/xml/schemas}zeroDopplerTimeFirstLine').text
        data_xml['stopTime'] = xmlfileslc.find('{http://www.rsi.ca/rs2/prod/xml/schemas}imageGenerationParameters').find('{http://www.rsi.ca/rs2/prod/xml/schemas}sarProcessingInformation').find('{http://www.rsi.ca/rs2/prod/xml/schemas}zeroDopplerTimeLastLine').text

        data_xml['polarisation'] = xmlfileslc.find('{http://www.rsi.ca/rs2/prod/xml/schemas}sourceAttributes').find('{http://www.rsi.ca/rs2/prod/xml/schemas}radarParameters').find('{http://www.rsi.ca/rs2/prod/xml/schemas}polarizations').text.split()

        data_xml['mode'] = xmlfileslc.find('{http://www.rsi.ca/rs2/prod/xml/schemas}sourceAttributes').find('{http://www.rsi.ca/rs2/prod/xml/schemas}radarParameters').find('{http://www.rsi.ca/rs2/prod/xml/schemas}acquisitionType').text
        
        data_xml['absoluteOrbitNumber'] = int(xmlfileslc.find('{http://www.rsi.ca/rs2/prod/xml/schemas}sourceAttributes').find('{http://www.rsi.ca/rs2/prod/xml/schemas}orbitAndAttitude').find('{http://www.rsi.ca/rs2/prod/xml/schemas}orbitInformation').find('{http://www.rsi.ca/rs2/prod/xml/schemas}orbitDataFile').text.split('_')[0])   
        
        data_xml['Pass'] = xmlfileslc.find('{http://www.rsi.ca/rs2/prod/xml/schemas}sourceAttributes').find('{http://www.rsi.ca/rs2/prod/xml/schemas}orbitAndAttitude').find('{http://www.rsi.ca/rs2/prod/xml/schemas}orbitInformation').find('{http://www.rsi.ca/rs2/prod/xml/schemas}passDirection').text.upper()
        
        data_xml['Looking'] = xmlfileslc.find('{http://www.rsi.ca/rs2/prod/xml/schemas}sourceAttributes').find('{http://www.rsi.ca/rs2/prod/xml/schemas}radarParameters').find('{http://www.rsi.ca/rs2/prod/xml/schemas}antennaPointing').text

        data_xml['Wavelength'] = ['C']

        data_xml['Frequency'] = float(xmlfileslc.find('{http://www.rsi.ca/rs2/prod/xml/schemas}sourceAttributes').find('{http://www.rsi.ca/rs2/prod/xml/schemas}radarParameters').find('{http://www.rsi.ca/rs2/prod/xml/schemas}radarCenterFrequency').text)
        
        data_xml['productType'] = xmlfileslc.find('{http://www.rsi.ca/rs2/prod/xml/schemas}imageGenerationParameters').find('{http://www.rsi.ca/rs2/prod/xml/schemas}generalProcessingInformation').find('{http://www.rsi.ca/rs2/prod/xml/schemas}productType').text

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

        for nodes in xmlfileslc.find('{http://www.rsi.ca/rs2/prod/xml/schemas}imageAttributes').find('{http://www.rsi.ca/rs2/prod/xml/schemas}geographicInformation').find('{http://www.rsi.ca/rs2/prod/xml/schemas}geolocationGrid').findall('{http://www.rsi.ca/rs2/prod/xml/schemas}imageTiePoint'):
        
                data_xml['line'].append(float(nodes.find('{http://www.rsi.ca/rs2/prod/xml/schemas}imageCoordinate').find('{http://www.rsi.ca/rs2/prod/xml/schemas}line').text))
                data_xml['pixel'].append(float(nodes.find('{http://www.rsi.ca/rs2/prod/xml/schemas}imageCoordinate').find('{http://www.rsi.ca/rs2/prod/xml/schemas}pixel').text))

                data_xml['latitude'].append(float(nodes.find('{http://www.rsi.ca/rs2/prod/xml/schemas}geodeticCoordinate').find('{http://www.rsi.ca/rs2/prod/xml/schemas}latitude').text))

                data_xml['longitude'].append(float(nodes.find('{http://www.rsi.ca/rs2/prod/xml/schemas}geodeticCoordinate').find('{http://www.rsi.ca/rs2/prod/xml/schemas}longitude').text))

                data_xml['height'].append(float(nodes.find('{http://www.rsi.ca/rs2/prod/xml/schemas}geodeticCoordinate').find('{http://www.rsi.ca/rs2/prod/xml/schemas}height').text))

        # Linear interpolation for the incidence angle
        tmp = [float(xmlfileslc.find('{http://www.rsi.ca/rs2/prod/xml/schemas}imageGenerationParameters').find('{http://www.rsi.ca/rs2/prod/xml/schemas}sarProcessingInformation').find('{http://www.rsi.ca/rs2/prod/xml/schemas}incidenceAngleNearRange').text),
                float(xmlfileslc.find('{http://www.rsi.ca/rs2/prod/xml/schemas}imageGenerationParameters').find('{http://www.rsi.ca/rs2/prod/xml/schemas}sarProcessingInformation').find('{http://www.rsi.ca/rs2/prod/xml/schemas}incidenceAngleFarRange').text)]
        usermessage.warningmsg(__name__,read_RSAT2annotation_xml.__name__,__file__,'RADARSAT-2 provides only near- and far-ragne incidence angles. They will be linearly interpolated.',None,True)
        b = tmp[0]
        a = (tmp[1] - tmp[0]) / (np.max(data_xml['pixel']) - np.min(data_xml['pixel']))
        data_xml['incidenceAngle'] = a * np.array(data_xml['pixel']) + b

        # Linear interpolation for the azimuthTime
        tmp1 = datetime.datetime.strptime(data_xml['startTime'],"%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
        tmp2 = datetime.datetime.strptime(data_xml['stopTime'],"%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
        usermessage.warningmsg(__name__,read_RSAT2annotation_xml.__name__,__file__,'RADARSAT-2 provides only start and stop azimut time. They will be linearly interpolated.',None,True)
        b = tmp1
        a = (tmp2 - tmp1) / (np.max(data_xml['line']) - np.min(data_xml['line']))
        data_xml['azimuthTime'] = []
        for di in a * np.array(data_xml['line']) + b:
               data_xml['azimuthTime'].append(datetime.datetime.fromtimestamp(di).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

        data_orbits = dict()
        data_orbits['time'] = []
        data_orbits['orb_X_int'] = []
        data_orbits['orb_Y_int'] = []
        data_orbits['orb_Z_int'] = []
        data_orbits['orb_VX_int'] = []
        data_orbits['orb_VY_int'] = []
        data_orbits['orb_VZ_int'] = []

        for nodes in xmlfileslc.find('{http://www.rsi.ca/rs2/prod/xml/schemas}sourceAttributes').find('{http://www.rsi.ca/rs2/prod/xml/schemas}orbitAndAttitude').find('{http://www.rsi.ca/rs2/prod/xml/schemas}orbitInformation').findall('{http://www.rsi.ca/rs2/prod/xml/schemas}stateVector'):

                data_orbits['time'].append(nodes.find('{http://www.rsi.ca/rs2/prod/xml/schemas}timeStamp').text)
                
                data_orbits['orb_X_int'].append(float(nodes.find('{http://www.rsi.ca/rs2/prod/xml/schemas}xPosition').text))
                data_orbits['orb_Y_int'].append(float(nodes.find('{http://www.rsi.ca/rs2/prod/xml/schemas}yPosition').text))
                data_orbits['orb_Z_int'].append(float(nodes.find('{http://www.rsi.ca/rs2/prod/xml/schemas}zPosition').text))

                data_orbits['orb_VX_int'].append(float(nodes.find('{http://www.rsi.ca/rs2/prod/xml/schemas}xVelocity').text))
                data_orbits['orb_VY_int'].append(float(nodes.find('{http://www.rsi.ca/rs2/prod/xml/schemas}yVelocity').text))
                data_orbits['orb_VZ_int'].append(float(nodes.find('{http://www.rsi.ca/rs2/prod/xml/schemas}zVelocity').text))

        return data_xml, data_orbits
