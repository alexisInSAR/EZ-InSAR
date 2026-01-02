Import, download, check the SLC images (and orbit files)
########################################################

**The following sections present the management of SLC images with EZ-InSAR**.

Import the SLC data
********************

For Sentinel-1 data
===================

.. note::

   **EZ-InSAR** can manage the .zip and .SAFE files of Sentinel-1 products but we recommend using the .zip files for space-storage compliance.

First, users must to define the satellite parameters. The relative orbits must be defined:

.. code-block:: python

   job.relorbit = 1

The second parameter is the satellite direction (ASCENDING or DESCENDING): 

.. code-block:: python

   job.satpass = 'ASCENDING'

.. note::

   You can use the ``s1iwburstIDapp`` to automatically find the relative orbit and the satellite direction: 

   .. code-block:: python
      
      from ezinsar.eicomponents.sensor.s1module import s1iwburstIDapp
      job.relorbit, job.satpass = s1iwburstIDapp.S1burstIDmap().checkfile().downloadfile().detectfromIDmap(jobezinsar).analyse(jobezinsar)

      # Users will have a list of orbit/direction couples. 

The next step is the creation of the SLC list. Here the Copernicus server will be used in order to create the SLC list.  

.. code-block:: python

   job.initiateSLC(mode='online',verbose=True,server='Copernicus')

Based on the SLC list, **EZ-InSAR** can now download the images: 

.. code-block:: python
   
   job.downloadSLC(username=<Username>,password=<Password>)

And the orbit files can be downloaded (the server can be specified):

.. code-block:: python
   
   job.downloadorbit(username=<Username>,password=<Password>,server='ASF')

Of course, it is also possible to import the SLC list from files, or from a saved list of SLCs. 

ETAD files can be downloaded by using the corresponding functions. The server will be Copernicus. 

.. code-block:: python
   
   job.downloadETAD()(username=<Username>,password=<Password>)

For other sensors
=================

EZ-InSAR will create the SLC list based on your available stored files: 

.. code-block:: python

   job.initiateSLC(mode='onfile',verbose=True)

**The name of SAR files needs to respect some conventions:**

* for TerraSAR-X or PAZ: unzipped PAZ1_* or TSX1_* directory in the SLC directory. 

Check the SLC list
******************

**EZ-InSAR** can check the SLC list to verify that the consistency of SLC files with the user parameters:

.. code-block:: python

   job.checkSLClist(verbose = True, mode = 'low')

The option ``mode`` can be ``'high'`` or ``'low'``. If ``'high'``, the warmings will be errors. 

Print the SLC list
******************

**EZ-InSAR** can print an overview of the SLC list. 

.. code-block:: python

   job.printSLClist(verbose = True)

Save the SLC list
*****************

**EZ-InSAR** can the SLC list in .csv format. This list could be used later. 

.. code-block:: python

   job.saveSLClist(verbose = True, file = 'SLClist.csv')

Display a map of SLCs
*********************

The user can display a map of the SLCs. There are two different modes: 

* ``'Extent'`` to display the SLC extents (slices); 
* ``'Bursts'`` to display the burst limits if the SLCs are Sentinel-1 and already downloaded. 

If the user gives the ``figure`` option (other than None), the figure will be saved and not displayed. 

.. code-block:: python

   job.displaySLClist(verbose = True, basemap = 'World_Imagery', mode = 'Extent', figure = None)

Save a .kmz file from a SLC list
********************************

The SLC list can be saved in .kmz for Google-Earth visualisation: 

.. code-block:: python

   job.writeSLClisttokmz(file = 'SLClist.kmz')
