#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Dialog for server selection for the SLC Retrieval
    
    (Supplementary module for EZ-InSAR)

Changelog:
        * 1.0.0: Initial version, Feb. 2025

"""
###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QComboBox, QPushButton, QDialog
from ezinsar.constants import __EZInSARserverImagery__
from ezinsardesktopmodule.config.settings import __theme__

###########################################################################################
## Class
###########################################################################################
class ServerDialog(QDialog):
    def __init__(self, parent=None):
        super(ServerDialog, self).__init__(parent)

        self.setStyleSheet(__theme__)

        self.result = None

        servernamelabel = QLabel("<p><b>Server for online imagery:<\b></p>")
        servernamelabel.setToolTip("""
                                <p>Please select the server for online imagery.</p>
                                """)

        self.servername = QComboBox()
        self.servername.addItems(__EZInSARserverImagery__)
        self.btOkay = QPushButton("Okay")
        self.btOkay.clicked.connect(self.valid)

        mainLayout = QGridLayout()
        mainLayout.addWidget(servernamelabel, 0, 0, 1, 1)
        mainLayout.addWidget(self.servername, 0, 1, 1, 1)
        mainLayout.addWidget(self.btOkay, 1, 0, 1, 2)
        self.setLayout(mainLayout)

        self.setWindowTitle("Server Selection")
       
    def valid(self):
        self.result = self.servername.currentText()
        self.accept()