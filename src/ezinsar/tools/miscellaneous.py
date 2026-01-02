#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module for miscellaneous

    
    (From `ezinsar` package)

Changelog:
        * 3.3.0: Several changes have been done, Oct. 2025, Alexis Hrysiewicz 
                * Add the mintpycondaenv variable
        * 3.2.1: Add the function to check the checksum and a download function, Aug. 2025, Alexis Hrysiewicz
        * 3.2.0: New features (license checking, config file generation, etc.), Alexis Hrysiewicz, May 2025
        * 3.1.0: Initial version, March. 2024

"""

################################################################################
## Python packages
################################################################################
import os, requests
from ezinsar import usermessage, constants
import glob, shutil
import datetime
import platform
import importlib
import subprocess
import filecmp
import sys
import hashlib
from urllib.parse import urlsplit
from tqdm import tqdm
import time

################################################################################
def checksum(file,strMD5,verbose=True,log=None):
        """Checksum MD5"""

        if not os.path.isfile(file):
                raise ValueError(usermessage.errormsg(__name__,checksum.__name__,__file__,constants.__copyright__,'The file %s does not exist.' % (file),log))
        
        with open(file, 'rb') as fi:
                databyte = fi.read()    
                md5_file = hashlib.md5(databyte).hexdigest()
        del databyte

        usermessage.ezprint('Hash file: %s' % (md5_file),log,verbose)
        usermessage.ezprint('Hash reference: %s' % (strMD5),log,verbose)

        if not strMD5 == None:
                if md5_file == strMD5:
                        return True 
                else:
                        usermessage.warningmsg(__name__,checksum.__name__,__file__,'The hash is not similar.',log,True)  
                        return False
        else:
                usermessage.warningmsg(__name__,checksum.__name__,__file__,'The referent hash is None, the function will return True (i.e., both values are similar).',log,True)
                return True

def checklicense(asklicense=True):
        """Check the license agreements"""

        licpath = os.path.expanduser("~") + os.sep + '.ezinsar' + os.sep + 'lic'
        if not os.path.isdir(licpath):
                os.makedirs(licpath)
        
        licenses = []
        for mi in ['ezinsar'] + constants.__EZInSARoptionalmodule__: 
                if mi == 'ezinsar':
                        exec('from %s import __file__ as tmpfile' % (mi))
                        tmp = eval('tmpfile').replace('src%s%s%s__init__.py' % (os.sep,mi,os.sep),'LICENSE')
                        tmpbis = eval('tmpfile').replace('src%s%s%s__init__.py' % (os.sep,mi,os.sep),'PYTHONPACKAGES')
                        exec('from %s import __namePackage__ as tmp12' % (mi))
                        exec('from %s import __versionPackage__ as tmp22' % (mi))

                        if os.path.isfile(licpath+os.sep+'LICENSE_%s_signed' % (mi)):
                                valid = True
                        else:
                                valid = False

                        res = {'Name': eval('tmp12'),
                                'key': mi,
                                'version': eval('tmp22'),
                                'licensefile': tmp,
                                'licensevalidatedfile': licpath+os.sep+'LICENSE_%s_signed' % (mi),
                                'licensevalidated': valid,
                                'PYTHONPACKAGES': tmpbis,
                                'processor': True,
                                }
                        
                        licenses.append(res)
                        
                else:
                        try: 
                                if mi.lower() == 'gamma':
                                        if not os.environ['ezinsargamma'] in ['True','true',True,1]:
                                                raise ValueError('ERROR')
                                if  mi in constants.__EZInSARoptionalmoduleProcessor__:
                                        processor = True
                                else:
                                        processor = False
                                exec('from ezinsar%smodule import __file__ as tmpfile' % (mi))
                                tmp = eval('tmpfile').replace('src%sezinsar%smodule%s__init__.py' % (os.sep,mi,os.sep),'LICENSE')
                                tmpbis = eval('tmpfile').replace('src%sezinsar%smodule%s__init__.py' % (os.sep,mi,os.sep),'PYTHONPACKAGES')
                                exec('from ezinsar%smodule import __namePackage__ as tmp12' % (mi))
                                exec('from ezinsar%smodule import __versionPackage__ as tmp22' % (mi))

                                if os.path.isfile(licpath+os.sep+'LICENSE_ezinsar%smodule_signed' % (mi)):
                                        valid = True
                                else:
                                        valid = False

                                res = {'Name': eval('tmp12'),
                                        'key': mi,
                                        'version': eval('tmp22'),
                                        'licensefile': tmp,
                                        'PYTHONPACKAGES': tmpbis,
                                        'licensevalidatedfile': licpath+os.sep+'LICENSE_ezinsar%smodule_signed' % (mi),
                                        'licensevalidated': valid,
                                        'processor': processor,
                                        }
                                
                                licenses.append(res)
                        except:
                                a = 'dummy'

        for li in licenses:
                if not li['licensevalidated']:
                        if asklicense == True:
                                usermessage.ezprint('Please, accept the license terms for %s (and software used).' % (li['Name']),None,True)

                                with open(li['licensefile'],'r') as fi:
                                        h = 0
                                        for line in fi.readlines():
                                                if h < 15:   
                                                        print(line)
                                                        h = h + 1
                                                else:
                                                        h = 0
                                                        anwser = input(line)

                                with open(li['PYTHONPACKAGES'],'r') as fi:
                                        h = 0
                                        for line in fi.readlines():
                                                if h < 15:   
                                                        print(line)
                                                        h = h + 1
                                                else:
                                                        h = 0
                                                        anwser = input(line)   
                                anwser = 'no'
                                while not anwser in ['y','yes']:
                                        anwser = input('Please, accept the license terms for %s, version %s => "y", "yes":   ' % (li['Name'],li['version']))
                                shutil.copy(li['licensefile'],li['licensevalidatedfile'])

                        else:
                                shutil.copy(li['licensefile'],li['licensevalidatedfile'])
        
        return licenses

def writexmlfromdict(dictvalue, 
                     file,
                     rootname = 'EZ-InSAR-Job',
                     indent = '\t',
                     commented = True,
                     version = '1.0.0',
                     verbose = False,
                     log = None):
        """Write an EZ-InSAR job, converted to dict, in a .xml file

        The function writes an EZ-InSAR job, converted to dict, in a .xml file

        Args:
                dictvalue (dict): EZ-InSAR job in dict format
                file (str): file 
                rootname (str): Root name of the .xml file. [Default: EZ-InSAR-Job]
                indent (str): Indent symbol [Default: \t]
                commented (bool): Add comments: i.e., version, date of creation, date of updating. [Default: True]
                version (str): Version [Default: 1.0.0]
                verbose (bool): Verbose [Default: True]
                log (str): log [Default: None]

        """
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,writexmlfromdict.__name__,__file__,constants.__copyright__,
                        'verbose',"bool",log))
        
        if not isinstance(dictvalue,dict):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,writexmlfromdict.__name__,__file__,constants.__copyright__,
                        'dictvalue',"'dict'",log))
        
        if not isinstance(file,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,writexmlfromdict.__name__,__file__,constants.__copyright__,
                        'file',"'str'",log))
        
        if not isinstance(rootname,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,writexmlfromdict.__name__,__file__,constants.__copyright__,
                        'rootname',"'str'",log))
        
        if not isinstance(indent,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,writexmlfromdict.__name__,__file__,constants.__copyright__,
                        'indent',"'str'",log))
        
        if not isinstance(commented,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,writexmlfromdict.__name__,__file__,constants.__copyright__,
                        'commented',"'bool'",log))
        
        def parselinexml(key,value,h,indent):
                
                if 'numpy' in str(type(value)):
                        value = list(value)

                if isinstance(value,list):
                        xmltmp = indent*h + '<%s type="list">\n' % (key)
                        for keyi in value:
                                xmltmp = xmltmp + parselinexml('item',keyi,h+1,indent)
                        xmltmp = xmltmp + indent*h + '</%s>\n' % (key)
                elif value == None:
                        xmltmp = indent*h + '<%s type="null"/>\n' % (key)
                elif isinstance(value,bool):
                        xmltmp = indent*h + '<%s type="bool">%s</%s>\n' % (key,str(value).lower(),key)
                elif isinstance(value,str):
                        xmltmp = indent*h + '<%s type="str">%s</%s>\n' % (key,value,key)
                elif isinstance(value,int):
                        xmltmp = indent*h + '<%s type="int">%s</%s>\n' % (key,value,key)
                elif isinstance(value,float):
                        xmltmp = indent*h + '<%s type="float">%s</%s>\n' % (key,value,key)
                elif isinstance(value,dict):
                        xmltmp = indent*h + '<%s type="dict">\n' % (key)
                        for keydict in list(value.keys()):
                                xmltmp = xmltmp + parselinexml(keydict,value[keydict],h+1,indent)
                        xmltmp = xmltmp + indent*h + '</%s>\n' % (key)
                elif isinstance(value,datetime.datetime):
                        xmltmp = indent*h + '<%s type="str">%s</%s>\n' % (key,value.strftime('%Y-%m-%dT%H:%M:%S'),key)
                return xmltmp 
        
        ## Add the comments
        xml = ''
        xml = xml + '<?xml version="1.0" ?>\n'

        if commented:
                xml = xml + '<!-- %s -->\n' % ('EZ-InSAR job xml file in version %s created by EZ-InSAR version %s' % (version,constants.__version__))
                if not os.path.isfile(file):
                        xml = xml + '<!-- %s -->\n' % ('Created: %s' % (datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')))
                else:
                        with open(file, "r") as fi:
                                datecreation = fi.readlines()[2]
                        if 'Created' in datecreation:
                                xml = xml + '%s' % (datecreation)
                xml = xml + '<!-- %s -->\n' % ('Updated: %s' % (datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')))

        ## Create the string
        xml = xml + "<%s>\n" % (rootname)
        h = 1 
        for key in list(dictvalue.keys()):
                xml = xml + parselinexml(key,dictvalue[key],h,indent)                
        xml = xml + "</%s>\n" % (rootname)

        usermessage.ezprint(xml,log,verbose)

        # Write 
        with open(file.replace('.ei','')+'.ei','w') as f_out:
                f_out.write(xml)

def get_dir_size(path='.'):
        """Compute the size of a directory. 

        The function compute the size of a directory. 

        Note: 
                The log paramater will be extracted from the job. 

        Args:
                path (str): Path

        Returns:
                float: size in MB
        """

        total = 0
        if os.path.isdir(path):
                with os.scandir(path) as it:
                        for entry in it:
                                if entry.is_file():
                                        total += entry.stat().st_size
                                elif entry.is_dir():
                                        total += get_dir_size(entry.path)
        elif os.path.isfile(path):
                total = os.path.getsize(path)/1e6

        return total/1e6

def checkmodule(modulename,type='core',checkupdate=True):
        """Check modules of EZ-InSAR

        The function will check modules of EZ-InSAR (i.e., version, copyrights, etc.)  

        Args:
                modulename (str): Name/Prefix of the EZ-InSAR module
                type (Optional, str): Type of the module. Can be core, sensor, processor, optional. [Default: core].    
        """
        if modulename.lower() == 'gamma':
                if not os.environ['ezinsargamma'] in ['True','true',True,1]:
                        raise ValueError('ERROR')
                
        if not type in ['core','processor','sensor','optional']:
                raise ValueError(usermessage.errormsg(__name__,checkmodule.__name__,__file__,constants.__copyright__,
                                'The type argument is not correct.',None))

        ## Check if the release is public or private 
        if os.path.isfile(__file__.replace('src%sezinsar%stools%smiscellaneous.py' % (os.sep,os.sep,os.sep),'RELEASE')):
                public = True
                release = 'unknown'
                publicmodule = []
                with open(__file__.replace('src%sezinsar%stools%smiscellaneous.py' % (os.sep,os.sep,os.sep),'RELEASE'),'r') as fi: 
                        for lines in fi.readlines(): 
                                if 'Release:' in lines:
                                        release = lines.strip().split(':')[-1].strip()
                                if 'EZ-InSAR-Module' in lines:
                                        publicmodule.append(lines.strip().split('version:')[0].strip().split('-')[-1].lower())
        else: 
                public = False
                release = 'unknown'
                publicmodule = []
        
        ## Check the installed versions 
        result = {}
        for vi in ['__namePackage__',
                        '__authorPackage__',
                        '__copyrightPackage__',
                        '__versionPackage__',
                        ]:

                if type == 'core':
                        result[vi] = eval("importlib.import_module('%s').%s" % (modulename,vi))
                elif type == 'sensor':
                       result[vi] = eval("importlib.import_module('ezinsar.eicomponents.sensor.%s').%s" % (modulename,vi))
                elif type == 'processor':
                        result[vi] = eval("importlib.import_module('ezinsar.eicomponents.processor.%s').%s" % (modulename,vi))
                elif type == 'optional':
                        result[vi] = eval("importlib.import_module('ezinsar%smodule').%s" % (modulename,vi))

        if type in ['core','sensor','processor']:
                if public:
                        result['__versionPackage__'] = result['__versionPackage__'] + ' / Public Release: %s' % (release)
                else: 
                        result['__versionPackage__'] = result['__versionPackage__'] + ' / Developer Mode'
        else: 
                if public:
                        if modulename in publicmodule: 
                                result['__versionPackage__'] = result['__versionPackage__'] + ' / Public Release: %s' % (release)
                        else: 
                                result['__versionPackage__'] = result['__versionPackage__'] + ' / Developer Mode'
                else: 
                        result['__versionPackage__'] = result['__versionPackage__'] + ' / Developer Mode'

        ## Check the online availability (i.e., new version or new release)
        if checkupdate: 
                if (type in ['core','sensor','processor']) or (modulename in publicmodule):
                        if public:
                                regularcheck = False
                                currentrelease = datetime.datetime.strptime(release,'%b-%Y.%d')
                                listrelease =[]
                                a = subprocess.check_output('git ls-remote --heads https://github.com/alexisInSAR/EZ-InSAR/', shell=True).strip().decode("utf-8").split('\n')
                                for li in a: 
                                        try:
                                                relstr = li.split('\t')[-1].replace('refs/heads/','')
                                                listrelease.append(datetime.datetime.strptime(relstr,'%b-%Y.%d'))
                                        except:
                                                a = 'dummy'
                                        
                                listrelease = sorted(listrelease)
                                result['__versionUpdate__'] = 'up-to-date'
                                for li in listrelease: 
                                        if li > currentrelease: 
                                                result['__versionUpdate__'] = 'New release - %s' % (li.strftime('%b-%Y.%-d'))

                        else: 
                                regularcheck = True
                else: 
                        regularcheck = True
                                
                if regularcheck: 
                        if type == 'core':
                                a = eval("importlib.import_module('%s').__file__" % (modulename))
                        elif type == 'sensor':
                                a = eval("importlib.import_module('ezinsar.eicomponents.sensor.%s').__file__" % (modulename))
                        elif type == 'processor':
                                a = eval("importlib.import_module('ezinsar.eicomponents.processor.%s').__file__" % (modulename))
                        elif type == 'optional':
                                a = eval("importlib.import_module('ezinsar%smodule').__file__" % (modulename))
                                if modulename.lower() == 'gamma':
                                        if not os.environ['ezinsargamma'] in ['True','true',True,1]:
                                                raise ValueError('ERROR')
                        if type in ['core','optional']:
                                pathmodule = os.path.dirname(os.path.dirname(os.path.dirname(a)))
                        else: 
                                pathmodule = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(a))))))
                        
                        curdir = os.getcwd()
                        os.chdir(pathmodule)
                        gitrepo = subprocess.check_output('git remote -v',shell=True).strip().decode("utf-8").split('\n')[0].split('\t')[-1].split(' ')[0].split('/')[-1].replace('.git','')
                        os.chdir(curdir)

                        template = 'https://raw.githubusercontent.com/alexisInSAR/%s/refs/heads/main/src/ezinsar/' % (gitrepo)
                        
                        if type == 'core':
                               url = template+'__init__.py'
                        elif type == 'sensor':
                               url = template+'eicomponents/sensor/%s/__init__.py' % (modulename)
                        elif type == 'processor':
                               url = template+'eicomponents/processor/%s/__init__.py' % (modulename)
                        elif type == 'optional':
                                if modulename.lower() in ['multispectral','desktop','webapp','server']:
                                        modulename = modulename.capitalize()
                                else:
                                        modulename = modulename.upper()
                                url = 'https://raw.githubusercontent.com/alexisInSAR/%s/refs/heads/main/src/ezinsar%smodule/__init__.py' % (gitrepo,modulename.lower())

                        result['__versionUpdate__'] = 'unknown'
                        for li in requests.get(url).text.split('\n'): 
                                if 'versionPackage' in li: 
                                        result['__versionUpdate__'] = eval('%s' % (li.split('=')[-1]))

                        if result['__versionUpdate__'] == 'unknown':
                                if os.path.isfile(os.path.expanduser("~")+os.sep+'.my-credentials'):
                                        checktoken = os.path.expanduser("~")+os.sep+'.my-credentials'
                                elif os.path.isfile(os.path.expanduser("~")+os.sep+'.git-credentials'):
                                        checktoken = os.path.expanduser("~")+os.sep+'.git-credentials'
                                else: 
                                        checktoken = None

                                if not checktoken == None:
                                        with open(checktoken,'r') as fi: 
                                                lines = fi.readlines()[0]
                                        access_token = lines.split(':')[-1].split('@')[0]
                                
                                        headers = {"Authorization": f"Bearer {access_token}"}
                                        for li in requests.get(url,headers=headers).text.split('\n'): 
                                                if 'versionPackage' in li: 
                                                        result['__versionUpdate__'] = eval('%s' % (li.split('=')[-1]))
                                                        break

                        if not result['__versionUpdate__'] == 'unknown': 
                                if result['__versionUpdate__'] == result['__versionPackage__'].split(':')[-1].strip().split('/')[0].strip(): 
                                        result['__versionUpdate__'] = 'up-to-date'

        else: 
                result['__versionUpdate__'] = 'unknown'

        return result   

def listmodule(type):
        """List modules of EZ-InSAR

        The function will list modules of EZ-InSAR  

        Args:
                type (str): Type of the module. Can be core, sensor, processor.    
        """
        list = []
        if type == 'sensor':
                from ezinsar.eicomponents import sensor
                for li in glob.glob(sensor.__file__.replace('__init__.py','*')):
                        if os.path.isdir(li):
                                if not '__pycache__' in li:
                                        list.append(li.split(os.sep)[-1])
        elif type == 'processor':
                from ezinsar.eicomponents import processor
                for li in glob.glob(processor.__file__.replace('__init__.py','*')):
                        if os.path.isdir(li):
                                if not '__pycache__' in li:
                                        list.append(li.split(os.sep)[-1])
        
        return list

def forceossep(path):
        return path.replace('/',os.sep).replace('\\',os.sep)

def updatemodule(modulename):
        """Update modules of EZ-InSAR

        The function will update modules of EZ-InSAR.  

        Args:
                modulename (str): Name/Prefix of the EZ-InSAR module
                type (Optional, str): Type of the module. Can be core, sensor, processor, optional. [Default: core].    
        """
        if modulename == 'ezinsar':
                type = 'core'
        elif modulename in listmodule('sensor'):
                type = 'sensor'
        elif modulename in listmodule('processor'):
                type = 'processor'
        else:
                type = 'optional'   

        moduleinfo = checkmodule(modulename,type=type,checkupdate=True)

        usermessage.ezprint('Update the module %s' % (modulename),None,True)

        if moduleinfo['__versionUpdate__'] == 'up-to-date':
                usermessage.ezprint('\tThe module is up-to-date. No update required.\nSTOP HERE',None,True)
        else:
                if 'Developer Mode' in moduleinfo['__versionPackage__']:
                        usermessage.ezprint('\tThe module has been installed from the private repo. The update functionality is locked for such repository. Please use git.\nSTOP HERE',None,True)
                else:
                        if not modulename == 'ezinsar':
                                usermessage.ezprint('\tThe module has been/will be updated with the core of EZ-InSAR.\nSTOP HERE',None,True)  
                        else:
                                usermessage.ezprint('\tStart the update...',None,True)  
                                newrelease = moduleinfo['__versionUpdate__'].split(' - ')[-1].strip()
                                usermessage.ezprint('\tNew release: %s' % (newrelease),None,True)  

                                pathcurrent = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

                                usermessage.ezprint('\tPath of the current installation: %s' % (pathcurrent),None,True)  

                                pathnew = constants.__cachedir__+os.sep+'tmpupdate'                                
                                # os.system("git clone https://github.com/alexisInSAR/EZ-InSAR-Private/ -b %s %s" % (newrelease,pathnew+os.sep+'EZ-InSAR'))

                                ## Detect the new modules 
                                # listoptmodule = [x.split(os.sep)[-1] for x in glob.glob(pathnew + os.sep+ 'EZ-InSAR' + os.sep + 'modules' + os.sep + 'EZ-InSAR-Module*')]
                                # for mi in listoptmodule: 
                                #         os.rename(pathnew + os.sep+ 'EZ-InSAR' + os.sep + 'modules' + os.sep + mi,
                                #                 pathnew+os.sep+mi)  

                                listoptmodule = ['EZ-InSAR'] + ['EZ-InSAR-Module-TSDisplayer','EZ-InSAR-Module-Multispectral'] #listoptmodule

                                for module in listoptmodule: 
                                        listcopyfile = []
                                        listdelfile = []

                                        usermessage.ezprint('\tUpdate %s' % (module),None,True) 
                                        filenew = glob.glob(pathnew+'%s%s%s**%s*' % (os.sep,module,os.sep,os.sep) , recursive=True)
                                        for filei in filenew:
                                                if not os.path.isdir(filei):
                                                        if os.path.isfile(filei.replace(pathnew,pathcurrent)): 
                                                                if not filecmp.cmp(filei,filei.replace(pathnew,pathcurrent),shallow=False): 
                                                                        listcopyfile.append(
                                                                                (filei,
                                                                                filei.replace(pathnew,pathcurrent)))    
                                                        else: 
                                                                listcopyfile.append(
                                                                        (filei,
                                                                        filei.replace(pathnew,pathcurrent)))        

                                        fileold = glob.glob(pathcurrent+'%s%s%s**%s*' % (os.sep,module,os.sep,os.sep), recursive=True)
                                        for filei in fileold:
                                                if not os.path.isdir(filei):
                                                        if not os.path.isfile(filei.replace(pathcurrent,pathnew)): 
                                                                listdelfile.append(filei)     

                                        # Copy the file 
                                        for couplei in listcopyfile: 
                                                usermessage.ezprint('\t\tCopy %s\n\t\t\t--> %s' % (couplei[0],couplei[1]),None,True) 
                                                #COpy function

                                        # Delete the file 
                                        for filei in listdelfile: 
                                                usermessage.ezprint('\t\tDelete %s' % (filei),None,True) 
                                                #Delete function

                                        usermessage.ezprint('\t\tDone',None,True)
                                        
                        sys.exit('Exit for update')

def createdummyEZInSARconf(interactive=True):
        """Create a EZInSAR configuration file
        """

        def affectdefault(anwser,defaultvalue):
                if anwser == '':
                        value = defaultvalue
                else:
                        value = anwser
                return value
        
        # from pathlib import Path
        # def find_file(filename, search_path):
        #         search_path = Path(search_path)
        #         return [str(p) for p in search_path.rglob(filename)]

        usermessage.ezprint('Create the EZInSARconf file',None,True)

        if interactive == True: 
                conf_username = affectdefault(input('\tUsername [default: %s]: ' % (constants.__username__)),constants.__username__)
                conf_password = affectdefault(input('\tPassword [default: %s]: ' % (constants.__password__)),constants.__password__)
                conf_tokenM2M = affectdefault(input('\tToken M2M [default: none]: '),'none')
                conf_cache = forceossep(affectdefault(input('\tEZ-InSAR cache directory [default: %s]: ' % (constants.__cachedir__)),constants.__cachedir__))
  
                conf_pathserverdatabase = os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'server.config'

                conf_pathisce2 = forceossep(affectdefault(input('\tPath of ISCE-2 [default: %s]: ' % (constants.__requirement_ISCE2__[0].replace(os.sep+'install',''))),constants.__requirement_ISCE2__[0].replace(os.sep+'install','')))
                
                conf_pathsnappy = forceossep(affectdefault(input('\tPath of SNAPPY [default: %s]: ' % (constants.__requirement_SNAP__)),constants.__requirement_SNAP__))
                conf_pathsnapgpt = forceossep(affectdefault(input('\tPath of SNAP-GPT [default: %s]: ' % (constants.__requirement_SNAP_GPT__)),constants.__requirement_SNAP_GPT__))
                
                conf_pathdoris = forceossep(affectdefault(input('\tPath of Doris [default: %s]: ' % (constants.__requirement_Doris__)),constants.__requirement_Doris__))
                
                conf_pathstamps = forceossep(affectdefault(input('\tPath of StamPS [default: %s]: ' % (constants.__requirement_StaMPS__[0].replace(os.sep+'bin',''))),constants.__requirement_StaMPS__[0].replace(os.sep+'bin','')))
                
                conf_pathlicsbas = forceossep(affectdefault(input('\tPath of LicSBAS [default: %s]: ' % (constants.__requirement_LiCSBAS__.split(':')[0].replace(os.sep+'LiCSBAS'+os.sep +'bin',''))),constants.__requirement_LiCSBAS__.split(':')[0].replace(os.sep+'LiCSBAS'+os.sep +'bin','')))
                

                conf_pathserverdatabase = forceossep(conf_pathserverdatabase)

                conf_ISCE2modesymlink  = 'dummy'
                while not conf_ISCE2modesymlink in ['True','False']:
                        conf_ISCE2modesymlink = affectdefault(input('\tISCE-2 Mode Symlink [default: %s]: ' % (constants.__ISCE2_modesymlink__)),'%s' % (constants.__ISCE2_modesymlink__))
                conf_ISCE2modesymlink = (conf_ISCE2modesymlink=='True')

                conf_SNAPcachemax  = 'dummy'
                while not isinstance(conf_SNAPcachemax,int):
                        try: 
                                conf_SNAPcachemax = int(affectdefault(input('\tMax. Cache for SNAP [default: %s]: ' % (constants.__SNAPcachemax__)),'%s' % (constants.__SNAPcachemax__)))
                        except: 
                                conf_SNAPcachemax = 'dummy'
                                usermessage.ezprint('\t\tA integer is required.',None,True)

                conf_SNAPcacheclean = True
                conf_SNAPwrapper = 'gpt'

                conf_defautprocessor  = 'dummy'
                while not conf_defautprocessor in ['gamma','doris','isce2','snap']:
                        conf_defautprocessor = affectdefault(input('\tDefault SAR/InSAR processor [default: %s]: ' % (constants.__defautprocessor__)),constants.__defautprocessor__)

                conf_S1server  = 'Copernicus'
                while not conf_S1server in ['Copernicus','ASF']:
                        conf_S1server = affectdefault(input('\tDefault Sentinel-1 server [default: %s]: ' % (constants.__S1server__)),constants.__S1server__)

        else: 
                conf_username = constants.__username__
                conf_password = constants.__password__
                conf_tokenM2M = 'none'
                conf_cache = forceossep(os.path.expanduser("~") + os.sep + '.ezinsar' + os.sep + 'cache')
                conf_pathisce2 = constants.__requirement_ISCE2__[0].replace(os.sep+'install','')
                conf_pathsnappy = constants.__requirement_SNAP__
                conf_pathsnapgpt = constants.__requirement_SNAP_GPT__
                conf_pathdoris = constants.__requirement_Doris__
                conf_pathstamps = constants.__requirement_StaMPS__[0].replace(os.sep+'bin','')
                conf_pathlicsbas = constants.__requirement_LiCSBAS__.split(':')[0].replace(os.sep+'LiCSBAS'+os.sep +'bin','')

                conf_pathserverdatabase = forceossep(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'server.config')
                conf_ISCE2modesymlink = constants.__ISCE2_modesymlink__
                conf_SNAPcachemax = constants.__SNAPcachemax__
                conf_SNAPcacheclean = True
                conf_SNAPwrapper = 'gpt'
                conf_defautprocessor = constants.__defautprocessor__
                conf_S1server = constants.__S1server__

        conf_loggingmode = 'INFO'
        conf_nameDockerImage = 'ezinsar'
        conf_mintpycondaenv = 'default'
        conf_isce2condaenv = 'default'
        conf_licsbascondaenv = 'default'
        conf_miaplpycondaenv = 'default'
        conf_sarveycondaenv = 'default'
        conf_wgetlimit = 'auto'
        conf_wgetlimitmin = '12.5m'
        conf_wgetlimitmax = '50.0m'
        conf_chunksize = 8192
        conf_SLCdownloader = 'python'
        conf_sleepSLCdownload = 2

        textstr = ''

        for parai in ['username',
                'password',
                'tokenM2M',
                'cache',
                'pathisce2',
                'pathsnappy',
                'pathsnapgpt',
                'pathdoris',
                'pathstamps',
                'pathlicsbas',
                'pathserverdatabase',
                'ISCE2modesymlink',
                'SNAPcachemax',
                'SNAPcacheclean',
                'SNAPwrapper',
                'defautprocessor',
                'S1server',
                'loggingmode',
                'nameDockerImage',
                'mintpycondaenv',
                'isce2condaenv',
                'licsbascondaenv',
                'miaplpycondaenv',
                'sarveycondaenv',
                'wgetlimit',
                'wgetlimitmin',
                'wgetlimitmax',
                'chunksize',
                'SLCdownloader',
                'sleepSLCdownload']:
                
                textstr = textstr + '%s::%s\n' % (parai,eval('conf_%s' % (parai)))
        
        usermessage.ezprint('\nConfiguration file:\n',None,True)
        usermessage.ezprint(textstr,None,True)

        with open(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'user.config','w') as fout:
                fout.write(textstr)
        usermessage.ezprint('\nFile saved in %s' % (os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'user.config'),None,True)

def download_file(url, 
        username = None,
        password = None,
        output_file=None,
        retries=10,
        verbose=True,
        log=None):
        """Download function
        """

        if output_file == None:
                filename = os.path.basename(urlsplit(url).path)
                if not filename:
                        raise ValueError(usermessage.errormsg(__name__,download_file.__name__,__file__,constants.__copyright__,'Cannot determine filename from URL. Please provide output_file.',log))        
        else:
                filename = output_file

        attempt = 0
        while attempt < retries:
                existing_size = 0
                if os.path.exists(filename):
                        existing_size = os.path.getsize(filename)

                headers = {
                        'Range': f'bytes={existing_size}-'
                }
                try:
                        usermessage.ezprint('EZ-InSAR - Downloader - Starting download from: %s' % (url),log,verbose)

                        if password == None:
                                response = requests.get(url, headers=headers, stream=True, allow_redirects=True, timeout= (5, 5))
                        else:
                                response = requests.get(url, headers=headers, auth=(username, password), stream=True, allow_redirects=True, timeout= (5, 5))

                        if response.status_code == 416:
                                usermessage.ezprint('EZ-InSAR - Downloader - Download already done.',log,verbose)
                
                        response.raise_for_status() 

                        content_range = response.headers.get('Content-Range')
                        if content_range:
                                total_size = int(content_range.split('/')[-1])
                        else:
                                content_length = response.headers.get('Content-Length')
                                total_size = int(content_length) + existing_size if content_length else None

                        mode = 'ab' if existing_size > 0 else 'wb'

                        with open(filename, mode) as f:
                                if verbose:
                                        with tqdm(
                                                total=total_size,
                                                unit='B',
                                                unit_scale=True,
                                                unit_divisor=1024,
                                                desc=filename,
                                                initial=existing_size,
                                                ascii=True,
                                                dynamic_ncols=True,
                                                mininterval=0.1,
                                                disable=total_size is None,
                                                ) as progress_bar:
                                                        for chunk in response.iter_content(chunk_size=constants.__chunksize__):
                                                                if chunk:
                                                                        f.write(chunk)
                                                                        progress_bar.update(len(chunk)) 
                                else:
                                        with open(filename, 'wb') as f:
                                                for chunk in response.iter_content(chunk_size=constants.__chunksize__):
                                                        if chunk:
                                                                f.write(chunk)

                        usermessage.ezprint('EZ-InSAR - Downloader ls- Download complete',log,verbose)
                        return
                
                except requests.exceptions.ReadTimeout as errt:
                        attempt += 1
                        usermessage.ezprint(f"Read timeout on attempt {attempt}/{retries}. Retrying...",log,verbose)
                        time.sleep(1)
                except requests.exceptions.HTTPError as errh:
                        raise ValueError(usermessage.errormsg(__name__,download_file.__name__,__file__,constants.__copyright__,'EZ-InSAR - Downloader - HTTP Error: %s' % (errh),log)) 
                except requests.exceptions.ConnectionError as errc:
                        # raise ValueError(usermessage.errormsg(__name__,download_file.__name__,__file__,constants.__copyright__,'EZ-InSAR - Downloader - Connection Error: %s' % (errc),log)) 
                        attempt += 1
                        usermessage.ezprint(f"Read timeout on attempt {attempt}/{retries}. Retrying...",log,verbose)
                        time.sleep(1)
                except requests.exceptions.Timeout as errt:
                        raise ValueError(usermessage.errormsg(__name__,download_file.__name__,__file__,constants.__copyright__,'EZ-InSAR - Downloader - Timeout Error: %s' % (errt),log)) 
                except requests.exceptions.RequestException as err:
                        raise ValueError(usermessage.errormsg(__name__,download_file.__name__,__file__,constants.__copyright__,'EZ-InSAR - Downloader - Other Error: %s' % (err),log))
                



