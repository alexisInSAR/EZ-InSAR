function runGUISBASnetwork(action,miesar_para)
%   Function to define interferogram network using various possibilities
%   and paramaters. Use the GUISBASnetwork.fig
%
%   See also runGUISBASnetwork, runGUIstampsparameters,
%   stampsMERGEDprocessing, stampsprocessing, stampsPSprocessing,
%   stampsSBASprocessing.

%   Copyright 2021 Alexis Hrysiewicz, UCD / iCRAG2 
%   Version: 1.0.0 
%   Date: 30/11/2021

global axi % It will be nice to modify the code to remove this global variable. 

switch action
   
    case 'init'
        %% Initialisation of the GUI 
        
        % Load the StaMPS directory  
        fi = fopen([miesar_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{2};
        
        % Check if the interfergram list is here, if not: create a defaut
        % list
        if exist([pathstampsprocessing,'/SMALL_BASELINES.list']) == 0
            cur = cd;
            cd(pathstampsprocessing)
            sb_find_mod(0.5,120,1000);
            cd(cur);
        end
        
        % Open the GUI 
        fignet = open('GUISBASnetwork.fig');
        fignet.UserData = miesar_para; 

        axi = findobj(fignet,'Tag','axes1');
        
        % And display
        runGUISBASnetwork('display',[]);
        
    case 'display'
        %% Display the current network
        a = gcf;
        tmp_para = a.UserData; 

        % Load the StaMPS directory
        fi = fopen([tmp_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{2};
        
        % Load the SBAS variables
        small_baseline_flag = 'y';
        cur = cd;
        cd(pathstampsprocessing)
        load psver
        psname=['ps',num2str(psver)];
        cd(cur);
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %Extract from sb_baseline_plot.m (STAMPS scripts)
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        ix=[];
        sb=load([pathstampsprocessing,'/small_baselines.list']);
        n_ifg=size(sb,1);
        if small_baseline_flag=='y' & isempty(ix) & exist('./parms.mat','file')
            drop_ifg_index=getparm('drop_ifg_index');
            if ~isempty(drop_ifg_index)
                ix=setdiff([1:n_ifg],drop_ifg_index);
            end
        end
        if ~isempty(ix)
            sb=sb(ix,:);
        else
            ix=1:size(sb,1);
        end
        ps=load([pathstampsprocessing,'/',psname]);
        n_ifg=size(sb,1);
        [yyyymmdd,I,J]=unique(sb);
        ifg_ix=reshape(J,n_ifg,2);
        x=ifg_ix(:,1);
        y=ifg_ix(:,2);
        day=str2num(datestr(ps.day,'yyyymmdd'));
        [B,I]=intersect(day,yyyymmdd);
        x=I(x);
        y=I(y);
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        % Display the network
        cla(axi)
        wi = waitbar(0,'Display the network ...');
        for i1=1:length(x)
            l=line(axi,[ps.day(x(i1)),ps.day(y(i1))],[ps.bperp(x(i1)),ps.bperp(y(i1))]);
            %text((ps.day(x(i))+ps.day(y(i)))/2,(ps.bperp(x(i))+ps.bperp(y(i)))/2,num2str(ix(i)));
            set(l,'color',[0 0 0],'linewidth',1); 
            
            if i1./(fix(length(x)./10)) == fix(i1./fix(length(x)./10)) 
                waitbar(i1./length(x),wi);
            end 
        end
        close(wi);
        
        hold(axi,'on'); p = plot(axi,ps.day,ps.bperp,'ro');
        set(p,'markersize',12,'linewidth',2);
        hold(axi,'off');
        datetick(axi,'x','yyyy')
        ylabel(axi,'B_{perp}')
        xlabel(axi,'Time');
        axi.FontSize = 15; axi.FontWeight = 'bold';
        grid(axi,'on');
        
        yil = get(axi,'Ylim'); 
        xil = get(axi,'Xlim'); 
        hold(axi,'on');
        title(axi,sprintf('Number of ifgs: %d',length(x)),'FontSize',20,'Color','red','FontWeight','bold'); 
        hold(axi,'off');
        
    case 'stampstool'
        %% Create a interferogram network using the StaMPS function
        a = gcf;
        tmp_para = a.UserData; 

        % Load the StaMPS directory 
        fi = fopen([tmp_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{2};
        
        % Ask the SBAS parameters 
        prompt = {'Threshold of coherence','Threshold of temporal baseline','Threshold of perpendicular baseline'};
        dlgtitle = 'StaMPS Network';
        dims = [1 35];
        definput = {'0.5','120','500'};
        answer = inputdlg(prompt,dlgtitle,dims,definput);
        
        % Compute the network
        cur = cd;
        cd(pathstampsprocessing)
        sb_find_mod(str2num(answer{1}),str2num(answer{2}),str2num(answer{3}));
        cd(cur);
        
        % Display the network
        runGUISBASnetwork('display',[]);
        
    case 'etalabtool'
        %% Create a interferogram network using the ETALAB considerations
        a = gcf;
        tmp_para = a.UserData;
        
        % Load the StaMPS directory 
        fi = fopen([tmp_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{2};
        
        % Compute the network
        cur = cd;
        cd(pathstampsprocessing)
        sb_find_ETALAB_network;
        cd(cur);
        
        % Display the network
        runGUISBASnetwork('display',[]);
        
    case 'addifg'
        %% Tool to add an interferogram
        a = gcf;
        tmp_para = a.UserData;

        % Load the StaMPS directory 
        fi = fopen([tmp_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{2};
        
        % Add and modify the network according to user
        flist = fopen([pathstampsprocessing,'/small_baselines.list'],'r');
        list = textscan(flist,'%s %s'); fclose(flist);
        
        listnum = [];
        listnum(:,1) = datenum(datetime(list{1},'InputFormat','yyyyMMdd'));
        listnum(:,2) = datenum(datetime(list{2},'InputFormat','yyyyMMdd'));
        listnum = sort(unique([listnum(:)]));
        
        [xifg,yifg] = getline(axi);
        
        pos1 = find(abs(xifg(1) - listnum) == min(abs(xifg(1) - listnum))) ;
        pos2 = find(abs(xifg(end) - listnum) == min(abs(xifg(end) - listnum))) ;
        
        flist = fopen([pathstampsprocessing,'/small_baselines.list'],'a');
        fprintf(flist,'%s %s\n',datestr(listnum(pos1),'yyyymmdd'),datestr(listnum(pos2),'yyyymmdd'));
        fclose(flist);
        
        % Display the network
        runGUISBASnetwork('display',[]);
        
    case 'removeifg'
        %% Tool to remove an interferogram
        a = gcf;
        tmp_para = a.UserData;

        % Load the StaMPS directory 
        fi = fopen([tmp_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{2};
        
        % Modify the network according to user
        flist = fopen([pathstampsprocessing,'/small_baselines.list'],'r');
        list = textscan(flist,'%s %s'); fclose(flist);
        
        listnum = [];
        listnum(:,1) = datenum(datetime(list{1},'InputFormat','yyyyMMdd'));
        listnum(:,2) = datenum(datetime(list{2},'InputFormat','yyyyMMdd'));
        listnumuni = sort(unique([listnum(:)]));
        
        [xifg,yifg] = getline(axi);
        
        xifg = sort(xifg); 
        
        pos1 = find(abs(xifg(1) - listnumuni) == min(abs(xifg(1) - listnumuni))) ;
        pos2 = find(abs(xifg(end) - listnumuni) == min(abs(xifg(end) - listnumuni))) ;
        
        pos1 = find(listnumuni(pos1) == listnum(:,1));
        pos2 = find(listnumuni(pos2) == listnum(:,2));
        
        pos = intersect(pos1,pos2);
        listnum(pos,:) = [];
        
        fid=fopen([pathstampsprocessing,'/small_baselines.list'],'w');
        for i1=1:length(listnum)
            fprintf(fid,'%s %s\n',datestr(listnum(i1,1),'yyyymmdd'),datestr(listnum(i1,2),'yyyymmdd'));
        end
        fclose(fid); 
        
        % Display the network
        runGUISBASnetwork('display',[]);
        
    case 'zoomin'
        %% To zoom
        zoom(axi); 
        
    case 'panon'
        %% To move
        pan(axi); 
        
    case 'save'
        %% To save an image of network
        a = gcf;
        tmp_para = a.UserData;

        Figi = figure('Visible','off');
        Figi.Position = [28 87 972 711];
        copyobj(axi, Figi);
        saveas(Figi,[tmp_para.WK,'/network_SBAS_StaMPS.jpg']); 
        close(Figi); 
end