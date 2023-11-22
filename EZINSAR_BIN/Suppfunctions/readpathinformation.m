function [configpath] = readpathinformation(file)
%   readpathinformation(file)
%       [file]           : path to pathinformation file
%
%       Function to read the path in the txt file
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 30/11/2021
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)

configpath = []; 
%[a,b] = system(['grep ''pathISCE'' ',file,' | awk ''END {print $2}''']); configpath.pathISCE = strtrim(b);
%[a,b] = system(['grep ''pathStaMPS'' ',file,' | awk ''END {print $2}''']); configpath.pathStaMPS = strtrim(b);
%[a,b] = system(['grep ''pathgdal'' ',file,' | awk ''END {print $2}''']); configpath.pathgdal = strtrim(b);
%[a,b] = system(['grep ''pathpython3'' ',file,' | awk ''END {print $2}''']); configpath.pathpython3 = strtrim(b);
[a,b] = system(['grep ''pathwget'' ',file,' | awk ''END {print $2}''']); configpath.pathwget = strtrim(b);
[a,b] = system(['grep ''ASFID'' ',file,' | awk ''END {print $2}''']); configpath.ASFID = strtrim(b);
[a,b] = system(['grep ''ASFPWD'' ',file,' | awk ''END {print $2}''']); configpath.ASFPWD = strtrim(b);
