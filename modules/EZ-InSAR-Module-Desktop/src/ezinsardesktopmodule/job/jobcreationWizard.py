#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Create an EZ-InSAR job

The module allows to create the main window of EZ-InSAR Desktop 
    
    (Supplementary module for EZ-InSAR)

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Feb. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Create an EZ-InSAR job

usage: 
    ezinsardesktop_create

"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, QFileInfo
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, 
                            QLabel, QLineEdit, QMessageBox, QVBoxLayout, 
                            QWizard, QWizardPage, QComboBox, QSpinBox, 
                            QDateTimeEdit, QPushButton, QFileDialog)
from PyQt5.QtWebEngineWidgets import QWebEngineView

import os, io, importlib, sys
import numpy as np
import datetime 
import folium
from shapely.geometry import Polygon
import fiona
import pyproj
from osgeo import gdal
from docopt import docopt

from ezinsar import constants, usermessage
import ezinsar.job as ez
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule.tools.docsWidget import DocsDialog

###########################################################################################
## Class for the Wizard
###########################################################################################
class createEZInSARjob(QWizard):
    def __init__(self, parent=None):
        super(createEZInSARjob, self).__init__(parent)

        self.pathjobfile = None
        self.addPage(IntroductionPage())
        self.addPage(JobNamePage())
        self.addPage(SatInfoPage())
        self.addPage(PathJobPage())
        self.addPage(RoiInfoPage())
        self.addPage(DEMInfoPage())
        self.setWindowTitle("EZ-InSAR - Job creation tool")
        self.resize(1000, 300)
        self.setStyleSheet(__theme__)

        self.setOption(QWizard.HaveHelpButton, True)
        self.button(QWizard.HelpButton).clicked.connect(self.openhelp)

    def openhelp(self):
        helpdial = DocsDialog('applications%sjob%snewjob.html' % (os.sep,os.sep))
        helpdial.show()
        helpdial.exec()

    def accept(self):
        ## Get attributes
        self.pathjobfile = os.path.abspath(self.page(1).jobPathLineEdit.text())
        nameJob = self.page(1).jobTitleLineEdit.text()
        nameUser = self.page(1).jobUserLineEdit.text()

        satellite = self.page(2).satNameList.currentText()
        modesat = self.page(2).satModeList.currentText()

        pol = []
        if self.page(2).satPol1.isChecked():
            pol.append('VV')
        if self.page(2).satPol2.isChecked():
            pol.append('VH')
        if self.page(2).satPol3.isChecked():
            pol.append('HH')
        if self.page(2).satPol4.isChecked():
            pol.append('HV')

        if satellite == 'S1':
            relorbit = self.page(2).satRelorbitSpin.value()
            satpass = self.page(2).satPassList.currentText().upper()
        else:
            relorbit = None
            satpass = None

        date1 = self.page(2).satDate1Value.dateTime().toPyDateTime()
        date2 = self.page(2).satDate2Value.dateTime().toPyDateTime()

        pathWK = self.page(3).pathWorkLineEdit.text()
        pathSLC = self.page(3).pathSLCLineEdit.text()
        pathOrbit = self.page(3).pathOrbitLineEdit.text()
        pathAux = self.page(3).pathAuxLineEdit.text()
        if pathOrbit == 'None':
            pathOrbit = None
        if pathAux == 'None':
            pathAux = None
        
        bbox = self.page(4).pathROILineEdit.text()

        pathDEM = self.page(5).pathDEMLineEdit.text()
        nameDEM = self.page(5).nameDEMLineEdit.text()
        typeDEM = self.page(5).modeDEMList.currentText()

        # Create the job 
        job = ez.EIjob(verbose=True,
            polarisation=pol,
            satmode=modesat,
            satellite=satellite,
            relorbit=relorbit,
            satpass=satpass,
            log=constants.__cachedir__ + os.sep + self.pathjobfile.split(os.sep)[-1].replace('.ei','_job.log'))
        
        job.nameJob = nameJob
        job.user = nameUser
        job.workdirectory = pathWK
        job.pathSLC = pathSLC
        job.pathorbit = pathOrbit
        job.pathaux = pathAux
        job.pathDEM = pathDEM
        job.nameDEM = nameDEM
        job.typeDEM = typeDEM
        job.date1 = date1
        job.date2 = date2

        if not bbox == 'None':
            if len(bbox.split(',')) == 4:
                bbox = bbox.split(',')
                for idx, bboxi in enumerate(bbox):
                    bbox[idx] = float(bbox[idx])
            job.importroi(input=bbox)

        job.check(verbose=False)

        super(createEZInSARjob, self).accept()

        try:
            ez.save(job,self.pathjobfile,verbose=False)
            reply = QMessageBox.information(self,
                    "EZ-InSAR created",
                    'The EZ-InSAR job %s was successfull created in %s' % (job.nameJob,self.pathjobfile))
        except:
            reply = QMessageBox.critical(self, "Error with the EZ-InSAR job creation.",
                    'Please check the log.',
                    QMessageBox.Ignore)

###########################################################################################
## Introduction page class
###########################################################################################
class IntroductionPage(QWizardPage):
    def __init__(self, parent=None):
        super(IntroductionPage, self).__init__(parent)

        self.setTitle("Welcome to the tool for EZ-InSAR job creation")
        self.setPixmap(QWizard.BackgroundPixmap,
            QPixmap(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop.svg').scaled(256,256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

        label = QLabel("""
                <p>The current tool will help users to create an EZ-InSAR job. Some parameters will be asked but they can be modified after the creation.</p>
                <p>Please follow the different step in order to create the EZ-InSAR job.</p>
                <p><i>Keep default values for undefined. However, such parameters should be changed after the job creation.<\i></p>
                """
            )
        
        label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(label)

        self.setLayout(layout)

###########################################################################################
## JobName page class
###########################################################################################
class JobNamePage(QWizardPage):
    def __init__(self, parent=None):
        super(JobNamePage, self).__init__(parent)

        self.setTitle("Step 1/4 - EZ-InSAR job Name")
        self.setSubTitle("""
                        <b>Specify mandatory information for the EZ-InSAR job<\b>
                        """)
        
        self.setPixmap(QWizard.BackgroundPixmap,
            QPixmap(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop.svg').scaled(256,256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        
        jobTitleLabel = QLabel("EZ-InSAR job title:")
        jobTitleLabel.setToolTip("""
                            <p>The title of the EZ-InSAR will be used in the EZ-InSAR report.</p>
                            <p>It is not mandatory but very useful.</p>     
                            """)
        self.jobTitleLineEdit = QLineEdit()
        self.jobTitleLineEdit.setPlaceholderText('Title of the EZ-InSAR')
        jobTitleLabel.setBuddy(self.jobTitleLineEdit)

        jobUserLabel = QLabel("Producer/User:")
        jobUserLabel.setToolTip("""
                            <p>The producer/user name will be used to track the origin of results: i.e., in the EZ-InSAR report.</p>
                            """)
        self.jobUserLineEdit = QLineEdit()
        self.jobUserLineEdit.setText(os.path.expanduser('~').split(os.sep)[-1])
        jobUserLabel.setBuddy(self.jobUserLineEdit)

        jobPathLabel = QLabel("EZ-InSAR job file:")
        jobPathLabel.setToolTip("""
                            <p>The EZ-InSAR job file will contain ALL the information regarding EZ-InSAR processing.</p>
                            """)
        self.jobPathLineEdit = QLineEdit()
        self.jobPathLineEdit.setPlaceholderText('Path of the EZ-InSAR job file')
        jobPathLabel.setBuddy(self.jobPathLineEdit)
        jobPathBt = QPushButton("Select")
        jobPathBt.setToolTip('Select the EZ-InSAR job file')
        jobPathBt.clicked.connect(self.setSaveFileName)

        self.registerField('jobPath*', self.jobPathLineEdit)

        layout = QGridLayout()
        layout.addWidget(jobTitleLabel, 0, 0)
        layout.addWidget(self.jobTitleLineEdit, 0, 1)
        layout.addWidget(jobUserLabel, 1, 0)
        layout.addWidget(self.jobUserLineEdit, 1, 1)
        layout.addWidget(jobPathLabel, 2, 0)
        layout.addWidget(self.jobPathLineEdit, 2, 1)
        layout.addWidget(jobPathBt, 2, 2)

        # btHelp = QPushButton("Help", self)
        # # btHelp.clicked.connect(self.openhelp)
        # layout.addWidget(btHelp, 5, 0)

        self.setLayout(layout)

    ###########################################################################################
    ## Callbacks
    def setSaveFileName(self):    
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,
                "Save an EZ-InSAR job file",
                self.jobPathLineEdit.text(),
                "*.ei", options=options)
        if fileName:
            if not fileName.endswith('.ei'):
                fileName = fileName + '.ei'
            self.jobPathLineEdit.setText(fileName)

###########################################################################################
## SatInfo page class
###########################################################################################
class SatInfoPage(QWizardPage):
    def __init__(self, parent=None):
        super(SatInfoPage, self).__init__(parent)

        self.setTitle("Step 2/5 - Satellite Information")
        self.setSubTitle("""
                        <p><b>Specify the satellite information<\b></p>
                        <p>Some information will be modifyied by EZ-InSAR according to the files stored on disks.</p>
                        """)
        
        self.setPixmap(QWizard.BackgroundPixmap,
            QPixmap(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop.svg').scaled(256,256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
    
        self.satNameLabel = QLabel("Platform/Sensor:")
        self.satNameLabel.setToolTip("""
                                    <p>Define the name of platform/sensor that acquired imagery. EZ-InSAR detects any optional EZ-InSAR modules (i.e., for NISAR or SAOCOM).</p>
                                    """)
        self.satNameList = QComboBox()
        listsat = np.sort(list(constants.__sensors__.keys())).tolist()
        for satiopt in constants.__EZInSARoptionalmoduleSAT__:
            try:
                importlib.import_module('ezinsar%smodule' % (satiopt)).__versionPackage__,
            except:
                listsat.remove(satiopt.upper())
        self.satNameList.addItems(listsat)
        self.satNameList.setCurrentIndex(listsat.index("S1"))
        self.satNameLabel.setBuddy(self.satNameList)
        self.satNameList.currentTextChanged.connect(self.updatesatInfoPage)

        self.satModeLabel = QLabel("Mode of acquisition:")
        self.satModeLabel.setToolTip("""
                                    <p>Define the used acquisition mode. Please read the EZ-InSAR documentation for more information.</p>
                                    """)
        self.satModeList = QComboBox()
        self.satModeList.addItems(list(constants.__sensors__['S1']))
        self.satModeLabel.setBuddy(self.satModeList)

        self.satPolLabel = QLabel("Polarisation(s):")
        self.satPolLabel.setToolTip("""
                                    <p>Define the desired polarisation(s).</p>
                                    <p>However, be aware that certain processors (e.g., ISCE-2) and time-series-analysis processors are not able to deal with several polarisaton(s). It will be require to repeat the EZ-InSAR job.</p>
                                    """)
        self.satPolGroup = QGridLayout()
        self.satPol1 = QCheckBox("VV")
        self.satPol1.setChecked(True) 
        self.satPol2 = QCheckBox("VH")
        self.satPol2.setChecked(False) 
        self.satPol3 = QCheckBox("HH")
        self.satPol3.setChecked(False) 
        self.satPol4 = QCheckBox("HV")
        self.satPol4.setChecked(False) 
        self.satPol1.clicked.connect(self.updatesatInfoPage)
        self.satPol2.clicked.connect(self.updatesatInfoPage)
        self.satPol3.clicked.connect(self.updatesatInfoPage)
        self.satPol4.clicked.connect(self.updatesatInfoPage)
        self.satPolGroup.addWidget(self.satPol1, 0, 0)
        self.satPolGroup.addWidget(self.satPol2, 0, 1)
        self.satPolGroup.addWidget(self.satPol3, 1, 0)
        self.satPolGroup.addWidget(self.satPol4, 1, 1)
        # self.satPolLabel.setBuddy(self.satPolGroup)

        self.satPassLabel = QLabel("Satellite direction:")
        self.satPassLabel.setToolTip("""
                                    <p>Define the satellite direction (Ascending or Descending).</p>
                                    <p>Only required for online imagery. EZ-InSAR will detect this parameter while image files are stored on disk(s).</p>
                                    """)
        self.satPassList = QComboBox()
        self.satPassList.addItems(['Ascending','Descending'])
        self.satPassLabel.setBuddy(self.satPassList)

        self.satRelorbitLabel = QLabel("Relative orbit:")
        self.satRelorbitLabel.setToolTip("""
                                    <p>Define the relative orbit.</p>
                                    <p>Only required for online imagery. EZ-InSAR will detect this parameter while image files are stored on disk(s).</p>
                                    """)
        self.satRelorbitSpin = QSpinBox()
        self.satRelorbitSpin.setMaximum(100000)
        self.satRelorbitSpin.setMinimum(1)
        self.satRelorbitSpin.setValue(1)
        self.satRelorbitLabel.setBuddy(self.satRelorbitSpin)
 
        self.satDate1Label = QLabel("Start Date:")
        self.satDate1Label.setToolTip("""
                                    <p>Define the start date for online search.</p>
                                    <p>Only required for online imagery. EZ-InSAR will detect this parameter while image files are stored on disk(s).</p>
                                    """)
        self.satDate1Value = QDateTimeEdit()
        self.satDate1Value.setDisplayFormat("yyyy-MM-dd HH:mm:ss") 
        self.satDate1Value.setMinimumDate(datetime.datetime(1900, 1, 1, 0, 0, 0))
        self.satDate1Value.setMaximumDate(datetime.datetime(2500, 1, 1, 0, 0, 0))
        self.satDate1Value.setDate(datetime.datetime(2014, 1, 1, 0, 0, 0))

        self.satDate2Label = QLabel("End Date:")
        self.satDate2Label.setToolTip("""
                                    <p>Define the end date for online search.</p>
                                    <p>Only required for online imagery. EZ-InSAR will detect this parameter while image files are stored on disk(s).</p>
                                    """)
        self.satDate2Value = QDateTimeEdit()
        self.satDate2Value.setDisplayFormat("yyyy-MM-dd HH:mm:ss") 
        self.satDate2Value.setMinimumDate(datetime.datetime(1900, 1, 1, 0, 0, 0))
        self.satDate2Value.setMaximumDate(datetime.datetime(2500, 1, 1, 0, 0, 0))
        self.satDate2Value.setDate(datetime.datetime.now())
        
        layout = QGridLayout()
        layout.addWidget(self.satNameLabel, 0, 0)
        layout.addWidget(self.satNameList, 0, 1)
        layout.addWidget(self.satModeLabel, 1, 0)
        layout.addWidget(self.satModeList, 1, 1)
        layout.addWidget(self.satPolLabel, 2, 0)
        layout.addLayout(self.satPolGroup, 2, 1)
        layout.addWidget(self.satRelorbitLabel, 3, 0)
        layout.addWidget(self.satRelorbitSpin, 3, 1)
        layout.addWidget(self.satPassLabel, 4, 0)
        layout.addWidget(self.satPassList, 4, 1)
        layout.addWidget(self.satDate1Label, 5, 0)
        layout.addWidget(self.satDate1Value, 5, 1)
        layout.addWidget(self.satDate2Label, 6, 0)
        layout.addWidget(self.satDate2Value, 6, 1)

        self.setLayout(layout)

    ###########################################################################################
    ## Callbacks
    def updatesatInfoPage(self):
        if not self.satNameList.currentText() == 'S1':
            self.satRelorbitSpin.setDisabled(True)
            self.satPassList.setDisabled(True)
            self.satPassList.setDisabled(True)
            self.satDate1Value.setDisabled(True)
            self.satDate2Value.setDisabled(True)
        else:
            self.satRelorbitSpin.setDisabled(False)
            self.satDate2Value.setDisabled(False)
            self.satPassList.setDisabled(False)
            self.satPassList.setDisabled(False)
            self.satDate1Value.setDisabled(False)
            self.satDate2Value.setDisabled(False)

        AllItems = [self.satModeList.itemText(i) for i in range(self.satModeList.count())]
        currItem = self.satModeList.currentText()
        listnew = list(constants.__sensors__[self.satNameList.currentText()])
        self.satModeList.clear()
        self.satModeList.addItems(listnew)
        if currItem in listnew:
            self.satModeList.setCurrentIndex(listnew.index(currItem))

        pol = []
        if self.satPol1.isChecked():
            pol.append('VV')
        if self.satPol2.isChecked():
            pol.append('VH')
        if self.satPol3.isChecked():
            pol.append('HH')
        if self.satPol4.isChecked():
            pol.append('HV')
        if len(pol)==0:
            reply = QMessageBox.critical(self, "Error with the polarisation(s)",
                    'At least one polarisation is required.',
                    QMessageBox.Ok)
            if self.sender().text() == 'VV':
                self.satPol1.setChecked(True)
            elif self.sender().text() == 'VH':
                self.satPol2.setChecked(True)
            elif self.sender().text() == 'HH':
                self.satPol3.setChecked(True)
            else:
                self.satPol4.setChecked(True)
            
###########################################################################################
## PathJob page class
###########################################################################################
class PathJobPage(QWizardPage):
    def __init__(self, parent=None):
        super(PathJobPage, self).__init__(parent)

        self.setTitle("Step 3/5 - Directory Paths")        
        self.setSubTitle("""
                        <p><b>Specify the directory paths<\b></p>
                        <p>If None, EZ-InSAR will replace the path(s) by a dummy directory (i.e., .EZInSARcache).</p>
                        """)
        
        self.setPixmap(QWizard.BackgroundPixmap,
            QPixmap(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop.svg').scaled(256,256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        
        pathWorkLabel = QLabel("Path of the work directory:")
        pathWorkLabel.setToolTip("""
                                <p>Define the directory where EZ-InSAR will store ALL working files.</p>
                                """)
        self.pathWorkLineEdit = QLineEdit()
        self.pathWorkLineEdit.setPlaceholderText('Path of the work directory')
        self.pathWorkLineEdit.setReadOnly(True)
        pathWorkBt = QPushButton("Select")
        pathWorkBt.setToolTip('Select the work directory')
        pathWorkBt.clicked.connect(self.setExistingDirectory)
        self.registerField('pathWK*', self.pathWorkLineEdit)

        pathSLCLabel = QLabel("Path of the SLC directory:")
        pathSLCLabel.setToolTip("""
                                <p>Define the SLC-image directory.</p>
                                """)
        self.pathSLCLineEdit = QLineEdit()
        self.pathSLCLineEdit.setPlaceholderText('Path of the SLC directory')
        self.pathSLCLineEdit.setReadOnly(True)
        pathSLCBt = QPushButton("Select")
        pathSLCBt.setToolTip('Select the SLC directory')
        pathSLCBt.clicked.connect(self.setExistingDirectory)
        self.registerField('pathSLC*', self.pathSLCLineEdit)

        pathOrbitLabel = QLabel("Path of the orbit directory:")
        pathOrbitLabel.setToolTip("""
                                <p>Define the orbit-file directory. Only required for Sentinel-1 imagery.</p>
                                """)
        self.pathOrbitLineEdit = QLineEdit()
        self.pathOrbitLineEdit.setPlaceholderText('Path of the orbit directory')
        self.pathOrbitLineEdit.setReadOnly(True)
        self.pathOrbitLineEdit.setText('None')
        pathOrbitBt = QPushButton("Select")
        pathOrbitBt.setToolTip('Select the orbit directory')
        pathOrbitBt.clicked.connect(self.setExistingDirectory)

        pathAuxLabel = QLabel("Path of the aux directory:")
        pathAuxLabel.setToolTip("""
                                <p>Define the aux-file directory. Can be required for Sentinel-1 imagery, however it seems that it is not longer required due to the new version of the IPF processor.<\p
                                """)
        self.pathAuxLineEdit = QLineEdit()
        self.pathAuxLineEdit.setPlaceholderText('Path of the aux directory')
        self.pathAuxLineEdit.setReadOnly(True)
        self.pathAuxLineEdit.setText('None')
        pathAuxBt = QPushButton("Select")
        pathAuxBt.setToolTip('Select the aux directory')
        pathAuxBt.clicked.connect(self.setExistingDirectory)
        
        layout = QGridLayout()
        layout.addWidget(pathWorkLabel, 0, 0)
        layout.addWidget(self.pathWorkLineEdit, 0, 1)
        layout.addWidget(pathWorkBt, 0, 2)
        layout.addWidget(pathSLCLabel, 1, 0)
        layout.addWidget(self.pathSLCLineEdit, 1, 1)
        layout.addWidget(pathSLCBt, 1, 2)
        layout.addWidget(pathOrbitLabel, 2, 0)
        layout.addWidget(self.pathOrbitLineEdit, 2, 1)
        layout.addWidget(pathOrbitBt, 2, 2)
        layout.addWidget(pathAuxLabel, 3, 0)
        layout.addWidget(self.pathAuxLineEdit, 3, 1)
        layout.addWidget(pathAuxBt, 3, 2)

        self.setLayout(layout)

    ###########################################################################################
    ## Callbacks
    def setExistingDirectory(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        if 'work directory' in self.sender().toolTip():
            title = 'Please select the work directory'
        elif 'SLC directory' in self.sender().toolTip():
            title = 'Please select the SLC directory'
        elif 'orbit directory' in self.sender().toolTip():
            title = 'Please select the orbit directory'
        elif 'aux directory' in self.sender().toolTip():
            title = 'Please select the aux directory'

        directory = QFileDialog.getExistingDirectory(self,
            title, options=options)
        if (directory) and ('work directory' in self.sender().toolTip()):
            self.pathWorkLineEdit.setText(directory)
        elif (directory) and ('SLC directory' in self.sender().toolTip()):
            self.pathSLCLineEdit.setText(directory)
        elif (directory) and ('orbit directory' in self.sender().toolTip()):
            self.pathOrbitLineEdit.setText(directory)
        elif (directory) and ('aux directory' in self.sender().toolTip()):
            self.pathAuxLineEdit.setText(directory)

###########################################################################################
## RoiInfo page class
###########################################################################################
class RoiInfoPage(QWizardPage):
    def __init__(self, parent=None):
        super(RoiInfoPage, self).__init__(parent)

        self.setTitle("Step 4/5 - Region of Interest")
        self.setSubTitle("""
                        <p><b>Specify the Region of Interest.<\b></p>
                         <p>It is possible to give a vector file (i.e., ESRI Shape file) or a string of coordinates (W,S,E,N). The coordinates must be in longitude and latitude. <i>The ROI can be modified with advanced tools after creation.<\i></p>
                        """)
        
        self.setPixmap(QWizard.BackgroundPixmap,
            QPixmap(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop.svg').scaled(256,256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
       
        pathROILabel = QLabel("Region of Interest:")
        pathROILabel.setToolTip("""
                                <p>Define the Region of Interest. A vector file can be given or a coordinate string (i.e., <-6.5,53.2,-6,53.5>).<\p
                                """)
        self.pathROILineEdit = QLineEdit()
        self.pathROILineEdit.setPlaceholderText('Give the Region of Interest')
        pathROIBt = QPushButton("Select")
        pathROIBt.setToolTip('Select the Region of Interest file')
        pathROIBt.clicked.connect(self.setOpenFileName)
        self.pathROILineEdit.textChanged.connect(self.updateROIInfoPage)
        self.registerField('pathROI*', self.pathROILineEdit)
        
        layout = QGridLayout()
        layout.addWidget(pathROILabel, 0, 0)
        layout.addWidget(self.pathROILineEdit, 0, 1)
        layout.addWidget(pathROIBt, 0, 2)

        # Initialisation of the map
        m = folium.Map(
            location=[0,0], zoom_start=1
            )
        data = io.BytesIO()
        m.save(data, close_file=False)
        
        self.mapWidget = QWebEngineView()
        self.mapWidget.setHtml(data.getvalue().decode())
        self.mapWidget.resize(640, 640)

        layout.addWidget(self.mapWidget, 1,1)

        self.setLayout(layout)

    ###########################################################################################
    ## Callbacks
    def setOpenFileName(self):    
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,
                "Select a vector file", self.pathROILineEdit.text(),
                "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            self.pathROILineEdit.setText(fileName)

    def updateROIInfoPage(self):
        bbox = self.pathROILineEdit.text()
        checkROI = False
        if os.path.isfile(bbox):
            try:
                with fiona.open(bbox) as roifile:
                    for feature in roifile:
                        a = len(feature['geometry']["coordinates"][0])
                checkROI = True
            except:
                checkROI = False
                reply = QMessageBox.critical(self, "Error with the ROI file",
                    'The ROI file is not compatible with EZ-InSAR',
                    QMessageBox.Ignore)
                self.pathROILineEdit.setText('None')

        elif len(bbox.split(',')) == 4:
            bbox = bbox.split(',')
            checkROI = True
            for idx, bboxi in enumerate(bbox):
                try:
                    bbox[idx] = float(bbox[idx])
                except:
                    checkROI = False
        else:
            checkROI = False

        if checkROI:
            if isinstance(bbox,list):
                lon = [bbox[0],bbox[2],bbox[2],bbox[0],bbox[0]]
                lat = [bbox[1],bbox[1],bbox[3],bbox[3],bbox[1]]
            else:
                input = bbox
                bbox = None
                with fiona.open(input) as roifile:
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

                lon = bbox.exterior.xy[0].tolist()
                lat = bbox.exterior.xy[1].tolist()

            m = folium.Map(
                location=[0,0], zoom_start=15
                )
            folium.PolyLine(list(zip(lat,lon)),
                        color='red',
                        weight=2,
                        popup=folium.Popup('Region of Interest'),
                        opacity=1).add_to(m)
        
            m.fit_bounds([[np.min(lat), np.min(lon)], [np.max(lat), np.max(lon)]])            
            data = io.BytesIO()
            m.save(data, close_file=False)
            self.mapWidget.setHtml(data.getvalue().decode())

###########################################################################################
## DEMInfo page class
########################################################################################### 
class DEMInfoPage(QWizardPage):
    def __init__(self, parent=None):
        super(DEMInfoPage, self).__init__(parent)

        self.setTitle("Step 5/5 - Digital Elevation Model")
        self.setSubTitle("""
                        <p><b>Specify the DEM information.<\b><p>
                        <p>If the DEM file does not exist, the file must be downloaded after the job creation.</p>
                        """)
        
        self.setPixmap(QWizard.BackgroundPixmap,
            QPixmap(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop.svg').scaled(256,256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            
        pathDEMLabel = QLabel("Path of the DEM directory:")
        pathDEMLabel.setToolTip("""
                                <p>Define the directory where the DEM file is/will be stored.<\p
                                """)
        self.pathDEMLineEdit = QLineEdit()
        self.pathDEMLineEdit.setPlaceholderText('Path of the DEM directory')
        self.pathDEMLineEdit.setReadOnly(True)
        pathDEMBt = QPushButton("Select")
        pathDEMBt.setToolTip('Select the DEM directory')
        pathDEMBt.clicked.connect(self.setExistingDirectory)
        self.registerField('pathDEM*', self.pathDEMLineEdit)

        nameDEMLabel = QLabel("Name of the DEM file:")
        nameDEMLabel.setToolTip("""
                                <p>Define the name of the DEM file. If the user wants to use a external DEM, please select the file.<\p
                                """)
        self.nameDEMLineEdit = QLineEdit()
        self.nameDEMLineEdit.setText('EZInSARDEM')
        self.nameDEMLineEdit.textChanged.connect(self.updateDEMInfoPage)
        nameDEMBt = QPushButton("Select")
        nameDEMBt.setToolTip('Select the DEM file')
        nameDEMBt.clicked.connect(self.setOpenFileName)

        modeDEMLabel = QLabel("Type/Source of the DEM file:")
        modeDEMLabel.setToolTip("""
                                <p>Define the source/type of the DEM. If the DEM is not external, the ellipsoid correction will be performed b y default.<\p
                                """)
        self.modeDEMList = QComboBox()
        self.listDEM = ['SRTM','SRTM-ell',
                    'NASADEM','NASADEM-ell',
                    'Copernicus','Copernicus-ell',
                    'Copernicus3','Copernicus3-ell',
                    'perso']
        self.modeDEMList.addItems(self.listDEM)
        self.modeDEMList.setCurrentIndex(self.listDEM.index("Copernicus-ell"))
        # self.modeDEMList.setBuddy(self.modeDEMList)

        layout = QGridLayout()
        layout.addWidget(pathDEMLabel, 0, 0)
        layout.addWidget(self.pathDEMLineEdit, 0, 1)
        layout.addWidget(pathDEMBt, 0, 2)
        layout.addWidget(nameDEMLabel, 1, 0)
        layout.addWidget(self.nameDEMLineEdit, 1, 1)
        layout.addWidget(nameDEMBt, 1, 2)
        layout.addWidget(modeDEMLabel, 2, 0)
        layout.addWidget(self.modeDEMList, 2, 1)
 
        self.setLayout(layout)

    ###########################################################################################
    ## Callbacks
    def updateDEMInfoPage(self):
        if os.path.isfile(self.pathDEMLineEdit.text()+os.sep+self.nameDEMLineEdit.text()):
            self.modeDEMList.setCurrentIndex(self.listDEM.index("perso"))
    
    def setExistingDirectory(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        if 'DEM directory' in self.sender().toolTip():
            title = 'Please select the DEM directory'
        directory = QFileDialog.getExistingDirectory(self,
            title, options=options)
        if (directory) and ('DEM directory' in self.sender().toolTip()):
            self.pathDEMLineEdit.setText(directory)

    def setOpenFileName(self):    
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,
                "Select a DEM file", self.nameDEMLineEdit.text(),
                "All Files (*);;", options=options)
        if fileName:
            try:
                dst = gdal.Open(fileName).GetRasterBand(1)
                dst = None
                self.pathDEMLineEdit.setText(os.path.dirname(fileName))
                self.nameDEMLineEdit.setText(fileName.split(os.sep)[-1])
            except:
                reply = QMessageBox.critical(self, "Error with the DEM file",
                    'The DEM file is not compatible with EZ-InSAR (via GDAL).',
                    QMessageBox.Ignore)
                self.nameDEMLineEdit.setText('EZInSARDEM')

###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the Image Displayer from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        wizard = createEZInSARjob()
        wizard.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()