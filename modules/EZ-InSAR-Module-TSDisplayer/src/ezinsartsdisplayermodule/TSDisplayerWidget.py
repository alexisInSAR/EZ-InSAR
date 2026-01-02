#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR TSDisplayer**: Open the Time-Series Displayer

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.0.0: Initial version, Mar. 2025

"""

__docstringapp__ = """EZ-InSAR TSDisplayer: Open the Time-Series Displayer

usage: 
    ezinsartsdisplayer_run [options]

Options:
    -f, --file <str>        EZ-InSAR job file

Other-options:
    -h, --help
"""
###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, QUrl 
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QMessageBox, QPushButton, QFileDialog, QWidget, QProgressDialog, QDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

import os, sys, time
import requests
from docopt import docopt
from multiprocessing import Process
import socket
import random, string 
import shutil

from ezinsar import constants, usermessage
from ezinsartsdisplayermodule import appbuilder, aboutDial
from ezinsartsdisplayermodule import __namePackage__, __authorPackage__, __copyrightPackage__, __versionPackage__
from ezinsartsdisplayermodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)

from ezinsar.tools import ezinsardata

# Try to import the theme from desktop
try:
    from ezinsardesktopmodule.config.settings import __theme__
except:
    __theme__ = None

__timeouterror__ = 0.5 # in minutes
host = '127.0.0.1'

def portused(port, host):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        result = s.connect_ex((host, port))
        return result == 0  

port = None
for porttest in [8050,8051,8052,8053,8054,8055,8056,8057,8058,8059,8060]: 
    if not portused(porttest,host): 
        port = porttest
        break

if port == None: 
    raise ValueError(usermessage.errormsg(__name__,__name__,__file__,constants.__copyright__,
            'There are not porst free.',None))

###########################################################################################
## Classes
###########################################################################################
class DocsDialog(QDialog):
    """QWidget class 
        Build the widget windows
    """

    def __init__(self, key, parent=None):
        super(DocsDialog, self).__init__(parent)

        self.setWindowTitle("EZ-InSAR - Documentation")
        self.setStyleSheet(__theme__)
        self.resize(750, 750)
        self.parent = parent

        if isinstance(key,list):
            key = os.sep.join(key) + '.html'

        if '#' in key:
            urlbase = key.split('#')[0]
        else:
            urlbase = key
        
        url = '%s%s%s' % (os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
           '%sdocs%sbuild%shtml%s' % (os.sep,os.sep,os.sep,os.sep),
           urlbase)
            
        self.page = QWebEngineView()
        url = QUrl.fromLocalFile(url)

        if '#' in key:
            self.page.loadFinished.connect(self.on_load_finished)
            self.fragment = key[-1]
        self.page.load(url)

        layout = QGridLayout()
        layout.addWidget(self.page, 0, 0, 1, 10)
        self.setLayout(layout)

    def on_load_finished(self, ok): # from ChatGPT
        js_scroll = f"""
                    const el = document.getElementById("{self.fragment}");
                    if (el) {{
                        el.scrollIntoView({{behavior: "smooth"}});
                    }}
                    """
        self.page.page().runJavaScript(js_scroll)

class WebEnginePage(QWebEnginePage):
    """Class definition"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  
        
class tsdiplayer(QWidget):
    """QWidget class 
    """

    def __init__(self, pathfile, parent=None):
        super(tsdiplayer, self).__init__(parent)

        if pathfile == None:
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getOpenFileName(self,
                    "Select an EZ-InSAR data file",'',
                    "*.eidata", options=options)
            pathfile = fileName

        pathfile = os.path.abspath(pathfile)
        try:
            tmp = ezinsardata.loadEZdata(pathfile,verbose=False,partialreading=['datainformation'])
        except Exception as e:
            raise ValueError(usermessage.errormsg(__name__,__name__,__file__,constants.__copyright__,'%s' % (e),None))

        self.pathfile = pathfile
        self.setWindowTitle("EZ-InSAR - Time-Series Displayer - File: %s" % (self.pathfile.split(os.sep)[-1]))
        self.resize(1680, 1200)
        self.parent = parent
        self.cachedir_obs = constants.__cachedir__+os.sep+'tsdisplayer'+''.join(random.choice(string.ascii_lowercase) for i in range(16))

        if not __theme__ == None:
            self.setStyleSheet(__theme__)
        
        ## Start the server
        self.server = Process(target=appbuilder.startWebserver,args=(self.pathfile,host,port,self.cachedir_obs),daemon = True)
        self.server.start()

        ## Initialise the GUI
        widgetlogo = QLabel()
        if QApplication.primaryScreen().size().width() * QApplication.primaryScreen().devicePixelRatio() > 2000:
            x = 128
        else:
            x = 64
        Logo = QPixmap(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_tsdisplayer.svg').scaled(x,x, Qt.KeepAspectRatio,Qt.SmoothTransformation)
        Logo.setDevicePixelRatio(QApplication.primaryScreen().devicePixelRatio())
        widgetlogo.setPixmap(Logo)
        widgettitle = QLabel('<p style="font-size:20px"><b>%s</b></p>' % (self.pathfile.split(os.sep)[-1]))
        
        aboutBt = QPushButton('About')
        aboutBt.clicked.connect(self.openAbout)

        btHelp = QPushButton("Help", self)
        btHelp.clicked.connect(self.openhelp)

        ## Wait for the server
        Dialprogress = QProgressDialog('Loading the application',None,0,100, self)
        Dialprogress.setValue(0)
        Dialprogress.setWindowTitle('Please wait...')
        Dialprogress.show()
        QApplication.processEvents()

        h = 0
        hbis = 0
        start = False
        while start == False:
            try: 
                rep = requests.get('http://%s:%s' % (host,port))
                start = True
            except:
                start = False
            time.sleep(0.1)
            
            h = h + 1
            hbis = hbis + 1
            if h >= 100:
                h = 99
            Dialprogress.setValue(h)
            QApplication.processEvents()

            if hbis > 10*60*__timeouterror__:
                reply = QMessageBox.critical(self, "EZ-InSAR TS-Displayer Error",
                    'Time-out error with the Flask/Dash server.',
                    QMessageBox.Ok)
                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,constants.__copyright__,'Time-out error with the Flask/Dash server.',None))

        time.sleep(1)
        Dialprogress.setValue(100)
        QApplication.processEvents()
        Dialprogress.close()
            
        ## Load the application
        self.mapWidget= QWebEngineView() 
        self.mapWidget.showMaximized()
        self.page = WebEnginePage(self.mapWidget)
        self.mapWidget.setPage(self.page)
        self.mapWidget.load(QUrl('http://%s:%s' % (host,port)))

        ## Add the transparency
        self.page.setBackgroundColor(Qt.transparent)
        self.mapWidget.setAutoFillBackground(True)
        self.mapWidget.setAttribute(Qt.WA_TranslucentBackground)
        self.mapWidget.setStyleSheet("background:transparent")
        self.page.setBackgroundColor(Qt.transparent)

        ## Layout
        layout = QGridLayout()
        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 6, Qt.AlignCenter)
        layout.addWidget(aboutBt, 0, 11, 1, 1)
        layout.addWidget(btHelp, 0, 10, 1, 1)
        layout.addWidget(self.mapWidget, 1, 0, 8, 12)

        self.setLayout(layout)

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def openhelp(self):
        helpdial = DocsDialog(['app'])
        helpdial.show()
        helpdial.exec()

    def closeEvent(self, event):
        ret = QMessageBox.warning(self, "Quit?",
                "Are you sure to quit EZ-InSAR TSDisplayer?",
                QMessageBox.Yes | QMessageBox.Cancel)
        if ret == QMessageBox.Yes:
            self.server.terminate()

            if os.path.isdir(self.cachedir_obs):
                shutil.rmtree(self.cachedir_obs)

            time.sleep(0.1)
            event.accept()
        else: 
            event.ignore()

    def openAbout(self):
        dial = aboutDial.aboutDiag()
        dial.exec_()
        
###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    usermessage.openingmsg(__file__,__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Welcome to EZ-InSAR Time-Series Displayer',None,True,lockfree=True)
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_tsdisplayer_whiteback.svg'))
    widget = tsdiplayer(args['--file'])
    widget.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()
