function mintpy_parameters(src,evt,action,miesar_para)
%   Function to manage the parameters for ISCE
%
%   See also mintpy_allstep, mintpy_API_tsview, mintpy_parameters, mintpy_API_plot_trans, mintpy_API_view, mintpy_processing, mintpy_API_save, mintpy_network_plot.
%
%   Copyright 2022 Alexis Hrysiewicz, UCD / iCRAG2
%   Version: 1.0.0
%   Date: 17/02/2020
%   Modified by Xiaowen Wang, UCD, 10/03/2022

switch action
    case 'pathmintpy'
        %% Creation of directories
        % Check if the directory already is created
        rep = 1;
        if exist([miesar_para.WK,'/mintpydirectory.log']) == 0 
               
            % Directory to MintPy processing
            pathmintpyprocessing = [miesar_para.WK,'/stackmintpy'];
            system(['mkdir -p ',pathmintpyprocessing]);
            pathmintpyprocessingbis = uigetdir(pathmintpyprocessing);

            if strcmp(pathmintpyprocessing,pathmintpyprocessingbis) == 0
%                system(['rm -R ',pathmintpyprocessing]);
                pathmintpyprocessing = pathmintpyprocessingbis;
            end
            fi = fopen([miesar_para.WK,'/mintpydirectory.log'],'w');
            fprintf(fi,'%s\n',pathmintpyprocessing);
            fclose(fi);

            % Initialisation of the smallbaselineApp.cfg
            mintpy_parameters([],[],'readcfgfile',miesar_para)
            
        else
            f = msgbox('The mintpy directory is alreay exist, click OK to reset it!', 'Set MintPy workpath','warn'); 
            system(['rm ', miesar_para.WK, '/mintpydirectory.log']);             
        end

        % Active the next buttons
        set(findobj(gcf,'Tag','mintpy_ISCE_network_button'),'Enable','on');
        set(findobj(gcf,'Tag','mintpy_parameters_button'),'Enable','on');
        set(findobj(gcf,'Tag','mintpy_ref_point_button'),'Enable','on');
        set(findobj(gcf,'Tag','mintpy_step_popup'),'Enable','on');
        set(findobj(gcf,'Tag','mintpy_step_button'),'Enable','on');
        set(findobj(gcf,'Tag','mintpy_all_steps_button'),'Enable','on');
        set(findobj(gcf,'Tag','mintpy_plot_vel_button'),'Enable','on');
        set(findobj(gcf,'Tag','mintpy_plot_ts_button'),'Enable','on');
        set(findobj(gcf,'Tag','mintpy_plot_prof_button'),'Enable','on');
        set(findobj(gcf,'Tag','mintpy_save_button'),'Enable','on');

    case 'readcfgfile'
        %% Read the smallbaselineApp.cfg and save a .mat files

        % Check the directory
        if exist([miesar_para.WK,'/mintpydirectory.log']) == 0
            si = ['The preparation of Mintpy stack is not detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si);
        end

        % Load the MintPy directory
        fi = fopen([miesar_para.WK,'/mintpydirectory.log'],'r');
        pathmintpyprocessing = textscan(fi,'%s'); fclose(fi); pathmintpyprocessing = pathmintpyprocessing{1}{1};

        % Initialise the .mat
        mintpy_full_parameters = [];
        mintpy_full_parameters.list = cell(1);
        h = 1;
        % Read the file
        fid = fopen(['smallbaselineApp.cfg'],'rt');
        while true
            thisline = fgetl(fid);
            if ~ischar(thisline); break; end
            if isempty(thisline)==0
                if strcmp(thisline(1),'#')== 0
                    if strcmp(thisline(1:7),'mintpy.')
                        a = strsplit(thisline,' ');
                        name_parameter = a{1};
                        value_parameter = a{3};
                        info_parameter = strjoin(a(4:end));
                        eval(['mintpy_full_parameters.',name_parameter,'.name=','''',name_parameter,''';'])
                        eval(['mintpy_full_parameters.',name_parameter,'.value=','''',value_parameter,''';'])
                        eval(['mintpy_full_parameters.',name_parameter,'.info=','''',info_parameter,''';'])
                        mintpy_full_parameters.list{h} = name_parameter;
                        h = h + 1;
                    end
                end
            end
        end
        fclose(fid);

        % Save the .mat
        save([pathmintpyprocessing,'/mintpy_full_parameters.mat'],'-STRUCT','mintpy_full_parameters');

        % Run the other scripts
        mintpy_parameters([],[],'writecfgfile',miesar_para);
        mintpy_parameters([],[],'initialisation_parameters',miesar_para);

    case 'writecfgfile'
        %% Write the ISCE_smallbaselineApp.cfg

        % Check the directory
        if exist([miesar_para.WK,'/mintpydirectory.log']) == 0
            si = ['The preparation of Mintpy stack is not detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si);
        end

        % Load the MintPy directory
        fi = fopen([miesar_para.WK,'/mintpydirectory.log'],'r');
        pathmintpyprocessing = textscan(fi,'%s'); fclose(fi); pathmintpyprocessing = pathmintpyprocessing{1}{1};
        mintpy_full_parameters = load([pathmintpyprocessing,'/mintpy_full_parameters.mat']);

        % Name the .cfg
        paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
        switch paramslc.pass
            case 'Asc'
                Porb = 'A';
            case 'Desc'
                Porb = 'D';
        end
        name_cfg = ['mintpyfullparametersSen',Porb,'T',paramslc.track,'.cfg'];

        % Write the .cfg file
        fi = fopen([pathmintpyprocessing,'/',name_cfg],'w');
        fprintf(fi,'# vim: set filetype=cfg:\n');
        fprintf(fi,'##------------------------ %s ------------------------##\n',name_cfg);
        for i1 = 1 : length(mintpy_full_parameters.list)
            name_parameter = mintpy_full_parameters.list{i1};
            eval(['value_parameter = mintpy_full_parameters.',name_parameter,'.value;']);
            eval(['info_parameter = mintpy_full_parameters.',name_parameter,'.info;']);

            %             fprintf(fi,'%s\t\t\t\t=%s %s\n',name_parameter,value_parameter,info_parameter);
            fprintf(fi,'%s\t\t\t\t= %s\n',name_parameter,value_parameter);
        end
        fclose(fi);

    case 'initialisation_parameters'
        %% Initialisation of first parameters

        % Check the directory
        if exist([miesar_para.WK,'/mintpydirectory.log']) == 0
            si = ['The preparation of Mintpy stack is not detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si);
        end

        % Load the MintPy directory
        fi = fopen([miesar_para.WK,'/mintpydirectory.log'],'r');
        pathmintpyprocessing = textscan(fi,'%s'); fclose(fi); pathmintpyprocessing = pathmintpyprocessing{1}{1};
        mintpy_full_parameters = load([pathmintpyprocessing,'/mintpy_full_parameters.mat']);

        % Modification of parameters
        mintpy_full_parameters.mintpy.compute.cluster.value = 'local';
        mintpy_full_parameters.mintpy.compute.numWorker.value = '4';
        mintpy_full_parameters.mintpy.load.processor.value = 'isce';
        mintpy_full_parameters.mintpy.load.autoPath.value = 'no';
        mintpy_full_parameters.mintpy.load.metaFile.value       = [miesar_para.WK,'/reference/IW*.xml'];
        mintpy_full_parameters.mintpy.load.baselineDir.value    = [miesar_para.WK,'/baselines'];
        mintpy_full_parameters.mintpy.load.unwFile.value        = [miesar_para.WK,'/merged/interferograms/*/filt*.unw'];
        mintpy_full_parameters.mintpy.load.corFile.value        = [miesar_para.WK,'/merged/interferograms/*/filt*.cor'];
        mintpy_full_parameters.mintpy.load.connCompFile.value   = [miesar_para.WK,'/merged/interferograms/*/filt*.unw.conncomp'];
        mintpy_full_parameters.mintpy.load.ionoFile.value       = 'None';
        mintpy_full_parameters.mintpy.load.intFile.value        = 'None';
        mintpy_full_parameters.mintpy.load.demFile.value        = [miesar_para.WK,'/merged/geom_reference/hgt.rdr'];
        mintpy_full_parameters.mintpy.load.lookupYFile.value    = [miesar_para.WK,'/merged/geom_reference/lat.rdr'];
        mintpy_full_parameters.mintpy.load.lookupXFile.value    = [miesar_para.WK,'/merged/geom_reference/lon.rdr'];
        mintpy_full_parameters.mintpy.load.incAngleFile.value   = [miesar_para.WK,'/merged/geom_reference/los.rdr'];
        mintpy_full_parameters.mintpy.load.azAngleFile.value    = [miesar_para.WK,'/merged/geom_reference/los.rdr'];
        mintpy_full_parameters.mintpy.load.shadowMaskFile.value = [miesar_para.WK,'/merged/geom_reference/shadowMask.rdr'];
        mintpy_full_parameters.mintpy.load.waterMaskFile.value  = [miesar_para.WK,'/merged/geom_reference/waterMask.rdr'];
        mintpy_full_parameters.mintpy.load.bperpFile.value      = 'None';

        [lonta,lata] = read_kml([miesar_para.WK,'/area.kml']);
        mintpy_full_parameters.mintpy.subset.lalo.value = [num2str(min(lata)),':',num2str(max(lata)),',',num2str(min(lonta)),':',num2str(max(lonta))];

        mintpy_full_parameters.mintpy.unwrapError.method.value     = 'auto';
        mintpy_full_parameters.mintpy.unwrapError.numSample.value  = '20';

        mintpy_full_parameters.mintpy.networkInversion.weightFunc.value = 'var';
        mintpy_full_parameters.mintpy.networkInversion.maskDataset.value = 'coherence';
        mintpy_full_parameters.mintpy.networkInversion.maskThreshold.value = '0.2';
        mintpy_full_parameters.mintpy.networkInversion.minTempCoh.value = '0.4';

        mintpy_full_parameters.mintpy.troposphericDelay.method.value 	= 'height_correlation';

        mintpy_full_parameters.mintpy.deramp.value = 'linear';
        mintpy_full_parameters.mintpy.save.hdfEos5.value    = 'yes';

        % Save the modification
        save([pathmintpyprocessing,'/mintpy_full_parameters.mat'],'-STRUCT','mintpy_full_parameters');
        mintpy_parameters([],[],'writecfgfile',miesar_para);

    case 'selectionreferencepoint'
        %% User selection of reference point by map

        % Check the directory
        if exist([miesar_para.WK,'/mintpydirectory.log']) == 0
            si = ['The preparation of Mintpy stack is not detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'String',si);
            set(findobj(gcf,'Tag','maintextoutput'),'ForegroundColor','red');
            error(si);
        end

        % Load the MintPy directory
        fi = fopen([miesar_para.WK,'/mintpydirectory.log'],'r');
        pathmintpyprocessing = textscan(fi,'%s'); fclose(fi); pathmintpyprocessing = pathmintpyprocessing{1}{1};

        % Read the reference point
        mintpy_full_parameters = load([pathmintpyprocessing,'/mintpy_full_parameters.mat']);
        rfpt = mintpy_full_parameters.mintpy.reference.lalo.value;

        % Read the kml
        [lont,latt] = read_kml([miesar_para.WK,'/target.kml']);
        [lonta,lata] = read_kml([miesar_para.WK,'/area.kml']);

        %         % Check if maskConnComp.h5 is here:
        %         if exist([pathmintpyprocessing,'/maskConnComp.h5'])
        %             mode_mask = 1;
        %             maskConnComp = h5read([pathmintpyprocessing,'/maskConnComp.h5'],'/mask');
        %
        %             maskConnComp = h5read(['maskConnComp.h5'],'/mask');
        %             maskConnComp = cellfun(@(x) strcmp(x,'TRUE'), maskConnComp, 'UniformOutput',false);
        %             maskConnComp = double(cell2mat(maskConnComp));
        %
        %             lat = h5read(['inputs/geometryRadar.h5'],'/latitude');
        %             lon = h5read(['inputs/geometryRadar.h5'],'/longitude');
        %
        %             h5dump -d latitude -b LE -o test.raw inputs/geometryRadar.h5
        %
        %             system('gdalinfo inputs/geometryRadar.h5')
        %             system('gdal_translate -of GTiff HDF5:"inputs/geometryRadar.h5://latitude":0 test.tif')
        %
        %             figure;
        %             p1 = pcolor(lon,lat,maskConnComp);
        %             set(p1,'EdgeColor','none');
        %         else
        %             mode_mask = 0;
        %         end

        % Display the figure
        figi = figure('name','Selection of reference point','numbertitle','off'); figi.Position = [48 71 1292 727];

        geoplot(latt,lont,'-r');
        hold on; geoplot(lata,lonta,'-b'); hold off;
        lg = legend('Target','ROI');
        axi = gca;
        axi.FontSize = 25; axi.FontWeight = 'bold'; geobasemap('satellite');
        title('Selection of reference point');

        % User input
        if strcmp(rfpt,'auto') == 1
            title('Select the reference point');
            h = drawpoint;
            latrf = h.Position(1);
            lonrf = h.Position(2);
            h.Label = 'Reference point';
            mintpy_full_parameters.mintpy.reference.lalo.value = [num2str(latrf),', ',num2str(lonrf)];
            % Save the modification
            save([pathmintpyprocessing,'/mintpy_full_parameters.mat'],'-STRUCT','mintpy_full_parameters');
            mintpy_parameters([],[],'writecfgfile',miesar_para);
            title('Move the reference point if needed');
        else
            a = split(rfpt,',');
            latrf = str2num(a{1});
            lonrf = str2num(a{2});
            h = drawpoint('Position',[latrf lonrf]);
            h.Label = 'Reference point';
            title('Move the reference point if needed');
        end
        addlistener(h,'MovingROI',@(src,evt) savereferencepoint(src,evt,pathmintpyprocessing,mintpy_full_parameters,miesar_para));

    case 'GUImintpyparameters'
        %% GUI for user selection of parameters

        % Check the directory
        if exist([miesar_para.WK,'/mintpydirectory.log']) == 0
            si = ['The preparation of Mintpy stack is not detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'String',si);
            set(findobj(gcf,'Tag','maintextoutput'),'ForegroundColor','red');
            error(si);
        end

        % Load the MintPy directory
        fi = fopen([miesar_para.WK,'/mintpydirectory.log'],'r');
        pathmintpyprocessing = textscan(fi,'%s'); fclose(fi); pathmintpyprocessing = pathmintpyprocessing{1}{1};

        %For the figure
        figmintpypara = uifigure('Position',[200 100 1000 800],'Name','MintPy Parameters');
        gridfigmintpypara = uigridlayout(figmintpypara,[10 1]);
        titlemintpypara = uilabel(gridfigmintpypara,'Text','Selection of MintPy parameters','HorizontalAlignment','center','VerticalAlignment','center','FontSize',30,'FontWeight','bold');
        titlemintpypara.Layout.Row = 1;
        titlemintpypara.Layout.Column = [1];
        tablemintpypara = uitable(gridfigmintpypara,'ColumnEditable',[false true false]);
        tablemintpypara.Layout.Row = [2 10];
        tablemintpypara.Layout.Column = [1];
        tablemintpypara.CellEditCallback = @(src,event) GUImintpyparameters('cellchanged');

        %For the menu
        mpara_mintpypara = uimenu(figmintpypara,'Text','&Parameters');
        mpara_mintpypara_defaut = uimenu(mpara_mintpypara,'Text','Defaut parameters');
        mpara_mintpypara_defaut.MenuSelectedFcn = @(src,event) GUImintpyparameters('defaut');

        mmode_mintpypara = uimenu(figmintpypara,'Text','&Mode');
        mmode_mintpypara_bt = uimenu(mmode_mintpypara,'Text','Expert mode','Checked','on');
        mmode_mintpypara_bt.MenuSelectedFcn = @(src,event) GUImintpyparameters('mode');

        GUImintpyparameters('mode')
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Other functions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    function GUImintpyparameters(action)
        %% Manage the list of parameters
        switch action
            case 'mode'
                list_paramaters = {'mintpy.compute.cluster = local', ...
                    'mintpy.load.numWorker', ...
                    'mintpy.load.processor', ...
                    'mintpy.load.autoPath', ...
                    'mintpy.load.metaFile', ...
                    'mintpy.load.unwFile', ...
                    'mintpy.load.corFile', ...
                    'mintpy.load.connCompFile', ...
                    'mintpy.load.intFile', ...
                    'mintpy.load.demFile', ...
                    'mintpy.load.lookupYFile', ...
                    'mintpy.load.lookupXFile', ...
                    'mintpy.load.incAngleFile', ...
                    'mintpy.load.azAngleFile', ...
                    'mintpy.load.shadowMaskFile', ...
                    'mintpy.subset.lalo', ...
                    'mintpy.reference.lalo', ...
                    'mintpy.network.tempBaseMax', ...
                    'mintpy.network.perpBaseMax', ...
                    'mintpy.network.startDate', ...
                    'mintpy.network.endDate', ...
                    'mintpy.unwrapError.method', ...
                    'mintpy.networkInversion.weightFunc', ...
                    'mintpy.networkInversion.maskDataset', ...
                    'mintpy.networkInversion.maskThreshold', ...
                    'mintpy.networkInversion.minTempCoh', ...
                    'mintpy.troposphericDelay.method', ...
                    'mintpy.deramp', ...
                    'mintpy.save.hdfEos5'};

                if strcmp(mmode_mintpypara_bt.Checked,'on')
                    mmode_mintpypara_bt.Checked = 'off';
                    titlemintpypara.Text = 'Selection of MintPy parameters (Normal mode)';
                else
                    mmode_mintpypara_bt.Checked = 'on';
                    titlemintpypara.Text = 'Selection of MintPy parameters (Expert mode)';
                end

                %Create the table
                mintpy_full_parameters = load([pathmintpyprocessing,'/mintpy_full_parameters.mat']);
                cell_mintpy_parameters = cell(1);
                h = 1;
                for i1 = 1 : length(mintpy_full_parameters.list)
                    name_parameter = mintpy_full_parameters.list{i1};
                    eval(['value_parameter = mintpy_full_parameters.',name_parameter,'.value;']);
                    eval(['info_parameter = mintpy_full_parameters.',name_parameter,'.info;']);
                    if strcmp(mmode_mintpypara_bt.Checked,'on')
                        cell_mintpy_parameters{h,1} = name_parameter;
                        cell_mintpy_parameters{h,2} = value_parameter;
                        cell_mintpy_parameters{h,3} = info_parameter;
                        h = h + 1;
                    else
                        if isempty(find(strcmpi(list_paramaters,name_parameter))==1) == 0
                            cell_mintpy_parameters{h,1} = name_parameter;
                            cell_mintpy_parameters{h,2} = value_parameter;
                            cell_mintpy_parameters{h,3} = info_parameter;
                            h = h + 1;
                        end
                    end
                end

                % Update the table
                table_mintpy_parameters = cell2table(cell_mintpy_parameters,'VariableNames',{'Parameters' 'Value' 'Information'});
                tablemintpypara.Data = table_mintpy_parameters;

            case 'defaut'
                % Update the parameters with defaut values
                close(figmintpypara);
                mintpy_parameters([],[],'readcfgfile',miesar_para);
                mintpy_parameters([],[],'writecfgfile',miesar_para);
                mintpy_parameters([],[],'initialisation_parameters',miesar_para);
                %             mintpy_parameters('selectionreferencepoint',miesar_para);
                mintpy_parameters([],[],'GUImintpyparameters',miesar_para);

            case 'cellchanged'
                % Check the user inputs
                cell_mintpy_parameters = table2cell(tablemintpypara.Data);
                mintpy_full_parameters = load([pathmintpyprocessing,'/mintpy_full_parameters.mat']);
                for i1 = 1 : size(cell_mintpy_parameters,1)
                    name_parameter = cell_mintpy_parameters{i1,1};
                    value_parameter = cell_mintpy_parameters{i1,2};
                    info_parameter = cell_mintpy_parameters{i1,3};
                    %                     eval(['mintpy_full_parameters.',name_parameter,'.name=','''',name_parameter,''';'])
                    eval(['mintpy_full_parameters.',name_parameter,'.value=','''',value_parameter,''';'])
                    %                     eval(['mintpy_full_parameters.',name_parameter,'.info=','''',info_parameter,''';'])
                end
                % Update the file
                save([pathmintpyprocessing,'/mintpy_full_parameters.mat'],'-STRUCT','mintpy_full_parameters');
                mintpy_parameters([],[],'writecfgfile',miesar_para);
        end
    end

end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Other functions (no global)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function savereferencepoint(src,evt,pathmintpyprocessing,mintpy_full_parameters,miesar_para)
latrf = evt.CurrentPosition(1);
lonrf = evt.CurrentPosition(2);
mintpy_full_parameters.mintpy.reference.lalo.value = [num2str(latrf),', ',num2str(lonrf)];
save([pathmintpyprocessing,'/mintpy_full_parameters.mat'],'-STRUCT','mintpy_full_parameters');
mintpy_parameters([],[],'writecfgfile',miesar_para);
title('Move the reference point if needed');
end
