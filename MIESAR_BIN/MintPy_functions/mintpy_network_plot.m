function mintpy_network_plot(src,evt,action,miesar_para)
%   Function to check the network from MintPy processing
%
%   See also mintpy_allstep, mintpy_API_tsview, mintpy_parameters, mintpy_API_plot_trans, mintpy_API_view, mintpy_processing, mintpy_API_save, mintpy_network_plot.
%
%   Copyright 2022 Alexis Hrysiewicz, UCD / iCRAG2
%   Version: 1.0.0
%   Date: 17/02/2020

% Load the MintPy directory
fi = fopen([miesar_para.WK,'/mintpydirectory.log'],'r');
pathmintpyprocessing = textscan(fi,'%s'); fclose(fi); pathmintpyprocessing = pathmintpyprocessing{1}{1};

% Check the network from MintPy is here.
if exist([pathmintpyprocessing,'/network.pdf'])
    action = 'isce_base';
    actionbis = 'mintpy';
else
    action = 'isce_base';
    actionbis = 'NONE';
end

%% Display the network from ISCE
switch action
    case 'isce_base'

        % List the baselines from single master stack
        list_SM_stack = dir([miesar_para.WK,'/baselines']);

        % Read the baselines
        dmaster = [];
        dslave = [];
        baselines = [];
        for i1 = 1 : length(list_SM_stack)
            name = list_SM_stack(i1).name;
            if length(name) == 17
                namesplit = strsplit(name,'_');
                dmaster = [dmaster; datetime(namesplit{1},'InputFormat','yyyyMMdd')];
                dslave = [dslave; datetime(namesplit{2},'InputFormat','yyyyMMdd')];
                bperpi = [];
                fid = fopen([miesar_para.WK,'/baselines/',name,'/',name,'.txt'],'rt');
                while true
                    thisline = fgetl(fid);
                    if ~ischar(thisline); break; end
                    if contains(thisline,'Bperp')
                        thisline = strsplit(thisline,' ');
                        bperpi = [bperpi; str2num(thisline{3})];
                    end
                end
                fclose(fid);
                baselines = [baselines; [0 mean(bperpi)]];
            end
        end

        % Open the list of computed interfergrams from ISCE
        list_ifg = dir([miesar_para.WK,'/merged/interferograms']);
        difgmaster = [];
        difgslave = [];
        for i1 = 1 : length(list_ifg)
            name = list_ifg(i1).name;
            if length(name) == 17
                namesplit = strsplit(name,'_');
                difgmaster = [difgmaster; datetime(namesplit{1},'InputFormat','yyyyMMdd')];
                difgslave = [difgslave; datetime(namesplit{2},'InputFormat','yyyyMMdd')];
            end
        end
        difgmaster = datenum(difgmaster);
        difgslave = datenum(difgslave);

        % Manage the network
        SM = unique([[datenum(dmaster); datenum(dslave)] [baselines(:,1); baselines(:,2)]],'rows');

        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %Extract from sb_baseline_plot.m (STAMPS scripts)
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        n_ifg=size(difgmaster,1);
        [yyyymmdd,I,J]=unique([difgmaster difgslave]);
        ifg_ix=reshape(J,n_ifg,2);
        x=ifg_ix(:,1);
        y=ifg_ix(:,2);
        [B,I]=intersect(SM(:,1),yyyymmdd);
        x=I(x);
        y=I(y);
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        % Display
        figi = figure('name','Computed Interferogram network from ISCE','numbertitle','off');
        figi.Position = [159 77 1400 882];
        axi = gca;
        set(findobj(gcf,'Tag','name_progressbar'),'Text','Display the interferogram network.'); drawnow; pause(0.01);
        for i1=1:length(x)
            l=line(axi,datetime([SM(x(i1),1),SM(y(i1),1)],'ConvertFrom','datenum'),[SM(x(i1),2),SM(y(i1),2)]);
            set(l,'color',[0 0 0],'linewidth',1);

            if i1./(fix(length(x)./10)) == fix(i1./fix(length(x)./10))
                set(findobj(gcf,'Tag','progressbar'),'Value',(i1./length(x)).*100);
            end
            
        end

        hold(axi,'on'); p = plot(axi,datetime(SM(:,1),'ConvertFrom','datenum'),SM(:,2),'ro');
        pbis = plot(axi,unique(dmaster),0,'bo');
        set(p,'markersize',12,'linewidth',2);
        set(pbis,'markersize',12,'linewidth',2);
        hold(axi,'off');
        ylabel(axi,'B_{perp}')
        xlabel(axi,'Time');
        axi.FontSize = 15; axi.FontWeight = 'bold';
        grid(axi,'on');
        yil = get(axi,'Ylim');
        xil = get(axi,'Xlim');
        hold(axi,'on');
        text(axi,xil(1)+(xil(2)-xil(1)).*0.8,yil(1)+(yil(2)-yil(1)).*0.9,sprintf('Number of ifgs: %d',length(x)),'FontSize',20,'Color','red','FontWeight','bold');
        hold(axi,'off');
        title('Computed Interferogram network from ISCE (average baselines)');

end

%% Display the network from MintPy
switch actionbis
    case 'mintpy'
        % Conversion of pdf to jpg
        cmd = ['pdftoppm -jpeg -r 500 ',[pathmintpyprocessing,'/network.pdf'],' ',[pathmintpyprocessing,'/network.jpg']];
        system(cmd);

        % Display the images
        figi = figure('name','Selected Interferogram network from MintPy','numbertitle','off');
        figi.Position = [159 77 1400 882];
        axi = gca;
        im = imread([pathmintpyprocessing,'/network.jpg-1.jpg']);
        imshow(im);
        title('Selected Interferogram network from MintPy');
end