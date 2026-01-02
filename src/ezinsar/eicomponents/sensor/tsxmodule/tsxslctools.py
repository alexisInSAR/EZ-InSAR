#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage TerraSAR-X and PAZ SLCs for EZ-InSAR

The module allows to manage TerraSAR-X and PAZ SLCs in .zip for an `EIjob`
    
    (From `ezinsar` package)

Changelog:
        * 1.1.0: Some optimisations, Feb. 2024, Alexis Hrysiewicz
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
import xml.etree.ElementTree as ET
from scipy.spatial import ConvexHull
from typing import Optional
import xml.etree.ElementTree as ET
import shutil
import xmltodict
import re
import copy 

from ezinsar.eicomponents.slcmodule import slctools
from ezinsar import constants
from ezinsar import usermessage
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
        server: Optional[str] = None, 
        satellite: Optional[str] = 'TSX', 
        ):
        """Initialise the TSX/PAZ SLC list 

        The function initialise the TSX/PAZ SLC listfor an ``EIjob``. 

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                mode (str): Mode for the list creation [Default: 'onfile']. Can be 'online' or 'list' or 'onfile' 
                server (str): Server for the 'online' mode [Default: 'None']. Not used
                satellite (str): Satellite [Default: 'TSX']. Not used.

        Returns:
                `EIjob`: Return an EZ-InSAR class

        """   

        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,initiateSLC.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        
        if not (isinstance(mode,str) and mode in ['onfile']):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,initiateSLC.__name__,__file__,__copyright__,
                        'mode','"online" or "onfile"',job.log))
                
        if not (isinstance(satellite,str) and satellite in ['TSX','PAZ']):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,initiateSLC.__name__,__file__,__copyright__,
                        'mode','"TSX or PAZ"',job.log))
        
        usermessage.openingmsg(__name__,initiateSLC.__name__,__file__,__copyright__,'Create the TSSX/PAZ SLC list for EZ-InSAR',job.log,verbose)

        if not job.satellite == None:
                if job.satellite == 'TSX' or job.satellite == 'PAZ': 
                        if mode == 'onfile':
                                usermessage.ezprint('Mode: base on files - the SLC list will be created based on available files:',job.log,verbose)
                                job = createTSXlistonfile(job,verbose)
        else:
                raise ValueError(usermessage.errormsg(__name__,initiateSLC.__name__,__file__,__copyright__,'The satellite is not defined.',job.log))
                
        return job

################################################################################
################################################################################
## Sub-functions
################################################################################
################################################################################
def createTSXlistonfile(job,verbose):
        """Create the TSX/PAZ SLC list with the **onfile** mode

        The function initialise the TSX/PAZ SLC for an ``EIjob``, with the **onfile** mode.  

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose

        Returns:
                `EIjob`: Return an EZ-InSAR class

        """ 
        lon,lat = job.roi.exterior.xy

        listSLC = copy.deepcopy(listSLCempty)

        listfile = glob.glob(job.pathSLC+os.sep+'PAZ*') + glob.glob(job.pathSLC+os.sep+'TSX*')

        for filei in listfile:
                usermessage.ezprint('Process the file %s' % (filei),job.log,verbose)

                pol = job.polarisation[0]

                TSXannoresults = detectTSXannotationfromxml(filei,pol)

                listSLC['Name'].append(filei.split(os.sep)[-1])
                listSLC['Date1'].append(TSXannoresults['data_xmli1']['startTime'])
                listSLC['Date2'].append(TSXannoresults['data_xmli1']['stopTime'])
                listSLC['Platform'].append(TSXannoresults['data_xmli1']['missionId'])
                listSLC['Mode'].append(TSXannoresults['data_xmli1']['mode'])
                listSLC['Beam'].append(None)
                listSLC['Orbit'].append(int(TSXannoresults['data_xmli1']['absoluteOrbitNumber']))
                listSLC['RelativeOrbit'].append(int(TSXannoresults['data_xmli1']['relativeOrbitNumber']))
                listSLC['OrbitDirection'].append(TSXannoresults['data_xmli1']['Pass'].upper())
                listSLC['Looking'].append(TSXannoresults['data_xmli1']['Looking'])
                listSLC['Wavelength'].append(TSXannoresults['data_xmli1']['Wavelength'])
                listSLC['Frequency'].append(TSXannoresults['data_xmli1']['Frequency'])
                listSLC['ProcessingLevel'].append(TSXannoresults['data_xmli1']['productType'])
                listSLC['Server'].append('DISK')
                listSLC['Url'].append(filei)
                listSLC['Status'].append('DISK')
                listSLC['SizeMB'].append(float(0))
                listSLC['Stored'].append(False)
                listSLC['Processed'].append(False)

                for idx in [1,2,3,4]:
                        try: 
                                listSLC['Polarisation%s' % (idx)].append(TSXannoresults['data_xmli1']['polarisation'][idx-1])
                        except: 
                                listSLC['Polarisation%s' % (idx)].append(None)
            
                lonpts = TSXannoresults['data_xmli1']['longitude']
                latpts = TSXannoresults['data_xmli1']['latitude']
                
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
                raise ValueError(usermessage.errormsg(__name__,createTSXlistonfile.__name__,__file__,__copyright__,'The list is empty.',job.log))

        return job 

def detectTSXannotationfromxml(file,pol):
        """Detect and read the annonation files from TSX directory (or PAZ)

        The function detects and reads the annonation files from TSX directory (or PAZ)

        Args:
                file (str): Fullpath of the TSX directory
                pol (str): Selected polarisation (e.g., 'VV')

        Returns:
                dict: Dict of TerraSAR-X annotations

        """ 
        filexml = glob.glob(file+os.sep+'*SAR*.xml')[0]
        data_xmli1, data_orbitsi1  = read_TSXannotation_xml(filexml) 

        TSXannoresults = dict()
        TSXannoresults['data_xmli1'] = data_xmli1
        TSXannoresults['data_orbitsi1'] = data_orbitsi1

        return TSXannoresults

def read_TSXannotation_xml(path_xml): 
        """Read the annonation files from the TSX .xml files

        The function reads the annonation files from TSX .xml files

        Args:
                path_xml (str): Fullpath of the .xml files

        Returns:
                dict: Dict of TSX annotations per subswath
                dict: Dict of S1 orbit per subswath

        """ 

        xmlfileslc = ET.parse(path_xml)

        data_xml = dict()

        data_xml['missionId'] = xmlfileslc.find('.//generalHeader/mission').text
        data_xml['startTime'] = xmlfileslc.find('.//sceneInfo/start/timeUTC').text
        data_xml['stopTime'] = xmlfileslc.find('.//sceneInfo/stop/timeUTC').text
        data_xml['polarisation'] = []
        if xmlfileslc.find('.//productInfo/acquisitionInfo/polarisationMode').text == 'SINGLE': 
                data_xml['polarisation'].append(xmlfileslc.find('.//productInfo/acquisitionInfo/polarisationList/polLayer').text)
        else:  
                for poli in xmlfileslc.findall('.//productInfo/acquisitionInfo/polarisationList/polLayer'):
                        data_xml['polarisation'].append(poli.text.upper())
        
        data_xml['mode'] = xmlfileslc.find('.//productInfo/acquisitionInfo/imagingMode').text 

        data_xml['absoluteOrbitNumber'] = xmlfileslc.find('.//productInfo/missionInfo/absOrbit').text       
        data_xml['relativeOrbitNumber'] = xmlfileslc.find('.//productInfo/missionInfo/relOrbit').text   
        data_xml['Pass'] = xmlfileslc.find('.//productInfo/missionInfo/orbitDirection').text
        data_xml['productType'] =  'SLC'
        data_xml['Looking'] = 'Right'
        data_xml['Wavelength'] = ['X']
        data_xml['Frequency'] = [0]
        data_xml['azimuthTime'] = [xmlfileslc.findall('.//sceneInfo/sceneCenterCoord/azimuthTimeUTC')[0].text.split('Z')[0]]
        data_xml['slantRangeTime'] = []
        data_xml['line'] = [float(xmlfileslc.findall('.//sceneInfo/sceneCenterCoord/refRow')[0].text)]
        data_xml['pixel'] = [float(xmlfileslc.findall('.//sceneInfo/sceneCenterCoord/refColumn')[0].text)]
        data_xml['latitude'] = [float(xmlfileslc.findall('.//sceneInfo/sceneCenterCoord/lat')[0].text)]
        data_xml['longitude'] = [float(xmlfileslc.findall('.//sceneInfo/sceneCenterCoord/lon')[0].text)]
        data_xml['height'] = []
        data_xml['incidenceAngle'] = [float(xmlfileslc.findall('.//sceneInfo/sceneCenterCoord/incidenceAngle')[0].text)]
        data_xml['elevationAngle'] = []
        data_xml['Xtrack_f_DC'] = []

        for nodes in xmlfileslc.findall('.//sceneInfo/sceneCornerCoord/azimuthTimeUTC'):
                data_xml['azimuthTime'].append(nodes.text)
        for nodes in xmlfileslc.findall('.//sceneInfo/sceneCornerCoord/lat'):
                data_xml['latitude'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//sceneInfo/sceneCornerCoord/lon'):
                data_xml['longitude'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//sceneInfo/sceneCornerCoord/incidenceAngle'):
                data_xml['incidenceAngle'].append(float(nodes.text))

        for nodes in xmlfileslc.findall('.//sceneInfo/sceneCornerCoord/refRow'):
                data_xml['line'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//sceneInfo/sceneCornerCoord/refColumn'):
                data_xml['pixel'].append(float(nodes.text))

        data_orbits = dict()
        data_orbits['time'] = []
        data_orbits['orb_X_int'] = []
        data_orbits['orb_Y_int'] = []
        data_orbits['orb_Z_int'] = []
        data_orbits['orb_VX_int'] = []
        data_orbits['orb_VY_int'] = []
        data_orbits['orb_VZ_int'] = []

        for nodes in xmlfileslc.findall('.//orbit/stateVec/timeUTC'): 
                data_orbits['time'].append(nodes.text)
        for nodes in xmlfileslc.findall('.//orbit/stateVec/posX'): 
                data_orbits['orb_X_int'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//orbit/stateVec/posY'): 
                data_orbits['orb_Y_int'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//orbit/stateVec/posZ'): 
                data_orbits['orb_Z_int'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//orbit/stateVec/velX'): 
                data_orbits['orb_VX_int'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//orbit/stateVec/velY'): 
                data_orbits['orb_VY_int'].append(float(nodes.text))
        for nodes in xmlfileslc.findall('.//orbit/stateVec/velZ'): 
                data_orbits['orb_VZ_int'].append(float(nodes.text))

        data_xml['burst_loc'] = None

        return data_xml, data_orbits

################################################################################
## Function to split the polarisation for TSX and PAZ (required for ISCE)
################################################################################
def tsxsplitpol(job,
        slcpath,
        newpathSLC, 
        verbose: Optional[bool] = None, 
        ):
        """Split the polarisation data for TSX and PAZ (required for ISCE)

        The function will split the polarisation data for an ``EIjob`` coregistration. 

        Args:
                job (`EIjob`): EZ-InSAR job
                slcpath (str): Old path of the image
                newpathSLC (str): New path of the image
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                newslcpath

        """   

        if not os.path.isdir(newpathSLC): 
                os.mkdir(newpathSLC)

        slcname = os.path.abspath(slcpath).split(os.sep)[-1]
        
        # Create the directories
        if os.path.isdir(newpathSLC+os.sep+slcname): 
                shutil.rmtree(newpathSLC+os.sep+slcname)
        os.mkdir(newpathSLC+os.sep+slcname)
        for diri in ['ANNOTATION','AUXRASTER','IMAGEDATA','PREVIEW','SUPPORT']:
                if not os.path.isdir(newpathSLC+os.sep+slcname+os.sep+diri): 
                        os.mkdir(newpathSLC+os.sep+slcname+os.sep+diri)

        # Link the desired files
        listfile = glob.glob(os.path.abspath(slcpath)+os.sep+'ANNOTATION'+os.sep+'GEOREF.xml') + \
                glob.glob(os.path.abspath(slcpath)+os.sep+'ANNOTATION'+os.sep+'*'+job.polarisation[0].upper()+'*') + \
                glob.glob(os.path.abspath(slcpath)+os.sep+'AUXRASTER'+os.sep+'stdcalcomposite_MRES*') + \
                glob.glob(os.path.abspath(slcpath)+os.sep+'AUXRASTER'+os.sep+'*'+job.polarisation[0].upper()+'*') + \
                glob.glob(os.path.abspath(slcpath)+os.sep+'IMAGEDATA'+os.sep+'*'+job.polarisation[0].upper()+'*') + \
                glob.glob(os.path.abspath(slcpath)+os.sep+'PREVIEW'+os.sep+'BROWSE*') + \
                glob.glob(os.path.abspath(slcpath)+os.sep+'PREVIEW'+os.sep+'COMPOSITE_QL*') + \
                glob.glob(os.path.abspath(slcpath)+os.sep+'PREVIEW'+os.sep+'MAP_PLOT*') + \
                glob.glob(os.path.abspath(slcpath)+os.sep+'PREVIEW'+os.sep+'stdcalcomposite_MRES*') + \
                glob.glob(os.path.abspath(slcpath)+os.sep+'PREVIEW'+os.sep+'*'+job.polarisation[0].upper()+'*') + \
                glob.glob(os.path.abspath(slcpath)+os.sep+'SUPPORT'+os.sep+'*')

        for fi in listfile: 
                dironly = os.path.dirname(fi).split(os.sep)[-1]
                inputfile = fi
                outputfile = newpathSLC+os.sep+slcname+os.sep+dironly+os.sep+fi.split(os.sep)[-1]
                if os.path.islink(outputfile):
                        os.unlink(outputfile) 
                os.symlink(inputfile,outputfile)

        ## Modify the header file
        # Comment: 
        # The seperation of polarisation-related layers is very complex if the use
        # of automatic algorithm is desired. The first option is to manually script
        # the wanted and desired part from the .xml header file. 

        fixml = glob.glob(os.path.abspath(slcpath)+os.sep+'*SAR*.xml')[0]

        with open(fixml,'r') as f_in:
                xmlstr = (f_in.read())

        dictfile = xmltodict.parse(xmlstr)
        idx_poldel = []
        idx_polgood = -1
        nb_layer = len(dictfile['level1Product']['productInfo']['acquisitionInfo']['polarisationList']['polLayer'])

        for idx, poli in enumerate(dictfile['level1Product']['productInfo']['acquisitionInfo']['polarisationList']['polLayer']): 
                if not poli.upper() == job.polarisation[0].upper():
                        idx_poldel.append(idx+1)
                else: 
                        idx_polgood = idx+1

        list_substr = []
        for idx_pol in idx_poldel: 
                for key in ['imageData','quicklooks','dopplerCentroid','noise','imageDataQuality','calibrationConstant']: 
                        title_start=xmlstr.find('<%s layerIndex="%s"' % (key,idx_pol))
                        backend_text=xmlstr[title_start:]
                        title_end=backend_text.find('</%s>' % (key))
                        final_text=backend_text[0:title_end+len('</%s>' % (key))+1]
                        # print(final_text)
                        list_substr.append(final_text)

        for key in ['correctedInstrumentDelay','settings','antennaPattern']:
                for match1, match2 in zip(re.finditer(r"<%s>" % (key), xmlstr, re.DOTALL),re.finditer(r"</%s>" % (key), xmlstr, re.DOTALL)):
                        idx1 = match1.start()
                        idx2 = match2.end()  
                        substr = xmlstr[idx1:idx2+1]
                        if not '<polLayer>%s</polLayer>' % (job.polarisation[0].upper()) in substr:
                                list_substr.append(substr)
                
        for key in ['rawDataQuality']:
                for match1, match2 in zip(re.finditer(r"<%s>" % (key), xmlstr, re.DOTALL),re.finditer(r"</%s>" % (key), xmlstr, re.DOTALL)):
                        idx1 = match1.start()
                        idx2 = match2.end()  
                        substr = xmlstr[idx1:idx2+1]
                        if not '<polarization>%s</polarization>' % (job.polarisation[0].upper()) in substr:
                                list_substr.append(substr)

        for key in ['absCalFactor','internalDelay']:
                for match1, match2 in zip(re.finditer(r"<%s" % (key), xmlstr, re.DOTALL),re.finditer(r"</%s>" % (key), xmlstr, re.DOTALL)):
                        idx1 = match1.start()
                        idx2 = match2.end()  
                        substr = xmlstr[idx1:idx2]
                        if not 'polarisationChannel="%s"' % (job.polarisation[0].upper()) in substr:
                                list_substr.append(substr)

        for substri in list_substr:
                xmlstr = xmlstr.replace(substri, '')

        for idx, poli in enumerate(dictfile['level1Product']['productInfo']['acquisitionInfo']['polarisationList']['polLayer']): 
                if not poli.upper() == job.polarisation[0].upper():
                        xmlstr = xmlstr.replace('<polLayer>%s</polLayer>' % (poli), '')

        xmlstr = xmlstr.replace('layerIndex="%s"' % (idx_polgood), 'layerIndex="%s"' % (1))
        
        # print(xmlstr)
        with open(newpathSLC+os.sep+slcname+os.sep+fixml.split(os.sep)[-1], 'w') as output:
                output.write(xmlstr)
       
        return newpathSLC+os.sep+slcname


   