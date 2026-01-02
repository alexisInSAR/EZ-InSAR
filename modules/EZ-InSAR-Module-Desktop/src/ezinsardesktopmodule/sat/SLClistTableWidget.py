#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR Desktop**: Open a window for the EZ-InSAR SLC list

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Changelog:
    * 1.1.3: Change the import line, Dec. 2025, Alexis Hrysiewicz
    * 0.1.0: Initial version, Feb. 2025

"""

__docstringapp__ = """EZ-InSAR Desktop: Open a a window for the EZ-InSAR SLC list

usage: 
    ezinsardesktop_SLClist -f <str> [options]

Arguments:
    -f, --file <str>        EZ-InSAR job file

Other-options:
    -h, --help
"""


###########################################################################################
## Packages
###########################################################################################
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon,  QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QPushButton, QWidget, QTableView, QGroupBox

import os, sys
import numpy as np
from docopt import docopt
import datetime

from ezinsar import constants, usermessage
import ezinsar.job as ez
from ezinsardesktopmodule import __file__ as __root_module__
__root_module__ = os.path.dirname(__root_module__)
from ezinsardesktopmodule.config.settings import __theme__
from ezinsardesktopmodule.tools import tools
from ezinsardesktopmodule import __copyrightPackage__, __namePackage__, __versionPackage__
from ezinsardesktopmodule.tools.docsWidget import DocsDialog

###########################################################################################
## Classes
###########################################################################################
class PandasTableModel(QStandardItemModel):
    """Table Pandas Table class"""
    def __init__(self, data, parent=None):
        QStandardItemModel.__init__(self, parent)
        self._data = data
        for col in data.columns:
            data_col = [QStandardItem("{}".format(x)) for x in data[col].values]
            for idx, ri in enumerate(data_col):
                data_col[idx].setEditable(False)
            self.appendColumn(data_col)
        return

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def headerData(self, x, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[x]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self._data.index[x]
        return None
    
class SLClisttable(QWidget):
    """Widget class"""
    closing = pyqtSignal(bool)

    def __init__(self, jobfile, parent=None):
        super(SLClisttable, self).__init__(parent)

        self.pathjobfile = jobfile
        self.setWindowTitle("EZ-InSAR - SLC list")
        self.resize(750,500)

        self.setStyleSheet(__theme__)

        job = ez.load(self.pathjobfile,verbose=False)
        
        widgetlogo = tools.create_logo_wigdet()
        widgettitle = QLabel('<p style="font-size:20px"><b>Single-Look-Complex List</b></p>')
        btQuit = QPushButton("Close", self)
        
        btHelp = QPushButton("Help", self)
        btHelp.clicked.connect(self.openhelp)

        self.pdtable = QTableView()
        self.model = PandasTableModel(job.SLClist)
        self.pdtable.setModel(self.model)


        infogrp = QGroupBox('SLC overview')
        infogrpLayout = QGridLayout()


        nbFileLabel =  QLabel("<p><b>File(s)/Slice(s):</b></p>")
        nbFileLabel.setToolTip("""
                                <p>Number of files available in the SLC list. Several files (i.e., slices) must be required for an unique dates with Sentinel-1.</p>
                                """)
        nbFile = QLabel("%s" % (len(job.SLClist['Name'])))
        infogrpLayout.addWidget(nbFileLabel,0,0,1,1,Qt.AlignLeft)
        infogrpLayout.addWidget(nbFile,0,1,1,1,Qt.AlignRight)

        dates = []
        dateformatted = []
        for idxrow, row in job.SLClist.iterrows():
            dates.append(row['Date1'].split('T')[0])
            dateformatted.append(datetime.datetime.strptime(row['Date1'].split('T')[0],'%Y-%m-%d').timestamp())
        dates = np.sort(dates).tolist()
        dateformatted = np.sort(dateformatted).tolist()

        nbDateLabel =  QLabel("<p><b>Date(s):</b></p>")
        nbDateLabel.setToolTip("""
                                <p>Number of dates available in the SLC list.</p>
                                """)
        nbDate = QLabel("%s" % (len(np.unique(dates))))
        infogrpLayout.addWidget(nbDateLabel,1,0,1,1,Qt.AlignLeft)
        infogrpLayout.addWidget(nbDate,1,1,1,1,Qt.AlignRight)

        nbDate1Label =  QLabel("<p><b>First date:</b></p>")
        nbDate1 = QLabel("%s" % (dates[0]))
        infogrpLayout.addWidget(nbDate1Label,2,0,1,1,Qt.AlignLeft)
        infogrpLayout.addWidget(nbDate1,2,1,1,1,Qt.AlignRight)

        nbDate2Label =  QLabel("<p><b>Last date:</b></p>")
        nbDate2 =  QLabel("%s" % (dates[-1]))
        infogrpLayout.addWidget(nbDate2Label,3,0,1,1,Qt.AlignLeft)
        infogrpLayout.addWidget(nbDate2,3,1,1,1,Qt.AlignRight)

        nbTSLabel =  QLabel("<p><b>Median temporal sampling [days]:</b></p>")
        nbTS =  QLabel("%s" % (np.median(np.gradient(dateformatted)/(3600*24))))
        infogrpLayout.addWidget(nbTSLabel,4,0,1,1,Qt.AlignLeft)
        infogrpLayout.addWidget(nbTS,4,1,1,1,Qt.AlignRight)

        infogrp.setLayout(infogrpLayout)

        layout = QGridLayout()
        layout.addWidget(widgetlogo, 0, 0, 1, 1)
        layout.addWidget(widgettitle, 0, 1, 1, 8, Qt.AlignCenter)
        layout.addWidget(self.pdtable, 2, 0, 8, 10)
        layout.addWidget(infogrp, 10, 0, 1, 10)
        layout.addWidget(btQuit, 0, 9, 1, 1)
        layout.addWidget(btHelp,11, 0, 1, 1)
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
    
    usermessage.openingmsg(__file__,main.__name__,__file__,__namePackage__+'\n\t\t'+__versionPackage__+'\n\t\t'+__copyrightPackage__,'Open the SLC list from EZ-InSAR Desktop Application',None,True,lockfree=True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))
    if tools.checklicense():
        widget = SLClisttable(os.path.abspath(args['--file']))
        widget.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__=='__main__':
    main()

