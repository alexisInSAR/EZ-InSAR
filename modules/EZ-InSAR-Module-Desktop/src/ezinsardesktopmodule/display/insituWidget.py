#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open the dialog to display an EZ-InSAR insitu data 

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.0.0: Initial version, Mar. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open the dialog to display an EZ-InSAR insitu data 

usage: 
    insituWidget.py -f <str> [options]

Argmuents: 
    -f, --file <str>    File

Other-options:
    -h, --help
"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit, QMessageBox, QComboBox, QPushButton,  QWidget, QDialog, QGroupBox, QTextEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

import os, sys, io
from docopt import docopt
import plotly.graph_objects as go
import plotly

import folium
from folium import plugins

from ezinsar import usermessage

from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsar.tools import ezinsardata

###########################################################################################
## Classes
##########################################################################################
class descripDial(QDialog):
    """Import Widget"""
    closing = pyqtSignal(bool)

    def __init__(self, shdescript, lgdescript, parent=None):
        super(descripDial, self).__init__(parent)

        self.resize(500, 500)
        self.parent = parent
        self.validation = False
        self.shdescript = shdescript
        self.lgdescript = lgdescript
     
        self.setWindowTitle("EZ-InSAR - Metadata Description" )
        self.setStyleSheet(__theme__)

        layout = QGridLayout()

        label1 = QLabel('<p><b>Short Description:</b></p>')
        self.shtext = QLineEdit()
        self.shtext.setText(self.shdescript)

        label2 = QLabel('<p><b>Long Description:</b></p>')
        self.lgtext = QTextEdit()
        self.lgtext.setText(self.lgdescript)

        layout = QGridLayout()
        layout.addWidget(label1,0,0,1,1)
        layout.addWidget(self.shtext,1,0,1,1)
        layout.addWidget(label2,2,0,1,1)
        layout.addWidget(self.lgtext,3,0,5,1)

        saveBt = QPushButton('Save')
        saveBt.clicked.connect(self.save)
        layout.addWidget(saveBt,15,0,1,2)

        self.setLayout(layout)

    def save(self):
        self.shdescript = self.shtext.text()
        self.lgdescript = self.lgtext.toPlainText()
        self.validation = True
        self.close()


class insitudisplay(QWidget):
    """Import Widget"""
    closing = pyqtSignal(bool)

    def __init__(self, file, log = None, parent=None):
        super(insitudisplay, self).__init__(parent)

        self.resize(750, 500)
        self.success = False
        self.false = False
        self.parent = parent
        self.log = log
        self.file = file
        self.insitudata = ezinsardata.loadEZdata(self.file,mode='insitu',verbose=False)
        
        self.setStyleSheet(__theme__)

        infogrp = QGroupBox('File information')
        infogrpLayout = QGridLayout()
        NameValueLabel = QLabel('<p><b>Name:</b></p>')
        self.NameValue = QLineEdit()
        self.NameValue.setText(self.insitudata.datainformation['Name'])

        OrigFileValueLabel = QLabel('<p><b>Original file:</b></p>')
        OrigFileValue = QLineEdit()
        OrigFileValue.setText(self.insitudata.datainformation['Original file'])
        OrigFileValue.setReadOnly(True)

        dataUnitValueLabel = QLabel('<p><b>Data Unit:</b></p>')
        self.dataUnitValue = QLineEdit()
        self.dataUnitValue.setText(','.join(self.insitudata.datainformation['Data Unit']))

        infogrpLayout.addWidget(NameValueLabel,0,0,1,1)
        infogrpLayout.addWidget(self.NameValue,0,1,1,1)
        infogrpLayout.addWidget(OrigFileValueLabel,1,0,1,1)
        infogrpLayout.addWidget(OrigFileValue,1,1,1,1)
        infogrpLayout.addWidget(dataUnitValueLabel,2,0,1,1)
        infogrpLayout.addWidget(self.dataUnitValue,2,1,1,1)

        infogrp.setLayout(infogrpLayout)

        toolgrp = QGroupBox('Tools')
        toolgrpLayout = QGridLayout()
        mapBt = QPushButton('Open the map')
        mapBt.clicked.connect(self.openmap)
        descriptionBt = QPushButton('Open the description')
        descriptionBt.clicked.connect(self.openDescriptionWidget)
        toolgrpLayout.addWidget(mapBt,0,0,1,1)
        toolgrpLayout.addWidget(descriptionBt,1,0,1,1)
        toolgrp.setLayout(toolgrpLayout)

        plotgrp = QGroupBox('Plot')
        plotgrpLayout = QGridLayout()

        dataselectedLabel = QLabel('<p><b>Selected Data:</b></p>')
        self.dataselected = QComboBox()
        self.dataselected.addItems(self.insitudata.datainformation['Data Header'][1::])
        self.dataselected.currentIndexChanged.connect(self.updateplot)

        errselectedLabel = QLabel('<p><b>Selected Error:</b></p>')
        self.errselected = QComboBox()
        self.errselected.addItems(['None'])
        self.errselected.addItems(self.insitudata.datainformation['Data Header'][1::])
        self.errselected.currentIndexChanged.connect(self.updateplot)

        self.plotWidget = QWebEngineView() 
        self.updateplot()

        plotgrpLayout.addWidget(dataselectedLabel,0,0,1,1)
        plotgrpLayout.addWidget(self.dataselected,0,1,1,1)
        plotgrpLayout.addWidget(errselectedLabel,0,2,1,1)
        plotgrpLayout.addWidget(self.errselected,0,3,1,1)
        plotgrpLayout.addWidget(self.plotWidget,1,0,4,4)

        plotgrp.setLayout(plotgrpLayout)
    
        layout = QGridLayout()
        layout.addWidget(infogrp, 0, 0, 1, 5)
        layout.addWidget(toolgrp, 0, 5, 1, 5)
        layout.addWidget(plotgrp, 1, 0, 7, 10)


        self.setLayout(layout)

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def messageerror(self,msg):
        reply = QMessageBox.critical(self, "EZ-InSAR Error",
                msg,
                QMessageBox.Ok)
        
    def messagesuccess(self,msg):
        reply = QMessageBox.information(self, "EZ-InSAR Information",
                msg,
                QMessageBox.Ok)
    
    def closemaybe(self):
        """Close"""
        return self.close()
    
    def openmap(self):
        dial = QDialog()
        dial.setWindowTitle("EZ-InSAR - Map" )
        dial.setStyleSheet(__theme__)

        layout = QGridLayout()

        m = folium.Map(
            location=[self.insitudata.lat['value'],self.insitudata.lon['value']], zoom_start=13,
            tiles=None,
            )
        folium.raster_layers.TileLayer(tiles='openstreetmap', name='OpenStreetMap').add_to(m)

        folium.Marker(location=[self.insitudata.lat['value'],self.insitudata.lon['value']],
                        popup=folium.Popup('In-situ Measurement')).add_to(m)
        
        m  = tools.addfoliumTile(m)

        plugins.MousePosition().add_to(m)
        plugins.MeasureControl().add_to(m)
        folium.LayerControl(collapsed=True).add_to(m)
        
        data = io.BytesIO()
        m.save(data, close_file=False)
        mapWidget= QWebEngineView() 
        mapWidget.setHtml(data.getvalue().decode())

        layout.addWidget(mapWidget,0,0)

        dial.setLayout(layout)

        dial.show()
        dial.exec_()

    def openDescriptionWidget(self):
        dial = descripDial(self.insitudata.datainformation['Short Description'],self.insitudata.datainformation['Long Description'])
        dial.exec_()

        if dial.validation: 
            self.insitudata.datainformation['Short Description'] = dial.shdescript
            self.insitudata.datainformation['Long Description'] = dial.lgdescript
            ezinsardata.saveEZdata(self.insitudata,self.file,verbose=False)

    def updateplot(self):

        x = self.insitudata.data['value']['date']
        y = self.insitudata.data['value'][self.dataselected.currentText()]

        fig = go.Figure()

        if self.errselected.currentText() == 'None':
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode='markers',
                marker_color='black'
            ))
        else:
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode='markers',
                marker_color='black',
                error_y=dict(type='data', array=self.insitudata.data['value'][self.errselected.currentText()])
            ))

        fig.update_traces(mode='markers',marker_size=10)
        fig.update_layout(yaxis_zeroline=True)
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(
                title=dict(
                    text="Time"
                )
            ),
            yaxis=dict(
                title=dict(
                    text=self.dataselected.currentText()
                )
            ),
        )

        html = '<html><body>'
        html = html + plotly.offline.plot(fig, output_type='div', include_plotlyjs='cdn')
        html = html + '</body></html>'

        self.plotWidget.setHtml(html)

###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)
    
    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Import file to an EZ-InSAR insitu data',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        widget = insitudisplay(args['--file'])
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()


