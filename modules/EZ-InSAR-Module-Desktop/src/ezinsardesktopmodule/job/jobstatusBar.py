#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module for the creation of the EZ-InSAR job status bar

The module allows to create the creation of the EZ-InSAR job status bar
    
    (Supplementary module for EZ-InSAR)

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Feb. 2025

"""
###########################################################################################
## Packages
###########################################################################################
## For PyQt
from PyQt5.QtCore import QFileInfo, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout

## Python
import os 
import numpy as np

## For EZ-InSAR
from ezinsardesktopmodule.tools import tools
root = QFileInfo(__file__).absolutePath()
from ezinsardesktopmodule import __file__ as __moduleroot__
from ezinsardesktopmodule.config.settings import __theme__

###########################################################################################
## Class creation 
###########################################################################################
class barjobinfowidget(QWidget):
    def __init__(self):    
        super(barjobinfowidget, self).__init__()

        self.setStyleSheet(__theme__)
        
        self.barjobinfo = QGridLayout()

        self.labeljob = None
        self.labeldirectory = None
        self.labelroi = None
        self.labelslclist = None
        self.labelDEM = None
        self.labelcoreg = None
        self.labelifg = None
        self.labelts = None
        self.labelint = None
        self.labeloffset = None

        self.logolabeljob = None
        self.logolabeldirectory = None
        self.logolabelroi = None
        self.logolabelslclist = None
        self.logolabelDEM = None
        self.logolabelcoreg = None
        self.logolabelifg = None
        self.logolabelts = None
        self.logolabelint = None
        self.logolabeloffset = None
       
        self.logolabeljob = QLabel()
        self.logolabeljob.setPixmap(QPixmap(root + '%simages%slights%sred.png' % (os.sep,os.sep,os.sep)).scaledToHeight(16))
        self.labeljob = QLabel("<b>%s</b>" % ('EZ-InSAR job'))
        self.labeljob.setToolTip("Please create or open an EZ-InSAR job")
        self.barjobinfo.addWidget(self.logolabeljob,0,0,1,1,Qt.AlignRight)
        self.barjobinfo.addWidget(self.labeljob,0,1,1,1,Qt.AlignLeft)

        self.logolabeldirectory = QLabel()
        self.logolabeldirectory.setPixmap(QPixmap(root + '%simages%slights%sred.png' % (os.sep,os.sep,os.sep)).scaledToHeight(16))
        self.labeldirectory = QLabel("<b>%s</b>" % ('Directories'))
        self.labeldirectory.setToolTip("Please create or open an EZ-InSAR job")
        self.barjobinfo.addWidget(self.logolabeldirectory,0,2,1,1,Qt.AlignRight)
        self.barjobinfo.addWidget(self.labeldirectory,0,3,1,1,Qt.AlignLeft)

        self.logolabelroi = QLabel()
        self.logolabelroi.setPixmap(QPixmap(root + '%simages%slights%sred.png' % (os.sep,os.sep,os.sep)).scaledToHeight(16))
        self.labelroi = QLabel("<b>%s</b>" % ('Region of Interest'))
        self.labelroi.setToolTip("Please create or open an EZ-InSAR job")
        self.barjobinfo.addWidget(self.logolabelroi,0,4,1,1,Qt.AlignRight)
        self.barjobinfo.addWidget(self.labelroi,0,5,1,1,Qt.AlignLeft)

        self.logolabelslclist = QLabel()
        self.logolabelslclist.setPixmap(QPixmap(root + '%simages%slights%sred.png' % (os.sep,os.sep,os.sep)).scaledToHeight(16))
        self.labelslclist = QLabel("<b>%s</b>" % ('SLC list'))
        self.labelslclist.setToolTip("Please create or open an EZ-InSAR job")
        self.barjobinfo.addWidget(self.logolabelslclist,0,6,1,1,Qt.AlignRight)
        self.barjobinfo.addWidget(self.labelslclist,0,7,1,1,Qt.AlignLeft)

        self.logolabelDEM = QLabel()
        self.logolabelDEM.setPixmap(QPixmap(root + '%simages%slights%sred.png' % (os.sep,os.sep,os.sep)).scaledToHeight(16))
        self.labelDEM = QLabel("<b>%s</b>" % ('Digital elevation Model'))
        self.labelDEM.setToolTip("Please create or open an EZ-InSAR job")
        self.barjobinfo.addWidget(self.logolabelDEM,0,8,1,1,Qt.AlignRight)
        self.barjobinfo.addWidget(self.labelDEM,0,9,1,1,Qt.AlignLeft)

        self.logolabelcoreg = QLabel()
        self.logolabelcoreg.setPixmap(QPixmap(root + '%simages%slights%sred.png' % (os.sep,os.sep,os.sep)).scaledToHeight(16))
        self.labelcoreg = QLabel("<b>%s</b>" % ('Coregistration stack'))
        self.labelcoreg.setToolTip("Please create or open an EZ-InSAR job")
        self.barjobinfo.addWidget(self.logolabelcoreg,1,0,1,1,Qt.AlignRight)
        self.barjobinfo.addWidget(self.labelcoreg,1,1,1,1,Qt.AlignLeft)

        self.logolabelifg = QLabel()
        self.logolabelifg.setPixmap(QPixmap(root + '%simages%slights%sred.png' % (os.sep,os.sep,os.sep)).scaledToHeight(16))
        self.labelifg = QLabel("<b>%s</b>" % ('Interferogram stack'))
        self.labelifg.setToolTip("Please create or open an EZ-InSAR job")
        self.barjobinfo.addWidget(self.logolabelifg,1,2,1,1,Qt.AlignRight)
        self.barjobinfo.addWidget(self.labelifg,1,3,1,1,Qt.AlignLeft)

        self.logolabelts = QLabel()
        self.logolabelts.setPixmap(QPixmap(root + '%simages%slights%sred.png' % (os.sep,os.sep,os.sep)).scaledToHeight(16))
        self.labelts = QLabel("<b>%s</b>" % ('Displacement time-series'))
        self.labelts.setToolTip("Please create or open an EZ-InSAR job")
        self.barjobinfo.addWidget(self.logolabelts,1,4,1,1,Qt.AlignRight)
        self.barjobinfo.addWidget(self.labelts,1,5,1,1,Qt.AlignLeft)

        self.logolabelint = QLabel()
        self.logolabelint.setPixmap(QPixmap(root + '%simages%slights%sred.png' % (os.sep,os.sep,os.sep)).scaledToHeight(16))
        self.labelint = QLabel("<b>%s</b>" % ('Intensity stack'))
        self.labelint.setToolTip("Please create or open an EZ-InSAR job")
        self.barjobinfo.addWidget(self.logolabelint,1,6,1,1,Qt.AlignRight)
        self.barjobinfo.addWidget(self.labelint,1,7,1,1,Qt.AlignLeft)

        self.logo1 = QLabel()
        # self.logo1.setToolTip = '<p>University College Dublin</p>'
        # self.logo1.setPixmap(QPixmap(os.path.dirname(__moduleroot__) + '%simages%sUCDlogo.png' % (os.sep,os.sep)).scaledToHeight(48,Qt.SmoothTransformation))
        # self.logo2 = QLabel()
        # self.logo2.setToolTip = '<p>Research Ireland in Applied Geosiences</p>'
        # self.logo2.setPixmap(QPixmap(os.path.dirname(__moduleroot__) + '%simages%sicrag-logo.png' % (os.sep,os.sep)).scaledToHeight(32,Qt.SmoothTransformation))
        # self.barjobinfo.addWidget(self.logo1,0,10,2,3,Qt.AlignCenter)
        # self.barjobinfo.addWidget(self.logo2,0,14,2,3,Qt.AlignCenter)
        self.barjobinfo.addWidget(self.logo1,0,10,2,1,Qt.AlignCenter)


        self.setLayout(self.barjobinfo)

    def update(self,job=None,jofile=None):
        if job==None:
            import ezinsar.job as ez
            job = ez.load(jofile,verbose=False)

        imagered = root + '%simages%slights%sred.png' % (os.sep,os.sep,os.sep)
        imageorange = root + '%simages%slights%sorange.png' % (os.sep,os.sep,os.sep)
        imagegreen = root + '%simages%slights%sgreen.png' % (os.sep,os.sep,os.sep)

        # For the job
        if not 'EIjob' in str(type(job)):
            image = imagered
            msg = 'No EZ-InSAR job'
        else:
            image = imagegreen
            msg = 'EZ-InSAR job ready'
        self.labeljob.setToolTip(msg)
        pixmap = QPixmap(image)
        self.logolabeljob.setPixmap(pixmap.scaledToHeight(16))

        # For the directories 
        checkdir = [os.path.isdir(job.workdirectory),
                    os.path.isdir(job.pathSLC),
                    os.path.isdir(job.pathorbit),
                    os.path.isdir(job.pathaux),
                    os.path.isdir(job.pathDEM),
        ]
        if np.unique(checkdir).all() == True: 
            image = imagegreen
            msg = 'All directories found.'
        elif True in checkdir:
            image = imageorange
            msg = 'Directory(ies) is/are missing'
        else:
            image = imagered
            msg = 'Directories missing'
        self.labeldirectory.setToolTip(msg)
        pixmap = QPixmap(image)
        self.logolabeldirectory.setPixmap(pixmap.scaledToHeight(16))

        # For the Region of Interest
        if job.roi == None: 
            image = imagered
            msg = 'Please define a Region of Interest'
        else:
            image = imagegreen
            msg = 'Region of Interest defined'
        self.labelroi.setToolTip(msg)
        pixmap = QPixmap(image)
        self.logolabelroi.setPixmap(pixmap.scaledToHeight(16))

        # For the SLC list
        try: 
            len(np.unique(job.SLClist['RelativeOrbit'])) 
            image = imagegreen
            msg = 'SLC list found'
        except:
            image = imagered
            msg = 'Please retrieve a SLC list'
        self.labelslclist.setToolTip(msg)
        pixmap = QPixmap(image)
        self.logolabelslclist.setPixmap(pixmap.scaledToHeight(16))
        
        # For the DEM 
        if job.pathDEM == None or job.nameDEM == None: 
            image = imagered
            msg = 'Please define the DEM'
        else:
            if os.path.isfile(job.pathDEM+os.sep+job.nameDEM): 
                image = imagegreen
                msg = 'DEM defined'
            else: 
                image = imageorange
                msg = 'DEM defined but not stored.'
        self.labelDEM.setToolTip(msg)
        pixmap = QPixmap(image)
        self.logolabelDEM.setPixmap(pixmap.scaledToHeight(16))

        # For the coregistration
        if not job.coregistration == None: 
            tmp = eval("job.coregistration.%s" % (tools.processingstep(job.coregistration)[-1]))
            if tmp['done']['value']: 
                image = imagegreen
                msg = 'Coregistration processing performed.'
            else:
                image = imageorange
                msg = 'Coregistration processing not fully performed.'
        else: 
            image = imagered
            msg = 'No coregistration job'
        self.labelcoreg.setToolTip(msg)
        pixmap = QPixmap(image)
        self.logolabelcoreg.setPixmap(pixmap.scaledToHeight(16))

        # For the ifgstack
        if not job.ifgstack == None: 
            tmp = eval("job.ifgstack.%s" % (tools.processingstep(job.ifgstack)[-1]))
            if tmp['done']['value']: 
                image = imagegreen
                msg = 'Interferometric-stack processing performed.'
            else:
                image = imageorange
                msg = 'Interferometric-stack processing not fully performed.'
        else: 
            image = imagered
            msg = 'No interferometric-stack job'
        self.labelifg.setToolTip(msg)
        pixmap = QPixmap(image)
        self.logolabelifg.setPixmap(pixmap.scaledToHeight(16))

        # For the ts-processing
        if not job.tsprocessing == None: 
            tmp = eval("job.tsprocessing.%s" % (tools.processingstep(job.tsprocessing)[-1]))
            if tmp['done']['value']: 
                image = imagegreen
                msg = 'Time-series-analysis processing performed.'
            else:
                image = imageorange
                msg = 'Time-series-analysis processing not fully performed.'
        else: 
            image = imagered
            msg = 'No time-series-analysis job'
        self.labelts.setToolTip(msg)
        pixmap = QPixmap(image)
        self.logolabelts.setPixmap(pixmap.scaledToHeight(16))

        # For the intensity
        if not job.intstack == None: 
            tmp = eval("job.intstack.%s" % (tools.processingstep(job.intstack)[-1]))
            if tmp['done']['value']: 
                image = imagegreen
                msg = 'Intensity-stack processing performed.'
            else:
                image = imageorange
                msg = 'Intensity-stack processing not fully performed.'
        else: 
            image = imagered
            msg = 'No intensity-stack job'
        self.labelint.setToolTip(msg)
        pixmap = QPixmap(image)
        self.logolabelint.setPixmap(pixmap.scaledToHeight(16))

        job = None