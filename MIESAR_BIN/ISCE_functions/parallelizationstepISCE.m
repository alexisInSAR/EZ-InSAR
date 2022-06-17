function [modepara] = parallelizationstepISCE(namestep,miesar_para)
%   Function to run, in parallel, the ISCE processing 
%
%   See also ISCEPROCESSING, PARALLELIZATIONSTEPISCE, RUNISCEALLSTEP,
%   CHECKIPF.py.

%   Copyright 2021 Alexis Hrysiewicz, UCD / iCRAG2 
%   Version: 1.0.0 
%   Date: 30/11/2021

%% Define the step name

% For SLC stack and IFG stack
stepara = {'run_02_unpack_secondary_slc',...
    'run_05_overlap_geo2rdr',...
    'run_06_overlap_resample',...
    'run_07_pairs_misreg',...
    'run_09_fullBurst_geo2rdr',...
    'run_10_fullBurst_resample',...
    'run_12_merge_reference_secondary_slc',...
    'run_12_unwrap',...
    'run_13_grid_baseline',...
    'run_13_generate_burst_igram',...
    'run_14_merge_burst_igram',...
    'run_15_filter_coherence',...
    'run_15_filter_coherence'}; 

%% Find the index of the selected step(s)
Index = find(cellfun(@(s) ~isempty(strfind(namestep, s)), stepara)==1); 

if isempty(Index)==1
    warning(sprintf('The %s step cannot be parallelized.',namestep));
    modepara = 0;
else
    modepara = 1;
    
    % Ask the number of jobs
    prompt = {sprintf('Number of jobs for %s step',namestep)};
    dlgtitle = 'Parallelization Parameters';
    dims = [1 35];
    definput = {num2str(fix(feature('numcores')./2))}; %50 % of core number
    answer = inputdlg(prompt,dlgtitle,dims,definput);
    hmax = str2num(answer{1});
    if isempty(hmax)==1
        error('The number of core must be a number.');
    end
    
    %Threshold regarding the number of cores
    if hmax > feature('numcores')
        error('The number of core must be lower than the number of available cores.');
    end 
    
    % Write the job files
    fid = fopen([miesar_para.WK,'/run_files/',namestep],'r');
    file = textscan(fid,'%s %s %s'); fclose(fid);
    fid = fopen([miesar_para.WK,'/run_files/',namestep,'_para'],'w');
    h = 1;
    for i1 = 1 : length(file{1})
        if h == hmax
            fprintf(fid,'%s %s %s %s\n',file{1}{i1},file{2}{i1},file{3}{i1},'&');
            fprintf(fid,'wait\n');
            h = 1;
        else
        	fprintf(fid,'%s %s %s %s\n',file{1}{i1},file{2}{i1},file{3}{i1},'&');
        end
        h = h + 1;
    end
    fprintf(fid,'wait\n');
    fclose(fid);
    system(['chmod a+x ',miesar_para.WK,'/run_files/',namestep,'_para']);
end
end
