function isce_preprocessing_SM(src,evt,action,miesar_para)
%   isce_preprocessing_SM(src,evt,action,miesar_para)
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
%           - Alexis Hrysiewicz, UCD / iCRAG, 18/07/2022: optimal network
%           option
%           - Alexis Hrysiewicz, UCD / iCRAG, 16/10/2023: fix
%
%   -------------------------------------------------------
%   Version history:
%           2.0.0 Beta: Initial (unreleased)
%           2.1.1 Beta: Initial (unreleased)

isce_switch_stackfunctions(src,evt,[],miesar_para)

% For the SLC parameters
paramslc = load([miesar_para.WK,'/parmsSLC.mat']);

% Open the SLC list
if exist([miesar_para.WK,'/SLC.list'])
    fid = fopen([miesar_para.WK,'/SLC.list'],'r');
    list = textscan(fid,['%s %s %s %s %s %s %s %s']); fclose(fid);
else
    si = ['The SLC list is not detected.'];
    update_textinformation([],[],[],si,'error');
    error(si);
end

%% Command for unpacking
pathout = [miesar_para.WK,'/slc_unpacked'];
if exist(pathout) == 0
    mkdir(pathout)
end

cmd = [];

for i1 = 1 : length(list{1})

    % For the date
    di = strsplit(list{2}{i1},'T'); di = di{1};
    di = strrep(di,'-','');

    % For Sentinel-1 SM
    if strcmp(paramslc.mode,'S1_SM') == 1
        if exist([paramslc.pathSLC,'/',list{1}{i1},'.SAFE']) == 7 | exist([paramslc.pathSLC,'/',list{1}{i1},'.zip']) == 2
            if exist([paramslc.pathSLC,'/',list{1}{i1},'.SAFE']) == 7
                pathinput = [paramslc.pathSLC,'/',list{1}{i1},'.SAFE'];
            elseif exist([paramslc.pathSLC,'/',list{1}{i1},'.zip']) == 2
                pathinput = [paramslc.pathSLC,'/',list{1}{i1},'.zip'];
            end
            cmdi = ['unpackFrame_S1.py -i ',pathinput,' -o ',[pathout,'/',di],' -p ',' vv ',' -b ', paramslc.pathorbit];
            cmd = [cmd,sprintf('%s\n',cmdi)];
        end

    elseif strcmp(paramslc.mode,'PAZ_SM') == 1 | strcmp(paramslc.mode,'PAZ_SPT') == 1
        if exist([paramslc.pathSLC,'/',list{1}{i1}]) == 7
            pathinput = [paramslc.pathSLC,'/',list{1}{i1}];

            cmdi = ['unpackFrame_PAZ.py -i ',pathinput,' -o ',[pathout,'/',di]];
            cmd = [cmd,sprintf('%s\n',cmdi)];
        end

    elseif strcmp(paramslc.mode,'TSX_SM') == 1 | strcmp(paramslc.mode,'TSX_SPT') == 1
        if exist([paramslc.pathSLC,'/',list{1}{i1}]) == 7
            pathinput = [paramslc.pathSLC,'/',list{1}{i1}];

            cmdi = ['unpackFrame_TSX_ezinsar.py -i ',pathinput,' -o ',[pathout,'/',di]];
            cmd = [cmd,sprintf('%s\n',cmdi)];
        end
    elseif strcmp(paramslc.mode,'CSK_SM') == 1 | strcmp(paramslc.mode,'CSK_SPT') == 1
        if exist([paramslc.pathSLC,'/',list{1}{i1}]) == 7
            pathinput = [paramslc.pathSLC,'/',list{1}{i1}];

            cmdi = ['unpackFrame_CSK.py -i ',pathinput,' -o ',[pathout,'/',di]];
            cmd = [cmd,sprintf('%s\n',cmdi)];
        end
    end
end

%% Command for pre-processing

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

% Preparation of the command: the script identifies the stack type and creates the good command to run ISCE.
para_stack = cell(1);
para_stack{1,1} = '--slc_directory';
para_stack{1,2} = [miesar_para.WK,'/slc_unpacked/'];
para_stack{2,1} = '--bbox';
para_stack{2,2} = ['"',num2str(min(lata)),' ',num2str(max(lata)),' ',num2str(min(lonta)),' ',num2str(max(lonta)),'"'];
para_stack{3,1} = '--working_directory';
para_stack{3,2} = miesar_para.WK;
para_stack{4,1} = '--dem';
para_stack{4,2} = pathdem;

prompt = {'Reference date in YYYYMMDD format:'};
dlgtitle = 'Reference date';
dims = [1 35];
definput = {'20200204'};
answer = inputdlg(prompt,dlgtitle,dims,definput);
while isempty(answer) == 1
    drawnow
end
referdate = answer{1};
% Check if the reference date is good
referdatenb = datenum(datetime(referdate,'InputFormat','yyyyMMdd'));
if isempty(find(referdatenb==datei))==1
    f = msgbox('The reference date is not in the SLC list', 'Error','error');
    error('The reference date is not in the SLC list');
end

para_stack{5,1} = '--reference_date';
para_stack{5,2} = referdate;

switch modestack
    case 'slc' % if the stack type is SLC
        answer = questdlg('The SLC stack has been selected.','Stacking Mode','YES','NO','YES');
        if strcmp(answer,'NO') == 1
            error('The wrong mode has been selected.');
        end

        prompt = {'Time Threshold','Baseline Threshold'};
        dlgtitle = 'Network parameters';
        dims = [1 35];
        definput = {'90','5000'};
        answer = inputdlg(prompt,dlgtitle,dims,definput);
        th1 = answer{1};
        th2 = answer{2};
        if isempty(str2num(th1))==1 | isempty(str2num(th2))==1
            error('The number of looks must be numbers...');
        end
        para_stack{6,1} = '--time_threshold';
        para_stack{6,2} = th1;
        para_stack{7,1} = '--baseline_threshold';
        para_stack{7,2} = th2;

        para_stack{8,1} = '--azimuth_looks';
        para_stack{8,2} = '1';
        para_stack{9,1} = '--range_looks';
        para_stack{9,2} = '1';
        para_stack{10,1} = '--workflow';
        para_stack{10,2} = 'slc';

        %         prompt = {'Use zero doppler geometry for processing:'};
        %         dlgtitle = 'Zero Doppler';
        %         dims = [1 35];
        %         definput = {'No'};
        %         answer = inputdlg(prompt,dlgtitle,dims,definput);
        para_stack{11,1} = '--zero';
        para_stack{11,2} = '';

    case 'ifg' % if the stack type is IFG
        answer = questdlg('The IFG stack has been selected.','Stacking Mode','YES','NO','YES');
        if strcmp(answer,'NO') == 1
            error('The wrong mode has been selected.');
        end

        prompt = {'Time Threshold [days or auto]','Baseline Threshold [days or auto]'};
        dlgtitle = 'Network parameters';
        dims = [1 35];
        definput = {'90','5000'};
        answer = inputdlg(prompt,dlgtitle,dims,definput);
        th1 = answer{1};
        th2 = answer{2};
        if isempty(str2num(th1))==1 | isempty(str2num(th2))==1
            error('The number of looks must be numbers...');
        end
        para_stack{6,1} = '--time_threshold';
        para_stack{6,2} = th1;
        para_stack{7,1} = '--baseline_threshold';
        para_stack{7,2} = th2;

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
        para_stack{8,1} = '--azimuth_looks';
        para_stack{8,2} = nbz;
        para_stack{9,1} = '--range_looks';
        para_stack{9,2} = nbr;

        para_stack{10,1} = '--unw_method';
        para_stack{10,2} = 'snaphu';

        prompt = {'Filter strength'};
        dlgtitle = 'Filtering parameter';
        dims = [1 35];
        definput = {'0.2'};
        answer = inputdlg(prompt,dlgtitle,dims,definput);
        filt_str = answer{1};
        if isempty(str2num(filt_str))==1
            error('The filter strength must be number (float)...');
        end
        para_stack{11,1} = '--filter_strength';
        para_stack{11,2} = filt_str;

        para_stack{12,1} = '--workflow';

        % Here we do not use the workflow named "interferogram" to write
        % the files in the good path.
        para_stack{12,2} = 'slc';

        %         prompt = {'Use zero doppler geometry for processing:'};
        %         dlgtitle = 'Zero Doppler';
        %         dims = [1 35];
        %         definput = {'No'};
        %         answer = inputdlg(prompt,dlgtitle,dims,definput);
        para_stack{13,1} = '--zero';
        para_stack{13,2} = '';

end

cmdpre = ['stackStripMap.py'];
for i1 = 1 : size(para_stack,1)
    cmdpre = [cmdpre,' ',para_stack{i1,1},' ',para_stack{i1,2}];
end
cmdpre = [cmdpre, ' --nofocus'];

% Save the command in a log file
fi = fopen([miesar_para.WK,'/commandstack.log'],'w'); fprintf(fi,'%s',cmdpre); fclose(fi);

% Final dialog box
answer = questdlg(sprintf('The command is:\n\n%s',cmdpre),'Final script','RUN','CANCEL','CANCEL');

%% Run the command
switch answer
    case 'RUN'
        scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];
        fid = fopen(scripttoeval,'w');
        fprintf(fid,'cd %s\n',miesar_para.WK);
        fprintf(fid,'%s\n',cmd);
        fprintf(fid,'%s\n',cmdpre);
        fprintf(fid,'rm run_files/*.job');
        fclose(fid);
        % Run the script
        system(['chmod a+x ',scripttoeval]);
        if strcmp(computer,'MACI64') == 1
            system('./runmacterminal.sh');
        else
            system(['./',scripttoeval]);
        end
        try
            delete(scripttoeval)
        end

        if strcmp(modestack,'ifg') == 1
            %% Here we add the last step to compute the interferogram
            conversionstacks_SM(src,evt,'laststep_IFG_stack',miesar_para,para_stack)
        end

        removewatermask_ISCEprocessing_SM(src,evt,[],miesar_para); %temporary fix
        isceprocessing([],[],'updatepopmenustep',miesar_para)
end
