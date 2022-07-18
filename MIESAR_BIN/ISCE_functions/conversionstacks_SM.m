function conversionstacks_SI_SM(src,evt,action,miesar_para,para_stack)
%   conversionstacks(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%       [mode]          : "stack" or "convert"
%
%       conversionstacks_SI_SM converts the InSAR stacks (for StripMap data):
%           - from StaMPS stack (SLC stack) to MintPy stack (ifg stack);
%           - from MintPy stack (ifg stack) to StaMPS stack (SLC stack);
%
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also conversionstacks_SI_IW, isce_switch_stackfunctions,
%   conversionstacks_SI_SM, parallelizationstepISCE, dem_box_cal, iscedisplayifg, removewatermask_ISCEprocessing_SM, isce_preprocessing_S1_IW, runISCEallstep, isce_preprocessing_SM, selectionofstack, isceprocessing.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.0.0 Beta
%   Date: 12/07/2022
%
%   -------------------------------------------------------
%   Modified:
%           - Alexis Hrysiewicz, UCD / iCRAG, 18/07/2022: modifcation of
%           text information
%
%   -------------------------------------------------------
%   Version history:
%           2.0.0 Alpha: Initial (unreleased)

switch action
    case 'laststep_IFG_stack'
        %% Add the last step to process an interfergram stack
        disp('OKAY')
        % After to prepare the stack for SLC stacks
        
        % Interferogram network 
        [IFG,ref_date] = compute_network_ISCE(miesar_para,para_stack); 

        firun = fopen([miesar_para.WK,'/run_files/run_09_igram'],'w');    
        for i1 = 1 : size(IFG,1)
            fi = fopen([miesar_para.WK,'/configs/config_igram_',IFG{i1,1},'_',IFG{i1,2}],'w'); 
            fprintf(fi,'[Common]\n');
            fprintf(fi,'##########################\n');
            fprintf(fi,'##########################\n');
            fprintf(fi,'[Function-1]\n');
            fprintf(fi,'crossmul : \n');
            fprintf(fi,'reference : %s/merged/SLC/%s/%s.slc\n',miesar_para.WK,IFG{i1,1},IFG{i1,1});
            fprintf(fi,'secondary : %s/merged/SLC/%s/%s.slc\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'outdir : %s/merged/interferograms/%s_%s/fine\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'alks : %s\n',para_stack{8,2});
            fprintf(fi,'rlks : %s\n',para_stack{9,2});
            fprintf(fi,'##########################\n');
            fprintf(fi,'##########################\n');
            fprintf(fi,'[Function-2]\n');
            fprintf(fi,'FilterAndCoherence : \n');
            fprintf(fi,'input : %s/merged/interferograms/%s_%s/fine.int\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'filt : %s/merged/interferograms/%s_%s/filt_fine.int\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'coh : %s/merged/interferograms/%s_%s/filt_fine.cor\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'strength : %s\n',para_stack{11,2});
            fprintf(fi,'##########################\n');
            fprintf(fi,'##########################\n');
            fprintf(fi,'[Function-3]\n');
            fprintf(fi,'unwrap : \n');
            fprintf(fi,'ifg : %s/merged/interferograms/%s_%s/filt_fine.int\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'coh : %s/merged/interferograms/%s_%s/filt_fine.cor\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'unwprefix : %s/merged/interferograms/%s_%s/filt_fine\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'nomcf : False\n');
            fprintf(fi,'reference : %s/slc_unpacked_crop/%s/data\n',miesar_para.WK,ref_date);
            fprintf(fi,'defomax : 2\n');
            fprintf(fi,'alks : %s\n',para_stack{8,2});
            fprintf(fi,'rlks : %s\n',para_stack{9,2});
            fprintf(fi,'method : snaphu\n');
            fprintf(fi,'##########################\n');
            fclose(fi); 
            
            fprintf(firun,'stripmapWrapper.py -c %s\n',[miesar_para.WK,'/configs/config_igram_',IFG{i1,1},'_',IFG{i1,2}]); 
        end 
        fclose(firun); 


    case 'IF2SLC'
        %% Conversion MintPy stack to StaMPS stack

                % Names of stacks
                namestack = 'merged_mintpy';
                newnamestack = 'merged'; % We need to initiate the processing with merged directory because the .xml files use absolute paths. Better for the next...
        
                % Check the directory (NEEDED?)
                if exist([miesar_para.WK,'/',namestack])
                    si = ['The stack directory seems existed.'];
                    update_textinformation([],[],[],si,'information');
                else
                    si = ['The stack directory does not seem existed.'];
                    update_textinformation([],[],[],si,'error');
                    error(si);
                end
        
                if exist([miesar_para.WK,'/merged_stamps'])
                    si = ['The stack directory seems existed. Please remove merged_stamps directory.'];
                    update_textinformation([],[],[],si,'error');
                    error(si);
                end
        
                % Information
                disp('----------------------------------------------------------------------')
                disp('----------------------------------------------------------------------')
                disp('Convertion of stack: MintPy to StaMPS')
                disp('----------------------------------------------------------------------')
                disp('----------------------------------------------------------------------')
        
                if exist([miesar_para.WK,'/',newnamestack])
                    si = ['ERROR: The new stack is detected.'];
                    update_textinformation([],[],[],si,'error');
                    error(['ERROR: The new stack is detected.']);
                else
                    system(['mkdir ',miesar_para.WK,'/',newnamestack]);
                end
        
                % Copy the directories
                si = ['Copy the directories to generate the SLC stack...'];
                set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
                update_progressbar_MIESAR(0./3,findobj(gcf,'Tag','progressbar'),miesar_para,'defaut'); drawnow; pause(0.01);
                copyfile([miesar_para.WK,'/',namestack,'/baselines'],[miesar_para.WK,'/',newnamestack,'/baselines'])
                update_progressbar_MIESAR(1./3,findobj(gcf,'Tag','progressbar'),miesar_para,'defaut'); drawnow; pause(0.01);
                copyfile([miesar_para.WK,'/',namestack,'/geom_reference'],[miesar_para.WK,'/',newnamestack,'/geom_reference'])
                update_progressbar_MIESAR(2./3,findobj(gcf,'Tag','progressbar'),miesar_para,'defaut'); drawnow; pause(0.01);
                copyfile([miesar_para.WK,'/',namestack,'/SLC'],[miesar_para.WK,'/',newnamestack,'/SLC'])
                update_progressbar_MIESAR(3./3,findobj(gcf,'Tag','progressbar'),miesar_para,'defaut'); drawnow; pause(0.01);
                si = ['Copy the directories to generate the SLC stack: OKAY'];
                set(findobj(gcf,'Tag','maintextoutput'),'Value',si);


                % Rename the directory
                movefile([miesar_para.WK,'/',newnamestack],[miesar_para.WK,'/merged_stamps']);

    case 'SLC2IFG'
        %% Conversion StaMPS stack to ISCE stack

        % Names of stacks
        namestack = 'merged_stamps';
        newnamestack = 'merged'; % We need to initiate the processing with merged directory because the .xml files use absolute paths. Better for the next...

        % Find the reference data
        fi = fopen([miesar_para.WK,'/commandstack.log'],'r');
        b = textscan(fi,'%s'); fclose(fi); b = b{1};
        IndexC = strfind(b,['--reference_date']);
        Index = find(not(cellfun('isempty',IndexC)));
        datem = b{Index+1};
        refdate = datem; 

        % Check the directory (NEEDED?)
        if exist([miesar_para.WK,'/',namestack])
            si = ['The stack directory seems existed.'];
            update_textinformation([],[],[],si,'information');
        else
            si = ['The stack directory does not seem existed.'];
            update_textinformation([],[],[],si,'error');
            error(si);
        end

        if exist([miesar_para.WK,'/merged_mintpy'])
            si = ['The stack directory seems existed. Please remove merged_stamps directory.'];
            update_textinformation([],[],[],si,'error');
            error(si);
        end

        % Information
        disp('----------------------------------------------------------------------')
        disp('----------------------------------------------------------------------')
        disp('Convertion of stack: StaMPS to MintPy')
        disp('----------------------------------------------------------------------')
        disp('----------------------------------------------------------------------')

        % Creation of directory
        if exist([miesar_para.WK,'/configs_files_tmp'])
            si = ['ERROR: configs_files_tmp is here'];
            update_textinformation([],[],[],si,'error');
            error(['ERROR: configs_files_tmp is here']);
        else
            system(['mkdir ',miesar_para.WK,'/configs_files_tmp']);
        end

        if exist([miesar_para.WK,'/',newnamestack])
            si = ['ERROR: The new stack is detected.'];
            update_textinformation([],[],[],si,'error');
            error(['ERROR: The new stack is detected.']);
        else
            system(['mkdir ',miesar_para.WK,'/',newnamestack]);
        end

        % User inputs
        prompt = {'Temporal baseline','Perpendicular baseline','Range Looks (integer):','Azimuth Looks (integer):','Filter Strength (integer):'};
        dlgtitle = 'Interferogram parameters';
        definput = {'1000','10000','3','3','0.2'};
        dims = [1 100];
        opts.Interpreter = 'tex';
        answer = inputdlg(prompt,dlgtitle,dims,definput,opts);

        para_stack = cell(1); %dummy cell parameters

        para_stack{5,2} = refdate; 
        para_stack{6,2} = answer{1}; 
        para_stack{7,2} = answer{2}; 
        para_stack{8,2} = answer{3};
        para_stack{9,2} = answer{4};
        para_stack{11,2} = answer{5};

        [IFG,ref_date] = compute_network_ISCE(miesar_para,para_stack); 

        % Create the config files
        disp('Creation of config files:')

        scripttoeval = ['scripttoeval_',miesar_para.id,'.sh']; 
        firun = fopen(scripttoeval,'w');    
        for i1 = 1 : size(IFG,1)
            fi = fopen([miesar_para.WK,'/configs_files_tmp/config_igram_',IFG{i1,1},'_',IFG{i1,2}],'w'); 
            fprintf(fi,'[Common]\n');
            fprintf(fi,'##########################\n');
            fprintf(fi,'##########################\n');
            fprintf(fi,'[Function-1]\n');
            fprintf(fi,'crossmul : \n');
            fprintf(fi,'reference : %s/merged/SLC/%s/%s.slc\n',miesar_para.WK,IFG{i1,1},IFG{i1,1});
            fprintf(fi,'secondary : %s/merged/SLC/%s/%s.slc\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'outdir : %s/merged/interferograms/%s_%s/fine\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'alks : %s\n',para_stack{8,2});
            fprintf(fi,'rlks : %s\n',para_stack{9,2});
            fprintf(fi,'##########################\n');
            fprintf(fi,'##########################\n');
            fprintf(fi,'[Function-2]\n');
            fprintf(fi,'FilterAndCoherence : \n');
            fprintf(fi,'input : %s/merged/interferograms/%s_%s/fine.int\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'filt : %s/merged/interferograms/%s_%s/filt_fine.int\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'coh : %s/merged/interferograms/%s_%s/filt_fine.cor\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'strength : %s\n',para_stack{11,2});
            fprintf(fi,'##########################\n');
            fprintf(fi,'##########################\n');
            fprintf(fi,'[Function-3]\n');
            fprintf(fi,'unwrap : \n');
            fprintf(fi,'ifg : %s/merged/interferograms/%s_%s/filt_fine.int\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'coh : %s/merged/interferograms/%s_%s/filt_fine.cor\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'unwprefix : %s/merged/interferograms/%s_%s/filt_fine\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fi,'nomcf : False\n');
            fprintf(fi,'reference : %s/slc_unpacked_crop/%s/data\n',miesar_para.WK,ref_date);
            fprintf(fi,'defomax : 2\n');
            fprintf(fi,'alks : %s\n',para_stack{8,2});
            fprintf(fi,'rlks : %s\n',para_stack{9,2});
            fprintf(fi,'method : snaphu\n');
            fprintf(fi,'##########################\n');
            fclose(fi); 
            
            fprintf(firun,'stripmapWrapper.py -c %s\n',[miesar_para.WK,'/configs_files_tmp/config_igram_',IFG{i1,1},'_',IFG{i1,2}]); 
        end 
        fclose(firun); 

        % Copy the directories
        si = ['Copy the directories to generate the IFG stack...'];
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
        update_progressbar_MIESAR(0./3,findobj(gcf,'Tag','progressbar'),miesar_para,'defaut'); drawnow; pause(0.01);
        copyfile([miesar_para.WK,'/',namestack,'/baselines'],[miesar_para.WK,'/',newnamestack,'/baselines'])
        update_progressbar_MIESAR(1./3,findobj(gcf,'Tag','progressbar'),miesar_para,'defaut'); drawnow; pause(0.01);
        copyfile([miesar_para.WK,'/',namestack,'/geom_reference'],[miesar_para.WK,'/',newnamestack,'/geom_reference'])
        update_progressbar_MIESAR(2./3,findobj(gcf,'Tag','progressbar'),miesar_para,'defaut'); drawnow; pause(0.01);
        copyfile([miesar_para.WK,'/',namestack,'/SLC'],[miesar_para.WK,'/',newnamestack,'/SLC'])
        update_progressbar_MIESAR(3./3,findobj(gcf,'Tag','progressbar'),miesar_para,'defaut'); drawnow; pause(0.01);
        si = ['Copy the directories to generate the IFG stack: OKAY'];
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
        
        % Run the script
        system(['chmod a+x ',scripttoeval]); pause(0.5)
        if strcmp(computer,'MACI64') == 1
            %     system('./runmacterminal.sh');
        else
            system(['./',scripttoeval]);
        end
        try
            delete(scripttoeval)
        end

        system(['rm -r ',miesar_para.WK,'/configs_files_tmp']);
        movefile([miesar_para.WK,'/',newnamestack],[miesar_para.WK,'/merged_mintpy']);


end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [IFG,ref_date] = compute_network_ISCE(miesar_para,para_stack)

% Read the dates
tmp = dir([miesar_para.WK,'/baselines']);
file_bperp = cell(1);
h = 1;
for i1 = 1 : length(tmp)
    if isempty(strfind(tmp(i1).name,'.txt')) == 0
        file_bperp{h} = tmp(i1).name;
        h = h + 1;
    end
end

dates_slc = cell(1);
h = 1;
for i1 = 1 : length(file_bperp)
    a = strsplit(file_bperp{i1},'.');
    b = strsplit(a{1},'_');
    dates_slc{h} = b{1}; h = h + 1; dates_slc{h} = b{2}; h = h + 1;
end
dates_slc = unique(dates_slc);

% Read the reference date
ref_date = file_bperp{1}; ref_date = strsplit(ref_date,'_'); ref_date = ref_date{1};

% Read the baselines
bperp = [];
for i1 = 1 : length(dates_slc)
    if strcmp(dates_slc{i1},ref_date) == 1
        bperp(i1) = 0;
    else
        fi = fopen([miesar_para.WK,'/baselines/',ref_date,'_',dates_slc{i1},'.txt'],'r');
        data = textscan(fi,'%s %f'); fclose(fi);
        bperp(i1) = mean(data{2});
    end
end

% Computation of the ifg network
IFG = cell(1);
h = 1;
for i1 = 1 : length(dates_slc)
    for i2 = i1 + 1 : length(dates_slc)
        d1 = dates_slc{i1};
        d2 = dates_slc{i2};

        btemp = datenum(datetime(d2,'InputFormat','yyyyMMdd')) - datenum(datetime(d1,'InputFormat','yyyyMMdd'));
        baselines = bperp(i2) - bperp(i1);

        if abs(btemp) <= str2num(para_stack{6,2}) & abs(baselines) <= str2num(para_stack{7,2})
            IFG{h,1}  = d1; IFG{h,2}  = d2;
            h = h + 1;
        end
    end
end
