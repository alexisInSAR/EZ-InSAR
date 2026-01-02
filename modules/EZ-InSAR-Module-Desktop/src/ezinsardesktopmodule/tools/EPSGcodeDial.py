#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a Dialog for EPSG selection

The module allows to open a Dialog for EPSG selection

    (Supplementary module for EZ-InSAR Desktop Module)

Changelog:
    * 0.1.0: Initial version, Feb. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a Dialog for EPSG selection

usage: 
    ezinsardesktop_epsg [options]

Optional-arguments:
    -b, --bbox <str> Bbox in <W,S,E,N> string format

Other-options:
    -h, --help
"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit, QComboBox, QDialog, QPushButton, QGroupBox, QScrollArea, QProgressDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView

from docopt import docopt
import os, sys, io
import folium
import pyproj
import numpy as np
from shapely.geometry import Polygon

from ezinsar import usermessage
from ezinsardesktopmodule import __file__ as __root_module__
from ezinsardesktopmodule import __versionPackage__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__

###########################################################################################
## EPSGcodeDial class
###########################################################################################
class EPSGcodeDial(QDialog):
    """QDialog class 

        Build the dialog windows
    """
    def __init__(self, parent=None, epsgcode = 4326, map = True, roi = None):
        super(EPSGcodeDial, self).__init__(parent)

        self.parent = parent
        self.map = map
        self.epsgcode = epsgcode
        self.validation = False

        ## Create the list of EPSG codes
        Dialprogress = QProgressDialog('Loading the EPSG-Code tool',None,0,100, self)
        Dialprogress.setWindowTitle('Please wait...')
        Dialprogress.show()

        if not roi == None:
            roilon = [roi[0], roi[2], roi[2], roi[0], roi[0]]
            roilat = [roi[1], roi[1], roi[3], roi[3], roi[1]]
            roi = Polygon(list(zip(roilon,roilat)))
        self.roi = roi

        self.listCode = ['']
        for idx, codei in enumerate(pyproj.get_codes('EPSG','CRS')): 
            y_proj = pyproj.CRS("epsg:{}".format(codei))

            if not roi == None:
                lon = [y_proj.area_of_use.west, 
                    y_proj.area_of_use.east, 
                    y_proj.area_of_use.east, 
                    y_proj.area_of_use.west, 
                    y_proj.area_of_use.west]
                lat = [y_proj.area_of_use.south, 
                    y_proj.area_of_use.south, 
                    y_proj.area_of_use.north, 
                    y_proj.area_of_use.north, 
                    y_proj.area_of_use.south]
                
                polycode = Polygon(list(zip(lon,lat)))
                if polycode.intersection(self.roi).area/self.roi.area*100 > 0:
                    self.listCode.append(y_proj.name + ' - Code: %s' % (codei))
            else: 
                self.listCode.append(y_proj.name + ' - Code: %s' % (codei))
            
            if np.fix((idx+1)/1000) == (idx+1)/1000:
                Dialprogress.setValue(int(100*((idx+1)/len(pyproj.get_codes('EPSG','CRS')))))
                QApplication.processEvents()

        self.listCode = np.sort(self.listCode).tolist()

        ## Create the dialog
        EPSGcodefindlabel = QLabel("<p><b>Search an EPSG CRS code:<\b></p>")
        EPSGcodefindlabel.setToolTop = """<Search an EPSG CRS code based on strings>"""
        self.EPSGcodefindLineEdit = QLineEdit()
        if not self.epsgcode == None: 
            self.EPSGcodefindLineEdit.setText('Code: %s' % (self.epsgcode))
        else:
            self.EPSGcodefindLineEdit.setText('')
        self.EPSGcodefindLineEdit.setPlaceholderText('Entre an EPSG CRS code')
        self.EPSGcodefindLineEdit.textChanged.connect(self.updateDial)

        EPSGcodeListlabel = QLabel("<p><b>List of EPSG CRS codes:<\b></p>")
        EPSGcodeListlabel.setToolTop = """<List of EPSG CRS codes available>"""
        self.EPSGcodeList = QComboBox()
        self.EPSGcodeList.addItems(self.listCode)
        self.EPSGcodeList.currentTextChanged.connect(self.updateEPSG)

        groupinfo = QGroupBox('CRS Information')
        areainfo = QScrollArea()
        self.infoLabel = QLabel("Please select a CRS")
        self.infoLabel.setWordWrap(True)
        areainfo.setWidget(self.infoLabel)
        areainfo.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        areainfo.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        areainfo.setWidgetResizable(True)
        layoutgroupinfo = QGridLayout()
        layoutgroupinfo.addWidget(areainfo , 0, 0)
        groupinfo.setLayout(layoutgroupinfo)

        if self.map == True:
            m, data = self.createmap()
            self.mapWidget = QWebEngineView()
            self.mapWidget.setHtml(data.getvalue().decode())

        self.btCancel = QPushButton("Cancel")
        self.btCancel.clicked.connect(self.cancel)
        self.btOkay = QPushButton("Select the current EPSG code")
        self.btOkay.clicked.connect(self.valid)

        mainLayout = QGridLayout()
        mainLayout.addWidget(EPSGcodefindlabel, 0, 0, 1, 1)
        mainLayout.addWidget(self.EPSGcodefindLineEdit, 0, 1, 1, 1)
        mainLayout.addWidget(EPSGcodeListlabel, 1, 0, 1, 1)
        mainLayout.addWidget(self.EPSGcodeList, 1, 1, 1, 1)
        if self.map == True:
            mainLayout.addWidget(groupinfo, 3, 0, 1, 1)    
            mainLayout.addWidget(self.mapWidget, 3, 1, 1, 1)
        else: 
            mainLayout.addWidget(groupinfo, 3, 0, 1, 2)    

        mainLayout.addWidget(self.btOkay, 10, 1, 1, 1)
        mainLayout.addWidget(self.btCancel, 10, 0, 1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("EZ-InSAR - EPSG CRS Selection")
        self.setGeometry(200,200,600,600)

        self.updateDial()
        self.updateEPSG()
        Dialprogress.close()
    
    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def updateDial(self):
        """Update the Dialog         
        """
        newlist = []
        if self.EPSGcodefindLineEdit.text() == '':
            newlist = self.listCode
        else: 
            for codei in self.listCode: 
                text = self.EPSGcodefindLineEdit.text().split()
                check = []
                for text in self.EPSGcodefindLineEdit.text().split():
                    if text.lower() in codei.lower(): 
                        check.append(True)
                    else: 
                        check.append(False)
                if not False in check: 
                    newlist.append(codei)
        self.EPSGcodeList.clear()
        self.EPSGcodeList.addItems(newlist)

        if not self.infoLabel.text() == 'Please select a CRS':
            self.btOkay.setEnabled(True)
        else: 
            self.btOkay.setEnabled(False)

    def updateEPSG(self):
        """Update the EPSG code         
        """
        if 'QComboBox' in str(type(self.sender())): 
            try: 
                self.epsgcode = int(self.EPSGcodeList.currentText().split('- Code: ')[-1])
                tmp = pyproj.CRS("epsg:{}".format(self.epsgcode))
                self.infoLabel.setText(str(tmp.to_string))
                lon = [tmp.area_of_use.west, 
                        tmp.area_of_use.east, 
                        tmp.area_of_use.east, 
                        tmp.area_of_use.west, 
                        tmp.area_of_use.west]
                lat = [tmp.area_of_use.south, 
                        tmp.area_of_use.south, 
                        tmp.area_of_use.north, 
                        tmp.area_of_use.north, 
                        tmp.area_of_use.south]
                if self.map == True:    
                    m ,data = self.createmap(lon=lon,lat=lat)
                    self.mapWidget.setHtml(data.getvalue().decode())

            except: 
                self.infoLabel.setText('Please select a CRS')
                if self.map == True:    
                    m ,data = self.createmap()
                    self.mapWidget.setHtml(data.getvalue().decode())

        if not self.infoLabel.text() == 'Please select a CRS':
            self.btOkay.setEnabled(True)
        else: 
            self.btOkay.setEnabled(False)
    
    def createmap(self,lon=None,lat=None):
        """Create the map if required    
        """
        m = folium.Map(
            location=[0,0], zoom_start=1
            )
        if not lat == None:
            folium.PolyLine(list(zip(lat,lon)),
                        color='red',
                        weight=2,
                        popup=folium.Popup('CRS Bounds'),
                        opacity=1).add_to(m)
            
        if not self.roi == None:
            folium.PolyLine(list(zip(self.roi.exterior.xy[1],self.roi.exterior.xy[0])),
                        color='black',
                        weight=2,
                        popup=folium.Popup('Region of Interest'),
                        opacity=1).add_to(m)

            m.fit_bounds([[np.min(lat), np.min(lon)], [np.max(lat), np.max(lon)]])     
        data = io.BytesIO()
        m.save(data, close_file=False)

        return m, data
    
    def valid(self):
        """Validation    
        """
        self.validation = True
        self.accept()

    def cancel(self):
        """Cancelation        
        """
        self.validation = False
        self.close()

###########################################################################################
## Main 
###########################################################################################
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    usermessage.openingmsg(__file__,__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the EPSG code tool',None,True,lockfree=True)
    
    if not args['--bbox'] == None: 
        checkbbox = True
        bbox = args['--bbox'].split(',')
        if len(bbox) == 4:
            for idx, bi in enumerate(bbox):
                try:
                    bbox[idx] = float(bi)
                except:
                    checkbbox = False
        else: 
            checkbbox = False
        if not checkbbox == True:
            raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__versionPackage__,'The ROI is not recognised.',None))
    else: 
        bbox = None
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        widget = EPSGcodeDial(roi=bbox)
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()