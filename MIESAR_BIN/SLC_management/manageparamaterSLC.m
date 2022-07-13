function manageparamaterSLC(src,evt,action,miesar_para)
%   manageparamaterSLC(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to manage the SLC parameters (updating and saving) from
%       the GUI inputs.
%
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also createlistSLC, GUIpathdirectory, displayextensionS1, initparmslc, readxmlannotationS1, displayextensionTSXPAZ, manageparamaterSLC, downloaderSLC, manageSLC.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 29/11/2021
%
%   -------------------------------------------------------
%   Modified:
%           - Alexis Hrysiewicz, UCD / iCRAG, 07/07/2022: StripMap
%           implementation
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)
%           2.0.0 Alpha: Initial (unreleased)

%% Action from user inputs
switch action
    case 'update'
        %% Updating of GUI
        paramslc = load([miesar_para.WK,'/parmsSLC.mat']);

        % Mode of data
        switch paramslc.mode
            case 'S1_IW'
                set(findobj(gcf,'Tag','mainpopmode'),'Value','S1_IW');
            case 'S1_SM'
                set(findobj(gcf,'Tag','mainpopmode'),'Value','S1_SM');
            case 'TSX_SM' 
                set(findobj(gcf,'Tag','mainpopmode'),'Value','TSX_SM');
            case 'TSX_SPT' 
                set(findobj(gcf,'Tag','mainpopmode'),'Value','TSX_SPT');
            case 'PAZ_SM' 
                set(findobj(gcf,'Tag','mainpopmode'),'Value','PAZ_SM');
            case 'PAZ_SPT' 
                set(findobj(gcf,'Tag','mainpopmode'),'Value','PAZ_SPT');
            case 'CSK_SM' 
                set(findobj(gcf,'Tag','mainpopmode'),'Value','CSK_SM');
            case 'CSK_SPT' 
                set(findobj(gcf,'Tag','mainpopmode'),'Value','CSK_SPT');
        end

        % Mode for Sentinel-1 data
        % For the other data, we use dumpy values.

        % Track of satellites
        set(findobj(gcf,'Tag','maintexttrack'),'Value',paramslc.track);

        % Name of satellites
        switch paramslc.sat
            case 'A'
                set(findobj(gcf,'Tag','mainboxS1A'),'Value',1);
                set(findobj(gcf,'Tag','mainboxS1B'),'Value',0);
            case 'B'
                set(findobj(gcf,'Tag','mainboxS1A'),'Value',0);
                set(findobj(gcf,'Tag','mainboxS1B'),'Value',1);
            case 'AB'
                set(findobj(gcf,'Tag','mainboxS1A'),'Value',1);
                set(findobj(gcf,'Tag','mainboxS1B'),'Value',1);
            case ''
                set(findobj(gcf,'Tag','mainboxS1A'),'Value',0);
                set(findobj(gcf,'Tag','mainboxS1B'),'Value',0);
        end

        % Pass of satellites
        switch paramslc.pass
            case 'Asc'
                set(findobj(gcf,'Tag','mainpoppass'),'Value','Ascending');
            case 'Desc'
                set(findobj(gcf,'Tag','mainpoppass'),'Value','Descending');
        end

        % Date 1
        set(findobj(gcf,'Tag','maintextdate1'),'Value',datetime(paramslc.date1));

        % Date 2
        set(findobj(gcf,'Tag','maintextdate2'),'Value',datetime(paramslc.date2));

    case 'save'
        %% Save the SLC parameters from the GUI inputs

        % Mode of data
        if strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'S1_IW') == 1
            mode = 'S1_IW';
        elseif strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'S1_SM') == 1
            mode = 'S1_SM';
        elseif strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'PAZ_SM') == 1 
            mode = 'PAZ_SM';
        elseif strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'PAZ_SPT') == 1 
            mode = 'PAZ_SPT';
        elseif strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'TSX_SM') == 1 
            mode = 'TSX_SM'; 

            si = ['This sensor is not implemented yet.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si); 

        elseif strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'TSX_SPT') == 1 
            mode = 'TSX_SPT';

            si = ['This sensor is not implemented yet.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si); 

        elseif strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'CSK_SM') == 1 
            mode = 'CSK_SM'; 

            si = ['This sensor is not implemented yet.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si); 

        elseif strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'CSK_SPT') == 1 
            mode = 'CSK_SPT';

            si = ['This sensor is not implemented yet.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si); 

        elseif strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'ALOS2_SM') == 1 
            mode = 'ALOS2_SM';

            si = ['This sensor is not implemented yet.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si);

        elseif strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'ALOS2_SPT') == 1 
            mode = 'ALOS2_SPT';

            si = ['This sensor is not implemented yet.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si); 

        end

        % Mode for Sentinel-1
        if strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'S1_IW') == 1 | strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'S1_SM') == 1

            % Track of satellites
            track = get(findobj(gcf,'Tag','maintexttrack'),'Value');

            % Name of satellites
            if get(findobj(gcf,'Tag','mainboxS1A'),'Value') == 1 & get(findobj(gcf,'Tag','mainboxS1B'),'Value') == 1
                sat = 'AB';
                set(findobj(gcf,'Tag','maintextoutput'),'Value',['']);
            elseif get(findobj(gcf,'Tag','mainboxS1A'),'Value') == 1 & get(findobj(gcf,'Tag','mainboxS1B'),'Value') == 0
                sat = 'A';
                set(findobj(gcf,'Tag','maintextoutput'),'Value',['']);
            elseif get(findobj(gcf,'Tag','mainboxS1A'),'Value') == 0 & get(findobj(gcf,'Tag','mainboxS1B'),'Value') == 1
                sat = 'B';
                set(findobj(gcf,'Tag','maintextoutput'),'Value',['']);
            elseif get(findobj(gcf,'Tag','mainboxS1A'),'Value') == 0 & get(findobj(gcf,'Tag','mainboxS1B'),'Value') == 0
                set(findobj(gcf,'Tag','maintextoutput'),'Value',['Please select at least one satellite.']);
                set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red')
                error('Please select at least one satellite.')
            end

            % Pass of satellites
            if strcmp(get(findobj(gcf,'Tag','mainpoppass'),'Value'),'Ascending') == 1
                pass = 'Asc';
            else
                pass = 'Desc';
            end

            % Date 1
            date1 = datestr(get(findobj(gcf,'Tag','maintextdate1'),'Value'),'yyyy-mm-dd');

            % Date 2
            date2 = datestr(get(findobj(gcf,'Tag','maintextdate2'),'Value'),'yyyy-mm-dd');

            % Display some information
            si = ['The parameters of SLCs are saved.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black')

        else

            % Mode for other data
            track = '001';
            sat = 'AB';
            pass = 'Asc';
            date1 = '1900-01-01';
            date2 = '2000-01-01';

            % Display some information
            si = ['The SLCs should be already donwloaded and stored in the slc directory.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');

        end

        % Save the parameters
        save([miesar_para.WK,'/parmsSLC.mat'],'date1','date2','sat','mode','track','pass','-append');

        % Update the GUI
        manageparamaterSLC([],[],'update',miesar_para);

end

% We change the GUI
if strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'S1_IW') == 1 | strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'S1_SM') == 1

    set(findobj(gcf,'Tag','maintexttrack'),'Enable','on')
    set(findobj(gcf,'Tag','mainboxS1A'),'Enable','on')
    set(findobj(gcf,'Tag','mainboxS1B'),'Enable','on')
    set(findobj(gcf,'Tag','mainpoppass'),'Enable','on')
    set(findobj(gcf,'Tag','maintextdate1'),'Enable','on')
    set(findobj(gcf,'Tag','maintextdate2'),'Enable','on')
    set(findobj(gcf,'Tag','buttondownloaderS1'),'Enable','on')

    if strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'S1_SM') == 1
        set(findobj(gcf,'Tag','buttoncheckIPF'),'Enable','off')
    else
        set(findobj(gcf,'Tag','buttoncheckIPF'),'Enable','on')
    end 

else
    set(findobj(gcf,'Tag','maintexttrack'),'Enable','off')
    set(findobj(gcf,'Tag','mainboxS1A'),'Enable','off')
    set(findobj(gcf,'Tag','mainboxS1B'),'Enable','off')
    set(findobj(gcf,'Tag','mainpoppass'),'Enable','off')
    set(findobj(gcf,'Tag','maintextdate1'),'Enable','off')
    set(findobj(gcf,'Tag','maintextdate2'),'Enable','off')
    set(findobj(gcf,'Tag','buttondownloaderS1'),'Enable','off')
    set(findobj(gcf,'Tag','buttoncheckIPF'),'Enable','off')
    
end

if strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'S1_IW') == 0
    set(findobj(gcf,'Tag','bt_crop_stampsprocessing'),'Enable','off')
    set(findobj(gcf,'Tag','modeiscesteppara'),'Enable','off')
else
    set(findobj(gcf,'Tag','bt_crop_stampsprocessing'),'Enable','on')
    set(findobj(gcf,'Tag','modeiscesteppara'),'Enable','on')
end 