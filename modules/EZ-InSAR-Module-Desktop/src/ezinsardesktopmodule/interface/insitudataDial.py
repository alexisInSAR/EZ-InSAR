#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open the dialog to import an EZ-InSAR insitu data 

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.0.0: Initial version, Mar. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open the dialog to import an EZ-InSAR insitu data 

usage: 
    insitudataDial.py -f <str> [options]

Argmuents: 
    -f, --file <str>    File

Other-options:
    -h, --help
"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit, QMessageBox, QPushButton,  QWidget, QGroupBox, QTextEdit, QFileDialog, QSpinBox, QDoubleSpinBox, QToolBox

import os, sys
from docopt import docopt

from ezinsar import usermessage
from ezinsar.tools import ezinsardata

from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsardesktopmodule.tools import EPSGcodeDial

###########################################################################################
## Classes
##########################################################################################
class insitudial(QWidget):
    """Import Widget"""
    closing = pyqtSignal(bool)

    def __init__(self, file, log = None, parent=None):
        super(insitudial, self).__init__(parent)

        self.resize(750, 500)
        self.success = False
        self.false = False
        self.parent = parent
        self.log = log
        self.file = file
        self.insitudata = ezinsardata.insitu()
        
        self.setWindowTitle("EZ-InSAR - Import file to EZ-InSAR insitu data" )
        self.setStyleSheet(__theme__)

        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p style="font-size:20px"><b>Import file to EZ-InSAR insitu data</b></p>')
        quitBt = QPushButton('Quit')
        importBt = QPushButton('Import')

        mainWidget = QToolBox()

        filegrp = QGroupBox('File information')
        filegrpLayout = QGridLayout()
        fileNameLabel = QLabel('<p><b>File:</b></p>')
        fileName = QLineEdit()
        fileName.setText(self.file)
        fileName.setReadOnly(True)
        filegrpLayout.addWidget(fileNameLabel,0,0,1,1)
        filegrpLayout.addWidget(fileName,0,1,1,1)
        filegrp.setLayout(filegrpLayout)

        formatgrp = QGroupBox('Format')
        formatgrpLayout = QGridLayout()
        delimiterLabel = QLabel('<p><b>Delimiter:</b></p>')
        self.delimiter = QLineEdit()
        self.delimiter.setText(';')
        self.delimiter.setPlaceholderText('Delimiter symbol')

        headerlineLabel = QLabel('<p><b>Header line(s):</b></p>')
        self.headerline = QSpinBox()
        self.headerline.setValue(0)
        self.headerline.setMinimum(0)
        self.headerline.setMaximum(1000)

        dateFormatLabel = QLabel('<p><b>Date Format:</b></p>')
        self.dateFormat = QLineEdit()
        self.dateFormat.setText('%Y-%m-%dT%H:%M:%S.%fZ')
        self.dateFormat.setPlaceholderText('Date Format')

        formatgrpLayout.addWidget(delimiterLabel,0,0,1,1)
        formatgrpLayout.addWidget(self.delimiter,0,1,1,1)
        formatgrpLayout.addWidget(headerlineLabel,1,0,1,1)
        formatgrpLayout.addWidget(self.headerline,1,1,1,1)
        formatgrpLayout.addWidget(dateFormatLabel,2,0,1,1)
        formatgrpLayout.addWidget(self.dateFormat,2,1,1,1)

        formatgrp.setLayout(formatgrpLayout)

        datagrp = QGroupBox('Data')
        datagrpLayout = QGridLayout()
        colnamesLabel = QLabel('<p><b>Column Names:</b></p>')
        self.colnames = QLineEdit()
        self.colnames.setText("date,displacement")

        dataunitsLabel = QLabel('<p><b>Data Units:</b></p>')
        self.dataunits = QLineEdit()
        self.dataunits.setText("time,mm")

        datagrpLayout.addWidget(colnamesLabel,0,0,1,1)
        datagrpLayout.addWidget(self.colnames,0,1,1,1)
        datagrpLayout.addWidget(dataunitsLabel,1,0,1,1)
        datagrpLayout.addWidget(self.dataunits,1,1,1,1)

        datagrp.setLayout(datagrpLayout)

        locgrp = QGroupBox('Location')
        locgrpLayout = QGridLayout()

        xLabel = QLabel('<p><b>X/Longitude Coordinate:</b></p>')
        self.xValue = QDoubleSpinBox()
        self.xValue.setDecimals(9)
        self.xValue.setValue(0)
        self.xValue.setMinimum(-1e9)
        self.xValue.setMaximum(1e9)

        yLabel = QLabel('<p><b>Y/Latitude Coordinate:</b></p>')
        self.yValue = QDoubleSpinBox()
        self.yValue.setDecimals(9)
        self.yValue.setValue(0)
        self.yValue.setMinimum(-1e9)
        self.yValue.setMaximum(1e9)

        zLabel = QLabel('<p><b>Z/Elevation Coordinate:</b></p>')
        self.zValue = QDoubleSpinBox()
        self.zValue.setDecimals(3)
        self.zValue.setValue(0)
        self.zValue.setMinimum(-1e9)
        self.zValue.setMaximum(1e9)

        egspLabel = QLabel('<p><b>EPSG Code:</b></p>')
        self.egspValue = QLineEdit()
        self.egspValue.setText('4326')

        egspLabelBt = QPushButton('EGSP Tool')
        egspLabelBt.clicked.connect(self.openEPSGcodeDiag)

        locgrpLayout.addWidget(xLabel,0,0,1,1)
        locgrpLayout.addWidget(self.xValue,0,1,1,1)
        locgrpLayout.addWidget(yLabel,1,0,1,1)
        locgrpLayout.addWidget(self.yValue,1,1,1,1)
        locgrpLayout.addWidget(zLabel,2,0,1,1)
        locgrpLayout.addWidget(self.zValue,2,1,1,1)
        locgrpLayout.addWidget(egspLabel,3,0,1,1)
        locgrpLayout.addWidget(self.egspValue,3,1,1,1)
        locgrpLayout.addWidget(egspLabelBt,3,2,1,1)

        locgrp.setLayout(locgrpLayout)

        descriptiongrp = QGroupBox('Description')
        descriptiongrpLayout = QGridLayout()
        shDescriptionLabel = QLabel('<p><b>Short Description:</b></p>')
        self.shDescriptionText = QLineEdit()
        self.shDescriptionText.setText("")

        lgDescriptionLabel = QLabel('<p><b>Long Description:</b></p>')
        self.lgDescriptionText = QTextEdit()
        self.lgDescriptionText.setText("")

        descriptiongrpLayout.addWidget(shDescriptionLabel,0,0,1,1)
        descriptiongrpLayout.addWidget(self.shDescriptionText,0,1,1,1)
        descriptiongrpLayout.addWidget(lgDescriptionLabel,1,0,1,1)
        descriptiongrpLayout.addWidget(self.lgDescriptionText,1,1,1,1)

        descriptiongrp.setLayout(descriptiongrpLayout)

        mainWidget.addItem(formatgrp,'Format')
        mainWidget.addItem(datagrp,'Data')
        mainWidget.addItem(locgrp,'Location')
        mainWidget.addItem(descriptiongrp,'Description')

        layout = QGridLayout()
        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 8, Qt.AlignCenter)
        layout.addWidget(filegrp, 1, 0, 1, 10)
        layout.addWidget(mainWidget, 2, 0, 1, 10)
        layout.addWidget(quitBt, 0, 9, 1, 1)
        layout.addWidget(importBt, 3, 9, 1, 1)

        quitBt.clicked.connect(self.closemaybe)
        importBt.clicked.connect(self.importdata)

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
    
    def openEPSGcodeDiag(self):
        """Selection of a EPSG code
        """
        reply = EPSGcodeDial.EPSGcodeDial()
        reply.exec_()
        if reply.validation == True: 
            self.egspValue.setText(str(reply.epsgcode))

    def importdata(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,
                "Select a .txt file",'',
                "*.eidata", options=options)
        
        if fileName:
            try:
                self.insitudata.readfromtxt(self.file,
                    delimiter=self.delimiter.text(),
                    header=self.headerline.value(),
                    dateformat=self.dateFormat.text(),
                    dataunits=self.dataunits.text().split(','),
                    colnames=self.colnames.text().split(','),
                    location=[self.xValue.value(),self.yValue.value(),self.zValue.value()],
                    epsg = int(self.egspValue.text()),
                    log = self.log,
                    verbose=False,
                    )

                self.insitudata.datainformation['Short Description'] = self.shDescriptionText.text()
                self.insitudata.datainformation['Long Description'] = self.lgDescriptionText.toPlainText()
                ezinsardata.saveEZdata(self.insitudata,fileName,verbose=False,log=self.log)

                self.messagesuccess('File saved: %s' % (fileName))

                if not self.parent == None:
                    print('Replace the widget')

            except:
                self.messageerror('Error during the import. Please see the log')

            if (not self.log == None) and (not self.parent==None):
                self.parent.updatelog()

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
        widget = insitudial(args['--file'])
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()


