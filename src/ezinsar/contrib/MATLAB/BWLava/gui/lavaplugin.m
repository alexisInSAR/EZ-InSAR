function hdl = lavaplugin(figmain)
%   lavaplugin(figmain)
%       [figmain]           : main figure of BWLava application
%
%       Script to create the Lava Detector of BWLava application
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

figlavaplugin = uifigure('Position',[68 242 750 284],'Name','BWLava Application: Lava Detector','HandleVisibility','on','Visible','off');
gridfiglavaplugin = uigridlayout(figlavaplugin,[13 18]);

maskinglabellavaplugin = uilabel(gridfiglavaplugin,'Text','Masking','HorizontalAlignment','center','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
maskinglabellavaplugin.Layout.Row = [1 2];
maskinglabellavaplugin.Layout.Column = [1 6];

maskinglistlavaplugin = uilistbox(gridfiglavaplugin,'Tag','maskinglistlavaplugin');
maskinglistlavaplugin.Layout.Row = [3 5];
maskinglistlavaplugin.Layout.Column = [1 6];

maskingbtvectorfilelavaplugin = uibutton(gridfiglavaplugin,'Text','Import a vector file','WordWrap','on','Tag','maskingbtvectorfilelavaplugin','Visible','on');
maskingbtvectorfilelavaplugin.Layout.Row = [6 7];
maskingbtvectorfilelavaplugin.Layout.Column = [1 3];
maskingbtvectorfilelavaplugin.ButtonPushedFcn = @(src,evt,arg1,arg2) updatelavadetector(src,evt,figmain,'vectormask');

maskingbtmatlabfilelavaplugin = uibutton(gridfiglavaplugin,'Text','Import a MATLAB file','WordWrap','on','Tag','maskingbtmatlabfilelavaplugin','Visible','off');
maskingbtmatlabfilelavaplugin.Layout.Row = [6 7];
maskingbtmatlabfilelavaplugin.Layout.Column = [4 6];

maskingbtdeletelavaplugin = uibutton(gridfiglavaplugin,'Text','Delete a mask zone','WordWrap','on','Tag','maskingbtdeletelavaplugin');
maskingbtdeletelavaplugin.Layout.Row = [8 9];
maskingbtdeletelavaplugin.Layout.Column = [1 6];
maskingbtdeletelavaplugin.ButtonPushedFcn = @(src,evt,arg1,arg2) updatelavadetector(src,evt,figmain,'deletemask');

maskingbtnewlavaplugin = uibutton(gridfiglavaplugin,'Text','Trace a new mask zone','WordWrap','on','Tag','maskingbtnewlavaplugin');
maskingbtnewlavaplugin.Layout.Row = [10 11];
maskingbtnewlavaplugin.Layout.Column = [1 6];
maskingbtnewlavaplugin.ButtonPushedFcn = @(src,evt,arg1,arg2) updatelavadetector(src,evt,figmain,'tracemask');

lavalabellavaplugin = uilabel(gridfiglavaplugin,'Text','Lava-flow part(s)','HorizontalAlignment','center','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
lavalabellavaplugin.Layout.Row = [1 2];
lavalabellavaplugin.Layout.Column = [7 12];

lavalistlavaplugin = uilistbox(gridfiglavaplugin,'Tag','lavalistlavaplugin');
lavalistlavaplugin.Layout.Row = [3 5];
lavalistlavaplugin.Layout.Column = [7 12];

lavabtvectorfilelavaplugin = uibutton(gridfiglavaplugin,'Text','Import a vector file','WordWrap','on','Tag','lavabtvectorfilelavaplugin','Visible','off');
lavabtvectorfilelavaplugin.Layout.Row = [6 7];
lavabtvectorfilelavaplugin.Layout.Column = [7 12];

lavabtdeletelavaplugin = uibutton(gridfiglavaplugin,'Text','Delete a lava-part zone','WordWrap','on','Tag','lavabtdeletelavaplugin');
lavabtdeletelavaplugin.Layout.Row = [8 9];
lavabtdeletelavaplugin.Layout.Column = [7 12];
lavabtdeletelavaplugin.ButtonPushedFcn = @(src,evt,arg1,arg2) updatelavadetector(src,evt,figmain,'deletelavapart');

lavabtnewlavaplugin = uibutton(gridfiglavaplugin,'Text','Trace a new lava-part zone','WordWrap','on','Tag','lavabtnewlavaplugin');
lavabtnewlavaplugin.Layout.Row = [10 11];
lavabtnewlavaplugin.Layout.Column = [7 12];
lavabtnewlavaplugin.ButtonPushedFcn = @(src,evt,arg1,arg2) updatelavadetector(src,evt,figmain,'tracelavepart');

pplabellavaplugin = uilabel(gridfiglavaplugin,'Text','Post-processing (optional)','HorizontalAlignment','center','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
pplabellavaplugin.Layout.Row = [1 2];
pplabellavaplugin.Layout.Column = [13 18];

ppswitchlavaplugin = uiswitch(gridfiglavaplugin,"slider");
ppswitchlavaplugin.Items = {'Enabled','Disabled'};
ppswitchlavaplugin.Tag = 'ppswitchlavaplugin';
ppswitchlavaplugin.FontWeight = 'bold';
ppswitchlavaplugin.Layout.Row = [4 6];
ppswitchlavaplugin.Layout.Column = [13 18];

ppkipukalabellavaplugin = uilabel(gridfiglavaplugin,'Text','False-kipuka threshold (pixel):','HorizontalAlignment','left','VerticalAlignment','center','FontSize',12.5,'FontWeight','normal','WordWrap','on');
ppkipukalabellavaplugin.Layout.Row = [7 8];
ppkipukalabellavaplugin.Layout.Column = [13 16];

ppkipukathreslavaplugin = uieditfield(gridfiglavaplugin,"numeric","Limits",[0 inf],'Value',20,'Tag','ppkipukathreslavaplugin');
ppkipukathreslavaplugin.Layout.Row = [7 8];
ppkipukathreslavaplugin.Layout.Column = [17 18];

pperodlabellavaplugin = uilabel(gridfiglavaplugin,'Text','Cleaning power (pixel):','HorizontalAlignment','left','VerticalAlignment','center','FontSize',12.5,'FontWeight','normal','WordWrap','on');
pperodlabellavaplugin.Layout.Row = [9 10];
pperodlabellavaplugin.Layout.Column = [13 16];

pperodthreslavaplugin = uieditfield(gridfiglavaplugin,"numeric","Limits",[0 50],'Value',3,'Tag','pperodthreslavaplugin');
pperodthreslavaplugin.Layout.Row = [9 10];
pperodthreslavaplugin.Layout.Column = [17 18];

btrunlavaplugin = uibutton(gridfiglavaplugin,'Text','Run the detection','WordWrap','on','FontWeight','bold','Tag','btrunlavaplugin');
btrunlavaplugin.Layout.Row = [12 13];
btrunlavaplugin.Layout.Column = [1 18];
btrunlavaplugin.ButtonPushedFcn = @(src,evt,arg1,arg2) updatelavadetector(src,evt,figmain,'runcomputation');

figlavaplugin.Visible = 'on';

hdl = gcf;
figmain.UserData.LavaDetector = hdl;

end
