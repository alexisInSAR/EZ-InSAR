#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module from the **EZ-InSAR** constants

The module stores the different `ezinsar` constants, required by **EZ-InSAR**. Some parameters can be modified by the user.  
    
    (From `ezinsar` package)

Attributes:
    __name__ (str): Name of the Python package
    __author__ (str): Main authors of `ezinsar`
    __copyright__ (str): Copyright
    __version__ (str): Current version
    __error__ (str): Header for the error message
    __warning__ (str): Header for the warning message
    __displayline1__ (str): String line (1)
    __displayline2__ (str): String line (2)
    __sensors__ (dict): Table of sensors/modes available in EZ-InSAR for InSAR applications
    __sensorsintensity__ (dict): Table of sensors/modes available in EZ-InSAR for intensity applications
    __listmode__ (list): List of sensors/modes available in EZ-InSAR for InSAR applications
    __listmodeintensity__ (list): List of sensors/modes available in EZ-InSAR for intensity applications
    __beamRSAT__ (list): List of RADARSAT beams
    __requirement_ISCE2__ (list): Absolute pathes needed to be added to the os environment for ISCE-2
    __requirement_ISCE2_Python__ (list): Absolute pathes needed to be added to the os environment for Python
    __ISCE2_modesymlink__ (bool): Usage of symbolic link for ISCE-2
    __requirement_Doris__ (list): Absolute pathes needed to be added to the os environment for Doris
    __dorisTScompatibility (list): List of TS processors compatible with Doris
    __requirement_SNAP__ (list): Absolute pathes needed to be added to the os environment for SNAP
    __SNAPcachemax__ (int): Max value for the SNAP cache
    __requirement_StaMPS__ (list): Absolute pathes needed to be added to the os environment for StaMPS
    __defautprocessor__ (str): Default processor [default: 'isce2']
    __S1server__ (str): Default server for Sentinel-1 imagery [default: 'Copernicus']
    __cachedir__ (str): Directory of the EZ-InSAR cache
    __loggingmode__ (str): Logging level. **Can be modified by the user**. Can be ``NOTSET``, ``DEBUG``, ``INFO``, ``WARN``, ``ERROR``, ``CRITICAL``
    __username__ (str): Username of the SLC server for downloading (i.e., ``Copernicus`` for ``S1``). **Can be modified by the user**.
    __password__ (str): Password of the SLC server for downloading (i.e., ``Copernicus`` for ``S1``). **Can be modified by the user**.
    __wgetlimit__ (str): wget limit rate for SLC downloading [default: '12.5m']
    __chunksize__ (int): chunk limit for SLC downloading [default: 4096*2]
    __SLCdownloader__ (str): mode for the downloader. Can be python or wget [default: python]
    __sleepSLCdownload__ (int): Sleep time in seconds for SLC downloading. [default: 2]
    __linkAW3D30__ (str): Link to the ALOS DEM imagery
    __tilesAW3D30__ (str): Link to the ALOS DEM tile information
    __webappdebugmode__ (bool): Debug mode of the EZ-InSAR standalone application
    __webappaddress__ (str): Default address of the EZ-InSAR standalone application
    __webappport__ (int): Default port of the EZ-InSAR standalone application 
    __webappmaxlinelog__ (int): Max. lines displayed in the EZ-InSAR standalone application
    __webappreverselog__ (bool): Inversion of line order for the log of the EZ-InSAR standalone application [Default: ``False``]
    __serverdebugmode__ (bool):  Debug mode of the EZ-InSAR server
    __nameserver__ (str): Name of the EZ-InSAR server
    __adminname__ (str): Admin name for the EZ-InSAR server
    __serveraddress__ (str): Default address of the EZ-InSAR server
    __serverport__ (int): Default port of the EZ-InSAR server
    __nbcontainers__ (int): Max. number of container per user for the EZ-InSAR server
    __maxcore__ (int): Max. number of cores per user for the EZ-InSAR server
    __maxram__ (int): Max. number of RAM per user for the EZ-InSAR server
    __websitetestconn__ (str): Default website to test the internet connection
    __imagelicensencu__ (str): Default Link for the image for the NCU license
    __licensetextncu__ (str): Default Link for the test for the NCU license
    __msglicensencu__  (str): Default Link for the message for the NCU license
    __imagelicense__ (str): Default Link for the image for the CU license
    __licensetext__  (str): Default Link for the test for the CU license 
    __msglicense__  (str): Default Link for the message for the CU license
  
Changelog:
    * 3.3.0: Several changes have been done, Oct. 2025, Alexis Hrysiewicz 
        * Add the conda variables
    * 3.2.0: Several changes have been done, May. 2025, Alexis Hrysiewicz 
        * Move variables in the configuration file
        * Modification of the configuration file locations
        * Delete the pandas reading
    * 3.1.0: Several changes have been done, Feb. 2024, Alexis Hrysiewicz
        * __serverdatabase__ has been added. 
        * __CopernicusSLCdownloader__ has been changed to __SLCdownloader__ 
        * Add the RSAT2 support
    * 3.0.0: Initial version, Dec. 2024

"""

################################################################################
from ezinsar import __namePackage__
from ezinsar import __copyrightPackage__
from ezinsar import __versionPackage__
from ezinsar import __authorPackage__

from datetime import datetime
import os 
# import pandas as pd
import numpy as np
import platform

################################################################################
__name__ =  __namePackage__
__author__ = __authorPackage__
__copyright__ = __copyrightPackage__
__version__ = __versionPackage__

__error__ = 'ERROR in EZ-InSAR processing:'
__warning__ = 'WARNING in EZ-InSAR processing:'

__displayline1__ = '################################################################################'
__displayline2__ = '--------------------------------------------------------------------------------'

################################################################################
## Read the EZ-InSAR configuration file
################################################################################
home_dir = os.path.expanduser("~")

conffile = False

conf_username = 'username' 
conf_password = 'password'
conf_tokenM2M = 'none'
conf_cache = home_dir + os.sep + '.ezinsar' + os.sep + 'cache'

if platform.system == 'Windows': 
    conf_pathisce2 = ['<Dummy Path>']
    conf_pathsnappy = '<Dummy Path>'
    conf_pathsnapgpt = '<Dummy Path>'
    conf_pathdoris = '<Dummy Path>'
    conf_pathstamps = '<Dummy Path>'
    conf_pathlicsbas = '<Dummy Path>'
else:
    conf_pathisce2 = ['/usr/local/isce2']
    conf_pathsnappy = '/usr/local/esa-snap/bin'
    conf_pathsnapgpt = '/usr/local/esa-snap/bin'
    conf_pathdoris = '/usr/local/doris'
    conf_pathstamps = '/usr/local/stamps'
    conf_pathlicsbas = '/usr/local/licsbas'

conf_pathserverdatabase = home_dir+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'server.config'
conf_licenseagreements = False

pathisce2 = '/usr/local/bin'
conf_pathisce2Python = []

conf_ISCE2modesymlink = True 
conf_SNAPcachemax = 5000
conf_SNAPcacheclean = True
conf_SNAPwrapper = 'gpt'
conf_defautprocessor = 'isce2'
conf_S1server = 'Copernicus'
conf_loggingmode = 'INFO'
conf_nameDockerImage = 'ezinsar'
conf_mintpycondaenv = 'default'
conf_isce2condaenv = 'default'
conf_licsbascondaenv = 'default'
conf_miaplpycondaenv = 'default'
conf_sarveycondaenv = 'default'
conf_wgetlimit = 'auto'
conf_wgetlimitmin = '12.5m'
conf_wgetlimitmax = '50.0m'
conf_chunksize = 8192
conf_SLCdownloader = 'python'
conf_sleepSLCdownload = 2

if os.path.isfile(home_dir+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'user.config'):
    # conf = pd.read_csv(home_dir+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'user.config',delimiter='::',header=None,engine='python',names=['Variable','Value'])
    
    conf = {'Variable': [],'Value': []}
    with open(home_dir+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'user.config','r') as fconf:
        for lines in fconf.readlines():
            conf['Variable'].append(lines.split('::')[0].strip())
            conf['Value'].append(lines.split('::')[-1].strip())

    for proci in ['username', 'password','tokenM2M','cache', 'pathisce2', 'pathsnappy', 'pathdoris', 'pathstamps','pathlicsbas','pathsnapgpt','pathserverdatabase','licenseagreements',
    'ISCE2modesymlink','SNAPcachemax','SNAPcacheclean','SNAPwrapper','defautprocessor','S1server','loggingmode','nameDockerImage','mintpycondaenv','isce2condaenv','licsbascondaenv','miaplpycondaenv', 'sarveycondaenv','wgetlimit','wgetlimitmin','wgetlimitmax','chunksize','SLCdownloader','sleepSLCdownload',
    ]:
        if proci in list(conf['Variable']): 
            idx = np.where(proci == np.array(list(conf['Variable'])))[0][0]

            if not proci == 'pathisce2': 
                exec('conf_%s = r"%s"' % (proci,conf['Value'][idx]))
            else: 
                conf_pathisce2 = []
                pathisce2 = conf['Value'][idx]
                for li in ['install','install/bin','install/packages','install/packages/isce2/applications','contrib/stack/','contrib/stack/topsStack','contrib/timeseries/prepStackToStaMPS/bin','applications']: 
                    conf_pathisce2.append(pathisce2+os.sep+li)

    conf_pathisce2Python = []
    for li in ['install','install/packages']: 
        conf_pathisce2Python.append(pathisce2+os.sep+li)

conf_pathisce2.append(__file__.replace('constants.py','3rdparty'))
conf_pathisce2.append(__file__.replace('constants.py','3rdparty'+os.sep+'isce2mod'))

################################################################################
## List of EZ-InSAR modules
################################################################################
__EZInSARoptionalmodule__ = ['desktop','gamma','gnss','multispectral','nisar','saocom','server','webapp','weather','tsdisplayer','postprocessing','hydroocean']
__EZInSARoptionalmoduleSAT__ = ['nisar','saocom']
__EZInSARoptionalmoduleProcessor__ = ['gamma']
__EZInSARserverImagery__ = ['Copernicus','ASF','EarthDATA','GEODES']

################################################################################
## Export formats
################################################################################
__exportformatvector__ = ['CSV','ESRI Shapefile','GeoJSON','XLSX']
__exportformatvectorext__ = ['.csv','.shp','.GeoJSON','.xlsx']

################################################################################
## Available DEMs
################################################################################
__DEMlist__ = ['SRTM','SRTM-ell',
        'NASADEM','NASADEM-ell',
        'Copernicus','Copernicus-ell',
        'Copernicus3','Copernicus3-ell',
        'AW3D30',
        'AW3D30-ell',
        'RGEALTI-1m',
        'RGEALTI-5m',
        'COPDEM30','COPDEM30-ell',
        'COPDEM90','COPDEM90-ell',
        'perso']

################################################################################
## Available sensors
################################################################################
__sensors__ = {'S1': {'IW': ['gamma','isce2','licsbas','snap'], 'SM': ['gamma','isce2','doris','snap']},
               
               'ALOS': {'FBS': ['gamma','isce2'], 'FBD': ['gamma','isce2']},
               
               'ALOS2': {'SBS': ['gamma','isce2'], 'UBS': ['gamma','isce2'], 'UBD': ['gamma','isce2'], 'SBS': ['gamma','isce2'], 'UBS': ['gamma','isce2'], 'UBD': ['gamma','isce2'], 'HBS': ['gamma','isce2'], 'HBD': ['gamma','isce2'], 'HBQ': ['gamma','isce2'], 'FBS': ['gamma','isce2'], 'FBD': ['gamma','isce2'], 'FBQ': ['gamma','isce2'],'WBS': ['gamma'],'WBD': ['gamma']}, # 'WWS WWD VBS VBD'
               
               'RSAT': {'Fine': ['gamma'], 'STD': ['gamma']}, # STD, Fine, Wide, Extended, ScanSAR
               
               'RSAT2': {'SQ': ['gamma','doris','isce2'], 'FQ': ['gamma','doris','isce2']},
               
               'TSX': {'SM': ['gamma','isce2','snap'], 'SL': ['gamma','isce2'], 'HS': ['gamma','isce2'], 'ST': ['gamma','isce2']}, #ScanSAR Wide (SCW) ScanSAR (SC)
               
               'PAZ': {'SM': ['gamma','isce2','snap','doris'], 'SL': ['gamma','isce2','doris'], 'HS': ['gamma','isce2','doris'], 'ST': ['gamma','isce2']},
               
               'CSK': {'HI': ['gamma','doris','isce2','snap'], 'PP': ['gamma']}, # HI, PP, SW, SH
               
               'CSKSG': {'SM': ['gamma'], 'PP': ['gamma']}, #  SM, PP, QP, SC1, SC2
               
               'NISAR': {'SS': ['gamma']},

               'SAOCOM': {'SM': ['gamma','doris','snap']}, #TOPSAR Narrow or TOPSAR Wide
            }

__sensorsintensity__ = {'S1': {'IW': ['gamma','snap'], 'SM': ['gamma']},
               'ALOS': {'FBS': None, 'FBD': None},
               'ALOS2': {'SBS': None, 'UBS': None, 'UBD': None, 'SBS': None, 'UBS': None, 'UBD': None, 'HBS': None, 'HBD': None, 'HBQ': None, 'FBS': None, 'FBD': None, 'FBQ': None}, # 'WBS WBD WWS WWD VBS VBD'
               'RST': {'SM': None},
               'RST2': {'SM': None},
               'TSX': {'SM': None, 'SL': None, 'HSSPT': None, 'ST': None},
               'PAZ': {'SM': None, 'SL': None, 'HSSPT': None, 'ST': None},
               'CSK': {'HI': None, 'SPT': None},
               'NISAR': {'SS': None},
            }

__listmode__ = []
for si in list(__sensors__.keys()): 
    __listmode__ = __listmode__ + list(__sensors__[si].keys())
__listmode__ = np.unique(__listmode__)

__listmodeintensity__ = []
for si in list(__sensorsintensity__.keys()): 
    __listmodeintensity__ = __listmodeintensity__ + list(__sensorsintensity__[si].keys())
__listmodeintensity__ = np.unique(__listmodeintensity__)

__beamRSAT__ = ['FN1','FN2','FN3','FN4','FN5','SNA','SNB','ST1','ST2','ST3','ST4','ST5','ST6','ST7','SWA','SWB','WD1','WD2','WD3','EH3','EH4','EH6','EL1']

__TSapproach__ = {'stamps': ['Small-Baselines Subset / sbas', 'Persistent Scatters / ps'], 
                'mintpy': ['Small-Baselines Subset / sbas'],
                'miaplpy': ['Phase-linking / ps'], 
                'sarvey': ['Phase-linking / ps'], 
                }

################################################################################
## EZ-InSAR License
################################################################################
__licenseagreements__ = (conf_licenseagreements=='True')

################################################################################
## EZ-InSAR computation parameters
################################################################################
__orbit_poly_order__ = 3

################################################################################
## USGS EarthExplorer
################################################################################
__tokenM2M__ = conf_tokenM2M

################################################################################
## ISCE-2 processor information
################################################################################
__requirement_ISCE2__ = conf_pathisce2
__requirement_ISCE2_Python__ = conf_pathisce2Python
__ISCE2_modesymlink__ = (conf_ISCE2modesymlink=='True')

################################################################################
## Doris processor information
################################################################################
__requirement_Doris__ = conf_pathdoris
__dorisTScompatibility__ = ['normal','StaMPS_PS','StaMPS_SBAS','StaMPS_PSSBAS']

################################################################################
## SNAP processor information 
################################################################################
__requirement_SNAP__ = conf_pathsnappy
__requirement_SNAP_GPT__ = conf_pathsnapgpt
__SNAPcachemax__ = int(conf_SNAPcachemax)
__SNAPcacheclean__ = (conf_SNAPcacheclean=='True')
__SNAP_wrapper__ = conf_SNAPwrapper # can be snappy or gpt
__SNAPTScompatibility__ = ['normal','StaMPS_PS']

################################################################################
## StaMPS processor information 
################################################################################
__requirement_StaMPS__ = [conf_pathstamps+os.sep+'bin',conf_pathstamps+os.sep+'matlab']

# ## Modification of the startup.m required by StaMPS
# if not os.path.isdir(home_dir+os.sep+'Documents'):
#     os.mkdir(home_dir+os.sep+'Documents')
# if not os.path.isdir(home_dir+os.sep+'Documents'+os.sep+'MATLAB'):
#     os.mkdir(home_dir+os.sep+'Documents'+os.sep+'MATLAB') 

# check = False
# if os.path.isfile(home_dir+os.sep+'Documents'+os.sep+'MATLAB'+os.sep+'startup.m'):
#     with open(home_dir+os.sep+'Documents'+os.sep+'MATLAB'+os.sep+'startup.m','r') as fi:
#         for li in fi:
#             if "addpath('%s')" % (conf_pathstamps+os.sep+'matlab') in li:
#                 check = True

# if check == False:
#     with open(home_dir+os.sep+'Documents'+os.sep+'MATLAB'+os.sep+'startup.m','a') as fi:
#         fi.write("\naddpath('%s')" % (conf_pathstamps+os.sep+'matlab'))

################################################################################
## LiCSBAS processor information
################################################################################
__requirement_LiCSBAS__ = conf_pathlicsbas+os.sep+'LiCSBAS'+os.sep +'bin'+':'+conf_pathlicsbas+os.sep+'LiCSBAS'+os.sep +'LiCSBAS_lib'+':'+conf_pathlicsbas + os.sep + 'licsar_extra' + os.sep + 'python'+':'+conf_pathlicsbas + os.sep + 'licsar_proc' + os.sep + 'python'+':'

################################################################################
## Environment for the Docker container (used to force the environment)
################################################################################
__dockerenv__ = """CONDA_EXE='/miniconda3/bin/conda'
ISCE_STACK='/miniconda3/share/isce2'
conda='/miniconda3/bin/conda'
XML_CATALOG_FILES='file:///miniconda3/etc/xml/catalog file:///etc/xml/catalog'
PWD='/root'
GSETTINGS_SCHEMA_DIR='/miniconda3/share/glib-2.0/schemas'
CONDA_PREFIX='/miniconda3'
GSETTINGS_SCHEMA_DIR_CONDA_BACKUP=''
ISCE_HOME='/miniconda3/lib/python3.10/site-packages/isce'
HOME='/root'
LS_COLORS='rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=00:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc=01;31:*.arj=01;31:*.taz=01;31:*.lha=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:*.tzo=01;31:*.t7z=01;31:*.zip=01;31:*.z=01;31:*.dz=01;31:*.gz=01;31:*.lrz=01;31:*.lz=01;31:*.lzo=01;31:*.xz=01;31:*.zst=01;31:*.tzst=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.alz=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.cab=01;31:*.wim=01;31:*.swm=01;31:*.dwm=01;31:*.esd=01;31:*.avif=01;35:*.jpg=01;35:*.jpeg=01;35:*.mjpg=01;35:*.mjpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.webp=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:*~=00;90:*#=00;90:*.bak=00;90:*.crdownload=00;90:*.dpkg-dist=00;90:*.dpkg-new=00;90:*.dpkg-old=00;90:*.dpkg-tmp=00;90:*.old=00;90:*.orig=00;90:*.part=00;90:*.rej=00;90:*.rpmnew=00;90:*.rpmorig=00;90:*.rpmsave=00;90:*.swp=00;90:*.tmp=00;90:*.ucf-dist=00;90:*.ucf-new=00;90:*.ucf-old=00;90:'
CONDA_PROMPT_MODIFIER='(base)'
CPL_ZIP_ENCODING='UTF-8'
LESSCLOSE='/usr/bin/lesspipe %s %s'
PYTHONPATH='/usr/lib/python3.12/dist-packages:'
TERM='xterm'
bashrc='/root/.bashrc'
CPLUS_INCLUDE_PATH='/usr/include/gdal'
LESSOPEN='| /usr/bin/lesspipe %s'
CONDA_SHLVL=1
SHLVL=1
GDAL_DRIVER_PATH='/miniconda3/lib/gdalplugins'
PROJ_DATA='/miniconda3/share/proj'
CONDA_PYTHON_EXE='/miniconda3/bin/python'
CONDA_DEFAULT_ENV='base'
GDAL_DATA='/miniconda3/share/gdal'
PATH='/miniconda3/bin:/miniconda3/condabin:/usr/lib/python3.12/dist-packages/isce/library:/usr/lib/python3.12/dist-packages/isce/helper:/usr/lib/python3.12/dist-packages/isce/defaults:/usr/lib/python3.12/dist-packages/isce/components:/usr/lib/python3.12/dist-packages/isce/applications:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
C_INCLUDE_PATH='/usr/include/gdal'
PROJ_NETWORK='ON'
_='/usr/bin/env'"""

def create_docker_string():
    for idx, li in enumerate(__dockerenv__.split('\n')):
        if idx == 0:
            cmd = 'export %s' % (li)
        else:
            cmd = cmd + '; export %s' % (li)

    return cmd 

################################################################################
## This part can be modified by the user: DON'T CHANGE THE VARIABLE TYPE
################################################################################
## General parameters
__defautprocessor__ = conf_defautprocessor
__S1server__ = conf_S1server
__cachedir__ = conf_cache

if not os.path.isdir(__cachedir__): 
    os.makedirs(__cachedir__)

if not os.path.isdir(home_dir+os.sep+'.ezinsar'+os.sep+'config'): 
    os.makedirs(home_dir+os.sep+'.ezinsar'+os.sep+'config')

## For logging
__loggingmode__ = conf_loggingmode
if __loggingmode__ == 'DEBUG':
    __SNAPloggingmode__ = True
else: 
    __SNAPloggingmode__ = False

## For Docker
__nameDockerImage__ = conf_nameDockerImage

## For conda
__mintpycondaenv__ = conf_mintpycondaenv
__isce2condaenv__ = conf_isce2condaenv
__licsbascondaenv__ = conf_licsbascondaenv 
__miaplpycondaenv__ = conf_miaplpycondaenv 
__sarveycondaenv__ = conf_sarveycondaenv

## For Server downloading
__username__ = conf_username
__password__ = conf_password
__wgetlimit__ = conf_wgetlimit = 'auto' # Only for SLC downloading 
__wgetlimitmin__ = conf_wgetlimitmin # Only for SLC downloading 
__wgetlimitmax__ = conf_wgetlimitmax # Only for SLC downloading 
__chunksize__ = int(conf_chunksize) # Only for SLC and orbit downloading  
__SLCdownloader__ = conf_SLCdownloader ## Only for Copernicus server, can be python or wget
__sleepSLCdownload__ = int(conf_sleepSLCdownload) ## Sleep time in second for Copernicus and ASF servers

## For DEMs
__linkAW3D30__ = 'https://www.eorc.jaxa.jp/ALOS/aw3d30/data/release_v2404/'
__tilesAW3D30__ = 'https://www.eorc.jaxa.jp/ALOS/jp/dataset/aw3d30/data/List_of_all_tiles_in_AW3D30.txt'

## For EZ-InSAR Webapp (standalone) (required a module)
__webappdebugmode__ = True # Can be True of False
__webappaddress__ = '0.0.0.0' # Default address for the GUI
__webappport__ = 8050 # Default port for the GUI
__webappmaxlinelog__ = 30 # Max. number of lines displayed in the GUI
__webappreverselog__ = False # Reverse the log
__webappinterval__ = 500 #updating time for the GUI (in ms)

## Information for the EZ-InSAR server
__serverdebugmode__ = True # Can be True of False
__nameserver__ = 'an UCD server'
__adminname__ = '[Alexis Hrysiewicz](https://www.icrag-centre.org/people/dralexishrysiewicz.html) (UCD/iCRAG)'
__serveraddress__ = 'dedede' # Default address for the server
__serverport__ = 8050 # Default port for the server
__serverdatabase__ = conf_pathserverdatabase
__nbcontainers__ = 4 # Default value for the number of containers
__maxcore__ = 2 # Default value for the number of cores
__maxram__ = 3543 # Default value (in Mb) for the RAM

# Check if the confif file is created
if not os.path.isfile(__serverdatabase__):
    with open(__serverdatabase__,'w') as fout: 
        fout.write('[database]\n')
        fout.write('con = sqlite:////%s \n' % (os.path.dirname(__serverdatabase__)+os.sep+'serverusers.db'))

################################################################################
## License information for the archive creation
################################################################################
__websitetestconn__ = 'https://www.icrag-centre.org'

## License for the EZ-InSAR archives (non-commercial use)
__imagelicensencu__ = 'https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-nc-sa.png'
__licensetextncu__ = 'https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.txt'
__msglicensencu__ = 'Copyright %s. This work is openly licensed via CC BY-NC-SA 4.0.' % (datetime.now().strftime('%Y'))

## License for the EZ-InSAR archives (commercial use)
__imagelicense__ = 'https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-sa.png'
__licensetext__ = 'https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt'
__msglicense__ = 'Copyright %s. This work is openly licensed via CC BY-SA 4.0.' % (datetime.now().strftime('%Y'))
