#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module for the THEIA server

The module allows to connect EZ-InSAR with the data stored by https://theia.cnes.fr/atdistrib/rocket/#/home.
    
    (From `ezinsar` package)

Changelog:
    * 3.1.0: Initial version, Feb. 2025

Note:

    This script is based on the scripts from Olivier Hagolle https://github.com/olivierhagolle/theia_download 

"""
################################################################################
## Python packages
################################################################################
from typing import Optional, Union
from datetime import date, datetime
import requests
import numpy as np
import os 
import sys 
import glob
import json
import time
from shapely.geometry import Polygon
import pandas as pd 

if sys.version_info[0] == 2:
    from urllib import urlencode
elif sys.version_info[0] > 2:
    from urllib.parse import urlencode

from ezinsar import constants
from ezinsar import usermessage

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
        level = 'LEVEL2A',
        relorbit = None, 
        cloudcover = 100,
        server = 'https://theia.cnes.fr/atdistrib',
        resto = 'resto2',
        log = None, 
        verbose = True,
    ):
    """Retrieve a list of images for THEIA server.

    The function will retrieve a list of images for THEIA server based on user inputs. 

    Args:
        satellite (str): Satellite name 
        roi (any): Region of Interest in POLYGON format (shapely)
        date1 (any): start date for the request in datetime [Default: ``datetime.strptime('2015-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')``
        date2 (any): end date for the request in datetime [Default: ``datetime.strptime('2030-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')``
        level (str): Processing level regarding the satellite [Default: ``LEVEL2A``] 
        relorbit (number): Relative orbit for radar data [Default: ``None``] 
        cloudcover (float or int): Max. value of the cloud coverage for multispectral data [Default: 100]
        server: Server of data [Default: https://theia.cnes.fr/atdistrib]
        resto: Resto for THEIA [Default: resto2]
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
    
    if not satellite in ['Landsat', 'Landsat57', 'SPOTWORLDHERITAGE', 'SWH1', 'LANDSAT', 'SENTINEL2', 'Snow','VENUS', 'VENUSVM05','LANDSAT5', 'LANDSAT7', 'LANDSAT8', 'SPOT1', 'SPOT2', 'SPOT3', 'SPOT4', 'SPOT5','S2','SENTINEL2A', 'SENTINEL2B', 'VENUS', 'VENUSVM05']:
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'satellite',"['Landsat', 'Landsat57', 'SPOTWORLDHERITAGE', 'SWH1', 'LANDSAT', 'SENTINEL2', 'Snow','VENUS', 'VENUSVM05','LANDSAT5', 'LANDSAT7', 'LANDSAT8', 'SPOT1', 'SPOT2', 'SPOT3', 'SPOT4', 'SPOT5','S2','SENTINEL2A', 'SENTINEL2B', 'VENUS', 'VENUSVM05']",log))

    usermessage.openingmsg(__name__,retrieve.__name__,__file__,__copyright__,'Create the image list for EZ-InSAR for %s data from the THEIA server' % (satellite),log,verbose)

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

    if (not level in ['LEVEL1C','LEVEL2A','LEVEL3A']):
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'level',"['LEVEL1C','LEVEL2A','LEVEL3A']",log))
    usermessage.ezprint('\tLevel: %s' % (level),log,verbose)

    if not relorbit == None: 
        if (not isinstance(relorbit,int)):
            raise TypeError(usermessage.typeerrormsg(
                __name__,retrieve.__name__,__file__,__copyright__,
                'relorbit','integer',log))
        usermessage.ezprint('\tRelative orbit: %s' % (relorbit),log,verbose)


    if (not isinstance(cloudcover,int)):
        raise TypeError(usermessage.typeerrormsg(
            __name__,retrieve.__name__,__file__,__copyright__,
            'cloudcover','int',log))
    usermessage.ezprint('\tCloud cover: %s' % (cloudcover),log,verbose)

    ## Create the query 
    usermessage.ezprint('Create the query:',log,verbose)

    xbbox, ybbox = roi.exterior.xy 

    query_geom = 'box={lonmin},{latmin},{lonmax},{latmax}'.format(
        latmin=np.min(ybbox), latmax=np.max(ybbox), lonmin=np.min(xbbox), lonmax=np.max(xbbox))
    dict_query = {'box': '{lonmin},{latmin},{lonmax},{latmax}'.format(
        latmin=np.min(ybbox), latmax=np.max(ybbox), lonmin=np.min(xbbox), lonmax=np.max(xbbox))}

    if satellite in ['Landsat', 'Landsat57', 'SPOTWORLDHERITAGE', 'SWH1', 'LANDSAT', 'SENTINEL2', 'Snow','VENUS', 'VENUSVM05']: 
        dict_query['collection'] = satellite
    
    elif satellite in ['LANDSAT5', 'LANDSAT7', 'LANDSAT8', 'SPOT1', 'SPOT2', 'SPOT3', 'SPOT4', 'SPOT5','S2','SENTINEL2A', 'SENTINEL2B', 'VENUS', 'VENUSVM05']:
        dict_query['platform'] = satellite

        if satellite in ['LANDSAT5', 'LANDSAT7']:
            dict_query['collection'] = 'Landsat57'
        elif satellite in ['LANDSAT5', 'LANDSAT7']:
            dict_query['collection'] = 'Landsat'
        elif satellite in ['SPOT1', 'SPOT2', 'SPOT3', 'SPOT4', 'SPOT5']:
            dict_query['collection'] = 'SPOTWORLDHERITAGE'
        elif satellite in ['S2','SENTINEL2A', 'SENTINEL2B']:
            dict_query['collection'] = 'SENTINEL2'
        elif satellite in ['VENUS']:
            dict_query['collection'] = 'VENUS'
        elif satellite in ['VENUSVM05']:
            dict_query['collection'] = 'VENUSVM05'

    dict_query['startDate'] = date1.strftime('%Y-%m-%d')
    dict_query['completionDate'] = date2.strftime('%Y-%m-%d')
    dict_query['maxRecords'] = 500

    if satellite in ["SENTINEL2","VENUS","VENUSVM05"]:
        dict_query['processingLevel'] = level

    if not relorbit == None:
        dict_query['relativeOrbitNumber'] = relorbit

    query = "%s/%s/api/collections/%s/search.json?" % (
        server, resto, dict_query['collection']) + urlencode(dict_query)
    
    usermessage.ezprint('\tdone',log,verbose)

    ## Send the request
    usermessage.ezprint('Send the request:',log,verbose)
    response = requests.get(query).json()

    ## Create the data list
    usermessage.ezprint('Create the list of images',log,verbose)

    try:
        # Dummy line to generate an error if empty
        dummy = response["features"][0]["properties"]
    except:
        raise ValueError(usermessage.errormsg(__name__,retrieve.__name__,__file__,__copyright__,'No product corresponds to selection criteria. In addition, there could be an error with the server connection. Please read the response for more information:\n\n\n%s' % (response),log))

    listdata = dict()
    listdata['Name'] = []
    listdata['ID'] = []
    listdata['Date1'] = []
    listdata['Date2'] = []
    listdata['Mode'] = []
    listdata['Orbit'] = []
    listdata['Platform'] = []
    listdata['PolyFrame'] = []
    listdata['Cloudcover'] = []
    listdata['ProcessingLevel'] = []
    listdata['Quicklook'] = []
    listdata['Server'] = []
    listdata['Url'] = []
    listdata['Status'] = []
    listdata['SizeMB'] = []
    
    if len(response["features"]) == 500: 
        usermessage.warningmsg(__name__,retrieve.__name__,__file__,'500 files have been detected and this value is a threshold. Please change the input parameters to avoid any missing images.',log,True)

    for imgi in range(len(response["features"])):
        listdata['Name'].append(response["features"][imgi]['properties']['title'])
        listdata['ID'].append(response["features"][imgi]["id"])
        listdata['Date1'].append(response["features"][imgi]['properties']['startDate'])
        listdata['Date2'].append(response["features"][imgi]['properties']['completionDate'])
        listdata['Platform'].append(response["features"][imgi]['properties']['platform'])
        listdata['Mode'].append(response["features"][imgi]['properties']['sensorMode'])
        listdata['Orbit'].append(response["features"][imgi]['properties']['orbitNumber'])
        try:
                listdata['PolyFrame'].append(str(Polygon(response["features"][imgi]['geometry']['coordinates'][0])))
        except:
                listdata['PolyFrame'].append(str(Polygon(response["features"][imgi]['geometry']['coordinates'][0][0])))
        cloudtemp = response["features"][imgi]["properties"]["cloudCover"]
        if cloudtemp is not None:
            listdata['Cloudcover'].append(int(cloudtemp))
        else:
            listdata['Cloudcover'].append(0)
        listdata['ProcessingLevel'].append(response["features"][imgi]['properties']['processingLevel'])
        listdata['Quicklook'].append(response["features"][imgi]['properties']['quicklook'])
        listdata['Server'].append('THEIA') 
        listdata['Url'].append(response["features"][imgi]['properties']['services']['download']['url']) 
        listdata['Status'].append('ONLINE') 
        listdata['SizeMB'].append(None) 
    
    usermessage.ezprint('\tdone',log,verbose)

    listpd = pd.DataFrame.from_dict(listdata)
    
    return listpd