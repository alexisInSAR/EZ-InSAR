#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Installer for EZ-InSAR, cross-platform

Changelog:
    * 1.2.0: Add the support of the last miniconda version and delete the support of wget, Sep. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial release, May 2025

License: 
    * Same as EZ-InSAR (GPL-v3)

"""

# pyinstaller -F --add-data EZ_InSAR_logo.svg:. --add-data EZ_InSAR_logo_whiteback.svg:. -n EZInSAR_Installer_MacOS_ARM EZInSAR_Installer.py
# pyinstaller -F --add-data EZ_InSAR_logo.svg:. --add-data EZ_InSAR_logo_whiteback.svg:. -n EZInSAR_Installer_Win EZInSAR_Installer.py
# pyinstaller -F --add-data EZ_InSAR_logo.svg:. --add-data EZ_InSAR_logo_whiteback.svg:. -n EZInSAR_Installer_Linux_Ubuntu2004 EZInSAR_Installer.py

###########################################################################################
## Packages and variables
###########################################################################################
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, 
                            QLabel, QLineEdit, 
                            QWizard, QWizardPage, QComboBox, QSpinBox, 
                            QProgressBar, QTextEdit,QScrollArea,QWidget, QPushButton)

import os, sys
import subprocess 
import platform
import requests
import time
import webbrowser
import glob 

__author__ = 'Alexis Hrysiewicz, UCD / iCRAG'
__copyright__ = "Copyright 2025, EZ-InSAR / UCD / iCRAG"
__version__ = 'Installer version 1.2.0'

if not platform.system() == 'Windows':
    dummyverbose = '> /dev/null 2>&1'
else: 
    dummyverbose = '> NUL'

listpythonver = ['Python 3.13.7',
                'Python 3.13.6',
                'Python 3.13.5',
                'Python 3.13.4',
                'Python 3.13.3',
                'Python 3.13.2',
                'Python 3.13.1',
                'Python 3.13.0',
                'Python 3.12.10',
                'Python 3.12.9',
                'Python 3.12.8',
                'Python 3.12.7',
                'Python 3.12.6',
                'Python 3.12.5',
                'Python 3.12.4',
                'Python 3.12.3',
                'Python 3.12.2',
                'Python 3.12.1',
                'Python 3.12.0',
                'Python 3.11.12',
                'Python 3.11.11',
                'Python 3.11.10',
                'Python 3.11.9', 
                'Python 3.11.8',
                'Python 3.11.7',
                'Python 3.11.6',
                'Python 3.11.5',
                'Python 3.11.4',
                'Python 3.11.3',
                'Python 3.11.2',
                'Python 3.11.1',
                'Python 3.11.0',
                'Python 3.10.17',
                'Python 3.10.16',
                'Python 3.10.15',
                'Python 3.10.14',
                'Python 3.10.13',
                'Python 3.10.12',
                'Python 3.10.11',
                'Python 3.10.10',
                'Python 3.10.9',
                'Python 3.10.8',
                'Python 3.10.7',
                'Python 3.10.6',
                'Python 3.10.5',
                'Python 3.10.4',
                'Python 3.10.3',
                'Python 3.10.2',
                'Python 3.10.1',
                'Python 3.10.0']

listmodule = ['Desktop','GAMMA','GNSS','Multispectral','NISAR','SAOCOM','TSDisplayer','Weather','Webapp','PostProcessing','Server']
listmodulerelease = ['Desktop','TSDisplayer']

if os.path.isdir(os.path.expanduser("~")+os.sep+'miniforge3'):
    condadir = os.path.expanduser("~")+os.sep+'miniforge3'
else:
    condadir = os.path.expanduser("~")+os.sep+'miniconda3'

curenv = os.environ.copy()
curenv['CONDA_PLUGINS_AUTO_ACCEPT_TOS'] = 'yes' # For the last versions of miniconda

config_var = {
    'username': ['Username','xxxxxxx','str','This username can be used for SLC download.'],
    'password': ['Password','xxxxxxx','str','This password can be used for SLC download.'],
    'cache': ['EZ-InSAR cache directory',os.path.expanduser("~")+ os.sep +'.ezinsar'+os.sep+'cache','str','Cache of EZ-InSAR'],
    'pathisce2': ['Path of ISCE-2','<Path of ISCE-2>','str','Path of ISCE-2 SAR/InSAR processor'],
    'pathsnappy': ['Path of SNAP snappy','<Path of snappy>','str','Path of snappy, used by SNAP SAR/InSAR processor'],
    'pathsnapgpt': ['Path of SNAP GPT','<Path of snap gpt>','str','Path of GPT, used by SNAP SAR/InSAR processor'],
    'pathdoris': ['Path of Doris','<Path of Doris>','str','Path of Doris SAR/InSAR processor'],
    'pathstamps': ['Path of StaMPS','<Path of StaMPS>','str','Path of StaMPS SAR/InSAR processor'],
    'pathlicsbas': ['Path of LicSBAS','<Path of LicSBAS>','str','Path of LicSBAS SAR/InSAR processor'],
    'ISCE2modesymlink': ['Enable the links of ISCE-2',True,'bool','Symbolic links will be used by ISCE-2'],
    'SNAPcachemax': ['Max. cached of SNAP',5000,'int','Max. value of the SNAP cache [MB]'],
    'SNAPcacheclean': ['Clean the SNAP cache',True,'bool','Enable the cleaning of the SNAP cache'],
    'SNAPwrapper': ['Wrapper for SNAP',['gpt','snappy'],'list','Selected wrapper for SNAP'],
    'defautprocessor': ['Default processor',['isce2','snap','doris'],'list','Default SAR/InSAR processor used by EZ-InSAR'],
    'S1server': ['Sentinel-1 server',['Copernicus','ASF'],'list','Favourite Sentinel-1 server (can be changed)'],
    'loggingmode': ['Logging Mode',['INFO','DEBUG'],'list','Logging mode'],
    'nameDockerImage': ['Docker Image Name','ezinsar','str','Name of the Docker image'],
    'wgetlimit': ['Wget Mode','auto','str','wget limit mode'],
    'wgetlimitmin': ['Wget Day. Limit','12.5m','str','wget limit in MB/s during the day hours'],
    'wgetlimitmax': ['Wget Night. Limit','50.0m','str','wget limit in MB/s during the night hours'],
    'chunksize': ['Downloader Chunk Size',8192,'int','Chunk size for the python downloader'],
    'SLCdownloader': ['SLC Downloader mode',['python','wget'],'list','Mode of the SLC downloader'],
    'sleepSLCdownload': ['Downloader Sleep',2,'int','Time sleep between SLC downloads in seconds'],
}

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Worker(QObject):
    textSignal = pyqtSignal(str)
    barprogressSignal = pyqtSignal(int)
    finished = pyqtSignal()
    intReady = pyqtSignal(int)
    error = pyqtSignal(str)
    success = pyqtSignal(str)
    
    def __init__(self, 
        condaenv,
        condadir,         
        dirinstall,  
        pythonver,       
        listmoduleinstall, 
        checkgdal, 
        modedev,    
        parent=None):
        super(Worker, self).__init__(parent)

        self.running = True
        self.messageerror = ''
        self.messagesuccess = ''
        self.barprocessvalue = 0
        self.condaenv = condaenv
        self.condadir = condadir
        self.dirinstall = dirinstall
        self.pythonver = pythonver
        self.listmoduleinstall = listmoduleinstall
        self.checkgdal = checkgdal
        self.modedev = modedev 

    def run(self):
        ## Reminder
        self.textSignal.emit('Conda Environment: %s' % (self.condaenv))
        self.textSignal.emit('Python Version: %s' % (self.pythonver))
        self.textSignal.emit('Installation in: %s' % (self.dirinstall))

        ## Create the directory
        if not os.path.isdir(self.dirinstall):
            os.makedirs(self.dirinstall)
            self.textSignal.emit('\tCreate the installation directory')
        self.barprogressSignal.emit(10)

        ## Check if the conda environment exists (and create if it is required)
        if not platform.system() == 'Windows':
            cmd = "source %s/etc/profile.d/conda.sh && conda activate %s" % (self.condadir,self.condaenv)
        else:
            cmd = "conda activate %s" % (self.condaenv)

        if not platform.system() == 'Windows': 
            result = subprocess.run(
                    cmd,
                    shell=True,
                    executable="/bin/bash",
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        else: 
            result = subprocess.run(
                    cmd,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

        if result.returncode == 0:
            self.textSignal.emit('The conda env %s exists, it will be used.' % (self.condaenv))
        else:
            self.textSignal.emit('The conda env %s does not exist, it will be created.' % (self.condaenv))

            if not platform.system() == 'Windows':
                cmd = "source %s/etc/profile.d/conda.sh && conda create --name %s python==%s --yes" % (self.condadir,self.condaenv,self.pythonver)
            else:
                cmd = "conda create --name %s python==%s --yes" % (self.condaenv,self.pythonver)
            self.runcmd(cmd)
            
        self.barprogressSignal.emit(20)

        ## Install GDAL (with conda, pre-build)
        self.textSignal.emit('Install GDAL with conda (and some pre-built packages).')

        if not platform.system() == 'Windows':
            if self.checkgdal:
                tmpcmd = "source %s/etc/profile.d/conda.sh && " \
                    "conda run -n %s conda install --yes -c conda-forge GDAL==$(gdal-config --version | awk -F'[.]' '{print $1\".\"$2}') " % (self.condadir,self.condaenv)
            else:
                tmpcmd = "source %s/etc/profile.d/conda.sh && " \
                    "conda run -n %s conda install --yes -c conda-forge GDAL" % (self.condadir,self.condaenv)
                
            self.runcmd(tmpcmd)
        else:
                tmpcmd = "conda install -n %s --yes -c conda-forge libgdal==3.10" % (self.condaenv)
                self.runcmd(tmpcmd)
                tmpcmd = "conda install -n %s --yes -c conda-forge gdal==3.10" % (self.condaenv)
                self.runcmd(tmpcmd)
                # tmpcmd = "conda install -n %s --yes -c conda-forge h5df" % (self.condaenv)
                # self.runcmd(tmpcmd)
                tmpcmd = "conda install -n %s --yes -c conda-forge h5py" % (self.condaenv)
                self.runcmd(tmpcmd)
                
        self.barprogressSignal.emit(30)

        ###### Install EZ-InSAR-3 core
        if not os.path.isdir('%s%sEZ-InSAR' %(self.dirinstall,os.sep)): 
            self.textSignal.emit('Download EZ-InSAR from public GitHub.')

            if self.modedev: 
                urlcore = 'https://github.com/alexisInSAR/EZ-InSAR-3.git'
                keycore = '-3'
            else:
                urlcore = 'https://github.com/alexisInSAR/EZ-InSAR.git'
                keycore = ''

            ## Here we consider that the repository is public
            if not platform.system() == 'Windows':
                self.runcmd("source %s/etc/profile.d/conda.sh && " \
                    "cd %s && git clone %s --progress" % (
                            self.condadir,
                            self.dirinstall,
                            urlcore))
            else:
                self.runcmd("cd %s && conda run -n %s git clone %s --progress" % (
                        self.dirinstall,
                        self.condaenv,
                        urlcore))
                
        else: 
            keycore = ''
                    
        if not self.modedev: # move the modules directories
            for limi in glob.glob("%s%sEZ-InSAR%s%smodules%sEZ-InSAR-Modules-*" % (self.dirinstall,os.sep,keycore,os.sep,os.sep)):
                os.rename(limi,'%s%s%s' % (self.dirinstall,os.sep,limi.split(os.sep[-1])))

        self.textSignal.emit('Install EZ-InSAR (core).')

        if not platform.system() == 'Windows':
            self.runcmd("source %s/etc/profile.d/conda.sh && " \
                "cd %s%sEZ-InSAR%s && conda run -n %s pip3 install -r requirements.txt" % (self.condadir,self.dirinstall,os.sep,keycore,self.condaenv))
            self.runcmd("source %s/etc/profile.d/conda.sh && " \
                "cd %s%sEZ-InSAR%s && conda run -n %s pip3 install -e ." % (self.condadir,self.dirinstall,os.sep,keycore,self.condaenv))
        else:
            self.runcmd("cd %s%sEZ-InSAR%s && conda run -n %s pip3 install -r requirements.txt" % (self.dirinstall,os.sep,keycore,self.condaenv))
            self.runcmd("cd %s%sEZ-InSAR%s && conda run -n %s pip3 install -e ." % (self.dirinstall,os.sep,keycore,self.condaenv))

        ## Install EZ-InSAR-3 optional modules
        for idx, mi in enumerate(self.listmoduleinstall):

            if not os.path.isdir('%s%sEZ-InSAR-Module-%s' %(self.dirinstall,os.sep,mi)): 
                self.textSignal.emit('Download EZ-InSAR-Module-%s:' % (mi))

                if not platform.system() == 'Windows':
                    self.runcmd("source %s/etc/profile.d/conda.sh && " \
                        "cd %s && git clone %s --progress" % (
                                self.condadir,
                                self.dirinstall,
                                'https://github.com/alexisInSAR/EZ-InSAR-Module-%s.git' % (mi)))
                else: 
                    self.runcmd("cd %s && conda run -n %s git clone %s --progress" % (
                                self.dirinstall,
                                self.condaenv,
                                'https://github.com/alexisInSAR/EZ-InSAR-Module-%s.git' % (mi)))

            self.textSignal.emit('Install EZ-InSAR-Module-%s:' % (mi))

            if not platform.system() == 'Windows':
                self.runcmd("source %s/etc/profile.d/conda.sh && " \
                    "cd %s%sEZ-InSAR-Module-%s && conda run -n %s pip3 install -e ." % (self.condadir,self.dirinstall,os.sep,mi,self.condaenv))
            else: 
                self.runcmd("cd %s%sEZ-InSAR-Module-%s && conda run -n %s pip3 install -e ." % (self.dirinstall,os.sep,mi,self.condaenv))

            self.barprogressSignal.emit(40+int(60*((idx+1)/len(self.listmoduleinstall))))
            time.sleep(1)

        time.sleep(1)

        self.finished.emit()

    def runcmd(self,cmdtxt):
        self.textSignal.emit('Run the command: %s' % (cmdtxt))

        if not platform.system() == 'Windows':
            pr = subprocess.Popen(cmdtxt, 
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, 
                    shell=True,
                    executable="/bin/bash",
                    env = curenv)
            
            if (not len("".join(pr.stdout.readline().decode('utf-8').strip().split())) == 0) and (not pr.stdout == None):
                while (line := pr.stdout.readline().decode('utf-8')) != "":
                    self.textSignal.emit(line.replace('\n',' '))
            else: 
                if (not len("".join(pr.stderr.readline().decode('utf-8').strip().split())) == 0) and (not pr.stderr == None):
                    while (line := pr.stderr.readline().decode('utf-8')) != "":
                        self.textSignal.emit(line.replace('\n',' ')) 
        else:
            os.system(cmdtxt + ' %s' % (dummyverbose))
        
        self.textSignal.emit('\tdone')

#########################################################
class EZInSAR_Installer(QWizard):
    def __init__(self, parent=None):
        super(EZInSAR_Installer, self).__init__(parent)

        self.pathjobfile = None
        self.addPage(IntroductionPage())
        self.addPage(RequirementsPage())
        self.addPage(EnvironmentPage())
        self.addPage(ModulePage())
        self.addPage(InstallPage())
        self.addPage(ConfigPage())
        self.addPage(EndPage())

        self.setWindowTitle("EZ-InSAR-3 - Easy Installer")
        self.setFixedSize(1000, 750)
        self.currentIdChanged.connect(self.installrun)
        self.workprocess = None
        self.threadprocess = None
        self.setWizardStyle(QWizard.ModernStyle)

    def installrun(self,new_id):
        if new_id == 1 or new_id == 5 or new_id == 6:
            self.button(QWizard.BackButton).setEnabled(False)
        elif new_id == 4:

            self.button(QWizard.BackButton).setEnabled(False)
            self.button(QWizard.NextButton).setEnabled(False)

            listmoduleinstall = []
            for idx, mi in enumerate(listmodule):
                checked = eval('self.page(3).checkEZ_%s.isChecked()' % (mi))
                if checked: 
                    listmoduleinstall.append(mi)

            ## Preparation of the variables
            self.workerprocess = Worker(
                self.page(2).condaenvLineEdit.text(), # condaenv
                condadir, 
                self.page(2).dirinstallLineEdit.text(), # dirinstall
                self.page(2).pythonverComboBox.currentText().replace('Python ',''), # pythonver
                listmoduleinstall,
                self.page(1).checkgdal.isChecked(),
                self.page(3).modedev.isChecked()) 
        
            self.threadprocess = QThread()
            self.workerprocess.moveToThread(self.threadprocess)
            self.threadprocess.started.connect(self.workerprocess.run)
            self.workerprocess.finished.connect(self.threadprocess.quit)
            self.workerprocess.textSignal.connect(self.updateinfotext)
            self.workerprocess.barprogressSignal.connect(self.updateprogressbar)
            self.workerprocess.finished.connect(self.stopcurrentworker)      
            self.threadprocess.start()
               
    def updateinfotext(self,newtext):
        QApplication.processEvents()
        textstr = self.page(4).infotext.toPlainText() + '\n' + newtext
        self.page(4).infotext.setText(textstr)
        self.page(4).infotext.verticalScrollBar().setValue(self.page(4).infotext.verticalScrollBar().maximum())
        time.sleep(0.001)

    def updateprogressbar(self,value):
        self.page(4).progressbar.setValue(value)
        QApplication.processEvents()
        time.sleep(0.001)

    def stopcurrentworker(self):
        self.workerprocess = None
        # self.threadprocess = None
        self.page(4).setButtonText(QWizard.NextButton, "Next")
        self.button(QWizard.NextButton).setEnabled(True)
        self.updateprogressbar(100)

    def accept(self):
        super(EZInSAR_Installer, self).accept()

        condaenv = self.page(2).condaenvLineEdit.text()
        
        if not platform.system() == 'Windows':
            cmd = "source %s/etc/profile.d/conda.sh && conda run -n %s ezinsar toolkit configfile --nointeractive --nolicensecheck" % (condadir,condaenv)
        else:
            cmd = "conda run -n %s ezinsar toolkit configfile --nointeractive --nolicensecheck" % (condaenv)
        self.wrappedcmd(cmd)

        # Create the shortcuts 
        if self.page(6).checkshortcut.isChecked():
            if not platform.system() == 'Windows':
                cmd = "source %s/etc/profile.d/conda.sh && conda run -n %s ezinsar toolkit shortcut --nolicensecheck" % (condadir,condaenv)
            else:
                cmd = "conda run -n %s ezinsar toolkit shortcut --nolicensecheck" % (condaenv)
            self.wrappedcmd(cmd)
            
        # Open the documentation
        if self.page(6).checkopenDocs.isChecked():
            url = 'file:'+self.page(2).dirinstallLineEdit.text()+os.sep+'EZ-InSAR-3'+os.sep+'docs'+os.sep+'build'+os.sep+'html'+os.sep+'index.html'
            webbrowser.open_new(url)

    def wrappedcmd(self,cmdtxt):
        print('Run the command: %s' % (cmdtxt))

        if not platform.system() == 'Windows':
            pr = subprocess.Popen(cmdtxt, 
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, 
                    shell=True,
                    executable="/bin/bash",
                    env = curenv)
            
            if (not len("".join(pr.stdout.readline().decode('utf-8').strip().split())) == 0) and (not pr.stdout == None):
                while (line := pr.stdout.readline().decode('utf-8')) != "":
                    print(line.replace('\n',' '))
            else: 
                if (not len("".join(pr.stderr.readline().decode('utf-8').strip().split())) == 0) and (not pr.stderr == None):
                    while (line := pr.stderr.readline().decode('utf-8')) != "":
                        print(line.replace('\n',' ')) 
        else:
            os.system(cmdtxt + ' %s' % (dummyverbose))

###########################################################################################
## Introduction page class
###########################################################################################
class IntroductionPage(QWizardPage):
    def __init__(self, parent=None):
        super(IntroductionPage, self).__init__(parent)

        self.setTitle("<span style='font-size:20pt;'>EZ-InSAR-3</span>")
        self.setSubTitle("<span style='font-size:15pt;'>Installer for %s</span>" % (platform.system()))

        label = QLabel("""
                <p><b>The EZ-InSAR installer offers an user-friendly to install EZ-InSAR by preparing the Python/conda environment.</b></p>
                <p>The installation steps are as follows: (1) verification of the requirements; (2) definition of the user environment; (3) selection of the EZ-InSAR modules; (4) installation of EZ-InSAR (and selected optional modules); (5) creation of the EZ-InSAR configuration files; and (6) finalisation of the installation.</p>
                <p style="color:red;"><b>Warning:</b></p>
                <p style="color:red;">No SAR/InSAR processors will be installed. Users require to install them independently.</p>
                <p><b>Latest versions of EZ-InSAR and optional modules will be installed.</b></p>
                """)
        
        logo = QLabel()
        logo.setPixmap(QPixmap(resource_path('EZ_InSAR_logo_whiteback.svg')).scaled(512, 512, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        label.setWordWrap(True)
        layout = QGridLayout()
        layout.addWidget(label,0,0,5,6)
        layout.addWidget(logo,7,0,4,1)
        layout.addWidget(QLabel('%s' % (__version__)),7,5,1,1, Qt.AlignRight)
        layout.addWidget(QLabel('%s' % (__copyright__)),8,5,1,1, Qt.AlignRight)
        layout.addWidget(QLabel('%s' % (__author__)),9,5,1,1, Qt.AlignRight)
        layout.addWidget(QLabel('Interface built with PyQT 5'),10,5,1,1, Qt.AlignRight)

        self.setLayout(layout)

###########################################################################################
## Requirements page class
###########################################################################################
class RequirementsPage(QWizardPage):
    def __init__(self, parent=None):
        super(RequirementsPage, self).__init__(parent)

        self.setTitle("<span style='font-size:20pt;'>EZ-InSAR-3</span>")
        self.setSubTitle("<span style='font-size:15pt;'>Requirements</span>")
        
        label = QLabel("""
                <p><b>The installer has checked that all requirements are installed and available for EZ-InSAR.</b></p>                      
                <p style="color:red;">If one of them is <b>needed</b>, please follow the guidelines available in the EZ-InSAR documentation or install file. There will be an error during the installation.</p>
                <p>Futher information are available with the tooltips.</p>  
                <p style='font-size:10pt;'><b>Requirements:</b></p>
                """
            )
        label.setWordWrap(True)
        
        labelconda = QLabel("<b>Conda or Miniconda:</b>")
        labelconda.setToolTip('Check if Conda manager is installed.')
        self.checkconda = QCheckBox("")
        self.checkconda.setEnabled(False)

        btconda = QPushButton("Install from the web")
        btconda.clicked.connect(self.openhelpconda)

        labelgdal = QLabel("<b>GDAL:</b>")
        labelgdal.setToolTip('Check if GDAL is installed, however the library will be installed by conda.')
        self.checkgdal = QCheckBox("")
        self.checkgdal.setEnabled(False)

        btgdal = QPushButton("Install from the web")
        btgdal.clicked.connect(self.openhelpgdal)

        labelaws = QLabel("<b>Amazon CLI:</b>")
        labelaws.setToolTip('Check if Amazon CLI is installed, but it is not required for the installation. It will be required for DEM downloading.')
        self.checkaws = QCheckBox("")
        self.checkaws.setEnabled(False)
        
        btaws = QPushButton("Install from the web")
        btaws.clicked.connect(self.openhelpaws)

        labelgit = QLabel("<b>Git / Git Credentials:</b>")
        labelgit.setToolTip('It considers that Git is installed, and the Git credentials are stored in the .my-crediential or .git-crediential files. Required for the developer mode.')
        self.checkgit = QCheckBox("")
        self.checkgit.setEnabled(False)

        btgit = QPushButton("Install from the web")
        btgit.clicked.connect(self.openhelpgit)

        btcheck = QPushButton("Check the requirements")
        btcheck.clicked.connect(self.checkrequirements)

        layout = QGridLayout()
        layout.addWidget(label, 0, 0, 1, 3)

        layout.addWidget(labelconda, 1, 0)
        layout.addWidget(self.checkconda, 1, 1, 1, 2)
        layout.addWidget(btconda, 1, 2, 1, 2)
        
        layout.addWidget(labelgdal, 2, 0)
        layout.addWidget(self.checkgdal, 2, 1, 1, 2)
        layout.addWidget(btgdal, 2, 2, 1, 2)

        layout.addWidget(labelaws, 3, 0)
        layout.addWidget(self.checkaws, 3, 1, 1, 2)
        layout.addWidget(btaws, 3, 2, 1, 2)

        layout.addWidget(labelgit, 4, 0)
        layout.addWidget(self.checkgit, 4, 1, 1, 2)
        layout.addWidget(btgit, 4, 2, 1, 2)

        layout.addWidget(btcheck, 5, 0, 1, 4)

        self.setLayout(layout)

        self.checkrequirements()   
        
    ###########################################################################################
    ## Callbacks
    def checkrequirements(self):
        if os.system("conda -h %s" % (dummyverbose)) == 0:
            self.checkconda.setChecked(True)
            self.checkconda.setText('Ready')
        else:
            self.checkconda.setChecked(False)
            self.checkconda.setText('Needed')

        if os.system("gdalinfo --version %s" % (dummyverbose)) == 0:
            self.checkgdal.setChecked(True)
            self.checkgdal.setText('Ready')
        else:
            self.checkgdal.setChecked(False)
            self.checkgdal.setText('It should be okay.')

        if os.system("aws help %s" % (dummyverbose)) == 0:
            self.checkaws.setChecked(True)
            self.checkaws.setText('Ready')
        else:
            self.checkaws.setChecked(False)
            self.checkaws.setText('Needed')

        if os.path.isfile(os.path.expanduser("~")+os.sep+'.my-credentials') or os.path.isfile(os.path.expanduser("~")+os.sep+'.git-credentials') :
            self.checkgit.setChecked(True)
            self.checkgit.setText('Ready')
        else:
            self.checkgit.setChecked(False)
            self.checkgit.setText('Needed')

    def openhelpconda(self):
        webbrowser.open_new('https://www.anaconda.com/docs/getting-started/miniconda/install')
    def openhelpgdal(self):
        webbrowser.open_new('https://gdal.org/en/stable/download.html')
    def openhelpaws(self):
        webbrowser.open_new('https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html')
    def openhelpgit(self):
        webbrowser.open_new('https://git-scm.com/downloads')

###########################################################################################
## Environment page class
###########################################################################################
class EnvironmentPage(QWizardPage):
    def __init__(self, parent=None):
        super(EnvironmentPage, self).__init__(parent)

        self.setTitle("<span style='font-size:20pt;'>EZ-InSAR-3</span>")
        self.setSubTitle("<span style='font-size:15pt;'>Python environment</span>")
        
        label = QLabel("""
                <p><b>Please define the Python environment desired for EZ-InSAR.</b></p>             
                <p>Keep all default values if wanted.</p>
                """
            )
        label.setWordWrap(True)

        labelcondaenv = QLabel("<b>Conda Env. Name:</b>")
        self.condaenvLineEdit = QLineEdit()
        self.condaenvLineEdit.setText('EZ-InSAR-3')

        labelpythonver = QLabel("<b>Python Version:</b>")
        self.pythonverComboBox = QComboBox()
        self.pythonverComboBox.addItems(listpythonver)
        self.pythonverComboBox.setCurrentIndex(listpythonver.index('Python 3.10.14'))

        labeldirinstall = QLabel("<b>Installation Directory:</b>")
        self.dirinstallLineEdit = QLineEdit()
        self.dirinstallLineEdit.setText('%s%sEZ-InSAR' %(os.path.expanduser("~"),os.sep))
    
        layout = QGridLayout()
        layout.addWidget(label, 0, 0, 1, 3)

        layout.addWidget(labelcondaenv, 1, 0, 1, 1)
        layout.addWidget(self.condaenvLineEdit, 1, 1, 1, 1)

        layout.addWidget(labelpythonver, 2, 0, 1, 1)
        layout.addWidget(self.pythonverComboBox, 2, 1, 1, 1)

        layout.addWidget(labeldirinstall, 3, 0, 1, 1)
        layout.addWidget(self.dirinstallLineEdit, 3, 1, 1, 1)

        self.setLayout(layout)

###########################################################################################
## Module page class
###########################################################################################
class ModulePage(QWizardPage):
    def __init__(self, parent=None):
        super(ModulePage, self).__init__(parent)

        self.setTitle("<span style='font-size:20pt;'>EZ-InSAR-3</span>")
        self.setSubTitle("<span style='font-size:15pt;'>Modules</span>")

        self.layout = QGridLayout()

        modedevlabel = QLabel("<b>Mode dev.:</b>")
        self.modedev = QCheckBox("")
        self.modedev.setChecked(False)
        self.modedev.clicked.connect(self.updatelistmodule)
        self.layout.addWidget(modedevlabel, 0, 0, 1, 1)
        self.layout.addWidget(self.modedev, 0, 1, 1, 2)
   
        label = QLabel("""
                <p><b>The installer used the git credentials and was able to detect the accessible EZ-InSAR modules.</b></p>  
                <p style="color:red;">If unaccessible optional module(s) is/are desired, please contact the EZ-InSAR authors.</p>
                <p style='font-size:10pt;'><b>Modules:</b></p> 
                """
            )
        label.setWordWrap(True)
        self.layout.addWidget(label, 1, 0, 1, 3)

        ## For EZ-InSAR core
        labelEZcore = QLabel("<b>EZ-InSAR-3 (core):</b>")
        self.checkEZcore = QCheckBox("")
        self.layout.addWidget(labelEZcore, 2, 0, 1, 1)
        self.layout.addWidget(self.checkEZcore, 2, 1, 1, 2)

        for idx, mi in enumerate(listmodule):
            exec('self.labelEZ_%s = QLabel("<b>EZ-InSAR-3-Module-%s:</b>")' % (mi,mi))
            exec('self.checkEZ_%s = QCheckBox("")' % (mi))
            exec('self.layout.addWidget(self.labelEZ_%s, %s, 0, 1, 1)' % (mi,idx+3))
            exec('self.layout.addWidget(self.checkEZ_%s, %s, 1, 1, 2)' % (mi,idx+3))

        self.setLayout(self.layout)
        self.setButtonText(QWizard.NextButton, "Install")

        self.updatelistmodule()

    ###########################################################################################
    ## Callbacks
    def updatelistmodule(self):
        
        #Check the core 
        if self.modedev.isChecked():
            out = self.checkmodule(type='core')
            if not out == 'unknown': 
                self.checkEZcore.setEnabled(False)
                self.checkEZcore.setChecked(True)
                self.checkEZcore.setText(out)
            else:
                self.checkEZcore.setChecked(False)
                self.checkEZcore.setEnabled(False)
            self.checkEZcore.setText('From the private repository / %s' % (out))

        else:
            self.checkEZcore.setEnabled(False)
            self.checkEZcore.setChecked(True)
            self.checkEZcore.setText('From the public release')

        #Check the optional module
        for idx, mi in enumerate(listmodule):
            if self.modedev.isChecked():
                checkremote = True
            else:
                if mi in listmodulerelease:
                    enabledvalue = False
                    checkedvalue = True
                    textvalue = "Offered with the public release"
                    checkremote = False
                else:
                    checkremote = True
            
            if checkremote:
                out = self.checkmodule(type='optional',modulename=mi)
                if not out == 'unknown': 
                    enabledvalue = True
                    checkedvalue = False
                    textvalue = 'From the private repository / %s' % (out)
                else:
                    enabledvalue = False
                    checkedvalue = False
                    textvalue = "No access from the private repository"

            exec('self.checkEZ_%s.setEnabled(enabledvalue)' % (mi))
            exec('self.checkEZ_%s.setChecked(checkedvalue)' % (mi))
            exec('self.checkEZ_%s.setText(textvalue)' % (mi))

    def checkmodule(self,type='core',modulename=None):

        result = {}
        ## Check the online availability
        template = 'https://raw.githubusercontent.com/alexisInSAR/EZ-InSAR-3/refs/heads/main/src/ezinsar/'
        if type == 'core':
            url = template+'__init__.py'
        else:
            if modulename.lower() in ['multispectral','desktop','webapp','server']:
                    modulename = modulename.capitalize()
            else:
                    modulename = modulename.upper()
            url = 'https://raw.githubusercontent.com/alexisInSAR/EZ-InSAR-Module-%s/refs/heads/main/src/ezinsar%smodule/__init__.py' % (modulename,modulename.lower())

        result['__versionUpdate__'] = 'unknown'
        for li in requests.get(url).text.split('\n'): 
                if 'versionPackage' in li: 
                        result['__versionUpdate__'] = eval('%s' % (li.split('=')[-1]))

        if result['__versionUpdate__'] == 'unknown':
                if os.path.isfile(os.path.expanduser("~")+os.sep+'.git-credentials'):
                    filegit = os.path.isfile(os.path.expanduser("~")+os.sep+'.git-credentials')
                elif os.path.isfile(os.path.expanduser("~")+os.sep+'.my-credentials'): 
                    filegit = os.path.isfile(os.path.expanduser("~")+os.sep+'.my-credentials')   
                else: 
                    filegit = None

                if not filegit == None:
                    with open(os.path.expanduser("~")+os.sep+'.git-credentials','r') as fi: 
                            lines = fi.readlines()[0]
                    access_token = lines.split(':')[-1].split('@')[0]
            
                    headers = {"Authorization": f"Bearer {access_token}"}
                    for li in requests.get(url,headers=headers).text.split('\n'): 
                            if 'versionPackage' in li: 
                                    result['__versionUpdate__'] = eval('%s' % (li.split('=')[-1]))
                                    break
                            
        return result['__versionUpdate__']
    
###########################################################################################
## Install page class
###########################################################################################
class InstallPage(QWizardPage):
    def __init__(self, parent=None):
        super(InstallPage, self).__init__(parent)

        self.setTitle("<span style='font-size:20pt;'>EZ-InSAR-3</span>")
        self.setSubTitle("<span style='font-size:15pt;'>Installation</span>")
        
        label = QLabel("""
                <p><b>Please wait for the installation.</b></p>  
                """
            )
        label.setWordWrap(True)
        
        layout = QGridLayout()
        layout.addWidget(label, 0, 0, 1, 3)

        self.progressbar = QProgressBar(self)
        layout.addWidget(self.progressbar, 1, 0, 1, 3)

        self.infotext = QTextEdit('Installation of EZ-InSAR')
        self.infotext.setReadOnly(True)
        layout.addWidget(self.infotext, 2, 0, 10, 3)

        self.setButtonText(QWizard.NextButton, "Please wait")
    
        self.setLayout(layout)

###########################################################################################
## Configuration page class
###########################################################################################
class ConfigPage(QWizardPage):
    def __init__(self, parent=None):
        super(ConfigPage, self).__init__(parent)

        self.setTitle("<span style='font-size:20pt;'>EZ-InSAR-3</span>")
        self.setSubTitle("<span style='font-size:15pt;'>Configuration</span>")
        
        label = QLabel("""
                <p><b>Please change the different parameters of EZ-InSAr in order to personalise your installation.</b></p>  
                <p><i>However, it is recommended to keep the default values.</i></p>  
                """
            )
        label.setWordWrap(True)

        layout = QGridLayout()
        layout.addWidget(label, 0, 0, 1, 3)

        tabconfig = QScrollArea()
        tabconfig.setWidgetResizable(True)
        tabconfigwidget = QWidget()
        tabconfig.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tabconfig.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        tabconfiglayout = QGridLayout()

        for idx, vari in enumerate(list(config_var.keys())): 
            exec('self.labelconfig_%s = QLabel("<b>%s</b>")' % (vari,config_var[vari][0]))
            exec('self.labelconfig_%s.setToolTip("%s")' % (vari,config_var[vari][3]))

            if config_var[vari][2] == 'str': 
                exec("self.valueconfig_%s = QLineEdit(r'%s')" % (vari,config_var[vari][1]))

                if vari == 'password':
                    exec('self.valueconfig_%s.setEchoMode(QLineEdit.Password)' % (vari))

            elif config_var[vari][2] == 'bool': 
                exec('self.valueconfig_%s = QCheckBox("Enable (or not) the option")' % (vari))
                exec('self.valueconfig_%s.setChecked(%s)' % (vari,config_var[vari][1]))

            elif config_var[vari][2] == 'int': 
                exec('self.valueconfig_%s = QSpinBox()' % (vari))
                exec('self.valueconfig_%s.setMaximum(1000000)' % (vari))
                exec('self.valueconfig_%s.setMinimum(1)' % (vari))
                exec('self.valueconfig_%s.setValue(%s)' % (vari,config_var[vari][1]))
    
            elif config_var[vari][2] == 'list': 
                exec('self.valueconfig_%s = QComboBox()' % (vari))
                exec('self.valueconfig_%s.addItems(%s)' % (vari,str(config_var[vari][1])))

            exec('tabconfiglayout.addWidget(self.labelconfig_%s, %s, 0, 1, 1)' % (vari,idx+1))
            exec('tabconfiglayout.addWidget(self.valueconfig_%s, %s, 1, 1, 2)' % (vari,idx+1))

        tabconfigwidget.setLayout(tabconfiglayout)
        tabconfig.setWidget(tabconfigwidget)

        layout.addWidget(tabconfig, 1, 0, 10, 3)

        self.setLayout(layout)
  
###########################################################################################
## End page class
###########################################################################################
class EndPage(QWizardPage):
    def __init__(self, parent=None):
        super(EndPage, self).__init__(parent)

        self.setTitle("<span style='font-size:20pt;'>EZ-InSAR-3</span>")
        self.setSubTitle("<span style='font-size:15pt;'>Successfull</span>")

        label = QLabel("""
                <p><b>The installation is done. Do not forget to install the docker image if Windows is used.</b></p>
                """)
    
        label.setWordWrap(True)

        layout = QGridLayout()

        layout.addWidget(label, 0, 0, 1, 3)

        labelshortcut = QLabel("<b>Create the shortcuts:</b>")
        self.checkshortcut = QCheckBox("Enable the creation of shortcuts")
        self.checkshortcut.setChecked(True)
        layout.addWidget(labelshortcut, 1, 0, 1, 1)
        layout.addWidget(self.checkshortcut, 1, 1, 1, 2)

        labelopenDocs = QLabel("<b>Open the documentation:</b>")
        self.checkopenDocs = QCheckBox("Enable the opening of the docs")
        self.checkopenDocs.setChecked(True)
        layout.addWidget(labelopenDocs, 2, 0, 1, 1)
        layout.addWidget(self.checkopenDocs, 2, 1, 1, 2)

        logo = QLabel()
        logo.setPixmap(QPixmap(resource_path('EZ_InSAR_logo_whiteback.svg')).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        layout.addWidget(logo,12,2,3,1, Qt.AlignRight)
        layout.addWidget(QLabel("<span style='font-size:20pt;'><b>Enjoy EZ-InSAR</b></span>"),13,0,1,2, Qt.AlignLeft)

        self.setLayout(layout)

###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path('EZ_InSAR_logo_whiteback.svg')))
    app.setStyle('Fusion')
    wizard = EZInSAR_Installer()
    wizard.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()