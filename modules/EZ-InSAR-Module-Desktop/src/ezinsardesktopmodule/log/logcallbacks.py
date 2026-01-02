#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

import subprocess
from ezinsardesktopmodule.config.settings import __nbLineLog__
from collections import deque

def updatelog(logfile):

        with open(logfile, 'r') as f:
                text = ''.join(list(deque(f, maxlen=__nbLineLog__)))

        return text   


    