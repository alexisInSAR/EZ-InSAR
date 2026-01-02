#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open the tool for data access to CEDA UK archive

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.0.0: Initial version, Mar. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open the tool for data access to CEDA UK archive

usage: 
    CEDAukWidget.py [options]

Other-options:
    -h, --help
"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit, QMessageBox, QComboBox, QPushButton,  QWidget, QDialog, QGroupBox, QDateTimeEdit, QTextEdit, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView

import os, sys
from docopt import docopt
import datetime
import pandas as pd
import glob
from shapely.wkt import loads
import plotly.graph_objects as go
import plotly

try:
    from ezinsarweathermodule.api import CEDAarchiveapi
except:
    a = 'dummy'

from ezinsar import usermessage, constants
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule.config import settings
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsardesktopmodule.log import logWorker
import time 

###########################################################################################
## Classes
##########################################################################################
class WorkerExtraction(QObject):

    textSignal = pyqtSignal(str)
    finished = pyqtSignal()
    intReady = pyqtSignal(int)
    error = pyqtSignal(str)
    success = pyqtSignal(str)
    progress = pyqtSignal(float)
    data = pyqtSignal(pd.DataFrame)
    
    def __init__(self, result, outputdir, log = None, parent=None):
        super(WorkerExtraction, self).__init__(parent)

        self.TextInfo = ''
        self.running = True
        self.messageerror = ''
        self.messagesuccess = ''
        self.parent = parent    
        self.result = result
        self.outputdir = outputdir
        self.log = log

    def run(self):
        try:
            self.result.extract(self.result.roi,
                        outputdir = self.outputdir,
                        verbose = True,
                        log = self.log)
            self.data.emit(self.result.Data)
            time.sleep(1)

        except:
            time.sleep(1)
            self.messageerror = 'Error during the extraction'
            self.error.emit(self.messageerror)
    
        if self.messageerror == '':
            self.messagesuccess = 'Extraction completed.'
            self.success.emit(self.messagesuccess)
            
        self.running=False
        self.finished.emit()

class WorkerDownloader(QObject):

    textSignal = pyqtSignal(str)
    finished = pyqtSignal()
    intReady = pyqtSignal(int)
    error = pyqtSignal(str)
    success = pyqtSignal(str)
    progress = pyqtSignal(float)
    
    def __init__(self, result, idDial, outputdir, log = None, parent=None):
        super(WorkerDownloader, self).__init__(parent)

        self.TextInfo = ''
        self.running = True
        self.messageerror = ''
        self.messagesuccess = ''
        self.parent = parent    
        self.result = result
        self.idDial = idDial
        self.outputdir = outputdir
        self.log = log

    def run(self):
        try:
            CEDAarchiveapi.give_token(self.idDial.token.toPlainText())
            self.result.download(outputdir = self.outputdir,
                            modeforce = False,
                            verbose = False,
                            log = self.log)
            time.sleep(1)

        except:
            time.sleep(1)
            self.messageerror = 'Error during the downloading'
            self.error.emit(self.messageerror)
    
        if self.messageerror == '':
            self.messagesuccess = 'Downloading completed.'
            self.success.emit(self.messagesuccess)

        self.running=False
        self.finished.emit()

class IDquery(QDialog):
    """ID Dialog"""
    def __init__(self, parent=None):
        super(IDquery, self).__init__(parent)

        self.username = ''
        self.password = ''
        self.tokeen = ''
        self.success = False

        self.setStyleSheet(__theme__)

        self.title = QLabel("<p><b>CEDA-UK Id</b></p>")

        self.btOkay = QPushButton("Start")
        self.btOkay.clicked.connect(self.valid)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.title, 0, 0, 1, 5)
        mainLayout.addWidget(self.btOkay, 6, 0, 1, 5)

        tokenlabel = QLabel("<p>Token:</p>")
        self.token = QTextEdit()
        self.token.setPlaceholderText('Please find your token. See https://services-beta.ceda.ac.uk/api/token/create/')
        mainLayout.addWidget(tokenlabel, 1, 0, 1, 5)
        mainLayout.addWidget(self.token, 2, 0, 4, 5)

        self.setLayout(mainLayout)
        self.setWindowTitle("ID")

    def valid(self):
        self.success = True
        self.accept()

class CEDAdata(QWidget):
    """Downloader Widget"""
    closing = pyqtSignal(bool)

    def __init__(self, log = None, parent=None):
        super(CEDAdata, self).__init__(parent)

        self.setWindowTitle("EZ-InSAR - CEDA UK Archive Data")
        self.resize(750, 500)
        self.success = False
        self.false = False
        self.parent = parent
        self.log = log

        self.setStyleSheet(__theme__)

        self.result = CEDAarchiveapi.HadUKGrid()

        self.threadlog = None
        self.workerlog = None
        self.threadprocess = None
        self.workerprocess = None
        
        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p style="font-size:20px"><b>Access to CEDA UK Archive Dataset</b></p>')
        btQuit = QPushButton("Close", self)

        inputgrp = QGroupBox('User input')
        inputgrpLayout = QGridLayout()

        roiLabel = QLabel('<b>Region on Interest:</b>')
        roiLabel.setToolTip("""
                            <p>Region of Interest selected.</p>
                            """)
        self.roi = QLineEdit()
        self.roi.setPlaceholderText('POINT (-4 52)')
        self.roi.textChanged.connect(self.updateroi)
        self.roibt = QPushButton('Select')
        inputgrpLayout.addWidget(roiLabel,0,0,1,1)
        inputgrpLayout.addWidget(self.roi,0,1,1,1)
        inputgrpLayout.addWidget(self.roibt,0,2,1,1)

        outputdirLabel = QLabel('<b>Ouput Directory:</b>')
        self.outputdir = QLineEdit()
        self.outputdir.setText(constants.__cachedir__+os.sep+'tmpweather')
        self.outputdirbt = QPushButton('Select')
        self.outputdirbt.clicked.connect(self.changedirectory)
        inputgrpLayout.addWidget(outputdirLabel,1,0,1,1)
        inputgrpLayout.addWidget(self.outputdir,1,1,1,1)
        inputgrpLayout.addWidget(self.outputdirbt,1,2,1,1)

        Date1Label = QLabel("<b>First Date:</b>")
        Date1Label.setToolTip("""
                                    <p>Define the first date for online search.</p>
                                    """)
        self.Date1Value = QDateTimeEdit()
        self.Date1Value.setDisplayFormat("yyyy-MM-dd HH:mm:ss") 
        self.Date1Value.setMinimumDate(datetime.datetime(1900, 1, 1, 0, 0, 0))
        self.Date1Value.setMaximumDate(datetime.datetime(2500, 1, 1, 0, 0, 0))
        self.Date1Value.setDate(self.result.date1)
        self.Date1Value.dateTimeChanged.connect(self.changeDate1)
        inputgrpLayout.addWidget(Date1Label,2,0,1,1)
        inputgrpLayout.addWidget(self.Date1Value,2,1,1,1)

        Date2Label = QLabel("<b>End Date:</b>")
        Date2Label.setToolTip("""
                                    <p>Define the end date for online search.</p>
                                    """)
        self.Date2Value = QDateTimeEdit()
        self.Date2Value.setDisplayFormat("yyyy-MM-dd HH:mm:ss") 
        self.Date2Value.setMinimumDate(datetime.datetime(1900, 1, 1, 0, 0, 0))
        self.Date2Value.setMaximumDate(datetime.datetime(2500, 1, 1, 0, 0, 0))
        self.Date2Value.setDate(self.result.date2)
        self.Date2Value.dateTimeChanged.connect(self.changeDate2)
        inputgrpLayout.addWidget(Date2Label,3,0,1,1)
        inputgrpLayout.addWidget(self.Date2Value,3,1,1,1)

        inputgrp.setLayout(inputgrpLayout)

        datagrp = QGroupBox('CEDA Dataset')
        datagrpLayout = QGridLayout()
        
        datasetLabel = QLabel('<b>Dataset:</b>')
        datasetLabel.setToolTip("""
                                <p>Dataset selected.</p>
                                """)
        self.dataset = QComboBox()
        self.dataset.addItems(['HadUK-Grid'])
        self.dataset.setCurrentIndex(0)
        datagrpLayout.addWidget(datasetLabel,0,0,1,1)
        datagrpLayout.addWidget(self.dataset,0,1,1,1)

        versionLabel = QLabel('<b>Version:</b>')
        versionLabel.setToolTip("""
                                <p>Version selected.</p>
                                """)
        self.version = QComboBox()
        self.version.addItems(['None'])
        self.version.setCurrentIndex(0)
        self.versionbt = QPushButton('Retrieve')
        datagrpLayout.addWidget(versionLabel,1,0,1,1)
        datagrpLayout.addWidget(self.version,1,1,1,1)
        datagrpLayout.addWidget(self.versionbt,1,2,1,1)
        self.versionbt.clicked.connect(self.retrieveversion)
        self.version.currentTextChanged.connect(self.saveversion)

        sparesLabel = QLabel('<b>Spatial resolution:</b>')
        sparesLabel.setToolTip("""
                                <p>Spatial resolution selected.</p>
                                """)
        self.spatialres = QComboBox()
        self.spatialres.addItems(['None'])
        self.spatialres.setCurrentIndex(0)
        self.spatialres.setEnabled(False)
        self.spatialresbt = QPushButton('Retrieve')
        self.spatialresbt.setEnabled(False)
        datagrpLayout.addWidget(sparesLabel,2,0,1,1)
        datagrpLayout.addWidget(self.spatialres,2,1,1,1)
        datagrpLayout.addWidget(self.spatialresbt,2,2,1,1)
        self.spatialresbt.clicked.connect(self.retrievespatialres)
        self.spatialres.currentTextChanged.connect(self.savespatialres)

        variableLabel = QLabel('<b>Variable:</b>')
        variableLabel.setToolTip("""
                                <p>Variable selected.</p>
                                """)
        self.variable = QComboBox()
        self.variable.addItems(['None'])
        self.variable.setCurrentIndex(0)
        self.variable.setEnabled(False)
        self.variablebt = QPushButton('Retrieve')
        self.variablebt.setEnabled(False)
        datagrpLayout.addWidget(variableLabel,3,0,1,1)
        datagrpLayout.addWidget(self.variable,3,1,1,1)
        datagrpLayout.addWidget(self.variablebt,3,2,1,1)
        self.variablebt.clicked.connect(self.retrievevariable)
        self.variable.currentTextChanged.connect(self.savevariable)

        tempresLabel = QLabel('<b>Temporal resolution:</b>')
        tempresLabel.setToolTip("""
                                <p>Temporal resolution.</p>
                                """)
        self.tempres = QComboBox()
        self.tempres.addItems(['None'])
        self.tempres.setCurrentIndex(0)
        self.tempres.setEnabled(False)
        self.tempresbt = QPushButton('Retrieve')
        self.tempresbt.setEnabled(False)
        datagrpLayout.addWidget(tempresLabel,4,0,1,1)
        datagrpLayout.addWidget(self.tempres,4,1,1,1)
        datagrpLayout.addWidget(self.tempresbt,4,2,1,1)
        self.tempresbt.clicked.connect(self.retrievetempres)
        self.tempres.currentTextChanged.connect(self.savetempres)

        updateLabel = QLabel('<b>Update:</b>')
        updateLabel.setToolTip("""
                                <p>Update selected.</p>
                                """)
        self.update = QComboBox()
        self.update.addItems(['None'])
        self.update.setCurrentIndex(0)
        self.update.setEnabled(False)
        self.updatebt = QPushButton('Retrieve')
        self.updatebt.setEnabled(False)
        datagrpLayout.addWidget(updateLabel,5,0,1,1)
        datagrpLayout.addWidget(self.update,5,1,1,1)
        datagrpLayout.addWidget(self.updatebt,5,2,1,1)
        self.updatebt.clicked.connect(self.retrieveupdate)
        self.update.currentTextChanged.connect(self.saveupdate)
        
        datagrp.setLayout(datagrpLayout)

        resultgrp = QGroupBox('Results')
        resultgrpLayout = QGridLayout()

        self.importbt = QPushButton('Import .csv')
        self.importbt.clicked.connect(self.importcsv)
        self.retrievelinkbt = QPushButton('Retrieve links')
        self.retrievelinkbt.setEnabled(False)
        self.retrievelinkbt.clicked.connect(self.checklink)
        self.displaylinkbt = QPushButton('Display links')
        self.displaylinkbt.clicked.connect(self.displaylinkDial)
        self.downloadbt = QPushButton('Download files')
        self.downloadbt.clicked.connect(self.rundownload)
        self.extractbt = QPushButton('Extract data')
        self.extractbt.clicked.connect(self.runextract)
        self.displaytable = QPushButton('Display results')
        self.displaytable.clicked.connect(self.displayDataFrame)
        self.plotbt = QPushButton('Plot results')
        self.plotbt.clicked.connect(self.plotDataFrame)
        self.exportbt = QPushButton('Export .csv')
        self.exportbt.clicked.connect(self.exportcsv)

        resultgrpLayout.addWidget(self.importbt,0,0,1,1)
        resultgrpLayout.addWidget(self.retrievelinkbt,1,0,1,1)
        resultgrpLayout.addWidget(self.displaylinkbt,2,0,1,1)
        resultgrpLayout.addWidget(self.downloadbt,3,0,1,1)
        resultgrpLayout.addWidget(self.extractbt,0,1,1,1)
        resultgrpLayout.addWidget(self.displaytable,1,1,1,1)
        resultgrpLayout.addWidget(self.plotbt,2,1,1,1)
        resultgrpLayout.addWidget(self.exportbt,3,1,1,1)

        resultgrp.setLayout(resultgrpLayout)

        layout = QGridLayout()
        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 8, Qt.AlignCenter)
        layout.addWidget(inputgrp, 1, 0, 1, 10)
        layout.addWidget(datagrp, 2, 0, 1, 10)
        layout.addWidget(resultgrp, 3, 0, 1, 10)
        layout.addWidget(btQuit, 0, 9, 1, 1)
        self.setLayout(layout)

        btQuit.clicked.connect(self.closemaybe)

        self.checkgui()

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def saveCLASS(self):
        try: 
            self.result.Data = self.workerprocess.result.Data
        except:
            self.result.Data = self.parent.workerprocess.result.Data

    def updateroi(self):
        try: 
            self.result.roi = loads(self.roi.text())
        except:
            a = 'dummy'

        self.checkgui()

    def checkgui(self): 
        if self.result.links:
            self.displaylinkbt.setEnabled(True)
            self.downloadbt.setEnabled(True)
            self.extractbt.setEnabled(True)
        else:
            self.displaylinkbt.setEnabled(False)
            self.downloadbt.setEnabled(False)
            self.extractbt.setEnabled(False)
        
        if self.result.Data.empty:
            self.displaytable.setEnabled(False)
            self.plotbt.setEnabled(False)
            self.exportbt.setEnabled(False)
        else:
            self.displaytable.setEnabled(True)
            self.plotbt.setEnabled(True)
            self.exportbt.setEnabled(True)

        if glob.glob(self.outputdir.text()+os.sep+'*.nc'):
            if not self.result.roi == None:
                self.extractbt.setEnabled(True)
            else:
                self.extractbt.setEnabled(False)
        else:
            self.extractbt.setEnabled(False)

    def changeDate2(self):
        self.result.date2 = self.Date2Value.dateTime().toPyDateTime()
        self.result.links = []
        self.checkgui()

    def changeDate1(self):
        self.result.date1 = self.Date1Value.dateTime().toPyDateTime()
        self.result.links = []
        self.checkgui()

    def retrieveversion(self):
        self.result.checkversion(log = self.log,verbose=False)
        tmp = self.result.version
        self.version.clear()
        self.version.addItems(self.result.listversion)
        self.version.setCurrentIndex(self.result.listversion.index(tmp))
        self.spatialresbt.setEnabled(True)
        self.spatialres.setEnabled(True)
    def saveversion(self):
        self.result.version = self.version.currentText()
        self.result.links = []
        self.checkgui()

    def retrievespatialres(self):
        self.result.checkspatialres(log = self.log,verbose=False)
        tmp = self.result.spatialres
        self.spatialres.clear()
        self.spatialres.addItems(self.result.listspatialres)
        self.spatialres.setCurrentIndex(self.result.listspatialres.index(tmp))
        self.variablebt.setEnabled(True)
        self.variable.setEnabled(True)
    def savespatialres(self):
        self.result.spatialres = self.spatialres.currentText()
        self.result.links = []
        self.checkgui()

    def retrievevariable(self):
        self.result.checkvariable(log = self.log,verbose=False)
        tmp = self.result.variable
        self.variable.clear()
        self.variable.addItems(self.result.listvariable)
        self.variable.setCurrentIndex(self.result.listvariable.index(tmp))
        self.tempresbt.setEnabled(True)
        self.tempres.setEnabled(True)
    def savevariable(self):
        self.result.variable = self.variable.currentText()
        self.result.links = []
        self.checkgui()

    def retrievetempres(self):
        self.result.checktempres(log = self.log,verbose=False)
        tmp = self.result.tempres
        self.tempres.clear()
        self.tempres.addItems(self.result.listtempres)
        self.tempres.setCurrentIndex(self.result.listtempres.index(tmp))
        self.updatebt.setEnabled(True)
        self.update.setEnabled(True)
    def savetempres(self):
        self.result.tempres = self.tempres.currentText()
        self.result.links = []
        self.checkgui()

    def retrieveupdate(self):
        self.result.checkupdate(log = self.log,verbose=False)
        tmp = self.result.update
        self.update.clear()
        self.update.addItems(self.result.listupdate)
        self.update.setCurrentIndex(self.result.listupdate.index(tmp))
        self.retrievelinkbt.setEnabled(True)
    def saveupdate(self):
        self.result.update = self.update.currentText()
        self.result.links = []
        self.checkgui()

    def checklink(self): 
        self.result.listNCfile(verbose = False, log = self.log)
        if self.result.links:
            self.messagesuccess('Links saved')
        else:
            self.messageerror('No links')
        self.checkgui()

    def displaylinkDial(self): 
        dial = QDialog()
        dial.setWindowTitle('Link results')
        dial.setStyleSheet(__theme__)
        dial.resize(500,500)
        text = QTextEdit()
        text.setText('\n'.join(self.result.links))
        text.setReadOnly(True)
        dialLayout = QGridLayout()
        dialLayout.addWidget(text,0,0,1,1)
        dial.setLayout(dialLayout)
        dial.show()
        dial.exec_()

    def changedirectory(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        title = 'Please select the output directory'
        directory = QFileDialog.getExistingDirectory(self,
            title, options=options)
        if directory:
            self.outputdir.setText(directory)

    def closemaybe(self):
        """Close"""
        self.closing.emit(True)
        return self.close()

    def messageerror(self,msg):
        reply = QMessageBox.critical(self, "EZ-InSAR Error",
                msg,
                QMessageBox.Ok)
        
    def messagesuccess(self,msg):
        reply = QMessageBox.information(self, "EZ-InSAR Information",
                msg,
                QMessageBox.Ok)
        
    def importcsv(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,
                    "Select a .csv file",'',
                    "*.csv", options=options)
        # fileName = '/home/alexis/Applications_InSAR/EZ-InSAR/EZ-InSAR-3-Module-Weather/test/test.csv'
        if fileName: 
            try: 
                self.result.csv_to_data(fileName,
                                        verbose = False,
                                        log = self.log)
                self.Date1Value.setDateTime(self.result.Data['Date'].to_list()[0])
                self.Date2Value.setDateTime(self.result.Data['Date'].to_list()[-1])

                self.roi.setText(str(self.result.roi))

                self.retrieveversion()
                self.retrievespatialres()
                self.retrievevariable()
                self.retrievetempres()
                self.retrieveupdate()
                self.messagesuccess('File imported.')
            except:
                self.messagesuccess('Error during the import.')

    def displayDataFrame(self):
        dial = QDialog()
        dial.setWindowTitle('Data')
        dial.setStyleSheet(__theme__)
        dial.resize(500,500)
        text = QTextEdit()
        text.setText(self.result.Data.to_string())
        text.setReadOnly(True)
        dialLayout = QGridLayout()
        dialLayout.addWidget(text,0,0,1,1)
        dial.setLayout(dialLayout)
        dial.show()
        dial.exec_()

    def plotDataFrame(self):
        dial = QDialog()
        dial.setWindowTitle('Plot')
        dial.setStyleSheet(__theme__)
        dial.resize(1000,750)

        fig = go.Figure()

        if self.result.variable == 'rainfall':
            if 'POINT' in str(self.result.roi): 
                
                fig.add_trace(go.Bar(
                    x=self.result.Data['Date'], y=self.result.Data['Value'],
                    name=self.result.variable,
                    marker_color='black'
                ))     
        else:
            fig.add_trace(go.Scatter(
                x=self.result.Data['Date'], y=self.result.Data['Value'],
                name=self.result.variable,
                marker_color='black'
            ))
            fig.update_traces(mode='markers',marker_size=10)
        
        fig.update_layout(yaxis_zeroline=True)
        fig.update_layout(
            title="HadUK-Grid %s / %s / %s\n%s" %(self.result.variable,self.result.spatialres,self.result.tempres,self.result.roi),
            xaxis=dict(
                title=dict(
                    text="Time"
                )
            ),
            yaxis=dict(
                title=dict(
                    text= self.result.variable
                )
            ),
        )
        
        FigureWidget= QWebEngineView() 

        if not settings.__plotlyCached__:
            html = '<html><body>'
            html = html + plotly.offline.plot(fig, output_type='div', include_plotlyjs='cdn')
            html = html + '</body></html>'
            FigureWidget.setHtml(html)
        else: 
            fig.write_html(constants.__cachedir__+os.sep+'figuretmp.html')
            FigureWidget.load(QUrl.fromLocalFile(constants.__cachedir__+os.sep+'figuretmp.html'))

        dialLayout = QGridLayout()
        dialLayout.addWidget(FigureWidget,0,0,1,1)
        dial.setLayout(dialLayout)
        dial.show()
        dial.exec_()

    def exportcsv(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,
                "Select a .csv file",'',
                "*.csv", options=options)
        if fileName: 
            self.result.data_to_csv(file=fileName,verbose=False,log=self.log)
        
    def stopcurrentworker(self):
        """Stop the current worker"""
        self.workerprocess = None
        self.setEnabled(True)

    def rundownload(self):
        
        reply = IDquery()
        reply.exec_()

        if reply.success:
            if self.parent == None:
                if self.workerprocess == None:
                    self.workerprocess = WorkerDownloader(self.result, reply, self.outputdir.text(), log = self.log)
                    self.threadprocess = QThread()
                    self.workerprocess.moveToThread(self.threadprocess)
                    self.threadprocess.started.connect(self.workerprocess.run)
                    self.workerprocess.finished.connect(self.threadprocess.quit)
                    self.workerprocess.error.connect(self.messageerror)
                    self.workerprocess.success.connect(self.messagesuccess)
                    self.workerprocess.finished.connect(self.stopcurrentworker)      
                    self.threadprocess.start()
                else:
                    self.messageerror('There already is a current processing. Please stop it before running another one.')

            else:
                if self.parent.workerprocess == None:
                    self.parent.dockprogressbar.show()

                    self.parent.workerprocess = WorkerDownloader(self.result, reply, self.outputdir.text(), log = self.log)
                    self.parent.threadprocess = QThread()
                    self.parent.workerprocess.moveToThread(self.parent.threadprocess)
                    self.parent.threadprocess.started.connect(self.parent.workerprocess.run)
                    self.parent.workerprocess.finished.connect(self.parent.threadprocess.quit)
                    self.parent.workerprocess.textSignal.connect(self.parent.updateTextEditverbose)
                    self.parent.workerprocess.progress.connect(self.parent.updateprogressbar)
                    self.parent.workerprocess.error.connect(self.parent.messageerror)
                    self.parent.workerprocess.success.connect(self.parent.messagesuccess)
                    self.parent.workerprocess.finished.connect(self.parent.stopcurrentworker)   
                    self.parent.workerprocess.success.connect(self.parent.stopcurrentworker)

                    # Initiate the loggin worker/thread
                    self.parent.workerlog = logWorker.Worker(self.log,self.parent.workerprocess)
                    self.parent.threadlog = QThread()
                    self.parent.workerlog.moveToThread(self.parent.threadlog)
                    self.parent.workerlog.textSignal.connect(self.parent.updateTextEditverbose)
                    self.parent.threadlog.started.connect(self.parent.workerlog.run)
                    self.parent.workerlog.finished.connect(self.parent.threadlog.quit)

                    # Start both workers
                    self.parent.threadprocess.start()
                    self.parent.threadlog.start()
                    self.parent.qtCancel.setEnabled(True)

                else:
                    self.messageerror('There already is a current processing. Please stop it before running another one.')

    def runextract(self):
        
        if self.parent == None:
            if self.workerprocess == None:
                self.workerprocess = WorkerExtraction(self.result, self.outputdir.text(), log = self.log)
                self.threadprocess = QThread()
                self.workerprocess.moveToThread(self.threadprocess)
                self.threadprocess.started.connect(self.workerprocess.run)
                self.workerprocess.finished.connect(self.threadprocess.quit)
                self.workerprocess.error.connect(self.messageerror)
                self.workerprocess.success.connect(self.messagesuccess)
                self.workerprocess.finished.connect(self.stopcurrentworker)      
                self.workerprocess.data.connect(self.saveCLASS)
                self.threadprocess.start()
            else:
                self.messageerror('There already is a current processing. Please stop it before running another one.')

        else:
            if self.parent.workerprocess == None:
                self.parent.dockprogressbar.show()

                self.parent.workerprocess = WorkerExtraction(self.result, self.outputdir.text(), log = self.log)
                self.parent.threadprocess = QThread()
                self.parent.workerprocess.moveToThread(self.parent.threadprocess)
                self.parent.threadprocess.started.connect(self.parent.workerprocess.run)
                self.parent.workerprocess.finished.connect(self.parent.threadprocess.quit)
                self.parent.workerprocess.textSignal.connect(self.parent.updateTextEditverbose)
                self.parent.workerprocess.progress.connect(self.parent.updateprogressbar)
                self.parent.workerprocess.error.connect(self.parent.messageerror)
                self.parent.workerprocess.success.connect(self.parent.messagesuccess)
                self.parent.workerprocess.finished.connect(self.parent.stopcurrentworker)   
                self.parent.workerprocess.success.connect(self.parent.stopcurrentworker)
                self.parent.workerprocess.data.connect(self.saveCLASS) 

                # Initiate the loggin worker/thread
                self.parent.workerlog = logWorker.Worker(self.log,self.parent.workerprocess)
                self.parent.threadlog = QThread()
                self.parent.workerlog.moveToThread(self.parent.threadlog)
                self.parent.workerlog.textSignal.connect(self.parent.updateTextEditverbose)
                self.parent.threadlog.started.connect(self.parent.workerlog.run)
                self.parent.workerlog.finished.connect(self.parent.threadlog.quit)

                # Start both workers
                self.parent.threadprocess.start()
                self.parent.threadlog.start()
                self.parent.qtCancel.setEnabled(True)

            else:
                self.messageerror('There already is a current processing. Please stop it before running another one.')

###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)
    
    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Data access to CEDA Archives',None,True,lockfree=True)

    try:
        import ezinsarweathermodule 
    except:
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'The EZ-InSAR Weather Module is not available',None))

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        widget = CEDAdata()
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()


