#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Open the EZ-InSAR documentation

This application allows to open the EZ-InSAR documentation. 

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 

        $ ezinsar docs --help

Changelog:
    * 3.1.0: Initial version, Feb. 2025

"""

__docstringapp__ =  """EZ-InSAR application: Open the EZ-InSAR documentation

usage: ezinsar docs [options]

Other-options:
    -m, --module <str>      EZ-InSAR module name for documentation
    -h, --help

"""

from docopt import docopt
from ezinsar import usermessage
from ezinsar import constants
__copyright__ = constants.__copyright__

import webbrowser
import os

def main():
    """Main function"""
    args = docopt(__docstringapp__)
             
    usermessage.openingmsg(__name__,main.__name__,__file__,__copyright__,'Run the EZ-InSAR documentation via the default web browser',None,True)

    if args['--module'] == None:
        usermessage.ezprint('Open the documentation for EZ-InSAR',None,True)
        url = 'file:'+__file__.replace('ezinsarapp_docs.py','')+'..'+os.sep+'..'+os.sep+'..'+os.sep+'docs'+os.sep+'build'+os.sep+'html'+os.sep+'index.html'
    else:  
        if args['--module'].lower() in ['multispectral','server','desktop','webapp']:
            args['--module'] = args['--module'].capitalize()
        else:
            args['--module'] = args['--module'].upper()

        name = 'EZ-InSAR %s Module' % (args['--module'])
        usermessage.ezprint('Open the documentation for %s' % (name),None,True)
        try: 
            exec('import ezinsar%smodule' % (args['--module'].lower()))
            tmp = eval("ezinsar%smodule.__file__.replace('src/ezinsar%smodule/__init__.py','')" % (args['--module'].lower(),args['--module'].lower()))            
            url = 'file:'+tmp+'docs'+os.sep+'build'+os.sep+'html'+os.sep+'index.html'
            if not os.path.isfile(url.split(':')[-1]):
                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'The %s is not available in your current EZ-InSAR installation.' % (name),None))
        except:
            raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'The %s is not available in your current EZ-InSAR installation (or the documentation is not available)' % (name),None))
    
    usermessage.ezprint('\tOpen the file %s in your browser' % (url),None,True)
    webbrowser.open_new(url)
       
if __name__=='__main__':
    main()