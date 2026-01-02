#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Run an EZ-InSAR sub-program

This application allows to run an EZ-InSAR sub-program. 

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 

        $ ezinsar program --help

Changelog:
    * 3.0.0: Initial version, Dec. 2024

"""

__docstringapp__ =  """EZ-InSAR application: Run an EZ-InSAR sub-program

usage: ezinsar program <program> [<args>...] [options]

Arguments:
    <str>        Name of the EZ-InSAR sub-program

Other-options:
    -h, --help
    -q, --quiet         Suppress verbose

"""

from docopt import docopt
import os 
from subprocess import call
import pandas as pd
import numpy as np

from ezinsar import usermessage
from ezinsar import constants
__copyright__ = constants.__copyright__

def main():
    """Main function"""
    args = docopt(__docstringapp__,options_first=True)
       
    if args['--quiet']: 
        verbose = False
    else:
        verbose = True

    ################################################################################################################
    ## For BWLava 
    ################################################################################################################
    if args['<program>'].lower() == 'bwlava':
        usermessage.openingmsg(__name__,__name__,__file__,__copyright__,'Open the BWLava application with MATLAB',None,verbose)
        try: 
            import matlab.engine
            use_matlabengine = True
        except: 
            usermessage.warningmsg(__name__,__name__,__file__,'Impossible to import the MATLAB engine. Please see if your installation is correct.',None,verbose)
            use_matlabengine = False
        if use_matlabengine:
            usermessage.ezprint('Start the MATLAB engine',None,verbose)
            eng = matlab.engine.start_matlab()
            eng.cd(constants.__file__.replace('constants.py','contrib'+os.sep+'MATLAB'+os.sep+'BWLava'+os.sep))
            eng.BWLava
        else: 
            import sys
            cmd = '''matlab -nodesktop -r "cd %s; BWLava('close')"''' % (constants.__file__.replace('constants.py','contrib'+os.sep+'MATLAB'+os.sep+'BWLava'+os.sep))
            sys.exit(os.system(cmd))

    ################################################################################################################
    ## For EGMStoolkit 
    ################################################################################################################
    elif args['<program>'].lower() == 'egmstoolkit':
        usermessage.openingmsg(__name__,__name__,__file__,__copyright__,'Open the EGMStoolkit application',None,verbose)
        status = os.system('EGMStoolkit %s' % (' '.join(args['<args>'])))
        if not status == 0: 
            raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error when trying to run EGMStoolkit. Please check your installation: https://github.com/alexisInSAR/EGMStoolkit',None))
        
    ################################################################################################################
    ## For Volcano name 
    ################################################################################################################
    elif args['<program>'].lower() == 'volcanoname':
        usermessage.openingmsg(__name__,__name__,__file__,__copyright__,'Print the Holocene Volcano List from Global Volcanism Program database. ',None,verbose)
        db = pd.read_csv(os.path.dirname(__file__)+os.sep+'..'+os.sep+'3rdparty'+os.sep+'GVP_Volcano_List_Holocene.csv') 

        tmp = np.sort(db['Volcano Name']).tolist()
        while not len(tmp)/3 == np.fix(len(tmp)/3):
            tmp = tmp + [' ']
        tmp = np.array(tmp).reshape(int(len(tmp)/3),3)

        for i1 in range(tmp.shape[0]):
            usermessage.ezprint("{:<50}".format(tmp[i1,0]) + "{:<50}".format(tmp[i1,1]) + "{:<50}".format(tmp[i1,2]),None,verbose)

    ################################################################################################################
    ## List the available programs
    ################################################################################################################
    elif args['<program>'].lower() == 'list':
        usermessage.openingmsg(__name__,__name__,__file__,__copyright__,'Print the list of available external-programs',None,verbose)

        list = {'BWLava': 'MATLAB tool to extract lava-flow outlines from InSAR coherence images.',
                'EGMStoolkit': 'Python application to download, process and manipulate InSAR datasets from European Ground Motion service.',
                'VolcanoName': 'Print the volcano names from the Global Volcanism Program database.',
                'list': 'Print the list of available programs.',
                }
        
        for ki in list.keys(): 
            usermessage.ezprint('External program: %s' % (ki),None,verbose)
            usermessage.ezprint('\t%s\n' % (list[ki]),None,verbose)
    ################################################################################################################

    else: 
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'The program %s is not available in EZ-InSAR.' % (args['<program>']),None))
       
if __name__=='__main__':
    main()