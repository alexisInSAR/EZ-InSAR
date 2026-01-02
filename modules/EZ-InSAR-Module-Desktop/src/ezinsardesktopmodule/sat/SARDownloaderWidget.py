#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a window to download SLC/orbits

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 1.1.0: Add the ETAD file download, Aug. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Feb. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a window to download SLC/orbits

usage: 
    ezinsardesktop_downloader -f <str> [options]

Arguments:
    -f, --file <str>        EZ-InSAR job file

Other-options:
    -h, --help
"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QIcon,  QStandardItemModel, QStandardItem, QFont
from PyQt5.QtWidgets import QApplication, QCheckBox, QGridLayout, QLabel, QLineEdit, QMessageBox, QComboBox, QPushButton,  QWidget, QTableView, QDialog, QGroupBox

import os, sys
import numpy as np
from docopt import docopt
import datetime
import pandas as pd
from datetime import timedelta

from ezinsardesktopmodule.sat import SARDownloadWorker
from ezinsardesktopmodule.log import logWorker

from ezinsar import constants, usermessage
import ezinsar.job as ez
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsardesktopmodule.tools.docsWidget import DocsDialog

###########################################################################################
## Classes
###########################################################################################
class IDquery(QDialog):
    """ID Dialog"""
    def __init__(self, server, mode, parent=None):
        super(IDquery, self).__init__(parent)

        self.server = server
        self.mode = mode
        self.username = ''
        self.password = ''
        self.serverorbit = 'Copernicus'
        self.orbitfilebased = True
        self.success = False

        self.setStyleSheet(__theme__)

        if self.mode == 'image':
            self.title = QLabel("<p><b>Image Download from %s<\b></p>" % (self.server))
        elif self.mode == 'orbit':
            self.title = QLabel("<p><b>Orbit Download from %s<\b></p>" % (self.server))
        else:
            self.title = QLabel("<p><b>ETAD Download from %s<\b></p>" % (self.server))

        self.btimport = QPushButton("Load ID from EZ-InSAR")
        self.btimport.clicked.connect(self.importid)

        self.btOkay = QPushButton("Start")
        self.btOkay.clicked.connect(self.valid)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.title, 0, 0, 1, 5)
        mainLayout.addWidget(self.btOkay, 6, 0, 1, 5)
        mainLayout.addWidget(self.btimport, 5, 0, 1, 5)

        idlabel = QLabel("<p>Username/Email:</p>")
        self.idtext = QLineEdit()
        self.idtext.setPlaceholderText('your username')
        self.idtext.textChanged.connect(self.updatebtstart)    

        mainLayout.addWidget(idlabel, 1, 0, 1, 2)
        mainLayout.addWidget(self.idtext, 1, 2, 1, 3)

        passwordlabel = QLabel("<p>Password:</p>")
        self.passwordtext = QLineEdit()
        self.passwordtext.setPlaceholderText('your password') 
        self.passwordtext.setEchoMode(QLineEdit.Password)
        self.passwordtext.textChanged.connect(self.updatebtstart)

        mainLayout.addWidget(passwordlabel, 2, 0, 1, 2)
        mainLayout.addWidget(self.passwordtext, 2, 2, 1, 3)

        if not mode == 'image':
            filebasedLabel = QLabel("<p>Only for stored files:</p>")
            self.filebased = QComboBox()
            self.filebased.addItems(['True','False'])
            self.filebased.setCurrentIndex([True,False].index(self.orbitfilebased))
            mainLayout.addWidget(filebasedLabel, 3, 0, 1, 2)
            mainLayout.addWidget(self.filebased, 3, 2, 1, 3)

            serverbisLabel = QLabel("<p>Server:</p>")
            self.serverbis = QComboBox()

            if not mode == 'etad':
                self.serverbis.addItems(['Copernicus','ASF'])
                if not self.server == "EarthDATA":
                    self.serverbis.setCurrentIndex(['Copernicus','ASF'].index(self.server))
                else:
                    self.serverbis.setCurrentIndex(0)
            else:
                self.serverbis.addItems(['Copernicus'])
            self.serverbis.currentTextChanged.connect(self.changerserver)
            mainLayout.addWidget(serverbisLabel, 4, 0, 1, 2)
            mainLayout.addWidget(self.serverbis, 4, 2, 1, 3)

        self.setLayout(mainLayout)

        self.setWindowTitle("SAR Downloader Start")

        self.updatebtstart()

    def changerserver(self):
        self.title.setText("<p><b>Orbit Download from %s<\b></p>" % (self.serverbis.currentText()))

    def importid(self):
        self.idtext.setText(constants.__username__)
        self.passwordtext.setText(constants.__password__)

    def updatebtstart(self):
        if self.passwordtext.text() == '' or self.idtext.text() == '':
            self.btOkay.setEnabled(False)
        else:
            self.btOkay.setEnabled(True)
       
    def valid(self):
        if not self.mode == 'image':
            self.serverorbit = self.serverbis.currentText()
            self.orbitfilebased = (self.filebased.currentText() == 'True')
        self.username = self.idtext.text()
        self.password  = self.passwordtext.text()
        self.success = True
        self.accept()

class AdvOptDialog(QDialog):
    """Advanced options Dialog"""
    def __init__(self, server, advancedoptions, parent=None):
        super(AdvOptDialog, self).__init__(parent)

        self.setStyleSheet(__theme__)

        self.server = server
        self.advancedoptions = advancedoptions

        servernamelabel = QLabel("<p><b>Advanced options for the %s server<\b></p>" % (self.server))
        
        self.btOkay = QPushButton("Okay")
        self.btOkay.clicked.connect(self.valid)

        mainLayout = QGridLayout()
        mainLayout.addWidget(servernamelabel, 0, 0, 1, 1)
        
        zippingLabel = QLabel("<p>Re-zip the files:</p>")
        zippingLabel.setToolTip("""
                                <p>EZ-InSAR will re-zip the downloaded files.</p>
                                """)
        self.zipping = QComboBox()
        self.zipping.addItems(['True','False'])
        self.zipping.setCurrentIndex([True,False].index(self.advancedoptions['zipping']))

        if (not self.server == 'EarthDATA') or (not self.server == 'GEODES'):
            mainLayout.addWidget(zippingLabel, 1, 0, 1, 1)
            mainLayout.addWidget(self.zipping, 1, 1, 1, 1)

        if self.server == 'Copernicus':
            modepartialLabel = QLabel("<p>Mode of partial downloading:</p>")
            self.modepartial = QComboBox()
            self.modepartial.addItems(['include','exclude'])
            self.modepartial.setCurrentIndex(['include','exclude'].index(self.advancedoptions['modepartial']))

            partialdownloadingLabel = QLabel("<p>Partial-downloading pattern:</p>")
            self.partialdownloading = QLineEdit()
            if not self.advancedoptions['partialdownloading'] == None:
                self.partialdownloading.setText(','.join(self.advancedoptions['partialdownloading']))
            else:
                self.partialdownloading.setText(None)
            self.partialdownloading.setPlaceholderText('-vh-,.tiff')            

            mainLayout.addWidget(modepartialLabel, 2, 0, 1, 1)
            mainLayout.addWidget(self.modepartial, 2, 1, 1, 1)

            mainLayout.addWidget(partialdownloadingLabel, 3, 0, 1, 1)
            mainLayout.addWidget(self.partialdownloading, 3, 1, 1, 1)

        elif self.server == 'ASF':
            burstonly = QLabel("<p>Only the intersected Sentinel-1 IW burst:</p>")
            self.burstonly = QComboBox()
            self.burstonly.addItems(['True','False'])
            self.burstonly.setCurrentIndex([True,False].index(self.advancedoptions['burstonly']))

            mainLayout.addWidget(burstonly, 2, 0, 1, 1)
            mainLayout.addWidget(self.burstonly, 2, 1, 1, 1)
        
        mainLayout.addWidget(self.btOkay, 5, 0, 1, 2)
        self.setLayout(mainLayout)

        self.setWindowTitle("Advanced Options")
       
    def valid(self):
        self.advancedoptions['zipping'] = (self.zipping.currentText() == 'True')

        if self.server == 'Copernicus':
            self.advancedoptions['modepartial'] = self.modepartial.currentText()
            if self.partialdownloading.text() == '':
                self.advancedoptions['partialdownloading'] = None
            else:
                self.advancedoptions['partialdownloading'] = self.partialdownloading.text().split(',')
        elif self.server == 'ASF':
            self.advancedoptions['burstonly'] = (self.burstonly.currentText() == 'True')

        self.accept()

class PandasTableModel(QStandardItemModel):
    """Table object"""
    def __init__(self, data, parent=None):
        QStandardItemModel.__init__(self, parent)
        self._data = data
        for col in data.columns:
            data_col = [QStandardItem("{}".format(x)) for x in data[col].values]
            for idx, ri in enumerate(data_col):
                data_col[idx].setEditable(False)
                tmp = QFont()
                if data['Selected'][idx] == True:
                    tmp.setBold(True)
                else:
                    tmp.setBold(False)
                data_col[idx].setFont(tmp)
            self.appendColumn(data_col)
        return

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def headerData(self, x, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[x]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self._data.index[x]
        return None
    
class Downloader(QWidget):
    """Downloader Widget"""
    closing = pyqtSignal(bool)

    def __init__(self, jobfile, parent=None):
        super(Downloader, self).__init__(parent)

        self.pathjobfile = jobfile
        self.setWindowTitle("EZ-InSAR - SAR Downloader")
        self.resize(750, 500)
        self.success = False
        self.false = False
        self.parent = parent

        self.setStyleSheet(__theme__)

        self.threadlog = None
        self.workerlog = None
        self.threadprocess = None
        self.workerprocess = None

        self.advancedoptions = {'burstonly': False,
                            'partialdownloading': None,
                            'modepartial': 'exclude',
                            'zipping': True}

        job = ez.load(self.pathjobfile,verbose=False)
        self.SLClist = job.SLClist
        
        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p style="font-size:20px"><b>SAR Data Downloader<\b></p>')
        btQuit = QPushButton("Close", self)

        btHelp = QPushButton("Help", self)
        btHelp.clicked.connect(self.openhelp)

        self.serverlabel = QLabel('<p><b>Selected server:<\b> %s</p>' % (job.SLClist['Server'][0]))
        self.serverlabel.setToolTip("""
                                    <p>Name of the selected server for SLC.</p>
                                    """)
        
        selectiongroup = QGroupBox('Selection')
        selectiongroupLayout = QGridLayout()
        
        self.modeSafeLabel = QLabel('<p>Safe Mode:</p>')
        self.modeSafeLabel.setToolTip("""
                                <p>The Safe Mode allows to make sure that all images for a same date will be selected for downloading. The Safe Mode is mandatory.</p>
                                """)
        self.modeSafe = QCheckBox("")
        self.modeSafe.setChecked(True)
        self.modeSafe.setEnabled(False)

        self.btall = QPushButton("Unselect all", self)
        self.btall.clicked.connect(self.selectall)

        self.templateLabel = QLabel('<p>Pre-selection:</p>') 
        self.templateLabel.setToolTip("""
                                <p>EZ-InSAR offers some pre-selections of SLCs regarding temporal sampling. Only available with the safe mode.</p>
                                """)
        self.templatelist = QComboBox()
        self.templatelist.addItems(['','monthly','bimonthly','trimonthly','4monthly','5monthly','6monthly','yearly','2yearly'])
        self.templatelist.currentTextChanged.connect(self.preselect)

        selectiongroupLayout.addWidget(self.modeSafeLabel,0,0,1,1)
        selectiongroupLayout.addWidget(self.modeSafe,0,1,1,1)
        selectiongroupLayout.addWidget(self.btall,1,0,1,2)
        selectiongroupLayout.addWidget(self.templateLabel,2,0,1,1)
        selectiongroupLayout.addWidget(self.templatelist,2,1,1,1)
        selectiongroup.setLayout(selectiongroupLayout)

        toolgroup = QGroupBox('Tools')
        toolgroupLayout = QGridLayout()

        self.btcheck = QPushButton("Check the SLC list", self)
        self.btcheck.setToolTip("""
                                <p>Check the SLC list.</p>
                                """)
        self.btcheck.clicked.connect(self.checkSLC)

        self.btadvopts = QPushButton("Advanced options", self)
        self.btadvopts.clicked.connect(self.queryadvopt)

        self.btTimeest = QPushButton("Estimated time", self)
        self.btTimeest.clicked.connect(self.estimatetime)

        toolgroupLayout.addWidget(self.btcheck,0,0,1,1)
        toolgroupLayout.addWidget(self.btTimeest,1,0,1,1)
        toolgroupLayout.addWidget(self.btadvopts,2,0,1,1)
        toolgroup.setLayout(toolgroupLayout)

        dwgroup = QGroupBox('Download')
        dwgroupLayout = QGridLayout()

        self.btdwSLC = QPushButton("Download the images", self)
        self.btdwSLC.clicked.connect(self.lauchSLCdw)
        self.btdworb = QPushButton("Download the orbit files", self)
        self.btdworb.clicked.connect(self.lauchorbitdw)
        self.btdwetad = QPushButton("Download the ETAD files", self)
        self.btdwetad.clicked.connect(self.lauchetaddw)
        if job.satellite == 'S1':
            self.btdwetad.setEnabled(True)
        else:
            self.btdwetad.setEnabled(False)
       
        dwgroupLayout.addWidget(self.btdwSLC,0,0,1,1)
        dwgroupLayout.addWidget(self.btdworb,1,0,1,1)
        dwgroupLayout.addWidget(self.btdwetad,2,0,1,1)
        dwgroup.setLayout(dwgroupLayout)

        self.pdtable = QTableView()
        self.pdtable.setShowGrid(False)
        self.pdtable.setSelectionBehavior(self.pdtable.SelectRows)

        job.checkSLClist(verbose=False)
        datadict = {'File': job.SLClist['Name'],
                    'SizeMB': job.SLClist['SizeMB'],
                    'Downloaded': job.SLClist['Stored'],
                    'Selected':[True] * len(job.SLClist['Stored']),
                    }
        
        data = pd.DataFrame.from_dict(datadict)
        self.model = PandasTableModel(data)
        self.pdtable.setModel(self.model)
        self.pdtable.doubleClicked.connect(self.clickcell)

        layout = QGridLayout()
        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 8, Qt.AlignCenter)
        layout.addWidget(self.serverlabel, 1, 0, 1, 7, Qt.AlignLeft)
        layout.addWidget(self.pdtable, 2, 0, 9, 8)
        layout.addWidget(selectiongroup,2,8,1,2)
        layout.addWidget(toolgroup,3,8,1,2)
        layout.addWidget(dwgroup,10,8,1,2)
        layout.addWidget(btQuit, 0, 9, 1, 1)
        layout.addWidget(btHelp, 20, 0, 1, 1)

        self.setLayout(layout)

        btQuit.clicked.connect(self.closemaybe)

        self.updatebtdw()

        job = None

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def openhelp(self):
        helpdial = DocsDialog(['applications','satellite','satdownloader'])
        helpdial.show()
        helpdial.exec()
    
    def closemaybe(self):
        """Close"""
        self.closing.emit(True)
        return self.close()
    
    def readtable(self):
        """Read the table"""
        table = {'Name':[],
                'SizeMB':[],
                'Downloaded':[],
                'Selected':[]}
        idx = 0
        while idx < self.model.rowCount():   
            table['Name'].append(self.model.item(idx,column=0).text())
            if not (self.model.item(idx,column=1).text() == None or self.model.item(idx,column=1).text() == 'None'):
                table['SizeMB'].append(float(self.model.item(idx,column=1).text()))
            else:
                table['SizeMB'].append(None)
            table['Downloaded'].append(bool(not self.model.item(idx,column=2).text() == 'False'))
            table['Selected'].append(bool(not self.model.item(idx,column=3).text() == 'False'))
            idx = idx + 1
        data = pd.DataFrame.from_dict(table)
        return data

    def estimatetime(self):
        """Estimate the required time"""
        sizelist = []
        data = self.readtable()
        for idx, rowi in data.iterrows():
                if rowi['Downloaded'] == False and rowi['Selected'] == True:
                    if not rowi['SizeMB'] == None:
                        sizelist.append(rowi['SizeMB'])
                    else:
                        sizelist.append(np.nan)
        sizelist = np.array(sizelist)
        idx = np.where(np.isnan(sizelist))
        sizelist[idx] = np.nanmean(sizelist)

        if 'Copernicus' in self.serverlabel.text() or 'GEODES' in self.serverlabel.text():
            estspeed = 8000/(20*60)
        elif ('ASF' in self.serverlabel.text()) or ('EarthDATA' in self.serverlabel.text()):   
            if constants.__wgetlimit__ == 'auto':
                estspeed = 7/24 * 30 + 14/24 * float(constants.__wgetlimitmin__.replace('m','')) # 30M/S seems the limit
            else:
                estspeed = float(constants.__wgetlimit__.replace('m',''))
        duration = datetime.timedelta(seconds=np.sum(sizelist) / estspeed)
        
        msg = "<p>Considering that the user connection bandwith is not limited (or limited by EZ-InSAR), the estimated time for SLC file(s) is:</p>" \
            "<p>%s</p>" \
            "<p>for %s files and %0.0f GB,</p>" \
            "<p>with an average speed of %0.1f MB/s.</p>" \
            "<p>This time is broadly estimated and can vary.</p>" % (str(duration).split('.')[0], sizelist.shape[0],np.sum(sizelist)/1000,estspeed)
        reply = QMessageBox.information(self, "EZ-InSAR Information",
                msg,
                QMessageBox.Ok)
        
    def selectall(self):
        """Select all"""
        data = self.readtable()
        if 'Unselect all' == self.btall.text():
            data['Selected'] = [False] * len(data['Name'])
            self.btall.setText('Select all')
        else:
            data['Selected'] = [True] * len(data['Name'])
            self.btall.setText('Unselect all')
        self.model = PandasTableModel(data)
        self.pdtable.setModel(self.model)
        self.templatelist.setCurrentIndex(0)
        self.updatebtdw()

    def preselect(self):
        """Enable the pre-selection"""
        if not self.modeSafe.isChecked():
            reply = QMessageBox.critical(self, "EZ-InSAR Error",
                'The pre-selection is only enabled with the Safe Mode.',
                QMessageBox.Ok)
            self.modeSafe.setChecked(True)

        if not self.templatelist.currentText() == '':
            index = self.templatelist.currentText()

            listdate = []
            for datei in self.SLClist['Date1']:
                listdate.append(datei.split('T')[0])
            listdate = np.unique(listdate)

            listdatef = []
            listdateftimestamp = []
            for di in listdate:
                a = datetime.datetime.strptime(di,'%Y-%m-%d')
                listdatef.append(a)
                listdateftimestamp.append(a.timestamp())
                
            newindex = []
            di = listdatef[0]
            while di <= listdatef[-1]: 
                idx = np.argmin(np.abs(di.timestamp() - np.array(listdateftimestamp)))
                newindex.append(idx)
                if index == 'monthly': 
                        di = di + timedelta(days=30)
                elif index == 'bimonthly': 
                        di = di + timedelta(days=2*30)
                elif index == 'trimonthly': 
                        di = di + timedelta(days=3*30)
                elif index == '4monthly': 
                        di = di + timedelta(days=4*30)
                elif index == '5monthly': 
                        di = di + timedelta(days=5*30)
                elif index == '6monthly': 
                        di = di + timedelta(days=6*30)
                elif index == 'yearly': 
                        di = di + timedelta(days=365.25*1)
                elif index == '2yearly': 
                        di = di + timedelta(days=365.25*2)
            index = []
            for idx in np.sort(np.unique(newindex)): 
                    index.append(idx)
            
            selecteddates = []
            for idx in index:
                selecteddates.append(listdate[idx])
            
            data = self.readtable()
            newlistselect = [False] * len(data['Name'])
            for idx, di in enumerate(self.SLClist['Date1']):
                datestr = di.split('T')[0]
                if datestr in selecteddates:
                    newlistselect[idx] = True
            
            data['Selected'] = newlistselect
            self.model = PandasTableModel(data)
            self.pdtable.setModel(self.model)
            self.updatebtdw()

    def clickcell(self):
        """Event when cell is clicked"""
        selectedidx = np.unique([index.row() for index in self.pdtable.selectedIndexes()])[0]
        data = self.readtable()

        if self.modeSafe.isChecked():
            newidx = []
            for idx, di in enumerate(self.SLClist['Date1']):
                if self.SLClist['Date1'][selectedidx].split('T')[0] == di.split('T')[0]:
                    newidx.append(idx)
        else:
            newidx = [selectedidx]

        oldvalue = data['Selected'][selectedidx]
        for idx in newidx:
            if oldvalue == True:
                data['Selected'][idx] = False
            else:
                data['Selected'][idx] = True
        self.model = PandasTableModel(data)
        self.pdtable.setModel(self.model)
        self.updatebtdw()

    def updatetable(self,list):
        data = self.readtable()
        data['Downloaded'] = list
        self.model = PandasTableModel(data)
        self.pdtable.setModel(self.model)
        # self.pdtable.resizeColumnsToContents()

        self.pdtable.rowViewportPosition(30)
        # self.pdtable.scrollTo(self.pdtable.selectRow(1))

    def checkSLC(self):
        """check the SLC"""
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try: 
            job = ez.load(self.pathjobfile,verbose=False)
            len(job.SLClist['Name'])
            data = self.readtable()
            try: 
                job.checkSLClist(verbose=False)
                if not self.parent == None:
                    self.parent.updatelog()
                QApplication.restoreOverrideCursor()
                datadict = {'File': job.SLClist['Name'],
                    'SizeMB': job.SLClist['SizeMB'],
                    'Downloaded': job.SLClist['Stored'],
                    'Selected': data['Selected'],
                    }

                data = pd.DataFrame.from_dict(datadict)
                self.model = PandasTableModel(data)
                self.pdtable.setModel(self.model)
                reply = QMessageBox.information(self, "EZ-InSAR Information",
                    'The SLC list seems fine.',
                    QMessageBox.Ok)
            except:
                QApplication.restoreOverrideCursor()
                reply = QMessageBox.critical(self, "EZ-InSAR Error",
                    'Error during the verification of the SLC list. Please see the log.',
                    QMessageBox.Ok)
    
        except:
            QApplication.restoreOverrideCursor()
            reply = QMessageBox.critical(self, "EZ-InSAR Error",
                    'Error: No SLC list.',
                    QMessageBox.Ok)
            job = None

    def queryadvopt(self):
        """Open the advanced option dialog"""
        reply = AdvOptDialog(self.SLClist['Server'][0], self.advancedoptions)
        reply.exec_()
        self.advancedoptions = reply.advancedoptions

    def updatebtdw(self): # And the estimated time button
        """Update the button status"""
        data = self.readtable()
        if not True in data['Selected'].to_list():
            self.btdwSLC.setEnabled(False)
            self.btTimeest.setEnabled(False)
        else:
            self.btdwSLC.setEnabled(True)
            self.btTimeest.setEnabled(True)

    def messageerror(self,msg):
        reply = QMessageBox.critical(self, "EZ-InSAR Error",
                msg,
                QMessageBox.Ok)
        
    def messagesuccess(self,msg):
        reply = QMessageBox.information(self, "EZ-InSAR Information",
                msg,
                QMessageBox.Ok)
        
    def stopcurrentworker(self):
        """Stop the current worker"""
        self.workerprocess = None
        self.setEnabled(True)

    def lauchSLCdw(self):
        """Start the dowloading (SLC)"""
        listdate = []
        for datei in self.SLClist['Date1']:
            listdate.append(datei.split('T')[0])
        listdateunique = np.unique(listdate)

        indexselected = []
        for idx, di in enumerate(self.readtable()['Selected']):
            if di == True:
                d1 = self.SLClist['Date1'][idx].split('T')[0]
                indexselected.append(listdateunique.tolist().index(d1))
        indexselected = np.sort(indexselected).tolist()

        reply = IDquery(self.SLClist['Server'][0],'image')
        reply.exec_()

        if reply.success:
            job = ez.load(self.pathjobfile,verbose=False)
            logfile = job.log
            job = None
                
            if self.parent == None:
                if self.workerprocess == None:
                    self.setEnabled(False)
                    self.workerprocess = SARDownloadWorker.Worker(self.pathjobfile, reply, self.advancedoptions, mode='image',indexdate = indexselected)
                    self.threadprocess = QThread()
                    self.workerprocess.moveToThread(self.threadprocess)
                    self.threadprocess.started.connect(self.workerprocess.run)
                    self.workerprocess.currentSLClist.connect(self.updatetable)
                    self.workerprocess.finished.connect(self.threadprocess.quit)
                    self.workerprocess.error.connect(self.messageerror)
                    self.workerprocess.success.connect(self.messagesuccess)
                    self.workerprocess.finished.connect(self.stopcurrentworker)      
                    self.threadprocess.start()
                else:
                    self.messageerror('There already is a current processing. Please stop it before running another one.')

            else:
                if self.parent.workerprocess == None:
                    self.parent.dockprogressbar.show()

                    self.setEnabled(False)
                    self.parent.workerprocess = SARDownloadWorker.Worker(self.pathjobfile, reply, self.advancedoptions, mode='image', indexdate = indexselected)
                    self.parent.threadprocess = QThread()
                    self.parent.workerprocess.moveToThread(self.parent.threadprocess)
                    self.parent.threadprocess.started.connect(self.parent.workerprocess.run)
                    self.parent.workerprocess.finished.connect(self.parent.threadprocess.quit)
                    self.parent.workerprocess.textSignal.connect(self.parent.updateTextEditverbose)
                    self.parent.workerprocess.progress.connect(self.parent.updateprogressbar)
                    self.parent.workerprocess.error.connect(self.parent.messageerror)
                    self.parent.workerprocess.success.connect(self.parent.messagesuccess)
                    self.parent.workerprocess.finished.connect(self.parent.stopcurrentworker)   
                    self.parent.workerprocess.success.connect(self.parent.stopcurrentworker)

                    # Initiate the loggin worker/thread
                    self.parent.workerlog = logWorker.Worker(logfile,self.parent.workerprocess)
                    self.parent.threadlog = QThread()
                    self.parent.workerlog.moveToThread(self.parent.threadlog)
                    self.parent.workerlog.textSignal.connect(self.parent.updateTextEditverbose)
                    self.parent.threadlog.started.connect(self.parent.workerlog.run)
                    self.parent.workerlog.finished.connect(self.parent.threadlog.quit)

                    # Start both workers
                    self.parent.threadprocess.start()
                    self.parent.threadlog.start()
                    self.parent.qtCancel.setEnabled(True)

                else:
                    self.messageerror('There already is a current processing. Please stop it before running another one.')

    def lauchorbitdw(self):
        """Start the dowloading (Orbit)"""
        reply = IDquery(self.SLClist['Server'][0],'orbit')
        reply.exec_()

        if reply.success:
            job = ez.load(self.pathjobfile,verbose=False)
            logfile = job.log
            job = None
                
            if self.parent == None:
                if self.workerprocess == None:
                    self.setEnabled(False)
                    self.workerprocess = SARDownloadWorker.Worker(self.pathjobfile, reply, self.advancedoptions, mode='orbit')
                    self.threadprocess = QThread()
                    self.workerprocess.moveToThread(self.threadprocess)
                    self.threadprocess.started.connect(self.workerprocess.run)
                    self.workerprocess.finished.connect(self.threadprocess.quit)
                    self.workerprocess.error.connect(self.messageerror)
                    self.workerprocess.success.connect(self.messagesuccess)
                    self.workerprocess.finished.connect(self.stopcurrentworker)      
                    self.threadprocess.start()
                else:
                    self.messageerror('There already is a current processing. Please stop it before running another one.')

            else:
                if self.parent.workerprocess == None:
                    self.parent.dockprogressbar.show()
                    self.setEnabled(False)
                    self.parent.workerprocess = SARDownloadWorker.Worker(self.pathjobfile, reply, self.advancedoptions, mode='orbit')
                    self.parent.threadprocess = QThread()
                    self.parent.workerprocess.moveToThread(self.parent.threadprocess)
                    self.parent.threadprocess.started.connect(self.parent.workerprocess.run)
                    self.parent.workerprocess.finished.connect(self.parent.threadprocess.quit)
                    self.parent.workerprocess.textSignal.connect(self.parent.updateTextEditverbose)
                    self.parent.workerprocess.progress.connect(self.parent.updateprogressbar)
                    self.parent.workerprocess.error.connect(self.parent.messageerror)
                    self.parent.workerprocess.success.connect(self.parent.messagesuccess)
                    self.parent.workerprocess.finished.connect(self.parent.stopcurrentworker)   
                    self.parent.workerprocess.success.connect(self.parent.stopcurrentworker)

                    # Initiate the loggin worker/thread
                    self.parent.workerlog = logWorker.Worker(logfile,self.parent.workerprocess)
                    self.parent.threadlog = QThread()
                    self.parent.workerlog.moveToThread(self.parent.threadlog)
                    self.parent.workerlog.textSignal.connect(self.parent.updateTextEditverbose)
                    self.parent.threadlog.started.connect(self.parent.workerlog.run)
                    self.parent.workerlog.finished.connect(self.parent.threadlog.quit)

                    # Start both workers
                    self.parent.qtCancel.setEnabled(True)
                    self.parent.threadprocess.start()
                    self.parent.threadlog.start()

                else:
                    self.messageerror('There already is a current processing. Please stop it before running another one.')

    def lauchetaddw(self):
        """Start the dowloading (ETAD)"""
        reply = IDquery('Copernicus','etad')
        reply.exec_()

        if reply.success:
            job = ez.load(self.pathjobfile,verbose=False)
            logfile = job.log
            job = None
                
            if self.parent == None:
                if self.workerprocess == None:
                    self.setEnabled(False)
                    self.workerprocess = SARDownloadWorker.Worker(self.pathjobfile, reply, self.advancedoptions, mode='etad')
                    self.threadprocess = QThread()
                    self.workerprocess.moveToThread(self.threadprocess)
                    self.threadprocess.started.connect(self.workerprocess.run)
                    self.workerprocess.finished.connect(self.threadprocess.quit)
                    self.workerprocess.error.connect(self.messageerror)
                    self.workerprocess.success.connect(self.messagesuccess)
                    self.workerprocess.finished.connect(self.stopcurrentworker)      
                    self.threadprocess.start()
                else:
                    self.messageerror('There already is a current processing. Please stop it before running another one.')

            else:
                if self.parent.workerprocess == None:
                    self.parent.dockprogressbar.show()
                    self.setEnabled(False)
                    self.parent.workerprocess = SARDownloadWorker.Worker(self.pathjobfile, reply, self.advancedoptions, mode='etad')
                    self.parent.threadprocess = QThread()
                    self.parent.workerprocess.moveToThread(self.parent.threadprocess)
                    self.parent.threadprocess.started.connect(self.parent.workerprocess.run)
                    self.parent.workerprocess.finished.connect(self.parent.threadprocess.quit)
                    self.parent.workerprocess.textSignal.connect(self.parent.updateTextEditverbose)
                    self.parent.workerprocess.progress.connect(self.parent.updateprogressbar)
                    self.parent.workerprocess.error.connect(self.parent.messageerror)
                    self.parent.workerprocess.success.connect(self.parent.messagesuccess)
                    self.parent.workerprocess.finished.connect(self.parent.stopcurrentworker)   
                    self.parent.workerprocess.success.connect(self.parent.stopcurrentworker)

                    # Initiate the loggin worker/thread
                    self.parent.workerlog = logWorker.Worker(logfile,self.parent.workerprocess)
                    self.parent.threadlog = QThread()
                    self.parent.workerlog.moveToThread(self.parent.threadlog)
                    self.parent.workerlog.textSignal.connect(self.parent.updateTextEditverbose)
                    self.parent.threadlog.started.connect(self.parent.workerlog.run)
                    self.parent.workerlog.finished.connect(self.parent.threadlog.quit)

                    # Start both workers
                    self.parent.qtCancel.setEnabled(True)
                    self.parent.threadprocess.start()
                    self.parent.threadlog.start()

                else:
                    self.messageerror('There already is a current processing. Please stop it before running another one.')
   
   
###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not os.path.isfile(args['--file']):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No file',None))
    
    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the SAR downloader from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        widget = Downloader(os.path.abspath(args['--file']))
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()


