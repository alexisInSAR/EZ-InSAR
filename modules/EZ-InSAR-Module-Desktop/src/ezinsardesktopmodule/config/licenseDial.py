#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a dialog for license validation

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.0.0: Initial version, Feb. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a dialog for license validation

usage: 
    ezinsardesktop_license

"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QDialog, QTextEdit, QPushButton, QTabWidget, QWidget, QCheckBox

import os, shutil, sys

from ezinsardesktopmodule import __file__ as __root_module__
from ezinsardesktopmodule import __versionPackage__,__copyrightPackage__
from ezinsardesktopmodule.config.settings import __theme__
from ezinsar.constants import __cachedir__
__root_module__ = os.path.dirname(__root_module__)
from ezinsar.tools import miscellaneous

###########################################################################################
## Class
###########################################################################################
class tabModule(QWidget):
    """QDialog class 

        Build the dialog window
    """
    def __init__(self, license, parent=None):
        super(tabModule, self).__init__(parent)
        self.setStyleSheet(__theme__)
        self.resize(500,500)
        self.parent = parent
        self.license = license

        mainLayout = QGridLayout()

        infoLabel = QLabel("""
                        <p><b>Please, accept the license terms for %s, version %s</p>
                        """ % (self.license['Name'],self.license['version']))
        infoLabel.setWordWrap(True)

        self.textLicense = QTextEdit()
        with open(self.license['licensefile'],'r') as fi:
            lines = fi.readlines()
        self.textLicense.setText(''.join(lines))
        self.textLicense.setReadOnly(True)
        self.textLicense.verticalScrollBar().valueChanged.connect(self.updatebt)

        self.check1Label = QLabel('I accept the term of this license regarding the use of %s. In addition, I also accept the license of the Python packages, dependencies, SAR/InSAR processor used by %s. I know I can find a full license information in the documentation, in the source directory of this software.' % (self.license['Name'], self.license['Name']))
        self.check1Label.setWordWrap(True)

        self.check1 = QCheckBox('I accept this statement')
        if len(lines) == 1:
            self.check1.setEnabled(True)
        else:
            self.check1.setEnabled(False)
        self.check1.clicked.connect(self.parent.checkcheck)

        if license['licensevalidated']:
            self.check1.setChecked(True)
            self.check1.setEnabled(True)

        mainLayout.addWidget(infoLabel, 1, 0, 1, 10)
        mainLayout.addWidget(self.textLicense, 2, 0, 10, 10)
        mainLayout.addWidget(self.check1Label, 13, 0, 1, 10)
        mainLayout.addWidget(self.check1, 14, 0, 1, 10)

        self.setLayout(mainLayout)

    def updatebt(self):                    
        if self.textLicense.verticalScrollBar().value() == self.textLicense.verticalScrollBar().maximum():
            self.check1.setEnabled(True)

class licenseDial(QDialog):
    """QDialog class 

        Build the dialog window
    """
    def __init__(self, licenses=None, parent=None, force = False):
        super(licenseDial, self).__init__(parent)

        self.parent = parent
        self.validation = False
        self.h = 0
        self.force = force

        if not licenses == None:
            self.licenses = licenses
        else:
            self.licenses = miscellaneous.checklicense(asklicense=False)

        self.setStyleSheet(__theme__)
        self.resize(750,500)

        mainLayout = QGridLayout()

        infoLabel = QLabel("""
                        <p><b>Please, accept the license terms for EZ-InSAR and modules.</p>
                        """)
        infoLabel.setWordWrap(True)

        self.tabs = QTabWidget()
        self.tabs.tabBar().setUsesScrollButtons(True)
        for li in self.licenses:
            if li['licensevalidated'] == False or self.force == True:
                self.tabs.addTab(tabModule(li,parent=self),li['Name'])
                if li['licensevalidated']:
                    self.h = self.h + 1

        self.btaccept = QPushButton('I accept the terms of this/these license(s)')
        self.btaccept.setEnabled(False)
        self.btaccept.clicked.connect(self.acceptlicense)

        mainLayout.addWidget(infoLabel, 1, 0, 1, 10)
        mainLayout.addWidget(self.tabs, 2, 0, 10, 10)
        mainLayout.addWidget(self.btaccept, 13, 0, 1, 10)

        self.setLayout(mainLayout)
        self.setWindowTitle("EZ-InSAR - Licenses")

        if self.tabs.count() == self.h:
            self.btaccept.setEnabled(True)
        else:
            self.btaccept.setEnabled(False)

    def checkcheck(self):
        if self.tabs.currentWidget().check1.isChecked():
            self.h = self.h + 1
        else:
            self.h = self.h - 1

        if self.tabs.count() == self.h:
            self.btaccept.setEnabled(True)
        else:
            self.btaccept.setEnabled(False)

    def acceptlicense(self):
        for li in self.licenses:
            if li['licensevalidated'] == False or self.force == True:
                shutil.copy(li['licensefile'],li['licensevalidatedfile'])
        self.validation = True
        self.close()

###########################################################################################
## Main 
###########################################################################################
def main():
    """Main function""" 
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    widget = licenseDial(force=True)
    widget.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()