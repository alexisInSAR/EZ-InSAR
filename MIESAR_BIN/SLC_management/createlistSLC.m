function createlistSLC(src,evt,action,miesar_para)
%   createlistSLC(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to create the list of SLCs
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also createlistSLC, GUIpathdirectory, displayextensionS1,
%   initparmslc, readxmlannotationS1, displayextensionTSXPAZ, manageparamaterSLC, downloaderSLC, manageSLC.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.0.0 Alpha
%   Date: 07/07/2022
%
%   -------------------------------------------------------
%   Modified:
%           - Alexis Hrysiewicz, UCD / iCRAG, 18/07/2022: modifcation of
%           text information
%
%   -------------------------------------------------------
%   Version history:
%           2.0.0 Alpha: Initial (unreleased)

%% Open the variables
% For the path information
[configpath] = readpathinformation([miesar_para.cur,'/pathinformation.txt']);
% For the SLC parameters
paramslc = load([miesar_para.WK,'/parmsSLC.mat']);

%% For Sentinel-1 data 
if strcmp(paramslc.mode,'S1_IW') == 1 | strcmp(paramslc.mode,'S1_SM')

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

        box = [num2str(min(lon)),',',num2str(min(lat)),',',num2str(max(lon)),',',num2str(max(lat))];
        % For the mode
        switch paramslc.mode
            case 'S1_IW'
                % Connection to ASF server
                key_mode = 'IW';
                cmd1 = ['curl https://api.daac.asf.alaska.edu/services/search/param?platform=',key_sat,'\&beamMode=',key_mode,'\&bbox=',box,'\&start=',date1str,'\&end=',date2str,'\&relativeOrbit=',paramslc.track,'\&flightDirection=',Porb,'\&processingLevel=SLC\&maxResults=10000\&output=csv > tmp_list_SLC.csv'];
                system(cmd1);

            case 'S1_SM'
                % Connection to ASF server
                key_mode = 'S1';
                cmd1 = ['curl https://api.daac.asf.alaska.edu/services/search/param?platform=',key_sat,'\&beamMode=',key_mode,'\&bbox=',box,'\&start=',date1str,'\&end=',date2str,'\&relativeOrbit=',paramslc.track,'\&flightDirection=',Porb,'\&processingLevel=SLC\&maxResults=10000\&output=csv > tmp_list_SLC.csv'];
                system(cmd1);
                key_mode = 'S2';
                cmd1 = ['curl https://api.daac.asf.alaska.edu/services/search/param?platform=',key_sat,'\&beamMode=',key_mode,'\&bbox=',box,'\&start=',date1str,'\&end=',date2str,'\&relativeOrbit=',paramslc.track,'\&flightDirection=',Porb,'\&processingLevel=SLC\&maxResults=10000\&output=csv >> tmp_list_SLC.csv'];
                system(cmd1);
                key_mode = 'S3';
                cmd1 = ['curl https://api.daac.asf.alaska.edu/services/search/param?platform=',key_sat,'\&beamMode=',key_mode,'\&bbox=',box,'\&start=',date1str,'\&end=',date2str,'\&relativeOrbit=',paramslc.track,'\&flightDirection=',Porb,'\&processingLevel=SLC\&maxResults=10000\&output=csv >> tmp_list_SLC.csv'];
                system(cmd1);
                key_mode = 'S4';
                cmd1 = ['curl https://api.daac.asf.alaska.edu/services/search/param?platform=',key_sat,'\&beamMode=',key_mode,'\&bbox=',box,'\&start=',date1str,'\&end=',date2str,'\&relativeOrbit=',paramslc.track,'\&flightDirection=',Porb,'\&processingLevel=SLC\&maxResults=10000\&output=csv >> tmp_list_SLC.csv'];
                system(cmd1);
                key_mode = 'S5';
                cmd1 = ['curl https://api.daac.asf.alaska.edu/services/search/param?platform=',key_sat,'\&beamMode=',key_mode,'\&bbox=',box,'\&start=',date1str,'\&end=',date2str,'\&relativeOrbit=',paramslc.track,'\&flightDirection=',Porb,'\&processingLevel=SLC\&maxResults=10000\&output=csv >> tmp_list_SLC.csv'];
                system(cmd1);
                key_mode = 'S6';
                cmd1 = ['curl https://api.daac.asf.alaska.edu/services/search/param?platform=',key_sat,'\&beamMode=',key_mode,'\&bbox=',box,'\&start=',date1str,'\&end=',date2str,'\&relativeOrbit=',paramslc.track,'\&flightDirection=',Porb,'\&processingLevel=SLC\&maxResults=10000\&output=csv >> tmp_list_SLC.csv'];
                system(cmd1);
        end  

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

%% For the PAZ and TSX data
elseif strcmp(paramslc.mode,'PAZ_SM') == 1 | strcmp(paramslc.mode,'PAZ_SPT') == 1 | strcmp(paramslc.mode,'TSX_SM') == 1 | strcmp(paramslc.mode,'TSX_SPT') == 1

    if strcmp(paramslc.mode,'PAZ_SM') == 1 | strcmp(paramslc.mode,'PAZ_SPT') == 1 
        key_name = 'PAZ1';
    else
        key_name = 'TSX1';
    end 

    list_dir = dir([paramslc.pathSLC,'/',key_name,'*']);

    fres = fopen([miesar_para.WK,'/SLC.list'],'w');
    for i1 = 1 : length(list_dir)
        % Read the .xml
        path_xml = dir([paramslc.pathSLC,'/',list_dir(i1).name,'/',key_name,'*.xml']);
        path_xml = [paramslc.pathSLC,'/',list_dir(i1).name,'/',path_xml(1).name];

        data_xml = xml2struct(path_xml); 

        name = list_dir(i1).name; 

        d1 = data_xml.level1Product.productInfo.sceneInfo.start.timeUTC.Text;
        d1 = strrep(d1,'Z','');
        d2 = data_xml.level1Product.productInfo.sceneInfo.stop.timeUTC.Text;
        d2 = strrep(d1,'Z','');
        absorbit = data_xml.level1Product.productInfo.missionInfo.absOrbit.Text;
        relorbit = data_xml.level1Product.productInfo.missionInfo.relOrbit.Text;

        if strcmp(data_xml.level1Product.productInfo.acquisitionInfo.polarisationMode.Text,'SINGLE') == 1
            pol1 = data_xml.level1Product.productInfo.acquisitionInfo.polarisationList.polLayer.Text;
            pol2 = 'None'; 
        end

        % Save
        fprintf(fres,'%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n',name,d1,d2,relorbit,absorbit,pol1,pol2,'Stored');

        update_progressbar_MIESAR(i1./length(list_dir),findobj(gcf,'Tag','progressbar'),miesar_para,'defaut'); drawnow; pause(0.00001); 
    end
    fclose(fres);

end 

