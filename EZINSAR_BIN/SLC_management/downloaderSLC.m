function downloaderSLC(miesar_para)
%   downloaderSLC(miesar_para)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to download the SLCs via a GUI.
%
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also createlistSLC, GUIpathdirectory, displayextensionS1, initparmslc, readxmlannotationS1, displayextensionTSXPAZ, manageparamaterSLC, downloaderSLC, manageSLC.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.0.0 Beta
%   Date: 16/02/2022
%
%   -------------------------------------------------------
%   Modified:
%           - Alexis Hrysiewicz, UCD / iCRAG, 07/07/2022: StripMap
%           implementation
%           - Alexis Hrysiewicz, UCD / iCRAG, 18/07/2022: modification of
%           text information
%           - Alexis Hrysiewicz, UCD / iCRAG, 22/11/2023: API to download
%           the orbit files
%           - Alexis Hrysiewicz, UCD / iCRAG, 29/02/2024: API to download
%           the orbit files from Copernicus
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)
%           2.0.0 Beta: Initial (unreleased)
%           2.2.0 Beta: Initial (unreleased)
%           2.2.2 Beta: Initial (unreleased)

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
    update_textinformation([],[],[],si,'error');
    error('The SLC list is not present.');
end

%% Open the figure
figapidownloader = uifigure('Position',[300 100 1200 900],'Name','Sentinel-1 SLC Downloader');
glapidownloader = uigridlayout(figapidownloader,[20 5]);

titleapidownloader = uilabel(glapidownloader,'Text','Sentinel-1 SLC Downloader','HorizontalAlignment','center','VerticalAlignment','center','FontSize',30,'FontWeight','bold');
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
btdownloadapidownloader.Layout.Row = [16];
btdownloadapidownloader.Layout.Column = [5];

% btdownloadapidownloaderorbitsASF = uibutton(glapidownloader,'Text','Download orbit files from ASF server (based on the downloaded files)','WordWrap','on','ButtonPushedFcn', @(btn,event) download_orbit_ASF(btn,event));
% btdownloadapidownloaderorbitsASF.Layout.Row = [17 18];
% btdownloadapidownloaderorbitsASF.Layout.Column = [5];

btdownloadapidownloaderorbitsCopernicus = uibutton(glapidownloader,'Text','Download orbit files from Copernicus server (based on the downloaded files)','WordWrap','on','ButtonPushedFcn', @(btn,event) download_orbit_Coper(btn,event));
btdownloadapidownloaderorbitsCopernicus.Layout.Row = [19 20];
btdownloadapidownloaderorbitsCopernicus.Layout.Column = [5];

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

    % function download_orbit_ASF(btn,event)
    % 
    %     if exist([miesar_para.WK,'/tmp_list_orbits_download.txt'])
    %         delete([miesar_para.WK,'/tmp_list_orbits_download.txt'])
    %     end
    % 
    %     wo = weboptions;
    %     wo.Timeout = 60;
    % 
    %     % Parse 1
    %     w1 = waitbar(0,'Please wait for the downloading of precise-orbit list...');
    %     url_precise = 'https://s1qc.asf.alaska.edu/aux_poeorb/';
    %     response_precise = webread(url_precise,wo);
    % 
    %     link_precise = cell(1);
    %     date1_precise = [];
    %     date2_precise = [];
    %     datep_precise = [];
    %     sat_precise = [];
    % 
    %     h = 1;
    %     tmp1 = strsplit(response_precise,'\n');
    %     for i1 = 1 : length(tmp1)
    %         tmp2 = strsplit(tmp1{i1},' ');
    %         try
    %             tmp3 = split(tmp2{2},'"');
    % 
    %             if strcmp(tmp3{1},'href=')
    %                 tmp4 = split(tmp3{2},'"');
    %                 tmp5 = tmp4{1};
    % 
    %                 link_precise{h} = [url_precise,tmp5];
    %                 tmp6 = strsplit(tmp5,'_');
    % 
    %                 datep_precise = [datep_precise; datetime(tmp6{6},'InputFormat','yyyyMMdd''T''HHmmss')];
    %                 date1_precise = [date1_precise; datetime(strrep(tmp6{7},'V',''),'InputFormat','yyyyMMdd''T''HHmmss')];
    % 
    %                 tmp7 = strsplit(tmp6{8},'.');
    %                 date2_precise = [date2_precise; datetime(tmp7{1},'InputFormat','yyyyMMdd''T''HHmmss')];
    % 
    %                 if strcmp(tmp6{1},'S1A')
    %                     sat_precise = [sat_precise; 1];
    %                 elseif strcmp(tmp6{1},'S1B')
    %                     sat_precise = [sat_precise; 2];
    %                 end
    %                 h = h + 1;
    %             end
    %         end
    %         if fix(i1./1000) == i1./1000
    %             waitbar(i1./length(tmp1),w1);
    %         end
    %     end
    %     close(w1);
    % 
    %     % Parse 2
    %     w1 = waitbar(0,'Please wait for the downloading of restitued-orbit list...');
    % 
    %     url_restitued = 'https://s1qc.asf.alaska.edu/aux_resorb/';
    %     response_restitued = webread(url_restitued,wo);
    % 
    %     link_restitued = cell(1);
    %     date1_restitued = [];
    %     date2_restitued = [];
    %     datep_restitued = [];
    %     sat_restitued = [];
    % 
    %     h = 1;
    %     tmp1 = strsplit(response_restitued,'\n');
    %     for i1 = 1 : length(tmp1)
    %         tmp2 = strsplit(tmp1{i1},' ');
    %         try
    %             tmp3 = split(tmp2{2},'"');
    % 
    %             if strcmp(tmp3{1},'href=')
    %                 tmp4 = split(tmp3{2},'"');
    %                 tmp5 = tmp4{1};
    % 
    %                 link_restitued{h} = [url_restitued,tmp5];
    %                 tmp6 = strsplit(tmp5,'_');
    % 
    %                 datep_restitued = [datep_restitued; datetime(tmp6{6},'InputFormat','yyyyMMdd''T''HHmmss')];
    %                 date1_restitued = [date1_restitued; datetime(strrep(tmp6{7},'V',''),'InputFormat','yyyyMMdd''T''HHmmss')];
    % 
    %                 tmp7 = strsplit(tmp6{8},'.');
    %                 date2_restitued = [date2_restitued; datetime(tmp7{1},'InputFormat','yyyyMMdd''T''HHmmss')];
    % 
    %                 if strcmp(tmp6{1},'S1A')
    %                     sat_restitued = [sat_restitued; 1];
    %                 elseif strcmp(tmp6{1},'S1B')
    %                     sat_restitued = [sat_restitued; 2];
    %                 end
    %                 h = h + 1;
    %             end
    %         end
    %         if fix(i1./1000) == i1./1000
    %             waitbar(i1./length(tmp1),w1);
    %         end
    %     end
    %     close(w1);
    % 
    %     % Read the list of SLCs (based on the available files)
    %     list_SLC = dir(paramslc.pathSLC);
    % 
    %     data1_SLC = [];
    %     data2_SLC = [];
    %     sat_SLC = [];
    % 
    %     for i1 = 1 : length(list_SLC)
    %         if isempty(strfind(list_SLC(i1).name,'.zip')) == 0
    %             tmp1 = strsplit(list_SLC(i1).name,'_');
    % 
    %             data1_SLC = [data1_SLC; datetime(tmp1{5},'InputFormat','yyyyMMdd''T''HHmmss')];
    %             data2_SLC = [data2_SLC; datetime(tmp1{6},'InputFormat','yyyyMMdd''T''HHmmss')];
    % 
    %             if strcmp(tmp1{1},'S1A')
    %                 sat_SLC = [sat_SLC; 1];
    %             elseif strcmp(tmp1{1},'S1B')
    %                 sat_SLC = [sat_SLC; 2];
    %             end
    %         end
    %     end
    % 
    %     if isempty(data1_SLC) == 1
    %         error('No .zip files');
    %     end
    % 
    %     % Check the orbit files for the SLCs
    %     orbit_required = cell(1);
    %     for i1 = 1 : length(data1_SLC)
    %         idxp = find((data1_SLC(i1) > date1_precise) & (data2_SLC(i1) < date2_precise) & (sat_SLC(i1) == sat_precise));
    %         if isempty(idxp) == 0
    %             orbit_required{i1} = link_precise{idxp(end)};
    %         else
    %             idxr = find((data1_SLC(i1) > date1_restitued) & (data2_SLC(i1) < date2_restitued) & (sat_SLC(i1) == sat_restitued));
    %             if isempty(idxr) == 0
    %                 orbit_required{i1} = link_restitued{idxr(end)};
    %             else
    %                 error(sprintf('No orbit file found for the date %s',data1_SLC(i1)));
    %             end
    %         end
    %     end
    %     orbit_required = unique(orbit_required);
    % 
    %     % Write the tmp file
    %     w1 = waitbar(0.5,'Download the orbit files...');
    %     waitbar(0.5,w1)
    % 
    %     fi = fopen('tmp_list_orbits_download.txt','w');
    %     for i1 = 1 : length(orbit_required)
    %         fprintf(fi,'%s\n',orbit_required{i1});
    %     end
    %     fclose(fi);
    %     close(w1);
    % 
    %     % Download the orbits
    %     [configpath] = readpathinformation([miesar_para.cur,'pathinformation.txt']);
    %     cmd1 = sprintf('wget --user %s --password %s -P %s -i %s',configpath.ASFID,configpath.ASFPWD,paramslc.pathorbit,'tmp_list_orbits_download.txt');
    %     system(cmd1);
    % 
    %     if exist([miesar_para.WK,'/tmp_list_orbits_download.txt'])
    %         delete([miesar_para.WK,'/tmp_list_orbits_download.txt'])
    %     end
    % 
    %     % Move the files
    %     listorbits = dir(paramslc.pathorbit);
    %     for i1 = 1 : length(listorbits)
    %         if isempty(strfind(listorbits(i1).name,'.EOF')) == 0
    %             tmp1 = strsplit(listorbits(i1).name,'_');
    %             di = strsplit(strrep(tmp1{end},'.EOF',''),'T');
    %             di = di{1};
    % 
    %             if exist([paramslc.pathorbit,'/',di]) == 0
    %                 mkdir([paramslc.pathorbit,'/',di])
    %             end
    % 
    %             movefile([paramslc.pathorbit,'/',listorbits(i1).name,],[paramslc.pathorbit,'/',di,'/',listorbits(i1).name,]);
    %         end
    %     end
    %     w1 = msgbox("Orbit files downloaded");
    % 
    % end

    function download_orbit_Coper(btn,event)
        % Some requirements 
        query_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products";
        download_url = "https://zipper.dataspace.copernicus.eu/odata/v1/Products";

        T0 = 12 * 86400.0 / 175.0 + 60;
        T1 = 60;
        
        % Check the SLC files already downloaded
        mode_stored = 0;
        for i1 = 1 : length(list{1})
            tmp = strsplit(list{1}{i1},'/');
            if exist([paramslc.pathSLC,'/',tmp{end},'.zip']) == 2 | exist([paramslc.pathSLC,'/',tmp{end},'.SAFE']) == 2
                mode_stored = 1;
            end 
        end 
        
        file_rqd_orbit = cell(1,1);
        h = 1;
        for i1 = 1 : length(list{1})
            tmp = strsplit(list{1}{i1},'/');
            if (mode_stored == 0) | (exist([paramslc.pathSLC,'/',tmp{end},'.zip']) == 2 | exist([paramslc.pathSLC,'/',tmp{end},'.SAFE']) == 2)
                file_rqd_orbit{h,1} = tmp{end};
                file_rqd_orbit{h,2} = datetime(list{2}{i1}); 

                if isempty(strfind(tmp{end},'S1A')) == 0
                    file_rqd_orbit{h,3} = 'S1A';
                else
                    file_rqd_orbit{h,3} = 'S1B';
                end 
                h = h + 1;
            end 
        end  

        % Detection of the orbit files
        w1 = waitbar(0,'Detection of the orbit files:...');
        w1.Resize = 'on';

        orbitsfile = cell(1,1); 
        for i1 = 1 : size(file_rqd_orbit,1)

            waitbar(i1/size(file_rqd_orbit,1),w1,sprintf('For %s: ...',file_rqd_orbit{i1,2}))
        
            % Search option
            date1_research_str = [datestr(file_rqd_orbit{i1,2}(1) - seconds(T0),'yyyy-mm-ddTHH:MM:SS'),'.000Z']; 
            date2_research_str = [datestr(file_rqd_orbit{i1,2}(1) + seconds(T1),'yyyy-mm-ddTHH:MM:SS'),'.000Z']; 
            options = weboptions("ContentType", "auto","Timeout",42,"RequestMethod",'get');

            
            urlpeo = ["https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=startswith(Name,'",file_rqd_orbit{i1,3},"') and contains(Name,'AUX_POEORB') and ContentDate/Start lt ",date1_research_str," and ContentDate/End gt ",date2_research_str];
            urlreo = ["https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=startswith(Name,'",file_rqd_orbit{i1,3},"') and contains(Name,'AUX_RESORB') and ContentDate/Start lt ",date1_research_str," and ContentDate/End gt ",date2_research_str];
            response = webread(join(urlpeo,''),options);
            
            try 
                % Check precise orbit files (considering that the wrong POEORB files are
                % not available on this server)
                orbitsfile{i1,1} = join([download_url,"(",response.value(1).Id,")/$value"],'');
                orbitsfile{i1,2} = response.value(1).Name; 
                orbitsfile{i1,3} = datestr(file_rqd_orbit{i1,2},'yyyymmdd');
                waitbar(i1/size(file_rqd_orbit,1),w1,sprintf('For %s: POEORB file found',file_rqd_orbit{i1,2}))
            catch
                % Check restitued orbit files
                response = webread(join(urlreo,''),options);
                orbitsfile{i1,1} = join([download_url,"(",response.value(1).Id,")/$value"],'');
                orbitsfile{i1,2} = response.value(1).Name;
                orbitsfile{i1,3} = datestr(file_rqd_orbit{i1,2},'yyyymmdd');
                waitbar(i1/size(file_rqd_orbit,1),w1,sprintf('For %s: RESORB file found',file_rqd_orbit{i1,2}))
            end 
        end 

        close(w1)

        prompt = {'Username:','Password:'};
        dlgtitle = 'Copernicus Server';
        fieldsize = [1 45; 1 45];
        definput = {'Your username (email)','Your password'};
        answer = inputdlg(prompt,dlgtitle,fieldsize,definput);
                    
        % Retrieval of use token
        request = ["curl -d 'client_id=cdse-public' -d 'username=",answer{1},"' -d 'password=''",answer{2},"''' -d 'grant_type=password' 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token' | python3 -m json.tool | grep 'access_token' | awk -F\"" '{print $4}'"];
        [a,b] = system(join(request,''));
        b = strsplit(b,'\n'); 
        usertoken = b{end-1}; 

        % Download the orbit
        w1 = waitbar(0,'Download the orbit files');
        w1.Resize = 'on';

        for i1 = 1 : size(orbitsfile,1)
            pathorbitfile = [paramslc.pathorbit,'/',orbitsfile{i1,2}];
            urlorbit = orbitsfile{i1,1};    

            if exist(pathorbitfile) == 0
                check_file = 0;
                while check_file == 0
                    [a,b] = system(join(['curl -H "Authorization: Bearer ',usertoken,'" ''',urlorbit,''' --location-trusted --output ',pathorbitfile,'.tmp'],''))
                    s = dir([pathorbitfile,'.tmp']); 
                    if (isempty(strfind(pathorbitfile,'POEORB')) == 0 & s.bytes < 1e6) | (isempty(strfind(pathorbitfile,'RESORB')) == 0 & s.bytes < 2e5)
                        % Update the token 
                        request = ["curl -d 'client_id=cdse-public' -d 'username=",answer{1},"' -d 'password=''",answer{2},"''' -d 'grant_type=password' 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token' | python3 -m json.tool | grep 'access_token' | awk -F\"" '{print $4}'"];
                        [a,b] = system(join(request,''));
                        b = strsplit(b,'\n'); 
                        usertoken = b{end-1}; 
                    else
                        check_file = 1;
                    end
                end         
                movefile([pathorbitfile,'.tmp'],pathorbitfile)
            end 

            waitbar(i1./size(orbitsfile,1),w1,'Download the orbit files');
        end 
        close(w1)
  
        % Move the files
        for i1 = 1 : length(orbitsfile)
            if exist([paramslc.pathorbit,'/',orbitsfile{i1,3}]) == 0
                mkdir([paramslc.pathorbit,'/',orbitsfile{i1,3}])
            end
            try
                movefile([paramslc.pathorbit,'/',orbitsfile{i1,2}],[paramslc.pathorbit,'/',orbitsfile{i1,3},'/',orbitsfile{i1,2}]);
            end 
        end
        w1 = msgbox("Orbit files downloaded");

    end 
end
