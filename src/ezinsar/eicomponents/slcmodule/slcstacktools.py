#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to add some functions for the Stripmap-like SLC stacks. 

The module allows to add some tools for the ALOS, ALOS-2, TSX/PAZ SLC stacks. 
    
    (From `ezinsar` package)

Changelog:
        * 3.1.0: Several changes, Feb. 2025, Alexis Hrysiewicz
                * Nez interpolation of orbits
                * Add the support of RADARSAT-2, CSK, SAOCOM, 
        * 3.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import os
import numpy as np
from shapely.geometry import Polygon
import glob
import datetime
from typing import Optional, Union
from scipy import interpolate
from scipy.interpolate import LinearNDInterpolator
import matplotlib.pyplot as plt
import copy 
from shapely.wkt import loads
import pyproj
import rasterio as rio
from rasterio import mask

## From EZ-InSAR
from ezinsar import constants
from ezinsar import usermessage
from ezinsar.eicomponents.sensor.alos2module import alos2slctools
from ezinsar.eicomponents.sensor.tsxmodule import tsxslctools
from ezinsar.eicomponents.sensor.rsat2module import rsat2slctools
from ezinsar.eicomponents.sensor.cskmodule import cskslctools
from ezinsar.eicomponents.sensor.csksgmodule import csksgslctools
try: 
        from ezinsarnisarmodule import nisarslctools
except: 
        a = 'dummy' 
try: 
        from ezinsarsaocommodule import saocomslctools
except: 
        a = 'dummy' 


__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Function to compute the coarse network for StripMap imagery 
################################################################################
def commputecoarsenetwork(pathSLC,bbox,polarisation,sat,
        DEM: Optional[Union[str,float,int]] = 500,
        figure: Optional[Union[None,str]] = None,
        preref: Optional[Union[None,str]] = None,
        verbose: Optional[bool] = True,  
        log: Optional[Union[str,None]] = None,  
        ):
        """Compute the potential best reference date for StriMap images

        The function computes the the potential best reference date, ONLY FOR SM and SS.

        Note: 
                The best potential reference date will be computed by barycentre method.

        Args:
                pathSLC (str): Path of the SLC directory
                bbox (any): Polygon vector of the bbox
                polarisation (str): Selected polarisation
                sat (str): Satellite
                DEM (str): Fullpath of the DEM file or a scalar value [Default: 500]
                figure (str): Figure file [Default: None]
                preref (str): Pre-selected reference date [Default: None],  in YYYYMMDD format
                verbose (bool, Optional): verbose [Default: `True`]
                log (str): logging [Default: `None`]

        Returns:
                best_ref (str): Best potential reference date
                dates (list): Dates of the SLCs
                Btempnorm (list): Float of the temporal baselines in days (normalised to the reference dates)
                Btempnorm (list): Float of the perpendicular baselines in metres (normalised to the reference dates)

        """
        
        # Check the input parameters
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,commputecoarsenetwork.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if (not isinstance(pathSLC,str)):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,commputecoarsenetwork.__name__,__file__,__copyright__,
                        'pathSLC','str',log))
        else:
                if not os.path.isdir(pathSLC):
                        raise ValueError(usermessage.errormsg(__name__,commputecoarsenetwork.__name__,__file__,__copyright__,
                        'The pathSLC does not exists.'),log,verbose)
                
        if not sat in ['TSX','PAZ','ALOS2','ALOS','RSAT2','CSK','CSKSG','NISAR','SAOCOM']:
                raise TypeError(usermessage.typeerrormsg(
                        __name__,commputecoarsenetwork.__name__,__file__,__copyright__,
                        'sat',"'TSX','PAZ','ALOS2','ALOS','RSAT2','CSK','CSKSG','NISAR','SAOCOM'",log))

        if isinstance(bbox,str): 
                try:
                        bbox = loads(bbox)
                except:
                       raise TypeError(usermessage.typeerrormsg(
                                __name__,commputecoarsenetwork.__name__,__file__,__copyright__,
                                'bbox','Polygon',log))  
        else: 
                if not (isinstance(bbox, Polygon)):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,commputecoarsenetwork.__name__,__file__,__copyright__,
                                'bbox','Polygon',log))
        
        if isinstance(DEM,str):
                if not os.path.isfile(DEM):
                        raise ValueError(usermessage.errormsg(__name__,commputecoarsenetwork.__name__,__file__,__copyright__,
                        'The DEM file does not exists.'),log,verbose)  
        else: 
                if not (isinstance(DEM,float) or isinstance(DEM,int)):  
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,commputecoarsenetwork.__name__,__file__,__copyright__,
                                'DEM','path, int, or float',log))  
                
        if not figure == None:
                if (not isinstance(figure,str)):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,commputecoarsenetwork.__name__,__file__,__copyright__,
                                'figure','str',log))

        if not preref == None:
                if (not isinstance(preref,str)):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,commputecoarsenetwork.__name__,__file__,__copyright__,
                                'preref','str (format YYYYMMDD)',log))

        usermessage.openingmsg(__name__,commputecoarsenetwork.__name__,__file__,__copyright__,'Script to compute the coarse network of interferograms and isolate the best candidate for the super single master',log,verbose)

        ## Compute the target point 
        usermessage.ezprint('Computation of the target point: ...',log,verbose)
        usermessage.warningmsg(__name__,commputecoarsenetwork.__name__,__file__,'The target point will be the average point (barycentre) in the polygon given by bbox.',log,verbose)

        lon_ROI = bbox.exterior.xy[0]
        lat_ROI = bbox.exterior.xy[1]

        if isinstance(DEM,str):
                usermessage.ezprint('\tRead the DEM %s' % (DEM),log,verbose)

                with rio.open(DEM) as demfile:
                        out_image, out_transform = mask.mask(demfile,[bbox],crop=True)
                elev_target = np.nanmean(out_image)
                usermessage.ezprint('\tThe average elevation is %f meter from the DEM file.' % (elev_target),log,verbose)
        else:
                usermessage.ezprint('\tElevation value from the user: %s m.' % (DEM),log,verbose)
                elev_target = DEM

        lon_target = np.mean(np.array(bbox.exterior.xy[0]))
        lat_target = np.mean(np.array(bbox.exterior.xy[1]))

        usermessage.ezprint('\tThe average target point is located at %f lat and %f lon.' % (lat_target, lon_target),log,verbose)

        # Conversion of lon,lat coord to ECEF (for the target) (large change????)
        if sat in ['PAZ','TSX','RSAT2','CSK','CSKSG','NISAR']: 
                transformer = pyproj.Transformer.from_crs(
                {"proj":'latlong', "ellps":'WGS84', "datum":'WGS84'},
                {"proj":'geocent', "ellps":'WGS84', "datum":'WGS84'},
                )
        else:
                transformer = pyproj.Transformer.from_crs(
                {"proj":'latlong', "ellps":'GRS80', "datum":'WGS84'},
                {"proj":'geocent', "ellps":'GRS80', "datum":'WGS84'},
                )
        x_target, y_target, z_target = transformer.transform(lon_target,lat_target,elev_target,radians = False)
        usermessage.ezprint('\t\tX [m]: %s\n\t\tY [m]: %s\n\t\tZ [m]: %s\n\t\t\tIn ECEF coordinates' % (x_target, y_target, z_target),log,verbose)

        usermessage.ezprint('\tDone',log,verbose)

        ## Read the SLC list
        usermessage.ezprint('Create the SLC list:...',log,verbose)

        list_SLC = []
        dates_SLC = []
        sat_list = []

        if sat in ['PAZ','TSX']: 
                for slci in glob.glob(pathSLC+os.sep+'PAZ*') + glob.glob(pathSLC+os.sep+'TSX*'):
                        list_SLC.append(slci)

                        annoresults = tsxslctools.detectTSXannotationfromxml(slci,'VV')
                        dates_SLC.append(annoresults['data_xmli1']['startTime'].split('.')[0])
        elif sat in ['RSAT2']: 
                for slci in glob.glob(pathSLC+os.sep+'RS2*'):
                        list_SLC.append(slci)
                        annoresults = rsat2slctools.detectRSAT2annotation(slci,'HH')
                        dates_SLC.append(annoresults['data_xmli1']['startTime'].split('.')[0])

        elif sat in ['CSK']: 
                for slci in glob.glob(pathSLC+os.sep+'CSK*'):
                        list_SLC.append(slci)
                        annoresults = cskslctools.detectCSKannotation(slci,'HH')
                        dates_SLC.append(annoresults['data_xmli1']['startTime'].split('.')[0])

        elif sat in ['CSKSG']: 
                for slci in glob.glob(pathSLC+os.sep+'CSG*'):
                        list_SLC.append(slci)
                        annoresults = csksgslctools.detectCSKSGannotation(slci,'HH')
                        dates_SLC.append(annoresults['data_xmli1']['startTime'].split('.')[0])

        elif sat in ['NISAR']: 
                for slci in glob.glob(pathSLC+os.sep+'NISAR*h5'):
                        list_SLC.append(slci)
                        annoresults = nisarslctools.detectNISARannotation(slci,'HH')
                        dates_SLC.append(annoresults['data_xmli1']['startTime'].split('.')[0])
                
        elif sat in ['SAOCOM']: 
                for slci in glob.glob(pathSLC+os.sep+'*SAR*'):
                        list_SLC.append(slci)
                        annoresults = saocomslctools.detectSAOCOMannotation(slci,'VV')
                        dates_SLC.append(annoresults['data_xmli1']['startTime'].split('.')[0])

        else: 
                for li in glob.glob(pathSLC+os.sep+'*'+os.sep+'VOL*') + glob.glob(pathSLC+os.sep+'*'+os.sep+'*.CEOS'): 
                        list_SLC.append(os.path.dirname(li))

                for slci in list_SLC:
                        annoresults = alos2slctools.detectALOS2annotationfromxml(slci)
                        dates_SLC.append(annoresults['data_xmli1']['startTime'].split('.')[0])

        dates_unique = []
        for di in dates_SLC:
                a = datetime.datetime.strptime(datetime.datetime.strftime(datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S"),'%Y-%m-%d'),"%Y-%m-%d")
                dates_unique.append(a)
        dates_unique = np.sort(np.unique(dates_unique))
        usermessage.ezprint('\tDone',log,verbose)
        
        ## Read the satellite parameters for each acquisition
        usermessage.ezprint('Read the satellite parameters for each acquisition...',log,verbose)
        para_sat = {'process': [], 'dates' : [],'Xsat' : [], 'Ysat' : [], 'Zsat' : [], 'incsat' : [], 'Xtarget' : [], 'Ytarget' : [], 'Ztarget' : []}

        usermessage.ezprint('Extraction of satellites parameters from the header files:',log,verbose)

        for di in list_SLC:

                if sat in ['PAZ','TSX']: 
                        annoresults = tsxslctools.detectTSXannotationfromxml(di,'VV')
                elif sat in ['RSAT2']: 
                        annoresults = rsat2slctools.detectRSAT2annotation(di,'HH')
                elif sat in ['CSK']: 
                        annoresults = cskslctools.detectCSKannotation(di,'HH')
                elif sat in ['CSKSG']: 
                        annoresults = csksgslctools.detectCSKSGannotation(di,'HH')
                elif sat in ['NISAR']: 
                        annoresults = nisarslctools.detectNISARannotation(di,'HH')
                elif sat in ['SAOCOM']: 
                        annoresults = saocomslctools.detectSAOCOMannotation(di,'VV')
                else: 
                        annoresults = alos2slctools.detectALOS2annotationfromxml(di) 

                date_slc = annoresults['data_xmli1']['startTime'].split('Z')[0]
                lon = annoresults['data_xmli1']['longitude']
                lat = annoresults['data_xmli1']['latitude']
                inc = annoresults['data_xmli1']['incidenceAngle']
                times = annoresults['data_xmli1']['azimuthTime']    

                # Interpolation of time for the target point
                azimuthTimestamp = []
                for di in times:
                        if 'Z' in di: 
                                azimuthTimestamp.append(datetime.datetime.strptime(di.split('Z')[0],"%Y-%m-%dT%H:%M:%S.%f").timestamp())
                        else: 
                                azimuthTimestamp.append(datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S.%f").timestamp())

                interp = LinearNDInterpolator(list(zip(lon, lat)), azimuthTimestamp)
                azimuthTimestamp_target = interp(lon_target,lat_target)
                azimuthTimes_target = datetime.datetime.fromtimestamp(int(azimuthTimestamp_target))

                interp = LinearNDInterpolator(list(zip(lon, lat)), inc)
                inc_target = interp(lon_target,lat_target)

                # Read the orbits
                data_orbits = annoresults['data_orbitsi1']
        
                # Interpolation of orbits 
                azimuthTimestamp_orbit = [] 
                for di in data_orbits['time']:
                        if 'Z' in di: 
                                azimuthTimestamp_orbit.append(datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
                        else:
                                azimuthTimestamp_orbit.append(datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S.%f").timestamp())

                # fi = interpolate.PchipInterpolator(azimuthTimestamp_orbit, data_orbits['orb_X_int'])
                # x_sat_target = fi(azimuthTimestamp_target)
                # fi = interpolate.PchipInterpolator(azimuthTimestamp_orbit, data_orbits['orb_Y_int'])
                # y_sat_target = fi(azimuthTimestamp_target)
                # fi = interpolate.PchipInterpolator(azimuthTimestamp_orbit, data_orbits['orb_Z_int'])
                # z_sat_target = fi(azimuthTimestamp_target)

                fi = np.poly1d(np.polyfit(azimuthTimestamp_orbit, data_orbits['orb_X_int'], constants.__orbit_poly_order__))
                x_sat_target = fi(azimuthTimestamp_target)
                fi = np.poly1d(np.polyfit(azimuthTimestamp_orbit, data_orbits['orb_Y_int'], constants.__orbit_poly_order__))
                y_sat_target = fi(azimuthTimestamp_target)
                fi = np.poly1d(np.polyfit(azimuthTimestamp_orbit, data_orbits['orb_Z_int'], constants.__orbit_poly_order__))   
                z_sat_target = fi(azimuthTimestamp_target)

                # Store the values
                para_sat['dates'].append(datetime.datetime.strptime(datetime.datetime.strftime(azimuthTimes_target,'%Y-%m-%d'),"%Y-%m-%d"))
                para_sat['Xsat'].append(x_sat_target)
                para_sat['Ysat'].append(y_sat_target)
                para_sat['Zsat'].append(z_sat_target)
                para_sat['incsat'].append(inc_target)
                para_sat['Xtarget'].append(x_target)
                para_sat['Ytarget'].append(y_target)
                para_sat['Ztarget'].append(z_target)
                para_sat['process'].append(True)

        usermessage.ezprint('\tDone',log,verbose)

        ## Fake best reference date from computation
        if not preref == None:
                usermessage.ezprint('The user selected a reference date: %s' %(preref),log,verbose)
                idx_ref = np.where(dates_unique == datetime.datetime.strptime(preref,"%Y%m%d"))[0]

                if idx_ref.size == 0:
                        idx_ref = np.min(np.where(np.array(para_sat['process']) == True))
                        print('\tError: the selected date is not in the SLC dates.')
                        raise ValueError(usermessage.errormsg(__name__,commputecoarsenetwork.__name__,__file__,__copyright__,
                                'The preselected date is not in the SLC dates.'),log,verbose)  
                else:
                        idx_ref = idx_ref[0]
                        if para_sat['process'][idx_ref] == False:
                                idx_ref = np.min(np.where(np.array(para_sat['process']) == True))
                                raise ValueError(usermessage.errormsg(__name__,commputecoarsenetwork.__name__,__file__,__copyright__,
                                        'The preselected date is not processed.'),log,verbose) 
        else:
                usermessage.ezprint('The user did not select a reference date.',log,verbose)
                idx_ref = np.min(np.where(np.array(para_sat['process']) == True))
                # idx_ref = np.median(np.where(np.array(para_sat['process']) == True)).astype('int')
                # idx_ref = np.max(np.where(np.array(para_sat['process']) == True))

        ## Computation of the parameters 
        usermessage.ezprint('Computation of the parameters:...',log,verbose)

        Bperp = []
        Btemp = []
        for h, di in enumerate(para_sat['dates']):
                if para_sat['process'][h] == True and h != idx_ref:

                        M = np.array((para_sat['Xsat'][idx_ref],para_sat['Ysat'][idx_ref],para_sat['Zsat'][idx_ref]))
                        S = np.array((para_sat['Xsat'][h],para_sat['Ysat'][h],para_sat['Zsat'][h]))
                        P = np.array((x_target,y_target,z_target))

                        R1 = np.linalg.norm(M - P)
                        R2 = np.linalg.norm(S - P)

                        B = np.linalg.norm(M - S)

                        Bpari = R1 - R2
                        Bperpi = np.sqrt(B ** 2 - Bpari ** 2)
                        
                        in_vec1 = np.matmul(P,M.T)
                        angle_of_vec1 = np.arccos(in_vec1 / (np.linalg.norm(P)*np.linalg.norm(M)))

                        in_vec2 = np.matmul(P,S.T)
                        angle_of_vec2 = np.arccos(in_vec2 / (np.linalg.norm(P)*np.linalg.norm(S)))

                        if angle_of_vec1 > angle_of_vec2:
                                Bperpi = - Bperpi

                        Btempi = (para_sat['dates'][h].timestamp() - para_sat['dates'][idx_ref].timestamp()) / (24*3600)
                        
                elif para_sat['process'][h] == True and h == idx_ref:
                        Bperpi = 0
                        Btempi = 0
                else:
                        Bperpi = np.nan
                        Btempi = np.nan

                # Save
                Bperp.append(-Bperpi)
                Btemp.append(Btempi)

        usermessage.ezprint('\tDone',log,verbose)

        ## Detection of the best potential reference using geometric barycentre
        usermessage.ezprint('Detection of the best potential reference using geometric barycentre:...',log,verbose)
        usermessage.ezprint('\tThis assumption is only valid for Sentinel-1 stack regarding the acquisiton sampling and orbits parameters (and precisions).',log,verbose)

        dates_slc_sec = []
        for di in para_sat['dates']:
                dates_slc_sec.append(di.timestamp())

        dates_slc_sec = np.where(np.array(para_sat['process']) == False, np.nan, dates_slc_sec)
        dates_mean = np.nanmean(dates_slc_sec)

        Bperpmean = np.nanmean(Bperp)

        a = (dates_slc_sec-np.nanmin(dates_slc_sec))/(np.nanmax(dates_slc_sec) - np.nanmin(dates_slc_sec))
        ab =(dates_mean-np.nanmin(dates_slc_sec))/(np.nanmax(dates_slc_sec) - np.nanmin(dates_slc_sec))

        b = (Bperp-np.nanmin(Bperp))/(np.nanmax(Bperp) - np.nanmin(Bperp))
        bb = (Bperpmean-np.nanmin(Bperp))/(np.nanmax(Bperp) - np.nanmin(Bperp))

        dist = np.sqrt( (a - ab)**2 + (b - bb)**2 )
        idx_best_ref = np.nanargmin(dist)

        Btempnorm = list(np.array(copy.deepcopy(Btemp)) - Btemp[idx_best_ref])
        Bperpnorm = list(np.array(copy.deepcopy(Bperp)) - Bperp[idx_best_ref])

        ## Display the results
        usermessage.ezprint('Results:',log,verbose)

        for idx, di in enumerate(dates_unique):
                if not idx_best_ref == idx:
                        tmp = ''
                else:
                        tmp = ' BEST REFERENCE'
                usermessage.ezprint('\tFor the date %s%s: \n\t\tBTEMP = %0.3f day(s) / BPERP = %0.3f m\n\t\tBTEMP = %0.3f day(s) / BPERP = %0.3f m (regarding the new ref)' % (datetime.datetime.strftime(di,'%Y%m%d'),tmp,Btemp[idx],Bperp[idx],Btempnorm[idx],Bperpnorm[idx]),log,verbose)

        usermessage.ezprint('\nTHE BEST POTENTIAL REFERENCE IMAGES SHOULD BE: %s\n' % (datetime.datetime.strftime(para_sat['dates'][idx_best_ref],'%Y-%m-%d')) ,log,verbose)
        usermessage.ezprint('The results are qualitative and can vary due to the accuracy of orbits and the sampling.',log,verbose)

        if not figure == None: 

                ## Plotting
                plt.scatter(para_sat['dates'], np.array(Bperp), c="black", label="SAR Acquisitions")
                plt.scatter(para_sat['dates'][idx_best_ref], Bperp[idx_best_ref], c="red", label="Best Potential Reference Date")
                plt.scatter(para_sat['dates'][idx_ref], Bperp[idx_ref], marker='1', c="blue", label="Selected Reference Date")
                plt.xlabel("Time")
                plt.ylabel("Bperp [m]")
                plt.legend(loc='best')
                plt.title('Coarse network of interferograms. Reference date: %s' %(datetime.datetime.strftime(para_sat['dates'][idx_best_ref],'%Y-%m-%d')))
                plt.savefig(figure.replace('.jpg','')+'.jpg', dpi=450)

                usermessage.ezprint('Please, visualise the network with the figure in: \n\t%s' % (figure.replace('.jpg','')+'.jpg'),log,verbose)

        return para_sat['dates'][idx_best_ref], para_sat['dates'], Btempnorm, Bperpnorm
