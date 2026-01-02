#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module for the Copernicus server

The module allows to connect EZ-InSAR with the data stored by https://dataspace.copernicus.eu/
    
    (From `ezinsar` package)

Changelog:
    * 3.2.2: Delete the support of wget for Windows, Alexis Hrysiewicz, Sep. 2025
    * 3.2.1: Various changes, Alexis Hrysiewicz, Aug. 2025
        * Implementation of the orbit and ETAD files for Sentinel-1
    * 3.1.0: Initial version, Feb. 2025

"""
################################################################################
## Python packages
################################################################################
from typing import Optional, Union
from datetime import datetime, timedelta
import requests
import numpy as np
import os 
import time
from shapely.geometry import Polygon
import pandas as pd 
import shutil
from clint.textui import progress
import copy 
import glob
import platform

from ezinsar import constants
from ezinsar import usermessage
from ezinsar.eicomponents.slcmodule import slctools
from ezinsar.eicomponents.templatevar import listSLCempty

################################################################################
## Variables
################################################################################
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## retrieve FUNCTION
################################################################################
def retrieve(satellite, 
        roi, 
        date1 = datetime.strptime('2015-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
        date2 = datetime.strptime('2030-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
        level = 'SLC',
        satmode = 'IW', 
        polarisation = ['VV'],
        relorbit = 1, 
        satpass = 'ASCENDING',
        cloudcover = 100,
        SMswath = None,
        log = None, 
        verbose = True,
    ):
    """Retrieve a list of images for Copernicus server.

    The function will retrieve a list of images for Copernicus server based on user inputs. 

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
        cloudcover (float or int): Max. value of the cloud coverage [Default: 100]
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
    
    # if not satellite in ['S1','S2']:
    #     raise TypeError(usermessage.typeerrormsg(
    #         __name__,retrieve.__name__,__file__,__copyright__,
    #         'satellite',"['S1','S2']",log))

    usermessage.openingmsg(__name__,retrieve.__name__,__file__,__copyright__,'Create the image list for EZ-InSAR for %s data from the Copernicus server' % (satellite),log,verbose)

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

    if (not level in ['SLC','GRD','L1C', 'L2A','ETAD','OCN','Quarterly Mosaics','Monthly Mosaics']):
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'level',"['SLC','GRD','L1C', 'L2A','ETAD','OCN','Quarterly Mosaics','Monthly Mosaics']",log))
    usermessage.ezprint('\tLevel: %s' % (level),log,verbose)

    if (not isinstance(relorbit,int)):
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'relorbit','integer',log))
    if satellite == 'S1': 
        usermessage.ezprint('\tRelative orbit: %s' % (relorbit),log,verbose)

    if not satmode in ['IW','SM']: 
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'satmode','IW or SM',log))
    if satellite == 'S1': 
        usermessage.ezprint('\tMode of acquisition: %s' % (satmode),log,verbose)

    if not satpass in ['ASCENDING','DESCENDING']: 
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'satmode','IW or SM',log))
    if satellite == 'S1': 
        usermessage.ezprint('\tSatellite direction: %s' % (satpass),log,verbose)

    if satellite == 'S1': 
        if isinstance(polarisation,list): 
            for poli in polarisation: 
                if not poli in ['VV','VH','HV','HH']: 
                    raise TypeError(usermessage.typeerrormsg(
                        __name__,retrieve.__name__,__file__,__copyright__,
                        'polarisation',"['VV','VH','HV','HH']",log))
        else:
            raise TypeError(usermessage.typeerrormsg(
                __name__,retrieve.__name__,__file__,__copyright__,
                'polarisation','list',log))
        
    if (not isinstance(cloudcover,float)) and (not isinstance(cloudcover,int)):
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
                'level','float or int',log))
    if not satellite == 'S1': 
        usermessage.ezprint('\tMax. cloud coverage %s' % (cloudcover),log,verbose)
    
    ## Create the query 
    listSLC = copy.deepcopy(listSLCempty)
    
    lon,lat = roi.exterior.xy

    usermessage.ezprint('Send the request:',log,verbose)
    endpage = False
    pagenb = 1
    while endpage == False:
        if satellite == 'S1': 
            if level == 'Monthly Mosaics': 
                url = 'https://catalogue.dataspace.copernicus.eu/resto/api/collections/GLOBAL-MOSAICS/search.json?&maxRecords=50&box=%s&platform=%s&startDate=%s&completionDate=%s&page=%d' % (
                    '%s,%s,%s,%s' % (np.min(lon),np.min(lat),np.max(lon),np.max(lat)),
                    'SENTINEL-1',
                    date1.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    date2.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    pagenb)
                
            elif not level == 'ETAD': 

                if not relorbit == 0: 
                    url = 'https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel1/search.json?productType=%s&startDate=%s&completionDate=%s&maxRecords=100&box=%s&sensorMode=%s&orbitDirection=%s&relativeOrbitNumber=%d&sortParam=completionDate&sortOrder=descending&page=%d' % (level,
                                    date1.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    date2.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    '%s,%s,%s,%s' % (np.min(lon),np.min(lat),np.max(lon),np.max(lat)),
                                    satmode,
                                    satpass,
                                    relorbit,
                                    pagenb)
                    
                else: 
                    url = 'https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel1/search.json?productType=%s&startDate=%s&completionDate=%s&maxRecords=100&box=%s&sensorMode=%s&sortParam=completionDate&sortOrder=descending&page=%d' % (level,
                                    date1.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    date2.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    '%s,%s,%s,%s' % (np.min(lon),np.min(lat),np.max(lon),np.max(lat)),
                                    satmode,
                                    pagenb)
                    
            else: 

                usermessage.ezprint('The ETAD files are desired.',log,verbose)

                if not satmode == 'IW': 
                    level = '%s_ETA__AX' % (SMswath)
                else: 
                    level = '%s_ETA__AX' % (satmode)

                url = 'https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel1/search.json?productType=%s&startDate=%s&completionDate=%s&maxRecords=100&box=%s&sensorMode=%s&orbitDirection=%s&relativeOrbitNumber=%d&sortParam=completionDate&sortOrder=descending&page=%d' % (level,
                                date1.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                date2.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                '%s,%s,%s,%s' % (np.min(lon),np.min(lat),np.max(lon),np.max(lat)),
                                satmode,
                                satpass,
                                relorbit,
                                pagenb)
                
        elif satellite == 'S2': 
            if level == 'Quarterly Mosaics':
                url = 'https://catalogue.dataspace.copernicus.eu/resto/api/collections/GLOBAL-MOSAICS/search.json?&maxRecords=50&box=%s&platform=%s&page=%d' % (
                    '%s,%s,%s,%s' % (np.min(lon),np.min(lat),np.max(lon),np.max(lat)),
                    'SENTINEL-2',
                    pagenb)
            else:
                currentlevel = level.replace('L','S2MSI')
                url = 'https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json?startDate=%s&completionDate=%s&maxRecords=50&box=%s&cloudCover=[0,%s]&productType=%s&sortParam=completionDate&sortOrder=descending&page=%d' % (date1.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    date2.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    '%s,%s,%s,%s' % (np.min(lon),np.min(lat),np.max(lon),np.max(lat)),
                    int(cloudcover), 
                    currentlevel,
                    pagenb)
                
        elif 'COPDEM' in satellite:
            if '30' in satellite: 
                sat1 = 'COP-DEM'
                sat2 = 'DGE_30'
            else: 
                sat1 = 'COP-DEM'
                sat2 = 'DGE_90'
            
            url = 'https://catalogue.dataspace.copernicus.eu/resto/api/collections/%s/search.json?productType=%s&maxRecords=50&box=%s&sortParam=completionDate&sortOrder=descending&page=%d' % (sat1,sat2,'%s,%s,%s,%s' % (np.min(lon),np.min(lat),np.max(lon),np.max(lat)),
                pagenb)

        jsonresponse = requests.get(url).json()

        try:
            dummy = jsonresponse['features'][0]['properties']
            endpage = False
            usermessage.ezprint('\tRequest for the page %d' % (pagenb),log,verbose)
        except: 
            endpage = True
            usermessage.ezprint('\tEnd of the request',log,verbose)

        if satellite == 'S1' and (not level == 'Monthly Mosaics'): 
            for idx, imgi in enumerate(jsonresponse['features']): 

                polrequest = imgi['properties']['polarisation'].split('&')
                test_pol = False
                for poli in polarisation: 
                    if poli in polrequest:
                        test_pol = True
                    else:
                        test_pol = False

                ## FOR SENTINEL-1
                if (satellite == 'S1' or (imgi['properties']['Platform'] == 'S1A' and satellite == 'Sentinel-1A') or (imgi['properties']['Platform'] == 'S1B' and satellite == 'Sentinel-1B')) and (test_pol == True) and ((relorbit==0) or (relorbit == imgi['properties']['relativeOrbitNumber'])): 

                    # Name 
                    listSLC['Name'].append(imgi['properties']['title'].replace('.SAFE','.zip'))
                    # Date1
                    listSLC['Date1'].append(imgi['properties']['startDate'])
                    # Date2
                    listSLC['Date2'].append(imgi['properties']['completionDate'])
                    # Platform
                    listSLC['Platform'].append(imgi['properties']['platform'])
                    # Mode
                    listSLC['Mode'].append(imgi['properties']['sensorMode'])
                    # Orbit
                    listSLC['Orbit'].append(imgi['properties']['orbitNumber'])
                    # RelativeOrbit
                    listSLC['RelativeOrbit'].append(imgi['properties']['relativeOrbitNumber'])
                    #Polygon 
                    try:
                            listSLC['PolyFrame'].append(str(Polygon(imgi['geometry']['coordinates'][0])))
                    except:
                            listSLC['PolyFrame'].append(str(Polygon(imgi['geometry']['coordinates'][0][0])))
                    # Pass
                    listSLC['OrbitDirection'].append(imgi['properties']['orbitDirection'])
                    # Looking
                    listSLC['Looking'].append('Right')
                    # Wavelength
                    listSLC['Wavelength'].append(['C'])
                    # Frequency
                    listSLC['Frequency'].append([0])
                    # Processing-levels
                    listSLC['ProcessingLevel'].append('SLC')
                    # Polarisation 1
                    listSLC['Polarisation1'].append(polrequest[0])
                    # Polarisation 2
                    try: 
                            listSLC['Polarisation2'].append(polrequest[1])
                    except:
                            listSLC['Polarisation2'].append(None) 
                    # Polarisation 3
                    listSLC['Polarisation3'].append(None) 
                    # Polarisation 4
                    listSLC['Polarisation4'].append(None) 
                    # Quicklook
                    listSLC['Quicklook'].append(imgi['properties']['thumbnail']) 
                    # SERVER
                    listSLC['Server'].append('Copernicus') 
                    # URL
                    listSLC['Url'].append(imgi['properties']['services']['download']['url']) 
                    # Status 
                    listSLC['Status'].append(imgi['properties']['status']) 
                    # SIZE-(MB)
                    listSLC['SizeMB'].append(imgi['properties']['services']['download']['size']/1e6) 
                    # Stored
                    listSLC['Stored'].append(False) 
                    # Processed 
                    listSLC['Processed'].append(False) 

        else: 
            for idx, imgi in enumerate(jsonresponse['features']): 
                # Name 
                listSLC['Name'].append(imgi['properties']['title'].replace('.SAFE','.zip'))
                # Date1
                listSLC['Date1'].append(imgi['properties']['startDate'])
                # Date2
                listSLC['Date2'].append(imgi['properties']['completionDate'])
                # Platform
                listSLC['Platform'].append(imgi['properties']['platform'])
                # Mode
                listSLC['Mode'].append(imgi['properties']['sensorMode'])
                # Orbit
                listSLC['Orbit'].append(imgi['properties']['orbitNumber'])
                #Polygon 
                try:
                        listSLC['PolyFrame'].append(str(Polygon(imgi['geometry']['coordinates'][0])))
                except:
                        listSLC['PolyFrame'].append(str(Polygon(imgi['geometry']['coordinates'][0][0])))

                # Processing-levels
                listSLC['ProcessingLevel'].append(imgi['properties']['processingLevel'])
                # SERVER
                listSLC['Server'].append('Copernicus') 
                # URL
                listSLC['Url'].append(imgi['properties']['services']['download']['url']) 
                # Status 
                listSLC['Status'].append(imgi['properties']['status']) 
                # SIZE-(MB)
                listSLC['SizeMB'].append(imgi['properties']['services']['download']['size']/1e6)     
                
                listSLC['Cloudcover'].append(imgi['properties']['cloudCover'])
                listSLC['Quicklook'].append(imgi['properties']['thumbnail']) 

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
        username: Optional[str] = constants.__username__,  
        password: Optional[str] = constants.__password__,
        partialdownloading: Optional[Union[list,None]] = None,
        modepartial: Optional[str] = 'exclude', 
        zipping: Optional[bool] = True, 
        access_token = None, 
        session = None,
        headers = None,
        log = None, 
        verbose = True,
        verboseprogress = True,
        sizecheck = 250e6,
    ):
    """Download a single file from Copernicus server.

    The function will download a single image from Copernicus server. 

    Args:
        image (any): Image row for EZ-InSAR data list
        directory (str): Directory for file storing
        username (str, Optional): Username of the server [Default: `constants.__username__`]. 
        password (str, Optional): password of the server [Default: `constants.__password__`].
        partialdownloading (list, Optional): Download only selected part of the .zip file (only compatible with the Copernicus server)
        modepartial (str, Optional): Mode of the selection of the partial downloading. Can be include or exclude. (only compatible with the Copernicus server) [default: exclude]
        zipping (bool, Optional): Force the zipping of .SAFE file
        access_token (any, Optional): Initial access token [Default: `None`] 
        session (any, Optional): Initial session [Default: `None`] 
        headers (any, Optional): Initial headers [Default: `None`] 
        log (str): Log value [Default: `None`]
        verbose (bool): verbose [Default: `True`]
        verboseprogress (bool): verbose of the progress bar [Default: `True`]
        sizecheck (float): Size check
        
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

    usermessage.openingmsg(__name__,download.__name__,__file__,__copyright__,'Download a single file from the Copernicus server',log,verbose)

    if access_token == None:
        access_token = get_access_token(username, password)
        headers = {"Authorization": f"Bearer {access_token}"}
        session = requests.Session()
        session.headers.update(headers)

    if partialdownloading == None: 
        if constants.__SLCdownloader__ == 'python': 
            url = f"https://zipper.dataspace.copernicus.eu/odata/v1/Products(%s)/$value" % (image['Url'].split('/')[-1])
            success = False

            while success == False: 
                response = session.get(url, headers=headers, stream=True)
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

                    if os.path.getsize(directory+os.sep+image['Name']+'.tmp') > sizecheck: 
                        success = True
                    else: 
                        success = False
                        os.remove(directory+os.sep+image['Name']+'.tmp')
                        access_token = get_access_token(username, password)
                        headers = {"Authorization": f"Bearer {access_token}"}
                        session = requests.Session()
                        session.headers.update(headers)
                
            os.rename(directory+os.sep+image['Name']+'.tmp',directory+os.sep+image['Name'])

        elif constants.__SLCdownloader__ == 'wget': 
            if platform.system() == 'Windows':
                raise ValueError(usermessage.errormsg(__name__,download.__name__,__file__,constants.__copyright__,'The wget mode is not available with Windows. Please modify the __SLCdownloader__ option to python.',log))
            
            if os.path.isdir(directory+os.sep+'tmp'):
                shutil.rmtree(directory+os.sep+'tmp')
            os.mkdir(directory+os.sep+'tmp')

            success = False
            while success == False:  
                if constants.__wgetlimit__ == 'auto': 
                    if (datetime.today().hour > 22) and (datetime.today().hour < 5): 
                        wgetlimit = constants.__wgetlimitmax__
                    else:
                        wgetlimit = constants.__wgetlimitmin__
                else:
                        wgetlimit = constants.__wgetlimit__


                cmdi = "wget --limit-rate %s --header 'Authorization: Bearer %s' '%s' -O %s" % (wgetlimit,access_token,image['Url'],directory+os.sep+'tmp'+os.sep+image['Name'])
                os.system(cmdi)

                if os.path.getsize(directory+os.sep+'tmp'+os.sep+image['Name']) > sizecheck: 
                    success = True
                else: 
                    success = False
                    os.remove(directory+os.sep+'tmp'+os.sep+image['Name'])
                    access_token = get_access_token(username, password)

            os.rename(directory+os.sep+'tmp'+os.sep+image['Name'],
                directory+os.sep+image['Name'])
            shutil.rmtree(directory+os.sep+'tmp')

    else: 
        copernicuspartialdownloading(username,
            password,
            image,
            partialdownloading,
            directory,
            access_token, 
            session, 
            headers, 
            verbose,
            log, 
            mode = modepartial,
            zipping = zipping)

################################################################################
## Partial donwloading for Copernicus Data Space 
################################################################################
def copernicuspartialdownloading(username,
    password,
    image,
    listvar,
    output_dir,
    access_token, 
    session,
    headers,
    verbose,
    log,
    mode='include',
    zipping=True):
    """Download the selected data from Copernicus server. 

    The function downloads a set of selected files from the Copernicus server. 

    Note: 
        Two modes are available: include or exclude. See example: 
        * to download only VV data: exclude -vv-
        * to not download .tiff file: exclude measurements
        * to download only the annotation files: include annotation
        * etc.  

    Args:
        username (str): Username of the Copernicus server. 
        password (str): password of the Copernicus server.
        image (dict): Image dictionary
        output_dir (str): Output directory
        access_token (str): Copernicus User token
        session (any): initial session of the request
        headers (any): initial header of the request
        verbose (bool): verbose
        log (bool): log
        mode (str, Optional): can be include or exclude
        zipping (bool): Zip the dataset 

    """
        
    if not isinstance(verbose,bool):
        raise TypeError(usermessage.typeerrormsg(
            __name__,copernicuspartialdownloading.__name__,__file__,__copyright__,
            'verbose','True or False',log))
    
    if not isinstance(username,str):
        raise TypeError(usermessage.typeerrormsg(
                __name__,copernicuspartialdownloading.__name__,__file__,__copyright__,
                'username','str',log))
    
    if not isinstance(password,str):
        raise TypeError(usermessage.typeerrormsg(
                __name__,copernicuspartialdownloading.__name__,__file__,__copyright__,
                'password','str',log))
    
    if not isinstance(listvar,list):
        raise TypeError(usermessage.typeerrormsg(
                __name__,copernicuspartialdownloading.__name__,__file__,__copyright__,
                'listvar','list',log))

    if not isinstance(zipping,bool):
        raise TypeError(usermessage.typeerrormsg(
                __name__,copernicuspartialdownloading.__name__,__file__,__copyright__,
                'zipping','True or False',log))

    if not mode in ['include','exclude']:
        raise TypeError(usermessage.typeerrormsg(
                __name__,copernicuspartialdownloading.__name__,__file__,__copyright__,
                'mode','include or exclude',log))

    usermessage.openingmsg(__name__,copernicuspartialdownloading.__name__,__file__,__copyright__,'Partial downloading from the Copernicus server',log,verbose)

    # Print some inputs 
    usermessage.ezprint('File: %s' % (image['Name']),log,verbose)
    usermessage.ezprint('Url: %s' % (image['Url']),log,verbose)
    usermessage.ezprint('Mode: %s' % (mode),log,verbose)
    usermessage.ezprint('Variable: %s' % (listvar),log,verbose)
    usermessage.ezprint('Output directory: %s' % (output_dir),log,verbose)

    ## Explore the dataset
    usermessage.ezprint('Exploration of the dataset...',log,verbose)
    id = image['Url'].split('/')[-1]

    url_tmp = "https://download.dataspace.copernicus.eu/odata/v1/Products(%s)/Nodes(%s)/Nodes" % (id,image['Name'].replace('.zip','.SAFE'))

    results = {'namefile': [],
        'parentdir': [],
        'url': [],
        'urlzipper': [],
        'contentlength': [],
        'required': []}

    def urlasking(results,url,parent_dir): 
        reponse = requests.get(url).json()['result']

        for ri in reponse: 
            if not ri['ContentLength'] == 0:
                results['namefile'].append(ri['Id'])
                results['parentdir'].append(parent_dir)
                results['url'].append(ri['Nodes']['uri'])
                results['contentlength'].append(ri['ContentLength'])
            else: 
                urlasking(results,ri['Nodes']['uri'],parent_dir+os.sep+ri['Id'])
        return results
    
    urlasking(results,url_tmp,'')
    usermessage.ezprint('\tdone',log,verbose)

    ## Create the downloading link
    usermessage.ezprint('Create the link for the zipper...',log,verbose)
    for idx, urli in enumerate(results['url']):
        results['urlzipper'].append(urli.replace('https://download.dataspace.copernicus.eu/odata/v1/Products','https://zipper.dataspace.copernicus.eu/odata/v1/Products')[0:-5]+'$value') 
    usermessage.ezprint('\tdone',log,verbose)

    ## Check if required
    usermessage.ezprint('Check if the file is required...',log,verbose)
    for idx, file in enumerate(results['namefile']):
        pathfull = results['parentdir'][idx]+os.sep+file
            
        if mode == 'include': 
                check = False
        else:
                check = True

        for vari in listvar: 
            if vari in pathfull:
                print 
                check = not check
            
        results['required'].append(check)

    for idx, file in enumerate(results['namefile']): 
        usermessage.ezprint('\t%s: %s' % (results['parentdir'][idx]+os.sep+file,results['required'][idx]) ,log,verbose)        

    ## Downloading 
    usermessage.ezprint('Downloading...',log,verbose)
    
    if os.path.isdir(output_dir+os.sep+'tmp'): 
        shutil.rmtree(output_dir+os.sep+'tmp')
    os.mkdir(output_dir+os.sep+'tmp')

    for idx, file in enumerate(results['namefile']): 
        if results['required'][idx] == True: 
            usermessage.ezprint('Download the file: %s...' % (file),log,verbose)    
            pathdir = output_dir+os.sep+'tmp'+os.sep+results['parentdir'][idx]
            if os.sep == "/": 
                pathdir = pathdir.replace('/',os.sep)
            if not os.path.isdir(pathdir):
                os.makedirs(pathdir)

            success = False

            while success == False: 
                            
                if constants.__SLCdownloader__ == 'wget':
                    if not platform.system() == 'Windows':
                        cmdi = "wget --limit-rate %s --header 'Authorization: Bearer %s' '%s' -O %s" % (constants.__wgetlimit__,access_token,results['urlzipper'][idx],pathdir+os.sep+file)
                        os.system(cmdi)
                    else:
                        raise ValueError(usermessage.errormsg(__name__,download.__name__,__file__,constants.__copyright__,'The wget mode is not available with Windows. Please modify the __SLCdownloader__ option to python.',log))

                else:
                    response = session.get(results['urlzipper'][idx], headers=headers, stream=True)
                    total_length = int(response.headers.get('content-length'))
                    with open(pathdir+os.sep+file, "wb") as fout:
                        if verbose: 
                            for chunk in progress.bar(response.iter_content(chunk_size=constants.__chunksize__), expected_size=(total_length/constants.__chunksize__) + 1): 
                                if chunk:
                                    fout.write(chunk)
                        else: 
                            for chunk in response.iter_content(chunk_size=constants.__chunksize__):
                                if chunk:
                                    fout.write(chunk)

                if os.path.getsize(pathdir+os.sep+file) == results['contentlength'][idx]: 
                    success = True
                else: 
                    os.remove(pathdir+os.sep+file)
                    access_token = get_access_token(username, password)
                    headers = {"Authorization": f"Bearer {access_token}"}
                    session = requests.Session()
                    session.headers.update(headers)
                    
                time.sleep(0.001)        

    usermessage.ezprint('\tdone',log,verbose)

    ## Creation of the final file
    os.rename(output_dir+os.sep+'tmp', output_dir+os.sep+image['Name'].replace('.zip','.SAFE'))

    if zipping == True: 
        usermessage.ezprint('Creation of the .zip file: %s' % (image['Name']) ,log,verbose)

        shutil.make_archive(output_dir+os.sep+image['Name'].replace('.zip','.SAFE'),
            'zip',
            output_dir+os.sep,
            image['Name'].replace('.zip','.SAFE'))

        if os.path.isdir(output_dir+os.sep+image['Name'].replace('.zip','.SAFE')):
            shutil.rmtree(output_dir+os.sep+image['Name'].replace('.zip','.SAFE'))
            
        os.rename(output_dir+os.sep+image['Name'].replace('.zip','.SAFE')+'.zip',
            output_dir+os.sep+image['Name'])

        usermessage.ezprint('\tdone',log,verbose)

################################################################################
## get_access_token function 
################################################################################               
def get_access_token(username: str, password: str) -> str:
    """Function to generate the token for the Copernicus server 

    The function will generate a token regarding the Copernicus server access.  

    Note: 
            See https://documentation.dataspace.copernicus.eu/APIs.html

    Args:
            username (str, Optional): Username of the server [Default: `constants.__username__`]. 
            password (str, Optional): password of the server [Default: `constants.__password__`].

    Returns:
            str: Token

    """
    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
        }
    try:
        r = requests.post("https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
        data=data,
        )
        r.raise_for_status()
    except Exception as e:
        raise Exception(
        f"Access token creation failed. Reponse from the server was: {r.json()}"
        )
    return r.json()["access_token"]

################################################################################
## retrieveorbit FUNCTION
################################################################################
def retrieveorbit(s1orbitclass,  
        log = None, 
        verbose = True,
    ):
    """Retrieve the Sentinel-1 orbit files based on the S1 orbit class

    The function will retrieve the Sentinel-1 orbit files based on the S1 orbit class.

    Args:
        s1orbitclass (any): S1 orbit class
        log (str): Log value
        verbose (bool): verbose [Default: `None`]

    Returns:
        s1orbitclass
    
    """ 

    if verbose == None:
            verbose = True
    if not isinstance(verbose,bool):
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieveorbit.__name__,__file__,__copyright__,
            'verbose','True or False',log))
    
    usermessage.openingmsg(__name__,retrieveorbit.__name__,__file__,__copyright__,'Retrieve the %s orbit files from the Copernicus server' % (s1orbitclass.satellite),log,verbose)

    ######################################
    ## For Sentinel-1
    if s1orbitclass.satellite == 'S1': 
        QUERY_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
        DOWNLOAD_URL = "https://zipper.dataspace.copernicus.eu/odata/v1/Products"
        T0 = timedelta(seconds=(12 * 86400.0) / 175.0 + 60)
        T1 = timedelta(seconds=60)

        name_orbit = [] 
        download_url = []

        error_felching = False

        usermessage.ezprint('Check the available orbit files:',log,verbose) 
        for dslc, sati, namei, checkstored in zip(s1orbitclass.SLClist['Date1'], s1orbitclass.SLClist['Platform'], s1orbitclass.SLClist['Name'], s1orbitclass.SLClist['Stored']):

            if s1orbitclass.filebased == False or (s1orbitclass.filebased == True and checkstored == True): 

                D1 = datetime.strptime(dslc,'%Y-%m-%dT%H:%M:%S.%fZ') - T0
                D2 = datetime.strptime(dslc,'%Y-%m-%dT%H:%M:%S.%fZ') + T1

                # Detection of stored orbit files
                orbitlist=glob.glob(s1orbitclass.pathorbit+os.sep+'*.EOF')

                check_file_precise = False
                for pi in orbitlist:
                    if sati in pi: 
                        orb_test = os.path.abspath(pi).split(os.sep)[-1].split('V')[1].split('.')[0]
                        d1 = datetime.strptime(orb_test.split('_')[0], "%Y%m%dT%H%M%S")
                        d2 = datetime.strptime(orb_test.split('_')[1], "%Y%m%dT%H%M%S")
                        if d1 <= D1 <= d2 and d1 <= D2 <= d2:
                            if (not 'RESORB' in pi) or (not 'MOEORB' in pi):
                                check_file_precise = True

                if check_file_precise == True: 
                    usermessage.ezprint('\tOrbit file: found for %s' % (namei),log,verbose)  
                else: 
                    usermessage.ezprint('\tOrbit file: not found for %s\n\t\tRetrieval...' % (namei),log,verbose)

                usermessage.ezprint('\t\t\tCheck the available orbit files:',log,verbose)
                date1_research_str = D1.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                date2_research_str = D2.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

                # Check if the precise files are available
                tmp = ("startswith(Name,'%s') and contains(Name,'%s') and ContentDate/Start lt '%s' and ContentDate/End gt '%s'"% (sati,'AUX_POEORB',date1_research_str,date2_research_str))
                para_filter = {"$filter": tmp, "$orderby": "ContentDate/Start asc", "$top": 1}
                responsetmp = requests.get(QUERY_URL, params=para_filter).json()

                try: 
                    response = responsetmp["value"]
                    s1orbitclass.error_felching.append(False) 
                except: 
                    s1orbitclass.error_felching.append(True)  
                    response = []
                    usermessage.warningmsg(__name__,retrieveorbit.__name__,__file__,'Error during the PEORB file felching for %s: EZ-InSAR will try it later' % (namei),log,verbose)                                            

                if not len(response) == 0:
                    response = response[0] 
                    usermessage.ezprint('\t\t\t\tPrecise orbit file available for %s' % (namei),log,verbose)                         
                    download_url.append(f"{DOWNLOAD_URL}({response['Id']})/$value")
                    name_orbit.append(response['Name'])

                else: 
                    tmp = ("startswith(Name,'%s') and contains(Name,'%s') and ContentDate/Start lt '%s' and ContentDate/End gt '%s'"% (sati,'AUX_MOEORB',date1_research_str,date2_research_str))
                    para_filter = {"$filter": tmp, "$orderby": "ContentDate/Start asc", "$top": 1}
                    responsetmp = requests.get(QUERY_URL, params=para_filter).json()
                    try: 
                        response = responsetmp["value"]
                        s1orbitclass.error_felching.append(False) 
                    except: 
                        s1orbitclass.error_felching.append(True) 
                        response = []
                        usermessage.warningmsg(__name__,retrieveorbit.__name__,__file__,'Error during the MOEORB file felching for %s: EZ-InSAR will try it later' % (namei),log,verbose) 
                    
                    if not len(response) == 0:
                        response = response[0] 
                        usermessage.ezprint('\t\t\t\tMOEORB orbit file available for %s' % (namei),log,verbose)                         
                        download_url.append(f"{DOWNLOAD_URL}({response['Id']})/$value")
                        name_orbit.append(response['Name'])
                    
                    else: 
                        tmp = ("startswith(Name,'%s') and contains(Name,'%s') and ContentDate/Start lt '%s' and ContentDate/End gt '%s'"% (sati,'AUX_RESORB',date1_research_str,date2_research_str))
                        para_filter = {"$filter": tmp, "$orderby": "ContentDate/Start asc", "$top": 1}
                        responsetmp = requests.get(QUERY_URL, params=para_filter).json()
                        try: 
                            response = responsetmp["value"]
                            s1orbitclass.error_felching.append(False)  
                        except: 
                            s1orbitclass.error_felching.append(True)  
                            response = []
                            usermessage.warningmsg(__name__,retrieveorbit.__name__,__file__,'Error during the RESORB file felching for %s: EZ-InSAR will try it later' % (namei),log,verbose) 
                        
                        if not len(response) == 0:
                            response = response[0] 
                            usermessage.ezprint('\tRestitued orbit file available for %s' % (namei),log,verbose)                         
                            download_url.append(f"{DOWNLOAD_URL}({response['Id']})/$value")
                            name_orbit.append(response['Name'])
                        
                        else: 
                            usermessage.warningmsg(__name__,retrieveorbit.__name__,__file__,'No orbit file for the SLC %s.' % (namei),log,verbose)

        s1orbitclass.listfile = download_url
        s1orbitclass.listfilename = name_orbit

    else: 
        raise ValueError(usermessage.errormsg(__name__,retrieveorbit.__name__,__file__,__copyright__,
                'The selected satellite is not available.',log,verbose))
    
    return s1orbitclass

################################################################################
## downloadorbit FUNCTION
################################################################################
def downloadorbit(s1orbitclass,username,password,
        log = None, 
        verbose = True,
    ):
    """Download the Sentinel-1 orbit files based on the S1 orbit class

    The function will download the Sentinel-1 orbit files based on the S1 orbit class.

    Args:
        s1orbitclass (any): S1 orbit class
        log (str): Log value
        verbose (bool): verbose [Default: `None`]

    Returns:
        s1orbitclass
    
    """ 
    if verbose == None:
            verbose = True
    if not isinstance(verbose,bool):
        raise TypeError(usermessage.typeerrormsg(
            __name__,downloadorbit.__name__,__file__,__copyright__,
            'verbose','True or False',log))
    
    usermessage.openingmsg(__name__,downloadorbit.__name__,__file__,__copyright__,'Download the orbit files from the Copernicus server',log,verbose)

    usermessage.ezprint('Download the orbit files:',log,verbose) 

    access_token = get_access_token(username, password)
    headers = {"Authorization": f"Bearer {access_token}"}

    # Download
    session = requests.Session()
    session.headers.update(headers)

    for urli, namei in zip(s1orbitclass.listfile, s1orbitclass.listfilename):
        usermessage.ezprint('\tFor the file %s' %(namei),log,verbose)

        if not os.path.isfile(s1orbitclass.pathorbit+os.sep+namei):
            usermessage.ezprint('\t\tDownloading...',log,verbose)

            success = False
            
            while success == False: 
                response = session.get(urli, headers=headers, stream=True)
                total_length = int(response.headers.get('content-length'))

                with open(s1orbitclass.pathorbit+os.sep+namei+'.tmp', "wb") as file:
                    if verbose: 
                        for chunk in progress.bar(response.iter_content(chunk_size=constants.__chunksize__), expected_size=(total_length/constants.__chunksize__) + 1): 
                            if chunk:
                                file.write(chunk)
                    else: 
                        for chunk in response.iter_content(chunk_size=constants.__chunksize__):
                            if chunk:
                                file.write(chunk)

                    if (os.path.getsize(s1orbitclass.pathorbit+os.sep+namei+'.tmp') > 1e6 and ('POEORB' in namei)) or (os.path.getsize(s1orbitclass.pathorbit+os.sep+namei+'.tmp') > 2e5 and ('MOEORB' in namei)) or (os.path.getsize(s1orbitclass.pathorbit+os.sep+namei+'.tmp') > 2e5 and ('RESORB' in namei)): 
                        success = True
                    else: 
                        success = False
                        os.remove(s1orbitclass.pathorbit+os.sep+namei+'.tmp')
                        access_token = get_access_token(username, password)
                        headers = {"Authorization": f"Bearer {access_token}"}
                        session = requests.Session()
                        session.headers.update(headers)

            os.rename(s1orbitclass.pathorbit+os.sep+namei+'.tmp',s1orbitclass.pathorbit+os.sep+namei)

        else: 
            usermessage.ezprint('\t\tKeeping because the file is already stored.',log,verbose)

    ## IF ERROR                                
    if True in s1orbitclass.error_felching: 
        usermessage.warningmsg(__name__,downloadorbit.__name__,__file__,'EZ-InSAR reruns the orbit downloading because of some errors with the Copernicus server (after 5 seconds)',log,verbose)
        time.sleep(5)
        s1orbitclass.retrieve().download(username,password)
    else: 
        usermessage.ezprint('End of the orbit downloading without errors.',log,verbose) 

    return s1orbitclass 

################################################################################
## simplydownload FUNCTION
################################################################################
def simplydownload(listimage, 
        directory,
        username: Optional[str] = constants.__username__,  
        password: Optional[str] = constants.__password__,
        log = None, 
        verbose = True,
        verboseprogress = True,
        sizecheck = 250e6,
    ):
    """Download multiple files from Copernicus server.

    The function will download multiple images from Copernicus server. 

    Args:
        image (any): Image row for EZ-InSAR data list
        directory (str): Directory for file storing
        username (str, Optional): Username of the server [Default: `constants.__username__`]. 
        password (str, Optional): password of the server [Default: `constants.__password__`].
        log (str): Log value [Default: `None`]
        verbose (bool): verbose [Default: `True`]
        verboseprogress (bool): verbose of the progress bar [Default: `True`]
        sizecheck (float): Size check
    """ 

    access_token = get_access_token(username, password)
    headers = {"Authorization": f"Bearer {access_token}"}
    session = requests.Session()
    session.headers.update(headers)
    
    for idxrow, row in listimage.iterrows():
        dwrequired = False
        if (not (row['Stored'] == True or row['Processed'] == True)) and row['Status'] == 'ONLINE': 
            dwrequired = True 

        # if os.path.isfile(directory+os.sep+row['Name']):
        #     dwrequired = False

        if dwrequired == True:
            usermessage.ezprint('The file %s is ongoing to be downloaded:...' % (row['Name']),log,verbose)
        else:
            usermessage.ezprint('The file %s will not be downloaded (can be already downloaded).' % (row['Name']),log,verbose)

        if dwrequired == True:                      
            download(row,
                    directory,
                    username = username, 
                    password = password,  
                    access_token = access_token, 
                    session = session, 
                    headers = headers, 
                    log = log, 
                    verbose = False, 
                    verboseprogress = verboseprogress,
                    sizecheck=sizecheck,
                    )