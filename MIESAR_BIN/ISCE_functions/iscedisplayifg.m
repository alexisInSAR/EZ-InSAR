function iscedisplayifg(src,evt,action,miesar_para)
%   iscedisplayifg(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%       
%       Function to visualise the interferograms using mdx.py script with a
%       GUI.
%
%       See also conversionstacks_SI_IW, isce_switch_stackfunctions, conversionstacks_SI_SM, parallelizationstepISCE, dem_box_cal, iscedisplayifg, removewatermask_ISCEprocessing_SM, isce_preprocessing_S1_IW, runISCEallstep, isce_preprocessing_SM, selectionofstack, isceprocessing.
%   
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 17/02/2020
%
%   -------------------------------------------------------
%   Modified:
%           - Alexis Hrysiewicz, UCD / iCRAG, 18/07/2022: modifcation of
%           text information
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)

%% Check the directories
if exist([miesar_para.WK,'/merged/interferograms'])
    pathifg = [miesar_para.WK,'/merged/interferograms']; 
    si = ['Interferograms directory: OK.'];
    update_textinformation([],[],[],si,'information');
elseif exist([miesar_para.WK,'/merged_mintpy/interferograms'])
    pathifg = [miesar_para.WK,'/merged_mintpy/interferograms']; 
    si = ['Interferograms directory: OK.'];
    update_textinformation([],[],[],si,'information');
else
    si = ['Error: no directory with interferograms'];
    update_textinformation([],[],[],si,'error');
    error(['Error: no directory with interferograms']); 
end 

%% Create the list of interferograms
a = dir(pathifg); 
list = cell(1);
h = 1; 
for i1 = 1 : length(a)
    if length(a(i1).name) == 17
        list{h,1} = a(i1).name; 
        h = h + 1; 
    end 
end 

%% Create the GUI
figapiiscedisp = uifigure('Position',[300 100 1200 900],'Name','List of interferograms');

glapiiscedisp = uigridlayout(figapiiscedisp,[10 5]);

titleapiiscedisp = uilabel(glapiiscedisp,'Text','Visualisation of interferograms using mdx.py','HorizontalAlignment','center','VerticalAlignment','center','FontSize',30,'FontWeight','bold');
titleapiiscedisp.Layout.Row = 1;
titleapiiscedisp.Layout.Column = [1 5];

labellistiscedisp = uilabel(glapiiscedisp,'Text','List of interferograms:','HorizontalAlignment','Left','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
labellistiscedisp.Layout.Row = [2];
labellistiscedisp.Layout.Column = [1 5];

listiscedisp = uilistbox(glapiiscedisp); 
listiscedisp.Layout.Row = [3 9];
listiscedisp.Layout.Column = [1 4];
listiscedisp.Items = list; 
listiscedisp.Multiselect = 'off'; 
listiscedisp.ValueChangedFcn = @(btn,event) run_update_ifg(btn,event);

gridmodeiiscedisp = uigridlayout(glapiiscedisp,[7 1]);
gridmodeiiscedisp.Layout.Row = [3 9];
gridmodeiiscedisp.Layout.Column = [5];

labelmodeiiscedisp = uilabel(gridmodeiiscedisp,'Text','Select the images:','HorizontalAlignment','right','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
labelmodeiiscedisp.Layout.Row = [1];
labelmodeiiscedisp.Layout.Column = [1];

mode_ifg = uicheckbox(gridmodeiiscedisp,'Text','Interferogram'); mode_ifg.Layout.Row = [2]; mode_ifg.Layout.Column = [1];
mode_cor = uicheckbox(gridmodeiiscedisp,'Text','Coherence'); mode_cor.Layout.Row = [3]; mode_cor.Layout.Column = [1]; 
mode_ifg_filt = uicheckbox(gridmodeiiscedisp,'Text','Filt. Interferogram'); mode_ifg_filt.Layout.Row = [4]; mode_ifg_filt.Layout.Column = [1]; 
mode_cor_filt = uicheckbox(gridmodeiiscedisp,'Text','Filt. Coherence'); mode_cor_filt.Layout.Row = [5]; mode_cor_filt.Layout.Column = [1]; 
mode_unw = uicheckbox(gridmodeiiscedisp,'Text','Unwrapped Phase'); mode_unw.Layout.Row = [6]; mode_unw.Layout.Column = [1]; 
mode_unw_conn = uicheckbox(gridmodeiiscedisp,'Text','Connection'); mode_unw_conn.Layout.Row = [7]; mode_unw_conn.Layout.Column = [1]; 

buttonapiiscedisp = uibutton(glapiiscedisp,'Text','Display the selected interferogram','ButtonPushedFcn', @(btn,event) run_display_ifg(btn,event));
buttonapiiscedisp.Layout.Row = [10];
buttonapiiscedisp.Layout.Column = [1 5];

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Other functions (global)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Update from the list
    function run_update_ifg(btn,event)
        pathi = [pathifg,'/',listiscedisp.Value];

        if exist([pathi,'/fine.int'])
            mode_ifg.Enable = 'on';
        else
            mode_ifg.Enable = 'off';
        end
        if exist([pathi,'/fine.cor'])
            mode_cor.Enable = 'on';
        else
            mode_cor.Enable = 'off';
        end
        if exist([pathi,'/filt_fine.int'])
            mode_ifg_filt.Enable = 'on';
        else
            mode_ifg_filt.Enable = 'off';
        end
        if exist([pathi,'/filt_fine.cor'])
            mode_cor_filt.Enable = 'on';
        else
            mode_cor_filt.Enable = 'off';
        end
        if exist([pathi,'/filt_fine.unw'])
            mode_unw.Enable = 'on';
        else
            mode_unw.Enable = 'off';
        end
        if exist([pathi,'/filt_fine.unw.conncomp'])
            mode_unw_conn.Enable = 'on';
        else
            mode_unw_conn.Enable = 'off';
        end
    end

    function run_display_ifg(btn,event)
        pathi = [pathifg,'/',listiscedisp.Value];

        if mode_ifg.Value == 0 &  mode_cor.Value == 0 & mode_ifg_filt.Value == 0 & mode_cor_filt.Value == 0 & mode_unw.Value == 0 & mode_unw_conn.Value == 0 
            error('Please, select an image'); 
        else
            cmd = 'mdx.py '; 
            if mode_ifg.Value == 1 & strcmp(mode_ifg.Enable,'on') == 1
                cmd = [cmd,pathi,'/fine.int ']; 
            end 
            if mode_cor.Value == 1 & strcmp(mode_cor.Enable,'on') == 1
                cmd = [cmd,pathi,'/fine.cor ']; 
            end 
            if mode_ifg_filt.Value == 1 & strcmp(mode_ifg_filt.Enable,'on') == 1
                cmd = [cmd,pathi,'/filt_fine.int ']; 
            end 
            if mode_cor_filt.Value == 1 & strcmp(mode_cor_filt.Enable,'on') == 1
                cmd = [cmd,pathi,'/filt_fine.cor ']; 
            end 
            if mode_unw.Value == 1 & strcmp(mode_unw.Enable,'on') == 1
                cmd = [cmd,pathi,'/filt_fine.unw ']; 
            end 
            if mode_unw_conn.Value == 1 & strcmp(mode_unw_conn.Enable,'on') == 1
                cmd = [cmd,pathi,'/filt_fine.unw.conncomp ']; 
            end 
            cmd = [cmd,'&']; 

            % Run the mdx.py
            system(cmd); 
        end 
    end
end 
