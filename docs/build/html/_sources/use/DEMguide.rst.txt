Download the DEM 
################

**EZ-InSAR offers the possibility to download a DEM from four different sources: (1) NASADEM; (2) SRTM; (3) Copernicus and (4) personal DEM:** 

* The SRTM and SRTM-ell keys correspond to the normal SRTM DEM.
  
* The NASADEM and NASADEM-ell keys corresponds to the reprocessed SRTM DEM by NASA. 

* The Copernicus and Copernicus-ell keys corresponds to the reprocessed Copernicus DEM by ESA. See `this page <https://spacedata.copernicus.eu/web/cscda/dataset-details?articleId=394198>`_ for more details.  

.. note:: 

   InSAR processing requires elevations relative to the ellipsoid. The '-ell' extension allows to correct elevations with the associated ellipsoid. In case of the use of personal DEM, an external ellipsoid file can be given by the user.

Firs, the user can to define some variables of the **EZ-InSAR** job: 

.. code-block:: python

    job.nameDEM = 'dem_EZInSAR.wgs84.tif'
    job.typeDEM = 'Copernicus-ell' # ell for the ell. correction

And, they can download the DEM by using the **EZ-InSAR** job method: 

.. code-block:: python

    job.downloaddem()

Several options are available:

- *bbox*: the user can give a bbox (automatic extracted from SLC extent); 
- *ell*: the user can give a .tif file for the geoid (automatic downloaded for the downloaded DEM); 
- *ellcorrection* (True or False): applied the ellepsoid correction; 
- *processor*: convert the DEM file for a given InSAR processor; 
- *clip* (True of False): clip the DEM regarding the bbox coordinates; 
- *verbose* and *log* options. 

.. note:: 

    For the Sentinel-1 IW, **EZ-InSAR** will compute the bbox regarding bursts overlapping the user's Region of Interest. 

**In addition, EZ-InSAR offers the possibility to display the DEM, e.g.,:**

.. code-block:: python    
    
    job.displaydem(figure=None,
        mode='hillshade', 
        azimuth=225.0, 
        angle_altitude=45.0, 
        verbose=None,
        log=None)

If the figure is not *None*, the map will be saved into a .jpg image (and therefore not displayed). 