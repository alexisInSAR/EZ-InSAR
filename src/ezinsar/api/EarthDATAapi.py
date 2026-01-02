#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module for the Earth Data NASA server

The module allows to connect EZ-InSAR with the data stored by Earth Data NASA
    
    (From `ezinsar` package)

Changelog:
    * 3.2.2: Delete the support of wget for Windows, Alexis Hrysiewicz, Sep. 2025
    * 3.2.1: Add the checksum, Aug. 2025, Alexis Hrysiewicz
    * 3.2.0: Initial release, Alexis Hrysiewcz, Aug. 2025

"""
################################################################################
## Python packages
################################################################################
from typing import Optional, Union
from datetime import datetime, timedelta
from xml.etree import ElementTree
import requests
import numpy as np
import os 
import glob
import pandas as pd 
import shutil
from clint.textui import progress
import asf_search
from ezinsar.eicomponents.templatevar import listSLCempty
import copy 
import platform
import subprocess
import json
import xmltodict

from ezinsar import constants
from ezinsar import usermessage
from ezinsar.eicomponents.slcmodule import slctools
from ezinsar.tools import miscellaneous

################################################################################
## Variables
################################################################################
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""
################################################################################
## class query
################################################################################
class query:
    
    def __init__(self,
            satellite,
            roi,
            level = 'SLC',
            date1 = datetime.strptime('2025-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
            date2 = datetime.strptime('2027-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
            satmode = 'IW', 
            polarisation = ['VV'],
            relorbit = 1, 
            satpass = 'ASCENDING',
            beam = None,
            frame = None,
            freesearch = '', 
            verbose = True, 
            log = None,
            ):
        self.urlcollection = "https://cmr.earthdata.nasa.gov/search/collections.json"
        self.collection = {'title': [],'id' : []}
        self.granules = []

        self.platform = satellite
        self.roi = roi
        self.level = level
        self.date1 = date1
        self.date2 = date2

        self.satmode = satmode
        self.polarisation = polarisation
        self.relorbit = relorbit
        self.satpass = satpass

        self.pagesize = 100

        self.freesearch = freesearch

        usermessage.ezprint('Initialise of the query for the EarthDATA server:',log,verbose)
        usermessage.ezprint('\tSatellite: %s' % (self.platform),log,verbose)
        usermessage.ezprint('\tRegion of Interest: %s' % (self.roi),log,verbose)
        usermessage.ezprint('\tLevel: %s' % (self.level),log,verbose)
        usermessage.ezprint('\tDate 1: %s' % (self.date1),log,verbose)
        usermessage.ezprint('\tDate 2: %s' % (self.date2),log,verbose)
        usermessage.ezprint('\tSatellite Mode: %s' % (self.satmode),log,verbose)
        usermessage.ezprint('\tPolarisation: %s' % (self.polarisation),log,verbose)
        usermessage.ezprint('\tRelative orbit: %s' % (self.relorbit),log,verbose)
        usermessage.ezprint('\tPass direction: %s' % (self.satpass),log,verbose)
        usermessage.ezprint('\tPage Size: %s' % (self.pagesize),log,verbose)

        if self.platform == 'SWOT': 
            if self.freesearch == '': 
                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'A free search parameter is required for SWOT data.',log,verbose))
            usermessage.ezprint('\tFree search: %s' % (self.freesearch),log,verbose)

    def retrievecollection(self,
            verbose = True, 
            log = None,
            ):
        
        usermessage.ezprint('Find the collection(s):',log,verbose)
        usermessage.ezprint('\tSatellite: %s' % (self.platform),log,verbose)
        usermessage.ezprint('\tLevel: %s' % (self.level),log,verbose)

        if self.platform == 'Sentinel-1' or self.platform == 'S1':
            url = self.urlcollection + "?platform=Sentinel-1A&platform=Sentinel-1B&platform=Sentinel-1C&page_size=100"
        elif self.platform == 'ALOS':
            url = self.urlcollection + "?platform=ALOS&page_size=100"
        elif self.platform == 'SWOT':
            url = self.urlcollection + "?platform=SWOT&page_size=100"
        elif self.platform == 'NISAR-Track':
            url = self.urlcollection + "?platform=NISAR&page_size=100"

        response = requests.get(url).json()

        if not self.platform == 'NISAR-Track':
            for li in response['feed']['entry']:
                if self.level == 'SLC':
                    if (('SLC' in li['title']) or ('Single Look Complex' in li['title']) or ('Level 1.1' in li['title'])) and (not 'METADATA' in li['title']):
                        self.collection['title'].append(li['title'])
                        self.collection['id'].append(li['id'])
                elif ('SWOT' in li['title']) and (self.level in li['title']) and (self.freesearch in li['title']): 
                    self.collection['title'].append(li['title'])
                    self.collection['id'].append(li['id'])
        
        elif self.platform == 'NISAR-Track':
            for li in response['feed']['entry']:
                if 'NISAR Ancillary' in li['title']:
                    self.collection['title'].append(li['title'])
                    self.collection['id'].append(li['id'])

        usermessage.ezprint('Collection(s) found:',log,verbose)
        for idx, colleci in enumerate(self.collection['title']):
            usermessage.ezprint('\tTitle: %s' % (colleci),log,verbose)

        return self
    
    def retrievegranule(self,
            verbose = True, 
            log = None,
            ):

        xroi,yroi = self.roi.exterior.xy

        usermessage.ezprint('Find the granules(s):',log,verbose)

        bounding_box = '%s,%s,%s,%s' % (np.min(xroi),
                                    np.min(yroi),
                                    np.max(xroi),
                                    np.max(yroi))

        results = []

        for idxc, colleci in enumerate(self.collection['id']): 
            usermessage.ezprint('\tCollection: %s' % (self.collection['title'][idxc]),log,verbose)

            validpage = True
            idxpage = 1
            while validpage: 

                usermessage.ezprint('\tQuery the page %s' % (idxpage),log,verbose)
                if self.platform == 'NISAR-Track':
                    url = "https://cmr.earthdata.nasa.gov/search/granules.native?collection_concept_id=%s&page_size=%s&page_num=%s" % (colleci,
                        self.pagesize,
                        idxpage)
                else:
                    url = "https://cmr.earthdata.nasa.gov/search/granules.native?collection_concept_id=%s&bounding_box=%s&temporal=%s/%s&page_size=%s&page_num=%s" % (colleci,
                        bounding_box,
                        self.date1.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        self.date2.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        self.pagesize,
                        idxpage)

                response = xmltodict.parse(ElementTree.tostring(ElementTree.fromstring(requests.get(url).content)))

                try: 
                    results = results + response['results']['result']
                    idxpage = idxpage + 1
                except:
                    validpage = False
                    usermessage.ezprint('\t\tEnd of the query',log,verbose)

        usermessage.ezprint('\tTotal results: %s' % (len(results)),log,verbose)

        usermessage.ezprint('\tFiltering of granules:',log,verbose)      
        for ri in results:
                        
            if not self.platform in ['SWOT','NISAR-Track']: 
                metadata = ri['Granule']['AdditionalAttributes']['AdditionalAttribute']
                listmetadata = [x['Name'] for x in metadata]
            
                ## For Sentinel-1
                if self.platform == 'Sentinel-1' or self.platform == 'S1':
                    if (metadata[listmetadata.index('BEAM_MODE')]['Values']['Value'] == self.satmode) and ('+'.join(self.polarisation) in metadata[listmetadata.index('POLARIZATION')]['Values']['Value']) and ((metadata[listmetadata.index('PATH_NUMBER')]['Values']['Value'] == str(self.relorbit))) and ((metadata[listmetadata.index('ASCENDING_DESCENDING')]['Values']['Value'] == str(self.satpass))):
                        self.granules.append(ri['Granule'])

                ## For ALOS
                elif self.platform == 'ALOS':
                    if (metadata[listmetadata.index('BEAM_MODE')]['Values']['Value'] == self.satmode) and ('+'.join(self.polarisation) in metadata[listmetadata.index('POLARIZATION')]['Values']['Value']) and ((metadata[listmetadata.index('ASCENDING_DESCENDING')]['Values']['Value'] == str(self.satpass))):
                        self.granules.append(ri['Granule'])
                    
            elif self.platform == 'SWOT': 
                ## For SWOT
                ri = eval('%s' % (ri['#text']))
                self.granules.append(ri)


            elif self.platform == 'NISAR-Track':
                if 'NISAR_TrackFrame_L' in ri['#text']:
                    self.granules.append(ri)

        usermessage.ezprint('\t\tDone with %s granules' % (len(self.granules)),log,verbose)

        return self

###############################################################################
## retrieve FUNCTION
################################################################################
def retrieve(satellite, 
        roi, 
        date1 = datetime.strptime('2015-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
        date2 = datetime.strptime('2030-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
        level = 'SLC',
        satmode = 'IW', 
        polarisation = ['VV'],
        relorbit = 0, 
        satpass = 'ASCENDING',
        beam = None,
        frame = None,
        log = None, 
        verbose = True,
    ):
    """Retrieve a list of images for EarthData server.

    The function will retrieve a list of images for EarthData server based on user inputs. 

    Args:
        satellite (str): Satellite name 
        roi (any): Region of Interest in POLYGON format (shapely)
        date1 (any): start date for the request in datetime [Default: ``datetime.strptime('2015-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')``
        date2 (any): end date for the request in datetime [Default: ``datetime.strptime('2030-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')``
        level (str): Processing level regarding the satellite [Default: ``SLC``]
        satmode (str): Mode of acquisition [Default: ``IW``]
        polarisation (list): List of polarisation [Default: ``['VV]``]
        relorbit (number): Relative orbit for radar data [Default: ``1``] 
        satpass (str): Sallite directory [Default: ``ASCENDING``] 
        log (str): Log value
        verbose (bool): verbose [Default: `None`]

    Returns:
        list: List of data in EZ-InSAR format
    
    """ 

    if verbose == None:
            verbose = True
    if not isinstance(verbose,bool):
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'verbose','True or False',log))
    
    if not satellite in ['S1','RSAT']:
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'satellite',"['S1','RSAT']",log))
    
    usermessage.openingmsg(__name__,retrieve.__name__,__file__,__copyright__,'Create the image list for EZ-InSAR for %s data from the Earth Data NASA server' % (satellite),log,verbose)
   
    ## Query the collection
    response = query(satellite,
            roi,
            date1 = date1,
            date2 = date2,
            level = level,
            satmode = satmode,
            polarisation = polarisation,
            relorbit = relorbit,
            satpass = satpass,verbose=verbose,log=log).retrievecollection(verbose=verbose,log=log).retrievegranule(verbose=verbose,log=log)

    ## Create the list
    usermessage.ezprint('Create the data list:',log,verbose)
    listSLC = copy.deepcopy(listSLCempty)

    for granulei in response.granules:
        metadata = granulei['AdditionalAttributes']['AdditionalAttribute']
        listmetadata = [x['Name'] for x in metadata]

        if 'SENTINEL' in granulei['Platforms']['Platform']['ShortName']: 
            listSLC['Name'].append(granulei['DataGranule']['ProducerGranuleId']+'.zip')
        else: 
            listSLC['Name'].append(granulei['DataGranule']['ProducerGranuleId'])

        if not 'Z' in granulei['Temporal']['RangeDateTime']['BeginningDateTime']:
            granulei['Temporal']['RangeDateTime']['BeginningDateTime'] = granulei['Temporal']['RangeDateTime']['BeginningDateTime']+'Z'

        if len(granulei['Temporal']['RangeDateTime']['BeginningDateTime']) == 20: 
            granulei['Temporal']['RangeDateTime']['BeginningDateTime'] = granulei['Temporal']['RangeDateTime']['BeginningDateTime'].replace('Z','.000000Z')
            usermessage.warningmsg(__name__,retrieve.__name__,__file__,'Issue wiht the date format: The decimal second will be added.',log,verbose)
        listSLC['Date1'].append(granulei['Temporal']['RangeDateTime']['BeginningDateTime'])

        if len(granulei['Temporal']['RangeDateTime']['EndingDateTime']) == 20: 
            granulei['Temporal']['RangeDateTime']['EndingDateTime'] = granulei['Temporal']['RangeDateTime']['EndingDateTime'].replace('Z','.000000Z')
            usermessage.warningmsg(__name__,retrieve.__name__,__file__,'Issue wiht the date format: The decimal second will be added.',log,verbose)
        listSLC['Date2'].append(granulei['Temporal']['RangeDateTime']['EndingDateTime'])

        if granulei['Platforms']['Platform']['ShortName'].lower() == 'sentinel-1a':
            listSLC['Platform'].append('S1A')
        elif granulei['Platforms']['Platform']['ShortName'].lower() == 'sentinel-1b':
            listSLC['Platform'].append('S1B')
        elif granulei['Platforms']['Platform']['ShortName'].lower() == 'sentinel-1c':
            listSLC['Platform'].append('S1C')
        elif granulei['Platforms']['Platform']['ShortName'].lower() == 'sentinel-1d':
            listSLC['Platform'].append('S1D')

        listSLC['Mode'].append(metadata[listmetadata.index('BEAM_MODE_TYPE')]['Values']['Value'])
        listSLC['Beam'].append(metadata[listmetadata.index('BEAM_MODE')]['Values']['Value'])
        listSLC['Frame'].append(metadata[listmetadata.index('FRAME_NUMBER')]['Values']['Value'])
            
        listSLC['Orbit'].append(int(granulei['OrbitCalculatedSpatialDomains']['OrbitCalculatedSpatialDomain']['OrbitNumber']))

        listSLC['RelativeOrbit'].append(metadata[listmetadata.index('PATH_NUMBER')]['Values']['Value'])

        lat = [metadata[listmetadata.index('FAR_START_LAT')]['Values']['Value'],
               metadata[listmetadata.index('NEAR_START_LAT')]['Values']['Value'],
               metadata[listmetadata.index('NEAR_END_LAT')]['Values']['Value'],
               metadata[listmetadata.index('FAR_END_LAT')]['Values']['Value']]
        
        lon = [metadata[listmetadata.index('FAR_START_LON')]['Values']['Value'],
               metadata[listmetadata.index('NEAR_START_LON')]['Values']['Value'],
               metadata[listmetadata.index('NEAR_END_LON')]['Values']['Value'],
               metadata[listmetadata.index('FAR_END_LON')]['Values']['Value']]
        lonfloat = [float(x) for x in lon]
        latfloat = [float(x) for x in lat]

        polytmp = "POLYGON ((%f %f, %f %f, %f %f, %f %f, %f %f))" % (
                lonfloat[0], latfloat[0],
                lonfloat[1], latfloat[1],
                lonfloat[2], latfloat[2],
                lonfloat[3], latfloat[3],
                lonfloat[0], latfloat[0])
        
        listSLC['PolyFrame'].append(polytmp)

        listSLC['OrbitDirection'].append(metadata[listmetadata.index('ASCENDING_DESCENDING')]['Values']['Value'])

        if metadata[listmetadata.index('LOOK_DIRECTION')]['Values']['Value'] == 'R':
            listSLC['Looking'].append('Right')
        else: 
            listSLC['Looking'].append('Left')

        if 'sentinel' in granulei['Platforms']['Platform']['ShortName'].lower(): 
            listSLC['Wavelength'].append(['C'])

        listSLC['Frequency'].append([0])

        listSLC['ProcessingLevel'].append(metadata[listmetadata.index('PROCESSING_TYPE')]['Values']['Value'])

        pollist = metadata[listmetadata.index('POLARIZATION')]['Values']['Value'].split('+')

        listSLC['Polarisation1'].append(pollist[0])

        try: 
            listSLC['Polarisation2'].append(pollist[1])
        except:
            listSLC['Polarisation2'].append(None)

        try: 
            listSLC['Polarisation3'].append(pollist[2])
        except:
            listSLC['Polarisation3'].append(None) 

        try: 
            listSLC['Polarisation4'].append(pollist[3])
        except:
            listSLC['Polarisation4'].append(None)  

        listSLC['Server'].append('EarthDATA') 

        listSLC['Url'].append(granulei['OnlineAccessURLs']['OnlineAccessURL'][0]['URL']) 

        listSLC['Status'].append('ONLINE') 

        listSLC['SizeMB'].append(float(granulei['DataGranule']['SizeMBDataGranule']))

        listSLC['MD5CheckSum'].append(metadata[listmetadata.index('MD5SUM')]['Values']['Value'])

        listSLC['Stored'].append(False) 
        listSLC['Processed'].append(False) 
            
    listSLC = slctools.checklistconsistency(listSLC,log=log,verbose=verbose)
    listdata = pd.DataFrame.from_dict(listSLC)

    # ## Reindex, sorting by dates
    # listdates = [datetime.strptime(x,'%Y-%m-%dT%H:%M:%S.%fZ') for x in listSLC['Date1']]
    # sort_index = np.argsort(listdates)
    # listdata.loc[sort_index].reset_index(drop=True,inplace=True)

    usermessage.ezprint('\tdone',log,verbose)

    return listdata

################################################################################
## download FUNCTION
################################################################################
def download(image, 
        directory,
        username: Optional[str] = constants.__username__,  
        password: Optional[str] = constants.__password__,  
        log = None, 
        verbose = True,
    ):
    """Download a single file from ASF server.

    The function will download a single image from ASF server. 

    Args:
        image (any): Image row for EZ-InSAR data list
        directory (str): Directory for file storing
        username (str, Optional): Username of the server [Default: `constants.__username__`]. 
        password (str, Optional): password of the server [Default: `constants.__password__`].
        log (str): Log value [Default: `None`]
        verbose (bool): verbose [Default: `True`]

    """ 

    if verbose == None:
            verbose = True
    if not isinstance(verbose,bool):
        raise TypeError(usermessage.typeerrormsg(
            __name__,download.__name__,__file__,__copyright__,
            'verbose','True or False',log))
    
    if not isinstance(directory,str): 
        raise TypeError(usermessage.typeerrormsg(
            __name__,download.__name__,__file__,__copyright__,
            'directory','str',log))
    if not os.path.isdir(directory): 
        usermessage.warningmsg(__name__,download.__name__,__file__,'The directory for storing does not exist. It will be created.',log,verbose)
        os.makedirs(directory)

    usermessage.openingmsg(__name__,download.__name__,__file__,__copyright__,'Download a single file from the ASF server',log,verbose)

    ## Download the file 
    usermessage.ezprint('Download the file: %s' % (image['Name']),log,verbose)

    success = False

    while success == False:

        if os.path.isdir(directory+os.sep+'tmp'):
            shutil.rmtree(directory+os.sep+'tmp')
        os.mkdir(directory+os.sep+'tmp')

        if constants.__wgetlimit__ == 'auto': 
            if (datetime.today().hour > 22) and (datetime.today().hour < 5): 
                wgetlimit = constants.__wgetlimitmax__
            else:
                wgetlimit = constants.__wgetlimitmin__
        else:
                wgetlimit = constants.__wgetlimit__

        if constants.__SLCdownloader__ == 'wget':
            if  platform.system() == 'Windows':
                raise ValueError(usermessage.errormsg(__name__,download.__name__,__file__,constants.__copyright__,'The wget mode is not available with Windows. Please modify the __SLCdownloader__ option to python.',log))
            
            cmdi = 'wget --limit-rate %s -c --http-user="%s" --http-password="%s" "%s" -P %s' % (wgetlimit,username,password,image['Url'],directory+os.sep+'tmp')
            os.system(cmdi)

        else:
            miscellaneous.download_file(image['Url'],
                            username=username,
                            password=password,
                            verbose=verbose,
                            log=log,
                            output_file=directory+os.sep+'tmp'+os.sep+image['Name'])

        os.rename(directory+os.sep+'tmp'+os.sep+image['Url'].split('/')[-1],
            directory+os.sep+image['Url'].split('/')[-1])
        shutil.rmtree(directory+os.sep+'tmp')
    
        success = miscellaneous.checksum(directory+os.sep+image['Url'].split('/')[-1],
                image['MD5CheckSum'],
                verbose=False,
                log=log)
            
        if success == False:
            os.remove(directory+os.sep+image['Url'].split('/')[-1])

    usermessage.ezprint('\tdone',log,verbose)

