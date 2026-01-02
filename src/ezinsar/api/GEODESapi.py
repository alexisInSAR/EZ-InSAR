#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module for the GEODES server

The module allows to connect EZ-InSAR with the data stored by https://geodes.cnes.fr/. 
    
    (From `ezinsar` package)

Changelog:
        * 3.2.2: Delete the support of wget for Windows, Alexis Hrysiewicz, Sep. 2025
        * 3.2.1: Finalise the script
        * 3.1.0: Initial version, Feb. 2025

"""
################################################################################
## Python packages
################################################################################
from typing import Optional, Union
import datetime
import requests
import numpy as np
from shapely.geometry import Polygon
import pandas as pd 
import shutil
import os 
from clint.textui import progress
import copy 
import time
import platform

from ezinsar import constants
from ezinsar import usermessage
from ezinsar.eicomponents.templatevar import listSLCempty
from ezinsar.eicomponents.slcmodule import slctools
from ezinsar.tools import miscellaneous

################################################################################
## Variables
################################################################################
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

__nblimitpage__ = 25
"""str: Page-size limit
"""

################################################################################
## retrieve FUNCTION
################################################################################
def retrieve(satellite, 
        roi, 
        date1 = datetime.datetime.strptime('2015-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
        date2 = datetime.datetime.strptime('2030-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
        satmode = 'IW', 
        level = 'SLC',
        relorbit = 1,
        satpass = 'ASCENDING',
        polarisation = ['VV','VH'],
        cloudcover = 100, 
        log = None, 
        verbose = True,
    ):
    """Retrieve a list of images for GEODES server.

    The function will retrieve a list of images for GEODES server based on user inputs. 

    Args:
        satellite (str): Satellite name (i.e., S1, S2, etc.)
        roi (any): Region of Interest in POLYGON format (shapely)
        date1 (any): start date for the request in datetime [Default: ``datetime.strptime('2015-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')``
        date2 (any): end date for the request in datetime [Default: ``datetime.strptime('2030-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')``
        satmode (str): Mode of acquisition for radar data [Default: ``IW``] 
        level (str): Processing level regarding the satellite [Default: ``SLC``] 
        relorbit (number): Relative orbit for radar data [Default: ``1``] 
        satpass (str): Orbit direction for radar data [Default: ``ASCENDING``] 
        polarisation (list): Polarisation list for radar data [Default: ``[VV, VH]``] 
        cloudcover (float or int): Max. value of the cloud coverage for multispectral data [Default: 100]
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
    
    if not satellite in ['S1','Sentinel-1A','Sentinel-1B','Sentinel-1C','Sentinel-1D',
                        'S2','Sentinel-2A','Sentinel-2B',
                        'Venus','VM1','VM5',
                        ]:
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'satellite',"'S1','Sentinel-1A','Sentinel-1B','Sentinel-1C','Sentinel-1D','S2','Sentinel-2A','Sentinel-2B',Venus','VM1','VM5'",log))
    
    usermessage.openingmsg(__name__,retrieve.__name__,__file__,__copyright__,'Create the image list for EZ-InSAR for %s data from the GEODES server' % (satellite),log,verbose)

    ## Check the user input 
    usermessage.ezprint('User parameters:',log,verbose)
    usermessage.ezprint('\tSatellite: %s' % (satellite),log,verbose)

    if not 'polygon' in str(type(roi)).lower():
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'roi','Polygon',log))
    usermessage.ezprint('\tROI: %s' % (roi),log,verbose)

    if not 'datetime' in str(type(date1)).lower():
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'roi','datetime',log))
    usermessage.ezprint('\tDate 1: %s' % (date1),log,verbose)
    if not 'datetime' in str(type(date2)).lower():
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'date2','datetime',log))
    usermessage.ezprint('\tDate 2: %s' % (date2),log,verbose)

    if (satellite in ['Sentinel-1','S1','Sentinel-1A','Sentinel-1B','Sentinel-1C','Sentinel-1D']):
        if (not satmode in ['IW','SM']):
            raise TypeError(usermessage.typeerrormsg(
                __name__,retrieve.__name__,__file__,__copyright__,
                'satmode',"['IW','SM']",log))
        
        usermessage.ezprint('\tMode: %s' % (satmode),log,verbose)
    else: 
        usermessage.ezprint('\tMode: %s' % ('Bypassed'),log,verbose)

    if (satellite in ['S1','Sentinel-1A','Sentinel-1B']):
        if (not level in ['SLC']):
            raise TypeError(usermessage.typeerrormsg(
                __name__,retrieve.__name__,__file__,__copyright__,
                'level',"['SLC']",log))
        
        usermessage.ezprint('\tLevel: %s' % (level),log,verbose)
    elif (satellite in ['S2','Sentinel-2A','Sentinel-2B','Venus','VM1','VM5']):
        if not level in ['L1C','L2A']:
            raise TypeError(usermessage.typeerrormsg(
                __name__,retrieve.__name__,__file__,__copyright__,
                'level',"['L1C','L2A']",log))
    usermessage.ezprint('\tLevel: %s' % (level),log,verbose)

    if (satellite in ['Sentinel-1','S1','Sentinel-1A','Sentinel-1B','Sentinel-1C','Sentinel-1D']):
        if (not isinstance(relorbit,int)):
            raise TypeError(usermessage.typeerrormsg(
                __name__,retrieve.__name__,__file__,__copyright__,
                'relorbit','integer',log))
        
        usermessage.ezprint('\tRelative orbit: %s' % (relorbit),log,verbose)
    else: 
        usermessage.ezprint('\tRelative orbit: %s' % ('Bypassed'),log,verbose)

    if (satellite in ['Sentinel-1','S1','Sentinel-1A','Sentinel-1B','Sentinel-1C','Sentinel-1D']):
        if (not satpass in ['ASCENDING','DESCENDING']):
            raise TypeError(usermessage.typeerrormsg(
                __name__,retrieve.__name__,__file__,__copyright__,
                'satpass','ASCENDING or DESCENDING',log))
        
        usermessage.ezprint('\tOrbit direction: %s' % (satpass),log,verbose)
    else: 
        usermessage.ezprint('\tOrbit direction: %s' % ('Bypassed'),log,verbose)

    if (satellite in ['Sentinel-1','S1','Sentinel-1A','Sentinel-1B','Sentinel-1C','Sentinel-1D']):
        if (not isinstance(polarisation,list)):
            raise TypeError(usermessage.typeerrormsg(
                __name__,retrieve.__name__,__file__,__copyright__,
                'polarisation','list',log))

        for poli in polarisation: 
            if not poli in ['VV','VH','HV','HH']: 
                raise TypeError(usermessage.typeerrormsg(
                    __name__,retrieve.__name__,__file__,__copyright__,
                    'polarisation','VV or/and VH or/and HV or/and HH',log))
        
        usermessage.ezprint('\tPolarisation: %s' % (polarisation),log,verbose)
    else: 
        usermessage.ezprint('\tPolarisation: %s' % ('Bypassed'),log,verbose)

    cloudcover = int(cloudcover)
    if (satellite in ['S2','Sentinel-2A','Sentinel-2B','Venus','VM1','VM5']):
        if (not isinstance(cloudcover,int)):
            raise TypeError(usermessage.typeerrormsg(
                __name__,retrieve.__name__,__file__,__copyright__,
                'cloudcover','int',log))

        usermessage.ezprint('\tCloud cover: %s' % (cloudcover),log,verbose)
    else: 
        usermessage.ezprint('\tCloud cover: %s' % ('Bypassed'),log,verbose) 

    ## Create the request
    ## Create the query 
    listSLC = copy.deepcopy(listSLCempty)

    usermessage.ezprint('Send the request:',log,verbose) 
    headers = {'Content-Type': 'application/json'}
    url = "https://geodes-portal.cnes.fr/api/stac/search"

    endpage = False
    pagenb = 1
    while endpage == False:

        xbbox, ybbox = roi.exterior.xy
        payload = {"page": pagenb, "limit": __nblimitpage__, "bbox": [np.min(xbbox), np.min(ybbox), np.max(xbbox), np.max(ybbox)], 
                "sortBy": [{ "direction": 'asc', "field": "start_datetime" }],
                "query": dict()}
        
        payload['query']['start_datetime'] = {}
        payload['query']['end_datetime'] = {}
        payload['query']['start_datetime']['gte'] = date1.strftime('%Y-%m-%dT%H:%M:%S') + '.000Z'
        payload['query']['end_datetime']['lte'] = date2.strftime('%Y-%m-%dT%H:%M:%S') + '.000Z'

        ## For the Sentinel-1
        if (satellite in ['Sentinel-1','S1','Sentinel-1A','Sentinel-1B','Sentinel-1C','Sentinel-1D']):

            payload['query']['sar:polarizations'] = {}
            payload['query']['sar:polarizations']['in'] = polarisation

            payload['query']['platform'] = {}
            if satellite == 'S1':
                payload['query']['platform']['in'] = ['S1A','S1B','S1C','S1D']
            elif satellite == 'Sentinel-1A':
                payload['query']['platform']['in'] = ['S1A']
            elif satellite == 'Sentinel-1B':
                payload['query']['platform']['in'] = ['S1B']
            elif satellite == 'Sentinel-1C':
                payload['query']['platform']['in'] = ['S1C']
            elif satellite == 'Sentinel-1D':
                payload['query']['platform']['in'] = ['S1D']  

            payload['query']['product:type'] = {}
            payload['query']['product:type']['in'] = [level] 

            payload['query']['sar:instrument_mode'] = {}
            payload['query']['sar:instrument_mode']['in'] = [satmode]

            payload['query']['sar:polarizations']['in'] = polarisation

            payload['query']['sat:relative_orbit'] = {}
            payload['query']['sat:relative_orbit']['eq'] = relorbit

            payload['query']['spaceborne:orbitDirection'] = {}
            payload['query']['spaceborne:orbitDirection']['eq'] = satpass.lower().capitalize()

        ## For multispectral data
        else: 
            payload['query']['platform'] = {}
            if satellite == 'S2':
                payload['query']['platform']['in'] = ['S2A','S2B']
            elif satellite == 'Sentinel-2A':
                payload['query']['platform']['in'] = ['S2A']
            elif satellite == 'Sentinel-2B':
                payload['query']['platform']['in'] = ['S2B']  

            elif satellite == 'Venus':
                payload['query']['platform']['in'] = ['VM1','VM5']
            elif satellite == 'VM1':
                payload['query']['platform']['in'] = ['VM1']
            elif satellite == 'VM5':
                payload['query']['platform']['in'] = ['VM5']  

            payload['query']['eo:cloud_cover'] = {}
            payload['query']['eo:cloud_cover']['lte'] = cloudcover

            payload['query']['processing:level'] = {}
            if satellite in ['S2','Sentinel-2A','Sentinel-2B']:
                payload['query']['processing:level']['eq'] = level
            elif satellite in ['Venus','VM1','VM5']:
                payload['query']['processing:level']['eq'] = level
               
        data = str(payload).replace('\'','"')
        response = requests.post(url, data = data, headers = headers, verify=True).json()

        try:
            dummy = response['features'][0]['properties']

            nbreturn = response['context']['returned']
            nblimit = response['context']['limit']
            nbmatch = response['context']['matched']
            nbpagetotal = np.ceil(nbmatch/nblimit)

            endpage = False
            usermessage.ezprint('\tRequest for the page %d of %d (Return: %d / Total Matched: %d)' % (pagenb,nbpagetotal,nbreturn,nbmatch),log,verbose)
        except: 
            endpage = True
            usermessage.ezprint('\tEnd of the request',log,verbose)

        if satellite in ['S1','Sentinel-1','Sentinel-1A','Sentinel-1B','Sentinel-1C','Sentinel-1D']: 
            for idx, imgi in enumerate(response['features']): 

                ## FOR SENTINEL-1
                if (satellite == 'S1' or (imgi['properties']['Platform'] == 'S1A' and satellite == 'Sentinel-1A') or (imgi['properties']['Platform'] == 'S1B' and satellite == 'Sentinel-1B') or (imgi['properties']['Platform'] == 'S1C' and satellite == 'Sentinel-1C') or (imgi['properties']['Platform'] == 'S1D' and satellite == 'Sentinel-1D')) and (relorbit == imgi['properties']['sat:relative_orbit']): 
                    
                    # Name 
                    listSLC['Name'].append(imgi['properties']['identifier']+'.zip')
                    
                    # Date1
                    prefix = imgi['properties']['start_datetime'].split('.')[0]
                    decsec = imgi['properties']['start_datetime'].split('.')[-1].replace('Z','').ljust(6, '0')[:6]
                    listSLC['Date1'].append(prefix+'.'+decsec+'Z')

                    # Date2
                    prefix = imgi['properties']['end_datetime'].split('.')[0]
                    decsec = imgi['properties']['end_datetime'].split('.')[-1].replace('Z','').ljust(6, '0')[:6]
                    listSLC['Date2'].append(prefix+'.'+decsec+'Z')

                    # Platform
                    listSLC['Platform'].append(imgi['properties']['platform'])
                    
                    # Mode
                    listSLC['Mode'].append(imgi['properties']['sar:instrument_mode'])
                    
                    # Orbit
                    listSLC['Orbit'].append(imgi['properties']['sat:absolute_orbit'])
                    
                    # RelativeOrbit
                    listSLC['RelativeOrbit'].append(imgi['properties']['sat:relative_orbit'])
                    
                    #Polygon 
                    try:
                            listSLC['PolyFrame'].append(str(Polygon(imgi['geometry']['coordinates'][0])))
                    except:
                            listSLC['PolyFrame'].append(str(Polygon(imgi['geometry']['coordinates'][0][0])))
                    
                    # Pass
                    listSLC['OrbitDirection'].append(imgi['properties']['sat:orbit_state'])
                   
                    # Looking
                    listSLC['Looking'].append('Right')
                    
                    # Wavelength
                    listSLC['Wavelength'].append(['C'])
                    
                    # Frequency
                    listSLC['Frequency'].append([0])
                    
                    # Processing-levels
                    listSLC['ProcessingLevel'].append(imgi['properties']['product:type'])
                    
                    # Polarisation 1
                    listSLC['Polarisation1'].append(imgi['properties']['sar:polarizations'].split()[0])
                   
                    # Polarisation 2
                    try: 
                            listSLC['Polarisation2'].append(imgi['properties']['sar:polarizations'].split()[1])
                    except:
                            listSLC['Polarisation2'].append(None) 
                    
                    # Polarisation 3
                    listSLC['Polarisation3'].append(None) 
                    
                    # Polarisation 4
                    listSLC['Polarisation4'].append(None) 
                    
                    # SERVER
                    listSLC['Server'].append('GEODES') 
                    
                    # URL
                    a = imgi['assets'][imgi['properties']['identifier']+'.zip']['href']
                    listSLC['Url'].append(a) 

                    # Status 
                    listSLC['Status'].append('ONLINE') 
                    
                    # SIZE-(MB)
                    a = float(imgi['assets'][imgi['properties']['identifier']+'.zip']['description'].split('bytes')[0].split(':')[-1])/1e6
                    listSLC['SizeMB'].append(a)     

                    # MD5CheckSum
                    a = imgi['assets'][imgi['properties']['identifier']+'.zip']['description'].split(':')[-1].strip()
                    listSLC['MD5CheckSum'].append(a)

                    # Stored
                    listSLC['Stored'].append(False) 
                    
                    # Processed 
                    listSLC['Processed'].append(False) 

                    # Quicklook
                    keysquicklook = None
                    for x in list(imgi['assets'].keys()):
                        if x.endswith('.jpg') :
                            keysquicklook = x
                    if not keysquicklook == None:
                        keysquicklook = imgi['assets'][keysquicklook]['href']
                    listSLC['Quicklook'].append(keysquicklook)

        else: 
            for idx, imgi in enumerate(response['features']):
                # Name 
                listSLC['Name'].append(imgi['properties']['identifier']+'.zip')
                # Date1
                prefix = imgi['properties']['start_datetime'].split('.')[0]
                decsec = imgi['properties']['start_datetime'].split('.')[-1].replace('Z','').ljust(6, '0')[:6]
                listSLC['Date1'].append(prefix+'.'+decsec+'Z')
                # Date2
                prefix = imgi['properties']['end_datetime'].split('.')[0]
                decsec = imgi['properties']['end_datetime'].split('.')[-1].replace('Z','').ljust(6, '0')[:6]
                listSLC['Date2'].append(prefix+'.'+decsec+'Z')
                # Platform
                listSLC['Platform'].append(imgi['properties']['platform'])
                # Mode
                listSLC['Mode'].append(None)
                # Orbit
                listSLC['Orbit'].append(imgi['properties']['sat:absolute_orbit'])
                #Polygon 
                try:
                    listSLC['PolyFrame'].append(str(Polygon(imgi['geometry']['coordinates'][0])))
                except:
                    listSLC['PolyFrame'].append(str(Polygon(imgi['geometry']['coordinates'][0][0])))
                # Processing-levels
                listSLC['ProcessingLevel'].append(imgi['properties']['processing:level'])
                # SERVER
                listSLC['Server'].append('GEODES') 
                # URL
                keysquicklook = None
                for x in list(imgi['assets'].keys()):
                    if imgi['properties']['identifier'] in x:
                        keysquicklook = x
                listSLC['Url'].append(imgi['assets'][keysquicklook]['href'])

                a = None
                b = None
                for x in imgi['assets'][keysquicklook]['description'].split('\n'):
                    if 'File size:' in x:
                        a = float(x.split('bytes')[0].split(':')[-1])/1e6
                    if 'Checksum MD5:' in x:
                        b = x.split(':')[-1].strip()

                # SIZE-(MB)
                listSLC['SizeMB'].append(a)     

                # MD5CheckSum
                listSLC['MD5CheckSum'].append(b)     
        
                # Status 
                listSLC['Status'].append('ONLINE') 

                listSLC['Cloudcover'].append(imgi['properties']['eo:cloud_cover'])

                keysquicklook = None
                for x in list(imgi['assets'].keys()):
                    if x.endswith('.jpg') or x.endswith('QKL_ALL.png') :
                        keysquicklook = x
                if not keysquicklook == None:
                    keysquicklook = imgi['assets'][keysquicklook]['href']
                listSLC['Quicklook'].append(keysquicklook) 

        pagenb = pagenb + 1

    usermessage.ezprint('\tdone. The list has been created.',log,verbose)

    listSLC = slctools.checklistconsistency(listSLC,log=log,verbose=verbose) 
    listdata = pd.DataFrame.from_dict(listSLC)

    return listdata

################################################################################
## download FUNCTION
################################################################################
def download(image, 
        directory,
        password: Optional[str] = constants.__password__,
        verbose = True,
        verboseprogress = True,
        log = None, 
    ):
    """Download a single file from GEODES server.

    The function will download a single image from GEODES server. 

    Args:
        image (any): Image row for EZ-InSAR data list
        directory (str): Directory for file storing
        password (str, Optional): password of the server [Default: `constants.__password__`].
        log (str): Log value [Default: `None`]
        verbose (bool): verbose [Default: `True`]
        verboseprogress (bool): verbose of the progress bar [Default: `True`]
        
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

    usermessage.openingmsg(__name__,download.__name__,__file__,__copyright__,'Download a single file from the GEODES server',log,verbose)

    ## Check if the file is online 
    avail = checkavailabity(image, 
        password = password, 
        verbose = True,
        log = log, 
        )
        
    if avail == False: 
        raise ValueError(usermessage.errormsg(__name__,download.__name__,__file__,__copyright__,'The file is on Tier 3 (tape). The use has to request its transfer via the GEODES explorer.',log))

    ## Download 
    success = False
    while success == False:

        if constants.__SLCdownloader__ == 'python': 

            headers = {"X-API-Key": password}
            session = requests.Session()
            session.headers.update(headers)
            url = image['Url']
            
            response = session.get(url, headers=headers, stream=True, verify=False)
            # response.raise_for_status()
            # response.status_code == 429

            total_length = int(response.headers.get('content-length'))

            with open(directory+os.sep+image['Name']+'.tmp', "wb") as file:
                if verboseprogress: 
                    for chunk in progress.bar(response.iter_content(chunk_size=constants.__chunksize__), expected_size=(total_length/constants.__chunksize__) + 1): 
                        if chunk:
                            file.write(chunk)
                else: 
                    for chunk in response.iter_content(chunk_size=constants.__chunksize__):
                        if chunk:
                            file.write(chunk)

            os.rename(directory+os.sep+image['Name']+'.tmp',directory+os.sep+image['Name'])

        elif constants.__SLCdownloader__ == 'wget': 
            if platform.system() == 'Windows':
                    ValueError(usermessage.errormsg(__name__,download.__name__,__file__,constants.__copyright__,'The wget mode is not available with Windows. Please modify the __SLCdownloader__ option to python.',log))
            
            if os.path.isdir(directory+os.sep+'tmp'):
                shutil.rmtree(directory+os.sep+'tmp')
            os.mkdir(directory+os.sep+'tmp')

            if constants.__wgetlimit__ == 'auto': 
                if (datetime.datetime.today().hour > 22) and (datetime.datetime.today().hour < 5): 
                    wgetlimit = constants.__wgetlimitmax__
                else:
                    wgetlimit = constants.__wgetlimitmin__
            else:
                    wgetlimit = constants.__wgetlimit__

            cmdi = 'wget -L --no-check-certificate --limit-rate %s --header "X-API-Key: %s" "%s" -O %s' % (wgetlimit,password,image['Url'],directory+os.sep+'tmp'+os.sep+image['Name'])
            print(cmdi)
            os.system(cmdi)

            os.rename(directory+os.sep+'tmp'+os.sep+image['Name'],
                directory+os.sep+image['Name'])
            shutil.rmtree(directory+os.sep+'tmp')

        # Check the files
        success = miscellaneous.checksum(directory+os.sep+image['Name'],
                        image['MD5CheckSum'],
                        verbose=False,
                        log=log)

        if success == False:
            os.remove(directory+os.sep+image['Name'])
            raise ValueError(usermessage.errormsg(__name__,download.__name__,__file__,__copyright__,'The file is not correct (please check the user quota of GEODES server). The file will be deleted.',log))

################################################################################
## checkavailabity FUNCTION
################################################################################
def checkavailabity(image, 
        password: Optional[str] = constants.__password__,
        verbose = True,
        log = None, 
    ):
    """Check the availabity of a file 

    The function will check the availabity of a file 

    Args:
        image (any): Image row for EZ-InSAR data list
        password (str, Optional): password of the server [Default: `constants.__password__`].
        log (str): Log value [Default: `None`]
        verbose (bool): verbose [Default: `True`]
    """ 
    url = 'https://geodes-portal.cnes.fr/availability/' + image['Name'].split('.')[0]

    headers = {'Content-Type': 'application/json', "X-API-Key": password, "Prefer": "respond-async"}
    response = requests.get(url, headers = headers).json()
    
    availability = False
    for fi in response['files']: 
        if fi['checksum'] == image['MD5CheckSum']: 
            availability = fi['available']

    return availability
        





