#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module for geocoding of SAR/InSAR products for EZ-InSAR

The module stores the different functions to interpolate the SAR/InSAR products into a DEM coordinates. These functions are required for ISCE-2 and Doris. These functions use GDAL.
    
    (From `ezinsar` package)

Changelog:
        * 3.2.0: Add the masking based on a masked DEM in DEM geometry, Jun. 2025, Alexis Hrysiewicz
        * 3.1.0: Fix regarding the AREA_OR_PIXEL metadata and documentation added, Feb. 2024, Alexis Hrysiewicz
        * 3.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
from osgeo import gdal, osr
import numpy as np
import scipy 
from typing import Optional, Union
import os 
import glob
from scipy.interpolate.interpnd import _ndim_coords_from_arrays
from scipy.spatial import cKDTree

from ezinsar import usermessage
from ezinsar import constants
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""
################################################################################
## Interpolation of InSAR products into a DEM grid
################################################################################
def rdr2geotiff(
        InSARfile, 
        latitudefile,
        longitudefile, 
        outputfile, 
        dx, 
        dy, 
        processor: Optional[str] = 'isce2',
        mode: Optional[str] = 'auto',
        ROIpoly: Optional[Union[any,None]] = None, 
        interpmethod: Optional[str] = 'nearest',
        format: Optional[str] = 'GTiff', 
        srscode: Optional[int] = 4326,
        uchar: Optional[bool] = True, 
        nodata: Optional[Union[int,float]] = 0,
        colormap: Optional[str] = 'auto',
        coherencefile: Optional[Union[str,None]] = None,
        demradarfile: Optional[Union[str,None]] = None,
        demgeofile: Optional[Union[str,None]] = None,
        coherenceth: Optional[float] = 0.2,
        shadowfile: Optional[Union[None, str]] = None, 
        nblineinput: Optional[Union[int,None]] = None,
        nbcolinput: Optional[Union[int,None]] = None,
        verbose: Optional[bool] = True, 
        log: Optional[Union[str,None]] = None,
        ):
        """Geocoding of SAR/InSAR products onto a regular DEM grid 

        The function will geocode the SAR/InSAR products based on the longitude and latitude files. Used by ISCE-2 and Doris. 

        This function is used by EZ-InSAR to geocode any InSAR images produced by Doris and ISCE-2. Indeed, the processors only generate the latitude and longitude grids. Here, the scripts in used to interpolate the results onto a regular-gridded GTiff image. Users requires to give some files (i.e., latitude and longitude grids, interfograms, etc.) and some other files (i.e., coherence) in order to mask the images. The detection of InSAR-result types (i.e., interferogram, unwrapped images, coherence) is automatic because it is based on the file name. However, the user can force the used mode. 

        The algorithm first generates a regular grid based on the ROI (or the DEM) extents. The coordinates are moved by a half pixel because InSAR observes the pixel centre, which is not compatible with the AREA_OR_PIXEL=Area metadata. Then the function interpolates the InSAR productes according to the user input parameters. The interferograms are interpolated using the complex pixel values. A max. distance parameter is used by default to avoid over-interpolations: 3 times the pixel size. Finally, the images are stored in GTiff format (in float or uchar). If the uchar images are created, a colormap is added into GTiff files. 

        Args:
                InSARfile (str): Full path of the SAR/InSAR file (can be an interferogram or coherence image) 
                latitudefile (str): Full path of the latitude file
                longitudefile (str): Full path of the longitude file
                outputfile (str): Full path of the output file
                dx (int or float): Delta lontitude (or meter)
                dy (int or float): Delta latitude (or meter)
                processor (str, Optional): InSAR processor. [Default: ``isce2``]. 
                mode (str, Optional): Mode of the geocoding. Can be ifg, coh, unw or auto. If auto, the mode will be detected. [Default: ``auto``]. 
                ROIpoly (any, Optional): Shapely polygon of the Region of Interest. [Default: `None`]. If `None`, the full grid will be geocoded.
                interpmethod (str, Optional): Method of interpolation. Can be nearest or linear or cubic. [Default: ``linear``]. 
                format (str, Optional): Format of the output file, (see GDAL driver). [Default: ``GTiff``].         
                srscode (str, Optional): EPSG code of the used coordinate system. [Default: ``4326``].   
                uchar (bool, Optional): UCHAR format, i.e., an colormap will be applied for easier visualisation. Can be True or False. This format is not available for unwrapped interferogram. [Default: `True`]. 
                nodata (int or float, Optional): Value for the non-data. [Default: ``0``]. 
                colormap (str, Optional): Colormap used by the uchar file. Can be a colormap name or auto. If auto, the colormap will be sar for the ifgs and gray for coherence. Only valid for GTiff. [Default: ``auto``]. 
                coherencefile (str): Coherence file to mask the images. If `None`, no masking will be applied. [Default: `None`].
                shadowfile (str): Shadow/layover file to mask the images. If `None`, no masking will be applied. [Default: `None`].
                demradarfile (str): DEM radar required by Doris to mask the NaN values. If None, no masking will be applied. [Default: `None`].
                demgeofile (str): DEM file to mask the NaN values. If None, no masking will be applied. [Default: `None`].
                coherenceth (float, Optional): Coherence threshold for masking. [Default: ``0.5``].
                nblineinput (int, Optional): Number of rows. Needed by Doris. [Default: `None`].
                nbcolinput (int, Optional): Number of columns. Needed by Doris. [Default: `None`].
                verbose (bool, Optional): verbose [Default: `True`].
                log (str): Log file [Default: `None`].

        """

        ## Check the input parameters
        if not os.path.isfile(InSARfile):
                raise ValueError(usermessage.errormsg(__name__,rdr2geotiff.__name__,__file__,__copyright__,
                                'The InSARfile %s does not exist.' % (InSARfile),log))
        if not os.path.isfile(latitudefile):
                raise ValueError(usermessage.errormsg(__name__,rdr2geotiff.__name__,__file__,__copyright__,
                                'The latitudefile does not exist.',log))
        if not os.path.isfile(longitudefile):
                raise ValueError(usermessage.errormsg(__name__,rdr2geotiff.__name__,__file__,__copyright__,
                                'The longitudefile does not exist.',log))

        if not processor in ['isce2','doris']:
                raise TypeError(usermessage.typeerrormsg(
                        __name__,rdr2geotiff.__name__,__file__,__copyright__,
                        'processor','isce2 or doris',log))
        
        if not mode in ['auto','ifg','unw','coh']:
                raise TypeError(usermessage.typeerrormsg(
                        __name__,rdr2geotiff.__name__,__file__,__copyright__,
                        'mode',"'auto','ifg','unw','coh'",log))

        if not interpmethod in ['linear','nearest','cubic']:
                raise TypeError(usermessage.typeerrormsg(
                        __name__,rdr2geotiff.__name__,__file__,__copyright__,
                        'interpmethod',"'linear','nearest'",log))
        
        if not format in ['GTiff']:
                raise TypeError(usermessage.typeerrormsg(
                        __name__,rdr2geotiff.__name__,__file__,__copyright__,
                        'format',"'GTiff'",log))

        if not isinstance(uchar,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,rdr2geotiff.__name__,__file__,__copyright__,
                        'uchar','True or False',log))

        if not (isinstance(nodata,int) or isinstance(nodata,float)):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,rdr2geotiff.__name__,__file__,__copyright__,
                        'nodata','int or float',log))
        
        list_colormap = []
        for li in glob.glob(os.path.dirname(__file__)+os.sep+'colormap'+os.sep+'*.csv'): 
                list_colormap.append(li.split(os.sep)[-1].split('.')[0].replace('cmap_',''))
        if not colormap == 'auto':
                if not colormap in list_colormap: 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,rdr2geotiff.__name__,__file__,__copyright__,
                                'colormap','%s' % (list_colormap),log))

        if (not coherencefile == None) and (not os.path.isfile(coherencefile)):
                raise ValueError(usermessage.errormsg(__name__,rdr2geotiff.__name__,__file__,__copyright__,
                                'The coherence file does not exist.',log))
    
        if not isinstance(coherenceth,float):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,rdr2geotiff.__name__,__file__,__copyright__,
                        'coherenceth','float',log))
        
        if (not shadowfile == None) and (not os.path.isfile(shadowfile)):
                raise ValueError(usermessage.errormsg(__name__,rdr2geotiff.__name__,__file__,__copyright__,
                                'The shadow file does not exist.',log))
        
        if processor == 'doris': 
                if not isinstance(nblineinput,int):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,rdr2geotiff.__name__,__file__,__copyright__,
                                'nblineinput','int',log))
                if not isinstance(nbcolinput,int):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,rdr2geotiff.__name__,__file__,__copyright__,
                                'nbcolinput','int',log))

        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,rdr2geotiff.__name__,__file__,__copyright__,
                        'verbose','True or False',log))

        usermessage.openingmsg(__name__,rdr2geotiff.__name__,__file__,__copyright__,'Geocoding of SAR/InSAR products',log,verbose)

        ## Detection of mode
        if mode == 'auto': 
                usermessage.ezprint('Detection of mode:',log,verbose) 
                if ('int' in InSARfile.split(os.sep)[-1]) or ('diff' in InSARfile.split(os.sep)[-1]): 
                        mode = 'ifg'
                elif ('coh' in InSARfile.split(os.sep)[-1]) or ('cor' in InSARfile.split(os.sep)[-1]) or ('cc' in InSARfile.split(os.sep)[-1]): 
                        mode = 'coh'
                else: 
                        mode = 'unw'

                usermessage.ezprint('\tdone',log,verbose) 
        
        ## Display the file parameters for the user
        usermessage.ezprint('File parameters:',log,verbose) 
        usermessage.ezprint('\tSRS: EPSG:%d' % (srscode),log,verbose) 
        usermessage.ezprint('\tLongitude file: %s' % (longitudefile),log,verbose) 
        usermessage.ezprint('\tLatitude file: %s' % (latitudefile),log,verbose) 
        usermessage.ezprint('\tInput file: %s' % (InSARfile),log,verbose) 
        usermessage.ezprint('\tOuput file: %s' % (outputfile),log,verbose) 
        usermessage.ezprint('\tMode: %s' % (mode),log,verbose) 
        usermessage.ezprint('\tProcessor: %s' % (processor),log,verbose) 

        ## Read the files 
        usermessage.ezprint('Read the input files:',log,verbose) 
        if processor == 'isce2': 
                # Read the latitude file
                filat = gdal.Open(latitudefile) 
                lat = filat.GetRasterBand(1).ReadAsArray()
                filat = None

                ## Read the longitude file
                filon = gdal.Open(longitudefile)
                lon = filon.GetRasterBand(1).ReadAsArray()
                filon = None

                ## Read the ifg
                fidata = gdal.Open(InSARfile)
                if mode == 'unw': 
                        datainput = fidata.GetRasterBand(2).ReadAsArray()
                else: 
                        datainput = fidata.GetRasterBand(1).ReadAsArray()
                fidata = None

                datainput[datainput == 0] = np.nan
                datainput[lat == 0] = np.nan
                datainput[lon == 0] = np.nan

                if not coherencefile == None: 
                        ficoh = gdal.Open(coherencefile)
                        coh = ficoh.GetRasterBand(1).ReadAsArray()
                        ficoh = None
                        usermessage.ezprint('\tMasking based on the file: %s\n\tand a threshold of %s' % (coherencefile,coherenceth),log,verbose) 
                        datainput[(coherenceth>=coh)] = np.nan

                if not shadowfile == None:
                        fishadow = gdal.Open(shadowfile)
                        shadow = fishadow.GetRasterBand(1).ReadAsArray()
                        fishadow = None
                        usermessage.ezprint('\tMasking based on the shadow file: %s' % (shadowfile),log,verbose) 
                        datainput[(shadow>=1)] = np.nan

                if not demradarfile == None:
                        fidem = gdal.Open(demradarfile)
                        dem = fidem.GetRasterBand(1).ReadAsArray()
                        fidem = None
                        usermessage.ezprint('\tMasking based on the dem file: %s' % (demradarfile),log,verbose) 
                        datainput[(dem<=-450)] = np.nan #Auto correction
                        datainput[(abs(dem)<=1e-3)] = np.nan
                        datainput[(dem==0)] = np.nan

        elif processor == 'doris':
                nbl = nblineinput
                nbc = nbcolinput

                # Read the latitude file
                with open(latitudefile,"rb") as fi:
                        lat = np.reshape(np.fromfile(fi, np.float32),(nbl,nbc))

                ## Read the longitude file
                with open(longitudefile,"rb") as fi:
                        lon = np.reshape(np.fromfile(fi, np.float32),(nbl,nbc))

                ## Read the ifg
                with open(InSARfile,"rb") as fi:
                        if mode == 'ifg': 
                                datainput = np.reshape(np.fromfile(fi, np.complex64),(nbl,nbc))
                        elif mode == 'unw':
                                unw = np.reshape(np.fromfile(fi, np.float32),(nbl,nbc))
                                datainput = unw
                        else:
                                
                                datainput = np.reshape(np.fromfile(fi, np.float32),(nbl,nbc))
                
                datainput[datainput == 0] = np.nan
                datainput[lat == 0] = np.nan
                datainput[lon == 0] = np.nan

                if not demradarfile == None: 
                        with open(demradarfile,"rb") as fi:
                                dem = np.reshape(np.fromfile(fi, np.float32),(nbl,nbc))
                        usermessage.ezprint('\tMasking of the NaN-value of the DEM',log,verbose) 
                        datainput[(dem==0)] = np.nan

                if not coherencefile == None: 
                        with open(coherencefile,"rb") as fi:
                                coh = np.reshape(np.fromfile(fi, np.float32),(nbl,nbc))
                        coh[coh==0] = np.nan
                        usermessage.ezprint('\tMasking based on the file: %s\n\tand a threshold of %s' % (coherencefile,coherenceth),log,verbose) 
                        datainput[(coherenceth>=coh)] = np.nan

        usermessage.ezprint('\tdone',log,verbose) 

        ## Grid generation 
        usermessage.ezprint('Generation of the grid:',log,verbose) 

        if not ROIpoly == None:
                lat_vec = np.arange(np.min(ROIpoly.exterior.xy[1]),np.max(ROIpoly.exterior.xy[1]),dy)
                lon_vec = np.arange(np.min(ROIpoly.exterior.xy[0]),np.max(ROIpoly.exterior.xy[0]),dx)
        else:
                lat_vec = np.arange(np.nanmin(lat),np.nanmax(lat),dy)
                lon_vec = np.arange(np.nanmin(lon),np.nanmax(lon),dx)

        usermessage.ezprint('\tXmin: %s' % (np.min(lon_vec)),log,verbose)                         
        usermessage.ezprint('\tYmin: %s' % (np.min(lat_vec)),log,verbose)   
        usermessage.ezprint('\tXmax: %s' % (np.max(lon_vec)),log,verbose)                         
        usermessage.ezprint('\tYmax: %s' % (np.max(lat_vec)),log,verbose)  
        usermessage.ezprint('\tNumber of lines: %s' % (len(lat_vec)),log,verbose) 
        usermessage.ezprint('\tNumber of columns: %s' % (len(lon_vec)),log,verbose)
        usermessage.ezprint('\tInterpolation methods: %s' % (interpmethod),log,verbose)
               
        ## Output 
        usermessage.ezprint('Output file information:',log,verbose)
        usermessage.ezprint('\tFormat: %s' % (format),log,verbose)
        usermessage.ezprint('\tUCHAR: %s' % (uchar),log,verbose)
        usermessage.ezprint('\tNo-data value: %s' % (nodata),log,verbose)

        # Correction of the colormap is mode == auto
        if colormap == 'auto': 
                if mode == 'ifg': 
                        colormap = 'sar'
                if mode == 'coh':
                        colormap = 'gray'
        if uchar == True: 
                usermessage.ezprint('\tColormap: %s' % (colormap),log,verbose)

        ## Interpolation        
        usermessage.ezprint('Interpolation:',log,verbose)
        lon_grid, lat_grid = np.meshgrid(lon_vec, lat_vec)
        pts = (lon.flatten(),lat.flatten())
        data_grid = scipy.interpolate.griddata(pts, datainput.flatten(), (lon_grid, lat_grid),method=interpmethod, rescale=True)

        # Max distance correction 
        ptstmp = np.vstack((lon.flatten(),lat.flatten())).T
        tree = cKDTree(ptstmp)
        xi = _ndim_coords_from_arrays(tuple(np.meshgrid(lon_vec, lat_vec)),ndim=ptstmp.shape[1])
        dists, indexes = tree.query(xi)
        data_grid[dists > np.mean([dx,dy]*3)] = np.nan

        usermessage.ezprint('\tdone:',log,verbose)

        ## Mask the interpolated results based on the masked DEM
        if not demgeofile == None: 
                usermessage.ezprint('Mask the results based on a masked DEM:',log,verbose)
                usermessage.ezprint('\tFile: %s' % (demgeofile),log,verbose)
                
                options = gdal.WarpOptions(width=data_grid.shape[1],
                                height=data_grid.shape[0],
                                outputBounds = [np.min(lon_grid),
                                                np.min(lat_grid),
                                                np.max(lon_grid),
                                                np.max(lat_grid),
                                ]
                                )
                maskGEO = gdal.Warp('/vsimem/tmp.tif',demgeofile, options=options)
                # print(maskGEO.ReadAsArray())
                data_grid[np.flipud(maskGEO.ReadAsArray())==nodata] = nodata

        # Little corrections
        data_grid = np.flipud(data_grid)
        if mode == 'ifg': 
                data_grid = np.angle(data_grid)

        ## Extract the information of the output file 
        usermessage.ezprint('Write the output file:',log,verbose)
        image_size = data_grid.shape
        nx = image_size[0]
        ny = image_size[1]
        xmin, ymin, xmax, ymax = [min(lon_grid.flatten()), min(lat_grid.flatten()), max(lon_grid.flatten()), max(lat_grid.flatten())]
        xres = (xmax - xmin) / float(ny)
        yres = (ymax - ymin) / float(nx)

        if not format == 'GTiff': 
                geotransform = (xmin, xres, 0, ymax, 0, -yres)
        else: 
                geotransform = (xmin-xres/2, xres, 0, ymax-yres/2, 0, -yres)

        if uchar == True and (not nodata == 0): 
                usermessage.warningmsg(__name__,rdr2geotiff.__name__,__file__,'0 nodata value is required for uchar file: modification.',log,verbose)
                nodata = 0
        if mode == 'ifg' and uchar == True:
                data_grid[data_grid==np.nan] = 0
                data_grid = ((data_grid + np.pi)/(2*np.pi))*256
                data_grid[data_grid==128] = 0
                dst_ds = gdal.GetDriverByName(format).Create(outputfile, ny, nx, 1, gdal.GDT_Byte)
        elif mode == 'coh' and uchar == True:
                data_grid[data_grid==np.nan] = 0
                data_grid = data_grid*255
                data_grid[data_grid==0] = 0
                dst_ds = gdal.GetDriverByName(format).Create(outputfile, ny, nx, 1, gdal.GDT_Byte)
        elif mode == 'unw' and uchar == True:
                usermessage.warningmsg(__name__,rdr2geotiff.__name__,__file__,'UCHAR format is not compatible with the unwrapped ifgs: the file will be saved in float.',log,verbose)
                data_grid[data_grid==np.nan] = nodata
                dst_ds = gdal.GetDriverByName(format).Create(outputfile, ny, nx, 1, gdal.GDT_Float32)
        else: 
                data_grid[data_grid==np.nan] = nodata
                dst_ds = gdal.GetDriverByName(format).Create(outputfile, ny, nx, 1, gdal.GDT_Float32)

        dst_ds.SetGeoTransform(geotransform)                            # specify coords
        srs = osr.SpatialReference()                                     # establish encoding
        srs.ImportFromEPSG(srscode)                                     # WGS84 lat/long
        dst_ds.SetProjection(srs.ExportToWkt())                         # export coords to file
        dst_ds.GetRasterBand(1).WriteArray(data_grid)                   # write r-band to the raster
        dst_ds.GetRasterBand(1).SetNoDataValue(nodata)                  # No-data value
        dst_ds.SetMetadata({"AREA_OR_POINT": "Point","TIFFTAG_SOFTWARE": "Created with EZ-InSAR %s %s" % (constants.__version__,constants.__copyright__)})
        dst_ds.FlushCache()                                             # write to disk
        dst_ds = None                                                   # Close the output file

        usermessage.ezprint('\tdone:',log,verbose)

        ## Add the colormap for uchar files
        if uchar ==  True and format == 'GTiff' and (not mode == 'unw'):
                usermessage.ezprint('Replacement of the colormap:',log,verbose)
                ds = gdal.Open(outputfile, 1)
                band = ds.GetRasterBand(1)
                colors = gdal.ColorTable()
                fc = open(glob.glob(os.path.dirname(__file__)+os.sep+'colormap'+os.sep+'cmap_'+colormap+'.csv')[0],'r')
                h = 0
                for entre in fc:
                        a  = entre.split()
                        colors.SetColorEntry(int(h), (int(a[0]), int(a[1]), int(a[2])))
                        h = h + 1
                fc.close()
                band.SetRasterColorTable(colors)
                band.SetRasterColorInterpretation(gdal.GCI_PaletteIndex)
                del band, ds
                usermessage.ezprint('\tdone:',log,verbose)

################################################################################
## Conversion of geotiff (float) to uchar, with colormap
################################################################################
def geotifffloat2uchar(
        input, 
        output: Optional[Union[str,None]] = None,
        mode: Optional[str] = 'auto',
        nodata: Optional[Union[int,float]] = 0,
        colormap: Optional[str] = 'auto',
        AREA_OR_POINT: Optional[str] = 'Point',
        verbose: Optional[bool] = True, 
        log: Optional[Union[str,None]] = None,
        ):
        """Convertion of float to uchar for Geotiff file. 

        The function will convert a float GeoTiff to an uchar GeoTiff, with colormap. This function is used by Gamma and SNAP. 

        The function reads a GTiff image (created using the float byte format), and convert it to a uchar image, adding a colormap. The detection of InSAR-result types (i.e., interferogram, unwrapped images, coherence) is automatic because it is based on the file name. However, the user can force the used mode. 

        Args:
                input (str): Full path of the output file
                output (str): Full path of the output file
                mode (str, Optional): Mode of the geocoding. Can be ifg, coh, unw or auto. If auto, the mode will be detected. [Default: ``auto``].          
                nodata (int or float, Optional): Value for the non-data. [Default: ``0``]. 
                colormap (str, Optional): Colormap used for the uchar file. Can be a colormap name or auto. If auto, the colormap will be sar for the ifgs and gray for coherence. Only valid for GTiff. [Default: ``auto``].
                AREA_OR_POINT (str, Optional): de 
                verbose (bool, Optional): verbose [Default: `True`].
                log (str): Log file [Default: `None`].

        """

        ## Check the input parameters
        if not os.path.isfile(input):
                raise ValueError(usermessage.errormsg(__name__,geotifffloat2uchar.__name__,__file__,__copyright__,
                                'The input file does not exist.',log))
        
        if not mode in ['auto','ifg','unw','coh']:
                raise TypeError(usermessage.typeerrormsg(
                        __name__,geotifffloat2uchar.__name__,__file__,__copyright__,
                        'mode',"'auto','ifg','coh'",log))
        
        if not AREA_OR_POINT in ['Point','Area']:
                raise TypeError(usermessage.typeerrormsg(
                        __name__,geotifffloat2uchar.__name__,__file__,__copyright__,
                        'AREA_OR_POINT',"'Point','Area'",log))

        if not (isinstance(nodata,int) or isinstance(nodata,float)):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,geotifffloat2uchar.__name__,__file__,__copyright__,
                        'nodata','int or float',log))
        
        list_colormap = []
        for li in glob.glob(os.path.dirname(__file__)+os.sep+'colormap'+os.sep+'*.csv'): 
                list_colormap.append(li.split(os.sep)[-1].split('.')[0].replace('cmap_',''))
        if not colormap == 'auto':
                if not colormap in list_colormap: 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,geotifffloat2uchar.__name__,__file__,__copyright__,
                                'colormap','%s' % (list_colormap),log))

        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,geotifffloat2uchar.__name__,__file__,__copyright__,
                        'verbose','True or False',log))

        usermessage.openingmsg(__name__,geotifffloat2uchar.__name__,__file__,__copyright__,'Convert a Float GTiff to Uchar',log,verbose)

        usermessage.ezprint('Input file: %s' % (input),log,verbose)

        if mode == 'auto': 
                if ('int' in input.split(os.sep)[-1]) or ('diff' in input.split(os.sep)[-1]): 
                        mode = 'ifg'
                elif ('coh' in input.split(os.sep)[-1]) or ('cor' in input.split(os.sep)[-1]) or ('cc' in input.split(os.sep)[-1]): 
                        mode = 'coh'
                else: 
                        mode = 'unw'

        src_ds = gdal.Open(input)
        band = src_ds.GetRasterBand(1).ReadAsArray()
        band[band == nodata] = 0
        if mode == 'ifg':
                band = ((band + np.pi)/(2*np.pi))*256
                band[band==128] = 0
        elif mode == 'coh':
                band[band==nodata] = 0
                band = band*255

        if output == None:
                output = input.replace('.tif','.uchar.tif')

        dst_ds = gdal.GetDriverByName("GTiff").Create(output, src_ds.RasterXSize, src_ds.RasterYSize, 1, gdal.GDT_Byte)
        dst_ds.SetGeoTransform(src_ds.GetGeoTransform()) 
        dst_ds.SetProjection(src_ds.GetProjection())
        dst_ds.GetRasterBand(1).WriteArray(band)   
        dst_ds.GetRasterBand(1).SetNoDataValue(nodata)
        if AREA_OR_POINT == 'Point':
                dst_ds.SetMetadata({"AREA_OR_POINT": "Point","TIFFTAG_SOFTWARE": "Created with EZ-InSAR %s %s" % (constants.__version__,constants.__copyright__)})
        else:
                dst_ds.SetMetadata({"AREA_OR_POINT": "Area","TIFFTAG_SOFTWARE": "Created with EZ-InSAR %s %s" % (constants.__version__,constants.__copyright__)})
        dst_ds.FlushCache()

        if colormap == 'auto': 
                if mode == 'ifg': 
                        colormap = 'sar'
                if mode == 'coh':
                        colormap = 'gray'

        src_ds = None
        dst_ds = None

        ds = gdal.Open(output, 1)
        band = ds.GetRasterBand(1)
        colors = gdal.ColorTable()
        fc = open(glob.glob(os.path.dirname(__file__)+os.sep+'colormap'+os.sep+'cmap_'+colormap+'.csv')[0],'r')
        h = 0
        for entre in fc:
                a  = entre.split()
                colors.SetColorEntry(int(h), (int(a[0]), int(a[1]), int(a[2])))
                h = h + 1
        fc.close()
        band.SetRasterColorTable(colors)
        band.SetRasterColorInterpretation(gdal.GCI_PaletteIndex)
        del band, ds

        usermessage.ezprint('Output file: %s with the %s colormap' % (output,colormap),log,verbose)