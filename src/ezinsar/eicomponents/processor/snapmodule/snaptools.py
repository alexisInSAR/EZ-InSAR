#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to add some tool functions for SNAP processor

The module allows to add some sub-functions for SNAP processor.
    
    (From `ezinsar` package)

Changelog:
        * 1.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import os
from typing import Optional, Union
import numpy as np
import shutil
import glob
from osgeo import gdal, osr
from skimage.measure import block_reduce
from skimage.io import imsave, imread
import random
import string 
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
from osgeo import gdal

from ezinsar import usermessage
from ezinsar import constants
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
################################################################################
def snapclearcache(verbose=True,log=None):
        """Clean the SNAP's cache

        The function will clear the cache of SNAP.

        Args:
                verbose (bool): verbose mode
                log (str): log file

        """
        usermessage.openingmsg(__name__,snapclearcache.__name__,__file__,__copyright__,'Clean the cache of SNAP',log,verbose)
        
        pathcache = constants.__requirement_SNAP__.replace('snap-python','var')+os.sep+'cache'+os.sep+'temp'
        
        if os.path.isdir(pathcache): 
                size = 0
                for ele in os.scandir(pathcache):
                        size+=os.path.getsize(ele)
     
                usermessage.ezprint('Cache found in %s: %0.0f MB' %(pathcache,size/(1024*1024)),log,verbose) 

                if size/(1024*1024) > constants.__SNAPcachemax__:
                        usermessage.ezprint('\tThe total size is higher than the threshold (%d). The directory will be deleted.' %(constants.__SNAPcachemax__),log,verbose) 
                        shutil.rmtree(pathcache)

################################################################################
## Check the parameters of a dict
################################################################################
def checksnapparafromdict(paradict,jobcoreg,verbose):
        """Check the parameters of a dict for an ``ezinsar`` job using SNAP

        The function checks the parameters of a dict for an ``ezinsar.coregistration`` or ``ezinsar.ifgstack``.   

        Args:
                paradict (dict): parameter
                jobcoreg (``ezinsar.coregistration``): EZ-InSAR coregistration job for SNAP processor
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        Returns:
                ``ezinsar`` processing job: Return an EZ-InSAR coregistration class
        
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
                                        __name__,checksnapparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'True or False',jobcoreg.log))

                elif infopara['modepara'][idx] == 'list':
                        if not paradict[namepara]['value'] in infopara['valuelist'][idx]: 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checksnapparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'%s' % (infopara['valuelist'][idx]),jobcoreg.log))
                        
                elif infopara['modepara'][idx] == 'email':
                        if not isinstance(paradict[namepara]['value'],str): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checksnapparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'str',jobcoreg.log))
                        
                elif infopara['modepara'][idx] == 'int':
                        if not isinstance(paradict[namepara]['value'],int): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checksnapparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'int',jobcoreg.log))

                elif infopara['modepara'][idx] == 'int-':
                        if isinstance(paradict[namepara]['value'],str): 
                                if not paradict[namepara]['value'] == '-': 
                                        raise TypeError(usermessage.typeerrormsg(
                                        __name__,checksnapparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),"int or '-'",jobcoreg.log))
                        else: 
                                if not isinstance(paradict[namepara]['value'],int): 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,checksnapparafromdict.__name__,__file__,__copyright__,
                                                "parameter %s in %s" % (namepara,namestep),"int or '-'",jobcoreg.log))

                elif infopara['modepara'][idx] == 'float':
                        if not isinstance(paradict[namepara]['value'],float): 
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,checksnapparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),'float',jobcoreg.log))
                        
                elif infopara['modepara'][idx] == 'float-':
                        if isinstance(paradict[namepara]['value'],str): 
                                if not paradict[namepara]['value'] == '-': 
                                        raise TypeError(usermessage.typeerrormsg(
                                        __name__,checksnapparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),"float or '-'",jobcoreg.log))
                        else: 
                                if not isinstance(paradict[namepara]['value'],float): 
                                        raise TypeError(usermessage.typeerrormsg(
                                                __name__,checksnapparafromdict.__name__,__file__,__copyright__,
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
                                        __name__,checksnapparafromdict.__name__,__file__,__copyright__,
                                        "parameter %s in %s" % (namepara,namestep),"None, user or a file",jobcoreg.log))

        return jobcoreg

################################################################################
## Read the date file
################################################################################
def readdatefile(datefile):
        listdate = []
        with open(datefile) as fi:
                for di in fi:
                        listdate.append(di.strip())

        return listdate

################################################################################
## Detect sub-swath in a directory
################################################################################
def detectIW(pathdir,date=None):
        IW = []
        if not date == None: 
                listfile = glob.glob(pathdir+os.sep+'*'+date+'*.dim')
        else: 
                listfile = glob.glob(pathdir+os.sep+'*.dim')

        for li in listfile: 
                if 'IW1' in li:
                        IW.append('IW1')
                if 'IW2' in li:
                        IW.append('IW2')
                if 'IW3' in li:
                        IW.append('IW3')
        
        IW = np.sort(IW)

        return IW

################################################################################
## Create a mosaic of .bmp images
################################################################################
def createbmpmosaic(file,
        outputfile,
        mlran, 
        mlazi,
        mode = 'intensity',
        polarisation: Optional[str] = 'vv',
        scale: Optional[float] = 1.0,
        exp: Optional[float] = 0.35,
        verbose: Optional[bool] = True,
        log: Optional[str] = None,
        ):
        """Create a mosaic of .bmp images

        The function will create a mosaic of .bmp images. This function is for Sentinel-1 IW data. 

        Args:
                verbose (bool): verbose mode
                log (str): log file


        verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.

        """

        if not isinstance(file,list):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createbmpmosaic.__name__,__file__,__copyright__,
                        'file','list',log))
        else: 
                for li in file: 
                        if not li.endswith('.data'):
                                 raise TypeError(usermessage.typeerrormsg(
                                        __name__,createbmpmosaic.__name__,__file__,__copyright__,
                                        'file','.data file',log))
                        
        if not isinstance(outputfile,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createbmpmosaic.__name__,__file__,__copyright__,
                        'outputfile','str',log))       

        if not isinstance(mlran,int):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createbmpmosaic.__name__,__file__,__copyright__,
                        'mlran','int',log))
        
        if not isinstance(mlazi,int):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createbmpmosaic.__name__,__file__,__copyright__,
                        'mlazi','int',log))   
        
        if not isinstance(polarisation,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createbmpmosaic.__name__,__file__,__copyright__,
                        'polarisation','str',log))   
        
        if not isinstance(scale,float):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createbmpmosaic.__name__,__file__,__copyright__,
                        'scale','float',log))
        
        if not isinstance(exp,float):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createbmpmosaic.__name__,__file__,__copyright__,
                        'exp','float',log))
                
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createbmpmosaic.__name__,__file__,__copyright__,
                        'verbose','bool',log))

        usermessage.openingmsg(__name__,createbmpmosaic.__name__,__file__,__copyright__,'Create a mosaic of .bmp image',log,verbose)
        listoutput = []

        format = outputfile.split(os.sep)[-1].split('.')[-1]

        for fi in file:
                if not os.path.isdir(fi):
                        raise ValueError(usermessage.errormsg(__name__,createbmpmosaic.__name__,__file__,__copyright__,'Impossible to read the file',log))
                               
                if 'iw1' in fi.split(os.sep)[-1].lower(): 
                        iw = 'IW1'
                elif 'iw2' in fi.split(os.sep)[-1].lower(): 
                        iw = 'IW2'
                else:
                        iw = 'IW3'

                if mode == 'intensity':
                        realfile = glob.glob(fi+os.sep+'*q*'+iw+'*'+polarisation.upper()+'*.img')[0]
                        imagfile = glob.glob(fi+os.sep+'*i*'+iw+'*'+polarisation.upper()+'*.img')[0]

                        tmpfile = constants.__cachedir__+os.sep+'tmp_'+''.join(random.choice(string.ascii_lowercase) for i in range(16))+'.'+format
                        
                        createintensitybmp([realfile, imagfile],
                                tmpfile,
                                mlran, 
                                mlazi,
                                scale = scale, 
                                exp = exp, 
                                verbose = False, log = log)
                        
                        listoutput.append(tmpfile)
       
        # Create the mosaic
        fig, axs = plt.subplots(1, len(listoutput))    
        h = 1   
        for ax, li in zip(axs.flat,listoutput): 
                im = plt.imread(li)
                ax.imshow(im)
                ax.set_title('IW%s' % (h))

                h = h + 1

        # Save the new image
        fig.canvas._print_pil(outputfile, fmt = format.upper(), pil_kwargs={'dpi': [450,450]})

        # Clean the cache
        for li in listoutput: 
                if os.path.isfile(li):
                        os.remove(li)

################################################################################
## Create intensity .bmp image
################################################################################
def createintensitybmp(files,
        outputfile,
        mlran, 
        mlazi,
        colormap: Optional[str] = 'gray',
        scale: Optional[float] = 1.0,
        exp: Optional[float] = 0.35,
        verbose: Optional[bool] = True,
        log: Optional[str] = None,
        ):
        """Create an intensity .bmp image

        The function will compute a .bmp image of intensity, from the complex number. The normalisation is done on the 0% - 0.9999% range.

        Args:
                files (list): List of two files (real and part of complex image)
                outputfile (str): Fullpath of the output file
                mlran (int): Multilooking factor in range
                mlazi (int): Multilooking factor in azimut
                colormap (str): Colormap [default: gray]
                scale (float): Scaling value [default: 1.0]
                exp (float): exponential value [default: 0.35]
                verbose (bool): verbose [Default: `None`].
                log (str): log [Default: `None`].

        """

        if not isinstance(files,list):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createintensitybmp.__name__,__file__,__copyright__,
                        'file','list',log))
        else: 
                for li in files: 
                        if not os.path.isfile(li):
                                 raise TypeError(usermessage.typeerrormsg(
                                        __name__,createintensitybmp.__name__,__file__,__copyright__,
                                        'file','.img file',log))
                        
        if not isinstance(outputfile,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createintensitybmp.__name__,__file__,__copyright__,
                        'outputfile','str',log))       

        if not isinstance(mlran,int):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createintensitybmp.__name__,__file__,__copyright__,
                        'mlran','int',log))
        
        if not isinstance(mlazi,int):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createintensitybmp.__name__,__file__,__copyright__,
                        'mlazi','int',log))   
        
        if not isinstance(scale,float):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createintensitybmp.__name__,__file__,__copyright__,
                        'scale','float',log))
        
        if not isinstance(exp,float):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createintensitybmp.__name__,__file__,__copyright__,
                        'exp','float',log))
                
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createintensitybmp.__name__,__file__,__copyright__,
                        'verbose','bool',log))
        
        list_colormap = []
        for li in glob.glob(os.path.dirname(__file__)+os.sep+'..'+os.sep+'..'+os.sep+'..'+os.sep+'tools'+os.sep+'colormap'+os.sep+'*.csv'): 
                list_colormap.append(li.split(os.sep)[-1].split('.')[0].replace('cmap_',''))
        if not colormap in list_colormap: 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createintensitybmp.__name__,__file__,__copyright__,
                        'colormap','%s' % (list_colormap),log))
        
        usermessage.openingmsg(__name__,createintensitybmp.__name__,__file__,__copyright__,'Create a intensity .bmp image',log,verbose)

        ## Detection of files
        realfile = None
        imagfile = None

        for fi in files:
                if 'q_' in fi.split(os.sep)[-1]:
                      realfile = fi
                if 'i_' in fi.split(os.sep)[-1]:
                      imagfile = fi 

        usermessage.ezprint('Real-part file: %s' % (realfile),log,verbose)
        usermessage.ezprint('Imaginary-part file: %s' % (imagfile),log,verbose)

        # Open the files
        usermessage.ezprint('Open the file:',log,verbose)
        fimag = gdal.Open(realfile)
        realpart = fimag.GetRasterBand(1).ReadAsArray().astype(float)
        fimag = None

        fimag = gdal.Open(imagfile)
        imagfile = fimag.GetRasterBand(1).ReadAsArray().astype(float)
        fimag = None
        usermessage.ezprint('\tdone',log,verbose)

        # Compute the intensity
        usermessage.ezprint('Compute the intensity:',log,verbose)
        intimage = realpart * realpart + imagfile * imagfile
        usermessage.ezprint('\tdone',log,verbose)

        # Multilooking
        usermessage.ezprint('Multilooking and scaling: %s/%s, scale=%s and exp=%s' % (mlran,mlazi,scale,exp),log,verbose)
        intimage = block_reduce(intimage, block_size=(mlazi,mlran), func=np.nanmean, cval=0)
        intimage = np.nanmean(intimage) * scale * (intimage**exp)
        usermessage.ezprint('\tdone',log,verbose)

        # Normalisation 
        usermessage.ezprint('Normalise the image:',log,verbose)
        intimage = (intimage - 0) / (np.nanquantile(intimage,0.9999) - 0)
        usermessage.ezprint('\tdone',log,verbose)

        # Add the colormap 
        usermessage.ezprint('Apply the colormap %s:' % (colormap),log,verbose)
        color = np.loadtxt(glob.glob(os.path.dirname(__file__)+os.sep+'..'+os.sep+'..'+os.sep+'..'+os.sep+'tools'+os.sep+'colormap'+os.sep+'cmap_'+colormap+'.csv')[0])
        newcmp = ListedColormap(color/255)
        data = np.uint8(newcmp(intimage)[:, :, :-1]*255)
        usermessage.ezprint('\tdone',log,verbose)

        # Saving 
        usermessage.ezprint('Write the file %s:' % (outputfile),log,verbose)
        imsave(outputfile,data)
        usermessage.ezprint('\tdone',log,verbose)

################################################################################
## Create interferogram .bmp image from SLCs
################################################################################
def createifgbmpnocorrection(filemaster,fileslave,
        outputfile,
        mlran, 
        mlazi,
        colormap: Optional[str] = 'gray',
        verbose: Optional[bool] = True,
        log: Optional[str] = None,
        ):
        """Create an inteferogram .bmp image

        The function will compute a .bmp images of inteferograms based on the SLCs. In this case, no correction will be applied (i.e., flat-Earth and topography).

        Args:
                filemaster (list): List of two files (real and part of complex image)
                fileslave (list): List of two files (real and part of complex image)
                outputfile (str): Fullpath of the output file
                mlran (int): Multilooking factor in range
                mlazi (int): Multilooking factor in azimut
                colormap (str): Colormap [default: gray]
                verbose (bool): verbose [Default: `None`].
                log (str): log [Default: `None`].

        """

        if not isinstance(filemaster,list):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createifgbmpnocorrection.__name__,__file__,__copyright__,
                        'file','list',log))
        else: 
                for li in filemaster: 
                        if not os.path.isfile(li):
                                 raise TypeError(usermessage.typeerrormsg(
                                        __name__,createifgbmpnocorrection.__name__,__file__,__copyright__,
                                        'file','.img file',log))
                        
        if not isinstance(fileslave,list):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createifgbmpnocorrection.__name__,__file__,__copyright__,
                        'file','list',log))
        else: 
                for li in fileslave: 
                        if not os.path.isfile(li):
                                 raise TypeError(usermessage.typeerrormsg(
                                        __name__,createifgbmpnocorrection.__name__,__file__,__copyright__,
                                        'file','.img file',log))
                        
        if not isinstance(outputfile,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createifgbmpnocorrection.__name__,__file__,__copyright__,
                        'outputfile','str',log))       

        if not isinstance(mlran,int):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createifgbmpnocorrection.__name__,__file__,__copyright__,
                        'mlran','int',log))
        
        if not isinstance(mlazi,int):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createifgbmpnocorrection.__name__,__file__,__copyright__,
                        'mlazi','int',log))   
                
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createifgbmpnocorrection.__name__,__file__,__copyright__,
                        'verbose','bool',log))
        
        list_colormap = []
        for li in glob.glob(os.path.dirname(__file__)+os.sep+'..'+os.sep+'..'+os.sep+'..'+os.sep+'tools'+os.sep+'colormap'+os.sep+'*.csv'): 
                list_colormap.append(li.split(os.sep)[-1].split('.')[0].replace('cmap_',''))
        if not colormap in list_colormap: 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createifgbmpnocorrection.__name__,__file__,__copyright__,
                        'colormap','%s' % (list_colormap),log))
        
        usermessage.openingmsg(__name__,createifgbmpnocorrection.__name__,__file__,__copyright__,'Create a interferogram .bmp image (without correction)',log,verbose)

        ## Detection of files
        realfilemaster = None
        imagfilemaster = None

        for fi in filemaster:
                if 'q_' in fi.split(os.sep)[-1]:
                      realfilemaster = fi
                if 'i_' in fi.split(os.sep)[-1]:
                      imagfilemaster = fi 

        ## Detection of files
        realfileslave = None
        imagfileslave = None

        for fi in fileslave:
                if 'q_' in fi.split(os.sep)[-1]:
                      realfileslave = fi
                if 'i_' in fi.split(os.sep)[-1]:
                      imagfileslave = fi 

        usermessage.ezprint('MASTER Real-part file: %s' % (realfilemaster),log,verbose)
        usermessage.ezprint('MASTER Imaginary-part file: %s' % (imagfilemaster),log,verbose)
        usermessage.ezprint('SLAVE Real-part file: %s' % (realfileslave),log,verbose)
        usermessage.ezprint('SLAVE Imaginary-part file: %s' % (imagfileslave),log,verbose)

        # Open the files
        usermessage.ezprint('Open the file:',log,verbose)
        fimag = gdal.Open(realfilemaster)
        realpart_m = fimag.GetRasterBand(1).ReadAsArray().astype(float)
        fimag = None

        fimag = gdal.Open(imagfilemaster)
        imagfile_m = fimag.GetRasterBand(1).ReadAsArray().astype(float)

        fimag = gdal.Open(realfileslave)
        realpart_s = fimag.GetRasterBand(1).ReadAsArray().astype(float)
        fimag = None

        fimag = gdal.Open(imagfileslave) 
        imagfile_s = fimag.GetRasterBand(1).ReadAsArray().astype(float)
        fimag = None
        
        usermessage.ezprint('\tdone',log,verbose)

        # Compute the interferogram
        usermessage.ezprint('Compute the interferogram:',log,verbose)
        slc_m = realpart_m + imagfile_m * 1j
        slc_s = realpart_s + imagfile_s * 1j
        usermessage.ezprint('\tdone',log,verbose)

        usermessage.ezprint('Multilooking: %s/%s' % (mlran,mlazi),log,verbose)
        ifg = np.multiply(slc_m, np.conj(slc_s))
        ifg = block_reduce(ifg, block_size=(mlazi,mlran), func=np.nanmean, cval=0) # multilooking
        ifg = np.angle(ifg)
        ifg[ifg==0] = np.nan
        usermessage.ezprint('\tdone',log,verbose)

        # Normalisation 
        usermessage.ezprint('Normalise the image:',log,verbose)
        ifg = ((ifg + np.pi)/(2*np.pi))
        usermessage.ezprint('\tdone',log,verbose)

        # Add the colormap 
        usermessage.ezprint('Apply the colormap %s:' % (colormap),log,verbose)
        color = np.loadtxt(glob.glob(os.path.dirname(__file__)+os.sep+'..'+os.sep+'..'+os.sep+'..'+os.sep+'tools'+os.sep+'colormap'+os.sep+'cmap_'+colormap+'.csv')[0])
        newcmp = ListedColormap(color/255)
        data = np.uint8(newcmp(ifg)[:, :, :-1]*255)
        usermessage.ezprint('\tdone',log,verbose)

        # Saving 
        usermessage.ezprint('Write the file %s:' % (outputfile),log,verbose)
        imsave(outputfile,data)
        usermessage.ezprint('\tdone',log,verbose)

################################################################################
## Create interferogram .bmp
################################################################################
def createifgbmp(file,
        outputfile,
        mlran, 
        mlazi,
        colormap: Optional[str] = 'gray',
        verbose: Optional[bool] = True,
        log: Optional[str] = None,
        ):
        """Create an inteferogram .bmp image

        The function will compute a .bmp images of inteferograms.

        Args:
                file (list): List of two files (real and part of complex image)
                outputfile (str): Fullpath of the output file
                mlran (int): Multilooking factor in range
                mlazi (int): Multilooking factor in azimut
                colormap (str): Colormap [default: gray]
                verbose (bool): verbose [Default: `None`].
                log (str): log [Default: `None`].

        """

        if not isinstance(file,list):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createifgbmp.__name__,__file__,__copyright__,
                        'file','list',log))
        else: 
                for li in file: 
                        if not os.path.isfile(li):
                                 raise TypeError(usermessage.typeerrormsg(
                                        __name__,createifgbmp.__name__,__file__,__copyright__,
                                        'file','.img file',log))
                        
        if not isinstance(outputfile,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createifgbmp.__name__,__file__,__copyright__,
                        'outputfile','str',log))       

        if not isinstance(mlran,int):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createifgbmp.__name__,__file__,__copyright__,
                        'mlran','int',log))
        
        if not isinstance(mlazi,int):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createifgbmp.__name__,__file__,__copyright__,
                        'mlazi','int',log))   
                
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createifgbmp.__name__,__file__,__copyright__,
                        'verbose','bool',log))
        
        list_colormap = []
        for li in glob.glob(os.path.dirname(__file__)+os.sep+'..'+os.sep+'..'+os.sep+'..'+os.sep+'tools'+os.sep+'colormap'+os.sep+'*.csv'): 
                list_colormap.append(li.split(os.sep)[-1].split('.')[0].replace('cmap_',''))
        if not colormap in list_colormap: 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createifgbmp.__name__,__file__,__copyright__,
                        'colormap','%s' % (list_colormap),log))
        
        usermessage.openingmsg(__name__,createifgbmp.__name__,__file__,__copyright__,'Create an interferogram .bmp image',log,verbose)

        ## Detection of files
        realfile = None
        imagfile = None

        for fi in file:
                if 'q_' in fi.split(os.sep)[-1]:
                      realfile = fi
                if 'i_' in fi.split(os.sep)[-1]:
                      imagfile = fi 

        usermessage.ezprint('Real-part file: %s' % (realfile),log,verbose)
        usermessage.ezprint('Imaginary-part file: %s' % (imagfile),log,verbose)

        # Open the files
        usermessage.ezprint('Open the files:',log,verbose)
        fimag = gdal.Open(realfile)
        realpart = fimag.GetRasterBand(1).ReadAsArray().astype(float)
        fimag = None
        fimag = gdal.Open(imagfile)
        imagfile = fimag.GetRasterBand(1).ReadAsArray().astype(float)
        fimag = None

        # Compute the interferogram
        usermessage.ezprint('Compute the interferogram:',log,verbose)
        ifg = realpart + imagfile * 1j
        usermessage.ezprint('\tdone',log,verbose)

        if (not mlran == 1 and mlazi == 1):
                usermessage.ezprint('Multilooking: %s/%s' % (mlran,mlazi),log,verbose)
                ifg = block_reduce(ifg, block_size=(mlazi,mlran), func=np.nanmean, cval=0) # multilooking
                usermessage.ezprint('\tdone',log,verbose)

        ifg = np.angle(ifg)
        ifg[ifg==0] = np.nan

        # Normalisation 
        usermessage.ezprint('Normalise the image:',log,verbose)
        ifg = ((ifg + np.pi)/(2*np.pi))
        usermessage.ezprint('\tdone',log,verbose)

        # Add the colormap 
        usermessage.ezprint('Apply the colormap %s:' % (colormap),log,verbose)
        color = np.loadtxt(glob.glob(os.path.dirname(__file__)+os.sep+'..'+os.sep+'..'+os.sep+'..'+os.sep+'tools'+os.sep+'colormap'+os.sep+'cmap_'+colormap+'.csv')[0])
        newcmp = ListedColormap(color/255)
        data = np.uint8(newcmp(ifg)[:, :, :-1]*255)
        usermessage.ezprint('\tdone',log,verbose)

        # Saving 
        usermessage.ezprint('Write the file %s:' % (outputfile),log,verbose)
        imsave(outputfile,data)
        usermessage.ezprint('\tdone',log,verbose)

################################################################################
## Create interferogram .bmp
################################################################################
def createcohbmp(file,
        outputfile,
        mlran, 
        mlazi,
        colormap: Optional[str] = 'gray',
        verbose: Optional[bool] = True,
        log: Optional[str] = None,
        ):
        """Create a coherence .bmp image

        The function will compute a .bmp images of coherences.

        Args:
                file (str): Path of the coherence file
                outputfile (str): Fullpath of the output file
                mlran (int): Multilooking factor in range
                mlazi (int): Multilooking factor in azimut
                colormap (str): Colormap [default: gray]
                verbose (bool): verbose [Default: `None`].
                log (str): log [Default: `None`].

        """

        if not os.path.isfile(file):
                        raise TypeError(usermessage.typeerrormsg(
                        __name__,createcohbmp.__name__,__file__,__copyright__,
                        'file','.img file',log))
                        
        if not isinstance(outputfile,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createcohbmp.__name__,__file__,__copyright__,
                        'outputfile','str',log))       

        if not isinstance(mlran,int):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createcohbmp.__name__,__file__,__copyright__,
                        'mlran','int',log))
        
        if not isinstance(mlazi,int):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createcohbmp.__name__,__file__,__copyright__,
                        'mlazi','int',log))   
                
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createcohbmp.__name__,__file__,__copyright__,
                        'verbose','bool',log))
        
        list_colormap = []
        for li in glob.glob(os.path.dirname(__file__)+os.sep+'..'+os.sep+'..'+os.sep+'..'+os.sep+'tools'+os.sep+'colormap'+os.sep+'*.csv'): 
                list_colormap.append(li.split(os.sep)[-1].split('.')[0].replace('cmap_',''))
        if not colormap in list_colormap: 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createcohbmp.__name__,__file__,__copyright__,
                        'colormap','%s' % (list_colormap),log))
        
        usermessage.openingmsg(__name__,createcohbmp.__name__,__file__,__copyright__,'Create an coherence .bmp image',log,verbose)

        # Open the files
        usermessage.ezprint('Open the files:',log,verbose)
        fimag = gdal.Open(file)
        coherence = fimag.GetRasterBand(1).ReadAsArray().astype(float)
        fimag = None

        # Compute the multilook
        if (not mlran == 1) and (not mlazi == 1):
                usermessage.ezprint('Multilooking: %s/%s' % (mlran,mlazi),log,verbose)
                coherence = block_reduce(coherence, block_size=(mlazi,mlran), func=np.nanmean, cval=0) # multilooking
                usermessage.ezprint('\tdone',log,verbose)

        coherence[coherence==0] = np.nan

        # Add the colormap 
        usermessage.ezprint('Apply the colormap %s:' % (colormap),log,verbose)
        color = np.loadtxt(glob.glob(os.path.dirname(__file__)+os.sep+'..'+os.sep+'..'+os.sep+'..'+os.sep+'tools'+os.sep+'colormap'+os.sep+'cmap_'+colormap+'.csv')[0])
        newcmp = ListedColormap(color/255)
        data = np.uint8(newcmp(coherence)[:, :, :-1]*255)
        usermessage.ezprint('\tdone',log,verbose)

        # Saving 
        usermessage.ezprint('Write the file %s:' % (outputfile),log,verbose)
        imsave(outputfile,data)
        usermessage.ezprint('\tdone',log,verbose)

################################################################################
## Create unwrapped .bmp
################################################################################
def createunwbmp(file,
        outputfile,
        mlran, 
        mlazi,
        colormap: Optional[str] = 'jet',
        verbose: Optional[bool] = True,
        log: Optional[str] = None,
        ):
        """Create an unwrapped-interferogram .bmp image

        The function will compute a .bmp images of unwrapped interferograms.

        Args:
                file (str): Path of the coherence file
                outputfile (str): Fullpath of the output file
                mlran (int): Multilooking factor in range
                mlazi (int): Multilooking factor in azimut
                colormap (str): Colormap [default: jet]
                verbose (bool): verbose [Default: `None`].
                log (str): log [Default: `None`].

        """

        if not os.path.isfile(file):
                        raise TypeError(usermessage.typeerrormsg(
                        __name__,createcohbmp.__name__,__file__,__copyright__,
                        'file','.img file',log))
                        
        if not isinstance(outputfile,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createcohbmp.__name__,__file__,__copyright__,
                        'outputfile','str',log))       

        if not isinstance(mlran,int):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createcohbmp.__name__,__file__,__copyright__,
                        'mlran','int',log))
        
        if not isinstance(mlazi,int):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createcohbmp.__name__,__file__,__copyright__,
                        'mlazi','int',log))   
                
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createcohbmp.__name__,__file__,__copyright__,
                        'verbose','bool',log))
        
        list_colormap = []
        for li in glob.glob(os.path.dirname(__file__)+os.sep+'..'+os.sep+'..'+os.sep+'..'+os.sep+'tools'+os.sep+'colormap'+os.sep+'*.csv'): 
                list_colormap.append(li.split(os.sep)[-1].split('.')[0].replace('cmap_',''))
        if not colormap in list_colormap: 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,createcohbmp.__name__,__file__,__copyright__,
                        'colormap','%s' % (list_colormap),log))
        
        usermessage.openingmsg(__name__,createcohbmp.__name__,__file__,__copyright__,'Create an coherence .bmp image',log,verbose)

        # Open the files
        usermessage.ezprint('Open the files:',log,verbose)
        fimag = gdal.Open(file)
        unw = fimag.GetRasterBand(1).ReadAsArray().astype(float)
        fimag = None 

        unw[unw==0] = np.nan
        unw[np.abs(unw)<=1e-3] = np.nan
        # fact = 5
        # unw = (unw - (np.nanmean(unw)-fact*np.nanstd(unw)) / ( (np.nanmean(unw)+fact*np.nanstd(unw)) - np.nanmean(unw)-fact*np.nanstd(unw)))
        unw = (unw - np.nanmin(unw)) / (np.nanmax(unw) - np.nanmin(unw))

        # Add the colormap 
        usermessage.ezprint('Apply the colormap %s:' % (colormap),log,verbose)
        color = np.loadtxt(glob.glob(os.path.dirname(__file__)+os.sep+'..'+os.sep+'..'+os.sep+'..'+os.sep+'tools'+os.sep+'colormap'+os.sep+'cmap_'+colormap+'.csv')[0])
        newcmp = ListedColormap(color/255)
        data = np.uint8(newcmp(unw)[:, :, :-1]*255)
        usermessage.ezprint('\tdone',log,verbose)

        # Saving 
        usermessage.ezprint('Write the file %s:' % (outputfile),log,verbose)
        imsave(outputfile,data)
        usermessage.ezprint('\tdone',log,verbose)

################################################################################
## Conversion from ENVI format to geotiff for SNAP
################################################################################
def ENVI2geotiff(file,
        outputfile,
        coherencefile: Optional[str] = None,
        cohthreshold: Optional[float] = 0.2,
        shadowfile: Optional[str] = None,
        format: Optional[str] = 'GTiff', 
        srscode: Optional[int] = 4326,
        nodata: Optional[Union[int,float]] = 0,
        verbose: Optional[bool] = True,
        log: Optional[str] = None,
        ):
        """Convert ENVI-format images from SNAP to geotiff after geocoding. 

        The function will convert the ENVI-format images from SNAP to geotiff after geocoding. 

        Args:
                file (str): Path of the coherence file
                outputfile (str): Fullpath of the output file
                coherencefile (str): Fullpath of the coherence image for masking. [Default: None]. If None, no masking will be applied. 
                cohthreshold (float): Coherence threshold for masking [Default: 0.2]
                shadowfile (str): Fullpath of the shadow/layover image for masking. [Default: None]. If None, no masking will be applied. 
                format (str): Format of output. [Default: GTiff]
                srscode (int): SRS code (not used). [Default: 4326]
                nodata (int or float): No-data value. [Default: 0]
                verbose (bool): verbose [Default: `None`].
                log (str): log [Default: `None`].

        """

        if not os.path.isfile(file):
                        raise TypeError(usermessage.typeerrormsg(
                        __name__,ENVI2geotiff.__name__,__file__,__copyright__,
                        'file','.img file',log))

        if not coherencefile == None:
                if not os.path.isfile(coherencefile):
                        raise TypeError(usermessage.typeerrormsg(
                        __name__,ENVI2geotiff.__name__,__file__,__copyright__,
                        'coherencefile','.img file',log))
        
        if not shadowfile == None:
                if not os.path.isfile(shadowfile):
                        raise TypeError(usermessage.typeerrormsg(
                        __name__,ENVI2geotiff.__name__,__file__,__copyright__,
                        'shadowfile','.img file',log))
                        
        if not isinstance(outputfile,str):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ENVI2geotiff.__name__,__file__,__copyright__,
                        'outputfile','str',log))       

        if not isinstance(cohthreshold,float):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ENVI2geotiff.__name__,__file__,__copyright__,
                        'cohthreshold','float',log))
        
        if not (isinstance(nodata,int) or isinstance(nodata,float)):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ENVI2geotiff.__name__,__file__,__copyright__,
                        'nodata','int or float',log))
                
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,ENVI2geotiff.__name__,__file__,__copyright__,
                        'verbose','bool',log))

        usermessage.openingmsg(__name__,ENVI2geotiff.__name__,__file__,__copyright__,'Convert the ENVI file to GTiff',log,verbose)
       
        fimag = gdal.Open(file)
        data = fimag.GetRasterBand(1).ReadAsArray().astype(float)
        fimag = None 

        if  not coherencefile == None:
                fimag = gdal.Open(coherencefile)
                datacoh = fimag.GetRasterBand(1).ReadAsArray().astype(float)
                fimag = None
                data[datacoh<=cohthreshold] = nodata

        if not shadowfile == None:
                fimag = gdal.Open(shadowfile)
                datashadow = fimag.GetRasterBand(1).ReadAsArray().astype(float)
                fimag = None
                data[datashadow!=0] = nodata

        src_ds = gdal.Open(file)
        nx = data.shape[0]
        ny = data.shape[1]

        dst_ds = gdal.GetDriverByName(format).Create(outputfile, ny, nx, 1, gdal.GDT_Float32)

        dst_ds.SetGeoTransform(list(src_ds.GetGeoTransform()))                     # specify coords
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(srscode)                                     # WGS84 lat/long
        dst_ds.SetProjection(srs.ExportToWkt())                         # export coords to file
        dst_ds.GetRasterBand(1).WriteArray(data)                   # write r-band to the raster
        dst_ds.GetRasterBand(1).SetNoDataValue(nodata)                  # No-data value
        dst_ds.SetMetadata({"AREA_OR_POINT": "Area","TIFFTAG_SOFTWARE": "Created with EZ-InSAR %s %s" % (constants.__version__,constants.__copyright__)})
        dst_ds.FlushCache()                                             # write to disk
        dst_ds = None        
        src_ds = None

        usermessage.ezprint('Done for the file %s' % (outputfile) ,log,verbose)
        