Run EZ-InSAR
============

Create an EZ-InSAR job
----------------------

**The first step is the definition of an EZ-InSAR job. So, the EZ-InSAR package needs to be imported:**

.. code-block:: python
   
   import ezinsar.job as ez

Then, the job can be easily initialised: 

.. code-block:: python

   job = ez.EIjob(verbose=True,polarisation=['VV','VH'])

.. note::

   All EZ-InSAR job's attributes can be given during the initialisation of the job as optional arguments. 

By default, the Sentinel-1 data - in IW acquition mode - will be used. Then, the paths of the required directories must be defined:

.. code-block:: python

   job.workdirectory = './WKtest'            # Path of the workdirectory
   job.pathSLC = './WKtest/Data_slc'         # Path of the SLCs (if needed)
   job.pathorbit = './WKtest/Data_orbit'     # Path of the orbit files (if needed)
   job.pathaux = './WKtest/Data_aux'         # Path of the Aux. files (if needed)

Using Sentinel-1 imagery, we must to define the research dates:

.. code-block:: python
   
   from datetime import datetime
   
   job.date1 = datetime.strptime('2020-12-01T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')      # First date of the research
   job.date2 = datetime.strptime('2020-12-31T00:00:00.000000Z','%Y-%m-%dT%H:%M:%S.%fZ')      # Last date of the research

These dates are only used for researching the SAR acquisitions. During processing, **EZ-InSAR** will try to use all the files stored. 

**The next step to intialise an EZ-InSAR job is the definition of a Region of Interest (ROI).**. The method *importroi* deals with tree definition of ROIs: 

1. by a file: it can be a shapefile, or other vector drivers which can be read by GDAL:

   .. code-block:: python

      job.importroi(input=<your vector file>) 

2. by a BBOX in longitude and latitude coordinates (EPGS:4326):

   .. code-block:: python

      job.importroi(input=[W,S,E,N]) 

3. by a name of a volcano. 

   .. code-block:: python

      job.importroi(input='Campi Flegrei', radiusvolc = 20000)

   Here the option *radiusvolc* allows to define the radius of the ROI (in metres).  

   .. note:: 

      EZ-InSAR can displayed the volcano list by using the sub-program volcanoname: 

      .. code-block:: bash

         ezinsar program volcanoname

**Finally, the directories can be easily created by:**

.. code-block:: python

   job.mkdir()

*mkdir* has the same behaviour than the *mkdir* system command. 

**At this stage, the EZ-InSAR job is ready.**

Process InSAR data using EZ-InSAR
---------------------------------

.. toctree::
   :maxdepth: 2

   slcguide
   DEMguide
   coregguide
   ifgguide
   tsguide
   intguide
   
Save and load an EZ-InSAR job
-----------------------------

Any EZ-InSAR job (i.e., ezinsar, coregistration, interferogram stack, time-series analysis) can be saved and stored. 

.. code-block:: python

   ez.save(job,'jobsave')
   newjob = ez.load('jobsave.ei')

.. note:: 

   The loaded job will be the same type of the stored job: e.g., if the user stored only a coregistration job, the loaded job will be a coregistration job. 

   In this example, only the coregistration job is saved and loaded. 
   
   .. code-block:: python

      ez.save(job.coregistration,'jobsave')
      newjobcoregistration = ez.load('jobsave.ei')