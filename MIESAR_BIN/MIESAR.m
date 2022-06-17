function MIESAR(src,evt,action,miesar_para)
%   IPSP main function to run MIESAR, with or without parameter.
%   Some other functions are here. 
%
%   See also GUIMIESAR

%   Copyright 2021 Alexis Hrysiewicz, UCD / iCRAG2 
%   Version: 1.0.0 
%   Date: 29/11/2021 
%   Modified by Xiaowen Wang, UCD, 24/02/2022
%% If the function is ran without input 
warning('off')
if nargin == 0
    action='initialisation';
    %Save the current directory
    cur = cd; 
    
    %Add the paths
    addpath([cur,'/3rdparty']);
    addpath([cur,'/Suppfunctions']);
    addpath([cur,'/SLC_management']);
    addpath([cur,'/ISCE_functions']);
    addpath([cur,'/StaMPS_functions']);
    addpath([cur,'/MintPy_functions']);
    addpath([cur,'/private']);
    addpath([cur,'/help']);
end

%% If the function is ran with input 
switch action
    case 'initialisation'
        %% Initialisation 
        %Save important information
    	miesar_para.cur = which('MIESAR'); n = find(miesar_para.cur=='/'); miesar_para.cur = miesar_para.cur(1:n(end)); 
    	miesar_para.date = datestr(datetime); 
    	miesar_para.id = string2hash([miesar_para.cur, miesar_para.date]); 
    	
        % Opening of GUI
        hmain = GUIMIESAR(miesar_para);
        
        % Information about paths
        if exist([miesar_para.cur,'pathinformation.txt'])==0
            si = ['The file pathinformation.txt do not exist...'];
            set(findobj(hmain,'Tag','maintextoutput'),'String',si);
            set(findobj(hmain,'Tag','maintextoutput'),'ForegroundColor','red');
        else
            [configpath] = readpathinformation([miesar_para.cur,'pathinformation.txt']);
            h = 0;
            miesar_para.configpath = configpath; 
        end
        
        %% Information about the work directory
        hdl = findobj(hmain,'Tag','mainbutWKpath');
        si = ['The work directory is not defined... Click on the Work Directory button.'];
        set(findobj(hmain,'Tag','maintextoutput'),'Value',si);
        set(findobj(hmain,'Tag','maintextoutput'),'FontColor','black');        
        
    case 'defineWK'

        %% Define the work directory
        %Dialog box for the Work directory
        miesar_para.WK = uigetdir(miesar_para.cur,'Select your work directory');   
        if miesar_para.WK == 0
            si = ['Please select the REAL TRUE GOOD AND ACTIVE FOLDER. =)'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red'); 
            error(si);
        end 
        
        str=['Go to the directory: ', miesar_para.WK];disp(str);cd(miesar_para.WK);
        
        if exist(miesar_para.WK) == 7
            set(gcf,'Userdata',miesar_para);
    
            %%% Check the folder slc, dem, orbits, and aux 
            if exist([miesar_para.WK,'/slc']) == 0 %#ok<EXIST> 
                cmd=['mkdir ', miesar_para.WK, '/slc'];
                system(cmd);
            end
            if exist([miesar_para.WK,'/dem']) == 0 %#ok<EXIST> 
                cmd=['mkdir ', miesar_para.WK, '/dem'];
                system(cmd);
            end
            if exist([miesar_para.WK,'/orbits']) == 0 %#ok<EXIST> 
                cmd=['mkdir ', miesar_para.WK, '/orbits'];
                system(cmd);
            end
            if exist([miesar_para.WK,'/aux']) == 0 %#ok<EXIST> 
                cmd=['mkdir ', miesar_para.WK, '/aux'];
                system(cmd);
            end     
              
            %Initialisation of panels
            set(findobj(gcf,'Tag','mainuipanelprepdata'),'Visible','on');
            set(findobj(gcf,'Tag','mainuipanelisceprocess'),'Visible','on');
            set(findobj(gcf,'Tag','mainuipaneldispprocess'),'Visible','on');
            
            si = ['MIESAR is initialised and ready to run.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');
            
            %Activation of bar menu
    %         set(findobj(gcf,'Tag','barmenu12'),'Enable','on');
    %         set(findobj(gcf,'Tag','barmenu13'),'Enable','on');
    %         set(findobj(gcf,'Tag','barmenu14'),'Enable','on');
    %         set(findobj(gcf,'Tag','barmenu2'),'Enable','on');
    %         set(findobj(gcf,'Tag','barmenu3'),'Enable','on');
    %         set(findobj(gcf,'Tag','barmenu4'),'Enable','on');
    %         set(findobj(gcf,'Tag','barmenu5'),'Enable','on');
    
            set(findobj(gcf,'Tag','mainbutWKpath'),'Backgroundcolor','green');   
            set(findobj(gcf,'Tag','mainbutWKpath'),'ToolTip',sprintf('The Work directory is %s.\n\tYou can click on this button to change the current work directory.',miesar_para.WK));
            
            %Check of SLC directories
            if exist([miesar_para.WK,'/parmsSLC.mat']) == 0
                initparmslc(miesar_para.WK)
            end
            manageparamaterSLC([],[],'update',miesar_para);   
            
            selectionofstack(src,evt,'modestack',miesar_para);
        else 
            si = ['Please select the REAL TRUE GOOD AND ACTIVE FOLDER. =)'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red'); 
            error(si)
        end   

    case 'SLCmanager'
        %% GUI SLC manager
        
        %Loading of directory
        path = load([miesar_para.WK,'/parmsSLC.mat']);
        
        %Open the GUI
        hfig = open('GUIslcmanager.fig');

        set(hfig,'Userdata',miesar_para)
        
        %Display the paths
        if iscell(path.pathSLC) == 1
            path.pathSLC = path.pathSLC{1};
        end
        if iscell(path.pathorbit) == 1
            path.pathorbit = path.pathorbit{1};
        end
        if iscell(path.pathaux) == 1
            path.pathaux = path.pathaux{1};
        end
        
        if exist(path.pathSLC)
            set(findobj(hfig,'Tag','GUIslcmanagerslc'),'string',path.pathSLC,'ForegroundColor','green','FontWeight','bold');
        else
            path.pathSLC=[miesar_para.WK,'/slc'];
            set(findobj(hfig,'Tag','GUIslcmanagerslc'),'string',path.pathSLC,'ForegroundColor','red','FontWeight','bold');
        end
        
        if exist(path.pathorbit)
            set(findobj(hfig,'Tag','GUIslcmanagerorbit'),'string',path.pathorbit,'ForegroundColor','green','FontWeight','bold');
        else
            path.pathorbit=[miesar_para.WK,'/orbits'];
            set(findobj(hfig,'Tag','GUIslcmanagerorbit'),'string',path.pathorbit,'ForegroundColor','red','FontWeight','bold');
        end
        
        if exist(path.pathaux)
            set(findobj(hfig,'Tag','GUIslcmanageraux'),'string',path.pathaux,'ForegroundColor','green','FontWeight','bold');
        else
            path.pathaux=[miesar_para.WK,'/aux'];
            set(findobj(hfig,'Tag','GUIslcmanageraux'),'string',path.pathaux,'ForegroundColor','red','FontWeight','bold');
        end
        
    case 'SLCmanagervalidation'
        %% Validation of SLC directories
        
        %Save the paths and close the GUI
        pathSLC = get(findobj(gcf,'Tag','GUIslcmanagerslc'),'string');
        pathorbit = get(findobj(gcf,'Tag','GUIslcmanagerorbit'),'string');
        pathaux = get(findobj(gcf,'Tag','GUIslcmanageraux'),'string');
        miesar_para = get(gcf,'Userdata'); 

        save([miesar_para.WK,'/parmsSLC.mat'],'pathSLC','pathorbit','pathaux','-append');
        close(gcf)
        
        %Display a short message
        si = ['The directory of SLC is defined.'];
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
        set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');

    case 'Selectionzone'
        %% Selection of study area

        %Check if the target file exists
        if exist([miesar_para.WK,'/target.kml'])==0
            cur = cd;
            [file,path] = uigetfile({'*.kml'},cur,'Select a .kml for the target zone');
            [status,msg] = copyfile([path,'/',file],[miesar_para.WK,'/target.kml']);
        else
            %Dialog box for updating the kml file
            kml_file=[miesar_para.WK,'/target.kml'];
            answer = questdlg(kml_file,'Do you want to update the target zone?','Yes','NO','NO');
            switch answer
                case 'Yes'
                    cur = cd;
                    [file,path] = uigetfile({'*.kml'},cur,'Select a new .kml for the target zone');
                    [status,msg] = copyfile([path,'/',file],[miesar_para.WK,'/target.kml'],'f');
            end


        end

        %Display the target and compute the study area
        hwb = webmap('World Imagery');
        [lont,latt] = read_kml([miesar_para.WK,'/target.kml']);
        wmline(latt,lont,'OverlayName','Target')
        if exist([miesar_para.WK,'/area.kml'])==0
            ext = 0;
            lata = [min(latt)-ext.*(max(latt)-min(latt)) min(latt)-ext.*(max(latt)-min(latt)) ...
                max(latt)+ext.*(max(latt)-min(latt)) max(latt)+ext.*(max(latt)-min(latt)) ...
                min(latt)-ext.*(max(latt)-min(latt))]
            lonta = [min(lont)-ext.*(max(lont)-min(lont)) max(lont)+ext.*(max(lont)-min(lont)) ...
                max(lont)+ext.*(max(lont)-min(lont)) min(lont)-ext.*(max(lont)-min(lont)) ...
                min(lont)-ext.*(max(lont)-min(lont))];
                
            kmlwriteline([miesar_para.WK,'/area.kml'],lata,lonta);
        end
        [lonta,lata] = read_kml([miesar_para.WK,'/area.kml']);
        save([miesar_para.WK,'/parmsSLC.mat'],'lata','lonta','-append'); 
        wmline(lata,lonta,'OverlayName','Area','Color','red');
        
        si = ['The WMS is opened.'];
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
        set(findobj(gcf,'Tag','maintextoutput'),'FontColor','green');

    case 'information'
        %% Display information
        
        si = [sprintf('About:\n'),...
            sprintf('\n------------------------\n'),...
            sprintf('\n'),...
            sprintf('The EZ-InSAR is a Matlab toolbox that make a link between the ISCE processor and StaMPS. It allows to compute the displacements from Sentinel-1 data using the no-convential approaches PS and SBAS.\n'),...
            sprintf('\n'), ...
            sprintf('It is developed by Alexis Hrysiewicz (alexis.hrysiewicz@ucd.ie).\n'), ...
            sprintf('\n\t\t Alpha Version 0.1 (2020).\n')];
        fi = msgbox(si,'About');
        
    case 'quit'
        %% Rage quit button
        
        answer = questdlg('Are you sure to quit EZ-InSAR?', ...
            'Quit?', ...
            'Quit','Return','Return');
        switch answer
            case 'Quit'
                fh=findall(0,'type','figure');
                for i1 = 1 : length(fh)
                    close(fh(i1)); 
                end 
                
        end

    case 'close'
        %% Close function
       disp('---------------------------------------------------------')
        disp('Closing of EZ-InSAR')
        disp('---------------------------------------------------------')
        disp('Deleting of figures...'); close all; 
        disp('Remove the variables'); clear all; 
end
