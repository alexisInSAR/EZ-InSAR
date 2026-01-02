#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module for the ASF server

The module allows to connect EZ-InSAR with the data stored by ASF
    
    (From `ezinsar` package)

Changelog:
    * 3.2.2: Delete the support of wget for Windows, Alexis Hrysiewicz, Sep. 2025
    * 3.2.1: Various changes, Alexis Hrysiewicz, Aug. 2025
        * Implementation of the orbit file for Sentinel-1
        * Add the checksum 
    * 3.2.0: Bug fix for the Sentinel-1 dates, Alexis Hrysiewcz, Jul. 2025
    * 3.1.0: Initial version, Feb. 2025

"""
################################################################################
## Python packages
################################################################################
from typing import Optional, Union
from datetime import datetime
import requests
import numpy as np
import os 
import glob
import pandas as pd 
import shutil
from clint.textui import progress
from burst2safe.burst2safe import burst2safe
from ezinsar.eicomponents.templatevar import listSLCempty
import copy 
import platform
import urllib
import re
from asf_search import ASFSession
from asf_search.download import download as asf_download

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

__timeout_ASF__ = 5000
"""int: Time out in seconds for feching orbit files from the ASF server
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
        relorbit = 0, 
        satpass = 'ASCENDING',
        beam = None,
        frame = None,
        log = None, 
        verbose = True,
    ):
    """Retrieve a list of images for ASF server.

    The function will retrieve a list of images for ASF server based on user inputs. 

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
    
    if not satellite in ['S1','RSAT','ALOS2','NISAR']:
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'satellite',"['S1','RSAT','ALOS2','NISAR']",log))

    if satellite == 'RSAT':
        if not beam in constants.__beamRSAT__:
            raise TypeError(usermessage.typeerrormsg(
                __name__,retrieve.__name__,__file__,__copyright__,
                'satellite',"%s" % (constants.__beamRSAT__),log))

    usermessage.openingmsg(__name__,retrieve.__name__,__file__,__copyright__,'Create the image list for EZ-InSAR for %s data from the ASF server' % (satellite),log,verbose)

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

    if (not level in ['SLC']):
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'level',"['SLC']",log))
    usermessage.ezprint('\tLevel: %s' % (level),log,verbose)

    if relorbit == None:
        relorbit = 0
    if (not isinstance(relorbit,int)):
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'relorbit','integer',log))
    usermessage.ezprint('\tRelative orbit: %s' % (relorbit),log,verbose)

    if not satmode in ['IW','SM','SS']+list(constants.__sensors__['RSAT'].keys()): 
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'satmode','IW or SM',log))
    usermessage.ezprint('\tMode of acquisition: %s' % (satmode),log,verbose)

    if not satpass in ['ASCENDING','DESCENDING'] and not satellite in ['RSAT','ALOS2']: 
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'satpass',"'ASCENDING','DESCENDING'",log))
    usermessage.ezprint('\tSatellite direction: %s' % (satpass),log,verbose)

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
    usermessage.ezprint('\tPolarisation: %s' % (polarisation),log,verbose)

    if satellite in ['RSAT']:
        if not beam in constants.__beamRSAT__: 
            raise TypeError(usermessage.typeerrormsg(
                __name__,retrieve.__name__,__file__,__copyright__,
                'beam',"%s" % (constants.__beamRSAT__),log))
        usermessage.ezprint('\tBeam: %s' % (beam),log,verbose)

    ## Create the query 
    lon,lat = roi.exterior.xy

    if not len(polarisation) == 1:
        if 'VV' in polarisation and 'VH' in polarisation:
            pol = 'VV+VH'
        elif 'HH' in polarisation and 'HV' in polarisation:
            pol = 'HH+HV'
        else:
            raise ValueError(usermessage.errormsg(__name__,retrieve.__name__,__file__,__copyright__,'No correct polarisation.',log))
    elif len(polarisation) == 1:
            pol = polarisation[0]
    else: 
        raise ValueError(usermessage.errormsg(__name__,retrieve.__name__,__file__,__copyright__,'No correct polarisation.',log))

    usermessage.ezprint('Send the request:',log,verbose)
    if satmode == 'IW' and (satellite == 'S1' or 'Sentinel' in satellite): 
        if not relorbit == 0: 
            
            url = 'https://api.daac.asf.alaska.edu/services/search/param?platform=%s&beamMode=%s&bbox=%s&start=%s&end=%s&relativeOrbit=%d&flightDirection=%s&processingLevel=SLC&maxResults=10000&output=json' % (satellite,
                satmode,
                '%s,%s,%s,%s' % (np.min(lon),np.min(lat),np.max(lon),np.max(lat)),
                date1.strftime("%Y-%m-%dT%H:%M:%SUTC"),
                date2.strftime("%Y-%m-%dT%H:%M:%SUTC"),
                relorbit,
                satpass[0])
        else:
            url = 'https://api.daac.asf.alaska.edu/services/search/param?platform=%s&beamMode=%s&bbox=%s&start=%s&end=%s&flightDirection=%s&processingLevel=SLC&maxResults=10000&output=json' % (satellite,
                satmode,
                '%s,%s,%s,%s' % (np.min(lon),np.min(lat),np.max(lon),np.max(lat)),
                date1.strftime("%Y-%m-%dT%H:%M:%SUTC"),
                date2.strftime("%Y-%m-%dT%H:%M:%SUTC"),
                satpass[0])
        
        ## Send the request
        response = requests.get(url).json()
    
    elif satmode == 'SM' and (satellite == 'S1' or 'Sentinel' in satellite):
        listsm = ['S1','S2','S3','S4','S5','S6']
                        
        check_json = False
        h = 0 
        while check_json == False:
            
            url = 'https://api.daac.asf.alaska.edu/services/search/param?platform=%s&beamMode=%s&bbox=%s&start=%s&end=%s&relativeOrbit=%d&flightDirection=%s&processingLevel=SLC&maxResults=10000&output=json' % (satellite,
                listsm[h],
                '%s,%s,%s,%s' % (np.min(lon),np.min(lat),np.max(lon),np.max(lat)),
                date1.strftime("%Y-%m-%dT%H:%M:%SUTC"),
                date2.strftime("%Y-%m-%dT%H:%M:%SUTC"),
                relorbit,
                satpass[0])
            
            response = requests.get(url).json()

            if response[0]:
                check_json = True
                usermessage.ezprint('\tData for the %s mode, EZ-InSAR will stop here.' % (listsm[h]),log,verbose)
            else: 
                usermessage.ezprint('\tNo data for the %s mode, EZ-InSAR will try the next one.' % (listsm[h]),log,verbose)

            h = h + 1
    
    # For default search
    else:
        if satellite == 'RSAT':
            satellite = 'RADARSAT-1'
            if level == 'SLC':
                level = 'L1'
        elif satellite == 'ALOS2':
            satellite = 'ALOS-2'
            if level == 'SLC':
                level = 'L1.1' 
            
        if satellite == 'RSAT':
            url = 'https://api.daac.asf.alaska.edu/services/search/param?platform=%s&beamMode=%s&bbox=%s&start=%s&end=%s&flightDirection=%s&processingLevel=%s' % (satellite,
                    satmode,
                    '%s,%s,%s,%s' % (np.min(lon),np.min(lat),np.max(lon),np.max(lat)),
                    date1.strftime("%Y-%m-%dT%H:%M:%SUTC"),
                    date2.strftime("%Y-%m-%dT%H:%M:%SUTC"),
                    satpass[0],
                    level)
            
            if not beam == None:
                url = url+'&beamSwath=%s' % (beam)

            
        else: 
            # url = 'https://api.daac.asf.alaska.edu/services/search/param?platform=%s&beamMode=%s&bbox=%s&start=%s&end=%s&processingLevel=%s' % (satellite,
            #         beam,
            #         '%s,%s,%s,%s' % (np.min(lon),np.min(lat),np.max(lon),np.max(lat)),
            #         date1.strftime("%Y-%m-%dT%H:%M:%SUTC"),
            #         date2.strftime("%Y-%m-%dT%H:%M:%SUTC"),
            #         level)
            
            url = 'https://api.daac.asf.alaska.edu/services/search/param?platform=%s&bbox=%s&start=%s&end=%s&processingLevel=%s' % (satellite,
                    '%s,%s,%s,%s' % (np.min(lon),np.min(lat),np.max(lon),np.max(lat)),
                    date1.strftime("%Y-%m-%dT%H:%M:%SUTC"),
                    date2.strftime("%Y-%m-%dT%H:%M:%SUTC"),
                    level)

        # if not relorbit == 0:
        #     url = url+'&relativeOrbit=%d' % (relorbit)

        # if not frame == None:
        #     url = url+'&asfframe=%s' % (frame)
            
        url = url+'&maxResults=10000&output=json'

        ## Send the request
        response = requests.get(url).json()

    usermessage.ezprint('\tdone',log,verbose)

    ## Create the list
    usermessage.ezprint('Create the data list:',log,verbose)
    listSLC = copy.deepcopy(listSLCempty)

    for idx in range(len(response[0])):
        imgi = response[0][idx]
        if '+' in imgi['polarization']: 
            polrequest = imgi['polarization'].split('+')
        else:
            polrequest = imgi['polarization']

        test_pol = False
        for poli in polarisation:    
            if poli in polrequest:
                    test_pol = True
            else:
                    test_pol = False

        if (relorbit == int(imgi['relativeOrbit']) or relorbit == 0) and (test_pol == True):
            
            listSLC['Name'].append(imgi['fileName'])

            print(imgi)

            if not 'Z' in imgi['startTime']:
                imgi['startTime'] = imgi['startTime']+'Z'
            if len(imgi['startTime']) == 20: 
                imgi['startTime'] = imgi['startTime'].replace('Z','.000000Z')
                usermessage.warningmsg(__name__,retrieve.__name__,__file__,'Issue wiht the date format: The decimal second will be added.',log,verbose)
            listSLC['Date1'].append(imgi['startTime'])

            if not 'Z' in imgi['stopTime']:
                imgi['stopTime'] = imgi['stopTime']+'Z'
            if len(imgi['stopTime']) == 20: 
                imgi['stopTime'] = imgi['stopTime'].replace('Z','.000000Z')
                usermessage.warningmsg(__name__,retrieve.__name__,__file__,'Issue wiht the date format: The decimal second will be added.',log,verbose)
            listSLC['Date2'].append(imgi['stopTime'])         

            if imgi['platform'] == 'Sentinel-1A':
                listSLC['Platform'].append('S1A')
            elif imgi['platform'] == 'Sentinel-1B':
                listSLC['Platform'].append('S1B')
            elif imgi['platform'] == 'Sentinel-1C':
                listSLC['Platform'].append('S1C')
            elif imgi['platform'] == 'RADARSAT-1':
                listSLC['Platform'].append('RSAT')
            elif imgi['platform'] == 'ALOS-2':
                 listSLC['Platform'].append('ALOS2')

            listSLC['Mode'].append(satmode)
            listSLC['Beam'].append(beam)
            listSLC['Frame'].append(int(imgi['frameNumber']))
            
            listSLC['Orbit'].append(int(imgi['absoluteOrbit']))

            listSLC['RelativeOrbit'].append(int(imgi['relativeOrbit']))

            listSLC['PolyFrame'].append(imgi['stringFootprint'])

            listSLC['OrbitDirection'].append(imgi['flightDirection'])

            listSLC['Looking'].append('Right')

            listSLC['Wavelength'].append(['C'])

            listSLC['Frequency'].append([0])

            listSLC['ProcessingLevel'].append(level)

            listSLC['Polarisation1'].append(polrequest[0])

            try: 
                listSLC['Polarisation2'].append(polrequest[1])
            except:
                listSLC['Polarisation2'].append(None) 

            listSLC['Polarisation3'].append(None) 
            listSLC['Polarisation4'].append(None) 

            listSLC['Server'].append('ASF') 

            listSLC['Url'].append(imgi['downloadUrl']) 

            listSLC['Status'].append('ONLINE') 

            if not imgi['sizeMB'] in [None,'None']: 
                listSLC['SizeMB'].append(float(imgi['sizeMB']))
            
            listSLC['MD5CheckSum'].append(imgi['md5sum'])

            listSLC['Stored'].append(False) 

            listSLC['Processed'].append(False) 
            
    listSLC = slctools.checklistconsistency(listSLC,log=log,verbose=verbose)
    listdata = pd.DataFrame.from_dict(listSLC)
    print(listdata)

    usermessage.ezprint('\tdone',log,verbose)

    return listdata

################################################################################
## download FUNCTION
################################################################################
def download(image, 
        directory,
        username: Optional[str] = constants.__username__,  
        password: Optional[str] = constants.__password__, 
        burstonly: Optional[bool] = False,
        roi = None, 
        polarisation = None, 
        log = None, 
        verbose = True,
        verboseprogress = True,
    ):
    """Download a single file from ASF server.

    The function will download a single image from ASF server. 

    Args:
        image (any): Image row for EZ-InSAR data list
        directory (str): Directory for file storing
        username (str, Optional): Username of the server [Default: `constants.__username__`]. 
        password (str, Optional): password of the server [Default: `constants.__password__`].
        burstonly (bool, Optional): Download only the required bursts (only compatible with ASF server). [Default: `False`]
        roi (any, Option): Region of Interest. Required for the burstonly mode. [Default: `None`]
        polarisation (list, Option): List of polarisation. Required for the burstonly mode. [Default: `None`]
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

    usermessage.openingmsg(__name__,download.__name__,__file__,__copyright__,'Download a single file from the ASF server',log,verbose)

    ## Download the file 
    if burstonly == False: 

        success = False
        usermessage.ezprint('Download the file: %s' % (image['Name']),log,verbose)

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

        while success == False:

            if constants.__SLCdownloader__ == 'python':

                miscellaneous.download_file(image['Url'], 
                    username = username,
                    password = password,
                    output_file=directory+os.sep+'tmp'+os.sep+image['Name'],
                    verbose=verboseprogress,
                    log=log)

            else:
                if not platform.system() == 'Windows':
                    cmdi = 'wget --limit-rate %s -c --http-user="%s" --http-password="%s" "%s" -P %s' % (wgetlimit,username,password,image['Url'],directory+os.sep+'tmp')
                    os.system(cmdi)
                else:
                    raise ValueError(usermessage.errormsg(__name__,download.__name__,__file__,constants.__copyright__,'The wget mode is not available with Windows. Please modify the __SLCdownloader__ option to python.',log)) 
            
            success = miscellaneous.checksum(directory+os.sep+'tmp'+os.sep+image['Url'].split('/')[-1],
                        image['MD5CheckSum'],
                        verbose=False,
                        log=log)
            
            if success == False:
                os.remove(directory+os.sep+'tmp'+os.sep+image['Url'].split('/')[-1])

        os.rename(directory+os.sep+'tmp'+os.sep+image['Url'].split('/')[-1],
            directory+os.sep+image['Url'].split('/')[-1])
        shutil.rmtree(directory+os.sep+'tmp')

        #########################################################################################
        # # ERROR (after several hours) with this method to methods of downloading  
        #########################################################################################
        # elif constants.__SLCdownloader__ == 'python':

        #     success = False
        #     while success == False: 

        #         session = asf_search.ASFSession()
        #         session = asf_search.ASFSession.auth_with_creds(session, username=username,password=password)
        #         response = response = session.get(image['Url'], stream=True, hooks={'response': asf_search.download.strip_auth_if_aws}) 
        #         total_length = int(response.headers.get('content-length'))

        #         with open(directory+os.sep+image['Name']+'.tmp', "wb") as file:
        #             if verboseprogress: 
        #                 for chunk in progress.bar(response.iter_content(chunk_size=constants.__chunksize__), expected_size=(total_length/constants.__chunksize__) + 1): 
        #                     if chunk:
        #                         file.write(chunk)
        #             else: 
        #                 for chunk in response.iter_content(chunk_size=constants.__chunksize__):
        #                     if chunk:
        #                         file.write(chunk)

        #         if os.path.getsize(directory+os.sep+image['Name']+'.tmp') == total_length: 
        #             success = True
        #             os.rename(directory+os.sep+image['Name']+'.tmp',directory+os.sep+image['Name'])
        #         else: 
        #             success = False

        #     session.close()

        usermessage.ezprint('\tdone',log,verbose)

    elif burstonly == True and image['Mode'] == 'IW':

        if roi == None: 
            raise TypeError(usermessage.typeerrormsg(
                __name__,download.__name__,__file__,__copyright__,
                'roi','Region of Interest in Polygon',log))

        if polarisation == None: 
            raise TypeError(usermessage.typeerrormsg(
                __name__,download.__name__,__file__,__copyright__,
                'polarisation','list',log))

        usermessage.ezprint('Download the file: %s with the burst-only mode activated' % (image['Name']),log,verbose)

        if not glob.glob(directory+os.sep+'*'+image['Date1'].split('T')[0].replace('-','')+'*.zip'):
            os.environ['EARTHDATA_USERNAME'] = username
            os.environ['EARTHDATA_PASSWORD'] = password

            if os.path.isdir(directory+os.sep+'tmp'):
                    shutil.rmtree(directory+os.sep+'tmp')
            os.mkdir(directory+os.sep+'tmp')

            burst2safe(orbit=image['Orbit'],
                    extent = roi,                                        
                    polarizations = polarisation,
                    mode = 'IW',
                    all_anns=True, 
                    work_dir = directory+os.sep+'tmp',
            )

            # Renaming
            fi = glob.glob(directory+os.sep+'tmp'+os.sep+'*.SAFE')[0]

            # Zipping 
            shutil.make_archive(fi,
                    'zip',
                    directory+os.sep+'tmp',
                    fi.split(os.sep)[-1])

            os.rename(fi+'.zip',directory+os.sep+fi.replace('.SAFE','.zip').split(os.sep)[-1])
            shutil.rmtree(directory+os.sep+'tmp')

            usermessage.ezprint('\tdone',log,verbose)

    else: 
        usermessage.ezprint('\tAlready downloaded regarding the only burst mode).',log,verbose) 

################################################################################
## baseline FUNCTION
################################################################################
def baseline(framename, 
        level = 'SLC',
        log = None, 
        verbose = True,
    ):
    """Retrieve the baseline information from the ASF server.

    The function will retrieve the baseline information from the ASF server based on user inputs. 

    Args:
        framename (str): Name of the Frame
        level (str): Processing level regarding the satellite [Default: ``SLC``]
        log (str): Log value
        verbose (bool): verbose [Default: `None`]

    Returns:
        list:
    
    """ 

    if verbose == None:
            verbose = True
    if not isinstance(verbose,bool):
        raise TypeError(usermessage.typeerrormsg(
            __name__,baseline.__name__,__file__,__copyright__,
            'verbose','True or False',log))
    
    usermessage.openingmsg(__name__,baseline.__name__,__file__,__copyright__,'Retrieve the baseline information from the ASF server',log,verbose)

    ## Check the user input 
    usermessage.ezprint('User parameters:',log,verbose)

    if (not isinstance(framename,str)):
        raise TypeError(usermessage.typeerrormsg(
            __name__,baseline.__name__,__file__,__copyright__,
            'framename','str',log))
    usermessage.ezprint('\tFrame name: %s' % (framename),log,verbose)

    if (not level in ['SLC']):
        raise TypeError(usermessage.typeerrormsg(
            __name__,baseline.__name__,__file__,__copyright__,
            'level',"['SLC']",log))
    usermessage.ezprint('\tLevel: %s' % (level),log,verbose)

    usermessage.ezprint('Send the request:',log,verbose)
    url = 'https://api.daac.asf.alaska.edu/services/search/baseline?reference=%s&processingLevel=%s&output=geojson' % (framename,
            level)
    
    ## Send the request
    response = requests.get(url).json()
    usermessage.ezprint('\tdone',log,verbose)
    
    ## Create the list
    usermessage.ezprint('Create the baseline list:',log,verbose)

    data = dict()
    data['Name'] = []
    data['Date1'] = []
    data['Date2'] = []
    data['perpendicularBaseline'] = []
    data['temporalBaseline'] = []
    data['PolyFrame'] = []

    for imgi in response['features']:
        data['Name'].append(imgi['properties']['fileName'])

        if not 'Z' in imgi['properties']['startTime']:
            imgi['properties']['startTime'] = imgi['properties']['startTime']+'Z'
        if len(imgi['properties']['startTime']) == 20: 
            imgi['properties']['startTime'] = imgi['properties']['startTime'].replace('Z','.000000Z')
            usermessage.warningmsg(__name__,retrieve.__name__,__file__,'Issue wiht the date format: The decimal second will be added.',log,verbose)
        data['Date1'].append(imgi['properties']['startTime']) 

        if not 'Z' in imgi['properties']['stopTime']:
            imgi['properties']['stopTime'] = imgi['properties']['stopTime']+'Z'
        if len(imgi['properties']['stopTime']) == 20: 
            imgi['properties']['stopTime'] = imgi['properties']['stopTime'].replace('Z','.000000Z')
            usermessage.warningmsg(__name__,retrieve.__name__,__file__,'Issue wiht the date format: The decimal second will be added.',log,verbose)
        data['Date2'].append(imgi['properties']['stopTime']) 

        data['perpendicularBaseline'].append(imgi['properties']['perpendicularBaseline'])
        data['temporalBaseline'].append(imgi['properties']['temporalBaseline'])
        data['PolyFrame'].append(imgi['geometry']['coordinates'])
   
    listdata = pd.DataFrame.from_dict(data)

    usermessage.ezprint('\tdone',log,verbose)

    return listdata

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
            __name__,baseline.__name__,__file__,__copyright__,
            'verbose','True or False',log))
    
    usermessage.openingmsg(__name__,baseline.__name__,__file__,__copyright__,'Retrieve the %s orbit files from the ASF server' % (s1orbitclass.satellite),log,verbose)

    ######################################
    ## For Sentinel-1

    if s1orbitclass.satellite == 'S1':
        # Check the precise files
        usermessage.ezprint('Load the list of precise-orbit files available... (can take several minutes)',log,verbose) 
                
        url_precise = "https://s1qc.asf.alaska.edu/aux_poeorb/"
        html = urllib.request.urlopen(url_precise, timeout = __timeout_ASF__)
        text = html.read()
        plaintext = text.decode('utf8')
        links = re.findall("href=[\"\'](.*?)[\"\']", plaintext)
        orbits_precise = []
        for li in links:
                if ".EOF" in li:
                        orbits_precise.append(li)
        usermessage.ezprint('\tDone',log,verbose) 

        # Check the restitued files (should work because of the RESORB files since 2024-01-01)
        usermessage.ezprint('Load the list of restitued-orbit files available... (can take several minutes)',log,verbose) 

        try: 
                url_restitued = "https://s1qc.asf.alaska.edu/aux_resorb/"
                html = urllib.request.urlopen(url_restitued, timeout = __timeout_ASF__)        
                text = html.read()
                plaintext = text.decode('utf8')
                links = re.findall("href=[\"\'](.*?)[\"\']", plaintext)
                orbits_restitued = []
                for li in links:
                        if ".EOF" in li:
                                orbits_restitued.append(li)
                usermessage.ezprint('\tDone',log,verbose)
        
        except:
                usermessage.warningmsg(__name__,retrieveorbit.__name__,__file__,'Impossible to felch the orbit file...\nProbabily to due a HTTP Error 504: Gateway Time-out error...\tThe next steps will bypass the restituded orbit files.',log,verbose)
                orbits_restitued = []

        dateSLC = []

        for idxrow, row in s1orbitclass.SLClist.iterrows():
            dateSLC.append(datetime.strptime(row['Date1'], '%Y-%m-%dT%H:%M:%S.%fZ'))

        # Check the required orbits
        orbitdownload = []
        for dslc, sati, namei, checkstored in zip(dateSLC, s1orbitclass.SLClist['Platform'], s1orbitclass.SLClist['Name'], s1orbitclass.SLClist['Stored']):
                            
            if s1orbitclass.filebased == False or (s1orbitclass.filebased == True and checkstored == True): 
                usermessage.ezprint('Check the orbit files for the SLC %s acquired by %s' % (namei,sati),log,verbose) 

                check_precise=False
                check_restitued=False
                name_orbit_precise = []
                name_orbit_restitued = []
                for pi in orbits_precise:
                    if sati in pi: 
                        orb_test = pi.split('V')[1].split('.')[0]
                        d1 = datetime.strptime(orb_test.split('_')[0], "%Y%m%dT%H%M%S" )
                        d2 = datetime.strptime(orb_test.split('_')[1], "%Y%m%dT%H%M%S" )
                        if d1 <= dslc <= d2:
                            check_precise=True
                            name_orbit_precise.append(pi)

                if check_precise:
                    for ni in name_orbit_precise:
                        usermessage.ezprint('\tThe precise orbit %s has been found.' % (ni),log,verbose) 
            
                    if len(name_orbit_precise) == 1: 
                        orbitdownload.append(url_precise+name_orbit_precise[0])
                    else: 
                        usermessage.warningmsg(__name__,retrieveorbit.__name__,__file__,'Several files detected: keep the latest.',log,verbose)
                        orbitdownload.append(url_precise+name_orbit_precise[-1])
                else:
                    usermessage.ezprint('\tNo precise orbit has been found, check the restitued orbits...',log,verbose) 
                    for pi in orbits_restitued:
                        if sati in pi: 
                            orb_test = pi.split('V')[1].split('.')[0]
                            d1 = datetime.strptime(orb_test.split('_')[0], "%Y%m%dT%H%M%S" )
                            d2 = datetime.strptime(orb_test.split('_')[1], "%Y%m%dT%H%M%S" )
                            if d1 <= dslc <= d2:
                                check_restitued=True
                                name_orbit_restitued.append(pi)
                    if check_restitued:
                        for ni in name_orbit_restitued:
                            usermessage.ezprint('\tThe restitued orbit %s has been found.' % (ni),log,verbose) 
                        if len(name_orbit_restitued) == 1: 
                            orbitdownload.append(url_restitued+name_orbit_restitued[0])
                        elif len(name_orbit_restitued) >= 1: 
                            usermessage.warningmsg(__name__,retrieveorbit.__name__,__file__,'Several files detected: keep the latest.',log,verbose)
                            orbitdownload.append(url_restitued+name_orbit_restitued[-1])
                        else: 
                            usermessage.warningmsg(__name__,retrieveorbit.__name__,__file__,'No orbit files have been found.',log,verbose)

        s1orbitclass.listfile = np.unique(orbitdownload)

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
    
    usermessage.openingmsg(__name__,downloadorbit.__name__,__file__,__copyright__,'Download the orbit files from the ASF server',log,verbose)

    session = None  
    if session == None: 
            session = ASFSession().auth_with_creds(username=username,password=password)
    
    # Loop for having a message
    for filei in s1orbitclass.listfile: 
        usermessage.ezprint('Download: %s...' % (filei),log,verbose) 
        asf_download.download_urls([filei], s1orbitclass.pathorbit, session, processes=1)
        usermessage.ezprint('\tDone',log,verbose) 

    return s1orbitclass 
