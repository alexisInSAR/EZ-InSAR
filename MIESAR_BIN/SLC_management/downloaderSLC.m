function downloaderSLC(miesar_para)
%   downloaderSLC(miesar_para)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to download the SLCs via a GUI. 
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also manageparamaterSLC, initparmslc, readxmlannotationS1, downloaderSLC.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 16/02/2022
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)


%% Initialisation of variables

% Open the variables

% For the SLC parameters
paramslc = load([miesar_para.WK,'/parmsSLC.mat']);

% For the SLC list (check if this file is okay)
if exist([miesar_para.WK,'/SLC.list'])
    fid = fopen([miesar_para.WK,'/SLC.list'],'r');
    list = textscan(fid,['%s %s %s %s %s %s %s %s']); fclose(fid);
else
    si = ['The SLC list is not present.'];
    set(findobj(gcf,'Tag','maintextoutput'),'String',si);
    set(findobj(gcf,'Tag','maintextoutput'),'ForegroundColor','red');
    error('The SLC list is not present.');
end

%% Open the figure
figapidownloader = uifigure('Position',[300 100 1200 900],'Name','Sentinel-1 IW Downloader');
glapidownloader = uigridlayout(figapidownloader,[20 5]);

titleapidownloader = uilabel(glapidownloader,'Text','Sentinel-1 IW Downloader','HorizontalAlignment','center','VerticalAlignment','center','FontSize',30,'FontWeight','bold');
titleapidownloader.Layout.Row = 1;
titleapidownloader.Layout.Column = [1 5];

labeltableapidownloader = uilabel(glapidownloader,'Text','List of acquisitions:','HorizontalAlignment','Left','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
labeltableapidownloader.Layout.Row = [2];
labeltableapidownloader.Layout.Column = [1 4];

SLCapimintpytsview = uilistbox(glapidownloader,'Multiselect','on','ValueChangedFcn',@(src,event) updategaugetarget(0,1));
SLCapimintpytsview.Layout.Row = [3 18];
SLCapimintpytsview.Layout.Column = [1 4];

labelwaitbarapidownloader = uilabel(glapidownloader,'Text','Percentage of downloaded SLCs:','HorizontalAlignment','Left','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
labelwaitbarapidownloader.Layout.Row = [19];
labelwaitbarapidownloader.Layout.Column = [1 4];

lgapidownloader  = uigauge(glapidownloader,'linear');
lgapidownloader.Layout.Row = [20];
lgapidownloader.Layout.Column = [1 4];

btselectallapidownloader = uibutton(glapidownloader,'Text','Select all','ButtonPushedFcn', @(btn,event) run_select_all(btn,event));
btselectallapidownloader.Layout.Row = [3];
btselectallapidownloader.Layout.Column = [5];

btdeselectallapidownloader = uibutton(glapidownloader,'Text','Deselect all','ButtonPushedFcn', @(btn,event) run_deselect_all(btn,event));
btdeselectallapidownloader.Layout.Row = [4];
btdeselectallapidownloader.Layout.Column = [5];

safemodeapidownloader = uicheckbox(glapidownloader,'Text','Safe Mode','Value',1);
safemodeapidownloader.Layout.Row = [5];
safemodeapidownloader.Layout.Column = [5];

labelsqbarapidownloader = uilabel(glapidownloader,'Text','Sequential selection: (6-day modulus)','HorizontalAlignment','Left','VerticalAlignment','center','FontSize',15,'FontWeight','bold');
labelsqbarapidownloader.Layout.Row = [6];
labelsqbarapidownloader.Layout.Column = [5];

sqbarapidownloader = uispinner(glapidownloader,'Limits', [1 inf],'Value', 1,'ValueChangedFcn',@(src,event) sequential_select(src,event));
sqbarapidownloader.Layout.Row = [7];
sqbarapidownloader.Layout.Column = [5];

btsaveselectionapidownloader = uibutton(glapidownloader,'Text','Save selection','ButtonPushedFcn', @(btn,event) save_selection(btn,event));
btsaveselectionapidownloader.Layout.Row = [12];
btsaveselectionapidownloader.Layout.Column = [5];

btloadselectionapidownloader = uibutton(glapidownloader,'Text','Load selection','ButtonPushedFcn', @(btn,event) load_selection(btn,event));
btloadselectionapidownloader.Layout.Row = [13];
btloadselectionapidownloader.Layout.Column = [5];

btdownloadapidownloader = uibutton(glapidownloader,'Text','Download','ButtonPushedFcn', @(btn,event) download_selection(btn,event));
btdownloadapidownloader.Layout.Row = [20];
btdownloadapidownloader.Layout.Column = [5];

%% Create the SLC date list
rescell = cell(1);
hdw = 0;
for i1 = 1 : length(list{1})
    if exist([paramslc.pathSLC,'/',list{1}{i1},'.zip']) == 2 | exist([paramslc.pathSLC,'/',list{1}{i1},'.SAFE']) == 2
        rescell{i1} = [list{2}{i1},' ',list{1}{i1},' (Downloaded)'];
        hdw = hdw + 1;
    else
        rescell{i1} = [list{2}{i1},' ',list{1}{i1}];
    end
end
SLCapimintpytsview.Items = rescell;
dateslc = [];
for i1 = 1 : length(SLCapimintpytsview.Items)
    dateslc(i1,1) = datenum(SLCapimintpytsview.Items{i1}(1:10));
end

%% Update the displayed list
updatelist([],[]);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Other functions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    function save_selection(btn,event)
        savedselection = SLCapimintpytsview.Value;
        save([miesar_para.WK,'/savedselectionSLC.mat'],'savedselection');
    end

    function load_selection(btn,event)
        if exist([miesar_para.WK,'/savedselectionSLC.mat'])
            res = load([miesar_para.WK,'/savedselectionSLC.mat']);
            SLCapimintpytsview.Value = res.savedselection;
        end
    end

    function download_selection(btn,event)
        [configpath] = readpathinformation([miesar_para.cur,'pathinformation.txt']);
        paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
        for i1 = 1 : length(SLCapimintpytsview.Items)
            IndexC = strfind(SLCapimintpytsview.Value,SLCapimintpytsview.Items{i1});
            Index = find(not(cellfun('isempty',IndexC)));
            if isempty(Index) == 0
                urllast = list{8}{i1};
                cmd1 = sprintf('wget -c --http-user=%s --http-password=%s "%s" -P %s',configpath.ASFID,configpath.ASFPWD,urllast,paramslc.pathSLC);
                system(cmd1);
                updatelist([],[]);
                drawnow; pause(1);
            end
            
        end
    end

    function sequential_select(src,event)
        if sqbarapidownloader.Value == 1
            run_select_all([],[]);
        else
            
            dateslci = unique(dateslc);
            %             dt = gradient(dateslci);
            %
            %             block = cell(1);
            %             ni = find(dt>sqbarapidownloader.Value.*6);
            %             if isempty(ni) == 1
            %                 block{1} = dateslci;
            %             elseif  length(ni) == 1
            %                 block{1} = dateslci(1:ni);
            %                 block{2} = dateslci(ni+1:end);
            %             else
            %                 for i1 = 1 : length(ni)-1
            %                     if i1 == 1
            %                     block{i1} = dateslci(1:ni(i1));
            %                     elseif i1 == ni(end)
            %                       block{i1} = dateslci(ni(i1)+1:end);
            %                     else
            %                       block{i1} = dateslci(ni(i1-1)+1:ni(i1)+1);
            %                     end
            %                 end
            %             end
            
            % No optimised
            over = sqbarapidownloader.Value.*6;
            wanted_unique_dates = [min(dateslci):over:max(dateslci)];
            index_slc = [];
            for i1 = 1 : length(wanted_unique_dates)
                n = find(wanted_unique_dates(i1)==dateslc);
                if isempty(n)==0
                    index_slc = [index_slc; n];
                end
            end
            SLCapimintpytsview.Value = SLCapimintpytsview.Items(index_slc);
        end
        updategaugetarget([],[])
    end

    function run_select_all(btn,event)
        SLCapimintpytsview.Value = SLCapimintpytsview.Items;
        check_unique_dates
        updategaugetarget([],[])
    end

    function run_deselect_all(btn,event)
        SLCapimintpytsview.Value = SLCapimintpytsview.Items{1};
        check_unique_dates
        updategaugetarget([],[])
    end

    function check_unique_dates
        if safemodeapidownloader.Value == 1
            res = [];
            for i1 = 1 : length(SLCapimintpytsview.Value)
                res(i1,1) = datenum(SLCapimintpytsview.Value{i1}(1:10));
            end
            res = unique(res);
            
            resbis = cell(1);
            h = 1;
            for i1 = 1 : length(dateslc)
                di = dateslc(i1);
                if isempty(find(di == res)) == 0
                    resbis{h} = SLCapimintpytsview.Items{i1};
                    h = h + 1;
                end
            end
            SLCapimintpytsview.Value = resbis;
        end
        updategaugetarget([],[])
    end

    function updategaugetarget(src,event)
        lgapidownloader.MajorTicks = sort([0 20 40 60 80 100 100.*length(SLCapimintpytsview.Value)./length(SLCapimintpytsview.Items)]);
        ni = find(lgapidownloader.MajorTicks == 100.*length(SLCapimintpytsview.Value)./length(SLCapimintpytsview.Items));
        lgapidownloader.MajorTickLabels = {'' '' '' '' '' '' ''};
        lgapidownloader.MajorTickLabels{1} = '0';
        lgapidownloader.MajorTickLabels{end} = '100';
        lgapidownloader.MajorTickLabels{ni} = num2str(100.*length(SLCapimintpytsview.Value)./length(SLCapimintpytsview.Items));
        if event == 1
            check_unique_dates; 
        end 
        
    end

    function updatelist(src,event)
        rescell = cell(1);
        hdw = 0;
        for i1 = 1 : length(list{1})
            if exist([paramslc.pathSLC,'/',list{1}{i1},'.zip']) == 2 | exist([paramslc.pathSLC,'/',list{1}{i1},'.SAFE']) == 2
                rescell{i1} = [list{2}{i1},' ',list{1}{i1},' (Downloaded)'];
                hdw = hdw + 1;
            else
                rescell{i1} = [list{2}{i1},' ',list{1}{i1}];
            end
        end
        SLCapimintpytsview.Items = rescell;
        lgapidownloader.Value = hdw./length(list{1});
        updategaugetarget(src,event)
    end
end
