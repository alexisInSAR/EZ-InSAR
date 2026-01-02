#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Create the display widget

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Mar. 2025

"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtWidgets import QApplication, QCheckBox, QGridLayout, QLabel, QMessageBox, QComboBox, QPushButton, QWidget, QFileSystemModel, QTreeView,  QMenu, QTextEdit, QAction, QDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView

import os, sys
import shutil

from ezinsar import constants
from ezinsar.tools import ezinsardata
import ezinsar.job as ez
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule.display import imageWidget, mapWidget
from ezinsardesktopmodule.interface.pluginsWidget import openTSDisplayer

###########################################################################################
## Classes
###########################################################################################
class InfoDial(QDialog):
    def __init__(self,title,message,detailedtext):
        super(InfoDial, self).__init__()
        self.setWindowTitle(title)
        self.resize(700,350)
        self.setStyleSheet(__theme__)

        layout = QGridLayout()
        messlabel1 = QLabel('<b>Directory:</b>')
        messlabel2 = QLabel('<b>File:</b>')
        mess1 = QLabel(os.path.dirname(message))
        mess2 = QLabel(message.split(os.sep)[-1])

        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(detailedtext)
        layout.addWidget(messlabel1,0,0,1,1)
        layout.addWidget(messlabel2,1,0,1,1)
        layout.addWidget(mess1,0,1,1,1)
        layout.addWidget(mess2,1,1,1,1)
        layout.addWidget(text,2,0,1,2)
        self.setLayout(layout)

class displayer(QWidget):
    """Main class"""

    def __init__(self,file,parent=None):
        """Initialisation"""
        super(displayer, self).__init__()

        self.file = file
        self.setStyleSheet(__theme__)
        self.parent = parent

        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p><b>File<\b>: %s</p>' % ( self.file.split(os.sep)[-1]))
        btQuit = QPushButton("Close", self)
        btQuit.clicked.connect(self.closemaybe)

        type = tools.detect_file_type(file)
        checkimage, _ = tools.checkGDALimage(file)

        if (('image data' in type) or ('bitmap' in type)) and checkimage == False: 
            self.object = imageWidget.imagedisplayer(file)

        elif file.endswith('.bmp') and checkimage == False: 
            self.object = imageWidget.imagedisplayer(file)

        elif checkimage == True:
            self.object = mapWidget.mapdisplayer(file)
            
        elif 'ASCII text' in type:
            self.object = QTextEdit()
            with open(file,'r') as fi: 
                lines = fi.readlines()
            self.object.setText(''.join(lines))

            btsave = QPushButton("Save", self)
            btsave.clicked.connect(self.save_txt)

        elif file.endswith('.eidata'):
            tmp = ezinsardata.loadEZdata(file,partialreading = ['classtype'])
            if tmp.classtype['value'] == 'displacement':
                try: # Check if the module is available
                    from ezinsartsdisplayermodule import __file__
                    self.object = QLabel('<p><b>Please open the Time-series Displayer via the tool panel.</b></p>')
                except:
                    self.object = QLabel('<p><b>Please install the EZ-InSAR TSDisplayer Module for EZ-InSAR.</b></p>')
            else:
                if os.path.isfile(self.parent.curEZInSARjob):
                    job = ez.load(self.parent.curEZInSARjob,verbose=False)
                    log = job.log
                    job = None
                else:
                    log = None
                from ezinsardesktopmodule.display import insituWidget 
                self.object = insituWidget.insitudisplay(file,log=log,parent=self.parent)

        elif file.endswith('.pdf'):
            import webbrowser
            webbrowser.open_new(file)
            self.object = QLabel('<p><b>The .pdf is currently opened in this webbrowser.</b></p>')
            # self.object = QWebEngineView() 
            # self.object.load(QUrl.fromLocalFile(os.path.abspath(file)))

        else: 
            self.object = QLabel('<p><b>NOT COMPATIBLE WITH EZ-INSAR.</b></p>')

        layout = QGridLayout()

        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 6)
        layout.addWidget(self.object, 1, 0, 9, 10)

        if 'ASCII text' in type:
            layout.addWidget(btsave, 12, 9, 1, 1)

        layout.addWidget(btQuit, 0, 9, 1, 1)
    
        self.setLayout(layout)

    def save_txt(self):
        """Save the txt file"""
        ret = QMessageBox.warning(self, "Quit?",
                "Do you want to save your changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if ret == QMessageBox.Save:
            with open(self.file,'w') as fout: 
                fout.write('%s\n' % (self.object.toPlainText()))
        
    def closemaybe(self):
        """Close event"""
        return self.close()
        
class datatree(QWidget):
    """Main class"""
    
    def __init__(self,curEZInSARjob, parent = None):
        """Initialisation"""
        super(datatree, self).__init__()
        self.curEZInSARjob = curEZInSARjob
        self.list = None
        self.curdir = None 
        self.listwk = None
        self.menu = None
        self.parent = parent
        
        self.setStyleSheet(__theme__)
        self.checkwk()
        
        layout = QGridLayout()

        self.listwk = QComboBox()
        self.listwk.addItems(self.list)
        self.allfiles = QCheckBox('Show all files')
        self.allfiles.setChecked(True)
        self.listwk.currentIndexChanged.connect(self.updatetree)
        self.allfiles.clicked.connect(self.updatetree)
        
        self.tree = QTreeView()
        self.updatetree()

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.openMenu)
        self.tree.doubleClicked.connect(self.openfromfile)
    
        layout.addWidget(self.listwk,0,0,1,3)
        layout.addWidget(self.allfiles,1,0,1,3)
        layout.addWidget(self.tree,2,0,5,3)

        self.setLayout(layout)

        job = None
     
    def openMenu(self,position):
        """Open the menu"""
        self.menu = QMenu()

        index = self.tree.currentIndex()
        
        if self.listwk.currentText() == 'SLC Directory':
            self.menu.addAction(QAction("Information", self,
                                        statusTip="",
                                        triggered=self.contextmenuaction)) 

        if os.path.isdir(self.model.filePath(index)):
            self.menu.addAction(QAction("Delete it", self,
                                        statusTip="",
                                        triggered=self.contextmenuaction)) 
        elif os.path.isfile(self.model.filePath(index)):
            if not self.listwk.currentText() == 'SLC Directory':
                self.menu.addAction(QAction("Open it", self,
                                            statusTip="",
                                            triggered=self.contextmenuaction))
                
                if self.model.filePath(index).endswith('.eidata'):
                    try: # Check if the module is available
                        from ezinsartsdisplayermodule import __file__
                        self.menu.addAction(QAction("Open it with the Time-Series Displayer", self,
                                            statusTip="",
                                            triggered=self.contextmenuaction))
                    except:
                        a = 'dummy'

                self.menu.addAction(QAction("Information", self,
                                            statusTip="",
                                            triggered=self.contextmenuaction)) 

            self.menu.addAction(QAction("Delete it", self,
                                        statusTip="",
                                        triggered=self.contextmenuaction)) 

        self.menu.exec_(self.tree.viewport().mapToGlobal(position))
         

    def updatetree(self):
        """Update the tree"""
        job = ez.load(self.curEZInSARjob,verbose=False)

        if self.listwk.currentText() == 'Work Directory':
            self.curdir = job.workdirectory
        elif self.listwk.currentText() == 'Coreg. Work Directory':
            self.curdir = job.coregistration.workdirectory
        elif self.listwk.currentText() == 'Ifg. Work Directory':
            self.curdir = job.ifgstack.workdirectory
        elif self.listwk.currentText() == 'TS Work Directory':
            self.curdir = job.tsprocessing.workdirectory
        elif self.listwk.currentText() == 'Int. Work Directory':
            self.curdir = job.intstack.workdirectory
        elif self.listwk.currentText() == 'SLC Directory':
            self.curdir = job.pathSLC
        elif self.listwk.currentText() == 'Orbit Directory':
            self.curdir = job.pathorbit
        elif self.listwk.currentText() == 'Aux. Directory':
            self.curdir = job.pathaux
        elif self.listwk.currentText() == 'DEM Directory':
            self.curdir = job.pathDEM
        
        self.model = QFileSystemModel()
        self.model.setRootPath(self.curdir)
        if not self.allfiles.isChecked():
            self.model.setNameFilters(['*.jpg','*.ras','*.png','*.'+job.nameDEM.split('.')[-1],'*.tif','*.bmp'])
            self.model.setNameFilterDisables(False)
        else:
            self.model.setNameFilters([])
            self.model.setNameFilterDisables(True)

        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.curdir))
        self.tree.setColumnWidth(0, 250)
        self.tree.setAlternatingRowColors(True)

        job = None

    def checkwk(self):
        """Check the work directories"""
        self.list = ['Work Directory']
        job = ez.load(self.curEZInSARjob,verbose=False)
        if not job.pathSLC == None: 
            if os.path.isdir(job.pathSLC):
                self.list.append('SLC Directory')
        if not job.pathorbit == None: 
            if os.path.isdir(job.pathorbit):
                self.list.append('Orbit Directory')
        if not job.pathaux == None: 
            if os.path.isdir(job.pathaux):
                self.list.append('Aux. Directory')
        if not job.pathDEM == None: 
            if os.path.isdir(job.pathDEM):
                self.list.append('DEM Directory')
        if not job.coregistration == None:
            if os.path.isdir(job.coregistration.workdirectory):
                self.list.append('Coreg. Work Directory')
        if not job.ifgstack == None:
            if os.path.isdir(job.ifgstack.workdirectory):
                self.list.append('Ifg. Work Directory')
        if not job.tsprocessing == None:
            if os.path.isdir(job.tsprocessing.workdirectory):
                self.list.append('TS Work Directory')
        if not job.intstack == None:
            if os.path.isdir(job.intstack.workdirectory):
                self.list.append('Int. Work Directory')
        job = None

    def contextmenuaction(self):
        """Menu context callbacks"""
        if self.sender().text() == 'Open it': 
            self.openfromfile()
        elif self.sender().text() == 'Open it with the Time-Series Displayer': 
            self.openTSDisplayerfromparent()
        elif self.sender().text() == 'Delete it': 
            self.deletefile()
        elif self.sender().text() == 'Information':
            self.getinfo()

    def getinfo(self):
        index = self.tree.currentIndex()
        type = tools.detect_file_type(self.model.filePath(index))

        if not self.listwk.currentText() == 'SLC Directory':
            if ('image data' in type) or ('data' in type):
                checkimage, metadata = tools.checkGDALimage(self.model.filePath(index))
            else:
                metadata = 'No information'
        else:
            job = ez.load(self.curEZInSARjob,verbose=False)

            try:
                strtext = 'No information'
                for idxrow, row in job.SLClist.iterrows():
                    if row['Name'] == self.model.filePath(index).split(os.sep)[-1]:
                        strtext = ''
                        for keyi in row.keys():
                            if not keyi == 'Quicklook':
                                strtext = strtext + '<p><b>%s:</b> %s</p>' % (keyi, row[keyi])
                        break
            except:
                    strtext = 'No information'

            metadata = strtext

        metawin = InfoDial('Information','%s' % (self.model.filePath(index)),metadata)
        metawin.show()
        metawin.exec_()

    def openfromfile(self):
        """Callback: open the file"""
        index = self.tree.currentIndex()        
        if os.path.isfile(self.model.filePath(index)):
            if not self.parent.curwidget == None:
                self.parent.curwidget.close()
                self.parent.curwidget = None

            self.parent.curwidget = displayer(self.model.filePath(index),parent=self.parent)
            self.parent.mainlayout.addWidget(self.parent.curwidget,0,0)

    def openTSDisplayerfromparent(self):
        index = self.tree.currentIndex()        
        if os.path.isfile(self.model.filePath(index)):
            openTSDisplayer(self.model.filePath(index)) #Goes to Plugins functions

    def deletefile(self):
        """Callback: delete the file"""
        ret = QMessageBox.warning(self, "Delete?",
                "Are you sure to delete it?",
                QMessageBox.Ok | QMessageBox.Cancel)
        
        if ret == QMessageBox.Ok: 
            index = self.tree.currentIndex()
            if os.path.isfile(self.model.filePath(index)):
                os.remove(self.model.filePath(index))
            elif os.path.isdir(self.model.filePath(index)):
                shutil.rmtree(self.model.filePath(index))

####################################
## For debug
####################################
if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = datatree('/Users/alexis_hrysiewicz/Test_DIR/Test_Desktop/testetna.ei')
    widget.show()
    sys.exit(app.exec_())

