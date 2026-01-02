#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Create a widget for tools

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 1.1.0: Various changes, Aug. 2025, Alexis Hrysiewicz
        * Change the logos
        * Add new tools
    * 1.0.0: Initial version, Mar. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Create a widget for tools

usage: 
    plugins.py [options]

Other-options:
    -h, --help
"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtGui import QIcon,  QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QApplication, QGridLayout, QMessageBox, QWidget, QLineEdit, QFileDialog, QTreeView, QAbstractItemView, QDialog, QLabel, QPushButton

import os, sys
import subprocess
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import ezinsar.job as ez
from ezinsar.tools import ezinsardata

from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsardesktopmodule.tools.docsWidget import DocsDialog
from ezinsardesktopmodule.log import logcallbacks, logWorker

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

##########################################################################################
## Classes
##########################################################################################
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, figobj, axesobj, parent=None, dpi=100):
        self.fig, self.axes = plt.subplots()
        self.fig = figobj
        self.axes = axesobj
        self.axes.patch.set_alpha(0.0)
        super().__init__(self.fig)
        self.setStyleSheet("background: transparent") 
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(True)

class dummyfigure(QDialog):
    def __init__(self, figobj, axesobj, title, parent=None):
        super(dummyfigure, self).__init__(parent)
        self.resize(750, 750)
        self.setStyleSheet(__theme__)
        self.setWindowTitle("%s" % (title))
        Layout = QGridLayout()
        self.sc = MplCanvas(figobj, axesobj, dpi=300)
        toolbar = NavigationToolbar(self.sc, self)
        toolbar.setStyleSheet("background-color: rgba(255, 255, 255, 150);")
        Layout.addWidget(toolbar,0,0,1,1)
        Layout.addWidget(self.sc,1,0,1,1)
        self.setLayout(Layout)

class plugins(QWidget):
    """Plugin Widget"""

    def __init__(self, log = None, parent=None):
        super(plugins, self).__init__(parent)

        self.setWindowTitle("EZ-InSAR - Plugins")
        self.resize(750, 500)
        self.success = False
        self.false = False
        self.parent = parent
        self.log = log

        self.listtools = []

        self.setStyleSheet(__theme__)

        self.main = QTreeView()
        parent = QStandardItemModel()

        ## Detect if the mode is dark or not
        background_color = self.palette().color(self.backgroundRole())
        if (0.299 * background_color.red() + 0.587 * background_color.green() + 0.114 * background_color.blue()) < 128:
            # Dark mode: YES
            exticons = 'icons'+os.sep+'light'+os.sep
        else:
            # Dark mode: NO
            exticons = 'icons'+os.sep+'dark'+os.sep

        ########################################################################
        ## For the EZ-InSAR CORE
        ########################################################################
        ezinsarcore = QStandardItem('EZ-InSAR')
        ezinsarcore.setIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))

        # For EZ-InSAR job
        ezinsarcorejobtools_0 = QStandardItem('Smart modificaiton of paths')
        ezinsarcorejobtools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'paper.png'))
        ezinsarcorejobtools_0.setToolTip('Tools to modify the paths inside an EZ-InSAR job.')
        self.listtools.append('Smart modificaiton of paths')
        ezinsarcorejob = QStandardItem('Advanced tools for EZ-InSAR jobs')
        ezinsarcorejob.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'paper.png'))
        ezinsarcorejob.appendRow(ezinsarcorejobtools_0)

        parent.appendRow([ezinsarcorejob])

        # For Sentinel-1
        ezinsarcoresatelliteS1tools_0 = QStandardItem('Detection of Sentinel-1 IW Track')
        ezinsarcoresatelliteS1tools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
        ezinsarcoresatelliteS1tools_0.setToolTip('Offers a quick detection of best Sentinel-1 track and orbit regarding an EZ-InSAR job.')
        self.listtools.append('Detection of Sentinel-1 IW Track')

        ezinsarcoresatelliteS1tools_1 = QStandardItem('Pre-computaton of Sentinel-1 IW Baselines')
        ezinsarcoresatelliteS1tools_1.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
        ezinsarcoresatelliteS1tools_1.setToolTip('Pre-computation of Sentinel-1 IW perpendicular baselines from ASF data.')
        self.listtools.append('Pre-computaton of Sentinel-1 IW Baselines')

        ezinsarcoresatelliteS1tools_2 = QStandardItem('List the planned Sentinel-1 acquisitions')
        ezinsarcoresatelliteS1tools_2.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'sat.png'))
        ezinsarcoresatelliteS1tools_2.setToolTip('List the planned Sentinel-1 acquisitions as planned by ESA.')
        self.listtools.append('List the planned Sentinel-1 acquisitions')

        ezinsarcoresatelliteS1 = QStandardItem('Sentinel-1')
        ezinsarcoresatelliteS1.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'sat.png'))
        ezinsarcoresatelliteS1.appendRow(ezinsarcoresatelliteS1tools_0)
        ezinsarcoresatelliteS1.appendRow(ezinsarcoresatelliteS1tools_1)
        ezinsarcoresatelliteS1.appendRow(ezinsarcoresatelliteS1tools_2)

        # For Satellite
        ezinsarcoresatellite =  QStandardItem('Satellite') 
        ezinsarcoresatellite.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'sat.png'))
        ezinsarcoresatellite.appendRow(ezinsarcoresatelliteS1)

        parent.appendRow([ezinsarcoresatellite])
        
        # For Processing
        ezinsarcoreprocessingTStools_0 = QStandardItem('Define a reference point')
        ezinsarcoreprocessingTStools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'map.png'))
        ezinsarcoreprocessingTStools_0.setToolTip('Help for the definition of a reference regarding Time-series analysis processing')
        self.listtools.append('Define a reference point')

        ezinsarcoreprocessingTStools_1 = QStandardItem('Create a mask')
        ezinsarcoreprocessingTStools_1.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
        ezinsarcoreprocessingTStools_1.setToolTip('Create a user-defined mask for Time-series analysis processing')
        self.listtools.append('Create a mask')

        ezinsarcoreprocessingTStools = QStandardItem('Time-Series Analysis')
        ezinsarcoreprocessingTStools.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
        ezinsarcoreprocessingTStools.appendRow(ezinsarcoreprocessingTStools_0)
        ezinsarcoreprocessingTStools.appendRow(ezinsarcoreprocessingTStools_1)

        ezinsarcoreprocessing =  QStandardItem('Processing') 
        ezinsarcoreprocessing.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
        ezinsarcoreprocessing.appendRow(ezinsarcoreprocessingTStools)

        parent.appendRow([ezinsarcoreprocessing])

        # For Display
        ezinsarcoredisplayquicklooktools_0 = QStandardItem('Quicklook of InSAR-derived velocity')
        ezinsarcoredisplayquicklooktools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'map.png'))
        ezinsarcoredisplayquicklooktools_0.setToolTip('Quicklook of displacement velocity')
        self.listtools.append('Quicklook of InSAR-derived velocity')

        ezinsarcoredisplayquicklooktools_1 = QStandardItem('Quicklook of InSAR-derived velocity standard deviation')
        ezinsarcoredisplayquicklooktools_1.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'map.png'))
        ezinsarcoredisplayquicklooktools_1.setToolTip('Quicklook of STD displacement velocity')
        self.listtools.append('Quicklook of InSAR-derived velocity standard deviation')

        ezinsarcoredisplayquicklooktools_2 = QStandardItem('Quicklook of used interferometric network')
        ezinsarcoredisplayquicklooktools_2.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'display.png'))
        ezinsarcoredisplayquicklooktools_2.setToolTip('Quicklook of used interferometric network')
        self.listtools.append('Quicklook of used interferometric network')

        ezinsarcoredisplayquicklook = QStandardItem('Quicklook') 
        ezinsarcoredisplayquicklook.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'map.png'))
        ezinsarcoredisplayquicklook.appendRow(ezinsarcoredisplayquicklooktools_0)
        ezinsarcoredisplayquicklook.appendRow(ezinsarcoredisplayquicklooktools_1)
        ezinsarcoredisplayquicklook.appendRow(ezinsarcoredisplayquicklooktools_2)

        ezinsarcoredisplayinsitutools_0 = QStandardItem('Open the in-situ data displayer')
        ezinsarcoredisplayinsitutools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'display.png'))
        ezinsarcoredisplayinsitutools_0.setToolTip('Open the in-situ data displayer')
        self.listtools.append('Open the in-situ data displayer')

        ezinsarcoredisplayinsitu = QStandardItem('In-situ') 
        ezinsarcoredisplayinsitu.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'field.png'))
        ezinsarcoredisplayinsitu.appendRow(ezinsarcoredisplayinsitutools_0)

        ezinsarcoredisplayimagetools_0 = QStandardItem('Open the image inspector')
        ezinsarcoredisplayimagetools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'display.png'))
        ezinsarcoredisplayimagetools_0.setToolTip('Open the image inspector')
        self.listtools.append('Open the image inspector')

        ezinsarcoredisplayimage = QStandardItem('Image') 
        ezinsarcoredisplayimage.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'display.png'))
        ezinsarcoredisplayimage.appendRow(ezinsarcoredisplayimagetools_0)

        ezinsarcoredisplay =  QStandardItem('Display') 
        ezinsarcoredisplay.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'map.png'))
        ezinsarcoredisplay.appendRow(ezinsarcoredisplayquicklook)
        ezinsarcoredisplay.appendRow(ezinsarcoredisplayinsitu)
        ezinsarcoredisplay.appendRow(ezinsarcoredisplayimage)

        parent.appendRow([ezinsarcoredisplay])

        # For Post-processing
        ezinsarcorepostprocessingfiltertools_0 = QStandardItem('Open the filtering tool')
        ezinsarcorepostprocessingfiltertools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
        ezinsarcorepostprocessingfiltertools_0.setToolTip('Add more advanced tools for temporal and spatial filtering')
        self.listtools.append('Open the filtering tool')

        ezinsarcorepostprocessingfilter =  QStandardItem('Filter') 
        ezinsarcorepostprocessingfilter.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
        ezinsarcorepostprocessingfilter.appendRow(ezinsarcorepostprocessingfiltertools_0)
        
        ezinsarcorepostprocessinguncertools_0 = QStandardItem('Open the uncertainty computation')
        ezinsarcorepostprocessinguncertools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
        ezinsarcorepostprocessinguncertools_0.setToolTip('Add some tools for uncertainty computations')
        self.listtools.append('Open the uncertainty computation')

        ezinsarcorepostprocessinguncer =  QStandardItem('Uncertainty') 
        ezinsarcorepostprocessinguncer.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
        ezinsarcorepostprocessinguncer.appendRow(ezinsarcorepostprocessinguncertools_0)

        ezinsarcorepostprocessinganalysistools_0 = QStandardItem('Open the statistic tool')
        ezinsarcorepostprocessinganalysistools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'calc.png'))
        ezinsarcorepostprocessinganalysistools_0.setToolTip('Open the statistic tool')
        self.listtools.append('Open the statistic tool')

        ezinsarcorepostprocessinganalysistools_1 = QStandardItem('Open the profile tool')
        ezinsarcorepostprocessinganalysistools_1.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'calc.png'))
        ezinsarcorepostprocessinganalysistools_1.setToolTip('Open the profile tool')
        self.listtools.append('Open the profile tool')

        ezinsarcorepostprocessinganalysis = QStandardItem('Analysis') 
        ezinsarcorepostprocessinganalysis.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
        ezinsarcorepostprocessinganalysis.appendRow(ezinsarcorepostprocessinganalysistools_0)
        ezinsarcorepostprocessinganalysis.appendRow(ezinsarcorepostprocessinganalysistools_1)

        ezinsarcorepostprocessinganalysisclasstools_0 = QStandardItem('SVD classification')
        ezinsarcorepostprocessinganalysisclasstools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'calc.png'))
        ezinsarcorepostprocessinganalysisclasstools_0.setToolTip('Open the SDV-classification tool')
        self.listtools.append('SVD classification')

        ezinsarcorepostprocessinganalysisclasstools_1 = QStandardItem('ICA classification')
        ezinsarcorepostprocessinganalysisclasstools_1.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'calc.png'))
        ezinsarcorepostprocessinganalysisclasstools_1.setToolTip('Open the ICA-classification tool')
        self.listtools.append('ICA classification')

        ezinsarcorepostprocessinganalysisclasstools_2 = QStandardItem('SSA classification')
        ezinsarcorepostprocessinganalysisclasstools_2.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'calc.png'))
        ezinsarcorepostprocessinganalysisclasstools_2.setToolTip('Open the SSA-classification tool')
        self.listtools.append('SSA classification')

        ezinsarcorepostprocessinganalysisclasstools_3 = QStandardItem('Kmeans classification')
        ezinsarcorepostprocessinganalysisclasstools_3.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'calc.png'))
        ezinsarcorepostprocessinganalysisclasstools_3.setToolTip('Open the Kmeans-classification tool')
        self.listtools.append('Kmeans classification')

        ezinsarcorepostprocessinganalysisclasstools_4 = QStandardItem('Trend classification')
        ezinsarcorepostprocessinganalysisclasstools_4.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'calc.png'))
        ezinsarcorepostprocessinganalysisclasstools_4.setToolTip('Open the Trend-classification tool')
        self.listtools.append('Trend classification')

        ezinsarcorepostprocessinganalysisclass = QStandardItem('Classification') 
        ezinsarcorepostprocessinganalysisclass.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'calc.png'))
        ezinsarcorepostprocessinganalysisclass.appendRow(ezinsarcorepostprocessinganalysisclasstools_0)
        ezinsarcorepostprocessinganalysisclass.appendRow(ezinsarcorepostprocessinganalysisclasstools_1)
        ezinsarcorepostprocessinganalysisclass.appendRow(ezinsarcorepostprocessinganalysisclasstools_2)
        ezinsarcorepostprocessinganalysisclass.appendRow(ezinsarcorepostprocessinganalysisclasstools_3)
        ezinsarcorepostprocessinganalysisclass.appendRow(ezinsarcorepostprocessinganalysisclasstools_4)
        ezinsarcorepostprocessinganalysis.appendRow(ezinsarcorepostprocessinganalysisclass)

        ezinsarcorepostprocessing = QStandardItem('Post-processing') 
        ezinsarcorepostprocessing.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
        ezinsarcorepostprocessing.appendRow(ezinsarcorepostprocessingfilter)
        ezinsarcorepostprocessing.appendRow(ezinsarcorepostprocessinguncer)
        ezinsarcorepostprocessing.appendRow(ezinsarcorepostprocessinganalysis)

        parent.appendRow(ezinsarcorepostprocessing)

        # For Physical-modelling
        ezinsarcorephysicalmodeltools_0 = QStandardItem('Undersampling of displacements')
        ezinsarcorephysicalmodeltools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
        ezinsarcorephysicalmodeltools_0.setToolTip('Open the tools for displacement undersampling')
        self.listtools.append('Undersampling of displacements')

        ezinsarcorephysicalmodeltools_1 = QStandardItem('Model inversion')
        ezinsarcorephysicalmodeltools_1.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
        ezinsarcorephysicalmodeltools_1.setToolTip('Open the tools for displacement inversion')
        self.listtools.append('Model inversion')

        ezinsarcorephysicalmodeltools_2 = QStandardItem('Model displayer')
        ezinsarcorephysicalmodeltools_2.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'map.png'))
        ezinsarcorephysicalmodeltools_2.setToolTip('Open the tools for displacement-model results')
        self.listtools.append('Model displayer')

        ezinsarcorephysicalmodel = QStandardItem('Physical modelling') 
        ezinsarcorephysicalmodel.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
        ezinsarcorephysicalmodel.appendRow(ezinsarcorephysicalmodeltools_0)
        ezinsarcorephysicalmodel.appendRow(ezinsarcorephysicalmodeltools_1)
        ezinsarcorephysicalmodel.appendRow(ezinsarcorephysicalmodeltools_2)

        parent.appendRow(ezinsarcorephysicalmodel)

        # For Import
        ezinsarcoreimporttools_0 = QStandardItem('Import file to EZ-InSAR in-situ data')
        ezinsarcoreimporttools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'dw.png'))
        ezinsarcoreimporttools_0.setToolTip('Import file to EZ-InSAR in-situ data')
        self.listtools.append('Import file to EZ-InSAR in-situ data')

        ezinsarcoreimporttools_1 = QStandardItem('Import an EGMS dataset')
        ezinsarcoreimporttools_1.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'dw.png'))
        ezinsarcoreimporttools_1.setToolTip('Import an EGMS dataset')
        self.listtools.append('Import an EGMS dataset')

        ezinsarcoreimport = QStandardItem('Import') 
        ezinsarcoreimport.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'dw.png'))
        ezinsarcoreimport.appendRow(ezinsarcoreimporttools_0)
        ezinsarcoreimport.appendRow(ezinsarcoreimporttools_1)

        parent.appendRow(ezinsarcoreimport)

        # For Export
        ezinsarcoreexporttools_0 = QStandardItem('Export the time-series results')
        ezinsarcoreexporttools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'export.png'))
        ezinsarcoreexporttools_0.setToolTip('Export the time-series results')
        self.listtools.append('Export the time-series results')

        ezinsarcoreexport = QStandardItem('Export') 
        ezinsarcoreexport.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'export.png'))
        ezinsarcoreexport.appendRow(ezinsarcoreexporttools_0)

        parent.appendRow(ezinsarcoreexport)

        ########################################################################
        ## For the Optional Modules
        ########################################################################        
        # For the EZ-InSAR Multispectral Module
        try: 
            from ezinsarmultispectralmodule import __file__ as __root_module_tmp__  
            __root_module_tmp__ = os.path.dirname(__root_module_tmp__)  

            ezinsarmultispectimagesS2_tools_0 = QStandardItem('Download Sentinel-2 image(s)')
            ezinsarmultispectimagesS2_tools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'dw.png'))
            ezinsarmultispectimagesS2_tools_0.setToolTip('Download Sentinel-2 images from Copernicus Server')
            self.listtools.append('Download Sentinel-2 image(s)')

            ezinsarmultispectimagesS2_tools_1 = QStandardItem('Process Sentinel-2 image(s)')
            ezinsarmultispectimagesS2_tools_1.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
            ezinsarmultispectimagesS2_tools_1.setToolTip('Process Sentinel-2 images')
            self.listtools.append('Process Sentinel-2 image(s)')

            ezinsarmultispectimagesS2 = QStandardItem('Sentinel-2')
            ezinsarmultispectimagesS2.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'sat.png'))
            ezinsarmultispectimagesS2.appendRow(ezinsarmultispectimagesS2_tools_0)
            ezinsarmultispectimagesS2.appendRow(ezinsarmultispectimagesS2_tools_1)

            ezinsarmultispectimagesLandsat_tools_0 = QStandardItem('Process LandSat-8/9 image(s)')
            ezinsarmultispectimagesLandsat_tools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
            ezinsarmultispectimagesLandsat_tools_0.setToolTip('Download LandSat-8/9 images')
            self.listtools.append('Process LandSat-8/9 image(s)')

            ezinsarmultispectimagesLandsat = QStandardItem('LandSat-8/9')
            ezinsarmultispectimagesLandsat.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'sat.png'))
            ezinsarmultispectimagesLandsat.appendRow(ezinsarmultispectimagesLandsat_tools_0)

            ezinsarmultispectimages = QStandardItem('Satellite')
            ezinsarmultispectimages.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'sat.png'))
            ezinsarmultispectimages.appendRow(ezinsarmultispectimagesS2)
            ezinsarmultispectimages.appendRow(ezinsarmultispectimagesLandsat)

            ezinsarmultispect = QStandardItem('EZ-InSAR Multispectral Module')
            ezinsarmultispect.setIcon(QIcon(__root_module_tmp__.replace('src%sezinsarmultispectralmodule' % (os.sep),'private')+os.sep+'EZ_InSAR_logo_multispectral_whiteback.svg'))
            ezinsarmultispect.appendRow(ezinsarmultispectimages)

            parent.appendRow(ezinsarmultispect)
        except:
            a = 'dummy'

        # For the EZ-InSAR TSDisplayer 
        try: 
            from ezinsartsdisplayermodule import __file__ as __root_module_tmp__  
            __root_module_tmp__ = os.path.dirname(__root_module_tmp__)  

            ezinsartsdisplayer_tools_0 = QStandardItem('Open the time series displayer')
            ezinsartsdisplayer_tools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'map.png'))
            ezinsartsdisplayer_tools_0.setToolTip('Open the time series displayer')
            self.listtools.append('Open the time series displayer')

            ezinsartsdisplayerroot = QStandardItem('EZ-InSAR Time-series Displayer Module')
            ezinsartsdisplayerroot.setIcon(QIcon(__root_module_tmp__.replace('src%sezinsartsdisplayermodule' % (os.sep),'private')+os.sep+'EZ_InSAR_logo_tsdisplayer_whiteback.svg'))
            ezinsartsdisplayerroot.appendRow(ezinsartsdisplayer_tools_0)

            parent.appendRow(ezinsartsdisplayerroot)
        except:
            a = 'dummy'

        # For the EZ-InSAR Weather Module
        try: 
            from ezinsarweathermodule import __file__ as __root_module_tmp__  
            __root_module_tmp__ = os.path.dirname(__root_module_tmp__)  

            ezinsarweatherCEDAUK_tools_0 = QStandardItem('Retrieve weather data from HadUK-Grid')
            ezinsarweatherCEDAUK_tools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'dw.png'))
            ezinsarweatherCEDAUK_tools_0.setToolTip('Retrieve weather in-situ data from HadUK-Grid')
            self.listtools.append('Retrieve weather data from HadUK-Grid')

            ezinsarweather = QStandardItem('Weather')
            ezinsarweather.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'weather.png'))
            ezinsarweather.appendRow(ezinsarweatherCEDAUK_tools_0)

            ezinsarweatherroot = QStandardItem('EZ-InSAR Weather Module')
            ezinsarweatherroot.setIcon(QIcon(__root_module_tmp__.replace('src%sezinsarweathermodule' % (os.sep),'private')+os.sep+'EZ_InSAR_logo_weather_whiteback.svg'))
            ezinsarweatherroot.appendRow(ezinsarweather)

            parent.appendRow(ezinsarweatherroot)
        except:
            a = 'dummy'

        # For the EZ-InSAR GNSS Module
        try: 
            from ezinsargnssmodule import __file__ as __root_module_tmp__  
            __root_module_tmp__ = os.path.dirname(__root_module_tmp__)  

            ezinsargnssinsitu_tools_0 = QStandardItem('Compare in-situ data and InSAR')
            ezinsargnssinsitu_tools_0.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'gear.png'))
            ezinsargnssinsitu_tools_0.setToolTip('Open the tools to compare in-situ data and InSAR results')
            self.listtools.append('Compare in-situ data and InSAR')

            ezinsargnssinsitu = QStandardItem('In-situ')
            ezinsargnssinsitu.setIcon(QIcon(os.path.abspath(__file__).replace('pluginsWidget.py','')+exticons+'field.png'))
            ezinsargnssinsitu.appendRow(ezinsargnssinsitu_tools_0)

            ezinsargnssroot = QStandardItem('EZ-InSAR GNSS Module')
            ezinsargnssroot.setIcon(QIcon(__root_module_tmp__.replace('src%sezinsargnssmodule' % (os.sep),'private')+os.sep+'EZ_InSAR_logo_gnss_whiteback.svg'))
            ezinsargnssroot.appendRow(ezinsargnssinsitu)

            parent.appendRow(ezinsargnssroot)
        except:
            a = 'dummy'

        ## Final creation
        self.main.setModel(parent)
        self.main.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.main.doubleClicked.connect(self.runplugin)
        self.main.setHeaderHidden(True)

        btHelp = QPushButton("Help", self)
        btHelp.clicked.connect(self.openhelp)

        layout = QGridLayout()
        layout.addWidget(QLabel("<p><b>EZ-InSAR's tools</b></p>"), 0, 0, 1, 9)
        layout.addWidget(btHelp, 0, 9, 1, 1)
        layout.addWidget(self.main, 1, 0, 1, 10)

        ## Search bar
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search a tool...")
        self.search_box.textChanged.connect(self.search_tools)
        layout.addWidget(self.search_box, 2, 0, 1, 10)

        self.setLayout(layout)

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def openhelp(self):
        helpdial = DocsDialog(['tools','index'])
        helpdial.show()
        helpdial.exec()

    def search_tools(self, text):
        """Search function"""
        def recursive_search(item):
            item_matches = text.lower() in item.text().lower()
            child_matches = False

            for i in range(item.rowCount()):
                child = item.child(i)
                child_matched = recursive_search(child)
                child_matches = child_matches or child_matched

            if item_matches or child_matches:
                index = self.main.model().indexFromItem(item)
                self.main.setRowHidden(item.row(), item.parent().index() if item.parent() else self.main.model().invisibleRootItem().index(), False)
                self.main.expand(index)
                return True
            else:
                index = self.main.model().indexFromItem(item)
                self.main.setRowHidden(item.row(), item.parent().index() if item.parent() else self.main.model().invisibleRootItem().index(), True)
                return False

        if not text.strip():
            self.main.collapseAll()
        else:
            root_item = self.main.model().invisibleRootItem()
            for i in range(root_item.rowCount()):
                recursive_search(root_item.child(i))

    def messageerror(self,msg):
        """Send an error message"""
        reply = QMessageBox.critical(self, "EZ-InSAR Error",
                msg,
                QMessageBox.Ok)
        
    def messagesuccess(self,msg):
        """Send an information message"""
        reply = QMessageBox.information(self, "EZ-InSAR Information",
                msg,
                QMessageBox.Ok)
        
    def runplugin(self):
        indexselected = self.main.selectedIndexes()[0]
        toolname = indexselected.model().itemFromIndex(indexselected).text()

        if toolname in self.listtools:

            ###########################################################
            ## Smart modification of paths
            if 'Smart modificaiton of paths' == toolname:
                if not os.path.isfile(self.parent.curEZInSARjob):
                    self.messageerror('Please load an EZ-InSAR job')
                else:
                    job = ez.load(self.parent.curEZInSARjob,verbose=False)

                    options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
                    directory = QFileDialog.getExistingDirectory(self,
                        'Change the new root directory', options=options)
                    
                    if directory:
                        try:
                            job = job.changedir(directory,verbose=False) 
                            ez.save(job,self.parent.curEZInSARjob,verbose=False)
                            job = None
                            self.parent.updatelog()
                            self.messagesuccess('Modification successfull in %s' % (self.parent.curEZInSARjob))

                        except Exception as e:
                            self.messageerror('%s' % (e))

            ###########################################################
            ## For Detection of Sentinel-1 IW Track
            elif 'Detection of Sentinel-1 IW Track' == toolname:
                if not os.path.isfile(self.parent.curEZInSARjob):
                    self.messageerror('Please load an EZ-InSAR job')
                else:
                    job = ez.load(self.parent.curEZInSARjob,verbose=False)
                    if (not job.satellite == 'IW') and (not job.satmode == 'IW'): 
                        self.messageerror('This tool is only available with Sentinel-1 IW data.')
                    else:
                        try: 
                            from ezinsardesktopmodule.sat.tools.s1 import S1detectionWidget
                            len(job.SLClist['Name'])
                            job = None
                            if not self.parent.curwidget == None:
                                self.parent.curwidget.close()
                                self.parent.curwidget = None
                            self.parent.curwidget = S1detectionWidget.S1detectiontrack(self.parent.curEZInSARjob, parent=self.parent)
                            self.parent.mainlayout.addWidget(self.parent.curwidget,0,0)
                            self.parent.curwidget.closing.connect(self.parent.updatelog)
                        except:
                            job = None
                            self.messageerror('Error: No SLC list.')
            
            ###########################################################
            ## For Pre-computaton of Sentinel-1 IW Baselines
            elif 'Pre-computaton of Sentinel-1 IW Baselines' == toolname:
                if not os.path.isfile(self.parent.curEZInSARjob):
                    self.messageerror('Please load an EZ-InSAR job')
                else:
                    job = ez.load(self.parent.curEZInSARjob,verbose=False)
                    if (not job.satellite == 'IW') and (not job.satmode == 'IW'): 
                        self.messageerror('This tool is only available with Sentinel-1 IW data.')
                    else:
                        try: 
                            from ezinsardesktopmodule.sat.tools.s1 import S1ASFbaselinesWidget 
                            len(job.SLClist['Name'])
                            job = None
                            if not self.parent.curwidget == None:
                                self.parent.curwidget.close()
                                self.parent.curwidget = None
                            self.parent.curwidget = S1ASFbaselinesWidget.S1asfbaselines(self.parent.curEZInSARjob)
                            self.parent.mainlayout.addWidget(self.parent.curwidget,0,0)
                            self.parent.curwidget.closing.connect(self.parent.updatelog)
                        except:
                            job = None
                            self.messageerror('Error: No SLC list.')

            ###########################################################
            # ## List the planned Sentinel-1 acquisitions
            # elif 'List the planned Sentinel-1 acquisitions' == toolname:
                

            ###########################################################
            ## Quicklook of InSAR-derived velocity
            ## Quicklook of InSAR-derived velocity standard deviation
            elif ('Quicklook of InSAR-derived velocity' == toolname) or ('Quicklook of InSAR-derived velocity standard deviation' == toolname):
                options = QFileDialog.Options()
                fileName, _ = QFileDialog.getOpenFileName(self,
                        "Select an EZ-InSAR Data file",'',
                        "*.eidata", options=options)
                if fileName:
                    data = ezinsardata.loadEZdata(fileName,
                            partialreading = ['lat','lon','lat_grid','lon_grid',
                                            'rateLOS','rateUD','rateEW','rateNS',
                                            'sigmarateLOS','sigmarateUD','sigmarateEW','sigmarateNS',
                                            ],
                            verbose=False)
                    
                    if 'Quicklook of InSAR-derived velocity' == toolname:
                        mode='rateLOS'
                    else:
                        mode='sigmarateLOS'

                    try:
                        figobj, axobj = data.quicklook(mode = mode,
                                            returnfig = True,
                                            )
                        reply = dummyfigure(figobj,axobj,title='Quicklook for %s' % (fileName.split(os.sep)[-1]))
                        reply.show()
                        reply.exec_()
                    except Exception as e:
                        self.messageerror('%s' % (e))

            ###########################################################
            ## Open the time series displayer
            elif 'Open the time series displayer' == toolname:
                options = QFileDialog.Options()
                fileName, _ = QFileDialog.getOpenFileName(self,
                        "Select an EZ-InSAR Data file",'',
                        "*.eidata", options=options)
                if fileName:
                    openTSDisplayer(fileName)

            ###########################################################
            ## Open the in-situ data displayer
            elif 'Open the in-situ data displayer' == toolname:
                options = QFileDialog.Options()
                fileName, _ = QFileDialog.getOpenFileName(self,
                        "Select an EZ-InSAR Data file",'',
                        "*.eidata", options=options)
                if fileName:
                    startok = False
                    try:
                        tmp = ezinsardata.loadEZdata(fileName,mode = 'insitu',partialreading = ['classtype'])
                        if  tmp.classtype['value'] == 'insitu':
                            startok = True
                        else:
                            startok = False
                    except:
                            startok = False
                    if startok:
                        if os.path.isfile(self.parent.curEZInSARjob):
                            job = ez.load(self.parent.curEZInSARjob,verbose=False)
                            log = job.log
                            job = None
                        else:
                            log = None
                        from ezinsardesktopmodule.display import insituWidget 
                        if not self.parent.curwidget == None:
                            self.parent.curwidget.close()
                            self.parent.curwidget = None
                        self.parent.curwidget = insituWidget.insitudisplay(fileName,log=log,parent=self.parent)
                        self.parent.mainlayout.addWidget(self.parent.curwidget,0,0)
                        self.parent.curwidget.closing.connect(self.parent.updatelog)

            ###########################################################
            ## Import file to EZ-InSAR in-situ data
            elif 'Import file to EZ-InSAR in-situ data' == toolname:
                options = QFileDialog.Options()
                fileName, _ = QFileDialog.getOpenFileName(self,
                        "Select an EZ-InSAR in-situ Data file",'',
                        "*", options=options)
                if fileName:
                    if os.path.isfile(self.parent.curEZInSARjob):
                        job = ez.load(self.parent.curEZInSARjob,verbose=False)
                        log = job.log
                        job = None
                    else:
                        log = None
                    from ezinsardesktopmodule.interface import insitudataDial 
                    if not self.parent.curwidget == None:
                        self.parent.curwidget.close()
                        self.parent.curwidget = None
                    self.parent.curwidget = insitudataDial.insitudial(fileName,log=log,parent=self.parent)
                    self.parent.mainlayout.addWidget(self.parent.curwidget,0,0)
                    self.parent.curwidget.closing.connect(self.parent.updatelog)

            ###########################################################
            ## Import an EGMS dataset
            elif 'Import an EGMS dataset' == toolname:
                from ezinsar.contrib.python import importEGMS
                if not self.parent.curwidget == None:
                    self.parent.curwidget.close()
                    self.parent.curwidget = None
                self.parent.curwidget = importEGMS.GUIimportEGMS(parent=self.parent)
                self.parent.mainlayout.addWidget(self.parent.curwidget,0,0)
                
            ###########################################################
            ## Export the time-series results
            elif 'Export the time-series results' == toolname:
                from ezinsardesktopmodule.interface import exportEZdataWidget 
                if not self.parent.curwidget == None:
                    self.parent.curwidget.close()
                    self.parent.curwidget = None
                self.parent.curwidget = exportEZdataWidget.exportWidget(parent=self.parent)
                self.parent.mainlayout.addWidget(self.parent.curwidget,0,0)

            ###########################################################
            ## Retrieve weather data from HadUK-Grid
            elif 'Retrieve weather data from HadUK-Grid' == toolname:
                from ezinsardesktopmodule.interface.weather import CEDAukWidget 
                if not os.path.isfile(self.parent.curEZInSARjob):
                    self.messageerror('Please load an EZ-InSAR job')
                else:
                    job = ez.load(self.parent.curEZInSARjob,verbose=False)
                    if not self.parent.curwidget == None:
                        self.parent.curwidget.close()
                        self.parent.curwidget = None
                    self.parent.curwidget = CEDAukWidget.CEDAdata(log=job.log,parent = self.parent)
                    self.parent.mainlayout.addWidget(self.parent.curwidget,0,0)
                    self.parent.curwidget.closing.connect(self.parent.updatelog)
                    job = None

            ###########################################################
            ## Compare in-situ data and InSAR
            elif 'Compare in-situ data and InSAR' == toolname:
                options = QFileDialog.Options()
                fileName, _ = QFileDialog.getOpenFileName(self,
                        "Select an EZ-InSAR in-situ Data file",'',
                        "*.eidata", options=options)
                if fileName:
                    from ezinsargnssmodule.gui import compareWidget
                    if not self.parent.curwidget == None:
                        self.parent.curwidget.close()
                        self.parent.curwidget = None
                    try: 
                        self.parent.curwidget = compareWidget.comparedisplay(fileName,parent=self.parent)
                        self.parent.mainlayout.addWidget(self.parent.curwidget,0,0)
                        self.parent.curwidget.closing.connect(self.parent.updatelog)
                    except Exception as e:
                        self.messageerror('%s' %(e))

            ###########################################################
            ###########################################################    
            ## Dummy reply
            else:
                self.messageerror('The tool %s is not implemented. It will be added in a next version of EZ-InSAR.' % (toolname))

def openTSDisplayer(file,parent=None):
    startok = False
    try:
        tmp = ezinsardata.loadEZdata(file,mode = 'displacement',partialreading = ['classtype'])
        if  tmp.classtype['value'] == 'displacement':
            startok = True
        else:
            startok = False
    except:
            startok = False
    if startok:
        cmd = 'ezinsar tsdisplayer -f %s' % (file)
        subprocess.Popen(cmd,shell=True)

###########################################################################################
## For debug 
########################################################################################### 
def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    widget = plugins()
    widget.show()
    sys.exit(app.exec_())
if __name__=='__main__':
    main()

