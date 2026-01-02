#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to import and display the ROI from an EZ-InSAR job 

The module allows to display and import the ROI for an `EIjob`. 
    
    (From `ezinsar` package)

Changelog:
        * 3.3.1: Check the check method, Dec. 2025, Alexis Hrysiewicz
        * 3.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################ 
import os
import numpy as np
from shapely.geometry import Polygon
from shapely.wkt import loads
import fiona
import pyproj
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from typing import Optional, Union
import pandas as pd

from ezinsar import constants
from ezinsar import usermessage
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Function to import the ROI for the EZ-InSAR job 
################################################################################
def importroi(job, input, verbose: Optional[bool] = None, radiusvolc: Optional[float] = 20000):
        """Import a ROI into an EZ-InSAR job

        The function imports a ROI into an ``EIjob``.  

        Args:
                job (`EIjob`): EZ-InSAR job
                input (str or list of float): Input information. See Notes
                radiusvolc (float or int): Radius for volcano selection in meter
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                `EIjob`: Return an EZ-InSAR class 

        Notes: 
                The input argument can be given under three different variable: 
                        - a str for a fullpath of a vector file (e.g., shapefile)
                        - a str as 'S,W,N,E' in EPGS:4326 coordinates; 
                        - a list of float in [S , W, N, E] format, in EPGS:4326 coordinates; 
                        - a str as a volcano name.

        """   

        if not 'EIjob' in str(type(job)):
                raise ValueError(usermessage.errormsg(__name__,importroi.__name__,__file__,__copyright__,
                        'The job parameter is not a EZ-InSAR job.'),job.log)
        
        if (not isinstance(radiusvolc,float)) and (not isinstance(radiusvolc,int)):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,importroi.__name__,__file__,__copyright__,
                        'radiusvolc','int or float',job.log))

        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,importroi.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))

        usermessage.openingmsg(__name__,importroi.__name__,__file__,__copyright__,'Import the ROI for EZ-InSAR',job.log,verbose)

        # If the input is a list 
        if isinstance(input, list):
                usermessage.ezprint('Use the ROI given by the user via a list of coordinates in EPGS:4326',job.log,verbose)

                if not len(input) == 4:
                        raise ValueError(usermessage.errormsg(__name__,importroi.__name__,__file__,__copyright__,'The bbox list must contain four elements.'),job.log)
                
                bbox = loads("POLYGON ((%f %f, %f %f, %f %f, %f %f, %f %f))" % (
                input[0], input[1],
                input[2], input[1],
                input[2], input[3],
                input[0], input[3],
                input[0], input[1]))

        # If the input is a shapely polygon
        elif 'shapely.geometry.polygon.Polygon' in str(type(input)): 
                usermessage.ezprint('Use the ROI given by the user via a shapely polygon in EPGS:4326',job.log,verbose)
                bbox = input

        # If the input is a string 
        elif isinstance(input, str):

                # If the input is a file
                if os.path.isfile(input): 
                        
                        usermessage.ezprint('Use the ROI given by the user via the file %s' % (input),job.log,verbose)

                        with fiona.open(input) as roifile:
                                
                                for feature in roifile:
                                        if len(feature['geometry']["coordinates"][0]) == 1:
                                                bbox = Polygon(feature['geometry']["coordinates"][0][0])
                                        else: 
                                                bbox = Polygon(feature['geometry']["coordinates"][0])
                                        
                                if not roifile.crs == 'EPSG:4326':
                                        usermessage.ezprint('\tWarp the polygon in EPGS:4326...',job.log,verbose)

                                        lontmp = []
                                        lattmp = []

                                        meter_to_latlon = pyproj.Transformer.from_crs(roifile.crs,'epsg:4326')
                                        for index, point in enumerate(bbox.exterior.coords):
                                                lati, loni = meter_to_latlon.transform(point[0],point[1])
                                                lontmp.append(loni)
                                                lattmp.append(lati)
                                        
                                        bbox = Polygon(list(zip(lontmp, lattmp)))

                                        usermessage.ezprint('\t\tdone.',job.log,verbose)
                                                
                elif len(input.split(',')) == 4: 
                        usermessage.ezprint('Use the ROI given by the user via a string of coordinates in EPGS:4326',job.log,verbose)

                        bbox = loads("POLYGON ((%f %f, %f %f, %f %f, %f %f, %f %f))" % (
                        float(input.split(',')[0]), float(input.split(',')[1]),
                        float(input.split(',')[2]), float(input.split(',')[1]),
                        float(input.split(',')[2]), float(input.split(',')[3]),
                        float(input.split(',')[0]), float(input.split(',')[3]),
                        float(input.split(',')[0]), float(input.split(',')[1])))

                else:
                        usermessage.ezprint('Try a volcano name: %s' % (input), job.log,verbose)
                        usermessage.ezprint('\tRead the Holocene Volcano List from Global Volcanism Program database. Please cite this as: Global Volcanism Program, 2024. [Database] Volcanoes of the World (v. 5.1.7; 26 Apr 2024). Distributed by Smithsonian Institution, compiled by Venzke, E. https://doi.org/10.5479/si.GVP.VOTW5-2023.5.1', job.log,verbose)

                        db = pd.read_csv(os.path.dirname(__file__)+os.sep+'..'+os.sep+'..'+os.sep+'3rdparty'+os.sep+'GVP_Volcano_List_Holocene.csv')
                        
                        check_volc = False
                        for idx, volc in enumerate(db['Volcano Name']):
                                if input == volc:
                                        latc = db['Latitude'][idx]
                                        lonc = db['Longitude'][idx]
                                        usermessage.ezprint('\tVolcano %s detected\n\t\tLat: %f Lon: %f' % (input,latc,lonc), job.log,verbose)

                                        usermessage.ezprint('\tComputation of the ROI', job.log,verbose)
                                        convfunc = pyproj.Transformer.from_crs('epsg:4326','epsg:900913')
                                        xc, yc = convfunc.transform(latc,lonc)

                                        xpoly = xc + np.cos(np.linspace(-np.pi,np.pi,25)) * radiusvolc
                                        ypoly = yc + np.sin(np.linspace(-np.pi,np.pi,25)) * radiusvolc
                                        
                                        convfunc = pyproj.Transformer.from_crs('epsg:900913','epsg:4326')
                                        lat, lon = convfunc.transform(xpoly,ypoly)

                                        bbox = Polygon([i for i in zip(lon, lat)])
                                        check_volc = True
                        
                        if check_volc == False:
                                raise ValueError(usermessage.errormsg(__name__,importroi.__name__,__file__,__copyright__,'The ROI is not recognised.',job.log))

        else: 
                raise ValueError(usermessage.errormsg(__name__,importroi.__name__,__file__,__copyright__,'The ROI is not recognised.',job.log))

        job.roi = bbox
        usermessage.ezprint('\tThe ROI (in EPGS:4326) is: %s' % (str(bbox)),job.log,verbose)
        usermessage.ezprint('\n\tSaved in the job "%s"' % (job.nameJob),job.log,verbose)

        return job

################################################################################
## Function to display the ROI for the EZ-InSAR job 
################################################################################
def display(job, verbose: Optional[bool] = None,
                basemap: Optional[str] = 'World_Imagery',
                figure: Optional[Union[str,None]] = None, 
                figurewidth: Optional[int] = 2000):
        """Display the ROI from an EZ-InSAR job

        The function displays the ROI from an ``EIjob``.  

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                basemap (str): mode of the display [Default: ``extent``]. Can be ``NatGeo_World_Map``,``USA_Topo_Maps``,``World_Imagery``,``World_Physical_Map``,``World_Shaded_Relief``,``World_Street_Map``,``World_Terrain_Base``,``World_Topo_Map``
                figure (str): Path of the figure to save the figure [Default: ``None``]. If ``None``, the figure will be displayed.
                figurewidth (int): Pixel width of the basemap figure (i.e., resolution) [Default: 2000].

        Returns:
                `EIjob`: Return an EZ-InSAR class 

        """  

        if not 'EIjob' in str(type(job)):
                raise ValueError(usermessage.errormsg(__name__,display.__name__,__file__,__copyright__,
                        'The job parameter is not a EZ-InSAR job.',job.log))
        
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,display.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        
        if not isinstance(basemap,str): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,display.__name__,__file__,__copyright__,
                        'basemap',"'NatGeo_World_Map','USA_Topo_Maps','World_Imagery','World_Physical_Map','World_Shaded_Relief','World_Street_Map','World_Terrain_Base','World_Topo_Map'"),job.log)
        usermessage.openingmsg(__name__,display.__name__,__file__,__copyright__,'Display a map with the ROI of the EZ-InSAR job',job.log,verbose)

        if not (isinstance(figure,str) or figure == None): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,display.__name__,__file__,__copyright__,
                        'figure','str or None',job.log))
        
        # Extract the coordinates
        try: 
                lon,lat = job.roi.exterior.xy
        except: 
                raise ValueError(usermessage.errormsg(__name__,display.__name__,__file__,__copyright__,
                        'The ROI is not defined.',job.log))

        usermessage.ezprint('\tLoad the figure...',job.log,verbose)
        
        # Plot the ROI
        fig = plt.figure(figsize=(8, 8))
        m = Basemap(projection='merc', resolution='f',epsg=4326, 
                        llcrnrlon = np.min(lon)-(np.max(lon)-np.min(lon))*0.25,
                        llcrnrlat = np.min(lat)-(np.max(lat)-np.min(lat))*0.25,
                        urcrnrlon = np.max(lon)+(np.max(lon)-np.min(lon))*0.25,
                        urcrnrlat = np.max(lat)+(np.max(lat)-np.min(lat))*0.25)       
        
        m.plot(lon,lat,'-',linewidth=2,color='red',latlon=True,label='User ROI')
        m.plot([np.min(lon),np.max(lon),np.max(lon),np.min(lon),np.min(lon)],[np.min(lat),np.min(lat),np.max(lat),np.max(lat),np.min(lat)],'--',linewidth=1,color='red',latlon=True,label='ROI for EZ-InSAR')

        m.arcgisimage(service=basemap, xpixels = figurewidth, ypixels = figurewidth, verbose = verbose)
        
        m.drawparallels(np.linspace(np.fix(np.min(lat))-1,np.fix(np.max(lat))+1,10),labels=[1,0,0,0])
        m.drawmeridians(np.linspace(np.fix(np.min(lon))-1,np.fix(np.max(lon))+1,10),labels=[0,0,0,1])
        
        plt.legend()
        plt.title('Map of the EZ-InSAR ROI for "%s"' %(job.nameJob))

        # Save the figure
        if figure == None:
                usermessage.ezprint('\tDisplay the figure...',job.log,verbose)
                plt.show()
        else:
                plt.savefig(figure, dpi=450)
                usermessage.ezprint('\tThe figure has been saved to %s' % (figure),job.log,verbose)

        return job
    