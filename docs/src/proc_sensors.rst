SAR and InSAR processors and sensors
====================================

**EZ-InSAR** incorporates the most popular InSAR processors to perform SAR interferometric and displacement time-series analysis. 

**Overall, the current open-source processors are:**

* **ISCE-2** - *Interferometric synthetic aperture radar Scientific Computing Environment (ISCE-2)*. ISCE-2 is an InSAR processing software developed by NASA's Jet Propulsion Laboratory (JPL) and it is currently the best free available software of its kind. For Sentinel-1 TOPS data, ISCE-2 provides a set of applications (e.g., topsApp.py and stackSentinel.py) to easily control the data processing.
* **StaMPS** - *Stanford Method for Persistent Scatterers (StaMPS)*. StaMPS is a software package that can implement PS or SBAS methods to extract ground displacements from time series of synthetic aperture radar (SAR) acquisitions. The original version was developed at Stanford University but subsequent development has taken place at the University of Iceland, Delft University of Technology and the University of Leeds.
* **MintPy** - *The Miami INsar Time-series software in Python (MintPy)*. MintPy is an open-source package for InSAR time series analysis. It can read the stack of interferograms (coregistered and unwrapped) and produces three-dimensional (2D in space and 1D in time) ground surface displacement in line-of-sight direction. It includes a routine time series analysis application (i.e., smallbaselineApp.py) and some independent toolbox.
* **SNAP** - *Sentinel Application Platform (SNAP)*. SNAP is a common architecture for all Sentinel Toolboxes. The SNAP architecture is ideal for Earth observation (EO) processing and analysis due to the following technological innovations: extensibility, portability, modular rich client platform, generic EO data abstraction, tiled memory management, and a graph processing framework. SNAP and the individual Sentinel Toolboxes support numerous sensors other than Sentinel sensors.
* **Doris** - *Delft object-oriented radar interferometric software (Doris)*. Delft Institute of Earth Observation and Space Systems of Delft University of Technology has developed an Interferometric Synthetic Aperture Radar (InSAR) processor named Doris. The Doris software can be downloaded freely from this site for non-commercial applications (conditions).
* **LiCSBAS**. LiCSBAS is an open-source package in Python and bash to carry out InSAR time series analysis using LiCSAR products (i.e., unwrapped interferograms and coherence) which are freely available on the COMET-LiCS web portal.

**The next tables gives the compatibility between available sensors and processors in EZ-InSAR (X for No, O for Yes)**: 

Processors available for SAR/InSAR processing
---------------------------------------------

+--------------+------------------------------+------------------------------+----------------------+---------------------------------+
| Processor    | Coregistration               | Interferometric stack        | Time-Series analysis | Remark                          |
+==============+==============================+==============================+======================+=================================+
|| **ISCE2**   || O                           || O                           ||                     ||                                |
|| **SNAP**    || O                           || O                           ||                     ||                                |
|| **Doris**   || Only for StripMap-like data || Only for StripMap-like data ||                     ||                                |
|| **StaMPS**  ||                             ||                             || O                   || PS, SBAS and merged approaches |
|| **MintPy**  ||                             ||                             || O                   || SBAS approach                  |
|| **LiCSBAS** ||                             ||                             || O                   || SBAS approach                  |
+--------------+------------------------------+------------------------------+----------------------+---------------------------------+

Sensors available for InSAR processing
--------------------------------------

+-------------------------------------+------------------------+-------+---------------------------+-----------------------------------------------------------------------------+---------------+
| Satellite                           | Mode                   | Ready | Supported InSAR processor | Remarks                                                                     | EZ-InSAR keys |
+-------------------------------------+------------------------+-------+---------------------------+-----------------------------------------------------------------------------+---------------+
|| **Sentinel-1**                     || *IW*                  || O    || ISCE2, LiCSBAS, SNAP     || A, B and C / Automatic downloading                                         || S1 - IW      |
||                                    || *StripMap*            || O    || ISCE2, Doris, SNAP       || -                                                                          || S1 - SM      |
|| **TerraSAR-X**                     || *ScanSAR*             || X    ||                          || TSX and TDM                                                                || TSX - SC     |
||                                    || *StripMap*            || O    || ISCE2, Doris             || Under tests. ISCE and Doris will read only one Pol.                        || TSX - SM     |
||                                    || *Spotlight*           || O    || ISCE2, Doris             || Not tested with ISCE2. Under tests. ISCE and Doris will read only one Pol. || TSX - SPT    |
||                                    || *HS-Spotlight*        || O    || ISCE2, Doris             || Not tested with ISCE2                                                      || TSX - HSSPT  |
||                                    || *Staring-Spotlight*   || O    || ISCE2                    || Not tested with ISCE2                                                      || TSX - STSPT  |
|| **PAZ**                            || *StripMap*            || O    || ISCE2, Doris             || Not tested with ISCE2. Under tests. ISCE and Doris will read only one Pol. || PAZ - SM     |
||                                    || *Spotlight*           || O    || ISCE2, Doris             || Not tested with ISCE2. Under tests. ISCE and Doris will read only one Pol. || PAZ - SPT    |
||                                    || *HS-Spotlight*        || O    || ISCE2, Doris             || Not tested with ISCE2. Under tests. ISCE and Doris will read only one Pol. || PAZ - HSSPT  |
||                                    || *Staring-Spotlight*   || O    || ISCE2                    || Not tested with ISCE2                                                      || PAZ - STSPT  |
|| **COSMO-SkyMed**                   || *HIMAGE*              || O    || Doris, ISCE2             || Under test. ISCE and Doris will read only one Pol.                         || CSK - HI     |
||                                    || *PingPong*            || O    ||                          || Implementation in progress                                                 || CSK - PP     |
||                                    || *ScanSAR Wide*        || X    ||                          || Implementation in progress                                                 || CSK - SW     |
||                                    || *ScanSAR Huge*        || X    ||                          || Implementation in progress                                                 || CSK - PP     |
|| **COSMO-SkyMed Second Generation** || *StripMap*            || O    ||                          || Implementation in progress                                                 || CSK - SM     |
||                                    || *PingPong*            || O    ||                          || Implementation in progress                                                 || CSK - PP     |
||                                    || *Quad Pol*            || X    ||                          || Implementation in progress                                                 || CSK - QP     |
||                                    || *ScanSAR-1*           || X    ||                          || Implementation in progress                                                 || CSK - SC1    |
||                                    || *ScanSAR-2*           || X    ||                          || Implementation in progress                                                 || CSK - SC2    |
|| **ALOS1**                          || *StripMap*            || O    || ISCE2                    || Under tests                                                                || ALOS - SM    |
||                                    || *Spotlight*           || O    || ISCE2                    || Under tests                                                                || ALOS - SPT   |
||                                    || *ScanSAR*             || X    ||                          || Under tests                                                                || ALOS - SC    |
|| **ALOS2**                          || *StripMap*            || O    || ISCE2                    || Under tests                                                                || ALOS2 - SM   |
||                                    || *Spotlight*           || O    || ISCE2                    || Under tests                                                                || ALOS2 - SPT  |
||                                    || *ScanSAR*             || X    ||                          || Under tests                                                                || ALOS2 - SC   |
|| **RADARSAT-1**                     || *Standard*            || X    ||                          || Implementation in progress                                                 || RSAT - STD   |
||                                    || *Fine*                || X    ||                          || Implementation in progress                                                 || RSAT - Fine  |
||                                    || *Wide*                || X    ||                          || Implementation in progress                                                 || RSAT - Wide  |
||                                    || *Extended*            || X    ||                          || Implementation in progress                                                 || RSAT - EXT   |
||                                    || *ScanSAR*             || X    ||                          || Implementation in progress                                                 || RSAT - SC    |
|| **RADARSAT-2**                     || *StripMap Quad. Pol.* || O    || Doris, ISCE2             || Under test. ISCE and Doris will read only one Pol.                         || RSAT2 - FQ   |
||                                    || *Fine Quad. Pol*      || O    || Doris, ISCE2             || Under test. ISCE and Doris will read only one Pol.                         || RSAT2 - FQ   |
+-------------------------------------+------------------------+-------+---------------------------+-----------------------------------------------------------------------------+---------------+

Please find the sources of data used for implementation: 

* Sentinel-1: Copernicus Data Space Ecosystem amd Alaska Satellite Facility

* TerraSAR-X: https://earth.esa.int/eogateway/missions/terrasar-x-and-tandem-x/sample-data

* PAZ: https://earth.esa.int/eogateway/missions/paz/sample-data

* COSMO-SkyMed: https://earth.esa.int/eogateway/missions/cosmo-skymed/sample-data

* COSMO-SkyMed Second Generation: https://earth.esa.int/eogateway/missions/cosmo-skymed-second-generation/sample-data 

* ALOS1: Alaska Satellite Facility

* ALOS2: https://www.eorc.jaxa.jp/ALOS/en/alos-2/datause/a2_sample_e.htm

* RADARSAT-1: https://earth.esa.int/eogateway/missions/radarsat/sample-data

* RADARSAT-2: https://earth.esa.int/eogateway/catalog/radarsat-2-esa-archive 


Sensors available for SAR backscatter-intensity computation
-----------------------------------------------------------

+----------------+----------------+--------------+--------+
| Satellite      | Processor      | Variables    | Remark |
+================+================+==============+========+
| **Sentinel-1** | SNAP (only IW) | sigma0 and 0 |        |
+----------------+----------------+--------------+--------+

Sensors available for Offset-tracking computation
-------------------------------------------------

Processor regarding the operating system
----------------------------------------

+--------------+-----------------------------------+-------------------------------------------------------+-------+
| Processor    | Windows                           | MacOS                                                 | Linux |
+==============+===================================+=======================================================+=======+
|| **ISCE2**   ||                                  || The user needs to compiles the sources or use Docker || Yes  |
|| **Doris**   || Yes (EZ-InSAR uses Docker)       || The user needs to compiles the sources or use Docker || Yes  |
|| **StaMPS**  || No                               || The user needs to compiles the sources               || Yes  |
|| **MintPy**  || Not tested but Yes (theorically) || Yes                                                  || Yes  |
|| **LiCSBAS** || Not tested but Yes (theorically) || Yes                                                  || Yes  |
|| **SNAP**    || Yes                              || Yes                                                  || Yes  |
+--------------+-----------------------------------+-------------------------------------------------------+-------+

**However, for MacOS Silicon and Windows system, we recommend using the Docker version of EZ-InSAR.**

**The use of Docker will increase the computing time, especially for Windows.**

Servers available with **EZ-InSAR**
-----------------------------------

+----------------------------+------------------------------------+-------------------------------+----------------+
| Server                     | Imagery/Files                      | Features                      | Identification |
+============================+====================================+===============================+================+
|| **Copernicus Data Space** || Sentinel-1, Sentinel-2, S1 orbits || Partial downloading possible || ID / Password |
|| **ASF**                   || Sentinel-1, S1 orbits             || Burst splitting possible     || ID / Password |
|| **EarthDATA**             || Sentinel-1                        ||                              || ID / Password |
|| **GEODES**                || Sentinel-1, Sentinel-2,S1 orbits  || Implementation in progress   || Token         |
|| **THEIA**                 || Sentinel-2, etc.                  || Implementation in progress   || ID / Password |
+----------------------------+------------------------------------+-------------------------------+----------------+
