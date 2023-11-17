function managePOLTSXPAZ(src,evt,action,miesar_para)
%   managePOLTSXPAZ(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to manage the dual-polarisation images from TSX and PAZ.
%
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also createlistSLC, GUIpathdirectory, displayextensionS1, initparmslc, readxmlannotationS1, displayextensionTSXPAZ, manageparamaterSLC, downloaderSLC, manageSLC.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.1.0 Beta
%   Date: 28/09/2023
%
%   -------------------------------------------------------
%   Version history:
%           2.1.0 Beta: Initial (unreleased)

switch action

    case 'init'

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


        % Create the GUI
        figpolTSX = uifigure('Position',[503 313 825 458],'Name','TerraSAR-X/PAZ: Selection of the polarisation','HandleVisibility','on','Visible','on');
        gridfigpolTSX = uigridlayout(figpolTSX,[6 4]);
        figpolTSX.UserData = miesar_para;

        logowarning = uiimage(gridfigpolTSX,'ImageSource','private/warning.png');
        logowarning.Layout.Row = [1 3];
        logowarning.Layout.Column = [1];

        maintitle = uilabel(gridfigpolTSX,'Text','TerraSAR-X/PAZ: Selection of the polarisation','HorizontalAlignment','center','VerticalAlignment','center','FontSize',25,'FontWeight','bold');
        maintitle.Layout.Row = [1];
        maintitle.Layout.Column = [2 4];

        maintext = uilabel(gridfigpolTSX,'Text','The dual-polarisation images have been detected. EZ-InSAR is able to process only a single polarisation. Please select the desired polarisation and the directory for the linked files. The SLC path will be changed: if you want to recreate the SLC list, do not forget to change the SLC path by the original directory.','HorizontalAlignment','left','VerticalAlignment','center','FontSize',15,'WordWrap','on');
        maintext.Layout.Row = [2 3];
        maintext.Layout.Column = [2 4];

        pollabel = uilabel(gridfigpolTSX,'Text','Polarisation:','HorizontalAlignment','left','VerticalAlignment','center','FontSize',15,'FontWeight','bold','WordWrap','on');
        pollabel.Layout.Row = [4];
        pollabel.Layout.Column = [1];

        polselection = uidropdown(gridfigpolTSX,'Tag','polselection','Enable','on');
        polselection.Layout.Row = [4];
        polselection.Layout.Column = [2 4];

        pol_list = unique([unique(list{end-2}); unique(list{end-1})]);
        pol_list(strcmp(pol_list,'None')) = [];
        polselection.Items = pol_list;
        polselection.Value = pol_list{1};
        polselection.Tooltip = 'Click to select the polarisation.';

        pathlabel = uilabel(gridfigpolTSX,'Text','Path of linked files:','HorizontalAlignment','left','VerticalAlignment','center','FontSize',15,'FontWeight','bold','WordWrap','on');
        pathlabel.Layout.Row = [5];
        pathlabel.Layout.Column = [1];

        patheditfield = uieditfield(gridfigpolTSX,'text','Tag','patheditfield');
        patheditfield.Layout.Row = [5];
        patheditfield.Layout.Column = [2 4];
        patheditfield.Value = [paramslc.WK,'/slc_link_one_pol'];

        btrunpol = uibutton(gridfigpolTSX,'Text','Run the selection of polarisation','Tag','btrunpol');
        btrunpol.ButtonPushedFcn = @(src,evt,arg1,arg2) managePOLTSXPAZ([],[],'runpol',figpolTSX);
        btrunpol.Layout.Row = [6];
        btrunpol.Layout.Column = [1 4];
        btrunpol.Tooltip = 'Click to split the data';


    case 'runpol'
        figpolTSX= miesar_para; 
        miesar_para = figpolTSX.UserData;

        paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
        set(findobj(figpolTSX,'Tag','polselection'),'Enable','off');
        set(findobj(figpolTSX,'Tag','patheditfield'),'Enable','off');
        set(findobj(figpolTSX,'Tag','btrunpol'),'Enable','off');

        poltag = get(findobj(figpolTSX,'Tag','polselection'),'Value');
        pathfileslinked = get(findobj(figpolTSX,'Tag','patheditfield'),'Value');

        paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
        fid = fopen([miesar_para.WK,'/SLC.list'],'r');
        list = textscan(fid,['%s %s %s %s %s %s %s %s']); fclose(fid);
        
        if exist([pathfileslinked]) == 0
            mkdir(pathfileslinked);
        else 
            rmdir(pathfileslinked,'s');
        end 

        % In Unix language (easier) (link the files)
        for i1 = 1 : length(list{1})
            if exist([pathfileslinked,'/',list{1}{i1}]) == 0
                mkdir([pathfileslinked,'/',list{1}{i1}]);
            end 

            if exist([pathfileslinked,'/',list{1}{i1},'/ANNOTATION']) == 0
                mkdir([pathfileslinked,'/',list{1}{i1},'/ANNOTATION']);
            end 
            system(['ln -s ',[paramslc.pathSLC,'/',list{1}{i1},'/ANNOTATION/GEOREF.xml'],' ',[pathfileslinked,'/',list{1}{i1},'/ANNOTATION/GEOREF.xml']]);
            system(['ln -s ',[paramslc.pathSLC,'/',list{1}{i1},'/ANNOTATION/*',upper(poltag),'*'],' ',[pathfileslinked,'/',list{1}{i1},'/ANNOTATION/.']]);

            if exist([pathfileslinked,'/',list{1}{i1},'/AUXRASTER']) == 0
                mkdir([pathfileslinked,'/',list{1}{i1},'/AUXRASTER']);
            end 
            system(['ln -s ',[paramslc.pathSLC,'/',list{1}{i1},'/AUXRASTER/stdcalcomposite_MRES*'],' ',[pathfileslinked,'/',list{1}{i1},'/AUXRASTER/.']])
            system(['ln -s ',[paramslc.pathSLC,'/',list{1}{i1},'/AUXRASTER/*',upper(poltag),'*'],' ',[pathfileslinked,'/',list{1}{i1},'/AUXRASTER/.']]);

            if exist([pathfileslinked,'/',list{1}{i1},'/IMAGEDATA']) == 0
                mkdir([pathfileslinked,'/',list{1}{i1},'/IMAGEDATA']);
            end 
            system(['ln -s ',[paramslc.pathSLC,'/',list{1}{i1},'/IMAGEDATA/*',upper(poltag),'*'],' ',[pathfileslinked,'/',list{1}{i1},'/IMAGEDATA/.']]);

            if exist([pathfileslinked,'/',list{1}{i1},'/PREVIEW']) == 0
                mkdir([pathfileslinked,'/',list{1}{i1},'/PREVIEW']);
            end 
            system(['ln -s ',[paramslc.pathSLC,'/',list{1}{i1},'/PREVIEW/BROWSE*'],' ',[pathfileslinked,'/',list{1}{i1},'/PREVIEW/.']]);
            system(['ln -s ',[paramslc.pathSLC,'/',list{1}{i1},'/PREVIEW/COMPOSITE_QL*'],' ',[pathfileslinked,'/',list{1}{i1},'/PREVIEW/.']]);
            system(['ln -s ',[paramslc.pathSLC,'/',list{1}{i1},'/PREVIEW/MAP_PLOT*'],' ',[pathfileslinked,'/',list{1}{i1},'/PREVIEW/.']]);
            system(['ln -s ',[paramslc.pathSLC,'/',list{1}{i1},'/PREVIEW/*',upper(poltag),'*'],' ',[pathfileslinked,'/',list{1}{i1},'/PREVIEW/.']]);

            if exist([pathfileslinked,'/',list{1}{i1},'/SUPPORT']) == 0
                mkdir([pathfileslinked,'/',list{1}{i1},'/SUPPORT']);
            end 
            system(['ln -s ',[paramslc.pathSLC,'/',list{1}{i1},'/SUPPORT/*'],' ',[pathfileslinked,'/',list{1}{i1},'/SUPPORT/.']]);

            % system(['ln -s ',[paramslc.pathSLC,'/',list{1}{i1},'/*.xml'],' ',[pathfileslinked,'/',list{1}{i1},'/.']]);

            listxml = dir([paramslc.pathSLC,'/',list{1}{i1},'/*1_SAR_*.xml']); 
            splitTSXPAZdualpolheader([paramslc.pathSLC,'/',list{1}{i1},'/',listxml(1).name],[pathfileslinked,'/',list{1}{i1},'/',listxml(1).name],upper(poltag))

        end 

        % Modification of the SLC path
        paramslc.pathSLC = pathfileslinked;
        save([miesar_para.WK,'/parmsSLC.mat'],'-STRUCT','paramslc');

        % Close the window
        close(figpolTSX)


end