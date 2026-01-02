#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module for the main window of EZ-InSAR Desktop

The module allows to run the main window of EZ-InSAR Desktop 
    
    (Supplementary module for EZ-InSAR)

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Feb. 2025

"""
###########################################################################################
## Packages
###########################################################################################
## For PyQt
from PyQt5.QtCore import QFileInfo, Qt, QThread
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QAction, QApplication, QFileDialog, QMainWindow, QMessageBox, QTextEdit, QPushButton, QWidget, QGridLayout, QDockWidget, QProgressBar

## Python
import os
import webbrowser
import shutil
import subprocess
import datetime
import time

## For EZ-InSAR Desktop
from ezinsardesktopmodule.job import jobparameterWidget, jobdirectoryWidget, jobstatusBar
from ezinsardesktopmodule.roi import roiWidget
from ezinsardesktopmodule.sat import satparameterWidget, SLClistOnlineWorker, SLClistTableWidget, SLCMapWidget, ServerDialog, SARDownloaderWidget
from ezinsardesktopmodule.sat.tools.s1 import S1detectionWidget, S1ASFbaselinesWidget
from ezinsardesktopmodule.dem import DEMWidget
from ezinsardesktopmodule.process import processInitDialog, processParameterWidget, processRunDialog
from ezinsardesktopmodule.display import displayWidget
from ezinsardesktopmodule.interface import pluginsWidget
from ezinsardesktopmodule.log import logcallbacks, logWorker
from ezinsardesktopmodule.tools import tools, threadcpuram
from ezinsardesktopmodule.config import configDial, aboutDial, licenseDial
from ezinsardesktopmodule.config.settings import __usefullinks__

## For EZ-InSAR
from ezinsardesktopmodule import __file__ as __moduleroot__
import ezinsar.job as ez
from ezinsar.constants import __EZInSARoptionalmodule__, __cachedir__
from ezinsar import usermessage
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__

###########################################################################################
## MainWindow class
###########################################################################################
class MainWindow(QMainWindow):
    """Main class"""
    ## Initialisation of the class
    def __init__(self):
        super(MainWindow, self).__init__()
        self.root = QFileInfo(__file__).absolutePath()
        self.curEZInSARjob = 'No EZ-InSAR loaded'
        self.curjob = None

        self.setWindowTitle("%s[*] - EZ-InSAR" % (self.curEZInSARjob))
        self.curapp = None
        self.curwidget = None

        self.setStyleSheet(__theme__)

        # Create the worker/thread variables
        self.threadlog = None
        self.workerlog = None

        self.threadprocess = None
        self.workerprocess = None

        # Store the processing mode 
        self.processingmode = None
        self.processingapproach = None
        self.processor = None

        # Create the main layout
        self.mainlayout = QGridLayout()
        self.mainlayoutwidget = QWidget()
        self.mainlayoutwidget.setLayout(self.mainlayout)
        self.setCentralWidget(self.mainlayoutwidget)

        # Create the menus
        self.createActions()
        self.createMenus()
        self.createStatusBar()

        # Create the docks
        self.createDockWindows()

        # Initialise the threads/workers variables
        self.thread = threadcpuram.RenderThread()
        self.thread.textSignal.connect(self.updateTextEditcpuram)
        self.thread.start()

    ###########################################################################################
    ## Callbacks 
    ###########################################################################################
    ## Create a new EZ-InSAR job file (via the wizard)
    def newFile(self):
        """Create a new job with the assistant"""
        try:
            from ezinsardesktopmodule.job import jobcreationWizard
            self.mainlayoutwidget.setEnabled(False)
            self.curwidget = jobcreationWizard.createEZInSARjob()
            self.curwidget.exec_()
            self.curEZInSARjob = self.curwidget.pathjobfile
            self.curwidget.close()
            self.curwidget = None
            self.mainlayoutwidget.setEnabled(True)
            self.open()

        except:
            self.curwidget.close()
            self.curwidget = None
            self.mainlayoutwidget.setEnabled(True)
            reply = QMessageBox.critical(self, "Error during the creation of the EZ-InSAR job",
                    'There is an error during the creation of the EZ-InSAR job. Please see the log.',
                    QMessageBox.Ok)

    ## Open a EZ-InSAR job file
    def open(self):
        """Open an EZ-InSAR job"""
        if 'Open' in self.sender().text(): 
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getOpenFileName(self,
                    "Select an EZ-InSAR job file",'',
                    "*.ei", options=options)
        else: 
            fileName = self.curEZInSARjob
        
        if fileName:
            try: 
                self.job = ez.load(fileName,verbose=False)
                if not 'EIjob' in str(type(self.job)):
                    reply = QMessageBox.critical(self, "Opening error ",
                        'The file is not an EZ-InSAR job file',
                        QMessageBox.Ok)
                    raise ValueError
                try: 
                    if self.job.log == None: 
                        pathlog = __cachedir__+os.sep+fileName.split(os.sep)[-1].replace('.ei','.log')
                        reply = QMessageBox.warning(self, "Log file error ",
                        'There is no log file in the current job. However it is required. The log will be stored in %s' % (pathlog),
                        QMessageBox.Ok)
                        self.job.log = pathlog
                        ez.save(self.job,fileName,verbose=False)

                    if not os.path.isfile(self.job.log):
                        with open(self.job.log,'w') as flog:
                            flog.write('init\n')
                
                    self.job.check(verbose=False)
                    self.curEZInSARjob = fileName
                    self.setWindowTitle("EZ-InSAR - %s / Job Title: %s" % (self.curEZInSARjob.split(os.sep)[-1],self.job.nameJob))
                    self.updateTextEditverbosefrommsg(logcallbacks.updatelog(self.job.log))
                    self.barjob.update(job=self.job)
                    self.messagesuccess('Job %s imported' % (self.job.nameJob))

                    ## Unlock the mainwindow
                    # self.saveAct.setEnabled(True)
                    self.saveAsAct.setEnabled(True)
                    self.fileMenujobdir.setEnabled(True)
                    self.fileMenujobpara.setEnabled(True)
                    self.fileMenujobroi.setEnabled(True)
                    self.fileMenujobroilog.setEnabled(True)
                    self.SARMenu.setEnabled(True)
                    self.demMenu.setEnabled(True)
                    self.processMenu.setEnabled(True)
                
                    # self.dockdata.hide()
                    self.datasetList = displayWidget.datatree(self.curEZInSARjob,parent=self)
                    self.dockdata.setWidget(self.datasetList)

                except Exception as e:
                    self.messageerror(f"Error during the verification of the EZ-InSAR job:\n{e}")
            except Exception as e:
                self.messageerror(f"Error during the opening of the EZ-InSAR job:\n{e}")

    # ## Save the current EZ-InSAR job
    # def save(self):
    #     ez.save(self.job,self.curEZInSARjob,verbose=False)
    #     self.messagesuccess('Job save')
    #     self.updateTextEditverbosefrommsg(logcallbacks.updatelog(self.job.log))

    ## Export the current EZ-InSAR job
    def saveAs(self):
        """Export the EZ-InSAR job"""
        if os.path.isfile(self.curEZInSARjob):
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(self,
                    "Select an EZ-InSAR job file",'',
                    "*.ei", options=options)
            if fileName:
                try: 
                    shutil.copy(self.curEZInSARjob,fileName)
                    self.messagesuccess('EZ-InSAR job exported to %s' %(fileName))
                except:
                    self.messageerror('Error during the export of the EZ-InSAR job')
        else:
            self.messageerror('Please load an EZ-InSAR job')

    ## Change the job parameters
    def jobparameters(self):
        """Open the job-parameter tool"""
        if not os.path.isfile(self.curEZInSARjob):
            self.messageerror('Please load an EZ-InSAR job')
        else:
            if not self.curwidget == None:
                self.curwidget.close()
                self.curwidget = None
            self.curwidget = jobparameterWidget.jobparameter(self.curEZInSARjob)
            self.mainlayout.addWidget(self.curwidget,0,0)
            self.curwidget.closing.connect(self.updatelog)

    ## Change the job directories
    def jobdirectory(self):
        """Open the job-directory tool"""
        if not os.path.isfile(self.curEZInSARjob):
            self.messageerror('Please load an EZ-InSAR job')
        else:
            if not self.curwidget == None:
                self.curwidget.close()
                self.curwidget = None
            self.curwidget = jobdirectoryWidget.jobdirectory(self.curEZInSARjob)
            self.mainlayout.addWidget(self.curwidget,0,0)
            self.curwidget.closing.connect(self.updatelog)

    ## Create the job directories
    def jobdirectorycreate(self):
        """Create the job directories"""
        if not os.path.isfile(self.curEZInSARjob):
            self.messageerror('Please load an EZ-InSAR job')
        else:
            try: 
                job = ez.load(self.curEZInSARjob,verbose=False)
                job.mkdir(verbose=False)
                self.updatelog()
                self.messagesuccess('The job directories are ready.')
            except:
                self.messageerror('Error during the creation of directories')

    ## Open the log (external application)
    def logcallback(self):
        """Open the EZ-InSAR log"""
        if not os.path.isfile(self.curEZInSARjob):
            self.messageerror('Please load an EZ-InSAR job')
        else:
            cmd = 'python3 %s -f %s' % (__moduleroot__.replace('__init__.py','log'+os.sep+'logWidget.py'),
                                        self.curEZInSARjob)
            subprocess.Popen(cmd,shell=True)
    
    ## Open the ROI widget
    def roicallback(self):
        """Open the ROI tool"""
        if not os.path.isfile(self.curEZInSARjob):
            self.messageerror('Please load an EZ-InSAR job')
        else:
            if not self.curwidget == None:
                self.curwidget.close()
                self.curwidget = None
            self.curwidget = roiWidget.roitool(self.curEZInSARjob)
            self.mainlayout.addWidget(self.curwidget,0,0)
            self.curwidget.closing.connect(self.updatelog)

    ## Change the satellite parameters
    def satcallback(self):
        """Open the sat-parameter tool"""
        if not os.path.isfile(self.curEZInSARjob):
            self.messageerror('Please load an EZ-InSAR job')
        else:
            if not self.curwidget == None:
                self.curwidget.close()
                self.curwidget = None
            self.curwidget = satparameterWidget.satparameter(self.curEZInSARjob)
            self.mainlayout.addWidget(self.curwidget,0,0)
            self.curwidget.closing.connect(self.updatelog)

    ## Retrieve a SLC list
    def SLClistretrievecallback(self):
        """Retrieve a SLC list"""
        if not os.path.isfile(self.curEZInSARjob):
            self.messageerror('Please load an EZ-InSAR job')
        else:
            # From a SLC list
            if self.sender().text() == 'Based on an EZ-InSAR SLC list': 
                options = QFileDialog.Options()
                fileName, _ = QFileDialog.getOpenFileName(self,
                        "Select an EZ-InSAR SLC List",'',
                        "*.csv", options=options)
                if fileName: 
                    try: 
                        job = ez.load(self.curEZInSARjob,verbose=False)
                        job.initiateSLC(mode='list',file=fileName)
                        ez.save(job,self.curEZInSARjob) 
                        job = None
                        self.messagesuccess('The SLC has been imported.')
                        self.openSLClist()
                    except:
                        self.messageerror('Error during the import of the SLClist')

            # From files stored in disks
            elif self.sender().text() == 'Based on local imagery': 
                    try: 
                        job = ez.load(self.curEZInSARjob,verbose=False)
                        job.initiateSLC(mode='onfile',verbose=False)
                        ez.save(job,self.curEZInSARjob) 
                        job = None
                        self.messagesuccess('The SLC has been created/updated based the stored files.')
                        self.openSLClist()
                    except:
                        self.messageerror('Error during the import of the SLClist')
                    self.updatelog()

            elif self.sender().text() == 'Based on online imagery': 
                job = ez.load(self.curEZInSARjob,verbose=False)
                logfile = job.log
                job = None
                
                if self.workerprocess == None:

                    reply = ServerDialog.ServerDialog()
                    reply.exec_()
                    if not reply.result == None:
                        self.dockprogressbar.show()
                        
                        # Initiate the downloader worker/thread
                        self.workerprocess = SLClistOnlineWorker.Worker(self.curEZInSARjob,server=reply.result)
                        self.threadprocess = QThread()
                        self.workerprocess.moveToThread(self.threadprocess)
                        self.workerprocess.textSignal.connect(self.updateTextEditverbose)
                        self.threadprocess.started.connect(self.workerprocess.run)
                        self.workerprocess.finished.connect(self.threadprocess.quit)
                        self.workerprocess.finished.connect(self.stopcurrentworker)
                        self.workerprocess.error.connect(self.messageerror)
                        self.workerprocess.success.connect(self.messagesuccess)
                        self.workerprocess.success.connect(self.openSLClist)

                        # Initiate the loggin worker/thread
                        self.workerlog = logWorker.Worker(logfile,self.workerprocess)
                        self.threadlog = QThread()
                        self.workerlog.moveToThread(self.threadlog)
                        self.workerlog.textSignal.connect(self.updateTextEditverbose)
                        self.threadlog.started.connect(self.workerlog.run)
                        self.workerlog.finished.connect(self.threadlog.quit)
            
                        # Start both workers
                        self.qtCancel.setEnabled(True)
                        self.threadprocess.start()
                        self.threadlog.start()

                else:
                    self.messageerror('There already is a current processing. Please stop it before running another one.')

    ## For the SLC table
    def openSLClist(self):
        """Open the SLC list"""
        if not os.path.isfile(self.curEZInSARjob):
            self.messageerror('Please load an EZ-InSAR job')
        else:
            job = ez.load(self.curEZInSARjob,verbose=False)
            try: 
                len(job.SLClist['Name'])
                job = None
                if not self.curwidget == None:
                    self.curwidget.close()
                    self.curwidget = None
                self.curwidget = SLClistTableWidget.SLClisttable(self.curEZInSARjob)
                self.mainlayout.addWidget(self.curwidget,0,0)
                self.curwidget.closing.connect(self.updatelog)
            except:
                self.messageerror('Error: No SLC list.')
            job = None

    ## Check the SLC list
    def checkSLClist(self):
        """Check the SLC list"""
        if not os.path.isfile(self.curEZInSARjob):
            self.messageerror('Please load an EZ-InSAR job')
        else:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try: 
                job = ez.load(self.curEZInSARjob,verbose=False)
                len(job.SLClist['Name'])
                try: 
                    job.checkSLClist(verbose=False)
                    self.updatelog()
                    QApplication.restoreOverrideCursor()
                    self.messagesuccess('The SLC list seems fine. Please see the log.')
                except:
                    QApplication.restoreOverrideCursor()
                    self.messageerror('Error during the verification of the SLC list. Please see the log.')
                job = None
            except:
                QApplication.restoreOverrideCursor()
                self.messageerror('Error: No SLC list.')

    ## Open the SLC map
    def openSLCmap(self):
        """Open the SLC map"""
        if not os.path.isfile(self.curEZInSARjob):
            self.messageerror('Please load an EZ-InSAR job')
        else:
            job = ez.load(self.curEZInSARjob,verbose=False)
            try: 
                len(job.SLClist['Name'])
                job = None
                if not self.curwidget == None:
                    self.curwidget.close()
                    self.curwidget = None
                self.curwidget = SLCMapWidget.SLClistmap(self.curEZInSARjob)
                self.mainlayout.addWidget(self.curwidget,0,0)
                self.curwidget.closing.connect(self.updatelog)
            except:
                job = None
                self.messageerror('Error: No SLC list.')

    ## Export the SLC list
    def exportSLClist(self):
        """Export the SLC list"""
        if not os.path.isfile(self.curEZInSARjob):
            self.messageerror('Please load an EZ-InSAR job')
        else:
            if self.sender().text() == 'To a .csv file' or self.sender().text() == 'To a .kmz file': 
                options = QFileDialog.Options()
                if self.sender().text() == 'To a .csv file':
                    fileName, _ = QFileDialog.getSaveFileName(self,
                            "Select a .csv file",'',
                            "*.csv", options=options)
                else:
                    fileName, _ = QFileDialog.getSaveFileName(self,
                            "Select a .kmz file",'',
                            "*.kmz", options=options)
                if fileName: 
                    try: 
                        job = ez.load(self.curEZInSARjob,verbose=False)
                        if self.sender().text() == 'To a .csv file':
                            job.saveSLClist(file=fileName,verbose=False)
                        else:
                            QApplication.setOverrideCursor(Qt.WaitCursor)
                            job.writeSLClisttokmz(file=fileName,verbose=False)
                            QApplication.restoreOverrideCursor()
                        job = None
                        self.messagesuccess('The SLC has been exported to %s.' % (fileName))
                    except:
                        self.messageerror('Error during the export of the SLClist')
                    self.updatelog()   

    ## For the Downloader
    def SLCdownloader(self):
        """Open the SAR Downloader"""
        if not os.path.isfile(self.curEZInSARjob):
            self.messageerror('Please load an EZ-InSAR job')
        else:
            job = ez.load(self.curEZInSARjob,verbose=False)
            try: 
                len(job.SLClist['Name'])
                job = None
                if not self.curwidget == None:
                    self.curwidget.close()
                    self.curwidget = None
                self.curwidget = SARDownloaderWidget.Downloader(self.curEZInSARjob,parent=self)
                self.mainlayout.addWidget(self.curwidget,0,0)
                self.curwidget.closing.connect(self.updatelog)
            except:
                job = None
                self.messageerror('Error: No SLC list.')             
        
    ## S1 detection tracks
    def S1trackcallback(self):
        """Detection of S1 tracks"""
        if not self.curwidget == None:
            self.curwidget.close()
            self.curwidget = None
        self.curwidget = S1detectionWidget.S1detectiontrack(self.curEZInSARjob,parent=self)
        self.mainlayout.addWidget(self.curwidget,0,0)
        self.curwidget.closing.connect(self.updatelog)

    ## ASF Baselines
    def S1ASFBaselines(self):
        """Open the ASF baseline tools"""
        if not os.path.isfile(self.curEZInSARjob):
            self.messageerror('Please load an EZ-InSAR job')
        else:
            job = ez.load(self.curEZInSARjob,verbose=False)
            if (not job.satellite == 'IW') and (not job.satmode == 'IW'): 
                self.messageerror('This tool is only available with Sentinel-1 IW data.')
            else:
                try: 
                    len(job.SLClist['Name'])
                    job = None
                    if not self.curwidget == None:
                        self.curwidget.close()
                        self.curwidget = None
                    self.curwidget = S1ASFbaselinesWidget.S1asfbaselines(self.curEZInSARjob)
                    self.mainlayout.addWidget(self.curwidget,0,0)
                    self.curwidget.closing.connect(self.updatelog)
                except:
                    job = None
                    self.messageerror('Error: No SLC list.')

    ## Open the DEM window
    def DEMcallback(self):
        """Open the DEM tool"""
        if not self.curwidget == None:
            self.curwidget.close()
            self.curwidget = None
        self.curwidget = DEMWidget.DEMtool(self.curEZInSARjob,parent=self)
        self.mainlayout.addWidget(self.curwidget,0,0)
        self.curwidget.closing.connect(self.updatelog)

    ## Change the processing mode
    def processingcheck(self):
        """Check the processing mode"""
        job = ez.load(self.curEZInSARjob,verbose=False)

        creationsuccess = True

        if self.sender().text() == 'Coregistration':
            if job.coregistration == None:
                reply = processInitDialog.ProcessInit(mode='coregistration')
                reply.exec_()
                if reply.validation: 
                    try: 
                        job.initiatecoreg(processor=reply.result[0])
                    except:
                        creationsuccess = False
                else:
                    creationsuccess = False

            if creationsuccess:
                try:
                    self.processor = job.coregistration.processor
                    self.processingmode = 'coregistration'
                    self.processingapproach = None
                except:
                    self.messageerror('Error during the coregistration job creation')

        elif self.sender().text() == 'Interferometric stack':
            if job.ifgstack == None:
                reply = processInitDialog.ProcessInit(mode='ifgstack',prevprocessor=self.processor)
                reply.exec_()
                if reply.validation: 
                    try: 
                        job.initiateifg(processor=reply.result[0])
                    except:
                        creationsuccess = False
                else:
                    creationsuccess = False

            if creationsuccess:
                try: 
                    self.processor = job.ifgstack.processor
                    self.processingmode = 'ifgstack'
                    self.processingapproach = None
                except:
                        self.messageerror('Error during the ifgstack job creation')

        elif self.sender().text() == 'Time-serie analysis':    
            if job.tsprocessing == None:
                reply = processInitDialog.ProcessInit(mode='tsprocessing')
                reply.exec_()
                if reply.validation:
                    try: 
                        job.initiatets(processor=reply.result[0],mode=reply.result[1])
                        self.processingapproach = reply.result[1]
                    except:
                        creationsuccess = False
                else:
                    creationsuccess = False

            if creationsuccess:
                try:
                    self.processingapproach = job.tsprocessing.mode
                    self.processingmode = 'tsprocessing'
                    self.processor = job.tsprocessing.processor
                except:
                        self.messageerror('Error during the tsprocessing job creation')

        elif self.sender().text() == 'Intensity stack':
            if job.intstack == None:
                reply = processInitDialog.ProcessInit(mode='intstack')
                reply.exec_()
                if reply.validation: 
                    try: 
                        job.initiateint(processor=reply.result[0])
                    except:
                        creationsuccess = False
                else:
                    creationsuccess = False

            if creationsuccess:
                try:
                    self.processor = job.intstack.processor
                    self.processingmode = 'intstack'
                    self.processingapproach = None
                except:
                        self.messageerror('Error during the intstack job creation')

        if creationsuccess == False:
            self.messageerror('Error during the creation of the processing job. Please see the log.')
        else: 
            ez.save(job,self.curEZInSARjob,verbose=False)
            self.updateTextEditverbosefrommsg(logcallbacks.updatelog(job.log))
            self.barjob.update(job)
            self.processingupdatemenu()
            self.messagesuccess('Mode: %s activated' % (self.processingmode))

    def processingupdatemenu(self):
        """Update the processing menu"""
        self.processMenuprocMenu.clear()
        self.processMenuapprMenu.clear()

        if self.processingmode == 'coregistration':
            self.processMenumodeMenuCoregistration.setChecked(True)
            self.processMenumodeMenuIfgstack.setChecked(False)
            self.processMenumodeMenuTSprocessing.setChecked(False)
            self.processMenumodeMenuIntstack.setChecked(False)
            self.processMenurunMenu.setEnabled(True)
            self.processMenuparaMenu.setEnabled(True)

        elif self.processingmode == 'ifgstack':
            self.processMenumodeMenuCoregistration.setChecked(False)
            self.processMenumodeMenuIfgstack.setChecked(True)
            self.processMenumodeMenuTSprocessing.setChecked(False)
            self.processMenumodeMenuIntstack.setChecked(False)
            self.processMenurunMenu.setEnabled(True)
            self.processMenuparaMenu.setEnabled(True)

        elif self.processingmode == 'tsprocessing':
            self.processMenumodeMenuCoregistration.setChecked(False)
            self.processMenumodeMenuIfgstack.setChecked(False)
            self.processMenumodeMenuTSprocessing.setChecked(True)
            self.processMenumodeMenuIntstack.setChecked(False)
            self.processMenurunMenu.setEnabled(True)
            self.processMenuparaMenu.setEnabled(True)

        elif self.processingmode == 'intstack':
            self.processMenumodeMenuCoregistration.setChecked(False)
            self.processMenumodeMenuIfgstack.setChecked(False)
            self.processMenumodeMenuTSprocessing.setChecked(False)
            self.processMenumodeMenuIntstack.setChecked(True)
            self.processMenurunMenu.setEnabled(True)
            self.processMenuparaMenu.setEnabled(True)

        else: 
            self.processMenurunMenu.setEnabled(False)
            self.processMenuparaMenu.setEnabled(False)

        for proci in tools.listprocessor(self.processingmode):
            exec("self.processMenuprocMenu.addAction(self.processMenuprocMenu%s)" % (proci.lower()))
            if proci.lower() == self.processor: 
                exec("self.processMenuprocMenu%s.setChecked(True)" % (proci.lower()))
            else:
                exec("self.processMenuprocMenu%s.setChecked(False)" % (proci.lower()))
        
        if self.processingmode == 'tsprocessing':
            for appri in tools.listapproach(self.processor):
                exec("self.processMenuapprMenu.addAction(self.processMenuapprMenu%s)" % (appri.lower()))
                if appri.lower() == self.processingapproach: 
                    exec("self.processMenuapprMenu%s.setChecked(True)" % (appri.lower()))
                else:
                    exec("self.processMenuapprMenu%s.setChecked(False)" % (appri.lower()))            

    def updateprocessor(self):
        reply = QMessageBox.warning(self, "EZ-InSAR Warning",
                'A change of the processor will cause a re-creation of the processing job. Are you sure',
                QMessageBox.Cancel | QMessageBox.Ok)
        
        if reply == QMessageBox.Ok:
            self.processor = self.sender().text().lower()
            job = ez.load(self.curEZInSARjob,verbose=False)
            if self.processingmode == 'coregistration':
                job.coregistration = None
                job.initiatecoreg(processor=self.processor)
            elif self.processingmode == 'ifgstack':
                job.ifgstack = None
                job.initiateifg(processor=self.processor)
            elif self.processingmode == 'tsprocessing':
                job.tsprocessing = None
                job.initiatets(processor=self.processor,mode=self.processingapproach)
            elif self.processingmode == 'intstack':
                job.intstack = None
                job.initiateint(processor=self.processor)

            ez.save(job,self.curEZInSARjob,verbose=False)
            self.updateTextEditverbosefrommsg(logcallbacks.updatelog(job.log))
            self.barjob.update(job)
            self.processingupdatemenu()

            if not self.curwidget == None:
                self.curwidget.close()
                self.curwidget == None
                self.sender().setText('Modify')
                self.processparameter()

    def updateapproach(self):
        """Update the TS approach"""
        reply = QMessageBox.warning(self, "EZ-InSAR Warning",
                'A change of the approach will cause a re-creation of the processing job. Are you sure',
                QMessageBox.Cancel | QMessageBox.Ok)
        if reply == QMessageBox.Ok:
            if self.sender().text().lower() == 'Small-baselines':
                self.processingapproach = 'sbas'
            else: 
                self.processingapproach = 'ps'

            job = ez.load(self.curEZInSARjob,verbose=False)
            job.tsprocessing = None
            job.initiatets(processor=self.processor,mode=self.processingapproach)
            ez.save(job,self.curEZInSARjob,verbose=False)
            self.updateTextEditverbosefrommsg(logcallbacks.updatelog(job.log))
            self.barjob.update(job)
            self.processingupdatemenu()

    def processparameter(self):
        """Callback for processing parameters"""
        if self.sender().text() == 'Modify':
            if not self.curwidget == None:
                self.curwidget.close()
                self.curwidget = None
            self.curwidget = processParameterWidget.parameterWidget(self.curEZInSARjob,mode=self.processingmode,parent=self)
            self.mainlayout.addWidget(self.curwidget,0,0)
            self.curwidget.closing.connect(self.updatelog)

        elif self.sender().text() == 'Check':
            job = ez.load(self.curEZInSARjob,verbose=False)
            try: 
                exec("job.%s.check(verbose=False)" % (self.processingmode))
                self.messagesuccess('The parameters of the %s seem correct. Please see the log.' % (tools.mode2title(self.processingmode)))
            except:
                self.messagesuccess('Error during the verification of the %s. Please see the log.' % (tools.mode2title(self.processingmode)))
            self.updateTextEditverbosefrommsg(logcallbacks.updatelog(job.log))

        elif self.sender().text() == 'Import':
            job = ez.load(self.curEZInSARjob,verbose=False)

            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getOpenFileName(self,
                        "Select a .ei processing job file.",'',
                        "*.ei", options=options)
            if fileName: 
                jobtmp = ez.load(fileName,verbose=False)
                try: 
                    exec("job.%s = jobtmp" % (self.processingmode))
                    exec("job.%s.check(verbose=False)" % (self.processingmode))
                    self.messagesuccess('Processing job imported. Please see the log.')
                    ez.save(job,self.curEZInSARjob,verbose=False)
                except:
                    self.messagesuccess('Error during the import. Please see the log.')
                self.updateTextEditverbosefrommsg(logcallbacks.updatelog(job.log))
                jobtmp = None

        elif self.sender().text() == 'Export':
            job = ez.load(self.curEZInSARjob,verbose=False)
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(self,
                    "Select an EZ-InSAR job file",'',
                    "*.ei", options=options)
            if fileName:
                exec("ez.save(job.%s,fileName,verbose=False)" % (self.processingmode))
                self.messagesuccess('Processing job exported. Please see the log.')

        elif self.sender().text() == 'Reset':
            job = ez.load(self.curEZInSARjob,verbose=False)
            exec('job.%s = None' % (self.processingmode))
            ez.save(job,self.curEZInSARjob,verbose=False)
            if self.processingmode == 'coregistration': 
                self.sender().setText('Coregistration')
            elif self.processingmode == 'ifgstack':
                self.sender().setText('Interferometric stack')
            elif self.processingmode == 'tsprocessing': 
                self.sender().setText('Time-serie analysis')
            elif self.processingmode == 'intstack':
                self.sender().setText('Intensity stack')
            self.processingcheck()
            self.updateTextEditverbosefrommsg(logcallbacks.updatelog(job.log))
            self.barjob.update(job)
            self.sender().setText('Reset')

    def runprocessing(self): 
        reply = processRunDialog.runDial(self.curEZInSARjob, mode = self.processingmode, parent=self)
        reply.exec_()

    ## Dummy callback
    def dummycallback(self):
        print('test')

    ## Open the EZ-InSAR settings
    def settings(self):
        """Open the settings"""
        reply = configDial.configDial(parent=self)
        reply.exec_()

    ## About Widget
    def about(self):
        """Open the About window"""
        reply = aboutDial.aboutDiag()
        reply.exec_()

    ## Open the licenses
    def openlicense(self):
        reply = licenseDial.licenseDial(force=True)
        reply.exec_()
    
    ## Docs 
    def docs(self):
        """Open the documentation"""
        docslink = None
        for mi in __EZInSARoptionalmodule__: 
            if mi.lower() in self.sender().text().lower():
               docslink = mi.lower()
        if docslink == None:
            docslink = 'ezinsar'
        if docslink == 'ezinsar':
            exec('from ezinsar import __file__ as tmpfile')
            tmp = eval("tmpfile.replace('src%sezinsar%s__init__.py','')" % (os.sep,os.sep)) 
        else:
            exec('from ezinsar%smodule import __file__ as tmpfile' % (docslink.lower()))   
            tmp = eval("tmpfile.replace('src%sezinsar%smodule%s__init__.py','')" % (os.sep,docslink.lower(),os.sep))   
        url = 'file:'+tmp+'docs'+os.sep+'build'+os.sep+'html'+os.sep+'index.html'  
        webbrowser.open_new_tab(url.replace(os.sep,'/'))

    ## Other websites
    def openlinkothers(self):
        """Open other useful websites"""
        url = None
        for linktype in list(__usefullinks__.keys()):
            for link in list(__usefullinks__[linktype].keys()):
                if self.sender().text() == link: 
                    url = __usefullinks__[linktype][link]
        webbrowser.open_new_tab(url)

    ####################################################
    ## High-level callbacks
    def updateTextEditcpuram(self):
        """Return of CPU/RAM info"""
        value = self.cpurammonitor.verticalScrollBar().value()
        self.cpurammonitor.setText(self.thread.TextInfo)
        self.cpurammonitor.verticalScrollBar().setValue(value)

    def coloriselog(self,msg):
        """Colorise the log"""
        newtext=[]
        msg = msg.split('\n')
        
        checkwarning = False
        checkerror = False
        for idx, msgi in enumerate(msg):
            try:
                datetime.datetime.strptime(msgi[0:23].replace(',','.'),"%Y-%m-%d %H:%M:%S.%f")
                datedetect = True
            except:
                datedetect = False
            
            if datedetect:
                if ('- WARNING -' in msgi):
                    checkwarning = True
                    checkerror = False
                elif ('- ERROR -' in msgi):
                    checkerror = True
                    checkwarning = False
                else:
                    checkerror = False
                    checkwarning = False

            if checkwarning:               
                newtext.append('<span style="color:#FF7800"><br>%s</span>' % (msgi))
            elif checkerror:
                newtext.append('<span style="color:#A40000"><br>%s</span>' % (msgi))
            else:
                newtext.append('<span style=""><br>%s</span>' % (msgi))

        newtext = '\n'.join(newtext)
        return(newtext)
    
    def updateprogressbar(self,value):
        """Update the processing bar"""
        self.progressbar.setValue(int(value*100))

    def updateTextEditverbose(self):
        """Open the verbose text"""
        v1 = self.VerboseWidget.verticalScrollBar().value() 
        v2 = self.VerboseWidget.verticalScrollBar().maximum()
        if v1 == 0:
            v1 = 1
        if v2 == 0:
            v2 = 1
        if v1/v2 > 0.95:
            self.VerboseWidget.setText(self.coloriselog(self.workerlog.TextInfo))
            self.VerboseWidget.verticalScrollBar().setValue(self.VerboseWidget.verticalScrollBar().maximum())
        else:
            self.VerboseWidget.setText(self.workerlog.TextInfo)
            v3 = self.VerboseWidget.verticalScrollBar().maximum()
            self.VerboseWidget.verticalScrollBar().setValue(int((v1/v3)*v3))

    def updateTextEditverbosefrommsg(self,msg):
        """Update the verbose text based on an unique message"""
        v1 = self.VerboseWidget.verticalScrollBar().value() 
        v2 = self.VerboseWidget.verticalScrollBar().maximum()
        if v1 == 0:
            v1 = 1
        if v2 == 0:
            v2 = 1
        if v1/v2 > 0.95:
            self.VerboseWidget.setText(self.coloriselog(msg))
            self.VerboseWidget.verticalScrollBar().setValue(self.VerboseWidget.verticalScrollBar().maximum())
        else:
            self.VerboseWidget.setText(self.coloriselog(msg))
            v3 = self.VerboseWidget.verticalScrollBar().maximum()
            self.VerboseWidget.verticalScrollBar().setValue(int((v1/v3)*v3))

    def updatelog(self):
        """Update the log"""
        job = ez.load(self.curEZInSARjob,verbose=False,modelog=False)
        self.barjob.update(job)
        self.updateTextEditverbosefrommsg(logcallbacks.updatelog(job.log))
        job = None 

    def stopcurrentworker(self):
        """Destroy the worker"""
        if not self.curwidget == None:
            self.curwidget.setEnabled(True)
        self.qtCancel.setEnabled(False)
        self.dockprogressbar.hide()
        time.sleep(1)
        self.workerprocess = None
        time.sleep(0.5)
        self.updatelog()

    def forcestopthread(self):
        """Force the worker destruction"""
        with open(self.job.log,'a') as flog:
            flog.write('EZ-InSAR KEY: STOP\n')
        self.stopcurrentworker()
        time.sleep(1)

    ###########################################################################################
    ## Callbacks for the Graphicak User Interface
    ###########################################################################################

    ###########################################################################################
    ## Create the menu actions
    def createActions(self):
        """Create the menus"""

        ## File Actions  
        self.newAct = QAction("New", self,
                shortcut=QKeySequence.New, 
                statusTip="Create a new EZ-InSAR job file",
                triggered=self.newFile)
        self.openAct = QAction("Open...",
                self, shortcut=QKeySequence.Open,
                statusTip="Open a EZ-InSAR job file", triggered=self.open)
        # self.saveAct = QAction("Save...", self,
        #         shortcut=QKeySequence.Save,
        #         statusTip="Save the EZ-InSAR job",
        #         triggered=self.save,
        #         enabled=False)
        self.saveAsAct = QAction("Export the EZ-InSAR job...", self,
                shortcut=QKeySequence.SaveAs,
                statusTip="Export the EZ-InSAR job under a new name",
                triggered=self.saveAs,
                enabled=False)
        self.exitAct = QAction("Exit", self, shortcut="Ctrl+Q",
                statusTip="Exit EZ-InSAR ", triggered=self.close)
        self.aboutAct = QAction("About", self,
                statusTip="Show the EZ-InSAR's About box",
                triggered=self.about)
    
    def createMenus(self):
        ############################################
        ## File Menu
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        # self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()

        # Job parameters

        self.fileMenujobpara = QAction("Parameters", self,
                                statusTip="Change EZ-InSAR job parameters",
                                triggered=self.jobparameters,
                                enabled=False)
        self.fileMenu.addAction(self.fileMenujobpara)
        
        self.fileMenujobdir = self.fileMenu.addMenu("&Directories")
        self.fileMenujobdir.setEnabled(False)

        self.fileMenujobdir.addAction(QAction("Change", self,
                                        statusTip="Change directory/file path(s) used by the EZ-InSAR job",
                                        triggered=self.jobdirectory))
        self.fileMenujobdir.addAction(QAction("Create", self,
                                        statusTip="Create directory/file path(s) used by the EZ-InSAR job",
                                        triggered=self.jobdirectorycreate))
        self.fileMenu.addSeparator()

        # Region of Interest
        self.fileMenujobroi = QAction("Region of Interest", self,
                            statusTip="Change the Region of Interest",
                            triggered=self.roicallback,
                            enabled=False)
        self.fileMenu.addAction(self.fileMenujobroi)  
        self.fileMenu.addSeparator()

        # Log 
        self.fileMenujobroilog = QAction("Log", self,
                                statusTip="Open the log file",
                                triggered=self.logcallback,
                                enabled=False)
        self.fileMenu.addAction(self.fileMenujobroilog) 
        
        # Export a report
        # self.fileMenu.addSeparator()
        # self.fileMenu.addAction(QAction("Export a report", self,
        #                                 statusTip="",
        #                                 triggered=self.dummycallback))   
        self.fileMenu.addSeparator()

        # Exit button 
        self.fileMenu.addAction(self.exitAct)

        self.menuBar().addSeparator()

        ############################################
        ## SAR imagery menu
        self.SARMenu = self.menuBar().addMenu("&SAR Imagery")
        self.SARMenu.setEnabled(False)

        self.SARMenu.addAction(QAction("Parameters", self,
                                        statusTip="Change the satellite parameters (i.e., sensors, tracks, etc.)",
                                        triggered=self.satcallback))
        
        self.SARMenuSLClistMenu = self.SARMenu.addMenu("&Single-look-complex list")
        self.SARMenuSLClistMenu.addAction(QAction("Open the table", self,
                                        statusTip="Open the table for the current SLC list",
                                        triggered=self.openSLClist)) 
        
        self.SARMenuSLClistMenucreateMenu = self.SARMenuSLClistMenu.addMenu("&Retrieve")
        self.SARMenuSLClistMenucreateMenu.addAction(QAction("Based on online imagery", self,
                                        statusTip="The SLC will be created/updated based the online files.",
                                        triggered=self.SLClistretrievecallback))   
        self.SARMenuSLClistMenucreateMenu.addAction(QAction("Based on local imagery", self,
                                        statusTip="The SLC will be created/updated based the stored files.",
                                        triggered=self.SLClistretrievecallback))  
        self.SARMenuSLClistMenucreateMenu.addAction(QAction("Based on an EZ-InSAR SLC list", self,
                                        statusTip="The SLC will be created/updated based the EZ-InSAR SLC list file.",
                                        triggered=self.SLClistretrievecallback)) 
        
        self.SARMenuSLClistMenu.addAction(QAction("Check the SLC list", self,
                                        statusTip="Check the SLC list",
                                        triggered=self.checkSLClist)) 
        
        self.SARMenuSLClistMenu.addAction(QAction("Display SLC extents", self,
                                        statusTip="Display a map with the SLC extents",
                                        triggered=self.openSLCmap))
        
        self.SARMenuExportMenu = self.SARMenuSLClistMenu.addMenu("&Export")
        self.SARMenuExportMenu.addAction(QAction("To a .csv file", self,
                                        statusTip="Export a SLC list to a .csv file",
                                        triggered=self.exportSLClist)) 
        self.SARMenuExportMenu.addAction(QAction("To a .kmz file", self,
                                        statusTip="Export a SLC list to a .kmz file",
                                        triggered=self.exportSLClist)) 
          
        self.SARMenu.addAction(QAction("Downloader", self,
                                        statusTip="Open the downloader",
                                        triggered=self.SLCdownloader)) 
  
        self.SARMenutoolsMenu = self.SARMenu.addMenu("&Tools")
        self.SARMenutoolsMenuS1Menu = self.SARMenutoolsMenu.addMenu("Sentinel-1")
        self.SARMenutoolsMenuS1Menu.addAction(QAction("IW Track/Orbit detection", self,
                                        statusTip="Offer the possibility to automatically detect the S1-IW track(s) and relative orbit(s) based on the Region of Interest",
                                        triggered=self.S1trackcallback))   
        self.SARMenutoolsMenuS1Menu.addAction(QAction("ASF Baseline computation", self,
                                        statusTip="Download the S1-IW perpendicular baselines from ASF.",
                                        triggered=self.S1ASFBaselines)) 

        ############################################
        ## DEM menu
        self.demMenu = self.menuBar().addMenu("&DEM")  
        self.demMenu.setEnabled(False)
        self.demMenu.addAction(QAction("Import", self,
                                        statusTip="",
                                        triggered=self.DEMcallback)) 
        # self.demMenu.addAction(QAction("Display", self,
        #                                 statusTip="",
        #                                 triggered=self.DEMcallback)) 
        
        ############################################
        ## Processing 
        self.processMenu = self.menuBar().addMenu("&Processing")
        self.processMenu.setEnabled(False)

        self.processMenumodeMenu = self.processMenu.addMenu("&Mode")
        self.processMenumodeMenuCoregistration = QAction("Coregistration", self,
                                                statusTip="Select the coregistration processing",
                                                checkable=True,
                                                triggered=self.processingcheck)
        
        self.processMenumodeMenuIfgstack = QAction("Interferometric stack", self,
                                                statusTip="Select the interferometric-stack processing",
                                                checkable=True,
                                                triggered=self.processingcheck)

        self.processMenumodeMenuTSprocessing = QAction("Time-serie analysis", self,
                                                statusTip="Select the time-series analysis processing",
                                                checkable=True,
                                                triggered=self.processingcheck)
        
        self.processMenumodeMenuIntstack = QAction("Intensity stack", self,
                                                statusTip="Select the intensity-stack processing",
                                                checkable=True,
                                                triggered=self.processingcheck)

        self.processMenumodeMenu.addAction(self.processMenumodeMenuCoregistration) 
        self.processMenumodeMenu.addAction(self.processMenumodeMenuIfgstack) 
        self.processMenumodeMenu.addAction(self.processMenumodeMenuTSprocessing)
        self.processMenumodeMenu.addAction(self.processMenumodeMenuIntstack)  

        self.processMenuprocMenu = self.processMenu.addMenu("&Processor")

        self.processMenuprocMenugamma = QAction("GAMMA", self,
                                        statusTip="Select the GAMMA processor",
                                        checkable=True,
                                        triggered=self.updateprocessor)
        self.processMenuprocMenudoris = QAction("Doris", self,
                                       statusTip="Select the Doris processor",
                                        checkable=True,
                                        triggered=self.updateprocessor)
        self.processMenuprocMenuisce2 = QAction("ISCE2", self,
                                        statusTip="Select the ISCE-2 processor",
                                        checkable=True,
                                        triggered=self.updateprocessor)
        self.processMenuprocMenusnap = QAction("SNAP", self,
                                        statusTip="Select the SNAP processor",
                                        checkable=True,
                                        triggered=self.updateprocessor)
        self.processMenuprocMenustamps = QAction("StaMPS", self,
                                        statusTip="Select the StaMPS processor",
                                        checkable=True,
                                        triggered=self.updateprocessor)
        self.processMenuprocMenumintpy = QAction("MintPy", self,
                                        statusTip="Select the MintPy processor",
                                        checkable=True,
                                        triggered=self.updateprocessor)
        self.processMenuprocMenumiaplpy = QAction("Miaplpy", self,
                                        statusTip="Select the Miaplpy processor",
                                        checkable=True,
                                        triggered=self.updateprocessor)
        self.processMenuprocMenusarvey = QAction("SARvey", self,
                                        statusTip="Select the SARvey processor",
                                        checkable=True,
                                        triggered=self.updateprocessor)

        self.processMenuapprMenu = self.processMenu.addMenu("&Approach")

        self.processMenuapprMenusbas = QAction("Small-baselines", self,
                                        statusTip="Select the Small-Baselines Subset Approach",
                                        checkable=True)
        
        self.processMenuapprMenups = QAction("Persistent Scatterer", self,
                                        statusTip="Select the Persistent-Scatterer Approach",
                                        checkable=True)
        
     
        self.processMenuparaMenu = self.processMenu.addMenu("&Parameters") 
        self.processMenuparaMenu.setEnabled(False)

        self.processMenuparaMenu.addAction(QAction("Modify", self,
                                        statusTip="Modify the processing parameters",
                                        triggered=self.processparameter))
        self.processMenuparaMenu.addAction(QAction("Check", self,
                                        statusTip="Check the processing parameters",
                                        triggered=self.processparameter))
        self.processMenuparaMenu.addAction(QAction("Import", self,
                                        statusTip="Import an EZ-InSAR processing job",
                                        triggered=self.processparameter))
        self.processMenuparaMenu.addAction(QAction("Export", self,
                                        statusTip="Export an EZ-InSAR processing job",
                                        triggered=self.processparameter))
        self.processMenuparaMenu.addAction(QAction("Reset", self,
                                        statusTip="Reset an EZ-InSAR processing job",
                                        triggered=self.processparameter))
        # self.processMenuparaMenu.addAction(QAction("Delete the processing directory", self,
        #                                 statusTip="",
        #                                 triggered=self.dummycallback))

        self.processMenurunMenu = QAction("Run", self,
                                    statusTip="Run the SAR/InSAR processing",
                                    triggered=self.runprocessing)
        self.processMenurunMenu.setEnabled(False)
        self.processMenu.addAction(self.processMenurunMenu)

        self.toolMenu = self.menuBar().addMenu("Tools")
        
        self.viewMenu = self.menuBar().addMenu("&View")
        self.menuBar().addSeparator()

        ## Help menu
        self.helpMenu = self.menuBar().addMenu("&Help")
        
        self.helpMenudocsMenu = self.helpMenu.addMenu("&Open the documentations")
        self.helpMenudocsMenu.addAction(QAction("&EZ-InSAR", self,
                                        statusTip="Open the EZ-InSAR documentation",
                                        triggered=self.docs))   
        for mi in __EZInSARoptionalmodule__: 
            try: 
                if mi == 'gamma':
                    if mi.lower() == 'gamma':
                        if not os.environ['ezinsargamma'] in ['True','true',True,1]:
                            raise ValueError('ERROR')
                exec('from ezinsar%smodule import __file__ as tmpfile' % (mi.lower()))
                exec('from ezinsar%smodule import __namePackage__ as tmp2' % (mi.lower()))
                mi = eval('tmp2')
                self.helpMenudocsMenu.addAction(QAction("%s" % (mi), self,
                                            statusTip=" Opne the documentation for %s" % (mi),
                                            triggered=self.docs))  
            except: 
                a = 'dummy'

        self.helpMenuOthers = self.helpMenu.addMenu("Useful links")

        for linktype in list(__usefullinks__.keys()):
            exec('self.helpMenuOthers_%s = self.helpMenuOthers.addMenu(linktype)' % (linktype))
            for link in list(__usefullinks__[linktype].keys()):
                exec('self.helpMenuOthers_%s.addAction(QAction("%s", self,triggered=self.openlinkothers))' % (linktype,link))

        self.helpMenu.addSeparator()
        self.helpMenu.addAction(QAction("Settings", self,
                                        statusTip="Open the EZ-InSAR settings",
                                        triggered=self.settings))
        
        self.helpMenu.addSeparator()
        self.helpMenu.addAction(QAction("Licenses", self,
                                        statusTip="Open the license information",
                                        triggered=self.openlicense))

        self.helpMenu.addSeparator()
        self.helpMenu.addAction(self.aboutAct)

    ####################################################
    ## Create the status bar
    def createStatusBar(self):
        """Create the statuts bar"""
        self.statusBar().showMessage("Please create or open an EZ-InSAR job")

    ####################################################
    ## Create the docks
    def createDockWindows(self):
        """Create the docks"""
        dock = QDockWidget("EZ-InSAR job status", self)
        self.barjob = jobstatusBar.barjobinfowidget()
        dock.setWidget(self.barjob)
        self.addDockWidget(Qt.TopDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        dockverbose = QDockWidget("Live Log", self)
        self.VerboseWidget = QTextEdit(dockverbose)
        self.VerboseWidget.setReadOnly(True)
        self.VerboseWidget.setText('Please create or open an EZ-InSAR job')
        dockverbose.setWidget(self.VerboseWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, dockverbose)
        self.viewMenu.addAction(dockverbose.toggleViewAction())

        self.dockdata = QDockWidget("Dataset(s)", self) 
        self.dockdata.show()
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockdata)
        self.viewMenu.addAction(self.dockdata.toggleViewAction())

        dockplugins = QDockWidget("Tool Panel", self) 
        dockplugins.hide()
        dockplugins.setWidget(pluginsWidget.plugins(parent=self))
        self.addDockWidget(Qt.LeftDockWidgetArea, dockplugins)
        actiontools = dockplugins.toggleViewAction()
        actiontools.setShortcut("Ctrl+T")
        self.toolMenu.addAction(actiontools)

        dock = QDockWidget("System Monitor", self)
        dock.hide()
        self.cpurammonitor = QTextEdit(dock)
        self.cpurammonitor.setReadOnly(True)
        dock.setWidget(self.cpurammonitor)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        self.dockprogressbar = QDockWidget("Progress", self)
        self.dockprogressbar.hide()
        layout = QGridLayout()
        self.progressbar = QProgressBar()
        self.progressbar.setValue(100)
        self.qtCancel = QPushButton("Cancel", self.dockprogressbar)
        self.qtCancel.setEnabled(False)
        self.qtCancel.clicked.connect(self.forcestopthread)
        layout.addWidget(self.progressbar,0,3,1,7)
        layout.addWidget(self.qtCancel,0,10,1,1)
        self.dockprogressbarwidget = QWidget()
        self.dockprogressbar.setWidget(self.dockprogressbarwidget)
        self.dockprogressbarwidget.setLayout(layout)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dockprogressbar)
        self.viewMenu.addAction(self.dockprogressbar.toggleViewAction())

        self.tabifyDockWidget(self.dockdata,dockverbose)

    def messageerror(self,msg):
        """Send an error message"""
        reply = QMessageBox.critical(self, "EZ-InSAR Error",
                msg,
                QMessageBox.Ok)
        
    def messagesuccess(self,msg):
        """Send an information message"""
        reply = QMessageBox.information(self, "EZ-InSAR Information",
                msg,
                QMessageBox.Ok)
        
    def closeEvent(self, event):
        ret = QMessageBox.warning(self, "Quit?",
                "Are you sure to quit EZ-InSAR?",
                QMessageBox.Yes | QMessageBox.Cancel)
        
        if ret == QMessageBox.Yes:
            if os.path.isfile(__cachedir__+os.sep+'tmp.bmp'):
                os.remove(__cachedir__+os.sep+'tmp.bmp')
            if os.path.isfile(__cachedir__+os.sep+'maptmp.html'):
                os.remove(__cachedir__+os.sep+'maptmp.html')
            if os.path.isfile(__cachedir__+os.sep+'figuretmp.html'):
                os.remove(__cachedir__+os.sep+'figuretmp.html')
            usermessage.ezprint('##########################\nClose EZ-InSAR Desktop Application\n##########################\n',None,True)
            event.accept()
        else: 
            event.ignore()

##########################################################################################
## Running 
##########################################################################################
if __name__ == '__main__':

    import sys

    usermessage.openingmsg(__file__,__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Welcome to EZ-InSAR (Desktop Application)',None,True,lockfree=True)

    sys.argv[0] = 'EZ-InSAR'
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(QFileInfo(__file__).absolutePath() + '%simages%sEZ_InSAR_logo_desktop_whiteback.svg' % (os.sep,os.sep)))
    app.setApplicationName('EZ-InSAR')

    if tools.checklicense():

        mainWin = MainWindow()
        mainWin.setGeometry(0, 0, 
                            app.desktop().screenGeometry().width(),
                            app.desktop().screenGeometry().height())
    

        from ezinsardesktopmodule.config import openingDial
        openWin = openingDial.openingDial()
        openWin.run()

        mainWin.show()
        sys.exit(app.exec_())
    else:
        sys.exit()