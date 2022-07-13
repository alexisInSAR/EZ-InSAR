For new: 

In GUIMIESAR.m: line 694 
line 172 (check if the sensor is here)

In SLC_management

modify createlistSLC.m 
add displayextensionTSXPAZ

manageSLC.m case extension displayextensionTSXPAZ

manageparameterSLC.m save 
                      update

ISCE_functions:

isce_preprocessing_SM %% Command for unpacking
elseif strcmp(paramslc.mode,'PAZ_SM') == 1 | strcmp(paramslc.mode,'PAZ_SPT') == 1
        if exist([paramslc.pathSLC,'/',list{1}{i1}]) == 7
            pathinput = [paramslc.pathSLC,'/',list{1}{i1}];

            cmdi = ['unpackFrame_PAZ.py -i ',pathinput,' -o ',[pathout,'/',di]];
            cmd = [cmd,sprintf('%s\n',cmdi)];
        end
    end


isceprocessing open_coarse_network_check

StaMPS: stampsprocessing singlemasterstack 

MintPy: mintpy_parameters.m initialisation_parameters


