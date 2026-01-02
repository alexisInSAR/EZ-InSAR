#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to add some tool functions for Doris processor

The module allows to add some sub-functions for Doris processor.
    
    (From `ezinsar` package)

Note: 
        Each function can directly used in Python scripts or/and a Python terminal

Changelog:
        * 1.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import os
from typing import Optional, Union
import glob
import shutil
import subprocess
import multiprocessing
import numpy as np

from ezinsar import usermessage
from ezinsar import constants
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Flatten a seq
################################################################################
def flattenseq(seq):
        """Create a flatten list for a sequence

        The function creates a flatten list from a sequence.

        Args:
                seq (any): log file from the job
        
        Returns:
                (list): cornefrefdict

        """
        l = []
        for elt in seq:
                t = type(elt)
                if t is tuple or t is list:
                        for elt2 in flattenseq(elt):
                                l.append(elt2)
                else:
                        l.append(elt)
        return l

################################################################################
## Check the parameters of a dict
################################################################################
def checkdorisparafromdict(paradict,jobcoreg,verbose):
        """Check the parameters of a dict for an ``ezinsar`` job using Doris

        The function checks the parameters of a dict for an ``ezinsar.coregistration`` or ``ezinsar.ifgstack`` with the Doris processor.

        Args:
                paradict (dict): parameter
                jobcoreg (``ezinsar.job``): EZ-InSAR job for Doris processor
                verbose (bool): verbose. 

        Returns:
                ``ezinsar.job`` job: Return an EZ-InSAR processing job class
        
        """

        try: 
                namestep = paradict['name']['value']
        except:
                namestep = 'Email information'

        usermessage.ezprint('\tCheck the %s:' % (namestep),jobcoreg.log,verbose)

        listpara = list(paradict.keys())
        modepara = []
        for parai in listpara:
               modepara.append(paradict[parai]['format'])
        valuelist = []
        for parai in listpara:
               valuelist.append(paradict[parai]['valuelist']) 
        valuepara = []
        for parai in listpara:
               valuepara.append(paradict[parai]['value']) 

        infopara = {'listpara':     listpara,
                'modepara':     modepara,
                'valuelist':    valuelist,
                'valuepara':    valuepara}
        
        for idx, namepara in enumerate(infopara['listpara']): 

                if paradict[namepara]['format'] == 'list': 
                        exttext='\n\t\t\t<Format: %s>\n\t\t\t<Possible values: %s>' % ('predefined',paradict[namepara]['valuelist'])
                else: 
                        exttext = '\n\t\t\t<Format: %s>' % (paradict[namepara]['format']) 

                usermessage.ezprint('\t\t%s: %s\n\t\t\t<Description: %s>%s' % (namepara,paradict[namepara]['value'],paradict[namepara]['description'],exttext),jobcoreg.log,verbose)

                if infopara['modepara'][idx] == 'bool':
                        if not isinstance(paradict[namepara]['value'],bool):
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkdorisparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'True or False',jobcoreg.log))

                elif infopara['modepara'][idx] == 'list':
                        if not paradict[namepara]['value'] in infopara['valuelist'][idx]: 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkdorisparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'%s' % (infopara['valuelist'][idx]),jobcoreg.log))
                        
                elif infopara['modepara'][idx] == 'email':
                        if not isinstance(paradict[namepara]['value'],str): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkdorisparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'str',jobcoreg.log))
                        
                elif infopara['modepara'][idx] == 'int':
                        if not isinstance(paradict[namepara]['value'],int): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkdorisparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'int',jobcoreg.log))

                elif infopara['modepara'][idx] == 'int-':
                        if isinstance(paradict[namepara]['value'],str): 
                                if not paradict[namepara]['value'] == '-': 
                                        raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkdorisparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),"int or '-'",jobcoreg.log))
                        else: 
                                if not isinstance(paradict[namepara]['value'],int): 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,checkdorisparafromdict.__name__,__file__,__copyright__,
                                                "parameter %s in %s" % (namepara,namestep),"int or '-'",jobcoreg.log))

                elif infopara['modepara'][idx] == 'float':
                        if not isinstance(paradict[namepara]['value'],float): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkdorisparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'float',jobcoreg.log))
                        
                elif infopara['modepara'][idx] == 'float-':
                        if isinstance(paradict[namepara]['value'],str): 
                                if not paradict[namepara]['value'] == '-': 
                                        raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkdorisparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),"float or '-'",jobcoreg.log))
                        else: 
                                if not isinstance(paradict[namepara]['value'],float): 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,checkdorisparafromdict.__name__,__file__,__copyright__,
                                                "parameter %s in %s" % (namepara,namestep),"float or '-'",jobcoreg.log))
                        
                elif infopara['modepara'][idx] == 'pathuser':
                        check_error = False
                        if not paradict[namepara]['value'] == None: 
                                if not paradict[namepara]['value'] == 'user': 
                                        check_error = True
                                else: 
                                        if not os.path.isfile(paradict[namepara]['value']):
                                                check_error = True
                        if check_error: 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checkdorisparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),"None, user or a file",jobcoreg.log))

        return jobcoreg

################################################################################
## Read the image parameter from a .res file
################################################################################
def readimagepara(path_info,mode='slc'):
        """Read the image parameter from a .res file

        The function reads the image parameter from a .res file

        Args:
                path_info (str): Path of the .res file
                mode (str, Optional): Type of the .res file. Can be ``slc`` or ``ifg`` or ``coh``

        Returns:
                paraimage (dict)
        
        """

        paraimage = dict()

        if mode == 'slc':
                paraimage['Number_of_lines_original'] = int(subprocess.check_output('grep "Number_of_lines_original:" '+path_info+" | awk 'END {print $2}'", shell=True, encoding="utf-8").strip())
                paraimage['Number_of_pixels_original'] = int(subprocess.check_output('grep "Number_of_pixels_original:" '+path_info+" | awk 'END {print $2}'", shell=True, encoding="utf-8").strip())
                
                paraimage['Data_output_file'] = (subprocess.check_output('grep "Data_output_file:" '+path_info+" | awk 'END {print $2}'", shell=True, encoding="utf-8").strip())
                paraimage['Data_output_format'] = (subprocess.check_output('grep "Data_output_format:" '+path_info+" | awk 'END {print $2}'", shell=True, encoding="utf-8").strip())
                
                paraimage['First_pixel_azimuth_time (UTC)'] = (subprocess.check_output('grep "First_pixel_azimuth_time (UTC):" '+path_info+" | awk 'END {print $3}'", shell=True, encoding="utf-8").strip()) +' '+(subprocess.check_output('grep "First_pixel_azimuth_time (UTC):" '+path_info+" | awk 'END {print $4}'", shell=True, encoding="utf-8").strip())
                paraimage['IMAGE_MODE'] = (subprocess.check_output('grep "IMAGE_MODE:" '+path_info+" | awk 'END {print $2}'", shell=True, encoding="utf-8").strip()) 
                paraimage['SWATH'] = (subprocess.check_output('grep "SWATH:" '+path_info+" | awk 'END {print $2}'", shell=True, encoding="utf-8").strip()) 
                paraimage['Sensor platform mission identifer'] = (subprocess.check_output('grep "Sensor platform mission identifer:" '+path_info+" | awk 'END {print $5}'", shell=True, encoding="utf-8").strip()) 
                paraimage['PASS'] = (subprocess.check_output('grep "PASS" '+path_info+" | awk 'END {print $5}'", shell=True, encoding="utf-8").strip()) 

                paraimage['First_line (w.r.t. original_image)'] = int(subprocess.check_output('grep -w "First_line" '+path_info+" | grep -v '#' | awk 'END {print $4}'", shell=True, encoding="utf-8").strip())
                paraimage['Last_line (w.r.t. original_image)'] = int(subprocess.check_output('grep "Last_line" '+path_info+" | grep -v '#' | awk 'END {print $4}'", shell=True, encoding="utf-8").strip())
                paraimage['First_pixel (w.r.t. original_image)'] = int(subprocess.check_output('grep "First_pixel" '+path_info+" | grep -v '#' | awk 'END {print $4}'", shell=True, encoding="utf-8").strip())
                paraimage['Last_pixel (w.r.t. original_image)'] = int(subprocess.check_output('grep "Last_pixel" '+path_info+" | grep -v '#' | awk 'END {print $4}'", shell=True, encoding="utf-8").strip())
                paraimage['Number of lines (non-multilooked)'] = int(subprocess.check_output('grep "Number of lines" '+path_info+" | awk 'END {print $5}'", shell=True, encoding="utf-8").strip())
                paraimage['Number of pixels (non-multilooked)'] = int(subprocess.check_output('grep "Number of pixels" '+path_info+" | awk 'END {print $5}'", shell=True, encoding="utf-8").strip())
        
        elif mode == 'ifg':
                # paraimage['Number of lines (non-multilooked)'] = int(subprocess.check_output('grep "Number of lines (multilooked):" '+path_info+" | awk 'END {print $5}'", shell=True, encoding="utf-8").strip())
                # paraimage['Number of pixels (non-multilooked)'] = int(subprocess.check_output('grep "Number of pixels (multilooked):" '+path_info+" | awk 'END {print $5}'", shell=True, encoding="utf-8").strip())
                paraimage['Data_output_file'] = (subprocess.check_output('grep "Data_output_format:" '+path_info+" | awk 'END {print $2}'", shell=True, encoding="utf-8").strip())

                paraimage['First_line (w.r.t. original_master)'] = int(subprocess.check_output('grep -w "First_line" '+path_info+" | grep -v '#' | awk 'END {print $4}'", shell=True, encoding="utf-8").strip())
                paraimage['Last_line (w.r.t. original_master)'] = int(subprocess.check_output('grep "Last_line" '+path_info+" | grep -v '#' | awk 'END {print $4}'", shell=True, encoding="utf-8").strip())
                paraimage['First_pixel (w.r.t. original_master)'] = int(subprocess.check_output('grep "First_pixel" '+path_info+" | grep -v '#' | awk 'END {print $4}'", shell=True, encoding="utf-8").strip())
                paraimage['Last_pixel (w.r.t. original_master)'] = int(subprocess.check_output('grep "Last_pixel" '+path_info+" | grep -v '#' | awk 'END {print $4}'", shell=True, encoding="utf-8").strip())
                
                paraimage['Number of lines (non-multilooked)'] = int(paraimage['Last_line (w.r.t. original_master)'] - paraimage['First_line (w.r.t. original_master)'] + 1)
                paraimage['Number of pixels (non-multilooked)'] = int(paraimage['Last_pixel (w.r.t. original_master)'] - paraimage['First_pixel (w.r.t. original_master)'] + 1)

        elif mode == 'coh':
                paraimage['Number of lines (non-multilooked)'] = int(subprocess.check_output('grep "Number of lines (multilooked):" '+path_info+" | awk 'END {print $5}'", shell=True, encoding="utf-8").strip())
                paraimage['Number of pixels (non-multilooked)'] = int(subprocess.check_output('grep "Number of pixels (multilooked):" '+path_info+" | awk 'END {print $5}'", shell=True, encoding="utf-8").strip())
                paraimage['Data_output_file'] = (subprocess.check_output('grep "Data_output_format:" '+path_info+" | awk 'END {print $2}'", shell=True, encoding="utf-8").strip())


        return paraimage

################################################################################
## Multilook an image with cpxfiddle
################################################################################
def multilookimage(listfile,
                mode,
                listpara,
                format_image,
                mlran,
                mlazi,
                colormap: Optional[str] = constants.__file__.replace('constants.py','tools%scolormap%scmap_gray.csv' % (os.sep,os.sep)),
                nbworker: Optional[int] = 1,
                exp: Optional[float] = 0.6,
                power: Optional[float] = 1.0,
                fout: Optional[Union[None,list]] = None, 
                log: Optional[Union[None,str]] = None,
                verbose: Optional[bool] = None,
                ):
        """Wrapper for the cpxfiddle command

        The function applies multilooking with the cpxfiddle programs. 

        Note: 
                This function is parallelised. The type of image should be the same. 

        Args:
                listfile (list of str): List of files 
                mode (str): mag / mixed / normal
                listpara (list of dict): List of dict containing the image parameters
                format_image (str): Format of the images
                mlran (int): Multilook factor in range
                mlazi (int): Multilook factor in azimuth
                colormap (str, optional): Path of the desired colormap.
                nbworker (int): Number of workers [Default: ``1``]
                exp (int): Exponential factor for the intensity [Default: ``0.6``]
                power (int): Power factor for the intensity [Default: ``1.0``]
                fout (list of str): List of output files. [Default: `None`]
                log (str): log. [Default: `None`]
                verbose (bool): verbose mode. [Default: `None`]
        
        """
        if not constants.__requirement_Doris__ in os.environ['PATH']:
                os.environ['PATH'] = os.environ['PATH']+':'+constants.__requirement_Doris__+':.'
                
        ## Check the input parameters
        if not isinstance(listfile,list):
            raise TypeError(usermessage.typeerrormsg(
                __name__,multilookimage.__name__,__file__,__copyright__,
                'listfile','list',log))
        else: 
                for fi in listfile: 
                        if not os.path.isfile(fi): 
                                raise ValueError(usermessage.errormsg(__name__,multilookimage.__name__,__file__,__copyright__,
                                        'The file %s does not exist.' % (fi),log))
                        
        if not mode in ['mag','mixed','normal','coh']:
            raise TypeError(usermessage.typeerrormsg(
                __name__,multilookimage.__name__,__file__,__copyright__,
                'mode',"['mag','mixed','normal'",log))
        
        if not isinstance(listpara,list):
            raise TypeError(usermessage.typeerrormsg(
                __name__,multilookimage.__name__,__file__,__copyright__,
                'listpara','list',log))
        
        if not isinstance(format_image,str):
            raise TypeError(usermessage.typeerrormsg(
                __name__,multilookimage.__name__,__file__,__copyright__,
                'format_image','str',log))
        
        if not isinstance(mlran,int):
            raise TypeError(usermessage.typeerrormsg(
                __name__,multilookimage.__name__,__file__,__copyright__,
                'mlran','int',log))
        
        if not isinstance(mlazi,int):
            raise TypeError(usermessage.typeerrormsg(
                __name__,multilookimage.__name__,__file__,__copyright__,
                'mlazi','int',log))
        
        if not os.path.isfile(colormap): 
                raise ValueError(usermessage.errormsg(__name__,multilookimage.__name__,__file__,__copyright__,
                        'The colormap file %s does not exist.' % (colormap),log))
        
        if not isinstance(nbworker,int):
            raise TypeError(usermessage.typeerrormsg(
                __name__,multilookimage.__name__,__file__,__copyright__,
                'nbworker','int',log))
        
        if not isinstance(exp,float):
            raise TypeError(usermessage.typeerrormsg(
                __name__,multilookimage.__name__,__file__,__copyright__,
                'exp','float',log))
        
        if not isinstance(power,float):
            raise TypeError(usermessage.typeerrormsg(
                __name__,multilookimage.__name__,__file__,__copyright__,
                'power','float',log))
        
        if not isinstance(verbose,bool):
            raise TypeError(usermessage.typeerrormsg(
                __name__,multilookimage.__name__,__file__,__copyright__,
                'verbose','bool',log))
        
        usermessage.openingmsg(__name__,multilookimage.__name__,__file__,__copyright__,'Multilooking of the images',log,verbose)

        usermessage.ezprint('List of files: %s' % (listfile),log,verbose) 
        usermessage.ezprint('Mode: %s' % (mode),log,verbose) 
        usermessage.ezprint('Format: %s' % (format_image),log,verbose) 
        usermessage.ezprint('mlran: %s' % (mlran),log,verbose) 
        usermessage.ezprint('mlazi: %s' % (mlazi),log,verbose) 
        usermessage.ezprint('Colormap: %s' % (colormap),log,verbose) 
        usermessage.ezprint('Nb. Worker: %s' % (nbworker),log,verbose) 
        usermessage.ezprint('Exponential: %s' % (exp),log,verbose) 
        usermessage.ezprint('Power: %s' % (power),log,verbose) 

        usermessage.ezprint('Creation of the commands:',log,verbose) 

        dict_cmd = dict()

        for idx, fi in enumerate(listfile): 

                if mode == 'mag': 
                       outputformat = '-osunraster -e%s -s%s -c%s' % (exp,power,colormap)
                elif mode == 'mixed':
                       outputformat = '-osunraster -e%s -s%s -c%s' % (exp,power,colormap) 
                elif mode == 'coh':
                       outputformat = '-osunraster -b -c%s -r 0.0/1.0' % (colormap) 
                       mode = 'normal'
                else: 
                        outputformat = '-ofloat'
                        mode = 'normal'

                if (fout == None) or (not isinstance(fout,list)):
                        foutit = fi+'.ras'
                else:
                        foutit = fout[idx]

                cmdi = "cpxfiddle -w %d %s -q%s -M%d/%d %s %s > %s" % (listpara[idx]['Number of pixels (non-multilooked)'],
                                format_image,
                                mode,
                                mlazi,
                                mlran,
                                outputformat,
                                fi,
                                foutit)

                dict_cmd['cmd%s' % (idx)] = [ cmdi.split(' '),
                                        None]

        usermessage.ezprint('\tdone',log,verbose) 

        # Run the commands 
        wrappersubprocess(dict_cmd,
                0,
                nbworker,
                verbose,
                log)
        
################################################################################
## Wrapper of the subprocess of Doris
################################################################################
def wrappersubprocess(list_cmd,
                nb_cores,
                nb_worker,
                verbose,
                log):
        """Wrapper for Doris subprocesses 

        The function will run several subprocesses for Doris regarding the number of workers  

        Args:
                list_cmd (dict) : command dictionary
                nb_worker (str) : number of workers
                verbose (bool): verbose mode
                log (str or None): log file from the job

        """
        
        maxidx_job = len(list(list_cmd.keys())) - 1
        i = 0
        while i <= maxidx_job:
                for it in np.arange(i,i+nb_worker,1):

                        if it <= maxidx_job:
                                exec("p%s = multiprocessing.Process(target=subprocessrun, args=(list_cmd['cmd%s'][0], list_cmd['cmd%s'][1], nb_cores, verbose, log))" % (it,it,it) )
                                exec('p%s.start()' % (it))

                for it in np.arange(i,i+nb_worker,1):
                        if it <= maxidx_job:
                                exec('p%s.join()' % (it))
                        i = i + 1
        
################################################################################
## Run a subprocess for Doris 
################################################################################
def subprocessrun(cmd,
                input_card,
                nb_cores,
                verbose,
                log):
        """Run a subprocess for Doris

        The function will run a subprocess for Doris

        Args:
                cmd (list) : command
                input_card (str) : input card 
                verbose (bool): verbose mode 
                log (str or None): log file from the job

        """
        usermessage.ezprint('Run Doris:',log,verbose)
        usermessage.ezprint('\tCommand: %s' % (cmd),log,verbose)

        # Modification of the env variables 
        if not constants.__requirement_Doris__ in os.environ['PATH']:
                os.environ['PATH'] = os.environ['PATH']+':'+constants.__requirement_Doris__+':.' 
        my_env = os.environ.copy()

        if not nb_cores == 0: 
                my_env['MKL_NUM_THREADS'] = '%s' % (nb_cores)
                my_env['NUMEXPR_NUM_THREADS'] = '%s' % (nb_cores)
                my_env['OMP_NUM_THREADS'] = '%s' % (nb_cores)
                my_env['OPENBLAS_NUM_THREADS'] = '%s' % (nb_cores)
                my_env['VECLIB_MAXIMUM_THREADS'] = '%s' % (nb_cores)

        if not input_card == None:
                param = []
                with open(input_card,'r') as fi:
                        for li in fi:
                                param.append(li)
                usermessage.ezprint('\tParameters: %s' % (cmd),log,verbose)
                usermessage.ezprint('%s' % ('\t\t'+'\t\t'.join(param)),log,verbose)

        if (not '>' in cmd) and (not 'doris.rmstep.sh' in cmd) and (not 'cp' in cmd): 

                if 'cd' in cmd:
                        os.chdir(cmd[1])
                        cmd = cmd[3::]

                pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env = my_env)
                
                try: 
                        while (line := pr.stdout.readline()) != "":
                                usermessage.ezprint(line.replace('\n',' '),log,verbose)     
                        if (not pr.stderr.readline().strip() == ''):
                                while (line := pr.stderr.readline()) != "":
                                        usermessage.ezprint(line.replace('\n',' '),log,verbose)   
                                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the Doris processing',log))
                except KeyboardInterrupt:
                        pr.terminate()
        else:
                cmd = ' '.join(cmd)
                os.system(cmd)

        usermessage.ezprint('\tdone',log,verbose)

##########################################################################################
def readDEMpara(path_DEM):
        """Read the DEM parameters 

        The function will read the DEM parameters. 

        Args: 
                path_DEM (str): Path of the DEM 

        """

        if not os.path.isfile(path_DEM):
                print(path_DEM)
                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'The file does not exist.',None))

        paraDEM = dict()

        cmdi = "gdalinfo "+path_DEM+" > out.tmp"
        os.system(cmdi)

        paraDEM['samples'] = int(subprocess.check_output('grep "Size is" '+"out.tmp | awk 'END {print $3}'", shell=True, encoding="utf-8").strip().split(',')[0])
        paraDEM['lines'] = int(subprocess.check_output('grep "Size is" '+"out.tmp | awk 'END {print $4}'", shell=True, encoding="utf-8").strip())

        paraDEM['lon'] = float(subprocess.check_output('grep "Upper Left" '+"out.tmp | awk 'END {print $4}'", shell=True, encoding="utf-8").strip().split(',')[0])
        paraDEM['lat'] = float(subprocess.check_output('grep "Upper Left" '+"out.tmp | awk 'END {print $5}'", shell=True, encoding="utf-8").strip().split(')')[0])

        paraDEM['deltalon'] = float(subprocess.check_output('grep "Pixel Size" '+"out.tmp | awk 'END {print $4}'", shell=True, encoding="utf-8").strip().split(',')[0].split('(')[-1])
        paraDEM['deltalat'] = float(subprocess.check_output('grep "Pixel Size" '+"out.tmp | awk 'END {print $4}'", shell=True, encoding="utf-8").strip().split(',')[-1].split(')')[0])

        paraDEM['lonmin'] = float(subprocess.check_output('grep "Upper Left" '+"out.tmp | awk 'END {print $4}'", shell=True, encoding="utf-8").strip().split(',')[0])
        paraDEM['latmax'] = float(subprocess.check_output('grep "Upper Left" '+"out.tmp | awk 'END {print $5}'", shell=True, encoding="utf-8").strip().split(')')[0])
        paraDEM['lonmax'] = float(subprocess.check_output('grep "Lower Right" '+"out.tmp | awk 'END {print $4}'", shell=True, encoding="utf-8").strip().split(',')[0])
        paraDEM['latmin'] = float(subprocess.check_output('grep "Lower Right" '+"out.tmp | awk 'END {print $5}'", shell=True, encoding="utf-8").strip().split(')')[0])
        
        paraDEM['nodata'] = float(subprocess.check_output('grep "NoData Value" '+"out.tmp | awk 'END {print $2}'", shell=True, encoding="utf-8").strip().split('=')[-1])

        if os.path.isfile('out.tmp'):
                os.remove('out.tmp')

        return paraDEM

################################################################################
## Check the processor in the .res files
################################################################################
def checkprocess(resfile,
        keyprocess,
        verbose: Optional[bool] = True,
        log: Optional[str] = None):
        """Check the process of the .res file for Doris

        This function checks if a Doris has been done. 

        Args: 
                resfile (str): Path of the .res file
                keyprocess (str): Key of the processing
                verbose (bool, optional): Verbose. [Default: `True`]
                log (str, optional): Verbose. [Default: `None`]

        Returns: 
                bool: bool variable for the checking 

        """
        if not os.path.isfile(resfile):
                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'The file does not exist.',log))

        if not keyprocess in ['readfiles',
                'readfiles',
                'precise_orbits',
                'crop',
                'sim_amplitude',
                'master_timing',
                'oversample',
                'resample',
                'filt_azi',
                'filt_range',
                'coarse_orbits',
                'coarse_correl',
                'fine_coreg',
                'timing_error',
                'dem_assist',
                'comp_coregpm',
                'interfero',
                'coherence',
                'comp_refphase',
                'subtr_refphase',
                'comp_refdem',
                'subtr_refdem',
                'filtphase',
                'unwrap',
                'est_orbits',
                'slant2h',
                'geocoding',
                'dinsar',]:
                raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Bad key.',log))
                        
        check = subprocess.check_output("grep '%s:' %s | awk 'NR==1{print $2}'" % (keyprocess,resfile), shell=True, encoding="utf-8").strip()

        if check == '1':
                check = True
        else:
                check = False

        return check

################################################################################
## Delete a date from a SLC stack
################################################################################
def deletedate(job, date=None, 
        verbose: Optional[bool] = None,
        bypassuser: Optional[bool] = False):
        """Delete a date in a Doris ``ezinsar`` stack

        The function will detele a date from ``ezinsar.coregistration`` or ``ezinsar.ifgstack``.   

        Args:
                job (``ezinsar.job``): job (can be an ``ezinsar.job``)
                date (str): date in string needed to be deleted (cannot be the reference date). [Default: `None`]
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                bypassuser (bool, Optional): Confirmation from the user [Default: `False`].

        Returns:
                ``ezinsar`` processing job: Return an EZ-InSAR coregistration class
        
        """
        if not ('doriscoregistration.coregistration' in str(type(job)) or 'dorisifgstack.ifgstack' in str(type(job))):
                raise ValueError(usermessage.errormsg(__name__,deletedate.__name__,__file__,__copyright__,
                                'The job parameter is not a complete EZ-InSAR processing.',None))
        
        if verbose == None:
                verbose = job.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,deletedate.__name__,__file__,__copyright__,
                        'verbose','True or False',job.log))
        
        if not isinstance(date,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,deletedate.__name__,__file__,__copyright__,
                        'date','str',job.log))
        
        if not isinstance(bypassuser,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,deletedate.__name__,__file__,__copyright__,
                        'bypassuser','bool',job.log))
        
        usermessage.openingmsg(__name__,deletedate.__name__,__file__,__copyright__,'Delete a date from a Doris stack',job.log,verbose)

        
        if 'doriscoregistration.coregistration' in str(type(job)):
                usermessage.ezprint('Detection of a coregistration job',job.log,verbose) 

                ## Read the date file (final date file as priority)
                pathdate = None
                if os.path.isfile(job.pathstack+os.sep+'rslc_'+job.polarisation[0].lower()+os.sep+'dates'):
                        pathdate = job.pathstack+os.sep+'rslc_'+job.polarisation[0].lower()+os.sep+'dates'
                elif os.path.isfile(job.workdirectory+os.sep+'dates'):
                        pathdate = job.workdirectory+os.sep+'dates'

                if pathdate == None:
                        raise ValueError(usermessage.errormsg(__name__,deletedate.__name__,__file__,__copyright__,
                                'No dates file found.',job.log))
                
                datelist = []
                with open(pathdate,'r') as fi:
                        for di in fi:
                                datelist.append(di.split()[0])

                if not date in datelist:
                        raise ValueError(usermessage.errormsg(__name__,deletedate.__name__,__file__,__copyright__,
                                'The selected date is not in the date list.',job.log))
                
                if date == job.refdate:
                        raise ValueError(usermessage.errormsg(__name__,deletedate.__name__,__file__,__copyright__,
                                'Impossible to delete the reference date.',job.log))
                
                usermessage.ezprint('The date %s will be deleted (all polarisations will be deleted).' % (date),job.log,verbose)

                ## Create the list of the files
                listfile = []
                listfile = listfile + glob.glob(job.workdirectory+os.sep+'slc'+os.sep+'*'+date+'*')
                listfile = listfile + glob.glob(job.workdirectory+os.sep+'slc'+os.sep+'*'+date+'*')
                listfile = listfile + glob.glob(job.pathstack+os.sep+'rslc_??'+os.sep+'*'+date+'*')
                
                usermessage.ezprint('All the following files will be deleted:',job.log,verbose)
                for fi in listfile:
                        usermessage.ezprint('\t%s' % (fi.split(os.sep)[-1]),job.log,verbose)

                usermessage.warningmsg(__name__,deletedate.__name__,__file__,'Removal of a date can create inconstency inside the Doris stack and a decrease of the coregistration accuracy. The user should rerun the computation of interferometric network to keep this file accurate.',job.log,verbose)

                if bypassuser == False:
                        userconfirmation = input('\nPlease confirm the removal of the date? [yes or no]? ')

                        if not userconfirmation in ['y','1',1,'yes','okay']:
                                raise ValueError(usermessage.errormsg(__name__,deletedate.__name__,__file__,__copyright__,
                                'Stopped by the user.',job.log))
                        
                # Delete 
                for fi in listfile:
                        if os.path.isfile(fi):
                                os.remove(fi)

                # Rebuild the date file
                with open(job.workdirectory+os.sep+'dates','w') as fout:
                        for di in datelist:
                                if not date == di:
                                        fout.write('%s\n' % (di))

                for poli in job.polarisation:
                        if os.path.isdir(job.pathstack+os.sep+'rslc_'+poli.lower()):
                                shutil.copy(job.pathstack+os.sep+'rslc_'+poli.lower()+os.sep+'dates')

################################################################################
## Read the date file
################################################################################
def readdatefile(datefile):
        """Read a date file
        
        The function allows to read a date file. 

        Args: 
                datefile (str): date file

        Returns:
                list: List of dates in YYYYMMDD format.
                
        """

        listdate = []
        with open(datefile) as fi:
                for di in fi:
                        listdate.append(di.strip())

        return listdate