#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

from PyQt5.QtCore import pyqtSignal, QObject
import time
import ezinsar.job as ez

class Worker(QObject):
    textSignal = pyqtSignal(str)
    finished = pyqtSignal()
    intReady = pyqtSignal(int)
    error = pyqtSignal(str)
    success = pyqtSignal(str)
    
    def __init__(self, jobfile, server = 'Copernicus', parent=None):
        super(Worker, self).__init__(parent)
        self.jobfile = jobfile
        self.TextInfo = ''
        self.job = ez.load(jobfile,verbose=False)
        self.job.SLClist = None
        self.running = True
        self.messageerror = ''
        self.messagesuccess = ''
        self.server = server

    def run(self):
        try:
            self.job.initiateSLC(mode='online',server=self.server,verbose=False)
            ez.save(self.job,self.jobfile,verbose=False)
            time.sleep(1)
        except Exception as e:
            self.messageerror = '%s' % (e)
            self.error.emit(self.messageerror)
            time.sleep(1)
        if self.messageerror == '':
            self.messagesuccess = 'The SLC list has been created.'
            self.success.emit(self.messagesuccess)

        self.running = False
        self.finished.emit()
    
