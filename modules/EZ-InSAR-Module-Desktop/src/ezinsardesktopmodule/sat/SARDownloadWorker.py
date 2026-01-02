#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-


from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication

import time
import ezinsar.job as ez

class Worker(QObject):

    textSignal = pyqtSignal(str)
    finished = pyqtSignal()
    intReady = pyqtSignal(int)
    error = pyqtSignal(str)
    success = pyqtSignal(str)
    progress = pyqtSignal(float)
    currentSLClist = pyqtSignal(list)
    
    def __init__(self, jobfile, reply, advoptions, mode = 'image', parent=None, indexdate=None):
        super(Worker, self).__init__(parent)

        self.jobfile = jobfile
        self.TextInfo = ''
        self.job = ez.load(jobfile,verbose=False)
        self.running = True
        self.messageerror = ''
        self.messagesuccess = ''
        self.valueprogress = 0.0
        self.parent = parent    

        self.indexdate = indexdate
        self.server = reply.server
        self.mode = mode
        self.username =  reply.username
        self.password = reply.password
        self.serverorbit = reply.serverorbit
        self.orbitfilebased = reply.orbitfilebased
        self.advancedoptions = advoptions

    def run(self):
        try:
            if self.mode == 'image':
                self.valueprogress = 0 
                self.progress.emit(self.valueprogress)
                QApplication.processEvents()

                for idx in self.indexdate:
                    self.job.downloadSLC(index = [idx],
                                        verbose=False,
                                        username=self.username,
                                        password=self.password,
                                        burstonly = self.advancedoptions['burstonly'],
                                        partialdownloading = self.advancedoptions['partialdownloading'],
                                        modepartial = self.advancedoptions['modepartial'],
                                        zipping = self.advancedoptions['zipping'],
                                        )
                
                    self.valueprogress = (idx+1)/len(self.indexdate)
                    self.progress.emit(self.valueprogress)
                    self.currentSLClist.emit(self.job.SLClist['Stored'].to_list())
                    QApplication.processEvents()

            elif self.mode == 'orbit':
                self.job.downloadorbit(verbose=False,
                                    server=self.serverorbit,
                                    username=self.username,
                                    password=self.password,
                                    filebased = self.orbitfilebased)
            
            else:
                self.job.downloadETAD(verbose=False,
                                    username=self.username,
                                    password=self.password,
                                    filebased = self.orbitfilebased)
                
            time.sleep(1)

        except Exception as e:
            time.sleep(1)
            self.messageerror = '%s' % (e)
            self.error.emit(self.messageerror)
    
        if self.messageerror == '':
            self.messagesuccess = 'Downloading completed.'
            self.success.emit(self.messagesuccess)

        self.running=False
        self.finished.emit()
    
