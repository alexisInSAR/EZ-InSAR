function mintpy_API_plot_trans(src,evt,action,miesar_para)
%   mintpy_API_plot_trans(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to interface the plot_transection.py from MintPy. 
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also mintpy_allstep, mintpy_API_tsplottrans, mintpy_parameters, mintpy_API_plot_trans, mintpy_API_plottrans, mintpy_processing, mintpy_API_save, mintpy_network_plot.
%
%   Examples and parameter descriptions from MintPy mintpy_API_plot_trans.py script: https://github.com/insarlab/MintPy
%   Author: Zhang Yunjun, Heresh Fattahi, 2013
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 17/02/2022
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initiale (unreleased)

%% Create the GUI
figapimintpyplottrans = uifigure('Position',[200 100 1000 800],'Name','MintPy''s plottrans.py Application');
glapimintpyplottrans = uigridlayout(figapimintpyplottrans,[20 5]);

tbapimintpyplottrans = uitoolbar(figapimintpyplottrans);
helpapimintpyplottrans = uipushtool(tbapimintpyplottrans);
helpapimintpyplottrans.Icon = fullfile(matlabroot,'toolbox','matlab','icons','help_ex.png');
helpapimintpyplottrans.Tooltip = 'Help';
helpapimintpyplottrans.ClickedCallback = @help_mintpy_API_plottrans;

    function help_mintpy_API_plottrans(src,event)
        cmd = {'Help for plot_transection.py';...
            '---------------------------------------';
            'Please:';
            '1) Select your dataset(s)';
            '2) Select your subdataset (optional) regarding the use of plot_transection.py command';
            '3) Modify the parameters (yes/no or VALUE)';
            '4) Run'};
        boxtmp = msgbox(cmd, 'Help','Help for plot_transection.py');
    end 

titleapimintpyplottrans = uilabel(glapimintpyplottrans,'Text','MintPy''s plottrans.py Application','HorizontalAlignment','center','VerticalAlignment','center','FontSize',30,'FontWeight','bold');
titleapimintpyplottrans.Layout.Row = [1 2];
titleapimintpyplottrans.Layout.Column = [1 5];

labeldatasetapimintpyplottrans = uilabel(glapimintpyplottrans,'Text','Dataset:','HorizontalAlignment','Left','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
labeldatasetapimintpyplottrans.Layout.Row = [3];
labeldatasetapimintpyplottrans.Layout.Column = [1 2];

labelsubdatasetapimintpyplottrans = uilabel(glapimintpyplottrans,'Text','Subdataset:','HorizontalAlignment','Right','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
labelsubdatasetapimintpyplottrans.Layout.Row = [3];
labelsubdatasetapimintpyplottrans.Layout.Column = [4 5];

datasetapimintpyplottrans = uilistbox(glapimintpyplottrans,'Multiselect','on','ValueChangedFcn', @(src,event) subdatasetupdate(src,event));
datasetapimintpyplottrans.Layout.Row = [4 5];
datasetapimintpyplottrans.Layout.Column = [1 2];

subdatasetapimintpyplottrans = uitextarea(glapimintpyplottrans);
subdatasetapimintpyplottrans.Layout.Row = [4 5];
subdatasetapimintpyplottrans.Layout.Column = [4 5];
subdatasetapimintpyplottrans.Tooltip = {'example:';...
    'plottrans.py velocity.h5';...
    'plottrans.py velocity.h5 velocity --wrap --wrap-range -2 2 -c cmy --lalo-label';...
    'plottrans.py velocity.h5 --ref-yx  210 566                              #change reference pixel for display';...
    'plottrans.py velocity.h5 --sub-lat 31.05 31.10 --sub-lon 130.05 130.10  #subset in lalo / yx';...
    '  ';...
    'plottrans.py timeseries.h5';...
    'plottrans.py timeseries.h5 -m no                   #do not use auto mask';...
    'plottrans.py timeseries.h5 --ref-date 20101120     #change reference date';...
    'plottrans.py timeseries.h5 --ex drop_date.txt      #exclude dates to plot';...
    'plottrans.py timeseries.h5 ''*2017*'' ''*2018*''       #all acquisitions in 2017 and 2018';...
    'plottrans.py timeseries.h5 20200616_20200908       #reconstruct interferogram on the fly';...
    '';...
    'plottrans.py ifgramStack.h5 coherence';...
    'plottrans.py ifgramStack.h5 unwrapPhase-           #unwrapPhase only in the presence of unwrapPhase_bridging';...
    'plottrans.py ifgramStack.h5 -n 6                   #the 6th slice';...
    'plottrans.py ifgramStack.h5 20171010_20171115      #all data      related with 20171010_20171115';...
    'plottrans.py ifgramStack.h5 ''coherence*20171010*''  #all coherence related with 20171010';...
    'plottrans.py ifgramStack.h5 unwrapPhase-20070927_20100217 --zero-mask --wrap     #wrapped phase';...
    'plottrans.py ifgramStack.h5 unwrapPhase-20070927_20100217 --mask ifgramStack.h5  #mask using connected components';...

    '# GPS (for one subplot in geo-coordinates only)';...
    'plottrans.py geo_velocity_msk.h5 velocity --show-gps --gps-label   #show locations of available GPS';...
    'plottrans.py geo_velocity_msk.h5 velocity --show-gps --gps-comp enu2los --ref-gps GV01';...
    'plottrans.py geo_timeseries_ERA5_ramp_demErr.h5 20180619 --ref-date 20141213 --show-gps --gps-comp enu2los --ref-gps GV01';...

    '# Save and Output';...
    'plottrans.py velocity.h5 --save';...
    'plottrans.py velocity.h5 --nodisplay';...
    'plottrans.py geo_velocity.h5 velocity --nowhitespace';...
    };
labeltableapimintpyplottrans = uilabel(glapimintpyplottrans,'Text','Selection of parameters:','HorizontalAlignment','Left','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
labeltableapimintpyplottrans.Layout.Row = [6];
labeltableapimintpyplottrans.Layout.Column = [1 5];

tableapimintpyplottrans = uitable(glapimintpyplottrans,'ColumnEditable',[false true false]);
tableapimintpyplottrans.Layout.Row = [6 19];
tableapimintpyplottrans.Layout.Column = [1 5];

buttonapimintpyplottrans = uibutton(glapimintpyplottrans,'Text','Run','ButtonPushedFcn', @(btn,event) run_api_plottrans(btn,event));
buttonapimintpyplottrans.Layout.Row = [20];
buttonapimintpyplottrans.Layout.Column = [1 5];

%% Initialisation of datasets

% Load the MintPy directory
fi = fopen([miesar_para.WK,'/mintpydirectory.log'],'r');
pathmintpyprocessing = textscan(fi,'%s'); fclose(fi); pathmintpyprocessing = pathmintpyprocessing{1}{1};

%% Check the possible datasets
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

%% Modification of dropdown
datasetapimintpyplottrans.Items = data_set;
datasetapimintpyplottrans.Value = data_set{end};

subdatasetupdate([],[])

% Create the parameter table
paratable = {'--noverbose','no','Disable the verbose message printing (default: True).';...
    '--vlim', '' ,'Display limits for matrix plotting.';...
    '--offset', '' ,'offset between transects [for multiple files only; default: [0.05] m]. number of input offsets should be: 1 - same (sequential) offset between adjacent transects OR num_file - different (cumulative) offset for each file, starting from 0.';...
    '--unit', '' ,'unit for display.  Its priority > wrap';...
    '--yx0', '' ,'Y0 X0 start point of the profile in pixel number [y, x]';...
    '--yx1', '' ,'Y1 X1 end point of the profile in pixel number [y, x]';...
    '--lalo0', '' ,'LAT0 LON0 start point of the profile in [lat, lon]';...
    '--lalo1', '' ,'LAT1 LON1 end point of the profile in [lat, lon]';...
    '--line-file', '' ,'LOLA_FILE file with start and end point info in lon lat, same as GMT format. GMT xy file, i.e. transect_lonlat.xy';...
    '--interpolation', '' ,'{nearest,bilinear,cubic} interpolation method while extacting profile along the line. Default: nearest.';...
    '--markersize', '' ,'Point marker size. Default: 2.0';...
    '--fontsize','','font size';...
    '--fontcolor','','font color (default: k).';...
    '--nowhitespace','no','do not display white space';...
    '--noaxis','no','do not display axis';...
    '--notick','no','do not display tick in x/y axis';...
    '--colormap','','colormap used for display, i.e. jet, cmy, RdBu, hsv, jet_r, temperature, viridis, etc. More at https://mintpy.readthedocs.io/en/latest/api/colormaps/';...
    '--cmap-lut','','number of increment of colormap lookup table (default: 256).';...
    '--cmap-vlist','','list of 3 float numbers, for truncated colormap only (default: [0.0, 0.7, 1.0]).';...
    '--nocolorbar','no','do not display colorbar';...
    '--cbar-nbins','','number of bins for colorbar.';...
    '--cbar-ext','','{both,max,None,min,neither} Extend setting of colorbar; based on data stat by default.';...
    '--cbar-label','','colorbar label colorbar location for single plot (default: right).';...
    '--cbar-size','','colorbar size and pad (default: 2%).';...
    '--notitle','no','do not display title';...
    '--title-in','no','draw title in/out of axes';...
    '--figtitle','',' Title shown in the figure.';...
    '--title4sentinel1','no','display Sentinel-1 A/B and IPF info in title.';...
    '--figsize','','figure size in inches - width and length';...
    '--dpi','','DPI - dot per inch - for display/write (default: 300).';...
    '--figext','','{.emf,.eps,.pdf,.png,.ps,.raw,.rgba,.svg,.svgz} File extension for figure output file (default: .png).';...
    '--fignum','','number of figure windows';...
    '--nrows','','subplot number in row';...
    '--ncols','','subplot number in column';...
    '--wspace','','width space between subplots in inches';...
    '--hspace','','height space between subplots in inches';...
    '--no-tight-layout','no','disable automatic tight layout for multiple subplots';...
    '--coord','','{radar,geo} Display in radar/geo coordination system (for geocoded file only; default: geo).';...
    '--animation','no','enable animation mode';...
    '-o','','[OUTFILE [OUTFILE ...]], --outfile [OUTFILE [OUTFILE ...]] save the figure with assigned filename. By default, it''s calculated based on the input file name.';...
    '--save','no','save the figure';...
    '--nodisplay','no','save and do not display the figure';...
    '--update','no','enable update mode for save figure: skip running if 1) output file already exists AND 2) output file is newer than input file.';...
    '--sub-x','','XMIN XMAX subset display in x/cross-track/range direction';...
    '--sub-y','','YMIN YMAX subset display in y/along-track/azimuth direction';...
    '--sub-lat','','LATMIN LATMAX subset display in latitude';...
    '--sub-lon','','LONMIN LONMAX subset display in longitude';...
    };

tableapimintpyplottrans.Data = cell2table(paratable,'VariableNames',{'Parameters' 'Value' 'Information'});

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Other functions (global)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Update the pathdataset (no used)
    function subdatasetupdate(src,event)
%         cur_value = datasetapimintpyplottrans.Value;
%         pref = '';
%         if isempty(strfind(cur_value,'geo'))==0 & strcmp(cur_value,'geometryRadar.h5')== 0
%             pref = 'geo/';
%         elseif strcmp(cur_value,'ifgramStack.h5')== 1 | strcmp(cur_value,'geometryRadar.h5')== 1
%             pref = 'inputs/';
%         else
%             pref = '';
%         end
%         pathdataset = [pathmintpyprocessing,'/',pref,cur_value];
    end

%% Run the application
    function run_api_plottrans(btn,event)
        cur_dataset = datasetapimintpyplottrans.Value;

        if  length(cur_dataset) > 1
            cur_subdataset = ''; 
        else
            cur_subdataset = subdatasetapimintpyplottrans.Value{1};
        end 
        
        pref = cell(1);
        for i1 = 1 : length(cur_dataset)
            if isempty(strfind(cur_dataset{i1},'geo'))==0
                pref{i1} = 'geo/';
            else
                pref{i1} = '';
            end
        end

        % Check the parameters
        paratablecheck = table2cell(tableapimintpyplottrans.Data);
        cmd = ['plot_transection.py '];
        for i1 = 1 : length(cur_dataset)
            cmd = [cmd, ' ',pref{i1},cur_dataset{i1}];
        end
        for i1 = 1 : size(paratablecheck)
            if isempty(paratablecheck{i1,2}) == 0 & strcmp(paratablecheck{i1,2},'no') == 0
                if strcmp(paratablecheck{i1,2},'yes') == 1
                    cmd = [cmd,' ',paratablecheck{i1,1}];
                else
                    cmd = [cmd,' ',paratablecheck{i1,1},' ',paratablecheck{i1,2}];
                end
            end
        end

        % Write the command
        scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];
        fid = fopen(scripttoeval,'w');
        fprintf(fid,'cd %s\n',[pathmintpyprocessing]);
        fprintf(fid,'%s > plottrans.log &\n',cmd);
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
