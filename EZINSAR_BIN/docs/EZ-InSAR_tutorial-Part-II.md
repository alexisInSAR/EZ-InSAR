# <font face="Times New Roman" size = "8">**Part II** </font> 

-----------------------------------------------


# <font face="Times New Roman" size="6">**Installation and configuration** </font> 

***[Ubuntu  20.04], updated on 03 August, 2022***




## 2.1. Setup Python environment

### 2.1.1 Check and install *conda* distribution 

It is recommended to use *conda* to install the python environment and the prerequisite packages. Either the [*Anconda*](https://docs.anaconda.com/anaconda/install/index.html) or [*Miniconda*](https://docs.conda.io/en/latest/miniconda.html) distributions are applicable, while we suggest using *Miniconda* since it is a small, bootstrap version of Anaconda.

- Check whether the *conda* distribution has already been installed. If  you have already installed *conda*, go to the **Step 2.1.2.**

```bash
conda -V
```

-  Install *Miniconda*  if no conda distribution is detected.  By default, it will be installed in the `$HOME` directory. 

```bash
mkdir -p ~/mconda; cd ~/mconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/mconda/miniconda3
~/mconda/miniconda3/bin/conda init bash
```

- Close and restart the shell for changes to take effect.

### 2.1.2 Create virtual Python environment: InSARenv 

Here we create a virtual environment "*InSARenv*", and all the packages supporting the EZ-InSAR toolbox will be installed in this Python environment.

```bash
# A. Install the basic tools and utils 

sudo apt install gcc g++ gawk tcsh build-essential make git
conda config --add channels conda-forge
conda config --set channel_priority strict
conda install wget git tree mamba --yes

# B. Create InSARenv & activate it 

conda create --name InSARenv --yes
conda activate InSARenv
```

### 2.1.3 MATLAB  

MATLAB is used to run EZ-InSAR, thus you need a licensed MATLAB installed on your computer. Also, the InSAR post-processing with StaMPS will also use MATLAB, and the successful running of StaMPS need some specific MATLAB toolbox to be pre-installed. 

- Check MATLAB has been installed on your OS, and can be accessed in a terminal. 

```bash
#A. Check whether MATLAB has been installed and be launched 

which matlab 

#B. If the echo of "which matlab" is null, then install MATLAB first, and then specify the MATLAB PATH below, and create a soft-link it to the directory '/usr/bin'

matlab_install_path="ADD-THE-MATLAB-PATH-HERE"
sudo ln -s $matlab_install_path/bin/matlab /usr/bin

#C. Then start MATLAB in a terminal
matlab 
```

- Type `ver`  in MATLAB and check whether the toolboxes below are available. If some of them are not installed, just click "Add-Ons" ---> "Get Add-Ons" in the MATLAB interface menu to fix the installation. 

```matlab
>> ver
-----------------------------------------
Curve Fitting Toolbox 
Financial Toolbox 
Image Processing Toolbox 
Mapping Toolbox 
Optimization Toolbox
Parallel Computing Toolbox 
Signal Processing Toolbox 
Statistics and Machine Learning Toolbox 
```



## 2.2 Install InSAR processing packages and EZ-InSAR

This part will first show the "Preparations" you have to do,  including the download of the required software or packages.  Then, the installations of the three InSAR processors "ISCE", "MintPy", and "StaMPS" will be illustrated. Finally, it will give a instruction on the configuration of EZ-InSAR. 

### 2.2.1 Preparations

```bash
# A. Define the path where you want the packages to be installed (Default:Your HOME path-"$HOME") 

EZINSAR_HOME="$HOME"           		  #Set the install path 

tools_insar=$EZINSAR_HOME/tools_insar
tool_DIR=$tools_insar/proc_insar
sudo mkdir -p $tool_DIR

# B. Download the source code (EZ-InSAR, ISCE, MintPy, StaMPS, TRAIN)
## Download EZ-InSAR source file, and put the unzipped EZ-InSAR into the "EZINSAR" directory in $tool_insar.

sudo git clone https://github.com/alexisInSAR/EZ-InSAR.git $tools_insar/EZ-InSAR
sudo mv $tools_insar/EZ-InSAR $tools_insar/EZINSAR

## Download the InSAR processor codes 
sudo git clone https://github.com/isce-framework/isce2.git $tool_DIR/isce2  
sudo git clone https://github.com/insarlab/MintPy.git      $tool_DIR/MintPy 
sudo git clone https://github.com/insarwxw/StaMPS.git      $tool_DIR/StaMPS
sudo git clone https://github.com/dbekaert/TRAIN.git       $tool_DIR/StaMPS/TRAIN

# C. Edit the configuration file
## 1) - Copy the configure template file "config_InSARenv.template" from the "EZINSAR/EZINSAR_BIN/docs/" directory into "$tools_insar";  
##    - Check and replace the PATH variable "$EZINSAR_HOME" in "config_InSARenv.rc" (Line #3). 
##    - Check and replace the Path varialbe $APS_toolbox in TRAIN 
##    - The other variables do not need to be modified if you strictly follow this install instruciton.

sudo cp $tools_insar/EZINSAR/EZINSAR_BIN/docs/config_InSARenv.template $tools_insar/config_InSARenv.rc

sudo sed -i "/EZINSAR_HOME=/c\EZINSAR_HOME=$EZINSAR_HOME"  $tools_insar/config_InSARenv.rc
sudo sed -i "/APS_toolbox=/c\APS_toolbox=$tool_DIR/StaMPS/TRAIN" $tool_DIR/StaMPS/TRAIN/APS_CONFIG.sh

## 2) Add the following lines in your "$HOME/.bashrc" file. 
##    Note you have to change the variable "$EZINSAR_HOME" if it is installed in a differnt PATH (e.g., /usr/local). 

# EZ-InSAR & InSARenv
EZINSAR_HOME="$HOME"           		 
export tools_insar="$EZINSAR_HOME/tools_insar"
alias load_insar='conda activate InSARenv; source $tools_insar/config_InSARenv.rc'

# **IMPORTANT**: Run `load_insar` in the terminal to load the "InSARenv" environmental and PATH variables before running EZ-InSAR each time.
```

### 2.2.2 Install ISCE 

ISCE-2 is now available on the `conda-forge` channel. Thus, one could install it by simply running:

```bash
conda install -c conda-forge isce2
```

### 2.2.3 Install MintPy

MintPy is written purely in Python. So, the use of MintPy just needs the installation of dependent python packages and then setup the environment variables properly. Please also refer the newest help information of [**MintPy installation**](https://github.com/insarlab/MintPy/blob/main/docs/installation.md).
**NOTE** You may need to fix the python version to a lower version (e.g., python=3.8) since the incompatiable error when using isce2 for python 3.10. (see [isce2 error for python > 3.10](https://github.com/isce-framework/isce2/issues/458)). 

```bash
# Install the mintpy requirements first and then the source code.
# 
cd $tool_DIR
conda install -c conda-forge --file ./MintPy/requirements.txt

#Close and restart the shell for changes to take effect
python -m pip install -e ./MintPy
```

### 2.2.4 Install StaMPS

- Check the *gcc* version of your OS first because the `src` code in StaMPS only supports gcc-7.  
- However, the default *gcc/g++* in Ubuntu 20.04 is gcc-9 or above. If in this case, you need to install the gcc-7 first.  
- Follow the [**instruciton**](https://linuxconfig.org/how-to-switch-between-multiple-gcc-and-g-compiler-versions-on-ubuntu-20-04-lts-focal-fossa) here to set the proper gcc/g++ versions.  If the error such as "E: Package 'gcc-7' has no installation candidate" appear, please refer to the solution **[here](https://askubuntu.com/questions/1406962/install-gcc7-on-ubuntu-22-04)**. 

```bash
### check which version of gcc
gcc -v  
#$ gcc version 9.3.0 (Ubuntu 9.3.0-17ubuntu1~20.04)

sudo apt install software-properties-common
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt install -y gcc-7 g++-7
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 7
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 7
sudo update-alternatives --config gcc
sudo update-alternatives --config g++ 
```

- Compile the `src` files and install the required dependencies 

```bash
# A. Compile the files in the "src" directory in StaMPS

cd $tool_DIR/StaMPS/src
sudo make
sudo make install

# B. Install "snaphu" & "triangle"  
# After the installation, run `which snaphu` && `which triangle` in the terminal to check their paths. 
# If the echo paths are not "/usr/bin", then modify the varialbes "SNAPHU_BIN" and "TRIANGLE_BIN" in the "config_InSARenv.rc" to the correct values.

sudo apt install snaphu 
sudo apt install triangle-bin
```

### 2.2.5 Install EZ-InSAR 

- Install the dependencies of some python script required by EZ-InSAR to your InSARenv.

```bash
conda install fiona geopandas rasterio
```

- EZ-InSAR uses "[aws](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)" to download the NASADEM or Copernicus DEM. Using the following commands to install it. 

```bash
cd $tool_DIR
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo unzip awscliv2.zip
sudo ./aws/install
```


- Set your ASF account and credentials for downloading the Sentinel-1 SAR data in "pathinformation.txt" in EZINSAR_BIN.

```bash
ASFID 	account-name
ASFPWD  password 
```



## 2.3 Test the installation and additional notes

### 2.3.1 Test the installation 

- Open a new terminal, and type the commands below to check the PATH environment 

```bash
source $HOME/.bashrc
load_insar  # warm up conda environment
echo $PATH
echo $TOOL_DIR $DATA_DIR $WEATHER_DIR
```

- Run the following to test the installation:

```bash
###         
topsApp.py -h            # test ISCE-2
smallbaselineApp.py -h   # test MintPy
solid_earth_tides.py -h  # test PySolid
tropo_pyaps3.py -h       # test PyAPS
mt_prep_isce             # test StaMPS
```


### 2.3.2 Some important notes for running MintPy

 **(1) Notes on account setup for [ERA5](https://retostauffer.org/code/Download-ERA5/)**

MintPy has the option of using ERA5 to correct for tropospheric delay. ERA5 data set is redistributed over the Copernicus Climate Data Store (CDS). Registration is required for the data access and downloading.

+ [Create a new account](https://cds.climate.copernicus.eu/user/register) on the CDS website if you don't own a user account yet. 
+ Create a file named `.cdsapirc` in your `$HOME` directory and add the following two lines:

```shell
url: https://cds.climate.copernicus.eu/api/v2
key: 12345:abcdefghij-134-abcdefgadf-82391b9d3f
```

> where *12345* is your personal user ID (UID), *the part behind the colon* is your personal API key. More details can be found [here](https://cds.climate.copernicus.eu/api-how-to). **Make sure** that you accept the data license in the Terms of use on ECMWF website.

- Test the account setup for ERA5 by running:

```bash
git clone https://github.com/insarlab/PyAPS.git --depth 1
python PyAPS/tests/test_dload.py
```

`WEATHER_DIR`: Optionally, if you defined an environment variable named `WEATHER_DIR` to contain the path to a directory, MintPy applications will download  the GAM files into the indicated directory. You can change `WEATHER_DIR`  in the configure file "config_InSARenv.rc". Also, the MintPy application will look for the GAM files in the directory before downloading a new  one to prevent downloading multiple copies if you work with different  dataset that cover the same date/time.

**(2) Notes on [dask](https://docs.dask.org) for parallel processing**

MintPy uses [dask](https://docs.dask.org) for the parallel processing at some of the steps. It is recommended  setting the `temporary-directory` in  [Dask configuration file](https://docs.dask.org/en/stable/configuration.html), e.g. `~/dask/dask.yaml`, by adding the following line, to avoid potential [workspace lock issue](https://github.com/insarlab/MintPy/issues/725). Check more details on parallel processing with Dask [here](./dask.md).

```yaml
temporary-directory: /tmp  # Directory for local disk like /tmp, /scratch, or /local

## If you are sharing the same machine with others, use the following instead to avoid permission issues with others.
# temporary-directory: /tmp/{replace_this_with_your_user_name}  # Directory for local disk like /tmp, /scratch, or /local
```

===============================**END**====================================
