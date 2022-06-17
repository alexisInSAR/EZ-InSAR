function initparmslc(WK)
%   Function to initiate the SLC parameters
%
%   See also manageparamaterSLC, manageSLC, downloaderSLC.

%   Copyright 2021 Alexis Hrysiewicz, UCD / iCRAG2 
%   Version: 1.0.0 
%   Date: 29/11/2021

%% Initialisation 
pathSLC ='NONE';
pathorbit ='NONE'; 
pathaux ='NONE'; 
date1 ='2015-01-01'; 
date2 ='2022-01-01'; 
sat ='AB'; 
mode ='IW'; 
track ='001'; 
pass ='Desc'; 
WK=WK;
%% Save on the work directory
save([WK,'/parmsSLC.mat'],'WK','pathSLC','pathorbit','pathaux','date1','date2','sat','mode','track','pass'); 
