#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Opening dialog

The module allows to open an opening dialog

    (Supplementary module for EZ-InSAR Desktop Module)

Changelog:
    * 1.0.0: Initial version, Mar. 2025

"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QDialog, QProgressBar

import os, sys, time, importlib, random
import numpy as np

from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsar import constants
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule.tools import tools

###########################################################################################
## EPSGcodeDial class
###########################################################################################
class openingDial(QDialog):
    """QDialog class 

        Build the dialog windows
    """
    def __init__(self, parent=None):
        super(openingDial, self).__init__(parent)

        self.parent = parent
        self.validation = False

        self.setStyleSheet(__theme__)
        
        mainLayout = QGridLayout()
        titleLabel = QLabel("<p style='font-size:20px'><b>Welcome to EZ-InSAR Desktop<\b></p>" )
        mainLayout.addWidget(titleLabel, 1, 0, 1, 10, Qt.AlignLeft)
        self.bar = QProgressBar()
        self.bar.setTextVisible(True)

        LogoLabel = QLabel()
        Logo = QPixmap(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg').scaled(256,256, Qt.KeepAspectRatio,Qt.SmoothTransformation)
        Logo.setDevicePixelRatio(QApplication.primaryScreen().devicePixelRatio())
        LogoLabel.setPixmap(Logo)
        mainLayout.addWidget(LogoLabel, 0, 0, 1, 10, Qt.AlignCenter)

        mainLayout.addWidget(QLabel("""
                                    <p>Version: %s</p>
                                    <p>%s</p>
                                    """ % (importlib.import_module('ezinsardesktopmodule').__versionPackage__,
                                           importlib.import_module('ezinsardesktopmodule').__copyrightPackage__,
                                           )
                                    ), 2, 0, 1, 10, Qt.AlignLeft)
        
        tmp = QLabel("""
                    <p>\n</p>
                    <p>Supported by EZ-InSAR Version %s</p>
                    """ % (importlib.import_module('ezinsar').__versionPackage__,
                            )
                    )
        tmp.setWordWrap(True)
        mainLayout.addWidget(QLabel(''), 3, 0, 1, 10)
        mainLayout.addWidget(tmp, 4, 5, 1, 5, Qt.AlignRight)
        mainLayout.addWidget(self.bar, 10, 0, 1, 10)
        self.setLayout(mainLayout)
        self.setWindowTitle("EZ-InSAR - Opening")

    ###########################################################################################
    ## Callbacks
    ###########################################################################################        
    def run(self):
        self.show()
        for idx in np.linspace(0,100,100):
            self.bar.setValue(int(idx))
            self.bar.setFormat('Please wait...')
            QApplication.processEvents()
            time.sleep(random.uniform(0,0.05))
        time.sleep(0.5)
        self.close()

    def runexit(self):
        self.show()
        for idx in np.linspace(0,100,100):
            self.bar.setValue(int(idx))
            self.bar.setFormat('Please wait...')
            QApplication.processEvents()
            time.sleep(random.uniform(0,0.05))
        time.sleep(0.5)
        self.close()
        sys.exit(-1)

###########################################################################################
## Main 
###########################################################################################
def main():
    """Main function""" 
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.gif'))
    if tools.checklicense():
        widget = openingDial()
        widget.runexit()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()