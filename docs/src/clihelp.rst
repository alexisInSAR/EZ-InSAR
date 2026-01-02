Command-line Interface
======================

**EZ-InSAR can be launched by command-line interface. The name of the command is ezinsar. This is the easiest way to run EZ-InSAR based on an EZ-InSAR job file.**

Commun use and options
----------------------

.. code:: bash 

    ezinsar <command>

The help can be displayed: 

.. code:: bash 

    ezinsar --help 
    #or 
    ezinsar -h 

Each command-related help can be displayed: 

.. code:: bash 

    ezinsar  <command> --help 

SAR data management
-------------------

ezinsar *S1slc*
^^^^^^^^^^^^^^^

*S1slc* allows to download Sentinel-1 data. By default, EZ-InSAR will explorer the different track and satellite directory to propose the best option. Be carefully, there is a large list of parameters. At the minimum, users requires to give the path of the SLC files and the Region of Interest: 

.. code:: bash 

    ezinsar S1slc -s <path_SLC or EZ-InSAR job file> -b <bbox>

An EZ-InSAR job can be given under the *ezinsarjob* option. All other parameters will be bypassed to respect the parameters contained in the job file.

Example
+++++++

**Without an EZ-InSAR job**

The command will download Sentinel-1 IW for a Region of Interest in Ireland, between 2014 and 2024 (included) for the descending 125 acquitions, and the VV polarisation. The selected server is ASF and EZ-InSAR will save the maps of SLC extents.

.. code:: bash 

    ezinsar S1slc -s Data_slc -b private/ROI_Clara.shp -i 2014-01-01T00:00:00 -j 2025-01-01T00:00:00 -o 125 -f d --polarisation VV -u xxxxxx -p xxxxxx --server ASF --savemap --download --nolog 

**With an EZ-InSAR job**

Here, dummy values are required for the path of SLCs and the ROI. In addition, the username and password will be extrated from the EZ-InSAR config file. 

.. code:: bash 

    ezinsar S1slc -s . -b 0,0,0,0 --ezinsarjob job_Clara.ei -u xxxxxx -p xxxxxx --savemap --download --nolog 

ezinsar *S1orbit*
^^^^^^^^^^^^^^^^^

*S1orbit* will download Sentinel-1 orbit files. At the minimum, a SLC-list file and a directory (to store the orbit files) are required. 

.. code:: bash 

    ezinsar S1orbit -f <path_SLC> -o <path_orbit>

Instead of a SLC-list file, the user can give an EZ-InSAR job file. 

Example
+++++++

**Without an EZ-InSAR job**

If no EZ-InSAR job is given, a SLC list is required. 

.. code:: bash

    ezinsar S1orbit -f SLC.list -o Data_orbit -u xxxxxx -p xxxxxxx --server Copernicus --nolog 

**With an EZ-InSAR job**

Here, dummy value is required for the path of orbit files. 

.. code:: bash

    ezinsar S1orbit -f job_EZInSAR.ei -o . -u xxxxxx -p xxxxxxx --server Copernicus --nolog 

ezinsar *S1etad*
^^^^^^^^^^^^^^^^^

*S1etad* will download Sentinel-1 ETAD files. An EZ-InSAR job file is required. 

.. code:: bash 

    ezinsar S1etad -f <EZ-InSAR job file> 

Digital Elevation Model download 
--------------------------------

ezinsar *DEM*
^^^^^^^^^^^^^

*DEM* will download a DEM file regarding the user's options. Directory path and bbox are required but users can give an EZ-InSAR job file instead of the path (all other parameters will be bypassed to respect the parameters contained by the job file). This command also has options to apply a correction according to ellipsoid elevations. 

.. code:: bash 

    ezinsar DEM -s <pathDEM or EZ-InSAR job file> -b <W,S,E,N>

Example
+++++++

**Without an EZ-InSAR job**

If an EZ-InSAR job is not given, users needs to define the DEM directory path and the Region of Interest (here the ROI is given by using a vector file). We define to use the Copernicus DEM with the ellipsoid correction and block the cropping of the DEM. The planned InSAR processor is ISCE-2. 

.. code:: bash 

    ezinsar dem run -s ./DEM -b private/ROI_Clara.shp --nameDEM DEM_Clara --typeDEM Copernicus-ell --no_clip --processor isce2

**With an EZ-InSAR job**

Here, dummy value is required for the ROI because it will be extracted from the job. 

.. code:: bash 

    ezinsar dem run -s job_EZInSAR.ei -b 0,0,0,0 --typeDEM Copernicus-ell --processor isce2

SAR and InSAR processing
------------------------

ezinsar *init*
^^^^^^^^^^^^^^

*init* can be used to generate an EZ-InSAR job file. No arguments are required but this command has a large list of options to set the EZ-InSAR processing job up.

.. code:: bash 

    ezinsar init -p isce2

To add a coregistration processing job into the EZ-InSAR job: 

.. code:: bash 

    ezinsar init -f <your job file> -j <your job file> -t coreg

This command can also used to modify the parameters of the job. 

.. code:: bash 

    ezinsar init -j <your job file> -m '<step>:<parameter>=<new value>' 

For example, to modify the value of the done parameter for the checkSLC step: 

.. code:: bash 

    ezinsar init -j <your job file> -m 'checkSLC:done=True' 

ezinsar *run*
^^^^^^^^^^^^^

*run* will execute the processing contained in the selected EZ-InSAR job. If several processing are stored, EZ-InSAR will ask the wanted processing from users. 

.. code:: bash 

    ezinsar run -f <your job file> -s <name of the step (or number of the step)>

For example, the processing step can be given by using a step name: i.e., 'extractimage'. Several steps can be given by using several comma-separeted step names and : i.e., 'initref,extractimage'. All the steps can be done by using the full name or a number: i.e., 1-3, in this case, all the steps from checkSLC to coarserefdate will be processed in case of coregistration processing. If 'all' is used as the step name, it will process all different steps

ezinsar *bestref*
^^^^^^^^^^^^^^^^^

*bestref* will compute a coarse interferometric network to find the best reference date, and based on a geometric average (i.e., barycentre). This command is accurate for Sentinel-1 data, but we recommend selecting manually the reference date for the other sensors, by visualising the output of this command. 

.. code:: bash 

    ezinsar bestref -s <path of the SLC files> -b <bbox>

ezinsar *update*
^^^^^^^^^^^^^^^^

*update* will update an EZ-InSAR processing based on an EZ-InSAR job file. 

.. code:: bash 

    ezinsar update -f <EZ-InSAR job file> 

.. admonition:: Warning
  :class: warning

  This function is not fully implemented and tested.

ezinsar *job*
^^^^^^^^^^^^^^^^

*job* will add some tools in order to manupilate EZ-InSAR jobs. 

.. code:: bash 

    ezinsar job -h

Example
+++++++

The following function will remove the coregistration processing available in the EZ-InSAR job. 

.. code:: bash 

    ezinsar job -f job.ei -t clearprocess --process coregistration

Quick interferogram computation 
-------------------------------

The following commands allow to quickly compute an interferogram. Do not hesitate to check the full lists of options. 

ezinsar *quickifg*
^^^^^^^^^^^^^^^^^^

The first command will compute interferograms based on SLC files. It is available for Sentinel-1 data, other sensors will be implemented later. For a set of default parameters: 

.. code:: bash 

    ezinsar quickifg -m <path-of-the-reference-image> -s <path-of-the-secondary-image>

ezinsar *lastS1*
^^^^^^^^^^^^^^^^

*lastS1* will compute the last Sentinel-1 interferogram (available for IW and SM acquisition modes). Only a work directory and a Region of Interest are required. For an use of default parameters: 

.. code:: bash 

    ezinsar lastS1 -w <path_wk> -b <bbox>

Archive the EZ-InSAR results
----------------------------

Both commands can be used to archive, share the EZ-InSAR results by using the archive function. *archive* will create the archive and *archive_decrypt* will decrypte an EZ-InSAR archive if it is encrypted. Also there is a large list of options to create the archive. 

.. code:: bash 

    ezinsar archive -f <EZ-InSAR job file>  # Create the archive
    ezinsar archive_decrypt -f <EZ-InSAR archive> -k <key> # Unzip the archive

.. admonition:: Warning
  :class: warning

  We are actively working on this functionnality of EZ-InSAR. Please see the documentation to know which processing are compatible. 

Interface commands
------------------

ezinsar *desktop*
^^^^^^^^^^^^^^^^^

*desktop* will open the command-line interface of the EZ-InSAR Desktop module. 

.. code:: bash 

    ezinsar desktop -h    

ezinsar *webapp*
^^^^^^^^^^^^^^^^

*webapp* will open the command-line interface of the EZ-InSAR WebApp module. 

.. code:: bash 

    ezinsar webapp -h    

ezinsar *tsdisplayer*
^^^^^^^^^^^^^^^^^^^^^

*tsdisplayer* will open the command-line interface of the EZ-InSAR time-series Displayer module. 

.. code:: bash 

    ezinsar tsdisplayer -h    

Docker command
--------------

EZ-InSAR offers a command to run EZ-InSAR inside a Docker container. 

ezinsar *docker*
^^^^^^^^^^^^^^^^

.. code:: bash 

    ezinsar docker -v /media/Data1/Workdirectory -p 8050

The argument volume allows to mount the directory onto the container. 

Optional-module-related commands
--------------------------------

ezinsar *gamma*
^^^^^^^^^^^^^^^

*gamma* will open the command-line interface of the EZ-InSAR GAMMA module. 

ezinsar *gnss*
^^^^^^^^^^^^^^

*gnss* will open the command-line interface of the EZ-InSAR GNSS module. 

ezinsar *multispectral*
^^^^^^^^^^^^^^^^^^^^^^^

*multispectral* will open the command-line interface of the EZ-InSAR multispectral module. 

Sub-program command
-------------------

Even if EZ-InSAR provides an environment for SAR/InSAR data, some supplementary programs (developed in MATLAB and Python language) can be available. Please see the related documentation in order to know the available tools.

ezinsar *program*
^^^^^^^^^^^^^^^^^

.. code:: bash 

    ezinsar program <name of the sub-program> [options]

Documentation
-------------

The *docs* command will open the documentation (online or offline). 

.. code:: bash 
    
    ezinsar docs

If a specified documentation - related to an optional EZ-InSAR module - is desired: i.e., for the Multispectral module:

.. code:: bash 
    
    ezinsar docs -m multispectral

Manage installation
-------------------

The *toolkit* command allows to manage the current installation of EZ-InSAR. 

