function runISCEallstep(action,modepara,figstep,miesar_para)
%   runISCEallstep(action,modepara,figstep,miesar_para)
%       [action]        : name of the action to perform (string value)
%       [modepara]      : parall. model (0 or 1)
%       [figstep]       : GUI for the selection of steps
%       [miesar_para]   : user parameters (struct.)
%
%       Function to run several ISCE steps.
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also conversionstacks_SI_IW, isce_switch_stackfunctions, conversionstacks_SI_SM, parallelizationstepISCE, dem_box_cal, iscedisplayifg, removewatermask_ISCEprocessing_SM, isce_preprocessing_S1_IW, runISCEallstep, isce_preprocessing_SM, selectionofstack, isceprocessing.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 30/11/2021
%
%   -------------------------------------------------------
%   Modified:
%           - Alexis Hrysiewicz, UCD / iCRAG, 18/07/2022: modifcation of
%           text information
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initiale (unreleased)

isce_switch_stackfunctions([],[],[],miesar_para)

switch action
    
    case 'init'
        %% Create the GUI for user input
        
        % Load the log 
        fi = fopen([miesar_para.WK,'/stackstepisce.log'],'r'); logstack = textscan(fi,'%s %s'); fclose(fi);
        
        % Display the GUI 
        figstep = uifigure;
        figstep.Name = 'Launching of all steps';
        headerbox = [];
        h = 400;
        for i1 = 1 : length(logstack{1})
            switch logstack{2}{i1}
                case 'RUN'
                    headerbox(i1) = uicheckbox(figstep, 'Text',logstack{1}{i1},'Value', 0,'Position',[150 h 300 15]);
                case 'NE'
                    headerbox(i1) = uicheckbox(figstep, 'Text',logstack{1}{i1},'Value', 1,'Position',[150 h 300 15]);
            end
            h = h - 20;
        end
        btn = uibutton(figstep,'push','Position',[75, 75, 400, 22],'Text','Launch the processing','ButtonPushedFcn',@(btn,event) runISCEallstep('run',modepara,figstep,miesar_para));
        
    case 'run'
        %% Run several selected steps

        % Load the log 
        fi = fopen([miesar_para.WK,'/stackstepisce.log'],'r'); logstack = textscan(fi,'%s %s'); fclose(fi);
        
        % Check the selected steps
        statestep = [];
        for i1 = 1 : length(logstack{1})
            statestep(i1) = get(findobj(figstep,'Text',logstack{1}{i1}),'Value');
        end
        
        % Create the script
        nrun = find(statestep==1);
        if isempty(nrun) == 0
            [nnrun] = gradient(nrun);
            if isempty(find(nnrun>1))==1

                scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];
                fid = fopen(scripttoeval,'w');

                fprintf(fid,'cd %s\n',[miesar_para.WK,'/run_files']);
                for i1 = 1 : length(logstack{1})
                    if statestep(i1)==1
                        if modepara == 1
                            [modeparabis] = parallelizationstepISCE(logstack{1}{i1},miesar_para);
                        else
                            modeparabis = 0;
                        end
                        if modeparabis == 1
                            fprintf(fid,'./%s\n',[logstack{1}{i1},'_para']);
                        else
                            fprintf(fid,'./%s\n',[logstack{1}{i1}]);
                        end
                        cmdbis = ['sed -i ''/',logstack{1}{i1},'/ s/NE/RUN/'' ',miesar_para.WK,'/stackstepisce.log'];
                        fprintf(fid,'%s\n',cmdbis);
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
                %Check if the selected steps follow each other
                si = ['Please, select the steps that follow each other.'];
                update_textinformation([],[],[],si,'error');
                error(si);
            end
            
        else
            %Check if at least one step is selected
            si = ['Please, select at least one step to run.'];
            update_textinformation([],[],[],si,'error');
            error(si);
        end
end
