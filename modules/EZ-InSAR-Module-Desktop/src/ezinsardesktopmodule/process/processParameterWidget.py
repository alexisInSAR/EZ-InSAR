#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a tool to change the parameters of an EZ-InSAR processing job

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 1.0.0: Initial version, Mar. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a tool to change the parameters of an EZ-InSAR processing job

usage: 
    ezinsardesktop_initprocess -f <str> -m <str> [options]

Arguments:
    -f, --file <str>        EZ-InSAR job file
    -m, --mode <str>        Processing mode. Can be coregistration, ifgstack, tsprocessing, intstack

Other-options:
    -h, --help
"""

###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (QApplication, QTabWidget, QCheckBox, QGridLayout, QLabel, QSpinBox, QLineEdit, QMessageBox, QComboBox, QPushButton, QFileDialog, QWidget, QGroupBox, QScrollArea, QLayout, QDoubleSpinBox)

import os, sys, time, copy
import numpy as np
from docopt import docopt

from ezinsar import constants, usermessage
import ezinsar.job as ez
from ezinsardesktopmodule import __file__ as __root_module__
from ezinsardesktopmodule.tools import tools
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsardesktopmodule.tools.docsWidget import DocsDialog

superparameter = {'title': ['str','Title of the processing job.'],
    'workdirectory': ['str','Path of the work directory.'],
    'pathSLC': ['str','Path of the SLC files.'],
    'pathorbit': ['str','Path of the orbit files.'],
    'pathaux': ['str','Path of the Aux. files.'],
    'pathDEM': ['str','Path of the DEM files.'],
    'nameDEM': ['str','Name of the DEM.'],
    'typeDEM': ['str','Type of the DEM.'],
    'pathstack': ['str','Path of the resampled SLCs.'],
    'refdate': ['str','Reference date (super-single-master).'],
    'polarisation': ['ckeck','Polarisation selected.'],
    'roi': ['str','Region of Interest.'],
    'satellite': ['str','Satellite.'],
    'satmode': ['str','Acquisition mode.'],
    'computercores': ['int','Number of used cores (only for gamma processor).'],
    'computernbthread': ['int','Number of used cores.'],
    'processor': ['str','InSAR processor.'],
    'modecropping': ['str','Mode of cropping.'],
    'modeforce': ['bool','Forcing mode.'],
    'modestack': ['str','Mode of the stack.'],
    'modeDEM': ['str','Mode of the DEM for import'],
    'modeacq': ['str','Mode of the beam'],
    'mlazi': ['int','Multilook factor in azimuth.'],
    'mlran': ['int','Multilook factor in range.'],
    'mlazidisplay': ['int','Multilook factor in azimuth for displaying.'],
    'mlrandisplay': ['int','Multilook factor in range for displaying.'],
    'pathstampsparms': ['str','.parm file for the StaMPS parameters'],
    'pathmintpyconfig': ['str','.parm file for the StaMPS parameters'],
    'date1': ['str','First date in YYYYMMDD format'],
    'date2': ['str','Last date in YYYYMMDD format'],
    'frame': ['str','Sentinel-1 frame'],
    'n_para': ['int','Number of workers.'],
    'mem_size': ['int','Max memory usage.'], 
    }

###########################################################################################
## Classes
###########################################################################################
class parameterWidget(QWidget):
    """QWidget class 

        Build the widget windows
    """

    closing = pyqtSignal(bool)

    def __init__(self, jobfile, mode, parent=None):
        super(parameterWidget, self).__init__(parent)

        self.pathjobfile = jobfile
        self.setWindowTitle("EZ-InSAR - Processing job parameters")
        self.resize(750,500)
        self.success = False
        self.false = False
        self.mode = mode
        self.parent = parent

        self.setStyleSheet(__theme__)

        ## Read the job
        job = ez.load(self.pathjobfile,verbose=False)
        self.jobprocess = eval("copy.deepcopy(job.%s)" % (self.mode))
        if self.jobprocess == None: 
            raise ValueError(usermessage.errormsg(__name__,__name__,__file__,constants.__copyright__,
                    'No processing job available.',None))

        ## Title + quit button
        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p style="font-size:20px"><b>EZ-InSAR parameters for %s processing job<\b></p>' %  (tools.mode2title(self.mode)))
        btQuit = QPushButton("Close", self)
        btSave = QPushButton("Save", self)
        
        btHelp = QPushButton("Help", self)
        btHelp.clicked.connect(self.openhelp)

        ############################################
        ## Create the tabs
        self.tabs = QTabWidget() 
        self.tabs.tabBar().setExpanding(True)

        self.quickaccessgroup = QGroupBox('Progressing')
        self.quickaccessgrouplayout = QGridLayout()

        self.tab0 = QScrollArea()
        self.tab0.setWidgetResizable(True)
        self.tab0widget = QWidget()
        self.tab0.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tab0.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tab0layout = QGridLayout()
        # self.tab0layout.addWidget(QLabel('<p><b>Super-parameters<\b></p>'),0,0,1,5, Qt.AlignLeft)

        for idx, parai in enumerate(list(superparameter.keys())): 
            if parai in list(vars(self.jobprocess)) and (not parai == 'polarisation'):
                tmplabel = QLabel('<p>Parameters: %s</p>' % (parai))
                tmplabel.setToolTip(superparameter[parai][1]) 
                self.tab0layout.addWidget(tmplabel,idx+1,0,1,1)

                if superparameter[parai][0] == 'str': 
                    exec("self.%s = QLineEdit(self)" % (parai))
                    exec("self.%s.setText(self.jobprocess.%s)" % (parai,parai))
                elif superparameter[parai][0] == 'int': 
                    exec("self.%s = QSpinBox(self)" % (parai))
                    exec("self.%s.setValue(self.jobprocess.%s)" % (parai,parai))
                elif superparameter[parai][0] == 'bool': 
                    exec("self.%s = QCheckBox(self)" % (parai))
                    exec("self.%s.setText('Enabled')" % (parai))
                    exec("self.%s.setChecked(self.jobprocess.%s)" % (parai,parai))
                exec("self.tab0layout.addWidget(self.%s,idx+1,2,1,4)" % (parai))

            elif parai == 'polarisation':
                tmplabel = QLabel('<p>Parameters: %s</p>' % (parai))
                tmplabel.setToolTip(superparameter[parai][1]) 
                self.tab0layout.addWidget(tmplabel,idx+1,0,1,2)

                for idxbis, poli in enumerate(['VV','VH','HH','HV']): 
                    exec("self.%s%s = QCheckBox(self)" % (parai,poli))
                    exec("self.%s%s.setText(poli)" % (parai,poli))
                    if poli in self.jobprocess.polarisation: 
                        exec("self.%s%s.setChecked(True)" % (parai,poli))
                    else: 
                        exec("self.%s%s.setChecked(False)" % (parai,poli))
                    exec("self.tab0layout.addWidget(self.%s%s,idx+1,2+idxbis,1,1)" % (parai,poli))

        self.tab0widget.setLayout(self.tab0layout)
        self.tab0.setWidget(self.tab0widget)
        self.tabs.addTab(self.tab0, "Super-parameters")
        bttmp = QPushButton('Super-parameters')
        bttmp.clicked.connect(self.quickaccess)
        bttmp.setStyleSheet('background-color : skyblue')
        self.quickaccessgrouplayout.addWidget(bttmp,0,0,1,1)
        
        ## For the processing parameters
        h = 1
        stepidx = 1
        for idx, vi in enumerate(vars(self.jobprocess)):
            tmp = eval('self.jobprocess.%s' % (vi))

            if isinstance(tmp,dict): 

                exec("self.tab%s = QScrollArea()" % (h))
                exec("self.tab%s.setWidgetResizable(False)" % (h))
                exec("self.tab%swidget = QWidget()" % (h))
                exec("self.tab%s.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)" % (h))
                exec("self.tab%s.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)" % (h))
                
                exec("self.tab%slayout = QGridLayout()" % (h))
                exec("self.tab%slayout.setSizeConstraint(QLayout.SetFixedSize)" % (h))

                if vi == 'email':
                    exec("self.tab%slayout.addWidget(QLabel('<p><b>Parameters for Email<\b></p>'),0,0,1,5, Qt.AlignLeft)" %(h))
                else:
                    exec("self.tab%slayout.addWidget(QLabel('<p><b>Parameters for Step %s: %s<\b></p>'),0,0,1,5, Qt.AlignLeft)" % (h,stepidx,vi))

                hline = 1
                for parai in list(tmp.keys()):
                    if not parai == 'name':
                        tmplabel = QLabel('<p>Parameters: %s</p>' % (parai))
                        tmplabel.setToolTip("""<p>Description: %s</p>
                                            <p>Format: %s</p>
                                            <p>Possible values: %s</p>
                                            """
                                            % (tmp[parai]['description'],tmp[parai]['format'],tmp[parai]['valuelist']))
                        exec("self.tab%slayout.addWidget(tmplabel,hline,0,1,2)" % (h))

                        if tmp[parai]['format'] == 'bool': 
                            exec("self.%s__%s = QCheckBox(self)" % (vi,parai.replace('.','_')))
                            if not parai == 'done':
                                exec("self.%s__%s.setText('Enabled')" % (vi,parai.replace('.','_')))
                            else: 
                                exec("self.%s__%s.setText('Completed')" % (vi,parai.replace('.','_')))
                            exec("self.%s__%s.setChecked(tmp[parai]['value'])" % (vi,parai.replace('.','_')))

                        elif tmp[parai]['format'] == 'float': 
                            exec("self.%s__%s = QDoubleSpinBox(self)" % (vi,parai.replace('.','_')))
                            exec("self.%s__%s.setMaximum(10000000)" % (vi,parai))
                            exec("self.%s__%s.setMinimum(-10000000)" % (vi,parai.replace('.','_')))
                            exec("self.%s__%s.setValue(tmp[parai]['value'])" % (vi,parai.replace('.','_')))

                        elif tmp[parai]['format'] == 'int': 
                            exec("self.%s__%s = QSpinBox(self)" % (vi,parai.replace('.','_')))
                            exec("self.%s__%s.setMaximum(10000000)" % (vi,parai.replace('.','_')))
                            exec("self.%s__%s.setMinimum(-10000000)" % (vi,parai.replace('.','_')))
                            exec("self.%s__%s.setValue(tmp[parai]['value'])" % (vi,parai.replace('.','_')))

                        elif tmp[parai]['format'] == 'list': 
                            exec("self.%s__%s = QComboBox(self)" % (vi,parai.replace('.','_')))
                            listtmp = [str(x) for x in tmp[parai]['valuelist']]
                            exec("self.%s__%s.addItems(listtmp)" % (vi,parai.replace('.','_')))
                            exec("self.%s__%s.setCurrentIndex(tmp[parai]['valuelist'].index(tmp[parai]['value']))" % (vi,parai.replace('.','_')))

                        else:
                            exec("self.%s__%s = QLineEdit(self)" % (vi,parai.replace('.','_'))) # Float- /int- / str / pathuser %email %password 
                            exec("self.%s__%s.setText(str(tmp[parai]['value']))" % (vi,parai.replace('.','_')))

                            if tmp[parai]['format'] == 'password': 
                                exec("self.%s__%s.setEchoMode(QLineEdit.Password)" % (vi,parai.replace('.','_')))

                        if parai == 'done':
                            exec("self.%s__%s.stateChanged.connect(self.updatecolourbt)" % (vi,parai.replace('.','_')))

                        exec("self.tab%slayout.addWidget(self.%s__%s,hline,2,1,1)" % (h,vi,parai.replace('.','_')))

                        hline = hline + 1

                exec("self.tab%s.adjustSize()" % (h))
                exec("self.tab%swidget.setLayout(self.tab%slayout)" % (h,h))
                exec("self.tab%s.setWidget(self.tab%swidget)" % (h,h))

                if vi == 'email' or vi == 'computer' or vi == 'mintpyparameter' or vi == 'plotoptions':
                    exec("self.tabs.addTab(self.tab%s, vi.capitalize())" %(h))
                    exec("self.bt%s = QPushButton(vi.capitalize())" % (h))
                    exec("self.bt%s.setStyleSheet('background-color : skyblue')" % (h))
                else:
                    exec("self.tabs.addTab(self.tab%s, 'Step %s')" % (h,stepidx))
                    exec("self.bt%s = QPushButton('Step %s: %s')" % (h, stepidx,vi))

                    if tmp['done']['value']:
                        exec("self.bt%s.setStyleSheet('background-color : green; color: white')" % (h))
                    else:
                        exec("self.bt%s.setStyleSheet('background-color : red; color: white')" % (h))
                
                exec("self.bt%s.clicked.connect(self.quickaccess)"  % (h))
                exec("self.quickaccessgrouplayout.addWidget(self.bt%s,h+1,0,1,1)"  % (h))

                if not (vi == 'email' or vi == 'computer' or vi == 'mintpyparameter' or vi == 'plotoptions'):
                    stepidx = stepidx + 1
                h = h + 1

        self.quickaccessgroup.setLayout(self.quickaccessgrouplayout)

        ## Layout
        layout = QGridLayout()
        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 7, Qt.AlignCenter)
        layout.addWidget(self.tabs, 1, 0, 1, 8)
        layout.addWidget(self.quickaccessgroup, 1, 9, 1, 1)
        layout.addWidget(btQuit, 0, 9, 1, 1)
        layout.addWidget(btSave, 10, 9, 1, 1)
        layout.addWidget(btHelp, 10, 0, 1, 1)

        self.setLayout(layout)

        btSave.clicked.connect(self.save)
        btQuit.clicked.connect(self.closemaybe)

        job = None

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def openhelp(self):
        helpdial = DocsDialog(['applications','processing','processparameters'])
        helpdial.show()
        helpdial.exec()
    
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

    def quickaccess(self):
        titles = []
        for i in range(self.tabs.count()):
            titles.append(self.tabs.tabText(i))

        idxstep = titles.index(self.sender().text().split(':')[0])
        self.tabs.setCurrentIndex(idxstep)

    def updatecolourbt(self):
        liststep = []
        for vari in list(vars(self.jobprocess)):
            tmp = eval("self.jobprocess.%s" % (vari))      
            if isinstance(tmp,dict):
                liststep.append(vari)

        idxbt = self.tabs.currentIndex()-1
        if eval("self.%s__done.isChecked()" % (liststep[idxbt])):
            exec("self.bt%s.setStyleSheet('background-color : green; color: white')" % (idxbt+1))
        else:
            exec("self.bt%s.setStyleSheet('background-color : red; color: white')" % (idxbt+1))

    def save(self):
        """Save the parameters in the job
        """
        job = ez.load(self.pathjobfile,verbose=False)
        self.jobprocess = eval("copy.deepcopy(job.%s)" % (self.mode))

        ## For the super-parameters
        for idx, parai in enumerate(list(superparameter.keys())): 
            if parai in list(vars(self.jobprocess)) and (not parai == 'polarisation'):

                if superparameter[parai][0] == 'bool': 
                    result = eval("self.%s.isChecked()" % (parai))

                elif superparameter[parai][0] == 'str': 
                    result = eval("self.%s.text()" % (parai))
            
                elif superparameter[parai][0] == 'float': 
                    result = float(eval("self.%s.value()" % (parai)))
                                    
                elif superparameter[parai][0] == 'int': 
                    result = int(eval("self.%s.text()" % (parai)))

                if result == '' or result == 'None':
                    result = None  

                exec("self.jobprocess.%s = result" % (parai))
               
            elif parai == 'polarisation':
                result = []
                if eval("self.polarisation%s.isChecked()" % ('VV')):
                    result.append('VV')
                if eval("self.polarisation%s.isChecked()" % ('VH')):
                    result.append('VH')
                if eval("self.polarisation%s.isChecked()" % ('HH')):
                    result.append('HH')
                if eval("self.polarisation%s.isChecked()" % ('HV')):
                    result.append('HV')

                exec("self.jobprocess.polarisation = result")

        ## For the processing parameters
        for idx, vi in enumerate(vars(self.jobprocess)):
            tmp = eval('self.jobprocess.%s' % (vi))

            if isinstance(tmp,dict): 
                for parai in list(tmp.keys()):
                    if not parai == 'name':
                        if tmp[parai]['format'] == 'bool': 
                            result = eval("self.%s__%s.isChecked()" % (vi,parai.replace('.','_')))

                        elif tmp[parai]['format'] == 'str': 
                            result = eval("self.%s__%s.text()" % (vi,parai.replace('.','_')))
                    
                        elif tmp[parai]['format'] == 'float-': 
                            result = eval("self.%s__%s.text()" % (vi,parai.replace('.','_')))
                            if not result == '-':
                                result = float(result)

                        elif tmp[parai]['format'] == 'float': 
                            result = float(eval("self.%s__%s.value()" % (vi,parai.replace('.','_'))))

                        elif tmp[parai]['format'] == 'int-': 
                            result = eval("self.%s__%s.text()" % (vi,parai.replace('.','_')))
                            if not result == '-':
                                result = int(result)
                                          
                        elif tmp[parai]['format'] == 'int': 
                            result = int(eval("self.%s__%s.text()" % (vi,parai.replace('.','_'))))

                        elif tmp[parai]['format'] == 'list': 
                            result = eval("self.%s__%s.currentText()" % (vi,parai.replace('.','_')))
                            liststr = [str(x) for x in tmp[parai]['valuelist']]
                            idxlist = liststr.index(result)

                            if tmp[parai]['valuelist'][idxlist] == None: 
                                result = None
                            elif isinstance(tmp[parai]['valuelist'][idxlist],bool):
                                result = (result == 'True')
                            elif isinstance(tmp[parai]['valuelist'][idxlist],float):
                                result = float(result)
                            elif isinstance(tmp[parai]['valuelist'][idxlist],int):
                                result = int(result)
                            elif isinstance(tmp[parai]['valuelist'][idxlist],str):
                                result = result
                            
                        elif tmp[parai]['format'] in ['floatmat','intmat']: 
                            result = eval("self.%s__%s.text()" % (vi,parai.replace('.','_')))
                            result = result.split(',')
                            if result:
                                if tmp[parai]['format'] == 'floatmat':
                                    resultbis = [float(x) for x in result]
                                else:   
                                    resultbis = [int(x) for x in result]
                                result = resultbis
                            else: 
                                result = None
                        else: 
                            result = eval("self.%s__%s.text()" % (vi,parai.replace('.','_')))

                        if result == '' or result == 'None':
                            result = None   

                        exec("self.jobprocess.%s['%s']['value'] = result" % (vi,parai))

        try: 
            exec("job.%s = self.jobprocess" % (self.mode))
            exec("job.%s.check(verbose=False)" % (self.mode))
            ez.save(job,self.pathjobfile,verbose=False)
            self.messagesuccess('The new parameters have been saved.')
        except Exception as e:
            self.messageerror('Error during the parameter saving: %s' % (e))

    def closemaybe(self):
        """Quit the Widget
        """
        ret = QMessageBox.warning(self, "Quit?",
                "Do you want to save your changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if ret == QMessageBox.Save:
            self.save()
            self.closing.emit(True)
            return self.close()
        if ret == QMessageBox.Cancel:
            return False
        if ret == QMessageBox.Discard:
            self.closing.emit(True)
            return self.close()

###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not os.path.isfile(args['--file']):
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No file',None))
    
    if not args['--mode'] in ['coregistration', 'ifgstack', 'tsprocessing', 'intstack']:
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No correct mode',None))

    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open a tool to change the parameters of an EZ-InSAR processing job from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        widget = parameterWidget(os.path.abspath(args['--file']), args['--mode'])
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()

