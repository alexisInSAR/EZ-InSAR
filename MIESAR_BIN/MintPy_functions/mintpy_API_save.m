function mintpy_API_save(src,evt,action,miesar_para)
%   Function to save the results from MintPy
%
%   See also mintpy_allstep, mintpy_API_tsview, mintpy_parameters, mintpy_API_plot_trans, mintpy_API_view, mintpy_processing, mintpy_API_save, mintpy_network_plot.
%
%   Copyright 2022 Alexis Hrysiewicz, UCD / iCRAG2
%   Version: 1.0.0
%   Date: 17/02/2020

% Load the MintPy directory
fi = fopen([miesar_para.WK,'/mintpydirectory.log'],'r');
pathmintpyprocessing = textscan(fi,'%s'); fclose(fi); pathmintpyprocessing = pathmintpyprocessing{1}{1};

%% Create the GUI
figapimintpysave = uifigure('Position',[200 100 1000 800],'Name','MintPy''s save.py Application');
glapimintpysave = uigridlayout(figapimintpysave,[20 5]);

titleapimintpysave = uilabel(glapimintpysave,'Text','MintPy''s save.py Application','HorizontalAlignment','center','VerticalAlignment','center','FontSize',30,'FontWeight','bold');
titleapimintpysave.Layout.Row = [1 2];
titleapimintpysave.Layout.Column = [1 5];

labelbgapimintpysave = uilabel(glapimintpysave,'Text','Selection of format:','HorizontalAlignment','Left','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
labelbgapimintpysave.Layout.Row = [3];
labelbgapimintpysave.Layout.Column = [1 5];

% formatitems = {'In GBIS','In GDAL','In GMT','In hdfeos5 (Timeseries)','In kite','In KMZ','In KMZ (Timeseries)','In QGIS (Timeseries)','In ROIPAC'};
formatitems = {'In KMZ','In KMZ (Timeseries)','In QGIS (Timeseries)'};
formatapimintpysave = uidropdown(glapimintpysave,'ValueChangedFcn', @(src,event) updateguifromformat(src,event));
formatapimintpysave.Layout.Row = [4];
formatapimintpysave.Layout.Column = [1 5];
formatapimintpysave.Items = formatitems;
formatapimintpysave.Value = 'In QGIS (Timeseries)';

labeldatasetapimintpysave = uilabel(glapimintpysave,'Text','Dataset:','HorizontalAlignment','Left','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
labeldatasetapimintpysave.Layout.Row = [5];
labeldatasetapimintpysave.Layout.Column = [1 2];

labelsubdatasetapimintpysave = uilabel(glapimintpysave,'Text','Subdataset:','HorizontalAlignment','Right','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
labelsubdatasetapimintpysave.Layout.Row = [5];
labelsubdatasetapimintpysave.Layout.Column = [4 5];

datasetapimintpysave = uidropdown(glapimintpysave,'ValueChangedFcn', @(src,event) updateparameters(src,event));
datasetapimintpysave.Layout.Row = [6];
datasetapimintpysave.Layout.Column = [1 2];

subdatasetapimintpysave = uitextarea(glapimintpysave);
subdatasetapimintpysave.Layout.Row = [6];
subdatasetapimintpysave.Layout.Column = [4 5];
subdatasetapimintpysave.Tooltip = {'example:';...
    'view.py velocity.h5';...
    'view.py velocity.h5 velocity --wrap --wrap-range -2 2 -c cmy --lalo-label';...
    'view.py velocity.h5 --ref-yx  210 566                              #change reference pixel for display';...
    'view.py velocity.h5 --sub-lat 31.05 31.10 --sub-lon 130.05 130.10  #subset in lalo / yx';...
    '  ';...
    'view.py timeseries.h5';...
    'view.py timeseries.h5 -m no                   #do not use auto mask';...
    'view.py timeseries.h5 --ref-date 20101120     #change reference date';...
    'view.py timeseries.h5 --ex drop_date.txt      #exclude dates to plot';...
    'view.py timeseries.h5 ''*2017*'' ''*2018*''       #all acquisitions in 2017 and 2018';...
    'view.py timeseries.h5 20200616_20200908       #reconstruct interferogram on the fly';...
    '';...
    'view.py ifgramStack.h5 coherence';...
    'view.py ifgramStack.h5 unwrapPhase-           #unwrapPhase only in the presence of unwrapPhase_bridging';...
    'view.py ifgramStack.h5 -n 6                   #the 6th slice';...
    'view.py ifgramStack.h5 20171010_20171115      #all data      related with 20171010_20171115';...
    'view.py ifgramStack.h5 ''coherence*20171010*''  #all coherence related with 20171010';...
    'view.py ifgramStack.h5 unwrapPhase-20070927_20100217 --zero-mask --wrap     #wrapped phase';...
    'view.py ifgramStack.h5 unwrapPhase-20070927_20100217 --mask ifgramStack.h5  #mask using connected components';...

    '# GPS (for one subplot in geo-coordinates only)';...
    'view.py geo_velocity_msk.h5 velocity --show-gps --gps-label   #show locations of available GPS';...
    'view.py geo_velocity_msk.h5 velocity --show-gps --gps-comp enu2los --ref-gps GV01';...
    'view.py geo_timeseries_ERA5_ramp_demErr.h5 20180619 --ref-date 20141213 --show-gps --gps-comp enu2los --ref-gps GV01';...

    '# Save and Output';...
    'view.py velocity.h5 --save';...
    'view.py velocity.h5 --nodisplay';...
    'view.py geo_velocity.h5 velocity --nowhitespace';...
    };

labeltableapimintpysave = uilabel(glapimintpysave,'Text','Selection of parameters:','HorizontalAlignment','Left','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
labeltableapimintpysave.Layout.Row = [7];
labeltableapimintpysave.Layout.Column = [1 5];

tableapimintpysave = uitable(glapimintpysave,'ColumnEditable',[false true false]);
tableapimintpysave.Layout.Row = [6 18];
tableapimintpysave.Layout.Column = [1 5];

btoptimiapimintpysave = uibutton(glapimintpysave,'Text','Optimisation');%,'ButtonPushedFcn', @(btn,event) updateoutputname(btn,event));
btoptimiapimintpysave.Layout.Row = [19];
btoptimiapimintpysave.Layout.Column = [1];

outputapimintpysave = uitextarea(glapimintpysave,'Value', {'Please, select the path of output'},'Editable','off');
outputapimintpysave.Layout.Row = [19];
outputapimintpysave.Layout.Column = [2 4];

btoutputapimintpysave = uibutton(glapimintpysave,'Text','Select','ButtonPushedFcn', @(btn,event) updateoutputname(btn,event));
btoutputapimintpysave.Layout.Row = [19];
btoutputapimintpysave.Layout.Column = [5];

buttonapimintpysave = uibutton(glapimintpysave,'Text','Run','ButtonPushedFcn', @(btn,event) run_api_save(btn,event));
buttonapimintpysave.Layout.Row = [20];
buttonapimintpysave.Layout.Column = [1 5];

updateguifromformat([],[]);

gdal_drivers = {'*.tif','GTiff'; ...
    '*.hdr','ENVI'};

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Other functions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Function to update some parameters regarding the format
    function updateparameters(src,event)
        switch formatapimintpysave.Value
            case 'In QGIS (Timeseries)'
                cur_dataset = datasetapimintpysave.Value;
                if isempty(strfind(cur_dataset,'geo'))==0
                    geo_file = [pathmintpyprocessing,'/geo/geo_geometryRadar.h5'];
                else
                    geo_file = [pathmintpyprocessing,'/geometryRadar.h5'];
                end
                paratable = table2cell(tableapimintpysave.Data);
                paratable{1,2} = geo_file;
                tableapimintpysave.Data = cell2table(paratable,'VariableNames',{'Parameters' 'Value' 'Information'});
        end
    end

%% Update the GUI from format
    function updateguifromformat(src,event)
        % GUI modification
        if strcmp(formatapimintpysave.Value,'In QGIS (Timeseries)') | strcmp(formatapimintpysave.Value,'In KMZ (Timeseries)')
            datasetapimintpysave.Enable = 'on';
            subdatasetapimintpysave.Enable = 'off';
            tableapimintpysave.Enable = 'on';
            btoptimiapimintpysave.Enable = 'off';
            outputapimintpysave.Enable = 'on';
            btoutputapimintpysave.Enable = 'on';
            buttonapimintpysave.Enable = 'on';
            mode_TS = 'on';
        elseif strcmp(formatapimintpysave.Value,'In KMZ')
            datasetapimintpysave.Enable = 'on';
            subdatasetapimintpysave.Enable = 'on';
            tableapimintpysave.Enable = 'on';
            btoptimiapimintpysave.Enable = 'off';
            outputapimintpysave.Enable = 'on';
            btoutputapimintpysave.Enable = 'on';
            buttonapimintpysave.Enable = 'on';
            mode_TS = 'off';
        else
            datasetapimintpysave.Enable = 'off';
            subdatasetapimintpysave.Enable = 'off';
            tableapimintpysave.Enable = 'off';
            btoptimiapimintpysave.Enable = 'off';
            outputapimintpysave.Enable = 'off';
            btoutputapimintpysave.Enable = 'off';
            buttonapimintpysave.Enable = 'off';
            error('No implemented yet');
        end

        % Modify the parameter tables
        switch formatapimintpysave.Value
            case 'In GBIS'
                %   file                  deformation file.
                %   dset                  date/date12 of timeseries, or date12 of interferograms to be converted
                % '--output OUTFILE output file name.
                tablepara = {'--geometry', '' ,'geometry file';...
                    '--mask', '' ,'mask file.';...
                    '--ref-lalo', '' ,'REF_LALO REF_LALO custom reference pixel in lat/lon';...
                    '--nodisplay','no','do not display the figure';...
                    '--ellipsoid2geoid','no','Convert the height of ellipsoid to geoid using "geoidheight" module Download & install geoidheight as below: https://github.com/geodesymiami/2021_Kirishima';...
                    };
            case 'In GDAL'
                %   file                  file to be converted, in geo coordinate.
                %-o OUTFILE, --output OUTFILE
                tablepara = {'--dataset','','date of timeseries, or date12 of interferograms to be converted output file base name. Extension is fixed by GDAL driver';...
                    '--output-format','','file format as defined by GDAL driver name, e.g. GTiff, ENVI, default: GTiff GDAL driver names can be found at https://gdal.org/drivers/raster/index.html';...
                    };
            case 'In GMT'
                %   file                  deformation file.
                %   dset                  date/date12 of timeseries, or date12 of interferograms to be converted
                % '--output OUTFILE output file name.
                tablepara = {'','',''};
            case 'In hdfeos5 (Timeseries)'
                % ts_file               Timeseries file
                tablepara = {'--template', '' ,'Template file for 1) arguments/options and 2) missing metadata';...
                    '--temp-coh', '' ,'Coherence/correlation file, i.e. temporalCoherence.h5';...
                    '--avg-spatial-coh', '' ,'Average spatial coherence file, i.e. avgSpatialCoh.h5';...
                    '--mask', '' ,'Mask file';...
                    '--geometry', '' ,'geometry file';...
                    '--update','no','Enable update mode, a.k.a. put XXXXXXXX as endDate in filename if endDate < 1 year';...
                    '--subset','no','Enable subset mode, a.k.a. put suffix _N31700_N32100_E130500_E131100';...
                    };
            case 'In kite'
                %   file                  file to be converted, in geo coordinate.
                %--output OUTFILE
                tablepara = {'--dataset', '' ,'dataset of interest to be converted. e.g.: velocity / stepYYYYMMDD for velocity HDF5 file, date12 in YYYYMMDD_YYYYMMDD for time-series HDF5 file, date12 in unwrapPhase-YYYYMMDD_YYYYMMDD for ifgramStack HDF5 file.';...
                    '--geom', '' ,'geometry file for incidence /azimuth angle and height.';...
                    '--mask', '' ,'mask file, or run mask.py to mask the input file beforehand.';...
                    '--subx', '' ,'XMIN XMAX subset display in x/cross-track/range direction';...
                    '--suby', '' ,'YMIN YMAX subset display in y/along-track/azimuth direction';...
                    '--sublat', '' ,'LATMIN LATMAX subset display in latitude';...
                    '--sublon', '' ,'LONMIN LONMAX subset display in longitude';...
                    };
            case 'In KMZ'
                %                       file                  file to be converted, in geo or radar coordinate.
                %                         Note: for files in radar-coordinate, the corresponding lookup table
                % %                         in radar-coordinate (as provided by ISCE) is required.
                % %   dset                  date of timeseries, or date12 of interferograms to be converted
                % -o OUTFILE, --output OUTFILE
                %                         output file base name. Extension is fixed with .kmz
                tablepara = {'--mask', '' ,'mask file for display';...
                    '--zero-mask','no','Mask pixels with zero value.';...
                    '--keep-kml-file','no','Do not remove KML and data/resource files after compressing into KMZ file.';...
                    '--geom', '' ,'geometry file with lat/lon. [required for file in radar coordinates]';...
                    '--step', '' ,'output one point per {step} pixels, to reduce file size (default: 5). For file in radar-coordinate ONLY.';...
                    '--vlim', '' ,'MIN MAX Y/value limits for plotting.';...
                    '-u', '' ,'unit for display.';...
                    '--colormap', '' ,'Colormap for plotting. Default: jet';...
                    '--wrap','no','re-wrap data to display data in fringes.';...
                    '--wrap-range', '' ,'MIN MAX range of one cycle after wrapping, default: [-pi, pi]';...
                    '--dpi NUM', '' ,'Figure DPI (dots per inch). Default: 600';...
                    '--figsize', '' ,'WID LEN Figure size in inches - width and length';...
                    '--cbar-loc', '' ,'{lower left,lower right,upper left,upper right} Location of colorbar in the screen. Default: lower left.';...
                    '--cbar-label', '' ,'Colorbar label. Default: Mean LOS velocity';...
                    '--cbar-bin-num', '' ,'Colorbar bin number (default: None).';...
                    '--noreference','no','do not show reference point';...
                    '--ref-color', '' ,'marker color of reference point';...
                    '--ref-size', '' ,'marker size of reference point (default: 5).';...
                    '--ref-marker', '' ,'marker symbol of reference point';...
                    '--subx', '' ,'XMIN XMAX subset display in x/cross-track/range direction';...
                    '--suby', '' ,'YMIN YMAX subset display in y/along-track/azimuth direction';...
                    '--sublat', '' ,'LATMIN LATMAX subset display in latitude';...
                    '--sublon', '' ,'LONMIN LONMAX subset display in longitude';...
                    };
            case 'In KMZ (Timeseries)'
                %                    File/Dataset to display
                %
                %   timeseries_file       Timeseries file to generate KML for
                %   --vel FILE            Velocity file, used for the color of dot
                %   --tcoh FILE           temporal coherence file, used for stat info
                %   --mask FILE           Mask file
                %   -o OUTFILE, --output OUTFILE
                %                         Output KMZ file name.
                tablepara = {'--vel', '' ,'Velocity file, used for the color of dot';...
                    '--tcoh', '' ,'temporal coherence file, used for stat info';...
                    '--mask', '' ,'mask file for display';...
                    '--steps', '' ,'STEPS STEPS STEPS list of steps for output pixel (default: [20, 5, 2]). Set to [20, 5, 0] to skip the 3rd high-resolution level to reduce file size.';...
                    '--level-of-details', '' ,'LODS LODS LODS LODS list of level of details to determine the visible range while browering. Default: 0, 1500, 4000, -1. Ref: https://developers.google.com/kml/documentation/kml_21tutorial';...
                    '--vlim', '' ,'VMIN VMAX min/max range in cm/yr for color coding.';...
                    '--wrap','no','re-wrap data to [VMIN, VMAX) for color coding.';...
                    '--colormap', '' ,'colormap used for display, i.e. jet, RdBu, hsv, jet_r, temperature, viridis,  etc. colormaps in Matplotlib - http://matplotlib.org/users/colormaps.html colormaps in GMT - http://soliton.vm.bytemark.co.uk/pub/cpt-city/';...
                    '--cutoff', '' ,'choose points with velocity >= cutoff * MAD. Default: 3.';...
                    '--min-percentage', '' ,'choose boxes with >= min percentage of pixels are deforming. Default: 0.2.';...
                    };
            case 'In QGIS (Timeseries)'
                %   ts_file               time-series HDF5 file
                % --outshp SHP_FILE
                tablepara = {'--geom', '' ,'geometry HDF5 file Output shape file.';...
                    '--bbox', '' ,'Y0 Y1 X0 X1 bounding box : minLine maxLine minPixel maxPixel';...
                    '--geo-bbox', '' ,'S N W E bounding box in lat lon: South North West East';...
                    };
            case 'In ROIPAC'
                %   file                  HDF5 file to be converted.
                %   dset                  date/date12 of timeseries, or date12 of interferograms to be converted
                %   -o OUTFILE, --output OUTFILE
                %                         output file name.
                tablepara = {'--mask', '' ,'[MASK_FILE ...] mask file';...
                    '--ref-yx', '' ,'REF_YX REF_YX custom reference pixel in y/x';...
                    '--ref-lalo', '' ,'REF_LALO REF_LALO custom reference pixel in lat/lon';...
                    };
        end
        tableapimintpysave.Data = cell2table(tablepara,'VariableNames',{'Parameters' 'Value' 'Information'});

        % Check the possible datasets
        list_data_set = dir(pathmintpyprocessing);
        data_set = cell(1);
        h = 1;
        for i1 = 1 : length(list_data_set)
            if isempty(strfind(list_data_set(i1).name,'.h5')) == 0
                data_set{h} = list_data_set(i1).name;
                h = h + 1;
            end
        end
        list_data_set = dir([pathmintpyprocessing,'/inputs']);
        for i1 = 1 : length(list_data_set)
            if isempty(strfind(list_data_set(i1).name,'.h5')) == 0
                data_set{h} = list_data_set(i1).name;
                h = h + 1;
            end
        end
        list_data_set = dir([pathmintpyprocessing,'/geo']);
        for i1 = 1 : length(list_data_set)
            if isempty(strfind(list_data_set(i1).name,'.h5')) == 0
                data_set{h} = list_data_set(i1).name;
                h = h + 1;
            end
        end

        h = 1;
        data_set_bis = cell(1);
        if strcmp(mode_TS,'on') == 1
            for i1 = 1 : length(data_set)
                if contains(data_set{i1},'timeseries')
                    data_set_bis{h} = data_set{i1};
                    h = h + 1;
                end
            end
        else
            data_set_bis = data_set;
        end

        % Modification of dropdown
        datasetapimintpysave.Items = data_set_bis;
        datasetapimintpysave.Value = data_set_bis{end};
        updateparameters([],[])
    end

%% Function of output name
    function updateoutputname(btn,event)
        switch formatapimintpysave.Value
            case 'In GBIS'
                filter = {'*.mat','GBIS Files (*.mat)'};
            case 'In GDAL'
                paratable = table2cell(tableapimintpysave.Data);
                if isempty(paratable{2,2}) == 1
                    filter = gdal_drivers;
                else
                    for i1 = 1 : size(gdal_drivers,1)
                        if strcmp(paratable{2,2},gdal_drivers{i1,2})
                            filter = gdal_drivers{i1,:};
                            break
                        end
                    end
                end
            case 'In GMT'
                filter = {'*.kmz','GMT Files (*.kmz)'};
            case 'In hdfeos5 (Timeseries)'
                filter = {'*.h5','hdfeos5 Files (*.h5)'};
            case 'In kite'
                filter = {'*','kite Files (*)'};
            case 'In KMZ'
                filter = {'*.kmz','KMZ Files (*.kmz)'};
            case 'In KMZ (Timeseries)'
                filter = {'*.kmz','KMZ Files (*.kmz)'};
            case 'In QGIS (Timeseries)'
                filter = {'*.shp','QGIS Files (*.shp)'};
            case 'In ROIPAC'
                filter = {'*','ROIPAC Files (*)'};
        end

        [file, path] = uiputfile(filter);
        name_path = [path,file];

        switch formatapimintpysave.Value
            case 'In GDAL'
                paratable = table2cell(tableapimintpysave.Data);
                if isempty(paratable{2,2}) == 1
                    fileext = strsplit(file,'.'); fileext = ['*.',fileext{end}];
                    for i1 = 1 : size(gdal_drivers,1)
                        if strcmp(fileext,gdal_drivers{i1,1})
                            paratable{2,2} = gdal_drivers{i1,2}
                            break
                        end
                    end
                    tableapimintpysave.Data = cell2table(paratable,'VariableNames',{'Parameters' 'Value' 'Information'});
                end
        end

        outputapimintpysave.Value = name_path;
    end

%% Fuction to run the save_*.py application from Mintpy
    function run_api_save(btn,event)
        cur_dataset = datasetapimintpysave.Value;
        cur_subdataset = subdatasetapimintpysave.Value{1};

        % Check the datasets
        pref = '';
        if isempty(strfind(cur_dataset,'geo'))==0 & strcmp(cur_dataset,'geometryRadar.h5')== 0
            pref = 'geo/';
        elseif strcmp(cur_dataset,'ifgramStack.h5')== 1 | strcmp(cur_dataset,'geometryRadar.h5')== 1
            pref = 'inputs/';
        else
            pref = '';
        end

        % Check the good command
        switch formatapimintpysave.Value
            case 'In GBIS'
                cmdbase = 'save_gbis.py';
            case 'In GDAL'
                cmdbase = 'save_gdal.py';
            case 'In GMT'
                cmdbase = 'save_gmt.py';
            case 'In hdfeos5 (Timeseries)'
                cmdbase = 'save_hdfeos5.py';
            case 'In kite'
                cmdbase = 'save_kite.py';
            case 'In KMZ'
                cmdbase = 'save_kmz.py';
            case 'In KMZ (Timeseries)'
                cmdbase = 'save_kmz_timeseries.py';
            case 'In QGIS (Timeseries)'
                cmdbase = 'save_qgis.py';
            case 'In ROIPAC'
                cmdbase = 'save_roipac.py';
        end

        % Check the parameters
        paratablecheck = table2cell(tableapimintpysave.Data);

        cmd = [cmdbase,' ',pref,cur_dataset,' ',cur_subdataset];
        for i1 = 1 : size(paratablecheck)
            if isempty(paratablecheck{i1,2}) == 0 & strcmp(paratablecheck{i1,2},'no') == 0
                if strcmp(paratablecheck{i1,2},'yes') == 1
                    cmd = [cmd,' ',paratablecheck{i1,1}];
                else
                    cmd = [cmd,' ',paratablecheck{i1,1},' ',paratablecheck{i1,2}];
                end
            end
        end

        if strcmp(outputapimintpysave.Value{1},'Please, select the path of output') == 0
            cmd = [cmd,' -o ',outputapimintpysave.Value{1}];
        end

        % Write the command
        scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];
        fid = fopen(scripttoeval,'w');
        fprintf(fid,'cd %s\n',[pathmintpyprocessing]);
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
    end
end
