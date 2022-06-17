function sb_find_ETALAB_network
%   Function to create a interferogram network using ETALAB considerations 
%   
%   Based on the works of Marie-Pierre Doin's Team. 
%
%   See also runGUISBASnetwork, runGUIstampsparameters,
%   stampsMERGEDprocessing, stampsprocessing, stampsPSprocessing,
%   stampsSBASprocessing.

%   Copyright 2021 Alexis Hrysiewicz, UCD / iCRAG2 
%   Version: 1.0.0 
%   Date: 30/11/2021

%% Load the parameters 
load psver
psname=['ps',num2str(psver)];
ps=load(psname);

day = ps.day; 
bperp = ps.bperp; 

th_bperp = 50; % Here, the maximal bperp is hardly defined. 

sbname='small_baselines.list';

dateslc = sort(day);
difg = mean(gradient(dateslc));

%% Create all the interferograms
IFG = []; BPERP = []; 
for i1 = 1 : numel(dateslc) - 1
    for j1 = i1+1 : numel(dateslc)
        IFG = [IFG; [dateslc(i1) dateslc(j1)]];
        BPERP = [BPERP; [bperp(i1) bperp(j1)]]; 
    end
end

%% Create the desired network
h = 1;
IFG_bis = [];
wi = waitbar(0,'...'); 
for i1 = length(dateslc) : - 1 : 1
    %For n-1
    try
        dm = dateslc(i1-1);
        ds = dateslc(i1);
        pos1 = find(IFG(:,1) == dm);
        pos2 = find(IFG(:,2) == ds);
        pos = intersect(pos1,pos2);
        IFG_bis = [IFG_bis; IFG(pos,1) IFG(pos,2)];
    end
    %For n-2
    try
        dm = dateslc(i1-2);
        ds = dateslc(i1);
        pos1 = find(IFG(:,1) == dm);
        pos2 = find(IFG(:,2)  == ds);
        pos = intersect(pos1,pos2);
        IFG_bis = [IFG_bis; IFG(pos,1) IFG(pos,2)];
    end
    %For n-3
    try
        dm = dateslc(i1-3);
        ds = dateslc(i1);
        pos1 = find(IFG(:,1) == dm);
        pos2 = find(IFG(:,2)  == ds);
        pos = intersect(pos1,pos2);
        IFG_bis = [IFG_bis; IFG(pos,1) IFG(pos,2)];
    end
    %For n-3 months
    try
        ds = dateslc(i1);
        dsbis = ds - 3.*(365.25./12);
        diff = abs(dateslc - dsbis);
        diff(diff>difg) = NaN;
        pos_diff = find(diff==min(diff));
        dm = dateslc(pos_diff);
        pos1 = find(IFG(:,1) == dm);
        pos2 = find(IFG(:,2)  == ds);
        pos = intersect(pos1,pos2);
        pos3 =  find(dateslc == dm); pos4 = find(dateslc == ds);
        IFG_bis = [IFG_bis; IFG(pos,1) IFG(pos,2)];
    end
    %For n-1 year
    try
        ds = dateslc(i1);
        dsbis = ds - 12.*(365.25./12);
        diff = abs(dateslc - dsbis);
        diff(diff>difg) = NaN;
        pos_diff = find(diff==min(diff));
        dm = dateslc(pos_diff);
        pos1 = find(IFG(:,1) == dm);
        pos2 = find(IFG(:,2)  == ds);
        pos = intersect(pos1,pos2);
        pos3 =  find(dateslc == dm); pos4 = find(dateslc == ds);
        if abs(BPERP(pos,1)-BPERP(pos,2)) < th_bperp 
            IFG_bis = [IFG_bis; IFG(pos,1) IFG(pos,2)];
        end 
    end
    h = h + 1; 
    waitbar(h./length(dateslc),wi); 
end
close(wi); 

%% Clear the files 
IFG_bis = unique(IFG_bis,'rows');
fid=fopen(sbname,'w');
for i=1:size(IFG_bis)
    fprintf(fid,'%s %s\n',datestr(IFG_bis(i,1),'yyyymmdd'),datestr(IFG_bis(i,2),'yyyymmdd'));
end
fclose(fid);