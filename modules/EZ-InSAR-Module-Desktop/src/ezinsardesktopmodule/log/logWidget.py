#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a window for the EZ-InSAR log

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Feb. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a window for the EZ-InSAR log

usage: 
    ezinsardesktop_log -f <str> [options]

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
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QMessageBox, QPushButton, QFileDialog, QWidget, QTextEdit

import os, sys, shutil
from docopt import docopt

from ezinsar import constants, usermessage
import ezinsar.job as ez
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__

###########################################################################################
## Class for the Wizard
###########################################################################################
class logwidget(QWidget):
    """Class definition"""
    closing = pyqtSignal(bool)

    def __init__(self, jobfile, parent=None):
        super(logwidget, self).__init__(parent)

        self.pathjobfile = jobfile
        self.setWindowTitle("EZ-InSAR job - Log")
        self.setGeometry(0, 0, 750, 500)
        self.move(200, 100)
        self.success = False
        self.false = False

        self.setStyleSheet(__theme__)

        job = ez.load(self.pathjobfile,verbose=False)
        
        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p style="font-size:20px"><b>EZ-InSAR Job Log<\b></p>')

        clearbt = QPushButton("Clean")
        clearbt.clicked.connect(self.cleanlog)

        exportbt = QPushButton("Export")
        exportbt.clicked.connect(self.export)

        self.logText = QTextEdit()
        self.logText.setReadOnly(True)
        h = 1
        with open(job.log,'r') as flog:
            log = flog.readlines()
        log = ''.join(log)

        self.logText.setText(tools.coloriselog(log))

        layout = QGridLayout()
        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 2, 1, 4, Qt.AlignCenter)
        layout.addWidget(clearbt, 0, 7, 1, 1)
        layout.addWidget(exportbt, 0, 8, 1, 1)
        layout.addWidget(self.logText , 1, 0, 9, 9)

        job = None 

        self.setLayout(layout)

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def cleanlog(self):
        """Clean the log"""
        ret = QMessageBox.warning(self, "Clear the log?",
                "Are you sure to clean the log?",
                QMessageBox.Ok | QMessageBox.Cancel)
        if ret == QMessageBox.Ok:
            job = ez.load(self.pathjobfile,verbose=False)
            with open(job.log,'w') as flog:
                flog.write('\n')
            self.close()

    def export(self):
        """Export the log"""
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,
                "Select a log file",'',
                "*.log", options=options)
        if fileName:
            try: 
                if not fileName.endswith('.log'):
                    fileName = fileName + '.log'
                job = ez.load(self.pathjobfile,verbose=False)
                shutil.copy(job.log,fileName)
                reply = QMessageBox.information(self, "EZ-InSAR Information",
                    'The log has been exported to %s.' % (fileName) ,
                    QMessageBox.Ok)
            except:
                reply = QMessageBox.critical(self, "EZ-InSAR Error",
                    'Error during the log export.',
                    QMessageBox.Ok)
        
############################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not os.path.isfile(args['--file']):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No file',None))

    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the EZ-InSAR log from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    
    if tools.checklicense():
        widget = logwidget(os.path.abspath(args['--file']))
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()
        
if __name__=='__main__':
    main()
