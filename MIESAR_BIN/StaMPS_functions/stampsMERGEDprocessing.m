function stampsMERGEDprocessing(src,evt,action,miesar_para)
%   Function to run the merged StaMPS processing using PS and SBAS results
%
%   See also runGUISBASnetwork, runGUIstampsparameters,
%   stampsMERGEDprocessing, stampsprocessing, stampsPSprocessing,
%   stampsSBASprocessing.

%   Copyright 2021 Alexis Hrysiewicz, UCD / iCRAG2 
%   Version: 1.0.0 
%   Date: 30/11/2021

switch action
    
    case 'prep'
        %% Preparation and merge of PS/SBAS results

        % Check the directories
        if exist([miesar_para.WK,'/stampsdirectory.log'])
            si = ['The PS/SBAS processing will be done...'];
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
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{1};
        
        % Check the previous processing
        filelogSBAS = [pathstampsprocessing,'/SBASprocess.log'];
        filelogPS = [pathstampsprocessing,'/PSprocess.log'];
        call = {'StaMPS Step 1: Initial load of data',...
            'StaMPS Step 2: Estimate gamma',...
            'StaMPS Step 3: Select PS pixels',...
            'StaMPS Step 4: Weed out adjacent pixels',...
            'StaMPS Step 5: Correct wrapped phase for spatially-uncorrelated error',...
            'StaMPS Step 6: Unwrap phase',...
            'StaMPS Step 7: Calculate spatially correlated look angle (DEM) error',...
            'StaMPS Step 8: Filter spatially correlated noise'};
        
        % For the PS results
        rescellPS = cell(1);
        teststep5 = 1;
        for i1 = 1 : 8
            [a,test] = system(['grep ''',['stamps',num2str(i1)],''' ',filelogPS,' | awk ''END {print $2}''']); test = strtrim(test);
            c = call{i1};
            if strcmp(test,'RUN') == 1
                rescellPS{i1} = ['<HTML><FONT color="green">',c,'</Font></html>'];
            else
                rescellPS{i1} = ['<HTML><FONT color="red">',c,'</Font></html>'];
                if i1 == 5
                    teststep5 = 0;
                end
            end
        end
        
        % For the SBAS results 
        rescellSBAS = cell(1);
        for i1 = 1 : 8
            [a,test] = system(['grep ''',['stamps',num2str(i1)],''' ',filelogSBAS,' | awk ''END {print $2}''']); test = strtrim(test);
            c = call{i1};
            if strcmp(test,'RUN') == 1
                rescellSBAS{i1} = ['<HTML><FONT color="green">',c,'</Font></html>'];
            else
                rescellSBAS{i1} = ['<HTML><FONT color="red">',c,'</Font></html>'];
                if i1 == 5
                    teststep5 = 0;
                end
            end
        end
        
        
        % Run the merging of results
        if teststep5 == 1
            figi1 = figure('name','PS StaMPS processing','numbertitle','off','MenuBar', 'none','ToolBar','none'); figi1.Position = [111 147 941 350];
            uicontrol('Style','list', 'Position',[29 18 890 300], 'String',rescellPS,'FontSize',25);
            figi2 = figure('name','SBAS StaMPS processing','numbertitle','off','MenuBar', 'none','ToolBar','none'); figi2.Position = [111 147 941 350];
            uicontrol('Style','list', 'Position',[29 18 890 300], 'String',rescellSBAS,'FontSize',25);
            answer = questdlg('The necessary step have been detected and done. The MERGE approach is therefore possible.','Information',... ...
                'Ok','Cancel','Ok');
            switch answer
                case 'Ok'
                    close(figi1); close(figi2);
                    curdir = cd; 
                    fi = fopen([miesar_para.WK,'/stampsdirectory.log'],'r');
                    pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{2};
                    cd(pathstampsprocessing)
                    ps_sb_merge 
                    cd(curdir);
            end
        else
            si = ['It is not possible to run the merging of PS/SBAS points because the PS/SBAS processing are not finished.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red'); 
            error(si)
        end

        update_progressbar_MIESAR([],[],miesar_para,'stampsMERGED');
        
    case 'parm'
        %% Launch the GUI to select the StaMPS parameters
        cur = cd;

        % Check the log 
        if exist([miesar_para.WK,'/stampsdirectory.log'])
            si = ['Please select the parameters for the MERGED approach.'];
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
        
        if exist([pathstampsprocessing,'/MERGED'])==0
            si = ['The PS/SBAS are not merged. Please, merge the results.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red'); 
            error(si); 
        end 
        
        % Initialisation of the parameters
        cd([pathstampsprocessing,'/MERGED']);
        if exist('parms.mat') == 0
            system(['cp ',pathstampsprocessing,'/SMALL_BASELINES/parms.mat ',pathstampsprocessing,'/MERGED/parms.mat']);
        end
        cd(cur);
        
        % Run the GUI for the StaMPS parameters
        figparm = open('GUIstampsparameters.fig');
        figparm.UserData = miesar_para; 
        runGUIstampsparameters(figparm,'update','MERGED');
        
        cd(cur);

        update_progressbar_MIESAR([],[],miesar_para,'stampsMERGED');
        
    case 'run'
        %% Run the StaMPS processing using the MERGED approach
        
        % Check the directory
        if exist([miesar_para.WK,'/stampsdirectory.log'])
            si = ['The MERGED processing will be done...'];
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
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi);
        pathstampsprocessingbis = pathstampsprocessing{1}{2};
        pathstampsprocessing = pathstampsprocessing{1}{1};
        
        % Creation of the table to display
        filelog = [pathstampsprocessing,'/Mergedprocess.log'];
        call = {'StaMPS Step 6: Unwrap phase',...
            'StaMPS Step 7: Calculate spatially correlated look angle (DEM) error',...
            'StaMPS Step 8: Filter spatially correlated noise'};
        rescell = cell(1);
        for i1 = 1 : 3
            [a,test] = system(['grep ''',['stamps',num2str(i1+5)],''' ',filelog,' | awk ''END {print $2}''']); test = strtrim(test);
            c = call{i1};
            
            if strcmp(test,'RUN') == 1
                rescell{i1} = ['<HTML><FONT color="green">',c,'</Font></html>'];
            else
                rescell{i1} = ['<HTML><FONT color="red">',c,'</Font></html>'];
            end
        end
        figi = figure('name','PS/SBAS StaMPS processing','numbertitle','off','MenuBar', 'none','ToolBar','none'); figi.Position = [111 147 941 350];
        uicontrol('Style','list', 'Position',[29 18 890 300], 'String',rescell,'FontSize',25);
        
        % Select the step to run
        prompt = {'First step','Last Step'};
        dlgtitle = 'StaMPS Processing Step';
        dims = [1 35];
        definput = {'6','8'};
        answer = inputdlg(prompt,dlgtitle,dims,definput);
        close(figi);
        if isempty(answer) == 0
            step1 = str2num(answer{1});
            step2 = str2num(answer{2});
            if step1<6 | step2 < 6
                si = ['The processing with MERGED approach does not allow the step inferior to 6.'];
                set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
                set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red'); 
                error(si);
            end 
            cur = cd;
            % Run the selected steps
            for i1 = step1 : step2
                cd([pathstampsprocessingbis,'/MERGED'])
                stamps(step1,step2);
                cd(cur);
                system(['sed -i -e ''s/',['stamps',num2str(i1),' NE'],'/',['stamps',num2str(i1),' RUN'],'/g'' ',pathstampsprocessing,'/Mergedprocess.log']);
                update_progressbar_MIESAR([],[],miesar_para,'stampsMERGED');
            end
        else
            warning('StaMPS procesing has been cancelled.');
        end
end