#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to generate the **EZ-InSAR** message

The module allows to generate various user messages (i.e., error, warning, verbose). 
    
    (From `ezinsar` package)

Changelog:
        * 3.0.0: Initial version, Dec. 2024

"""
################################################################################
## Python packages
################################################################################
import logging
from ezinsar import constants
import os 

################################################################################
## Variables
################################################################################
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## openingmsg FUNCTION
################################################################################
def openingmsg(namescript,defname,filescript,copyright,msg,log,verbose, gui = False, lockfree=False, contribauthor = None, contribcopyright = None, contribversion = None, contribfile=None):
    """Display an opening message for the different modules of EZ-InSAR

    The function will display an opening message before the launch of EZ-InSAR command/scripts.  

    Note:
        Some constants and layout configuration can be modifed via the constants.py file. 

    Args:
        namescript (str): Name of the `ezinsar` module 
        defname (str): Name of the function
        filescript (str): Full path of the `ezinsar` module 
        copyright (str): Copyright
        msg (str): Message
        log (str): Log value. If `None`, no log will be used. 
        verbose (bool): Verbose value 
        gui (bool): GUI value (not used)
    
    """

    if lockfree == False: 
        msglicense = '\n\tThis program comes with ABSOLUTELY NO WARRANTY.\n\tThis is free software, and you are welcome to redistribute it under certain conditions.'
    else:
        msglicense = ''

    if not contribauthor == None: 
        msgcontrib = '\n\tThis script/program is a contribution.\n\t\tAuthor(s): %s.\n\t\tCopyright: %s\n\t\tVersion: %s\n\t\tFile: %s' % (contribauthor, contribcopyright, contribversion, contribfile)
    else: 
        msgcontrib = ''

    ## Assembly the message and run the ezprint function
    ezprint('%s\n%s %s\n\n%s\n%s.%s:\n\t%s\n\n\tScript: %s\n\t\t%s\n%s\n%s\n%s\n' % (constants.__displayline1__,
        constants.__name__,
        constants.__version__,
        constants.__displayline2__,
        namescript,
        defname,
        msg,
        filescript,
        copyright,
        msglicense,
        msgcontrib, 
        constants.__displayline1__,
        ),
        log,
        verbose, gui = gui)   
    

    __author__ = 'Alexis Hrysiewicz (UCD / iCRAG)'
__copyright__ = "Copyright 2025, EZ-InSAR / UCD / iCRAG"
__version__ = '1.0.0'

################################################################################
## typeerrormsg FUNCTION 
################################################################################
def typeerrormsg(namescript,defname,filescript,copyright,msg1,msg2,log, gui = False): 
    """Create a type-error message 

    The function creates a type-error message for EZ-InSAR

    Args:
        namescript (str): Name of the `ezinsar` module 
        defname (str): Name of the function
        filescript (str): Full path of the `ezinsar` module 
        copyright (str): Copyright
        msg1 (str): Name of the variable
        msg2 (str): Definition of the variable
        log (str): Log value. If `None`, no log will be used. 
        gui (bool): GUI value (not used)

    Returns:
        str: Output message
    
    """
    # Create the message
    msgsentence = ('%s\n\tparameter: %s for %s.%s\n\t\t%s\n\t\tmust be %s'
                    % (constants.__error__,msg1,namescript,defname,filescript,msg2))
    
    # Print the message into the log file
    if not log == None: 
        logging.basicConfig(filename=log, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger=logging.getLogger() 
        logger.setLevel(definelevel(constants.__loggingmode__)) 
        logger.error(msgsentence)#.replace('\n',' '))

    return msgsentence

################################################################################
## warningmsg FUNCTION
################################################################################
def warningmsg(namescript,defname,filescript,msg1,log,verbose, gui = False): 
    """Create a warning message 

    The function creates a warning message for EZ-InSAR. 

    Args:
        namescript (str): Name of the `ezinsar` module 
        defname (str): Name of the function
        filescript (str): Full path of the `ezinsar` module 
        msg1 (str): Message
        log (str): Log value. If `None`, no log will be used. 
        verbose (bool): Verbose value 
        gui (bool): GUI value (not used)
    
    """
    # Create the message
    msgsentence = ('%s in %s.%s\n\t%s\n\t\t--> %s'
                    % (constants.__warning__,namescript,defname,filescript,msg1))
    
    # Add the message into the log file
    if not log == None: 
        logging.basicConfig(filename=log, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger=logging.getLogger() 
        logger.setLevel(definelevel(constants.__loggingmode__)) 
        logger.warning(msgsentence)#.replace('\n',' '))

    # Print the message in the verbose
    if verbose == True: 
        ezprint(msgsentence,None,True)

################################################################################
################################################################################
def errormsg(namescript,defname,filescript,copyright,msg1,log, gui = False): 
    """Create an error message 

    The function creates an error message for EZ-InSAR  

    Args:
        namescript (str): Name of the `ezinsar` module 
        defname (str): Name of the function
        filescript (str): Full path of the `ezinsar` module 
        copyright (str): Copyright
        msg1 (str): Message
        log (str): Log value. If `None`, no log will be used. 
        gui (bool): GUI value (not used)

    Returns:
        str: Output message
    
    """
    # Create the message
    msgsentence = ('%s\n\tin %s.%s\n\t\t%s\n\t\t%s'
                    % (constants.__error__,namescript,defname,filescript,msg1))
    
    # Add the message into the log file
    if not log == None: 
        logging.basicConfig(filename=log, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger=logging.getLogger() 
        logger.setLevel(definelevel(constants.__loggingmode__)) 
        logger.error(msgsentence)#.replace('\n',' '))
    
    return msgsentence

################################################################################
################################################################################
def ezprint(msg,log,verbose, gui = False):
    """Print a message into the verbose and the log 

    The function print an message into the verbose and the log. 

    Args:
        msg (str): Message
        log (str): Log value. If `None`, no log will be used. 
        verbose (bool): Verbose value 
        gui (bool): GUI value (not used)

    """
    # Trick for the stopping from the GUI (not sexy)
    if not log == None: 

        if not os.path.isfile(log):
            with open(log,'w') as fi:
                fi.write('START THE LOG\n')

        with open(log, 'rb') as f:
            try:
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(-2, os.SEEK_CUR)
            except OSError:
                f.seek(0)
            last_line = f.readline().decode('utf8').strip()
        if last_line == 'EZ-InSAR KEY: STOP':
            raise ValueError(errormsg(__name__,__name__,__file__,__copyright__,'User terminated processing.',log))
        
    # Print it into the verbose
    if verbose == True:
        print(msg)

    # Print it into the log 
    if not log == None: 
        logging.basicConfig(filename=log, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger=logging.getLogger() 
        logger.setLevel(definelevel(constants.__loggingmode__)) 
        logger.info(msg)#.replace('\n',' '))
        # logger.info(msg)

################################################################################
################################################################################
def definelevel(level):
    """Define the logging level 

    The function defines the logging level for EZ-InSAR

    Args:
        level (str): Level of logging. Can be ``NOTSET``, ``DEBUG``, ``INFO``, ``WARN``, ``ERROR``, ``CRITICAL``.

    Returns:
        str: level of logging

    """
    if level == 'NOTSET': 
        out = logging.NOTSET
    elif level == 'DEBUG': 
        out = logging.DEBUG
    elif level == 'INFO': 
        out = logging.INFO
    elif level == 'WARN': 
        out = logging.WARN
    elif level == 'ERROR': 
        out = logging.ERROR
    elif level == 'CRITICAL': 
        out = logging.CRITICAL
    else: 
        out = logging.NOTSET
    
    return out

################################################################################
################################################################################
def getprocessingstep(job,mode='normal'):
    """Get the processing step from an `ezinsar` job

    The function gets the processing step from an `ezinsar` job.

    Args:
        job (``ezinsar.job``): EZ-InSAR job
        mode (str): mode of the ready. [default: ``normal``]

    Returns:
        list: List of processing steps

    """
    liststep = []
    for si in vars(job):
        if (not si in ['email','computer','plotoptions','communpara','mintpyparameter']) and isinstance(eval('job.%s' % (si)),dict):
            liststep.append(si)

    if mode == 'all':
        liststep.append('all')


    if mode == 'all':
        liststep.append('all')

    return liststep

################################################################################
################################################################################
def createmsgsensors(mode='normal'): 
    """Create an error message for the sensors available in EZ-InSAR

    The function creates an error message for the sensors available in EZ-InSAR. This function is based on the __sensors__ and __sensorsintensity__ variables. 
    
    Args: 
        mode (str): Mode of the sensors. Can be ``normal`` or ``intensity`` 

    Returns:
        str: Output message
    
    """
    if mode == 'normal':
        sensors = constants.__sensors__
    else:
        sensors = constants.__sensorsintensity__

    cmd = '------------------------------------------------------------\n\nPlease see the list of available sensors (and acquisition modes): '
    for sati in list(sensors.keys()): 
        cmd = cmd + '\n\tFor %s:' % (sati)        
        for modei in list(sensors[sati].keys()): 
            cmd = cmd + ' %s [' % (modei)       

            if not sensors[sati][modei] == None:
                for proci in sensors[sati][modei]:
                    cmd = cmd + ' %s' % (proci) 
            else:
                cmd = cmd + ' %s' % ('Not available') 
            cmd = cmd + ' ]'

    return cmd