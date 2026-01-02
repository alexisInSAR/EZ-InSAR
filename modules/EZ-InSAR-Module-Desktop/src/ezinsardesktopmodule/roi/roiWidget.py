#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a window for the EZ-InSAR Region of Interest

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Feb. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a window for the EZ-InSAR Region of Interest

usage: 
    ezinsardesktop_roi -f <str> [options]

Arguments:
    -f, --file <str>        EZ-InSAR job file

Other-options:
    -h, --help
"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit, QMessageBox, QComboBox, QSpinBox, QPushButton, QFileDialog, QWidget, QInputDialog, QDialog, QGroupBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

import os, sys, io
from docopt import docopt
import numpy as np
import pandas as pd

from shapely import Polygon
from shapely.wkt import loads
import fiona
import pyproj
import copy

import folium
from folium import plugins
import json
from folium.utilities import JsCode

from ezinsar import constants, usermessage
from ezinsar import __file__ as __rootEZInSAR__
import ezinsar.job as ez
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsardesktopmodule.tools.docsWidget import DocsDialog

###########################################################################################
## Classes
###########################################################################################
class VolcanoDialog(QDialog):
    """Class definition for the Volcano Dialog"""

    def __init__(self, job, parent=None):
        super(VolcanoDialog, self).__init__(parent)

        self.job = job
        self.result = None
        
        self.setStyleSheet(__theme__)
        
        db = pd.read_csv(os.path.dirname(__rootEZInSAR__)+os.sep+'3rdparty'+os.sep+'GVP_Volcano_List_Holocene.csv')

        title = QLabel('<p style="font-size:15px"><b>Search a volcano location based on the Holocene Volcano List from Global Volcanism Program database</b></p>')
        title.setWordWrap(True)

        volcanofindlabel = QLabel("<p><b>Search a volcano:</b></p>")
        volcanofindlabel.setToolTip("""
                                <p>Use the text to find a volcano name</p>
                                """)
        self.volcanofindLineEdit = QLineEdit()
        self.volcanofindLineEdit.setText('')
        self.volcanofindLineEdit.textChanged.connect(self.search)

        volcanoseleclabel = QLabel("<p><b>Select a volcano:</b></p>")
        volcanoseleclabel.setToolTip("""
                                <p>Use the list to select a volcano</p>
                                """)
        self.listvolc = []
        for idx, volc in enumerate(db['Volcano Name']):
            self.listvolc.append(volc)
        self.listvolc = np.sort(self.listvolc)
        self.volcano = QComboBox()
        self.volcano.addItems(self.listvolc)

        volcradiuslabel = QLabel("<b>Radius [m]:</b>")
        volcradiuslabel.setToolTip("""
                                    <p>Define the radius.</p>
                                    """)
        self.volcradius = QSpinBox()
        self.volcradius.setMaximum(1000000)
        self.volcradius.setMinimum(1)
        self.volcradius.setValue(20000)

        infocredit = QLabel('<p style="font-size:10px"><i>Read the Holocene Volcano List from Global Volcanism Program database. Please cite this as: Global Volcanism Program, 2024. [Database] Volcanoes of the World (v. 5.1.7; 26 Apr 2024). Distributed by Smithsonian Institution, compiled by Venzke, E. https://doi.org/10.5479/si.GVP.VOTW5-2023.5.1<\i></p>')
        infocredit.setWordWrap(True)

        self.btOkay = QPushButton("Okay", self)
        self.btOkay.clicked.connect(self.valid)

        mainLayout = QGridLayout()
        mainLayout.addWidget(title, 0, 0, 1, 5)
        mainLayout.addWidget(volcanofindlabel, 1, 0, 1, 1)
        mainLayout.addWidget(self.volcanofindLineEdit,1, 1, 1, 4)
        mainLayout.addWidget(volcanoseleclabel, 2, 0, 1, 1)
        mainLayout.addWidget(self.volcano, 2, 1, 1, 4)
        mainLayout.addWidget(volcradiuslabel, 3, 0, 1, 1)
        mainLayout.addWidget(self.volcradius, 3, 1, 1, 4)
        mainLayout.addWidget(infocredit, 4, 0, 1, 5)
        mainLayout.addWidget(self.btOkay, 5, 4, 1, 1)

        self.setLayout(mainLayout)
        self.setWindowTitle("ROI from volcano names")

    def search(self):
        """Search callback"""
        newlist = []
        if self.volcanofindLineEdit.text == '':
            newlist = self.listvolc
        else:
            for volc in self.listvolc:
                if self.volcanofindLineEdit.text().lower() in volc.lower():
                    newlist.append(volc)
        self.volcano.clear()
        self.volcano.addItems(newlist)

        if self.volcano.currentText() == '':
            self.btOkay.setDisabled(True)
        else:
            self.btOkay.setDisabled(False)

    def valid(self):
        """Valid callback"""
        radius = self.volcradius.value()
        volc = self.volcano.currentText()
        jobtmp = copy.deepcopy(self.job)
        jobtmp.log = None
        jobtmp.importroi(input=volc,radiusvolc=radius,verbose=False)
        self.result = jobtmp.roi
        jobtmp = None
        self.accept()

class WebEnginePage(QWebEnginePage):
    """Class definition"""
    roiSignal = pyqtSignal(str) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  
        self.roi = ''    
            
    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        coords_dict = json.loads(msg)
        coords = coords_dict['geometry']['coordinates'][0]
        self.roi = str(Polygon(coords))
        self.roiSignal.emit(self.roi)

class roitool(QWidget):
    """Class definition"""
    closing = pyqtSignal(bool)

    def __init__(self, jobfile, parent=None):
        super(roitool, self).__init__(parent)

        self.pathjobfile = jobfile
        self.setWindowTitle("EZ-InSAR job - Region of Interest")
        self.resize(750, 500)
        self.setStyleSheet(__theme__)
        self.success = False
        self.false = False
        
        job = ez.load(self.pathjobfile,verbose=False)
        
        self.roi = job.roi
        
        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p style="font-size:20px"><b>Region of Interest</b></p>')
        btQuit = QPushButton("Close", self)
        btQuit.clicked.connect(self.closemaybe)

        btHelp = QPushButton("Help", self)
        btHelp.clicked.connect(self.openhelp)

        roiLabel = QLabel("<p><b>Region of Interest:</b></p>")
        roiLabel.setToolTip("""
                                <p>Region of Interest</p>
                                """)
        self.roiLineEdit = QLineEdit()
        self.roiLineEdit.setText(str(job.roi))
        self.roiLineEdit.setReadOnly(True)
        self.roiLineEdit.textChanged.connect(self.updatemap)

        # Import the map (required folium and PyQtWebEngine==5.15.2 / PyQtWebEngine-Qt5==5.15.2 because Chromium in 64 Bits)
        m, data = self.createmap(job.roi)
        self.mapWidget= QWebEngineView() 
        self.page = WebEnginePage(self.mapWidget)
        self.mapWidget.setPage(self.page)
        self.mapWidget.setHtml(data.getvalue().decode())
        self.page.roiSignal.connect(self.roifrommap)

        btimportgrp = QGroupBox('Import options')
        btimportgrpLayout = QGridLayout()
        btOpenFile = QPushButton("Open a vector file", self)
        btOpenFile.clicked.connect(self.openVector)
        btVolc = QPushButton("From a Volcano name", self)
        btVolc.clicked.connect(self.roifromvolcano)
        btCoord = QPushButton("From coordinates", self)
        btCoord.clicked.connect(self.roifromcoord)
        btimportgrpLayout.addWidget(btOpenFile,0,0,1,1)
        btimportgrpLayout.addWidget(btCoord,0,1,1,1)
        btimportgrpLayout.addWidget(btVolc,0,2,1,1)
        btimportgrp.setLayout(btimportgrpLayout)

        btSave = QPushButton("Save", self)
        btSave.clicked.connect(self.save)
        
        layout = QGridLayout()
        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 7, Qt.AlignCenter)
        layout.addWidget(btQuit, 0, 9, 1, 1)
        layout.addWidget(roiLabel, 1, 0, 1, 1)
        layout.addWidget(self.roiLineEdit, 1, 1, 1, 9)
        layout.addWidget(self.mapWidget, 2, 0, 7, 10)
        layout.addWidget(btimportgrp, 9, 0, 1, 4)
        layout.addWidget(btSave, 10, 9, 1, 1)
        layout.addWidget(btHelp, 10, 0, 1, 1)

        job = None

        self.setLayout(layout)

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def openhelp(self):
        helpdial = DocsDialog('applications%sroi%sroi.html' % (os.sep,os.sep))
        helpdial.show()
        helpdial.exec()

    def closemaybe(self):
        """Close event"""
        ret = QMessageBox.warning(self, "Quit?",
                "Do you want to save your changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if ret == QMessageBox.Save:
            self.save()
            self.closing.emit(True)
            return self.close()
        if ret == QMessageBox.Cancel:
            return False
        if ret == QMessageBox.Discard:
            self.closing.emit(True)
            return self.close()
        
    def save(self):
        """Save event"""
        job = ez.load(self.pathjobfile,verbose=False)
        job.roi = self.roi
        job.check(verbose=False)
        ez.save(job,self.pathjobfile,verbose=False)
        reply = QMessageBox.information(self, "EZ-InSAR Information",
            'The new region of interest has been saved.',
            QMessageBox.Ok)

    def roifromvolcano(self):
        """Callback for volcano selection"""
        diag = VolcanoDialog(ez.load(self.pathjobfile,verbose=False))
        diag.exec_()
        if not diag.result == None:
            self.roi = diag.result
            self.roiLineEdit.setText(str(self.roi))

    def roifromcoord(self):
        """Callback for vector-file selection"""
        text, ok = QInputDialog.getText(self, "Region from Interest from coordinates",
                "Lon/Lat Coordinates in W,S,E,N format:", QLineEdit.Normal)
        if ok and text != '':
            checkROI = True
            if len(text.split(',')) == 4:
                text = text.split(',')
                for idx, texti in enumerate(text):
                    try:
                        text[idx] = float(text[idx])
                    except:
                        checkROI = False
            else:
                checkROI = False
            
            if checkROI:
                lon = [text[0],text[2],text[2],text[0],text[0]]
                lat = [text[1],text[1],text[3],text[3],text[1]]

                bbox = Polygon(list(zip(lon, lat)))
                self.roi = bbox
                self.roiLineEdit.setText(str(self.roi))
            else:
                reply = QMessageBox.critical(self, "Error with the ROI coordinates",
                    'The %s is not compatible with EZ-InSAR.' % (text),
                    QMessageBox.Ignore)

    def roifrommap(self):
        """Callback for roi-from-map selection"""
        self.roi = loads(self.page.roi)
        self.roiLineEdit.setText(str(self.roi))

    def updatemap(self):
        """Update the map"""
        m, data = self.createmap(self.roi)
        self.mapWidget.setHtml(data.getvalue().decode())

    def openVector(self):
        """Open a vector file"""
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,
                "Select a vector file",
                "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            try:
                with fiona.open(fileName) as roifile:
                    for feature in roifile:
                        if len(feature['geometry']["coordinates"][0]) == 1:
                            bbox = Polygon(feature['geometry']["coordinates"][0][0])
                        else: 
                            bbox = Polygon(feature['geometry']["coordinates"][0])   
                        if not roifile.crs == 'EPSG:4326':
                            lontmp = []
                            lattmp = []
                            meter_to_latlon = pyproj.Transformer.from_crs(roifile.crs,'epsg:4326')
                            for index, point in enumerate(bbox.exterior.coords):
                                    lati, loni = meter_to_latlon.transform(point[0],point[1])
                                    lontmp.append(loni)
                                    lattmp.append(lati)
                            bbox = Polygon(list(zip(lontmp, lattmp)))
                        self.roi = bbox
                        self.roiLineEdit.setText(str(self.roi))
            except:
                reply = QMessageBox.critical(self, "Error with the ROI file",
                    'The ROI file is not compatible with EZ-InSAR',
                    QMessageBox.Ignore)

    def createmap(self,roi):
        """Create the map"""

        m = folium.Map(
            location=[0,0], zoom_start=1,
            tiles=None,
            )
        folium.raster_layers.TileLayer(tiles='openstreetmap', name='OpenStreetMap').add_to(m)

        if not roi == None:
            lat = roi.exterior.xy[1]
            lon = roi.exterior.xy[0]

            folium.PolyLine(list(zip(lat,lon)),
                        color='red',
                        weight=2,
                        popup=folium.Popup('Region of Interest'),
                        opacity=1).add_to(m)
            folium.PolyLine(list(zip([np.min(lat), np.min(lat), np.max(lat), np.max(lat), np.min(lat)],
                                    [np.min(lon),np.max(lon),np.max(lon),np.min(lon), np.min(lon)])),
                        color='black',
                        weight=2,
                        popup=folium.Popup('ROI used by EZ-InSAR'),
                        opacity=1).add_to(m)

            m  = tools.addfoliumTile(m)

            plugins.Geocoder().add_to(m)
            plugins.MousePosition().add_to(m)
            plugins.MeasureControl().add_to(m)
            folium.LayerControl(collapsed=True).add_to(m)
            plugins.Draw(export=False,
                        draw_options={
                            'polyline':False,
                            'rectangle':True,
                            'polygon':True,
                            'circle':False,
                            'marker':False,
                            'circlemarker':False},
                        edit_options={'edit':False, "polygon": {"allowIntersection": False}},
                        show_geometry_on_click=True,
                        on={
                            "click": JsCode(
                            """
                            function(event) {
                                alert(JSON.stringify(this.toGeoJSON()));
                            }
                            """
                            )
                        }
                        ).add_to(m)
            
            m.fit_bounds([[np.min(lat), np.min(lon)], [np.max(lat), np.max(lon)]])     

        data = io.BytesIO()
        m.save(data, close_file=False)

        return m, data

###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not os.path.isfile(args['--file']):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No file',None))

    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the EZ-InSAR Region-of-Interest tool from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        widget = roitool(os.path.abspath(args['--file']))
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()
    
if __name__=='__main__':
    main()

