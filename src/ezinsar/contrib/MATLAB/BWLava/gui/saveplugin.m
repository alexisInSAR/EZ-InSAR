function hdl = saveplugin(figmain)
%   saveplugin(figmain)
%       [figmain]           : main figure of BWLava application
%
%       Script to create the saving plugin of BWLava application
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

figsaveplugin = uifigure('Position',[978 174 563 248],'Name','BWLava Application: Save','HandleVisibility','on','Visible','off');
gridfigsaveplugin = uigridlayout(figsaveplugin,[4 4]);

masklabelsaveplugin = uilabel(gridfigsaveplugin,'Text','Mask export','HorizontalAlignment','center','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
masklabelsaveplugin.Layout.Row = [1];
masklabelsaveplugin.Layout.Column = [1 2];

maskgeotifsaveplugin = uibutton(gridfigsaveplugin,'Text','Export the mask into a .tif file','WordWrap','on','Tag','maskgeotifsaveplugin','Visible','on','FontWeight','bold');
maskgeotifsaveplugin.Layout.Row = [4];
maskgeotifsaveplugin.Layout.Column = [1 2];
maskgeotifsaveplugin.ButtonPushedFcn = @(src,evt,arg1,arg2) updatesave(src,evt,figmain,'geotiffmask');

outlinelabelsaveplugin = uilabel(gridfigsaveplugin,'Text','Outline export','HorizontalAlignment','center','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
outlinelabelsaveplugin.Layout.Row = [1];
outlinelabelsaveplugin.Layout.Column = [3 4];

labeloutlineselectsaveplugin = uilabel(gridfigsaveplugin,'Text','Mode:','HorizontalAlignment','left','VerticalAlignment','center','FontSize',12.5,'FontWeight','bold');
labeloutlineselectsaveplugin.Layout.Row = [2];
labeloutlineselectsaveplugin.Layout.Column = [3];

outlineselectsaveplugin = uidropdown(gridfigsaveplugin,"Items",["Pixel centres","Pixel edges"],'Tag','outlineselectsaveplugin','Value','Pixel edges');
outlineselectsaveplugin.Layout.Row = [2];
outlineselectsaveplugin.Layout.Column = [4];

labeloutlineformatsaveplugin = uilabel(gridfigsaveplugin,'Text','Format:','HorizontalAlignment','left','VerticalAlignment','center','FontSize',12.5,'FontWeight','bold');
labeloutlineformatsaveplugin.Layout.Row = [3];
labeloutlineformatsaveplugin.Layout.Column = [3];

outlineformatsaveplugin = uidropdown(gridfigsaveplugin,"Items",[".kml file",".shp file"],'Tag','outlineformatsaveplugin','Value','.shp file');
outlineformatsaveplugin.Layout.Row = [3];
outlineformatsaveplugin.Layout.Column = [4];

outlinerunsaveplugin = uibutton(gridfigsaveplugin,'Text','Export the outlines','WordWrap','on','Tag','outlinerunsaveplugin','Visible','on','FontWeight','bold');
outlinerunsaveplugin.Layout.Row = [4];
outlinerunsaveplugin.Layout.Column = [3 4];
outlinerunsaveplugin.ButtonPushedFcn = @(src,evt,arg1,arg2) updatesave(src,evt,figmain,'outlines');

figsaveplugin.Visible = 'on';

hdl = gcf;
figmain.UserData.Save = hdl;

end
