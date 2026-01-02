#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a window for parameters of an EZ-InSAR job

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 0.1.0: Initial version, Feb. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a window for parameters of an EZ-InSAR job

usage: 
    ezinsardesktop_parameter -f <str> [options]

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
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QFileDialog, QWidget, QGroupBox

import os, sys
from docopt import docopt

from ezinsar import constants, usermessage
import ezinsar.job as ez
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsardesktopmodule.tools.docsWidget import DocsDialog

###########################################################################################
## Class 
###########################################################################################
class jobparameter(QWidget):
    """Class definition"""
    closing = pyqtSignal(bool)

    def __init__(self, jobfile, parent=None):
        super(jobparameter, self).__init__(parent)

        self.pathjobfile = jobfile
        self.setWindowTitle("EZ-InSAR - Job Parameters")
        self.resize(750, 500)
        self.setStyleSheet(__theme__)

        self.success = False
        self.false = False

        job = ez.load(self.pathjobfile,verbose=False)
        
        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p style="font-size:20px"><b>Job Parameters</b></p>')
        btQuit = QPushButton("Close", self)
        btQuit.clicked.connect(self.closemaybe)

        jobPathLabel = QLabel("<p><b>EZ-InSAR-job file:</b></p>")
        jobPathLabel.setToolTip("""
                                <p>The path of the EZ-InSAR job file.</p>
                                <p>It cannot be changed</p>     
                                """)
        self.jobPathLineEdit = QLineEdit()
        self.jobPathLineEdit.setReadOnly(True)
        self.jobPathLineEdit.setEnabled(False)
        self.jobPathLineEdit.setText(self.pathjobfile)

        jobTitleLabel = QLabel("<p><b>EZ-InSAR-job title:</b></p>")
        jobTitleLabel.setToolTip("""
                            <p>The title of the EZ-InSAR will be used in the EZ-InSAR report.</p>
                            <p>It is not mandatory but very useful.</p>     
                            """)
        self.jobTitleLineEdit = QLineEdit()
        self.jobTitleLineEdit.setText(job.nameJob)

        jobUserLabel = QLabel("<p><b>Producer/User:</b></p>")
        jobUserLabel.setToolTip("""
                                <p>The producer/user name will be used to track the origin of results: i.e., in the EZ-InSAR report.</p>
                                """)
        self.jobUserLineEdit = QLineEdit()
        self.jobUserLineEdit.setText(job.user)

        jobLogLabel = QLabel("<p><b>Log File:</b></p>")
        jobLogLabel.setToolTip("""
                            <p>The EZ-InSAR log file is required for the EZ-InSAR Desktop application.</p>
                            """)
        self.jobLogLineEdit = QLineEdit()
        self.jobLogLineEdit.setText(job.log)
        self.jobLogLineEdit.setReadOnly(True)
        jobLogBt = QPushButton("Select")
        jobLogBt.setToolTip('Select the EZ-InSAR log file')
        jobLogBt.clicked.connect(self.setLogFileName)

        btHelp = QPushButton("Help", self)
        btHelp.clicked.connect(self.openhelp)

        btSave = QPushButton("Save", self)
        btSave.clicked.connect(self.save)
        
        layout = QGridLayout()
        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 8, Qt.AlignCenter)
        layout.addWidget(btQuit, 0, 9, 1, 1)

        grp = QGroupBox()
        grpLayout = QGridLayout()
        grpLayout.addWidget(jobPathLabel, 0, 0, 1, 1)
        grpLayout.addWidget(self.jobPathLineEdit, 0, 1, 1, 8)
        grpLayout.addWidget(jobTitleLabel, 1, 0, 1, 1)
        grpLayout.addWidget(self.jobTitleLineEdit, 1, 1, 1, 8)
        grpLayout.addWidget(jobUserLabel, 2, 0, 1, 1)
        grpLayout.addWidget(self.jobUserLineEdit, 2, 1, 1, 8)
        grpLayout.addWidget(jobLogLabel, 3, 0, 1, 1)
        grpLayout.addWidget(self.jobLogLineEdit, 3, 1, 1, 8)
        grpLayout.addWidget(jobLogBt, 3, 9, 1, 1)
        grp.setLayout(grpLayout)

        layout.addWidget(grp, 1, 0, 1, 10)
        layout.addWidget(btHelp, 2, 0, 1, 1)
        layout.addWidget(btSave, 2, 9, 1, 1)

        self.setLayout(layout)

    ###########################################################################################
    ## Callbacks
    def openhelp(self):
        helpdial = DocsDialog('applications%sjob%sjobparameters.html#for-the-job-parameters' % (os.sep,os.sep))
        helpdial.show()
        helpdial.exec()
    
    def setLogFileName(self):    
        """Define the log file"""
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,
                "Select a Log file", self.jobLogLineEdit.text(),
                "*.log", options=options)
        if fileName:
            self.jobLogLineEdit.setText(fileName)

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
        """Save the EZ-InSAR jog"""
        job = ez.load(self.pathjobfile,verbose=False)
        job.nameJob = self.jobTitleLineEdit.text()
        job.user = self.jobUserLineEdit.text()
        job.log = self.jobLogLineEdit.text()
        job.check(verbose=False)
        ez.save(job,self.pathjobfile,verbose=False)
        reply = QMessageBox.information(self, "EZ-InSAR Information",
            'The new job parameters have been saved.',
            QMessageBox.Ok)

###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not os.path.isfile(args['--file']):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No file',None))

    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the Job parameter tool from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        widget = jobparameter(os.path.abspath(args['--file']))
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()
