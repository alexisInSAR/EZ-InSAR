#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open the export-data tool

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.0.0: Initial version, Jul. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open the export-data tool

usage: 
    ezinsardesktop_exportdata -f <str> [options]

Arguments:
    -f, --file <str>        EZ-InSAR data file

Other-options:
    -h, --help
"""
################################################################################
## Python packages
################################################################################
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QCheckBox, QGridLayout, QLabel, QLineEdit, QMessageBox, QComboBox, QPushButton, QFileDialog, QWidget, QGroupBox, QDialog, QTextEdit, QSpinBox, QListWidget, QAbstractItemView

import os, sys, time
import numpy as np
from docopt import docopt
import pathlib

from ezinsar import constants, usermessage
from ezinsar.tools import ezinsardata
from ezinsardesktopmodule import __file__ as __root_module__
from ezinsardesktopmodule.tools import EPSGcodeDial
from ezinsardesktopmodule.log import logWorker
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__, __docker_running__
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__

################################################################################
## Desktop application
################################################################################
class Worker(QObject):
        """Worker class 

                Build the worker
        """
        textSignal = pyqtSignal(str)
        finished = pyqtSignal()
        intReady = pyqtSignal(int)
        error = pyqtSignal(str)
        success = pyqtSignal(str)

        def __init__(self, input, output, variable, format, epgs, verbose = False, parent=None):
                super(Worker, self).__init__(parent)

                self.TextInfo = ''
                self.running = True
                self.messageerror = ''
                self.messagesuccess = ''
                self.parent = parent 
                self.verbose = verbose   

                self.inputfile = input
                self.outputfile = output
                self.variable = variable
                self.format = format
                self.epgs = int(epgs)

        def run(self):
                try:    
                        tmp = ezinsardata.loadEZdata(self.inputfile,verbose=False)
                        ezinsardata.exportEZdata(tmp,
                                                self.outputfile,
                                                variable = self.variable,
                                                format = self.format,
                                                epgs = self.epgs,
                                                verbose=True)
                        del tmp 

                except Exception as e:
                        time.sleep(1)
                        self.messageerror = '%s' % (e)
                        self.error.emit(self.messageerror)
        
                if self.messageerror == '':
                        self.messagesuccess = 'Export completed in %s.' % (self.outputfile,)
                        self.success.emit(self.messagesuccess)

                self.running=False
                self.finished.emit()

class exportWidget(QWidget):
        """Import Widget"""
        closing = pyqtSignal(bool)

        def __init__(self, file = None, log = None, parent=None):
                super(exportWidget, self).__init__(parent)

                self.resize(1500, 1250)
                self.success = False
                self.false = False
                self.parent = parent
                self.log = log
                self.workerprocess = None
                self.threadprocess = None

                self.setWindowTitle("EZ-InSAR - Export EZ-InSAR file into vector formats")
                self.setStyleSheet(__theme__)

                widgetlogo = tools.create_logo_wigdet(logo=__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop.svg')
                widgettitle = QLabel('<p style="font-size:20px"><b>Export EZ-InSAR file into vector formats</b></p>')
                btclose = QPushButton("Close", self)
                btclose.clicked.connect(self.closemaybe)

                filesgrp = QGroupBox('IO files')
                filesgrpLayout = QGridLayout()

                inputFileValueLabel = QLabel('<p><b>Input file:</b></p>')
                self.inputFileValue = QLineEdit()
                self.inputFileValue.setReadOnly(True)
                self.inputFileValue.setPlaceholderText('Click on the selection button')
                if not file == None: 
                        self.inputFileValue.setText(file)       
                inputFileBtOpen = QPushButton("Select", self)
                inputFileBtOpen.clicked.connect(self.openinputfile)

                outputFileValueLabel = QLabel('<p><b>Ouput file:</b></p>')
                self.outputFileValue = QLineEdit()
                self.outputFileValue.setReadOnly(True)
                self.outputFileValue.setText('')
                outputFileBtOpen = QPushButton("Select", self)
                outputFileBtOpen.clicked.connect(self.openoutputfile)
                
                filesgrpLayout.addWidget(inputFileValueLabel,0,0,1,1)
                filesgrpLayout.addWidget(self.inputFileValue,0,1,1,1)
                filesgrpLayout.addWidget(inputFileBtOpen,0,2,1,1)
                filesgrpLayout.addWidget(outputFileValueLabel,1,0,1,1)
                filesgrpLayout.addWidget(self.outputFileValue,1,1,1,1)
                filesgrpLayout.addWidget(outputFileBtOpen,1,2,1,1)
                filesgrp.setLayout(filesgrpLayout)

                formatgrp = QGroupBox('Format')
                formatgrpLayout = QGridLayout()

                formatValueLabel = QLabel('<p><b>Export format:</b></p>')
                self.formatValue = QComboBox()
                self.formatValue.addItems(constants.__exportformatvector__)
                self.formatValue.setCurrentIndex(constants.__exportformatvector__.index('ESRI Shapefile'))
                self.formatValue.currentTextChanged.connect(self.updateGUI)

                listvarLabel = QLabel('<p><b>Variable:</b></p>')
                self.listvarValue = QListWidget()
                self.listvarValue.addItems(['rateLOS','sigmarateLOS','dispLOS'])
                self.listvarValue.setSelectionMode(QAbstractItemView.ExtendedSelection)
                self.listvarValue.itemSelectionChanged.connect(self.updateGUI)

                formatgrpLayout.addWidget(formatValueLabel,0,0,1,1)
                formatgrpLayout.addWidget(self.formatValue,0,1,1,1)
                formatgrpLayout.addWidget(listvarLabel,1,0,1,1)
                formatgrpLayout.addWidget(self.listvarValue,1,1,1,1)

                formatgrp.setLayout(formatgrpLayout)

                paragrp = QGroupBox('Parameters')
                paragrpLayout = QGridLayout()

                epgsValueLabel = QLabel('<p><b>EPGS code:</b></p>')
                self.epgsValue = QLineEdit()
                self.epgsValue.setReadOnly(True)
                self.epgsValue.setText('4326')
                self.epgsBtOpen = QPushButton("Select a code", self)
                self.epgsBtOpen.clicked.connect(self.openEPSGcodeDiag)

                paragrpLayout.addWidget(epgsValueLabel,0,0,1,1)
                paragrpLayout.addWidget(self.epgsValue,0,1,1,1)
                paragrpLayout.addWidget(self.epgsBtOpen,0,2,1,1)
                paragrp.setLayout(paragrpLayout)

                self.exportBt = QPushButton("Export the dataset", self)
                self.exportBt.setEnabled(False)
                self.exportBt.clicked.connect(self.runexport)
        
                layout = QGridLayout()
                layout.addWidget(widgetlogo, 0, 0, 1, 1)
                layout.addWidget(widgettitle, 0, 1, 1, 8, Qt.AlignCenter)
                layout.addWidget(btclose, 0, 9, 1, 1)

                layout.addWidget(filesgrp, 1, 0, 1, 10)
                layout.addWidget(formatgrp, 2, 0, 1, 10)
                layout.addWidget(paragrp, 3, 0, 1, 10)
                layout.addWidget(self.exportBt, 4, 0, 1, 10)

                self.setLayout(layout)

                self.updateGUI()

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
                
        def openinputfile(self): 
                options = QFileDialog.Options()
                fileName, _ = QFileDialog.getOpenFileName(self,
                        "Select an EZ-InSAR data file",'',
                        "*.eidata", options=options)
                if fileName: 
                        self.inputFileValue.setText(fileName)
                        self.updateGUI()

        def openoutputfile(self): 
                options = QFileDialog.Options()
                fileName, _ = QFileDialog.getSaveFileName(self,
                        "Select a name for the output file",'',
                        options=options)
                if fileName: 
                        self.outputFileValue.setText(fileName)
                        self.updateGUI()
                                            
        def updateGUI(self):
                if not self.outputFileValue.text() == '': 
                        idx = constants.__exportformatvector__.index(self.formatValue.currentText())
                        _, fileExtension = os.path.splitext(self.outputFileValue.text())
                        if fileExtension:
                                self.outputFileValue.setText(self.outputFileValue.text().replace(fileExtension,constants.__exportformatvectorext__[idx]))
                        else: 
                                self.outputFileValue.setText(self.outputFileValue.text() + constants.__exportformatvectorext__[idx])

                if not self.inputFileValue == '': 
                       self.epgsBtOpen.setEnabled(True)
                else: 
                       self.epgsBtOpen.setEnabled(False)

                selectedItems = [item.text() for item in self.listvarValue.selectedItems()]  

                if (selectedItems) and (not self.outputFileValue.text() == '') and (not self.inputFileValue == ''): 
                       self.exportBt.setEnabled(True)
                else:
                       self.exportBt.setEnabled(False)

        def openEPSGcodeDiag(self):
                tmp = ezinsardata.loadEZdata(self.inputFileValue.text(),partialreading=['lon','lat','lon_grid','lat_grid'],verbose=False)
                reply = EPSGcodeDial.EPSGcodeDial(roi=tmp.getextent(format='list'))
                reply.exec_()
                if reply.validation == True: 
                        self.epgsValue.setText(str(reply.epsgcode))

        def runexport(self):
                """Run the progressing 
                """
                self.exportBt.setEnabled(False)

                if self.workerprocess == None:
                        self.messagesuccess('Export in progress')

                        self.workerprocess = Worker(self.inputFileValue.text(),
                                        self.outputFileValue.text(),
                                        [item.text() for item in self.listvarValue.selectedItems()], 
                                        self.formatValue.currentText(),
                                        self.epgsValue.text())
                        self.threadprocess = QThread()
                        self.workerprocess.moveToThread(self.threadprocess)
                        self.threadprocess.started.connect(self.workerprocess.run)
                        self.workerprocess.finished.connect(self.threadprocess.quit)
                        self.workerprocess.error.connect(self.messageerror)
                        self.workerprocess.success.connect(self.messagesuccess)
                        self.workerprocess.finished.connect(self.stopcurrentworker)      
                        self.threadprocess.start()
                else:
                        self.messageerror('The worker for DEM import is still running. Please stop it, if required')

        def closemaybe(self):
                """Close"""
                return self.close()
        
        def stopcurrentworker(self):
                """Stop the current worker
                """
                self.workerprocess = None
                self.exportBt.setEnabled(True)
    
###########################################################################################
## DEBUG
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not os.path.isfile(args['--file']):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No file',None))
    
    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the Export-data tool from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        widget = exportWidget(file = os.path.abspath(args['--file']))
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()




