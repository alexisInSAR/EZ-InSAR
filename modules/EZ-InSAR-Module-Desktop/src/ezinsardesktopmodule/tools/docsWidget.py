#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open the Docs tool

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.0.0: Initial version, Aug. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open the DEM tool

usage: 
    ezinsardesktop_docs [options]

Options:
    -m, --module <str>        Name of the module

Other-options:
    -h, --help
"""
###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QComboBox, QWidget, QDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView

import os, sys
from docopt import docopt

from ezinsar import constants, usermessage
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__

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
        
        url = '%s%s%s' % (os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
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

class Docstool(QWidget):
    """QWidget class 
        Build the widget windows
    """

    def __init__(self, module=None, parent=None):
        super(Docstool, self).__init__(parent)

        self.setWindowTitle("EZ-InSAR - Documentation")
        self.setStyleSheet(__theme__)
        self.resize(1700, 750)
        self.parent = parent
        
        ## Detect the modules
        # For EZ-InSAR 
        exec('from ezinsar import __file__ as tmpfile')
        tmp = eval("tmpfile.replace('src%sezinsar%s__init__.py','')" % (os.sep,os.sep))
        url = 'file:'+tmp+'docs'+os.sep+'build'+os.sep+'html'+os.sep+'index.html'
        self.modulesInfo = {'EZ-InSAR': url.replace(os.sep,'/')}
        
        # For the optional modules
        for mi in constants.__EZInSARoptionalmodule__:
            try: 
                if mi == 'gamma':
                    if mi.lower() == 'gamma':
                        if not os.environ['ezinsargamma'] in ['True','true',True,1]:
                            raise ValueError('ERROR')
                exec('from ezinsar%smodule import __file__ as tmpfile' % (mi.lower()))
                exec('from ezinsar%smodule import __namePackage__ as tmp2' % (mi.lower()))
                name = eval('tmp2')
                tmp = eval("tmpfile.replace('src%sezinsar%smodule%s__init__.py','')" % (os.sep,mi.lower(),os.sep))  
                url = 'file:'+tmp+'docs'+os.sep+'build'+os.sep+'html'+os.sep+'index.html'
                self.modulesInfo[name] = url.replace(os.sep,'/')
            except: 
                a = 'dummy'

        ## Title + quit button  
        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p style="font-size:20px"><b>EZ-InSAR Documentation<\b></p>')

        ## List of modules
        self.list = QComboBox()
        self.list.addItems(list(self.modulesInfo.keys()))

        ## Webpage
        self.page = QWebEngineView()

        ## Layout
        layout = QGridLayout()
        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 8, Qt.AlignCenter)

        layout.addWidget(self.list, 1, 0, 1, 10)
        layout.addWidget(self.page, 2, 0, 10, 10)

        self.setLayout(layout)

        if module == None:
            self.list.setCurrentText('EZ-InSAR')
        else:
            idx = [x.lower() for x in constants.__EZInSARoptionalmodule__].index(module)
            self.list.setCurrentText(list(self.modulesInfo.keys())[idx+1])

        self.changepage()
        self.list.currentTextChanged.connect(self.changepage)

    ###########################################################################################
    ## Callbacks
    ###########################################################################################
    def changepage(self):
        self.page.load(QUrl(self.modulesInfo[self.list.currentText()]))
        
###########################################################################################
## main 
########################################################################################### 
def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if not args['--module'] == None:
        if not args['--module'].lower() in [x.lower() for x in constants.__EZInSARoptionalmodule__]:
            raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyrightPackage__,'No module available',None))
    
    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the Documentation tool from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_docs_whiteback.svg'))
    if tools.checklicense():
        widget = Docstool(module=args['--module'])
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()
