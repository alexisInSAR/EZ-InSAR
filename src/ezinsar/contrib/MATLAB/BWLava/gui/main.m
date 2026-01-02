function hdl = main(appmode)
%   main
%
%       Script to create the main menu of BWLava application
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

%% Create the main uifigure
figmain = uifigure('Position',[51 658 566 311],'Name','BWLava Application: Main Menu','HandleVisibility','on','Visible','off');
gridfigmain = uigridlayout(figmain,[28 15]);

%% Define the user variables
figmain.UserData.Data = []; 
figmain.UserData.Displayer = NaN; 
figmain.UserData.LavaDetector = NaN; 
figmain.UserData.Save = NaN; 
figmain.UserData.AppMode = appmode; 
figmain.UserData.CoordinatesInfo = {[],[]}; 
figmain.UserData.partlava = struct('x',[],'y',[],'nl1',[],'nl2',[],'nc1',[],'nc2',[]);
figmain.UserData.partmask = struct('x',[],'y',[],'nl1',[],'nl2',[],'nc1',[],'nc2',[]);

%% Closing function 
figmain.DeleteFcn = @(src,evt,arg1,arg2) closingfunction(src,evt,figmain);

%% Logos 
[folder,name] = fileparts(mfilename('fullpath'));

logoucd = uiimage(gridfigmain,'ImageSource',[folder,'/../private/UCDlogo.png']);
logoucd.Layout.Row = [1 3];
logoucd.Layout.Column = [1 2];

logoicrag = uiimage(gridfigmain,'ImageSource',[folder,'/../private/icrag-logo.png']);
logoicrag.Layout.Row = [1 3];
logoicrag.Layout.Column = [3 4];

logolmv = uiimage(gridfigmain,'ImageSource',[folder,'/../private/cropped-LOGO-LMV.png']);
logolmv.Layout.Row = [1 3];
logolmv.Layout.Column = [11 13];

logouca = uiimage(gridfigmain,'ImageSource',[folder,'/../private/UCA__Logo_head.png']);
logouca.Layout.Row = [1 3];
logouca.Layout.Column = [14 15];

%% Main title
maintitle = uilabel(gridfigmain,'Text','BWLava Application','HorizontalAlignment','center','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
maintitle.Layout.Row = [1 3];
maintitle.Layout.Column = [6 10];

%% Opening button 
btopen = uibutton(gridfigmain,'Text','Open the coherence image(s)'); 
btopen.ButtonPushedFcn = @(src,evt,arg1,arg2) openstack(src,evt,figmain);
btopen.Layout.Row = [4 6];
btopen.Layout.Column = [1 15];
btopen.Tooltip = 'Click to select the coherence image(s)';

%% For the image tables
tabledata = uitable(gridfigmain,"Data",table,'Tag','TableData');
tabledata.Layout.Row = [7 17];
tabledata.Layout.Column = [1 15];
tabledata.Tooltip = 'Click to modify the relevant values/parameters';
tabledata.ColumnEditable = [false false false true true];
tabledata.CellEditCallback = @(src,evt,arg1,arg2) rerunstepfromtable(src,evt,figmain);

%% Displayer button 
btdisplayer = uibutton(gridfigmain,'Text','Open the BWLava Displayer','Enable','off','Tag','btdisplayer'); 
btdisplayer.ButtonPushedFcn = @(src,evt,arg1,arg2) opendisplayer(src,evt,figmain);
btdisplayer.Layout.Row = [18 20];
btdisplayer.Layout.Column = [1 15];
btdisplayer.Tooltip = 'Open the Displayer';

%% Processing buttons
gridprocessingbt = uigridlayout(gridfigmain,[2 4]);
gridprocessingbt.Layout.Row = [21 28];
gridprocessingbt.Layout.Column = [1 15];

% Step 1: ROI selection
btroi = uibutton(gridprocessingbt,'Text',sprintf('Step 1:\nSelect the Region of Interest'),'WordWrap','on','Enable','off','Tag','btroi'); 
btroi.ButtonPushedFcn = @(src,evt,arg1,arg2) processstep(src,evt,figmain,'ROIselection');
btroi.Layout.Row = [1 2];
btroi.Layout.Column = [1];
btroi.Tooltip = 'Click to select the region of interest';

% Step 2: Segmentation
btseg = uibutton(gridprocessingbt,'Text',sprintf('Step 2:\nSegmentation'),'WordWrap','on','Enable','off','Tag','btseg');
btseg.ButtonPushedFcn = @(src,evt,arg1,arg2) processstep(src,evt,figmain,'segmentation');
btseg.Layout.Row = [1 2];
btseg.Layout.Column = [2];
btseg.Tooltip = 'Click to process the segmentation of coherence image(s)';

% Step 3: Lava flow detection
btld = uibutton(gridprocessingbt,'Text',sprintf('Step 3\nLava-flow detection'),'WordWrap','on','Enable','off','Tag','btld');
btld.ButtonPushedFcn = @(src,evt,arg1,arg2) updatelavadetector(src,evt,figmain,'init'); 
btld.Layout.Row = [1 2];
btld.Layout.Column = [3];
btld.Tooltip = 'Click to detect the lava flow';

% Step 4: Saving 
btsave = uibutton(gridprocessingbt,'Text',sprintf('Step 4\nSave the results'),'WordWrap','on','Enable','off','Tag','btsave');
btsave.ButtonPushedFcn = @(src,evt,arg1,arg2) updatesave(src,evt,figmain,'init');
btsave.Layout.Row = [1 2];
btsave.Layout.Column = [4];
btsave.Tooltip = 'Click to save the results';

%% Menu bar
about_help_menubar = uimenu(figmain,'Text','About');
% about_help_menubar.MenuSelectedFcn = @(src,evt,arg1,arg2) aboutfunction(src,evt,figmain);

%% Final modifications
figmain.Visible = 'on'; 

% Some information on the terminal
fprintf(1,'---------------------------------------------------------\n');
fprintf(1,'---------------------------------------------------------\n');
fprintf(1,'Welcome in BWLava Application:\n');
fprintf(1,'---------------------------------------------------------\n');
fprintf(1,'---------------------------------------------------------\n');
fprintf(1,'Version 2.0.1 Beta\n');

%% Extraction of handle
hdl = gcf; 

end 

function closingfunction(src,evt,figmain)
    if ishandle(figmain.UserData.Displayer)
        close(figmain.UserData.Displayer);
    end 
    if ishandle(figmain.UserData.LavaDetector)
        close(figmain.UserData.LavaDetector);
    end 
    if ishandle(figmain.UserData.Save)
        close(figmain.UserData.Save);
    end 

    if figmain.UserData.AppMode
        quit;
    end 
    
end
%closingfunction
%aboutfunction
