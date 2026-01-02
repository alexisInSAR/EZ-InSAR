function rerunstepfromtable(src,evt,figmain)
%   rerunstepfromtable(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : action name
%
%       Script to process the processing steps
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
% 

if evt.Indices(2) == 4
    idx = evt.Indices(1); 
    if isempty(figmain.UserData.Data.coherencecrop)==0
        figmain.UserData.Data.kernelfilt(idx) = evt.NewData; 
        figmain.UserData.Data.coherencefilt(:,:,idx) = medfilt2(figmain.UserData.Data.coherencecrop(:,:,idx),[figmain.UserData.Data.kernelfilt(idx),figmain.UserData.Data.kernelfilt(idx)]);
    else
        uimsg = uiconfirm(figmain,'Please run the cropping before to modify the filter kernel. However this value will be used.','Warning');
    end 
elseif evt.Indices(2) == 5
    if isempty(figmain.UserData.Data.coherencecrop)==0
        idx = evt.Indices(1); 
        figmain.UserData.Data.thesholdvalue(idx) = evt.NewData;
        figmain.UserData.Data.maskraw(:,:,idx) = double(im2bw(figmain.UserData.Data.coherencefilt(:,:,idx),figmain.UserData.Data.thesholdvalue(idx)));
        uimsg = uiconfirm(figmain,'The initial mask has been modified. Please re-run the lava detector.','Warning');
    else
        uimsg = uiconfirm(figmain,'Please run the segmentation before to modify the segmenation threshold.','Warning');
    end      

end 

if ishandle(figmain.UserData.Displayer)
    updatedisplayer([],[],figmain);
end 

