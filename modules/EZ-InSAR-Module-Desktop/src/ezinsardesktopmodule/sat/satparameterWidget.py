#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a window for satellite parameters of an EZ-InSAR job

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Mar. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a a window for satellite parameters of an EZ-InSAR job

usage: 
    ezinsardesktop_satparameter -f <str> [options]

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
from PyQt5.QtWidgets import QApplication, QCheckBox, QGridLayout, QComboBox, QSpinBox, QDateTimeEdit, QPushButton, QWidget, QGroupBox, QLabel, QMessageBox

import os, sys, importlib
from docopt import docopt
import datetime

from ezinsar import constants, usermessage
import ezinsar.job as ez
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsardesktopmodule.tools.docsWidget import DocsDialog

###########################################################################################
## Class for the Wizard
###########################################################################################
class satparameter(QWidget):
    """Class definition"""
    closing = pyqtSignal(bool)

    def __init__(self, jobfile, parent=None):
        super(satparameter, self).__init__(parent)

        self.pathjobfile = jobfile
        self.setWindowTitle("EZ-InSAR - Satellite parameters")
        self.resize(750,500)
        self.setStyleSheet(__theme__)

        self.success = False
        self.false = False

        job = ez.load(self.pathjobfile,verbose=False)
        
        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p style="font-size:20px"><b>Satellite Parameters</b></p>')
        btQuit = QPushButton("Close", self)

        btHelp = QPushButton("Help", self)
        btHelp.clicked.connect(self.openhelp)

        ########################################################################
        ## For the sensor
        grpSensor = QGroupBox('Sensor Information')
        grpSensorLayout = QGridLayout()

        self.satNameLabel = QLabel("<b>Platform/Sensor:<b>")
        self.satNameLabel.setToolTip("""
                                    <p>Define the name of platform/sensor that acquired imagery. EZ-InSAR detects any optional EZ-InSAR modules (i.e., for NISAR or SAOCOM).</p>
                                    """)
        self.satNameList = QComboBox()
        listsat = (list(constants.__sensors__.keys()))
        for satiopt in constants.__EZInSARoptionalmoduleSAT__:
            try:
                importlib.import_module('ezinsar%smodule' % (satiopt)).__versionPackage__,
            except:
                listsat.remove(satiopt.upper())
        self.satNameList.addItems(listsat)
        self.satNameList.setCurrentIndex(listsat.index(job.satellite))

        ## For the mode
        self.satModeLabel = QLabel("<b>Mode of acquisition:</b>")
        self.satModeLabel.setToolTip("""
                                    <p>Define the used acquisition mode. Please read the EZ-InSAR documentation for more information.</p>
                                    """)
        self.satModeList = QComboBox()
        self.satModeList.addItems(list(constants.__sensors__[job.satellite].keys()))
        self.satModeList.setCurrentIndex(list(constants.__sensors__[job.satellite].keys()).index(job.satmode))

        grpSensorLayout.addWidget(self.satNameLabel, 0, 0, 1, 1)
        grpSensorLayout.addWidget(self.satNameList, 0, 1, 1, 8)
        grpSensorLayout.addWidget(self.satModeLabel, 1, 0, 1, 1)
        grpSensorLayout.addWidget(self.satModeList, 1, 1, 1, 8)
        grpSensor.setLayout(grpSensorLayout)

        ########################################################################
        ## For the polarisation
        grpPol = QGroupBox('Polarisation Information')
        grpPolLayout = QGridLayout()

        self.satPolLabel = QLabel("<b>Polarisation(s):<b>")
        self.satPolLabel.setToolTip("""
                                    <p>Define the desired polarisation(s).</p>
                                    <p>However, be aware that certain processors (e.g., ISCE-2) and time-series-analysis processors are not able to deal with several polarisaton(s). It will be require to repeat the EZ-InSAR job.</p>
                                    """)
        self.satPol1 = QCheckBox("VV Polarisation")
        if 'VV' in job.polarisation: 
            self.satPol1.setChecked(True) 
        else:
            self.satPol1.setChecked(False) 
        self.satPol2 = QCheckBox("VH Polarisation")
        if 'VH' in job.polarisation: 
            self.satPol2.setChecked(True) 
        else:
            self.satPol2.setChecked(False) 
        self.satPol3 = QCheckBox("HH Polarisation")
        if 'HH' in job.polarisation: 
            self.satPol3.setChecked(True) 
        else:
            self.satPol3.setChecked(False) 
        self.satPol4 = QCheckBox("HV Polarisation")
        if 'HV' in job.polarisation: 
            self.satPol4.setChecked(True) 
        else:
            self.satPol4.setChecked(False) 

        grpPolLayout.addWidget(self.satPolLabel, 0, 0, 1, 3)
        grpPolLayout.addWidget(self.satPol1, 0, 5, 1, 4)
        grpPolLayout.addWidget(self.satPol2, 0, 10, 1, 4)
        grpPolLayout.addWidget(self.satPol3, 1, 5, 1, 4)
        grpPolLayout.addWidget(self.satPol4, 1, 10, 1, 4)
        grpPol.setLayout(grpPolLayout)
        
        ########################################################################
        ## For the direction
        grpOrb = QGroupBox('Orbit Information')
        grpOrbLayout = QGridLayout()

        self.satPassLabel = QLabel("<b>Satellite direction:</b>")
        self.satPassLabel.setToolTip("""
                                    <p>Define the satellite direction (Ascending or Descending).</p>
                                    <p>Only required for online imagery. EZ-InSAR will detect this parameter while image files are stored on disk(s).</p>
                                    """)
        self.satPassList = QComboBox()
        self.satPassList.addItems(['Ascending','Descending'])
        if not job.satpass == None: 
            self.satPassList.setCurrentIndex(['Ascending','Descending'].index(job.satpass.capitalize()))
        else:
            self.satPassList.setCurrentIndex(0)

        ## For the relative orbit
        self.satRelorbitLabel = QLabel("<b>Relative orbit:</b>")
        self.satRelorbitLabel.setToolTip("""
                                    <p>Define the relative orbit.</p>
                                    <p>Only required for online imagery. EZ-InSAR will detect this parameter while image files are stored on disk(s).</p>
                                    """)
        self.satRelorbitSpin = QSpinBox()
        self.satRelorbitSpin.setMaximum(100000)
        self.satRelorbitSpin.setMinimum(1)
        if not job.relorbit == None: 
            self.satRelorbitSpin.setValue(job.relorbit)
        else: 
            self.satRelorbitSpin.setValue(1)
 

        grpOrbLayout.addWidget(self.satPassLabel, 0, 0, 1, 1)
        grpOrbLayout.addWidget(self.satPassList, 0, 1, 1, 8)
        grpOrbLayout.addWidget(self.satRelorbitLabel, 1, 0, 1, 1)
        grpOrbLayout.addWidget(self.satRelorbitSpin, 1, 1, 1, 8)
        grpOrb.setLayout(grpOrbLayout)

        ########################################################################
        ## Dates
        grpDate = QGroupBox('Date Information')
        grpDateLayout = QGridLayout()

        self.satDate1Label = QLabel("<b>Start Date:</b>")
        self.satDate1Label.setToolTip("""
                                    <p>Define the start date for online search.</p>
                                    <p>Only required for online imagery. EZ-InSAR will detect this parameter while image files are stored on disk(s).</p>
                                    """)
        self.satDate1Value = QDateTimeEdit()
        self.satDate1Value.setDisplayFormat("yyyy-MM-dd HH:mm:ss") 
        self.satDate1Value.setMinimumDate(datetime.datetime(1900, 1, 1, 0, 0, 0))
        self.satDate1Value.setMaximumDate(datetime.datetime(2500, 1, 1, 0, 0, 0))
        self.satDate1Value.setDate(job.date1)

        self.satDate2Label = QLabel("<b>End Date:</b>")
        self.satDate2Label.setToolTip("""
                                    <p>Define the end date for online search.</p>
                                    <p>Only required for online imagery. EZ-InSAR will detect this parameter while image files are stored on disk(s).</p>
                                    """)
        self.satDate2Value = QDateTimeEdit()
        self.satDate2Value.setDisplayFormat("yyyy-MM-dd HH:mm:ss") 
        self.satDate2Value.setMinimumDate(datetime.datetime(1900, 1, 1, 0, 0, 0))
        self.satDate2Value.setMaximumDate(datetime.datetime(2500, 1, 1, 0, 0, 0))
        self.satDate2Value.setDate(job.date2)

        grpDateLayout.addWidget(self.satDate1Label, 0, 0, 1, 1)
        grpDateLayout.addWidget(self.satDate1Value, 0, 1, 1, 8)
        grpDateLayout.addWidget(self.satDate2Label, 1, 0, 1, 1)
        grpDateLayout.addWidget(self.satDate2Value, 1, 1, 1, 8)
        grpDate.setLayout(grpDateLayout)

        ########################################################################
        ## Save button
        btSave = QPushButton("Save", self)
        
        ########################################################################
        ## Layout
        layout = QGridLayout()

        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 8, Qt.AlignCenter)
        layout.addWidget(btQuit, 0, 9, 1, 1)
        layout.addWidget(grpSensor, 1, 0, 1, 10)
        layout.addWidget(grpPol, 2, 0, 1, 10)
        layout.addWidget(grpOrb, 3, 0, 1, 10)
        layout.addWidget(grpDate, 4, 0, 1, 10)
        layout.addWidget(btSave, 5, 9, 1, 1)
        layout.addWidget(btHelp, 5, 0, 1, 1)

        self.setLayout(layout)

        self.updatesatWidget()

        btQuit.clicked.connect(self.closemaybe)
        self.satPol1.clicked.connect(self.updatesatWidget)
        self.satPol2.clicked.connect(self.updatesatWidget)
        self.satPol3.clicked.connect(self.updatesatWidget)
        self.satPol4.clicked.connect(self.updatesatWidget)
        self.satNameList.currentTextChanged.connect(self.updatesatWidget)
        btSave.clicked.connect(self.save)

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def openhelp(self):
        helpdial = DocsDialog('applications%ssatellite%ssatparameters.html' % (os.sep,os.sep))
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

        job.satellite = self.satNameList.currentText()
        job.satmode = self.satModeList.currentText()

        pol = []
        if self.satPol1.isChecked():
            pol.append('VV')
        if self.satPol2.isChecked():
            pol.append('VH')
        if self.satPol3.isChecked():
            pol.append('HH')
        if self.satPol4.isChecked():
            pol.append('HV')
        job.polarisation = pol

        if job.satellite == 'S1':
            job.relorbit = self.satRelorbitSpin.value()
            job.satpass = self.satPassList.currentText().upper()
        else:
            job.relorbit = None
            job.satpass = None

        job.date1 = self.satDate1Value.dateTime().toPyDateTime()
        job.date2 = self.satDate2Value.dateTime().toPyDateTime()
        ez.save(job,self.pathjobfile,verbose=False)
        reply = QMessageBox.information(self, "EZ-InSAR Information",
            'The new satellite parameters have been saved.',
            QMessageBox.Ok)

    def updatesatWidget(self):
        """Update the widget"""
        if not self.satNameList.currentText() == 'S1':
            self.satRelorbitSpin.setDisabled(True)
            self.satPassList.setDisabled(True)
            self.satDate1Value.setDisabled(True)
            self.satDate2Value.setDisabled(True)
        else:
            self.satRelorbitSpin.setDisabled(False)
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
            if 'VV' in self.sender().text():
                self.satPol1.setChecked(True)
            elif 'VH' in self.sender().text():
                self.satPol2.setChecked(True)
            elif 'HH' in self.sender().text():
                self.satPol3.setChecked(True)
            elif 'HV' in self.sender().text():
                self.satPol4.setChecked(True)

###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not os.path.isfile(args['--file']):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No file',None))
    
    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the Satellite parameter tools from EZ-InSAR Desktop Application',None,True,lockfree=True)    

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    
    if tools.checklicense():
        widget = satparameter(os.path.abspath(args['--file']))
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()

