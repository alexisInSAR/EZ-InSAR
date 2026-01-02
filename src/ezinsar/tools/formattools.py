#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module for data format (i.e., Bytes)

    
    (From `ezinsar` package)

Changelog:
        * 3.1.0: Initial version, Apr. 2025

"""

################################################################################
## Python packages
################################################################################
import os
from ezinsar import usermessage, constants
import numpy as np 
import shutil
from osgeo import gdal, osr

################################################################################
def ENVIbyteswap(file,
                hdrfile,
                log = None,
                verbose = True,
                ):
       """Swap byte for ENVI data format"""
       usermessage.openingmsg(__name__,ENVIbyteswap.__name__,__file__,constants.__copyright__,'Byte swap for ENVI dataset',log,verbose)

       datatype = None
       byteorder = None
       bands = None
       samples = None
       lines = None
       with open(hdrfile,'r') as fi: 
              for text in fi.readlines():
                     if 'samples' in text: 
                            samples = int(text.split('=')[-1])
                     if 'lines' in text: 
                            lines = int(text.split('=')[-1])
                     if text.startswith('bands'): 
                            bands = int(text.split('=')[-1])
                     if 'data type' in text: 
                            datatype = int(text.split('=')[-1])
                     if 'byte order' in text: 
                            byteorder = int(text.split('=')[-1])

       if not bands == 1:
              raise ValueError(usermessage.errormsg(__name__,ENVIbyteswap.__name__,__file__,constants.__copyright__,'The function is only compatible with an unique band.',log))
       
       usermessage.ezprint('File: %s.' % (file),log,verbose)  
       usermessage.ezprint('HDR file: %s.' % (hdrfile),log,verbose)  
       usermessage.ezprint('Samples: %s.' % (samples),log,verbose)  
       usermessage.ezprint('Lines: %s.' % (lines),log,verbose)  
       usermessage.ezprint('Byte order: %s.' % (byteorder),log,verbose)  
       usermessage.ezprint('Data type: %s.' % (datatype),log,verbose)  
       
       newbyteorder = abs(byteorder-1)

       usermessage.ezprint('From the Byte order %s to %s' % (byteorder,newbyteorder),log,verbose)  

       shutil.copy(file,file+'.orig')
       shutil.copy(hdrfile,hdrfile+'.orig')

       if datatype == 4: 
              dtype = 'float32'

       data = np.fromfile(file+'.orig', dtype=dtype).reshape(lines,samples).byteswap(inplace=True)
       data.tofile(file)

       with open(hdrfile+'.orig','r') as fi: 
              text = fi.readlines()
       
       with open(hdrfile,'w') as fout: 
              for lines in text:
                     if 'byte order' in lines: 
                            fout.write('byte order = %s\n' % (newbyteorder))   
                     else: 
                            fout.write(lines)                    

       os.remove(hdrfile+'.orig')
       os.remove(file+'.orig')

       usermessage.ezprint('done',log,verbose) 

def readnodata(rasterfile): 
       "Read the nodata value from a raster" 
       
       srs = gdal.Open(rasterfile)
       nodatavalue = srs.GetRasterBand(1).GetNoDataValue()
       if nodatavalue == None: 
              nodatavalue = 0

       srs = None

       return nodatavalue

def areapointGTiff(rasterfile): 
       "Read the areapoint metadata value from a raster" 
       srs = gdal.Open(rasterfile)
       area_or_point = srs.GetMetadata().get('AREA_OR_POINT', 'Area') 
       srs = None
       return area_or_point

def epsg_from_raster(rasterfile): 
       "Read the EPSG code from a raster" 
       dataset = gdal.Open(rasterfile)
       wkt = dataset.GetProjection()
       if not wkt:
              return None
       srs = osr.SpatialReference()
       srs.ImportFromWkt(wkt)
       srs.AutoIdentifyEPSG()
       epsg = srs.GetAuthorityCode(None)
       return int(epsg) if epsg else None

def detectGDALdriver(rasterfile): 
       "Detect the driver type of a raster " 
       ds = gdal.OpenEx(rasterfile)

       if ds.RasterCount > 0 and ds.GetLayerCount() > 0:
              type = 'Raster/Vector'
       elif ds.RasterCount > 0:
              type = 'Raster'
       elif ds.GetLayerCount() > 0:
              type = 'Vector'
       else:
              type = 'None'

       ds = None
       return type
       

