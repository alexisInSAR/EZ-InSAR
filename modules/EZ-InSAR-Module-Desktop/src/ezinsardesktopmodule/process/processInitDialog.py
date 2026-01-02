#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a window to initiate a processing EZ-InSAR job

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 0.1.0: Initial version, Feb. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a window to initiate a processing EZ-InSAR job

usage: 
    ezinsardesktop_initprocess -f <str> -m <str> [options]

Arguments:
    -f, --file <str>        EZ-InSAR job file
    -m, --mode <str>        Processing mode. Can be coregistration, ifgstack, tsprocessing, intstack

Other-options:
    -h, --help
"""


###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QComboBox, QDialog, QPushButton, QGroupBox

import os, sys
from docopt import docopt

from ezinsar import constants, usermessage
from ezinsardesktopmodule import __file__ as __root_module__
from ezinsardesktopmodule import __versionPackage__
from ezinsardesktopmodule.tools import tools
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsardesktopmodule.tools.docsWidget import DocsDialog

###########################################################################################
## EPSGcodeDial class
###########################################################################################
class ProcessInit(QDialog):
    """QDialog class 

        Build the dialog windows
    """
    def __init__(self, parent=None, mode = 'coregistration', prevprocessor = None):
        super(ProcessInit, self).__init__(parent)

        self.parent = parent
        self.validation = False
        self.result = [None, None]
        self.mode = mode

        self.setStyleSheet(__theme__)

        titleLabel = QLabel("<p style='font-size:20px'><b>Creation of the EZ-InSAR processing job for <i>%s<\i><\b></p>" % (tools.mode2title(self.mode)))
        msg1 = QLabel("<p>Please select the processor (and approach if required) in order to craete the job.</p>")
        msg2 = QLabel("<p><i>EZ-InSAR will check the compatibilities between processor and imagery during the creation...<\i></p>")
        
        btHelp = QPushButton("Help", self)
        btHelp.clicked.connect(self.openhelp)

        grp1 = QGroupBox()
        layoutgrp1 = QGridLayout()

        processorLabel = QLabel("<p><b>SAR/InSAR processor:<\b></p>")
        self.processor = QComboBox()
        self.processor.addItems(tools.listprocessor(self.mode))
        if not prevprocessor == None: 
            self.processor.setCurrentIndex([x.lower() for x in tools.listprocessor(self.mode)].index(prevprocessor))
        else: 
            try: 
                self.processor.setCurrentIndex([x.lower() for x in tools.listprocessor(self.mode)].index(constants.__defautprocessor__))
            except:
                self.processor.setCurrentIndex(0)
        layoutgrp1.addWidget(processorLabel, 0, 0, 1, 1)
        layoutgrp1.addWidget(self.processor, 0, 1, 1, 1)
        grp1.setLayout(layoutgrp1)

        mainLayout = QGridLayout()
        mainLayout.addWidget(titleLabel, 0, 0, 1, 10, Qt.AlignCenter)
        mainLayout.addWidget(msg1, 1, 0, 1, 10)
        mainLayout.addWidget(msg2, 2, 0, 1, 10)
        mainLayout.addWidget(grp1, 3, 0, 1, 10)

        if self.mode == 'tsprocessing': 
            grp2 = QGroupBox()
            layoutgrp2 = QGridLayout()

            approachLabel = QLabel("<p><b>InSAR approach:<\b></p>")
            self.approach = QComboBox()
            self.approach.addItems(['Small-Baselines Subset','Persistent Scatters'])
            layoutgrp2.addWidget(approachLabel, 0, 0, 1, 1)
            layoutgrp2.addWidget(self.approach, 0, 1, 1, 1)
            grp2.setLayout(layoutgrp2)
            mainLayout.addWidget(grp2, 4, 0, 1, 10)
            self.processor.currentTextChanged.connect(self.updateapproach)

        self.btOkay = QPushButton("Create the processing job")
        self.btCancel = QPushButton("Cancel")

        self.btOkay.clicked.connect(self.valid)
        self.btCancel.clicked.connect(self.cancel)

        mainLayout.addWidget(self.btOkay, 10, 0, 1, 5)
        mainLayout.addWidget(self.btCancel, 10, 5, 1, 5)
        mainLayout.addWidget(btHelp, 11, 0, 1, 1)

        self.setLayout(mainLayout)

        self.setWindowTitle("EZ-InSAR - Creation for %s" % (tools.mode2title(self.mode)))
    
    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def openhelp(self):
        helpdial = DocsDialog(['applications','processing','processmode'])
        helpdial.show()
        helpdial.exec()

    def valid(self):
        """Validation    
        """
        self.validation = True
        self.result[0] = self.processor.currentText().lower()
        if self.mode == 'tsprocessing':
            if 'persistent' in self.approach.currentText().lower():
                self.result[1] = 'ps'
            elif 'linking' in self.approach.currentText().lower():
                self.result[1] = 'ps'
            else:
                self.result[1] = 'sbas'
        self.accept()

    def cancel(self):
        """Cancelation        
        """
        self.validation = False
        self.close()

    def updateapproach(self):
        """Update the InSAR approaches 
        """
        self.approach.clear()
        self.approach.addItems([x.split(' / ')[0] for x in constants.__TSapproach__[self.processor.currentText().lower()]])
        
###########################################################################################
## Main 
###########################################################################################
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not os.path.isfile(args['--file']):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No file',None))
    
    if not args['--mode'] in ['coregistration', 'ifgstack', 'tsprocessing', 'intstack']:
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No correct mode',None))

    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the Job parameter tools from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    
    if tools.checklicense():
        widget = ProcessInit(mode=args['--mode'])
        widget.show()
        app.exec_()

        if widget.validation:
            import ezinsar.job as ez
            job = ez.load(os.path.abspath(args['--file']),verbose=True)
            if args['--mode'] == 'coregistration': 
                job.initiatecoreg(processor=widget.result[0])
            elif args['--mode'] == 'ifgstack': 
                job.initiateifg(processor=widget.result[0])
            elif args['--mode'] == 'tsprocessing': 
                job.initiatets(processor=widget.result[0],mode=widget.result[1])
            elif args['--mode'] == 'instack': 
                job.initiateint(processor=widget.result[0])
            ez.save(job,os.path.abspath(args['--file']),verbose=True)
            job = None

    sys.exit()

if __name__=='__main__':
    main()
