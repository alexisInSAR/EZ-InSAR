function displayextensionS1(src,evt,action,miesar_para)
%   displayextensionS1(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to plot the extension of Sentinel-1 data
%
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also createlistSLC, GUIpathdirectory, displayextensionS1, initparmslc, readxmlannotationS1, displayextensionTSXPAZ, manageparamaterSLC, downloaderSLC, manageSLC.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.0.0 Alpha
%   Date: 07/07/2022
%
%   -------------------------------------------------------
%   Version history:
%           2.0.0 Alpha: Initial (unreleased)

% Open the variables
paramslc = load([miesar_para.WK,'/parmsSLC.mat']); fid = fopen([miesar_para.WK,'/SLC.list'],'r');
list = textscan(fid,['%s %s %s %s %s %s %s %s']); fclose(fid); testslc = 0;

% Check if we have a downloaded SLC
for i1 = 1 : length(list{1})
    if exist([paramslc.pathSLC,'/',list{1}{i1},'.zip']) == 2 | exist([paramslc.pathSLC,'/',list{1}{i1},'.SAFE']) == 7
        testslc = testslc + 1;
    end
end

% Read and display the burst coordinates
if testslc > 0
    set(findobj(gcf,'Tag','name_progressbar'),'Text','Read the Sentinel-1 extensions based on the .xml...'); drawnow; pause(0.01);

    % We have downloaded SLC(s)
    % Preparation of variables
    switch action
        case 'S1_IW'
            burst_extension = struct('Date','','IW1',[],'IW2',[],'IW3',[]);
        case 'S1_SM'
            burst_extension = struct('Date','','Ext',[]);
    end

    for i1 = 1 : length(list{1})
        update_progressbar_MIESAR(i1./length(list{1}),findobj(gcf,'Tag','progressbar'),miesar_para,'defaut') ;
        if exist([paramslc.pathSLC,'/',list{1}{i1},'.zip']) == 2 & exist([paramslc.pathSLC,'/',list{1}{i1},'.SAFE']) == 0
            % We need to unzip
            update_progressbar_MIESAR(i1./length(list{1}),findobj(gcf,'Tag','progressbar'),miesar_para,'defaut'); drawnow; pause(0.01);
            [a,b] = system(['unzip -l ',paramslc.pathSLC,'/',list{1}{i1},'.zip ']);
            c = strsplit(b,'\n');
            index_xml = find(contains(c, '.SAFE/annotation/s1') & contains(c, 'vv') & contains(c, '.xml'));

            % Read the .xml
            for i2 = 1 : length(index_xml)
                pathzipi = c{index_xml(i2)}; pathzipi = strsplit(pathzipi,' '); pathzipi = pathzipi{end};

                [a,b] = system(['unzip ',paramslc.pathSLC,'/',list{1}{i1},'.zip ',pathzipi,' -d ',miesar_para.WK,'/tmp_annotation_slc_burst']);

                di = strsplit(list{2}{i1},'.');
                burst_extension(i1).Date = datetime(di{1},'InputFormat','yyyy-MM-dd''T''HH:mm:ss');
                switch action
                    case 'S1_IW'
                        [burst_coordinates, nb_burst] = readxmlannotationS1([miesar_para.WK,'/tmp_annotation_slc_burst/',pathzipi],'S1_IW');
                        % Save the coordinates
                        if contains(pathzipi,'iw1') == 1
                            burst_extension(i1).IW1.nb_burst = nb_burst;
                            burst_extension(i1).IW1.burst_coordinates = burst_coordinates;
                        elseif contains(pathzipi,'iw2') == 1
                            burst_extension(i1).IW2.nb_burst = nb_burst;
                            burst_extension(i1).IW2.burst_coordinates = burst_coordinates;
                        elseif contains(pathzipi,'iw3') == 1
                            burst_extension(i1).IW3.nb_burst = nb_burst;
                            burst_extension(i1).IW3.burst_coordinates = burst_coordinates;
                        end
                    case 'S1_SM'
                        [burst_coordinates, nb_burst] = readxmlannotationS1([miesar_para.WK,'/tmp_annotation_slc_burst/',pathzipi],'S1_SM');
                        burst_extension(i1).Ext.nb_burst = nb_burst;
                        burst_extension(i1).Ext.burst_coordinates = burst_coordinates;

                end

                system(['rm -r ',miesar_para.WK,'/tmp_annotation_slc_burst']);
            end

        elseif exist([paramslc.pathSLC,'/',list{1}{i1},'.SAFE']) == 7
            update_progressbar_MIESAR(i1./length(list{1}),findobj(gcf,'Tag','progressbar'),miesar_para,'defaut'); drawnow; pause(0.01);
            list_xml = dir([paramslc.pathSLC,'/',list{1}{i1},'.SAFE/annotation/']);

            % We read the .xml
            for i2 = 1 : length(list_xml)
                if contains(list_xml(i2).name,'s1') & contains(list_xml(i2).name,'vv') & contains(list_xml(i2).name,'.xml')
                    pathzipi = list_xml(i2).name;

                    di = strsplit(list{2}{i1},'.');
                    burst_extension(i1).Date = datetime(di{1},'InputFormat','yyyy-MM-dd''T''HH:mm:ss');
                    switch action
                        case 'S1_IW'
                            [burst_coordinates, nb_burst] = readxmlannotationS1([paramslc.pathSLC,'/',list{1}{i1},'.SAFE/annotation/',pathzipi],'S1_IW');
                            % Save the coordinates
                            if contains(pathzipi,'iw1') == 1
                                burst_extension(i1).IW1.nb_burst = nb_burst;
                                burst_extension(i1).IW1.burst_coordinates = burst_coordinates;
                            elseif contains(pathzipi,'iw2') == 1
                                burst_extension(i1).IW2.nb_burst = nb_burst;
                                burst_extension(i1).IW2.burst_coordinates = burst_coordinates;
                            elseif contains(pathzipi,'iw3') == 1
                                burst_extension(i1).IW3.nb_burst = nb_burst;
                                burst_extension(i1).IW3.burst_coordinates = burst_coordinates;
                            end
                        case 'S1_SM'
                            [burst_coordinates, nb_burst] = readxmlannotationS1([miesar_para.WK,'/tmp_annotation_slc_burst/',pathzipi],'S1_SM');

                            burst_extension(i1).Ext.nb_burst = nb_burst;
                            burst_extension(i1).Ext.burst_coordinates = burst_coordinates;

                    end
                end
            end
        end
    end

    % Computation of colorscale based on the full set of dates
    dateslc = [];
    for i1 = 1 : length(burst_extension)
        di = strsplit(list{2}{i1},'.');
        dateslc = [dateslc; datetime(di{1},'InputFormat','yyyy-MM-dd''T''HH:mm:ss')];
    end

    if length(dateslc) == 1
        colori = 'black' ;
    else
        ci = jet;
        dateslcnorm = (datenum(dateslc) - min(datenum(dateslc)))./( max(datenum(dateslc)) - min(datenum(dateslc)));
        colori(:,1) = interp1(linspace(0,1,size(ci,1)),ci(:,1),dateslcnorm,'linear');
        colori(:,2) = interp1(linspace(0,1,size(ci,1)),ci(:,2),dateslcnorm,'linear');
        colori(:,3) = interp1(linspace(0,1,size(ci,1)),ci(:,3),dateslcnorm,'linear');
    end

    % And we can display opening a new figure
    set(findobj(gcf,'Tag','name_progressbar'),'Text','Display the SLC coverage...'); drawnow; pause(0.01);
    axmain = gcf;
    axiprogress = findobj(gcf,'Tag','progressbar');
    fig_ext_burst = figure('name','Coverage of SLCs','numbertitle','off'); fig_ext_burst.OuterPosition = [200 100 1080 700];

    if contains(struct2array(ver), 'Mapping Toolbox')
        gxi = geoaxes;
    else
        gxi = axes;
    end

    switch action
        case 'S1_IW'
            box_burst.IW1=[];  box_burst.IW2=[]; box_burst.IW3=[];

            for i1 = 1 : length(burst_extension)
                if isempty(burst_extension(i1).Date) == 0

                    for j1 = 1 : burst_extension(i1).IW1.nb_burst
                        box_burst.IW1.lat{i1,j1}=[min(burst_extension(i1).IW1.burst_coordinates(j1).latitude),max(burst_extension(i1).IW1.burst_coordinates(j1).latitude)];
                        box_burst.IW1.lon{i1,j1}=[min(burst_extension(i1).IW1.burst_coordinates(j1).longitude),max(burst_extension(i1).IW1.burst_coordinates(j1).longitude)];
                        hold(gxi,'on')
                        geoplot(gxi,burst_extension(i1).IW1.burst_coordinates(j1).latitude,burst_extension(i1).IW1.burst_coordinates(j1).longitude,'-','Color',colori(i1,:)); hold(gxi,'on')
                    end
                    for j1 = 1 : burst_extension(i1).IW2.nb_burst
                        box_burst.IW2.lat{i1,j1}=[min(burst_extension(i1).IW2.burst_coordinates(j1).latitude),max(burst_extension(i1).IW2.burst_coordinates(j1).latitude)];
                        box_burst.IW2.lon{i1,j1}=[min(burst_extension(i1).IW2.burst_coordinates(j1).longitude),max(burst_extension(i1).IW2.burst_coordinates(j1).longitude)];
                        hold(gxi,'on')
                        geoplot(gxi,burst_extension(i1).IW2.burst_coordinates(j1).latitude,burst_extension(i1).IW2.burst_coordinates(j1).longitude,'-','Color',colori(i1,:)); hold(gxi,'on')
                    end
                    for j1 = 1 : burst_extension(i1).IW3.nb_burst
                        box_burst.IW3.lat{i1,j1}=[min(burst_extension(i1).IW3.burst_coordinates(j1).latitude),max(burst_extension(i1).IW3.burst_coordinates(j1).latitude)];
                        box_burst.IW3.lon{i1,j1}=[min(burst_extension(i1).IW3.burst_coordinates(j1).longitude),max(burst_extension(i1).IW3.burst_coordinates(j1).longitude)];
                        hold(gxi,'on')
                        geoplot(gxi,burst_extension(i1).IW3.burst_coordinates(j1).latitude,burst_extension(i1).IW3.burst_coordinates(j1).longitude,'-','Color',colori(i1,:)); hold(gxi,'on')
                    end
                end
                update_progressbar_MIESAR(i1./length(list{1}),axiprogress,miesar_para,'defaut'); drawnow; pause(0.01);

            end
            save([miesar_para.WK,'/parmsSLC.mat'],'box_burst','-append');

        case 'S1_SM'
            assignin('base','burst_extension',burst_extension)
            box_burst.IW1=[];
            for i1 = 1 : length(burst_extension)

                if isempty(burst_extension(i1).Date) == 0
                    box_burst.IW1.lat{i1,1}=[min(burst_extension(i1).Ext.burst_coordinates.latitude),max(burst_extension(i1).Ext.burst_coordinates.latitude)];
                    box_burst.IW1.lon{i1,1}=[min(burst_extension(i1).Ext.burst_coordinates.longitude),max(burst_extension(i1).Ext.burst_coordinates.longitude)];
                    hold(gxi,'on')

                    if contains(struct2array(ver), 'Mapping Toolbox')
                        geoplot(gxi,burst_extension(i1).Ext.burst_coordinates.latitude,burst_extension(i1).Ext.burst_coordinates.longitude,'-','Color',colori(i1,:)); hold(gxi,'on')
                    else
                        plot(gxi,burst_extension(i1).Ext.burst_coordinates.longitude,burst_extension(i1).Ext.burst_coordinates.latitude,'-','Color',colori(i1,:)); hold(gxi,'on')
                    end

                end
                update_progressbar_MIESAR(i1./length(list{1}),axiprogress,miesar_para,'defaut'); drawnow; pause(0.01);

            end
            save([miesar_para.WK,'/parmsSLC.mat'],'box_burst','-append');
    end

    [lonta,lata] = read_kml([miesar_para.WK,'/area.kml']);
    [lont,latt] = read_kml([miesar_para.WK,'/target.kml']);

    if contains(struct2array(ver), 'Mapping Toolbox')
        hold(gxi,'on')
        geoplot(gxi,latt,lont,'--','Color','black'); hold(gxi,'on')
        hold(gxi,'on')
        geoplot(gxi,lata,lonta,'--','Color','green'); hold(gxi,'on')

        hold(gxi,'off')
        geobasemap(gxi,'satellite');

    else
        hold(gxi,'on')
        plot(gxi,lont,latt,'--','Color','black'); hold(gxi,'on')
        hold(gxi,'on')
        plot(gxi,lont,latt,'--','Color','green'); hold(gxi,'on')
        hold(gxi,'off')

    end
else
    % No downloaded SLC, ask to download the last acquisition
    fid = fopen([miesar_para.WK,'/SLC.list'],'r');
    list = textscan(fid,['%s %s %s %s %s %s %s %s']);
    fclose(fid);

    %Find the last date
    dateall = [];
    for i1 = 1 : length(list{2})
        di = strsplit(list{2}{i1},'T'); di = di{1};
        dateall = [dateall; datenum(di,'yyyy-mm-dd')];
    end
    lastday = unique(dateall); lastday = lastday(end);
    index_last = find(lastday ==  dateall);

    answer = questdlg(['No SLC in the directory, but the program need a SLC to create the extension files. Do you want that the program download the last SAR acquistions? (',num2str(length(index_last)),' slides)'], ...
        'WARNING', ...
        'YES','NO','NO');
    switch answer
        case 'YES'
            % Downloading
            for i1 = 1 : length(index_last)
                urllast = list{8}{index_last(i1)};
                [configpath] = readpathinformation([miesar_para.cur,'/pathinformation.txt']);
                cmd1 = sprintf('wget -c --http-user=%s --http-password=%s "%s" -P %s',configpath.ASFID,configpath.ASFPWD,urllast,paramslc.pathSLC);
                system(cmd1);
            end
    end
end
