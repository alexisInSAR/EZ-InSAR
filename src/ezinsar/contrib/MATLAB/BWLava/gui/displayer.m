function hdl = displayer(figmain)
%   displayer(figmain)
%       [figmain]           : main figure of BWLava application
%
%       Script to create the Displayer of BWLava application
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

figdisplayer = uifigure('Position',[700 91 932 731],'Name','BWLava Application: Displayer','HandleVisibility','on','Visible','off');
gridfigdisplayer = uigridlayout(figdisplayer,[10 10]);

labellistdisplayer = uilabel(gridfigdisplayer,'Text','Selected coherence image','HorizontalAlignment','center','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
labellistdisplayer.Layout.Row = [1];
labellistdisplayer.Layout.Column = [1 3];

listdisplayer = uidropdown(gridfigdisplayer,"Items",figmain.UserData.Data.files,'Tag','listdisplayer');
listdisplayer.Layout.Row = [1];
listdisplayer.Layout.Column = [4 10]; 

axdisplayer = uiaxes(gridfigdisplayer,'Tag','axesdisplayer');
axdisplayer.Layout.Row = [2 10];
axdisplayer.Layout.Column = [1 8];

bglabeldisplayer = uilabel(gridfigdisplayer,'Text','Image selection','HorizontalAlignment','center','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
bglabeldisplayer.Layout.Row = [2];
bglabeldisplayer.Layout.Column = [9 10];

bgdisplayer = uilistbox(gridfigdisplayer,"Items",["Raw coherence","Cropped coherence","Filtered coherence","Raw Binary image","Corrected Binary image"],'Tag','bgdisplayer');
bgdisplayer.Layout.Row = [3 4];
bgdisplayer.Layout.Column = [9 10];

labeloutlinesdisplayer = uilabel(gridfigdisplayer,'Text','Display the outlines','HorizontalAlignment','center','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
labeloutlinesdisplayer.Layout.Row = [8];
labeloutlinesdisplayer.Layout.Column = [9 10];

listoutlinesdisplayer = uidropdown(gridfigdisplayer,"Items",["None","Pixel centres","Pixel edges"],'Tag','listoutlinesdisplayer','Value','None');
listoutlinesdisplayer.Layout.Row = [9];
listoutlinesdisplayer.Layout.Column = [9 10];

figdisplayer.Visible = 'on'; 

hdl = gcf; 
figmain.UserData.Displayer = hdl; 

listdisplayer.ValueChangedFcn = @(src,evt,arg1,arg2) updatedisplayer([],[],figmain);
bgdisplayer.ValueChangedFcn = @(src,evt,arg1,arg2) updatedisplayer([],[],figmain);
listoutlinesdisplayer.ValueChangedFcn = @(src,evt,arg1,arg2) updatedisplayer([],[],figmain);

updatedisplayer([],[],figmain)

end 
