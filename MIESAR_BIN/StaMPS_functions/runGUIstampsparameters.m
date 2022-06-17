function runGUIstampsparameters(fig,action,mode)
%   Function to select the StaMPS parameters regarding the InSAR approaches
%
%   See also runGUISBASnetwork, runGUIstampsparameters,
%   stampsMERGEDprocessing, stampsprocessing, stampsPSprocessing,
%   stampsSBASprocessing.

%   Copyright 2021 Alexis Hrysiewicz, UCD / iCRAG2 
%   Version: 1.0.0 
%   Date: 30/11/2021

global figbis
a = gcf; 
miesar_para_stamps_para = a.UserData; 

switch action
    case 'update'
        a = gcf; 
        miesar_para_stamps_para = a.UserData;

        %% Update the StaMPS parameters from user
        
        % Load the StaMPS parameters
        fi = fopen([miesar_para_stamps_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{2};
        
        % Check the InSAR approach
        switch mode
            case 'PS'
                param = load([pathstampsprocessing,'/parms.mat']);
                pathstampsprocessing = pathstampsprocessing;
            case 'SBAS'
                param = load([pathstampsprocessing,'/SMALL_BASELINES/parms.mat']);
                pathstampsprocessing = [pathstampsprocessing,'/SMALL_BASELINES'];
            case 'MERGED'
                param = load([pathstampsprocessing,'/MERGED/parms.mat']);
                pathstampsprocessing = [pathstampsprocessing,'/MERGED'];
        end
        
        if param.small_baseline_flag == 'n'
            set(findobj(fig,'Tag','flagprocess'),'String','PS approach');
        elseif param.small_baseline_flag == 'y' & strcmp(mode,'SBAS') == 1
            set(findobj(fig,'Tag','flagprocess'),'String','SBAS approach');
            set(findobj(fig,'Tag','unwrap_hold_good_values'),'Enable','on');
        elseif param.small_baseline_flag == 'y' & strcmp(mode,'MERGED') == 1
            set(findobj(fig,'Tag','flagprocess'),'String','PS/SBAS approach');
            set(findobj(fig,'Tag','unwrap_hold_good_values'),'Enable','on');
        end
        
        % Update the parameters
        listparam = fields(param);
        for i1 = 1 : length(listparam)
            hi = findobj(fig,'Tag',listparam{i1});
            if isempty(hi)==0
                if isnumeric(getfield(param,listparam{i1}))==1
                    set(hi,'String',num2str(getfield(param,listparam{i1})));
                else
                    set(hi,'String',getfield(param,listparam{i1}));
                end
                
                if strcmp(mode,'MERGED') == 1
                    if isempty(strfind(listparam{i1},'unwrap')) == 1 & isempty(strfind(listparam{i1},'scla')) == 1 & isempty(strfind(listparam{i1},'tropo')) == 1 & isempty(strfind(listparam{i1},'ref')) == 1
                        set(hi,'Enable','off');
                    end
                end
            end
        end
        figbis = fig;
        
    case 'write'
        %% Write the new parameters
        a = gcf; 
        miesar_para_stamps_para = a.UserData;

        % Load the StaMPS directory 
        fi = fopen([miesar_para_stamps_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{2};
        
        % Check the InSAR approach
        mode = get(findobj(figbis,'Tag','flagprocess'),'String');
        switch mode
            case 'PS approach'
                param = load([pathstampsprocessing,'/parms.mat']);
                pathstampsprocessing = pathstampsprocessing;
                mm = 'PS';
            case 'SBAS approach'
                param = load([pathstampsprocessing,'/SMALL_BASELINES/parms.mat']);
                pathstampsprocessing = [pathstampsprocessing,'/SMALL_BASELINES'];
                mm = 'SBAS';
            case 'PS/SBAS approach'
                param = load([pathstampsprocessing,'/MERGED/parms.mat']);
                pathstampsprocessing = [pathstampsprocessing,'/MERGED'];
                mm = 'MERGED';
        end

        % Threshold regarding the core number
            hi = findobj(figbis,'Tag','n_cores');
            try 
                htest = str2num(get(hi,'String')); 
            catch 
                htest = 1 ; 
            end
            if isempty(htest) == 0
                if htest > feature('numcores')
                    error(sprintf('Please use a number of cores <= %d',feature('numcores')))
                end 
            else
                error('Please use a number for the n_cores parameter.')
            end 
        
        % Write the new parameter(s)
        cur = cd;
        cd(pathstampsprocessing);
        listparam = fields(param);
        wi = waitbar(0,'Writting of parameters');
        for i1 = 1 : length(listparam)
            hi = findobj(figbis,'Tag',listparam{i1});
            if isempty(hi)==0
                if isnumeric(getfield(param,listparam{i1}))==1
                    setparm(listparam{i1},str2num(get(hi,'String')));
                else
                    setparm(listparam{i1},get(hi,'String'));
                end
            end
            waitbar(i1./length(listparam),wi);
        end
        close(wi);
        cd(cur);
        
        % Update the GUI 
        runGUIstampsparameters(figbis,'update',mm)
        
    case 'validation'
        %% Validation of the StaMPS parameters
        runGUIstampsparameters(0,'write',0)
        close(figbis);
        
    case 'defaut'
        %% Modify the StaMPS parameters using defaut parameters 
        a = gcf; 
        miesar_para_stamps_para = a.UserData;
        
        % Load the StaMPS directory 
        fi = fopen([miesar_para_stamps_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{2};

        mode = get(findobj(figbis,'Tag','flagprocess'),'String'); 
        
        % Validation to write the parameters
        runGUIstampsparameters(0,'validation',0)
        
        % Check the InSAR approach
        switch mode
            case 'PS approach'
                pathstampsprocessing = pathstampsprocessing;
                mm = 'PS';
            case 'SBAS approach'
                pathstampsprocessing = [pathstampsprocessing,'/SMALL_BASELINES'];
                mm = 'SBAS';
            case 'PS/SBAS approach'
                pathstampsprocessing = [pathstampsprocessing,'/MERGED'];
                mm = 'MERGED';
        end
        
        % Modify the parameters 
        cur = cd;
        if strcmp(mm,'PS') == 1
            cd(pathstampsprocessing);
            system('rm parms.mat');
            cd(cur);
            stampsPSprocessing([],[],'parm',miesar_para_stamps_para)
        elseif strcmp(mm,'SBAS') == 1
            cd(pathstampsprocessing);
            system('rm parms.mat');
            cd(cur);
            stampsSBASprocessing([],[],'parm',miesar_para_stamps_para)
        elseif strcmp(mm,'MERGED') == 1
            cd(pathstampsprocessing);
            system('rm parms.mat');
            cd(cur);
            stampsMERGEDprocessing([],[],'parm',miesar_para_stamps_para)
        end
end
end