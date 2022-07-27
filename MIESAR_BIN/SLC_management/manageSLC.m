function manageSLC(src,evt,action,miesar_para)
%   manageSLC(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to manage the SLCs.
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also createlistSLC, GUIpathdirectory, displayextensionS1, initparmslc, readxmlannotationS1, displayextensionTSXPAZ, manageparamaterSLC, downloaderSLC, manageSLC.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 29/11/2021
%
%   -------------------------------------------------------
%   Modified:
%           - Xiaowen Wang, UCD, 02/03/2022: bug fix
%           - Alexis Hrysiewicz, UCD / iCRAG, 07/07/2022: StripMap
%           implementation
%           - Alexis Hrysiewicz, UCD / iCRAG, 18/07/2022: modifcation of
%           text information
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)
%           2.0.0 Beta: Initial (unreleased)

switch action
    
    case 'checking'
        %% Check the available SLCs 
        si = ['Create the SLC list:... '];
        update_textinformation([],[],[],si,'information');

        createlistSLC([],[],[],miesar_para);

        si = ['Create the SLC list: OKAY '];
        update_textinformation([],[],[],si,'success');

    case 'opening'
        %% Open the list of SLCs
        
        % Open the variables
        % For the SLC parameters
        paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
        % For the SLC list (check if this file is okay)
        if exist([miesar_para.WK,'/SLC.list'])
            fid = fopen([miesar_para.WK,'/SLC.list'],'r');
            list = textscan(fid,['%s %s %s %s %s %s %s %s']); fclose(fid);
        else
            si = ['The SLC list is not present.'];
            update_textinformation([],[],[],si,'error')
            error('The SLC list is not present.');
        end
        
        %Creation of the table to be displayed
        rescell = cell(1);
        for i1 = 1 : length(list{1})
            c = [];
            for i2 = 1 : length(list)-1
                c = [c,'   ',list{i2}{i1}];
            end
            if exist([paramslc.pathSLC,'/',list{1}{i1},'.zip']) == 2 | exist([paramslc.pathSLC,'/',list{1}{i1},'.SAFE']) == 7 | exist([paramslc.pathSLC,'/',list{1}{i1}]) == 7
                rescell{i1} = ['<HTML><FONT color="green">',c,'</Font></html>'];
            else
                rescell{i1} = ['<HTML><FONT color="red">',c,'</Font></html>'];
            end
        end
        
        % Display the table using a new GUI
        si = ['The SLC list is displayed.'];
        update_textinformation([],[],[],si,'success'); 
        figi = figure('name','List of available SLCs','numbertitle','off','MenuBar', 'none','ToolBar','none');
        figi.Position = [111 147 891 651];
        uicontrol('Style','list', 'Position',[29 18 840 617], 'String',rescell);
        
    case 'extension'
        %% Display the SLC extension
        if exist([miesar_para.WK,'/SLC.list'])

            si = ['Display the extension of SLCs ...'];
            update_textinformation([],[],[],si,'information'); 

            paramslc = load([miesar_para.WK,'/parmsSLC.mat']); fid = fopen([miesar_para.WK,'/SLC.list'],'r');

            if strcmp(paramslc.mode,'S1_IW') == 1
                displayextensionS1(src,evt,'S1_IW',miesar_para)
            elseif strcmp(paramslc.mode,'S1_SM') == 1
                displayextensionS1(src,evt,'S1_SM',miesar_para)
            elseif strcmp(paramslc.mode,'TSX_SM') == 1 | strcmp(paramslc.mode,'TSX_SPT') == 1 | strcmp(paramslc.mode,'PAZ_SM') == 1 | strcmp(paramslc.mode,'PAZ_SPT') == 1
                displayextensionTSXPAZ(src,evt,[],miesar_para)
            elseif strcmp(paramslc.mode,'CSK_SM') == 1 | strcmp(paramslc.mode,'CSM_SPT') == 1
                displayextensionCSK(src,evt,[],miesar_para)
            end 

            si = ['Display the extension of SLCs: OKAY'];
            update_textinformation([],[],[],si,'success'); 

        else

            % Information
            si = ['Please, checking the available SLC ...'];
            update_textinformation([],[],[],si,'error'); 

        end
        
    case 'alldownloading'
        %% Download the SLCs
        downloaderSLC(miesar_para)
        
end
end

