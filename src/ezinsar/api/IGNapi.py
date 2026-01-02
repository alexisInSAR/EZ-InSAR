#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module for the IGN data 

The module allows to create the downloader classes for the IGN datasets.

    (From `ezinsar` package)

Changelog:
    * 3.2.2: Delete the support of wget for Windows, Alexis Hrysiewicz, Sep. 2025
    * 3.1.0: Initial version, Mar. 2025


"""
################################################################################
## Python packages
################################################################################
from typing import Optional, Union
from datetime import date, datetime
import numpy as np
import os 
import glob
from shapely.geometry import Polygon
from shapely.wkt import loads
import pandas as pd 
import fiona
import requests
import re
import urllib
import shutil
from osgeo import gdal
import osgeo_utils
import py7zr
import platform

from ezinsar import constants
from ezinsar import usermessage
from ezinsar.tools import miscellaneous

################################################################################
## Variables
################################################################################
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## retrieve FUNCTION
################################################################################
class RGEALTI:

    def __init__(self,
        roi, 
        workdirectory,
        resolution = 5,
        log = None, 
        verbose = True,
        ):
        """Constructor"""
        
        if not isinstance(verbose,bool):
            raise TypeError(usermessage.typeerrormsg(
                __name__,__name__,__file__,__copyright__,
                'verbose','True or False',log))

        if not 'polygon' in str(type(roi)).lower():
            raise TypeError(usermessage.typeerrormsg(
                __name__,__name__,__file__,__copyright__,
                'roi','Polygon',log))
        
        if not resolution in [1,5]:
            raise TypeError(usermessage.typeerrormsg(
                __name__,__name__,__file__,__copyright__,
                'resolution','1 or 5',log))

        self.roi = roi
        self.resolution = resolution
        self.insee_code = []
        self.links = []
        self.workdirectory = workdirectory

    ################################################################################
    def detectdepartement(self,
        log=None,
        verbose=True): 
        """Detection of the insee codes based on the Region of Interest"""

        if not isinstance(verbose,bool):
            raise TypeError(usermessage.typeerrormsg(
                __name__,__name__,__file__,__copyright__,
                'verbose','True or False',log))
        
        depart_file = __file__.replace('api%sIGNapi.py' % (os.sep),'3rdparty%s' % (os.sep)) + 'dep_France.geojson'
        if not os.path.isfile(depart_file):
            usermessage.warningmsg(__name__,__name__,__file__,'The geosjon file for insee codes is required. EZ-InSAR will try to download it. You have to consider that you will use this file. ',log,verbose)  

            miscellaneous.download_file('https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/contours-geographiques-tres-simplifies-des-departements-2019/exports/geojson?lang=en&timezone=Europe%2FLondon',
                        verbose=verbose,
                        log=log, 
                        output_file=depart_file)

        # Extract the insee codes
        with fiona.open(depart_file) as roifile:           
            for feature in roifile:
                if len(feature['geometry']["coordinates"][0]) == 1:
                        bbox = Polygon(feature['geometry']["coordinates"][0][0])
                else: 
                        bbox = Polygon(feature['geometry']["coordinates"][0])
                if self.roi.intersection(bbox).area/self.roi.area*100 > 0: 
                    self.insee_code.append(feature['properties']["insee_dep"])

        self.insee_code = np.unique(self.insee_code).tolist()

        if not self.insee_code:
            raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'No DEM tiles retrieved for the given Region of Interest.',log))  

        usermessage.ezprint('The insee code(s) required for the REG-ALTI DEM is/are %s.' % (self.insee_code),log,verbose)   

    ################################################################################
    def getlink(self,
        log=None,
        verbose=True):
        """Append the required links"""
        
        if not isinstance(verbose,bool):
            raise TypeError(usermessage.typeerrormsg(
                __name__,__name__,__file__,__copyright__,
                'verbose','True or False',log))
        
        url = 'https://geoservices.ign.fr/rgealti'

        html = urllib.request.urlopen(url)        
        text = html.read()
        plaintext = text.decode('utf8')

        self.links = []
        for li in re.findall("href=[\"\'](.*?)[\"\']", plaintext):
            if ('https://data.geopf.fr/telechargement/download/RGEALTI' in li) and ('%sM' % (self.resolution) in li) and ('%sM' % (self.resolution) in li):
                for di in self.insee_code:
                    if ('_D%03d' % (int(di)) in li):
                        self.links.append((li))

        usermessage.ezprint('The files required for the REG-ALTI DEM is/are:',log,verbose)   
        for li in self.links: 
            usermessage.ezprint('\t%s' % (li.split('/')[-1]),log,verbose) 

    ###############################################################################
    def download(self,
        log=None,
        verbose=True): 
        """Downloader"""
        
        if not isinstance(verbose,bool):
            raise TypeError(usermessage.typeerrormsg(
                __name__,__name__,__file__,__copyright__,
                'verbose','True or False',log))
    
        if os.path.isdir(self.workdirectory+os.sep+'dirDEMtmp'):
            shutil.rmtree(self.workdirectory+os.sep+'dirDEMtmp')
        os.mkdir(self.workdirectory+os.sep+'dirDEMtmp')

        usermessage.ezprint('Start the downloading',log,verbose)   
        for li in self.links:
            usermessage.ezprint('\tFor %s' % (li.split('/')[-1]),log,verbose)   
            if not os.path.isfile(self.workdirectory+os.sep+'dirDEMtmp'+os.sep+li.split('/')[-1]):

                if constants.__SLCdownloader__ == 'wget':
                    if  platform.system() == 'Windows':
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,constants.__copyright__,'The wget mode is not available with Windows. Please modify the __SLCdownloader__ option to python.',log))
            
                    if constants.__wgetlimit__ == 'auto': 
                        if (datetime.today().hour > 22) and (datetime.today().hour < 5): 
                            wgetlimit = constants.__wgetlimitmax__
                        else:
                            wgetlimit = constants.__wgetlimitmin__
                    else:
                            wgetlimit = constants.__wgetlimit__

                    cmdi = 'wget --limit-rate %s -c "%s" -P %s' % (wgetlimit,li,self.workdirectory+os.sep+'dirDEMtmp')
                    os.system(cmdi)

                else:
                    miscellaneous.download_file(li,
                            verbose=verbose,
                            log=log, 
                            output_file=self.workdirectory+os.sep+'dirDEMtmp'+os.sep+li.split('/')[-1])

                usermessage.ezprint('\t\tdone',log,verbose)  
            else: 
                usermessage.ezprint('\t\talready downloaded',log,verbose)   

    ################################################################################
    def extractDEM(self,
        warpoption = True,
        log=None,
        verbose=True): 
        """Extractor"""
        
        if not isinstance(verbose,bool):
            raise TypeError(usermessage.typeerrormsg(
                __name__,__name__,__file__,__copyright__,
                'verbose','True or False',log))
    
        if os.path.isdir(self.workdirectory+os.sep+'dirDEMtmp'+os.sep+'tiles'):
            shutil.rmtree(self.workdirectory+os.sep+'dirDEMtmp'+os.sep+'tiles')
        os.mkdir(self.workdirectory+os.sep+'dirDEMtmp'+os.sep+'tiles')
        
        usermessage.ezprint('Unpack the tiles',log,verbose) ## All tiles will be unpacked
        for fi in glob.glob(self.workdirectory+os.sep+'dirDEMtmp'+os.sep+'*7z'): 
            with py7zr.SevenZipFile(fi,mode='r') as zipObj:
                listOfFileNames = zipObj.getnames()
                selectedfile = []
                for entry in listOfFileNames: 
                    if entry.endswith('.asc'):
                        selectedfile.append(entry)
                zipObj.extract(targets=selectedfile,path=self.workdirectory+os.sep+'dirDEMtmp'+os.sep+'tiles')
                             
        usermessage.ezprint('Merge the DEM tiles',log,verbose)
        filefinal = '%s%sdem_tmp_0.tif' % (self.workdirectory,os.sep)

        listtiles = glob.glob('%s%sdirDEMtmp%stiles%s*%s*%s*%s*%s*.asc' % (self.workdirectory,os.sep,os.sep,os.sep,os.sep,os.sep,os.sep,os.sep))
        dirtmp = os.path.dirname(listtiles[0])
        
        if 'WGS84UTM20' in listtiles[0].split(os.sep)[-1]: 
            code = 'EPSG:32620'
        elif 'RGFG95UTM22' in listtiles[0].split(os.sep)[-1]: 
            code = 'EPSG:2972'
        elif 'RGR92UTM40S' in listtiles[0].split(os.sep)[-1]: 
            code = 'EPSG:2975'
        elif 'RGSPM06U21' in listtiles[0].split(os.sep)[-1]: 
            code = 'IGNF:RGSPMO6U21'
        elif 'RGM04UTM38S' in listtiles[0].split(os.sep)[-1]: 
            code = 'IGNF:RGM04UTM38S'
        elif 'LAMB93' in listtiles[0].split(os.sep)[-1]: 
            code = 'IGNF:LAMB93'

        os.system("gdalbuildvrt -resolution highest -vrtnodata -9999 -a_srs %s -r cubic %s%sIGNtmp.vrt $(find %s -iname '%s')" % (code,self.workdirectory,os.sep,dirtmp,'*.asc')) 

        options = ''
        bboxclip = self.roi.exterior.xy

        options = options + ' -of GTiff -a_nodata %s -projwin %f %f %f %f -projwin_srs EPSG:4326' % (-9999,np.min(bboxclip[0]),np.max(bboxclip[1]),np.max(bboxclip[0]),np.min(bboxclip[1]))
        
        src_ds = gdal.Open('%s%sIGNtmp.vrt' % (self.workdirectory,os.sep))
        dst_ds = gdal.Translate('%s%sIGNtmp0.tif' % (self.workdirectory,os.sep), src_ds, options = options)
        src_ds = None
        dst_ds = None

        dem_input = '%s%sIGNtmp0.tif' % (self.workdirectory,os.sep)
        dem_output = '%s%sIGNtmp1.tif' % (self.workdirectory,os.sep)
        paralist = ['', '-A', dem_input, '--type', 'Float32', '--outfile', dem_output,'--calc', '"numpy.where(A==-9999,0,A)"','--NoDataValue','0']
        osgeo_utils.gdal_calc.main(paralist)

        if warpoption == True: 
            cmd_i = 'gdalwarp -r bilinear -t_srs "EPSG:4326" -overwrite %s %s' % ('%s%sIGNtmp1.tif' % (self.workdirectory,os.sep),
                                                                                filefinal)               
            os.system(cmd_i)
        else: 
            shutil.copy('%s%sIGNtmp1.tif' % (self.workdirectory,os.sep),filefinal)

        usermessage.ezprint('\tdone',log,verbose)

    ################################################################################
    def clean(self): 
        if os.path.isdir(self.workdirectory):
            for fi in glob.glob(self.workdirectory+os.sep+'dirDEMtmp*') + glob.glob(self.workdirectory+os.sep+'IGNtmp*'):
                if os.path.isdir(fi): 
                    shutil.rmtree(fi)
                else: 
                    os.remove(fi)

    ################################################################################ 
    def run(self,
        warpoption = True,
        log=None,
        verbose=True): 
        """Wrapper"""
        self.detectdepartement(log=log,verbose=verbose)
        self.getlink(log=log,verbose=verbose)
        self.download(log=log,verbose=verbose)
        self.extractDEM(warpoption=warpoption,log=log,verbose=verbose)
        self.clean()
