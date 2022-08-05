%%%%%%% Script to set the paths for EZ-InSAR %%%%%%%%%%%%%%
%% in your startup.m file you should have:
%%
% disp('Setting paths for MIESAR: Matlab Interface for Easy InSAR...')
% run( [ getenv('MIESAR_HOME') filesep 'addpath_MIESAR'] )
%%

disp('Added to path: EZ-InSAR Version 1.0.0 Beta')
libdir = [ getenv('MIESAR_BIN') filesep '.'  ];  
addpath(genpath(libdir),'-end'); 


