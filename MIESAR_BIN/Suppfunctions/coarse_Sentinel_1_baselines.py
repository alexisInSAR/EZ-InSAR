#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

##########################################################################################
# Header information 
###########################################################################

"""coarse_Sentinel_1_baselines.py: Script to compute the coarse network of interferograms and isolate the best candidate for the super single master"""

__author__ = "Alexis Hrysiewicz"
__copyright__ = "Copyright 2022"
__credits__ = ["Alexis Hrysiewicz"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Alexis Hrysiewicz"
__email__ = "alexis.hrysiewicz@ucd.ie"
__status__ = "Production"
__date__ = "Mar. 2022"

print("****************************************************************************************************************************")
print("coarse_Sentinel_1_baselines.py: Script to compute the coarse network of interferograms and isolate the best candidate for the super single master")
print("****************************************************************************************************************************")

###########################################################################
# Python packages
###########################################################################

import sys
import os
import os.path
import optparse
import numpy as np
import shutil
import fiona
from shapely.geometry import Point
import rasterio as rio
import matplotlib.pyplot as plt
from math import ceil
import pyproj
from rasterio import features
from rasterio import windows
import datetime
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import scipy.io
from scipy import interpolate
from scipy.interpolate import LinearNDInterpolator
import urllib.request
import re


###########################################################################
class OptionParser (optparse.OptionParser):
    def check_required(self, opt):
        option = self.get_option(opt)
        if getattr(self.values, option.dest) is None:
            self.error("%s option not supplied" % option)
###########################################################################
if '-h' in sys.argv or '--help' in sys.argv:
    print("example: python3 %s -d ./work_directory -r vv -e DEM -m None -u XXXXXX -p XXXXXX -o ./orbits -f yes [-a YYYYMMDD]" %
          sys.argv[0])
    print("or\nexample: python3 %s -d ./work_directory -r vv -e DEM -f yes [-a YYYYMMDD]" %
          sys.argv[0])
    print("or\nexample: python3 %s -h [--help]" % sys.argv[0])
    print('HELP:')
    print('\t-d [--directory]: work directory of MIESAR')
    print('\t-r [--radar]: selection of polarisation (vv or hh)')
    print('\t-e [--elev]: define the elevation of target point (integer or "DEM"). If this value is a number, it will be the elevation value; if this value is DEM, an average elevation will be computed from the DEM, according the target polygon stored in the kml file.')
    print('\t-m [--mode]: None or POD, POD will allow the computation using precise orbites')
    print('\t-u [--user]: username for https://s1qc.asf.alaska.edu')
    print('\t-p [--password]: password for https://s1qc.asf.alaska.edu')
    print('\t-o [--orbits]: path of orbit files')
    print('\t-f [--figure]: yes or no, to display the figure at the end of computation.')
    print('\t-a [--ref]: Pre-selection of reference date.')

    print('\nWARNING: The target point will be the average point in the polygon given by the kml file!')
    print('\nWARNING: The results are qualitative and can vary due to the accuracy of orbits and the sampling. Please, use the networks from ISCE or MintPy during the next steps.')

    sys.exit(-1)

if len(sys.argv) < 8:
    prog = os.path.basename(sys.argv[0])
    print("example: python3 %s -d ./work_directory -r vv -e DEM -m None -u XXXXXX -p XXXXXX -o ./orbits -f yes [-a YYYYMMDD]" %
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
    parser.add_option("-m", "--mode", dest="mode", action="store", type="string", default='None')  
    parser.add_option("-u", "--user", dest="user", action="store", type="string", default='')  
    parser.add_option("-p", "--password", dest="password", action="store", type="string", default='')  
    parser.add_option("-o", "--orbits", dest="orbits", action="store", type="string", default='./orbits')  
    parser.add_option("-f", "--figure", dest="figure", action="store", type="string", default='yes')  
    parser.add_option("-a", "--ref", dest="ref", action="store", type="string", default='None')        
    (options, args) = parser.parse_args()

###########################################################################
# Functions 
###########################################################################

# Function to read the xml files
def read_annotation_xml(path_xml): 
    xmlfileslc = ET.parse(path_xml)

    data_xml = dict()
    data_xml['azimuthTime'] = []
    data_xml['slantRangeTime'] = []
    data_xml['line'] = []
    data_xml['pixel'] = []
    data_xml['latitude'] = []
    data_xml['longitude'] = []
    data_xml['height'] = []
    data_xml['incidenceAngle'] = []
    data_xml['elevationAngle'] = []
    data_xml['Xtrack_f_DC'] = []

    for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/azimuthTime'):
        data_xml['azimuthTime'].append(nodes.text)
    for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/slantRangeTime'):
        data_xml['slantRangeTime'].append(nodes.text)
    for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/line'):
        data_xml['line'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/pixel'):
        data_xml['pixel'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/latitude'):
        data_xml['latitude'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/longitude'):
        data_xml['longitude'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/height'):
        data_xml['height'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/incidenceAngle'):
        data_xml['incidenceAngle'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/elevationAngle'):
        data_xml['elevationAngle'].append(float(nodes.text))

    data_orbits = dict()
    data_orbits['time'] = []
    data_orbits['orb_X_int'] = []
    data_orbits['orb_Y_int'] = []
    data_orbits['orb_Z_int'] = []
    data_orbits['orb_VX_int'] = []
    data_orbits['orb_VY_int'] = []
    data_orbits['orb_VZ_int'] = []

    for nodes in xmlfileslc.findall('.//generalAnnotation/orbitList/orbit/time'): 
        data_orbits['time'].append(nodes.text)
    for nodes in xmlfileslc.findall('.//generalAnnotation/orbitList/orbit/position/x'): 
        data_orbits['orb_X_int'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//generalAnnotation/orbitList/orbit/position/y'): 
        data_orbits['orb_Y_int'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//generalAnnotation/orbitList/orbit/position/z'): 
        data_orbits['orb_Z_int'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//generalAnnotation/orbitList/orbit/velocity/x'): 
        data_orbits['orb_VX_int'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//generalAnnotation/orbitList/orbit/velocity/y'): 
        data_orbits['orb_VY_int'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//generalAnnotation/orbitList/orbit/velocity/z'): 
        data_orbits['orb_VZ_int'].append(float(nodes.text))

    return data_xml, data_orbits

def read_precise_restitued_xml(path_xml): 
    xmlfileslc = ET.parse(path_xml)

    data_orbits = dict()
    data_orbits['time'] = []
    data_orbits['orb_X_int'] = []
    data_orbits['orb_Y_int'] = []
    data_orbits['orb_Z_int'] = []
    data_orbits['orb_VX_int'] = []
    data_orbits['orb_VY_int'] = []
    data_orbits['orb_VZ_int'] = []

    for nodes in xmlfileslc.findall('.//Data_Block/List_of_OSVs/OSV/UTC'): 
        data_orbits['time'].append(nodes.text.split('=')[1])
    for nodes in xmlfileslc.findall('.//Data_Block/List_of_OSVs/OSV/X'): 
        data_orbits['orb_X_int'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//Data_Block/List_of_OSVs/OSV/Y'): 
        data_orbits['orb_Y_int'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//Data_Block/List_of_OSVs/OSV/Z'): 
        data_orbits['orb_Z_int'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//Data_Block/List_of_OSVs/OSV/VX'): 
        data_orbits['orb_VX_int'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//Data_Block/List_of_OSVs/OSV/VY'): 
        data_orbits['orb_VY_int'].append(float(nodes.text))
    for nodes in xmlfileslc.findall('.//Data_Block/List_of_OSVs/OSV/VZ'): 
        data_orbits['orb_VZ_int'].append(float(nodes.text))

    return data_orbits

def find(lst, predicate):
    return (i for i, j in enumerate(lst) if predicate(j)).next()

###########################################################################
# Variable definition from option users
###########################################################################
print('Read the path information and parameters')

path_WK = options.pathWK

pol = options.pol.upper()
if pol == 'VV':
    key_pol = '_1SDV_'
else:
    key_pol = '_1SSV_'

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

# Extraction of coordinates
# gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
# gdf = gpd.read_file(path_WK+'/target.kml', driver='KML')

# lon_target = []
# lat_target = []
# for index, row in gdf.iterrows():
#      for pt in list(row['geometry'].exterior.coords): 
#         a = Point(pt)
#         lon_target.append(a.x)
#         lat_target.append(a.y)

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
# Read the list of SLCs to extract the unique dates
###########################################################################
print('Read the SLC list:')

with open(path_WK+'/SLC.list') as f:
        list_SLC = []
        dates_SLC = []
        list_pol = []
        sat_list = []
        for line in f:
            p = line.split()
            list_SLC.append(p[0])
            dates_SLC.append(p[1])
            list_pol.append(p[5])
            if 'S1A' in line:
                sat_list.append("S1A")
            elif 'S1B' in line:
                sat_list.append("S1B")

dates_unique = []
for di in dates_SLC:
    a = datetime.datetime.strptime(datetime.datetime.strftime(datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S.%f"),'%Y-%m-%d'),"%Y-%m-%d")
    dates_unique.append(a)
dates_unique = np.unique(dates_unique)

print('\t\t\tDone')

###########################################################################
# Download the precice orbites (or restitued) 
###########################################################################
if options.mode == 'POD':
    print('Mode of orbits: we will use the precise (or restitued) orbits, if available.')

    #Checking of precise orbites
    print('\tConnection to https://s1qc.asf.alaska.edu/aux_poeorb/ server to check the precise orbites...')

    url_precise = "https://s1qc.asf.alaska.edu/aux_poeorb/"
    html = urllib.request.urlopen(url_precise)
    text = html.read()
    plaintext = text.decode('utf8')
    links = re.findall("href=[\"\'](.*?)[\"\']", plaintext)
    orbits_precise = []
    for li in links:
        if ".EOF" in li:
            orbits_precise.append(li)
    print('\t\t\tDone')

    #Checking of restitued orbites
    print('\tConnection to https://s1qc.asf.alaska.edu/aux_resorb/ server to check the restitued orbites...')

    url_restitued = "https://s1qc.asf.alaska.edu/aux_resorb/"
    html = urllib.request.urlopen(url_restitued)
    text = html.read()
    plaintext = text.decode('utf8')
    links = re.findall("href=[\"\'](.*?)[\"\']", plaintext)
    orbits_restitued = []
    for li in links:
        if ".EOF" in li:
            orbits_restitued.append(li)
    print('\t\t\tDone')

    # Modification of list 
    print('\tOrganisation of SLC lists to download the orbits')
    dateslcorbits = []
    for di in dates_SLC:
        a = datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S.%f")
        dateslcorbits.append(a)

    # Creation of list to download
    orbits_name = []
    fi = open('tmp_download.txt','w')
    date_format = "%Y%m%dT%H%M%S"
    check_download = False
    for i in range(len(dateslcorbits)):
        if os.path.isfile(path_SLC+'/'+list_SLC[i]+'.zip') or os.path.isfile(path_SLC+'/'+list_SLC[i]+'.SAFE'):
            dslc = dateslcorbits[i]
            sati = sat_list[i]
            print('\tChecking of orbits for %s SLC acquired by %s' % (dslc,sati))
            check_precise=False
            check_restitued=False
            name_orbit_precise = []
            name_orbit_restitued = []
            for pi in orbits_precise:
                if sati in pi: 
                    orb_test = pi.split('V')[1].split('.')[0]
                    d1 = datetime.datetime.strptime(orb_test.split('_')[0], date_format)
                    d2 = datetime.datetime.strptime(orb_test.split('_')[1], date_format)
                    if d1 <= dslc <= d2:
                        check_precise=True
                        name_orbit_precise.append(pi)
            name_orbit_precise = name_orbit_precise[-1] #Modification to have the last files
            if check_precise:
                name_orbit_precise
                print('\t\tThe precise orbit %s has been found.' % (name_orbit_precise))
                orbits_name.append(name_orbit_precise)
            else:
                print('\t\tNo precise orbit has been found, checking of restitued orbit...')
                for pi in orbits_restitued:
                    if sati in pi: 
                        orb_test = pi.split('V')[1].split('.')[0]
                        d1 = datetime.datetime.strptime(orb_test.split('_')[0], date_format)
                        d2 = datetime.datetime.strptime(orb_test.split('_')[1], date_format)
                        if d1 <= dslc <= d2:
                            check_restitued=True
                            name_orbit_restitued.append(pi)
                if check_restitued:
                    name_orbit_restitued = name_orbit_restitued[-1]
                    orbits_name.append(name_orbit_restitued)
                    print('\tThe restitued orbit %s has been found.' % (name_orbit_restitued))
                else:
                    orbits_name.append('None')
            if check_precise:
                if not os.path.isfile(options.orbits+'/'+name_orbit_precise): 
                    check_download = True
                    # cmd = "wget --user %s --password %s -P %s %s" % (options.user,options.password,options.orbits,url_precise+name_orbit_precise)
                    # print(cmd)
                    print('\t\t\tNeed to be downloaded.')
                    fi.write(url_precise+name_orbit_precise+'\n')
                else:
                    print('\t\t\tAlready downloaded.')
            if check_restitued:
                ni = name_orbit_restitued
                if not os.path.isfile(options.orbits+'/'+name_orbit_restitued): 
                    check_download = True
                    # cmd = "wget --user %s --password %s -P %s %s" % (options.user,options.password,options.orbits,url_restitued+name_orbit_restitued)
                    # print(cmd)
                    fi.write(url_restitued+name_orbit_restitued+'\n')
                    print('\t\t\tNeed to be downloaded.')
                else:
                    print('\t\t\tAlready downloaded.')
        else:
            orbits_name.append('None')
    fi.close()

    #Download the orbits
    if check_download == True:
        cmd = "wget --user %s --password %s -P %s -i %s -nc" % (options.user,options.password,options.orbits,'tmp_download.txt')
        os.system(cmd)
    os.remove('tmp_download.txt')
else:
    print('Mode of orbits: we will use the orbites inside the slices.')

###########################################################################
# Read the satellite parameters for each acquisition
###########################################################################
para_sat = {'dates' : [],'nb_slice' : [],'process' : [], 'X' : [], 'Y' : [], 'Z' : [], 'inc' : []}

print('Extraction of satellites parameters from the xml files:')

for di in dates_unique:

    para_sat['dates'].append(di)

    distr = datetime.datetime.strftime(di,'%Y%m%d')
    
    #Seach the correct slide(s)
    matches = [match for match in list_SLC if distr in match]

    # print('There is/are %d slices for this date' % (len(matches)))
    para_sat['nb_slice'].append(len(matches))

    #Check if the files are downloaded
    testdw = 0
    ext = []
    for slci in matches:
        if os.path.isfile(path_SLC+'/'+slci+'.zip') and (key_pol in slci) and os.path.isfile(path_SLC+'/'+slci+'.SAFE'):
            testdw = testdw + 1
            ext.append('.SAFE')
        else:
            if os.path.isfile(path_SLC+'/'+slci+'.zip') and (key_pol in slci):
                testdw = testdw + 1
                ext.append('.zip')
            elif os.path.isfile(path_SLC+'/'+slci+'.SAFE') and (key_pol in slci):
                testdw = testdw + 1
                ext.append('.SAFE')

    if testdw == len(matches):
        para_sat['process'].append(True)
    else:
        para_sat['process'].append(False)
        para_sat['X'].append(np.nan)
        para_sat['Y'].append(np.nan)
        para_sat['Z'].append(np.nan)
        para_sat['inc'].append(np.nan)

    #Extraction of parameters
    if testdw == len(matches):
        h = 0 

        azimuthTime = []
        slantRangeTime = []
        line = []
        pixel = []
        latitude = []
        longitude = []
        height = []
        incidenceAngle = []
        elevationAngle = []
        Xtrack_f_DC = []

        time = []
        orb_X_int = []
        orb_Y_int = []
        orb_Z_int = []
        orb_VX_int = []
        orb_VY_int = []
        orb_VZ_int = []

        for slci in matches:

            #Check the POD orbits
            if options.mode == 'POD':
                id_orbit = [i for i, s in enumerate(list_SLC) if slci in s][0]
                slcorbiti = orbits_name[id_orbit]
            else:
                slcorbiti = 'None'
            
            #Detection of paths 
            if ext[h] == '.zip':
                with ZipFile(path_SLC + '/' + slci + ext[h], 'r') as zipObj:
                    listOfFileNames = zipObj.namelist()
                    # print(listOfFileNames)
                    for entry in listOfFileNames: 
                        if "annotation" in entry:
                            if (pol.lower() in entry) and ('iw1' in entry) and (not 'calibration' in entry) and (not 'noise' in entry):
                                path_xml_IW1 = entry
                            if (pol.lower() in entry) and ('iw2' in entry) and (not 'calibration' in entry) and (not 'noise' in entry):
                                path_xml_IW2 = entry
                            if (pol.lower() in entry) and ('iw3' in entry) and (not 'calibration' in entry) and (not 'noise' in entry):
                                path_xml_IW3 = entry

                    zipObj.extract(path_xml_IW1, path='tmp', pwd=None)      
                    zipObj.extract(path_xml_IW2, path='tmp', pwd=None)     
                    zipObj.extract(path_xml_IW3, path='tmp', pwd=None)  

                    shutil.copy2('tmp/'+path_xml_IW1,'tmp_IW1.xml')
                    shutil.copy2('tmp/'+path_xml_IW2,'tmp_IW2.xml')
                    shutil.copy2('tmp/'+path_xml_IW3,'tmp_IW3.xml')

                    shutil.rmtree('tmp')
            else:
                listOfFiles = os.listdir(path_SLC + '/' + slci + ext[h]+"/annotation") 
                for entry in listOfFiles:
                    if (pol.lower() in entry) and ('iw1' in entry) and (not 'calibration' in entry) and (not 'noise' in entry):
                        path_xml_IW1 = entry
                    if (pol.lower() in entry) and ('iw2' in entry) and (not 'calibration' in entry) and (not 'noise' in entry):
                        path_xml_IW2 = entry
                    if (pol.lower() in entry) and ('iw3' in entry) and (not 'calibration' in entry) and (not 'noise' in entry):
                        path_xml_IW3 = entry

                shutil.copy2(path_xml_IW1,'tmp_IW1.xml')
                shutil.copy2(path_xml_IW2,'tmp_IW2.xml')
                shutil.copy2(path_xml_IW3,'tmp_IW3.xml')

            h = h + 1

            # 
            print('We process the %s file.' % (slci+ext[h-1]))

            #Open the xml
            data_xmli1, data_orbitsi1  = read_annotation_xml('tmp_IW1.xml') 
            data_xmli2, data_orbitsi2  = read_annotation_xml('tmp_IW2.xml') 
            data_xmli3, data_orbitsi3  = read_annotation_xml('tmp_IW3.xml') 

            os.remove('tmp_IW1.xml') 
            os.remove('tmp_IW2.xml') 
            os.remove('tmp_IW3.xml') 

            #Save
            latitude = latitude + data_xmli1['latitude'] + data_xmli2['latitude'] + data_xmli3['latitude']
            longitude = longitude + data_xmli1['longitude'] + data_xmli2['longitude'] + data_xmli3['longitude']
            incidenceAngle = incidenceAngle + data_xmli1['incidenceAngle'] + data_xmli2['incidenceAngle'] + data_xmli3['incidenceAngle']
            azimuthTime = azimuthTime + data_xmli1['azimuthTime'] + data_xmli2['azimuthTime'] + data_xmli3['azimuthTime']
            azimuthTimestamp = []

            if options.mode == 'POD' and slcorbiti != 'None':
                if os.path.isfile(options.orbits+'/'+slcorbiti):
                    if 'RESORB' in slcorbiti:
                        print('\t We use the restitued orbit files.')    
                    else:
                        print('\t We use the precise orbit files.')
                    data_orbits = read_precise_restitued_xml(options.orbits+'/'+slcorbiti)
                    time = time + data_orbits['time']
                    orb_X_int = orb_X_int + data_orbits['orb_X_int']
                    orb_Y_int = orb_Y_int + data_orbits['orb_Y_int'] 
                    orb_Z_int = orb_Z_int + data_orbits['orb_Z_int']
                else:
                    print('\t ERROR with POD files: read the orbits in xml, so the accuracy is poor.')
                    time = time + data_orbitsi1['time'] + data_orbitsi2['time'] + data_orbitsi3['time']
                    orb_X_int = orb_X_int + data_orbitsi1['orb_X_int'] + data_orbitsi2['orb_X_int'] + data_orbitsi3['orb_X_int']
                    orb_Y_int = orb_Y_int + data_orbitsi1['orb_Y_int'] + data_orbitsi2['orb_Y_int'] + data_orbitsi3['orb_Y_int']
                    orb_Z_int = orb_Z_int + data_orbitsi1['orb_Z_int'] + data_orbitsi2['orb_Z_int'] + data_orbitsi3['orb_Z_int'] 
            else:
                print('\t We use the orbit files in xml, so the accuracy is poor.')
                time = time + data_orbitsi1['time'] + data_orbitsi2['time'] + data_orbitsi3['time']
                orb_X_int = orb_X_int + data_orbitsi1['orb_X_int'] + data_orbitsi2['orb_X_int'] + data_orbitsi3['orb_X_int']
                orb_Y_int = orb_Y_int + data_orbitsi1['orb_Y_int'] + data_orbitsi2['orb_Y_int'] + data_orbitsi3['orb_Y_int']
                orb_Z_int = orb_Z_int + data_orbitsi1['orb_Z_int'] + data_orbitsi2['orb_Z_int'] + data_orbitsi3['orb_Z_int']        

            timeorbit = []

        for di in azimuthTime:
            azimuthTimestamp.append(datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S.%f").timestamp())
            
        for di in time:
            timeorbit.append(datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S.%f").timestamp())

        # # plotting
        # plt.scatter(longitude,latitude,c=azimuthTimestamp)
        # plt.plot(lon_target,lat_target,c='red',marker=">")
        # plt.show()

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

        fi = interpolate.PchipInterpolator(timeorbit, orb_X_int)
        x_sat_target = fi(azimuthTimestamp_target)
        # print(x_sat_target)
        fi = interpolate.PchipInterpolator(timeorbit, orb_Y_int)
        y_sat_target = fi(azimuthTimestamp_target)
        # print(y_sat_target)
        fi = interpolate.PchipInterpolator(timeorbit, orb_Z_int)
        z_sat_target = fi(azimuthTimestamp_target)
        # print(z_sat_target)

        para_sat['X'].append(x_sat_target)
        para_sat['Y'].append(y_sat_target)
        para_sat['Z'].append(z_sat_target)
        para_sat['inc'].append(incidenceAngle_target)

print('\t\t\tDone')

###########################################################################
# Fake best reference date from computation
###########################################################################
if not options.ref == 'None':
    print('The user selected a reference date: %s' %(options.ref))
    idx_ref = np.where(dates_unique == datetime.datetime.strptime(options.ref,"%Y%m%d"))[0]
    if idx_ref.size == 0:
        idx_ref = np.min(np.where(np.array(para_sat['process']) == True))
        print('\tError: the selected date is not in the SLC dates.')
    else:
        idx_ref = idx_ref[0]
    if para_sat['process'][idx_ref] == False:
        idx_ref = np.min(np.where(np.array(para_sat['process']) == True))
        print('\tError: the selected date is not processed.')
else:
    print('The user did not select a reference date.')
    idx_ref = np.min(np.where(np.array(para_sat['process']) == True))
# idx_ref = np.median(np.where(np.array(para_sat['process']) == True)).astype('int')
# idx_ref = np.max(np.where(np.array(para_sat['process']) == True))

###########################################################################
# Computation of InSAR parameters 
###########################################################################
print('Computation of InSAR parameters: ')

Bperp = []
Btemp = []
h = 0 
for di in para_sat['dates']:
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

        Btempi = (para_sat['dates'][idx_ref].timestamp() - para_sat['dates'][h].timestamp()) / (24*3600)
        
    elif para_sat['process'][h] == True and h == idx_ref:
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
print('\t\tThis assumption is only valid for Sentinel-1 stack regarding the acquisitons and orbits parameters (and precisions)')

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
