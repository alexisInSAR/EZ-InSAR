#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to pre-process the Sentinel-1 SLC stack

The module allows to pre-process the Sentinel-1 SLC stack, directly from the files in .zip and .SAFE format for an `EIjob`
    
    (From `ezinsar` package)

Note: 
        Each function can directly used in Python scripts or/and a Python terminal

Changelog:
        * 1.1.0: Add the support of Sentinel-1 C and D, Feb. 2025, Alexis Hrysiewicz
        * 1.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import os
import numpy as np
from shapely.geometry import Polygon
import glob
from scipy.spatial import ConvexHull
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

from ezinsar import constants
from ezinsar import usermessage
from ezinsar.eicomponents.sensor.s1module import s1slctools
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Function to compute the coarse network
################################################################################
def commputecoarsenetwork(pathSLC,bbox,polarisation,
        pathorbit: Optional[Union[str,None]] = None,
        DEM: Optional[Union[str,float,int]] = 500,
        figure: Optional[Union[None,str]] = None,
        preref: Optional[Union[None,str]] = None,
        verbose: Optional[bool] = True,  
        log: Optional[Union[str,None]] = None,  
        ):
        """Compute the potential best reference date for a S1 network, from the .zip and .SAFE files 

        The function computes the the potential best reference date for a S1 network, from the .zip and .SAFE files.

        Args:
                pathSLC (str): Path of the SLC directory.
                bbox (any): Polygon vector of the bbox
                polarisation (str): Selected polarisation
                pathorbit (str): Path of the orbit file directory [Default: None].
                DEM (str): Fullpath of the DEM file [Default: None].
                figure (str): Figure file [Default: None]. If `None`, the figure will be displayed. 
                preref (str): Pre-selected reference date [Default: None],  in YYYYMMDD format. 
                verbose (bool, Optional): verbose [Default: `True`]. 
                log (str): logging [Default: `None`].

        Returns:
                best_ref (str): Best potential reference date
                dates (list): Dates of the SLCs
                Btempnorm (list): Float of the temporal baselines in days (normalised to the reference dates)
                Btempnorm (list): Float of the perpendicular baselines in metres (normalised to the reference dates)

        """

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
        
        if not pathorbit == None:
                if (not isinstance(pathorbit,str)):
                        raise TypeError(usermessage.typeerrormsg(
                                __name__,commputecoarsenetwork.__name__,__file__,__copyright__,
                                'pathorbit','str',log))
                else:
                        if not os.path.isdir(pathorbit):
                                raise ValueError(usermessage.errormsg(__name__,commputecoarsenetwork.__name__,__file__,__copyright__,
                                'The pathorbit does not exists.'),log,verbose)

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

        usermessage.openingmsg(__name__,commputecoarsenetwork.__name__,__file__,__copyright__,'Script to compute the coarse network of interferograms and isolate the best candidate for the super single master, from the Sentinel-1 .zip or .SAFE files',log,verbose)

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
                usermessage.ezprint('\tElevation from the user: %s m.' % (DEM),log,verbose)
                elev_target = DEM

        lon_target = np.mean(np.array(bbox.exterior.xy[0]))
        lat_target = np.mean(np.array(bbox.exterior.xy[1]))

        usermessage.ezprint('\tThe average target point is located at %f lat and %f lon.' % (lat_target, lon_target),log,verbose)

        # Conversion of lon,lat coord to ECEF (for the target)
        transformer = pyproj.Transformer.from_crs(
            {"proj":'latlong', "ellps":'WGS84', "datum":'WGS84'},
            {"proj":'geocent', "ellps":'WGS84', "datum":'WGS84'},
            )
        x_target, y_target, z_target = transformer.transform(lon_target,lat_target,elev_target,radians = False)
        usermessage.ezprint('\t\tX [m]: %s\n\t\tY [m]: %s\n\t\tZ [m]: %s\n\t\t\tIn ECEF coordinates' % (x_target, y_target, z_target),log,verbose)

        usermessage.ezprint('\tDone',log,verbose)

        ## Read the SLC list
        usermessage.ezprint('Create the SLC list:...',log,verbose)

        list_SLC = []
        dates_SLC = []
        sat_list = []
        for slci in glob.glob(pathSLC+os.sep+'*.zip') + glob.glob(pathSLC+os.sep+'*.SAFE'):
                p = slci.split(os.sep)[-1]
                list_SLC.append(p)
                dates_SLC.append(p.split('_')[5])
                if 'S1A' in p:
                        sat_list.append("S1A")
                elif 'S1B' in p:
                        sat_list.append("S1B")
                elif 'S1C' in p:
                        sat_list.append("S1C")
                elif 'S1D' in p:
                        sat_list.append("S1D")

        dates_unique = []
        for di in dates_SLC:
                a = datetime.datetime.strptime(datetime.datetime.strftime(datetime.datetime.strptime(di,"%Y%m%dT%H%M%S"),'%Y-%m-%d'),"%Y-%m-%d")
                dates_unique.append(a)
        dates_unique = np.sort(np.unique(dates_unique))
        usermessage.ezprint('\tDone',log,verbose)

        ## Manage the orbit file 
        if not pathorbit == None:
                usermessage.ezprint('Mode of orbits: we will use the precise (or restitued) orbits, if available.',log,verbose)

                dateslcorbits = []
                for di in dates_SLC:
                        a = datetime.datetime.strptime(di,"%Y%m%dT%H%M%S")
                        dateslcorbits.append(a)

                # Creation of list 
                orbits_name = []
                date_format = "%Y%m%dT%H%M%S"

                orbits_precise = glob.glob(pathorbit+os.sep+'*POEORB*.EOF')
                orbits_restitued = glob.glob(pathorbit+os.sep+'*RESORB*.EOF')

                for i1 in range(len(dateslcorbits)):
                        dslc = dateslcorbits[i1]
                        sati = sat_list[i1]

                        usermessage.ezprint('\tCheck the orbit file for the SLC %s acquired by %s' % (dslc,sati),log,verbose)
                        check_precise=False
                        check_restitued=False
                        name_orbit_precise = []
                        name_orbit_restitued = []

                        for pi in orbits_precise:

                                pi = pi.split(os.sep)[-1]
                                if sati in pi: 
                                        orb_test = pi.split('V')[1].split('.')[0]
                                        d1 = datetime.datetime.strptime(orb_test.split('_')[0], date_format)
                                        d2 = datetime.datetime.strptime(orb_test.split('_')[1], date_format)
                                        if d1 <= dslc <= d2:
                                                check_precise=True
                                                name_orbit_precise.append(pi)
                                
                        if len(name_orbit_precise)>0:
                                name_orbit_precise = name_orbit_precise[-1] #Modification to have the last files

                        if check_precise:
                                usermessage.ezprint('\t\tThe precise orbit %s has been found.' % (name_orbit_precise),log,verbose)
                                orbits_name.append(name_orbit_precise)

                        else:
                                usermessage.ezprint('\t\tNo precise orbit has been found, checking of restitued orbit...' % (name_orbit_precise),log,verbose)
                                
                                for pi in orbits_restitued:
                                        pi = pi.split(os.sep)[-1]
                                        if sati in pi: 
                                                orb_test = pi.split('V')[1].split('.')[0]
                                                d1 = datetime.datetime.strptime(orb_test.split('_')[0], date_format)
                                                d2 = datetime.datetime.strptime(orb_test.split('_')[1], date_format)
                                                if d1 <= dslc <= d2:
                                                        check_restitued=True
                                                        name_orbit_restitued.append(pi)
                                if check_restitued:
                                        orbits_name.append(name_orbit_restitued[-1])
                                        usermessage.ezprint('\t\tThe restitued orbit %s has been found.' % (name_orbit_restitued),log,verbose)
                                else:
                                        orbits_name.append(None)       

        else:
                usermessage.ezprint('Mode of orbits: we will use the precise (or restitued) orbits from the .zip or .SAFE files.',log,verbose)


        ## Read the satellite parameters for each acquisition
        usermessage.ezprint('Read the satellite parameters for each acquisition...',log,verbose)
        para_sat = {'dates' : [],'nb_slice' : [],'process' : [], 'X' : [], 'Y' : [], 'Z' : [], 'inc' : []}

        usermessage.ezprint('\tExtraction of satellites parameters from the xml files:',log,verbose)

        for di in dates_unique:

                para_sat['dates'].append(di)

                distr = datetime.datetime.strftime(di,'%Y%m%d')

                # Seach the correct slide(s)
                matches = [match for match in list_SLC if distr in match]

                usermessage.ezprint('\t\tThere is/are %d slices for the date %s' % (len(matches),distr),log,verbose)

                para_sat['nb_slice'].append(len(matches))

                latitude = []
                longitude = []
                incidenceAngle = []
                azimuthTime = []

                time = []
                orb_X_int = []
                orb_Y_int = []
                orb_Z_int = []

                for slcit in matches:
                        
                        slci = slcit.split('.')[0]

                        usermessage.ezprint('\t\t\tRead the file %s' % (slcit),log,verbose)
                        S1annoresults_slci = s1slctools.detectS1annoatationfromxml(pathSLC+os.sep+slcit,polarisation)
                        # burst_roi_slci = s1slctools.detection_S1burst_fromROI(bbox,S1annoresults_slci)

                        # Save 
                        for iwi in ['data_xmli1','data_xmli2','data_xmli3']: 
                                if not S1annoresults_slci[iwi] == None: 
                                        latitude = latitude + S1annoresults_slci[iwi]['latitude']
                                        longitude = longitude + S1annoresults_slci[iwi]['longitude']
                                        azimuthTime = azimuthTime + S1annoresults_slci[iwi]['azimuthTime']
                                        incidenceAngle = incidenceAngle + S1annoresults_slci[iwi]['incidenceAngle']

                        if not pathorbit == None:
                                if not isinstance(orbits_name,list):
                                        orbits_name = [orbits_name]

                                id_orbit = [i for i, s in enumerate(list_SLC) if slci in s][0]

                                slcorbiti = orbits_name[id_orbit]

                                if not slcorbiti == None:  

                                        if 'RESORB' in slcorbiti:
                                                usermessage.ezprint('\t\t\t\tRead the restitued orbit file.',log,verbose)
                                        else:
                                                usermessage.ezprint('\t\t\t\tRead the precise orbit file.',log,verbose)
                                        
                                        data_orbits = s1slctools.read_precise_restitued_xml(pathorbit+os.sep+slcorbiti)

                                        time = time + data_orbits['time']
                                        orb_X_int = orb_X_int + data_orbits['orb_X_int']
                                        orb_Y_int = orb_Y_int + data_orbits['orb_Y_int'] 
                                        orb_Z_int = orb_Z_int + data_orbits['orb_Z_int']
                                
                                else: 
                                        usermessage.ezprint('\t\t\t\tRead the orbit information provided by the .SAFE file.',log,verbose)
                                        for iwi in ['data_orbitsi1','data_orbitsi2','data_orbitsi3']: 
                                                if not S1annoresults_slci[iwi] == None: 
                                                        time = time + S1annoresults_slci[iwi]['time']
                                                        orb_X_int = orb_X_int + S1annoresults_slci[iwi]['orb_X_int']
                                                        orb_Y_int = orb_Y_int + S1annoresults_slci[iwi]['orb_Y_int']
                                                        orb_Z_int = orb_Z_int + S1annoresults_slci[iwi]['orb_Z_int']


                        else:   
                                usermessage.ezprint('\t\t\t\tRead the orbit information provided by the .SAFE file.',log,verbose)
                                for iwi in ['data_orbitsi1','data_orbitsi2','data_orbitsi3']: 
                                        if not S1annoresults_slci[iwi] == None: 
                                                time = time + S1annoresults_slci[iwi]['time']
                                                orb_X_int = orb_X_int + S1annoresults_slci[iwi]['orb_X_int']
                                                orb_Y_int = orb_Y_int + S1annoresults_slci[iwi]['orb_Y_int']
                                                orb_Z_int = orb_Z_int + S1annoresults_slci[iwi]['orb_Z_int']

                # Check if the intersection is correct
                pts = np.array([np.array(longitude),np.array(latitude)]).T
                hull = ConvexHull(pts)
                polyframe = Polygon(list(zip(pts[hull.vertices,0],pts[hull.vertices,1]))) 
                test_intersection = polyframe.intersects(bbox)

                if polyframe.intersection(bbox).area/bbox.area*100 < 98: 
                        usermessage.warningmsg(__name__,commputecoarsenetwork.__name__,__file__,'The intersection is not 100 %. Please check if a slice is missing.',log,verbose)  

                if test_intersection: 
                        para_sat['process'].append(True)

                        timeorbit = []
                        azimuthTimestamp = []     

                        for di in azimuthTime:
                                azimuthTimestamp.append(datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S.%f").timestamp())
                        
                        for di in time:
                                timeorbit.append(datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S.%f").timestamp())

                        # Interpolation of average value
                        interp = LinearNDInterpolator(list(zip(longitude, latitude)), incidenceAngle)
                        incidenceAngle_target = interp(lon_target,lat_target)
                        # print(incidenceAngle_target)

                        interp = LinearNDInterpolator(list(zip(longitude, latitude)), azimuthTimestamp)
                        azimuthTimestamp_target = interp(lon_target,lat_target)
                        # print(azimuthTimestamp_target)

                        timeorbit, indices = np.unique(np.array(timeorbit), return_index=True)
                        orb_X_int = np.take(orb_X_int,indices)
                        orb_Y_int = np.take(orb_Y_int,indices)
                        orb_Z_int = np.take(orb_Z_int,indices)

                        # fi = interpolate.PchipInterpolator(timeorbit, orb_X_int)
                        # x_sat_target = fi(azimuthTimestamp_target)
                        # fi = interpolate.PchipInterpolator(timeorbit, orb_Y_int)
                        # y_sat_target = fi(azimuthTimestamp_target)
                        # fi = interpolate.PchipInterpolator(timeorbit, orb_Z_int)
                        # z_sat_target = fi(azimuthTimestamp_target)

                        fi = np.poly1d(np.polyfit(timeorbit, orb_X_int, constants.__orbit_poly_order__))
                        x_sat_target = fi(azimuthTimestamp_target)
                        fi = np.poly1d(np.polyfit(timeorbit, orb_Y_int, constants.__orbit_poly_order__))
                        y_sat_target = fi(azimuthTimestamp_target)
                        fi = np.poly1d(np.polyfit(timeorbit, orb_Z_int, constants.__orbit_poly_order__))   
                        z_sat_target = fi(azimuthTimestamp_target)
                        
                        para_sat['X'].append(x_sat_target)
                        para_sat['Y'].append(y_sat_target)
                        para_sat['Z'].append(z_sat_target)
                        para_sat['inc'].append(incidenceAngle_target)
                
                else: 
                        para_sat['process'].append(False)
                        usermessage.warningmsg(__name__,commputecoarsenetwork.__name__,__file__,'No intersection with the slice. NaN values will be used.',log,verbose)  

                        para_sat['X'].append(np.nan)
                        para_sat['Y'].append(np.nan)
                        para_sat['Z'].append(np.nan)
                        para_sat['inc'].append(np.nan)

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

        ## Computation of InSAR parameters 
        usermessage.ezprint('Computation of InSAR parameters:...',log,verbose)

        Bperp = []
        Btemp = []
        for h, di in enumerate(para_sat['dates']):
                if para_sat['process'][h] == True and h != idx_ref:

                        M = np.array((para_sat['X'][idx_ref],para_sat['Y'][idx_ref],para_sat['Z'][idx_ref]))
                        S = np.array((para_sat['X'][h],para_sat['Y'][h],para_sat['Z'][h]))
                        P = np.array((x_target,y_target,z_target))

                        R1 = np.linalg.norm(M - P)
                        R2 = np.linalg.norm(S - P)

                        B = np.linalg.norm(M - S)

                        # #R2^2 = R1^2 + B^2 - 2*R1*B*cos(angle)
                        # angletmp = np.rad2deg(np.arccos((R2**2 - R1**2 - B**2)/(-2*R1*B)))
                        # alpha = angletmp - (90-para_sat['inc'][h])
                        
                        # Bperpi = B * np.cos(np.deg2rad(para_sat['inc'][h]) - np.deg2rad(alpha))

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
        usermessage.ezprint('\tThis assumption is only valid for Sentinel-1 stack regarding the acquisitons and orbits parameters (and precisions).',log,verbose)

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

        print(dist)

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
