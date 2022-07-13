# Some guidelines to add a new sensors
***

## If the sensors is in Spotlight or StripMap (and different than ALOS2)

### 1. In GUIMIESAR.m

1. Check from the line 172, if your sensor is available. If not, add it.

### 2. In SLC_management

1. Add your sensor is createlistSLC.m.
2. Script a function like displayextensionTSXPAZ.py.
3. In manageSLC.m, in *extension* case, add your sensor and the python script.
4. In manageparameterSLC.m, add your sensors in *save* and *update* cases. 

### 3. In ISCE_functions:

1. Add the command for unpacking in isce_preprocessing_SM.m. If you have scripted your own unpacking scripts, add it in 3rdparty directory, and modify the line 694 of GUIMIESAR.m. 
2. Script a function like coarse_TSX_PAZ_baselines.py. and add it in *open_coarse_network_check* case in isceprocessing.m 


## If the sensors is in TOPSARS 

Please send an email to the authors. 

## If the sensors is ALOS2 

Please send an email to the authors.
