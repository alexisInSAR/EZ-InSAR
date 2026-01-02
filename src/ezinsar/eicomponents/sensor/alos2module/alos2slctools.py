#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage ALOS-2 (and ALOS first generation) SLCs for EZ-InSAR

The module allows to manage ALOS-2 (and ALOS first generation) SLCs for an `EIjob`. Not working with ScanSAR data.  
    
    (From `ezinsar` package)

Changelog:
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
from scipy.spatial import ConvexHull
from typing import Optional
import xml.etree.ElementTree as ET
import xmltodict
import struct
import datetime
from scipy import interpolate
import pyproj
import copy 

from ezinsar import constants
from ezinsar import usermessage
from ezinsar.eicomponents.slcmodule import slctools
from ezinsar.eicomponents.templatevar import listSLCempty 
from ezinsar.api import ASFapi, Copernicusapi, GEODESapi, EarthDATAapi
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""
################################################################################
## Function to initialise the ALOS2 SLC list 
################################################################################
def initiateSLC(job,
        verbose: Optional[bool] = None, 
        mode: Optional[str] = 'onfile', 
        beam: Optional[str] = None,
        frame: Optional[int] = None,
        server: Optional[str] = constants.__S1server__, 
        satellite: Optional[str] = 'ALOS2', 
        ):
        """Initialise the ALOS2 SLC list 

        The function initialise the ALOS2 SLC for an ``EIjob``. 

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                mode (str): Mode for the list creation [Default: 'onfile']. 
                server (str): Server for the 'online' mode [Default: 'None']. Not used
                satellite (str): Satellite [Default: 'ALOS2']. Not used.

        Returns:
                `EIjob`: Return an EZ-InSAR class

        """   

        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,initiateSLC.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        
        if not (isinstance(mode,str) and mode in ['onfile','online']):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,initiateSLC.__name__,__file__,__copyright__,
                        'mode','"online" or "onfile"',job.log))
        
        if not (isinstance(satellite,str) and satellite in ['ALOS2','ALOS']):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,initiateSLC.__name__,__file__,__copyright__,
                        'mode','"ALOS2" or "ALOS"',job.log))
        
        usermessage.openingmsg(__name__,initiateSLC.__name__,__file__,__copyright__,'Create the SLC list for EZ-InSAR for ALOS-2 (or ALOS)',job.log,verbose)

        if not job.satellite == None:
                if job.satellite == 'ALOS2' or job.satellite == 'ALOS': 
                        if mode == 'onfile':
                                usermessage.ezprint('Mode: base on files - the SLC list will be created based on available files:',job.log,verbose)
                                job = createALOS2listonfile(job,verbose)
                        else:
                                usermessage.ezprint('Mode: online - the S1 SLC list will be created based on the job information:',job.log,verbose)
                                usermessage.ezprint('Acquisition mode: %s' %(job.satmode),job.log,verbose)
                                usermessage.ezprint('Relative orbite: %s' %(job.relorbit),job.log,verbose)
                                usermessage.ezprint('Pass direction: %s' %(job.satpass),job.log,verbose)
                                usermessage.ezprint('Polarisation: %s' %(job.polarisation),job.log,verbose)
                                usermessage.ezprint('Request for %s' % (satellite),job.log,verbose)
                                job = createALOS2listonline(job,verbose,server=server,satellite=satellite,beam=beam,polarisation=job.polarisation)
        else:
                raise ValueError(usermessage.errormsg(__name__,initiateSLC.__name__,__file__,__copyright__,'The satellite is not defined.',job.log))
                
        return job

################################################################################
################################################################################
## Sub-functions
################################################################################
################################################################################
def createALOS2listonline(job,verbose,server,satellite,beam,polarisation=['HH'],frame=None):
        """Create the ALOS/ALOS2 SLC list with the **online** mode

        The function initialise the ALOS/ALOS2 SLC for an ``EIjob``. 

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
                        beam = job.satmode, 
                        relorbit = job.relorbit, 
                        satpass = job.satpass,
                        polarisation = job.polarisation,
                        log = job.log, 
                        verbose = verbose,
                )

        # Save the list
        if listSLCpd.empty == False:
                job.SLClist = listSLCpd
        else:
                raise ValueError(usermessage.errormsg(__name__,createALOS2listonline.__name__,__file__,__copyright__,'The list is empty.',job.log))

        return job

def createALOS2listonfile(job,verbose):
        """Create the ALOS2 (or ALOS) SLC list with the **onfile** mode

        The function initialise the ALOS2 (or ALOS) SLC list for an ``EIjob``, with the **onfile** mode.  

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose

        Returns:
                `EIjob`: Return an EZ-InSAR class

        """ 
        lon,lat = job.roi.exterior.xy

        listSLC = copy.deepcopy(listSLCempty)
        
        listfile = []
        for li in glob.glob(job.pathSLC+os.sep+'*'+os.sep+'VOL*') + glob.glob(job.pathSLC+os.sep+'*'+os.sep+'*.CEOS'): 
                listfile.append(os.path.dirname(li))
        
        for filei in listfile:
                usermessage.ezprint('Process the file %s' % (filei),job.log,verbose)

                ALOS2annoresults = detectALOS2annotationfromxml(filei)

                listSLC['Name'].append(filei.split(os.sep)[-1])
                listSLC['Date1'].append(ALOS2annoresults['data_xmli1']['startTime'])
                listSLC['Date2'].append(ALOS2annoresults['data_xmli1']['stopTime'])
                listSLC['Platform'].append(ALOS2annoresults['data_xmli1']['missionId'])
                listSLC['Mode'].append(ALOS2annoresults['data_xmli1']['mode'])
                listSLC['Orbit'].append(int(ALOS2annoresults['data_xmli1']['absoluteOrbitNumber']))
                listSLC['RelativeOrbit'].append(int(ALOS2annoresults['data_xmli1']['relativeOrbitNumber']))
                listSLC['OrbitDirection'].append(ALOS2annoresults['data_xmli1']['Pass'].upper())
                listSLC['Looking'].append(ALOS2annoresults['data_xmli1']['Looking'])
                listSLC['Wavelength'].append(ALOS2annoresults['data_xmli1']['Wavelength'])
                listSLC['Frequency'].append(ALOS2annoresults['data_xmli1']['Frequency'])
                listSLC['ProcessingLevel'].append(ALOS2annoresults['data_xmli1']['productType'])
                listSLC['Server'].append('DISK')
                listSLC['Url'].append(filei)
                listSLC['Status'].append('DISK')
                listSLC['SizeMB'].append(float(0))
                listSLC['Stored'].append(False)
                listSLC['Processed'].append(False)

                for idx in [1,2,3,4]:
                        try: 
                                listSLC['Polarisation%s' % (idx)].append(ALOS2annoresults['data_xmli1']['polarisation'][idx-1])
                        except: 
                                listSLC['Polarisation%s' % (idx)].append(None)

                lonpts = ALOS2annoresults['data_xmli1']['longitude']
                latpts = ALOS2annoresults['data_xmli1']['latitude']
                
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
                raise ValueError(usermessage.errormsg(__name__,createALOS2listonfile.__name__,__file__,__copyright__,'The list is empty.',job.log))

        return job 

def detectALOS2annotationfromxml(file):
        """Detect and read the annonation files from the ALOS-2 (or ALOS) directory 

        The function detects and reads the annonation files from ALOS-2 (or ALOS) directory 

        Args:
                file (str): Fullpath of the ALOS-2 (or ALOS) directory

        Returns:
                dict: Dict of ALOS-2 (or ALOS) annotations

        """ 
        # If the file is provided by ASF
        if glob.glob(file+os.sep+'*.CEOS'): 
                fileLED = glob.glob(file+os.sep+'*.CEOS'+os.sep+'LED*')[0]
                fileVOL = glob.glob(file+os.sep+'*.CEOS'+os.sep+'VOL*')[0]
                fileTRL = glob.glob(file+os.sep+'*.CEOS'+os.sep+'TRL*')[0]
                fileIMG = glob.glob(file+os.sep+'*.CEOS'+os.sep+'IMG*')
                fileSUM = None
                fileXML = glob.glob(file+os.sep+'*.QR.XML')[0]
        
        # If the file is provided by JAXA
        else: 
                fileLED = glob.glob(file+os.sep+'LED*')[0]
                fileVOL = glob.glob(file+os.sep+'VOL*')[0]
                fileTRL = glob.glob(file+os.sep+'TRL*')[0]
                fileIMG = glob.glob(file+os.sep+'IMG*')
                fileSUM = glob.glob(file+os.sep+'summary*')[0]
                fileXML = None

        data_xmli1, data_orbitsi1  = read_ALOS2annotation(fileVOL,fileLED,fileTRL,fileIMG,fileSUM,fileXML) 

        ALOS2annoresults = dict()
        ALOS2annoresults['data_xmli1'] = data_xmli1
        ALOS2annoresults['data_orbitsi1'] = data_orbitsi1

        return ALOS2annoresults

def read_ALOS2annotation(fileVOL,fileLED,fileTRL,fileIMG,fileSUM,fileXML):
        """Read the annonation files from the ALOS2 files

        The function reads the annonation files from ALOS2 files

        Returns:
                dict: Dict of ALOS annotations per subswath
                dict: Dict of ALOS orbit per subswath

        """ 
        data_xml = dict()

        #############################################
        # This par is commun for both satellites
        
        # For the mission ID
        with open(fileVOL,'rb') as file:
                file.seek(360+20)
                value = struct.unpack_from("16s",file.read(16))[0].decode('utf-8').replace('D','E')
        data_xml['missionId'] = ' '.join(value.split())

        # For the productType
        with open(fileLED,'rb') as file:
                file.seek(720+1094)
                value = struct.unpack_from("16s",file.read(16))[0].decode('utf-8').replace('D','E')
        data_xml['productType'] = value.split()[0]
        
        # For the polarisation
        data_xml['polarisation'] = []
        for poli in ['VV','VH','HH','HV']: 
                for fi in np.sort(fileIMG): 
                        if poli in fi: 
                                data_xml['polarisation'].append(poli)    

        # For the mode / Looking
        with open(fileVOL,'rb') as file:
                file.seek(360+360*len(data_xml['polarisation'])+360*2+16)
                value = struct.unpack_from("40s",file.read(40))[0].decode('utf-8').split()[0]

        data_xml['mode'] = value.split(':')[-1][0:3]

        if value.split(':')[-1][0:3] == 'L': 
                data_xml['Looking'] = 'Left'
        else:
                data_xml['Looking'] = 'Right'

        if value.split(':')[-1][-1] == 'A': 
                data_xml['Pass'] = 'ASCENDING'
        else:
                data_xml['Pass'] = 'DESCENDING'

        data_xml['Wavelength'] = ['L']
        data_xml['Frequency'] = ['0']

        # For absoluteOrbitNumber / relativeOrbitNumber (fixed to 0)
        with open(fileLED,'rb') as file:
                file.seek(720+444)
                data_xml['absoluteOrbitNumber'] = struct.unpack_from("8s",file.read(8))[0].decode('utf-8').split()[0]
        data_xml['relativeOrbitNumber'] = '0'

        ########################################
        ## Tie-points
        try: 
                with open(fileIMG[0],'rb') as file:
                        file.seek(237)
                        SLCnblines = int(struct.unpack_from("8s",file.read(8))[0].decode('utf-8').split()[0])
                with open(fileIMG[0],'rb') as file:
                        file.seek(281)
                        SLCnbcols = int(struct.unpack_from("8s",file.read(8))[0].decode('utf-8').split()[0])
        except:
                with open(fileIMG[-1],'rb') as file:
                        file.seek(237)
                        SLCnblines = int(struct.unpack_from("8s",file.read(8))[0].decode('utf-8').split()[0])
                with open(fileIMG[-1],'rb') as file:
                        file.seek(281)
                        SLCnbcols = int(struct.unpack_from("8s",file.read(8))[0].decode('utf-8').split()[0])
                
        if data_xml['productType'] == '1.1':
                SLCnbcols = SLCnbcols / 8
        else:
                SLCnbcols = SLCnbcols / 2
        
        factor_undersampling_tiept = 100
        # l = np.arange(0, SLCnblines, factor_undersampling_tiept)
        # p = np.arange(0, SLCnbcols, factor_undersampling_tiept)
        l = np.round(np.linspace(0, SLCnblines, 10))
        p = np.round(np.linspace(0, SLCnbcols, 10))
        L, P = np.meshgrid(l,p)

        # For the longitude/latitude points 
        if 'AL2' in data_xml['missionId']:
                if data_xml['productType'] == '1.1':
                        offset = 720+4096+4680+16384+9860+1620+325000+511000+3072+728000
                else: 
                        offset = 720+4096+1620+4680+16384+9860+1620+325000+511000+3072+728000

                with open(fileLED,'rb') as file:
                        file.seek(offset+1024)
                        coeffstr = struct.unpack_from("1000s",file.read(1000))[0].decode('utf-8')
                        coeffstr = coeffstr.split()
                        coeff = []
                        for ci in coeffstr:
                                coeff.append(float(ci))

                with open(fileLED,'rb') as file:
                        file.seek(offset+3064)
                        origlat = float(struct.unpack_from("20s",file.read(20))[0].decode('utf-8').split()[0])
                        origlon = float(struct.unpack_from("20s",file.read(20))[0].decode('utf-8').split()[0])

                with open(fileLED,'rb') as file:
                        file.seek(offset+2024)
                        origpix = float(struct.unpack_from("20s",file.read(20))[0].decode('utf-8').split()[0])
                        origlin = float(struct.unpack_from("20s",file.read(20))[0].decode('utf-8').split()[0])
                
                L = L - origlin
                P = P - origpix

                LAT = coeff[0] * L**4 * P**4 + \
                        coeff[1] * L**3 * P**4 + \
                        coeff[2] * L**2 * P**4 + \
                        coeff[3] * L**1 * P**4 + \
                        coeff[4] * L**0 * P**4 + \
                        coeff[5] * L**4 * P**3 + \
                        coeff[6] * L**3 * P**3 + \
                        coeff[7] * L**2 * P**3 + \
                        coeff[8] * L**1 * P**3 + \
                        coeff[9] * L**0 * P**3 + \
                        coeff[10] * L**4 * P**2 + \
                        coeff[11] * L**3 * P**2 + \
                        coeff[12] * L**2 * P**2 + \
                        coeff[13] * L**1 * P**2 + \
                        coeff[14] * L**0 * P**2 + \
                        coeff[15] * L**4 * P**1 + \
                        coeff[16] * L**3 * P**1 + \
                        coeff[17] * L**2 * P**1 + \
                        coeff[18] * L**1 * P**1 + \
                        coeff[19] * L**0 * P**1 + \
                        coeff[20] * L**4 * P**0 + \
                        coeff[21] * L**3 * P**0 + \
                        coeff[22] * L**2 * P**0 + \
                        coeff[23] * L**1 * P**0 + \
                        coeff[24] * L**0 * P**0
                        
                LON = coeff[25] * L**4 * P**4 + \
                        coeff[26] * L**3 * P**4 + \
                        coeff[27] * L**2 * P**4 + \
                        coeff[28] * L**1 * P**4 + \
                        coeff[29] * L**0 * P**4 + \
                        coeff[30] * L**4 * P**3 + \
                        coeff[31] * L**3 * P**3 + \
                        coeff[32] * L**2 * P**3 + \
                        coeff[33] * L**1 * P**3 + \
                        coeff[34] * L**0 * P**3 + \
                        coeff[35] * L**4 * P**2 + \
                        coeff[36] * L**3 * P**2 + \
                        coeff[37] * L**2 * P**2 + \
                        coeff[38] * L**1 * P**2 + \
                        coeff[39] * L**0 * P**2 + \
                        coeff[40] * L**4 * P**1 + \
                        coeff[41] * L**3 * P**1 + \
                        coeff[42] * L**2 * P**1 + \
                        coeff[43] * L**1 * P**1 + \
                        coeff[44] * L**0 * P**1 + \
                        coeff[45] * L**4 * P**0 + \
                        coeff[46] * L**3 * P**0 + \
                        coeff[47] * L**2 * P**0 + \
                        coeff[48] * L**1 * P**0 + \
                        coeff[49] * L**0 * P**0
                
                data_xml['latitude'] = list(LAT.flatten())
                data_xml['longitude'] = list(LON.flatten())
                data_xml['line'] = list((L + origlin).flatten())
                data_xml['pixel'] = list((P + origpix).flatten())
                
        # For ALOS-1
        else:
                if not fileXML == None:
                        with open(fileXML,'r') as f_in:
                                xmlfile = (f_in.read())
                        dictfile = xmltodict.parse(xmlfile)
                        
                        # pts = dictfile['qualityReport']['geolocal']['eop:Footprint']['eop:multiExtentOf']['gml:MultiSurface']['gml:surfaceMember']['gml:Polygon']['gml:exterior']['gml:LinearRing']['gml:posList'].split(' ')
                        pts = dictfile['qualityReport']['geolocal']['wrsFootprint']['eop:Footprint']['eop:multiExtentOf']['gml:MultiSurface']['gml:surfaceMember']['gml:Polygon']['gml:exterior']['gml:LinearRing']['gml:posList'].split(' ')

                        data_xml['longitude'] = [float(pts[1]),
                                                float(pts[3]),
                                                float(pts[5]),
                                                float(pts[7]),
                                                float(pts[9]),
                                                ]
                        data_xml['latitude'] = [float(pts[0]),
                                                float(pts[2]),
                                                float(pts[4]),
                                                float(pts[6]),
                                                float(pts[8]),
                                                ]
                        
                        usermessage.warningmsg(__name__,__name__,__file__,'Compute the tie points. This computation needs to be checked.',None,True)

                        data_xml['line'] = [0, SLCnblines, SLCnblines, 0, 0]
                        data_xml['pixel'] = [0, 0, SLCnbcols, SLCnbcols, 0]
                        
                else: 
                        raise ValueError(usermessage.errormsg(__name__,createALOS2listonfile.__name__,__file__,__copyright__,'The .QR.xml file is required.',None))

        data_xml['height'] = []
        data_xml['Xtrack_f_DC'] = []
        data_xml['elevationAngle'] = []
        data_xml['Xtrack_f_DC'] = []
        data_xml['slantRangeTime'] = []

        # For the times
        if not fileSUM == None: 
                with open(fileSUM,'r') as fi: 
                        for line in fi:
                                if 'SceneStartDateTime=' in line: 
                                        value = line.split('=')[-1].split('\n')[0].replace('"','')
                                        data_xml['startTime'] = '%s-%s-%sT%s:%s:%s.%06dZ' % (
                                                        value.split()[0][0:4],
                                                        value.split()[0][4:6],
                                                        value.split()[0][6:8],
                                                        value.split()[1].split(':')[0],
                                                        value.split()[1].split(':')[1],
                                                        value.split()[1].split(':')[2].split('.')[0],
                                                        float(value.split()[1].split(':')[2].split('.')[1])*1000
                                                        )
                                elif 'SceneCenterDateTime=' in line: 
                                        value = line.split('=')[-1].split('\n')[0].replace('"','')
                                        data_xml['centerTime'] = '%s-%s-%sT%s:%s:%s.%06dZ' % (
                                                        value.split()[0][0:4],
                                                        value.split()[0][4:6],
                                                        value.split()[0][6:8],
                                                        value.split()[1].split(':')[0],
                                                        value.split()[1].split(':')[1],
                                                        value.split()[1].split(':')[2].split('.')[0],
                                                        float(value.split()[1].split(':')[2].split('.')[1])*1000
                                                        )
                                elif 'SceneEndDateTime=' in line: 
                                        value = line.split('=')[-1].split('\n')[0].replace('"','')
                                        data_xml['stopTime'] = '%s-%s-%sT%s:%s:%s.%06dZ' % (
                                                        value.split()[0][0:4],
                                                        value.split()[0][4:6],
                                                        value.split()[0][6:8],
                                                        value.split()[1].split(':')[0],
                                                        value.split()[1].split(':')[1],
                                                        value.split()[1].split(':')[2].split('.')[0],
                                                        float(value.split()[1].split(':')[2].split('.')[1])*1000
                                                        )

                # For the azimuthTime
                timing = [datetime.datetime.strptime(data_xml['startTime'],'%Y-%m-%dT%H:%M:%S.%fZ').timestamp(), 
                        datetime.datetime.strptime(data_xml['centerTime'],'%Y-%m-%dT%H:%M:%S.%fZ').timestamp(), 
                        datetime.datetime.strptime(data_xml['stopTime'],'%Y-%m-%dT%H:%M:%S.%fZ').timestamp()]

                timinterp = np.interp(data_xml['line'], [0, np.fix(SLCnblines/2), SLCnblines-1], timing)

        elif not fileXML == None: 
                # dictfile should be loaded
                data_xml['startTime'] = dictfile['qualityReport']['metadata']['productStartTime']
                data_xml['centerTime'] = 'NE'
                data_xml['stopTime'] = dictfile['qualityReport']['metadata']['productStopTime']

                timing = [datetime.datetime.strptime(data_xml['startTime'],'%Y-%m-%dT%H:%M:%S.%fZ').timestamp(), 
                        datetime.datetime.strptime(data_xml['stopTime'],'%Y-%m-%dT%H:%M:%S.%fZ').timestamp()]
                timinterp = np.interp(data_xml['line'], [0, SLCnblines-1], timing)

        else:
                raise ValueError(usermessage.errormsg(__name__,createALOS2listonfile.__name__,__file__,__copyright__,'The .QR.xml file is required.',None))

        data_xml['azimuthTime']  = []
        for ti in timinterp: 
                data_xml['azimuthTime'] .append(datetime.datetime.fromtimestamp(ti).strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

        ########################################
        ## Read the orbit data (This part seems commun)
        data_orbits = dict()
        data_orbits['time'] = []
        data_orbits['orb_X_int'] = []
        data_orbits['orb_Y_int'] = []
        data_orbits['orb_Z_int'] = []
        data_orbits['orb_VX_int'] = []
        data_orbits['orb_VY_int'] = []
        data_orbits['orb_VZ_int'] = []
        
        if data_xml['productType'] == '1.1':
                offset = 720+4096 
        else: 
                offset = 720
        with open(fileLED,'rb') as file:
                file.seek(offset+140)
                nb_orbitmeas = int(struct.unpack_from("4s",file.read(4))[0].decode('utf-8').split()[0])

        # Timing of the first point
        with open(fileLED,'rb') as file:
                file.seek(offset+144)
                fpt_year = int(struct.unpack_from("4s",file.read(4))[0].decode('utf-8').split()[0])
        with open(fileLED,'rb') as file:
                file.seek(offset+148)
                fpt_month = int(struct.unpack_from("4s",file.read(4))[0].decode('utf-8').split()[0])
        with open(fileLED,'rb') as file:
                file.seek(offset+152)
                fpt_day = int(struct.unpack_from("4s",file.read(4))[0].decode('utf-8').split()[0])
        with open(fileLED,'rb') as file:
                file.seek(offset+160)
                fpt_sec = float(struct.unpack_from("22s",file.read(22))[0].decode('utf-8').split()[0])
        with open(fileLED,'rb') as file:
                file.seek(offset+182)
                deltatime = float(struct.unpack_from("22s",file.read(22))[0].decode('utf-8').split()[0])

        hours = np.fix(fpt_sec / 3600)
        mins = np.fix((fpt_sec - (hours * 3600))/60)
        secs = fpt_sec -(hours * 3600 + mins * 60)

        initialtime = datetime.datetime.strptime('%04d-%02d-%02dT%02d:%02d:%02.6fZ' % (fpt_year,fpt_month,fpt_day,hours,mins,secs),'%Y-%m-%dT%H:%M:%S.%fZ')
      
        it = 1
        while it <= nb_orbitmeas: 
                
                timei = initialtime + (it-1) * datetime.timedelta(seconds=60)

                with open(fileLED,'rb') as file:
                        file.seek(offset+386+(it-1)*(518-387+1))
                
                        xi = float(struct.unpack_from("22s",file.read(22))[0].decode('utf-8').split()[0])
                        yi = float(struct.unpack_from("22s",file.read(22))[0].decode('utf-8').split()[0])
                        zi = float(struct.unpack_from("22s",file.read(22))[0].decode('utf-8').split()[0])
                        vxi = float(struct.unpack_from("22s",file.read(22))[0].decode('utf-8').split()[0])
                        vyi = float(struct.unpack_from("22s",file.read(22))[0].decode('utf-8').split()[0])
                        vzi = float(struct.unpack_from("22s",file.read(22))[0].decode('utf-8').split()[0])

                data_orbits['time'].append(timei.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
                data_orbits['orb_X_int'].append(xi)
                data_orbits['orb_Y_int'].append(yi)
                data_orbits['orb_Z_int'].append(zi)
                data_orbits['orb_VX_int'].append(vxi)
                data_orbits['orb_VY_int'].append(vyi)
                data_orbits['orb_VZ_int'].append(vzi)

                it = it + 1

        data_xml['burst_loc'] = None

        ########################################
        ## Computation of the incidence angle (from orbits)
        # Conversion of lon,lat coord to ECR (for the target points)
        transformer = pyproj.Transformer.from_crs(
            {"proj":'latlong', "ellps":'GRS80', "datum":'WGS84'},
            {"proj":'geocent', "ellps":'GRS80', "datum":'WGS84'},
            )
        meanelev = np.ones((1,len(data_xml['longitude'])))*250           
        x_target, y_target, z_target = transformer.transform(data_xml['longitude'],data_xml['latitude'],meanelev,radians = False)

        # Interpolation of orbits
        azimuthTimestamp_target = [] 
        for di in data_xml['azimuthTime']:
                azimuthTimestamp_target.append(datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S.%fZ").timestamp())

        azimuthTimestamp_orbit = [] 
        for di in data_orbits['time']:
                azimuthTimestamp_orbit.append(datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S.%fZ").timestamp())

        fi = interpolate.PchipInterpolator(azimuthTimestamp_orbit, data_orbits['orb_X_int'])
        x_sat_target = fi(azimuthTimestamp_target)
        fi = interpolate.PchipInterpolator(azimuthTimestamp_orbit, data_orbits['orb_Y_int'])
        y_sat_target = fi(azimuthTimestamp_target)
        fi = interpolate.PchipInterpolator(azimuthTimestamp_orbit, data_orbits['orb_Z_int'])
        z_sat_target = fi(azimuthTimestamp_target)

        slantrangedistance = np.sqrt((x_sat_target - x_target)**2 + (y_sat_target - y_target)**2 + (z_sat_target - z_target)**2)[0]/1000 # in km
        
        with open(fileLED,'rb') as file:
                file.seek(720+1886)
                a0 = float(struct.unpack_from("20s",file.read(20))[0].decode('utf-8').split()[0])
                a1 = float(struct.unpack_from("20s",file.read(20))[0].decode('utf-8').split()[0])
                a2 = float(struct.unpack_from("20s",file.read(20))[0].decode('utf-8').split()[0])
                a3 = float(struct.unpack_from("20s",file.read(20))[0].decode('utf-8').split()[0])
                a4 = float(struct.unpack_from("20s",file.read(20))[0].decode('utf-8').split()[0])
                a5 = float(struct.unpack_from("20s",file.read(20))[0].decode('utf-8').split()[0])
        
        data_xml['incidenceAngle'] = (a0 + a1 * slantrangedistance**1 + \
                a2 * slantrangedistance**2 + \
                a3 * slantrangedistance**3 + \
                a4 * slantrangedistance**4 + \
                a5 * slantrangedistance**5) * (180/np.pi) 
        
        return data_xml, data_orbits

################################################################################
## Function to split the polarisation for ALOS (required for ISCE)
################################################################################
def alossplitpol(job,
        slcpath,
        newpathSLC, 
        verbose: Optional[bool] = None, 
        ):
        """Split the polarisation data for ALOS (required for ISCE)

        The function will split the polarisation data for an ``EIjob`` coregistration. 

        Args:
                job (`EIjob`): EZ-InSAR job
                slcpath (str): old path of the ALOS file
                newpathSLC: new path of the ALOS file
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                

        """   

        raise ValueError(usermessage.errormsg(__name__,alossplitpol.__name__,__file__,__copyright__,
                        'Not implemented.',job.log))