function opendisplayer(src,evt,figmain)
%   opendisplayer(src,evt,figmain)
%       [src]           : callback value
%       [evt]           : callback value
%       [figmain]       : main figure of BWLava application
%
%       Script to open the displayer of the BWLava application
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.0.0 Beta
%   Date: 21/11/2024
%
%   -------------------------------------------------------
%   Modified:
%
%   -------------------------------------------------------
%   Version history:
%           2.0.0 Beta: Initial (unreleased)

if ishandle(figmain.UserData.Displayer)
    close(figmain.UserData.Displayer);
end 
figmain.UserData.Displayer = displayer(figmain); 