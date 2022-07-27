function initparmslc(WK)
%   initparmslc(WK)
%       [WK]   : work workdirectory path (string value) 
%
%       Function to initiate the SLC parameters. 
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also createlistSLC, GUIpathdirectory, displayextensionS1, initparmslc, readxmlannotationS1, displayextensionTSXPAZ, manageparamaterSLC, downloaderSLC, manageSLC.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 29/11/2021
%
%   -------------------------------------------------------
%   Modified:
%           - Alexis Hrysiewicz, UCD / iCRAG, 07/07/2022: StripMap
%           implementation
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)
%           2.0.0 Beta: Initial (unreleased)

%% Initialisation 
pathSLC = [WK,'/slc'];
pathorbit =[WK,'/orbits']; 
pathaux = [WK,'/file_aux']; 
date1 ='2015-01-01'; 
date2 ='2022-01-01'; 
sat ='AB'; 
mode ='S1_IW'; 
track ='001'; 
pass ='Desc'; 
WK=WK;

%% Save on the work directory
save([WK,'/parmsSLC.mat'],'WK','pathSLC','pathorbit','pathaux','date1','date2','sat','mode','track','pass'); 
