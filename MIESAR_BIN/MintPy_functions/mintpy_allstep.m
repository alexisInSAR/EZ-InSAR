function mintpy_allstep(src,evt,action,figstep,miesar_para)
%   Function to run several ISCE steps
%
%   See also ISCEPROCESSING, PARALLELIZATIONSTEPISCE, RUNISCEALLSTEP,
%   CHECKIPF.py.

%   Copyright 2022 Alexis Hrysiewicz, UCD / iCRAG2 
%   Version: 1.0.0 
%   Date: 15/02/2022

switch action
    
    case 'init'
        %% Create the GUI for user input

        % Load the log 
        fi = fopen([miesar_para.WK,'/stepmintpy.log'],'r'); logstack = textscan(fi,'%s %s'); fclose(fi);
        
        % Display the GUI 
        figstep = uifigure;
        figstep.Name = 'MintPy: Launching of all steps';
        headerbox = [];
        h = 400;
        for i1 = 1 : length(logstack{1})
            switch logstack{2}{i1}
                case 'RUN'
                    headerbox(i1) = uicheckbox(figstep,'Tag',logstack{1}{i1},'Text',[logstack{1}{i1},' ==> OKAY'],'Value', 0,'Position',[150 h 300 15],'FontColor','green');
                case 'NE'
                    headerbox(i1) = uicheckbox(figstep,'Tag',logstack{1}{i1},'Text',[logstack{1}{i1},' ==> NE'],'Value', 1,'Position',[150 h 300 15],'FontColor','red');
                case 'OPT'
                    headerbox(i1) = uicheckbox(figstep,'Tag',logstack{1}{i1},'Text',[logstack{1}{i1},' ==> OPT'],'Value', 0,'Position',[150 h 300 15],'FontColor','black');
            end
            h = h - 20;
        end
        btn = uibutton(figstep,'push','Position',[75, 75, 400, 22],'Text','Launch the processing','ButtonPushedFcn',@(btn,event,arg1,arg2,arg3) mintpy_allstep([],[],'run',figstep,miesar_para));
        
    case 'run'
        %% Run several selected steps
        
        % Load the log 
        fi = fopen([miesar_para.WK,'/stepmintpy.log'],'r'); logstack = textscan(fi,'%s %s'); fclose(fi);
        
        % Check the selected steps
        statestep = [];
        for i1 = 1 : length(logstack{1})
            statestep(i1) = get(findobj(figstep,'Tag',logstack{1}{i1}),'Value');
        end

        fi = fopen([miesar_para.WK,'/mintpydirectory.log'],'r');
        pathmintpyprocessing = textscan(fi,'%s'); fclose(fi); pathmintpyprocessing = pathmintpyprocessing{1}{1};

        paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
        switch paramslc.pass
            case 'Asc'
                Porb = 'A';
            case 'Desc'
                Porb = 'D';
        end
        name_cfg = ['mintpyfullparametersSen',Porb,'T',paramslc.track,'.cfg'];
        
        % Create the script
        nrun = find(statestep==1);
        if isempty(nrun) == 0

                scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];
                fid = fopen(scripttoeval,'w');
                fprintf(fid,'cd %s\n',[pathmintpyprocessing]);
                for i1 = 1 : length(logstack{1})
                    if statestep(i1)==1
                        fprintf(fid,'smallbaselineApp.py %s --dostep %s\n',name_cfg,logstack{1}{i1});
                        fprintf(fid,'%s\n',['sed -i ''/',logstack{1}{i1},'/ s/NE/RUN/'' ',miesar_para.WK,'/stepmintpy.log']);
                    end
                end
                fclose(fid);
                close(figstep);

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
        else
            %Check if at least one step is selected
            si = ['Please, select at least one step to run.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si);
        end
end
