function updatetable(src,evt,figmain)
%   updatetable(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [figmain]       : main figure of BWLava applicaiton
%
%       Script to update the data table
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

set(findobj(figmain,'Tag','TableData'),'Data',figmain.UserData.Data.stack2table); 

