function update_help(mode)
%   Function to update the Matlab help
%
%   update_help('user') to add the path in the documentation
%   update_help('dev') to create the .html from the edited .mlx files and
%   add the path in the documentation
%
%   Copyright 2021 Alexis Hrysiewicz, UCD / iCRAG2 
%   Version: 1.0.0 
%   Date: 30/11/2021

if ~(strcmp(mode,'user')) & ~(strcmp(mode,'dev'))
    error('Please, select the correct mode (user or devp')
end 


cur = cd;
rmpath(genpath('help'));

switch mode 
    case 'dev'
        cd('help/html');
        fprintf(1,'Create the .html files...\n')
        
        list_mlx = {'ISPSLink_toolbox_help_mainpage',...
            'ISPS_Link_gs_top',...
            'ISPS_reqts',...
            'ISPS_installation',...
            'ISPSLink_mainpart_installation',...
            'ISPSLink_PP_installation',...
            'ISPS_Link_dev_authors',...
            'ISPS_Link_PP_userguide',...
            'ISPS_Link_mainpart_userguide',...
            'ISPS_Link_userguide',...
            'ISPS_Link_PP_function_ref',...
            'ISPS_Link_mainpart_function_ref',...
            'ISPS_Link_function_ref'}; 
        
        w1 = waitbar(0,'Conversion of files...');
        for i1 = 1 : length(list_mlx)
            matlab.internal.liveeditor.openAndConvert([list_mlx{i1},'.mlx'],[list_mlx{i1},'.html']);
            waitbar(i1./length(list_mlx),w1);
        end 
        close(w1); 
        
    case 'user'
        fprintf(1,'Keep the .html files...\n')
end 

cd(cur);
addpath(genpath('help'));


