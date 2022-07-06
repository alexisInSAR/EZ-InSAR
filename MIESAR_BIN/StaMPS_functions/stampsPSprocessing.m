function stampsPSprocessing(src,evt,action,miesar_para)
%   stampsPSprocessing(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to run the PS StaMPS processing.
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
    case 'prep'
        %% Prepare the PS stack 
        
        % Check the directory
        if exist([miesar_para.WK,'/stampsdirectory.log'])
            si = ['The preparation of PS processing will be done...'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');
        else
            si = ['The preparation of StaMPS stack is not detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red'); 
            error(si);
        end 
        
        % Load the StaMPS directory 
        fi = fopen([miesar_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{2};
        
        % Preparation of the mt_prep script
        prompt = {'Amplitude dispersion','Number of patches in range',...
            'Number of patches in azimuth','Overlapping pixels between patches in range',...
            'overlapping pixels between patches in azimuth'};
        dlgtitle = 'mt_prep for PS approach';
        dims = [1 35];
        definput = {'0.4','1','1','50','200'};
        answer = inputdlg(prompt,dlgtitle,dims,definput);
        if length(answer) == 5  
            cmd = ['mt_prep_isce ',answer{1},' ',answer{2},' ',answer{3},' ',answer{4},' ',answer{5}];
        else 
            warning('Cancel the processing.')
            cmd= [];
        end
        % Write the script for evaluation
        scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];
        fid = fopen(scripttoeval,'w');
        fprintf(fid,'cd %s\n',pathstampsprocessing);
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

        update_progressbar_MIESAR([],[],miesar_para,'stampsPS')
        
    case 'parm'
        %% Launch the GUI to select the StaMPS parameters
        cur = cd;
                
        % Check the directory
        if exist([miesar_para.WK,'/stampsdirectory.log'])
            si = ['Please select the parameters for the PS approach.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');
        else
            si = ['The preparation of StaMPS stack is not detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'Fontcolor','red'); 
            error(si);
        end 
        
        % Load the StaMPS log 
        fi = fopen([miesar_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{2};
        
        % Initialisation of the parameters
        cd(pathstampsprocessing);
        getparm;
        cd(cur);
        
        %Run the GUI
        figparm = open('GUIstampsparameters.fig');
        figparm.UserData = miesar_para; 
        runGUIstampsparameters(figparm,'update','PS');
        cd(cur);

        update_progressbar_MIESAR([],[],miesar_para,'stampsPS')
        
    case 'run'
        %% Run the PS processing 

        % Check the directory
        if exist([miesar_para.WK,'/stampsdirectory.log'])
            si = ['The PS processing will be done...'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');
        else
            si = ['The preparation of StaMPS stack is not detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red'); 
            error(si);
        end 
        update_progressbar_MIESAR([],[],miesar_para,'stampsPS'); 
        
        % Load the log 
        fi = fopen([miesar_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi);
        pathstampsprocessingbis = pathstampsprocessing{1}{2};
        pathstampsprocessing = pathstampsprocessing{1}{1};
        
        % Creation of the table to display
        filelog = [pathstampsprocessing,'/PSprocess.log'];
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
        figi = figure('name','PS StaMPS processing','numbertitle','off','MenuBar', 'none','ToolBar','none'); figi.Position = [111 147 941 350];
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
            for i1 = step1 : step2
                cd(pathstampsprocessingbis)
                stamps(i1,i1);
                cd(cur);
                system(['sed -i -e ''s/',['stamps',num2str(i1),' NE'],'/',['stamps',num2str(i1),' RUN'],'/g'' ',pathstampsprocessing,'/PSprocess.log']); 
                update_progressbar_MIESAR([],[],miesar_para,'stampsPS')
            end 
        else
            warning('StaMPS procesing has been cancelled.'); 
        end  
end
