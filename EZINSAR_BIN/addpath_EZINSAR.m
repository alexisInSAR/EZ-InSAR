%%%%%%% Script to set the paths for EZ-InSAR %%%%%%%%%%%%%%
%% in your startup.m file you should have:
%%
% disp('Setting paths for EZ-InSAR: Matlab Interface for Easy InSAR...')
% run( [ getenv('EZINSAR_HOME') filesep 'addpath_EZINSAR'] )
%%

disp('Added to path: EZ-InSAR Version 2.0.1 Beta')
libdir = [ getenv('EZINSAR_BIN') filesep '.'  ];  
addpath(genpath(libdir),'-end'); 


