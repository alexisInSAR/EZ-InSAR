function isce_preprocessing_S1_IW(src,evt,action,miesar_para)
%   isce_preprocessing_S1_IW(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to perform the pre-processing of ISCE
%
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also conversionstacks_SI_IW, isce_switch_stackfunctions, conversionstacks_SI_SM, parallelizationstepISCE, dem_box_cal, iscedisplayifg, removewatermask_ISCEprocessing_SM, isce_preprocessing_S1_IW, runISCEallstep, isce_preprocessing_SM, selectionofstack, isceprocessing.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.0.0 Beta
%   Date: 11/07/2022
%
%   -------------------------------------------------------
%   Modified:
%           - Alexis Hrysiewicz, UCD / iCRAG, 18/07/2022: modifcation of
%           text information
%
%   -------------------------------------------------------
%   Version history:
%           2.0.0 Beta: Initial (unreleased)

isce_switch_stackfunctions(src,evt,[],miesar_para)

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
    update_textinformation([],[],[],si,'error');
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
    update_textinformation([],[],[],si,'error');
    error(si);
end

si = ['The files are detected.'];
update_textinformation([],[],[],si,'information');

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
                        ' -m ',referdate,' --start_date ',paramslc.date1,' --stop_date ',paramslc.date2];
                else
                    cmd = ['stackSentinel.py -s ',paramslc.pathSLC,' -d ',pathdem,' -a ',paramslc.pathaux,' -o ',paramslc.pathorbit, ...
                        ' -b ''',num2str(min(lata)),' ',num2str(max(lata)),' ',num2str(min(lonta)),' ',num2str(max(lonta)),''' -W slc',...
                        ' -m ',referdate,' --start_date ',paramslc.date1,' --stop_date ',paramslc.date2];
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
