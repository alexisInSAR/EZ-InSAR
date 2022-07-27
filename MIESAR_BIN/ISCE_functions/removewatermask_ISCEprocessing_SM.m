function removewatermask_ISCEprocessing_SM(src,evt,action,miesar_para)
%   isce_preprocessing_S1_SM(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to remove the water mask processing for StripMap
%       processing (temporary)
%
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also conversionstacks_SI_IW, isce_switch_stackfunctions, conversionstacks_SI_SM, parallelizationstepISCE, dem_box_cal, iscedisplayifg, removewatermask_ISCEprocessing_SM, isce_preprocessing_S1_IW, runISCEallstep, isce_preprocessing_SM, selectionofstack, isceprocessing.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.0.0 Beta
%   Date: 13/07/2022
%
%   -------------------------------------------------------
%   Version history:
%           2.0.0 Beta: Initial (unreleased)

%% Check the run file
file = dir([miesar_para.WK,'/configs/config_reference_*']); 
file = file.name; 

%% Read the file and save into another file
fid = fopen([miesar_para.WK,'/configs/',file],'r');
textfile = textscan(fid,'%s','Delimiter','\n'); fclose(fid); textfile = textfile{1};
idx = find(ismember(textfile, '[Function-2]')); 
if isempty(idx) == 1
    idx = length(textfile)+2; 
end 

fout = fopen([miesar_para.WK,'/configs/',file,'new'],'w');
for i1 = 1 : idx-2
    fprintf(fout,'%s\n',textfile{i1}); 
end 
fclose(fout);

%% Rename
delete([miesar_para.WK,'/configs/',file]); 
movefile([miesar_para.WK,'/configs/',file,'new'],[miesar_para.WK,'/configs/',file]); 



