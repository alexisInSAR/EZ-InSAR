#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manage the ezinsardata classes for EZ-InSAR

The module allows to create the EZ-InSAR displacement class using Doris. 
    
    (From `ezinsar` package)

Changelog:
        * 3.2.1: New methods, Alexis Hrysiewicz, Aug. 2025
        * 3.2.0: New methods 
        * 3.1.0: New class for in-situ data, Alexis Hrysiewicz, Mar. 2025
        * 3.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import os
from typing import Optional, Union
from osgeo import gdal, osr
import h5py
import numpy as np
import datetime 
import random
import string
import pandas as pd 
import pyproj
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import shutil
import time 
from shapely.wkt import loads 
from shapely import Polygon

from ezinsar import constants
from ezinsar import usermessage
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Class to manage the displacement class for EZ-InsAR
##      (part of EZ-InSAR)
################################################################################
class displacement:

        ################################################################################
        ## Initialistion of the class
        ################################################################################
        def __init__(self):
                
                """Initilisation of the class
                """        
                # Version information         
                self.version = {'value': '1.0.0',
                        'description': 'Version of the EZ-InSAR data file',
                        'format': 'str'}
        
                # Class
                self.classtype = {'value': 'displacement',
                        'description': 'Class for EZ-InSAR data file',
                        'format': 'str'}

                # Super paramater
                self.mode = {'value': 'LOS',
                        'description': 'Mode of the dataset. Can be LOS (for LOS displacements) or 3D (for vertical and horizontal displacements)',
                        'format': 'str'}

                # Temporal information
                self.dates = {'value': None,
                        'description': 'List of datetime representing the time series sampling',
                        'format': 'np.array'}
                self.n_image = {'value': None,
                        'description': 'Number of images',
                        'format': 'int'}
                self.n_ifg = {'value': None,
                        'description': 'Number of interferograms',
                        'format': 'int'}
                self.date_ref = {'value': None,
                        'description': 'Reference date in datetime',
                        'format': 'datetime'}
                self.ifg_date = {'value': None,
                        'description': 'List of interferograms in YYYYMMDD_YYYYMMDD format',
                        'format': 'np.array'}

                # Spatial information 
                self.lon = {'value': None,
                        'description': 'np.array of longitude coordinates. Vector of float (for scatterer computation)',
                        'format': 'np.array'} 
                self.lat = {'value': None,
                        'description': 'np.array of latitude coordinates. Vector of float (for scatterer computation)',
                        'format': 'np.array'} 
                self.lon_grid = {'value': None,
                        'description': 'np.array of longitude coordinates. Matrix of float (for raster computation)',
                        'format': 'np.array'} 
                self.lat_grid = {'value': None,
                        'description': 'np.array of latitude coordinates. Matrix of float (for raster computation)',
                        'format': 'np.array'}
                self.index_pts = {'value': None,
                        'description': 'np.array of point indexes. Vector of int',
                        'format': 'np.array'}
                self.x_utm = {'value': None,
                        'description': 'np.array of X-meter coordinates. Matrix/vector of float',
                        'format': 'np.array'}
                self.y_utm = {'value': None,
                        'description': 'np.array of Y-meter coordinates. Matrix/vector of float',
                        'format': 'np.array'}
                self.code_meter = {'value': None,
                        'description': 'String of the EPGS code for the meter coordinates',
                        'format': 'str'}

                # Supplemetary information
                self.amp_mean = {'value': None,
                        'description': 'np.array of mean amplitude. Matrix/vector of float',
                        'format': 'np.array'}
                self.hgt = {'value': None,
                        'description': 'np.array of elevation. Vector of float (for scatterer computation)',
                        'format': 'np.array'}
                self.hgt_grid = {'value': None,
                        'description': 'np.array of elevation. Maxtrix of float (for raster computation)',
                        'format': 'np.array'}
                self.heading = {'value': None,
                        'description': 'np.array of heading. Matrix/vector of float',
                        'format': 'np.array'} 
                self.inc_angle = {'value': None,
                        'description': 'np.array of inc_angle. Matrix/vector of float',
                        'format': 'np.array'}
                
                self.radlkU = {'value': None,
                        'description': 'np.array of vertical radarlook. Matrix/vector of float',
                        'format': 'np.array'}
                self.radlkE = {'value': None,
                        'description': 'np.array of hori. EW radarlook. Matrix/vector of float',
                        'format': 'np.array'}
                self.radlkN = {'value': None,
                        'description': 'np.array of hori. NS radarlook. Matrix/vector of float',
                        'format': 'np.array'}

                # Displacement information
                # For LOS
                self.dispLOS = {'value': None,
                        'description': 'LOS displacement np.array [n (number of points) x m (number of dates)] for scatterer computation. LOS displacement np.array [n (number of Y) x m (number of X) x k (number of dates)] for raster computation',
                        'format': 'np.array'}
                self.sigmadispLOS = {'value': None,
                        'description': 'LOS displacement sigma np.array [n (number of points) x m (number of dates)] for scatterer computation. LOS displacement sigma np.array [n (number of Y) x m (number of X) x k (number of dates)] for raster computation',
                        'format': 'np.array'}
                self.rateLOS = {'value': None,
                        'description': 'LOS displacement rate np.array [n (number of points) x 2] for scatterer computation. LOS displacement rate np.array [n (number of Y) x m (number of X) x 2] for raster computation',
                        'format': 'np.array'} 
                self.sigmarateLOS = {'value': None,
                        'description': 'LOS displacement sigma rate np.array [n (number of points) x 2] for scatterer computation. LOS displacement sigma rate np.array [n (number of Y) x m (number of X) x 2] for raster computation',
                        'format': 'np.array'} 

                # For 3D (using the same format)
                self.dispUD = {'value': None,
                        'description': 'UD displacement np.array [n (number of points) x m (number of dates)] for scatterer computation. UD displacement np.array [n (number of Y) x m (number of X) x k (number of dates)] for raster computation',
                        'format': 'np.array'}
                self.sigmadispUD = {'value': None,
                        'description': 'UD displacement sigma np.array [n (number of points) x m (number of dates)] for scatterer computation. UD displacement sigma np.array [n (number of Y) x m (number of X) x k (number of dates)] for raster computation',
                        'format': 'np.array'}
                self.rateUD = {'value': None,
                        'description': 'UD displacement rate np.array [n (number of points) x 2] for scatterer computation. UD displacement rate np.array [n (number of Y) x m (number of X) x 2] for raster computation',
                        'format': 'np.array'} 
                self.sigmarateUD = {'value': None,
                        'description': 'UD displacement sigma rate np.array [n (number of points) x 2] for scatterer computation. UD displacement sigma rate np.array [n (number of Y) x m (number of X) x 2] for raster computation',
                        'format': 'np.array'} 

                self.dispEW = {'value': None,
                        'description': 'EW displacement np.array [n (number of points) x m (number of dates)] for scatterer computation. EW displacement np.array [n (number of Y) x m (number of X) x k (number of dates)] for raster computation',
                        'format': 'np.array'}
                self.sigmadispEW = {'value': None,
                        'description': 'EW displacement sigma np.array [n (number of points) x m (number of dates)] for scatterer computation. EW displacement sigma np.array [n (number of Y) x m (number of X) x k (number of dates)] for raster computation',
                        'format': 'np.array'}
                self.rateEW = {'value': None,
                        'description': 'EW displacement rate np.array [n (number of points) x 2] for scatterer computation. EW displacement rate np.array [n (number of Y) x m (number of X) x 2] for raster computation',
                        'format': 'np.array'} 
                self.sigmarateEW = {'value': None,
                        'description': 'EW displacement sigma rate np.array [n (number of points) x 2] for scatterer computation. EW displacement sigma rate np.array [n (number of Y) x m (number of X) x 2] for raster computation',
                        'format': 'np.array'} 

                self.dispNS = {'value': None,
                        'description': 'NS displacement np.array [n (number of points) x m (number of dates)] for scatterer computation. NS displacement np.array [n (number of Y) x m (number of X) x k (number of dates)] for raster computation',
                        'format': 'np.array'}
                self.sigmadispNS = {'value': None,
                        'description': 'NS displacement sigma np.array [n (number of points) x m (number of dates)] for scatterer computation. NS displacement sigma np.array [n (number of Y) x m (number of X) x k (number of dates)] for raster computation',
                        'format': 'np.array'}
                self.rateNS = {'value': None,
                        'description': 'NS displacement rate np.array [n (number of points) x 2] for scatterer computation. NS displacement rate np.array [n (number of Y) x m (number of X) x 2] for raster computation',
                        'format': 'np.array'} 
                self.sigmarateNS = {'value': None,
                        'description': 'NS displacement sigma rate np.array [n (number of points) x 2] for scatterer computation. NS displacement sigma rate np.array [n (number of Y) x m (number of X) x 2] for raster computation',
                        'format': 'np.array'} 

                # For the reference point 
                self.referencepoint = {'value': {'lon_pt_ref': None, 
                                'lat_pt_ref': None, 
                                'lon_pt_refarea': None, 
                                'lat_pt_refarea': None, 
                                'radius': None, 
                                'rateLOS': None, 
                                'index': None}, 
                                'description': 'Dictionary for the reference point',
                                'format': 'dict'} 

                # For the baselines
                self.bperp = {'value': None,
                        'description': 'np.array of bperp',
                        'format': 'np.array'}
        
                # For the metadata
                self.datainformation = {'Name': None, 
                                'Path': None, 
                                'Target': None, 
                                'InSAR_Processor': None, 
                                'TS_Processor': None, 
                                'Approach': None, 
                                'Satellite': None, 
                                'Mode': None, 
                                'Pass': None, 
                                'Track': None, 
                                'Wavelength': None, 
                                'Date': None, 
                                'Importation': None, 
                                'Processing': None,
                                'Metadata_processing': None}
                
        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def print(self):
                """Print the class attributes"""

                attrs = vars(self)
                print(', '.join("%s: %s" % item for item in attrs.items()))

                return self
        
        def getformat(self): 
                if isinstance(self.lon['value'], np.ndarray):
                        mode = 'pt'
                else: 
                        mode = 'raster'

                return mode 
        
        def extractts(self,xpts,ypts,
                radius = 100,
                epsg = 4326,
                idx_pts = None):
                """Extract the displacement time series for a point, index(es)"""

                if idx_pts == None:  
                        x = self.x_utm['value']
                        y = self.y_utm['value']

                        transformer = pyproj.Transformer.from_crs("epsg:%s" % (epsg), "epsg:%s" % (self.code_meter['value'].split(':')[-1]), always_xy=True)
                        xpts_utm, ypts_utm = transformer.transform(xpts, ypts)
                        normi = np.sqrt((xpts_utm - x)**2 + (ypts_utm - y)**2)
                        idx_pts = np.where(normi<=radius)[0]

                dates = self.dates['value']
                        
                if isinstance(idx_pts,np.ndarray):
                        if idx_pts.size == 0:
                                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,constants.__copyright__,"There is no points closed to this location.",None))
                else:
                        if not idx_pts:
                                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,constants.__copyright__,"There is no points closed to this location.",None))

                if self.getformat() =='pt':
                        ydisp = np.mean(np.atleast_2d(self.dispLOS['value'][idx_pts,:]),axis=0).flatten()
                        try: 
                                sigmaydisp = np.mean(np.atleast_2d(self.sigmadispLOS['value'][idx_pts,:]),axis=0).flatten()
                        except:
                                sigmaydisp = np.ones_like(dates).flatten()*np.nan

                else:   
                        ydisp = []
                        sigmaydisp = []
                        for idxtime in np.arange(0,self.dispLOS['value'].shape[0]):
                                ydisp.append(np.nanmean(np.flipud(self.dispLOS['value'][idxtime,:,:])[idx_pts]))
                        ydisp = np.array(ydisp)

                        try:        
                                for idxtime in np.arange(0,self.dispLOS['value'].shape[0]):
                                        sigmaydisp.append(np.nanmean(np.flipud(self.sigmadispLOSdispLOS['value'][idxtime,:,:])[idx_pts]))
                        except: 
                                sigmaydisp = np.ones_like(dates).flatten()*np.nan

                        ydisp = np.nan_to_num(ydisp,nan=0) ## WHY

                return dates, ydisp, sigmaydisp
        
        def quicklook(self,
                mode='rateLOS',
                cmap = 'jet',
                vmin = 'auto',
                vmax = 'auto',
                vcentered = True,
                title = None,
                plotextent = False,
                returnfig=False):
                """Create a quicklook""" 
                
                if not mode in ['rateLOS','sigmarateLOS']:
                        raise TypeError(usermessage.typeerrormsg(
                                        __name__,__name__,__file__,__copyright__,
                                        'mode',"['rateLOS','sigmarateLOS'",None))

                if isinstance(vmin,str):
                        if not vmin == 'auto':
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,__name__,__file__,__copyright__,
                                        'vmin',"auto or float",None)) 
                else:
                        if not isinstance(vmin,float):
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,__name__,__file__,__copyright__,
                                        'vmin',"auto or float",None)) 
                        
                if isinstance(vmax,str):
                        if not vmax == 'auto':
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,__name__,__file__,__copyright__,
                                        'vmax',"auto or float",None)) 
                else:
                        if not isinstance(vmax,float):
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,__name__,__file__,__copyright__,
                                        'vmax',"auto or float",None)) 

                if not isinstance(vcentered,bool):
                        raise TypeError(usermessage.typeerrormsg(
                                        __name__,__name__,__file__,__copyright__,
                                        'vcentered',"bool",None))

                if not isinstance(self.lon['value'], np.ndarray):
                        dataset = 'raster'
                else: 
                        dataset = 'pts'

                if dataset == 'pts':
                        lon = self.lon['value']
                        lat = self.lat['value']
                else:
                        lon = self.lon_grid['value']
                        lat = self.lat_grid['value']

                if mode == 'rateLOS':
                        namecolorbar = 'LOS Displacement rate [mm/yr]'
                        strtitle = 'Quicklook of LOS Displacement rate'
                        value = self.rateLOS['value']

                elif mode == 'sigmarateLOS':
                        value = self.sigmarateLOS['value']
                        namecolorbar = 'Sigma LOS Displacement rate [mm/yr]'
                        strtitle = 'Quicklook of Sigma LOS Displacement rate'

                if vmax == 'auto':
                        if vcentered:
                                vmax = 0 + 3*np.nanstd(value.flatten())
                        else:
                                vmax = np.nanmean(value.flatten()) + 3*np.nanstd(value.flatten())
                if vmin == 'auto':
                        if vcentered:
                                vmin = 0 - 3*np.nanstd(value.flatten())
                        else:
                                vmin = np.nanmean(value.flatten()) - 3*np.nanstd(value.flatten())
                
                fig, ax = plt.subplots()

                if dataset == 'pts':
                        plt.scatter(lon,lat,
                                c=value,
                                vmin = vmin,
                                vmax = vmax,
                                s = 5,
                                cmap=cmap)
                else:
                        plt.imshow(value,
                                vmin = vmin,
                                vmax = vmax,
                                extent=[np.min(lon),np.max(lon),np.min(lat),np.max(lat)],
                                cmap=cmap)
                
                if plotextent == True: 
                        roi = self.getextent()
                        plt.plot(roi.exterior.xy[0],roi.exterior.xy[1],'--',linewidth=1,color='black')
                
                if title == None:
                        title = strtitle
                plt.title(title)

                cbar = plt.colorbar()
                cbar.set_label(namecolorbar)

                plt.xlabel('Longitude')
                plt.ylabel('Latitude')
                
                if returnfig == False:
                        plt.show()
                else:
                        return fig, ax

        def getextent(self,
                mode = 'ConvexHull', #bbox, ConvexHull
                format = 'shapely',
                idx_pts = None): #shapely, list
                """Extract the extent of the results""" 

                if not isinstance(self.lon['value'], np.ndarray):
                        lon = self.lon_grid['value']
                        lat = self.lat_grid['value']
                else: 
                        lon = self.lon['value']
                        lat = self.lat['value']

                if not idx_pts == None: 
                        lon = lon[idx_pts]
                        lat = lat[idx_pts]

                if mode == 'bbox':
                        roi = loads("POLYGON ((%f %f, %f %f, %f %f, %f %f, %f %f))" % (
                        np.min(lon), np.min(lat),
                        np.max(lon), np.min(lat),
                        np.max(lon), np.max(lat),
                        np.min(lon), np.max(lat),
                        np.min(lon), np.min(lat)))
                elif mode == 'ConvexHull':
                        pts = np.vstack((lon,lat)).T
                        from scipy.spatial import ConvexHull
                        hull = ConvexHull(pts)
                        roi = []
                        for idx in hull.vertices:
                              roi.append((pts[idx, 0], pts[idx, 1]))  
                        roi = Polygon(roi)
                
                if format == 'shapely':
                        return roi
                elif format == 'list':
                        x,y = roi.exterior.xy 
                        return [np.min(x),np.min(y),np.max(x),np.max(y)]
        
        def totif(self,file,
                mode='rateLOS',
                idx = 0, 
                srscode = 4326,
                nodata = 0,
                format = 'COG'): 
                
                if self.getformat == 'pt':
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,constants.__copyright__,"This function is only available for raster format.",None)) 

                raster = eval('self.%s["value"]' % (mode))
                image_size = raster.shape
                
                if len(image_size) == 3: 
                       raster = raster[idx,:,:] 
                       image_size = raster.shape

                nx = image_size[0]
                ny = image_size[1]

                #raster novalue
                raster[np.isnan(raster)] = 0

                xmin, ymin, xmax, ymax = [min(self.lon_grid['value'].flatten()), min(self.lat_grid['value'].flatten()), max(self.lon_grid['value'].flatten()), max(self.lat_grid['value'].flatten())]
                xres = (xmax - xmin) / float(ny)
                yres = (ymax - ymin) / float(nx)
                geotransform = (xmin, xres, 0, ymax, 0, -yres)

                dst_ds = gdal.GetDriverByName('MEM').Create("MEM", ny, nx, 1, gdal.GDT_Float32)
                dst_ds.SetGeoTransform(geotransform)
                srs = osr.SpatialReference() 
                srs.ImportFromEPSG(srscode) 
                dst_ds.SetProjection(srs.ExportToWkt())                         
                dst_ds.GetRasterBand(1).WriteArray(raster)                   
                dst_ds.GetRasterBand(1).SetNoDataValue(nodata)               
                dst_ds.SetMetadata({"AREA_OR_POINT": "Point","TIFFTAG_SOFTWARE": "Created with EZ-InSAR %s %s" % (constants.__version__,constants.__copyright__)})
                                           
                dst_ds.FlushCache()    
                
                driverOpt = []
                out_ds = gdal.Translate(file, dst_ds, format=format, creationOptions=driverOpt,
                                        noData=nodata, outputType=gdal.GDT_Float32)
                out_ds = None
                dst_ds = None # We close the rasters          

################################################################################
## Class to manage the in-situ data class for EZ-InsAR
##      (part of EZ-InSAR)
################################################################################
class insitu:

        ################################################################################
        ## Initialistion of the class
        ################################################################################
        def __init__(self):
                
                """Initilisation of the class
                """        
                # Version information         
                self.version = {'value': '1.0.0',
                        'description': 'Version of the EZ-InSAR in-situ data file',
                        'format': 'str'}
                
                # Class
                self.classtype = {'value': 'insitu',
                        'description': 'Class for EZ-InSAR data file',
                        'format': 'str'}
                
                # Data
                self.data = {'value': None,
                        'description': 'Pandas DataFrame of the data',
                        'format': 'pd.DataFrame'}
                
                # Location
                self.x = {'value': 0,
                        'description': 'Primary location in X (see EPSG code of primary coordinates)',
                        'format': 'float'}
                self.y = {'value': 0,
                        'description': 'Primary location in Y (see EPSG code of primary coordinates)',
                        'format': 'float'}
                self.z = {'value': 0,
                        'description': 'Primary location in Z (see EPSG code of primary coordinates)',
                        'format': 'float'}
                
                self.lon = {'value': 0,
                        'description': 'Secondary location in longitude (EPSG: 4326)',
                        'format': 'float'}
                self.lat = {'value': 0,
                        'description': 'Secondary location in latitude (EPSG: 4326)',
                        'format': 'float'}
                self.hgt = {'value': 0,
                        'description': 'Secondary location in longitude (EPSG: 4326)',
                        'format': 'float'}
                
                ## Metadata
                self.datainformation = {'Name': None, 
                                'Original file': None, 
                                'Short Description': None, 
                                'Long Description': None, 
                                'EPSG_secondary': None, 
                                'Data Header': [], 
                                'Data Unit': [], 
                                }
        
        ################################################################################
        ## Import a .txt file into an EZ-InSAR insitu data file
        ################################################################################
        def readfromtxt(self,
                        file,
                        delimiter: Optional[str] = ';',
                        header: Optional[int] = 0,
                        colnames: Optional[list] = ['Date','Displacement'],
                        dataunits: Optional[list] = ['time','mm'],
                        dateformat: Optional[str] = '%Y-%m-%dT%H:%M:%S.%fZ',
                        location: Optional[list] = [0,0,0],
                        epsg: Optional[int] = 4326,
                        verbose: Optional[bool] = True,
                        log: Optional[bool] = None):
                """Import a text file to create an EZ-InSAR insitu data file

                The function will create an EZ-InSAR insitu data file from a .txt file

                Args:
                        file (str): .txt file
                        delimiter (str): delimiter symbol [Default: ';']
                        header (int): Number of header lines [Default: 0]
                        colnames (list): List of str for row names [Default: ['date','displacement']]
                        dataunits (list): List of str for units [Default: ['time','mm']]
                        dateformat (str): Date format [Default: '%Y-%m-%dT%H:%M:%S.%fZ']
                        location (list): List of float for location [Default: [np.nan, np.nan, np.nan]]
                        epsg (int): EPSG code [Default: 4326]
                        verbose (bool, Optional): verbose [Default: `True`].
                        log (str): Log file [Default: `None`].
                        
                """

                if not isinstance(verbose,bool):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'verbose','True or False',log))
                
                if not log == None: 
                        if not isinstance(log,str): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,__name__,__file__,__copyright__,
                                        'log','str',log))  

                if not isinstance(file,str): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'output','str',log)) 
                if not os.path.isfile(file):
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                'The file %s does not exist.' % (file),log))

                if not isinstance(delimiter,str): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'delimiter','str',log)) 
                
                if not isinstance(header,int): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'header','int',log))
                if header == 0:
                        header = None
                
                if not isinstance(colnames,list): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'colnames','list',log))
                
                for idx, li in enumerate(colnames):
                        if not isinstance(li,str):
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,__name__,__file__,__copyright__,
                                        'colnames','list of str',log)) 
                        else:
                                colnames[idx] = colnames[idx].lower()
                if not colnames[0] == 'date':
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                'The first column must be date.',log))
                
                if not isinstance(dataunits,list): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'dataunits','list',log))
                for idx, li in enumerate(dataunits):
                        if not isinstance(li,str):
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,__name__,__file__,__copyright__,
                                        'dataunits','list of str',log)) 
                        else:
                                dataunits[idx] = dataunits[idx].lower()
                if not dataunits[0] == 'time':
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                'The first unit must be time.',log))
                
                if not isinstance(dateformat,str): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'dateformat','str',log))
                
                if not isinstance(location,list): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'location','list',log))
                for idx, li in enumerate(location):
                        if not isinstance(li,float):
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,__name__,__file__,__copyright__,
                                        'location','list of float',log)) 
                        
                if not isinstance(epsg,int): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'epsg','int',log))
                
                usermessage.openingmsg(__name__,__name__,__file__,__copyright__,'Import a .txt file to create an EZ-InSAR insitu data',log,verbose)

                ## Read the last lines to check the number of columns
                with open(file,'r') as fi:
                        line = fi.readlines()[-1]

                if not len(line.split(delimiter)) == len(colnames):
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                'EZ-InSAR detects %s columns but the colnames variables has %s columns.' % (len(line.split(delimiter)),len(colnames)),log))

                if not len(colnames) == len(dataunits):
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                'EZ-InSAR detects %s columns but the dataunits variables has %s columns.' % (len(colnames),len(dataunits)),log))

                data = pd.read_csv(file,names=colnames, header=header,delimiter=delimiter)

                ## Format the dates
                dates = []
                for di in data['date']:
                        if dateformat == 'decyear':
                                tmp = datetime.datetime(int(di), 1, 1) + datetime.timedelta(days = (di % 1) * 365) # https://stackoverflow.com/questions/20911015/decimal-years-to-datetime-in-python
                        else:
                                tmp = datetime.datetime.strptime(di,dateformat)
                        dates.append(tmp)
                data['date'] = dates

                self.data['value'] = data.sort_values(by='date', ascending=True)

                ## Location
                if not epsg == 4326:
                        self.x['value'] = location[0]
                        self.y['value'] = location[1]
                        self.z['value'] = location[2]
                        self.lon['value'], self.lat['value'] = pyproj.Transformer.from_crs('epsg:%s','epsg:4326' % (epsg),always_xy=True).transform(location[0],location[1])
                        self.hgt['value'] = location[2]
                else:
                        self.lon['value'] = location[0]
                        self.lat['value'] = location[1]
                        self.hgt['value'] = location[2]
                        self.x['value'] = location[0]
                        self.y['value'] = location[1]
                        self.z['value'] = location[2]

                ## Constructor
                self.datainformation = {'Name': file.split(os.sep)[-1], 
                                'Original file': file, 
                                'Short Description': 'Unknown', 
                                'Long Description': 'Unknown', 
                                'EPSG_primary': epsg, 
                                'Data Header': colnames, 
                                'Data Unit': dataunits, 
                                }
                
        ################################################################################
        ## Method to print the attributes
        ################################################################################
        def print(self):
                """Print the class attributes"""

                attrs = vars(self)
                print(', '.join("%s: %s" % item for item in attrs.items()))

                return self
        
        def extract(self):
                """Extrac the time series values into numpy array"""
                t = [x.to_pydatetime() for x in self.data['value']['date'].to_list()]
                y = np.array(self.data['value']['displacement'].to_list())
                sy = np.ones_like(y)*np.nan
                
                return t, y, sy

################################################################################
## Save an EZ-InSAR dataset into a file (h5 format)
################################################################################
def saveEZdata(dataset, 
        output,
        verbose: Optional[bool] = True,
        log: Optional[bool] = None):
        """Save an EZ-InSAR dataset into a file 

        The function will save an EZ-InSAR dataset into a h5 file.

        Args:
                dataset (any): EZ-InSAR data class
                output (str): Full path of the output file
                verbose (bool, Optional): verbose [Default: `True`].
                log (str): Log file [Default: `None`].
                
        """
        cur_dir = os.getcwd()

        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,saveEZdata.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if not log == None: 
                if not isinstance(log,str): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,saveEZdata.__name__,__file__,__copyright__,
                                'log','str',log))  

        if not isinstance(output,str): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,saveEZdata.__name__,__file__,__copyright__,
                        'output','str',log))  
        
        usermessage.openingmsg(__name__,saveEZdata.__name__,__file__,__copyright__,'Save an EZ-InSAR dataset.',log,verbose)

        ################################################################################
        ## For the version 1.0.0 of EZ-InSAR displacement class
        ################################################################################
        if dataset.version['value'] == '1.0.0' and ('displacement' in (str(type(dataset)))): 
                usermessage.ezprint('Write the file %s regarding the EZ-InSAR displacement dataset format %s...' % (os.path.abspath(output),dataset.version['value']),log,verbose)

                with h5py.File(output, "w") as f:
                        dset = f.create_dataset('version', data = dataset.version['value'], shape=1, dtype=h5py.string_dtype())
                        dset.attrs['format'] = dataset.version['format']
                        dset.attrs['description'] = dataset.version['description']

                        attrs = vars(dataset)
                        h = 0 
                        for item in attrs.items(): 
                                if not item[0] in ['version','referencepoint','datainformation']: 
                                        a = eval('dataset.%s' % (item[0]))

                                        # Modification of value for datetime.datetime
                                        if item[0] == 'date_ref':  
                                                a['value'] = a['value'].strftime('%Y-%m-%dT%H:%M:%S.%fZ') 
                                        elif item[0] == 'dates':
                                                b = []
                                                for di in a['value']: 
                                                        b.append(di.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
                                                a['value'] = b

                                        if not a['value'] is None: 
                                                exec("dset%s = f.create_dataset('%s', data = a['value'])" % (h,item[0]))
                                                exec("dset%s.attrs['format'] = a['format']" % (h))
                                                exec("dset%s.attrs['description'] = a['description']" % (h))

                                        h = h + 1

                        ## Write the reference point 
                        grpref = f.create_group("referencepoint", track_order=True)
                        for ki in dataset.referencepoint['value'].keys(): 
                                grpref.attrs[ki] = dataset.referencepoint['value'][ki]

                        ## Write the metadata
                        grpmeta = f.create_group("datainformation", track_order=True)
                        for ki in dataset.datainformation.keys():
                                if not dataset.datainformation[ki] is None: 
                                        grpmeta.attrs[ki] = dataset.datainformation[ki]

                usermessage.ezprint('\tdone',log,verbose)

        ################################################################################
        ## For the version 1.0.0 of EZ-InSAR insitu class
        ################################################################################
        elif dataset.version['value'] == '1.0.0' and ('insitu' in (str(type(dataset)))): 
                usermessage.ezprint('Write the file %s regarding the EZ-InSAR displacement insitu format %s...' % (os.path.abspath(output),dataset.version['value']),log,verbose)

                tmp=[]
                for idx, di in enumerate(dataset.data['value']['date']):
                        # tmp.append(di.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
                        tmp.append(di.timestamp())
                dataset.data['value']['date'] = tmp
                dataset.data['value'] = dataset.data['value'].to_numpy()

                with h5py.File(output, "w") as f:
                        dset = f.create_dataset('version', data = dataset.version['value'], shape=1, dtype=h5py.string_dtype())
                        dset.attrs['format'] = dataset.version['format']
                        dset.attrs['description'] = dataset.version['description']

                        attrs = vars(dataset)
                        h = 0 
                        for item in attrs.items(): 
                                 if not item[0] in ['version','datainformation']: 
                                        a = eval('dataset.%s' % (item[0]))

                                        if not a['value'] is None: 
                                                exec("dset%s = f.create_dataset('%s', data = a['value'])" % (h,item[0]))
                                                exec("dset%s.attrs['format'] = a['format']" % (h))
                                                exec("dset%s.attrs['description'] = a['description']" % (h))

                                        h = h + 1

                        ## Write the metadata
                        grpmeta = f.create_group("datainformation", track_order=True)
                        for ki in dataset.datainformation.keys():
                                if not dataset.datainformation[ki] is None: 
                                        grpmeta.attrs[ki] = dataset.datainformation[ki]

                usermessage.ezprint('\tdone',log,verbose)

        else: 
                ########################################################################################
                ## Error
                ########################################################################################
                raise ValueError(usermessage.errormsg(__name__,saveEZdata.__name__,__file__,__copyright__,
                        'The given dataset format is not compatible with the saveEZdata function.',log))

################################################################################
## Load an EZ-InSAR dataset from a file
################################################################################
def loadEZdata(input,
        mode: Optional[str] = 'displacement',
        partialreading: Optional[list] = ['all'], 
        verbose: Optional[bool] = True,
        log: Optional[bool] = None):
        """Load an EZ-InSAR dataset from a file 

        The function will load an EZ-InSAR dataset from a h5 file.

        Args:
                input (str): Data file
                mode (str): Mode of the EZ-InSAR data class. Can be displacement.        
                verbose (bool, Optional): verbose [Default: `True`].
                log (str): Log file [Default: `None`].

        Returns:
                any: EZ-InSAR data class
        
        """
        cur_dir = os.getcwd()

        if not os.path.isfile(input): 
                raise ValueError(usermessage.errormsg(__name__,loadEZdata.__name__,__file__,__copyright__,
                                'The file does not exist.',log)) 

        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,loadEZdata.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if not log == None: 
                if not isinstance(log,str): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,loadEZdata.__name__,__file__,__copyright__,
                                'log','str',log))  

        if not mode in ['displacement','insitu']: 
                raise TypeError(usermessage.typeerrormsg(
                                __name__,loadEZdata.__name__,__file__,__copyright__,
                                'mode','"displacement" or "insitu"',log))  

        usermessage.openingmsg(__name__,loadEZdata.__name__,__file__,__copyright__,'Load an EZ-InSAR dataset.',log,verbose)

        with h5py.File(input, "r") as f:
                
                ############################################################
                ## For the version 1.0.0 of DISPLACEMENT
                ############################################################
                if list(f['version'])[0].decode('UTF-8') == '1.0.0' and mode == 'displacement': 

                        # Initialisation
                        dataset = displacement()
                        dataset.version['value'] = '1.0.0' # Change the version 

                        # Reading of the matrix data
                        for ki in f.keys():
                                if not ki in ['version','datainformation','referencepoint']: 
                                        if partialreading[0] == 'all' or ki in partialreading:
                                                if f[ki].dtype == 'object':
                                                        if len(f[ki].shape) == 0:
                                                                out = f[ki][()].decode('UTF-8')

                                                                if ki == 'date_ref': 
                                                                        out = datetime.datetime.strptime(out,'%Y-%m-%dT%H:%M:%S.%fZ'), 
                                                        else:
                                                                if ki == 'dates':
                                                                        outlist = []
                                                                        for di in f[ki][()]: 
                                                                                outlist.append(datetime.datetime.strptime(di.decode('UTF-8'),'%Y-%m-%dT%H:%M:%S.%fZ'))
                                                                        out = outlist
                                                else:   
                                                        out = f[ki][()]

                                                exec("dataset.%s['value'] = out" % (ki))
                                
                        # For referencepoint
                        if partialreading[0] == 'all' or 'referencepoint' in partialreading:
                                for attri in f['referencepoint'].attrs.keys():
                                        exec("dataset.referencepoint['%s'] = f['referencepoint'].attrs['%s']" % (attri,attri))

                        # For datainformation
                        if partialreading[0] == 'all' or 'datainformation' in partialreading:
                                for attri in f['datainformation'].attrs.keys():
                                        exec("dataset.datainformation['%s'] = f['datainformation'].attrs['%s']" % (attri,attri))

                        # Read the metadata
                        if partialreading[0] == 'all' or 'metadata' in partialreading:
                                import ezinsar.job as ez
                                tmpfile = constants.__cachedir__+os.sep+'jobtmp_'+''.join(random.choice(string.ascii_lowercase) for i in range(16))+'.ei'
                                with open(tmpfile,'w') as fout:
                                        for li in dataset.datainformation['Metadata_processing']:
                                                fout.write(li)
                                try: 
                                        jobtmp = ez.load(tmpfile,verbose=False)
                                except:
                                        usermessage.warningmsg(__name__,loadEZdata.__name__,__file__,'No metadata stored.',log,verbose)
                                        jobtmp = 'None'

                                if os.path.isfile(tmpfile): 
                                        os.remove(tmpfile)

                                dataset.datainformation['Metadata_processing'] = jobtmp 

                ############################################################
                ## For the version 1.0.0 of insitu
                ############################################################
                elif list(f['version'])[0].decode('UTF-8') == '1.0.0' and mode == 'insitu': 

                        # Initialisation
                        dataset = insitu()
                        dataset.version['value'] = '1.0.0' # Change the version 

                        # Reading of the matrix data
                        for ki in f.keys():
                                if not ki in ['version','datainformation']: 
                                        if partialreading[0] == 'all' or ki in partialreading:
                                                if f[ki].dtype == 'object':
                                                        if len(f[ki].shape) == 0:
                                                                out = f[ki][()].decode('UTF-8')
                                                else:   
                                                        out = f[ki][()]

                                                exec("dataset.%s['value'] = out" % (ki))
                                
                   
                        # For datainformation
                        if partialreading[0] == 'all' or 'datainformation' in partialreading:
                                for attri in f['datainformation'].attrs.keys():
                                        exec("dataset.datainformation['%s'] = f['datainformation'].attrs['%s']" % (attri,attri))

                        if partialreading[0] == 'all' or 'data' in partialreading:
                                tmpdata = pd.DataFrame(dataset.data['value'],columns=dataset.datainformation['Data Header'])
                                tmp = []
                                for idx, di in enumerate(tmpdata['date']):
                                        tmp.append(datetime.datetime.fromtimestamp(di))
                                tmpdata['date'] = tmp
                                dataset.data['value'] = tmpdata
                                
                else: 
                        ####################
                        ## Error
                        ####################
                        raise ValueError(usermessage.errormsg(__name__,loadEZdata.__name__,__file__,__copyright__,
                                'The given file is not compatible with the loadEZdata function.',log))

        return dataset

################################################################################
## Export an EZ-InSAR data file into a vector format
################################################################################
def exportEZdata(input,
        output,
        variable: Optional[str] = ['rateLOS','sigmarateLOS','dispLOS'], 
        format: Optional[str] = 'ESRI Shapefile', 
        epgs: Optional[int] = 4326,
        roi: Optional[any] = None,   
        verbose: Optional[bool] = True,
        log: Optional[bool] = None):
        """Export an EZ-InSAR data file into a vector format

        The function will export an EZ-InSAR dataset. 

        Args:
                input (str): Data file
                mode (str): Mode of the EZ-InSAR data class. Can be displacement.        
                verbose (bool, Optional): verbose [Default: `True`].
                log (str): Log file [Default: `None`].
        
        """
        start = time.time()

        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,exportEZdata.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if not log == None: 
                if not isinstance(log,str): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,exportEZdata.__name__,__file__,__copyright__,
                                'log','str',log))  

        usermessage.openingmsg(__name__,exportEZdata.__name__,__file__,__copyright__,'Export an EZ-InSAR data file into a vector format.',log,verbose)

        usermessage.ezprint('Dataset: %s' % (input.datainformation['Name']),log,verbose)

        if not isinstance(input.lon['value'], np.ndarray):
                dataset = 'raster'
        else: 
                dataset = 'pts'
        usermessage.ezprint('Mode of the dataset: %s' % (dataset),log,verbose)
        if dataset == 'raster': 
                raise ValueError(usermessage.errormsg(__name__,exportEZdata.__name__,__file__,__copyright__,
                                'Raster dataset is not compatible with this function. The feature will be added soon.',log))

        ## FOR THE POINT DATASET
        if dataset == 'pts':
                if not format in ['CSV','ESRI','ESRI Shapefile','GeoJSON','XLSX']: 
                        raise TypeError(usermessage.typeerrormsg(
                                        __name__,exportEZdata.__name__,__file__,__copyright__,
                                        'mode',"['CSV','ESRI Shapefile','GeoJSON','XLSX']",log)) 
                usermessage.ezprint('Format: %s' % (format),log,verbose)

                if not isinstance(epgs,int):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,exportEZdata.__name__,__file__,__copyright__,
                                'epgs','int',log))
                usermessage.ezprint('EPSG code: %s' % (epgs),log,verbose)

                if not isinstance(variable,list):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,exportEZdata.__name__,__file__,__copyright__,
                                'variable','list',log))
                
                for li in variable: 
                        if not li in ['rateLOS','sigmarateLOS','dispLOS']: 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,exportEZdata.__name__,__file__,__copyright__,
                                        'variable',"['rateLOS','sigmarateLOS','dispLOS']",log))
                usermessage.ezprint('Variable(s): %s' % (variable),log,verbose)

                # Create the matrix
                usermessage.ezprint('Create the matrix of data:...',log,verbose)
                header = []

                MATDATA = input.lon['value']
                header.append('Longitude')
                MATDATA = np.vstack((MATDATA,input.lat['value']))
                header.append('Latitude')

                if 'rateLOS' in variable: 
                        if isinstance(input.rateLOS['value'], np.ndarray):
                                MATDATA = np.vstack((MATDATA,input.rateLOS['value']))
                                header.append('rateLOS')
                        else: 
                                raise ValueError(usermessage.errormsg(__name__,exportEZdata.__name__,__file__,__copyright__,
                                        'rateLOS is not available in the dataset.',log))

                if 'sigmarateLOS' in variable: 
                        if isinstance(input.sigmarateLOS['value'], np.ndarray):
                                MATDATA = np.vstack((MATDATA,input.sigmarateLOS['value']))
                                header.append('sigmarateLOS')
                        else: 
                                raise ValueError(usermessage.errormsg(__name__,exportEZdata.__name__,__file__,__copyright__,
                                        'sigmarateLOS is not available in the dataset.',log))
                        
                if 'dispLOS' in variable: 
                        if isinstance(input.dispLOS['value'], np.ndarray):
                                for idx, di in enumerate(input.dates['value']): 
                                        MATDATA = np.vstack((MATDATA,input.dispLOS['value'][:,idx]))
                                        header.append('D%s' % (di.strftime('%Y%m%d')))
                        else: 
                                raise ValueError(usermessage.errormsg(__name__,exportEZdata.__name__,__file__,__copyright__,
                                        'dispLOS is not available in the dataset.',log))        

                MATDATA = MATDATA.T

                if not epgs == 4326: 
                        import pyproj

                        latlon_to_meter = pyproj.Transformer.from_crs('epsg:4326','epsg:%s' % (epgs))
                        x,y = latlon_to_meter.transform(MATDATA[:,1],MATDATA[:,0])
                        MATDATA[:,0] = x
                        MATDATA[:,1] = y 
                        header[0] = 'X'
                        header[1] = 'Y'

                usermessage.ezprint('\tdone',log,verbose)

                ## Clipping 
                if not roi == None: 
                        from matplotlib import path
                        ROIpoly= path.Path(list(zip(roi.exterior.xy[0],roi.exterior.xy[1])))
                        LONLAT = np.dstack((MATDATA[:,0], MATDATA[:,1])).reshape((-1, 2))
                        idxselected = np.where(ROIpoly.contains_points(LONLAT) == True)[0]
                        MATDATA = MATDATA[idxselected,:]

                # Conversion
                usermessage.ezprint('Convert to pandas dataframe:...',log,verbose)
                df = pd.DataFrame(MATDATA,columns=header)
                usermessage.ezprint('\tdone',log,verbose)

                usermessage.ezprint('Cache the file:...',log,verbose)
                df.to_csv(constants.__cachedir__+os.sep+'tmp.csv',index=False,sep=';')
                usermessage.ezprint('\tdone',log,verbose)

                usermessage.ezprint('Conversion of the file in the correct format:...',log,verbose)    

                if not format == 'CSV':

                        # Write the VRT 
                        with open(constants.__cachedir__+os.sep+'tmp.vrt','w') as fout: 
                                fout.write('<OGRVRTDataSource>\n')
                                fout.write('\t<OGRVRTLayer name="tmp">\n')
                                fout.write('\t\t<SrcDataSource>%s</SrcDataSource>\n' % (constants.__cachedir__+os.sep+'tmp.csv'))
                                fout.write('\t\t<LayerSRS>EPSG:%s</LayerSRS>\n' % (epgs))
                                fout.write('\t\t<GeometryType>wkbPoint</GeometryType>\n')

                                for idx,hi in enumerate(header):
                                        fout.write('\t\t<Field name="%s" type="Real"/>\n' % (hi))
                                
                                fout.write('\t\t<GeometryField encoding="PointFromColumns" x="%s" y="%s"/>\n' % (header[0],header[1]))
                                fout.write('\t</OGRVRTLayer>\n')
                                fout.write('</OGRVRTDataSource>\n')

                        cmdi = "ogr2ogr -of '%s' -s_srs EPSG:%s -t_srs EPSG:%s -oo HEADERS=YES -oo SEPARATOR=SEMICOLON %s %s -overwrite" % (
                                format,
                                epgs,
                                epgs,
                                output, 
                                constants.__cachedir__+os.sep+'tmp.vrt',
                                )
                        usermessage.ezprint('\t\tThe command will be: %s' % (cmdi),log,verbose)
                        status = os.system(cmdi)
                        if not status == 0: 
                                raise ValueError(usermessage.errormsg(__name__,exportEZdata.__name__,__file__,__copyright__,
                                        'Error during the GDAL command.',log))    
                        
                        if os.path.isfile(constants.__cachedir__+os.sep+'tmp.vrt'):
                                os.remove(constants.__cachedir__+os.sep+'tmp.vrt')

                else: 
                        shutil.copy(constants.__cachedir__+os.sep+'tmp.csv',output)

                usermessage.ezprint('\tdone',log,verbose)

                if os.path.isfile(constants.__cachedir__+os.sep+'tmp.csv'):
                        os.remove(constants.__cachedir__+os.sep+'tmp.csv')

        usermessage.ezprint('\nPerformed in %0.3f seconds' % (time.time()-start),log,verbose)