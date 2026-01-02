#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a window for Sentine-1 baseline pre-computation with ASF server

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 0.1.0: Initial version, Feb. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a window for Sentine-1 baseline pre-computation with ASF server

usage: 
    ezinsardesktop_S1baselines -f <str> [options]

Arguments:
    -f, --file <str>        EZ-InSAR job file

Other-options:
    -h, --help
"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QPushButton, QWidget, QGroupBox, QMessageBox, QComboBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

import os, sys
import datetime
from docopt import docopt

from ezinsar import usermessage
import ezinsar.job as ez
from ezinsar import __file__ as __root_EZInSARmodule__
from ezinsardesktopmodule import __file__ as __root_module__
from ezinsardesktopmodule import __versionPackage__, __copyrightPackage__, __namePackage__
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule.tools import tools
__root_module__ = os.path.dirname(__root_module__)
from ezinsar.api import ASFapi  
import plotly.graph_objects as go
import plotly

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

class S1asfbaselines(QWidget):
    """Class for the Widget"""
    closing = pyqtSignal(bool)

    def __init__(self, jobfile, parent=None):
        super(S1asfbaselines, self).__init__(parent)

        self.pathjobfile = jobfile
        self.setWindowTitle("EZ-InSAR - Sentinel ASF Baselines")
        self.resize(750, 500)
        self.success = False
        self.false = False
        self.parent = parent
        self.log = None

        self.setStyleSheet(__theme__)

        ## Read the job
        job = ez.load(self.pathjobfile,verbose=False)
        self.log = job.log
        
        ## Title + quit button
        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p style="font-size:20px"><b>Sentinel ASF Baselines</b></p>')
        btQuit = QPushButton("Close", self)

        info = QLabel('<p><i>This tool offers the possibility to visualise the perpendicular baselines from the ASF computations. This is based on S1 IW frames and will be not accurate compared to the baseline computation performed during processing EZ-InSAR job. This computation is performed for all images.</i></p>')
        info.setWordWrap(True)
        
        grp0 = QGroupBox('Selection')
        grp0Layout = QGridLayout()
        frameLabel = QLabel("<b>S1-IW selected frame:</b>")
        self.frame = QComboBox()
        self.frame.addItems(job.SLClist['Name'])
        grp0Layout.addWidget(frameLabel,0,0,1,1)
        grp0Layout.addWidget(self.frame,0,1,1,1)
        grp0.setLayout(grp0Layout)
        self.btrun = QPushButton('Start the computation')
        self.btrun.clicked.connect(self.process)

        self.grp1 = QGroupBox('Results')
        self.grp1Layout = QGridLayout()
        self.grp1Layout.addWidget(QLabel(''))
        self.grp1.setLayout(self.grp1Layout)

        layout = QGridLayout()
        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 8, Qt.AlignCenter)
        layout.addWidget(info, 1, 0, 1, 10)
        layout.addWidget(grp0, 2, 0, 1, 10)
        layout.addWidget(self.btrun,3,0,1,10)
        layout.addWidget(self.grp1, 4, 0, 7, 10)
        layout.addWidget(btQuit, 0, 9, 1, 1)
        self.setLayout(layout)

        btQuit.clicked.connect(self.closemaybe)

        job = None

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def process(self):
        for i in reversed(range(self.grp1Layout.count())): 
            self.grp1Layout.itemAt(i).widget().setParent(None)

        self.btrun.setEnabled(False)
        self.messagesuccess('In progress, please wait...')

        QApplication.setOverrideCursor(Qt.WaitCursor)

        framename = self.frame.currentText().replace('.zip','').replace('SAFE','')
    
        try:
            listdata = ASFapi.baseline(framename,log=self.log,verbose=False)
            success = True
            errormsg = ''
        except Exception as e:
            success = False
            errormsg = '%s' % (e)

        if success:
            dates = []
            for di in listdata['Date1'].to_list():
                    dates.append(datetime.datetime.strptime(di,'%Y-%m-%dT%H:%M:%S.%fZ'))
            bperp = listdata['perpendicularBaseline'].to_list()

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=dates, y=bperp,
                name='Reference: %s' % (framename),
                mode='markers',
                marker_color='black'
            ))
            fig.update_traces(mode='markers',marker_size=10)
            fig.update_layout(yaxis_zeroline=True)
            fig.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(
                    title=dict(
                        text="Time"
                    )
                ),
                yaxis=dict(
                    title=dict(
                        text="Perpendicular Baseline [m]"
                    )
                ),
            )

            html = '<html><body>'
            html = html + plotly.offline.plot(fig, output_type='div', include_plotlyjs='cdn')
            html = html + '</body></html>'

            FigureWidget= QWebEngineView() 
            FigureWidget.setHtml(html)

            self.grp1Layout.addWidget(FigureWidget)
            self.messagesuccess('Baseline computation performed.')
        else:
            self.grp1Layout.addWidget(QLabel(''))
            self.messageerror('Error: %s' % (errormsg))

        QApplication.restoreOverrideCursor()
        self.btrun.setEnabled(True)
            
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

    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open a window for Sentine-1 baseline pre-computation with ASF server',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        widget = S1asfbaselines(os.path.abspath(args['--file']))
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()
