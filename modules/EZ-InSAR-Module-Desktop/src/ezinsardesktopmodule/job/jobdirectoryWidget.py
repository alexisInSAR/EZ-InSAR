#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a window for directories of an EZ-InSAR job

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Feb. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a window for directories of an EZ-InSAR job

usage: 
    ezinsardesktop_directory -f <str> [options]

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
class jobdirectory(QWidget):
    """Class definition"""

    closing = pyqtSignal(bool)

    def __init__(self, jobfile, parent=None):
        super(jobdirectory, self).__init__(parent)

        self.pathjobfile = jobfile
        self.setWindowTitle("EZ-InSAR - Job Directories")
        self.resize(750, 500)
        self.setStyleSheet(__theme__)

        self.success = False
        self.false = False

        job = ez.load(self.pathjobfile,verbose=False)
        
        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p style="font-size:20px"><b>Job Directories</b></p>')
        btQuit = QPushButton("Close", self)
        btQuit.clicked.connect(self.closemaybe)

        pathWorkLabel = QLabel("<b>Path of the work directory:</b>")
        pathWorkLabel.setToolTip("""
                                <p>Define the directory where EZ-InSAR will store ALL working files.</p>
                                """)
        self.pathWorkLineEdit = QLineEdit()
        self.pathWorkLineEdit.setReadOnly(True)
        self.pathWorkLineEdit.setText(job.workdirectory)
        pathWorkBt = QPushButton("Select")
        pathWorkBt.setToolTip('Select the work directory')
        pathWorkBt.clicked.connect(self.setExistingDirectory)

        pathSLCLabel = QLabel("<b>Path of the SLC directory:</b>")
        pathSLCLabel.setToolTip("""
                                <p>Define the SLC-image directory.</p>
                                """)
        self.pathSLCLineEdit = QLineEdit()
        self.pathSLCLineEdit.setText(job.pathSLC)
        self.pathSLCLineEdit.setReadOnly(True)
        pathSLCBt = QPushButton("Select")
        pathSLCBt.setToolTip('Select the SLC directory')
        pathSLCBt.clicked.connect(self.setExistingDirectory)

        pathOrbitLabel = QLabel("<b>Path of the orbit directory:</b>")
        pathOrbitLabel.setToolTip("""
                                <p>Define the orbit-file directory. Only required for Sentinel-1 imagery.</p>
                                """)
        self.pathOrbitLineEdit = QLineEdit()
        self.pathOrbitLineEdit.setReadOnly(True)
        if not job.pathorbit == None:
            self.pathOrbitLineEdit.setText(job.pathorbit)
        else: 
            self.pathOrbitLineEdit.setText('None')
        pathOrbitBt = QPushButton("Select")
        pathOrbitBt.setToolTip('Select the orbit directory')
        pathOrbitBt.clicked.connect(self.setExistingDirectory)

        pathAuxLabel = QLabel("<b>Path of the aux directory:</b>")
        pathAuxLabel.setToolTip("""
                                <p>Define the aux-file directory. Can be required for Sentinel-1 imagery, however it seems that it is not longer required due to the new version of the IPF processor.<\p
                                """)
        self.pathAuxLineEdit = QLineEdit()
        self.pathAuxLineEdit.setReadOnly(True)
        if not job.pathaux == None:
            self.pathAuxLineEdit.setText(job.pathaux)
        else:
            self.pathAuxLineEdit.setText('None')
        pathAuxBt = QPushButton("Select")
        pathAuxBt.setToolTip('Select the aux directory')
        pathAuxBt.clicked.connect(self.setExistingDirectory)

        pathDEMLabel = QLabel("<b>Path of the DEM directory:</b>")
        pathDEMLabel.setToolTip("""
                                <p>Define the DEM directory</p>
                                """)
        self.pathDEMLineEdit = QLineEdit()
        self.pathDEMLineEdit.setReadOnly(True)
        if not job.pathaux == None:
            self.pathDEMLineEdit.setText(job.pathDEM)
        else:
            self.pathDEMLineEdit.setText('None')
        pathDEMBt = QPushButton("Select")
        pathDEMBt.setToolTip('Select the DEM directory')
        pathDEMBt.clicked.connect(self.setExistingDirectory)

        btSave = QPushButton("Save", self)
        btSave.clicked.connect(self.save)
        
        btHelp = QPushButton("Help", self)
        btHelp.clicked.connect(self.openhelp)

        layout = QGridLayout()
        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 8, Qt.AlignCenter)
        layout.addWidget(btQuit, 0, 9, 1, 1)

        grp = QGroupBox()
        grpLayout = QGridLayout()
        grpLayout.addWidget(pathWorkLabel, 0, 0, 1, 1)
        grpLayout.addWidget(self.pathWorkLineEdit, 0, 1, 1, 8)
        grpLayout.addWidget(pathWorkBt, 0, 9, 1, 1)
        grpLayout.addWidget(pathSLCLabel, 1, 0, 1, 1)
        grpLayout.addWidget(self.pathSLCLineEdit, 1, 1, 1, 8)
        grpLayout.addWidget(pathSLCBt, 1, 9, 1, 1)
        grpLayout.addWidget(pathOrbitLabel, 2, 0, 1, 1)
        grpLayout.addWidget(self.pathOrbitLineEdit, 2, 1, 1, 8)
        grpLayout.addWidget(pathOrbitBt, 2, 9, 1, 1)
        grpLayout.addWidget(pathAuxLabel, 3, 0, 1, 1)
        grpLayout.addWidget(self.pathAuxLineEdit, 3, 1, 1, 8)
        grpLayout.addWidget(pathAuxBt, 3, 9, 1, 1)
        grpLayout.addWidget(pathDEMLabel, 4, 0, 1, 1)
        grpLayout.addWidget(self.pathDEMLineEdit, 4, 1, 1, 8)
        grpLayout.addWidget(pathDEMBt, 4, 9, 1, 1)
        grp.setLayout(grpLayout)

        layout.addWidget(grp, 1, 0, 1, 10)
        layout.addWidget(btSave, 2, 9, 1, 1)
        layout.addWidget(btHelp, 2, 0, 1, 1)

        self.setLayout(layout)

    ###########################################################################################
    ## Callbacks
    def openhelp(self):
        helpdial = DocsDialog('applications%sjob%sjobparameters.html#for-the-job-directories' % (os.sep,os.sep))
        helpdial.show()
        helpdial.exec()

    def setExistingDirectory(self):
        """Define a directory"""
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        if 'work directory' in self.sender().toolTip():
            title = 'Please select the work directory'
        elif 'SLC directory' in self.sender().toolTip():
            title = 'Please select the SLC directory'
        elif 'orbit directory' in self.sender().toolTip():
            title = 'Please select the orbit directory'
        elif 'aux directory' in self.sender().toolTip():
            title = 'Please select the aux directory'
        elif 'DEM directory' in self.sender().toolTip():
            title = 'Please select the DEM directory'

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
        elif (directory) and ('DEM directory' in self.sender().toolTip()):
            self.pathDEMLineEdit.setText(directory)

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
        job.workdirectory = self.pathWorkLineEdit.text()
        job.pathSLC = self.pathSLCLineEdit.text()

        if self.pathOrbitLineEdit.text() == 'None':
            reply = QMessageBox.information(self, "EZ-InSAR Warning",
                'The Orbit directory will be replaced by %s' % (constants.__cachedir__),
                QMessageBox.Ok)
            self.pathOrbitLineEdit.setText(constants.__cachedir__)
        job.pathorbit = self.pathOrbitLineEdit.text()

        if self.pathAuxLineEdit.text() == 'None':
            reply = QMessageBox.information(self, "EZ-InSAR Warning",
                'The Aux. directory will be replaced by %s' % (constants.__cachedir__),
                QMessageBox.Ok)
            self.pathAuxLineEdit.setText(constants.__cachedir__)
        job.pathaux = self.pathAuxLineEdit.text()

        if self.pathDEMLineEdit.text() == 'None':
            reply = QMessageBox.information(self, "EZ-InSAR Warning",
                'The DEM directory will be replaced by %s' % (constants.__cachedir__),
                QMessageBox.Ok)
            self.pathDEMLineEdit.setText(constants.__cachedir__)
        job.pathDEM = self.pathDEMLineEdit.text()

        job.check(verbose=False)
        ez.save(job,self.pathjobfile,verbose=False)
        reply = QMessageBox.information(self, "EZ-InSAR Information",
            'The new job directories have been saved.',
            QMessageBox.Ok)

###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not os.path.isfile(args['--file']):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No file',None))
    
    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the Job directory tools from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        widget = jobdirectory(os.path.abspath(args['--file']))
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()
