function mintpy_create_deramp_mask
%   mintpy_create_deramp_mask
%
%       Function to create a mask from user input for the MintPy
%       processing, via GUI. 
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also mintpy_allstep, mintpy_API_tsplottrans, mintpy_parameters, mintpy_API_plot_trans, mintpy_API_plottrans, mintpy_processing, mintpy_API_save, mintpy_network_plot.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 17/02/2022
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initiale (unreleased)

%% Find the MIESAR parameters
try 
    a = gcf; 
    miesar_para = a.UserData; 
catch 
    error('No MIESAR opened or active.')
end 

if exist([miesar_para.WK,'/mintpydirectory.log']) == 2
    fi = fopen([miesar_para.WK,'/mintpydirectory.log'],'r');
    pathmintpyprocessing = textscan(fi,'%s'); fclose(fi); pathmintpyprocessing = pathmintpyprocessing{1}{1};
else
    error('No processing for MintPy'); 
end 

%% Copy the mask
if exist([pathmintpyprocessing,'/maskTempCoh.h5']) == 2
    copyfile([pathmintpyprocessing,'/maskTempCoh.h5'],[pathmintpyprocessing,'/maskTempCoh_mod.h5'])
else
    error('The file maskTempCoh.h5 has not been created.'); 
end  

%% Read the initial mask
im = h5read([pathmintpyprocessing,'/maskTempCoh_mod.h5'], '/mask')';
imbin = zeros(size(im));
Index = find(cellfun(@(s) ~isempty(strfind('TRUE', s)), im)==1);
imbin(Index) = 1;
[X,Y] = meshgrid(1:size(imbin,1),1:size(imbin,2));

%% Conversion of the height image for visualisation
cmd = ['save_roipac.py ',pathmintpyprocessing,'/inputs/geometryRadar.h5 height -o tmp']

scripttoeval = ['scripttoeval_',miesar_para.id,'.sh'];
fid = fopen(scripttoeval,'w');
fprintf(fid,'%s\n',cmd);
fclose(fid);
% Run the script
system(['chmod a+x ',scripttoeval]);
if strcmp(computer,'MACI64') == 1
    % system('./runmacterminal.sh');
else
    system(['./',scripttoeval]);
end
try
    delete(scripttoeval)
end

% Read the image to display
fimdisplay = fopen('tmp','r'); imdisplay = fread(fimdisplay,[size(imbin,2) size(imbin,1)],'float32')'; fclose(fimdisplay);                                
delete tmp
delete tmp.rsc

%% Run the application
figmasking = uifigure('Position',[200 100 1000 500],'Name','Masking tool for MintPy');
glfigmasking = uigridlayout(figmasking,[6 9]);

mainaxisfigmasking = uiaxes(glfigmasking);
mainaxisfigmasking.Layout.Row = [1 6];
mainaxisfigmasking.Layout.Column = [1 6];

imagesc(mainaxisfigmasking,X(1,:),Y(:,1),imdisplay,'Tag','Elevation_map'); colormap(mainaxisfigmasking,'gray'); ci = colorbar(mainaxisfigmasking); ylabel(ci,'Elevation [m]'); xlabel(mainaxisfigmasking,'X'); ylabel(mainaxisfigmasking,'Y');

titlefigmasking = uilabel(glfigmasking,'Text','Masking tool for MintPy','HorizontalAlignment','center','VerticalAlignment','center','FontSize',20,'FontWeight','bold');
titlefigmasking.Layout.Row = [1];
titlefigmasking.Layout.Column = [7 9];

listpolyfigmasking = uilistbox(glfigmasking);
listpolyfigmasking.Layout.Row = [2 4];
listpolyfigmasking.Layout.Column = [7 9];
listpolyfigmasking.Items = {''};
listpolyfigmasking.Value = '';
listpolyfigmasking.ValueChangedFcn = @(src,evt) run_plot_poly(src,evt);

newbtfigmasking = uibutton(glfigmasking,'Text','New');
newbtfigmasking.Layout.Row = [5];
newbtfigmasking.Layout.Column = [7];
newbtfigmasking.ButtonPushedFcn = @(src,evt,arg1) run_new_poly_mask(src,evt,'new');

removebtfigmasking = uibutton(glfigmasking,'Text','Remove');
removebtfigmasking.Layout.Row = [5];
removebtfigmasking.Layout.Column = [8];
removebtfigmasking.ButtonPushedFcn = @(src,evt,arg1) run_new_poly_mask(src,evt,'remove');

validebtfigmasking = uibutton(glfigmasking,'Text','Validation');
validebtfigmasking.Layout.Row = [5];
validebtfigmasking.Layout.Column = [9];
validebtfigmasking.ButtonPushedFcn = @(src,evt,arg1) run_new_poly_mask(src,evt,'save');

runmaskbtfigmasking = uibutton(glfigmasking,'Text','MASK');
runmaskbtfigmasking.Layout.Row = [6];
runmaskbtfigmasking.Layout.Column = [9];
runmaskbtfigmasking.ButtonPushedFcn = @(src,evt,arg1) run_mask_poly(src,evt,'mintpy');

displaymaskcohfigmasking = uibutton(glfigmasking,'state','Text','Display the coh. mask)');
displaymaskcohfigmasking.Layout.Row = [6];
displaymaskcohfigmasking.Layout.Column = [7 8];
displaymaskcohfigmasking.ValueChangedFcn = @(src,evt) run_display_mask_tempcoh(src,evt);

para_mask = struct('Name','','x',[],'y',[]);
validebtfigmasking.Enable = 'off';

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Other functions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Function to display the mask from the temporal coherence
    function run_display_mask_tempcoh(src,evt)
        if displaymaskcohfigmasking.Value == 1
            hold(mainaxisfigmasking,"on");
            hmaskincoh = imagesc(mainaxisfigmasking,X(1,:),Y(:,1),imbin,"AlphaData",imbin,'Tag','cohmask_map');
            hold(mainaxisfigmasking,"off");
            run_plot_poly(src,evt)
        else
            delete(findobj(mainaxisfigmasking,'Tag','cohmask_map'))
        end
    end

%% Function to create the nez poly
    function run_new_poly_mask(src,evt,action)
        switch action
            case 'new'
                newbtfigmasking.Enable = 'off'; 
                removebtfigmasking.Enable = 'off'; 
                validebtfigmasking.Enable = 'on';
                runmaskbtfigmasking.Enable = 'off';
                displaymaskcohfigmasking.Enable = 'off';

                htmp = drawpolygon(mainaxisfigmasking,'Deletable',false);
            case 'save'
                htmp = findobj(mainaxisfigmasking,'Type','images.roi.polygon');
                xtmp = htmp.Position(:,1); xtmp = [xtmp; xtmp(1)];
                ytmp = htmp.Position(:,2); ytmp = [ytmp; ytmp(1)];
                
                if length(xtmp) > 2
                    lgstruct = size(para_mask,2);

                    if isempty(para_mask(1).Name) == 1
                        para_mask(1).Name = ['Poly_',num2str(1)];
                        para_mask(1).x = xtmp;
                        para_mask(1).y = ytmp;
                    elseif lgstruct == 1 && isempty(para_mask(1).Name) == 0
                        para_mask(lgstruct+1).Name = ['Poly_',num2str(lgstruct+1)];
                        para_mask(lgstruct+1).x = xtmp;
                        para_mask(lgstruct+1).y = ytmp;
                    else
                        para_mask(lgstruct+1).Name = ['Poly_',num2str(lgstruct+1)];
                        para_mask(lgstruct+1).x = xtmp;
                        para_mask(lgstruct+1).y = ytmp;
                    end

                    name_items = cell(1);
                    for i1 = 1 : size(para_mask,2)
                        name_items{i1} = para_mask(i1).Name;
                    end
                    listpolyfigmasking.Items = name_items;
                end
                delete(htmp);
                run_plot_poly([],[])
 
                newbtfigmasking.Enable = 'on'; 
                removebtfigmasking.Enable = 'on'; 
                validebtfigmasking.Enable = 'off';
                runmaskbtfigmasking.Enable = 'on';
                displaymaskcohfigmasking.Enable = 'on';

            case 'remove' 
                for i1 = 1 : size(para_mask,2)
                    if strcmp(listpolyfigmasking.Value,para_mask(i1).Name) == 1
                        para_mask(i1) = []; 
                    end 
                end
                run_plot_poly([],[])

                name_items = cell(1); 
                for i1 = 1 : size(para_mask,2)
                    name_items{i1} = para_mask(i1).Name; 
                end

                if isempty(name_items{1}) == 1
                    listpolyfigmasking.Items = {''}; 
                    para_mask = struct('Name','','x',[],'y',[]);
                else 
                    listpolyfigmasking.Items = name_items; 
                end 
        end
    end

%% Function to plot the new poly
    function run_plot_poly(src,evt)
        htmp = findobj(mainaxisfigmasking,'Type','line');
        delete(htmp)
        for i1 = 1 : size(para_mask,2)
            if strcmp( listpolyfigmasking.Value,para_mask(i1).Name) == 1
                hold(mainaxisfigmasking,'on'); plot(mainaxisfigmasking,para_mask(i1).x,para_mask(i1).y,'-'); hold(mainaxisfigmasking,'off');
            else
                hold(mainaxisfigmasking,'on'); plot(mainaxisfigmasking,para_mask(i1).x,para_mask(i1).y,'--'); hold(mainaxisfigmasking,'off');
            end
        end 

    end

%% Function to mask and modify the parameters files
    function run_mask_poly(src,evt,action)
        switch action
            case 'mintpy'
                for i1 = 1 : size(para_mask,2)
                        if i1 == 1                 
                            mask = inpolygon(X,Y,para_mask(i1).x,para_mask(i1).y);
                        else
                           mask = mask + inpolygon(X,Y,para_mask(i1).x,para_mask(i1).y) ;
                        end 
                end
                mask(mask>1) = 1; 
                ni = find(mask==1); 
                imbinbis = imbin;
                imbinbis(ni) = 0;
                imbinbis = int8(imbinbis)';

                % Save
                fileh5       = [pathmintpyprocessing,'/maskTempCoh_mod.h5'];
                dataset      = '/mask';

                fileattrib(fileh5,'+w');
                plist = 'H5P_DEFAULT';
                fid = H5F.open(fileh5,'H5F_ACC_RDWR',plist);
                dset_id = H5D.open(fid,dataset);
                H5D.write(dset_id,'H5ML_DEFAULT','H5S_ALL','H5S_ALL',plist,imbinbis);
                H5D.close(dset_id);
                H5F.close(fid);

                % Define the name of .cgf
                paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
                switch paramslc.pass
                    case 'Asc'
                        Porb = 'A';
                    case 'Desc'
                        Porb = 'D';
                end
                name_cfg = ['mintpyfullparametersSen',Porb,'T',paramslc.track,'.cfg'];

                % Modification of cfg file 
                mintpy_full_parameters = load([pathmintpyprocessing,'/mintpy_full_parameters.mat']);
                mintpy_full_parameters.mintpy.deramp.maskFile.value = 'maskTempCoh_mod.h5'; 

                save([pathmintpyprocessing,'/mintpy_full_parameters.mat'],'-STRUCT','mintpy_full_parameters');
                % Write the .cfg file
                fi = fopen([pathmintpyprocessing,'/',name_cfg],'w');
                fprintf(fi,'# vim: set filetype=cfg:\n');
                fprintf(fi,'##------------------------ %s ------------------------##\n',name_cfg);
                value_parameter = 'NULL'; 
                info_parameter = 'NULL'; 
                for i1 = 1 : length(mintpy_full_parameters.list)
                    name_parameter = mintpy_full_parameters.list{i1}; 
                    eval(['value_parameter = mintpy_full_parameters.',name_parameter,'.value;']);
                    eval(['info_parameter = mintpy_full_parameters.',name_parameter,'.info;']);

                    %             fprintf(fi,'%s\t\t\t\t=%s %s\n',name_parameter,value_parameter,info_parameter);
                    fprintf(fi,'%s\t\t\t\t= %s\n',name_parameter,value_parameter);
                end
                fclose(fi);
                close(figmasking)
        end

    end
end
