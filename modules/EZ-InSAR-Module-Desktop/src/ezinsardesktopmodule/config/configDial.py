#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a dialog for EZ-InSAR configuration

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.2: Add the conda env variables in the configuration, Oct. 2025, AH
    * 1.0.0: Initial version, Feb. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a dialog for EZ-InSAR configuration

usage: 
    ezinsardesktop_config

"""
###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QDialog, QPushButton, QGroupBox, QScrollArea, QProgressDialog, QMessageBox, QTabWidget, QWidget, QListWidget, QCheckBox, QSpinBox, QComboBox, QLineEdit

import os, sys
import pandas as pd

from ezinsar import constants
from ezinsar.tools import miscellaneous 
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config import settings, themes
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule.tools.docsWidget import DocsDialog

###########################################################################################
## EPSGcodeDial class
###########################################################################################
class configDial(QDialog):
    """QDialog class 

        Build the dialog window
    """
    def __init__(self, parent=None):
        super(configDial, self).__init__(parent)

        self.parent = parent
        self.validation = False
        self.resize(1500,750)

        self.setStyleSheet(__theme__)
        
        mainLayout = QGridLayout()

        tabs = QTabWidget() 
        tabs.tabBar().setExpanding(True)

        ###############################################################################################
        tab0 = QScrollArea()
        tab0.setWidgetResizable(True)
        tab0widget = QWidget()
        tab0.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tab0.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        tab0layout = QGridLayout()

        ## For the EZ-InSAR core module 
        grp0 = QGroupBox('EZ-InSAR core Module')
        grp0Layout = QGridLayout()
        vi = miscellaneous.checkmodule('ezinsar',type='core',checkupdate=False)

        for idx, vari in enumerate(list(vi.keys())):
            grp0Layout.addWidget(QLabel('<b>%s</b>' % (vari)),idx,1,1,1,Qt.AlignLeft)
            grp0Layout.addWidget(QLabel('%s' % (vi[vari])),idx,2,1,1,Qt.AlignRight)
        grp0.setLayout(grp0Layout)
        tab0layout.addWidget(grp0,0,0,1,1)

        ## For the EZ-InSAR processor modules 
        grp1 = QGroupBox('EZ-InSAR Processor Modules')
        grp1Layout = QGridLayout()

        for idx, modi in enumerate(miscellaneous.listmodule('processor')):
            exec("grp1_%s = QGroupBox()" % (modi))
            exec("grp1_%sLayout = QGridLayout()" % (modi))

            vi = miscellaneous.checkmodule(modi,type='processor',checkupdate=False)
            for idx2, vari in enumerate(list(vi.keys())):
                if not 'versionUpdate' in vari: 
                    tmp = QLabel('<b>%s</b>' % (vari))
                    exec("grp1_%sLayout.addWidget(tmp,idx2,0,1,1,Qt.AlignLeft)" % (modi))
                    tmp = QLabel('%s' % (vi[vari]))
                    exec("grp1_%sLayout.addWidget(tmp,idx2,1,1,1,Qt.AlignRight)" % (modi))

            exec("grp1_%s.setLayout(grp1_%sLayout)" % (modi,modi))
            exec("grp1Layout.addWidget(grp1_%s,idx,0)" % (modi))
        grp1.setLayout(grp1Layout)    
        tab0layout.addWidget(grp1,1,0,1,1)

        ## For the EZ-InSAR sensors modules
        grp1 = QGroupBox('EZ-InSAR Sensor Modules')
        grp1Layout = QGridLayout()

        for idx, modi in enumerate(miscellaneous.listmodule('sensor')):
            exec("grp1_%s = QGroupBox()" % (modi))
            exec("grp1_%sLayout = QGridLayout()" % (modi))

            vi = miscellaneous.checkmodule(modi,type='sensor',checkupdate=False)
            for idx2, vari in enumerate(list(vi.keys())):
                if not 'versionUpdate' in vari:
                    tmp = QLabel('<b>%s</b>' % (vari))
                    exec("grp1_%sLayout.addWidget(tmp,idx2,0,1,1,Qt.AlignLeft)" % (modi))
                    tmp = QLabel('%s' % (vi[vari]))
                    exec("grp1_%sLayout.addWidget(tmp,idx2,1,1,1,Qt.AlignRight)" % (modi))

            exec("grp1_%s.setLayout(grp1_%sLayout)" % (modi,modi))
            exec("grp1Layout.addWidget(grp1_%s,idx,0)" % (modi))
        grp1.setLayout(grp1Layout)    
        tab0layout.addWidget(grp1,2,0,1,1)

        ## For the EZ-InSAR sensors modules
        grp1 = QGroupBox('EZ-InSAR Optional Modules')
        grp1Layout = QGridLayout()

        for idx, modi in enumerate(constants.__EZInSARoptionalmodule__):
            try:  
                vi = miscellaneous.checkmodule(modi,type='optional',checkupdate=False)
                exec("grp1_%s = QGroupBox()" % (modi))
                exec("grp1_%sLayout = QGridLayout()" % (modi))

                for idx2, vari in enumerate(list(vi.keys())):
                    if not 'versionUpdate' in vari:
                        tmp = QLabel('<b>%s</b>' % (vari))
                        exec("grp1_%sLayout.addWidget(tmp,idx2,0,1,1,Qt.AlignLeft)" % (modi))
                        tmp = QLabel('%s' % (vi[vari]))
                        exec("grp1_%sLayout.addWidget(tmp,idx2,1,1,1,Qt.AlignRight)" % (modi))

                exec("grp1_%s.setLayout(grp1_%sLayout)" % (modi,modi))
                exec("grp1Layout.addWidget(grp1_%s,idx,0)" % (modi))
            except:
                a = 'dummy'
        grp1.setLayout(grp1Layout)    
        tab0layout.addWidget(grp1,3,0,1,1)
        tab0widget.setLayout(tab0layout)
        tab0.setWidget(tab0widget)
        tabs.addTab(tab0, "EZ-InSAR Modules")

        ###############################################################################################
        tab1 = QScrollArea()
        tab1.setWidgetResizable(True)
        tab1widget = QWidget()
        tab1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tab1.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        tab1layout = QGridLayout()

        desktopsettings = QGroupBox('EZ-InSAR Desktop Settings')
        desktopsettingsLayout = QGridLayout()

        dockerLabel = QLabel('<p><b>Docker Container Mode:</b></p>')
        dockerLabel.setToolTip("""
                            <p>Enable the EZ-InSAR running inside Docker container.</p> 
                            """)
        self.dockerrep = QCheckBox('Enable the mode')
        self.dockerrep.setEnabled(True)
        self.dockerrep.setChecked(settings.__docker_running__)

        FoliumTilesLabel = QLabel('<p><b>Unlocked Folium tiles:</b></p>')
        FoliumTilesLabel.setToolTip("""
                            <p>Unlock numerous Folium tiles.</p> 
                            """)
        self.FoliumTiles = QCheckBox('Add the supplementary tiles')
        self.FoliumTiles.setChecked(settings.__UnlockTiles__)
        self.FoliumTiles.clicked.connect(self.msgtiles)

        FoliumCachedLabel = QLabel('<p><b>Cache the Folium map:</b></p>')
        FoliumCachedLabel.setToolTip("""
                            <p>By caching the Folium map, EZ-InSAR will bypass the 2MB limit.</p> 
                            <p>This feature will be enabled for a limited number of Folium maps</p> 
                            """)
        self.FoliumCached = QCheckBox('Enable this feature')
        self.FoliumCached.setChecked(settings.__foliumCached__)

        PlotlyCachedLabel = QLabel('<p><b>Cache the Plotly figure:</b></p>')
        PlotlyCachedLabel.setToolTip("""
                            <p>By caching the Plotly figureap, EZ-InSAR will bypass the 2MB limit.</p> 
                            <p>This feature will be enabled for a limited number of Folium maps</p> 
                            """)
        self.PloltlyCached = QCheckBox('Enable this feature')
        self.PloltlyCached.setChecked(settings.__plotlyCached__)

        updatetimeLabel = QLabel('<p><b>GUI Updating Time [ms]:</b></p>')
        self.updatetime = QSpinBox()
        self.updatetime.setMinimum(200)
        self.updatetime.setMaximum(5000)
        self.updatetime.setValue(int(settings.__Updatetime__*1000))

        nblinelogLabel = QLabel('<p><b>Number of lines in live log:</b></p>')
        self.nblinelog = QSpinBox()
        self.nblinelog.setMinimum(100)
        self.nblinelog.setMaximum(10000)
        self.nblinelog.setValue(int(settings.__nbLineLog__))

        cpuupdatetimeLabel = QLabel('<p><b>CPU/RAW Monitor Updating Time [ms]:</b></p>')
        self.cpuupdatetime = QSpinBox()
        self.cpuupdatetime.setMinimum(200)
        self.cpuupdatetime.setMaximum(5000)
        self.cpuupdatetime.setValue(int(settings.__Cputime__*1000))

        themeLabel = QLabel('<p><b>Layout theme:</b></p>')
        self.theme = QComboBox()
        self.theme.addItems(themes.list_themes)
        
        with open(__file__.replace('configDial.py','settings.py'),'r') as fi:
            for line in fi.readlines():
                themecurrent = pd.read_csv(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'desktop.config',delimiter='::',header=None,engine='python',names=['Variable','Value'])['Value'][0]
                break
        try:
            self.theme.setCurrentIndex(themes.list_themes.index(themecurrent))
        except:
            self.theme.setCurrentIndex(themes.list_themes.index('default'))
        self.theme.currentTextChanged.connect(self.themepreview)

        desktopsettingsLayout.addWidget(dockerLabel,0,0,1,1)
        desktopsettingsLayout.addWidget(self.dockerrep,0,1,1,1)

        desktopsettingsLayout.addWidget(FoliumTilesLabel,1,0,1,1)
        desktopsettingsLayout.addWidget(self.FoliumTiles,1,1,1,1)

        desktopsettingsLayout.addWidget(FoliumCachedLabel,2,0,1,1)
        desktopsettingsLayout.addWidget(self.FoliumCached,2,1,1,1)

        desktopsettingsLayout.addWidget(PlotlyCachedLabel,3,0,1,1)
        desktopsettingsLayout.addWidget(self.PloltlyCached,3,1,1,1)

        desktopsettingsLayout.addWidget(updatetimeLabel,4,0,1,1)
        desktopsettingsLayout.addWidget(self.updatetime,4,1,1,1)

        desktopsettingsLayout.addWidget(nblinelogLabel,5,0,1,1)
        desktopsettingsLayout.addWidget(self.nblinelog,5,1,1,1)

        desktopsettingsLayout.addWidget(cpuupdatetimeLabel,6,0,1,1)
        desktopsettingsLayout.addWidget(self.cpuupdatetime,6,1,1,1)

        desktopsettingsLayout.addWidget(themeLabel,7,0,1,1)
        desktopsettingsLayout.addWidget(self.theme,7,1,1,1)

        desktopsettings.setLayout(desktopsettingsLayout)

        ezinsarsettings = QGroupBox('EZ-InSAR Settings')
        ezinsarsettingsLayout = QGridLayout()
        

        ## EZ-InSAR setting: commun
        tabsSETEZINSAR = QTabWidget() 
        tabsSETEZINSARglobal = QScrollArea()
        tabsSETEZINSARglobal.setWidgetResizable(True)
        tabsSETEZINSARglobalwidget = QWidget()
        tabsSETEZINSARgloballayout = QGridLayout()
        tabsSETEZINSARglobal.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tabsSETEZINSARglobal.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        label_cache = QLabel('<p><b>Cache of EZ-InSAR:</b></p>')
        self.value_cache = QLineEdit(constants.__cachedir__)
        tabsSETEZINSARgloballayout.addWidget(label_cache,0,0)
        tabsSETEZINSARgloballayout.addWidget(self.value_cache,0,1)

        label_defautprocessor = QLabel('<p><b>Default processor:</b></p>')
        self.value_defautprocessor = QComboBox()
        self.value_defautprocessor.addItems(['isce2','doris','snap','gamma','licsbas'])
        self.value_defautprocessor.setCurrentIndex(['isce2','doris','snap','gamma','licsbas'].index(constants.__defautprocessor__))
        tabsSETEZINSARgloballayout.addWidget(label_defautprocessor,1,0)
        tabsSETEZINSARgloballayout.addWidget(self.value_defautprocessor,1,1)

        label_nameDockerImage = QLabel('<p><b>Name of the Docker image:</b></p>')
        self.value_nameDockerImage = QLineEdit(constants.__nameDockerImage__)
        tabsSETEZINSARgloballayout.addWidget(label_nameDockerImage,2,0)
        tabsSETEZINSARgloballayout.addWidget(self.value_nameDockerImage,2,1)

        label_loggingmode = QLabel('<p><b>Logging levels:</b></p>')

        self.value_loggingmode = QComboBox()
        self.value_loggingmode.addItems(['NOTSET','DEBUG','INFO','WARN','ERROR','CRITICAL'])
        self.value_loggingmode.setCurrentIndex(['NOTSET','DEBUG','INFO','WARN','ERROR','CRITICAL'].index(constants.__loggingmode__))
        tabsSETEZINSARgloballayout.addWidget(label_loggingmode,3,0)
        tabsSETEZINSARgloballayout.addWidget(self.value_loggingmode,3,1)

        tabsSETEZINSARgloballayout.addWidget(tabsSETEZINSARglobalwidget)
        tabsSETEZINSARglobal.setLayout(tabsSETEZINSARgloballayout)
        tabsSETEZINSAR.addTab(tabsSETEZINSARglobal, "General")

        ## EZ-InSAR setting: Connection
        tabsSETEZINSARconnect = QScrollArea()
        tabsSETEZINSARconnect.setWidgetResizable(True)
        tabsSETEZINSARconnectwidget = QWidget()
        tabsSETEZINSARconnectlayout = QGridLayout()
        tabsSETEZINSARconnect.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tabsSETEZINSARconnect.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        label_username = QLabel('<p><b>Username:</b></p>')
        self.value_username = QLineEdit(constants.__username__)
        tabsSETEZINSARconnectlayout.addWidget(label_username,0,0)
        tabsSETEZINSARconnectlayout.addWidget(self.value_username,0,1)

        label_password = QLabel('<p><b>Password:</b></p>')
        self.value_password = QLineEdit(constants.__password__)
        self.value_password.setEchoMode(QLineEdit.Password)
        tabsSETEZINSARconnectlayout.addWidget(label_password,1,0)
        tabsSETEZINSARconnectlayout.addWidget(self.value_password,1,1)

        label_S1server = QLabel('<p><b>Sentinel-1 Server:</b></p>')
        self.value_S1server = QComboBox()
        self.value_S1server.addItems(['ASF','Copernicus'])
        self.value_S1server.setCurrentIndex(['ASF','Copernicus'].index(constants.__S1server__))
        tabsSETEZINSARconnectlayout.addWidget(label_S1server,2,0)
        tabsSETEZINSARconnectlayout.addWidget(self.value_S1server,2,1)

        label_wgetlimit = QLabel('<p><b>Wget Limit:</b></p>')
        self.value_wgetlimit = QLineEdit(constants.__wgetlimit__)
        tabsSETEZINSARconnectlayout.addWidget(label_wgetlimit,3,0)
        tabsSETEZINSARconnectlayout.addWidget(self.value_wgetlimit,3,1)

        label_wgetlimitmin = QLabel('<p><b>Wget Limit (Min.):</b></p>')
        self.value_wgetlimitmin = QLineEdit(constants.__wgetlimitmin__)
        tabsSETEZINSARconnectlayout.addWidget(label_wgetlimitmin,4,0)
        tabsSETEZINSARconnectlayout.addWidget(self.value_wgetlimitmin,4,1)

        label_wgetlimitmax = QLabel('<p><b>Wget Limit (Max.):</b></p>')
        self.value_wgetlimitmax = QLineEdit(constants.__wgetlimitmax__)
        tabsSETEZINSARconnectlayout.addWidget(label_wgetlimitmax,5,0)
        tabsSETEZINSARconnectlayout.addWidget(self.value_wgetlimitmax,5,1)

        label_chunksize = QLabel('<p><b>Chunk Size [MB]:</b></p>')
        self.value_chunksize = QLineEdit(str(constants.__chunksize__))
        tabsSETEZINSARconnectlayout.addWidget(label_chunksize,6,0)
        tabsSETEZINSARconnectlayout.addWidget(self.value_chunksize,6,1)

        label_SLCdownloader = QLabel('<p><b>Sentinel-1 Downloader:</b></p>')
        self.value_SLCdownloader = QComboBox()
        self.value_SLCdownloader.addItems(['wget','python'])
        self.value_SLCdownloader.setCurrentIndex(['wget','python'].index(constants.__SLCdownloader__))
        tabsSETEZINSARconnectlayout.addWidget(label_SLCdownloader,7,0)
        tabsSETEZINSARconnectlayout.addWidget(self.value_SLCdownloader,7,1)

        label_sleepSLCdownload = QLabel('<p><b>Sleep time [sec]:</b></p>')
        self.value_sleepSLCdownload = QLineEdit(str(constants.__sleepSLCdownload__))
        tabsSETEZINSARconnectlayout.addWidget(label_sleepSLCdownload,8,0)
        tabsSETEZINSARconnectlayout.addWidget(self.value_sleepSLCdownload,8,1)

        tabsSETEZINSARconnectlayout.addWidget(tabsSETEZINSARconnectwidget)
        tabsSETEZINSARconnect.setLayout(tabsSETEZINSARconnectlayout)
        tabsSETEZINSAR.addTab(tabsSETEZINSARconnect, "Connection")

        ## EZ-InSAR setting: ISCE-2
        tabsSETEZINSARisce2 = QScrollArea()
        tabsSETEZINSARisce2.setWidgetResizable(True)
        tabsSETEZINSARisce2widget = QWidget()
        tabsSETEZINSARisce2layout = QGridLayout()
        tabsSETEZINSARisce2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tabsSETEZINSARisce2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        label_pathisce2 = QLabel('<p><b>ISCE-2 path:</b></p>')
        self.value_pathisce2 = QLineEdit(os.path.dirname(constants.__requirement_ISCE2__[0]))
        tabsSETEZINSARisce2layout.addWidget(label_pathisce2,0,0)
        tabsSETEZINSARisce2layout.addWidget(self.value_pathisce2,0,1)

        label_ISCE2modesymlink = QLabel('<p><b>Use link:</b></p>')
        self.value_ISCE2modesymlink = QComboBox()
        self.value_ISCE2modesymlink.addItems(['True','False'])
        self.value_ISCE2modesymlink.setCurrentIndex(['True','False'].index(str(constants.__ISCE2_modesymlink__)))
        tabsSETEZINSARisce2layout.addWidget(label_ISCE2modesymlink,1,0)
        tabsSETEZINSARisce2layout.addWidget(self.value_ISCE2modesymlink,1,1)

        label_isce2condaenv = QLabel('<p><b>ISCE-2 conda Env.:</b></p>')
        self.value_isce2condaenv = QLineEdit(constants.__mintpycondaenv__)
        tabsSETEZINSARisce2layout.addWidget(label_isce2condaenv,2,0)
        tabsSETEZINSARisce2layout.addWidget(self.value_isce2condaenv,2,1)

        tabsSETEZINSARisce2layout.addWidget(tabsSETEZINSARisce2widget)
        tabsSETEZINSARisce2.setLayout(tabsSETEZINSARisce2layout)
        tabsSETEZINSAR.addTab(tabsSETEZINSARisce2, "ISCE-2")

        ## EZ-InSAR setting: SNAP
        tabsSETEZINSARsnap = QScrollArea()
        tabsSETEZINSARsnap.setWidgetResizable(True)
        tabsSETEZINSARsnapwidget = QWidget()
        tabsSETEZINSARsnaplayout = QGridLayout()
        tabsSETEZINSARsnap.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tabsSETEZINSARsnap.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        label_pathsnappy = QLabel('<p><b>SNAPPY path:</b></p>')
        self.value_pathsnappy = QLineEdit(constants.__requirement_SNAP__)
        tabsSETEZINSARsnaplayout.addWidget(label_pathsnappy,0,0)
        tabsSETEZINSARsnaplayout.addWidget(self.value_pathsnappy,0,1)

        label_pathsnapgpt = QLabel('<p><b>SNAP GPT path:</b></p>')
        self.value_pathsnapgpt = QLineEdit(constants.__requirement_SNAP_GPT__)
        tabsSETEZINSARsnaplayout.addWidget(label_pathsnapgpt,1,0)
        tabsSETEZINSARsnaplayout.addWidget(self.value_pathsnapgpt,1,1)

        label_SNAPcachemax = QLabel('<p><b>SNAP max. cache [MB]:</b></p>')
        self.value_SNAPcachemax = QLineEdit(str(constants.__SNAPcachemax__))
        tabsSETEZINSARsnaplayout.addWidget(label_SNAPcachemax,2,0)
        tabsSETEZINSARsnaplayout.addWidget(self.value_SNAPcachemax,2,1)

        label_SNAPcacheclean = QLabel('<p><b>SNAP cache cleaning:</b></p>')
        self.value_SNAPcacheclean = QComboBox()
        self.value_SNAPcacheclean.addItems(['True','False'])
        self.value_SNAPcacheclean.setCurrentIndex(['True','False'].index(str(constants.__SNAPcacheclean__)))
        tabsSETEZINSARsnaplayout.addWidget(label_SNAPcacheclean,3,0)
        tabsSETEZINSARsnaplayout.addWidget(self.value_SNAPcacheclean,3,1)

        label_SNAPwrapper = QLabel('<p><b>SNAP wrapper:</b></p>')
        self.value_SNAPwrapper = QComboBox()
        self.value_SNAPwrapper.addItems(['snappy','gpt'])
        self.value_SNAPwrapper.setCurrentIndex(['snappy','gpt'].index(constants.__SNAP_wrapper__))
        tabsSETEZINSARsnaplayout.addWidget(label_SNAPwrapper,4,0)
        tabsSETEZINSARsnaplayout.addWidget(self.value_SNAPwrapper,4,1)

        tabsSETEZINSARsnaplayout.addWidget(tabsSETEZINSARsnapwidget)
        tabsSETEZINSARsnap.setLayout(tabsSETEZINSARsnaplayout)
        tabsSETEZINSAR.addTab(tabsSETEZINSARsnap, "SNAP")

        ## EZ-InSAR setting: Doris
        tabsSETEZINSARdoris = QScrollArea()
        tabsSETEZINSARdoris.setWidgetResizable(True)
        tabsSETEZINSARdoriswidget = QWidget()
        tabsSETEZINSARdorislayout = QGridLayout()
        tabsSETEZINSARdoris.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tabsSETEZINSARdoris.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        label_pathdoris = QLabel('<p><b>Doris path:</b></p>')
        self.value_pathdoris = QLineEdit(constants.__requirement_Doris__)
        tabsSETEZINSARdorislayout.addWidget(label_pathdoris,0,0)
        tabsSETEZINSARdorislayout.addWidget(self.value_pathdoris,0,1)

        tabsSETEZINSARdorislayout.addWidget(tabsSETEZINSARdoriswidget)
        tabsSETEZINSARdoris.setLayout(tabsSETEZINSARdorislayout)
        tabsSETEZINSAR.addTab(tabsSETEZINSARdoris, "Doris")

        ## EZ-InSAR setting: StaMPS
        tabsSETEZINSARstamps = QScrollArea()
        tabsSETEZINSARstamps.setWidgetResizable(True)
        tabsSETEZINSARstamps.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tabsSETEZINSARstamps.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        tabsSETEZINSARstampswidget = QWidget()
        tabsSETEZINSARstampslayout = QGridLayout()

        label_pathstamps = QLabel('<p><b>StaMPS path:</b></p>')
        self.value_pathstamps = QLineEdit(os.path.dirname(constants.__requirement_StaMPS__[0]))
        tabsSETEZINSARstampslayout.addWidget(label_pathstamps,0,0)
        tabsSETEZINSARstampslayout.addWidget(self.value_pathstamps,0,1)

        tabsSETEZINSARstampslayout.addWidget(tabsSETEZINSARstampswidget)
        tabsSETEZINSARstamps.setLayout(tabsSETEZINSARstampslayout)
        tabsSETEZINSAR.addTab(tabsSETEZINSARstamps, "StaMPS")

        ## EZ-InSAR setting: LicSBAS
        tabsSETEZINSARlicsbas = QScrollArea()
        tabsSETEZINSARlicsbas.setWidgetResizable(True)
        tabsSETEZINSARlicsbaswidget = QWidget()
        tabsSETEZINSARlicsbaslayout = QGridLayout()
        tabsSETEZINSARlicsbas.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tabsSETEZINSARlicsbas.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        label_pathlicsbas = QLabel('<p><b>LicSBAS path:</b></p>')
        self.value_pathlicsbas = QLineEdit(os.path.dirname(os.path.dirname(constants.__requirement_LiCSBAS__.split(':')[0])))
        tabsSETEZINSARlicsbaslayout.addWidget(label_pathlicsbas,0,0)
        tabsSETEZINSARlicsbaslayout.addWidget(self.value_pathlicsbas,0,1)

        label_licsbascondaenv = QLabel('<p><b>LicSBAS conda Env.:</b></p>')
        self.value_licsbascondaenv = QLineEdit(constants.__licsbascondaenv__)
        tabsSETEZINSARlicsbaslayout.addWidget(label_licsbascondaenv,1,0)
        tabsSETEZINSARlicsbaslayout.addWidget(self.value_licsbascondaenv,1,1)

        tabsSETEZINSARlicsbaslayout.addWidget(tabsSETEZINSARlicsbaswidget)
        tabsSETEZINSARlicsbas.setLayout(tabsSETEZINSARlicsbaslayout)
        tabsSETEZINSAR.addTab(tabsSETEZINSARlicsbas, "LicSBAS")

        ## EZ-InSAR setting: Mintpy
        tabsSETEZINSARmintpy = QScrollArea()
        tabsSETEZINSARmintpy.setWidgetResizable(True)
        tabsSETEZINSARmintpywidget = QWidget()
        tabsSETEZINSARmintpylayout = QGridLayout()
        tabsSETEZINSARmintpy.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tabsSETEZINSARmintpy.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        label_mintpycondaenv = QLabel('<p><b>MintPy Conda Env.:</b></p>')
        self.value_mintpycondaenv = QLineEdit(constants.__mintpycondaenv__)
        tabsSETEZINSARmintpylayout.addWidget(label_mintpycondaenv,0,0)
        tabsSETEZINSARmintpylayout.addWidget(self.value_mintpycondaenv,0,1)

        tabsSETEZINSARmintpylayout.addWidget(tabsSETEZINSARmintpywidget)
        tabsSETEZINSARmintpy.setLayout(tabsSETEZINSARmintpylayout)
        tabsSETEZINSAR.addTab(tabsSETEZINSARmintpy, "MintPy")

        ## EZ-InSAR setting: MiaplPy
        tabsSETEZINSARmiaplpy = QScrollArea()
        tabsSETEZINSARmiaplpy.setWidgetResizable(True)
        tabsSETEZINSARmiaplpywidget = QWidget()
        tabsSETEZINSARmiaplpylayout = QGridLayout()
        tabsSETEZINSARmiaplpy.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tabsSETEZINSARmiaplpy.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        label_miaplpycondaenv = QLabel('<p><b>MiaplPy Conda Env.:</b></p>')
        self.value_miaplpycondaenv = QLineEdit(constants.__miaplpycondaenv__)
        tabsSETEZINSARmiaplpylayout.addWidget(label_miaplpycondaenv,0,0)
        tabsSETEZINSARmiaplpylayout.addWidget(self.value_miaplpycondaenv,0,1)

        tabsSETEZINSARmiaplpylayout.addWidget(tabsSETEZINSARmiaplpywidget)
        tabsSETEZINSARmiaplpy.setLayout(tabsSETEZINSARmiaplpylayout)
        tabsSETEZINSAR.addTab(tabsSETEZINSARmiaplpy, "MiaplPy")

        ## EZ-InSAR setting: Sarvey
        tabsSETEZINSARsarvey = QScrollArea()
        tabsSETEZINSARsarvey.setWidgetResizable(True)
        tabsSETEZINSARsarveywidget = QWidget()
        tabsSETEZINSARsarveylayout = QGridLayout()
        tabsSETEZINSARsarvey.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tabsSETEZINSARsarvey.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        label_sarveycondaenv = QLabel('<p><b>Sarvey Conda Env.:</b></p>')
        self.value_sarveycondaenv = QLineEdit(constants.__sarveycondaenv__)
        tabsSETEZINSARsarveylayout.addWidget(label_sarveycondaenv,0,0)
        tabsSETEZINSARsarveylayout.addWidget(self.value_sarveycondaenv,0,1)

        tabsSETEZINSARsarveylayout.addWidget(tabsSETEZINSARsarveywidget)
        tabsSETEZINSARsarvey.setLayout(tabsSETEZINSARsarveylayout)
        tabsSETEZINSAR.addTab(tabsSETEZINSARsarvey, "Sarvey")

        ezinsarsettingsLayout.addWidget(tabsSETEZINSAR)

        ezinsarsettings.setLayout(ezinsarsettingsLayout)

        btSavesettings = QPushButton('Save the settings')
        btSavesettings.clicked.connect(self.savesettings)

        tab1layout.addWidget(desktopsettings)
        tab1layout.addWidget(ezinsarsettings)
        tab1layout.addWidget(btSavesettings)

        tab1widget.setLayout(tab1layout)
        tab1.setWidget(tab1widget)
        tabs.addTab(tab1, "Settings")

        ###############################################################################################
        tab1 = QScrollArea()
        tab1.setWidgetResizable(True)
        tab1widget = QWidget()
        tab1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tab1.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        tab1layout = QGridLayout()
        tab1layout.addWidget(QLabel('<b>Update(s) of EZ-InSAR</b>'),0,0,1,1)

        self.btcheckupdate = QPushButton("Check for update(s)")
        self.btcheckupdate.clicked.connect(self.checkupdates)
        tab1layout.addWidget(self.btcheckupdate,1,0,1,1)

        self.listupdate = QListWidget()
        tab1layout.addWidget(self.listupdate,2,0,1,1)

        self.btupdate = QPushButton("Install the update(s)")
        self.btupdate.setEnabled(False)
        self.btupdate.clicked.connect(self.runupdate)
        tab1layout.addWidget(self.btupdate,3,0,1,1)

        tab1widget.setLayout(tab1layout)
        tab1.setWidget(tab1widget)
        tabs.addTab(tab1, "Updates")

        ###############################################################################################
        tab2 = QScrollArea()
        tab2.setWidgetResizable(True)
        tab2widget = QWidget()
        tab2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tab2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        tab2layout = QGridLayout()

        self.bttoolshortcut = QPushButton("Create the shortcut icons of EZ-InSAR")
        tab2layout.addWidget(self.bttoolshortcut,0,0,1,1)

        self.bttoolcleancache = QPushButton("Clean the EZ-InSAR cache")
        tab2layout.addWidget(self.bttoolcleancache,1,0,1,1)

        self.bttoolinfo = QPushButton("Generate the EZ-InSAR information report")
        tab2layout.addWidget(self.bttoolinfo,2,0,1,1)

        self.bttooltest = QPushButton("Test the EZ-InSAR installation")
        tab2layout.addWidget(self.bttooltest,3,0,1,1)

        self.bttoolshortcut.clicked.connect(self.adtools)
        self.bttoolcleancache.clicked.connect(self.adtools)
        self.bttoolinfo.clicked.connect(self.adtools)
        self.bttooltest.clicked.connect(self.adtools)

        tab2layout.addWidget(QLabel(' '),100,0,1,1)

        tab2widget.setLayout(tab2layout)
        tab2.setWidget(tab2widget)
        tabs.addTab(tab2, "Advanced tools")
       
       ###############################################################################################
        self.btOkay = QPushButton("Close")
        self.btOkay.clicked.connect(self.valid)

        btHelp = QPushButton("Help", self)
        btHelp.clicked.connect(self.openhelp)

        mainLayout.addWidget(tabs, 2, 0, 1, 10)
        mainLayout.addWidget(self.btOkay, 10, 9, 1, 1)
        mainLayout.addWidget(btHelp, 10, 0, 1, 1)

        self.setLayout(mainLayout)
        self.setGeometry(200,200,700,700)

        self.setWindowTitle("EZ-InSAR Configuration")
    
    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def openhelp(self):
        helpdial = DocsDialog(['settings','settings'])
        helpdial.show()
        helpdial.exec()

    def adtools(self):
        if self.sender().text() == 'Create the shortcut icons of EZ-InSAR': 
            cmd = 'ezinsar toolkit shortcut'
        elif self.sender().text() == 'Clean the EZ-InSAR cache':
            cmd = 'ezinsar toolkit cleancache'
        elif self.sender().text() == 'Generate the EZ-InSAR information report':
            cmd = 'ezinsar toolkit info --full --env --package --debug --bypassuser'
        elif self.sender().text() == 'Test the EZ-InSAR installation':
            cmd = 'ezinsar toolkit test'

        reply = QMessageBox.information(self, "EZ-InSAR Information",
                'Please wait during the running of the command:\n\t%s' % (cmd),
                QMessageBox.Ok)
        status = os.system(cmd)

        if status == 0:
            reply = QMessageBox.information(self, "EZ-InSAR Information",
                'Successfull:\n\t%s' % (cmd),
                QMessageBox.Ok)
        else:
            reply = QMessageBox.critical(self, "EZ-InSAR Error",
                'Error with:\n\t%s' % (cmd),
                QMessageBox.Ok)
        
        if self.sender().text() == 'Generate the EZ-InSAR information report':
            import platform, subprocess, glob
            filereport = glob.glob('EZInSAR_Report_*')[0]
            os.rename(filereport,constants.__cachedir__+os.sep+filereport)

            reply = QMessageBox.information(self, "EZ-InSAR Information",
                'The report file must be shared with thrusted people because it contains personal information (i.e., path, etc.). The username and password have been masked.',
                QMessageBox.Ok)
            
            if platform.system() == 'Windows':
                os.startfile(constants.__cachedir__+os.sep+filereport)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', constants.__cachedir__+os.sep+filereport])
            else:
                subprocess.run(['xdg-open', constants.__cachedir__+os.sep+filereport])

    def msgtiles(self):
        if self.FoliumTiles.isChecked():
            reply = QMessageBox.information(self, "EZ-InSAR Information",
                'The supplemetary basemap tiles will be added to EZ-InSAR. However their uses must respect the terms of conditions defined by the providers.',
                QMessageBox.Ok | QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                    self.FoliumTiles.setChecked(False)
            
    def savesettings(self):
        with open(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'desktop.config','w') as fout:
            fout.write('theme::%s\n' % (self.theme.currentText()))
            fout.write('docker_running::%s\n' % (str(self.dockerrep.isChecked()).capitalize()))
            fout.write('UnlockTiles::%s\n' % (str(self.FoliumTiles.isChecked()).capitalize()))
            fout.write('foliumCached::%s\n' % (str(self.FoliumCached.isChecked()).capitalize()))
            fout.write('plotlyCached::%s\n' % (str(self.PloltlyCached.isChecked()).capitalize()))
            fout.write('Updatetime::%s\n' % (self.updatetime.value()/1000))
            fout.write('nbLineLog::%s\n' % (self.nblinelog.value()))
            fout.write('Cputime::%s\n' % (self.cpuupdatetime.value()/1000))


        ## EZ-InSAR settings
        results = [
            self.value_username.text(),
            self.value_password.text(),
            self.value_cache.text(),
            self.value_pathisce2.text(),
            self.value_pathsnappy.text(),
            self.value_pathdoris.text(),
            self.value_pathstamps.text(),
            self.value_pathlicsbas.text(),
            self.value_pathsnapgpt.text(),
            self.value_ISCE2modesymlink.currentText(),
            int(self.value_SNAPcachemax.text()),
            self.value_SNAPcacheclean.currentText(),
            self.value_SNAPwrapper.currentText(),
            self.value_defautprocessor.currentText(),
            self.value_S1server.currentText(),
            self.value_loggingmode.currentText(),
            self.value_nameDockerImage.text(),
            self.value_mintpycondaenv.text(),
            self.value_isce2condaenv.text(),
            self.value_licsbascondaenv.text(),
            self.value_miaplpycondaenv.text(),
            self.value_sarveycondaenv.text(),
            self.value_wgetlimit.text(),
            self.value_wgetlimitmin.text(),
            self.value_wgetlimitmax.text(),
            int(self.value_chunksize.text()),
            self.value_SLCdownloader.currentText(),
            int(self.value_sleepSLCdownload.text()),
        ]

        conf = pd.read_csv(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'user.config',delimiter='::',header=None,engine='python',names=['Variable','Value'])

        for idx1, proci in enumerate(['username', 'password','cache', 'pathisce2', 'pathsnappy', 'pathdoris', 'pathstamps','pathlicsbas','pathsnapgpt',
        'ISCE2modesymlink','SNAPcachemax','SNAPcacheclean','SNAPwrapper','defautprocessor','S1server','loggingmode','nameDockerImage','mintpycondaenv','isce2condaenv','licsbascondaenv','miaplpycondaenv', 'sarveycondaenv','wgetlimit','wgetlimitmin','wgetlimitmax','chunksize','SLCdownloader','sleepSLCdownload',
        ]):
            if proci in list(conf['Variable']): 
                idx2 = list(conf['Variable']).index(proci)
                conf.loc[idx2, 'Value'] = results[idx1]
        conf.to_csv(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'user.config',sep=';',header=None,index=False)
        with open(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'user.config','r') as fi:
            texttmp = fi.readlines()
        with open(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'user.config','w') as fout:
            for idx, li in enumerate(texttmp):
                fout.write('%s' % (li.replace(';','::')))
        
        if self.parent == None:
            reply = QMessageBox.information(self, "EZ-InSAR Information",
                'New settings are saved.',
                QMessageBox.Ok)
        else:
            reply = QMessageBox.information(self, "EZ-InSAR Information",
                'New settings are saved. Please restart EZ-InSAR.',
                QMessageBox.Ok | QMessageBox.Cancel)
            
            if reply == QMessageBox.Ok:
                self.parent.close()
      
    def themepreview(self):
        themeselect = self.theme.currentText()
        theme = eval('themes.%s' % (themeselect))
        self.setStyleSheet(theme)

    def runupdate(self): 
        reply = QMessageBox.critical(self, "EZ-InSAR Error",
                'This feature will be available soon.',
                QMessageBox.Ok)

    def checkupdates(self):
        diagprogress = QProgressDialog('Checking...',None,0,100, self)
        diagprogress.setWindowTitle('Loading...')
        diagprogress.show()
        QApplication.processEvents()

        updates = []
        total = len(miscellaneous.listmodule('processor')) + len(miscellaneous.listmodule('sensor')) + len(constants.__EZInSARoptionalmodule__) + 1

        h = 1
        vi = miscellaneous.checkmodule('ezinsar',type='core',checkupdate=True)
        if (not vi['__versionPackage__'] == vi['__versionUpdate__']) and (not vi['__versionUpdate__'] == 'unknown'):
            updates.append('%s -- %s' % ('ezinsar',vi['__versionUpdate__']))
        diagprogress.setValue(int((h/total)*100))
        QApplication.processEvents()

        for idx, modi in enumerate(miscellaneous.listmodule('processor')):
            vi = miscellaneous.checkmodule(modi,type='processor',checkupdate=True)
            if (not vi['__versionPackage__'] == vi['__versionUpdate__']) and (not vi['__versionUpdate__'] == 'unknown'):
                updates.append('%s -- %s' % (modi,vi['__versionUpdate__']))
            h = h + 1
            diagprogress.setValue(int((h/total)*100))
            QApplication.processEvents()
        
        for idx, modi in enumerate(miscellaneous.listmodule('sensor')):
            vi = miscellaneous.checkmodule(modi,type='sensor',checkupdate=True)
            if (not vi['__versionPackage__'] == vi['__versionUpdate__']) and (not vi['__versionUpdate__'] == 'unknown'):
                updates.append('%s -- %s' % (modi,vi['__versionUpdate__']))
            h = h + 1
            diagprogress.setValue(int((h/total)*100))
            QApplication.processEvents()

        for idx, modi in enumerate(constants.__EZInSARoptionalmodule__):
            try:  
                vi = miscellaneous.checkmodule(modi,type='optional')
                if (not vi['__versionPackage__'] == vi['__versionUpdate__']) and (not vi['__versionUpdate__'] == 'unknown'):
                    updates.append('%s -- %s' % (modi,vi['__versionUpdate__']))
            except:
                a = 'dummy'
            h = h + 1
            diagprogress.setValue(int((h/total)*100))
            QApplication.processEvents()

        diagprogress.close()

        self.listupdate.clear()
        if updates:
            self.listupdate.addItems(updates)
            self.btupdate.setEnabled(True)
        else:
            self.listupdate.addItem('Up-to-date')
            self.btupdate.setEnabled(False)

    def valid(self):
        """Validation    
        """
        self.close()
        
    def cancel(self):
        """Cancelation        
        """
        self.validation = False
        self.close()

###########################################################################################
## Main 
###########################################################################################
def main():
    """Main function""" 
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_config_whiteback.svg'))
    
    if tools.checklicense():
        widget = configDial()
        widget.show()
        sys.exit(app.exec_())
    else: 
        sys.exit()

if __name__=='__main__':
    main()