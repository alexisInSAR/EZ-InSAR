# EZ-InSAR's Read-Me

![image info](https://img.shields.io/badge/python-3.10-green)
![image info](https://img.shields.io/badge/-documentation-blue)
![image info](https://img.shields.io/badge/Version-3-green)

> [!CAUTION]
> **This new version is in Python (from the version 3). The MATLAB version is now depreciated.** Of course, it still is available from the associated GitHub branch. 

> [!WARNING]
> **EZ-InSAR** is still under development and tests. The current version is Beta, meaning that some bugs and uncomplete scripts/functions can be found. Please carefully read the changelog file to know/follow the main changes. 
> 
> **This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions.**
> 
> **EZ-InSAR will manipulate directories and files in order to optimise the storage space required by heavy SAR/InSAR computations. Please ensure that all directory paths (.ie., working directory, SLC directory, orbit directory, etc.) are PERFECTLY defined, and ONLY USED by EZ-InSAR: i.e., directories do not exist, as EZ-InSAR will have to be able to delete them.**
  

> [!WARNING]
> The EZ-InSAR's Documentation is still being written.

**EZ-InSAR** is a toolbox written in Python to conduct Interferometric Synthetic Aperture Radar (InSAR) data processing using the software packages within Python script within a full and comprehensive environment. The toolbox now can generate SAR and InSAR products and conduct displacement time series analysis, based on the most robust and well-known SAR/InSAR processors. **EZ-InSAR** is thefeore a bridge/wrapper of several SAR/InSAR processors. EZ-InSAR can be used via: (1) Python scripting; (2) command-line interface; and (3) an easy-to-use Graphic-User-Interface (GUI). 

![image info](private/overview.png)

## EZ-InSAR structure

**EZ-InSAR contains a core and several optional modules. The EZ-InSAR core is provided with several modules to manipulate SAR/InSAR data, GUI, DEM tools, etc. The core is offered with a large amount of processor and sensor modules.**

**However, EZ-InSAR proposes several optional modules to get new features and advanced techniques. No modules are required to process InSAR data, but they allow to complete EZ-InSAR.** 

> [!NOTE]
> After retrieving an **EZ-InSAR** optional modules, their installation can be done by using *pip3*. **EZ-InSAR** will therefore unlock the new features: (1) new scripts and (2) new documentation. 

**The public release of EZ-InSAR is offered with**:

* EZ-InSAR-Module-Desktop;

* EZ-InSAR-Module-TSDisplayer.

## Use of EZ-InSAR

In your favorite terminal, you can use **EZ-InSAR** by typing:

```bash
  ezinsar <command> args [options]
```

The documentation of **EZ-InSAR** can be launched with this command: 

```bash  
  ezinsar docs 
```

The main asset of **EZ-InSAR** is that it can be used within any Python scripts, or controlled by its Graphic User Interface. Please see the corresponding documentation. 

## What's New?

**EZ-InSAR** is under continous development. The user should read the change log in order to have an clear idea of recent changes. 

## License

**EZ-InSAR** is distributed for free under the [**GPLV3 License**](https://www.gnu.org/licenses/gpl-3.0.html).

**EZ-InSAR** use various Python packages and depencendies. Please see the following files: 

- *PYTHONPACKAGES* is the list of Python packages imported by **EZ-InSAR**. 
- *THIRDPARTYLICENSES* is the list of **EZ-InSAR** depencendies; 
- *THIRDPARTYMOD* is the list of 3rd-party scripts redistributed with **EZ-InSAR**.

The documentation is copyrighted by Alexis Hrysiewicz and distributed under *CC BY* (Creative Commons Attribution 4.0 license). 

**Please ensure that you comply with the licences for each SAR/InSAR processor, file (i.e. DEMs), etc.**

## Acknowledgements

We acknowledge that the open-source InSAR processing software and codes used by **EZ-InSAR** are cited properly. 

For EZ-InSAR, please use the following reference: 

- Hrysiewicz, A., Wang, X. & Holohan, E.P. EZ-InSAR: An easy-to-use open-source toolbox for mapping ground surface deformation using satellite interferometric synthetic aperture radar. Earth Sci Inform (2023). https://doi.org/10.1007/s12145-023-00973-1

## Partners

**University College Dublin**

<a href="https://www.ucd.ie/"><img src="https://www.ucd.ie/t4media/crest-ucd.svg" alt="https://www.ucd.ie/" height="200"/></a>

**Research Ireland Centre for Applied Geosciences (iCRAG)**

<a href="https://www.icrag-centre.org/"><img src="https://www.icrag-centre.org/t4media/iCRAG_RI_stacked-new_digital-01%20(2)(1).png" alt="https://www.icrag-centre.org/" height="100"/></a>

**Based on the original idea of EZ-InSAR-2 developed during the AGEO project:**

<a href="https://ageoatlantic.eu/"><img src="https://ageoatlantic.eu/wp-content/uploads/2019/06/AGEO-transparent.png" alt="https://www.icrag-centre.org/" height="100"/></a> <a href="https://www.atlanticarea.eu/"><img src="https://ageoatlantic.eu/wp-content/uploads/2019/08/Logo_Interreg-Atlantic-Area_COLOR-FULL-300x81.png" alt="https://www.icrag-centre.org/" height="75"/></a>

