#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Trick to import the correct EZ-InSAR job class
"""

import os 

try: 
    if os.environ['ezinsargamma'] in ['True','true',True,1]:
        from ezinsargammamodule.core.ezinsarprocessor import *
        from ezinsargammamodule.cli.ezinsarappgamma_clitools import __help_CLIrun__
        print('Import the EZ-InSAR from the GAMMA module')
except: 
    from ezinsar.ezinsarprocessor import *
    __help_CLIrun__ = ''
