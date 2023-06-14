**This document provides alternative installation instructions using mamba instead of conda:**

Author: Maria del Mar Quiroga (University of Melbourne)

Date: 14 June 2023

Source: https://github.com/alexisInSAR/EZ-InSAR/issues/54 

***

1. Install mamba and other ubuntu and python libraries. Open a terminal and paste:
```
curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh
bash Mambaforge-Linux-x86_64.sh 
sudo apt install gcc g++ gawk tcsh build-essential make git
pip install wget gitpython tree mamba
```

2. Create a Python virtual environment. In the same terminal:
```
sudo apt install python3.8-venv
python -m venv InSARenv
source InSARenv/bin/activate
````

3. Install InSAR processing packages and EZ-InSAR. In the same terminal:
```
EZINSAR_HOME="$HOME"
tools_insar=$EZINSAR_HOME/tools_insar
tool_DIR=$tools_insar/proc_insar
sudo mkdir -p $tool_DIR
```
```
sudo git clone https://github.com/alexisInSAR/EZ-InSAR.git $tools_insar/EZ-InSAR
sudo mv $tools_insar/EZ-InSAR $tools_insar/EZINSAR
sudo git clone https://github.com/isce-framework/isce2.git $tool_DIR/isce2  
sudo git clone https://github.com/insarlab/MintPy.git      $tool_DIR/MintPy 
sudo git clone https://github.com/insarwxw/StaMPS.git      $tool_DIR/StaMPS
sudo git clone https://github.com/dbekaert/TRAIN.git       $tool_DIR/StaMPS/TRAIN
```
```
sudo cp $tools_insar/EZINSAR/EZINSAR_BIN/docs/config_InSARenv.template $tools_insar/config_InSARenv.rc
sudo sed -i "/EZINSAR_HOME=/c\EZINSAR_HOME=$EZINSAR_HOME"  $tools_insar/config_InSARenv.rc
sudo sed -i "/APS_toolbox=/c\APS_toolbox=$tool_DIR/StaMPS/TRAIN" $tool_DIR/StaMPS/TRAIN/APS_CONFIG.sh
```

4. Add the following lines to your .bashrc file:
````
# EZ-InSAR & InSARenv
EZINSAR_HOME="$HOME"                                          
export tools_insar="$EZINSAR_HOME/tools_insar"
alias load_insar='conda activate InSARenv; source $tools_insar/config_InSARenv.rc'
````

Vim instructions:

On the terminal type

```vi ~/.bashrc```


This will change the terminal to show your bashrc file on screen. Use the down arrow to go to the bottom of the file. Press the letter i, and the word "-- INSERT --" will appear at the bottom. Now copy the previous few lines, and paste them at the end of the file (right-click -> Paste). Press "Esc" key once, then ":" key, "w" key, and "q" key, then "Enter".

Then you will be back on the regular terminal. Run:

```
source ~/.bashrc
load_insar
```

5. Install ISCE. On the same terminal:
```
mamba  install -c conda-forge isce2
 
cd $tool_DIR
mamba install -c conda-forge --file ./MintPy/requirements.txt
```

7. Install MintPy. **Close the terminal and restart** for above changes to take effect!
```
sudo python -m pip install -e ./MintPy
```

8. Install StaMPS

```
sudo apt install software-properties-common
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt install -y gcc-7 g++-7
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 7
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 7
sudo update-alternatives --config gcc
sudo update-alternatives --config g++
```
```
cd $tool_DIR/StaMPS/src
sudo make
sudo make install

sudo apt install snaphu 
sudo apt install triangle-bin
```

9. Install EZ-InSAR
```
mamba install fiona geopandas rasterio

cd $tool_DIR
 
sudo curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o "awscliv2.zip"
sudo unzip awscliv2.zip
sudo ./aws/install
```

10. Set your ASF account and credentials. If using vim again, type:
```
vi ../EZINSAR/EZINSAR_BIN/pathinformation.txt
```
Then type "i", move around with the arrows to change the xxx's with your account-name and password:

```
ASFID    account-name
ASFPWD  password 
```
Once it's all good, "Esc", ":", "w", "q", "Enter". You should be back in the terminal.

11. Run MATLAB from the terminal. Type:
```
matlab 
```
