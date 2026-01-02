function BWLava(varargin)
%   BWLava
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.0.1 Beta
%   Date: 21/11/2024
%
%   -------------------------------------------------------
%   Modified:
%           2.0.1 Beta: Add the closing mode, Alexis Hrysiewicz, Jul. 2025
%   -------------------------------------------------------
%   Version history:
%           2.0.1 Beta: Fix (unreleased)
%           2.0.0 Beta: Initial (unreleased)

[folder,name] = fileparts(mfilename('fullpath')); 
p = genpath(folder); 
addpath(p); 

[status,errmsg] = license('checkout','Map_Toolbox');
if status == 0
    error(errmsg)
end 
[status,errmsg] = license('checkout','image_toolbox');
if status == 0
    error(errmsg)
end  

if nargin == 1
    if strcmp(varargin{1},'close')
        appmode = true;
    else
        appmode = false;
    end
else
    appmode = false;
end 

main(appmode); 


