%%%%%%% Script to set the paths for MIESAR %%%%%%%%%%%%%%
%% in your startup.m file you should have:
%%
% disp('Setting paths for MIESAR: Matlab Interface for Easy InSAR...')
% run( [ getenv('MIESAR_HOME') filesep 'addpath_MIESAR'] )
%%

disp('Added to path: MIESAR-v1.0')
libdir = [ getenv('MIESAR_BIN') filesep '.'  ];  
addpath(genpath(libdir),'-end'); 


