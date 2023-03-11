function EZ_InSAR(src,evt,action,miesar_para)
%   EZ_InSAR(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       EZ-InSAR main function to run Ez-InSAR, with or without parameter.
%       Some other function are here. 
%   
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also GUIMIESAR
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.0.1 Beta
%   Date: 29/11/2021 
%
%   -------------------------------------------------------
%   Modified:
%           - Xiaowen Wang, UCD, 24/02/2022: bug fix
%           - Alexis Hrysiewicz, UCD / iCRAG, 07/07/2022: 
%                   Modication of the function to display the GUI selection path. 
%                   Modification of the function for displaying the extension.
%           - Alexis Hrysiewicz, UCD / iCRAG, 18/07/2022: modifcation of
%           text information
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)
%           2.0.0 Beta: Initial (unreleased)
%           2.0.1 Beta: Initial (unreleased)

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
    	miesar_para.cur = which('EZ_InSAR'); n = find(miesar_para.cur=='/'); miesar_para.cur = miesar_para.cur(1:n(end)); 
    	miesar_para.date = datestr(datetime); 
    	miesar_para.id = string2hash([miesar_para.cur, miesar_para.date]); 
    	
        % Opening of GUI
        hmain = GUIMIESAR(miesar_para);
        
        % Information about paths
        if exist([miesar_para.cur,'pathinformation.txt'])==0
            si = ['The file pathinformation.txt do not exist...'];
            update_textinformation([],[],miesar_para,si,'error')
        else
            [configpath] = readpathinformation([miesar_para.cur,'pathinformation.txt']);
            h = 0;
            miesar_para.configpath = configpath; 
        end
        
        %% Information about the work directory
        hdl = findobj(hmain,'Tag','mainbutWKpath');
        si = ['The work directory is not defined... Click on the Work Directory button.'];   
        update_textinformation([],[],miesar_para,si,'information')
        
    case 'defineWK'

        %% Define the work directory
        %Dialog box for the Work directory
        miesar_para.WK = uigetdir(miesar_para.cur,'Select your work directory');   
        if miesar_para.WK == 0
            si = ['Please select a good folder. =)'];
            update_textinformation([],[],miesar_para,si,'error');   
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
            if exist([miesar_para.WK,'/file_aux']) == 0 %#ok<EXIST> 
                cmd=['mkdir ', miesar_para.WK, '/file_aux'];
                system(cmd);
            end     
              
            %Initialisation of panels
            set(findobj(gcf,'Tag','mainuipanelprepdata'),'Visible','on');
            set(findobj(gcf,'Tag','mainuipanelisceprocess'),'Visible','on');
            set(findobj(gcf,'Tag','mainuipaneldispprocess'),'Visible','on');
            
            si = ['MIESAR is initialised and ready to run.'];
            update_textinformation([],[],miesar_para,si,'success');  
            
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
            update_textinformation([],[],miesar_para,si,'error');  
            error(si)
        end   

    case 'SLCmanager'
        %% GUI SLC manager
        GUIpathdirectory(src,evt,'open',miesar_para,[],[]); 

    case 'Selectionzone'
        %% Selection of study area
        si = ['Selection of the study area:...'];
        update_textinformation([],[],miesar_para,si,'information'); 

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
                min(latt)-ext.*(max(latt)-min(latt))];
            lonta = [min(lont)-ext.*(max(lont)-min(lont)) max(lont)+ext.*(max(lont)-min(lont)) ...
                max(lont)+ext.*(max(lont)-min(lont)) min(lont)-ext.*(max(lont)-min(lont)) ...
                min(lont)-ext.*(max(lont)-min(lont))];
                
            kmlwriteline([miesar_para.WK,'/area.kml'],lata,lonta);
        end
        [lonta,lata] = read_kml([miesar_para.WK,'/area.kml']);
        save([miesar_para.WK,'/parmsSLC.mat'],'lata','lonta','-append'); 
        wmline(lata,lonta,'OverlayName','Area','Color','red');
        
        si = ['The WMS is opened.'];
        update_textinformation([],[],miesar_para,si,'success'); 

    case 'information'
        %% Display information
        
        si = [sprintf('About:\n'),...
            sprintf('\n------------------------\n'),...
            sprintf('\n'),...
            sprintf('The EZ-InSAR is a Matlab toolbox that make a link between the ISCE processor, StaMPS and MintPy. It allows to compute the displacements from Sentinel-1 data.\n'),...
            sprintf('\n'), ...
            sprintf('It is developed by Alexis Hrysiewicz (alexis.hrysiewicz@ucd.ie) and Xiaowen Wang.\n'), ...
            sprintf('\n\t\t Alpha Version 2.0.1 (2023).\n')];
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
