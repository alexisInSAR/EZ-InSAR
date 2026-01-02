#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open the Map-Displayer Widget

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.0: Tile virtualisation, Aug. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Mar. 2025

"""

__docstringapp__ = """Open the Map-Displayer Widget

usage: 
    ezinsardesktop_mapdisplayer -f <str> [options]

Arguments:
    -f, --file <str>        Image (georeferenced) file

Other-options:
    -h, --help
"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QEvent, QUrl
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtWidgets import QApplication, QGridLayout, QPushButton, QWidget, QGroupBox, QLabel, QDialog, QCheckBox, QComboBox, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

import os, sys, io
from docopt import docopt

import folium
from folium import plugins

from matplotlib.colors import ListedColormap
import matplotlib
from localtileserver import get_folium_tile_layer, TileClient

import numpy as np
import glob

from osgeo import gdal, osr

from ezinsar import constants, usermessage
from ezinsar.tools import formattools
from ezinsar.eicomponents.demmodule import demfunctions
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule.config import settings
from ezinsar.tools import __file__ as __fileColormaps__
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__

list_colormap = [x.replace('.csv','').replace('cmap_','') for x in glob.glob(__fileColormaps__.replace('__init__.py','colormap'+os.sep+'*.csv'))]
name_colormap = [x.split(os.sep)[-1] for x in list_colormap]

###########################################################################################
## Class for the Wizard
###########################################################################################
class optionsDial(QDialog):
    """Class definition"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  

        self.setWindowTitle('Options')
        self.validation = False

        layout = QGridLayout()

        LabelNoData = QLabel('<p><b>Mask no-data value:</b></p>')
        self.NoData = QCheckBox('Enable the masking')
        self.NoData.setChecked(self.parent.options['MaskNoData'])

        LabelColormap = QLabel('<p><b>Colormap:</b></p>')
        self.Colormap = QComboBox()
        self.Colormap.addItems(name_colormap)
        self.Colormap.setCurrentIndex(name_colormap.index(self.parent.options['Colormap']))

        btOkay = QPushButton('Okay')
        btOkay.clicked.connect(self.save)

        layout.addWidget(LabelNoData,0,0,1,1)
        layout.addWidget(self.NoData,0,1,1,1)
        layout.addWidget(LabelColormap,1,0,1,1)
        layout.addWidget(self.Colormap,1,1,1,1)

        layout.addWidget(btOkay,2,1,1,1)

        self.setLayout(layout)

    def save(self):
        self.parent.options = {'MaskNoData' : self.NoData.isChecked(),
                            'Colormap' : self.Colormap.currentText()}
        self.validation = True
        self.close()

class WebEnginePage(QWebEnginePage):
    """Class definition"""
    roiSignal = pyqtSignal(str) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  
        self.roi = '' 

class mapdisplayer(QWidget):
    """Class definition"""
    closing = pyqtSignal(bool)

    def __init__(self, file, parent=None):
        super(mapdisplayer, self).__init__(parent)

        self.file = file
        self.setWindowTitle("EZ-InSAR - Map Displayer: %s" % (file.split(os.sep)[-1]))
        self.resize(750, 500)
        self.mapid = constants.__cachedir__ + os.sep + 'maptmp.html'

        self.map = None

        self.options = {'MaskNoData' : True,
                        'Colormap' : 'jet'}

        self.zoom = 1

        self.setStyleSheet(__theme__)

        toolbar = QGroupBox()
        toolbarLayout = QGridLayout()

        optionsLabel = QPushButton('Options')        
        optionsLabel.clicked.connect(self.openOptions)
        optionsLabel.setEnabled(False)

        toolbarLayout.addWidget(optionsLabel,0,0)

        toolbar.setLayout(toolbarLayout)

        #########################################################################
        ## Create the map object
        self.createmap(init=True)
        
        ########################################################################
        ## Layout
        layout = QGridLayout()

        layout.addWidget(toolbar, 0, 0, 1, 3)
        layout.addWidget(self.object, 1, 0, 10, 15)

        self.setLayout(layout)

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def createimagemap(self,file):
        if not formattools.epsg_from_raster(file) == 4326:
            fileopen = constants.__cachedir__+os.sep+'tmptile.tif'
            demfunctions.warp(file,
                fileopen,
                epsg = 4326,
                nodata=False,
                format='GTiff',
                verbose=False,
                log=None)
        else:
            fileopen = file

        # Open the image
        with gdal.Open(fileopen) as ftiff: 
            ulx, xres, xskew, uly, yskew, yres  = ftiff.GetGeoTransform()
            lrx = ulx + (ftiff.RasterXSize * xres)
            lry = uly + (ftiff.RasterYSize * yres)
            projtiff = osr.SpatialReference(wkt=ftiff.GetProjection())            
            nodata = ftiff.GetRasterBand(1).GetNoDataValue()
            bounds = [[lry, ulx], [uly, lrx]]

            if ftiff.GetRasterBand(1).DataType == 1:
                colormap = None
            else:
                if 'cc' in file.split(os.sep)[-1] or 'coh' in file.split(os.sep)[-1]:
                    self.options['Colormap'] = 'gray'
                else:
                    self.options['Colormap'] = 'jet'
                colormap = matplotlib.colormaps[self.options['Colormap']]

        name = file

        return name, nodata, colormap, bounds
    
    def openOptions(self):
        reply = optionsDial(parent=self)
        reply.exec_()
        if reply.validation: 
            self.createmap()

    def createmap(self,init=False):
        self.map = None
        self.map = folium.Map(
                location=[0,0], zoom_start=1,
                tiles=None,
                    )
        
        name, nodata, colormap, bounds = self.createimagemap(self.file)
        
        ## Create the map
        folium.raster_layers.TileLayer(tiles='openstreetmap', name='OpenStreetMap').add_to(self.map)

        ## Create the data tiles
        client = TileClient(name)
        t = get_folium_tile_layer(client,nodata=nodata,attr='EZ-InSAR data',overlay=True,name=self.file.split(os.sep)[-1],colormap=colormap)
        self.map.add_child(t)

        ## Others
        # import branca.colormap as cm
        # colormap = cm.linear.Set1_09.scale(0, 35).to_step(10)
        # colormap.caption = "A colormap caption"
        # self.map.add_child(colormap)

        self.map.fit_bounds(bounds)  
        self.map = tools.addfoliumTile(self.map)
            
        plugins.MousePosition().add_to(self.map)
        plugins.MeasureControl().add_to(self.map)
        folium.LayerControl(collapsed=True).add_to(self.map)
        
        self.object= QWebEngineView() 
        page = WebEnginePage(self.object)
        self.object.setPage(page)
        
        if not settings.__foliumCached__:
            data = io.BytesIO()
            self.map.save(data, close_file=False) 
            self.object.setHtml(data.getvalue().decode())
        else:
            if os.path.isfile(self.mapid):
                os.remove(self.mapid)
            self.map.save(self.mapid,close_file=True) 
            if init:
                self.object.load(QUrl.fromLocalFile(self.mapid))
            else:
                self.object.reload()

###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not os.path.isfile(args['--file']):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No file',None))
    
    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the Map Displayer from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    
    if tools.checklicense():
        widget = mapdisplayer(os.path.abspath(args['--file']))
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()
        
if __name__=='__main__':
    main()

