EZ-InSAR's documentation
########################

.. admonition:: MATLAB version
  :class: Danger

  **This new version is in Python (from the version 3). The MATLAB version is now depreciated.** Of course, it still is available from the associated GitHub branch. 

.. admonition:: EZ-InSAR
  :class: warning

  **EZ-InSAR** is still under development and tests. The current version is Beta, meaning that some bugs and uncomplete scripts/functions can be found. Please carefully read the changelog file to know/follow the main changes. 

  **This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions.**

  **EZ-InSAR will manipulate directories and files in order to optimise the storage space required by heavy SAR/InSAR computations. Please ensure that all directory paths (.ie., working directory, SLC directory, orbit directory, etc.) are PERFECTLY defined, and ONLY USED by EZ-InSAR: i.e., directories do not exist, as EZ-InSAR will have to be able to delete them.**
  
.. admonition:: Documentaton
  :class: warning

  The EZ-InSAR's Documentaton is still being written.

Welcome to **EZ-InSAR**'s documentation!

**EZ-InSAR** is a toolbox written in Python to conduct Interferometric Synthetic Aperture Radar (InSAR) data processing using the software packages within Python script or an easy-to-use Graphic-User-Interface (GUI). The toolbox now can generate SAR and InSAR products and conduct displacement time series analysis. **EZ-InSAR** offers a bridge between SAR/InSAR processors. 

Nowadays, InSAR has been widely used in measuring ground surface deformation induced by either by tectonic processes (e.g., earthquakes, volcanoes) or anthroponomic activities (e.g., mining, ground water pumping). Most of the open source InSAR code are implemented in a UNIX environment, meaning that the operator not only needs expertise in the theoretical background of InSAR, but also the UNIX system itself.

The original purpose of the development of EZ-InSAR is creating a user-friendly SAR data processing chain for ones who are not familiar with InSAR but also interested in producing and analyzing ground displacement products by themselves. The spirit of EZ-InSAR is thus minimising the work of user in downloading, parametrising, and processing SAR data and visualising the results.

The initial version of **EZ-InSAR** was a contribution to the Platform for Atlantic Geohazard Risk Management (AGEO) project, which is funded by Interreg Atlantic Area Programme through the European Regional Development Fund. AGEO aims launching several Citizens' Observatory pilots on geohazards according too regional priorities. The project also aims engaging with local communities to actively participate in risk preparedness and monitoring, and incorporate local capacities into risk management systems. 

**EZ-InSAR** is currently developed on a Linux platform. The toolbox can generate SAR interferograms and conduct displacement time series analysis. EZ-InSAR can save the results in several popular formats, which can be then imported into the other platforms such as QGIS, GMT, and Google Earth for visualization and post-analysis.

**EZ-InSAR** is still under development by the Geohazard group at School of Earth Sciences, University College Dublin (UCD). 

.. toctree::
   :maxdepth: 1
   :caption: Content of the documentation:

   readme
   quickstart
   proc_sensors
   installation
   installationprocessor
   optmodules
   dem
   use/index
   clihelp
   tutorials/index
   technical
   subprograms/index
   authors
   contrib
   acknowledgments
   changelog
   dvptplan
   issue_tracker
   licenses

.. toctree::
   :maxdepth: 1
   :caption: Quick links

   api/index
   EZ-InSAR's GitHub <https://github.com/alexisInSAR/EZ-InSAR-3>
   University College Dublin <https://www.ucd.ie>
   iCRAG <https://www.icrag-centre.org>
