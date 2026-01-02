#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

from PyQt5.QtCore import pyqtSignal, QObject
import time, subprocess
from ezinsardesktopmodule.config import settings
from collections import deque
from ezinsardesktopmodule.config.settings import __nbLineLog__

class Worker(QObject):

    textSignal = pyqtSignal(str)
    finished = pyqtSignal()
    intReady = pyqtSignal(int)
    
    def __init__(self, logfile, threadprocess, parent=None):
        super(Worker, self).__init__(parent)
        self.logfile = logfile
        self.TextInfo = ''
        self.process = True
        self.threadprocess = threadprocess

    def stop(self): 
        self.process = False

    def run(self):  
        while self.threadprocess.running:
            try:
                with open(self.logfile, 'r') as f:
                    self.TextInfo = ''.join(list(deque(f, maxlen=__nbLineLog__)))

                self.textSignal.emit(self.TextInfo)
                time.sleep(settings.__Updatetime__)
            except:
                a = 'dummy'
        self.finished.emit()