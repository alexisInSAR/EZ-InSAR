#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open the Image-Displayer Widget

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.0.0: Initial version, Mar. 2025

"""

__docstringapp__ = """Open the Image-Displayer Widget

usage: 
    ezinsardesktop_imagedisplayer -f <str> [options]

Arguments:
    -f, --file <str>        Image file

Other-options:
    -h, --help
"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtWidgets import QApplication, QGridLayout, QPushButton, QWidget, QGroupBox, QLabel, QScrollArea

import os, sys
from docopt import docopt
from PIL import Image

from ezinsar import constants, usermessage
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsardesktopmodule.tools import tools

###########################################################################################
## Class for the Wizard
###########################################################################################
class QLabel_clicked(QLabel):
    clicked=pyqtSignal(str)
    

    def mousePressEvent(self, ev):
        if ev.type() == QEvent.MouseButtonDblClick:
            if ev.button() == Qt.LeftButton:
                self.info = 'Zoom in'
                self.clicked.emit(self.info)
            elif ev.button() == Qt.RightButton:
                self.info = 'Zoom out'
                self.clicked.emit(self.info)

class imagedisplayer(QWidget):
    """Class definition"""
    closing = pyqtSignal(bool)

    def __init__(self, file, parent=None):
        super(imagedisplayer, self).__init__(parent)

        self.pathfile = file
        self.setWindowTitle("EZ-InSAR - Image Displayer: %s" % (file.split(os.sep)[-1]))
        self.resize(750, 500)

        self.zoom = 1

        self.setStyleSheet(__theme__)

        
        toolbar = QGroupBox()
        toolbarLayout = QGridLayout()

        iconZoomInLabel = QPushButton()        
        iconZoomInIm = QIcon(os.path.dirname(__file__)+os.sep+'icons'+os.sep+'zoom-in.svg')
        iconZoomInLabel.setIcon(iconZoomInIm)
        iconZoomInLabel.clicked.connect(self.zoomin)

        iconZoomOutLabel = QPushButton()        
        iconZoomOutIm = QIcon(os.path.dirname(__file__)+os.sep+'icons'+os.sep+'zoom-out.svg')
        iconZoomOutLabel.setIcon(iconZoomOutIm)
        iconZoomOutLabel.clicked.connect(self.zoomout)

        iconHomeLabel = QPushButton()        
        iconHometIm = QIcon(os.path.dirname(__file__)+os.sep+'icons'+os.sep+'arrows.svg')
        iconHomeLabel.setIcon(iconHometIm)
        iconHomeLabel.clicked.connect(self.reset)

        toolbarLayout.addWidget(iconZoomInLabel,0,0)
        toolbarLayout.addWidget(iconZoomOutLabel,0,1)
        toolbarLayout.addWidget(iconHomeLabel,0,2)

        toolbar.setLayout(toolbarLayout)

        ########################################################################
        ## ScrollArea
        self.scrollarea = QScrollArea()

        ########################################################################
        ##  Read the image
        self.file = file

        if self.file.endswith('.ras'):
            image = Image.open(self.file).save(constants.__cachedir__+os.sep+'tmp.bmp')
            file = constants.__cachedir__+os.sep+'tmp.bmp'
        else:
            file = self.file

        self.object = QLabel_clicked()
        self.object.clicked.connect(self.clickevent)

        self.image = QImage(file)
        self.pixmap = QPixmap(self.image).scaled(QSize(self.frameGeometry().height()*self.zoom, self.frameGeometry().height()*self.zoom),Qt.KeepAspectRatio, Qt.SmoothTransformation) 
        self.object.setPixmap(self.pixmap)
        self.object.setScaledContents(False)
        self.scrollarea.setWidget(self.object)
        
        #########################################################################
        ## Layout
        layout = QGridLayout()

        layout.addWidget(toolbar, 0, 0, 1, 3)
        layout.addWidget(self.scrollarea, 1, 0, 1, 15)

        self.setLayout(layout)

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def zoomin(self):
        
        vcenter, hcenter = self.getcenter()

        self.object = QLabel_clicked()
        self.object.clicked.connect(self.clickevent)

        self.zoom = self.zoom + 1
        if self.zoom > 5:
            self.pixmap = QPixmap(self.image).scaled(QSize(self.frameGeometry().height()*self.zoom, self.frameGeometry().height()*self.zoom),Qt.KeepAspectRatio) 
        else:
            self.pixmap = QPixmap(self.image).scaled(QSize(self.frameGeometry().height()*self.zoom, self.frameGeometry().height()*self.zoom),Qt.KeepAspectRatio, Qt.SmoothTransformation) 
        self.object.setPixmap(self.pixmap)

        self.object.setPixmap(self.pixmap)
        self.scrollarea.setWidget(self.object)

        self.setcenter(vcenter,hcenter)

    def zoomout(self):
        if self.zoom > 1:
            vcenter, hcenter = self.getcenter()

            self.object = QLabel_clicked()
            self.object.clicked.connect(self.clickevent)

            self.zoom = self.zoom - 1
            if self.zoom > 5:
                self.pixmap = QPixmap(self.image).scaled(QSize(self.frameGeometry().height()*self.zoom, self.frameGeometry().height()*self.zoom),Qt.KeepAspectRatio) 
            else:
                self.pixmap = QPixmap(self.image).scaled(QSize(self.frameGeometry().height()*self.zoom, self.frameGeometry().height()*self.zoom),Qt.KeepAspectRatio, Qt.SmoothTransformation) 
            self.object.setPixmap(self.pixmap)
            self.scrollarea.setWidget(self.object)

            self.setcenter(vcenter,hcenter)

    def reset(self):
        self.object = QLabel_clicked()
        self.object.clicked.connect(self.clickevent)

        self.zoom = 1
        self.pixmap = QPixmap(self.image).scaled(QSize(self.frameGeometry().width()*self.zoom, self.frameGeometry().width()*self.zoom),Qt.KeepAspectRatio, Qt.SmoothTransformation) 
        self.object.setPixmap(self.pixmap)
        self.scrollarea.setWidget(self.object)

    def getcenter(self):
        vmin = self.scrollarea.verticalScrollBar().minimum()
        vmax = self.scrollarea.verticalScrollBar().maximum() - vmin + self.scrollarea.verticalScrollBar().pageStep()
        vcenter = ((self.scrollarea.verticalScrollBar().value() + self.scrollarea.verticalScrollBar().pageStep()/2) - vmin) / (vmax - vmin)

        hmin = self.scrollarea.horizontalScrollBar().minimum()
        hmax = self.scrollarea.horizontalScrollBar().maximum() - hmin + self.scrollarea.horizontalScrollBar().pageStep()
        hcenter = ((self.scrollarea.horizontalScrollBar().value() + self.scrollarea.horizontalScrollBar().pageStep()/2) - hmin) / (hmax - hmin)

        return vcenter, hcenter
    
    def setcenter(self,vcenter,hcenter):
        vmin = self.scrollarea.verticalScrollBar().minimum()
        vmax = self.scrollarea.verticalScrollBar().maximum() - vmin + self.scrollarea.verticalScrollBar().pageStep()
        vvalue = vcenter * (vmax - vmin) + vmin - self.scrollarea.verticalScrollBar().pageStep()/2

        hmin = self.scrollarea.verticalScrollBar().minimum()
        hmax = self.scrollarea.verticalScrollBar().maximum() - hmin + self.scrollarea.horizontalScrollBar().pageStep()
        hvalue = hcenter * (hmax - hmin) + hmin - self.scrollarea.horizontalScrollBar().pageStep()/2

        self.scrollarea.verticalScrollBar().setValue(int(round(vvalue)))
        self.scrollarea.horizontalScrollBar().setValue(int(round(hvalue)))

    def clickevent(self):
        if self.object.info == 'Zoom in':
            self.zoomin()
        elif self.object.info == 'Zoom out':
            self.zoomout()
        
###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not os.path.isfile(args['--file']):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No file',None))
    
    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the Image Displayer from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        widget = imagedisplayer(os.path.abspath(args['--file']))
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()
        
if __name__=='__main__':
    main()

