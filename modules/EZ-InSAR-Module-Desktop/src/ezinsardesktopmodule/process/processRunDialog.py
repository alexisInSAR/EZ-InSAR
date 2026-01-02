#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a dialog to run an EZ-InSAR processing

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Mar. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a dialog to run an EZ-InSAR processing

usage: 
    ezinsardesktop_run -f <str> -m <str> [options]

Arguments:
    -f, --file <str>        EZ-InSAR job file
    -m, --mode <str>        Processing mode. Can be coregistration, ifgstack, tsprocessing, intstack

Other-options:
    -h, --help
"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QDialog, QPushButton, QGroupBox, QMessageBox, QCheckBox

import os, sys, time
import numpy as np

from docopt import docopt

import ezinsar.job as ez
from ezinsar import usermessage, constants
from ezinsardesktopmodule import __file__ as __root_module__
from ezinsardesktopmodule import __versionPackage__
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule.log import logWorker
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__, __docker_running__
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsardesktopmodule.tools.docsWidget import DocsDialog

###########################################################################################
## EPSGcodeDial class
###########################################################################################
class Worker(QObject):
    """Worker class 

        Build the worker
    """
    textSignal = pyqtSignal(str)
    finished = pyqtSignal()
    intReady = pyqtSignal(int)
    error = pyqtSignal(str)
    success = pyqtSignal(str)
    
    def __init__(self, jobfile, mode, step, parent=None, verbose=False):
        super(Worker, self).__init__(parent)

        self.jobfile = jobfile
        self.TextInfo = ''
        self.running = True
        self.messageerror = ''
        self.messagesuccess = ''
        self.parent = parent 
        self.verbose = verbose   
        self.mode = mode
        self.step = step

        self.job = ez.load(jobfile,verbose=False)

    def run(self):
        try:
            for stepi in self.step: 
                exec("self.job.%s.run(step=stepi,verbose=True,docker=%s)" % (self.mode,__docker_running__))
                ez.save(self.job,self.jobfile,verbose=True)
                time.sleep(1)
        except:
            time.sleep(1)
            self.messageerror = 'Error during the %s' % (tools.mode2title(self.mode))
            self.error.emit(self.messageerror)
        
        if self.messageerror == '':
            self.messagesuccess = '%s completed' % (tools.mode2title(self.mode))
            self.success.emit(self.messagesuccess)

        self.running=False
        self.finished.emit()

class runDial(QDialog):
    """QDialog class 

        Build the dialog windows
    """
    def __init__(self, jobfile, parent=None, mode = 'coregistration'):
        super(runDial, self).__init__(parent)

        self.parent = parent
        self.validation = False
        self.result = [None, None]
        self.mode = mode
        self.jobfile = jobfile
        self.requiredstep = []
        self.workerprocess = None
        self.threadprocess = None

        self.setStyleSheet(__theme__)

        job = ez.load(self.jobfile,verbose=False)

        if eval('job.%s' % (self.mode)) == None:
            raise ValueError(usermessage.errormsg(__name__,__name__,__file__,constants.__copyright__,
                    'No processing job available.',None))
        
        mainLayout = QGridLayout()
        titleLabel = QLabel("<p style='font-size:20px'><b>Running for <i>%s</i></b></p>" % (tools.mode2title(self.mode)))
        mainLayout.addWidget(titleLabel, 0, 0, 1, 10, Qt.AlignCenter)

        msg1 = QLabel("<p><i>EZ-InSAR seems ready to run the processing job. Please  carefully read the following information before to run it.</i></p>")
        mainLayout.addWidget(msg1, 1, 0, 1, 10)

        grpinfo = QGroupBox('Processing information')
        grpinfolayout = QGridLayout()

        typeLabel = QLabel("<p><b>Processing type:</b></p>")
        type = QLabel("<p>%s</p>" % (self.mode))
        grpinfolayout.addWidget(typeLabel, 0, 0, 1, 1)
        grpinfolayout.addWidget(type, 0, 1, 1, 1)

        fileLabel = QLabel("<p><b>EZ-InSAR file:</b></p>")
        file = QLabel("<p>%s</p>" % (jobfile))
        grpinfolayout.addWidget(fileLabel, 1, 0, 1, 1)
        grpinfolayout.addWidget(file, 1, 1, 1, 1)

        logLabel = QLabel("<p><b>Logfile:</b></p>")
        log = QLabel("<p>%s</p>" % (job.log))
        grpinfolayout.addWidget(logLabel, 2, 0, 1, 1)
        grpinfolayout.addWidget(log, 2, 1, 1, 1)

        fileLabel = QLabel("<p><b>Title</b></p>")
        file = QLabel("<p>%s</p>" % (eval("job.%s.title" % (self.mode))))
        grpinfolayout.addWidget(fileLabel, 3, 0, 1, 1)
        grpinfolayout.addWidget(file, 3, 1, 1, 1)
        
        if __docker_running__:
            processorLabel = QLabel("<p><b>Processor (with Docker container):</b></p>")
        else: 
            processorLabel = QLabel("<p><b>Processor:</b></p>")
        processor = eval("QLabel('<p>%s</p>')" % (eval('job.%s.processor' % (self.mode))))
        grpinfolayout.addWidget(processorLabel, 4, 0, 1, 1)
        grpinfolayout.addWidget(processor, 4, 1, 1, 1)

        if self.mode == 'tsprocessing': 
            approachLabel = QLabel("<p><b>Approach:</b></p>")
            approach = eval("QLabel('<p>%s</p>')" % (eval('job.%s.mode' % (self.mode))))
            grpinfolayout.addWidget(approachLabel, 5, 0, 1, 1)
            grpinfolayout.addWidget(approach, 5, 1, 1, 1)

        tmp = eval("tools.checkprogress(job.%s)" % (self.mode))
        progressLabel = QLabel("<p><b>Progress:</b></p>")
        progress = QLabel("<p>%s step(s) of %s steps</p>" % (len(np.where(np.array(tmp)==True)[0]),len(tmp)))
        grpinfolayout.addWidget(progressLabel, 6, 0, 1, 1)
        grpinfolayout.addWidget(progress, 6, 1, 1, 1)

        grpinfo.setLayout(grpinfolayout)

        # Step checkbox
        grpstep = QGroupBox('Processing step(s):')
        grpsteplayout = QGridLayout()

        tmp = eval('job.%s' % (self.mode))

        self.steps = []
        self.updatestep = []

        for stepi in tools.processingstep(tmp):
            if not (stepi == 'email' or stepi == 'computer' or stepi == 'mintpyparameter' or stepi == 'plotoptions'): 
                if 'update' in stepi: 
                    self.updatestep.append(stepi)
                else: 
                    self.steps.append(stepi) 

        nl = int(np.fix(len(self.steps)+1)/2)
        h = 0
        for idx,stepi in enumerate(self.steps):
            if (idx)< nl: 
                nc = 0
            elif (idx) == nl:
                nc = 1
                h  = 0
        
            exec("self.step%s = QCheckBox('Step %s: %s')" % (stepi,idx+1,stepi))
            if eval('job.%s.%s["done"]["value"]' % (self.mode,stepi)): 
                exec("self.step%s.setChecked(False)"  % (stepi))
            else: 
                exec("self.step%s.setChecked(True)"  % (stepi))

            exec("grpsteplayout.addWidget(self.step%s, h, nc, 1, 1)"  % (stepi))
                  
            h = h + 1

        grpstep.setLayout(grpsteplayout)

        mainLayout.addWidget(grpinfo, 3, 0, 1, 10)
        mainLayout.addWidget(grpstep, 4, 0, 1, 10)

        
        if self.updatestep: 
            grpstepupdate = QGroupBox('Update processing:')
            grpstepupdatelayout = QGridLayout()

            exec("self.step%s = QCheckBox('Update the stack based on new images')" % (self.updatestep[0]))
            exec("self.step%s.setChecked(False)"  % (self.updatestep[0]))
            exec("self.step%s.clicked.connect(self.checkstepfromupdate)"  % (self.updatestep[0]))
            exec("grpstepupdatelayout.addWidget(self.step%s, 0, 0, 1, 1)"  % (self.updatestep[0]))
            
            grpstepupdate.setLayout(grpstepupdatelayout)
            mainLayout.addWidget(grpstepupdate, 5, 0, 1, 10)

        self.btOkay = QPushButton("Start the processing")
        self.btCancel = QPushButton("Cancel")

        self.btOkay.clicked.connect(self.valid)
        self.btCancel.clicked.connect(self.cancel)

        btHelp = QPushButton("Help", self)
        btHelp.clicked.connect(self.openhelp)

        mainLayout.addWidget(self.btOkay, 10, 5, 1, 5)
        mainLayout.addWidget(self.btCancel, 10, 0, 1, 5)
        mainLayout.addWidget(btHelp, 11, 0, 1, 1)

        self.setLayout(mainLayout)

        self.setWindowTitle("EZ-InSAR - Run")
    
    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def openhelp(self):
        helpdial = DocsDialog(['applications','processing','processrun'])
        helpdial.show()
        helpdial.exec()

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
        
    def stopcurrentworker(self):
        """Stop the current worker
        """
        self.workerprocess = None

    def valid(self):
        """Validation    
        """
        self.requiredstep = []
        if self.updatestep:
            if eval("self.step%s.isChecked()"  % (self.updatestep[0])): 
                self.requiredstep.append(self.updatestep[0])
                self.validation = True
            else:
                self.validation = False
        else: 
            self.validation = False

        if not self.validation:
            for idx,stepi in enumerate(self.steps):
                if eval("self.step%s.isChecked()"  % (stepi)):
                    self.requiredstep.append(stepi)

            if len(self.requiredstep) == 0:
                self.messageerror('No step(s) selected')
                self.validation = False
            else: 
                self.validation = True
        
        if self.validation:
            job = ez.load(self.jobfile,verbose=False)

            # Confirmation
            checkalready = False
            msg = "Please can you confirm the processing step(s)?"
            for stepi in self.requiredstep: 
                msg = msg + '\n\t%s' % (stepi)
                if eval('job.%s.%s["done"]["value"]' % (self.mode,stepi)):
                    checkalready = True
                    msg = msg + '(already performed)'

            if checkalready:
                msg = msg + '\n\nSome steps have been already computed. Please check the force mode if re-computing is required.'
            reply = QMessageBox.information(self, "Confirmation of the processing step(s)",
                msg,
                QMessageBox.Cancel | QMessageBox.Ok)
            if reply == QMessageBox.Ok:
                # Start the worker
                if self.parent == None:
                    if self.workerprocess == None:
                        self.workerprocess = Worker(self.jobfile,
                                            self.mode, 
                                            self.requiredstep,
                                            verbose=True)
                        self.threadprocess = QThread()
                        self.workerprocess.moveToThread(self.threadprocess)
                        self.threadprocess.started.connect(self.workerprocess.run)
                        self.workerprocess.finished.connect(self.threadprocess.quit)
                        self.workerprocess.error.connect(self.messageerror)
                        self.workerprocess.success.connect(self.messagesuccess)
                        self.workerprocess.finished.connect(self.stopcurrentworker)      
                        self.threadprocess.start()
                    else:
                        self.messageerror('The worker for SAR/InSAR processing is still running. Please stop it, if required')

                else:
                    self.accept()
                    job = ez.load(self.jobfile,verbose=False)
                    logfile = job.log
                    job = None

                    if self.parent.workerprocess == None:
                        self.parent.dockprogressbar.show()
                        self.parent.workerprocess = Worker(self.jobfile,
                                                    self.mode, 
                                                    self.requiredstep,
                                                    verbose=True)
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
                        self.messageerror('The worker for SAR/InSAR processing is still running. Please stop it, if required')

    def cancel(self):
        """Cancelation        
        """
        self.validation = False
        self.close()

    def checkstepfromupdate(self): 
        job = ez.load(self.jobfile,verbose=False)
        if self.updatestep:
            tmp = eval("tools.checkprogress(job.%s)" % (self.mode))
            if (len(np.where(np.array(tmp)==True)[0]) == len(tmp)): 
                for idx,stepi in enumerate(self.steps):
                    if eval("self.step%s.isChecked()"  % (self.updatestep[0])): 
                        exec("self.step%s.setChecked(False)"  % (stepi))
                    else: 
                        if eval('job.%s.%s["done"]["value"]' % (self.mode,stepi)): 
                            exec("self.step%s.setChecked(False)"  % (stepi))
                        else: 
                            exec("self.step%s.setChecked(True)"  % (stepi))
            else: 
                self.messageerror('The update processing requires to complete all processing steps. ')
                exec("self.step%s.setChecked(False)"  % (self.updatestep[0]))
        job = None

###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not os.path.isfile(args['--file']):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No file',None))
    
    if not args['--mode'] in ['coregistration', 'ifgstack', 'tsprocessing', 'intstack']:
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No correct mode',None))

    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open a dialog to run an EZ-InSAR processing from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        widget = runDial(os.path.abspath(args['--file']), mode = args['--mode'])
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()
        
if __name__=='__main__':
    main()
