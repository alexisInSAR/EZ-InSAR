function isceprocessing(src,evt,action,miesar_para)
%   Function to management the ISCE processing.
%
%   See also ISCEPROCESSING, PARALLELIZATIONSTEPISCE, RUNISCEALLSTEP,
%   CHECKIPF.py.

%   Copyright 2021 Alexis Hrysiewicz, UCD / iCRAG2
%   Version: 1.0.0
%   Date: 30/11/2021
%   Modified by Xiaowen Wang, UCD, 10/02/2022
switch action
    
    case 'IPFchecking'
        %% Check the IPF versions for the SLCs
        % Open the variables
        
        % For the SLC parameters
        if exist([miesar_para.WK,'/parmsSLC.mat'])
            paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
        else
            si = ['The SLC parameters do seems existed.'];
            set(findobj(gcf,'Tag','maintextoutput'),'String',si);
            set(findobj(gcf,'Tag','maintextoutput'),'ForegroundColor','red');
            f = errordlg('The SLC parameters do seems existed.','ERROR');
        end
        
        % Read the SLC list
        fid = fopen([miesar_para.WK,'/SLC.list'],'r');
        list = textscan(fid,['%s %s %s %s %s %s %s %s']); fclose(fid);
        
        % Preparation of variables
        date_IPF = [];
        IPF_version = [];
        
        % Read the IPF version in SLC files
        set(findobj(gcf,'Tag','name_progressbar'),'Text','Read the IPF versions...'); drawnow; pause(0.01);
        axiprogress = findobj(gcf,'Tag','progressbar');
        for i1 = 1 : length(list{1})
            update_progressbar_MIESAR(i1./length(list{1}),axiprogress,miesar_para,'defaut'); drawnow; pause(0.01);
            di = strsplit(list{2}{i1},'.');
            date_IPF = [date_IPF; datetime(di{1},'InputFormat','yyyy-MM-dd''T''HH:mm:ss')];
            
            if exist([paramslc.pathSLC,'/',list{1}{i1},'.zip']) == 2 & exist([paramslc.pathSLC,'/',list{1}{i1},'.SAFE']) == 0
                % We need to unzip the manifest
                [a,b] = system(['unzip ',paramslc.pathSLC,'/',list{1}{i1},'.zip ',list{1}{i1},'.SAFE/manifest.safe -d ',miesar_para.WK,'/tmp_manifest']);
                [a,b] = system(['grep "Sentinel-1 IPF" ',miesar_para.WK,'/tmp_manifest/',list{1}{i1},'.SAFE/manifest.safe',' | awk ''END {print $4}''']);
                c = strsplit(b,'"'); 
                IPFi = str2num(c{2});
                system(['rm -r ',miesar_para.WK,'/tmp_manifest']);
                
            elseif exist([paramslc.pathSLC,'/',list{1}{i1},'.SAFE']) == 7
                % We can extract directly because we have the .SAFE
                [a,b] = system(['grep "Sentinel-1 IPF" ',paramslc.pathSLC,'/',list{1}{i1},'.SAFE/manifest.safe',' | awk ''END {print $4}''']);
                c = strsplit(b,'"');
                IPFi = str2num(c{2});
            else
                IPFi = NaN;
            end
            
            IPF_version = [IPF_version; IPFi];
        end

        si = ['The IPF versions have been checked.'];
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si);

        %Display the results of IPF with messages
        figi = figure('name','Version of IPF','numbertitle','off');
        plot(date_IPF,IPF_version,'*k');
        xlabel('Time');
        ylabel('Version of IPF');
        a = gca;
        a.FontSize = 15; a.FontWeight = 'bold'; grid on; grid minor;
        if isempty(find(IPF_version <= 2.36))==1
            f = msgbox('All IPF versions are superior to 2.36. We don''t need the Aux files.','IPF Sentinel');
        else
            hold on; plot(date_IPF(find(IPF_version <= 2.36)),IPF_version(find(IPF_version <= 2.36)),'*r'); hold off;
            f = msgbox('Some acquisitions have a version inferior to 2.36 (in red). The Aux files must be used. See https://aux.sentinel1.eo.esa.int ', 'IPF Sentinel','warn');
        end
        
        
    case 'selectionDEM'
        %% Select the DEM
        paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
    
        si = ['Please, select the directory of the DEM or the dowload option.'];
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
        set(findobj(gcf,'Tag','maintextoutput'),'fontColor','black');
        
        %Question Dialog
        answer = questdlg('What is the used DEM?', ...
            'DEM', ...
            'Localhosted DEM','Download the DEM','Localhosted DEM');
        
        switch answer
            % If the DEM is a local DEM
            
            case 'Localhosted DEM'
                % Open the good directory

                selpath = uigetdir(miesar_para.WK,'Select the DEM directory');
                if selpath==0;   selpath = miesar_para.WK; end
                % Check the file used by ISCE
                cur = cd;
                cd(selpath);
                [a b] = system('ls'); b = strsplit(b);
                cd(cur);
                testDEM = 0;
                testvrt = 0;
                testxml = 0;
                for i1 = 1 : length(b) - 1
                    if isempty(strfind(b{i1},'dem.wgs84')) == 0 & isempty(strfind(b{i1},'.xml')) == 1 & isempty(strfind(b{i1},'.vrt')) == 1
                        testDEM = 1;
                        namedem = b{i1};
                    end
                    if isempty(strfind(b{i1},'dem.wgs84.vrt')) == 0
                        testvrt = 1;
                    end
                    if isempty(strfind(b{i1},'dem.wgs84.xml')) == 0
                        testxml = 1;
                    end
                end
                if testDEM == 1 & testvrt == 1 & testxml == 1
                    si = ['The selection of the DEM is finished.'];
                    set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
                    set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');                    
                    f = msgbox('All DEM files have been detected.','DEM files');
                    fid = fopen([miesar_para.WK,'/DEM_files.txt'],'w'); fprintf(fid,'%s',[selpath,'/',namedem]); fclose(fid);
                else
                    si = ['The selection of the DEM is not finished.'];
                    set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
                    set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');                    
                    f = msgbox('DEM files have not been detected.','DEM files','error');
                end
                
                % If we must download the DEM using the ISCE script
            case 'Download the DEM'
                if isfield(paramslc,'lonta') == 0 || isfield(paramslc,'lata') == 0
                    [lonta,lata] = read_kml([miesar_para.WK,'/area.kml']); 
                    paramslc.lonta=lonta;paramslc.lata=lata;   
                end
                
                if isfield(paramslc,'box_burst') == 0
                    errordlg('Please click "Check the SLC extension" first!')
                else
                   dem_region=dem_box_cal(paramslc.lonta,paramslc.lata,paramslc.box_burst);
                end
                
                dem_box_str=[mat2str(dem_region(1)),'/',mat2str(dem_region(2)),'/',mat2str(dem_region(3)),'/',mat2str(dem_region(4))]; 
                system(['chmod a+x ',miesar_para.cur,'/private/run_download_DEM.sh'])  ; 
                             
                answer = questdlg('Which DEM would you like to download?','DEM Downloading','NASADEM-1arc','COPERNICUS-1arc','Third-party Geotiff DEM','NASADEM-1arc');               
                switch answer
                    case 'NASADEM-1arc'                    
                         cmd = [miesar_para.cur,'/private/run_download_DEM.sh ',miesar_para.WK, ' ', dem_box_str];
                    case 'COPERNICUS-1arc'                         
                         cmd = [miesar_para.cur,'/private/run_download_DEM.sh ',miesar_para.WK, ' ', dem_box_str, ' 1'];
                    case 'Third-party Geotiff DEM'
                         cmd = [miesar_para.cur,'/private/run_download_DEM.sh ',miesar_para.WK, ' ', dem_box_str, ' 2'];
                    otherwise 
                        lastwarn ('No action will do.')
                        cmd = [''];
                end   
                
                fid = fopen([miesar_para.WK,'/DEM_files.txt'],'w'); fprintf(fid,'%s',[miesar_para.WK,'/dem/dem.wgs84']); fclose(fid);

                % Write the script
                scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];

                fid = fopen(scripttoeval,'w'); fprintf(fid,'%s\n',cmd); fclose(fid);
                % Run the sscript
                system(['chmod a+x ',scripttoeval]);
                if strcmp(computer,'MACI64') == 1
%                     system('./runmacterminal.sh');
                else
                    system(['./',scripttoeval]);
                end   
                try 
                    delete(scripttoeval)
                end 

                si = ['The preparation of DEM is finished.'];
                f = msgbox(si, 'Tip message','help'); 
        end
        
    case 'checkingDEM'
        %% Check and display the DEM
        
        % Open the variables
        axiprogress = findobj(gcf,'Tag','progressbar');
        % For the DEM files
        if exist([miesar_para.WK,'/DEM_files.txt'])==0
            si = ['There are not the DEM files.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            
            error(si);
        else
            si = ['The DEM files are detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','green');
        end
        
        set(findobj(gcf,'Tag','name_progressbar'),'Text','Displaying of DEM');
%         set(findobj(gcf,'Tag','progressbar'),'Value',(0/7).*100); drawnow; 
        update_progressbar_MIESAR(0/7,axiprogress,miesar_para,'defaut'); drawnow; pause(0.001);
        % Open the files
        set(findobj(gcf,'Tag','name_progressbar'),'Text','Opening of the files list...');
%         set(findobj(gcf,'Tag','progressbar'),'Value',(1/7).*100); drawnow; 
        update_progressbar_MIESAR(1/7,axiprogress,miesar_para,'defaut'); drawnow; pause(0.001);

        fid = fopen([miesar_para.WK,'/DEM_files.txt'],'r'); pathdem = textscan(fid,'%s'); fclose(fid); pathdem = cell2mat(pathdem{1});
        
        % Open the header information
        set(findobj(gcf,'Tag','name_progressbar'),'Text','Reading of header...');
%         set(findobj(gcf,'Tag','progressbar'),'Value',(2/7).*100); drawnow; 
        update_progressbar_MIESAR(2/7,axiprogress,miesar_para,'defaut'); drawnow; pause(0.001);

        xmldem = xml2struct([pathdem,'.vrt']);
        geo = strsplit(xmldem.VRTDataset.GeoTransform.Text,','); geo = cellfun(@str2num,geo);
        datatype = xmldem.VRTDataset.VRTRasterBand.Attributes.dataType;
        nbc = str2num(xmldem.VRTDataset.Attributes.rasterXSize);
        nbl = str2num(xmldem.VRTDataset.Attributes.rasterYSize);
        lat = geo(4) + (nbl-1) .* geo(6) : -geo(6) : geo(4);
        lon = geo(1) : geo(2) : geo(1) + (nbc-1).* geo(2);
        
        % Open the binary file
        set(findobj(gcf,'Tag','name_progressbar'),'Text','Opening of binary files...');
%         set(findobj(gcf,'Tag','progressbar'),'Value',(3/7).*100); drawnow; 
        update_progressbar_MIESAR(3/7,axiprogress,miesar_para,'defaut'); drawnow; pause(0.001);

        fid = fopen(pathdem,'r'); demraster = fread(fid,[nbc nbl],lower(datatype))'; fclose(fid);
        demraster = flipud(demraster);
        
        % Computation of lat/lon grid
        set(findobj(gcf,'Tag','name_progressbar'),'Text','Computation of the grid...');
%         set(findobj(gcf,'Tag','progressbar'),'Value',(4/7).*100); drawnow;
        update_progressbar_MIESAR(4/7,axiprogress,miesar_para,'defaut'); drawnow; pause(0.001);

        [X,Y] = meshgrid(lon,lat);
        
        % Compuation of the slope and aspect
        set(findobj(gcf,'Tag','name_progressbar'),'Text','Slope/Aspect computation...');
%         set(findobj(gcf,'Tag','progressbar'),'Value',(5/7).*100); drawnow; 
        update_progressbar_MIESAR(5/7,axiprogress,miesar_para,'defaut'); drawnow; pause(0.001);

        [aspect,slope] = gradientm(Y,X, demraster);
        aspect(isnan(aspect)==1) = 0;
        
        % Computation of shaded relief
        set(findobj(gcf,'Tag','name_progressbar'),'Text','Computation of shaded relief...');
%         set(findobj(gcf,'Tag','progressbar'),'Value',(6/7).*100); drawnow; 
        update_progressbar_MIESAR(6/7,axiprogress,miesar_para,'defaut'); drawnow; pause(0.001);

        azimuth = 315;
        elev = 45;
        shadedrelief = 255 .* ((cosd(90 - elev) .* cosd(slope)) + (sind(90 - elev) .* sind(slope) .* cosd(azimuth - aspect)));
                
        si = ['Opening of the figure'];
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
        set(findobj(gcf,'Tag','maintextoutput'),'Fontcolor','black');

        set(findobj(gcf,'Tag','name_progressbar'),'Text','Opening of the DEM visualisation');
%         set(findobj(gcf,'Tag','progressbar'),'Value',(7/7).*100); drawnow; 
        update_progressbar_MIESAR(7/7,axiprogress,miesar_para,'defaut'); drawnow; pause(0.001);
        
        % Display of the figure
        figi = figure('name','Visualisation of the DEM','numbertitle','off'); figi.Position = [48 71 1292 727];
        nameDEM = strsplit(pathdem,'/'); nameDEM = nameDEM{end};
        imagesc(lon,lat,shadedrelief); set(gca,'Ydir','normal');  colormap gray;
        title(strrep(nameDEM,'_','\_'));
        
        [lont,latt] = read_kml([miesar_para.WK,'/target.kml']);
        [lonta,lata] = read_kml([miesar_para.WK,'/area.kml']);
        
        hold on; plot(lont,latt,'-r'); hold off;
        hold on; plot(lonta,lata,'-b'); hold off;
        
        lg = legend('Target','ROI');
        axi = gca;
        axi.FontSize = 25; axi.FontWeight = 'bold'; xlabel('Longitude'); ylabel('Latitude');
        
    case 'prerunstack'
        %% Preparation of the ISCE stack
        
        % Detection of the stack type
        if strcmp(get(findobj(gcf,'Tag','radiobuttonISCEstack'),'Value'),'SLC stack') == 1
            modestack = 'slc';
        elseif strcmp(get(findobj(gcf,'Tag','radiobuttonISCEstack'),'Value'),'Coherence stack') == 1
            modestack = 'correl';
        elseif strcmp(get(findobj(gcf,'Tag','radiobuttonISCEstack'),'Value'),'Interferogram stack') == 1
            modestack = 'ifg';
        elseif strcmp(get(findobj(gcf,'Tag','radiobuttonISCEstack'),'Value'),'Offset stack') == 1
            error('The offset stack is not implemented.');
        end
                
        % For the SLC parameters
        paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
        
        % Find the DEM files
        if exist([miesar_para.WK,'/DEM_files.txt'])
            fid = fopen([miesar_para.WK,'/DEM_files.txt'],'r'); pathdem = textscan(fid,'%s'); fclose(fid); pathdem = cell2mat(pathdem{1});
        else
            si = ['The DEM files are not detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si);
        end
                
        % Open the ROI
        [lonta,lata] = read_kml([miesar_para.WK,'/area.kml']);
        
        % Ask the reference date
        prompt = {'Reference date in YYYYMMDD format:'};
        dlgtitle = 'Reference date';
        dims = [1 35];
        definput = {'20210101'};
        answer = inputdlg(prompt,dlgtitle,dims,definput);
        while isempty(answer) == 1
            drawnow
        end
        referdate = answer{1};

        % Open the SLC list
        if exist([miesar_para.WK,'/SLC.list'])
            fid = fopen([miesar_para.WK,'/SLC.list'],'r');
            list = textscan(fid,['%s %s %s %s %s %s %s %s']); fclose(fid);
        else
            si = ['The SLC list is not detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si);
        end
        
        si = ['The files are detected.'];
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
        set(findobj(gcf,'Tag','maintextoutput'),'FontColor','green');
        
        datei = [];
        for i1 = 1 : length(list{1})
            datei(i1,1) = datenum(datetime(list{2}{i1}(1:10),'InputFormat','yyyy-MM-dd'));
        end
        
        % Check if the reference date is good
        referdatenb = datenum(datetime(referdate,'InputFormat','yyyyMMdd'));
        if isempty(find(referdatenb==datei))==1
            f = msgbox('The reference date is not in the SLC list', 'Error','error');
            error('The reference date is not in the SLC list');
        end
        
        % Preparation of the command: the script identifies the stack type and creates the good command to run ISCE.
        switch modestack
            
            case 'slc' % if the stack type is SLC
                answer = questdlg('The SLC stack has been selected.','Stacking Mode','YES','NO','YES');
                if strcmp(answer,'NO') == 1
                    error('The wrong mode has been selected.');
                end
                answer = questdlg('Do you want a correlation using?','Correlation tool','NESD','Geometry','NESD');
                switch answer
                    case 'NESD'
                        answer = questdlg('Do you want to use the defaut threshold?','NESD tool','YES','NO','YES');
                        if strcmp(answer,'NO') == 1
                            prompt = {'Enter the threshold for NESD:'};
                            dlgtitle = 'NESD tool';
                            dims = [1 35];
                            definput = {'0.85'};
                            answer = inputdlg(prompt,dlgtitle,dims,definput);
                            thr = answer{1};
                            if isempty(str2num(thr))==1
                                error('The threshold must be a number...');
                            end
                            cmd = ['stackSentinel.py -s ',paramslc.pathSLC,' -d ',pathdem,' -a ',paramslc.pathaux,' -o ',paramslc.pathorbit, ...
                                ' -b ''',num2str(min(lata)),' ',num2str(max(lata)),' ',num2str(min(lonta)),' ',num2str(max(lonta)),''' -W slc -e ',thr,...
                                ' -m ',referdate,' --start_date ',paramslc.date1,' --stop_date ',paramslc.date2,' -z 1 -r 1'];
                        else
                            cmd = ['stackSentinel.py -s ',paramslc.pathSLC,' -d ',pathdem,' -a ',paramslc.pathaux,' -o ',paramslc.pathorbit, ...
                                ' -b ''',num2str(min(lata)),' ',num2str(max(lata)),' ',num2str(min(lonta)),' ',num2str(max(lonta)),''' -W slc',...
                                ' -m ',referdate,' --start_date ',paramslc.date1,' --stop_date ',paramslc.date2,' -z 1 -r 1'];
                        end
                    case 'Geometry'
                        cmd = ['stackSentinel.py -s ',paramslc.pathSLC,' -d ',pathdem,' -a ',paramslc.pathaux,' -o ',paramslc.pathorbit, ...
                            ' -b ''',num2str(min(lata)),' ',num2str(max(lata)),' ',num2str(min(lonta)),' ',num2str(max(lonta)),''' -W slc -C geometry',...
                            ' -m ',referdate,' --start_date ',paramslc.date1,' --stop_date ',paramslc.date2];
                end
                
            case 'ifg' % if the stack type is IFG
                answer = questdlg('The IFG stack has been selected.','Stacking Mode','YES','NO','YES');
                if strcmp(answer,'NO') == 1
                    error('The wrong mode has been selected.');
                end
                prompt = {'How many nearest neighbor connections have to be computed? (''all'' for all connections)'};
                dlgtitle = 'Nearest Neighbor Connections';
                dims = [1 35];
                definput = {'all'};
                answer = inputdlg(prompt,dlgtitle,dims,definput);
                c = answer{1};
                prompt = {'Azimuth Looks','Range Looks'};
                dlgtitle = 'Multilooking parameters';
                dims = [1 35];
                definput = {'2','8'};
                answer = inputdlg(prompt,dlgtitle,dims,definput);
                nbz = answer{1};
                nbr = answer{2};
                if isempty(str2num(nbz))==1 | isempty(str2num(nbr))==1
                    error('The number of looks must be numbers...');
                end
                prompt = {'Filter strength'};
                dlgtitle = 'Filtering parameter';
                dims = [1 35];
                definput = {'0.2'};
                answer = inputdlg(prompt,dlgtitle,dims,definput);
                filt_str = answer{1}; 
                if isempty(str2num(filt_str))==1 
                    error('The filter strength must be number (float)...');
                end
                answer = questdlg('Do you want a correlation using?','Correlation tool','NESD','Geometry','NESD');
                switch answer
                    case 'NESD'
                        answer = questdlg('Do you want to use the defaut threshold?','NESD tool','YES','NO','YES');
                        if strcmp(answer,'NO') == 1
                            prompt = {'Enter the threshold for NESD:'};
                            dlgtitle = 'NESD tool';
                            dims = [1 35];
                            definput = {'0.85'};
                            answer = inputdlg(prompt,dlgtitle,dims,definput);
                            
                            thr = answer{1};
                            if isempty(str2num(thr))==1
                                error('The threshold must be a number...');
                            end
                            cmd = ['stackSentinel.py -s ',paramslc.pathSLC,' -d ',pathdem,' -a ',paramslc.pathaux,' -o ',paramslc.pathorbit, ...
                                ' -b ''',num2str(min(lata)),' ',num2str(max(lata)),' ',num2str(min(lonta)),' ',num2str(max(lonta)),''' -e ',th,' -c ',c,...
                                ' -m ',referdate,' --start_date ',paramslc.date1,' --stop_date ',paramslc.date2,' -z ',nbz,' -r ',nbr,' -f ',filt_str];
                        else
                            cmd = ['stackSentinel.py -s ',paramslc.pathSLC,' -d ',pathdem,' -a ',paramslc.pathaux,' -o ',paramslc.pathorbit, ...
                                ' -b ''',num2str(min(lata)),' ',num2str(max(lata)),' ',num2str(min(lonta)),' ',num2str(max(lonta)),''' -c ',c,...
                                ' -m ',referdate,' --start_date ',paramslc.date1,' --stop_date ',paramslc.date2,' -z ',nbz,' -r ',nbr,' -f ',filt_str];
                        end
                    case 'Geometry'
                        cmd = ['stackSentinel.py -s ',paramslc.pathSLC,' -d ',pathdem,' -a ',paramslc.pathaux,' -o ',paramslc.pathorbit, ...
                            ' -b ''',num2str(min(lata)),' ',num2str(max(lata)),' ',num2str(min(lonta)),' ',num2str(max(lonta)),''' -C geometry -c ',c,...
                            ' -m ',referdate,' --start_date ',paramslc.date1,' --stop_date ',paramslc.date2,' -z ',nbz,' -r ',nbr,' -f ',filt_str];
                end
                
            case 'correl' % if the stack type is Coherence
                answer = questdlg('The Coherence stack has been selected.','Stacking Mode','YES','NO','YES');
                if strcmp(answer,'NO') == 1
                    error('The wrong mode has been selected.');
                end
                prompt = {'How many nearest neighbor connections have to be computed? (''all'' for all connections)'};
                dlgtitle = 'Nearest Neighbor Connections';
                dims = [1 35];
                definput = {'all'};
                answer = inputdlg(prompt,dlgtitle,dims,definput);
                c = answer{1};
                prompt = {'Azimuth Looks','Range Looks'};
                dlgtitle = 'Multilooking parameters';
                dims = [1 35];
                definput = {'2','8'};
                answer = inputdlg(prompt,dlgtitle,dims,definput);
                nbz = answer{1};
                nbr = answer{2};
                if isempty(str2num(nbz))==1 | isempty(str2num(nbr))==1
                    error('The number of looks must be numbers...');
                end
                answer = questdlg('Do you want a correlation using?','Correlation tool','NESD','Geometry','NESD');
                switch answer
                    case 'NESD'
                        answer = questdlg('Do you want to use the defaut threshold?','NESD tool','YES','NO','YES');
                        if strcmp(answer,'NO') == 1
                            prompt = {'Enter the threshold for NESD:'};
                            dlgtitle = 'NESD tool';
                            dims = [1 35];
                            definput = {'0.85'};
                            answer = inputdlg(prompt,dlgtitle,dims,definput);
                            thr = answer{1};
                            if isempty(str2num(thr))==1
                                error('The threshold must be a number...');
                            end
                            cmd = ['stackSentinel.py -s ',paramslc.pathSLC,' -d ',pathdem,' -a ',paramslc.pathaux,' -o ',paramslc.pathorbit, ...
                                ' -b ''',num2str(min(lata)),' ',num2str(max(lata)),' ',num2str(min(lonta)),' ',num2str(max(lonta)),''' -e ',th,' -c ',c,...
                                ' -m ',referdate,' --start_date ',paramslc.date1,' --stop_date ',paramslc.date2,' -z ',nbz,' -r ',nbr,' -W correlation'];
                        else
                            cmd = ['stackSentinel.py -s ',paramslc.pathSLC,' -d ',pathdem,' -a ',paramslc.pathaux,' -o ',paramslc.pathorbit, ...
                                ' -b ''',num2str(min(lata)),' ',num2str(max(lata)),' ',num2str(min(lonta)),' ',num2str(max(lonta)),''' -c ',c,...
                                ' -m ',referdate,' --start_date ',paramslc.date1,' --stop_date ',paramslc.date2,' -z ',nbz,' -r ',nbr,' -W correlation'];
                        end
                    case 'Geometry'
                        cmd = ['stackSentinel.py -s ',paramslc.pathSLC,' -d ',pathdem,' -a ',paramslc.pathaux,' -o ',paramslc.pathorbit, ...
                            ' -b ''',num2str(min(lata)),' ',num2str(max(lata)),' ',num2str(min(lonta)),' ',num2str(max(lonta)),''' -C geometry -c ',c,...
                            ' -m ',referdate,' --start_date ',paramslc.date1,' --stop_date ',paramslc.date2,' -z ',nbz,' -r ',nbr,' -W correlation'];
                end
        end
        
        % Save the command in a log file
        fi = fopen([miesar_para.WK,'/commandstack.log'],'w'); fprintf(fi,'%s',cmd); fclose(fi);
        
        % Final dialog box
        answer = questdlg(sprintf('The command is:\n\n%s',cmd),'Final script','RUN','CANCEL','CANCEL');
        
        % Run the command
        switch answer
            case 'RUN'
                scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];
                fid = fopen(scripttoeval,'w');
                fprintf(fid,'cd %s\n',miesar_para.WK);
		        fprintf(fid,'%s\n',cmd);
		        fclose(fid);
                % Run the script
                system(['chmod a+x ',scripttoeval]);
                if strcmp(computer,'MACI64') == 1
%                     system('./runmacterminal.sh');
                else
                    system(['./',scripttoeval]);
                    isceprocessing([],[],'updatepopmenustep',miesar_para)
                end   
                try 
                    delete(scripttoeval)
                end 
        end
                
    case 'updatepopmenustep'
        %% Update the popup menu concerning the ISCE steps
        
        %Check the orbits if re-run this step 
        paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
        cmd1=['find ',paramslc.pathorbit, ' -type l | xargs rm -f'];
        cmd2=['find ',paramslc.pathorbit, ' -name "*.EOF"|xargs -i ln -sf {} ', paramslc.pathorbit];
        system(cmd1);system(cmd2);
        
        % Load the directory
        cur = cd;
        
        % Check if the preparation of stack was done
        if exist([miesar_para.WK,'/run_files']) == 0
            si = ['The run_files directory is not detected. Please run the preparation of the ISCE stack.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si);
        else
            si = ['The run_files directory is detected. The steps are updated.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');
        end
        
        % Update the steps and update the menu
        cd([miesar_para.WK,'/run_files']);
        system('chmod a+x run_*');
        ls
        [a,b] = system('ls run* | grep -v ''para''');
        b = strsplit(b);
        b = b(1:end-1);
        cd(cur)
        
        h = 1;
        IndexC = strfind(b,['_',num2str(h),'_']);
        Index = find(not(cellfun('isempty',IndexC)));
        cellstep =  b;
        while isempty(Index)==0
            cellstep{h} = b{Index};
            h = h + 1;
            IndexC = strfind(b,['_',num2str(h),'_']);
            Index = find(not(cellfun('isempty',IndexC)));
        end
        set(findobj(gcf,'Tag','isceprocesspopupmenustep'),'Items',cellstep);
        
        % Update the log and check the modification of the ISCE stack. This log will be used to check the steps would be done.
        if exist([miesar_para.WK,'/stackstepisce.log'])==0
            fi = fopen([miesar_para.WK,'/stackstepisce.log'],'w');
            for i1 = 1 : length(cellstep); fprintf(fi,'%s %s\n',cellstep{i1},'NE'); end; fclose(fi);
        else
            fi = fopen([miesar_para.WK,'/stackstepisce.log'],'r'); logstack = textscan(fi,'%s %s'); fclose(fi);
            difftest = 0;
            for i1 = 1 : max(length(logstack{1}),length(cellstep))
                try
                    if strcmp(logstack{1}{i1},cellstep{i1}) == 0
                        difftest = 1;
                    end
                catch
                    difftest = 1;
                end
            end
            if difftest == 1
                warning('The log file does not correspond to the steps... It will be rewritten. The steps will be cancelled.');
                fi = fopen([miesar_para.WK,'/stackstepisce.log'],'w');
                for i1 = 1 : length(cellstep); fprintf(fi,'%s %s\n',cellstep{i1},'NE'); end; fclose(fi);
            end

            %Update the progress bar
            update_progressbar_MIESAR([],[],miesar_para,'isce')

        end
        
    case 'runselectedstep'
        %% Run the selected ISCE step
                
        % Identification of the selected step
        cellstep = get(findobj(gcf,'Tag','isceprocesspopupmenustep'),'Items');
        valuecellstep = get(findobj(gcf,'Tag','isceprocesspopupmenustep'),'Value');
        namestep = valuecellstep; 
        valuecellstep = find(cellfun(@(s) ~isempty(strfind(namestep, s)), cellstep)==1); 

        if isempty(strfind(namestep,'run'))==1
            si = ['Please, update the popmenu to run a selected step.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'Fontcolor','red');
            error(si);
        else
            si = [''];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'Fontcolor','black');
        end
        
        % Identification of the parallelization option
        if get(findobj(gcf,'Tag','modeiscesteppara'),'Value') == 1
            modepara = parallelizationstepISCE(namestep,miesar_para); 
        else
            modepara = 0;
        end
        
        % Read the log
        fi = fopen([miesar_para.WK,'/stackstepisce.log'],'r'); logstack = textscan(fi,'%s %s'); fclose(fi);
        
        % Check if the step already is done
        if valuecellstep == 1 | strcmp(logstack{2}{valuecellstep-1},'RUN') == 1
            if modepara == 1
                cmd = [namestep,'_para'];
            else
                cmd = namestep;
            end
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
            
            % Run the selected step
            if runi == 1
                scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];
                fid = fopen(scripttoeval,'w');
                fprintf(fid,'cd %s\n',[miesar_para.WK,'/run_files']);
                
                fprintf(fid,'./%s\n',cmd);
                fprintf(fid,'%s\n',['sed -i ''/',logstack{1}{valuecellstep},'/ s/NE/RUN/'' ',miesar_para.WK,'/stackstepisce.log']);
		        fclose(fid);

                logstack{2}{valuecellstep} = 'RUN';
                fi = fopen([miesar_para.WK,'/stackstepisce.log'],'w');
                for i1 = 1 : length(logstack{1}); fprintf(fi,'%s %s\n',logstack{1}{i1},logstack{2}{i1}); end;
                fclose(fi);

                % Run the script
                system(['chmod a+x ',scripttoeval]);
                if strcmp(computer,'MACI64') == 1
%                     system('./runmacterminal.sh');
                else
                        si = ['ISCE processing ',namestep, ' : IN PROGRESS'];
                        set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
                        set(findobj(gcf,'Tag','maintextoutput'),'FontColor','blue'); drawnow; pause(0.00001); 
                        status = system(['./',scripttoeval]);
                        if status == 0 
                            si = ['ISCE processing ',namestep, ' : COMPLETE'];
                            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
                            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','green'); drawnow; pause(0.00001); 
                        else 
                            si = ['ISCE processing ',namestep, ' : ERROR'];
                            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
                            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red'); drawnow; pause(0.00001); 
                        end 
                       
                     

                end   
                try 
                    delete(scripttoeval)
                end 
                
                fprintf('%s\n','')
                disp('*****************************************************************')
                fprintf('%s\t \n', ['**    The step  "', logstack{1}{valuecellstep}, '"  is finished!    **'])
                disp('*****************************************************************')
                fprintf('%s\n','')
            end
        else
            %Check if the previous step is done before the selected step
            si = ['The previous step is not done. Please, run the previous step before the selected step.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si);
        end
        
    case 'runallsteps'
        %% Run all the steps or several selected steps
        % Check if the parallelization is active
        if get(findobj(gcf,'Tag','modeiscesteppara'),'Value') == 1
            modepara = 1;
        else
            modepara = 0;
        end
        % Run the function
        runISCEallstep('init',modepara,NaN,miesar_para); 

    case 'open_coarse_network_check'
        %% Option to compute the coarse baselines
        si = ['Coarse computation of interferogram network: in progress.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');

        prompt = {'Orbit MODE [None or POD]','Potentiel Refence date [None or YYYYMMDD]'};
        dlgtitle = 'Pre-Computation of interferogram network';
        dims = [1 35];
        definput = {'None','None'};
        answer = inputdlg(prompt,dlgtitle,dims,definput); 

        paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
        [configpath] = readpathinformation([miesar_para.cur,'pathinformation.txt']);

        cmd = ['python3 ',miesar_para.cur,'/Suppfunctions/coarse_Sentinel_1_baselines.py -d',miesar_para.WK,' -r vv -e DEM']; 

        if strcmp(answer{1},'None')
            cmd = [cmd,' -f no']; 
        elseif strcmp(answer{1},'POD')
            cmd = [cmd,' -m POD -u ',configpath.ASFID,' -p ',configpath.ASFPWD,' -o ',paramslc.pathorbit,' -f no']; 
        else
            error('Bad parameters...')
        end 

        if strcmp(answer{2},'None')
            cmd  = cmd; 
        elseif length(answer{2}) == 8
            cmd = [cmd,' -a ',answer{2}]; 
        else
            error('Bad parameters...'); 
        end 
        
        system(cmd); 

        figi = figure('name','Coarse Interferogram network','numbertitle','off');
        figi.Position = [159 77 1400 882];
        axi = gca;
        im = imread([miesar_para.WK,'/coarse_ifg_network.jpg']);
        imshow(im);
          
        si = ['Coarse computation of interferogram network: DONE. Please use the best potential reference data for the next processing.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');

end
