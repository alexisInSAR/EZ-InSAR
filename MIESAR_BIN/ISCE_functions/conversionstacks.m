function conversionstacks(src,evt,action,miesar_para)
%   conversionstacks(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       conversionstacks converts the InSAR stacks:
%           - from StaMPS stack (SLC stack) to MintPy stack (ifg stack);
%           - from MintPy stack (ifg stack) to StaMPS stack (SLC stack);
%   
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also ISCEPROCESSING
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 06/07/2022
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)

switch action
    case 'IF2SLC'
        %% Conversion MintPy stack to StaMPS stack

        % Names of stacks
        namestack = 'merged_mintpy';
        newnamestack = 'merged'; % We need to initiate the processing with merged directory because the .xml files use absolute paths. Better for the next...

        % Find the reference data
        fi = fopen([miesar_para.WK,'/commandstack.log'],'r')
        b = textscan(fi,'%s'); fclose(fi); b = b{1};
        IndexC = strfind(b,['-m']);
        Index = find(not(cellfun('isempty',IndexC)));
        datem = b{Index+1};
        refdate = datem; 

        % Check the directory (NEEDED?)
        if exist([miesar_para.WK,'/',namestack])
            si = ['The stack directory seems existed.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');
        else
            si = ['The stack directory does not seem existed.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si);
        end

        if exist([miesar_para.WK,'/merged_stamps'])
            si = ['The stack directory seems existed. Please remove merged_stamps directory.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','re');
            error(si);
        end

        % Information
        disp('----------------------------------------------------------------------')
        disp('----------------------------------------------------------------------')
        disp('Convertion of stack: MintPy to StaMPS')
        disp('----------------------------------------------------------------------')
        disp('----------------------------------------------------------------------')

        % Creation of directory 
        if exist([miesar_para.WK,'/configs_files_tmp'])
            si = ['ERROR: configs_files_tmp is here'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(['ERROR: configs_files_tmp is here']);
        else
            system(['mkdir ',miesar_para.WK,'/configs_files_tmp']);
        end

        if exist([miesar_para.WK,'/',newnamestack])
            si = ['ERROR: The new stack is detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(['ERROR: The new stack is detected.']);
        else
            system(['mkdir ',miesar_para.WK,'/',newnamestack]);
        end

        % Read the dates
        dateslc = cell(1);
        list = dir([miesar_para.WK,'/',namestack,'/SLC']);
        h = 1;
        for i1 = 1 : length(list)
            if length(list(i1).name) == 8
                dateslc{h} = list(i1).name;
                h = h + 1;
            end
        end

        % Create the config files
        disp('Creation of config files:')

        % For the merging of SLCs
        for i1 = 1 : length(dateslc)
            fid = fopen([miesar_para.WK,'/configs_files_tmp/config_merge_',dateslc{i1}],'w');
            fprintf(fid,'[Common]\n');
            fprintf(fid,'##########################\n');
            fprintf(fid,'###################################\n');
            fprintf(fid,'[Function-1]\n');
            fprintf(fid,'mergeBursts :\n');
            fprintf(fid,'stack : %s\n',[miesar_para.WK,'/stack']);
            if strcmp(dateslc{i1},refdate) == 0
                s1 = [miesar_para.WK,'/coreg_secondarys/',dateslc{i1}];
                s2 = [miesar_para.WK,'/coreg_secondarys/',dateslc{i1}];
                s3 = 'True';
            else
                s1 = [miesar_para.WK,'/reference'];
                s2 = [miesar_para.WK,'/reference'];
                s3 = 'False';
            end
            fprintf(fid,'inp_reference : %s\n',s1);
            fprintf(fid,'dirname : %s\n',s2);
            fprintf(fid,'name_pattern : burst*slc\n');
            fprintf(fid,'outfile : %s\n',[miesar_para.WK,'/',newnamestack,'/SLC/',dateslc{i1},'/',dateslc{i1},'.slc']);
            fprintf(fid,'method : top\n');
            fprintf(fid,'aligned : %s\n',s3);
            fprintf(fid,'valid_only : True\n');
            fprintf(fid,'use_virtual_files : False\n');
            fprintf(fid,'multilook : False\n');
            fprintf(fid,'range_looks : 9\n');
            fprintf(fid,'azimuth_looks : 3\n');
            fclose(fid);
        end

        % For the merging of other parameters
        paralist = {'lat','lon','hgt','incLocal','los','shadowMask'};

        for i1 = 1 : length(paralist)
            if strcmp(paralist{i1},'shadowMask') == 1
                mlt = 'isce';
            else
                mlt = 'gdal';
            end

            fid = fopen([miesar_para.WK,'/configs_files_tmp/config_merge_',paralist{i1}],'w');
            fprintf(fid,'[Common]\n');
            fprintf(fid,'##########################\n');
            fprintf(fid,'###################################\n');
            fprintf(fid,'[Function-1]\n');
            fprintf(fid,'mergeBursts :\n');
            fprintf(fid,'stack : %s\n',[miesar_para.WK,'/stack']);
            s1 = [miesar_para.WK,'/reference'];
            s2 = [miesar_para.WK,'/geom_reference'];
            fprintf(fid,'inp_reference : %s\n',s1);
            fprintf(fid,'dirname : %s\n',s2);
            fprintf(fid,'name_pattern : %s*rdr\n',paralist{i1});
            fprintf(fid,'outfile : %s\n',[miesar_para.WK,'/',newnamestack,'/geom_reference/',paralist{i1},'.rdr']);
            fprintf(fid,'method : top\n');
            fprintf(fid,'aligned : False\n');
            fprintf(fid,'valid_only : False\n');
            fprintf(fid,'use_virtual_files : False\n');
            fprintf(fid,'multilook : True\n');
            fprintf(fid,'range_looks : 9\n');
            fprintf(fid,'azimuth_looks : 3\n');
            fprintf(fid,'multilook_tool : %s\n',mlt);

            if strcmp(paralist{i1},'hgt') == 0
                fprintf(fid,'no_data_value : 0\n');
            end

            fclose(fid);
        end

        % For the baselines grid
        for i1 = 1 : length(dateslc)
            fid = fopen([miesar_para.WK,'/configs_files_tmp/config_baselinegrid_',dateslc{i1}],'w');
            
            fprintf(fid,'[Common]\n');
            fprintf(fid,'##########################\n');
            fprintf(fid,'##########################\n');
            fprintf(fid,'[Function-1]\n');
            fprintf(fid,'baselineGrid : \n');
            fprintf(fid,'reference : %s/reference/\n',miesar_para.WK);
            if strcmp(dateslc{i1},refdate) == 0
                fprintf(fid,'secondary : %s/secondarys/%s\n',miesar_para.WK,dateslc{i1});
            else
                fprintf(fid,'secondary : %s/reference/\n',miesar_para.WK);
            end
            fprintf(fid,'baseline_file : %s/%s/baselines/%s/%s\n',miesar_para.WK,newnamestack,dateslc{i1},dateslc{i1});
            fclose(fid);
        end

        disp('Creation of config files: OKAY')

        % Create the run files
        disp('Creation of the run file:')

        scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];
        fid = fopen(scripttoeval,'w');

        for i1 = 1 : length(dateslc)
            fprintf(fid,'SentinelWrapper.py -c %s\n',[miesar_para.WK,'/configs_files_tmp/config_merge_',dateslc{i1}]);
        end
        for i1 = 1 : length(paralist)
            fprintf(fid,'SentinelWrapper.py -c %s\n',[miesar_para.WK,'/configs_files_tmp/config_merge_',paralist{i1}]);
        end
        for i1 = 1 : length(dateslc)
                fprintf(fid,'SentinelWrapper.py -c %s\n',[miesar_para.WK,'/configs_files_tmp/config_baselinegrid_',dateslc{i1}]);
        end
        fclose(fid);

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
        movefile([miesar_para.WK,'/',newnamestack],[miesar_para.WK,'/merged_stamps']);

    case 'SLC2IFG'
        %% Conversion StaMPS stack to ISCE stack

        % Names of stacks
        namestack = 'merged_stamps';
        newnamestack = 'merged'; % We need to initiate the processing with merged directory because the .xml files use absolute paths. Better for the next...

        % Find the reference data
        fi = fopen([miesar_para.WK,'/commandstack.log'],'r')
        b = textscan(fi,'%s'); fclose(fi); b = b{1};
        IndexC = strfind(b,['-m']);
        Index = find(not(cellfun('isempty',IndexC)));
        datem = b{Index+1};
        refdate = datem; 

        % Check the directory (NEEDED?)
        if exist([miesar_para.WK,'/',namestack])
            si = ['The stack directory seems existed.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');
        else
            si = ['The stack directory does not seem existed.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(si);
        end

        if exist([miesar_para.WK,'/merged_mintpy'])
            si = ['The stack directory seems existed. Please remove merged_stamps directory.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','re');
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
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(['ERROR: configs_files_tmp is here']);
        else
            system(['mkdir ',miesar_para.WK,'/configs_files_tmp']);
        end

        if exist([miesar_para.WK,'/',newnamestack])
            si = ['ERROR: The new stack is detected.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            error(['ERROR: The new stack is detected.']);
        else
            system(['mkdir ',miesar_para.WK,'/',newnamestack]);
        end

        % Read the dates
        dateslc = cell(1);
        list = dir([miesar_para.WK,'/',namestack,'/SLC']);
        h = 1;
        for i1 = 1 : length(list)
            if length(list(i1).name) == 8
                dateslc{h} = list(i1).name;
                h = h + 1;
            end
        end

        % User inputs
        prompt = {'Range Looks (integer):','Azimuth Looks (integer):','Network Connection (integer or all):','Filter Strength (integer):'};
        dlgtitle = 'Interferogram parameters';
        definput = {'25','5','all','0.2'};
        dims = [1 100];
        opts.Interpreter = 'tex';
        answer = inputdlg(prompt,dlgtitle,dims,definput,opts);

        range_looks = str2num(answer{1})
        azimuth_looks = str2num(answer{2}) 
        if strcmp(answer{3},'all')
            ncon = 'all'
        else
            ncon = answer{3}
        end 
        strength = str2num(answer{4})

        % Create the config files
        disp('Creation of config files:')

        % Creation of interferogram list
        IFG = cell(1); 

        if strcmp(ncon,'all')
            h = 1; 
            for i1 = 1 : length(dateslc) - 1
                for j1 = i1 + 1 : length(dateslc)
                    IFG{h,1} = dateslc{i1}; 
                    IFG{h,2} = dateslc{j1};
                    h = h + 1; 
                end 
            end 
        else
            ncon = str2num(ncon); 
            h = 1; 
            for i1 = 1 : length(dateslc) - 1
                j_end=i1 + ncon;
                if j_end > length(dateslc)
                    j_end=length(dateslc);
                end
                for j1 = i1 + 1 : j_end
                    IFG{h,1} = dateslc{i1}; 
                    IFG{h,2} = dateslc{j1};
                    h = h + 1; 
                end 
            end 
        end
 %      save IFG IFG

        % For the merging of SLCs
        for i1 = 1 : length(dateslc)
            fid = fopen([miesar_para.WK,'/configs_files_tmp/config_merge_',dateslc{i1}],'w');
            fprintf(fid,'[Common]\n');
            fprintf(fid,'##########################\n');
            fprintf(fid,'###################################\n');
            fprintf(fid,'[Function-1]\n');
            fprintf(fid,'mergeBursts :\n');
            fprintf(fid,'stack : %s\n',[miesar_para.WK,'/stack']);
            if strcmp(dateslc{i1},refdate) == 0
                s1 = [miesar_para.WK,'/coreg_secondarys/',dateslc{i1}];
                s2 = [miesar_para.WK,'/coreg_secondarys/',dateslc{i1}];
                s3 = 'True';
            else
                s1 = [miesar_para.WK,'/reference'];
                s2 = [miesar_para.WK,'/reference'];
                s3 = 'False';
            end
            fprintf(fid,'inp_reference : %s\n',s1);
            fprintf(fid,'dirname : %s\n',s2);
            fprintf(fid,'name_pattern : burst*slc\n');
            fprintf(fid,'outfile : %s\n',[miesar_para.WK,'/',newnamestack,'/SLC/',dateslc{i1},'/',dateslc{i1},'.slc']);
            fprintf(fid,'method : top\n');
            fprintf(fid,'aligned : %s\n',s3);
            fprintf(fid,'valid_only : True\n');
            fprintf(fid,'use_virtual_files : True\n');
            fprintf(fid,'multilook : False\n');
            fprintf(fid,'range_looks : %1.0f\n',range_looks);
            fprintf(fid,'azimuth_looks : %1.0f\n',azimuth_looks);
            fclose(fid);
        end

        % For the merging of other parameters
        paralist = {'lat','lon','hgt','incLocal','los','shadowMask'};

        for i1 = 1 : length(paralist)
            if strcmp(paralist{i1},'shadowMask') == 1
                mlt = 'isce';
            else
                mlt = 'gdal';
            end

            fid = fopen([miesar_para.WK,'/configs_files_tmp/config_merge_',paralist{i1}],'w');
            fprintf(fid,'[Common]\n');
            fprintf(fid,'##########################\n');
            fprintf(fid,'###################################\n');
            fprintf(fid,'[Function-1]\n');
            fprintf(fid,'mergeBursts :\n');
            fprintf(fid,'stack : %s\n',[miesar_para.WK,'/stack']);
            s1 = [miesar_para.WK,'/reference'];
            s2 = [miesar_para.WK,'/geom_reference'];
            fprintf(fid,'inp_reference : %s\n',s1);
            fprintf(fid,'dirname : %s\n',s2);
            fprintf(fid,'name_pattern : %s*rdr\n',paralist{i1});
            fprintf(fid,'outfile : %s\n',[miesar_para.WK,'/',newnamestack,'/geom_reference/',paralist{i1},'.rdr']);
            fprintf(fid,'method : top\n');
            fprintf(fid,'aligned : False\n');
            fprintf(fid,'valid_only : False\n');
            fprintf(fid,'use_virtual_files : True\n');
            fprintf(fid,'multilook : True\n');
            fprintf(fid,'range_looks : %1.0f\n',range_looks);
            fprintf(fid,'azimuth_looks : %1.0f\n',azimuth_looks);
            fprintf(fid,'multilook_tool : %s\n',mlt);
            if strcmp(paralist{i1},'hgt') == 0
                fprintf(fid,'no_data_value : 0\n');
            end
            fclose(fid);
        end

        for i1 = 1 : size(IFG,1)
            % Create the run_13_generate_burst_igram files 
            fid = fopen([miesar_para.WK,'/configs_files_tmp/config_generate_igram_',IFG{i1,1},'_',IFG{i1,2}],'w');
            fprintf(fid,'[Common]\n');
            fprintf(fid,'##########################\n');
            fprintf(fid,'###################################\n');
            fprintf(fid,'[Function-1]\n');
            fprintf(fid,'generateIgram :\n');
            if strcmp(IFG{i1,1},refdate)
                fprintf(fid,'reference : %s\n',[miesar_para.WK,'/reference']);
            else
                fprintf(fid,'reference : %s\n',[miesar_para.WK,'/coreg_secondarys/',IFG{i1,1}]);
            end
            if strcmp(IFG{i1,2},refdate)
                fprintf(fid,'secondary : %s\n',[miesar_para.WK,'/reference']);
            else
                fprintf(fid,'secondary : %s\n',[miesar_para.WK,'/coreg_secondarys/',IFG{i1,2}]);
            end
            fprintf(fid,'interferogram : %s\n',[miesar_para.WK,'/interferograms/',IFG{i1,1},'_',IFG{i1,2}]);
            fprintf(fid,'flatten : False\n');
            fprintf(fid,'interferogram_prefix : fine\n');
            fprintf(fid,'overlap : False\n');
            fprintf(fid,'###################################\n');
            fclose(fid);

            % Create the run_14_merge_burst_igram files 
            fid = fopen([miesar_para.WK,'/configs_files_tmp/config_merge_igram_',IFG{i1,1},'_',IFG{i1,2}],'w');
            fprintf(fid,'[Common]\n');
            fprintf(fid,'##########################\n');
            fprintf(fid,'###################################\n');
            fprintf(fid,'[Function-1]\n');
            fprintf(fid,'mergeBursts :\n');
            fprintf(fid,'stack : %s/stack\n',miesar_para.WK);
            fprintf(fid,'inp_reference : %s/interferograms/%s_%s\n',miesar_para.WK,IFG{i1,1},IFG{i1,2});
            fprintf(fid,'dirname : %s/interferograms/%s_%s\n',miesar_para.WK,IFG{i1,1},IFG{i1,2});
            fprintf(fid,'name_pattern : fine*int\n');
            fprintf(fid,'outfile : %s/merged/interferograms/%s_%s/fine.int\n',miesar_para.WK,IFG{i1,1},IFG{i1,2});
            fprintf(fid,'method : top\n');
            fprintf(fid,'aligned : True\n');
            fprintf(fid,'valid_only : True\n');
            fprintf(fid,'use_virtual_files : True\n');
            fprintf(fid,'multilook : True\n');
            fprintf(fid,'range_looks : %1.0f\n',range_looks);
            fprintf(fid,'azimuth_looks : %1.0f\n',azimuth_looks);
            fclose(fid); 

            % Create the run_15_filter_coherence files 
            fid = fopen([miesar_para.WK,'/configs_files_tmp/config_igram_filt_coh_',IFG{i1,1},'_',IFG{i1,2}],'w');
            fprintf(fid,'[Common]\n');
            fprintf(fid,'##########################\n');
            fprintf(fid,'###################################\n');
            fprintf(fid,'[Function-1]\n');
            fprintf(fid,'FilterAndCoherence :\n');
            fprintf(fid,'input : %s/merged/interferograms/%s_%s/fine.int\n',miesar_para.WK,IFG{i1,1},IFG{i1,2});
            fprintf(fid,'filt : %s/merged/interferograms/%s_%s/filt_fine.int\n',miesar_para.WK,IFG{i1,1},IFG{i1,2});
            fprintf(fid,'coh : %s/merged/interferograms/%s_%s/filt_fine.cor\n',miesar_para.WK,IFG{i1,1},IFG{i1,2});
            fprintf(fid,'strength : %1.2f\n',strength);
            fprintf(fid,'slc1 : %s/merged/SLC/%s/%s.slc.full\n',miesar_para.WK,IFG{i1,1},IFG{i1,1});
            fprintf(fid,'slc2 : %s/merged/SLC/%s/%s.slc.full\n',miesar_para.WK,IFG{i1,2},IFG{i1,2});
            fprintf(fid,'complex_coh : %s/merged/interferograms/%s_%s/fine.cor\n',miesar_para.WK,IFG{i1,1},IFG{i1,2});
            fprintf(fid,'range_looks : %1.0f\n',range_looks);
            fprintf(fid,'azimuth_looks : %1.0f\n',azimuth_looks);
            fclose(fid); 

            % Create the run_16_unwrap files 
            fid = fopen([miesar_para.WK,'/configs_files_tmp/config_igram_unw_',IFG{i1,1},'_',IFG{i1,2}],'w');
            fprintf(fid,'[Common]\n');
            fprintf(fid,'##########################\n');
            fprintf(fid,'###################################\n');
            fprintf(fid,'[Function-1]\n');
            fprintf(fid,'unwrap :\n');
            fprintf(fid,'ifg : %s/merged/interferograms/%s_%s/filt_fine.int\n',miesar_para.WK,IFG{i1,1},IFG{i1,2});
            fprintf(fid,'unw : %s/merged/interferograms/%s_%s/filt_fine.unw\n',miesar_para.WK,IFG{i1,1},IFG{i1,2});
            fprintf(fid,'coh : %s/merged/interferograms/%s_%s/filt_fine.cor\n',miesar_para.WK,IFG{i1,1},IFG{i1,2});
            fprintf(fid,'nomcf : False\n');
            fprintf(fid,'reference : %s/reference\n',miesar_para.WK);
            fprintf(fid,'defomax : 2\n');
            fprintf(fid,'rlks : %1.0f\n',range_looks);
            fprintf(fid,'alks : %1.0f\n',azimuth_looks);
            fprintf(fid,'rmfilter : False\n');
            fprintf(fid,'method : snaphu\n');
            fclose(fid); 
        end

        disp('Creation of config files: OKAY')

        % Create the run files
        disp('Creation of the run file:')

        scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];
        fid = fopen(scripttoeval,'w');

        for i1 = 1 : length(dateslc)
            fprintf(fid,'SentinelWrapper.py -c %s\n',[miesar_para.WK,'/configs_files_tmp/config_merge_',dateslc{i1}]);
        end
        for i1 = 1 : length(paralist)
            fprintf(fid,'SentinelWrapper.py -c %s\n',[miesar_para.WK,'/configs_files_tmp/config_merge_',paralist{i1}]);
        end
        for i1 = 1 : size(IFG,1)
            fprintf(fid,'SentinelWrapper.py -c %s\n',[miesar_para.WK,'/configs_files_tmp/config_generate_igram_',IFG{i1,1},'_',IFG{i1,2}]);
        end
        for i1 = 1 : size(IFG,1)
            fprintf(fid,'SentinelWrapper.py -c %s\n',[miesar_para.WK,'/configs_files_tmp/config_merge_igram_',IFG{i1,1},'_',IFG{i1,2}]);
        end
        for i1 = 1 : size(IFG,1)
            fprintf(fid,'SentinelWrapper.py -c %s\n',[miesar_para.WK,'/configs_files_tmp/config_igram_filt_coh_',IFG{i1,1},'_',IFG{i1,2}]);
        end
        for i1 = 1 : size(IFG,1)
            fprintf(fid,'SentinelWrapper.py -c %s\n',[miesar_para.WK,'/configs_files_tmp/config_igram_unw_',IFG{i1,1},'_',IFG{i1,2}]);
        end

        fclose(fid);

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



