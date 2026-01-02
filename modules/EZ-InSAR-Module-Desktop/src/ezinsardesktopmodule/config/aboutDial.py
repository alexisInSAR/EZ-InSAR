#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a dialog for EZ-InSAR about

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.0: Change the about logo, Aug. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Feb. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a dialog for EZ-InSAR about

usage: 
    ezinsardesktop_about

"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QDialog, QProgressBar, QPushButton

import os, sys, webbrowser

from ezinsardesktopmodule import __file__ as __root_module__
from ezinsardesktopmodule import __versionPackage__,__copyrightPackage__
from ezinsardesktopmodule.config.settings import __theme__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule import __file__ as __moduleroot__
from ezinsardesktopmodule.tools import tools

###########################################################################################
## Class
###########################################################################################
class aboutDiag(QDialog):
    """QDialog class 

        Build the dialog window
    """
    def __init__(self, parent=None):
        super(aboutDiag, self).__init__(parent)

        self.parent = parent
        self.validation = False

        self.setStyleSheet(__theme__)

        mainLayout = QGridLayout()
        self.bar = QProgressBar()
        self.bar.setTextVisible(True)

        LogoLabel = QLabel()
        Logo = QPixmap(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg').scaled(512,512, Qt.KeepAspectRatio,Qt.SmoothTransformation)
        Logo.setDevicePixelRatio(QApplication.primaryScreen().devicePixelRatio())
        LogoLabel.setPixmap(Logo)

        mainLayout.addWidget(LogoLabel, 0, 0, 1, 3, Qt.AlignCenter)
        
        infoLabel = QLabel("""
                        <p><b>EZ-InSAR Desktop</b> is an optional module of EZ-InSAR to provide a Desktop Graphical User Interface to EZ-InSAR.</p>
                        <p>Version: %s</p>
                        <p>Copyright: %s</p>
                        <p><i>Developed with PyQt5.</i></p>
                        <p></p>
                        <p>For further information, please use the <i>ezinsar toolkit info</i> command.</p>
                        """ % (__versionPackage__,__copyrightPackage__))
        infoLabel.setWordWrap(True)

        mainLayout.addWidget(infoLabel, 1, 0, 1, 3)
        
        logo1 = QPushButton()
        logo1.setIcon(QIcon(os.path.dirname(__moduleroot__) + '%simages%sUCDlogo.png' % (os.sep,os.sep)))
        logo1.setIconSize(QSize(64, 64))
        logo1.clicked.connect(self.openWebSite1)
        logo2 = QPushButton()
        logo2.setIcon(QIcon(os.path.dirname(__moduleroot__) + '%simages%sicrag-logo.png' % (os.sep,os.sep)))
        logo2.setIconSize(QSize(64, 64))
        logo2.clicked.connect(self.openWebSite2)
        mainLayout.addWidget(logo1, 2, 0, 1, 1, Qt.AlignCenter)
        mainLayout.addWidget(logo2, 2, 1, 1, 1, Qt.AlignCenter)

        linkbt = QPushButton()
        linkbt.setIcon(QIcon(os.path.dirname(__moduleroot__) + '%simages%sEZ_InSAR_logo_desktop_whiteback.svg' % (os.sep,os.sep)))
        linkbt.setIconSize(QSize(64, 64))
        linkbt.clicked.connect(self.openWebSite3)
        mainLayout.addWidget(linkbt, 2, 2, 1, 1, Qt.AlignCenter)

        self.setLayout(mainLayout)
        self.setWindowTitle("EZ-InSAR Desktop Module - About")

    def openWebSite1(self):
        url = 'https://www.ucd.ie'
        webbrowser.open_new_tab(url)

    def openWebSite2(self):
        url = 'https://www.icrag-centre.org'
        webbrowser.open_new_tab(url)

    def openWebSite3(self):
        url = 'https://github.com/alexisInSAR/EZ-InSAR' 
        webbrowser.open_new_tab(url)

###########################################################################################
## Main 
###########################################################################################
def main():
    """Main function""" 

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        widget = aboutDiag()
        widget.show()
        sys.exit(app.exec_())
    sys.exit()

if __name__=='__main__':
    main()