#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZ-InSAR application**

EZ-InSAR wrapper for running of different sub-programs.

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
        Please see the different command to have a full description:: 

                $ ezinsar --help

Changelog:
        * 3.3.1: New command for the hydroocean module, Nov. 2025, Alexis Hrysiewicz
        * 3.2.2: New command: S1detect, Sep. 2025, Alexis Hrysiewicz
        * 3.2.1: Several changes,  Aug. 2025, Alexis Hrysiewicz
                * Add the command for ETAD files
                * Add the multispectral entry
                * S1slc command becomes download
                * New command: S1planned
                * Improvements of the HELP
                * New interface for the DEM commands
        * 3.2.0: Add the job tool and the GNSS interface, Jul. 2025, Alexis Hrysiewicz
        * 3.1.0: New docs and toolkit commands, Feb. 2025, Alexis Hrysiewicz
        * 3.0.0: Initial version, Jan. 2024

"""
from ezinsar import __versionPackage__,__copyrightPackage__

__docstringapp__ = """EZ-InSAR application

Welcome to the EZ-InSAR wrapper for running of different programs.
                                   
                    ....                          
                   ...  ...                       
                      ...  ...                    
                         ....::  &&               
  &&&&&& &&&&&&&               &&&&&&&            
 &&&        &&&&            ..&&&&&&&&            
 &&&&&&    &&&                  &&&& ......       
 &&&&&&   &&&    &&&&&&&&          ..  ..  ...    
 &&&     &&&                            ...  ... 
  &&&&&& &&&&&&&                             ...  

              &&&&&&  &&&&&&&&  &&&&&&            
             &&&&     &&&  &&&  &&&  &&           
              &&&&&   &&&&&&&&  &&&&&&&&           
                &&&&  &&&  &&&  &&&  &&&           
              &&&&&&  &&&  &&&  &&&  &&&           
             &&&&&&   &&&  &&&  &&&  &&&   

                                                Version: %s 
                                                %s

usage:  
        ezinsar
        ezinsar <command> [<args>...] 
        ezinsar -h | --help
        ezinsar --version

ezinsar command - without arguments - will run EZ-InSAR via the Desktop application. 
This feature is offered by an optional module of EZ-InSAR. 
Please verify that the module is installed and ready. 
        
The SLC-related commands are:
        download                List and download SLC files

The DEM-related command is:
        dem                     Open the DEM interface

The processing-related commands are:
        init                    Create a .xml file for an EZ-InSAR job
        run                     Run an EZ-InSAR processing job
        bestref                 Compute a coarse interferometric network to find the best reference date
        update                  Update a full SAR/InSAR processing based on a EZ-InSAR job
        job                     Advanced tools for EZ-InSAR jobs

The interferogram-related commands are:
        quickifg                Quick computation of an interferogram

The Sentinel-1-related commands are: 
        S1orbit                 Download Sentinel-1 orbits
        S1etad                  Download Sentinel-1 ETAD files
        S1planned               Find the planned acquisitions of Sentinel-1 
        lastS1                  Quick computation of the most recent Sentinel-1 interferogram
        S1detect                Detect the Sentinel-1 IW track and orbits
        S1mosaic                Download S1 IW mosaics

The archive-related commands are:
        archive                 Create an EZ-InSAR archive
        archive_decrypt         Decrypt an EZ-InSAR archive

The interface-related commands are:
        desktop                 Open specific parts of EZ-InSAR Desktop application (use simply ezinsar command to open the application) (required the optional module)
        webapp                  Open the EZ-InSAR Graphical User Interface based on Plotly Dash (Web App) (required the optional module)
        tsdisplayer             Open the Time-Series Displayer (required the optional module)
                
The docker-related command is:
        docker                  Open an EZ-InSAR container

The optional-module-related commands are: 
        gamma                   Open the command-line interface for GAMMA processor (required the optional module)
        gnss                    Open the command-line interface for the EZ-InSAR GNSS module (required the optional module)
        multispectral           Open the command-line interface for the EZ-InSAR Multispectral module (required the optional module)
        hydroocean              Open the command-line interface for the EZ-InSAR Hydro-Ocean module (required the optional module)

The sub-application-related command is:
        program                 Run the EZ-InSAR sub-program

The documentation-related command is:
        docs                    Open the documentation in the Web browser

The installation-related command is
        toolkit                 Manage the installation of EZ-InSAR (i.e., updating and information printing)

Options: 
        --nolicensecheck        Lock the license verification. EZ-InSAR will consider that users have read the licenses.
        -h, --help              Show this screen.
        -v, --version           Show version.

See 'ezinsar <command> --help' for more information on a specific command.
""" % (__versionPackage__,__copyrightPackage__)

from subprocess import call
from docopt import docopt
import os 
import platform
import sys

from ezinsar import usermessage
from ezinsar.tools import miscellaneous
from ezinsar import constants
__copyright__ = constants.__copyright__

def main():
        """Main function"""

        if '--unlockgamma' in sys.argv:
                sys.argv.remove('--unlockgamma')  
                os.environ['ezinsargamma'] = 'true'

        args = docopt(__docstringapp__,
                options_first=True,version='%s:\n\tDeveloped by: %s\n\tVersion: %s\n\t%s\n\nFor more information, please use the toolkit command.' % (constants.__name__,constants.__author__,constants.__version__,constants.__copyright__))
        
        # Modification of args
        if '--nolicensecheck' in args['<args>']:
                asklicense = False
                args['<args>'].remove('--nolicensecheck')  
        else:
                asklicense = True

        #################################
        ## Run the Desktop application by default 
        if not args['<command>']:
                try:
                        from ezinsardesktopmodule.EZInSAR_Desktop import __file__ as __EZInSAR_Desktop__
                except:
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                        'EZ-InSAR Desktop is an optional module. Please verify that it is installed and ready.',None))
                # usermessage.openingmsg(__name__,main.__name__,__file__,__copyright__,'Welcome to EZ-InSAR (Desktop Application)',None,True)
                if not platform.system() == 'Windows':
                        exit(call(__EZInSAR_Desktop__, shell=True, env=os.environ.copy()))
                else:
                        os.system('python '+__EZInSAR_Desktop__)

        #################################
        ## For the normal command 
        else:  
                argv = [args['<command>']] + args['<args>']

                if args['<command>'] in ['download','S1planned','S1mosaic','S1detect','S1orbit','S1etad','init','run','bestref',
                                        'update','quickifg','lastS1','archive','archive_decrypt','webapp','3DdispSE','docker','program','docs','toolkit','job'] :
                        miscellaneous.checklicense(asklicense=asklicense)
                        
                        exit(call(['ezinsarapp_%s' % (args['<command>'])] + argv))

                # Run the dem interface 
                elif args['<command>'] in ['dem']:
                        miscellaneous.checklicense(asklicense=asklicense)
                        exit(call(['ezinsarapp_%s_master' % (args['<command>'].replace('2',''))] + argv))

                # Run the applications provided by the EZ-InSAR Server module
                elif args['<command>'] == 'server':
                        
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                        'The EZ-InSAR server is under development and currently not ready.',None))
                
                # Run the applications provided by the EZ-InSAR GAMMA module
                elif args['<command>'] == 'gamma':
                        miscellaneous.checklicense(asklicense=asklicense)
                        try:    
                                if os.environ['ezinsargamma'] in ['True','true',True,1]:
                                        from ezinsargammamodule.cli import ezinsarappgamma_clitools
                        except:
                                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                                'EZ-InSAR GAMMA Module is an optional module. Please verify that it is installed and ready.',None))
                        ezinsarappgamma_clitools.send_cmd(args)
                       
                # Run the applications provided by the EZ-InSAR Desktop module
                elif args['<command>'] == 'desktop':
                        try:
                                from ezinsardesktopmodule.tools.tools import send_cmd
                        except:
                                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                                'EZ-InSAR GAMMA Module is an optional module. Please verify that it is installed and ready.',None))
                        send_cmd(args)

                # Run the applications provided by the EZ-InSAR TSDisplayer module
                elif args['<command>'] == 'tsdisplayer':
                        miscellaneous.checklicense(asklicense=asklicense)
                        try:
                                from ezinsartsdisplayermodule import __file__ as __EZInSAR_TSDisplayer__
                        except:
                                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                                'EZ-InSAR TSDisplayer is an optional module. Please verify that it is installed and ready.',None))
                        exit(call(['ezinsartsdisplayer_run'] + args['<args>']))

                # Run the applications provided by the EZ-InSAR GNSS module
                elif args['<command>'] == 'gnss':
                        miscellaneous.checklicense(asklicense=asklicense)
                        try:
                                from ezinsargnssmodule.constants import __help_CLI__, send_cmd
                        except:
                                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                                'EZ-InSAR GNSS is an optional module. Please verify that it is installed and ready.',None))
                        send_cmd(args)

                # Run the applications provided by the EZ-InSAR Multispectral module
                elif args['<command>'] == 'multispectral':
                        miscellaneous.checklicense(asklicense=asklicense)
                        try:
                                from ezinsarmultispectralmodule.constants import __help_CLI__, send_cmd
                        except:
                                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                                'EZ-InSAR Multispectral is an optional module. Please verify that it is installed and ready.',None))
                        send_cmd(args)

                # Run the applications provided by the EZ-InSAR HydroOcean module
                elif args['<command>'] == 'hydroocean':
                        miscellaneous.checklicense(asklicense=asklicense)
                        try:
                                from ezinsarhydrooceanmodule.constants import __help_CLI__, send_cmd
                        except:
                                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                                                'EZ-InSAR HydroOcean is an optional module. Please verify that it is installed and ready.',None))
                        send_cmd(args)

                # For the help 
                elif args['<command>'] in ['help', None]:
                        exit(call(['ezinsar', '--help']))

                # For nothing
                else:
                        exit("%r is not a EZ-InSAR command. See 'ezinsar --help'." % args['<command>'])