function sb_find_ETALAB_network
%   sb_find_ETALAB_network
%
%       Function to create a interferogram network using some considerations 
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   Based on the works of Marie-Pierre Doin's Team. 
%   See Thollard, F.; Clesse, D.; Doin, M.-P.; Donadieu, J.; Durand, P.; Grandin, R.; Lasserre, C.; Laurent, C.; Deschamps-Ostanciaux, E.; Pathier, E.; Pointal, E.; Proy, C.; Specht, B. FLATSIM: The ForM@Ter LArge-Scale Multi-Temporal Sentinel-1 InterferoMetry Service. Remote Sens. 2021, 13, 3734. https://doi.org/10.3390/rs13183734 
%   See H. Ansari, F. De Zan and A. Parizzi, "Study of Systematic Bias in Measuring Surface Deformation With SAR Interferometry," in IEEE Transactions on Geoscience and Remote Sensing, vol. 59, no. 2, pp. 1285-1301, Feb. 2021, doi: 10.1109/TGRS.2020.3003421.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 30/11/2021
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)

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
