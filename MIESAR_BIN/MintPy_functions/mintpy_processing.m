function mintpy_processing(src,evt,action,miesar_para)
%   mintpy_processing(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to run the MintPy steps
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also mintpy_allstep, mintpy_API_tsplottrans, mintpy_parameters, mintpy_API_plot_trans, mintpy_API_plottrans, mintpy_processing, mintpy_API_save, mintpy_network_plot.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 17/02/2022
%
%   -------------------------------------------------------
%   Modified:
%           - Xiaowen Wang, UCD, 10/03/2022: bug fix
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)

switch action
    case 'runselectedstep'
        %% Run the selected Mintpy step

        % Identification of the selected step
        cellstep = get(findobj(gcf,'Tag','mintpy_step_popup'),'Items');
        valuecellstep = get(findobj(gcf,'Tag','mintpy_step_popup'),'Value');
        cellstepbis = cell(1); for i1 = 1 : length(cellstep); ci = strsplit(cellstep{i1},' '); cellstepbis{i1} = ci{end}; end; cellstep = cellstepbis; 
        valuecellstep = strsplit(valuecellstep,' '); valuecellstep = valuecellstep{end}; 

        namestep = valuecellstep; 
        valuecellstep = find(cellfun(@(s) ~isempty(strfind(namestep, s)), cellstep)==1)

        % Read the log
        if exist([miesar_para.WK,'/stepmintpy.log']) == 0
            fi = fopen([miesar_para.WK,'/stepmintpy.log'],'w');
            fprintf(fi,'load_data NE\n');
            fprintf(fi,'modify_network NE\n');
            fprintf(fi,'reference_point NE\n');
            fprintf(fi,'quick_overview OPT\n');
            fprintf(fi,'correct_unwrap_error OPT\n');
            fprintf(fi,'invert_network NE\n');
            %             fprintf(fi,'correct_LOD OPT\n');
            fprintf(fi,'correct_SET OPT\n');
            fprintf(fi,'correct_troposphere OPT\n');
            fprintf(fi,'deramp OPT\n');
            fprintf(fi,'correct_topography OPT\n');
            fprintf(fi,'residual_RMS NE\n');
            fprintf(fi,'reference_date NE\n');
            fprintf(fi,'velocity NE\n');
            fprintf(fi,'geocode NE\n');
            fprintf(fi,'google_earth NE\n');
            fprintf(fi,'hdfeos5 NE\n');
            fclose(fi);
        end

        fi = fopen([miesar_para.WK,'/stepmintpy.log'],'r'); logstack = textscan(fi,'%s %s'); fclose(fi);

        % Check if the step already is done
        previous = 0;
        if valuecellstep == 1
            previous = 1;
        elseif valuecellstep == 2 | valuecellstep == 3 | valuecellstep == 12 | valuecellstep == 13 | valuecellstep == 14 | valuecellstep == 15 | valuecellstep == 16
            if strcmp(logstack{2}{valuecellstep-1},'RUN') == 1
                previous = 1;
            end
        elseif valuecellstep == 6 | valuecellstep == 4
            if strcmp(logstack{2}{3},'RUN') == 1
                previous = 1;
            end
        elseif valuecellstep == 7 | valuecellstep == 8 | valuecellstep == 9 | valuecellstep == 10
            if strcmp(logstack{2}{6},'RUN') == 1
                previous = 1;
            end
        elseif valuecellstep == 11
            if strcmp(logstack{2}{6},'RUN') == 1
                previous = 1;
            end
        else
            previous = 1;
        end

        if previous == 1
            cmd = namestep;
            runi = 1;
            if strcmp(logstack{2}{valuecellstep},'RUN') == 1
                answer = questdlg(sprintf('The %s step already is done.\n\n Do you want to rerun this step?',namestep),'Warning','YES','NO','YES');
                switch answer
                    case 'YES'
                        runi = 1;
                    case 'NO'
                        runi = 0;
                end
            end
        else
            runi = 0;
        end

        % Run the selected step
        if runi == 1
            fi = fopen([miesar_para.WK,'/mintpydirectory.log'],'r');
            pathmintpyprocessing = textscan(fi,'%s'); fclose(fi); pathmintpyprocessing = pathmintpyprocessing{1}{1};

            % Define the name of .cgf
            paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
            switch paramslc.pass
                case 'Asc'
                    Porb = 'A';
                case 'Desc'
                    Porb = 'D';
            end
            name_cfg = ['mintpyfullparametersSen',Porb,'T',paramslc.track,'.cfg'];

            % Write the scripts
            scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];
            fid = fopen(scripttoeval,'w');
            fprintf(fid,'cd %s\n',[pathmintpyprocessing]);
            fprintf(fid,'smallbaselineApp.py %s --dostep %s\n',name_cfg,cmd);
            fprintf(fid,'%s\n',['sed -i ''/',logstack{1}{valuecellstep},'/ s/NE/RUN/'' ',miesar_para.WK,'/stepmintpy.log']);
            fclose(fid);
            logstack{2}{valuecellstep} = 'RUN';
            fi = fopen([miesar_para.WK,'/stepmintpy.log'],'w');
            for i1 = 1 : length(logstack{1}); fprintf(fi,'%s %s\n',logstack{1}{i1},logstack{2}{i1}); end
            fclose(fi);

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
        else
            %Check if the previous step is done before the selected step
            si = ['The previous step is not done. Please, run the previous step before the selected step.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si);
        end

    case 'infoselectedstep'
        cellstep = get(findobj(gcf,'Tag','mintpy_step_popup'),'Items');
        valuecellstep = get(findobj(gcf,'Tag','mintpy_step_popup'),'Value');
        cellstepbis = cell(1); for i1 = 1 : length(cellstep); ci = strsplit(cellstep{i1},' '); cellstepbis{i1} = ci{end}; end; cellstep = cellstepbis; 
        valuecellstep = strsplit(valuecellstep,' '); valuecellstep = valuecellstep{end};
        
        set(findobj(gcf,'Tag','maintextoutput'),'Value',['The selected step of MintPy is: ',valuecellstep]);
        set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');

        %Update the progress bar
         update_progressbar_MIESAR([],[],miesar_para,'MintPy'); 

end 
