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
%   See also manageparamaterSLC, initparmslc, readxmlannotationS1, downloaderSLC.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 29/11/2021
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)

%% Action from user inputs
switch action
    case 'update'
        %% Updating of GUI
        paramslc = load([miesar_para.WK,'/parmsSLC.mat']); 
        % Mode of acquisitions
        switch paramslc.mode
            case 'IW'
                set(findobj(gcf,'Tag','mainpopmode'),'Value','IW');
        end
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
        % Mode of acquisitions 
        if strcmp(get(findobj(gcf,'Tag','mainpopmode'),'Value'),'IW') == 1
            mode = 'IW';
        end
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
        
        % Save the parameters
        save([miesar_para.WK,'/parmsSLC.mat'],'date1','date2','sat','mode','track','pass','-append');
        
        % Update the GUI 
        manageparamaterSLC([],[],'update',miesar_para);
        
        % Display some information
        si = ['The parameters of SLCs are saved.'];
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
        set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black')
        
end

