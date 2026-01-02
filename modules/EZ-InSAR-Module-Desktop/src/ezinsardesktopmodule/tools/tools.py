#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Supplementary tools

The module allows to add some supplementary tools

    (Supplementary module for EZ-InSAR Desktop Module)

Changelog:
    * 1.0.0: Initial version, Mar. 2025

"""
import mimetypes
import datetime 
import os, subprocess
from ezinsardesktopmodule.config import settings
import folium
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)

from ezinsar.constants import __cachedir__
from ezinsar.tools import miscellaneous

from ezinsardesktopmodule.config import licenseDial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap

def checklicense():
    """Check the license agreements"""
    licenses = miscellaneous.checklicense(asklicense=False)

    rundial = False
    for li in licenses:
        if not li['licensevalidated']:
            rundial = True

    if rundial:
        licWin = licenseDial.licenseDial(licenses=licenses)
        licWin.show()
        licWin.exec_()

        if licWin.validation == True: 
            return True
        else:
            return False
    
    else:
        return True
    
def create_logo_wigdet(logo=__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop.svg'):
    """Create a EZ-InSAR logo"""
    widgetlogo = QLabel()

    if QApplication.primaryScreen().size().width()> 2000:
        x = 128
    else:
        x = 64
    Logo = QPixmap(logo).scaled(x,x, Qt.KeepAspectRatio,Qt.SmoothTransformation)
    Logo.setDevicePixelRatio(QApplication.primaryScreen().devicePixelRatio())
    widgetlogo.setPixmap(Logo)

    return widgetlogo

def checkGDALimage(file):
    """Check if an image is GDAL-compatible"""
    status = subprocess.Popen(['gdalinfo', '%s' % (file)],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True)
    reply = status.stdout.readlines()
    if 'ERROR' in reply[0]:
        check = False
        metadata = None
    else:
        if 'Coordinate System is:' in ''.join(reply):
            check = True
            metadata = ''.join(reply)
        else:
            check = False
            metadata = ''.join(reply)

    return check, metadata

def is_binary_string(bytes_data):
    """Heuristic to check if bytes are binary or text."""
    text_chars = bytearray({7, 8, 9, 10, 12, 13, 27}
                           | set(range(0x20, 0x100)) - {0x7f})
    return bool(bytes_data.translate(None, text_chars))

def detect_file_type(file_path):
    """
    Detects file type
    """
    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type:
        general_type = mime_type.split(os.sep)[0]
        if 'text' in general_type:
            return 'ASCII text'
        elif 'image' in general_type:
            return 'image data'

    try:
        with open(file_path, 'rb') as f:
            sample = f.read(2048)

            # Known magic number checks
            if sample.startswith(b'\xFF\xD8'):
                return 'image data, jpeg format'
            elif sample.startswith(b'\x89PNG\r\n\x1a\n'):
                return 'image data, png format'
            elif sample.startswith(b'GIF87a') or sample.startswith(b'GIF89a'):
                return 'image data, gif format'
            elif sample.startswith(b'\x42\x4D'):
                return 'image data, bmp format'
            elif sample.startswith(b'\x49\x49\x2A\x00') or sample.startswith(b'\x4D\x4D\x00\x2A'):
                return 'image data, tiff format'
            # elif sample.startswith(b'PK\x03\x04'):
            #     return 'archive', 'application/zip'
            # elif sample.startswith(b'%PDF-'):
            #     return 'image data, pdf format'
            elif sample.startswith(b'\x59\xA6\x6A\x95'):
                return 'image data, ras format'

            if is_binary_string(sample):
                return 'data'
            else:
                return 'ASCII text'

    except Exception as e:
        return 'None'

def processingstep(subjob):
    """List the processing steps"""
    liststep = []
    for vi in list(vars(subjob)):
        tmp = eval("subjob.%s" % (vi))
        if isinstance(tmp,dict):
            liststep.append(vi)

    return liststep

def mode2title(mode):
    """Create the processing title"""
    if mode == 'coregistration':
        title = 'Coregistration Processing'
    elif mode == 'ifgstack':
        title = 'Interferometric-stack Processing'
    elif mode == 'tsprocessing': 
        title = 'Time-series Analysis Processing'
    elif mode == 'intstack':
        title = 'Intensity-stack Processing'
    elif mode == 'offsetprocessing':
        title = 'Offset-Tracking Processing'

    return title

def listprocessor(mode):
    """List the processors""" 
    if mode in ['coregistration','ifgstack']: 
        list = ['ISCE2','Doris','SNAP']
        try: 
            if os.environ['ezinsargamma'] in ['True','true',True,1]:
                from ezinsargammamodule import __file__
                checkgamma = True
        except:
            checkgamma = False
        if checkgamma: 
            list = list + ['GAMMA']
    elif mode in ['tsprocessing']:
        list = ['StaMPS','MintPy','MiaplPy','SARvey']

    elif mode in ['intstack']:
        list = ['GAMMA','SNAP']
    
    elif mode in ['offsetprocessing']:
        list = ['GAMMA']

    return list

def listapproach(processor): 
    """List the InSAR approaches"""
    if processor == 'stamps':
        list = ['sbas','ps']
    elif processor == 'miaplpy':
        list = ['ps'] 
    else:
        list = ['sbas'] 
    return list

def checkprogress(subjob):
    """Check the progress of processing"""
    step = []
    for stepi in processingstep(subjob):
        if (not 'update' in stepi) and (not 'email' in stepi) and (not 'mintpy' in stepi) and (not 'plotoptions' in stepi): 
            tmp = eval("subjob.%s['done']['value']" % (stepi))
            if tmp: 
                step.append(True)
            else: 
                step.append(False)

    return step

def coloriselog(msg):
    """Add colors to log"""
    newtext=[]
    msg = msg.split('\n')
    
    checkwarning = False
    checkerror = False
    for idx, msgi in enumerate(msg):
        try:
            datetime.datetime.strptime(msgi[0:23].replace(',','.'),"%Y-%m-%d %H:%M:%S.%f")
            datedetect = True
        except:
            datedetect = False
        
        if datedetect:
            if ('- WARNING -' in msgi):
                checkwarning = True
                checkerror = False
            elif ('- ERROR -' in msgi):
                checkerror = True
                checkwarning = False
            else:
                checkerror = False
                checkwarning = False

        if checkwarning:               
            newtext.append('<span style="color:#FF7800"><br>%s</span>' % (msgi))
        elif checkerror:
            newtext.append('<span style="color:#A40000"><br>%s</span>' % (msgi))
        else:
            newtext.append('<span style=""><br>%s</span>' % (msgi))

    newtext = '\n'.join(newtext)
    return(newtext)

def addfoliumTile(m):
    """Add supplementary tiles for Folium maps"""
    if settings.__UnlockTiles__ == True:   
        from ezinsar import __file__
        tilesfile = {'Name': [],'Tile': [],'Contributors': []}
        with open(__file__.replace('__init__.py','3rdparty'+os.sep+'WMS'+os.sep+'foliumtiles.csv'),'r') as fconf:
            for lines in fconf.readlines():
                tilesfile['Name'].append(lines.split(' -/- ')[0].strip())
                tilesfile['Tile'].append(lines.split(' -/- ')[1].strip())
                tilesfile['Contributors'].append(lines.split(' -/- ')[2].strip())

        for idx, tilei in enumerate(tilesfile['Tile']):
            folium.TileLayer(
                tiles = tilesfile['Tile'][idx],
                attr = tilesfile['Contributors'][idx],
                name = tilesfile['Name'][idx],
                overlay = False,
                control = True,
                show=False,
            ).add_to(m)
    return m 

def send_cmd(args):
    from ezinsardesktopmodule.tools.tools import __help_CLI__
    from subprocess import call
    
    if not args['<args>']: 
            
            print(__help_CLI__)
    elif args['<args>'][0] in ['-h','--help', None]:
            from ezinsardesktopmodule.tools.tools import __help_CLI__
            print(__help_CLI__)
    elif args['<args>'][0] in ['create','parameter','directory','log','roi','satparameter','SLClist','SLCmap','downloader','DEM','initprocess','parameterprocess','run','config','about','S1track','S1baselines','TSdisplayer','imagedisplayer','mapdisplayer','epsg','license','inspector','exportdata','docs']:
            exit(call(['ezinsardesktop_%s' % (args['<args>'][0])]+args['<args>'][1::]))
    else:
            from ezinsardesktopmodule.tools.tools import __help_CLI__
            print(__help_CLI__)

__help_CLI__ = """EZ-InSAR Desktop Application (command-line interface)

usage:  
        ezinsar desktop <command> [<args>...] 
        ezinsar desktop -h | --help

ezinsar desktop is a command-line interface for EZ-InSAR Desktop application. It allows
to run indivisual tools integrated into the Graphical User Interface. 
        
The Job-related commands are:
        create                      Create an EZ-InSAR job
        parameter                   Open the EZ-InSAR job parameter tool
        directory                   Open the EZ-InSAR job directory tool
        log                         Open the EZ-InSAR log tool

The ROI-related command is:
        roi                         Open the EZ-InSAR Region of Interest tool

The Satellite-related commands are:
        satparameter                Open the EZ-InSAR satellite parameter tool
        SLClist                     Open the EZ-InSAR SLC list
        SLCmap                      Open a map with SLC extents
        downloader                  Open the SAR downloader
        S1track                     Open a tool for automatic track and relative orbit detection
        S1baselines                 Open a tool for pre-computation of baselines with the ASF server

The DEM-related command is: 
        DEM                         Open the DEM tool

The Processing-related commands are:
        initprocess                 Open a dialog to initiate an EZ-InSAR processing   
        parameterprocess            Open a tool to change the parameters of an EZ-InSAR processing job
        run                         Open a dialog to run an EZ-InSAR processing

The Display-related commands are:
        TSdisplayer                 Open the Time-series displayer of EZ-InSAR
        inspector                   Open the image inspector of EZ-InSAR
        imagedisplayer              Open the image displayer of EZ-InSAR
        mapdisplayer                Open the map displayer of EZ-InSAR

The Data-related command is:
        exportdata                  Open the data-export tool of EZ-InSAR

The Configuration-related commands are:
        epsg                        Open the EPSG-code tool

The Configuration-related commands are:
        config                      Open a dialog to configure EZ-InSAR   
        about                       Open the About dialog
        docs                        Open the documentation tool

Options: 
        -h, --help      Show this screen.

See 'ezinsar desktop <command> --help' for more information on a specific command.
"""