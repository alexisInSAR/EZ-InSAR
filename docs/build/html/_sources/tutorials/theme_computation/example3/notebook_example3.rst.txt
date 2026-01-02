Computation of a Sentinel-1 IW time series with LiCSBAS
=======================================================
By Alexis Hrysiewicz, Nov. 2024

Here the goal is the computation of time series LOS displacements between 2020 and 2022 at Fernandina volcano. We will use Sentinel-1 IW data, and the LiCSBAS processor. 

Also we will use EZ-InSAR in Python. 

1 Initialiation of the EZ-InSAR job
------------------------------------

The first step is an initialiation of an EZ-InSAR job. Of course, it is possible to define some parameters: 

* we want to use ONE polarisations available with Sentinel-1 data: **VV**; 
* we decide to use the no-default acquisition mode of Sentinel-1: **IW**; 
* we decide to active the **verbose**; 
* and we also decide to save the log into the *ezinsarexample.log* **file**.

**The Sentinel-1 satellites are selected by default.**

However, we need to modified some parameters: i.e., **the different directory paths and the dates**.

Because this is the easiest option, we can use Python to initialise our job. In your python terminal: 

.. code:: python

   ## Import the required Python packages
   from datetime import datetime 
   import ezinsar.job as ez
   import os

   ## Initialise the job
   job = ez.EIjob(verbose=True,polarisation=['VV'],satmode='IW',log='ezinsarexample.log')

   ## Path directory modofications
   job.workdirectory = os.path.abspath('.')
   job.pathSLC = os.path.abspath('./Data_slc')
   job.pathorbit = os.path.abspath('./Data_orbit')
   job.pathaux = os.path.abspath('./Data_aux')
   job.pathDEM = os.path.abspath('./DEM')

   ## Define the Region of Interest
   job.importroi(input=[-91.67536,-0.53197,-91.34927,-0.22441])

   ## Date definition 
   job.date1 = datetime.strptime('2020-02-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')
   job.date2 = datetime.strptime('2022-01-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')

   ## Satellite parameters 
   job.relorbit = 106
   job.satpass = 'ASCENDING'  

   ## Creation of the directories
   job.mkdir()

   ## Quick checking of the job
   job.check()

   ## Save the job 
   ez.save(job,'example3.ei')

   ## Quit Python 
   quit()

2 Download the Sentinel-1 data (SLC and orbits)
-----------------------------------------------

The SLC images are not required with this processor. 

3 Download the DEM
------------------

The DEM is not required with this processor. 

4 Coregistration
----------------

The coregistration processing is not required with this processor. 

5 Interferometric computation
-----------------------------

The interferometric-stack processing is not required with this processor. 

5 Time series analysis
----------------------

.. code:: python

   from datetime import datetime 
   import ezinsar.job as ez
   import os

   ## Import the EZ-InSAR job
   job = ez.load('example3.ei')

   ## Initialise the TS processing with LiCSBAS
   job.initiatets(processor='licsbas')

   ## Detection of the best frame
   job.tsprocessing.detectframe()
   job.tsprocessing.check()

   ## Processing (LibSBAS will automatically download the images)
   job.tsprocessing.run(step=['get_geotiff'])
   job.tsprocessing.run(step=['prep_ifg'])
   job.tsprocessing.run(step=['check_unw'])
   job.tsprocessing.run(step=['loop_closure'])
   job.tsprocessing.run(step=['sb_inv'])
   job.tsprocessing.run(step=['vel_std'])
   job.tsprocessing.run(step=['mask_ts'])
   job.tsprocessing.run(step=['filt_ts'])
   job.tsprocessing.run(step=['extract_res'])