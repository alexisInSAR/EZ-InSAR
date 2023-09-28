function hdl = GUIMIESAR(miesar_para)
%   GUIMIESAR(miesar_para)
%
%       Script to create the GUI of EZ-InSAR
%   
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also EZ_InSAR
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.1.0 Beta
%   Date: 23/02/2022
%
%   -------------------------------------------------------
%   Modified:
%           - Xiaowen Wang, UCD, 10/03/2022: bug fix
%           - Alexis Hrysiewicz, UCD / iCRAG, 07/07/2022: StripMap
%           implementation
%           - Alexis Hrysiewicz, UCD / iCRAG, 18/07/2022: check the
%           versions of tools
%           - Alexis Hrysiewicz, UCD / iCRAG, 25/04/2023: modification of
%           text information
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)
%           2.0.0 Beta: Initial (unreleased)
%           2.0.1 Beta: Initial (unreleased)
%           2.0.2 Beta: Initial (unreleased)
%           2.0.3 Beta: Initial (unreleased)
%           2.1.0 Beta: Initial (unreleased)

%% Creation of GUI for MIESAR
% To keep the gcf command, we need to create the figure using matlab
% scripts... 

%% Some information
figopen = uifigure('Position',[548 376 565 206],'Name','EZ-InSAR Application');
pg_figopen = uiprogressdlg(figopen,'Title','Loading of EZ-InSAR Application','Message','Opening the application');

pg_figopen.Value = .1; 
pg_figopen.Message = 'Open the core of MIESAR';
pause(0.25); 

%% Main uifigure
figmiesar = uifigure('Position',[19 15 1620 900],'Name','EZ-InSAR Application','HandleVisibility','on','Visible','off');
gridfigmiesar = uigridlayout(figmiesar,[28 15]);
figmiesar.UserData = miesar_para; 

figmiesar.DeleteFcn = @(src,evt,arg1,arg2) EZ_InSAR(src,evt,'close',figmiesar.UserData);

%% Logos 
% UCD 
logoucd = uiimage(gridfigmiesar,'ImageSource','private/UCDlogo.png');
logoucd.Layout.Row = [1 3];
logoucd.Layout.Column = [1 2];
logoucd.ImageClickedFcn = @(src,event) linklogo(src,'ucd');
logoucd.Tooltip = 'Go to www.ucd.ie/earthsciences';

% iCRAG 
logoicrag = uiimage(gridfigmiesar,'ImageSource','private/icrag-logo.png');
logoicrag.Layout.Row = [1 3];
logoicrag.Layout.Column = [3 4];
logoicrag.ImageClickedFcn = @(src,event) linklogo(src,'icrag');
logoicrag.Tooltip = 'Go to www.icrag-centre.org';

% Interreg
logointerreg = uiimage(gridfigmiesar,'ImageSource','private/atlanticarealogo.png');
logointerreg.Layout.Row = [1 3];
logointerreg.Layout.Column = [11 13];
logointerreg.ImageClickedFcn = @(src,event) linklogo(src,'interreg');
logointerreg.Tooltip = 'Go to www.atlanticarea.eu';

% AGEO
logoageo = uiimage(gridfigmiesar,'ImageSource','private/AGEO-transparent.png');
logoageo.Layout.Row = [1 3];
logoageo.Layout.Column = [14 15];
logoageo.ImageClickedFcn = @(src,event) linklogo(src,'ageo');
logoageo.Tooltip = 'Go to ageoatlantic.eu';

% Quick function to implement the website
    function linklogo(src,event)
        switch event
            case 'ucd'
                url = 'https://www.ucd.ie/earthsciences/';
            case 'icrag'
                url = 'https://www.icrag-centre.org/';
            case 'interreg'
                url = 'https://www.atlanticarea.eu/';
            case 'ageo'
                url = 'https://ageoatlantic.eu/';
        end
        web(url);
    end

%% Main title
maintitle = uilabel(gridfigmiesar,'Text','EZ-InSAR','HorizontalAlignment','center','VerticalAlignment','center','FontSize',50,'FontWeight','bold');
maintitle.Layout.Row = [1 3];
maintitle.Layout.Column = [6 10];

logoezinsar = uiimage(gridfigmiesar,'ImageSource','private/EZ_InSAR_logo.gif');
logoezinsar.Layout.Row = [1 3];
logoezinsar.Layout.Column = [6];

%% Path panel 
pathpanel = uipanel(gridfigmiesar,'Title','EZ-InSAR Paths','FontSize',20,'FontWeight','bold'); 
pathpanel.Layout.Row = [4 6];
pathpanel.Layout.Column = [1 15];

gridpathpanel = uigridlayout(pathpanel,[1 3]);

% For Work directory
btworkdirectory = uibutton(gridpathpanel,'Text','Set work directory','Tag','mainbutWKpath','Backgroundcolor','red'); 
btworkdirectory.ButtonPushedFcn = @(src,evt,arg1,arg2) EZ_InSAR(src,evt,'defineWK',figmiesar.UserData);
btworkdirectory.Layout.Row = [1];
btworkdirectory.Layout.Column = [1];
btworkdirectory.Tooltip = 'Click to select the work directory';

%% SLC panel
pg_figopen.Value = .2; 
pg_figopen.Message = 'Open the tools for SAR data';
pause(0.25); 

slcpanel = uipanel(gridfigmiesar,'Title','Preparation of SAR data','FontSize',20,'FontWeight','bold','Tag','mainuipanelprepdata'); 
slcpanel.Layout.Row = [7 25];
slcpanel.Layout.Column = [1 5];
slcpanel.Visible = 'off'; 

gridslcpanel = uigridlayout(slcpanel,[10 2]);

%Button SLC management
btslcmanage = uibutton(gridslcpanel,'Text','Manage data directory','Tag','mainbutmanageSLC'); 
btslcmanage.ButtonPushedFcn = @(src,evt,arg1,arg2) EZ_InSAR(src,evt,'SLCmanager',figmiesar.UserData);
btslcmanage.Layout.Row = [1];
btslcmanage.Layout.Column = [1 2];
btslcmanage.Tooltip = 'Click to select the SLCs, orbits abd Aux. directories.';

%Button area
btarea = uibutton(gridslcpanel,'Text','Selection of study area','Tag','mainbutselectionarea'); 
btarea.ButtonPushedFcn = @(src,evt,arg1,arg2) EZ_InSAR(src,evt,'Selectionzone',figmiesar.UserData);
btarea.Layout.Row = [2];
btarea.Layout.Column = [1 2];
btarea.Tooltip = 'Click to select the study area.';

%SLC parameter panel
slcparameterpanel = uipanel(gridslcpanel,'Title','Parameters of SLCs','FontSize',15,'FontWeight','bold'); 
slcparameterpanel.Layout.Row = [3 7];
slcparameterpanel.Layout.Column = [1 2];

%SLC parameter grid
gridslcparameterpanel = uigridlayout(slcparameterpanel,[5 5]);

%Labels
mode_labelslcparameter = uilabel(gridslcparameterpanel,'Text','Mode:','HorizontalAlignment','left','VerticalAlignment','center','FontSize',15,'FontWeight','bold'); 
mode_labelslcparameter.Layout.Row = 1;
mode_labelslcparameter.Layout.Column = 1;

track_labelslcparameter = uilabel(gridslcparameterpanel,'Text','Path:','HorizontalAlignment','left','VerticalAlignment','center','FontSize',15,'FontWeight','bold'); 
track_labelslcparameter.Layout.Row = 2;
track_labelslcparameter.Layout.Column = 1;

pass_labelslcparameter = uilabel(gridslcparameterpanel,'Text','Pass:','HorizontalAlignment','left','VerticalAlignment','center','FontSize',15,'FontWeight','bold'); 
pass_labelslcparameter.Layout.Row = 3;
pass_labelslcparameter.Layout.Column = 1;

date1_labelslcparameter = uilabel(gridslcparameterpanel,'Text','Date 1:','HorizontalAlignment','left','VerticalAlignment','center','FontSize',15,'FontWeight','bold'); 
date1_labelslcparameter.Layout.Row = 4;
date1_labelslcparameter.Layout.Column = 1;

date2_labelslcparameter = uilabel(gridslcparameterpanel,'Text','Date 2:','HorizontalAlignment','left','VerticalAlignment','center','FontSize',15,'FontWeight','bold'); 
date2_labelslcparameter.Layout.Row = 5;
date2_labelslcparameter.Layout.Column = 1;

%Controls of parameters
mode_controlslcparameter = uidropdown(gridslcparameterpanel,'Tag','mainpopmode','Enable','on'); 
mode_controlslcparameter.ValueChangedFcn = @(src,evt,arg1,arg2) manageparamaterSLC(src,evt,'save',figmiesar.UserData);
mode_controlslcparameter.Layout.Row = [1];
mode_controlslcparameter.Layout.Column = [2 3];
mode_controlslcparameter.Items = {'S1_IW','S1_SM','TSX_SM','TSX_SPT','PAZ_SM','PAZ_SPT','CSK_SM','CSK_SPT'};
mode_controlslcparameter.Value = {'S1_IW'};
mode_controlslcparameter.Tooltip = 'Click to select the mode of acquisition of data.';

track_controlslcparameter = uieditfield(gridslcparameterpanel,'text','Tag','maintexttrack'); 
track_controlslcparameter.ValueChangedFcn = @(src,evt,arg1,arg2) manageparamaterSLC(src,evt,'save',figmiesar.UserData);
track_controlslcparameter.Layout.Row = [2];
track_controlslcparameter.Layout.Column = [2 3];
track_controlslcparameter.Value = 'Edit Text';
track_controlslcparameter.Tooltip = 'Edit to define the path <XXX>.';

pass_controlslcparameter = uidropdown(gridslcparameterpanel,'Tag','mainpoppass'); 
pass_controlslcparameter.ValueChangedFcn = @(src,evt,arg1,arg2) manageparamaterSLC(src,evt,'save',figmiesar.UserData);
pass_controlslcparameter.Layout.Row = [3];
pass_controlslcparameter.Layout.Column = [2 3];
pass_controlslcparameter.Items = {'Ascending','Descending'};
pass_controlslcparameter.Value = {'Ascending'};
pass_controlslcparameter.Tooltip = 'Click to select the pass of acquisitions.';

date1_controlslcparameter = uidatepicker(gridslcparameterpanel,'Tag','maintextdate1'); 
date1_controlslcparameter.ValueChangedFcn = @(src,evt,arg1,arg2) manageparamaterSLC(src,evt,'save',figmiesar.UserData);
date1_controlslcparameter.Layout.Row = [4];
date1_controlslcparameter.Layout.Column = [2 5];
date1_controlslcparameter.DisplayFormat = 'yyyy-MM-dd';
date1_controlslcparameter.Tooltip = 'Edit to define the first date <YYYY-MM-DD>.';

date2_controlslcparameter = uidatepicker(gridslcparameterpanel,'Tag','maintextdate2'); 
date2_controlslcparameter.ValueChangedFcn = @(src,evt,arg1,arg2) manageparamaterSLC(src,evt,'save',figmiesar.UserData);
date2_controlslcparameter.Layout.Row = [5];
date2_controlslcparameter.Layout.Column = [2 5];
date2_controlslcparameter.DisplayFormat = 'yyyy-MM-dd';
date2_controlslcparameter.Tooltip = 'Edit to define the last date <YYYY-MM-DD>.';

satslcparameterpanel = uipanel(gridslcparameterpanel,'Title','Satellites (For S1)','FontSize',15,'FontWeight','bold'); 
satslcparameterpanel.Layout.Row = [1 3];
satslcparameterpanel.Layout.Column = [4 5];
satslcparameterpanel.Tooltip = 'Click to select the satellites.';

%SLC parameter grid
gridsatslcparameterpanel = uigridlayout(satslcparameterpanel,[2 1]);
SAsatslcparameterpanel = uicheckbox(gridsatslcparameterpanel, 'Text','Sentinel-1 A','Value', 1,'Enable','on','Tag','mainboxS1A');
SAsatslcparameterpanel.Layout.Row = [1];
SAsatslcparameterpanel.Layout.Column = [1 2];
SAsatslcparameterpanel.ValueChangedFcn = @(src,evt,arg1,arg2) manageparamaterSLC(src,evt,'save',figmiesar.UserData);
SBsatslcparameterpanel = uicheckbox(gridsatslcparameterpanel, 'Text','Sentinel-1 B','Value', 1,'Enable','on','Tag','mainboxS1B');
SBsatslcparameterpanel.Layout.Row = [2];
SBsatslcparameterpanel.Layout.Column = [1 2];
SBsatslcparameterpanel.ValueChangedFcn = @(src,evt,arg1,arg2) manageparamaterSLC(src,evt,'save',figmiesar.UserData);

%Button check
btslccheck = uibutton(gridslcpanel,'Text','Check the SLCs','Tag','buttoncheckslc'); 
btslccheck.ButtonPushedFcn = @(src,evt,arg1,arg2) manageSLC(src,evt,'checking',figmiesar.UserData);
btslccheck.Layout.Row = [8];
btslccheck.Layout.Column = [1];
btslccheck.Tooltip = 'Click to check the available SLCs';

%Button list
btslclist = uibutton(gridslcpanel,'Text','Show the SLC list','Tag','dede'); 
btslclist.ButtonPushedFcn = @(src,evt,arg1,arg2) manageSLC(src,evt,'opening',figmiesar.UserData);
btslclist.Layout.Row = [8];
btslclist.Layout.Column = [2];
btslclist.Tooltip = 'Click to open the SLC list.';

%Button SLCext
btslcext = uibutton(gridslcpanel,'Text','Check the SLC extension','Tag','dede'); 
btslcext.ButtonPushedFcn = @(src,evt,arg1,arg2) manageSLC(src,evt,'extension',figmiesar.UserData);
btslcext.Layout.Row = [9];
btslcext.Layout.Column = [1 2];
btslcext.Tooltip = 'Click to check the SLC extension';

%Button download
btslcdown = uibutton(gridslcpanel,'Text','Download the Sentinel-1 SLCs','Tag','buttondownloaderS1'); 
btslcdown.ButtonPushedFcn = @(src,evt,arg1,arg2) manageSLC(src,evt,'alldownloading',figmiesar.UserData);
btslcdown.Layout.Row = [10];
btslcdown.Layout.Column = [1 2];
btslcdown.Tooltip = 'Click to open the SLC downloader.';

%% ISCE panel
pg_figopen.Value = .4; 
pg_figopen.Message = 'Open the kernel for ISCE processor';
pause(0.25); 

iscepanel = uipanel(gridfigmiesar,'Title','ISCE Processing','FontSize',20,'FontWeight','bold','Tag','mainuipanelisceprocess'); 
iscepanel.Layout.Row = [7 25];
iscepanel.Layout.Column = [6 10];
iscepanel.Visible = 'off'; 

gridiscepanel = uigridlayout(iscepanel,[10 2]);

%Button check IPF
bt_checkipf_isceprocessing = uibutton(gridiscepanel,'Text','Check the IPF versions','Tag','buttoncheckIPF'); 
bt_checkipf_isceprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) isceprocessing(src,evt,'IPFchecking',figmiesar.UserData);
bt_checkipf_isceprocessing.Layout.Row = [1];
bt_checkipf_isceprocessing.Layout.Column = [1 2];
bt_checkipf_isceprocessing.Tooltip = 'Click to check the IPF versions of SLCs';

%Button selection DEM
bt_selectDEM_isceprocessing = uibutton(gridiscepanel,'Text','Select the DEM','Tag','dede'); 
bt_selectDEM_isceprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) isceprocessing(src,evt,'selectionDEM',figmiesar.UserData);
bt_selectDEM_isceprocessing.Layout.Row = [2];
bt_selectDEM_isceprocessing.Layout.Column = [1];
bt_selectDEM_isceprocessing.Tooltip = 'Click to select or download a DEM.';

%Button visualisation DEM
bt_visualiseDEM_isceprocessing = uibutton(gridiscepanel,'Text','Visualize the DEM','Tag','dede'); 
bt_visualiseDEM_isceprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) isceprocessing(src,evt,'checkingDEM',figmiesar.UserData);
bt_visualiseDEM_isceprocessing.Layout.Row = [2];
bt_visualiseDEM_isceprocessing.Layout.Column = [2];
bt_visualiseDEM_isceprocessing.Tooltip = 'Click to visualize the DEM.';

%Group mode stack
label_stackmode_isceprocessing = uilabel(gridiscepanel,'Text','Selection of the processing:','HorizontalAlignment','left','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
label_stackmode_isceprocessing.Layout.Row = 3;
label_stackmode_isceprocessing.Layout.Column = [1 2];
label_stackmode_isceprocessing.Tooltip = [sprintf('Help for ISCE stack:\n'),...
    sprintf('\n------------------------\n'),...
    sprintf('\n'),...
    sprintf('The box allow to select the type of stack that you want to compute:\n'),...
    sprintf('\t- The SLC stack is a stack of correlated SLC on a single reference. StaMPS needs this stack type.\n'), ...
    sprintf('\t- The IFG stack is a stack of unwrapped interferograms on a (super) single reference. MintPY needs this stack type.\n'),...
    sprintf('\n------------------------\n'),...
    sprintf('\nfor other information, please see the ISCE manual.')];

mode_stackmode_isceprocessing = uilistbox(gridiscepanel,'Tag','radiobuttonISCEstack');
mode_stackmode_isceprocessing.Items = {'SLC stack','Interferogram stack'};
mode_stackmode_isceprocessing.Layout.Row = 4;
mode_stackmode_isceprocessing.Layout.Column = [1 2];
mode_stackmode_isceprocessing.ValueChangedFcn = @(src,evt,arg1,arg2) selectionofstack(src,evt,'modestack',figmiesar.UserData); 

%Button checking single reference
bt_checkSSM_isceprocessing = uibutton(gridiscepanel,'Text','Select the best reference date','Tag','dede','Enable','on'); 
bt_checkSSM_isceprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) isceprocessing(src,evt,'open_coarse_network_check',figmiesar.UserData);
bt_checkSSM_isceprocessing.Layout.Row = [5];
bt_checkSSM_isceprocessing.Layout.Column = [1 2];
bt_checkSSM_isceprocessing.Tooltip = 'Click to find the best single reference using a coarse network of interferograms.';

%Button pre run
bt_prerun_isceprocessing = uibutton(gridiscepanel,'Text','Pre-run of ISCE processing','Tag','bt_prerun_isceprocessing');  
bt_prerun_isceprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) isceprocessing(src,evt,'prerunstack',figmiesar.UserData);
bt_prerun_isceprocessing.Layout.Row = [6];
bt_prerun_isceprocessing.Layout.Column = [1 2];
bt_prerun_isceprocessing.Tooltip = 'Click to run the preparation of ISCE stack.';

bt_convert_isceprocessing = uibutton(gridiscepanel,'Text','Convert the stack','Tag','bt_convert_isceprocessing','Enable','off','Visible','off');  
bt_convert_isceprocessing.Layout.Row = [6];
bt_convert_isceprocessing.Layout.Column = [1 2];
bt_convert_isceprocessing.Tooltip = 'Click to convert the ISCE stack.';

%ISCE steps panel
stepsiscepanel = uipanel(gridiscepanel,'Title','ISCE Steps','FontSize',15,'FontWeight','bold','Tag','stepsiscepanel'); 
stepsiscepanel.Layout.Row = [7 9];
stepsiscepanel.Layout.Column = [1 2];

gridstepsiscepanel = uigridlayout(stepsiscepanel,[3 2]);

%List of ISCE steps
list_steps_isceprocessing = uidropdown(gridstepsiscepanel,'Tag','isceprocesspopupmenustep'); 
list_steps_isceprocessing.Layout.Row = [1];
list_steps_isceprocessing.Layout.Column = [1 2];
list_steps_isceprocessing.Items = {'Step 1','Step 2','Step 3','Step 4','Step 5','Step 6','Step 7','Step 8','Step 9','Step 10',};
list_steps_isceprocessing.Value = {'Step 1'};
list_steps_isceprocessing.Tooltip = 'Click to select the step of ISCE processing.';
list_steps_isceprocessing.ValueChangedFcn = @(src,evt,arg1,arg2) isceprocessing(src,evt,'updatepopmenustep',figmiesar.UserData);

%Button step run
bt_steprun_isceprocessing = uibutton(gridstepsiscepanel,'Text','Run the selected step','Tag','bt_steprun_isceprocessing');  
bt_steprun_isceprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) isceprocessing(src,evt,'runselectedstep',figmiesar.UserData); 
bt_steprun_isceprocessing.Layout.Row = [2];
bt_steprun_isceprocessing.Layout.Column = [1];
bt_steprun_isceprocessing.Tooltip = 'Click to run the selected step of ISCE stack.';

%Check parallel
check_parallel_isceprocessing = uicheckbox(gridstepsiscepanel, 'Text','Parallelisation','Value', 0,'Tag','modeiscesteppara','Enable','on');
check_parallel_isceprocessing.Layout.Row = [2];
check_parallel_isceprocessing.Layout.Column = [2];
check_parallel_isceprocessing.Tooltip = 'Click to select the available parallelisation of ISCE steps.';

%Button all steps run
bt_allsteprun_isceprocessing = uibutton(gridstepsiscepanel,'Text','Run all the steps','Tag','TEST1');  
bt_allsteprun_isceprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) isceprocessing(src,evt,'runallsteps',figmiesar.UserData); 
bt_allsteprun_isceprocessing.Layout.Row = [3];
bt_allsteprun_isceprocessing.Layout.Column = [1 2];
bt_allsteprun_isceprocessing.Tooltip = 'Click to run all the step of ISCE stack.';

% %Button geocode ISCE
bt_geo_isceprocessing = uibutton(gridiscepanel,'Text','Geocode the results','Tag','dede','Enable','off');  
bt_geo_isceprocessing.ButtonPushedFcn = @(src,event,action) ISPSlinkmain(src,event,'defineWK');
bt_geo_isceprocessing.Layout.Row = [10];
bt_geo_isceprocessing.Layout.Column = [1];
bt_geo_isceprocessing.Tooltip = 'Click to geocode the available results of ISCE.';

%Button disp IFG ISCE
bt_disifg_isceprocessing = uibutton(gridiscepanel,'Text','Visualize the interferograms','Tag','dede','Enable','on');  
bt_disifg_isceprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) iscedisplayifg(src,evt,[],figmiesar.UserData); 
bt_disifg_isceprocessing.Layout.Row = [10];
bt_disifg_isceprocessing.Layout.Column = [2];
bt_disifg_isceprocessing.Tooltip = 'Click to visualize the interferograms.';

%% Displacement panel
disppanel = uipanel(gridfigmiesar,'Title','InSAR Time Series Analysis','FontSize',20,'FontWeight','bold','Tag','mainuipaneldispprocess'); 
disppanel.Layout.Row = [7 25];
disppanel.Layout.Column = [11 15];
disppanel.Visible = 'off'; 

griddisppanel = uigridlayout(disppanel,[10 2]);

tabdisp = uitabgroup(griddisppanel,'Tag','tab_disp');
tabdisp.Layout.Row = [1 10];
tabdisp.Layout.Column = [1 2];
tabdisp.SelectionChangedFcn = @(src,evt,arg1,arg2) selectionofstack(src,evt,'disp_tab',figmiesar.UserData);

tab_init_disp = uitab(tabdisp,'Title',' ','Tag','tab_init_disp');
tab_stamps_disp = uitab(tabdisp,'Title','StaMPS Processing','Tag','tab_stamps_disp');
tab_mintpy_disp = uitab(tabdisp,'Title','MintPy Processing','Tag','tab_mintpy_disp');

tab_stamps_disp.Tooltip = 'Click to use the StaMPS processor.';
tab_mintpy_disp.Tooltip = 'Click to use the MintPy processor.';

% Fake panel
grid_fakepaneldisp = uigridlayout(tab_init_disp,[10 2]); 
l1_fakepaneldisp = uilabel(grid_fakepaneldisp,'Text','Selection of InSAR Time Series processor:','HorizontalAlignment','left','VerticalAlignment','center','FontSize',20,'FontWeight','bold'); 
l1_fakepaneldisp.Layout.Row = [1];
l1_fakepaneldisp.Layout.Column = [1 2];

s1 = {'-> StaMPS processor:','Please, select the "StaMPS Processing" tab.'}; 
l2_fakepaneldisp = uilabel(grid_fakepaneldisp,'Text',s1,'HorizontalAlignment','left','VerticalAlignment','center','FontSize',20); 
l2_fakepaneldisp.Layout.Row = [2 5];
l2_fakepaneldisp.Layout.Column = [1 2];

s1 = {'-> MintPy processor:','Please, select the "MintPy Processing" tab.'}; 
l2_fakepaneldisp = uilabel(grid_fakepaneldisp,'Text',s1,'HorizontalAlignment','left','VerticalAlignment','center','FontSize',20); 
l2_fakepaneldisp.Layout.Row = [6 9];
l2_fakepaneldisp.Layout.Column = [1 2];

%% For STAMPS 
pg_figopen.Value = .6; 
pg_figopen.Message = 'Open the kernel for StaMPS processor';
pause(0.25); 

grid_stampsprocessing = uigridlayout(tab_stamps_disp,[10 2]); 

%Button cropping stamps
bt_crop_stampsprocessing = uibutton(grid_stampsprocessing,'Text','Crop the SLCs','Tag','bt_crop_stampsprocessing');  
bt_crop_stampsprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) stampsprocessing(src,evt,'cropping',figmiesar.UserData);
bt_crop_stampsprocessing.Layout.Row = [1];
bt_crop_stampsprocessing.Layout.Column = [1 2];
bt_crop_stampsprocessing.Tooltip = 'Click to crop the SLCs for the StaMPS processing (optional).'; 

%Button stack stamps
bt_stack_stampsprocessing = uibutton(grid_stampsprocessing,'Text','Create the StaMPS stack','Tag','dede');  
bt_stack_stampsprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) stampsprocessing(src,evt,'singlemasterstack',figmiesar.UserData);
bt_stack_stampsprocessing.Layout.Row = [2];
bt_stack_stampsprocessing.Layout.Column = [1 2];
bt_stack_stampsprocessing.Tooltip = 'Click to create the correct directories and files for StaMPS.'; 

% Initialisation of PS and SBAS panels (with grids)
panel_PS_stampsprocessing = uipanel(grid_stampsprocessing,'Title','PS approach','FontSize',15,'FontWeight','bold'); 
panel_PS_stampsprocessing.Layout.Row = [3 6];
panel_PS_stampsprocessing.Layout.Column = [1];

panel_SBAS_stampsprocessing = uipanel(grid_stampsprocessing,'Title','Small-baselines approach','FontSize',15,'FontWeight','bold'); 
panel_SBAS_stampsprocessing.Layout.Row = [3 6];
panel_SBAS_stampsprocessing.Layout.Column = [2];

grid_PS_stampsprocessing = uigridlayout(panel_PS_stampsprocessing,[3 1]);
grid_SBAS_stampsprocessing = uigridlayout(panel_SBAS_stampsprocessing,[5 1]);

%Button PS preparation stamps
bt_prePS_stampsprocessing = uibutton(grid_PS_stampsprocessing,'Text','Preparation','Tag','dede');  
bt_prePS_stampsprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) stampsPSprocessing(src,evt,'prep',figmiesar.UserData);
bt_prePS_stampsprocessing.Layout.Row = [1];
bt_prePS_stampsprocessing.Layout.Column = [1];
bt_prePS_stampsprocessing.Tooltip = 'Click to prepare the data for PS processing.'; 

%Button PS parameters stamps
bt_parametersPS_stampsprocessing = uibutton(grid_PS_stampsprocessing,'Text','StaMPS parameters','Tag','dede');  
bt_parametersPS_stampsprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) stampsPSprocessing(src,evt,'parm',figmiesar.UserData);
bt_parametersPS_stampsprocessing.Layout.Row = [2];
bt_parametersPS_stampsprocessing.Layout.Column = [1];
bt_parametersPS_stampsprocessing.Tooltip = 'Click to select the StaMPS parameters.'; 

%Button PS run stamps
bt_runPS_stampsprocessing = uibutton(grid_PS_stampsprocessing,'Text','Run','Tag','dede');  
bt_runPS_stampsprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) stampsPSprocessing(src,evt,'run',figmiesar.UserData);
bt_runPS_stampsprocessing.Layout.Row = [3];
bt_runPS_stampsprocessing.Layout.Column = [1];
bt_runPS_stampsprocessing.Tooltip = 'Click to run the StaMPS PS processing'; 

%Button SBAS network stamps
bt_netSBAS_stampsprocessing = uibutton(grid_SBAS_stampsprocessing,'Text','SBAS network','Tag','dede');  
bt_netSBAS_stampsprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) stampsSBASprocessing(src,evt,'network',figmiesar.UserData);
bt_netSBAS_stampsprocessing.Layout.Row = [1];
bt_netSBAS_stampsprocessing.Layout.Column = [1];
bt_netSBAS_stampsprocessing.Tooltip = 'Click to build the network of interferograms.'; 

%Button SBAS IFG stamps
bt_ifgSBAS_stampsprocessing = uibutton(grid_SBAS_stampsprocessing,'Text','Compute the interferograms','Tag','dede');  
bt_ifgSBAS_stampsprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) stampsSBASprocessing(src,evt,'computeifg',figmiesar.UserData);
bt_ifgSBAS_stampsprocessing.Layout.Row = [2];
bt_ifgSBAS_stampsprocessing.Layout.Column = [1];
bt_ifgSBAS_stampsprocessing.Tooltip = 'Click to compute the interferograms.'; 

%Button SBAS preparation stamps
bt_preSBAS_stampsprocessing = uibutton(grid_SBAS_stampsprocessing,'Text','Preparation','Tag','dede');  
bt_preSBAS_stampsprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) stampsSBASprocessing(src,evt,'prep',figmiesar.UserData);
bt_preSBAS_stampsprocessing.Layout.Row = [3];
bt_preSBAS_stampsprocessing.Layout.Column = [1];
bt_preSBAS_stampsprocessing.Tooltip = 'Click to prepare the data for SBAS processing.'; 

%Button SBAS parameters stamps
bt_parametersSBAS_stampsprocessing = uibutton(grid_SBAS_stampsprocessing,'Text','StaMPS parameters','Tag','dede');  
bt_parametersSBAS_stampsprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) stampsSBASprocessing(src,evt,'parm',figmiesar.UserData);
bt_parametersSBAS_stampsprocessing.Layout.Row = [4];
bt_parametersSBAS_stampsprocessing.Layout.Column = [1];
bt_parametersSBAS_stampsprocessing.Tooltip = 'Click to select the StaMPS parameters.'; 

%Button SBAS run stamps
bt_runSBAS_stampsprocessing = uibutton(grid_SBAS_stampsprocessing,'Text','Run','Tag','dede');  
bt_runSBAS_stampsprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) stampsSBASprocessing(src,evt,'run',figmiesar.UserData);
bt_runSBAS_stampsprocessing.Layout.Row = [5];
bt_runSBAS_stampsprocessing.Layout.Column = [1];
bt_runSBAS_stampsprocessing.Tooltip = 'Click to run the StaMPS SBAS processing'; 

% Panel of merged processing
panel_PSSBAS_stampsprocessing = uipanel(grid_stampsprocessing,'Title','Merged (PS and SBAS) approach','FontSize',15,'FontWeight','bold'); 
panel_PSSBAS_stampsprocessing.Layout.Row = [7 9];
panel_PSSBAS_stampsprocessing.Layout.Column = [1 2];

grid_PSSBAS_stampsprocessing = uigridlayout(panel_PSSBAS_stampsprocessing,[3 1]);

%Button PSSBAS merging stamps
bt_mergingPSSBAS_stampsprocessing = uibutton(grid_PSSBAS_stampsprocessing,'Text','Merge the PS and SBAS points','Tag','dede');  
bt_mergingPSSBAS_stampsprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) stampsMERGEDprocessing(src,evt,'prep',figmiesar.UserData);
bt_mergingPSSBAS_stampsprocessing.Layout.Row = [1];
bt_mergingPSSBAS_stampsprocessing.Layout.Column = [1];
bt_mergingPSSBAS_stampsprocessing.Tooltip = 'Click to merge the results from the PS and SBAS approaches.'; 

%Button PSSBAS parameters stamps
bt_parametersPSSBAS_stampsprocessing = uibutton(grid_PSSBAS_stampsprocessing,'Text','StaMPS parameters','Tag','dede');  
bt_parametersPSSBAS_stampsprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) stampsMERGEDprocessing(src,evt,'parm',figmiesar.UserData);
bt_parametersPSSBAS_stampsprocessing.Layout.Row = [2];
bt_parametersPSSBAS_stampsprocessing.Layout.Column = [1];
bt_parametersPSSBAS_stampsprocessing.Tooltip = 'Click to select the StaMPS parameters.'; 

%Button PSSBAS run stamps
bt_runPSSBAS_stampsprocessing = uibutton(grid_PSSBAS_stampsprocessing,'Text','Run','Tag','dede');  
bt_runPSSBAS_stampsprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) stampsMERGEDprocessing(src,evt,'run',figmiesar.UserData);
bt_runPSSBAS_stampsprocessing.Layout.Row = [3];
bt_runPSSBAS_stampsprocessing.Layout.Column = [1];
bt_runPSSBAS_stampsprocessing.Tooltip = 'Click to run the StaMPS merged processing';

%Button display stamps
bt_display_stampsprocessing = uibutton(grid_stampsprocessing,'Text','Display the results','Tag','dede');  
bt_display_stampsprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) stampsprocessing(src,evt,'display',figmiesar.UserData);
bt_display_stampsprocessing.Layout.Row = [10];
bt_display_stampsprocessing.Layout.Column = [1 2];
bt_display_stampsprocessing.Tooltip = 'Click to display the results from StaMPS';

%% For MintPy
pg_figopen.Value = .8; 
pg_figopen.Message = 'Open the kernel for MintPy processor';
pause(0.25); 

grid_minptpyprocessing = uigridlayout(tab_mintpy_disp,[10 2]); 

%Button initiate mintpy
bt_init_mintpyprocessing = uibutton(grid_minptpyprocessing,'Text','Initiate the MintPy processing','Tag','mintpy_initiate_button');  
bt_init_mintpyprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) mintpy_parameters(src,evt,'pathmintpy',figmiesar.UserData);
bt_init_mintpyprocessing.Layout.Row = [1];
bt_init_mintpyprocessing.Layout.Column = [1 2];
bt_init_mintpyprocessing.Tooltip = 'Click to initiate the MintPy processing.';

%Button check network mintpy
bt_net_mintpyprocessing = uibutton(grid_minptpyprocessing,'Text','Visualize the network of interferograms','Tag','mintpy_ISCE_network_button','Enable','off');   
bt_net_mintpyprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) mintpy_network_plot(src,evt,[],figmiesar.UserData);
bt_net_mintpyprocessing.Layout.Row = [2];
bt_net_mintpyprocessing.Layout.Column = [1 2];
bt_net_mintpyprocessing.Tooltip = 'Click to visualize the network of interferograms.';

%Button parameters mintpy
bt_parameters_mintpyprocessing = uibutton(grid_minptpyprocessing,'Text','MintPy parameters','Tag','mintpy_parameters_button','Enable','off');  
bt_parameters_mintpyprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) mintpy_parameters(src,evt,'GUImintpyparameters',figmiesar.UserData);
bt_parameters_mintpyprocessing.Layout.Row = [3];
bt_parameters_mintpyprocessing.Layout.Column = [1];
bt_parameters_mintpyprocessing.Tooltip = 'Click to define the parameters for MintPy.';

%Button georef mintpy
bt_georef_mintpyprocessing = uibutton(grid_minptpyprocessing,'Text','Select the reference point','Tag','mintpy_ref_point_button','Enable','off');    
bt_georef_mintpyprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) mintpy_parameters(src,evt,'selectionreferencepoint',figmiesar.UserData);
bt_georef_mintpyprocessing.Layout.Row = [3];
bt_georef_mintpyprocessing.Layout.Column = [2];
bt_georef_mintpyprocessing.Tooltip = 'Click to select the reference point for MintPy.';

%Panel steps mintpy
panel_steps_mintpyprocessing = uipanel(grid_minptpyprocessing,'Title','MintPy Steps','FontSize',15,'FontWeight','bold'); 
panel_steps_mintpyprocessing.Layout.Row = [4 7];
panel_steps_mintpyprocessing.Layout.Column = [1 2];

grid_steps_mintpyprocessing = uigridlayout(panel_steps_mintpyprocessing,[3 1]);

%List steps mintpy
list_steps_mintpyprocessing = uidropdown(grid_steps_mintpyprocessing,'Tag','mintpy_step_popup','Enable','off');   
list_steps_mintpyprocessing.Layout.Row = [1];
list_steps_mintpyprocessing.Layout.Column = [1];
list_steps_mintpyprocessing.Items = {'[1] load_data','[2] modify_network','[3] reference_point','[4] quick_overview','[5] correct_unwrap_error','[6] invert_network','[7] correct_SET','[8] correct_troposphere','[9] deramp','[10] correct_topography','[11] residual_RMS','[12] reference_date','[13] velocity','[14] geocode','[15] google_earth','[16] hdfeos5'}; 
list_steps_mintpyprocessing.Value = {'[1] load_data'};
list_steps_mintpyprocessing.Tooltip = 'Click to select the step of MintPy processing.';
list_steps_mintpyprocessing.ValueChangedFcn = @(src,evt,arg1,arg2) mintpy_processing(src,evt,'infoselectedstep',figmiesar.UserData);

%Button run mintpy
bt_runstep_mintpyprocessing = uibutton(grid_steps_mintpyprocessing,'Text','Run the selected step','Tag','mintpy_step_button','Enable','off');  
bt_runstep_mintpyprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2) mintpy_processing(src,evt,'runselectedstep',figmiesar.UserData);
bt_runstep_mintpyprocessing.Layout.Row = [2];
bt_runstep_mintpyprocessing.Layout.Column = [1];
bt_runstep_mintpyprocessing.Tooltip = 'Click to run the selected step of MintPy processing.';

%Button run all mintpy
bt_runallstep_mintpyprocessing = uibutton(grid_steps_mintpyprocessing,'Text','Run all the steps','Tag','mintpy_all_steps_button','Enable','off');    
bt_runallstep_mintpyprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2,arg3) mintpy_allstep(src,evt,'init',[],figmiesar.UserData);
bt_runallstep_mintpyprocessing.Layout.Row = [3];
bt_runallstep_mintpyprocessing.Layout.Column = [1];
bt_runallstep_mintpyprocessing.Tooltip = 'Click to run all the steps of MintPy processing.';

%Panel display mintpy
panel_display_mintpyprocessing = uipanel(grid_minptpyprocessing,'Title','Display the results','FontSize',15,'FontWeight','bold'); 
panel_display_mintpyprocessing.Layout.Row = [8 9];
panel_display_mintpyprocessing.Layout.Column = [1 2];

grid_display_mintpyprocessing = uigridlayout(panel_display_mintpyprocessing,[1 3]);

%Button display raster mintpy
bt_displayraster_mintpyprocessing = uibutton(grid_display_mintpyprocessing,'Text','Raster','Tag','mintpy_plot_vel_button','Enable','off');   
bt_displayraster_mintpyprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2,arg3) mintpy_API_view(src,evt,[],figmiesar.UserData);
bt_displayraster_mintpyprocessing.Layout.Row = [1];
bt_displayraster_mintpyprocessing.Layout.Column = [1];
bt_displayraster_mintpyprocessing.Tooltip = 'Click to display the MintPy results from raster data.';

%Button display ts mintpy
bt_displayts_mintpyprocessing = uibutton(grid_display_mintpyprocessing,'Text','Time series','Tag','mintpy_plot_ts_button','Enable','off');    
bt_displayts_mintpyprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2,arg3) mintpy_API_tsview(src,evt,[],figmiesar.UserData);
bt_displayts_mintpyprocessing.Layout.Row = [1];
bt_displayts_mintpyprocessing.Layout.Column = [2];
bt_displayts_mintpyprocessing.Tooltip = 'Click to display the MintPy results from time series data.';

%Button display profiles mintpy
bt_displayprofile_mintpyprocessing = uibutton(grid_display_mintpyprocessing,'Text','Profiles','Tag','mintpy_plot_prof_button','Enable','off');    
bt_displayprofile_mintpyprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2,arg3) mintpy_API_plot_trans(src,evt,[],figmiesar.UserData);
bt_displayprofile_mintpyprocessing.Layout.Row = [1];
bt_displayprofile_mintpyprocessing.Layout.Column = [3];
bt_displayprofile_mintpyprocessing.Tooltip = 'Click to display the MintPy results using profiles.';

%Button save mintpy
bt_save_mintpyprocessing = uibutton(grid_minptpyprocessing,'Text','Save the results','Tag','mintpy_save_button','Enable','off');  
bt_save_mintpyprocessing.ButtonPushedFcn = @(src,evt,arg1,arg2,arg3) mintpy_API_save(src,evt,[],figmiesar.UserData);
bt_save_mintpyprocessing.Layout.Row = [10];
bt_save_mintpyprocessing.Layout.Column = [1 2];
bt_save_mintpyprocessing.Tooltip = 'Click to save the MintPy results.';

%% Menu bar
%Level 0
help_menubar = uimenu(figmiesar,'Text','Help');
quit_menubar = uimenu(figmiesar,'Text','Quit');

%Level -1
help_help_menubar = uimenu(help_menubar,'Text','Help','Tag','dede');
% help_help_menubar.ButtonPushedFcn = @(src,event,action) EZ_InSAR(src,event,'defineWK');
check_versions_menubar = uimenu(help_menubar,'Text','Check the versions','Tag','dede');
check_versions_menubar.MenuSelectedFcn = @(src,evt,arg1,arg2) check_tool_versions(src,evt,[],[]);

about_help_menubar = uimenu(help_menubar,'Text','About','Tag','dede');
about_help_menubar.MenuSelectedFcn = @(src,evt,arg1,arg2) EZ_InSAR(src,evt,'information',figmiesar.UserData);

quit_menubar.MenuSelectedFcn = @(src,evt,arg1,arg2) EZ_InSAR(src,evt,'quit',figmiesar.UserData);

%% Progress bar
title_progressbar = uilabel(gridfigmiesar,'Text','Processing in progress:','HorizontalAlignment','left','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
title_progressbar.Tag = 'dede'; 
title_progressbar.Layout.Row = [26];
title_progressbar.Layout.Column = [1 2];

name_progressbar = uilabel(gridfigmiesar,'Text','','HorizontalAlignment','right','VerticalAlignment','center','FontSize',15);
name_progressbar.Tag = 'name_progressbar'; 
name_progressbar.Layout.Row = [26];
name_progressbar.Layout.Column = [3 5];

progressbar = uiaxes(gridfigmiesar); 
progressbar.Tag = 'progressbar';
progressbar.Layout.Row = [27 28];
progressbar.Layout.Column = [1 5];
progressbar.XLim = [0 100];
progressbar.YLim = [0 1];
plot(progressbar,[0 100 100 0 0],[0 0 1 1 0],'-k')
progressbar.XTick = []; 
progressbar.YTick = []; 
progressbar.Toolbar = []; 

%% Text info
name_text_info = uilabel(gridfigmiesar,'Text','Information:','HorizontalAlignment','left','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
name_text_info.Tag = 'label_maintextoutput'; 
name_text_info.Layout.Row = [26];
name_text_info.Layout.Column = [6 10];

text_info = uitextarea(gridfigmiesar,'Editable','off');
text_info.Tag = 'maintextoutput'; 
text_info.Layout.Row = [27 28];
text_info.Layout.Column = [6 10];

%% App info
dvpt_info = uilabel(gridfigmiesar,'Text','Developed by UCD''s team','HorizontalAlignment','right','VerticalAlignment','center','FontSize',10,'FontWeight','bold');
dvpt_info.Tag = 'dede'; 
dvpt_info.Layout.Row = [26];
dvpt_info.Layout.Column = [11 15];

version_info = uilabel(gridfigmiesar,'Text','Release: 2.1.0 Beta','HorizontalAlignment','right','VerticalAlignment','center','FontSize',10,'FontWeight','bold');
version_info.Tag = 'dede'; 
version_info.Layout.Row = [27];
version_info.Layout.Column = [11 15];

% githublink = uihyperlink(gridfigmiesar,'HorizontalAlignment','right','VerticalAlignment','center'); 
% githublink.Layout.Row = [28];
% githublink.Layout.Column = [15];
% githublink.Text = 'EZ-InSAR GitHub';
% githublink.URL = 'https://github.com/alexisInSAR/EZ-InSAR';

%% Finalisation of grid
pg_figopen.Value = 1; 
pg_figopen.Message = 'The application is ready.';
pause(0.25); 

close(figopen); 

figmiesar.Visible = 'on'; 

%% Some information on the terminal
disp(sprintf('---------------------------------------------------------'))
disp(sprintf('---------------------------------------------------------'))
disp(sprintf('Welcome in EZ-InSAR Application:'))
disp(sprintf('\tMatlab Interface for Easy InSAR'))
disp(sprintf('---------------------------------------------------------'))
disp(sprintf('---------------------------------------------------------'))
disp(sprintf('Open source application of bridge between ISCE/StaMPS/MintPy'))
disp(sprintf('Version 2.1.0 Beta'))
disp(sprintf('Developed by an UCD team.'))

%% Extraction of handle
hdl = gcf; 

end 
