#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

##########################################################################################
# Header information 
###########################################################################

"""coarse_CSK_baselines.py: Script to compute the coarse network of interferograms and isolate the best candidate for the super single master"""

__author__ = "Alexis Hrysiewicz"
__copyright__ = "coarse_CSK_baselines.py is part of EZ-InSAR toolbox"
__credits__ = ["Alexis Hrysiewicz"]
__license__ = "GPLV3"
__version__ = "1.0.0 Beta"
__maintainer__ = "Alexis Hrysiewicz"
__email__ = "alexis.hrysiewicz@ucd.ie"
__status__ = "Production"
__date__ = "Jul. 2022"

print("****************************************************************************************************************************")
print("coarse_CSK_baselines.py: Script to compute the coarse network of interferograms and isolate the best candidate for the super single master using COSMO-SkyMed data")
print("****************************************************************************************************************************")

###########################################################################
# Python packages
###########################################################################

from cmath import pi
import sys
import os
import os.path
import optparse
import numpy as np
import fiona
import rasterio as rio
import matplotlib.pyplot as plt
from math import ceil
import pyproj
from rasterio import features
from rasterio import windows
import datetime
import xml.etree.ElementTree as ET
import scipy.io
from scipy import interpolate
from scipy.interpolate import LinearNDInterpolator
import glob
import h5py

###########################################################################
class OptionParser (optparse.OptionParser):
    def check_required(self, opt):
        option = self.get_option(opt)
        if getattr(self.values, option.dest) is None:
            self.error("%s option not supplied" % option)
###########################################################################
if '-h' in sys.argv or '--help' in sys.argv:
    print("example: python3 %s -d ./work_directory -r vv -e DEM -f yes [-a YYYYMMDD]" %
          sys.argv[0])
    print("or\nexample: python3 %s -h [--help]" % sys.argv[0])
    print('HELP:')
    print('\t-d [--directory]: work directory of MIESAR')
    print('\t-r [--radar]: selection of polarisation (vv or hh)')
    print('\t-e [--elev]: define the elevation of target point (integer or "DEM"). If this value is a number, it will be the elevation value; if this value is DEM, an average elevation will be computed from the DEM, according the target polygon stored in the kml file.')
    print('\t-f [--figure]: yes or no, to display the figure at the end of computation.')
    print('\t-a [--ref]: Pre-selection of reference date.')

    print('\nWARNING: The target point will be the average point in the polygon given by the kml file!')
    print('\nWARNING: The results are qualitative and can vary due to the accuracy of orbits and the sampling. Please, use the networks from ISCE or MintPy during the next steps.')

    sys.exit(-1)

if len(sys.argv) < 8:
    prog = os.path.basename(sys.argv[0])
    print("example: python3 %s -d ./work_directory -r vv -e DEM -f yes [-a YYYYMMDD]" %
          sys.argv[0])
    print("or\nexample: python3 %s -d ./work_directory -r vv -e DEM -f yes [-a YYYYMMDD]" %
          sys.argv[0])
    print("or\nexample: python3 %s -h [--help]" % sys.argv[0])
    sys.exit(-1)
else:
    usage = "usage: %prog [options] "
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--directory", dest="pathWK", action="store", type="string", default='.')      
    parser.add_option("-r", "--radar", dest="pol", action="store", type="string", default='vv')                 
    parser.add_option("-e", "--elev", dest="elev", action="store", type="string", default='DEM') 
    parser.add_option("-f", "--figure", dest="figure", action="store", type="string", default='yes')  
    parser.add_option("-a", "--ref", dest="ref", action="store", type="string", default='None')        
    (options, args) = parser.parse_args()

###########################################################################
# Variable definition from option users
###########################################################################
print('Read the path information and parameters')

path_WK = options.pathWK
mode_elevetation = options.elev #or elevation value

# Read the SLC path
parmsSLC = scipy.io.loadmat(path_WK+'/parmsSLC.mat')
path_SLC = parmsSLC['pathSLC'][0]

print('\t\tDone')

###########################################################################
# Read the kml 
###########################################################################

print('Read the kml file to define the ROI: ')

print('WARNING: The target point will be the average point in the polygon given by the kml file!')

try:
    fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
except:
    fiona.drvsupport.supported_drivers['KML'] = 'rw'

c = fiona.open(path_WK+'/target.kml')
print( c.schema['geometry'])
if c.schema['geometry'] == '3D Polygon':
    coords = [np.array(poly['geometry']['coordinates']) for poly in c.values()][0][0]
elif c.schema['geometry'] == '3D LineString':
    coords = [np.array(poly['geometry']['coordinates']) for poly in c.values()][0]
else:
    print('WARNING: The .kml type is %s, so we try to read the coordinates.' % (c.schema['geometry']))
    coords = [np.array(poly['geometry']['coordinates']) for poly in c.values()][0][0]
lon_target = []
lat_target = []
for pt in coords:
    lon_target.append(pt[0])
    lat_target.append(pt[1])
print('WARNING: The target point will be the center point in the SLC image!')

# Extraction of elevation 
if mode_elevetation == 'DEM':
    #Read the DEM 
    print('\tRead the path of DEM files: elevation from DEM')
    with open(path_WK+'/DEM_files.txt') as f:
        path_DEM = f.readlines()
    path_DEM = path_DEM[0]

    dem = rio.open(path_DEM)
    dem_array = dem.read(1).astype('float64')

    with fiona.open(path_WK+'/target.kml', "r") as shapefile:
        shapes = [feature["geometry"] for feature in shapefile]

    bound_1 = features.bounds(shapes[0])
    bbox_1 = windows.from_bounds(*bound_1, dem.transform)

    window_transform1 = rio.windows.transform(window=bbox_1, transform=dem.transform)
    mask = rio.features.geometry_mask([shapes[0]],out_shape=(ceil(bbox_1.width), ceil(bbox_1.height)), 
                                       transform=window_transform1, invert=True)
    img_crop = dem.read(1, window=bbox_1)

    # Need to modify
    elev_target = np.mean(img_crop)
    print('\t\tThe average elevation is %f meter from the kml file and DEM files.' %(elev_target))
else:
    print('\tElevation from user')
    elev_target = float(mode_elevetation)
    print('\t\tThe user-defined average elevation is %f meter(s).' %(elev_target))

lon_target = np.mean(np.array(lon_target))
lat_target = np.mean(np.array(lat_target))

print('\tThe average target point is located at %f lat and %f lon. ' % (lat_target, lon_target))

# Conversion of lon,lat coord to ECEF (for the target)
transformer = pyproj.Transformer.from_crs(
    {"proj":'latlong', "ellps":'WGS84', "datum":'WGS84'},
    {"proj":'geocent', "ellps":'WGS84', "datum":'WGS84'},
    )
x_target, y_target, z_target = transformer.transform(lon_target,lat_target,elev_target,radians = False)
print('\tConversion of lat/lon coordinates to ECEF coordinates. ')

print('\t\tDone')

###########################################################################
# # Read the satellite parameters for each acquisition
# ###########################################################################
para_sat = {'dates' : [],'Xsat' : [], 'Ysat' : [], 'Zsat' : [], 'incsat' : [], 'Xtarget' : [], 'Ytarget' : [], 'Ztarget' : []}

print('Extraction of satellites parameters from the header files:')

with open(path_WK+'/SLC.list','r') as listslc:
    for fi in listslc:
        pathh5 = path_SLC + '/' + fi.split()[0] + '/' + fi.split()[3]

        f = h5py.File(pathh5, 'r')

        # Read the date
        date_slc = f['/'].attrs['Scene Sensing Start UTC'].decode("utf-8")
        print(date_slc)

        # Read the edge points
        tmp1 = f['/S01/SBI'].attrs['Bottom Left Geodetic Coordinates']
        tmp2 = f['/S01/SBI'].attrs['Bottom Right Geodetic Coordinates']
        tmp3 = f['/S01/SBI'].attrs['Top Left Geodetic Coordinates']
        tmp4 = f['/S01/SBI'].attrs['Top Right Geodetic Coordinates']

        lon = [tmp1[1],tmp2[1], tmp3[1], tmp4[1]]
        lat = [tmp1[0],tmp2[0], tmp3[0], tmp4[0]]

        t1 = f['/S01/SBI'].attrs['Zero Doppler Azimuth First Time']
        t2 = f['/S01/SBI'].attrs['Zero Doppler Azimuth Last Time']

        times = [t2,t2,t1,t1]

        # Interpolation of time for the target point
        interp = LinearNDInterpolator(list(zip(lon,lat)), times)
        azimuthTimestamp_target = interp(lon_target,lat_target)
        # print(azimuthTimestamp_target)

        # Read the orbits
        data_orbits = dict()
        data_orbits['time'] = f['/'].attrs['State Vectors Times']
        tmp = f['/'].attrs['ECEF Satellite Position']

        data_orbits['orb_X_int'] = [i[0] for i in tmp]
        data_orbits['orb_Y_int'] = [i[1] for i in tmp]
        data_orbits['orb_Z_int'] = [i[2] for i in tmp]

        # Interpolation of orbits 
        azimuthTimestamp_orbit = data_orbits['time']

        fi = interpolate.PchipInterpolator(azimuthTimestamp_orbit, data_orbits['orb_X_int'])
        x_sat_target = fi(azimuthTimestamp_target)
        # print(x_sat_target)
        fi = interpolate.PchipInterpolator(azimuthTimestamp_orbit, data_orbits['orb_Y_int'])
        y_sat_target = fi(azimuthTimestamp_target)
        # print(y_sat_target)
        fi = interpolate.PchipInterpolator(azimuthTimestamp_orbit, data_orbits['orb_Z_int'])
        z_sat_target = fi(azimuthTimestamp_target)
        # print(z_sat_target)

        # Save
        para_sat['dates'].append(datetime.datetime.strptime(datetime.datetime.strftime(datetime.datetime.strptime(date_slc[:-3],"%Y-%m-%d %H:%M:%S.%f"),'%Y-%m-%d'),"%Y-%m-%d"))
        para_sat['Xsat'].append(x_sat_target)
        para_sat['Ysat'].append(y_sat_target)
        para_sat['Zsat'].append(z_sat_target)
        para_sat['Xtarget'].append(x_target)
        para_sat['Ytarget'].append(y_target)
        para_sat['Ztarget'].append(z_target)

print('\t\t\tDone')

###########################################################################
# Fake best reference date from computation
###########################################################################
if not options.ref == 'None':
    print('The user selected a reference date: %s' %(options.ref))
    idx_ref = np.where(np.array(para_sat['dates']) == datetime.datetime.strptime(options.ref,"%Y%m%d"))[0]
    if idx_ref.size == 0:
        idx_ref = 0
        print('\tError: the selected date is not in the SLC dates.')
    else:
        idx_ref = idx_ref[0]
else:
    print('The user did not select a reference date.')
    idx_ref = 0

###########################################################################
# Computation of InSAR parameters 
###########################################################################
print('Computation of InSAR parameters: ')

Bperp = []
Btemp = []
h = 0 
for di in para_sat['dates']:
    if h != idx_ref:

        M = np.array((para_sat['Xsat'][idx_ref],para_sat['Ysat'][idx_ref],para_sat['Zsat'][idx_ref]))
        S = np.array((para_sat['Xsat'][h],para_sat['Ysat'][h],para_sat['Zsat'][h]))
        P = np.array((para_sat['Xtarget'][h],para_sat['Ytarget'][h],para_sat['Ysat'][h]))

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

        Btempi = (para_sat['dates'][idx_ref].timestamp() - para_sat['dates'][h].timestamp()) / (24*3600)
        
    elif h == idx_ref:
        Bperpi = 0
        Btempi = 0
    else:
        Bperpi = np.nan
        Btempi = np.nan

    #Save
    Bperp.append(Bperpi)
    Btemp.append(Btempi)

    h = h + 1

print('\t\t\tDone')

###########################################################################
# Detection of the best potential reference using geometric barycentre
###########################################################################
print('Detection of the best potential reference using geometric barycentre ... ')

dates_slc_sec = []
for di in para_sat['dates']:
    dates_slc_sec.append(di.timestamp())

dates_mean = np.nanmean(dates_slc_sec)
Bperpmean = np.nanmean(Bperp)

a = (dates_slc_sec-np.nanmin(dates_slc_sec))/(np.nanmax(dates_slc_sec) - np.nanmin(dates_slc_sec))
ab =(dates_mean-np.nanmin(dates_slc_sec))/(np.nanmax(dates_slc_sec) - np.nanmin(dates_slc_sec))

b = (Bperp-np.nanmin(Bperp))/(np.nanmax(Bperp) - np.nanmin(Bperp))
bb = (Bperpmean-np.nanmin(Bperp))/(np.nanmax(Bperp) - np.nanmin(Bperp))

dist = np.sqrt( (a - ab)**2 + (b - bb)**2 )
idx_best_ref = np.nanargmin(dist)

###########################################################################
# Display the results
###########################################################################
print('-------------------------------------------')
print('Results:')
print('\tThe best potential reference date should be:')
print('\t\t %s' %(datetime.datetime.strftime(para_sat['dates'][idx_best_ref],'%Y-%m-%d')))
print('\t\t Please, you can use the value of %s for the next processing.' %(datetime.datetime.strftime(para_sat['dates'][idx_best_ref],'%Y%m%d')))
print('\t\t WARNING: according to the previous assumptions...')
print('\nWARNING: The results are qualitative and can vary due to the accuracy of orbits and the sampling. Please, use the networks from ISCE or MintPy during the next steps.')

###########################################################################
# Plotting
###########################################################################
plt.scatter(para_sat['dates'], np.array(Bperp), c="black", label="SAR Acquisitions")
plt.scatter(para_sat['dates'][idx_best_ref], Bperp[idx_best_ref], c="red", label="Best Potential Reference Date")
plt.scatter(para_sat['dates'][idx_ref], Bperp[idx_ref], marker='1', c="blue", label="Selected Reference Date")
plt.xlabel("Time")
plt.ylabel("Bperp [m]")
plt.legend(loc='best')
plt.title('Coarse network of interferograms. Reference date: %s' %(datetime.datetime.strftime(para_sat['dates'][idx_best_ref],'%Y-%m-%d')))
plt.savefig(path_WK+'/coarse_ifg_network.jpg', dpi=450)
plt.savefig(path_WK+'/coarse_ifg_network.pdf', dpi=450)

print('Please, visualise the network with the figure in: \n\t%s' %(path_WK+'/coarse_ifg_network.jpg'))
print('-------------------------------------------')

if options.figure == 'yes':
    plt.show()

print("****************************************************************************************************************************")
print("Computation over.")
print("****************************************************************************************************************************")
