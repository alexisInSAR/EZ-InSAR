function manageSLC(src,evt,action,miesar_para)
%   manageSLC(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to manage the SLCs.
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also manageparamaterSLC, initparmslc, readxmlannotationS1, downloaderSLC.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 29/11/2021
%
%   -------------------------------------------------------
%   Modified:
%           - Xiaowen Wang, UCD, 02/03/2022: bug fix
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)

switch action
    
    case 'checking'
        %% Check the available SLCs using the user parameters
        
        % Open the variables
        % For the path information
        [configpath] = readpathinformation([miesar_para.cur,'/pathinformation.txt']);
        % For the SLC parameters
        paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
        % For the study area
        [lon,lat] = read_kml([miesar_para.WK,'/area.kml']);
        % For the dates
        date1 = datetime(paramslc.date1);
        date2 = datetime(paramslc.date2);
        date1str = datestr(date1,'yyyy-mm-ddTHH:MM:ssUTC');
        date2str = datestr(date2,'yyyy-mm-ddTHH:MM:ssUTC');
        % For the pass
        switch paramslc.pass
            case 'Asc'
            Porb = 'A';
            case 'Desc'
            Porb = 'D';
        end

        % For the sat
        switch paramslc.sat
            case 'AB'
                key_sat = 'S1';
            case 'A'
                key_sat = 'Sentinel-1A';
            case 'B'
                key_sat = 'Sentinel-1B';
        end 

        % For the mode
        switch paramslc.mode
            case 'IW'
                key_mode = 'IW';
        end     
        
        % Connection to ASF server
        box = [num2str(min(lon)),',',num2str(min(lat)),',',num2str(max(lon)),',',num2str(max(lat))];
        cmd1 = ['curl https://api.daac.asf.alaska.edu/services/search/param?platform=',key_sat,'\&beamMode=',key_mode,'\&bbox=',box,'\&start=',date1str,'\&end=',date2str,'\&relativeOrbit=',paramslc.track,'\&flightDirection=',Porb,'\&processingLevel=SLC\&maxResults=10000\&output=csv > tmp_list_SLC.csv'];
        si = ['Connection to the ASF server ...'];
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
        set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
        system(cmd1);
        
        % Read the SLC table
        M = readtable('tmp_list_SLC.csv');
        listStart = M.StartTime;
        for i1 = 1 : length(listStart)
            di1(i1) = listStart(i1);
        end
        [D,idx]=sort(di1);
        listStart = M.StartTime(idx);
        listEnd = M.EndTime(idx);
        M = readtable('tmp_list_SLC.csv',"TextType","string",'DatetimeType',"Text");
        listnName = M.GranuleName(idx);
        listOrbit = M.Orbit(idx);
        listPath = M.PathNumber(idx);
        listURL = M.URL(idx);
        
        % Write the SLC list
        fres = fopen([miesar_para.WK,'/SLC.list'],'w');
        for j2 = 1 : length(listnName)
            datestart = [datestr(listStart(j2),'yyyy-mm-ddTHH:MM:ss'),'.000000'];
            datestop = [datestr(listEnd(j2),'yyyy-mm-ddTHH:MM:ss'),'.000000'];
            if isempty(strfind(listnName{j2},'DV'))==0
                pol1 = 'VV'; pol2 = 'VH';
            else
                pol1 = 'HH'; pol2 = 'HV';
            end
            fprintf(fres,'%s\t%s\t%s\t%d\t%d\t%s\t%s\t%s\n',listnName{j2},datestart,datestop,listPath(j2),listOrbit(j2),pol1,pol2,listURL{j2});
        end
        fclose(fres);
        
        % Finalisation and information
        system('rm tmp_list_SLC.csv');
        si = ['List of SLCs created'];
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
        set(findobj(gcf,'Tag','maintextoutput'),'FontColor','green');
        
    case 'opening'
        %% Open the list of SLCs
        
        % Open the variables
        % For the SLC parameters
        paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
        % For the SLC list (check if this file is okay)
        if exist([miesar_para.WK,'/SLC.list'])
            fid = fopen([miesar_para.WK,'/SLC.list'],'r');
            list = textscan(fid,['%s %s %s %s %s %s %s %s']); fclose(fid);
        else
            si = ['The SLC list is not present.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'Fontcolor','red');
            error('The SLC list is not present.');
        end
        
        %Creation of the table to be displayed
        rescell = cell(1);
        for i1 = 1 : length(list{1})
            c = [];
            for i2 = 1 : length(list)-1
                c = [c,'   ',list{i2}{i1}];
            end
            if exist([paramslc.pathSLC,'/',list{1}{i1},'.zip']) == 2 | exist([paramslc.pathSLC,'/',list{1}{i1},'.SAFE']) == 2
                rescell{i1} = ['<HTML><FONT color="green">',c,'</Font></html>'];
            else
                rescell{i1} = ['<HTML><FONT color="red">',c,'</Font></html>'];
            end
        end
        
        % Display the table using a new GUI
        si = ['The SLC list is displayed.'];
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
        set(findobj(gcf,'Tag','maintextoutput'),'FontColor','green');
        figi = figure('name','List of available SLCs','numbertitle','off','MenuBar', 'none','ToolBar','none');
        figi.Position = [111 147 891 651];
        uicontrol('Style','list', 'Position',[29 18 840 617], 'String',rescell);
        
    case 'extension'
        %% Display the burst extension from the last SLC
        
        % Open the variables
        
        % For the SLC list
        if exist([miesar_para.WK,'/SLC.list'])
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
                set(findobj(gcf,'Tag','name_progressbar'),'Text','Read the SLC extensions based on the .xml...'); drawnow; pause(0.01);
                % We have downloaded SLC(s)
                % Preparation of variables
                burst_extension = struct('Date','','IW1',[],'IW2',[],'IW3',[]);
                
                for i1 = 1 : length(list{1})
%                     set(findobj(gcf,'Tag','progressbar'),'Value',(i1./length(list{1})).*100); pause(0.01);
                    update_progressbar_MIESAR(i1./length(list{1}),findobj(gcf,'Tag','progressbar'),miesar_para,'defaut') ; 
                    if exist([paramslc.pathSLC,'/',list{1}{i1},'.zip']) == 2 & exist([paramslc.pathSLC,'/',list{1}{i1},'.SAFE']) == 0
                        % We need to unzip
%                         set(findobj(gcf,'Tag','progressbar'),'Value',(i1./length(list{1})).*100); drawnow; pause(0.01);
                        update_progressbar_MIESAR(i1./length(list{1}),findobj(gcf,'Tag','progressbar'),miesar_para,'defaut'); drawnow; pause(0.01);
                        [a,b] = system(['unzip -l ',paramslc.pathSLC,'/',list{1}{i1},'.zip ']);
                        c = strsplit(b,'\n');
                        index_xml = find(contains(c, '.SAFE/annotation/s1') & contains(c, 'vv') & contains(c, '.xml'));
                        
                        % Read the .xml
                        for i2 = 1 : length(index_xml)
                            pathzipi = c{index_xml(i2)}; pathzipi = strsplit(pathzipi,' '); pathzipi = pathzipi{end};
                            
                            [a,b] = system(['unzip ',paramslc.pathSLC,'/',list{1}{i1},'.zip ',pathzipi,' -d ',miesar_para.WK,'/tmp_annotation_slc_burst']);
                            [burst_coordinates, nb_burst] = readxmlannotationS1([miesar_para.WK,'/tmp_annotation_slc_burst/',pathzipi]);
                            system(['rm -r ',miesar_para.WK,'/tmp_annotation_slc_burst']);
                            
                            % Save the coordinates
                            di = strsplit(list{2}{i1},'.');
                            burst_extension(i1).Date = datetime(di{1},'InputFormat','yyyy-MM-dd''T''HH:mm:ss');
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
                            
                        end
                        
                    elseif exist([paramslc.pathSLC,'/',list{1}{i1},'.SAFE']) == 7
%                         set(findobj(gcf,'Tag','progressbar'),'Value',(i1./length(list{1})).*100); drawnow; pause(0.01);
                        update_progressbar_MIESAR(i1./length(list{1}),findobj(gcf,'Tag','progressbar'),miesar_para,'defaut'); drawnow; pause(0.01);
                        % We can extract directly because we have the .SAFE
                        list_xml = dir([paramslc.pathSLC,'/',list{1}{i1},'.SAFE/annotation/']);
                        
                        % We read the .xml
                        for i2 = 1 : length(list_xml)
                            if contains(list_xml(i2).name,'s1') & contains(list_xml(i2).name,'vv') & contains(list_xml(i2).name,'.xml')
                                pathzipi = list_xml(i2).name;
                                [burst_coordinates, nb_burst] = readxmlannotationS1([paramslc.pathSLC,'/',list{1}{i1},'.SAFE/annotation/',pathzipi]);

                                % Save the coordinates
                                di = strsplit(list{2}{i1},'.');
                                burst_extension(i1).Date = datetime(di{1},'InputFormat','yyyy-MM-dd''T''HH:mm:ss');
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
                set(findobj(gcf,'Tag','name_progressbar'),'Text','Display the burst coverage...'); drawnow; pause(0.01);
                axmain = gcf; 
                axiprogress = findobj(gcf,'Tag','progressbar');
                fig_ext_burst = figure('name','Coverage of bursts','numbertitle','off'); fig_ext_burst.OuterPosition = [200 100 1080 700];
                box_burst.IW1=[];  box_burst.IW2=[]; box_burst.IW3=[];

                gxi = geoaxes; 
                
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

                [lonta,lata] = read_kml([miesar_para.WK,'/area.kml']);
                [lont,latt] = read_kml([miesar_para.WK,'/target.kml']);

                hold(gxi,'on')  
                geoplot(gxi,latt,lont,'--','Color','black'); hold(gxi,'on')
                hold(gxi,'on')  
                geoplot(gxi,lata,lonta,'--','Color','green'); hold(gxi,'on')

                hold(gxi,'off') 
                geobasemap(gxi,'satellite');
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
        else
            % Information
            si = ['Please, checking the available SLC ...'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
        end
        
    case 'alldownloading'
        %% Download the SLCs
        downloaderSLC(miesar_para)
        
end
end

