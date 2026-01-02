#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a window for the EZ-InSAR extent map

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Mar. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a window for the EZ-InSAR extent map

usage: 
    ezinsardesktop_SLCmap -f <str> [options]

Arguments:
    -f, --file <str>        EZ-InSAR job file

Other-options:
    -h, --help
"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QPushButton, QWidget, QProgressDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

import os, sys, io
import numpy as np
from docopt import docopt
import datetime

from shapely.wkt import loads
import branca.colormap as cm

import folium
from folium import plugins
from folium.features import PolyLine

from ezinsar import constants, usermessage
import ezinsar.job as ez
from ezinsar import __file__ as __root_EZInSARmodule__
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule.config import settings
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsardesktopmodule.tools.docsWidget import DocsDialog

###########################################################################################
## Classes
###########################################################################################
class WebEnginePage(QWebEnginePage):
    """Class for the Web Engine"""
    roiSignal = pyqtSignal(str) 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  
        self.roi = ''    

class SLClistmap(QWidget):
    """Class for the Widget"""
    closing = pyqtSignal(bool)

    def __init__(self, jobfile, parent=None):
        super(SLClistmap, self).__init__(parent)

        self.pathjobfile = jobfile
        self.setWindowTitle("EZ-InSAR job - Map of SLC extents")
        self.resize(750,500)
        self.success = False
        self.false = False

        self.mapid = constants.__cachedir__ + os.sep + 'maptmp.html'

        self.setStyleSheet(__theme__)

        ## Read the job
        job = ez.load(self.pathjobfile,verbose=False)
        
        ## Title + quit button
        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p style="font-size:20px"><b>Single-Look-Complex Extent Map</b></p>')
        btQuit = QPushButton("Close", self)

        btHelp = QPushButton("Help", self)
        btHelp.clicked.connect(self.openhelp)

        self.diagprogress = QProgressDialog('Creation of the map',None,0,100, self)
        self.diagprogress.setStyleSheet(__theme__)
        self.diagprogress.setWindowTitle('In progress')
        self.diagprogress.show()

        latall = []
        lonall = []

        m = folium.Map(
            location=[0,0], zoom_start=1,
            )
        
        data_tree = {"label": "Single-Look-Complex Images",
                    "select_all_checkbox": "Un/select all",
                    "children": []}
        
        datesorted = []
        datesortedtimestamp = []
        checkZ = False
        for idxrow, row in job.SLClist.iterrows():
            if 'Z' in row['Date1']:
                checkZ = True
            else:
                checkZ = False
            datesorted.append(datetime.datetime.strptime(row['Date1'].replace('Z',''),'%Y-%m-%dT%H:%M:%S.%f'))
            datesortedtimestamp.append(datetime.datetime.strptime(row['Date1'].replace('Z',''),'%Y-%m-%dT%H:%M:%S.%f').timestamp())
        np.sort(datesorted).tolist().reverse()
        np.sort(datesortedtimestamp).tolist().reverse()
    
        colormapjet = cm.LinearColormap(['blue','green','red'], vmin=np.min(datesortedtimestamp), vmax=np.max(datesortedtimestamp))

        for idx, di in enumerate(datesorted):
            if checkZ:
                distr = di.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                distr = di.strftime('%Y-%m-%dT%H:%M:%S.%f')
            idxnpos = list(job.SLClist['Date1']).index(distr)
            
            rowi = job.SLClist.iloc[idxnpos]
            datetmp = datetime.datetime.strptime(rowi['Date1'].replace('Z',''),'%Y-%m-%dT%H:%M:%S.%f')

            check_year = False
            for idxi1, tmpi1 in enumerate(data_tree['children']):
                if str(datetmp.year) == tmpi1["label"]:
                    check_year = True
                    idxyear = idxi1
            if not check_year:
                data_tree['children'].append({"label": "%s" % (str(datetmp.year)),
                                    "select_all_checkbox": "Un/select all",
                                    "children": []})
            check_year = False    
            for idxi1, tmpi1 in enumerate(data_tree['children']):
                if str(datetmp.year) == tmpi1["label"]:
                    check_year = True
                    idxyear = idxi1

            check_month = False
            for idxi2, tmpi2 in enumerate(data_tree['children'][idxyear]['children']):
                if datetmp.strftime('%b') == tmpi2["label"]:
                    check_month = True
                    idxmonth = idxi2
            if not check_month:
                data_tree['children'][idxyear]['children'].append({"label": "%s" % (datetmp.strftime('%b')),
                                                                    "select_all_checkbox": "Un/select all",
                                                                    "children": []})
            check_month = False
            for idxi2, tmpi2 in enumerate(data_tree['children'][idxyear]['children']):
                if datetmp.strftime('%b') == tmpi2["label"]:
                    check_month = True
                    idxmonth = idxi2

            check_day = False
            for idxi3, tmpi3 in enumerate(data_tree['children'][idxyear]['children'][idxmonth]['children']):
                if str(datetmp.day) == tmpi3["label"]:
                    check_day = True
                    idxday = idxi3
            if not check_day:
                data_tree['children'][idxyear]['children'][idxmonth]['children'].append({"label": "%s" % (str(datetmp.day)),
                                                                    "select_all_checkbox": "Un/select all",
                                                                    "children": []})
            check_day = False
            for idxi3, tmp3 in enumerate(data_tree['children'][idxyear]['children'][idxmonth]['children']):
                if str(datetmp.day) == tmp3["label"]:
                    check_day = True
                    idxday = idxi3

            lat = loads(rowi['PolyFrame']).exterior.xy[1]
            lon = loads(rowi['PolyFrame']).exterior.xy[0]
            lonall = lonall + lon.tolist()
            latall = latall + lat.tolist()

            strtext = ''
            for keyi in rowi.keys():
                if not keyi == 'Quicklook':
                        strtext = strtext + '<p><b>%s:</b> %s</p>' % (keyi, row[keyi])
                # else:    
                #         if (not row[keyi] == None): 
                #                 strtext = strtext + '<p><b>Quicklook:</b></p>'
                #                 strtext = strtext + '<img src="%s" alt="%s" width="300">' % (row[keyi],row[keyi])   

            iframe = folium.IFrame(strtext)
            popup = folium.Popup(iframe, min_width=300, max_width=300)
                         
            data_tree['children'][idxyear]['children'][idxmonth]['children'][idxday]['children'].append(
                        {"label": rowi['Date1'], 
                         "layer": PolyLine(list(zip(lat,lon)),
                                        color=colormapjet(datesortedtimestamp[idx]),
                                        popup=popup,
                                        show=False,
                                        ).add_to(m),
                        },
                        )

            self.diagprogress.setValue(int(100*((idx+1)/len(job.SLClist['Name']))))
            QApplication.processEvents()

        m = tools.addfoliumTile(m)

        m.fit_bounds([[np.min(latall), np.min(lonall)], [np.max(latall), np.max(lonall)]])     
        plugins.MousePosition().add_to(m)
        plugins.MeasureControl().add_to(m)
        folium.LayerControl(collapsed=True).add_to(m)
        plugins.treelayercontrol.TreeLayerControl(overlay_tree=data_tree,
                                                ).add_to(m)

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

        layout = QGridLayout()
        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 8, Qt.AlignCenter)
        layout.addWidget(self.mapWidget, 2, 0, 9, 10)
        layout.addWidget(btQuit, 0, 9, 1, 1)
        layout.addWidget(btHelp, 15, 0, 1, 1)
        self.setLayout(layout)

        btQuit.clicked.connect(self.closemaybe)

        job = None

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def closemaybe(self):
        """Close"""
        self.closing.emit(True)
        return self.close()
    
    def openhelp(self):
        helpdial = DocsDialog(['applications','satellite','satslclist'])
        helpdial.show()
        helpdial.exec()

###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not os.path.isfile(args['--file']):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No file',None))
    
    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the SLC map from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    
    if tools.checklicense():
        widget = SLClistmap(os.path.abspath(args['--file']))
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()
