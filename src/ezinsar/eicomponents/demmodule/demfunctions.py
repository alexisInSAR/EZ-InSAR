#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to add the functions for the DEM module

The module allows to add functions to the DEM modules
    
    (From `ezinsar` package)

Changelog:
        * 3.2.2: Delete the support of wget for Windows, Alexis Hrysiewicz, Sep. 2025
        * 3.2.1: Initial version, Sep. 2025

"""

from ezinsar import usermessage
from ezinsar import constants
from ezinsar.eicomponents.demmodule import demconstants
from ezinsar.api import Copernicusapi
from ezinsar.tools import formattools
import geopandas as gpd 
from shapely import ops
from shapely.wkt import loads
from shapely.geometry import shape
import datetime
import numpy as np 
import os 
import glob
from zipfile import ZipFile
from osgeo import gdal
import osgeo_utils.gdal_calc
from typing import Optional, Union
import platform
import rasterio
from rasterio import features
import scipy
import platform
from ezinsar.tools import miscellaneous

import elevation

######################################################
## printinfo
######################################################
def printinfo(verbose=True,full=True):
        """Print the DEM information

        The function prints the DEM information. 

        Args:
                verbose (bool): verbose [Default: `True`].

        """

        usermessage.openingmsg(__name__,__name__,__file__,constants.__copyright__,'List the DEMs available with EZ-InSAR',None,verbose)

        if full == False:
                usermessage.ezprint('The DEM list is as follows:',None,verbose)

        for demi in list(demconstants.__DEMinformation__.keys()):
                if not demi == 'perso':
                        if full == True:
                                usermessage.ezprint('%s\n%s\n%s' % (constants.__displayline2__,
                                                                demconstants.__DEMinformation__[demi]['name'],
                                                                constants.__displayline2__)
                                                                ,None,verbose) 
                                
                                for keyi in list(demconstants.__DEMinformation__[demi].keys()):
                                        if not keyi == 'extent_file':
                                                usermessage.ezprint('\t%s: %s' % (keyi.capitalize(),
                                                                                demconstants.__DEMinformation__[demi][keyi]),None,verbose) 
                                usermessage.ezprint('',None,verbose) 
                        else:
                                usermessage.ezprint('\t%s - %s' % (demconstants.__DEMinformation__[demi]['key'],
                                                                demconstants.__DEMinformation__[demi]['name']),None,verbose)
                
######################################################
## checkext
######################################################
def checkext(roi,
        keyDEM,
        verbose=True,
        log=None):
        """Check if the DEM covers the Region of Interest

        The function prints the DEM information. 

        Args:
                roi (any): Polygon 
                keyDEM (str): Key code of the DEM
                verbose (bool): verbose [Default: `True`].
                log (bool): log [Default: `None`].

        Returns: 
                bool: if the intersection is higher than 0

        """             

        usermessage.openingmsg(__name__,__name__,__file__,constants.__copyright__,'Check if the DEM covers the Region of Interest ',log,verbose)

        if not keyDEM in list(demconstants.__DEMinformation__.keys()): 
                raise TypeError(usermessage.typeerrormsg(
                                __name__,checkext.__name__,__file__,constants.__copyright__,
                                'keyDEM',list(demconstants.__DEMinformation__.keys()),log))

        usermessage.ezprint('Region of Interest: %s' % (roi),log,verbose) 
        usermessage.ezprint('DEM: %s' % (keyDEM),log,verbose) 

        # ## Create the extent polygon
        if keyDEM in ['SRTM','NASADEM','Copernicus','Copernicus3']: 
                data = gpd.read_file(demconstants.__DEMinformation__[keyDEM]['extent_file'])
                polyDEM = data['geometry'][0]
        elif 'RGEALTI' in keyDEM: 
                data = gpd.read_file('https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/contours-geographiques-tres-simplifies-des-departements-2019/exports/geojson?lang=en&timezone=Europe%2FLondon')
                polyDEM = ops.unary_union(data['geometry'])
        elif 'AW3D30' in keyDEM: 
                ## Used the file provided by Open Topography
                data = gpd.read_file('https://raw.githubusercontent.com/OpenTopography/Data_Catalog_Spatial_Boundaries/main/OpenTopography_Raster/AW3D30.geojson')
                polyDEM = data['geometry'][0]
        elif 'COPDEM' in keyDEM: 
                results = Copernicusapi.retrieve(keyDEM, 
                        roi, 
                        date1 = datetime.datetime.strptime('2000-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
                        date2 = datetime.datetime.strptime('2030-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
                        log = log, 
                        verbose = False,
                )
                polyDEM = ops.unary_union([loads(x) for x in results['PolyFrame'].tolist()])

        elif 'perso' == keyDEM: 
                raise ValueError(usermessage.errormsg(__name__,checkext.__name__,__file__,constants.__copyright__,'This function is not available with personal DEM.',log))

        ## Compute the intersection and results
        intersectionvalue = roi.intersection(polyDEM).area/roi.area*100
        if intersectionvalue == 100: 
                usermessage.ezprint('Full intersection of the Region of Interest and the DEM',log,verbose) 
        elif intersectionvalue == 0: 
                raise ValueError(usermessage.errormsg(__name__,checkext.__name__,__file__,constants.__copyright__,'No intersection between the Region of Interest and the DEM.',log))
        else: 
                usermessage.warningmsg(__name__,checkext.__name__,__file__,'Uncomplete intersection of the Region of Interest and the DEM: %0.3f %%, but this can be linked to sea.' % (intersectionvalue),log,verbose) 

        return (intersectionvalue>0)

######################################################
## createDEMlist
######################################################
def createDEMlist(lonmin,lonmax,latmin,latmax,typeDEM):
        """Create a list of tiles for DEM download. 

        Create a list of DEM tiles for `demtools.download` based on coordanites. 

        Args:
                lonmin (float): Minimal longitude
                lonmax (float): Maximal longitude
                latmin (float): Minimal latitude
                latmax (float): Maximal latitude
                typeDEM (str): Type of the DEM
                
        Returns: 
                list: List of the DEM tiles

        """ 

        listDEM = dict()
        listDEM['latmin'] = []
        listDEM['latmax'] = []
        listDEM['lonmin'] = []
        listDEM['lonmax'] = []
        listDEM['name'] = []
        listDEM['tile'] = [] # used by AW3D30

        if 'SRTM' in typeDEM:
                lon_sep = np.arange(lonmin,lonmax)
                lat_sep = np.arange(latmin,latmax)
                
                h = 0
                for loni in lon_sep:
                        for lati in lat_sep: 
                                listDEM['lonmin'].append(loni)   
                                listDEM['lonmax'].append(loni+1)     
                                listDEM['latmin'].append(lati)   
                                listDEM['latmax'].append(lati+1)      

                                listDEM['name'].append('dem_tmp_%d.tif' % (h))   
                                h = h + 1

        elif 'NASADEM' in typeDEM or 'Copernicus' in typeDEM:
                lon_sep = np.arange(lonmin,lonmax)
                lat_sep = np.arange(latmin,latmax)
                
                h = 0
                for loni in lon_sep:
                        for lati in lat_sep: 
                                
                                if loni < 0: 
                                        listDEM['lonmin'].append('w%0.3d' % (np.abs(loni)))  
                                else:
                                        listDEM['lonmin'].append('e%0.3d' % (loni))  

                                if lati < 0: 
                                        listDEM['latmin'].append('s%0.2d' % (np.abs(lati)))  
                                else:
                                        listDEM['latmin'].append('n%0.2d' % (lati)) 
                                
                                listDEM['name'].append('dem_tmp_%d.tif' % (h))   
                                h = h + 1

        elif 'AW3D30' in typeDEM: 
                lon_sep = np.arange(lonmin,lonmax)
                lat_sep = np.arange(latmin,latmax)
                
                h = 0
                for loni in lon_sep:
                        for lati in lat_sep: 
                                
                                if loni < 0: 
                                        listDEM['lonmin'].append('W%0.3d' % (np.abs(loni)))  
                                        tilew = 5
                                else:
                                        listDEM['lonmin'].append('E%0.3d' % (loni))  
                                        tilew = 0

                                if lati < 0: 
                                        listDEM['latmin'].append('S%0.3d' % (np.abs(lati)))  
                                        tilen = 5
                                else:
                                        listDEM['latmin'].append('N%0.3d' % (lati)) 
                                        tilen = 0
                                
                                listDEM['name'].append('dem_tmp_%d.tif' % (h))   

                                tile = ''
                                if lati < 0:  
                                        tile = tile + 'S%0.3d' % (np.abs(int(np.fix(np.abs(lati)/5.0)*5.0)+tilen))
                                else: 
                                        tile = tile + 'N%0.3d' % (np.abs(int(np.fix(np.abs(lati)/5.0)*5.0)+tilen))
                                if loni < 0:  
                                        tile = tile + 'W%0.3d' % (np.abs(int(np.fix(np.abs(loni)/5.0)*5.0)+tilew))
                                else: 
                                        tile = tile + 'E%0.3d' % (np.abs(int(np.fix(np.abs(loni)/5.0)*5.0)+tilew))
                                listDEM['tile'].append(tile)
                                
                                h = h + 1
        
        return listDEM

######################################################
## listtiles
######################################################
def listtiles(roi,
        keyDEM,
        verbose=True,
        log=None):
        """List the tiles regarding the DEM

        The function lists the tiles regarding the DEM

        Args:
                roi (any): Polygon 
                keyDEM (str): Key code of the DEM
                verbose (bool): verbose [Default: `True`].
                log (bool): log [Default: `None`].

        Returns: 
                (list): List of tiles
                
        """             

        usermessage.openingmsg(__name__,__name__,__file__,constants.__copyright__,'List the tiles regarding the DEM',log,verbose)

        if not keyDEM in list(demconstants.__DEMinformation__.keys()): 
                raise TypeError(usermessage.typeerrormsg(
                                __name__,checkext.__name__,__file__,constants.__copyright__,
                                'keyDEM',list(demconstants.__DEMinformation__.keys()),log))

        usermessage.ezprint('Region of Interest: %s' % (roi),log,verbose) 
        usermessage.ezprint('DEM: %s' % (keyDEM),log,verbose) 

        ## Compute the BBOX for the DEM
        listtile = []

        if keyDEM in ['SRTM','NASADEM','Copernicus','Copernicus3','AW3D30']:
                lon, lat = roi.exterior.xy 
                lonmin = np.floor(np.min(lon))
                lonmax = np.ceil(np.max(lon))
                latmin = np.floor(np.min(lat))
                latmax = np.ceil(np.max(lat)) 

                usermessage.ezprint('BBOX for the DEM search: %s / %s / %s / %s' % (lonmin,latmin,lonmax,latmax),log,verbose)

                listDEM = createDEMlist(lonmin,lonmax,latmin,latmax,keyDEM)

                for idx, demi in enumerate(listDEM['name']):
                        if keyDEM == 'SRTM':
                                a = 'dummy'
                        elif keyDEM == 'NASADEM':
                                listtile.append('NASADEM_HGT_'+listDEM['latmin'][idx]+listDEM['lonmin'][idx]+'.tif')
                        elif keyDEM == 'Copernicus':
                                listtile.append('Copernicus_DSM_COG_10_'+listDEM['latmin'][idx].upper()+'_00_'+listDEM['lonmin'][idx].upper()+'_00_DEM.tif')
                        elif keyDEM == 'Copernicus3':
                                listtile.append('Copernicus_DSM_COG_30_'+listDEM['latmin'][idx].upper()+'_00_'+listDEM['lonmin'][idx].upper()+'_00_DEM.tif')
                        elif keyDEM == 'AW3D30':
                                listtile.append(constants.__linkAW3D30__+listDEM['tile'][idx]+'/'+listDEM['latmin'][idx]+listDEM['lonmin'][idx]+'.zip')

        elif 'COPDEM' in keyDEM:
                results = Copernicusapi.retrieve(keyDEM, 
                        roi, 
                        date1 = datetime.datetime.strptime('2000-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
                        date2 = datetime.datetime.strptime('2030-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
                        log = log, 
                        verbose = False,
                )
                listtile = results['Name'].tolist()

        else: 
               listtile = [] 

        ## Display the results 
        if listtile:
                usermessage.ezprint('The potential tile(s) is/are:',log,verbose) 
                for ti in listtile: 
                        usermessage.ezprint('\t%s' % (ti),log,verbose) 
        else: 
                usermessage.warningmsg(__name__,listtiles.__name__,__file__,'This function is not available for DEM %s.' % (keyDEM),log,verbose) 

        return listtile

######################################################
## downloadtiles
######################################################
def downloadtiles(roi,
        keyDEM,
        outdir = '.'+os.sep+'demtiles',
        username = constants.__username__,
        password = constants.__password__,
        nameDEM = 'EZInSARDEM',
        tiles = None,
        verbose=True,
        log=None):
        """Download the DEM tiles

        The function download the DEM tiles

        Args:
                roi (any): Polygon 
                keyDEM (str): Key code of the DEM
                outdir (str): Output directory [Default: .].
                username (str): Username for provider with account 
                password (str): password for provider with account 
                verbose (bool): verbose [Default: `True`].
                log (bool): log [Default: `None`].
                
        """             

        usermessage.openingmsg(__name__,downloadtiles.__name__,__file__,constants.__copyright__,'Download the DEM tiles',log,verbose)

        if not keyDEM in list(demconstants.__DEMinformation__.keys()): 
                raise TypeError(usermessage.typeerrormsg(
                                __name__,downloadtiles.__name__,__file__,constants.__copyright__,
                                'keyDEM',list(demconstants.__DEMinformation__.keys()),log))

        usermessage.ezprint('Region of Interest: %s' % (roi),log,verbose) 
        usermessage.ezprint('DEM: %s' % (keyDEM),log,verbose) 
        usermessage.ezprint('Output Directory: %s' % (outdir),log,verbose) 
        usermessage.ezprint('Name of the DEM file(s): %s' % (nameDEM),log,verbose)

        if not tiles == None:  
                usermessage.ezprint('Pre-selected tiles: %s' % (tiles),log,verbose) 
                raise ValueError(usermessage.errormsg(__name__,downloadtiles.__name__,__file__,constants.__copyright__,'This option is not available with the current version of EZ-InSAR.',log))

        ## Create the ouput 
        if not os.path.isdir(outdir):
                os.mkdir(outdir)

        lon, lat = roi.exterior.xy 
        lonmin = np.floor(np.min(lon))
        lonmax = np.ceil(np.max(lon))
        latmin = np.floor(np.min(lat))
        latmax = np.ceil(np.max(lat)) 

        usermessage.ezprint('BBOX for the DEM search: %s / %s / %s / %s' % (lonmin,latmin,lonmax,latmax),log,verbose)

        ############################################################
        if 'SRTM' == keyDEM:  
                usermessage.ezprint('Download the SRTM DEM: ...',log,verbose)

                listDEM = createDEMlist(lonmin,lonmax,latmin,latmax,keyDEM)

                for idx, demi in enumerate(listDEM['name']):
                        usermessage.ezprint('\tFor the tile (%d of %d files): %d/%d/%d/%d => Found' % (
                                idx+1,len(listDEM['name']),
                                listDEM['lonmin'][idx],
                                listDEM['latmin'][idx],
                                listDEM['lonmax'][idx],
                                listDEM['latmax'][idx])
                                ,log,verbose)

                        elevation.clip(bounds=(listDEM['lonmin'][idx],
                                               listDEM['latmin'][idx],
                                               listDEM['lonmax'][idx],
                                               listDEM['latmax'][idx]), 
                                        output=os.path.abspath(outdir)+os.sep+nameDEM+'_%s.tif' % (idx)) 
                        elevation.clean()

        ############################################################
        elif 'NASADEM' in keyDEM: 
                usermessage.ezprint('Download the NASADEM DEM: ...',log,verbose) 
                
                listDEM = createDEMlist(lonmin,lonmax,latmin,latmax,keyDEM)
                
                for idx, demi in enumerate(listDEM['name']):
                        
                        usermessage.ezprint('\tFor the tile (%d of %d files): %s/%s => Found' % (idx+1,len(listDEM['name']),listDEM['lonmin'][idx],listDEM['latmin'][idx]),log,verbose)

                        if not os.path.isfile(outdir+os.sep+'NASADEM_HGT_'+listDEM['latmin'][idx]+listDEM['lonmin'][idx]+'.tif'):
                                cmdi = 'aws s3 cp s3://raster/NASADEM/NASADEM_be/%s.tif %s --endpoint-url https://opentopography.s3.sdsc.edu --no-sign-request' % ('NASADEM_HGT_'+listDEM['latmin'][idx]+listDEM['lonmin'][idx],outdir+os.sep)
                                os.system(cmdi)
                        else: 
                                usermessage.ezprint('\t\t The file has been found.',log,verbose)

                        if os.path.isfile(outdir+os.sep+'NASADEM_HGT_'+listDEM['latmin'][idx]+listDEM['lonmin'][idx]+'.tif'):
                                os.rename(outdir+os.sep+'NASADEM_HGT_'+listDEM['latmin'][idx]+listDEM['lonmin'][idx]+'.tif',
                                        outdir+os.sep+nameDEM+'_%s.tif' % (idx)
                                        )
                        else: 
                                usermessage.ezprint('\t\t This tile does not exist.',log,verbose) 

        ############################################################
        elif 'Copernicus' == keyDEM: 
                usermessage.ezprint('Download the Copernicus DEM (legacy): ...',log,verbose) 

                listDEM = createDEMlist(lonmin,lonmax,latmin,latmax,keyDEM)

                for idx, demi in enumerate(listDEM['name']):
                        
                        usermessage.ezprint('\tFor the tile (%d of %d files): %s/%s => Found' % (idx+1,len(listDEM['name']),listDEM['lonmin'][idx],listDEM['latmin'][idx]),log,verbose)

                        if not os.path.isfile(outdir+os.sep+'Copernicus_DSM_COG_10_'+listDEM['latmin'][idx].upper()+'_00_'+listDEM['lonmin'][idx].upper()+'_00_DEM.tif'):
                                cmdi = 'aws s3 cp s3://copernicus-dem-30m/%s/%s.tif %s --no-sign-request' % ('Copernicus_DSM_COG_10_'+listDEM['latmin'][idx].upper()+'_00_'+listDEM['lonmin'][idx].upper()+'_00_DEM','Copernicus_DSM_COG_10_'+listDEM['latmin'][idx].upper()+'_00_'+listDEM['lonmin'][idx].upper()+'_00_DEM',outdir+os.sep)
                                os.system(cmdi)
                        else: 
                                usermessage.ezprint('\t\t The file has been found.',log,verbose)

                        if os.path.isfile(outdir+os.sep+'Copernicus_DSM_COG_10_'+listDEM['latmin'][idx].upper()+'_00_'+listDEM['lonmin'][idx].upper()+'_00_DEM.tif'):
                                os.rename(outdir+os.sep+'Copernicus_DSM_COG_10_'+listDEM['latmin'][idx].upper()+'_00_'+listDEM['lonmin'][idx].upper()+'_00_DEM.tif',
                                        outdir+os.sep+nameDEM+'_%s.tif' % (idx))
                        else: 
                                usermessage.ezprint('\t\t This tile does not exist.',log,verbose)

        ############################################################
        elif 'Copernicus3' == keyDEM:  
                usermessage.ezprint('Download the Copernicus DEM (90-m spatial resolution): ...',log,verbose) 

                listDEM = createDEMlist(lonmin,lonmax,latmin,latmax,keyDEM)

                for idx, demi in enumerate(listDEM['name']):
                        
                        usermessage.ezprint('\tFor the tile (%d of %d files): %s/%s => Found' % (idx+1,len(listDEM['name']),listDEM['lonmin'][idx],listDEM['latmin'][idx]),log,verbose)

                        if not os.path.isfile(outdir+os.sep+'Copernicus_DSM_COG_30_'+listDEM['latmin'][idx].upper()+'_00_'+listDEM['lonmin'][idx].upper()+'_00_DEM.tif'):
                                cmdi = 'aws s3 cp s3://copernicus-dem-90m/%s/%s.tif %s --no-sign-request' % ('Copernicus_DSM_COG_30_'+listDEM['latmin'][idx].upper()+'_00_'+listDEM['lonmin'][idx].upper()+'_00_DEM','Copernicus_DSM_COG_30_'+listDEM['latmin'][idx].upper()+'_00_'+listDEM['lonmin'][idx].upper()+'_00_DEM',outdir+os.sep)
                                os.system(cmdi)
                        else: 
                                usermessage.ezprint('\t\t The file has been found.',log,verbose)

                        if os.path.isfile(outdir+os.sep+'Copernicus_DSM_COG_30_'+listDEM['latmin'][idx].upper()+'_00_'+listDEM['lonmin'][idx].upper()+'_00_DEM.tif'):
                                os.rename(outdir+os.sep+'Copernicus_DSM_COG_30_'+listDEM['latmin'][idx].upper()+'_00_'+listDEM['lonmin'][idx].upper()+'_00_DEM.tif',outdir+os.sep+nameDEM+'_%s.tif' % (idx))
                        else: 
                                usermessage.ezprint('\t\t This tile does not exist.',log,verbose)

        ############################################################
        elif 'AW3D30' in keyDEM: 
                usermessage.ezprint('Download the AW3D30 DSM: ...',log,verbose) 

                listDEM = createDEMlist(lonmin,lonmax,latmin,latmax,keyDEM)

                ## Create the links 
                listDEM['link'] = []

                for idx, demi in enumerate(listDEM['name']):
                        listDEM['link'].append(constants.__linkAW3D30__+listDEM['tile'][idx]+'/'+listDEM['latmin'][idx]+listDEM['lonmin'][idx]+'.zip')

                miscellaneous.download_file(constants.__tilesAW3D30__,
                        verbose=verbose,
                        log=log,
                        output_file='tmp.txt')

                tile_name = []
                tile_version = []
                with open('tmp.txt') as fi: 
                        for ti in fi: 
                                if not 'Tile' in ti: 
                                        tile_name.append(ti.split()[0])
                                        tile_version.append(ti.split()[1])
                os.remove('tmp.txt')
                usermessage.ezprint('\t\tdone',log,verbose) 

                usermessage.ezprint('\tDownload the DSM-tiles:',log,verbose) 
                for idx, demi in enumerate(listDEM['name']):
        
                        if listDEM['link'][idx].split('/')[-1].split('.')[0] in tile_name: 
                                usermessage.ezprint('\tFor the tile (%d of %d files): %s/%s => Found (downloading)' % (idx+1,len(listDEM['name']),listDEM['lonmin'][idx],listDEM['latmin'][idx]),log,verbose)

                                if constants.__SLCdownloader__ == 'wget':
                                        if  platform.system() == 'Windows':
                                                raise ValueError(usermessage.errormsg(__name__,downloadtiles.__name__,__file__,constants.__copyright__,'The wget mode is not available with Windows. Please modify the __SLCdownloader__ option to python.',log))
            
                                        cmdi = 'wget -c --http-user=%s --http-password=%s "%s" -P %s' % (
                                                username,password,listDEM['link'][idx],
                                                outdir+os.sep)
                                        os.system(cmdi)

                                else:
                                        miscellaneous.download_file(listDEM['link'][idx],
                                                username=username,
                                                password=password,
                                                verbose=verbose,
                                                log=log,
                                                output_file=outdir+os.sep+listDEM['link'][idx].split('/')[-1])
                                        
                        else: 
                                usermessage.ezprint('\tFor the tile (%d of %d files): %s/%s => Not available' % (idx+1,len(listDEM['name']),listDEM['lonmin'][idx],listDEM['latmin'][idx]),log,verbose)
                
                usermessage.ezprint('\t\tdone',log,verbose) 

                ## Unwrapping the tiles
                usermessage.ezprint('\tUnzip the DSM-tiles:',log,verbose)         
                listfile = glob.glob(outdir+os.sep+'*.zip')
                for idx, ti in enumerate(listfile):
                        with ZipFile(ti, 'r') as zipObj:
                                listOfFileNames = zipObj.namelist()
                                for entry in listOfFileNames: 
                                        if "_DSM.tif" in entry:
                                               zipObj.extract(entry, path=outdir, pwd=None) 
                        os.remove(ti) 

                # Rename (new idx)
                listfile = glob.glob(outdir+os.sep+'*'+os.sep+'*_DSM.tif')
                for idx, ti in enumerate(listfile):
                        os.rename(ti,outdir+os.sep+nameDEM+'_%s.tif' % (idx))
                        # shutil.rmtree(os.path.dirname(os.path.abspath(ti)))

                usermessage.ezprint('\t\tdone',log,verbose) 

        ############################################################
        elif 'RGEALTI-5m' == keyDEM: 
                usermessage.ezprint('Download the RGEALTI-5m DEM: ...',log,verbose)
                from ezinsar.api import IGNapi
                obj = IGNapi.RGEALTI(roi,outdir,resolution=5).run(warpoption=True,log=log,verbose=verbose)
                listfile = glob.glob(outdir+os.sep+'*.tif')
                for idx, ti in enumerate(listfile):
                        os.rename(ti,outdir+os.sep+nameDEM+'_%s.tif' % (idx))

        ############################################################
        elif 'RGEALTI-1m' in keyDEM: 
                usermessage.ezprint('Download the RGEALTI-1m DEM: ...',log,verbose)
                from ezinsar.api import IGNapi
                obj = IGNapi.RGEALTI(roi,outdir,resolution=1).run(warpoption=True,log=log,verbose=verbose)
                listfile = glob.glob(outdir+os.sep+'*.tif')
                for idx, ti in enumerate(listfile):
                        os.rename(ti,outdir+os.sep+nameDEM+'_%s.tif' % (idx))

        ############################################################
        elif 'COPDEM' in keyDEM: 
                usermessage.ezprint('Download the COPDEM: ...',log,verbose)
                from ezinsar.api import Copernicusapi
                import requests

                listtile = Copernicusapi.retrieve(keyDEM, 
                        roi, 
                        date1 = datetime.datetime.strptime('2000-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
                        date2 = datetime.datetime.strptime('2030-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
                        log = log, 
                        verbose = verbose,
                )

                access_token = Copernicusapi.get_access_token(username, password)
                headers = {"Authorization": f"Bearer {access_token}"}
                session = requests.Session()
                session.headers.update(headers)

                for idx, image in listtile.iterrows():
                        if not (os.path.isfile(outdir+os.sep+image['Name']) or os.path.isfile(outdir+os.sep+image['Name']+'.zip')):
                                usermessage.ezprint('For the tile (%d of %d files) => Downloading' % (idx+1,len(listtile['Name'])),log,verbose)
                                Copernicusapi.download(image, 
                                        outdir,
                                        username = username,  
                                        password = password,
                                        access_token = access_token, 
                                        session = session,
                                        headers = headers,
                                        log = log, 
                                        verbose = False,
                                        verboseprogress=True,
                                        sizecheck = 1e6,
                                        )
                        else: 
                                usermessage.ezprint('For the tile (%d of %d files) => Downloaded' % (idx+1,len(listtile['Name'])),log,verbose)

                for idx, li in enumerate(glob.glob(outdir+os.sep+'DEM*SAR*DGE*')):
                        if not li.endswith('.zip'): 
                                os.rename(li,li+'.zip')

                for idx, li in enumerate(glob.glob(outdir+os.sep+'DEM*SAR*DGE*')):
                        fileDEM = None
                        with ZipFile(li, 'r') as zipObj:
                                listOfFileNames = zipObj.namelist()
                                for entry in listOfFileNames: 
                                        if entry.endswith('_DEM.tif'):
                                                fileDEM = entry
                        fileDEM = os.path.abspath(li)+os.sep+fileDEM

                        usermessage.ezprint('Extract: %s' % (fileDEM),log,verbose)
                        src_ds = gdal.Open('%svsizip%s%s' % (os.sep,os.sep,fileDEM))
                        dst_ds = gdal.Translate(outdir+os.sep+nameDEM+'_%s.tif' % (idx), src_ds)
                        src_ds = None
                        dst_ds = None

                for idx, li in enumerate(glob.glob(outdir+os.sep+'*.zip')):
                        os.remove(li)
                        
        else: 
                usermessage.warningmsg(__name__,downloadtiles.__name__,__file__,'This function is not available for DEM %s.' % (keyDEM),log,verbose)

######################################################
## mergetiles
######################################################
def mergetiles(pathfile,
        outputfile,
        format='GTiff',
        verbose=True,
        log=None):
        """Merge the DEM tiles

        The function merges the DEM tiles

        Args:
                pathfile (str): Path of the file, i.e., ./DEMfile/*.tif 
                outputfile (str): Output file
                format (str): Format [Default: 'GTiff'].
                verbose (bool): verbose [Default: `True`].
                log (bool): log [Default: `None`].
                
        """    

        usermessage.openingmsg(__name__,mergetiles.__name__,__file__,constants.__copyright__,'Merge the DEM tiles',log,verbose)
        if not isinstance(pathfile,list):
                listfile = glob.glob(pathfile)
        else:
                listfile = pathfile

        usermessage.ezprint('Input file: %s' % (listfile),log,verbose) 
        usermessage.ezprint('Output format: %s' % (format),log,verbose) 
        usermessage.ezprint('Output file: %s' % (outputfile),log,verbose) 

        if os.path.isfile(outputfile): 
                raise ValueError(usermessage.errormsg(__name__,mergetiles.__name__,__file__,constants.__copyright__,'The file %s exists. Please delete it.' % (outputfile),log))
        
        nodata = formattools.readnodata(listfile[0])

        if platform.system() == 'Windows':
                keyprg = ''
        else: 
                keyprg = '.py'

        cmd = ['gdal_merge%s -q -o %s -of %s -a_nodata %s' % (keyprg,outputfile,format,nodata)]  
        for fi in listfile:
                cmd.append(fi)
        cmd = ' '.join(cmd)

        usermessage.ezprint('Run the GDAL command: %s' % (cmd),log,verbose) 
        os.system(cmd)

        if format == 'GTiff' and (listfile[0].endswith('.tif') or listfile[0].endswith('.tiff')):
                if platform.system() == 'Windows':
                        keyprg = ''
                else: 
                        keyprg = '.py'
                cmd = 'gdal_edit%s -mo AREA_OR_POINT=%s %s' % (keyprg,
                        formattools.areapointGTiff(listfile[0]),
                        outputfile,
                )
                os.system(cmd)

        # gdal_edit -mo AREA_OR_POINT=Point point.tif --config GTIFF_POINT_GEO_IGNORE YES 
        usermessage.ezprint('done.',log,verbose) 

######################################################
## extractmask
######################################################
def extractmask(inputfile,
        maskfile,
        value,
        format='GTiff',
        verbose=True,
        log=None):
        """Extract a mask from a raster

        The function extract a mask from a raster

        Args:
                inputfile (str): Input file
                maskfile (str): Output mask file
                value <int>: Value 
                format (str): Format [Default: 'GTiff'].
                verbose (bool): verbose [Default: `True`].
                log (bool): log [Default: `None`].
                
        """    

        usermessage.openingmsg(__name__,extractmask.__name__,__file__,constants.__copyright__,'Create a raster masked based on a value',log,verbose)

        if value in [None,'None']: 
                value = formattools.readnodata(inputfile)
        
        usermessage.ezprint('Input file: %s' % (inputfile),log,verbose) 
        usermessage.ezprint('Output format: %s' % (format),log,verbose) 
        usermessage.ezprint('Output file: %s' % (maskfile),log,verbose) 
        usermessage.ezprint('Value used for masking: %s' % (value),log,verbose) 

        src_ds = gdal.Open(inputfile)
        band = src_ds.GetRasterBand(1).ReadAsArray()
        mask = np.ones_like(band)
        mask[band==value] = 0

        dst_ds = gdal.GetDriverByName(format).Create(maskfile, src_ds.RasterXSize, src_ds.RasterYSize, 1, gdal.GDT_Byte)
        dst_ds.SetGeoTransform(src_ds.GetGeoTransform()) 
        dst_ds.SetProjection(src_ds.GetProjection())
        dst_ds.GetRasterBand(1).WriteArray(mask)   
        # dst_ds.GetRasterBand(1).SetNoDataValue(255)

        if format == 'GTiff' and (inputfile.endswith('.tif') or inputfile.endswith('.tiff')):
                dst_ds.SetMetadata({"AREA_OR_POINT": "%s" % (formattools.areapointGTiff(inputfile)),"TIFFTAG_SOFTWARE": "Created with EZ-InSAR %s %s" % (constants.__version__,constants.__copyright__)})
        dst_ds.FlushCache()

        usermessage.ezprint('Ouput file: %s' % (maskfile),log,verbose) 

        src_ds = None
        dst_ds = None

######################################################
## applymask
######################################################
def applymask(inputfile,
        outputfile,
        mask,
        invert=False, 
        format='GTiff',
        verbose=True,
        log=None):
        """Apply a mask to a raster

        The function applies a mask to a raster

        Args:
                inputfile (str): Input file
                outputfile (str): Output file
                maskfile (any): Mask information
                format (str): Format [Default: 'GTiff'].
                verbose (bool): verbose [Default: `True`].
                log (bool): log [Default: `None`].
                
        """    

        usermessage.openingmsg(__name__,applymask.__name__,__file__,constants.__copyright__,'Apply a mask to a raster',log,verbose)

        novalue = formattools.readnodata(inputfile)
        
        usermessage.ezprint('Input file: %s' % (inputfile),log,verbose) 
        usermessage.ezprint('Output format: %s' % (format),log,verbose) 
        usermessage.ezprint('Output file: %s' % (outputfile),log,verbose) 
        usermessage.ezprint('Mask information: %s' % (mask),log,verbose) 
        usermessage.ezprint('Nodata value: %s' % (novalue),log,verbose) 

        ## If the maks is a file
        if os.path.isfile(mask):

                if formattools.detectGDALdriver(mask) == 'Raster': 
                        src_ds = gdal.Open(mask)
                        mask = src_ds.GetRasterBand(1).ReadAsArray()
                        src_ds = None 

                        ## Read the input file
                        src_ds = gdal.Open(inputfile)
                        band = src_ds.GetRasterBand(1).ReadAsArray()
                        band[mask==0] = novalue
                        dst_ds = gdal.GetDriverByName(format).Create(outputfile, src_ds.RasterXSize, src_ds.RasterYSize, 1, gdal.GDT_Float32)
                        dst_ds.SetGeoTransform(src_ds.GetGeoTransform()) 
                        dst_ds.SetProjection(src_ds.GetProjection())
                        dst_ds.GetRasterBand(1).WriteArray(band)   
                        dst_ds.GetRasterBand(1).SetNoDataValue(novalue)

                        if format == 'GTiff' and (inputfile.endswith('.tif') or inputfile.endswith('.tiff')):
                                dst_ds.SetMetadata({"AREA_OR_POINT": "%s" % (formattools.areapointGTiff(inputfile)),"TIFFTAG_SOFTWARE": "Created with EZ-InSAR %s %s" % (constants.__version__,constants.__copyright__)})
                        dst_ds.FlushCache()

                else: 
                        cmd_i = 'ogr2ogr -of GeoJSON mask.geojson %s' % (mask)
                        os.system(cmd_i)
                        cmd_i = 'rio mask %s %s --geojson-mask %s --overwrite' % (
                                inputfile,
                                outputfile,
                                'mask.geojson',
                        )

                        if invert: 
                                cmd_i = cmd_i + ' --invert'

                        os.system(cmd_i)
                        if os.path.isfile('mask.geojson'):
                                os.remove('mask.geojson')

                        if format == 'GTiff' and (inputfile.endswith('.tif') or inputfile.endswith('.tiff')):
                                if platform.system() == 'Windows':
                                        keyprg = ''
                                else: 
                                        keyprg = '.py'
                                cmd = 'gdal_edit%s -mo AREA_OR_POINT=%s %s' % (keyprg,
                                        formattools.areapointGTiff(inputfile),
                                        outputfile,
                                )
                                os.system(cmd)

                usermessage.ezprint('Output file: %s' % (outputfile),log,verbose) 

                src_ds = None
                dst_ds = None

######################################################
## masktoshp
######################################################
def masktoshp(inputfile,
        outputfile,
        dilatefactor = 0,
        fillholes = False, 
        verbose=True,
        log=None):
        """Convert a mask to vector file 

        The function converts a mask to vector file 

        Args:
                inputfile (str): Input file
                outputfile (str): Output file
                dilatefactor (int): Dilation factor [Default: 0].
                verbose (bool): verbose [Default: `True`].
                log (bool): log [Default: `None`].
                
        """    

        usermessage.openingmsg(__name__,masktoshp.__name__,__file__,constants.__copyright__,'Convert a mask to vector file ',log,verbose)

        novalue = formattools.readnodata(inputfile)
        
        usermessage.ezprint('Input file: %s' % (inputfile),log,verbose) 
        usermessage.ezprint('Output file: %s' % (outputfile),log,verbose) 
        usermessage.ezprint('Nodata value: %s' % (novalue),log,verbose) 

        usermessage.ezprint('Dilate factor: %s' % (dilatefactor),log,verbose) 

        with rasterio.open(inputfile) as src:
                mask = src.read(1) 
                transform = src.transform
                crs = src.crs

        mask[mask==novalue] = 0
        mask[mask!=0] = 1

        # If dilate is enabled
        if not dilatefactor == 0: 
                structele = (np.ones((dilatefactor,dilatefactor)) == 1)
                mask = scipy.ndimage.binary_dilation(mask, structure=structele).astype(np.float32)
                if fillholes: 
                        mask = scipy.ndimage.binary_fill_holes(mask.astype(np.int8), structure=structele).astype(np.float32)
                                                               
        shapes = features.shapes(mask, transform=transform)
        polygons = [shape(geom) for geom, val in shapes if val == 1]
        gdf = gpd.GeoDataFrame(geometry=polygons, crs=crs)
        gdf.to_file(outputfile)

######################################################
## ellcorrection
######################################################
def ellcorrection(inputfile,
        outputfile,
        geoidecode,
        format='GTiff',
        nodata=True,
        verbose=True,
        log=None):
        """Apply the ellipsoid correction

        Apply the ellipsoid correction

        Args:
                inputfile (str): Input file
                geoidecode (str): Output file
                geoidecode (str): Geoide code or file
                value (int): Value 
                format (str): Format [Default: 'GTiff'].
                novalue (bool): Nodata value consideration [Default: True]
                verbose (bool): Verbose [Default: True]
                log (bool): log [Default: `None`].
                
        """    

        usermessage.openingmsg(__name__,ellcorrection.__name__,__file__,constants.__copyright__,'Apply the ellipsoid correction to a DEM',log,verbose)

        usermessage.ezprint('Input file: %s' % (inputfile),log,verbose) 
        usermessage.ezprint('Output format: %s' % (format),log,verbose) 
        usermessage.ezprint('Output file: %s' % (outputfile),log,verbose) 
        usermessage.ezprint('Mask the nodata values: %s' % (nodata),log,verbose) 

        if geoidecode.lower() in [x.lower() for x in ['EGM96','EGM1996','EGM08','EGM2008']]:
                usermessage.ezprint('Geoide code: %s' % (geoidecode),log,verbose) 
        elif os.path.isfile(geoidecode):
                usermessage.ezprint('Geoide file: %s' % (geoidecode),log,verbose) 
        else:
                raise ValueError(usermessage.errormsg(__name__,ellcorrection.__name__,__file__,constants.__copyright__,'The geoide must be EGM96, EGM08 or a file.',log))

        if geoidecode.lower() in [x.lower() for x in ['EGM96','EGM1996']]:
                geoid_file = constants.__cachedir__+os.sep+'egm96_15.gtx'
                if not os.path.isfile(geoid_file):
                        miscellaneous.download_file('https://github.com/OSGeo/proj-datumgrid/raw/master/egm96_15.gtx',
                                verbose=verbose,
                                log=log,
                                output_file=geoid_file)       
                else: 
                        usermessage.ezprint('\t\tThe file has been found.',log,verbose)  

        if geoidecode.lower() in [x.lower() for x in ['EGM08','EGM2008']]:
                usermessage.ezprint('\tDownload the EGM08 geoid model',log,verbose)
                geoid_file = constants.__cachedir__+os.sep+'egm08_25.gtx'
                if not os.path.isfile(geoid_file):
                        miscellaneous.download_file('https://media.githubusercontent.com/media/insarwxw/proj-datumgrid/master/world/egm08_25.gtx',
                                verbose=verbose,
                                log=log,
                                output_file=geoid_file)   
                else: 
                        usermessage.ezprint('\t\tThe file has been found.',log,verbose)  

        else: 
                geoid_file = geoidecode
                        
        cmd_i = 'gdalwarp -r bilinear -s_srs "+proj=longlat +datum=WGS84 +no_defs +geoidgrids=%s" -t_srs "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs" -overwrite' % (geoid_file)

        if nodata == True:
                novalue = formattools.readnodata(inputfile)
                cmd_i = cmd_i + ' -srcnodata %s -dstnodata %s' % (novalue,novalue)

        cmd_i = cmd_i + ' %s %s' % (inputfile,outputfile)               

        usermessage.ezprint('Run the GDAL command: %s' % (cmd_i),log,verbose) 
        os.system(cmd_i)

        if format == 'GTiff' and (inputfile.endswith('.tif') or inputfile.endswith('.tiff')):
                if platform.system() == 'Windows':
                        keyprg = ''
                else: 
                        keyprg = '.py'
                cmd = 'gdal_edit%s -mo AREA_OR_POINT=%s %s' % (keyprg,
                        formattools.areapointGTiff(inputfile),
                        outputfile,
                )
                os.system(cmd)

        usermessage.ezprint('done.',log,verbose) 
                    
######################################################
## translate
######################################################
def translate(inputfile,
        outputfile,
        roi = None,
        format='GTiff',
        nodata=True,
        byteswap = False,
        areaorpoint = 'Point', 
        xmlISCE = False,
        verbose=True,
        log=None):
        """Format the DEM 

        Format the DEM

        Args:
                inputfile (str): Input file
                outputfile (str): Output file
                roi (str): Region of Interest for cropping [Default: None]
                format (str): Format [Default: 'GTiff'].
                novalue (bool): Nodata value consideration [Default: True]
                byteswap (bool): Byte swap for Doris and Windows [Default: False]
                usepoint (bool): Force the use of Point system [Default: True]
                xmlISCE (bool): Create the auxilliary files for ISCE [Default: False]
                verbose (bool): Verbose [Default: True]
                log (bool): log [Default: `None`]
                
        """  
        usermessage.openingmsg(__name__,translate.__name__,__file__,constants.__copyright__,'Translate the DEM',log,verbose)

        usermessage.ezprint('Input file: %s' % (inputfile),log,verbose) 
        usermessage.ezprint('Output format: %s' % (format),log,verbose) 
        usermessage.ezprint('Output file: %s' % (outputfile),log,verbose) 
        usermessage.ezprint('Region of Interest: %s' % (roi),log,verbose) 

        usermessage.ezprint('Mask the nodata values: %s' % (nodata),log,verbose) 
        usermessage.ezprint('Byte Swap: %s' % (byteswap),log,verbose) 

        if (inputfile.endswith('.tif') or inputfile.endswith('.tiff')):
                if not formattools.areapointGTiff(inputfile) == areaorpoint:
                        usermessage.warningmsg(__name__,translate.__name__,__file__,'The input file uses AREA_OR_POINT=%s. It will be converted to %s, in-place.' % (formattools.areapointGTiff(inputfile), areaorpoint),log,verbose) 
                        if platform.system() == 'Windows':
                                keyprg = ''
                        else: 
                                keyprg = '.py'
                        cmd = 'gdal_edit%s -mo AREA_OR_POINT=%s %s --config GTIFF_POINT_GEO_IGNORE YES' % (keyprg,
                                        areaorpoint,inputfile,
                                )
                        os.system(cmd)

        options = '-of %s' % (format)
        if nodata:
                options = options + ' -a_nodata %s' % (nodata)
        if not roi == None: 
                lon, lat = roi.exterior.xy 
                lonmin = np.min(lon)
                lonmax = np.max(lon)
                latmin = np.min(lat)
                latmax = np.max(lat)
                options = options + ' -projwin %f %f %f %f -projwin_srs EPSG:4326' % (lonmin,latmax,lonmax,latmin)

        src_ds = gdal.Open(inputfile)
        dst_ds = gdal.Translate(outputfile, src_ds, options = options)
        src_ds = None
        dst_ds = None

        if format == 'ENVI' and byteswap == True:
        ## Byte swap if Windows is used (only required for Doris and ISCE-2???)
                formattools.ENVIbyteswap(outputfile,outputfile+'.hdr',verbose=False,log=log)

        if os.path.isfile(outputfile+'.aux.xml'):
                os.remove(outputfile+'.aux.xml')

        usermessage.ezprint('File saved in: %s.' % (outputfile),log,verbose)   

        if xmlISCE:
                from ezinsar.eicomponents.processor.isce2module import isce2tools
                os.environ['PATH'], os.environ['PYTHONPATH'] = isce2tools.isce2checkenv(mode='IW',verbose=False)
                cmd_i = 'fixImageXml.py -f -i %s' % (outputfile)
                status = os.system(cmd_i)

                if not status == 0:
                        raise ValueError(usermessage.errormsg(__name__,translate.__name__,__file__,constants.__copyright__,'Error during the ISCE conversion with the fixImageXml.py function.',log))

######################################################
## replace
######################################################
def replace(inputfile,
        outputfile,
        valueint,
        valueout,
        nodata=True,
        format = 'GTiff',
        verbose=True,
        log=None):
        """Replace values within the DEM raster

        Replace values within the DEM raster

        Args:
                inputfile (str): Input file
                outputfile (str): Output file
                valueint (float): Input value
                valueout (float): Output value
                novalue (bool): Nodata value consideration [Default: True]
                format (str): Format [Default: 'GTiff']
                verbose (bool): Verbose [Default: True]
                log (bool): log [Default: `None`]
                
        """  

        usermessage.openingmsg(__name__,replace.__name__,__file__,constants.__copyright__,'Replace values in the raster',log,verbose)

        usermessage.ezprint('Input file: %s' % (inputfile),log,verbose) 
        usermessage.ezprint('Output format: %s' % (format),log,verbose) 
        usermessage.ezprint('Output file: %s' % (outputfile),log,verbose) 

        usermessage.ezprint('Input value: %s' % (valueint),log,verbose) 
        usermessage.ezprint('Output value: %s' % (valueout),log,verbose) 

        usermessage.ezprint('Nodata: %s' % (nodata),log,verbose) 
 
        paralist = ['', '-A', inputfile, '--type', 'Float32', '--outfile', outputfile,'--calc', '"numpy.where(A==%s,%s,A)"' % (valueint,valueout),'--overwrite']
        if nodata:
                paralist = paralist + ['--NoDataValue','%s' % (valueout)]
        else:
                paralist = paralist + ['--hideNoData','--NoDataValue','none']

        osgeo_utils.gdal_calc.main(paralist)

        if format == 'GTiff' and (inputfile.endswith('.tif') or inputfile.endswith('.tiff')):
                if platform.system() == 'Windows':
                        keyprg = ''
                else: 
                        keyprg = '.py'
                cmd = 'gdal_edit%s -mo AREA_OR_POINT=%s %s' % (keyprg,
                        formattools.areapointGTiff(inputfile),
                        outputfile,
                )
                os.system(cmd)
        
        usermessage.ezprint('done.',log,verbose) 

######################################################
## warp
######################################################
def warp(inputfile,
        outputfile,
        epsg = None,
        roi = None,
        resolution = None,
        format='GTiff',
        nodata=True,
        verbose=True,
        log=None):
        """Warp the raster

        Warp the raster
                
        """    
        usermessage.openingmsg(__name__,warp.__name__,__file__,constants.__copyright__,'Wrap the raster',log,verbose)

        usermessage.ezprint('Input file: %s' % (inputfile),log,verbose) 
        usermessage.ezprint('Output format: %s' % (format),log,verbose) 
        usermessage.ezprint('Output file: %s' % (outputfile),log,verbose) 
        usermessage.ezprint('Mask the nodata values: %s' % (nodata),log,verbose) 
        usermessage.ezprint('Region of Interest: %s' % (roi),log,verbose) 
        usermessage.ezprint('Mask the nodata values: %s' % (nodata),log,verbose) 
        usermessage.ezprint('EPSG code: %s' % (epsg),log,verbose) 
        usermessage.ezprint('Resolution: %s' % (resolution),log,verbose) 

        cmd_i = 'gdalwarp -r bilinear -overwrite'

        if (not epsg == None) and (not epsg == 'None'):
                cmd_i = cmd_i + ' -t_srs "EPSG:%s"' %(epsg)

        if (not resolution == None) and (not resolution == 'None'):
                cmd_i = cmd_i + ' -tr %s %s' %(resolution,resolution)

        if nodata == True:
                novalue = formattools.readnodata(inputfile)
                cmd_i = cmd_i + ' -srcnodata %s -dstnodata %s' % (novalue,novalue)
                
        if not roi == None: 
                lon, lat = roi.exterior.xy 
                lonmin = np.min(lon)
                lonmax = np.max(lon)
                latmin = np.min(lat)
                latmax = np.max(lat)
                cmd_i = cmd_i + ' -te %f %f %f %f -te_srs EPSG:4326' % (lonmin,latmin,lonmax,latmax)

        cmd_i = cmd_i + ' %s %s' % (inputfile,outputfile)
        
        usermessage.ezprint('Run the GDAL command: %s' % (cmd_i),log,verbose) 
        os.system(cmd_i)

        if format == 'GTiff' and (inputfile.endswith('.tif') or inputfile.endswith('.tiff')):
                if platform.system() == 'Windows':
                        keyprg = ''
                else: 
                        keyprg = '.py'
                cmd = 'gdal_edit%s -mo AREA_OR_POINT=%s %s' % (keyprg,
                        formattools.areapointGTiff(inputfile),
                        outputfile,
                )
                os.system(cmd)

        usermessage.ezprint('done.',log,verbose) 