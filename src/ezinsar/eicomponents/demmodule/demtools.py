#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to pre-process the DEMs of EZ-InSAR. 

The module allows to manage and pre-process the DEM for an `EIjob`: i.e., downloading or cropping.
    
    (From `ezinsar` package)

Example: 

        Each function can directly used in Python scripts or/and a Python terminal::

                >>> # Import the EZ-InSAR packages
                >>> import ezinsar.job as ez
                >>> from ezinsar.eicomponents.demmodule import demtools
                >>> # Create the job by defining the polarisation and the satellite mode
                >>> job = ez.EIjob(verbose=True,polarisation=['VV','VH'],satmode='IW',roi='ROI.shp')
                >>> # Download a DEM for the EZ-InSAR job
                >>> job = demtools.download(job=job)
                >>> # OR, with the class method
                >>> job.downloaddem()

Changelog:
        * 3.3.1: Check the check method, Dec. 2025, Alexis Hrysiewicz
        * 3.2.1: Several changes, Alexis Hrysiewicz, Aug 2025
                * Geoide files are stored in the user cache directory
                * Rewriting of the download function
        * 3.2.0: Several changes 
                * Add the compatibility with Windows (Docker running), Alexis Hrysiewicz, May 2025
                * Add new DEM sources, Alexis Hrysiewicz, May 2025
        * 3.1.0: Add a parameter for no-data value and the coastline mode, add the byte swap for Windows, Alexis Hrysiewicz, Mar. 2025
        * 3.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import os
import numpy as np
from typing import Optional, Union
# import osgeo_utils.gdal_merge
# import osgeo_utils.gdal_calc
import rasterio as rio
import matplotlib.pyplot as plt

from ezinsar import constants
from ezinsar import usermessage
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Function to display a DEM
################################################################################
def display(job: Optional[Union[any,None]] = None, 
        pathDEM: Optional[Union[str,None]] = None, 
        figure: Optional[Union[str,None]] = None, 
        mode: Optional[str] = 'hillshade',
        azimuth: Optional[float] = 225.0, 
        angle_altitude: Optional[float] = 45.0, 
        verbose: Optional[Union[bool,None]] = None,
        log: Optional[Union[str,None]] = None,
        ):
        """Display the DEM for an EZ-InSAR job. 

        The function displays a DEM from a ``EIjob`` or from user inputs.  

        Args:
                job (`EIjob`): EZ-InSAR job
                pathDEM (str): Fullpath of the DEM file [Default: `None`]. 
                figure (str): Figure file [Default: `None`]. If `None`, the figure will be displayed.  
                mode (str): Mode of the map [Default: 'hillshade']. Can be 'hillshade' or 'raw'. 
                azimuth (float, Optional): Sun azimuth for the hillshade mode [Default: ``225.0``].
                angle_altitude (float, Optional): Sun altitude angle for the hillshade mode [Default: ``45.0``].
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                log (str): logging [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Notes: 
                The `demtools.display` function has a particular behaviour. Indeed, if job is given, the input values 
                will be provided from the `EIjob`. If not, the user requires to define all other arguments. 

                **The user arguments will bypass the values from the** `EIjob`. 

        Returns:
                `EIjob`: EZ-InSAR job

        """   

        usermessage.openingmsg(__name__,display.__name__,__file__,__copyright__,'Display the DEM',log,verbose)
        
        ## Detection of parameters regarding the job
        if not job == None: 
                if not 'EIjob' in str(type(job)):
                        raise ValueError(usermessage.errormsg(__name__,display.__name__,__file__,__copyright__,
                                'The job parameter is not a EZ-InSAR job.',None))  
        if pathDEM == None:
                if not job == None: 
                        pathDEM = job.pathDEM+os.sep+job.nameDEM

        if log == None:
                if not job == None: 
                        log = job.log

        if verbose == None:
                if not job == None: 
                        verbose = job.verbose
        else: 
                if not isinstance(verbose,bool): 
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,display.__name__,__file__,__copyright__,
                                'verbose','True or False',log)) 
                
        if isinstance(pathDEM,str): 
                if os.path.isfile(pathDEM): 
                        usermessage.ezprint('The path of the DEM is: %s.' % (pathDEM),log,verbose)
                else: 
                        raise ValueError(usermessage.errormsg(__name__,display.__name__,__file__,__copyright__,'The path does not exist.',log))  
        else: 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,display.__name__,__file__,__copyright__,
                        'pathDEM','a path or given by the job.',log))
        
        if not (isinstance(figure,str) or figure == None): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,display.__name__,__file__,__copyright__,
                        'figure','str or None',log))
        
        if not (isinstance(mode,str) and mode in ['hillshade','raw']): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,display.__name__,__file__,__copyright__,
                        'mode','hillshade or raw',log))
        
        if not isinstance(azimuth,float): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,display.__name__,__file__,__copyright__,
                        'azimuth','float',log))
        
        if not isinstance(angle_altitude,float): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,display.__name__,__file__,__copyright__,
                        'angle_altitude','float',log))

        # Create the hillshaded DEM
        with rio.open(pathDEM) as dem_dataset:
                dem_data = dem_dataset.read(1)

                if mode == 'hillshade': 
                        usermessage.ezprint('The DEM will be display using the hillshade mode.',log,verbose) 

                        azimuth = 360.0 - azimuth

                        x, y = np.gradient(dem_data)
                        slope = np.pi/2. - np.arctan(np.sqrt(x*x + y*y))
                        aspect = np.arctan2(-x, y)
                        azm_rad = azimuth*np.pi/180
                        alt_rad = angle_altitude*np.pi/180
                        
                        shaded = np.sin(alt_rad)*np.sin(slope) + np.cos(alt_rad)*np.cos(slope)*np.cos((azm_rad - np.pi/2.) - aspect)

                        datafig = 255*(shaded + 1)/2
                elif mode == 'raw': 
                        usermessage.ezprint('The DEM will be display using the raw mode.',log,verbose) 
                        datafig = dem_data

                fig = plt.figure(figsize=(8, 8))
                ext = [dem_dataset.bounds.left, dem_dataset.bounds.right, dem_dataset.bounds.bottom, dem_dataset.bounds.top]
                plt.imshow(datafig,extent=ext)
                if mode == 'hillshade': 
                        plt.set_cmap('gray'); 
                        plt.title('Hillshade')
                        ax=plt.gca(); ax.ticklabel_format(useOffset=False, style='plain') 
                elif mode == 'raw': 
                        plt.colorbar()
                        plt.set_cmap('gray'); 
                        plt.title('Raw DEM')
                        ax=plt.gca(); ax.ticklabel_format(useOffset=False, style='plain') 

                if figure == None:
                        usermessage.ezprint('\tDisplay the figure...',log,verbose)
                        plt.show()
                else:
                        plt.savefig(figure, dpi=450)
                        usermessage.ezprint('\tThe figure has been saved to %s' % (figure),log,verbose)

        return job

############################################################################################
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
