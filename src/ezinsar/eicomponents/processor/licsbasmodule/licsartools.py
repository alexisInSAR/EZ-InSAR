#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module for downloading LICSAR data from the COMET server

The module adds some tools to interact with the LICSAR data from the COMET server.
    
    (From `ezinsar` package)

Changelog:
        * 1.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
from osgeo import gdal, osr
import numpy as np
from datetime import datetime
from shapely.wkt import loads
from typing import Optional, Union 
from shapely.geometry import Polygon
import urllib
import urllib.request
import re
import os 
import requests
from clint.textui import progress
from tqdm import tqdm

from ezinsar import usermessage
from ezinsar import constants
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Env variable 
################################################################################
__timeout_LICSAR__ = 1000
"""int: Time out in seconds for feching orbit files from the LICSAR server
"""

################################################################################
## Interpolation of InSAR products into a DEM grid
################################################################################
def downloadInSARproducts(link, 
        outputdir, 
        date1: Optional[datetime.date] = datetime.strptime('2015-01-01T00:00:00.000100Z','%Y-%m-%dT%H:%M:%S.%fZ'), 
        date2: Optional[datetime.date] = datetime.now(), 
        products: Optional[list] = ['cc','diff','diff_unfiltered','unw'],
        epochs: Optional[bool] = True, 
        metadata: Optional[bool] = True, 
        LiCSBASprep: Optional[bool] = True,
        verbose: Optional[bool] = True, 
        log: Optional[Union[str,None]] = None,
        ):
        """Download the LICSAR data from the public server

        The function will download the LICSAR data from the public server. 

        Args:
                link (list of str): Code for the pass and the frame, e.g., ['74','074A_03683_192021']
                outputdir (str): Output directory 
                date1 (any): First date for the SLC checking in `datetime` format [Default: ``datetime.strptime('2015-01-01T00:00:00.000100Z','%Y-%m-%dT%H:%M:%S.%fZ')``].
                date2 (any): Last date for the SLC checking in `datetime` format [Default: `datetime.now()`].
                products (list): List of InSAR products needed to be donwloaded. [Default: ['cc','diff','diff_unfiltered','unw']]
                epochs (bool): Donwload the epochs directory [default: `True`]
                metadata (bool): Donwload the metadata directory [default: `True`]
                LiCSBASprep (bool): Create the directories for LICSBAS [default: `True`]
                verbose (bool, Optional): verbose [Default: `True`].
                log (str): Log file [Default: `None`].

        """

        ## Check the input parameters
        if not isinstance(link,list): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,downloadInSARproducts.__name__,__file__,__copyright__,
                        'link','list',log))
        
        if not isinstance(outputdir,str): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,downloadInSARproducts.__name__,__file__,__copyright__,
                        'outputdir','str',log))
        
        if not isinstance(products,list): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,downloadInSARproducts.__name__,__file__,__copyright__,
                        'products','list',log))
        
        if not isinstance(epochs,bool): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,downloadInSARproducts.__name__,__file__,__copyright__,
                        'epochs','bool',log))
        
        if not isinstance(metadata,bool): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,downloadInSARproducts.__name__,__file__,__copyright__,
                        'metadata','bool',log))
        
        if not isinstance(LiCSBASprep,bool): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,downloadInSARproducts.__name__,__file__,__copyright__,
                        'LiCSBASprep','bool',log))
        
        if not isinstance(verbose,bool): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,downloadInSARproducts.__name__,__file__,__copyright__,
                        'verbose','bool',log))

        usermessage.openingmsg(__name__,downloadInSARproducts.__name__,__file__,__copyright__,'Download InSAR prodcuts from the LICSAR server',log,verbose)

        ## Display the file parameters for the user
        usermessage.ezprint('Input parameter parameters:',log,verbose) 
        usermessage.ezprint('\tRelative Orbit: %s' % (link[0]),log,verbose) 
        usermessage.ezprint('\tFrame: %s' % (link[1]),log,verbose) 
        usermessage.ezprint('\tOuput directory: %s' % (outputdir),log,verbose) 
        usermessage.ezprint('\tProducts: %s' % (products),log,verbose) 
        usermessage.ezprint('\tDownload the epochs: %s' % (epochs),log,verbose) 
        usermessage.ezprint('\tDownload the metadata: %s' % (metadata),log,verbose) 

        ## Create the link for downloading 
        data = {'link': [], 'output': []}

        usermessage.ezprint('Create the links for downloading:',log,verbose) 

        if epochs == True: 
                usermessage.ezprint('\tFor the epochs directory',log,verbose) 
                
                url_precise = "https://gws-access.jasmin.ac.uk/public/nceo_geohazards/LiCSAR_products/%s/%s/epochs/" % (link[0],link[1])
                html = urllib.request.urlopen(url_precise, timeout = __timeout_LICSAR__)
                text = html.read()
                plaintext = text.decode('utf8')
                links = re.findall("href=[\"\'](.*?)[\"\']", plaintext)
                dates = []

                for linki in links: 
                        try: 
                                di = datetime.strptime(linki.replace('/',''),'%Y%m%d')

                                if di >= date1 and di <= date2:
                                        dates.append(linki.replace('/',''))
                        except:
                                a = 'dummy'

                if dates: 
                        for di in dates:
                                url_precise = "https://gws-access.jasmin.ac.uk/public/nceo_geohazards/LiCSAR_products/%s/%s/epochs/%s/" % (link[0],link[1],di)
                                html = urllib.request.urlopen(url_precise, timeout = __timeout_LICSAR__)
                                text = html.read()
                                plaintext = text.decode('utf8')
                                links = re.findall("href=[\"\'](.*?)[\"\']", plaintext)
                                for linki in links: 
                                        if linki.endswith('.png') or linki.endswith('.tif') or linki.endswith('.xml'): 
                                              data['link'].append(url_precise + linki)
                                              data['output'].append(outputdir+os.sep+'epochs'+os.sep+di+os.sep+linki)

                usermessage.ezprint('\t\tdone',log,verbose) 

        if metadata == True: 
                usermessage.ezprint('\tFor the metadata directory',log,verbose) 

                url_precise = "https://gws-access.jasmin.ac.uk/public/nceo_geohazards/LiCSAR_products/%s/%s/metadata/" % (link[0],link[1])
                html = urllib.request.urlopen(url_precise, timeout = __timeout_LICSAR__)
                text = html.read()
                plaintext = text.decode('utf8')
                links = re.findall("href=[\"\'](.*?)[\"\']", plaintext)

                for linki in links: 
                        if linki.endswith('.png') or linki.endswith('.tif') or linki.endswith('.xml')  or linki.endswith('.txt') or linki == 'baselines':
                                data['link'].append(url_precise + linki)
                                data['output'].append(outputdir+os.sep+'metadata'+os.sep+os.sep+linki)

                usermessage.ezprint('\t\tdone',log,verbose) 

        usermessage.ezprint('\tFor the interferogram directory',log,verbose)
        url_precise = "https://gws-access.jasmin.ac.uk/public/nceo_geohazards/LiCSAR_products/%s/%s/interferograms/" % (link[0],link[1])
        html = urllib.request.urlopen(url_precise, timeout = __timeout_LICSAR__)
        text = html.read()
        plaintext = text.decode('utf8')
        links = re.findall("href=[\"\'](.*?)[\"\']", plaintext)
        dates = []

        for linki in links: 
                try: 
                        di1 = datetime.strptime(linki.replace('/','').split('_')[0],'%Y%m%d')
                        di2 = datetime.strptime(linki.replace('/','').split('_')[1],'%Y%m%d')

                        if di1 >= date1 and di1 <= date2 and di2 >= date1 and di2 <= date2:
                                dates.append(linki.replace('/',''))
                except:
                        a = 'dummy'

        if dates: 
                for di in dates:
                        url_precise = "https://gws-access.jasmin.ac.uk/public/nceo_geohazards/LiCSAR_products/%s/%s/interferograms/%s/" % (link[0],link[1],di)
                        html = urllib.request.urlopen(url_precise, timeout = __timeout_LICSAR__)
                        text = html.read()
                        plaintext = text.decode('utf8')
                        links = re.findall("href=[\"\'](.*?)[\"\']", plaintext)

                        for linki in links: 
                                if linki.endswith('.png') or linki.endswith('.tif') or linki.endswith('.xml'): 
                                        check=False
                                        for producti in products: 
                                                if producti in linki: 
                                                        check=True
                                        if check: 
                                                data['link'].append(url_precise + linki)
                                                data['output'].append(outputdir+os.sep+'interferograms'+os.sep+di+os.sep+linki)
        usermessage.ezprint('\t\tdone',log,verbose) 
        
        if LiCSBASprep: 
                usermessage.ezprint('Modification of the directory for LiCSBAS compliance',log,verbose)

                for idx, a in enumerate(data['link']):
                        if 'geo.mli' in data['output'][idx] and os.sep+'epochs'+os.sep in data['output'][idx]: 
                                di = data['output'][idx].split(os.sep)[-1].split('.')[0]
                                data['output'][idx] = data['output'][idx].replace(os.sep+'epochs'+os.sep,os.sep+'GEOC.MLI'+os.sep).replace(di+os.sep,'')

                        elif 'geo' in data['output'][idx] and os.sep+'metadata'+os.sep in data['output'][idx]: 
                                data['output'][idx] = data['output'][idx].replace(os.sep+'metadata'+os.sep,os.sep+'GEOC'+os.sep)

                        elif 'metadata.txt' in data['output'][idx] or 'baselines' in data['output'][idx] or 'network.png' in data['output'][idx] or data['link'][idx].split('/')[-1].endswith('-poly.txt'):
                                data['output'][idx] = data['output'][idx].replace(os.sep+'metadata'+os.sep,os.sep+'GEOC'+os.sep)

                        else:# ('interferogram' in data['output'] or 'geo' in data['output'] or 'metadata.txt' in data['output'] or 'baselines' in data['output']) 
                                di = data['output'][idx].split(os.sep)[-1].split('.')[0]
                                data['output'][idx] = data['output'][idx].replace(os.sep+'interferograms'+os.sep,os.sep+'GEOC'+os.sep).replace(di+os.sep,'')
        
                ## Copy the first date in GEOC
                if epochs: 
                        idx = 0
                        while not data['output'][idx].endswith('.tif'): 
                               idx = idx + 1 

                        data['link'].append(data['link'][idx])
                        data['output'].append(data['output'][idx].replace('GEOC.MLI','GEOC'))

                usermessage.ezprint('\tdone',log,verbose) 
        
        ## Print the links
        usermessage.ezprint('Print the links',log,verbose)
        for idx, a in enumerate(data['link']):
                usermessage.ezprint('\tFile [%d/%d]: %s => %s' % (idx+1,len(data['link']),data['link'][idx],data['output'][idx]),log,verbose)

        ## Download the link
        usermessage.ezprint('Download the files',log,verbose)
        session = requests.Session()

        for idx, a in enumerate(data['link']):

                usermessage.ezprint('\tFile [%d/%d]: %s => %s' % (idx+1,len(data['link']),data['link'][idx],data['output'][idx]),log,verbose)

                # Create the directory 
                if not os.path.isdir(os.path.dirname(data['output'][idx])):
                        os.makedirs(os.path.dirname(data['output'][idx]))

                success = False 
                required = False

                while success == False: 
                        response = session.get(data['link'][idx], stream=True)
                        total_length = int(response.headers.get('content-length'))

                        if os.path.isfile(data['output'][idx]): 
                                if not os.path.getsize(data['output'][idx]) == total_length: 
                                        required = True
                        else:
                                required = True 

                        if required: 
                                with open(data['output'][idx], "wb") as file:
                                        if verbose: 
                                                for chunk in progress.bar(response.iter_content(chunk_size=constants.__chunksize__), expected_size=(total_length/constants.__chunksize__) + 1): 
                                                        if chunk:
                                                                file.write(chunk)
                                        else: 
                                                for chunk in response.iter_content(chunk_size=constants.__chunksize__):
                                                        if chunk:
                                                                file.write(chunk)

                                if os.path.getsize(data['output'][idx]) == total_length: 
                                        success = True
                        else: 
                                success = True
                                usermessage.warningmsg(__name__,downloadInSARproducts.__name__,__file__,'Already downloaded',log,verbose) 

################################################################################
## Detection of the frame for the LiCSBAS processor
################################################################################
def detectframe(relorbit: Optional[int] = 1,
        satpass: Optional[str] = 'ASCENDING',
        date1: Optional[datetime.date] = datetime.strptime('2014-01-01T00:00:00.000100Z','%Y-%m-%dT%H:%M:%S.%fZ'), 
        date2: Optional[datetime.date] = datetime.now(), 
        roi: Optional[any] = None,
        job: Optional[any] = None, 
        bypassuser: Optional[bool] = True, 
        verbose: Optional[bool] = None, 
        log: Optional[Union[str,None]] = None,
        ):
        """Detect the frame based on user input or EZ-InSAR job

        The function will detect the LiCSAR frame. 

        Args:
                relorbit (int): Relative orbit [Default: 1]
                satpass (str): Satellite direction [Default: ASCENDING]
                date1 (any): First date for the SLC checking in `datetime` format [Default: ``datetime.strptime('2015-01-01T00:00:00.000100Z','%Y-%m-%dT%H:%M:%S.%fZ')``].
                date2 (any): Last date for the SLC checking in `datetime` format [Default: `datetime.now()`].
                roi (any): Region of Interest under the EZ-InSAR format [Default: None]
                job (any): EZ-InSAR job. [Default: None]. If not None, it will bypassed the other parameters
                bypassuser (bool): Ask the user for the selection. [Default: True]
                verbose (bool, Optional): verbose [Default: `True`].
                log (str): Log file [Default: `None`].

        Returns: 
                dict: Frame information    
        """
        if not job == None:
                if (not 'licsbastsprocessing.sbas' in str(type(job))): 
                        raise ValueError(usermessage.errormsg(__name__,detectframe.__name__,__file__,__copyright__,
                                'The job parameter is not a EZ-InSAR job/processing.',log))
                else:
                        if verbose == None:
                                verbose = job.verbose
                        if not isinstance(verbose,bool):
                                raise TypeError(usermessage.typeerrormsg(
                                        __name__,detectframe.__name__,__file__,__copyright__,
                                        'verbose','True or False',jobcoreg.log))
                        if log == None:
                                log = job.log

                        verbose = job.verbose
                        usermessage.warningmsg(__name__,detectframe.__name__,__file__,'A EZ-InSAR job has been given, all other parameters will be bypassed.',log,verbose) 

                        relorbit = job.relorbit
                        satpass = job.satpass
                        roi = loads(job.roi)
                        date1 = datetime.strptime(job.date1,'%Y%m%d')
                        date2 = datetime.strptime(job.date2,'%Y%m%d')

        if not isinstance(relorbit,int): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,detectframe.__name__,__file__,__copyright__,
                        'relorbit','int',log))
        
        if not satpass in ['ASCENDING','DESCENDING']:
                raise TypeError(usermessage.typeerrormsg(
                        __name__,detectframe.__name__,__file__,__copyright__,
                        'satpass','ASCENDING or DESCENDING',log))

        if not isinstance(bypassuser,bool): 
                raise TypeError(usermessage.typeerrormsg(
                        __name__,detectframe.__name__,__file__,__copyright__,
                        'bypassuser','bool',log))

        usermessage.openingmsg(__name__,detectframe.__name__,__file__,__copyright__,'Detect the LiCSAR frame(s) for LiCSBAS processor',log,verbose)

        ## Display the file parameters for the user
        usermessage.ezprint('Input parameter parameters:',log,verbose) 
        usermessage.ezprint('\tRelative Orbit: %s' % (relorbit),log,verbose) 
        usermessage.ezprint('\tSatellite Pass: %s' % (satpass),log,verbose) 
        usermessage.ezprint('\tROI: %s' % (roi),log,verbose) 
        usermessage.ezprint('\tDate 1: %s' % (date1),log,verbose) 
        usermessage.ezprint('\tDate 2: %s' % (date2),log,verbose) 

        ## Detection of the available frames
        usermessage.ezprint('Detect the available frames',log,verbose) 

        url_precise = "https://gws-access.jasmin.ac.uk/public/nceo_geohazards/LiCSAR_products/%s/" % (relorbit)
        html = urllib.request.urlopen(url_precise, timeout = __timeout_LICSAR__)
        text = html.read()
        plaintext = text.decode('utf8')
        links = re.findall("href=[\"\'](.*?)[\"\']", plaintext)

        frames = []
        for linki in links:
                if len(linki.replace('/','').split('_')) == 3 and (not 'backup' in linki):
                        if '%s%s' % (relorbit,satpass[0]) in linki:
                                frames.append(linki.replace('/',''))

        if not frames:
                usermessage.warningmsg(__name__,detectframe.__name__,__file__,'No frames have been detected for the user inputs..',log,verbose) 
                return {'frame': None}

        usermessage.ezprint('\tdone',log,verbose) 

        ## Read the metadata
        usermessage.ezprint('Read the metadata from the LiCSAR server',log,verbose) 

        listdata = []

        for framei in tqdm(frames): 
                # usermessage.ezprint('\tFor the frame %s' % (framei),log,verbose) 

                try: 
                        data = {}
                        data['frame'] = framei

                        # Read the extents 
                        # usermessage.ezprint('\t\tRead the extents',log,verbose) 
                        url_precise = "https://gws-access.jasmin.ac.uk/public/nceo_geohazards/LiCSAR_products/%s/%s/metadata/%s-poly.txt" % (relorbit,framei,framei)
                        html = urllib.request.urlopen(url_precise, timeout = __timeout_LICSAR__)
                        text = html.read()
                        plaintext = text.decode('utf8').strip()

                        data['lon'] = []
                        data['lat'] = []
                        for fi in plaintext.split('\n'):
                                data['lon'].append(float(fi.split()[0]))
                                data['lat'].append(float(fi.split()[1]))

                        # Read the baselines 
                        # usermessage.ezprint('\t\tRead the baselines',log,verbose) 
                        url_precise = "https://gws-access.jasmin.ac.uk/public/nceo_geohazards/LiCSAR_products/%s/%s/metadata/baselines" % (relorbit,framei)
                        html = urllib.request.urlopen(url_precise, timeout = __timeout_LICSAR__)
                        text = html.read()
                        plaintext = text.decode('utf8').strip()

                        data['baselines'] = []
                        data['dates'] = []
                        for fi in plaintext.split('\n'):
                                data['baselines'].append(fi)
                        
                        data['dates'] = []
                        for li in data['baselines']:
                                data['dates'].append(li.split()[0])
                                data['dates'].append(li.split()[1])
                        data['dates'] = np.sort(np.unique(data['dates']))

                        # Read the gaps 
                        # usermessage.ezprint('\t\tRead the gaps',log,verbose) 
                        data['gaps'] = []
                        url_precise = "https://gws-access.jasmin.ac.uk/public/nceo_geohazards/LiCSAR_products/%s/%s/metadata/gaps.txt" % (relorbit,framei)
                        try:
                                html = urllib.request.urlopen(url_precise, timeout = __timeout_LICSAR__)
                                text = html.read()
                                plaintext = text.decode('utf8').strip()
                        except: 
                                data['gaps'] = None

                        if not data['gaps'] == None:
                                for fi in plaintext.split('\n'):
                                        data['gaps'].append(fi)

                        # Read the gaps 
                        # usermessage.ezprint('\t\tRead the ifg lacks',log,verbose) 
                        data['lackifg'] = []
                        url_precise = "https://gws-access.jasmin.ac.uk/public/nceo_geohazards/LiCSAR_products/%s/%s/metadata/lackifg.txt" % (relorbit,framei)
                        try:
                                html = urllib.request.urlopen(url_precise, timeout = __timeout_LICSAR__)
                                text = html.read()
                                plaintext = text.decode('utf8').strip()
                        except: 
                                data['lackifg'] = None

                        if not data['lackifg'] == None:
                                for fi in plaintext.split('\n'):
                                        data['lackifg'].append(fi)

                        # Read the metadata 
                        # usermessage.ezprint('\t\tRead the metadata',log,verbose) 
                        data['metadata'] = {}
                        url_precise = "https://gws-access.jasmin.ac.uk/public/nceo_geohazards/LiCSAR_products/%s/%s/metadata/metadata.txt" % (relorbit,framei)
                        try:
                                html = urllib.request.urlopen(url_precise, timeout = __timeout_LICSAR__)
                                text = html.read()
                                plaintext = text.decode('utf8').strip()
                        except: 
                                data['metadata'] = None

                        if not data['metadata'] == None:
                                for fi in plaintext.split('\n'):
                                        data['metadata'][fi.split('=')[0]] = fi.split('=')[1]

                        listdata.append(data)

                except:
                        usermessage.warningmsg(__name__,detectframe.__name__,__file__,'No full metadata data for the frame %s. It will be removed.' % (framei),log,verbose) 
        
        usermessage.ezprint('\tdone',log,verbose)
        
        ## Analyse
        usermessage.ezprint('Analyse the frames according to the user inputs',log,verbose) 

        if not listdata:
                usermessage.warningmsg(__name__,detectframe.__name__,__file__,'No frames have been detected for the user inputs..',log,verbose) 
                return {'frame': None}
        
        #IDX POLY INTERsection-TIME LACKIFGS DURATION
        framearray = np.empty([len(listdata),5])
        for idx, framei in enumerate(listdata):
                polyframe = Polygon(list(zip(framei['lon'],framei['lat'])))
                
                framearray[idx,0] = idx

                # Poly-intersection
                polyframe = Polygon(list(zip(framei['lon'],framei['lat'])))
                framearray[idx,1] = (polyframe.intersection(roi).area)/(roi.area)*100
                
                # Temporal intersection (using Polygon method)
                xmin = date1.timestamp()
                xmax = date2.timestamp()
                ymin = 0
                ymax = 1000
                polyuser = Polygon([
                        [xmin, ymin], 
                        [xmax, ymin], 
                        [xmax, ymax],
                        [xmin, ymax],
                        [xmin, ymin], 
                        ])

                xmin = datetime.strptime(framei['dates'][0],'%Y%m%d').timestamp()
                xmax = datetime.strptime(framei['dates'][-1],'%Y%m%d').timestamp()
                ymin = 0
                ymax = 1000
                polyLiCSAR = Polygon([
                        [xmin, ymin], 
                        [xmax, ymin], 
                        [xmax, ymax],
                        [xmin, ymax],
                        [xmin, ymin], 
                        ])

                AREA_LiCSAR = polyLiCSAR.intersection(polyuser).area

                durationgaps = 0
                if not framei['gaps'] == None:
                        for li in framei['gaps']: 
                                if datetime.strptime(li.split('_')[0],'%Y%m%d') >= date1 and datetime.strptime(li.split('_')[1],'%Y%m%d') <= date2:
                                        xmin = datetime.strptime(li.split('_')[0],'%Y%m%d').timestamp()
                                        xmax = datetime.strptime(li.split('_')[1],'%Y%m%d').timestamp()
                                        ymin = 0
                                        ymax = 1000
                                        polygapi = Polygon([
                                                [xmin, ymin], 
                                                [xmax, ymin], 
                                                [xmax, ymax],
                                                [xmin, ymax],
                                                [xmin, ymin], 
                                        ])
                                        AREA_LiCSAR = AREA_LiCSAR - (polygapi.area)

                                        durationgaps = durationgaps + (datetime.strptime(li.split('_')[1],'%Y%m%d')-datetime.strptime(li.split('_')[0],'%Y%m%d')).days

                framearray[idx,2] = (AREA_LiCSAR/(polyuser.area))*100

                # LACKIFGS
                if not framei['lackifg'] == None:
                        framearray[idx,3] = len(framei['lackifg'])
                else: 
                        framearray[idx,3] = 0

                # Duration 
                framearray[idx,4] = (datetime.strptime(framei['dates'][-1],'%Y%m%d')-datetime.strptime(framei['dates'][0],'%Y%m%d')).days
                
        # Sorting
        framearray = framearray[-framearray[:,4].argsort()]
        framearray = framearray[framearray[:,3].argsort(kind='mergesort')]
        framearray = framearray[-framearray[:,2].argsort(kind='mergesort')]
        framearray = framearray[-framearray[:,1].argsort(kind='mergesort')]

        listframesorted = []
        idxdeleted = []
        for h, idx in enumerate(framearray[:,0]):
                if not np.fix(framearray[h,1]) == 0:
                        listframesorted.append(listdata[int(framearray[h,0])])
                else:
                        idxdeleted.append(h)
        
        framearray = np.delete(framearray,idxdeleted,axis=0)
        usermessage.ezprint('\tdone',log,verbose)

        ## Analyse
        usermessage.ezprint('Print the results',log,verbose) 

        if framearray[0,1] == 0:
                usermessage.warningmsg(__name__,detectframe.__name__,__file__,'No frames have been detected for the user inputs..',log,verbose) 
                return {'frame': None}

        for idx, framei in enumerate(listframesorted):
                if idx == 0:
                        recom = '(RECOMMENDED by EZ-InSAR)'
                else:
                        recom = ''
                usermessage.ezprint('\tFor the frame %s %s' % (framei['frame'],recom),log,verbose) 

                usermessage.ezprint('\t\tThe spatial intersection is %0.1f %%.' % (framearray[idx,1]),log,verbose)
                usermessage.ezprint('\t\tThe temporal intersection is %0.1f %%.' % (framearray[idx,2]),log,verbose)
                usermessage.ezprint('\t\t\tFirst date of the LiCSAR data: %s' % (framei['dates'][0]),log,verbose)
                usermessage.ezprint('\t\t\tLast date of the LiCSAR data: %s' % (framei['dates'][-1]),log,verbose)
                usermessage.ezprint('\t\t\tDuration [in years]: %0.1f' % (framearray[idx,4]/365.25),log,verbose)
                if framei['gaps'] == None:
                        usermessage.ezprint('\t\tGaps: None',log,verbose)
                else:   
                        usermessage.ezprint('\t\tGaps:',log,verbose)
                        for li in framei['gaps']:
                                usermessage.ezprint('\t\t\t %s - %s' % (li.split('_')[0],li.split('_')[1]),log,verbose)
                if framei['lackifg'] == None:
                        usermessage.ezprint('\t\tInteferogram(s) missing: None',log,verbose)
                else: 
                        usermessage.ezprint('\t\tInteferogram(s) missing:',log,verbose)
                        for li in framei['lackifg']:
                                usermessage.ezprint('\t\t\t %s - %s' % (li.split('_')[0],li.split('_')[1]),log,verbose)

                usermessage.ezprint('\t\tMetadata:',log,verbose)
                for ki in list(framei['metadata'].keys()):
                        usermessage.ezprint('\t\t\t%s: %s' % (ki,framei['metadata'][ki]),log,verbose)

        ## USER SELECTION
        if bypassuser == False:
                usermessage.ezprint('\nUser selection:',log,verbose) 

                for idx, framei in enumerate(listframesorted):
                        if idx == 0:
                                recom = '(RECOMMENDED by EZ-InSAR)'
                        else:
                                recom = ''
                        usermessage.ezprint('\t%s) for the frame %s %s' % (idx, framei['frame'],recom),log,verbose)

                listidx = [str(x) for x,a in enumerate(list(framearray[:,0]))]
                idxbest = 'dummy'
                while not idxbest in listidx:
                        idxbest = input('\nPlease select the frame => ') 
                idxbest = int(idxbest)
        else:
                idxbest = 0

        # ## Saving 
        dataframe = listframesorted[idxbest]
        usermessage.ezprint('The frame %s has been selected.' % (dataframe['frame']),log,verbose) 

        return dataframe
        
        