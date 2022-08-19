<img src="https://github.com/alexisInSAR/EZ-InSAR/blob/Version_2_0_0_Beta/EZINSAR_BIN/private/EZ_InSAR_logo.gif" alt="Logo EZ-InSAR" width="250"> 

# EZ-InSAR 

**EZ-InSAR (formerly called MIESAR for Matlab Interface for Easy InSAR)** is a toolbox written in MATLAB to conduct Interferometric Synthetic Aperture Radar (InSAR) data processing with the open-source software (ISCE+StaMPS/MintPy) packages within a easy-to-use Graphic-User-Interface (GUI). The toolbox now can generate SAR interferograms using ISCE and conduct displacement time series analysis with either Persistent Scatters (**PS**) or Small-Baselines (**SBAS**) approaches using StaMPS or MintPy. 

**EZ-InSAR** minimizes the work of user in downloading, parametrizing, and processing the SAR data, so enabling these who are not familiar with InSAR but can also produce and analyze ground surface displacements by themselves. **EZ-InSAR** is also a contribution to the Platform for Atlantic Geohazard Risk Management (AGEO) project, which is funded by Interreg Atlantic Area Programme through the *European* Regional Development Fund.


**Release info**: Version 2.0.0 Beta, August 19, 2022

**Sensors:**
| Satellite | Mode | EZ-InSAR | SLC format |
|---|---|---|---|
|Sentinel-1|IW|Ready|.zip or .SAFE in the slc directory|
|Sentinel-1|StripMap|Ready|.zip or .SAFE in the slc directory|
|PAZ|StripMap|Ready|Unzipped PAZ1_* directory in the slc directory|
|TerraSAR-X|StripMap|Ready|Unzipped TSX1_* directory in the slc directory|
|Cosmo-SkyMed|StripMap|Ready|[directory of the acquisition]/CSK*.h5 in the slc directory|
|ALOS2|StripMap|No|NE|

For the Spotlight data, EZ-InSAR can manage the data similar to StripMap but the processing with ISCE should be modified. 

Please check the guidelines to add a new sensor: [here](https://github.com/alexisInSAR/EZ-InSAR/blob/Version_2_0_0_Beta/EZINSAR_BIN/docs/guide_new_sensors.md). 

## 1. Dependencies & Installation 

**EZ-InSAR** incorporates several the most popular open source InSAR processors to perform SAR interferometry and displacement time series analysis. These processors are: 

·         **[ISCE](https://github.com/isce-framework/isce2)** - Interferometric synthetic aperture radar Scientific Computing Environment (ISCE)

·         **[StaMPS](https://homepages.see.leeds.ac.uk/~earahoo/stamps/)** - Stanford Method for Persistent Scatterers (StaMPS)

·         **[MintPy](https://github.com/insarlab/MintPy)** - The Miami INsar Time-series software in PYthon (MintPY)

Some additional dependencies are needed to run the above InSAR processors or enhancing the functions of the code. For example, you may need the TRAIN package to correct for tropospheric errors in SAR interferograms when using StaMPS, and in MintPy you may need PyAPS to do the similar work. Some toolboxes of MATLAB are also needed for successfully running the SAR processing code, which will be descripted in detail in **Part II** of the help document. 

**EZ-InSAR** is developed on a Linux platform currently. The commercial software MATLAB is needed to run **EZ-InSAR**. 

See [**Installation**](./EZINSAR_BIN/docs/MIESAR-tutorial-Part-II.md) to install and configure the depended codes and software. 

## 1.2 Running the toolbox 

After the installation and configuration, lunch "Matlab" through a terminal, and then type "EZ_InSAR". 

![EZ-InSAR Interface](./EZINSAR_BIN/docs/MIESAR_interface.bmp)

​																						   **Figure 1.** The snapshot of the interface of EZ-InSAR.

Basically, the interface contains three independent modules shown as the "Data preparation module", "ISCE InSAR processing module", and "InSAR time series analysis module". The “EZ-InSAR Paths” button allows the user to define the work path for processing the data. The StaMPS and MintPy processors can be activated by clicking the corresponding tables in the "InSAR time series analysis module" module, respectively. Also, there is a progress bar showing the running progress of each step and an information box showing the useful tip during data processing at the bottom of the interface. 

A **tutorial** on the use of the toolbox can be downloaded from [**here**](xxxxx).

## 1.3 Developers & Contact

Based on original idea and development from Alexis Hrysiewicz, EZ-InSAR is developed and maintained by the **Natural Hazard Research** group lead by **[Eoghan Holohan](https://people.ucd.ie/eoghan.holohan)** at School of Earth Sciences, ***University College Dublin*** (UCD). The people who develop and document the toolbox are acknowledged below: 

- *Alexis Hrysiewicz,* Postdoctoral Researcher, School of Earth Sciences, UCD

  Email: alexis.hrysiewicz@ucd.ie 

- *Xiaowen Wang*, Research Scientist, School of Earth Sciences, UCD & Southwest Jiaotong University 

  Email: xiaowen.wang@ucd.ie; insarswxw@swjtu.edu.cn
  
## 1.4  Acknowledgement

We acknowledge that the open-source InSAR processing software and code used by EZ-InSAR are cited properly. EZ-InSAR is distributed for free under the [**GPLV3 License**](https://www.gnu.org/licenses/gpl-3.0.html).

## 1.5 Partners

|<img src="https://github.com/alexisInSAR/EZ-InSAR/blob/Version_2_0_0_Beta/EZINSAR_BIN/private/AGEO-transparent.png" alt="AGEO" width="150pix">|[**AGEO**](https://ageoatlantic.eu/)|
|---|---|
|<img src="https://github.com/alexisInSAR/EZ-InSAR/blob/Version_2_0_0_Beta/EZINSAR_BIN/private/atlanticarealogo.png" alt="Interreg Atlantic Area" width="150pix">|[**Interreg Atlantic Area**](https://www.atlanticarea.eu/)|
|<img src="https://github.com/alexisInSAR/EZ-InSAR/blob/Version_2_0_0_Beta/EZINSAR_BIN/private/icrag-logo.png" alt="iCRAG" height="50pix">|[**iCRAG**](https://www.icrag-centre.org/)|
|<img src="https://github.com/alexisInSAR/EZ-InSAR/blob/Version_2_0_0_Beta/EZINSAR_BIN/private/UCDlogo.png" alt="UCD" height="100pix"> |[**University College Dublin**](https://www.ucd.ie/)|
|<img src="https://github.com/alexisInSAR/EZ-InSAR/blob/Version_2_0_0_Beta/EZINSAR_BIN/private/SWJTULogo.png" alt="SWJTU" height="100pix"> |[**Southwest Jiaotong University**](https://en.swjtu.edu.cn/)|
