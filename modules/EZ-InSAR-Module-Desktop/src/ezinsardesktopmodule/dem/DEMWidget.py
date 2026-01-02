#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open the DEM tool

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Mar. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open the DEM tool

usage: 
    ezinsardesktop_DEM -f <str> [options]

Arguments:
    -f, --file <str>        EZ-InSAR job file

Other-options:
    -h, --help
"""
###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QCheckBox, QGridLayout, QLabel, QLineEdit, QMessageBox, QComboBox, QPushButton, QFileDialog, QWidget, QGroupBox, QDialog, QTextEdit

import os, sys, time
import numpy as np
from docopt import docopt

from ezinsar import constants, usermessage
import ezinsar.job as ez
from ezinsardesktopmodule import __file__ as __root_module__
from ezinsardesktopmodule.tools import EPSGcodeDial
from ezinsardesktopmodule.log import logWorker
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__, __docker_running__
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsardesktopmodule.tools.docsWidget import DocsDialog

###########################################################################################
## Classes
###########################################################################################
class HelpMessageBox(QDialog):
    def __init__(self,title,message,detailedtext):
        super(HelpMessageBox, self).__init__()
        self.setWindowTitle(title)
        self.resize(700,350)
        self.setStyleSheet(__theme__)

        layout = QGridLayout()
        messlabel = QLabel(message)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setMarkdown(detailedtext)
        layout.addWidget(messlabel)
        layout.addWidget(text)
        self.setLayout(layout)

class Worker(QObject):
    """Worker class 

        Build the worker
    """
    textSignal = pyqtSignal(str)
    finished = pyqtSignal()
    intReady = pyqtSignal(int)
    error = pyqtSignal(str)
    success = pyqtSignal(str)
    
    def __init__(self, jobfile, parent=None, verbose=False, ellfile = None, ellcorrection=True, processor=None, clip=True, EPSG = '4326', nodata= 0):
        super(Worker, self).__init__(parent)

        self.jobfile = jobfile
        self.TextInfo = ''
        self.running = True
        self.messageerror = ''
        self.messagesuccess = ''
        self.parent = parent 
        self.verbose = verbose   

        self.job = ez.load(jobfile,verbose=False)

        self.ellfile = ellfile
        self.ellcorrection = ellcorrection
        self.processor = processor
        self.clip = clip
        self.EPSG = EPSG
        self.nodata = nodata

    def run(self):
        try:
            self.job.downloaddem(ell = self.ellfile, 
                                ellcorrection = self.ellcorrection,
                                processor = self.processor, 
                                clip = self.clip, 
                                EPSG = self.EPSG, 
                                docker = __docker_running__, 
                                nodata = self.nodata,
                                verbose = self.verbose)
            ez.save(self.job,self.jobfile)
            time.sleep(1)

        except:
            time.sleep(1)
            self.messageerror = 'Error during the DEM import'
            self.error.emit(self.messageerror)
    
        if self.messageerror == '':
            self.messagesuccess = 'DEM import completed.'
            self.success.emit(self.messagesuccess)

        self.running=False
        self.finished.emit()

class DEMtool(QWidget):
    """QWidget class 

        Build the widget windows
    """

    closing = pyqtSignal(bool)

    def __init__(self, jobfile, parent=None):
        super(DEMtool, self).__init__(parent)

        self.pathjobfile = jobfile
        self.setWindowTitle("EZ-InSAR - DEM import")
        self.setStyleSheet(__theme__)
        self.resize(750, 500)
        self.success = False
        self.false = False
        self.parent = parent
        self.workerprocess = None
        self.threadprocess = None

        ## Read the job
        job = ez.load(self.pathjobfile,verbose=False)

        ## Title + quit button  
        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p style="font-size:20px"><b>Digital Elevation Model Import<\b></p>')
        btQuit = QPushButton("Close", self)

        ############################################
        ## EZ-InSAR DEM parameter group
        self.groupBox1 = QGroupBox("EZ-InSAR DEM information")
        self.groupBox1.show()

        # Path of the DEM
        demPathLabel = QLabel("<p><b>DEM Directory:<\b></p>")
        demPathLabel.setToolTip("""
                                <p>Path of the DEM directory</p>
                                """)
        self.demPathLineEdit = QLineEdit()
        self.demPathLineEdit.setReadOnly(True)
        self.demPathLineEdit.setText(job.pathDEM)
        self.demPathBt = QPushButton("Select", self)

        ## Name of the DEM
        demNameLabel = QLabel("<p><b>DEM Name:<\b></p>")
        demNameLabel.setToolTip("""
                                <p>Name of the DEM file.</p>
                                """)
        self.demNameLineEdit = QLineEdit()
        self.demNameLineEdit.setReadOnly(True)
        self.demNameLineEdit.setText(job.nameDEM)
        self.demNameBt = QPushButton("Select", self)

        # Type of the DEM
        demTypeLabel = QLabel("<p><b>DEM Type:<\b></p>")
        demTypeLabel.setToolTip("""
                                <p>Type of the DEM file. It will be automatically defined.</p>
                                """)
        self.demTypeLineEdit = QLineEdit()
        self.demTypeLineEdit.setReadOnly(True)
        self.demTypeLineEdit.setText(job.typeDEM)

        # ROI for the DEM
        roiLabel = QLabel("<p><b>Region of Interest:<\b></p>")
        roiLabel.setToolTip("""
                            <p>Region of interest in <W,S,E,N> format used to import the DEM.</p>
                            """)
        self.roiLineEdit = QLineEdit()
        self.roiLineEdit.setReadOnly(True)
        self.roiLineEdit.setText("%0.5f,%0.5f,%0.5f,%0.5f" % (np.min(job.roi.exterior.xy[0]),
                                                    np.min(job.roi.exterior.xy[1]),
                                                    np.max(job.roi.exterior.xy[0]),
                                                    np.max(job.roi.exterior.xy[1]),
                                ))
        
        ############################################
        ## Processor 
        self.groupBox2 = QGroupBox("SAR/InSAR processor")
        self.groupBox2.show()

        processorLabel = QLabel("<p><b>Processor:</p><\b>")
        processorLabel.setToolTip("""
                            <p>Name of the SAR/InSAR processor that will be used. It is required to format the DEM.</p>
                            """)
        self.processorList = QComboBox()
        self.processor = ['gamma',
                    'snap',
                    'doris',
                    'isce2']
        self.processorList.addItems(self.processor)
        self.processorList.setCurrentIndex(self.processor.index(constants.__defautprocessor__))
        
        ############################################
        ## Processing parameters
        self.btprocPara = QPushButton("Show advanced parameters", self)
        self.btprocPara.clicked.connect(self.showprocessingpara)

        self.groupBox3 = QGroupBox("Advanced parameters")
        self.groupBox3.hide()

        modeDEMLabel = QLabel("<p>Source of the DEM</p>")
        self.modeDEMList = QComboBox()
        self.listDEM = ['SRTM',
                    'NASADEM',
                    'Copernicus',
                    'perso']
        self.modeDEMList.addItems(self.listDEM)
        self.modeDEMList.setCurrentIndex(self.listDEM.index(job.typeDEM.replace('-ell','')))
        self.modeDEMList.currentTextChanged.connect(self.updatelayout)

        ellcorrectionLabel = QLabel("<p>Ellipsoid correction:</p>")
        self.ellcorrection = QCheckBox("Enable the correction")
        self.ellcorrection.setChecked(True) 
        self.ellcorrection.clicked.connect(self.updatelayout)

        ellfileLabel = QLabel("<p>Ellipsoid file</p>")
        self.ellfileLineEdit = QLineEdit()
        self.ellfileLineEdit.setReadOnly(True)
        self.ellfileLineEdit.setText('')
        self.ellfileBt = QPushButton("Select", self)

        croppingLabel = QLabel("<p>Cropping DEM:</p>")
        self.cropping = QCheckBox("Enable the cropping")
        self.cropping.setChecked(True) 

        EPSGcodeLabel = QLabel("<p>EPSG CRS Code</p>")
        self.EPSGcodeLineEdit = QLineEdit()
        self.EPSGcodeLineEdit.setReadOnly(False)
        self.EPSGcodeLineEdit.setText("4326")
        self.EPSGcodeBt = QPushButton("Find", self)

        NoDataLabel = QLabel("<p>No-Data Value</p>")
        self.NoDataLineEdit = QLineEdit()
        self.NoDataLineEdit.setReadOnly(False)
        self.NoDataLineEdit.setText("0")
        
        # Save button
        self.btImport = QPushButton("Import", self)

        # Help button
        btHelp = QPushButton("Help", self)
        
        ## Layout
        layout = QGridLayout()
        layoutgrp1 = QGridLayout()
        layoutgrp2 = QGridLayout()
        layoutgrp3 = QGridLayout()

        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 6, Qt.AlignCenter)
        layout.addWidget(btQuit, 0, 9, 1, 1)

        layoutgrp1.addWidget(demPathLabel, 1, 0, 1, 1)
        layoutgrp1.addWidget(self.demPathLineEdit, 1, 1, 1, 7)
        layoutgrp1.addWidget(self.demPathBt, 1, 9, 1, 1)
        layoutgrp1.addWidget(demNameLabel, 2, 0, 1, 1)
        layoutgrp1.addWidget(self.demNameLineEdit, 2, 1, 1, 7)
        layoutgrp1.addWidget(self.demNameBt, 2, 9, 1, 1)
        layoutgrp1.addWidget(demTypeLabel, 3, 0, 1, 1)
        layoutgrp1.addWidget(self.demTypeLineEdit, 3, 1, 1, 7)
        layoutgrp1.addWidget(roiLabel, 4, 0, 1, 1)
        layoutgrp1.addWidget(self.roiLineEdit, 4, 1, 1, 7)
        self.groupBox1.setLayout(layoutgrp1)
        layout.addWidget(self.groupBox1,1,0,1,10)

        layoutgrp2.addWidget(processorLabel, 0, 1, 1, 1)
        layoutgrp2.addWidget(self.processorList, 0, 2, 1, 7)
        self.groupBox2.setLayout(layoutgrp2)
        layout.addWidget(self.groupBox2,2,0,1,10)

        layout.addWidget(self.btprocPara, 3, 0, 1, 1)

        layoutgrp3.addWidget(modeDEMLabel, 0, 1, 1, 1)
        layoutgrp3.addWidget(self.modeDEMList, 0, 2, 1, 6)
        layoutgrp3.addWidget(ellcorrectionLabel, 1, 1, 1, 1)
        layoutgrp3.addWidget(self.ellcorrection, 1, 2, 1, 6)
        layoutgrp3.addWidget(ellfileLabel, 2, 1, 1, 1)
        layoutgrp3.addWidget(self.ellfileLineEdit, 2, 2, 1, 6)
        layoutgrp3.addWidget(self.ellfileBt, 2, 9, 1, 1)
        layoutgrp3.addWidget(croppingLabel, 3, 1, 1, 1)
        layoutgrp3.addWidget(self.cropping, 3, 2, 1, 6)
        layoutgrp3.addWidget(EPSGcodeLabel, 4, 1, 1, 1)
        layoutgrp3.addWidget(self.EPSGcodeLineEdit, 4, 2, 1, 6)
        layoutgrp3.addWidget(self.EPSGcodeBt, 4, 9, 1, 1)
        layoutgrp3.addWidget(NoDataLabel, 5, 1, 1, 1)
        layoutgrp3.addWidget(self.NoDataLineEdit, 5, 2, 1, 6)

        self.groupBox3.setLayout(layoutgrp3)
        layout.addWidget(self.groupBox3,4,0,1,10)
        
        layout.addWidget(self.btImport, 13, 9, 1, 1)
        layout.addWidget(btHelp, 13, 0, 1, 1)

        self.setLayout(layout)

        self.processorList.currentTextChanged.connect(self.updatelayout)

        btQuit.clicked.connect(self.closemaybe)
        self.demPathBt.clicked.connect(self.selectiondirectory)
        self.demNameBt.clicked.connect(self.selectiondemfile)
        self.EPSGcodeBt.clicked.connect(self.openEPSGcodeDiag)
        self.btImport.clicked.connect(self.progress)
        btHelp.clicked.connect(self.openhelp)

        job = None

        self.updatelayout()

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def messageerror(self,msg):
        """Error message
        """
        reply = QMessageBox.critical(self, "EZ-InSAR Error",
                msg,
                QMessageBox.Ok)
        
    def messagesuccess(self,msg):
        reply = QMessageBox.information(self, "EZ-InSAR Information",
                msg,
                QMessageBox.Ok)
        
    def showprocessingpara(self):
        """Show the advanced parameters    
        """
        if 'Show' in self.sender().text():
            self.groupBox3.show()
            self.btprocPara.setText('Mask advanced parameters')
        else:
            self.groupBox3.hide()
            self.btprocPara.setText('Show advanced parameters')

    def updatelayout(self):
        """Update the layout
        """
        if self.ellcorrection.isChecked():
            if not 'perso' in self.modeDEMList.currentText():
                self.demTypeLineEdit.setText(self.modeDEMList.currentText()+'-ell')
            else: 
                self.demTypeLineEdit.setText(self.modeDEMList.currentText())  
        else:
            self.demTypeLineEdit.setText(self.modeDEMList.currentText())

        if self.demNameLineEdit.text() == '':
            self.demNameLineEdit.setText('EZInSARDEM')

        if self.processorList.currentText() in ['gamma','snap']:
            self.EPSGcodeLineEdit.setEnabled(True)
        else:
            self.EPSGcodeLineEdit.setEnabled(False)
            if not self.EPSGcodeLineEdit.text() == '4326':
                self.messageerror('The EPSG Code 4326 is required.')
                self.EPSGcodeLineEdit.setText('4326')

        if self.demTypeLineEdit.text() == 'perso':
            if not os.path.isfile(self.demPathLineEdit.text()+os.sep+self.demNameLineEdit.text()):
                self.messageerror('EZ-InSAR does not detect the DEM file.')

            if self.ellcorrection.isChecked(): 
                if not os.path.isfile(self.ellfileLineEdit.text()):
                    self.messageerror('An ellipsoid file is required.')
    
    def selectiondirectory(self):
        """Selection of the DEM directory
        """
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
            'Select a DEM directory', options=options)
        if directory: 
            self.demPathLineEdit.setText(directory)
        self.updatelayout()

    def selectiondemfile(self):
        """Selection of the DEM file
        """
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,
                "Select an DEM file",'', options=options)
        if fileName: 
            self.demPathLineEdit.setText(os.path.dirname(fileName))
            self.demNameLineEdit.setText(fileName.split(os.sep)[-1])
        self.updatelayout()

    def openEPSGcodeDiag(self):
        """Selection of a EPSG code
        """
        reply = EPSGcodeDial.EPSGcodeDial(roi=[float(x) for x in self.roiLineEdit.text().split(',')])
        reply.exec_()
        if reply.validation == True: 
            self.EPSGcodeLineEdit.setText(str(reply.epsgcode))

    def save(self):
        """Save the DEM parameters in the job
        """
        job = ez.load(self.pathjobfile,verbose=False)
        if not self.demPathLineEdit.text() == '':
            job.pathDEM = self.demPathLineEdit.text()
        else: 
            job.pathDEM = None
        if not self.demNameLineEdit.text() == '':
            job.nameDEM = self.demNameLineEdit.text()
        else: 
            job.nameDEM = None
        job.typeDEM = self.demTypeLineEdit.text()
        ez.save(job,self.pathjobfile,verbose=False)

    def closemaybe(self):
        """Quit the Widget
        """
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
        
    def stopcurrentworker(self):
        """Stop the current worker
        """
        self.workerprocess = None
        self.btImport.setEnabled(True)

    def openhelp(self):
        helpdial = DocsDialog(['applications','dem','dem'])
        helpdial.show()
        helpdial.exec()

    def progress(self):
        """Run the progressing 
        """
        self.save()
        self.btImport.setEnabled(False)

        if self.ellfileLineEdit.text() == '':
            ellfile = None
        else:
            ellfile = self.ellfileLineEdit.text()

        if self.parent == None:
            if self.workerprocess == None:
                self.messagesuccess('Import in progress')

                self.workerprocess = Worker(self.pathjobfile,
                                    verbose=True,
                                    ellfile=ellfile,
                                    ellcorrection=self.ellcorrection.isChecked(),
                                    processor = self.processorList.currentText(),
                                    clip = self.cropping.isChecked(),
                                    EPSG = self.EPSGcodeLineEdit.text(),
                                    nodata = int(self.NoDataLineEdit.text()))
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

        else:
            job = ez.load(self.pathjobfile,verbose=False)
            logfile = job.log
            job = None

            if self.parent.workerprocess == None:
                self.parent.dockprogressbar.show()
                self.parent.workerprocess = Worker(self.pathjobfile,
                                            verbose=False,
                                            ellfile=ellfile,
                                            ellcorrection=self.ellcorrection.isChecked(),
                                            processor = self.processorList.currentText(),
                                            clip = self.cropping.isChecked(),
                                            EPSG = self.EPSGcodeLineEdit.text(),
                                            nodata = int(self.NoDataLineEdit.text()))
                self.parent.threadprocess = QThread()
                self.parent.workerprocess.moveToThread(self.parent.threadprocess)
                self.parent.threadprocess.started.connect(self.parent.workerprocess.run)
                self.parent.workerprocess.finished.connect(self.parent.threadprocess.quit)
                self.parent.workerprocess.textSignal.connect(self.parent.updateTextEditverbose)
                self.parent.workerprocess.error.connect(self.parent.messageerror)
                self.parent.workerprocess.success.connect(self.parent.messagesuccess)
                self.parent.workerprocess.finished.connect(self.parent.stopcurrentworker)   
                self.parent.workerprocess.success.connect(self.parent.stopcurrentworker)

                self.parent.workerlog = logWorker.Worker(logfile,self.parent.workerprocess)
                self.parent.threadlog = QThread()
                self.parent.workerlog.moveToThread(self.parent.threadlog)
                self.parent.workerlog.textSignal.connect(self.parent.updateTextEditverbose)
                self.parent.threadlog.started.connect(self.parent.workerlog.run)
                self.parent.workerlog.finished.connect(self.parent.threadlog.quit)

                self.parent.threadprocess.start()
                self.parent.threadlog.start()
                self.parent.qtCancel.setEnabled(True)
                
            else:
                self.messageerror('The worker for DEM import is still running. Please stop it, if required')

###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not os.path.isfile(args['--file']):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No file',None))
    
    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the DEM tool from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        widget = DEMtool(os.path.abspath(args['--file']))
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()
