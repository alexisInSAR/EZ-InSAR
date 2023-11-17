**This document provides alternative installation instructions using mamba instead of conda:**

Author: Maria del Mar Quiroga (University of Melbourne)

Modified by: Romain Beucher (ACCESS-NRI) / Madhiyeh Razeghi (USQ)

Date: 17 October 2023

***

## Requirements

Install base utilities for your system. Here we assume you are running an Ubuntu Linux system.

```bash
sudo apt-get update
sudo apt-get install -y build-essential
sudo apt-get install -y wget unzip git vim
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*
```

## Create an InSARenv Conda environment using Mamba

Miniforge provides a minimal conda/mamba installation which should be sufficient to run EZ_InSAR.

In your `$HOME` directory, we are going to install conda/mamba in the `conda` folder.

```bash
export CONDA_DIR=$HOME/conda

wget --quiet https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh

bash Miniforge3-Linux-x86_64.sh -b -p $CONDA_DIR
```

Put conda in path so we can use `mamba` without having to specify its full path.

```bash
export PATH=$CONDA_DIR/bin:$PATH
```

 Make sure `mamba` and `pip` are up to date and create the **InSARenv** environment.

```bash
mamba update -y  mamba pip
mamba create --name InSARenv
```

## Install InSAR processing packages and EZ-InSAR. 

In the same terminal:

```
EZINSAR_HOME="$HOME"
tools_insar=$EZINSAR_HOME/tools_insar
tool_DIR=$tools_insar/proc_insar
sudo mkdir -p $tool_DIR
```

Get the different modules from GitHub:

```
git clone https://github.com/alexisInSAR/EZ-InSAR.git $tools_insar/EZ-InSAR
sudo mv $tools_insar/EZ-InSAR $tools_insar/EZINSAR
git clone https://github.com/isce-framework/isce2.git $tool_DIR/isce2  
git clone https://github.com/insarlab/MintPy.git      $tool_DIR/MintPy 
git clone https://github.com/insarwxw/StaMPS.git      $tool_DIR/StaMPS
git clone https://github.com/dbekaert/TRAIN.git       $tool_DIR/StaMPS/TRAIN
```

Create/Modify the `configInSARenv.rc` file

```
cp $tools_insar/EZINSAR/EZINSAR_BIN/docs/config_InSARenv.template $tools_insar/config_InSARenv.rc
sed -i "/EZINSAR_HOME=/c\EZINSAR_HOME=$EZINSAR_HOME"  $tools_insar/config_InSARenv.rc
sed -i "/APS_toolbox=/c\APS_toolbox=$tool_DIR/StaMPS/TRAIN" $tool_DIR/StaMPS/TRAIN/APS_CONFIG.sh
```

**Init mamba (not just conda!)**. This will add the relevant `source` command to your `.bashrc`

I recommend setting `auto_activate_base` to `false`

```bash
mamba init
conda config --set auto_activate_base false
```

Add the following lines to your .bashrc file:

```bash
# EZ-InSAR & InSARenv
EZINSAR_HOME="$HOME"                                    
export tools_insar="$EZINSAR_HOME/tools_insar"
export tool_DIR=$tools_insar/proc_insar
alias load_insar='conda activate InSARenv; source $tools_insar/config_InSARenv.rc'
```

> [!NOTE]  
> Vim instructions:
>
>On the terminal type
>
>```vim ~/.bashrc```
>
>This will change the terminal to show your bashrc file on screen. Use the down arrow to go to the bottom of the file. Press the letter i, and the word "-- INSERT --" will appear at the bottom. Now copy the previous few lines, and paste them at the end of the file (right-click -> Paste). Press "Esc" key once, then ":" key, "w" key, and "q" key, then "Enter".


**Open a new terminal and run:**

```bash
load_insar
```

### Install ISCE. On the same terminal:

```bash
mamba  install -c conda-forge isce2
cd $tool_DIR
mamba install -c conda-forge --file ./MintPy/requirements.txt
```

### Install MintPy

```bash
pip install -e ./MintPy
```

### Install StaMPS

Make sure we have the relevant compilers installed:

```bash
sudo apt install software-properties-common
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt install -y gcc-7 g++-7
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 7
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 7
sudo update-alternatives --config gcc
sudo update-alternatives --config g++
```

Now build `StaMPS`:

```
cd $tool_DIR/StaMPS/src
make
make install
```

```
sudo apt install snaphu 
sudo apt install triangle-bin
```

### Install EZ-InSAR

```bash
mamba install fiona geopandas rasterio

cd $tool_DIR
 
wget https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

Set your ASF account and credentials. If using vim again, type:

```
vi ../EZINSAR/EZINSAR_BIN/pathinformation.txt
```
Then type "i", move around with the arrows to change the xxx's with your account-name and password:

```
ASFID    account-name
ASFPWD  password 
```
Once it's all good, "Esc", ":", "w", "q", "Enter". You should be back in the terminal.

### Run Matlab

Run MATLAB from the terminal. Type:
```
matlab 
```
