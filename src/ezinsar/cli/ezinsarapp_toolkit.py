#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Manage the EZ-InSAR installation

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 
        
        $ ezinsar info --help

Notes:
    The sensible information are masked (i.e., username and password). 

Changelog:
    * 3.3.1: Several changes, Dec. 2025, Alexis Hrysiewicz
        * Change the import line
        * Delete the link to the EZ-InSAR GAMMA module
    * 3.2.1: Bug fix, Alexis Hrysiewicz, Sep. 2025
    * 3.2.0: Several changes, Alexis Hrysiewicz, Jul. 2025
        * Add the creation of the config file
        * Add The shortcut creation
        * Add the cleaning of the cache
        * Add the docker image creation
        * Add the test function 
    * 3.1.0: Initial version, Feb. 2025

"""

__docstringapp__ = """EZ-InSAR application: Manage the EZ-InSAR installation

usage: ezinsar toolkit [update | info | configfile | shortcut | cleancache | docker | test] [options]

Arguments:
    info                    Print the EZ-InSAR-installation information (i.e., modules, version, etc.). 
                            Some other information cand be printed. See Optional-info-arguments
    update                  Update the EZ-InSAR toolkit based on the .git directory. See Optional-update-arguments
    configfile              Create the EZ-InSAR config file
    shortcut                Create the application shortcuts
    cleancache              Clean the cache
    docker                  Create the EZ-InSAR docker image
    test                    Test the installation of EZ-InSAR

Optional-update-arguments
    -m, --module <str>      Update a specified EZ-InSAR modules: "ezinsar" or any optional modules
    -i, --install           Install the new package with pip3 if new. It can be required if new command line interface. 
    --reinstall             Force the reinstall regardless of the new version

Optional-info-arguments
    --full                  Print the full information of EZ-InSAR: constants, cache, config files
    --packages              List all installed Python packages and their versions
    --env                   Print the environment variables. Some information can be critical for security. 
    --debug                 Report the installation information in a .txt file

Optional-shortcut-arguments
    --delete                Delete the shortcuts

Optional-configfile-arguments
    --nointeractive         lock the interactivity of the command

Optione-docker-argument
    --dockerimname <str>    Docker image name [Default: ezinsar]

Optione-test-argument
    --testSLCserver <str>    Docker image name [Default: ASF]

Other-options:
    --bypassuser            Bypass some user questions
    -h, --help

"""

from docopt import docopt
import os, glob, logging, importlib, platform, psutil, datetime, socket, subprocess, sys, shutil, subprocess, git
from ezinsar import usermessage
from ezinsar import constants
from ezinsar.tools import miscellaneous 
__copyright__ = constants.__copyright__

def main():
    """Main function"""
    args = docopt(__docstringapp__)
    # print(args)
    info = {}
    info['hostname']=socket.gethostname()

    if args['update'] == False and args['info'] == False and args['configfile'] == False and args['shortcut'] == False and args['cleancache'] == False and args['docker'] == False and args['test'] == False:
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                        'The required arguments are <info> or <update> or <configfile> or <shortcut> or <cleancache> or <docker> or <test>.',None))

    ########################################################################
    ## Update the installation
    ########################################################################
    if args['update'] == True:
        cur_dir = os.getcwd()

        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
            'This feature is not available with the current version.',None))

    ########################################################################
    ## Print the installation information
    ########################################################################
    elif args['info'] == True:

        if (not args['--module'] == None) or (args['--install'] == True) or (args['--reinstall'] == True) or (args['--nointeractive'] == True) or (args['--delete'] == True):
            raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                        'The optional arguments --module, --reinstall, --install, --nointeractive and --delete are only compatible with other modes.',None))

        namefile = 'EZInSAR_Report_%s_%s.txt' % (datetime.datetime.now().strftime('%Y%B%d'),info['hostname'])
        if args['--debug']:
                log = namefile
                logging.basicConfig(filename=log, filemode='w', 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                logger=logging.getLogger() 
                logger.setLevel('INFO') 
        else:
                namefile = None
                log = None

        usermessage.openingmsg(__name__,main.__name__,__file__,__copyright__,'Print the information installation of EZ-InSAR',log,True)

        ########################################################################
        result = miscellaneous.checkmodule('ezinsar')
        usermessage.ezprint('The EZ-InSAR core:\n\n\tName: %s\n\tAuthor: %s\n\tCopyright: %s\n\tVersion: %s\n\tNew version: %s' % (
                        result['__namePackage__'],
                        result['__authorPackage__'],
                        result['__copyrightPackage__'],
                        result['__versionPackage__'],
                        result['__versionUpdate__'],
                        ),    
                        log,True)

        ########################################################################
        usermessage.ezprint('\nThe EZ-InSAR sensor modules are:',log,True)
        for li in miscellaneous.listmodule('sensor'):
            result = miscellaneous.checkmodule(li,type='sensor')
            usermessage.ezprint('\n\tName: %s\n\tAuthor: %s\n\tCopyright: %s\n\tVersion: %s\n\tNew version: %s' % (
            result['__namePackage__'],
            result['__authorPackage__'],
            result['__copyrightPackage__'],
            result['__versionPackage__'],
            result['__versionUpdate__'],
            ),    
            log,True)               
        
        ########################################################################
        usermessage.ezprint('\nThe EZ-InSAR processor modules are:',log,True)
        from ezinsar.eicomponents import processor
        for li in miscellaneous.listmodule('processor'):
            result = miscellaneous.checkmodule(li,type='processor')
            usermessage.ezprint('\n\tName: %s\n\tAuthor: %s\n\tCopyright: %s\n\tVersion: %s\n\tNew version: %s' % (
            result['__namePackage__'],
            result['__authorPackage__'],
            result['__copyrightPackage__'],
            result['__versionPackage__'],
            result['__versionUpdate__'],
            ),  
            log,True)

        ########################################################################
        usermessage.ezprint('\nThe EZ-InSAR optional modules are:',log,True)
        for li in constants.__EZInSARoptionalmodule__:
                try:    
                    result = miscellaneous.checkmodule(li.split(os.sep)[-1],type='optional')
                    usermessage.ezprint('\n\tName: %s\n\tAuthor: %s\n\tCopyright: %s\n\tVersion: %s\n\tNew version: %s' % (
                    result['__namePackage__'],
                    result['__authorPackage__'],
                    result['__copyrightPackage__'],
                    result['__versionPackage__'],
                    result['__versionUpdate__'],
                    ),   
                    log,True)
                except:
                    a = 'dummy'

        ########################################################################
        if args['--full']:
            if os.path.isfile(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'user.config'):
                usermessage.ezprint('\nPrint the .EZInSARconf: %s' % (os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'user.config'),log,True)
                conffile = []
                with open(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'user.config') as fi:
                    for line in fi.readlines():
                        conffile.append(line.strip())

                # Mask sensible information
                for idx, line in enumerate(conffile):
                    if ('username' in line) or ('password' in line) or ('token' in line):
                        conffile[idx] = '%s::MASKED' % (line.split('::')[0])

                for li in conffile:
                    if li:
                        usermessage.ezprint('\t%s' % (li),log,True)

                ########################################################################
                usermessage.ezprint('\nPrint the processor versions:',log,True) 

                usermessage.ezprint('\n\tFor Doris:',log,True) 
                if os.path.isdir(constants.__requirement_Doris__):
                    output = subprocess.check_output("%s%sdoris -v" % (constants.__requirement_Doris__,os.sep), shell=True).decode('utf-8')
                    usermessage.ezprint('\n\t\t%s' % (output),log,True) 
                else: 
                    usermessage.ezprint('\n\t\tNOT FOUND',log,True) 

                usermessage.ezprint('\n\tFor ISCE-2:',log,True) 
                try: 
                    spec = importlib.util.spec_from_file_location("releases", "%s%sisce%srelease_history.py" % (constants.__requirement_ISCE2__[2],os.sep,os.sep))
                    foo = importlib.util.module_from_spec(spec)
                    sys.modules["releases"] = foo
                    spec.loader.exec_module(foo)
                    usermessage.ezprint('\n\t\t%s %s' % (foo.releases[-1].version,foo.releases[-1].yyyymmdd),log,True) 
                except: 
                    usermessage.ezprint('\n\t\tNOT FOUND',log,True) 

                usermessage.ezprint('\n\tFor MintPy:',log,True) 
                try: 
                    from mintpy import __version__ as __mintpyversion__
                    usermessage.ezprint('\n\t\t%s' % (__mintpyversion__),log,True) 
                except: 
                    usermessage.ezprint('\n\t\tNOT FOUND',log,True) 

                usermessage.ezprint('\n\tFor StaMPS:',log,True) 
                usermessage.ezprint('\n\t\tPlease check the StAMPS directory name',log,True) 

                usermessage.ezprint('\n\tFor LicSBAS:',log,True) 
                usermessage.ezprint('\n\t\tPlease check the Python package list',log,True) 

            else:
                usermessage.ezprint('\nPrint the .EZInSARconf: NOT FOUND',log,True)

        ########################################################################
        if args['--full']:
            usermessage.ezprint('\nPrint the constants of EZ-InSAR:',log,True)   
            for consti in dir(constants):
                if consti.startswith('__') and consti.endswith('__') and (not consti in ['__spec__','__doc__','__builtins__','__loader__']):
                    if not (('username' in consti) or ('password' in consti) or ('token' in consti)):
                        tmp = eval('constants.%s' % consti)
                        usermessage.ezprint('\t%s: %s' % (consti,tmp),log,True)
                    else: 
                        usermessage.ezprint('\t%s: MASKED' % (consti),log,True)

        ########################################################################
        if args['--full']:
            if os.path.isdir(constants.__cachedir__):
                usermessage.ezprint('\nPrint the EZ-InSAR cache: %s Size: %s MB' % (constants.__cachedir__,miscellaneous.get_dir_size(path=constants.__cachedir__)),log,True) 
                for fi in glob.glob(constants.__cachedir__+os.sep+'**', recursive=True):
                    usermessage.ezprint('\t%s' % (fi),log,True)
                    if os.path.isdir(fi):
                        usermessage.ezprint('\t\tDirectory',log,True) 
                    else:
                        usermessage.ezprint('\t\tFile Size: %s MB' % (os.path.getsize(fi)/1e6),log,True) 
            else:
                usermessage.ezprint('\nPrint the EZ-InSAR cache: NOT FOUND',log,True) 

        ########################################################################
        if args['--full']:
            usermessage.ezprint('\nPrint the computer information:',log,True)
            info['Platform']=platform.system()
            info['Platform release']=platform.release()
            info['Platform version']=platform.version()
            info['Architecture']=platform.machine()
            info['Processor']=platform.processor()
            info['Ram']=str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
            info['Python version']=platform.python_version()
            for ki in list(info.keys()):
                usermessage.ezprint('\t%s: %s' % (ki,info[ki]),log,True)

        #######################################################################
        if args['--packages']:
            usermessage.ezprint('\nPrint the installed Python packages (from the conda environment):',log,True)
            result = subprocess.run(
                                'conda list',
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT
                            )
            
            packagelist = result.stdout.decode().strip().split('\n')

            for line in packagelist:
                
                if '# packages in environment at' in line:
                    usermessage.ezprint('\tConda Environment is: %s' % (line.replace('# packages in environment at','').strip()),log,True)
                else:
                    if not line.startswith('#'):
                        usermessage.ezprint('\t\t%s' % (line.split()[0]),log,True)
                        usermessage.ezprint('\t\t\tVersion: %s' % (line.split()[1]),log,True)
                        usermessage.ezprint('\t\t\tBuild: %s' % (line.split()[2]),log,True)
                        usermessage.ezprint('\t\t\tChannel: %s' % (line.split()[3]),log,True)

        ########################################################################
        if args['--env']:
            if args['--debug']:
                if args['--bypassuser']:
                    answer = 'yes'
                else:
                    answer = input("Are you sure to print the environment variables? Some information can be critical for security. ['yes' or 'no'] => ")
            else:
                answer = 'yes'

            if answer.lower() in ["y","yes"]:
                usermessage.ezprint('\nPrint the environment variables:',log,True)
                for ki in os.environ.keys():
                    if ('USERNAME'.lower() in ki.lower()) or ('PASSWORD'.lower() in ki.lower()) or ('TOKEN'.lower() in ki.lower()):
                        usermessage.ezprint('\t%s: %s' % (ki,'MASKED'),log,True)
                    else:
                        usermessage.ezprint('\t%s: %s' % (ki,os.environ[ki]),log,True)
        
        ########################################################################
        if args['--debug']:
            with open(namefile,'r') as fi: 
                lines = fi.readlines()
            newline = []
            for li in lines:
                index = li.find('- INFO -')
                if index != -1:
                    newli = li[index + len('- INFO -'):]
                    newline.append(newli)
                else:
                    newline.append(li)
            with open(namefile,'w') as fi: 
                for line in newline:
                    fi.write('%s' % (line))
                fi.write('\n\nFile generated: %s\n' % (datetime.datetime.now()))
            
            usermessage.ezprint('\nReport saved in %s' % (namefile),None,True) 

    ########################################################################
    ## Create the application shortcuts
    ########################################################################
    elif args['shortcut'] == True:
        cur_dir = os.getcwd() 

        if (not args['--delete'] == True):
            for keyi in list(args.keys()):
                if '--' in keyi:
                    if (args[keyi] == True) and (not args[keyi] == None):
                        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                            'Shortcut needs to be given without options.',None))
            
            usermessage.ezprint('Create the shortcuts for EZ-InSAR',None,True)

            try:
                import ezinsardesktopmodule
                desktop = True
                config = True
            except:
                desktop = False
                config = False

            try:
                import ezinsartsdisplayermodule
                tsdisplayer = True
            except:
                tsdisplayer = False

            try:
                import ezinsardesktopmodule
                desktop = True
            except:
                desktop = False

            try:
                import ezinsardesktopmodule
                docs = True
            except:
                docs = False

            from ezinsar.tools import bundles_app
            if platform.system() == 'Windows':
                bundles_app.bundle_Windows(desktop=desktop,config=config,tsdisplayer=tsdisplayer,docs=docs)
            elif platform.system() == 'Linux':
                bundles_app.bundle_Linux(desktop=desktop,config=config,tsdisplayer=tsdisplayer,docs=docs)
            else:
                bundles_app.bundle_macOS(desktop=desktop,config=config,tsdisplayer=tsdisplayer,docs=docs)

        else:
            usermessage.ezprint('Delete the shortcuts for EZ-InSAR',None,True)

            home_dir = os.path.expanduser("~")

            if platform.system() == 'Windows':
                start_menu_cli = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\EZ-InSAR-CLI")
                start_menu_desktop = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\EZ-InSAR-Desktop")
                start_menu_tsdisplayer = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\EZ-InSAR-TSDisplayer")
                start_menu_config = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\EZ-InSAR-Config")
                if os.path.isdir(start_menu_cli):
                    shutil.rmtree(start_menu_cli)
                if os.path.isdir(start_menu_desktop):
                    shutil.rmtree(start_menu_desktop)
                if os.path.isdir(start_menu_tsdisplayer):
                    shutil.rmtree(start_menu_tsdisplayer)
                if os.path.isdir(start_menu_config):
                    shutil.rmtree(start_menu_config)
            elif platform.system() == 'Linux':
                if os.path.isfile("%s/.local/share/applications/EZ-InSAR-CLI.desktop" % (home_dir)):
                    os.remove("%s/.local/share/applications/EZ-InSAR-CLI.desktop" % (home_dir))
                if os.path.isfile("%s/.local/share/applications/EZ-InSAR-Desktop.desktop" % (home_dir)):
                    os.remove("%s/.local/share/applications/EZ-InSAR-Desktop.desktop" % (home_dir))
                if os.path.isfile("%s/.local/share/applications/EZ-InSAR-TSDisplayer.desktop" % (home_dir)):
                    os.remove("%s/.local/share/applications/EZ-InSAR-TSDisplayer.desktop" % (home_dir))
                if os.path.isfile("%s/.local/share/applications/EZ-InSAR-Config.desktop" % (home_dir)):
                    os.remove("%s/.local/share/applications/EZ-InSAR-Config.desktop" % (home_dir))
            else: 
                if os.path.isdir("%s/Applications/EZ-InSAR" % (home_dir)):
                    shutil.rmtree("%s/Applications/EZ-InSAR" % (home_dir))

        usermessage.ezprint('\tdone.',None,True)

    ########################################################################
    ## Create the EZ-InSAR config file
    ########################################################################
    elif args['configfile'] == True:
        miscellaneous.createdummyEZInSARconf(interactive=(args['--nointeractive']==False))

    ########################################################################
    ## Clear the cache
    ########################################################################
    elif args['cleancache'] == True:
        # listfile = glob.glob(constants.__cachedir__+os.sep+'*')
        # if listfile:
        #     for fi in listfile:
        #         if os.path.isfile(fi):
        #             os.remove(fi)
        #         elif os.path.isdir(fi):
        #             shutil.rmtree(fi)
        #     usermessage.ezprint('Cache cleaned.',None,True)
        # else:
        #     usermessage.ezprint('Cache already empty.',None,True)

        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
            'This feature is not available with the current version.',None))

    ########################################################################
    ## Create the docker image
    ########################################################################
    elif args['docker'] == True:
        usermessage.ezprint('Create the command for the creation of the EZ-InSAR docker image',None,True)
        os.chdir(__file__.replace('%ssrc%sezinsar%scli%sezinsarapp_toolkit.py' % (os.sep,os.sep,os.sep,os.sep),''))
        cmd = 'docker build --platform linux/amd64 -t %s -f docker/dockerfile .' % (args['--dockerimname']) 
        usermessage.ezprint('COMMAND: %s' % (cmd),None,True)
        os.system(cmd)

    ########################################################################
    ## Test the installation of EZ-InSAR
    ########################################################################
    elif args['test'] == True:
        usermessage.openingmsg(__name__,__name__,__file__,__copyright__,'Test the installation of EZ-InSAR',None,True)
        error = None
        idxerror = 0

        # ## Creation of an EZ-InSAR job
        if error == None:
            usermessage.ezprint('Step 1/5: Create an EZ-InSAR job',None,True)
            try:
                import ezinsar.job as ez
                jobtest = ez.EIjob(polarisation=['VV','VH'],verbose=False,log=os.path.abspath('.%sezinsartest.log' % (os.sep)))
                jobtest.workdirectory = os.path.abspath('.%sWKTMPtest' % (os.sep))
                jobtest.pathSLC = os.path.abspath('.%sWKTMPtest%sData_slc' % (os.sep,os.sep))
                jobtest.pathorbit = os.path.abspath('.%sWKTMPtest%sData_orbit' % (os.sep,os.sep))
                jobtest.pathaux = os.path.abspath('.%sWKTMPtest%sData_aux' % (os.sep,os.sep))
                jobtest.pathDEM = os.path.abspath('.%sWKTMPtest%sDEM' % (os.sep,os.sep))
                jobtest.importroi(input=[-6.411048606734975,53.25342126665545,-5.998374676516997,53.442792003200765])
                jobtest.mkdir()

                jobtest.relorbit = 1
                jobtest.satpass = 'ASCENDING'

                jobtest.date1 = datetime.datetime.strptime('2025-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')
                jobtest.date2 = datetime.datetime.strptime('2025-01-31T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')

                usermessage.ezprint('\tSuccess',None,True)
            except Exception as e: 
                error = e 
                idxerror = 1

        ## Retrieve a Sentinel-1 list
        if error == None:
            usermessage.ezprint('Step 2/5: Retrieve (and display) a Sentinel-1 list',None,True)
            try:
                jobtest.initiateSLC(mode='online',verbose=False,server=args['--testSLCserver'])
                jobtest.displaySLClist(verbose = False, basemap = 'World_Imagery', mode = 'Extent', figure = os.path.abspath('.%sWKTMPtest%sfigureSLCtest.jpg' % (os.sep,os.sep)))

                usermessage.ezprint('\tSuccess',None,True)
            except Exception as e: 
                error = e 
                idxerror = 2

        ## Download a DEM
        if error == None:
            usermessage.ezprint('Step 3/5: Download a DEM',None,True)
            try:
                jobtest.nameDEM = 'dem_EZInSAR.wgs84.tif'
                jobtest.typeDEM = 'Copernicus-ell'
                jobtest.downloaddem(verbose=False,bbox='-6.411048606734975,53.25342126665545,-5.998374676516997,53.442792003200765',useSLClist=False)
                
                usermessage.ezprint('\tSuccess',None,True)
            except Exception as e: 
                error = e 
                idxerror = 3

        ## Initialise a ISCE processing job
        if error == None:
            usermessage.ezprint('Step 4/5: Initialise ISCE and MintPy processing jobs',None,True)
            try:
                jobtest.initiatecoreg(processor='isce2')
                jobtest.coregistration.refdate = '2000-01-01'
                jobtest.initiateifg(processor='isce2')
                jobtest.initiatets(processor='mintpy')

                usermessage.ezprint('\tSuccess',None,True)
            except Exception as e: 
                error = e 
                idxerror = 4

        ## Save the job
        if error == None:
            usermessage.ezprint('Step 5/5: Save the job',None,True)
            try:
                ez.save(jobtest,os.path.abspath('.%sWKTMPtest%stestjob.ei' % (os.sep,os.sep)))

                usermessage.ezprint('\tSuccess',None,True)
            except Exception as e: 
                error = e 
                idxerror = 5

        ## Check the desktop module
        try:
            import ezinsardesktopmodule
            desktop = True
        except:
            desktop = False

        if error == None and desktop == True:
            usermessage.ezprint('Step 6/5: Check the desktop module',None,True)

            try:
                from PyQt5.QtWidgets import QApplication
                from PyQt5.QtGui import QIcon
                from PyQt5.QtCore import QTimer, QCoreApplication, Qt
                from ezinsardesktopmodule import __file__ as __root_module__
                
                QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
                __root_module__ = os.path.dirname(__root_module__)
                apptest = QApplication(sys.argv)
                apptest.setWindowIcon(QIcon(__root_module__+os.sep+'images'+os.sep+'EZ_InSAR_logo_desktop_whiteback.svg'))

                ## For the ROI tool
                from ezinsardesktopmodule.roi.roiWidget import roitool
                widgettest = roitool(os.path.abspath('.%sWKTMPtest%stestjob.ei' % (os.sep,os.sep)))
                widgettest.show()
                QTimer.singleShot(5000, apptest.quit)
                apptest.exec_()

                ## For the parameter tool
                from ezinsardesktopmodule.process.processParameterWidget import parameterWidget
                widgettest = parameterWidget(os.path.abspath('.%sWKTMPtest%stestjob.ei' % (os.sep,os.sep)), 'ifgstack')
                widgettest.show()
                QTimer.singleShot(5000, apptest.quit)
                apptest.exec_()

                usermessage.ezprint('\tSuccess',None,True)
            except Exception as e: 
                error = e 
                idxerror = 6
                    
        ## Cleaning 
        if os.path.isdir(os.path.abspath('.%sWKTMPtest' % (os.sep))):
            shutil.rmtree(os.path.abspath('.%sWKTMPtest' % (os.sep)))

        if not error == None:
            raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,
                        'TEST ERROR in Step %s: %s\nPlease see the log %s' % (idxerror,error,(os.path.abspath('.%sezinsartest.log' % (os.sep)))),None))
        else:
            if os.path.isfile(os.path.abspath('.%sezinsartest.log' % (os.sep))):
                os.remove(os.path.abspath('.%sezinsartest.log' % (os.sep)))
            usermessage.ezprint('\nALL steps were successfully performed. It seems that the EZ-InSAR installation is correct and ready.',None,True)

if __name__=='__main__':
    main()