#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to import EGMS time series results into EZ-InSAR

The module contains functions to import EGMS datasets into EZ-InSAR

Changelog:
        * 1.0.0: Initial version, Jul. 2025

"""

__author__ = 'Alexis Hrysiewicz (UCD / iCRAG)'
__copyright__ = "Copyright 2025, EZ-InSAR / UCD / iCRAG"
__version__ = '1.0.0'

################################################################################
## Python packages
################################################################################
import os
import pandas as pd
from typing import Optional, Union
import numpy as np
import time 
from datetime import datetime
import sys

from ezinsar.tools import ezinsardata
from ezinsar import usermessage, constants

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit, QMessageBox, QPushButton,  QWidget, QGroupBox, QSpinBox, QFileDialog, QComboBox

try: 
        from ezinsardesktopmodule.config.settings import __theme__
        from ezinsardesktopmodule.tools import tools
        from ezinsardesktopmodule import __file__ as __root_module__
        __root_module__ = os.path.dirname(__root_module__)
except:
         usermessage.warningmsg(__name__,__name__,__file__,'The GUI of this function will not be available because the EZ-InSAR desktop is required.',None,True)

################################################################################
## Import function
################################################################################
def importdata(file,
        relorbit,
        satpass,
        mode: Optional[str] = 'LOS',
        target: Optional[str] = 'None',
        verbose: Optional[bool] = True,
        log: Optional[Union[str,None]] = None,
        ): 
        """Import EGMS dataset into EZ-InSAR

        Args:   
                
                verbose (bool, Optional): Verbose. [Default: `True`]
                log (str, Optional): log. [Default: `None`]
        
        Returns:
                `stack` class
        """
        start = time.time()

        usermessage.openingmsg(__name__,__name__,__file__,constants.__copyright__,'Import EGMS dataset into EZ-InSAR',log,verbose,contribauthor=__author__,contribcopyright=__copyright__,contribversion=__version__,contribfile=__file__)

        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if not mode in ['LOS']:
                raise TypeError(usermessage.typeerrormsg(
                        __name__,__name__,__file__,__copyright__,
                        'mode','LOS',log))
        
        if not isinstance(relorbit,int):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,__name__,__file__,__copyright__,
                        'relorbit','int',log))

        if not satpass in ['ASCENDING','DESCENDING']:
                raise TypeError(usermessage.typeerrormsg(
                        __name__,__name__,__file__,__copyright__,
                        'satpass',"['ASCENDING','DESCENDING']",log))

        usermessage.ezprint('Import parameters:',log,verbose)
        usermessage.ezprint('\tFile: %s' % (file),log,verbose)

        ## Read the file 
        usermessage.ezprint('Read the file...',log,verbose)
        EGMSdata = pd.read_csv(file,delimiter=';')
        usermessage.ezprint('\tdone',log,verbose)

        ## Initialisation of the dataset
        usermessage.ezprint('Initialisation of the dataset...',log,verbose)
        data = ezinsardata.displacement()
        usermessage.ezprint('\tdone',log,verbose)

        ## Detection of the dataset mode
        usermessage.ezprint('The mode is %s.' % (mode),log,verbose)
        usermessage.ezprint('\tdone',log,verbose)
        data.mode['value'] = 'LOS'

        ## For the metadata
        usermessage.ezprint('Extract the metadata...',log,verbose)
                
        data.datainformation['Name'] = file.split(os.sep)[-1]
        data.datainformation['Target'] = target
        data.datainformation['InSAR_Processor'] = 'EGMS'
        data.datainformation['Satellite'] = 'S1'
        data.datainformation['Mode'] = 'IW'
        data.datainformation['Pass'] = satpass
        data.datainformation['Track'] = relorbit 
        data.datainformation['Wavelength'] = 0.055
        data.datainformation['TS_Processor'] = 'EGMS'
        data.datainformation['Approach'] = 'EGMS'
        data.datainformation['Date'] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        data.datainformation['Importation'] = 'regular'
        data.datainformation['Processing'] = 'raw'
        data.datainformation['Metadata_processing'] = 'None'
        data.datainformation['Path'] = os.path.dirname(file)

        usermessage.ezprint('\tdone',log,verbose)

        ## For the temporal data
        usermessage.ezprint('Extract the temporal information...',log,verbose)

        data.dates['value'] = []

        for keyi in list(EGMSdata.keys()):
                if ('20' in keyi) and (len(keyi) == 8):
                        data.dates['value'].append(datetime.strptime(keyi,'%Y%m%d'))

        data.n_image['value'] = int(len(data.dates['value']))
        data.n_ifg['value'] = int(0)
        data.date_ref['value'] = data.dates['value'][0]
        data.ifg_date['value'] = np.array([np.nan])

        usermessage.ezprint('\tdone',log,verbose)

        ## For the spatial data
        usermessage.ezprint('Extract the spatial information...',log,verbose)

        data.lon['value'] = np.array(EGMSdata['longitude'].to_list())
        data.lat['value'] = np.array(EGMSdata['latitude'].to_list())

        data.index_pts['value'] = None 

        data.x_utm['value'] = np.array(EGMSdata['easting'].to_list())
        data.y_utm['value'] = np.array(EGMSdata['northing'].to_list())
        data.code_meter['value'] = 'epsg:3035'

        usermessage.ezprint('\tdone',log,verbose)

        # For the ground data
        usermessage.ezprint('Extract the ground information...',log,verbose)

        data.hgt['value'] = np.array(EGMSdata['height_wgs84'].to_list())
        data.hgt_grid['value'] = np.array([0])
        data.heading['value'] = np.array([0])
        data.inc_angle['value'] = np.array(EGMSdata['incidence_angle'].to_list())

        usermessage.ezprint('\tdone',log,verbose)

        ## For the displacement data
        usermessage.ezprint('Extract the displacement information...',log,verbose)
        data.rateLOS['value'] = np.array(EGMSdata['mean_velocity'].to_list())
        data.sigmarateLOS['value'] = np.array(EGMSdata['mean_velocity_std'].to_list())
                                         
        tmp = np.empty((data.rateLOS['value'].shape[0],len(data.dates['value'])))
        
        h = 0
        for keyi in list(EGMSdata.keys()):
                if ('20' in keyi) and (len(keyi) == 8):
                        tmp[:,h] = EGMSdata[keyi].to_list()
                        h = h + 1 
        data.dispLOS['value'] = tmp
        data.sigmadispLOS['value'] = None

        usermessage.ezprint('\tdone',log,verbose)

        ## For the reference point
        data.referencepoint['value']['index'] = np.array([0])
        data.referencepoint['value']['lon_pt_ref'] = np.array([0])
        data.referencepoint['value']['lat_pt_ref'] = np.array([0])
        data.referencepoint['value']['lon_pt_refarea'] = np.array([0])
        data.referencepoint['value']['lat_pt_refarea'] = np.array([0])
        data.referencepoint['value']['radius'] = np.array([0])
        data.referencepoint['value']['rateLOS'] = np.array([0])

        usermessage.ezprint('\nPerformed in %0.3f seconds' % (time.time()-start),log,verbose)

        return data

################################################################################
## Desktop application
################################################################################
class GUIimportEGMS(QWidget):
        """Import Widget"""
        closing = pyqtSignal(bool)

        def __init__(self, log = None, parent=None):
                super(GUIimportEGMS, self).__init__(parent)

                self.resize(1500, 1250)
                self.success = False
                self.false = False
                self.parent = parent
                self.log = log

                self.setWindowTitle("EZ-InSAR - Import EGMS datasets into EZ-InSAR")
                self.setStyleSheet(__theme__)

                self.insardisp = []
                self.insarlistfilename = []
                self.insarlistshortfilename = []

                widgetlogo = tools.create_logo_wigdet(logo=__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop.svg')
                widgettitle = QLabel('<p style="font-size:20px"><b>Import EGMS datasets into EZ-InSAR</b></p>')
                btclose = QPushButton("Close", self)
                btclose.clicked.connect(self.closemaybe)

                filegrp = QGroupBox('EGMS file')
                filegrpLayout = QGridLayout()
                FileValueLabel = QLabel('<p><b>EGMS file [.csv]:</b></p>')
                self.fileValue = QLineEdit()
                self.fileValue.setReadOnly(True)
                self.fileValue.setPlaceholderText('Click on the selection button')
                FileBtOpen = QPushButton("Select", self)
                FileBtOpen.clicked.connect(self.openEGMSfile)
                filegrpLayout.addWidget(FileValueLabel,0,0,1,1)
                filegrpLayout.addWidget(self.fileValue,0,1,1,1)
                filegrpLayout.addWidget(FileBtOpen,0,2,1,1)
                filegrp.setLayout(filegrpLayout)

                paragrp = QGroupBox('Parameters')
                paragrpLayout = QGridLayout()
                modeValueLabel = QLabel('<p><b>Mode:</b></p>')
                self.modeValue = QComboBox()
                self.modeValue.addItems(['LOS','3D'])
                self.modeValue.currentTextChanged.connect(self.updateGUI)
                self.modeValue.setEnabled(False)

                relorbValueLabel = QLabel('<p><b>Relative orbit:</b></p>')
                self.relorbValue = QSpinBox()
                self.relorbValue.setMaximum(200)
                self.relorbValue.setMinimum(0)
                self.relorbValue.setValue(0)
                self.relorbValue.valueChanged.connect(self.updateGUI)

                satpassValueLabel = QLabel('<p><b>Satellite pass:</b></p>')
                self.satpassValue = QComboBox()
                self.satpassValue.addItems([None,'Ascending','Descending'])
                self.satpassValue.currentTextChanged.connect(self.updateGUI)

                targetValueLabel = QLabel('<p><b>Target name:</b></p>')
                self.targetValue = QLineEdit()
                self.targetValue.setPlaceholderText('Type the target name')

                paragrpLayout.addWidget(modeValueLabel,0,0,1,1)
                paragrpLayout.addWidget(self.modeValue,0,1,1,1)
                paragrpLayout.addWidget(relorbValueLabel,1,0,1,1)
                paragrpLayout.addWidget(self.relorbValue,1,1,1,1)
                paragrpLayout.addWidget(satpassValueLabel,2,0,1,1)
                paragrpLayout.addWidget(self.satpassValue,2,1,1,1)
                paragrpLayout.addWidget(targetValueLabel,3,0,1,1)
                paragrpLayout.addWidget(self.targetValue,3,1,1,1)
                paragrp.setLayout(paragrpLayout)

                outputgrp = QGroupBox('Output file')
                outputgrpLayout = QGridLayout()

                outDirValueLabel = QLabel('<p><b>Output directory:</b></p>')
                self.outDirValue = QLineEdit()
                self.outDirValue.setReadOnly(True)
                self.outDirValue.setPlaceholderText('Click on the selection button')
                outDirBtOpen = QPushButton("Select", self)
                outDirBtOpen.clicked.connect(self.openoutDir)

                outFileValueLabel = QLabel('<p><b>Output file:</b></p>')
                self.outFileValue = QLabel('None')

                outputgrpLayout.addWidget(outDirValueLabel,0,0,1,1)
                outputgrpLayout.addWidget(self.outDirValue,0,1,1,1)
                outputgrpLayout.addWidget(outDirBtOpen,0,2,1,1)

                outputgrpLayout.addWidget(outFileValueLabel,1,0,1,1)
                outputgrpLayout.addWidget(self.outFileValue,1,1,1,1)
                
                outputgrp.setLayout(outputgrpLayout)

                self.importBt = QPushButton("Import the file", self)
                self.importBt.setEnabled(False)
                self.importBt.clicked.connect(self.runimport)
        
                layout = QGridLayout()
                layout.addWidget(widgetlogo, 0, 0, 1, 1)
                layout.addWidget(widgettitle, 0, 1, 1, 8, Qt.AlignCenter)
                layout.addWidget(btclose, 0, 9, 1, 1)

                layout.addWidget(filegrp, 1, 0, 1, 10)
                layout.addWidget(paragrp, 2, 0, 1, 10)
                layout.addWidget(outputgrp, 3, 0, 1, 10)
                layout.addWidget(self.importBt, 4, 0, 1, 10)

                self.setLayout(layout)

                self.autonaming()

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
        def messageerror(self,msg):
                reply = QMessageBox.critical(self, "EZ-InSAR Error",
                        msg,
                        QMessageBox.Ok)
                
        def messagesuccess(self,msg):
                reply = QMessageBox.information(self, "EZ-InSAR Information",
                        msg,
                        QMessageBox.Ok)
                
        def openEGMSfile(self): 
                options = QFileDialog.Options()
                fileName, _ = QFileDialog.getOpenFileName(self,
                        "Select an EGMS dataset file",'',
                        "*.csv", options=options)
                if fileName: 
                        self.fileValue.setText(fileName)

                        if 'L3' in fileName.split(os.sep)[-1]: 
                                self.modeValue.setCurrentIndex(1)
                        else: 
                                self.modeValue.setCurrentIndex(0)
                                self.relorbValue.setValue(int(fileName.split(os.sep)[-1].split('_')[2]))
                        self.updateGUI()

        def openoutDir(self):
                options = QFileDialog.Options()
                directory = QFileDialog.getExistingDirectory(self,
                        "Select the output directory", options=options)
                if directory: 
                        self.outDirValue.setText(directory)   
                        self.updateGUI()

        def autonaming(self): 
                if '2015_2021' in self.fileValue.text().split(os.sep)[-1]: 
                        key = '_2015_2021'
                elif '2018_2022' in self.fileValue.text().split(os.sep)[-1]: 
                        key = '_2018_2022'
                elif '2019_2023' in self.fileValue.text().split(os.sep)[-1]: 
                        key = '_2019_2023'
                else: 
                        key = ''

                namefile = 'TS_%s_S1_IW_%s_%s_egms%s.eidata' % (self.modeValue.currentText(),
                                                              str(self.relorbValue.value()),
                                                              self.satpassValue.currentText().upper(),
                                                              key)
                self.outFileValue.setText(namefile)
        
        def updateGUI(self):
                self.autonaming()
                if (not self.relorbValue.value() == 0) and (not self.satpassValue.currentText() == '') and (not self.targetValue.text() == '') and (not self.outDirValue.text() == '') and (not self.fileValue.text() == ''): 
                        self.importBt.setEnabled(True)
                else: 
                        self.importBt.setEnabled(False)

        def runimport(self): 
                from ezinsar.contrib.python import importEGMS
                from ezinsar.tools import ezinsardata

                try: 
                        data = importEGMS.importdata(self.fileValue.text(),
                        self.relorbValue.value(),
                        self.satpassValue.currentText().upper(),
                        target=self.targetValue.text(),
                        verbose=False)

                        ezinsardata.saveEZdata(data,self.outDirValue.text()+os.sep+self.outFileValue.text(),verbose=False)

                        self.messagesuccess('File saved in %s' % (self.outDirValue.text()+os.sep+self.outFileValue.text()))

                except Exception as e:
                        self.messageerror('%s' % (e))

        def closemaybe(self):
                """Close"""
                return self.close()
    
###########################################################################################
## DEBUG
########################################################################################### 
def main():       
        app = QApplication(sys.argv)
        widget = GUIimportEGMS()
        widget.show()
        sys.exit(app.exec_())
if __name__=='__main__':
        main()




