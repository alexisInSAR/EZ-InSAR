#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""Module to create and control the detection of Sentinel-1 bursts from the ID maps

The module contains a class, different methods, and functions to run the `S1burstIDmap`
class.

    (From `ezinsar` package)

Changelog:
    * 3.3.1: Check the check method, Dec. 2025, Alexis Hrysiewicz
    * 3.2.2: Delete the support of wget and storage in cache, Alexis Hrysiewicz, Sep. 2025
    * 1.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################ 
import datetime 
import os 
import zipfile
import urllib.request  
import numpy as np
import fiona 
from alive_progress import alive_bar
import glob 
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from typing import Optional, Union

from ezinsar import constants
from ezinsar import usermessage
from ezinsar.tools import miscellaneous

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Creation of a class to manage the Sentinel-1 burst ID map
################################################################################
class S1burstIDmap:
    """`S1burstIDmap` class.

    Attributes:
        date_str_init (str, Optional): Initial date to find the ID map [Default: '29/05/2022']
        dirmap (str, Optional): Path of the ID-map directory [Default: __file__]
        pathIDmap (str, Optional): Path of the ID map [Default: None]
        verbose (bool, Optional): Verbose [Default: True]

    """

    ################################################################################
    ## Initialistion of the class
    ################################################################################
    def __init__(self,
        date_str_init: Optional[str] = '29/05/2022',
        dirmap: Optional[Union[str, None]] = None,
        pathIDmap: Optional[Union[str, None]] = None, 
        verbose: Optional[bool] = True,
        ):
        """Initialisation of the `S1burstIDmap` class.

        Args:
            date_str_init (str, Optional): Initial date to find the ID map [Default: '29/05/2022']
            dirmap (str, Optional): Path of the ID-map directory [Default: __file__]
            pathIDmap (str, Optional): Path of the ID map [Default: None]
            verbose (bool, Optional): Verbose [Default: True]

        """

        # ID maps parameters
        self.date_str_init = date_str_init
        if dirmap == None:
            dirmap = __file__
            self.dirmap = constants.__cachedir__+os.sep
        else: 
            self.dirmap = dirmap
            
        self.pathIDmap = pathIDmap
        self.verbose = verbose

        self.list_date = []

        self.Data = dict()
        self.Report = dict()

        # Check the map
        self.checkfile(verbose=False)

    ################################################################################
    ## Function to print the attributes
    ################################################################################
    def print(self):
        """Print the attributes for `S1burstIDmap`

        The method display a unstructured text of the job attributes.

        Returns:
            `S1burstIDmap`: Return the `S1burstIDmap` used

        """
        attrs = vars(self)
        print(', '.join("%s: %s" % item for item in attrs.items()))

        return self
    
    ################################################################################
    ## Check the avaibility of the maps
    ################################################################################
    def checkfile(self,verbose: Optional[bool] = None):
        """Check the last S1 ID map`

        The method checks the last available S1 ID map.

        Args: 
            verbose (bool, Optional): Verbose [Default: None]

        Returns:
            `S1burstIDmap`: Return the `S1burstIDmap` used

        """

        if verbose == None:
                verbose = self.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,self.checkfile.__name__,__file__,__copyright__,
                        'verbose','True or False',None))

        usermessage.openingmsg(__name__,self.checkfile.__name__,__file__,__copyright__,'Check the S1 ID map for detection of bursts',None,verbose)

        # Create the list of dates
        self.list_date = []; 
        datei = datetime.datetime.strptime(self.date_str_init, '%d/%m/%Y')

        while datei <=  datetime.datetime.now(): 
            datei = datei + datetime.timedelta(days=1)
            self.list_date.append(datei.strftime("%Y%m%d"))

        # Check if the directory exists
        for i1 in self.list_date:
            if os.path.isdir("%s/S1_burstid_%s" %(self.dirmap,i1)):
                self.pathIDmap = "%s/S1_burstid_%s" %(self.dirmap,i1)

                usermessage.ezprint('\tDetection of the directory: %s.' % (self.pathIDmap),None,verbose)

        if self.pathIDmap == None:
            usermessage.warningmsg(__name__,self.checkfile.__name__,__file__,'No detection of the directory...\n\tPlease download the .zip file.',None,verbose)
        
        return self
    
    ################################################################################
    ## Donwload the latest map
    ################################################################################
    def downloadfile(self,verbose: Optional[bool] = None): 
        """Download the last S1 ID map`

        The method downloads the last available S1 ID map.

        Args: 
            verbose (bool, Optional): Verbose [Default: None]

        Returns:
            `S1burstIDmap`: Return the `S1burstIDmap` used

        """

        if verbose == None:
                verbose = self.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,self.downloadfile.__name__,__file__,__copyright__,
                        'verbose','True or False',None))

        usermessage.openingmsg(__name__,self.downloadfile.__name__,__file__,__copyright__,'Download the S1 ID map for detection of bursts',None,verbose)

        h = 0
        while self.pathIDmap == None:
            i1 = self.list_date[h]
            try:
                status = urllib.request.urlopen("https://sar-mpc.eu/files/S1_burstid_%s.zip" %(i1)).getcode()
                self.pathIDmap = "https://sar-mpc.eu/files/S1_burstid_%s.zip" %(i1)
                usermessage.ezprint('\tCheck the https://sar-mpc.eu/files/S1_burstid_%s.zip link ==> DETECTED' %(i1),None,verbose)
            except:
                usermessage.ezprint('\tCheck the https://sar-mpc.eu/files/S1_burstid_%s.zip link ==> NO DETECTED' %(i1),None,verbose)

            h = h + 1
            if h == len(self.list_date):
                raise ValueError(usermessage.errormsg(__name__,self.downloadfile.__name__,__file__,__copyright__,'No detection of S1 burst ID map.',None))
            
            miscellaneous.download_file(self.pathIDmap,
                    output_file=self.dirmap+os.sep+self.pathIDmap.split('/')[-1],
                    verbose=verbose)
            
            usermessage.ezprint("\tUnzip the .zip file %s in %s" %(self.dirmap,i1),None,verbose)

            with zipfile.ZipFile("%s/S1_burstid_%s.zip" %(self.dirmap,i1), 'r') as zip_ref:
                zip_ref.extractall(self.dirmap)

            usermessage.ezprint("\tDelete the .zip file %s in %s" %(self.dirmap,i1),None,verbose)
            if os.path.isfile("%s/S1_burstid_%s.zip" %(self.dirmap,i1)): 
                os.remove("%s/S1_burstid_%s.zip" %(self.dirmap,i1))

        usermessage.ezprint('\tThe S1 burst ID map is in %s' % (self.pathIDmap),None,verbose)

        self.checkfile(verbose=False)

        return self
    
    ################################################################################
    ## Methods to detect the data regarding the burst IDs
    ################################################################################
    def detectfromIDmap(self,job,
        verbose: Optional[bool] = None, 
        Pass: Optional[Union[list,None]] = None,      
        Track: Optional[Union[list,None]] = None,                
        ):
        """Detect the S1 ID bursts

        The method detects the S1 ID bursts, satellite directions and track numbers
        regaridng the given `EIjob`. 

        Args: 
            job (EIjob): EZ-InSAR job
            verbose (bool, Optional): Verbose [Default: None]

        Returns:
            `S1burstIDmap`: Return the `S1burstIDmap` used

        """

        self.checkfile(verbose=False)

        if verbose == None:
                verbose = self.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(__name__,self.detectfromIDmap.__name__,__file__,__copyright__,
                    'verbose','True or False',None))

        usermessage.openingmsg(__name__,self.detectfromIDmap.__name__,__file__,__copyright__,'Detection the S1 track and pass from the S1 burst ID map',None,verbose)

        if not 'EIjob' in str(type(job)):
            raise ValueError(usermessage.errormsg(__name__,self.detectfromIDmap.__name__,__file__,__copyright__,
                'The job parameter is not a EZ-InSAR job.'),job.log,verbose)

        if not job.satellite == 'S1' and job.satmode == 'IW': 
            raise ValueError(usermessage.errormsg(__name__,self.detectfromIDmap.__name__,__file__,__copyright__,
                'The satellite must be S1 and IW acqution mode.'),job.log,verbose)

        # Detection of the initiale track and pass
        if Track == None:
            if not job.relorbit == None:
                Track_user = job.relorbit
            else:
                Track_user = None
        else: 
            Track_user = Track

        if Pass == None:
            if not job.satpass == None:
                Pass_user = job.satpass
            else:
                Pass_user = None
        else:
            Pass_user = Pass
            if isinstance(Pass_user,str):
                Pass_user = Pass_user.upper().split(',')
            for pii in Pass_user:
                if not (pii.upper() == 'ASCENDING' or pii.upper() == 'DESCENDING' or pii == None): 
                    raise ValueError(usermessage.errormsg(__name__,self.detectfromIDmap.__name__,__file__,__copyright__,
                        'The Pass argument can be ASCENDING or DESCENDING.'),job.log,verbose)

        # warnings.warn('The use of the S1 burst ID map is less accurate than the use of .xml S1 files.')
        usermessage.warningmsg(__name__,self.detectfromIDmap.__name__,__file__,'The use of the S1 burst ID map is less accurate than the use of .xml S1 files.',job.log,verbose)

        if not (isinstance(Track_user, list)):
            Track_user = [Track_user]
        if not isinstance(Pass_user, list):
            Pass_user = [Pass_user]

        if (isinstance(Track_user,list) and len(Pass_user)==1):
            Pass_usertmp = np.tile(Pass_user[0], [len(Track_user),1])
            Pass_user = []
            for i1 in Pass_usertmp:
                Pass_user.append(i1[0])

        if (isinstance(Track_user, list) and isinstance(Pass_user, list) and len(Track_user) !=1 and len(Pass_user) !=1): 
            if not len(Track_user) == len(Pass_user):
                raise ValueError(usermessage.errormsg(__name__,self.detectfromIDmap.__name__,__file__,__copyright__,
                        'The track and pass parameters do not have the same length.'),job.log,verbose)

        usermessage.ezprint('\tDetection of the S1 relative orbite and pass from:',job.log,verbose)

        for (tracki, passi) in zip(Track_user, Pass_user):
            usermessage.ezprint('\tThe S1 data with relative orbite of "%s" and direction "%s"' % (tracki,passi),job.log,verbose)

        # Read the kml files to detect the burst ID
        filesqlite = glob.glob('%s/IW/sqlite/*.sqlite3' % (self.pathIDmap))[-1]
            
        fiona.supported_drivers["SQLite"] = "r"

        usermessage.ezprint('Detection in progress...',job.log,verbose)

        h = 1
        with fiona.open(filesqlite) as shpfile:
            with alive_bar(len(shpfile)) as bar:
                for feature in shpfile:
                    polyburst = Polygon(feature['geometry']["coordinates"][0][0])

                    test_intersection = False
                    test_intersection = job.roi.intersects(polyburst)

                    if test_intersection:
                            
                        relative_orbit_number = feature['properties']['relative_orbit_number']
                        subswath_name = feature['properties']['subswath_name']
                        orbit_pass = feature['properties']['orbit_pass']
                        esa_burst_id = feature['properties']['burst_id']
                            
                        for (tracki, passi) in zip(Track_user, Pass_user):
                            if (tracki == relative_orbit_number or tracki == None) and (passi == orbit_pass or passi == None):
                                if not "%s_%04d" % (orbit_pass,relative_orbit_number) in self.Data:
                                    self.Data["%s_%04d" % (orbit_pass,relative_orbit_number)] = {'IW1': [], 
                                                                                                    'IW2': [],
                                                                                                    'IW3': []}
                                    
                                self.Data["%s_%04d" % (orbit_pass,relative_orbit_number)][subswath_name].append({'relative_orbit_number': relative_orbit_number, 
                                                                                                            'subswath_name': subswath_name, 
                                                                                                            'orbit_pass': orbit_pass, 
                                                                                                            'esa_burst_id': esa_burst_id, 
                                                                                                            'polyburst': polyburst})
                    bar()

        usermessage.ezprint('\tDONE',job.log,verbose)
        
        return self

    ################################################################################
    ## Methods to display the burst locations regarding the EZ-InSAR job
    ################################################################################
    def display(self,job,
            verbose: Optional[bool] = None,
            basemap: Optional[str] = 'World_Imagery',
            figure: Optional[Union[str,None]] = None):
        """Display the S1 bursts regarding the EZ-InSAR job

        The method displays the S1 bursts regarding the ``EIjob``.  

        Args:
                job (`EIjob`): EZ-InSAR job
                verbose (bool): verbose [Default: `None`]. If `None`, the function will use the value from the `EIjob` job.
                basemap (str): mode of the display [Default: ``extent``]. Can be ``NatGeo_World_Map``,``USA_Topo_Maps``,``World_Imagery``,``World_Physical_Map``,``World_Shaded_Relief``,``World_Street_Map``,``World_Terrain_Base``,``World_Topo_Map``
                figure (str): Path of the figure to save the figure [Default: ``None``]. If ``None``, the figure will be displayed.

        Returns:
                `S1burstIDmap`: Return an EZ-InSAR class 

        """  
        
        self.checkfile(verbose=False)

        if verbose == None:
                verbose = self.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(__name__,self.display.__name__,__file__,__copyright__,
                    'verbose','True or False',None))
        
        if not isinstance(basemap,str):
            raise TypeError(usermessage.typeerrormsg(__name__,self.display.__name__,__file__,__copyright__,
                'basemap','NatGeo_World_Map','USA_Topo_Maps','World_Imagery','World_Physical_Map','World_Shaded_Relief','World_Street_Map','World_Terrain_Base','World_Topo_Map',None))
        if not basemap in ['NatGeo_World_Map','USA_Topo_Maps','World_Imagery','World_Physical_Map','World_Shaded_Relief','World_Street_Map','World_Terrain_Base','World_Topo_Map']:
             raise TypeError(usermessage.typeerrormsg(__name__,self.display.__name__,__file__,__copyright__,
                'basemap','NatGeo_World_Map','USA_Topo_Maps','World_Imagery','World_Physical_Map','World_Shaded_Relief','World_Street_Map','World_Terrain_Base','World_Topo_Map',None))

        if not (figure == None or isinstance(figure,str)):
            raise TypeError(usermessage.typeerrormsg(__name__,self.display.__name__,__file__,__copyright__,
                'figure','str or None',None))
        
        usermessage.openingmsg(__name__,self.display.__name__,__file__,__copyright__,'Display the S1 track and pass from the S1 burst ID map',None,verbose)

        if not 'EIjob' in str(type(job)):
            raise ValueError(usermessage.errormsg(__name__,self.display.__name__,__file__,__copyright__,
                'The job parameter is not a EZ-InSAR job.'),job.log,verbose)

        if not job.satellite == 'S1' and job.satmode == 'IW': 
            raise ValueError(usermessage.errormsg(__name__,self.display.__name__,__file__,__copyright__,
                'The satellite must be S1 and IW acqution mode.'),None,verbose)
        
        if not self.Data:
            raise ValueError(usermessage.errormsg(__name__,self.display.__name__,__file__,__copyright__,
                'No detection has been done.'),None,verbose)

        # Compute the color
        listtrack = []
        for tracki in self.Data:
            listtrack.append(tracki)

        listtrackunique = np.unique(listtrack)
        listcolor = []
        for li in listtrackunique:
            a = np.random.randint(255, size=3)
            listcolor.append((a[0]/255,a[1]/255,a[2]/255))
        
        # Calculation of the map extent
        lonall = []
        latall = []
        for tracki in self.Data:
            ni = np.where(tracki == listtrackunique)[0][0]
            for idx in ['1','2','3']: 
                for iwi in self.Data[tracki]['IW%s' %(idx)]:
                    lonall = lonall + iwi['polyburst'].exterior.coords.xy[0].tolist()
                    latall = latall + iwi['polyburst'].exterior.coords.xy[1].tolist()

        # Plot the ROI
        lonroi,latroi = job.roi.exterior.xy
        fig = plt.figure(figsize=(8, 8))
        m = Basemap(projection='merc', resolution='f',epsg=4326, 
                        llcrnrlon = np.min(lonall)-(np.max(lonall)-np.min(lonall))*0.25,
                        llcrnrlat = np.min(latall)-(np.max(latall)-np.min(latall))*0.25,
                        urcrnrlon = np.max(lonall)+(np.max(lonall)-np.min(lonall))*0.25,
                        urcrnrlat = np.max(latall)+(np.max(latall)-np.min(latall))*0.25)       
        
        m.plot(lonroi,latroi,'-',linewidth=2,color='red',latlon=True,label='User ROI')
        m.plot([np.min(lonroi),np.max(lonroi),np.max(lonroi),np.min(lonroi),np.min(lonroi)],[np.min(latroi),np.min(latroi),np.max(latroi),np.max(latroi),np.min(latroi)],'--',linewidth=1,color='red',latlon=True,label='ROI for EZ-InSAR')

        for tracki in self.Data:
            ni = np.where(tracki == listtrackunique)[0][0]
            firstplot = True
            for idx in ['1','2','3']: 
                for iwi in self.Data[tracki]['IW%s' %(idx)]:
                    if firstplot:
                        m.plot(iwi['polyburst'].exterior.coords.xy[0],iwi['polyburst'].exterior.coords.xy[1],'-',linewidth=1,color=listcolor[ni],latlon=True,label='S1: %s' %(tracki))
                        firstplot = False
                    else:
                        m.plot(iwi['polyburst'].exterior.coords.xy[0],iwi['polyburst'].exterior.coords.xy[1],'-',linewidth=1,color=listcolor[ni],latlon=True)

        m.arcgisimage(service=basemap, xpixels = 2000, ypixels = 2000, verbose = verbose)
        
        m.drawparallels(np.linspace(np.fix(np.min(latall))-1,np.fix(np.max(latall))+1,10),labels=[1,0,0,0])
        m.drawmeridians(np.linspace(np.fix(np.min(lonall))-1,np.fix(np.max(lonall))+1,10),labels=[0,0,0,1])
        
        plt.legend()
        plt.title('Map of S1 burst locations for "%s"' %(job.nameJob))

        if figure == None:
            usermessage.ezprint('\tDisplay the figure...',job.log,verbose)
            plt.show()
        else:
            plt.savefig(figure, dpi=450)
            usermessage.ezprint('\tThe figure has been saved to %s' % (figure),job.log,verbose)

        return self
    
    ################################################################################
    ## Methods to analyse the burst locations regarding the EZ-InSAR job
    ################################################################################
    def analyse(self,job,verbose: Optional[bool] = None):
        """Analyse the S1 ID bursts

        The method detects the S1 ID bursts, satellite directions and track numbers
        regaridng the given `EIjob`. 
        
        Args: 
            job (EIjob): EZ-InSAR job
            verbose (bool, Optional): Verbose [Default: None]

        Returns:
            int: Best track number
            str: Best pass direction
            dict: Result dictionary

        """

        self.checkfile(verbose=False)

        if verbose == None:
                verbose = self.verbose
        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(__name__,self.analyse.__name__,__file__,__copyright__,
                    'verbose','True or False',None))
        
        usermessage.openingmsg(__name__,self.analyse.__name__,__file__,__copyright__,'Analyse the best S1 track and pass from the S1 burst ID map',None,verbose)

        if not 'EIjob' in str(type(job)):
            raise ValueError(usermessage.errormsg(__name__,self.analyse.__name__,__file__,__copyright__,
                'The job parameter is not a EZ-InSAR job.'),job.log,verbose)

        if not job.satellite == 'S1' and job.satmode == 'IW': 
            raise ValueError(usermessage.errormsg(__name__,self.analyse.__name__,__file__,__copyright__,
                'The satellite must be S1 and IW acqution mode.'),job.log,verbose)
        
        if not self.Data:
            raise ValueError(usermessage.errormsg(__name__,self.analyse.__name__,__file__,__copyright__,
                'No detection has been done.',job.log))

        listtrack = dict()
        for tracki in self.Data:
            listtrack[tracki] = []

        listtrackstr = []
        for tracki in self.Data:
            listtrackstr.append(tracki)

        trackarray = np.empty([len(self.Data),4])
        h = 0
        
        for tracki in self.Data:
            nbsw = 0
            nbb = 0
            firstburst = True
            for idx in ['1','2','3']: 
                if self.Data[tracki]['IW%s' %(idx)]:
                    nbsw = nbsw + 1 
                for iwi in self.Data[tracki]['IW%s' %(idx)]:
                    nbb = nbb + 1

                    if firstburst:
                        polymerged = iwi['polyburst']
                        firstburst = False
                    else:
                        polymerged = polymerged.union(iwi['polyburst'])

            polyintersect = polymerged.intersection(job.roi) 

            listtrack[tracki] = [nbsw,nbb]
            trackarray[h,0] = h
            trackarray[h,1] = nbsw
            trackarray[h,2] = nbb
            trackarray[h,3] = polyintersect.area/job.roi.area*100
            h = h + 1

        # Sorting
        trackarray = trackarray[trackarray[:,1].argsort()]
        trackarray = trackarray[trackarray[:,2].argsort(kind='mergesort')]

        usermessage.ezprint('The best S1 acquitions could be: (ranged by sub-swath number, then burst number):',job.log,verbose)
        
        checkbest = False
        besttrack = None
        bestpass = None

        res = dict()
        res['name'] = []
        res['sw'] = []
        res['nbb'] = []
        res['overlap'] = []

        for idx in np.arange(len(self.Data)):
            idxbis = int(trackarray[idx,0])

            if np.round(trackarray[idx,3]) == 100:
                checkover = True
                strinfo = 'OKAY'
            else:
                checkover = False
                strinfo = 'DELETED'
                
            usermessage.ezprint('%d: %s with %d required sub-swath(s) and %d burst(s) (%d %% of overlap) - %s' % (idx, listtrackstr[idxbis],trackarray[idx,1],trackarray[idx,2],trackarray[idx,3],strinfo),job.log,verbose)

            res['name'].append(listtrackstr[idxbis])
            res['sw'].append(trackarray[idx,1])
            res['nbb'].append(trackarray[idx,2])
            res['overlap'].append(trackarray[idx,3])

            if checkbest == False and checkover == True:
                besttrack = int(listtrackstr[idxbis].split('_')[-1])
                bestpass = listtrackstr[idxbis].split('_')[0]
                checkbest = True

        if checkbest == False:
            usermessage.warningmsg(__name__,self.detectfromIDmap.__name__,__file__,'No detection of 100%-coverage S1 data: None will be the outputs. Please try another value of the S1 relative orbite(s) and the pass direction(s)',job.log,verbose)

        return besttrack, bestpass, res
            

    