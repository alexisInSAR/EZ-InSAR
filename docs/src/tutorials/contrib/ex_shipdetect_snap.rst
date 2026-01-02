Ship detection from Sentinel-1 GRD images using SNAP
====================================================
**By Alexis Hrysiewicz, Sep. 2025**

Here the goal is the detection of objects over sea (i.e., ship detection) based on Sentinel-1 GRD images and the tools prodived by SNAP. 

**Outcomes**:

* Demonstration of the manipulation of Sentinel-1 GRD images with EZ-InSAR; 
* Demonstration of the wrapper of SNAP;
* Demonstration of the use of EZ-InSAR via Python scripts. 

Import the required packages (EZ-InSAR and others)
--------------------------------------------------

The first step is the import of Python packages from EZ-InSAR: 

.. code:: Python

   from datetime import datetime
   import ezinsar.job as ez
   from ezinsar.api import Copernicusapi
   
In addition, the contribution module needs to be imported: 

.. code:: Python

   from ezinsar.contrib.python import snapShipDectection

Creation of the EZ-InSAR job
----------------------------

The module will use an EZ-InSAR job, the job can be easily created: 

.. code:: Python
   
   job = ez.EIjob(verbose=True,
         polarisation=['VV'],
         workdirectory = os.path.abspath('WK'),            
         pathSLC = os.path.abspath('GRD_files'),
         pathorbit = os.path.abspath('Orbits'),
         pathaux = os.path.abspath('File_aux'),
         pathDEM = os.path.abspath('DEM'),
         )

Each required directory can be created by the associated methods: 

.. code:: Python 

   job.mkdir() 

Definition of the Region of Interest
------------------------------------

The next step is the selection of the Region of Interest. The ROI can be imported into the EZ-InSAR job: 

.. code:: Python

   job.importroi(input=[-6.8508,53.0384,-5.4063,53.6729])

The computation will be performed on the Dublin bay. 

Detection of the available images
---------------------------------

Due to the GRD levels, the list of images should be created by using the Copernicus API: 

.. code:: Python
   
   job.SLClist = Copernicusapi.retrieve('S1', 
      job.roi,    
      date1 = datetime.strptime('2014-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
      date2 = datetime.strptime('2025-08-31T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
      level = 'GRD',
      relorbit = 1,  
      satpass = 'ASCENDING')

.. note:: 

   We recommend defining the satellite parameters and dates here, EZ-InSAR will modify the EZ-InSAR job according to the selection parameters. 

EZ-InSAR now can check the list and propagate the satellite parameters into the job: 

.. code:: Python

   job.checkSLClist()
   job.printSLClist()


.. note:: 

   All functions/methods available for the SLC images are also available with the GRD images. 

Finally, the images can be downloaded: 

.. code:: Python

   job.downloadSLC()

Computation of the ship locations using SNAP
--------------------------------------------

The computation is based on a new method provided by the contrib script: 

.. code:: Python

   jobShip = snapShipDectection.jobsnapSD(job) # Here the job is required

Then the processing steps can be launched. The first step is the import of images for SNAP: 

.. code:: Python 
   
   jobShip.importGRD()

Due to the complexity of coastlines, it can be better to use a vector file in order to mask lands. The vector file will be injected (in-place) into the SNAP images. However, this step is optional. 

.. code:: Python
   
   jobShip.importVector(os.path.abspath('Irish_DEM/shorelineIE.shp'))

.. note:: 

   The dem module can be used to generate the vector files. 

Then, the detection can be carried out. Whereas the SNAP tool (in the Desktop application) corresponds to a single tool, EZ-InSAR will process the following steps: 

1. *Land-Sea-Mask* operator; 
2. *Calibration* operator; 
3. *AdaptiveThresholding* operator; 
4. *Object-Discrimination* operator. 

This step can similar than the tools provided by SNAP, but a single tool - available with the Desktop application - is not implemented with the GPT wrapper. In order to run the detection, the method is: 

.. code:: 

   jobSP.detection()

Finally, the conversion of the .csv vector file from SNAP to a .shp file can be done: 

.. code:: 

   jobSP.extractposition(output_directory=os.path.abspath('results'))
              
Wrapper for automatic detection from all the Sentinel-1 GRD images
------------------------------------------------------------------

The following script proposes an example for the full wrapper for the ship detection optimising the storage space: 

1. Definition of parameters.
2. Loop of processing: (1) Download the GRD image(s) for a date; (2) Detection; and (3) Cleaning. 
3. Post-processing of data: computation of a density map. 

The example is over Dublin Bay and uses the Sentinel-1 IW001 images. There are two options in order to display the detection with a raster: 

* via a computation of detection numbers per pixel; 
* via a probability computation with gaussian kernels. 

.. code:: Python

   #! /usr/bin/env python3
   # -*- coding: iso-8859-1 -*-
   """
   Example for a wrapper in order to detect ships based on Sentinel-1 IW GRD images 

   The module contains an example for a wrapper in order to detect ships based on Sentinel-1 IW GRD images. The targeted area is Dublin Bay. 

   Notes: 
         Each date is processed independently in order save storage spaces. 

   Changelog:
         * 1.0.0: Initial version, Sep. 2025

   """

   __author__ = 'Alexis Hrysiewicz (UCD / iCRAG)'
   __copyright__ = "Copyright 2025, EZ-InSAR / UCD / iCRAG"
   __version__ = '1.0.0'

   ######################################################################
   ## Import Python packages

   import ezinsar.job as ez
   from ezinsar.api import Copernicusapi
   from ezinsar.eicomponents.demmodule import demfunctions

   from ezinsar.contrib.python import snapShipDectection

   from datetime import datetime 
   import numpy as np
   import os
   import shutil 
   import glob 

   import geopandas as gpd
   from osgeo import gdal, osr
   from pyproj import Transformer
   import scipy.stats as st

   ######################################################################
   ## Create the EZ-InSAR job for processing
   job = ez.EIjob(verbose=True,
                  polarisation=['VV'],
                  workdirectory = os.path.abspath('IW1/WK'),          
                  pathSLC = os.path.abspath('IW1/GRD_files'),
                  pathorbit = os.path.abspath('IW1/Orbits'),
                  pathaux = os.path.abspath('IW1/File_aux'),
                  pathDEM = os.path.abspath('IW1/DEM'),
                  )

   ## Import the Region of Interest
   job.importroi(input=[-6.8508,53.0384,-5.4063,53.6729])

   ## Detect the images available from the online server
   job.SLClist = Copernicusapi.retrieve('S1', 
         job.roi, 
         date1 = datetime.strptime('2014-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
         date2 = datetime.strptime('2025-12-31T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ'),
         level = 'GRD',
         relorbit = 1, 
         satpass = 'ASCENDING')

   job.checkSLClist()
   job.printSLClist()

   ## Create the directories
   job.mkdir()

   ## Create the date list
   dates = []
   for datei in job.SLClist['Date1']:
         dates.append(datei.split('T')[0])
   dates = np.unique(dates)

   ## Reverse the index of dates in order to run the computation from recent dates to old dates. 
   listidx = np.arange(len(dates))[::-1] 

   ######################################################################
   ## Loop of processing 
   for diidx in listidx:
         print(dates[diidx])
         if not os.path.isfile(os.path.abspath('IW1/results') + os.sep + 'shipDetection_%s_%s_%s_%s_%s.shp' % ('S1',
                  job.satmode,
                  job.satpass,
                  job.relorbit,
                  dates[diidx].replace('-',''),
                  )): 

                  ## Downlaod the image(s)
                  job.downloadSLC(index=[diidx]) 
                  
                  ## Import the class from the contrib package
                  jobSP = snapShipDectection.jobsnapSD(job)

                  ## Import the GRD image
                  jobSP.importGRD()

                  ## Import the vector files
                  jobSP.importVector(os.path.abspath('Irish_DEM/shorelineIE.shp'))

                  ## Do the detection
                  jobSP.detection()

                  ## Convert the results into a shapefile 
                  jobSP.extractposition(output_directory=os.path.abspath('IW1/results'))

                  ## Cleaning 
                  if os.path.isdir(job.workdirectory):
                           shutil.rmtree(job.workdirectory)
                  if os.path.isdir(job.pathSLC):
                           shutil.rmtree(job.pathSLC)
                  if os.path.isdir(job.pathorbit):
                           shutil.rmtree(job.pathorbit)
                  if os.path.isdir(job.pathaux):
                           shutil.rmtree(job.pathaux)
                  if os.path.isdir(job.pathDEM):
                           shutil.rmtree(job.pathDEM)
                  job.mkdir()

   ######################################################################
   ## Post-processing: creation of a density map (in GTiff)
   ######################################################################
   def centres_to_edges(centres):
      """
      Function to convert pixel centres to edges
      """
      edges = np.zeros(len(centres) + 1)
      edges[1:-1] = (centres[:-1] + centres[1:]) / 2
      edges[0] = centres[0] - (edges[1] - centres[0])
      edges[-1] = centres[-1] + (centres[-1] - edges[-2])
      return edges

   ## The EPSG:3035 will be used
   transformer = Transformer.from_crs("epsg:4326", "epsg:3035", always_xy=True)

   ## Compute the grid extent
   lon,lat = job.roi.exterior.xy
   x, y = transformer.transform(lon, lat,radians=False)

   ## Spatial resolution in metre
   dx = 500

   xmin = np.round(np.min(x)/dx)*dx
   xmax = np.round(np.max(x)/dx)*dx
   ymin = np.round(np.min(y)/dx)*dx
   ymax = np.round(np.max(y)/dx)*dx

   ## Extract the point locations from the .shp files
   Xpts = []
   Ypts = []

   for filei in glob.glob('results/*.shp'):
      data = gpd.read_file(filei)
      for li in data['geometry']: 
         x, y = transformer.transform(li.x, li.y,radians=False)
         Xpts.append(x)
         Ypts.append(y)

   # ########################################################
   # ## Compute the number of detection per pixels
   # ########################################################
   # ## Compute the pixel centres
   # x_centres = np.arange(xmin,xmax,dx)
   # y_centres = np.arange(ymin,ymax,dx)

   # ## Compute the density map
   # x_edges = centres_to_edges(x_centres)
   # y_edges = centres_to_edges(y_centres)
   # H, _, _ = np.histogram2d(Xpts, Ypts, bins=[x_edges, y_edges])
   # H = np.flipud(H.T) ## It requires 

   ########################################################
   ## Compute the probability function via gaussian kernel 
   ########################################################
   xx, yy = np.mgrid[xmin:xmax:dx, ymin:ymax:dx]
   positions = np.vstack([xx.ravel(), yy.ravel()])
   values = np.vstack([Xpts, Ypts])
   kernel = st.gaussian_kde(values)
   H = np.reshape(kernel(positions).T, xx.shape)
   H = (H - np.min(H))/ (np.max(H)-np.min(H)) # normalisation

   ## Export a temporary GTiff
   nx = H.shape[0]
   ny = H.shape[1]
   xres = (xmax - xmin) / float(ny)
   yres = (ymax - ymin) / float(nx)
   geotransform = (xmin, xres, 0, ymax, 0, -yres)

   dst_ds = gdal.GetDriverByName('GTiff').Create('tmp.tif', ny, nx, 1, gdal.GDT_Float32)   
   dst_ds.SetGeoTransform(geotransform)                           
   srs = osr.SpatialReference()                             
   srs.ImportFromEPSG(3035)                                   
   dst_ds.SetProjection(srs.ExportToWkt())                       
   dst_ds.GetRasterBand(1).WriteArray(H)                   
   dst_ds.GetRasterBand(1).SetNoDataValue(0)         
   dst_ds.SetMetadata({"AREA_OR_POINT": "Point"})
   dst_ds.FlushCache()                                       
   dst_ds = None 

   ## Masking based on the vector file
   os.system('ogr2ogr -t_srs "EPSG:3035" tmp.shp Irish_DEM/shorelineIE.shp') ## Convert to EPSG:3035; temporary file

   ## Apply the vector file to the results by using the EZ-InSAR dem module (the naming will be performed here)
   demfunctions.applymask('tmp.tif',
         'shipDetection_%s_%s_%s_%s.tif' % ('S1',
                  job.satmode,
                  job.satpass,
                  job.relorbit,
         ),
         'tmp.shp',
         invert=True,
         verbose=True)

   ## Cleaning 
   for li in glob.glob('tmp.*'):
      os.remove(li)


