#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

from PyQt5.QtCore import pyqtSignal, QMutex, QMutexLocker, QSize, QThread, QWaitCondition
from ezinsardesktopmodule.config.settings import __Cputime__
import time, psutil

class RenderThread(QThread):

    textSignal = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super(RenderThread, self).__init__(parent)

        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.resultSize = QSize()
        self.restart = False
        self.abort = False
        self.TextInfo = ''
        

    def __del__(self):
        self.mutex.lock()
        self.abort = True
        self.condition.wakeOne()
        self.mutex.unlock()

        self.wait()

    def render(self):
        locker = QMutexLocker(self.mutex)

        if not self.isRunning():
            self.start(QThread.LowPriority)
        else:
            self.restart = True
            self.condition.wakeOne()

    def run(self):
        while True:
            self.mutex.lock()
            self.mutex.unlock()

            try: 
                while True:

                    ## Compute the read/write disk usage
                    start_time = time.time()
                    disk_io_counter = psutil.disk_io_counters()
                    start_read_bytes = disk_io_counter[2]
                    start_write_bytes = disk_io_counter[3]
                    network_io_counter = psutil.net_io_counters()
                    start_send_bytes = network_io_counter[0]
                    start_recv_bytes = network_io_counter[1]

                    time.sleep(__Cputime__)
                    disk_io_counter = psutil.disk_io_counters()
                    end_read_bytes = disk_io_counter[2]
                    end_write_bytes = disk_io_counter[3]
                    network_io_counter = psutil.net_io_counters()
                    end_send_bytes = network_io_counter[0]
                    end_recv_bytes = network_io_counter[1]
                    end_time = time.time()

                    time_diff = end_time - start_time

                    read_speed = (end_read_bytes - start_read_bytes)/time_diff
                    write_speed = (end_write_bytes - start_write_bytes)/time_diff
                    read_mega_bytes_sec = round(read_speed / (1024**2), 2)
                    write_mega_bytes_sec = round(write_speed / (1024**2), 2)

                    send_speed = (end_send_bytes - start_send_bytes)/time_diff
                    recv_speed = (end_recv_bytes - start_recv_bytes)/time_diff
                    send_mega_bytes_sec = round(send_speed / (1024**2), 2)
                    recv_mega_bytes_sec = round(recv_speed / (1024**2), 2)

                    if psutil.cpu_percent(interval=1) <= 50:
                        colorcpu = 'green'
                    elif psutil.cpu_percent(interval=1) <= 75:
                        colorcpu = 'orange'
                    else:
                        colorcpu = 'red'

                    if psutil.virtual_memory().percent <= 50:
                        colorram = 'green'
                    elif psutil.virtual_memory().percent <= 75:
                        colorram = 'orange'
                    else:
                        colorram = 'red'


                    self.TextInfo = """
                        <p><b>CPU usage</b>: <font color="%s">%0.2f %%</font></p>
                        <p><b>RAM Memory usage</b>: <font color="%s">%0.2f %%</font></p>
                        <p><b>Disk(s) reading/writing</b>:
                        <p style="text-indent:20px;">Reading: %0.2f MB/s</p>
                        <p style="text-indent:20px;">Writing: %0.2f MB/s</p>
                        <p><b>Disk(s) Storage(s)</b>:
                        """ % (colorcpu,
                               psutil.cpu_percent(interval=1),
                               colorram,
                               psutil.virtual_memory().percent,
                               read_mega_bytes_sec,
                               write_mega_bytes_sec)
                    
                    listdisk = psutil.disk_partitions()
                    for diski in listdisk:

                        tmp = psutil.disk_usage(diski.mountpoint)

                        if tmp.percent <= 50:
                            colordisk = 'green'
                        elif tmp.percent <= 75:
                            colordisk = 'orange'
                        else:
                            colordisk = 'red'

                        self.TextInfo = self.TextInfo + """
                            <p>Device: %s </p>
                            <p style="text-indent:20px;">Mount Point: %s </p>
                            <p style="text-indent:20px;">Total: %0.2f GB </p>
                            <p style="text-indent:20px;">Used: %0.2f GB </p>
                            <p style="text-indent:20px;">Free: %0.2f GB </p>
                            <p style="text-indent:20px;">Usage: <font color="%s">%0.2f %%</font> </p>
                            """% (
                            diski.device,
                            diski.mountpoint,
                            tmp.total / (2**30),
                            tmp.used / (2**30),
                            tmp.free / (2**30),
                            colordisk,
                            tmp.percent,
                            )
                        
                    ## For the network
                    self.TextInfo = self.TextInfo+ """
                        <p><b>Network(s) Send/Received</b>:
                        <p style="text-indent:20px;">Send: %0.2f MB/s</p>
                        <p style="text-indent:20px;">Received: %0.2f MB/s</p>
                        """ % (send_mega_bytes_sec,
                               recv_mega_bytes_sec)
                    
                    ## For the laptop battery
                    self.TextInfo = self.TextInfo + """
                        <p><b>Power battery (only for laptop)</b>:
                        """
                    
                    battery = psutil.sensors_battery()
                    if battery is not None:
                        self.TextInfo = self.TextInfo + """
                            <p style="text-indent:20px;">Battery Percentage: %0.2f %%<p>
                            """ % (
                                battery.percent,
                                )
                        if battery.power_plugged:
                            self.TextInfo = self.TextInfo + """
                                <p style="text-indent:20px;">Power plugged<p>
                                """ 
                        else:
                            self.TextInfo = self.TextInfo + """
                                <p style="text-indent:20px;">Power unplugged<p>
                                """
                    else:
                        self.TextInfo = self.TextInfo + """
                            <p style="text-indent:20px;">No battery information available.<p>
                            """
                        
                    # For the temperatures

                    self.textSignal.emit(self.TextInfo)

            except:
                a = 'dummy'

            self.mutex.lock()
            if not self.restart:
                self.condition.wait(self.mutex)
            self.restart = False
            self.mutex.unlock()