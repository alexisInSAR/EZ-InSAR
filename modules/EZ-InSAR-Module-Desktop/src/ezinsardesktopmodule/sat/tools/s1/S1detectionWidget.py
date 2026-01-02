#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a window for Sentine-1 relative-orbit and track detection

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 0.1.0: Initial version, Feb. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a window for Sentine-1 relative-orbit and track detection

usage: 
    ezinsardesktop_S1track -f <str> [options]

Arguments:
    -f, --file <str>        EZ-InSAR job file

Other-options:
    -h, --help
"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QUrl
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QPushButton, QWidget, QGroupBox, QListWidget, QMessageBox, QListWidgetItem
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

import os, sys, io, time
import numpy as np
from docopt import docopt

import folium
from folium import plugins
from folium.features import PolyLine

from ezinsar import constants, usermessage
from ezinsar.eicomponents.sensor.s1module import s1iwburstIDapp
import ezinsar.job as ez
from ezinsar import __file__ as __root_EZInSARmodule__
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule.log import logWorker
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule import __versionPackage__, __copyrightPackage__, __namePackage__
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule.config import settings

###########################################################################################
## Classes
###########################################################################################
class Worker(QObject):
    """Worker class"""
    textSignal = pyqtSignal(str)
    finished = pyqtSignal()
    intReady = pyqtSignal(int)
    error = pyqtSignal(str)
    success = pyqtSignal(str)
    
    def __init__(self, jobfile, parent=None):
        super(Worker, self).__init__(parent)

        self.jobfile = jobfile
        self.TextInfo = ''
        self.job = ez.load(jobfile,verbose=False)
        self.running = True
        self.messageerror = ''
        self.messagesuccess = ''
        self.result = None
        self.resultanalyse = None

    def run(self):
        try:
            self.job.satpass = None
            self.job.relorbit = None
            jobdetect = s1iwburstIDapp.S1burstIDmap().checkfile(verbose=False).downloadfile(verbose=False).detectfromIDmap(self.job,verbose=False)
            self.result = jobdetect.Data
            a, b , res = jobdetect.analyse(self.job,verbose=False)
            self.resultanalyse = [a,b,res]
            time.sleep(1)
            self.messagesuccess = 'Detection successfull'
            self.success.emit(self.messagesuccess)
        except:
            time.sleep(1)
            self.messageerror = 'Error during the detection'
            self.error.emit(self.messageerror)

        self.running=False
        self.finished.emit()
    
class WebEnginePage(QWebEnginePage):
    """Class for the Web Engine"""
    roiSignal = pyqtSignal(str) 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  
        self.roi = ''    

class S1detectiontrack(QWidget):
    """Class for the Widget"""
    closing = pyqtSignal(bool)

    def __init__(self, jobfile, parent=None):
        super(S1detectiontrack, self).__init__(parent)

        self.pathjobfile = jobfile
        self.setWindowTitle("EZ-InSAR - Sentinel-1 Track and Orbit detection")
        self.resize(750,500)
        self.success = False
        self.false = False
        self.parent = parent
        self.workerprocess = None
        self.threadprocess = None

        self.setStyleSheet(__theme__)

        self.mapid = constants.__cachedir__ + os.sep + 'maptmp.html'

        ## Read the job
        job = ez.load(self.pathjobfile,verbose=False)
        
        ## Title + quit button
        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p style="font-size:20px"><b>Sentinel-1 Track and Orbit detection<\b></p>')
        btQuit = QPushButton("Close", self)

        m, data = self.createmap(job.roi)
        
        self.mapWidget= QWebEngineView() 
        self.page = WebEnginePage(self.mapWidget)
        self.mapWidget.setPage(self.page)

        if not settings.__foliumCached__:
            data = io.BytesIO()
            m.save(data, close_file=False)
            self.mapWidget.setHtml(data.getvalue().decode())
        else:
            if os.path.isfile(self.mapid):
                os.remove(self.mapid)
            m.save(self.mapid,close_file=True) 
            self.mapWidget.load(QUrl.fromLocalFile(self.mapid))

        grp1 = QGroupBox('Detection')
        grp1Layout = QGridLayout()
        self.btrun = QPushButton('Run the detection')
        self.btrun.clicked.connect(self.progress)
        grp1Layout.addWidget(self.btrun,0,0,1,1)
        grp1.setLayout(grp1Layout)

        grp2 = QGroupBox('Results')
        grp2Layout = QGridLayout()
        self.listresult = QListWidget()
        self.listresult.itemSelectionChanged.connect(self.unlockbt)
        self.importtojob = QPushButton('Save to the job')
        grp2Layout.addWidget(self.listresult,0,0,3,1)
        grp2Layout.addWidget(self.importtojob,3,0,1,1)
        grp2.setLayout(grp2Layout)
        self.importtojob.setEnabled(False)
        self.importtojob.clicked.connect(self.savetojob)

        layout = QGridLayout()
        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 8, Qt.AlignCenter)
        layout.addWidget(self.mapWidget, 1, 0, 9, 6)
        layout.addWidget(grp1, 1, 6, 1, 4)
        layout.addWidget(grp2, 2, 6, 1, 4)
        layout.addWidget(btQuit, 0, 9, 1, 1)
        self.setLayout(layout)

        btQuit.clicked.connect(self.closemaybe)

        job = None

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def createmap(self,roi,result=None):
        """Create the map"""

        m = folium.Map(
            location=[0,0], zoom_start=1,
            tiles=None,
            )
        folium.raster_layers.TileLayer(tiles='openstreetmap', name='OpenStreetMap').add_to(m)

        if not roi == None:
            lat = roi.exterior.xy[1]
            lon = roi.exterior.xy[0]

            folium.PolyLine(list(zip(lat,lon)),
                        color='red',
                        weight=2,
                        popup=folium.Popup('Region of Interest'),
                        opacity=1).add_to(m)
            folium.PolyLine(list(zip([np.min(lat), np.min(lat), np.max(lat), np.max(lat), np.min(lat)],
                                    [np.min(lon),np.max(lon),np.max(lon),np.min(lon), np.min(lon)])),
                        color='black',
                        weight=2,
                        popup=folium.Popup('ROI used by EZ-InSAR'),
                        opacity=1).add_to(m)
            
            if not result == None:
                # Compute the color
                listtrack = []
                for tracki in result:
                    listtrack.append(tracki)

                listtrackunique = np.unique(listtrack)
                listcolor = []
                for li in listtrackunique:
                    a = np.random.randint(255, size=3)
                    listcolor.append((a[0],a[1],a[2]))
                
                # Calculation of the map extent
                lonall = []
                latall = []
                for tracki in result:
                    ni = np.where(tracki == listtrackunique)[0][0]
                    for idx in ['1','2','3']: 
                        for iwi in result[tracki]['IW%s' %(idx)]:
                            lonall = lonall + iwi['polyburst'].exterior.coords.xy[0].tolist()
                            latall = latall + iwi['polyburst'].exterior.coords.xy[1].tolist()

                for tracki in result:
                    ni = np.where(tracki == listtrackunique)[0][0]
                    fg = folium.FeatureGroup('S1: %s' %(tracki))
                    for idx in ['1','2','3']: 
                        for iwi in result[tracki]['IW%s' %(idx)]:
                                folium.PolyLine(list(zip(iwi['polyburst'].exterior.coords.xy[1],
                                    iwi['polyburst'].exterior.coords.xy[0])),
                                    color='#%02x%02x%02x' % (int(listcolor[ni][0]),int(listcolor[ni][1]),int(listcolor[ni][2])),
                                    weight=2,
                                    opacity=1).add_to(fg)
                    fg.add_to(m)
                              
                m.fit_bounds([[np.min(latall), np.min(lonall)], [np.max(latall), np.max(lonall)]])
            else: 
                m.fit_bounds([[np.min(lat), np.min(lon)], [np.max(lat), np.max(lon)]])

            m  = tools.addfoliumTile(m)
            folium.LayerControl(collapsed=True).add_to(m)

        data = io.BytesIO()
        m.save(data, close_file=False)

        return m, data
            
    def closemaybe(self):
        """Close"""
        self.closing.emit(True)
        return self.close()
    
    def messageerror(self,msg):
        """Error message
        """
        reply = QMessageBox.critical(self, "EZ-InSAR Error",
                msg,
                QMessageBox.Ok)
        
    def messagesuccess(self,msg):
        reply = QMessageBox.information(self, "EZ-InSAR Information",
                msg,
                QMessageBox.Ok)
    
    def progress(self):
        """Run the progressing 
        """
        self.btrun.setEnabled(False)

        if self.parent == None:
            if self.workerprocess == None:
                self.messagesuccess('Detection in progress')
                self.workerprocess = Worker(self.pathjobfile)
                self.threadprocess = QThread()
                self.workerprocess.moveToThread(self.threadprocess)
                self.threadprocess.started.connect(self.workerprocess.run)
                self.workerprocess.finished.connect(self.threadprocess.quit)
                self.workerprocess.error.connect(self.messageerror)
                self.workerprocess.success.connect(self.messagesuccess)
                self.workerprocess.success.connect(self.successupdate)
                self.workerprocess.finished.connect(self.stopcurrentworker)      
                self.threadprocess.start()
            else:
                self.messageerror('The worker is still running. Please stop it, if required')

        else:
            job = ez.load(self.pathjobfile,verbose=False)
            logfile = job.log
            job = None

            if self.parent.workerprocess == None:
                self.parent.dockprogressbar.show()
                self.parent.messagesuccess('Detection in progress')
                self.parent.workerprocess = Worker(self.pathjobfile)
                self.parent.threadprocess = QThread()
                self.parent.workerprocess.moveToThread(self.parent.threadprocess)
                self.parent.threadprocess.started.connect(self.parent.workerprocess.run)
                self.parent.workerprocess.finished.connect(self.parent.threadprocess.quit)
                self.parent.workerprocess.textSignal.connect(self.parent.updateTextEditverbose)
                self.parent.workerprocess.error.connect(self.parent.messageerror)
                self.parent.workerprocess.success.connect(self.parent.messagesuccess)
                self.parent.workerprocess.success.connect(self.successupdateforparent)
                self.parent.workerprocess.finished.connect(self.parent.stopcurrentworker)   
                self.parent.workerprocess.success.connect(self.parent.stopcurrentworker)

                self.parent.workerlog = logWorker.Worker(logfile,self.parent.workerprocess)
                self.parent.threadlog = QThread()
                self.parent.workerlog.moveToThread(self.parent.threadlog)
                self.parent.workerlog.textSignal.connect(self.parent.updateTextEditverbose)
                self.parent.threadlog.started.connect(self.parent.workerlog.run)
                self.parent.workerlog.finished.connect(self.parent.threadlog.quit)

                self.parent.threadprocess.start()
                self.parent.threadlog.start()
                self.parent.qtCancel.setEnabled(True)
                
            else:
                self.messageerror('The worker is still running. Please stop it, if required')
                
    def stopcurrentworker(self):
        """Stop the current worker
        """
        self.workerprocess = None
        self.btrun.setEnabled(True)
        
    def updateresult(self,result):
        self.listresult.clear()

        for idx, tracki in enumerate(result[2]['name']):
            item = QListWidgetItem(tracki.replace('_',' '))
            item.setToolTip("""
                            <p>%s</p>
                            <p>with %s required sub-swath(s)</p>
                            <p>and %s burst(s)</p> 
                            <p>%0.2f %% of overlap</p>
                            """
                            % (tracki.replace('_',' '),
                            result[2]['sw'][idx],
                            result[2]['nbb'][idx],
                            result[2]['overlap'][idx],
                            )
            )
            self.listresult.addItem(item)

    def unlockbt(self):
        self.importtojob.setEnabled(True)

    def successupdate(self):
        job = ez.load(self.pathjobfile,verbose=False)
        if self.workerprocess.messageerror == '':
            m, data = self.createmap(job.roi,result=self.workerprocess.result)
            if not settings.__foliumCached__:
                data = io.BytesIO()
                m.save(data, close_file=False)
                self.mapWidget.setHtml(data.getvalue().decode())
            else:
                if os.path.isfile(self.mapid):
                    os.remove(self.mapid)
                m.save(self.mapid,close_file=True) 
                self.mapWidget.load(QUrl.fromLocalFile(self.mapid))

            self.updateresult(self.workerprocess.resultanalyse)

        job = None

    def successupdateforparent(self):
        job = ez.load(self.pathjobfile,verbose=False)
        if self.parent.workerprocess.messageerror == '':
            m, data = self.createmap(job.roi,result=self.parent.workerprocess.result)

            if not settings.__foliumCached__:
                data = io.BytesIO()
                m.save(data, close_file=False)
                self.mapWidget.setHtml(data.getvalue().decode())
            else:
                if os.path.isfile(self.mapid):
                    os.remove(self.mapid)
                m.save(self.mapid,close_file=True) 
                self.mapWidget.load(QUrl.fromLocalFile(self.mapid))

            self.updateresult(self.parent.workerprocess.resultanalyse)
            
        job = None

    def savetojob(self):
        job = ez.load(self.pathjobfile,verbose=False)
        job.satpass = self.listresult.currentItem().text().split(' ')[0]
        job.relorbit = int(self.listresult.currentItem().text().split(' ')[1])
        ez.save(job,self.pathjobfile,verbose=False)
        job = None
        self.messagesuccess('New satellite parameters saved to the EZ-InSAR job.')

###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not os.path.isfile(args['--file']):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No file',None))
    
    job = ez.load(os.path.abspath(args['--file']),verbose=False)
    if (not job.satellite == 'IW') and (not job.satmode == 'IW'): 
        job = None
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'This tool is only available with Sentinel-1 IW data.',None))
    job = None

    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open a window for Sentine-1 relative-orbit and track detection',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    
    if tools.checklicense():
        widget = S1detectiontrack(os.path.abspath(args['--file']))
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()
