#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage Sentinel-1 GRD for EZ-InSAR

The module allows to manage Sentinel-1 GRD
    
    (From `ezinsar` package)

Changelog:

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
from osgeo import gdal, osr

from ezinsar import constants
from ezinsar import usermessage
from ezinsar.eicomponents.slcmodule import slctools
from ezinsar.api import ASFapi, Copernicusapi, GEODESapi, EarthDATAapi
from ezinsar.eicomponents.templatevar import listSLCempty
from ezinsar.tools import miscellaneous
from ezinsar.eicomponents.demmodule import demfunctions
from ezinsar.tools import formattools

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Initialise the SLC list
################################################################################
def runS1IWbasemap(roi,
        output_file,
        year = datetime.datetime.year,
        month = 'latest', 
        epsg = None,
        resolution = None,
        temp_dir: Optional[str] = '.'+os.sep+'tmp_'+''.join(random.choice(string.ascii_lowercase) for i in range(5)),
        username = constants.__username__,
        password = constants.__password__,
        dB: Optional[bool] = True,
        cleaning: Optional[bool] = True,
        printonly: Optional[bool] = False,
        verbose: Optional[bool] = True, 
        log: Optional[bool] = None, 
        ):

        """Download and create a GTiff images of Sentinel-1 from the monthly mosaics

        The function will download and create a GTiff images of Sentinel-1 from the monthly mosaics

        Args:

        """

        usermessage.openingmsg(__name__,__name__,__file__,constants.__copyright__,'Download and create a GTiff images of Sentinel-1 from the monthly mosaics',log,verbose)

        usermessage.ezprint('Region of Interest: %s' % (roi),log,verbose) 
        usermessage.ezprint('Output file: %s' % (output_file),log,verbose) 
        usermessage.ezprint('Year: %s' % (year),log,verbose) 
        usermessage.ezprint('Month: %s' % (month),log,verbose) 
        usermessage.ezprint('EPSG code if warping: %s' % (epsg),log,verbose) 
        usermessage.ezprint('Temporary directory: %s' % (temp_dir),log,verbose) 

        # Create the list of images 
        listS1data = Copernicusapi.retrieve('S1', 
                        roi, 
                        date1 = datetime.datetime.strptime('2013-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
                        date2 = datetime.datetime.strptime('2030-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
                        level = 'Monthly Mosaics',
                        log = log, 
                        verbose = verbose,
                )
        
        ## Fix the Names
        newname = [x+'.zip' for x in listS1data['Name']]
        listS1data['Name'] = newname

        usermessage.ezprint('Filter the results according to the user input',log,verbose) 

        # First depletion for the date
        idxdrop = []
        for idx, rowi in listS1data.iterrows():
                if int(rowi['Date1'].split('-')[0]) != year:
                        idxdrop.append(idx) 
        listS1data.drop(index=idxdrop, inplace=True)
        listS1data.reset_index(drop=True, inplace=True)

        if len(listS1data['Name']) == 0:
                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                'The year %s is not available.' % (year),log,verbose))

        # Second depletion for the QX
        listQ = []
        for idx, rowi in listS1data.iterrows():
                listQ.append(rowi['Name'].split('_')[4])
        listQ = np.sort(np.unique(listQ)).tolist()

        if month == 'latest':
                Qselected = listQ[-1]
        else:
                if not month in listQ:
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                'The quarter %s is not available in %s' % (month,listQ),log,verbose))
                else:
                        Qselected = month

        idxdrop = []
        for idx, rowi in listS1data.iterrows():
                if not rowi['Name'].split('_')[4] == Qselected:
                        idxdrop.append(idx) 
        listS1data.drop(index=idxdrop, inplace=True)
        listS1data.reset_index(drop=True, inplace=True)

        # # Last depletion for the TILES
        listTile = []
        for idx, rowi in listS1data.iterrows():
                listTile.append(rowi['Name'].split('_')[5][0:2])
        listTile = np.sort(np.unique(listTile)).tolist() 
        freqTile = {}
        for item in listTile:
                if item in freqTile:
                        freqTile[item] += 1
                else:
                        freqTile[item] = 1
        TileNb = max(freqTile, key=freqTile.get)
        idxdrop = []
        for idx, rowi in listS1data.iterrows():
                if not rowi['Name'].split('_')[5][0:2] == TileNb:
                        idxdrop.append(idx) 
        listS1data.drop(index=idxdrop, inplace=True)
        listS1data.reset_index(drop=True, inplace=True)

        usermessage.ezprint('\tdone',log,verbose) 
        
        if printonly == True:
                print(listS1data)
        
        else:
                # Download by using the simply wrapper
                Copernicusapi.simplydownload(listS1data, 
                                temp_dir,
                                username = username,  
                                password = password,
                                log = log, 
                                verbose = False,
                                verboseprogress = verbose,
                                sizecheck = 50e6,
                        )

                usermessage.ezprint('Detect and extract the tile(s)',log,verbose) 

                listfileVV = []
                listfileVH = []
               
                for fi in listS1data['Name']:
                        with ZipFile(temp_dir+os.sep+fi, 'r') as zipObj:
                                listOfFileNames = zipObj.namelist()
                        for entry in listOfFileNames:
                                if 'VV' in entry:
                                        listfileVV.append('%svsizip%s%s%s%s' % (os.sep,os.sep,temp_dir+os.sep+fi,os.sep,entry))
                                elif 'VH' in entry:
                                        listfileVH.append('%svsizip%s%s%s%s' % (os.sep,os.sep,temp_dir+os.sep+fi,os.sep,entry))
                               
                demfunctions.mergetiles(listfileVV,
                        temp_dir+os.sep+'tmp_VV.tif',
                        format='GTiff',
                        verbose=verbose,
                        log=log)
                
                demfunctions.mergetiles(listfileVH,
                        temp_dir+os.sep+'tmp_VH.tif',
                        format='GTiff',
                        verbose=verbose,
                        log=log)

                usermessage.ezprint('\tdone',log,verbose) 

                demfunctions.warp(temp_dir+os.sep+'tmp_VV.tif',
                        temp_dir+os.sep+'tmp_VV_2.tif',
                        epsg=epsg,
                        roi = roi,
                        resolution = resolution,
                        verbose=verbose,
                        log=log)
                
                demfunctions.warp(temp_dir+os.sep+'tmp_VH.tif',
                        temp_dir+os.sep+'tmp_VH_2.tif',
                        epsg=epsg,
                        roi = roi,
                        resolution = resolution,
                        verbose=verbose,
                        log=log)
                
                ## Assembly 
                usermessage.ezprint('Assemble the images',log,verbose)
                
                if output_file == 'auto':
                        output = 'Sentinel1_IW_mosaic_%s_%s_%s.tif' % (year,Qselected,'VV')
                        outputbis = 'Sentinel1_IW_mosaic_%s_%s_%s.tif' % (year,Qselected,'VH')
                else:
                        output = output_file + 'VV'
                        outputbis = output_file + 'VH'

                novalue = formattools.readnodata(temp_dir+os.sep+'tmp_VV_2.tif')

                src_ds = gdal.Open(temp_dir+os.sep+'tmp_VV_2.tif')
                bandVV = src_ds.GetRasterBand(1).ReadAsArray().astype(np.float32)
                bandVV[bandVV==novalue] = np.nan        

                if dB: 
                       bandVV = 10 * np.log10(bandVV)
                        
                dst_ds = gdal.GetDriverByName("GTiff").Create(output, src_ds.RasterXSize, src_ds.RasterYSize, 1, gdal.GDT_Float32)
                dst_ds.SetGeoTransform(src_ds.GetGeoTransform()) 
                dst_ds.SetProjection(src_ds.GetProjection())
                dst_ds.GetRasterBand(1).WriteArray(bandVV)   
                dst_ds.SetMetadata({"AREA_OR_POINT": "%s" % (formattools.areapointGTiff(temp_dir+os.sep+'tmp_VV.tif')),"TIFFTAG_SOFTWARE": "Created with EZ-InSAR %s %s" % (constants.__version__,constants.__copyright__)})
                dst_ds.FlushCache()
                src_ds = None
                dst_ds = None

                src_ds = gdal.Open(temp_dir+os.sep+'tmp_VH_2.tif')
                bandVH = src_ds.GetRasterBand(1).ReadAsArray().astype(np.float32)
                bandVH[bandVH==novalue] = np.nan   

                if dB: 
                       bandVH = 10 * np.log10(bandVH)

                dst_ds = gdal.GetDriverByName("GTiff").Create(outputbis, src_ds.RasterXSize, src_ds.RasterYSize, 1, gdal.GDT_Float32)
                dst_ds.SetGeoTransform(src_ds.GetGeoTransform()) 
                dst_ds.SetProjection(src_ds.GetProjection())
                dst_ds.GetRasterBand(1).WriteArray(bandVH)   
                dst_ds.SetMetadata({"AREA_OR_POINT": "%s" % (formattools.areapointGTiff(temp_dir+os.sep+'tmp_VH.tif')),"TIFFTAG_SOFTWARE": "Created with EZ-InSAR %s %s" % (constants.__version__,constants.__copyright__)})
                dst_ds.FlushCache()
                src_ds = None
                dst_ds = None
        
                usermessage.ezprint('\tdone',log,verbose)

                usermessage.ezprint('Saved in %s' % (output),log,verbose)

                if cleaning:
                        if os.path.isdir(temp_dir):
                                shutil.rmtree(temp_dir) 