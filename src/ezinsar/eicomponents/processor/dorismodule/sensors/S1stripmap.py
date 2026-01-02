#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to import Sentinel-1 StriMap data with Doris processor 

The module allows to import Sentinel-1 StripMap data with Doris processor from an ``ezinsar.coregistration`` job. 
    
    (From `ezinsar` package)

Changelog:
    * 1.2.1: Modification of the S1 reader, Oct. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import os 
from typing import Optional
import zipfile
import datetime
import xml.etree.ElementTree as ET
import numpy as np
from scipy.interpolate import LinearNDInterpolator
from shapely.wkt import loads
from scipy import interpolate
import shutil
import glob 
from osgeo import gdal

from ezinsar.eicomponents.sensor.s1module import s1slctools
from ezinsar.eicomponents.processor.dorismodule import doristools
from ezinsar import usermessage
from ezinsar import constants

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""
################################################################################
## Import a Sentinel-1 Stripmap image
################################################################################
def importS1SM(file,
        mode,
        modeorbit,
        pathorbit,
        prefixname, 
        outputdir, 
        polarisation, 
        cropping, 
        calibration, 
        roi,
        log, 
        verbose: Optional[bool] = None):
        """Import the Sentinel-1 StripMap image for Doris

        The function imports the Sentinel-1 StripMap image for Doris.  

        Args:

            file (str): path of the SLC file (.zip or .SAFE)
            mode (str): master or slave
            modeorbit (bool): Orbit mode
            pathorbit (str): path of the orbit files
            prefixname (str): name prefix for the naming of files 
            outputdir (str): path of the output directory
            polarisation (list of str): list of polarisation 
            cropping (any): cropping variable
            calibration (str): calibration mode
            roi (str): Region of Interest
            log (str): path of the log 
            verbose (bool): verbose [Default: `None`].

        """
        if (not os.path.isfile(file)) and (not os.path.isdir(file)):
            raise ValueError(usermessage.errormsg(__name__,importS1SM.__name__,__file__,__copyright__,
                    'The .zip or .SAFE file does not exist.',log))
        
        if not isinstance(prefixname,str):
            raise TypeError(usermessage.typeerrormsg(
                __name__,importS1SM.__name__,__file__,__copyright__,
                'prefixname','str',log))
        
        if not os.path.isdir(outputdir):
            raise ValueError(usermessage.errormsg(__name__,importS1SM.__name__,__file__,__copyright__,
                'The output directory does not exist.',log))
        
        if not isinstance(polarisation,list):
            raise TypeError(usermessage.typeerrormsg(
                __name__,importS1SM.__name__,__file__,__copyright__,
                'polarisation','list',log))

        if not calibration in [None,'beta0',
                                'beta0+noise',
                                'sigma0',
                                'sigma0+noise',
                                'gamma',
                                'gamma+noise',
                                'dn',
                                'dn+noise']:
            raise ValueError(usermessage.errormsg(__name__,importS1SM.__name__,__file__,__copyright__,
                'The calibration is not correct.',log))

        if not isinstance(verbose,bool):
            raise TypeError(usermessage.typeerrormsg(
                __name__,importS1SM.__name__,__file__,__copyright__,
                'verbose','True or False',log))

        usermessage.openingmsg(__name__,importS1SM.__name__,__file__,__copyright__,'Import Sentinel-1 StripMap data for Doris',log,verbose)

        usermessage.ezprint('Extraction of the image from %s using the EZ-InSAR built-in functions' % (file),log,verbose) 
        usermessage.ezprint('File: %s' % (file),log,verbose) 
        usermessage.ezprint('Mode: %s' % (mode),log,verbose) 
        usermessage.ezprint('Application of orbit files: %s' % (modeorbit),log,verbose) 
        usermessage.ezprint('Prefix: %s' % (prefixname),log,verbose) 
        usermessage.ezprint('Output directory: %s' % (outputdir),log,verbose) 
        usermessage.ezprint('Polarisation: %s' % (polarisation),log,verbose) 
        usermessage.ezprint('Cropping mode: %s' % (cropping),log,verbose) 
        usermessage.ezprint('Calibration mode: %s' % (calibration),log,verbose) 
        usermessage.ezprint('ROI: %s' % (roi),log,verbose) 
 
        ## Detection of files 
        fileslc = []
        fileann = []
        filecal = []
        filenoi = []

        # Extraction of the SLC files
        usermessage.ezprint('Detection and extraction of the required files:',log,verbose) 

        if "SAFE" in file:

            listOfFiles = os.listdir(file+os.sep+'measurement')
            for poli in polarisation:
                for entry in listOfFiles:
                    if poli.lower() in entry:
                        fileslc.append(file+"%smeasurement%s" % (os.sep,os.sep)+entry)

            listOfFiles = os.listdir(file+os.sep+'annotation')
            for poli in polarisation:
                for entry in listOfFiles:
                    if poli.lower() in entry:
                        fileann.append(file+"%sannotation%s" % (os.sep,os.sep)+entry)
 
            listOfFiles = os.listdir(file+os.sep+'annotation'+os.sep+'calibration')
            for poli in polarisation:
                for entry in listOfFiles:
                    if (poli.lower() in entry) and ('calibration-' in entry):
                        filecal.append(file+"%sannotation%scalibration%s" % (os.sep,os.sep,os.sep)+entry)

                    if (poli.lower() in entry) and ('noise-' in entry):
                        filenoi.append(file+"%sannotation%scalibration%s" % (os.sep,os.sep,os.sep)+entry)

        elif "zip" in file:

            with zipfile.ZipFile(file, 'r') as zipObj:
                listOfFileNames = zipObj.namelist()

                for poli in polarisation:
                    for entry in listOfFileNames: 
                        if "measurement" in entry:
                            if poli.lower() in entry:
                                fileslc.append(entry)
                        if "annotation" in entry and (not "calibration" in entry) and (not "rfi-" in entry):
                            if poli.lower() in entry:
                                fileann.append(entry)
                        if "annotation/calibration" in entry:
                            if (poli.lower() in entry) and ('calibration-' in entry):
                                filecal.append(entry)
                            if (poli.lower() in entry) and ('noise-' in entry):
                                filenoi.append(entry)

                usermessage.ezprint('Extraction from the .zip file (can take time)',log,verbose) 
                for idx, a in enumerate(fileslc): 
                    zipObj.extract(fileslc[idx], path="tmpslcextracted"+os.sep, pwd=None)
                    zipObj.extract(fileann[idx], path="tmpslcextracted"+os.sep, pwd=None)
                    zipObj.extract(filecal[idx], path="tmpslcextracted"+os.sep, pwd=None)
                    zipObj.extract(filenoi[idx], path="tmpslcextracted"+os.sep, pwd=None)
           
            # Replace the entry name 
            for idx, a in enumerate(fileslc): 
                fileslc[idx] = 'tmpslcextracted'+os.sep+file.split(os.sep)[-1].split('.')[0]+'.SAFE'+os.sep+'measurement'+os.sep+fileslc[idx].split(os.sep)[-1]
                fileann[idx] = 'tmpslcextracted'+os.sep+file.split(os.sep)[-1].split('.')[0]+'.SAFE'+os.sep+'annotation'+os.sep+fileann[idx].split(os.sep)[-1]
                filecal[idx] = 'tmpslcextracted'+os.sep+file.split(os.sep)[-1].split('.')[0]+'.SAFE'+os.sep+'annotation'+os.sep+'calibration'+os.sep+filecal[idx].split(os.sep)[-1] 
                filenoi[idx] = 'tmpslcextracted'+os.sep+file.split(os.sep)[-1].split('.')[0]+'.SAFE'+os.sep+'annotation'+os.sep+'calibration'+os.sep+filenoi[idx].split(os.sep)[-1] 

        usermessage.ezprint('\tdone',log,verbose) 
        usermessage.ezprint('SLC file(s) %s' % (fileslc),log,verbose) 
        usermessage.ezprint('Annotation file(s) %s' % (fileann),log,verbose) 
        usermessage.ezprint('Calibration file(s) %s' % (filecal),log,verbose) 
        usermessage.ezprint('Noise file(s) %s' % (filenoi),log,verbose) 

        ## Create the .res file
        for idx, poli in enumerate(polarisation): 
            with open(outputdir+os.sep+"%s.%s.slc.res" % (prefixname,poli.lower()),"w+") as f_res: 
                f_res.write("===============================================\n")
                if mode == "master":
                    f_res.write("MASTER RESULTFILE:                      %s.%s.slc.res\n" % (prefixname,poli.lower()))
                else:
                    f_res.write("SLAVE RESULTFILE:                      %s.%s.slc.res\n" % (prefixname,poli.lower()))

                f_res.write('Created by:                             EZ-InSAR\n')
                f_res.write('DVersion:                               Version (2015)\n')
                f_res.write('FFTW library:                           used\n')
                f_res.write('VECLIB library:                         not used\n')
                f_res.write('LAPACK library:                         used\n')
                f_res.write('Compiled at:                            XXXXXXXX\n')
                f_res.write('By GUN gcc:                             XXXXXXXX\n')
                f_res.write('===============================================\n') 
                f_res.write('File creation at:       '+datetime.date.today().strftime("%d-%b-%Y")+'\n\n')
                f_res.write(' -------------------------------------------------------\n')
                f_res.write('| Delft Institute of Earth Observation & Space Systems  |\n')
                f_res.write('|          Delft University of Technology               |\n')
                f_res.write('|              http://doris.tudelft.nl                  |\n')
                f_res.write('|                                                       |\n')
                f_res.write('| Author: (c) TUDelft - DEOS Radar Group                |\n')
                f_res.write(' -------------------------------------------------------\n\n\n')
                f_res.write('Start_process_control\n')
                f_res.write('readfiles:\t\t\t1\n')
                f_res.write('precise_orbits:\t\t1\n')
                f_res.write('crop:\t\t\t\t1\n')
                f_res.write('sim_amplitude:\t\t0\n')
                f_res.write('master_timing:\t\t0\n')
                f_res.write('oversample:\t\t\t0\n')
                f_res.write('resample:\t\t\t0\n')
                f_res.write('filt_azi:\t\t\t0\n')
                f_res.write('filt_range:\t\t\t0\n')
                f_res.write('NOT_USED:\t\t\t0\n')
                f_res.write('End_process_control\n\n\n')

                # Read of xml file
                xmlann = ET.parse(fileann[idx])
                
                f_res.write('*******************************************************************\n')
                f_res.write('*_Start_readfiles:\n')
                f_res.write('*******************************************************************\n')
                f_res.write('Volume_file: \t\t\t'+'dummy'+'\n')
                f_res.write('Volume_ID: \t\t\t'+xmlann.findall('.//adsHeader/missionDataTakeId')[0].text+'\n')
                f_res.write('Volume_identifier: \t\t\t'+'dummy'+'\n')
                f_res.write('Volume_set_identifier: \t\t\t'+'dummy'+'\n')
                f_res.write('Number of records in ref. file: \t\t\t'+'dummy'+'\n')
                f_res.write('SAR_PROCESSOR: \t\t\t'+'dummy'+'\n')
                f_res.write('SWATH: \t\t\t'+xmlann.findall('.//adsHeader/swath')[0].text+'\n')
                f_res.write('PASS: \t\t\t'+xmlann.findall('.//generalAnnotation/productInformation/pass')[0].text+'\n')
                f_res.write('IMAGE_MODE: \t\t\t'+xmlann.findall('.//adsHeader/mode')[0].text+'\n')
                f_res.write('polarisation: \t\t\t'+xmlann.findall('.//adsHeader/polarisation')[0].text+'\n')
                f_res.write('Product type specifier: \t\t\t'+xmlann.findall('.//adsHeader/missionId')[0].text+'\n')
                f_res.write('Logical volume generating facility: \t\t\t'+'dummy'+'\n')
                f_res.write('Location and date/time of product creation: \t\t\t'+'dummy'+'\n')
                f_res.write('RADAR_FREQUENCY (HZ): \t\t\t'+xmlann.findall('.//generalAnnotation/productInformation/radarFrequency')[0].text+'\n')
                f_res.write('Scene identification: \t\t\t'+'Orbit '+xmlann.findall('.//adsHeader/absoluteOrbitNumber')[0].text+'\n')
        
                #Extraction of the coordinate grid
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

                for nodes in xmlann.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/azimuthTime'):
                    data_xml['azimuthTime'].append(nodes.text)
                for nodes in xmlann.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/slantRangeTime'):
                    data_xml['slantRangeTime'].append(nodes.text)
                for nodes in xmlann.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/line'):
                    data_xml['line'].append(nodes.text)
                for nodes in xmlann.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/pixel'):
                    data_xml['pixel'].append(nodes.text)
                for nodes in xmlann.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/latitude'):
                    data_xml['latitude'].append(nodes.text)
                for nodes in xmlann.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/longitude'):
                    data_xml['longitude'].append(nodes.text)
                for nodes in xmlann.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/height'):
                    data_xml['height'].append(nodes.text)
                for nodes in xmlann.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/incidenceAngle'):
                    data_xml['incidenceAngle'].append(nodes.text)
                for nodes in xmlann.findall('.//geolocationGrid/geolocationGridPointList/geolocationGridPoint/elevationAngle'):
                    data_xml['elevationAngle'].append(nodes.text)

                data_xml['nbl'] = xmlann.findall('.//imageAnnotation/imageInformation/numberOfLines')[0].text
                data_xml['nbc'] = xmlann.findall('.//imageAnnotation/imageInformation/numberOfSamples')[0].text

                #Write of the parameters
                f_res.write('Scene location: \t\t\t lat: '+data_xml['latitude'][0]+' lon: '+data_xml['longitude'][0]+'\n')
                f_res.write('Sensor platform mission identifer: \t\t\t'+xmlann.findall('.//adsHeader/missionId')[0].text+'\n')
                f_res.write('Scene_center_heading: \t\t\t'+xmlann.findall('.//generalAnnotation/productInformation/platformHeading')[0].text+'\n')
                f_res.write('Scene_centre_latitude: \t\t\t'+str(np.mean(np.array(data_xml['latitude'],dtype=float)))+'\n')
                f_res.write('Scene_centre_longitude: \t\t\t'+str(np.mean(np.array(data_xml['longitude'],dtype=float)))+'\n')
                f_res.write('Radar_wavelength (m): \t\t\t'+str(299792458.0/float(xmlann.findall('.//generalAnnotation/productInformation/radarFrequency')[0].text))+'\n')
                f_res.write('First_pixel_azimuth_time (UTC): \t\t\t'+datetime.datetime.strptime(data_xml['azimuthTime'][0], '%Y-%m-%dT%H:%M:%S.%f').strftime('%d-%b-%Y %H:%M:%S.%f')+'\n')

                f_res.write('Pulse_Repetition_Frequency (computed, Hz): \t\t\t'+xmlann.findall('.//imageAnnotation/imageInformation/azimuthFrequency')[0].text+'\n')
                f_res.write('Total_azimuth_band_width (Hz): \t\t\t'+xmlann.findall('.//imageAnnotation/processingInformation/swathProcParamsList/swathProcParams/azimuthProcessing/totalBandwidth')[0].text+'\n')
                f_res.write('Weighting_azimuth: \t\t\t'+xmlann.findall('.//imageAnnotation/processingInformation/swathProcParamsList/swathProcParams/azimuthProcessing/windowType')[0].text+'\n')
                f_res.write('Range_time_to_first_pixel (2way) (ms): \t\t\t'+str(float(xmlann.findall('.//imageAnnotation/imageInformation/slantRangeTime')[0].text)*1000)+'\n')
                f_res.write('Range_sampling_rate (computed, MHz): \t\t\t'+str(float(xmlann.findall('.//generalAnnotation/productInformation/rangeSamplingRate')[0].text)/1000000)+'\n')
                f_res.write('Total_range_band_width (MHz): \t\t\t'+str(float(xmlann.findall('.//imageAnnotation/processingInformation/swathProcParamsList/swathProcParams/rangeProcessing/processingBandwidth')[0].text)/1000000)+'\n')
                f_res.write('Weighting_range: \t\t\t'+xmlann.findall('.//imageAnnotation/processingInformation/swathProcParamsList/swathProcParams/rangeProcessing/windowType')[0].text+'\n')

                #For the Doppler centroid
                for nodes in xmlann.findall('.//dopplerCentroid/dcEstimateList/dcEstimate/dataDcPolynomial'):
                    data_xml['Xtrack_f_DC'].append(nodes.text)
                f_res.write('Xtrack_f_DC_constant (Hz, early edge): \t\t\t'+data_xml['Xtrack_f_DC'][1].split()[0]+'\n')
                f_res.write('Xtrack_f_DC_linear (Hz/s, early edge): \t\t\t'+data_xml['Xtrack_f_DC'][1].split()[1]+'\n')
                f_res.write('Xtrack_f_DC_quadratic (Hz/s/s, early edge): \t\t\t'+data_xml['Xtrack_f_DC'][1].split()[2]+'\n')

                #Finalisation
                f_res.write('\n*******************************************************************\n')
                f_res.write('Datafile: \t\t\t'+fileslc[idx].split(os.sep)[-1]+'\n')
                f_res.write('Dataformat: \t\t\t'+'tiff'+'\n')
                f_res.write('Number_of_lines_original: \t\t\t'+data_xml['nbl']+'\n')
                f_res.write('Number_of_pixels_original: \t\t\t'+data_xml['nbc']+'\n')
                f_res.write('*******************************************************************\n')
                f_res.write('* End_readfiles:_NORMAL\n')
                f_res.write('*******************************************************************\n')

                # For the orbits
                f_res.write('\n\n*******************************************************************\n')
                f_res.write('*_Start_precise_orbits:\n')
                f_res.write('*******************************************************************\n')
                f_res.write(' t(s)            X(m)            Y(m)            Z(m)            X_V(m/s)            Y_V(m/s)            Z_V(m/s)\n')
                
                
                if modeorbit == False: 
                    usermessage.ezprint('Use the orbit in the .zip or .SAFE file',log,verbose) 

                    f_res.write('NUMBER_OF_DATAPOINTS:                    '+str(len(xmlann.findall('.//generalAnnotation/orbitList/orbit/position/x')))+'\n\n')

                    data_orbits = dict()
                    data_orbits['date_int'] = []
                    data_orbits['orb_X_int'] = []
                    data_orbits['orb_Y_int'] = []
                    data_orbits['orb_Z_int'] = []
                    data_orbits['orb_VX_int'] = []
                    data_orbits['orb_VY_int'] = []
                    data_orbits['orb_VZ_int'] = []

                    for nodes in xmlann.findall('.//generalAnnotation/orbitList/orbit/time'): 
                        date_temp = datetime.datetime.strptime(nodes.text, '%Y-%m-%dT%H:%M:%S.%f').strftime('%H:%M:%S.%f')
                        date_temp_sec = int(date_temp[0:2])*3600 + int(date_temp[3:5])*60 + float(date_temp[6:])
                        data_orbits['date_int'].append("%.5f" % date_temp_sec)
                    for nodes in xmlann.findall('.//generalAnnotation/orbitList/orbit/position/x'): 
                        data_orbits['orb_X_int'].append("%.5f" % float(nodes.text))
                    for nodes in xmlann.findall('.//generalAnnotation/orbitList/orbit/position/y'): 
                        data_orbits['orb_Y_int'].append("%.5f" % float(nodes.text))
                    for nodes in xmlann.findall('.//generalAnnotation/orbitList/orbit/position/z'): 
                        data_orbits['orb_Z_int'].append("%.5f" % float(nodes.text))
                    for nodes in xmlann.findall('.//generalAnnotation/orbitList/orbit/velocity/x'): 
                        data_orbits['orb_VX_int'].append("%.5f" % float(nodes.text))
                    for nodes in xmlann.findall('.//generalAnnotation/orbitList/orbit/velocity/y'): 
                        data_orbits['orb_VY_int'].append("%.5f" % float(nodes.text))
                    for nodes in xmlann.findall('.//generalAnnotation/orbitList/orbit/velocity/z'): 
                        data_orbits['orb_VZ_int'].append("%.5f" % float(nodes.text))

                    i1 = 0
                    while i1 < len(xmlann.findall('.//generalAnnotation/orbitList/orbit/position/x')):
                        f_res.write(''+data_orbits['date_int'][i1]+' '+data_orbits['orb_X_int'][i1]+' '+data_orbits['orb_Y_int'][i1]+' '+data_orbits['orb_Z_int'][i1]+' '+data_orbits['orb_VX_int'][i1]+' '+data_orbits['orb_VY_int'][i1]+' '+data_orbits['orb_VZ_int'][i1]+'\n')
                        i1 += 1

                else: 
                    usermessage.ezprint('Mode of orbits: we will use the precise (or restitued) orbits, if available.',log,verbose)

                    orbits_name = []
                    date_format = "%Y%m%dT%H%M%S"

                    orbits_precise = glob.glob(pathorbit+os.sep+'*POEORB*.EOF')
                    orbits_restitued = glob.glob(pathorbit+os.sep+'*RESORB*.EOF')

                   
                    dslc = datetime.datetime.strptime(data_xml['azimuthTime'][0], '%Y-%m-%dT%H:%M:%S.%f')
                    sati = xmlann.findall('.//adsHeader/missionId')[0].text

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

                    if orbits_name[0] == None: 
                        raise ValueError(usermessage.errormsg(__name__,importS1SM.__name__,__file__,__copyright__,
                            'No orbit file.',log,verbose))
                    
                    data_orbits = s1slctools.read_precise_restitued_xml(pathorbit+os.sep+orbits_name[0])

                    timeorbit = []
                    azimuthTimestamp = []     

                    for di in data_xml['azimuthTime']:
                        azimuthTimestamp.append(datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S.%f").timestamp())
                    
                    for di in data_orbits['time']:
                        timeorbit.append(datetime.datetime.strptime(di,"%Y-%m-%dT%H:%M:%S.%f").timestamp())

                    nb_orbit = 10
                    newtime = np.arange(np.fix(np.min(azimuthTimestamp))-(nb_orbit)*10,np.fix(np.max(azimuthTimestamp))+(nb_orbit)*10,10)

                    # fi = interpolate.PchipInterpolator(timeorbit, data_orbits['orb_X_int'])
                    # x_newtime = fi(newtime)
                    # fi = interpolate.PchipInterpolator(timeorbit, data_orbits['orb_Y_int'])
                    # y_newtime = fi(newtime)
                    # fi = interpolate.PchipInterpolator(timeorbit, data_orbits['orb_Z_int'])
                    # z_newtime = fi(newtime)
                    # fi = interpolate.PchipInterpolator(timeorbit, data_orbits['orb_VX_int'])
                    # vx_newtime = fi(newtime)
                    # fi = interpolate.PchipInterpolator(timeorbit, data_orbits['orb_VY_int'])
                    # vy_newtime = fi(newtime)
                    # fi = interpolate.PchipInterpolator(timeorbit, data_orbits['orb_VZ_int'])
                    # vz_newtime = fi(newtime)

                    fi = np.poly1d(np.polyfit(timeorbit, data_orbits['orb_X_int'], constants.__orbit_poly_order__))
                    x_newtime = fi(newtime)
                    fi = np.poly1d(np.polyfit(timeorbit, data_orbits['orb_Y_int'], constants.__orbit_poly_order__))
                    y_newtime = fi(newtime)
                    fi = np.poly1d(np.polyfit(timeorbit, data_orbits['orb_Z_int'], constants.__orbit_poly_order__))
                    z_newtime = fi(newtime)
                    fi = np.poly1d(np.polyfit(timeorbit, data_orbits['orb_VX_int'], constants.__orbit_poly_order__))
                    vx_newtime = fi(newtime)
                    fi = np.poly1d(np.polyfit(timeorbit, data_orbits['orb_VY_int'], constants.__orbit_poly_order__))
                    vy_newtime = fi(newtime)
                    fi = np.poly1d(np.polyfit(timeorbit, data_orbits['orb_VZ_int'], constants.__orbit_poly_order__))
                    vz_newtime = fi(newtime)

                    f_res.write('NUMBER_OF_DATAPOINTS:                    %s\n\n' % (len(x_newtime)))

                    for idxtime, ti in enumerate(newtime):
                        time = datetime.datetime.fromtimestamp(ti)
                        date_temp = time.strftime('%H:%M:%S.%f')
                        date_temp_sec = int(date_temp[0:2])*3600 + int(date_temp[3:5])*60 + float(date_temp[6:])
                        timestr = "%.6f" % (date_temp_sec)

                        f_res.write('%s %.6f %.6f %.6f %.6f %.6f %.6f\n' % (timestr,
                            x_newtime[idxtime], 
                            y_newtime[idxtime], 
                            z_newtime[idxtime], 
                            vx_newtime[idxtime], 
                            vy_newtime[idxtime], 
                            vz_newtime[idxtime], 
                            ))

                f_res.write('\n*******************************************************************\n')
                f_res.write('* End_precise_orbits:_NORMAL\n')
                f_res.write('*******************************************************************\n')

            # # Copy of the tiff SLC
            # gdalCall = 'gdal_translate'
            # outputDataFormat = 'MFF'
            # outputDataType   = 'CInt16'
            output_file = outputdir+os.sep+prefixname+'.'+poli.lower()

            # cmdi = '%s %s -ot %s -of %s %s' % (gdalCall,fileslc[idx],outputDataType,outputDataFormat,output_file)
    
            # For the cropping 
            crop = False

            if isinstance(cropping,list):
                First_pixel = cropping[0]
                Last_pixel = cropping[1]
                First_line = cropping[2]
                Last_line = cropping[3]
                crop = True

            elif cropping == 'auto': 

                interpline = LinearNDInterpolator(list(zip(data_xml['longitude'], data_xml['latitude'])), data_xml['line'])
                interppixel = LinearNDInterpolator(list(zip(data_xml['longitude'], data_xml['latitude'])), data_xml['pixel'])
                                                
                coords = loads(roi).exterior.xy
                lines = [interpline(np.min(coords[0]),np.min(coords[1])), 
                        interpline(np.max(coords[0]),np.min(coords[1])),
                        interpline(np.max(coords[0]),np.max(coords[1])),
                        interpline(np.min(coords[0]),np.max(coords[1]))]

                pixels = [interppixel(np.min(coords[0]),np.min(coords[1])), 
                        interppixel(np.max(coords[0]),np.min(coords[1])),
                        interppixel(np.max(coords[0]),np.max(coords[1])),
                        interppixel(np.min(coords[0]),np.max(coords[1]))]
                                                
                First_pixel = int(np.min(pixels))
                Last_pixel = int(np.max(pixels))
                First_line = int(np.min(lines))
                Last_line = int(np.max(lines))

                crop =True   

            # if crop == True: 
            #     cmdi = cmdi + (' -srcwin %s %s %s %s' % (int(First_pixel),int(First_line),int(Last_pixel)-int(First_pixel)+1,int(Last_line)-int(First_line)+1))

            # usermessage.ezprint('Extraction of the SLC tif file: %s' % (cmdi),log,verbose) 
            # os.system(cmdi)

            # if os.path.isfile(outputdir+os.sep+prefixname+'.hdr'):
            #     os.remove(outputdir+os.sep+prefixname+'.hdr')
            # if os.path.isfile(outputdir+os.sep+prefixname+'.hdr.aux.xml'):
            #     os.remove(outputdir+os.sep+prefixname+'.hdr.aux.xml')

            # os.rename(outputdir+os.sep+prefixname+'.j00',output_file+'.slc')

            with open(outputdir+os.sep+"%s.%s.slc.res" % (prefixname,poli.lower()),"a+") as f_res: 

                f_res.write('\n\n\n*******************************************************************\n')

                if mode == 'master':

                    f_res.write('*_Start_crop:			master step01\n')
                    f_res.write('*******************************************************************\n')
                    f_res.write('Data_output_file: 				%s\n' % (output_file.split(os.sep)[-1]+'.slc'))
                else:
                    f_res.write('*_Start_crop:			slave step01\n');
                    f_res.write('*******************************************************************\n')
                    f_res.write('Data_output_file: 				%s\n' % (output_file.split(os.sep)[-1]+'.slc'))
                
                f_res.write('Data_output_format: 				complex_short\n')

                if crop == True:  
                    f_res.write('First_line (w.r.t. original_image): 		'+str(First_line+1)+'\n')
                    f_res.write('Last_line (w.r.t. original_image): 		'+str(Last_line+1)+'\n')
                    f_res.write('First_pixel (w.r.t. original_image): 	    '+str(First_pixel+1)+'\n')
                    f_res.write('Last_pixel (w.r.t. original_image): 		'+str(Last_pixel+1)+'\n')
                    f_res.write('Number of lines (non-multilooked): 		'+str(int(Last_line)-int(First_line)+1)+'\n')   
                    f_res.write('Number of pixels (non-multilooked): 		'+str(int(Last_pixel)-int(First_pixel)+1)+'\n')  

                    SLCdata = np.memmap(output_file+'.slc', 
                                    dtype=np.int16, 
                                    mode='w+', 
                                    offset=0, 
                                    shape=((int(Last_line)-int(First_line)+1),2*(int(Last_pixel)-int(First_pixel)+1)), order='C')

                else:
                    f_res.write('First_line (w.r.t. original_image): 		'+'1'+'\n')
                    f_res.write('Last_line (w.r.t. original_image): 		'+data_xml['nbl']+'\n')
                    f_res.write('First_pixel (w.r.t. original_image): 	    '+'1'+'\n',1)
                    f_res.write('Last_pixel (w.r.t. original_image): 		'+data_xml['nbc']+'\n')
                    f_res.write('Number of lines (non-multilooked): 		'+data_xml['nbl']+'\n')
                    f_res.write('Number of pixels (non-multilooked): 		'+data_xml['nbc']+'\n')

                    SLCdata = np.memmap(output_file+'.slc', 
                                    dtype=np.int16, 
                                    mode='w+', 
                                    offset=0, 
                                    shape=(data_xml['nbl'],2*data_xml['nbc']), order='C')

                f_res.write('*******************************************************************\n')
                f_res.write('* End_crop:_NORMAL\n')
                f_res.write('*******************************************************************\n')
                
            ds = gdal.Open(fileslc[idx])
            Band = ds.GetRasterBand(1)
        
            nlinesrange = np.arange(First_line,Last_line+1,1)
            nCols = ds.RasterXSize

            blockslines = [nlinesrange[i:i + 1000] for i in range(0, len(nlinesrange), 1000)]

            pointerstart = 0
            for idx, nline in enumerate(blockslines): 
                usermessage.ezprint('\tRead the block %d (of %d) (block size: %d)' % (idx+1,len(blockslines),1000),log,verbose) 
                block = Band.ReadAsArray(0, int(np.min(nline)), nCols, int(np.max(nline)-np.min(nline)+1))[:,First_pixel:Last_pixel+1]
                pointerend = pointerstart + len(nline)-1
                pointerlines = np.arange(pointerstart,pointerend+1)

                value = np.zeros((len(nline),2*block.shape[1]))

                value[:,0::2,] = np.real(block)
                value[:,1::2] = np.imag(block)

                SLCdata[pointerlines,:] = value 
                SLCdata.flush()
            
                pointerstart = pointerend + 1
                
            ds = None

            # ## For the calibration 
            # if not calibration == None: 
            #     usermessage.ezprint('Read the calibration files',log,verbose) 
            #     xmlcal = ET.parse(filecal[idx])
            #     xmlnoi = ET.parse(filenoi[idx])

            #     linecal = []
            #     linepixel = []
                
            #     for nodes in xmlcal.findall('.//calibrationVectorList/calibrationVector/line'): 
            #         linecal.append(float(nodes.text))

            #     for nodes in xmlcal.findall('.//calibrationVectorList/calibrationVector/pixel'): 
            #         tmp = []
            #         for xi in nodes.text.split(' '): 
            #             tmp.append(float(xi))
            #         linepixel.append(tmp)

            #     para = doristools.readimagepara(outputdir+os.sep+"%s.%s.slc.res" % (prefixname,poli.lower()))
            #     a = np.arange(para['First_pixel (w.r.t. original_image)'],para['Last_pixel (w.r.t. original_image)']+1,1)
            #     b = np.arange(para['First_line (w.r.t. original_image)'],para['Last_line (w.r.t. original_image)']+1,1)

            #     calvalue = np.empty((len(linecal),len(linepixel[0])))
            #     noisevalue = np.empty((len(linecal),len(linepixel[0])))
            #     if 'beta' in calibration: 
            #         VALUE = xmlcal.findall('.//calibrationVectorList/calibrationVector/betaNought')
            #     elif 'sigma' in calibration: 
            #         VALUE = xmlcal.findall('.//calibrationVectorList/calibrationVector/sigmaNought')
            #     else:
            #         VALUE = xmlcal.findall('.//calibrationVectorList/calibrationVector/dn')
                
            #     h = 0
            #     for nodes in VALUE: 
            #         tmp = []
            #         for xi in nodes.text.split(' '): 
            #             tmp.append(float(xi))
            #         calvalue[h,:] = tmp
            #         h = h +1

            #     h = 0
            #     for nodes in xmlnoi.findall('.//calibrationVectorList/calibrationVector/noiseRangeLut'): 
            #         tmp = []
            #         for xi in nodes.text.split(' '): 
            #             tmp.append(float(xi))
            #         noisevalue[h,:] = tmp
            #         h = h +1

            #     interp1 = interpolate.RegularGridInterpolator((linepixel[0],linecal), calvalue.T,bounds_error=False, fill_value=np.nan)
            #     interp2 = interpolate.RegularGridInterpolator((linepixel[0],linecal), noisevalue.T,bounds_error=False, fill_value=np.nan)

            #     cal_interp = np.full((len(b),len(a)),np.nan)
            #     noise_interp = np.full((len(b),len(a)),np.nan)
            #     Xinterp, Yinterp = np.meshgrid(a,b)

            #     i1 = 0
            #     while i1 < cal_interp.shape[0]-1: 
            #         if np.fix(i1/1000) == i1/1000:
            #             usermessage.ezprint('Interpolation of calibration LUTs for the line %d (on %d)' % (i1,cal_interp.shape[0]-1),log,verbose) 
                    
            #         cal_interp[i1,:] = interp1((Xinterp[i1,:],Yinterp[i1,:]))
            #         noise_interp[i1,:] = interp2((Xinterp[i1,:],Yinterp[i1,:]))
                    
            #         i1 = i1 + 1 

            #     usermessage.ezprint('Calibration of the SLC:',log,verbose) 

            #     with open(output_file+'.slc', "rb") as fi: 
            #         data = np.reshape(np.fromfile(fi, np.int16),(para['Number of lines (non-multilooked)']*2,para['Number of pixels (non-multilooked)']))

            #     slcdata = np.empty(data[0::2,:].shape, dtype=np.complex)
            #     slcdata.real = data[0::2,:]
            #     slcdata.imag = data[1::2,:]

            #     amp = np.abs(slcdata)
            #     pha = np.angle(slcdata)

            #     if 'noise' in calibration: 
            #         amp = (amp**2 - noise_interp)/(cal_interp**2)
            #     else:
            #         amp = (amp**2)/(cal_interp**2)
                
            #     newslc = amp * np.exp(pha*1.j)
            #     newslcfloat = np.full((para['Number of lines (non-multilooked)']*2,para['Number of pixels (non-multilooked)']),np.nan,dtype='int16')
            #     newslcfloat[0::2,:] = newslc.real
            #     newslcfloat[1::2,:] = newslc.imag

            #     newslcfloat.tofile(output_file+'.slc', sep='', format='%d')

            #     usermessage.ezprint('\tdone',log,verbose) 

            usermessage.ezprint('SLC file is: %s' % (output_file+'.slc'),log,verbose) 
            usermessage.ezprint('.res file is: %s' % (outputdir+os.sep+"%s.%s.slc.res" % (prefixname,poli.lower())),log,verbose) 

        if os.path.isdir('tmpslcextracted'):
            shutil.rmtree('tmpslcextracted')
