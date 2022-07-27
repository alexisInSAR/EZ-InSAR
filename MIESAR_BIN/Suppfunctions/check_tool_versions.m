function check_tool_versions(src,evt,action,miesar_para)
%   check_tool_versions(src,evt,[],[])
%       [src]           : callback value
%       [evt]           : callback value
%       []        
%       []   
%
%       Function to check the version of MATLAB, ISCE, StaMPS and MintPy
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.0.0 Beta
%   Date: 18/07/2022
%
%   -------------------------------------------------------
%   Version history:
%           2.0.0 Beta: Initial (unreleased)

text = []; 
test = 0; 

%% For MATLAB 

% Check the version of MATLAB 
nb_ver = version; nb_ver = strsplit(nb_ver,'R'); nb_ver = nb_ver{end}(1:end-2); nb_ver = str2num(nb_ver); 

if nb_ver < 2015
    text = [text,'\nERROR: your MATLAB version can be too old...'];  
    test = 1; 
end 

%Check the toolbox from MATLAB 
toolbox = ver; 
toolboxname = cell(1); 
for i1 = 1 : length(toolbox)
    toolboxname{i1} = toolbox(i1).Name; 
end     

% For Curve Fitting Toolbox 
if sum(contains(toolboxname,'Curve Fitting Toolbox')) == 0
    text = [text,'\nWARNING: Curve Fitting Toolbox is not available of StaMPS.']; test = 1;   
end
if sum(contains(toolboxname,'Image Processing Toolbox')) == 0
    text = [text,'\nWARNING: Image Processing Toolbox is not available of StaMPS.']; test = 1; 
end
if sum(contains(toolboxname,'Mapping Toolbox')) == 0
    text = [text,'\nWARNING: Mapping Toolbox is not available of EZ-InSAR.']; test = 1;  
end
if sum(contains(toolboxname,'Signal Processing Toolbox')) == 0
    text = [text,'\nWARNING: Signal Processing Toolbox is not available of StaMPS.']; test = 1;   
end
if sum(contains(toolboxname,'Statistics and Machine Learning Toolbox')) == 0
    text = [text,'\nWARNING: Statistics and Machine Learning Toolbox is not available of StaMPS.']; test = 1;  
end

%% For ISCE

%% For StaMPS

%% For MintPy
[a,mintpy_text] = system('/home/alexis/miniconda3/envs/MintPYenv/bin/smallbaselineApp.py -h'); 
% [a,mintpy_text] = system('smallbaselineApp.py -h'); 

if isempty(strfind(mintpy_text,'load_data')) == 0 & ...
        isempty(strfind(mintpy_text,'modify_network')) == 0 & ...
        isempty(strfind(mintpy_text,'reference_point')) == 0 & ...
        isempty(strfind(mintpy_text,'quick_overview')) == 0 & ...
        isempty(strfind(mintpy_text,'correct_unwrap_error')) == 0 & ...
        isempty(strfind(mintpy_text,'invert_network')) == 0 & ...
        isempty(strfind(mintpy_text,'correct_LOD')) == 0 & ...
        isempty(strfind(mintpy_text,'correct_SET')) == 0 & ...
        isempty(strfind(mintpy_text,'correct_troposphere')) == 0 & ...
        isempty(strfind(mintpy_text,'deramp')) == 0 & ...
        isempty(strfind(mintpy_text,'correct_topography')) == 0 & ...
        isempty(strfind(mintpy_text,'residual_RMS')) == 0 & ...
        isempty(strfind(mintpy_text,'reference_date')) == 0 & ...
        isempty(strfind(mintpy_text,'velocity')) == 0 & ...
        isempty(strfind(mintpy_text,'geocode')) == 0 & ...
        isempty(strfind(mintpy_text,'google_earth')) == 0 & ...
        isempty(strfind(mintpy_text,'hdfeos5')) == 0 
        
    % MintPy seems good. 
else
    text = [text,'\nERROR: The compability with MintPY does seems to be correct.']; test = 1;  
end 

%% Display
if test == 1
    update_textinformation([],[],[],sprintf(text),'error'); 
else
    update_textinformation([],[],[],'All seems to be good.','success'); 
end


