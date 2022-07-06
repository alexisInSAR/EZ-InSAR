function stampsSBASprocessing(src,evt,action,miesar_para)
%   stampsSBASprocessing(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to run the SBAS StaMPS processing.
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also runGUISBASnetwork, runGUIstampsparameters, stampsMERGEDprocessing, stampsprocessing, stampsPSprocessing, stampsSBASprocessing.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 30/11/2021
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)

switch action
    case 'network'
        %% Compute the network of interferograms
        
        % Check the directory
        if exist([miesar_para.WK,'/stampsdirectory.log'])
            si = ['Opening of SBAS-Network tool...'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');
        else
            si = ['The preparation of StaMPS stack is not detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red'); 
            error(si);
        end 
        
        % Load the directory 
        fi = fopen([miesar_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{2};
        
        % Write the script for evaluation before to display the network
        curdir = cd;
        cmd = ['mt_extract_info_isce'];
        scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];
        fid = fopen(scripttoeval,'w');
        fprintf(fid,'cd %s\n',pathstampsprocessing);
        fprintf(fid,'%s\n',cmd);
        fprintf(fid,'cd %s\n',curdir);
        fprintf(fid,'rm exec.log\n');
        fclose(fid);
        fi = fopen('exec.log','w'); fclose(fi);
        
        % Run the script
        system(['chmod a+x ',scripttoeval]);
        if strcmp(computer,'MACI64') == 1
            %                     system('./runmacterminal.sh');
        else
            system(['./',scripttoeval]);
        end
        try
            delete(scripttoeval)
        end

        while exist('exec.log') == 2
            pause(2)
        end
        
        cd(pathstampsprocessing)
        ps_load_info;
        cd(curdir)
        
        % Run the GUI
        runGUISBASnetwork('init',miesar_para);
        
        update_progressbar_MIESAR([],[],miesar_para,'stampsSBAS')

    case 'computeifg'
        %% Compute the interferograms using the defined network
        
        % Load the directory 
        fi = fopen([miesar_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); 
        
        % Check the directory
        if exist([pathstampsprocessing{1}{2},'/small_baselines.list'])
            si = ['The computation fof SBAS interferograms will be done...'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');
        else
            si = ['The network file is not detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'Fontcolor','red'); 
            error(si);
        end 
        
        pathstampsprocessing = pathstampsprocessing{1}{2};
        
        % Write the script for evaluation
        cmd = ['make_small_baselines_isce'];
        scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];
        fid = fopen(scripttoeval,'w');
        fprintf(fid,'cd %s\n',[pathstampsprocessing]);
        fprintf(fid,'%s\n',cmd);
        fclose(fid);
        
        % Run the script
        system(['chmod a+x ',scripttoeval]);
        if strcmp(computer,'MACI64') == 1
            %                     system('./runmacterminal.sh');
        else
            system(['./',scripttoeval]);
        end
        try
            delete(scripttoeval)
        end

        update_progressbar_MIESAR([],[],miesar_para,'stampsSBAS')
        
    case 'prep'
        %% Prepare the SBAS StaMPS stack 
        
        % Load the directory 
        fi = fopen([miesar_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{2};
        
        % Parameters for mt_prep
        prompt = {'Amplitude dispersion','Number of patches in range',...
            'Number of patches in azimuth','Overlapping pixels between patches in range',...
            'overlapping pixels between patches in azimuth'};
        dlgtitle = 'mt_prep for SBAS approach';
        dims = [1 35];
        definput = {'0.6','1','1','50','200'};
        answer = inputdlg(prompt,dlgtitle,dims,definput);
        
        % Write the script for evaluation
        cmd = ['mt_prep_isce ',answer{1},' ',answer{2},' ',answer{3},' ',answer{4},' ',answer{5}];
        scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];
        fid = fopen(scripttoeval,'w');
        fprintf(fid,'cd %s\n',[pathstampsprocessing,'/SMALL_BASELINES']);
        fprintf(fid,'%s\n',cmd);
        fclose(fid);
        
        % Run the script
        system(['chmod a+x ',scripttoeval]);
        if strcmp(computer,'MACI64') == 1
            %                     system('./runmacterminal.sh');
        else
            system(['./',scripttoeval]);
        end
        try
            delete(scripttoeval)
        end

        update_progressbar_MIESAR([],[],miesar_para,'stampsSBAS')
        
    case 'parm'
        %% Launch the GUI to select the StaMPS parameters
        cur = cd;
        
        % Load the work directory 
%         fid = fopen('workdirectory.txt');
%         miesar_para.WK = fgetl(fid); fclose(fid);
        
        % Check the directory
        if exist([miesar_para.WK,'/stampsdirectory.log'])
            si = ['Please select the parameters for the SBAS approach.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');
        else
            si = ['The preparation of StaMPS stack is SBAS detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red'); 
            error(si);
        end 
        
        % Load the directory 
        fi = fopen([miesar_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{2};
        
        % Initialisation of the parameters
        cd([pathstampsprocessing,'/SMALL_BASELINES']);
        if exist('parms.mat') == 0
            sb_parms_initial;
        end 
        cd(cur);
        
        % Run the GUI
        figparm = open('GUIstampsparameters.fig');
        figparm.UserData = miesar_para; 
        runGUIstampsparameters(figparm,'update','SBAS');
        cd(cur);

        update_progressbar_MIESAR([],[],miesar_para,'stampsSBAS')
        
    case 'run'
        %% Run the SBAS processing 
        % Check the directory
        if exist([miesar_para.WK,'/stampsdirectory.log'])
            si = ['The SBAS processing will be done...'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');
        else
            si = ['The preparation of StaMPS stack is not detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red'); 
            error(si);
        end 
        update_progressbar_MIESAR([],[],miesar_para,'stampsSBAS'); 
        
        % Load the other directories 
        fi = fopen([miesar_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi);
        pathstampsprocessingbis = pathstampsprocessing{1}{2};
        pathstampsprocessing = pathstampsprocessing{1}{1};
        
        % Creation of the table to display
        filelog = [pathstampsprocessing,'/SBASprocess.log'];
        call = {'StaMPS Step 1: Initial load of data',...
            'StaMPS Step 2: Estimate gamma',...
            'StaMPS Step 3: Select PS pixels',...
            'StaMPS Step 4: Weed out adjacent pixels',...
            'StaMPS Step 5: Correct wrapped phase for spatially-uncorrelated error',...
            'StaMPS Step 6: Unwrap phase',...
            'StaMPS Step 7: Calculate spatially correlated look angle (DEM) error',...
            'StaMPS Step 8: Filter spatially correlated noise'};
        rescell = cell(1);
        for i1 = 1 : 8
            [a,test] = system(['grep ''',['stamps',num2str(i1)],''' ',filelog,' | amiesar_para.WK ''END {print $2}''']); test = strtrim(test);
            c = call{i1};
            
            if strcmp(test,'RUN') == 1
                rescell{i1} = ['<HTML><FONT color="green">',c,'</Font></html>'];
            else
                rescell{i1} = ['<HTML><FONT color="red">',c,'</Font></html>'];
            end
        end
        figi = figure('name','SBAS StaMPS processing','numbertitle','off','MenuBar', 'none','ToolBar','none'); figi.Position = [111 147 941 350];
        uicontrol('Style','list', 'Position',[29 18 890 300], 'String',rescell,'FontSize',25);
        
        % Select the step to run
        prompt = {'First step','Last Step'};
        dlgtitle = 'StaMPS Processing Step';
        dims = [1 35];
        definput = {'1','8'};
        answer = inputdlg(prompt,dlgtitle,dims,definput);
        close(figi);
        if isempty(answer) == 0
            step1 = str2num(answer{1});
            step2 = str2num(answer{2});
            cur = cd;
            % Run the selected step(s)
            for i1 = step1 : step2
                cd([pathstampsprocessingbis,'/SMALL_BASELINES'])
                stamps(i1,i1);
                cd(cur);
                system(['sed -i -e ''s/',['stamps',num2str(i1),' NE'],'/',['stamps',num2str(i1),' RUN'],'/g'' ',pathstampsprocessing,'/SBASprocess.log']);
                update_progressbar_MIESAR([],[],miesar_para,'stampsSBAS')
            end
        else
            warning('StaMPS procesing has been cancelled.');
        end
end
