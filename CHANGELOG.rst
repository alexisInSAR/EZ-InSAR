Change-log
==========

3.3.1 Alpha (Dec. 2025)
-----------------------

Overall
^^^^^^^

* For greater clarity, the links between EZ-InSAR and the optional GAMMA module have been modified. Before the change, EZ-InSAR tried to import the module, and returned a warning. EZ-InSAR will automatically import the E-InSAR job with GAMMA, if it is available. 

* Simplication of the import. Now, *import ezinsar.job as ez* is used to import a EZ-InSAR job. This modification is transparent for CLI users. Each module has been modified. 

* Now, the EZ-InSAR job class is checked with the following string: *EIjob*.

3.3.0 Alpha (Oct. 2025)
-----------------------

Overall
^^^^^^^

* Bug fix the links between EZ-InSAR and Docker 

* Add the parameters (configuration file) to change the conda environments when MintPy, ISCE-2, etc. are used. Currently under testing. 


3.2.3 Alpha (Oct. 2025)
-----------------------

Processor
^^^^^^^^^

* Modification of the Sentinel-1 SM Doris reader (delete the MFF format).


3.2.2 Alpha (Sep. 2025)
-----------------------

Overall
^^^^^^^

* Delete the support of wget for Windows.

Sensors
^^^^^^^

* New command *S1detect* for automatic detection of Sentinel-1 IW track and orbits 

* The burst file of s1iwbrustIDapp tool is stored in cached. 

3.2.1 Alpha (Sep. 2025)
-----------------------

Overall
^^^^^^^

* Harmonisation of Sentinel-1 orbit file management (checking, downloading). Copernicus server can retrieve MOEORB files.

DEM
^^^

* Geoide files are stored in the user cache directory.

* Full rewriting of the DEM module for best performance and accuracy. Now a full interface is available (see ezinsar dem command).

Sensors
^^^^^^^ 

* Implementation of the ETAD Sentinel-1 downloading (*job.downloadETAD()* function) and new CLI command *S1etad*. 

* New function (and command line) to find the next Sentinel-1 acquisitions from an EZ-InSAR job. 

APIs
^^^^

* Add the checksum with the ASF, EarthData APIs.

* Add an experimental support of the GEODES server.   

Overall
^^^^^^^

3.2.0 Alpha (Aug. 2025)
-----------------------

Overall
^^^^^^^

* Some bug fixes have been carried out.

* Some changes in order to have a compatibility with Windows (Docker running).

* New command to generate the EZ-InSAR configuration file: ezinsar toolkit configfile.

* DEM module is compatible with Windows.

* Increase the numbers of parameters in the EZ-InSAR configuration file.

* Add a fixed Docker environment.

* New DEM sources. 

* Documetation modifications. 

* Configuration file locations have been changed. 

* New function for job: changepaths 

* New tools with ezinsar toolkit 

* Development of the installer

Digital Elevation Model
^^^^^^^^^^^^^^^^^^^^^^^

* Add the possibility to prepare DEMs inside a Docker container. 

Processors
^^^^^^^^^^

* MiaplPy processor has been implemeneted (under testing). 

* SARvey processor has been implemeneted (under testing). 

3.1.0 Alpha (Feb. 2025)
-----------------------

.. admonition:: New structure
  :class: Warning

  The structure of EZ-InSAR has been modified. Now EZ-InSAR is seperated into a core and several modules (see the documentation). The module can be requested by emails: 

  - module for multispectral imagery; 
  - module for NISAR (under development);
  - etc. 

  The new structure is transparent for users. 

Overall
^^^^^^^

* Some bug fixes have been carried out.

* A new module named *templatevar.py* was created in order to store empty variables. 

* A new module name *miscellaneous.py* was created in order to store divers functions. 

* New *-m* or *--module** parameter for the *ezinsar docs*. This parameter allows to open the module-related docuementation. 

* Each version numbers for any SAR/InSAR processors and sensors is independent.  

* New command - *ezinsar info* allows to print the information of the EZ-InSAR installation. 

* Documentation writing.

Sensors
^^^^^^^

* New package *api* has been created to group the different api for data downloading. We started migrating the scripts into this package. 

* APIs for GEODES and THEIA servers under developments

* Fixes and improvements for the slctools.writeSLClisttokmz function

* *__CopernicusSLCdownloader__* has been changed to *__SLCdownloader__* as variable.

* Add the compatibility between different versions of SLC lists. 

* New method for unzip .zip SLC files

* Start the support of COSMO-SkyMed (StripMap-like imagery)

* Start the support of COSMO-SkyMed Second Generation (StripMap-like imagery)

* Start the support of RADARSAT-1 (StripMap-like imagery)

* Start the support of RADARSAT-2 (StripMap-like imagery)

* *checkSLClist* has been finalised. 

Processors
^^^^^^^^^^

* LiCBAS is functionnal. 

Others
^^^^^^

* A fix in the *geocoding.py* function has been solved (see change-log inside the function).

3.0.1 Alpha (Jan. 2025)
-----------------------

Overall
^^^^^^^

* Some bug fixes have been carried out. 

Processors
^^^^^^^^^^

* The descriptions and formats of each processing parameter for StaMPS have been added. 

* The verification of StaMPS parameters is now available. 

Graphical user interface
^^^^^^^^^^^^^^^^^^^^^^^^

* The SNAP coregistration and ifgstack processing are now available with the GUI (tests are being performed).

* The StaMPS ts processing are now available with the GUI (tests are being performed). 

3.0.0 Alpha (Dec. 2024)
-----------------------

.. admonition:: MATLAB version
  :class: Danger

  **This new version is in Python (from the version 3). The MATLAB version is now depreciated.** Of course, it still is available. 

Even if the spirit does not change, **EZ-InSAR-3** can be considered as a new toolkit and numerous changes have been done, please find a short summary of changes. 

Programming language
^^^^^^^^^^^^^^^^^^^^

* **EZ-InSAR** has been translated into Python language. **EZ-InSAR** can be launched by command-line interface, Python scripts or Graphical User interface. 

* MATLAB is still required for StaMPS, and has been integrated in the Python scripts via the MATLAB enguine.  

* Easier installation: i.e., the environment variables are automatically managed by **EZ-InSAR**. The user only needs to install the different SAR/InSAR processors.

* Docker file for any other operating systems different than Linux. 

* New documentation (local and online). 

Toolkit structure
^^^^^^^^^^^^^^^^^

* **EZ-InSAR** now uses EZ-InSAR job containing all information and parameters. 

* **EZ-InSAR** job are stored in .xml format files allowing user's changes. 

Graphical user interface
^^^^^^^^^^^^^^^^^^^^^^^^

* New graphical user interface developed as a web application. 

Satellite and Sensors
^^^^^^^^^^^^^^^^^^^^^

* The support of COSMO-SkyMed has been deleted and will be implemented in a next version. 

* Copernicus Data Space ans ASF servers can be used for Sentinel-1 downloading (SLC and orbit files). 

* Automatic detection of Sentinel-1 track and pass. 

Processors
^^^^^^^^^^

* Doris is now supported for Sentinel-1 StripMap. 

Digital Elevation Model
^^^^^^^^^^^^^^^^^^^^^^^

* Personal DEM is now supported (with and without ellipsoid correction). 

* SRTM DEM is now supported. 

* ALOS DEM is now supported (required user account). 

For ISCE-2
^^^^^^^^^^

* More parameters for processing. 

* Geocoding of interferometric products supported. 

* The development of stack updates has been started (i.e., not fully tested). 

For Doris
^^^^^^^^^

* New implementation for StripMap data (only for Sentinel-1). 

For SNAP
^^^^^^^^

* Backscatterer intensity stacks are now supported for Sentinel-1 imagery (only IW mode). 

For StaMPS
^^^^^^^^^^

* Fix regarding the super-single-master file naming (reference vs master). 

* Extraction of displacements is now supported. 

* Full parallisation of processing possible for the steps 1-4. 

For MintPy
^^^^^^^^^^

* Extraction of displacements is now supported. 

Divers
^^^^^^

* Implementation of multispectral (Sentinel-2 and Landsat 8/9) data. 

Ongoing developments
^^^^^^^^^^^^^^^^^^^^

* Creation of an EZ-InSAR server in order to run several EZ-InSAR instances inside Docker environment. The users will run EZ-InSAR via the GUI. 

* Implementation of the SNAP processor. 

* Documentation

2.2.4 Beta (August, 2024)
---------------------------

* Fix for the egm96-15 file (only for the NASADEM and SRTM). The previous link has been deactived. The Copernicus DEM can be used to avoid any problems. 

2.2.3 Beta (April, 2024)
--------------------------

* Fix regarding the detection of the reference date for StaMPS stack (StripMap data)

2.2.2 Beta (March, 2024)
------------------------

* Modification of the orbit-server server (ASF -> Copernicus Data Space)

* Add a change-log document in the main directory

2.2.1 Beta (January, 2024)
--------------------------

* Fix the NASADEM geoid conversion

2.2.0 Beta (November, 2023)
---------------------------

* Fix the issue with the Sentinel-1 SLC list

* Add the possibility to download the S1 orbits from QSF server, via the S1 downloader.

2.1.0 Beta (September, 2023)
----------------------------

* Management of the dual-polarisation mode for TerraSAR-X and PAZ data.

2.0.3 Beta (July, 2023)
-------------------------

* Some fixes concerning the creation of the Sentinel-1 IW list.

2.0.2 Beta (April, 2023)
------------------------

* Fix for the compatibility with the last version of MintPy.

2.0.1 Beta (March, 2023)
------------------------

* Some fixes concerning the creation of the Sentinel-1 IW list.

2.0.0 Beta (August 19, 2022)
----------------------------

* Support of SAR sensors with Stripmap acquisition mode (TerraSAR-X, COSMO-SkyMed, PAZ, Sentinel-1 in Stripmap mode)

* Modification of the main interface

1.0.0 beta (March 01, 2022)
---------------------------

* Initial version
