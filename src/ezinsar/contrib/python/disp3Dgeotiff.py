#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to inverse vertical and horizontal displacements from geotiff unwrapped images produced by EZ-InSAR

The module contains a simple processor to inverse vertical and horizontal displacements from geotiff images. Of course, it is not depended on the processor used. 

Restrictions: 
        * Only one wavelength can be used. 
        * The control of NS outputs is performed via the radarlook matrix. 
        * Atmospheric delay correction is performed via deramping. 
        * Coherence images must be in uchar format. 

Changelog:
        * 1.1.0: Hole filling and removal for the coherence mask, Dec. 2025, Alexis Hrysiewicz
        * 1.0.1: Bug fix for the interpolation, Oct. 2025, Alexis Hrysiewicz
        * 1.0.0: Initial version, Jul. 2025

"""

__author__ = 'Alexis Hrysiewicz (UCD / iCRAG)'
__copyright__ = "Copyright 2025, EZ-InSAR / UCD / iCRAG"
__version__ = '1.1.0'

################################################################################
## Python packages
################################################################################
import os
from typing import Optional, Union
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib import path
from shapely.geometry import Polygon
import fiona
import copy
from osgeo import gdal
from scipy.signal import medfilt2d
from scipy import optimize, interpolate
from skimage import measure
gdal.UseExceptions()

################################################################################
## Import the EZ-InSAR package
################################################################################
from ezinsar import usermessage, constants

## Surface models
def __modelfit1__(X,c0):
        x,y = X
        return c0

def __modelfit3__(X,c0,c1,c2):
        x,y = X
        return c0 + c1 * x + c2 * y

def __modelfit4__(X,c0,c1,c2,c3):
        x,y = X
        return c0 + c1 * x + c2 * y + c3 * x * y

def __modelfit6__(X,c0,c1,c2,c3,c4,c5):
        x,y = X
        return c0 + c1 * x + c2 * y + c3 * x * y + c4 * x**2 + c5 * y**2

################################################################################
## Class to manage the EZ-InSAR job
################################################################################
class stack:
        """EZ-InSAR job (`EIjob`) class.

        Attributes:
                user (str): Name/Definition of the user [Default: `None`]
                

        """

        ################################################################################
        ## Initialistion of the class
        ################################################################################
        def __init__(self,
                        phase_files,
                        coherence: Optional[list] = [],
                        wavelength = 0.055465760, 
                        interpmethod = 'linear',
                        verbose: Optional[bool] = True,
                        log: Optional[Union[str,None]] = None,
                        ):

                """Initialisation of the class  

                Args: 
                        phase_files (list): List of unwrapped phase files in geotiff
                        coherence (list, Optional): List of coherence files in geotiff (uchar format). [Default: []]
                        wavelength (float, Optional): Wavelength in m. [Default: 0.055465760]
                        interpmethod (str, Optional): Interpolation method. [Default: linear]
                        verbose (bool, Optional): Verbose. [Default: `True`]
                        log (str, Optional): log. [Default: `None`]
 
                """
                start = time.time()

                if not isinstance(verbose,bool):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'verbose','True or False',log))

                usermessage.openingmsg(__name__,__name__,__file__,constants.__copyright__,'Vertical and horizontal displacement inversion based on geotiff products: Initialisation of the stack (import and interpolation of datasets)',log,verbose,contribauthor=__author__,contribcopyright=__copyright__,contribversion=__version__,contribfile=__file__)

                self.filephase = phase_files
                self.filecoh = coherence
                self.wavelength = wavelength
                self.unwphase = []
                self.unwphasemasked = []
                self.unwphasederamped = []
                self.coh = []
                self.Xgrid = None
                self.Ygrid = None
                self.dispX = None
                self.dispY = None
                self.dispZ = None

                ## Import the files
                usermessage.ezprint('Import the files (with interpolation)',log,verbose) 

                for idx, fi in enumerate(phase_files): 

                        usermessage.ezprint('\tUnwrapped hase: %s' % (fi),log,verbose) 
                        
                        dataset = gdal.Open(fi)

                        if dataset is None:
                                raise ValueError(usermessage.typeerrormsg(
                                        __name__,__name__,__file__,__copyright__,
                                        'The file %s does not exist' % (fi),log))

                        geotransform = dataset.GetGeoTransform()
                        origin_x = geotransform[0]  
                        origin_y = geotransform[3] 
                        pixel_width = geotransform[1]
                        pixel_height = geotransform[5] 
                        cols = dataset.RasterXSize
                        rows = dataset.RasterYSize
                        x = np.arange(cols) * pixel_width + origin_x
                        y = np.arange(rows) * pixel_height + origin_y
                        X, Y = np.meshgrid(x, y)

                        tmp = dataset.GetRasterBand(1).ReadAsArray()
                        tmp[np.isnan(tmp)] = 0
                        tmp[tmp==0] = np.nan
                        if idx == 0: 
                                self.Xgrid = X
                                self.Ygrid = Y 
                        else:   
                                usermessage.ezprint('\t\tInterpolation by using the %s method' % (interpmethod),log,verbose) 
                                funcinter = interpolate.RegularGridInterpolator((X[0,:].flatten(),Y[:,0].flatten()),
                                                                        tmp.T,
                                                                        method=interpmethod,
                                                                        fill_value=np.nan,
                                                                        bounds_error=False)
                                tmp = funcinter((self.Xgrid,self.Ygrid))
                        
                        self.unwphase.append(tmp)
                        dataset = None

                        ## For the coherence images
                        if not coherence == []: 
                                usermessage.ezprint('\t\tCoherence: %s' % (coherence[idx]),log,verbose) 
                                dataset = gdal.Open(coherence[idx]) 
                        
                                if dataset.GetRasterBand(1).ReadAsArray().dtype in ['float32','float64']:
                                        tmp =dataset.GetRasterBand(1).ReadAsArray().astype(np.float32)
                                else:
                                        tmp =dataset.GetRasterBand(1).ReadAsArray().astype(np.float32)/255
                                tmp[np.isnan(tmp)] = 0
                                tmp[tmp==0] = np.nan
                                if not idx == 0: 
                                        usermessage.ezprint('\t\t\tInterpolation by using the %s method' % (interpmethod),log,verbose) 
                                        funcinter = interpolate.RegularGridInterpolator((X[0,:].flatten(),Y[:,0].flatten()),
                                                                        tmp.T,
                                                                        method=interpmethod,
                                                                        fill_value=np.nan,
                                                                        bounds_error=False)
                                        tmp = funcinter((self.Xgrid,self.Ygrid))
                                self.coh.append(tmp) 
                                dataset = None

                usermessage.ezprint('\nPerformed in %0.3f seconds' % (time.time()-start),log,verbose)

        ################################################################################
        ## Mask the phase based on the coherence 
        ################################################################################
        def maskfromcc(self,
                threshold: Optional[float] = 0.3,
                kernel: Optional[int] = 3,
                holecorrection: Optional[bool] = False,
                holecorrectionthres: Optional[int] = 50,
                verbose: Optional[bool] = True,
                log: Optional[Union[str,None]] = None,
                ): 
                """Mask the phase based on the coherence images

                Args: 
                        threshold (float, Optional): Threshold on the coherence. [Default: 0.3]
                        kernel (int, Optional): Kernel for filtering. [Default: 3]
                        verbose (bool, Optional): Verbose. [Default: `True`]
                        log (str, Optional): log. [Default: `None`]
                
                Returns:
                        `stack` class
                """
                start = time.time()

                if not isinstance(verbose,bool):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'verbose','True or False',log))

                usermessage.openingmsg(__name__,__name__,__file__,__copyright__,'Vertical and horizontal displacement inversion based on geotiff products: Mask the phase based on the coherence images',log,verbose,contribauthor=__author__,contribcopyright=__copyright__,contribversion=__version__,contribfile=__file__)

                usermessage.ezprint('Apply a filter on coherence images (kernel: %s):' % (kernel),log,verbose) 
                cohfilt = []
                self.unwphasemasked = []
                if self.filecoh: 
                        for idx, fi in enumerate(self.filecoh): 
                                usermessage.ezprint('\tProcess: %s' % (fi),log,verbose) 
                                cohfilt.append(medfilt2d(self.coh[idx],kernel_size=kernel))

                        usermessage.ezprint('Mask the displacement maps (threshold: %s):' % (threshold),log,verbose) 
                        for idx, fi in enumerate(self.filephase):
                                usermessage.ezprint('\tProcess: %s' % (fi),log,verbose)  
                                mask = np.ones_like(cohfilt[idx])
                                mask[cohfilt[idx]<threshold]=0

                                if holecorrection: 
                                        ll = measure.label(mask, connectivity=1, background=0)
                                        labels, counts = np.unique(ll, return_counts=True)
                                        valid = (labels >= 2) & (counts <= holecorrectionthres)
                                        small_labels = labels[valid]
                                        mask[np.isin(ll, small_labels)] = 0

                                        ll = measure.label(mask, connectivity=1, background=1)
                                        labels, counts = np.unique(ll, return_counts=True)
                                        valid = (labels >= 2) & (counts <= holecorrectionthres // 2)
                                        small_labels = labels[valid]
                                        mask[np.isin(ll, small_labels)] = 1

                                tmp = copy.deepcopy(self.unwphase[idx])
                                tmp[mask==0] = np.nan
                                self.unwphasemasked.append(tmp)
                
                else: 
                        usermessage.warningmsg(__name__,__name__,__file__,'No coherence files are given. The unmasked unwrappred phases will be copied.',log,verbose)
                        self.unwphasemasked = self.unwphase

                usermessage.ezprint('\nPerformed in %0.3f seconds' % (time.time()-start),log,verbose)

                return self

        ################################################################################
        ## Deramp the phases 
        ################################################################################
        def deramp(self,
                source: Optional[str] = 'masked',
                mask: Optional[None] = None,
                nbpoly: Optional[int] = 3,
                verbose: Optional[bool] = True,
                log: Optional[Union[str,None]] = None,
                ): 
                """Deramp the unwrapped phases

                Args:   
                        source (str, Optional): Data source. [Default: masked]
                        nbpoly (str, Optional): Number of parameters in the surface model. [Default: 3]
                        verbose (bool, Optional): Verbose. [Default: `True`]
                        log (str, Optional): log. [Default: `None`]
                
                Returns:
                        `stack` class
                """
                start = time.time()

                if not isinstance(verbose,bool):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'verbose','True or False',log))
                
                if not source in ['raw','masked']:
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'source',"['raw','masked']",log))
                
                if not nbpoly in [1,3,4,6]:
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'nbpoly','[1,3,4,6]',log))

                usermessage.openingmsg(__name__,__name__,__file__,__copyright__,'Vertical and horizontal displacement inversion based on geotiff products: Deramp the phase',log,verbose,contribauthor=__author__,contribcopyright=__copyright__,contribversion=__version__,contribfile=__file__)

                if source == 'masked':
                        datasource = self.unwphasemasked
                elif source == 'raw':
                        datasource = self.unwphase

                usermessage.ezprint('Dataset: %s' % (source),log,verbose) 

                if nbpoly == 1:
                        modelfit = __modelfit1__
                elif nbpoly == 3:
                        modelfit = __modelfit3__
                elif nbpoly == 4:
                        modelfit = __modelfit4__
                elif nbpoly == 6:
                        modelfit = __modelfit6__

                usermessage.ezprint('Deramp the phases (Number of parameters: %s):' % (nbpoly),log,verbose) 

                if os.path.isfile(mask):
                        usermessage.ezprint('The file %s will be used for masking:' % (mask),log,verbose) 
                        with fiona.open(mask) as maskfile:
                                for feature in maskfile:
                                        if len(feature['geometry']["coordinates"][0]) == 1:
                                                maskpoly = Polygon(feature['geometry']["coordinates"][0][0])
                                        else: 
                                                maskpoly = Polygon(feature['geometry']["coordinates"][0])

                ROIpoly= path.Path(list(zip(maskpoly.exterior.xy[0],maskpoly.exterior.xy[1])))
                XY = np.dstack((self.Xgrid, self.Ygrid)).reshape((-1, 2))
                mask = ROIpoly.contains_points(XY).reshape(self.Xgrid.shape) 

                self.unwphasederamped = []

                for idx, fi in enumerate(self.filecoh): 
                        usermessage.ezprint('\tProcess: %s' % (fi),log,verbose) 
                        
                        tmp = copy.deepcopy(datasource[idx])
                        tmp[mask==True] = np.nan

                        X = self.Xgrid[~np.isnan(tmp)].flatten()
                        Y = self.Ygrid[~np.isnan(tmp)].flatten()                        
                        Z = datasource[idx][~np.isnan(tmp)].flatten()

                        popt, pcov, infodict_ran, mesg_ran, _ = optimize.curve_fit(modelfit, np.vstack((X,Y)), Z,      
                                method='dogbox',
                                ftol=1e-10,xtol=1e-10,full_output=True)

                        para = np.zeros((1,6)).flatten()
                        para[0:len(popt)] = popt

                        model = __modelfit6__(np.vstack((self.Xgrid.flatten(),self.Ygrid.flatten())),
                                                para[0],
                                                para[1],
                                                para[2],
                                                para[3],
                                                para[4],
                                                para[5]).reshape(self.Xgrid.shape)

                        self.unwphasederamped.append(datasource[idx]-model)

                usermessage.ezprint('\nPerformed in %0.3f seconds' % (time.time()-start),log,verbose)

                return self

        ################################################################################
        ## Inversion of vertical and horizontal components 
        ################################################################################
        def inv(self,
                rdlk,  
                source: Optional[str] = 'deramped',
                verbose: Optional[bool] = True,
                log: Optional[Union[str,None]] = None,
                ): 
                """Inversion of vertical and horizontal components 

                Args:   
                        rdlk (np.darray): Radarlook matrix (line: nb of images, col: X,Y,Z rdlk). The Y values can be omitted. 
                        source (str, Optional): Data source. [Default: deramped]
                        verbose (bool, Optional): Verbose. [Default: `True`]
                        log (str, Optional): log. [Default: `None`]
                
                Returns:
                        `stack` class
                """
                start = time.time()

                if not isinstance(verbose,bool):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'verbose','True or False',log))
                
                if not isinstance(rdlk,np.ndarray):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'rdlk','np.darray',log))
                
                if not source in ['raw','masked','deramped']:
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'source',"['raw','masked','deramped']",log))

                usermessage.openingmsg(__name__,__name__,__file__,__copyright__,'Vertical and horizontal displacement inversion based on geotiff products: Inversion of vertical and horizontal components ',log,verbose,contribauthor=__author__,contribcopyright=__copyright__,contribversion=__version__,contribfile=__file__)

                if source == 'raw':
                        datasource = copy.deepcopy(self.unwphase)
                elif source == 'masked':
                        datasource = copy.deepcopy(self.unwphasemasked)
                elif source == 'deramped':
                        datasource = copy.deepcopy(self.unwphasederamped)

                usermessage.ezprint('Dataset: %s' % (source),log,verbose) 

                usermessage.ezprint('Build the matrix:',log,verbose) 

                for idx, fi in enumerate(self.filephase): 
                        tmp =(-datasource[idx].flatten()*self.wavelength)/(4*np.pi)
                        if idx == 0: 
                                X = tmp
                        else: 
                                X = np.vstack((X,tmp))
                usermessage.ezprint('\tdone',log,verbose) 

                usermessage.ezprint('Inversion:',log,verbose)
                X = X.T
                R = rdlk
                C = np.linalg.lstsq(R,X.T,rcond=None)
                usermessage.ezprint('\tdone',log,verbose) 

                if rdlk.shape[1] == 2: 
                        self.dispX = C[0].T[:,0].reshape(self.Xgrid.shape)
                        self.dispY = np.zeros_like(self.dispX)
                        self.dispY[self.dispY==0] = np.nan
                        self.dispZ = C[0].T[:,1].reshape(self.Xgrid.shape)

                        usermessage.warningmsg(__name__,__name__,__file__,'The NS component will be filled by np.nan.',log,verbose)

                else: 
                        self.dispX = C[0].T[:,0].reshape(self.Xgrid.shape)
                        self.dispX = C[0].T[:,1].reshape(self.Xgrid.shape)
                        self.dispZ = C[0].T[:,2].reshape(self.Xgrid.shape)

                usermessage.ezprint('\nPerformed in %0.3f seconds' % (time.time()-start),log,verbose)

                return self
        
        ################################################################################
        ## Export the results into Geotiff
        ################################################################################
        def exporttiff(self,
                path: Optional[str] = '.',
                verbose: Optional[bool] = True,
                log: Optional[Union[str,None]] = None,
                ): 
                """Export the results into getiff format

                Args:   
                        path (str, Optional): Path name. [Default: .]
                        verbose (bool, Optional): Verbose. [Default: `True`]
                        log (str, Optional): log. [Default: `None`]
                
                Returns:
                        `stack` class
                """

                def writegtiff(infile,outfile,disp):
                        ds = gdal.Open(infile)
                        driver = gdal.GetDriverByName("GTiff")
                        band = ds.GetRasterBand(1)
                        arr = band.ReadAsArray()
                        [rows, cols] = arr.shape
                        dst_ds = driver.Create(outfile, cols, rows, 1, gdal.GDT_Float32)
                        dst_ds.SetGeoTransform(ds.GetGeoTransform())
                        dst_ds.SetProjection(ds.GetProjection())
                        dst_ds.GetRasterBand(1).SetNoDataValue(np.nan)
                        dst_ds.GetRasterBand(1).WriteArray(disp.astype(np.float32))
                        dst_ds.SetMetadata({"AREA_OR_POINT": "Point","TIFFTAG_SOFTWARE": "Created with EZ-InSAR %s %s" % (constants.__version__,constants.__copyright__)})
                        dst_ds.FlushCache()
                        dst_ds = None
                        band=None
                        ds=None

                start = time.time()

                if not isinstance(verbose,bool):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'verbose','True or False',log))
                
                usermessage.openingmsg(__name__,__name__,__file__,__copyright__,'Vertical and horizontal displacement inversion based on geotiff products: Export the results into tiff images ',log,verbose,contribauthor=__author__,contribcopyright=__copyright__,contribversion=__version__,contribfile=__file__)

                if isinstance(self.dispX,np.ndarray):
                        writegtiff(self.filephase[0],path+os.sep+'dispEW.tif',self.dispX)
                        usermessage.ezprint('Horizontal displacements (EW) in %s' % (path+os.sep+'dispEW.tif'),log,verbose)

                if isinstance(self.dispY,np.ndarray):
                        writegtiff(self.filephase[0],path+os.sep+'dispNS.tif',self.dispY)
                        usermessage.ezprint('Horizontal displacements (NS) in %s' % (path+os.sep+'dispNS.tif'),log,verbose)

                if isinstance(self.dispZ,np.ndarray):
                        writegtiff(self.filephase[0],path+os.sep+'dispUD.tif',self.dispZ)
                        usermessage.ezprint('Vertical displacements (UD) in %s' % (path+os.sep+'dispUD.tif'),log,verbose)

                usermessage.ezprint('\nPerformed in %0.3f seconds' % (time.time()-start),log,verbose)

                return self
        
        ################################################################################
        ## Display functions
        ################################################################################
        def display(self,
                mode: Optional[str] = 'raw',
                figure: Optional[str] = None):
                """Display the unwrapped phases

                Args:   
                        mode (str, Optional): Mode for displaying. [Default: raw]
                        figure (str;, Optional): Filename of figure, if None, the figure will be saved. [Default: None]

                """
                if not mode in ['raw','masked','deramped']:
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,__name__,__file__,__copyright__,
                                'mode',"['raw','masked','deramped']",None))

                if mode == 'raw':
                        listLOS = copy.deepcopy(self.unwphase)
                elif mode == 'masked':
                        listLOS = copy.deepcopy(self.unwphasemasked)
                elif mode == 'deramped':
                        listLOS = copy.deepcopy(self.unwphasederamped)
                
                ## Create the figure
                fig, _axs = plt.subplots(nrows=2, ncols=len(self.unwphase))
                axs = _axs.flatten()

                for idx, phasei in enumerate(listLOS): 
                        
                        ## For the phases
                        imi = axs[idx].imshow((-phasei*self.wavelength)/(4*np.pi),
                                        cmap='jet',
                                        interpolation='none',
                                        extent=[
                                                np.min(self.Xgrid), 
                                                np.max(self.Xgrid), 
                                                np.min(self.Ygrid), 
                                                np.max(self.Ygrid), 
                                                ])
                        
                        axs[idx].set_xlabel('Longitude')
                        axs[idx].set_ylabel('Latitude')
                        axs[idx].set_title(self.filephase[idx].split(os.sep)[-1])
                        cbar = fig.colorbar(imi, ax=axs[idx], shrink=0.9)
                        cbar.ax.set_ylabel('LOS displacement [m]')
                        
                        ## For the coherences
                        if self.coh:
                                imi = axs[len(self.unwphase)+idx].imshow(self.coh[idx],cmap='grey',interpolation='none')
                                axs[len(self.unwphase)+idx].set_xlabel('Longitude')
                                axs[len(self.unwphase)+idx].set_ylabel('Latitude')
                                axs[len(self.unwphase)+idx].set_title(self.filecoh[idx].split(os.sep)[-1])
                                cbar = fig.colorbar(imi, ax=axs[len(self.unwphase)+idx], shrink=0.9)
                                cbar.ax.set_ylabel('Coherence')

                ## Finalisation
                # figManager = plt.get_current_fig_manager()
                # figManager.window.showMaximized()
                if figure == None:
                        fig.suptitle('Stack for inversion: %s unwrapped phases' % (mode), fontsize=16)
                        plt.show()
                else:
                        plt.savefig(figure, dpi=450)
                        usermessage.ezprint('Figure saved in %s' % (figure),None,True)

        def displayinv(self,
                vmin=-0.2,
                vmax=0.2,
                figure: Optional[str] = None): 
                """Display the horizontal and vertical components

                Args:   
                        vmin (float, Optional): Minimal value for colormap. [Default: -0.2]
                        vmax (float, Optional): Maximal value for colormap. [Default: -0.2]
                        figure (str;, Optional): Filename of figure, if None, the figure will be saved. [Default: None]

                """
                fig, _axs = plt.subplots(nrows=2, ncols=2)
                axs = _axs.flatten()

                imi = axs[0].imshow(self.dispX,
                                        cmap='jet',
                                        interpolation='none',
                                        extent=[
                                                np.min(self.Xgrid), 
                                                np.max(self.Xgrid), 
                                                np.min(self.Ygrid), 
                                                np.max(self.Ygrid), 
                                                ], 
                                        vmin=vmin,vmax=vmax)
                axs[0].set_xlabel('Longitude')
                axs[0].set_ylabel('Latitude')
                axs[0].set_title('West-East Displacement')
                cbar = fig.colorbar(imi, ax=axs[0], shrink=0.9)
                cbar.ax.set_ylabel('EW displacement [m]')

                imi = axs[1].imshow(self.dispY,
                                        cmap='jet',
                                        interpolation='none',
                                        extent=[
                                                np.min(self.Xgrid), 
                                                np.max(self.Xgrid), 
                                                np.min(self.Ygrid), 
                                                np.max(self.Ygrid), 
                                                ], 
                                        vmin=vmin,vmax=vmax)
                axs[1].set_xlabel('Longitude')
                axs[1].set_ylabel('Latitude')
                axs[1].set_title('South-North Displacement')
                cbar = fig.colorbar(imi, ax=axs[1], shrink=0.9)
                cbar.ax.set_ylabel('NS displacement [m]')

                imi = axs[2].imshow(self.dispZ,
                                        cmap='jet',
                                        interpolation='none',
                                        extent=[
                                                np.min(self.Xgrid), 
                                                np.max(self.Xgrid), 
                                                np.min(self.Ygrid), 
                                                np.max(self.Ygrid), 
                                                ], 
                                        vmin=vmin,vmax=vmax)
                axs[2].set_xlabel('Longitude')
                axs[2].set_ylabel('Latitude')
                axs[2].set_title('Vertical Displacement')
                cbar = fig.colorbar(imi, ax=axs[2], shrink=0.9)
                cbar.ax.set_ylabel('UD displacement [m]')

                axs[3].remove()

                ## Finalisation
                # figManager = plt.get_current_fig_manager()
                # figManager.window.showMaximized()
                if figure == None:
                        fig.suptitle('Inversed results', fontsize=16)
                        plt.show()
                else:
                        plt.savefig(figure, dpi=450)
                        usermessage.ezprint('Figure saved in %s' % (figure),None,True)

################################################################################
## Desktop application
################################################################################


