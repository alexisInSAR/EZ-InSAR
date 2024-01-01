function displayextensionCSK(src,evt,action,miesar_para)
%   displayextensionCSK(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to plot the extension of COSMO-SkyMed data
%
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also createlistSLC, GUIpathdirectory, displayextensionS1, initparmslc, readxmlannotationS1, displayextensionTSXPAZ, manageparamaterSLC, downloaderSLC, manageSLC.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.0.0 Beta
%   Date: 27/07/2022
%
%   -------------------------------------------------------
%   Version history:
%           2.0.0 Beta: Initial (unreleased)

% Open the variables
paramslc = load([miesar_para.WK,'/parmsSLC.mat']); fid = fopen([miesar_para.WK,'/SLC.list'],'r');
list = textscan(fid,['%s %s %s %s %s %s %s %s']); fclose(fid); testslc = 0;

% Read and display the burst coordinates
set(findobj(gcf,'Tag','name_progressbar'),'Text','Read the extensions based on the .xml...'); drawnow; pause(0.01);

% We have downloaded SLC(s)
% Preparation of variables
burst_extension = struct('Date','','Ext',[]);


for i1 = 1 : length(list{1})

    update_progressbar_MIESAR(i1./length(list{1}),findobj(gcf,'Tag','progressbar'),miesar_para,'defaut'); drawnow; pause(0.01);

    % Identification of xml
    path_h5 = [paramslc.pathSLC,'/',list{1}{i1},'/',list{4}{i1}];

    % Read the date from the lilst
    di = strsplit(list{2}{i1},'.');
    burst_extension(i1).Date = datetime(di{1},'InputFormat','yyyy-MM-dd''T''HH:mm:ss');

    Top_Left = h5readatt(path_h5,'/S01/SBI/','Top Left Geodetic Coordinates');
    Top_Right = h5readatt(path_h5,'/S01/SBI/','Top Right Geodetic Coordinates'); 
    Bottom_Left = h5readatt(path_h5,'/S01/SBI/','Bottom Left Geodetic Coordinates'); 
    Bottom_Right = h5readatt(path_h5,'/S01/SBI/','Bottom Right Geodetic Coordinates'); 


    % correction to the center point
    burst_coordinates.longitude = [Bottom_Left(2);Bottom_Right(2);Top_Right(2);Top_Left(2);Bottom_Left(2)]; 
    burst_coordinates.latitude = [Bottom_Left(1);Bottom_Right(1);Top_Right(1);Top_Left(1);Bottom_Left(1)]; 
    
    burst_extension(i1).Ext.nb_burst = 1;
    burst_extension(i1).Ext.burst_coordinates = burst_coordinates;

end

% Computation of colorscale based on the full set of dates
dateslc = [];

for i1 = 1 : length(burst_extension)
    di = strsplit(list{2}{i1},'.');
    dateslc = [dateslc; datetime(di{1},'InputFormat','yyyy-MM-dd''T''HH:mm:ss')];
end

if length(dateslc) == 1
    colori = 'black' ;
else
    ci = jet;
    dateslcnorm = (datenum(dateslc) - min(datenum(dateslc)))./( max(datenum(dateslc)) - min(datenum(dateslc)));
    colori(:,1) = interp1(linspace(0,1,size(ci,1)),ci(:,1),dateslcnorm,'linear');
    colori(:,2) = interp1(linspace(0,1,size(ci,1)),ci(:,2),dateslcnorm,'linear');
    colori(:,3) = interp1(linspace(0,1,size(ci,1)),ci(:,3),dateslcnorm,'linear');
end

% And we can display opening a new figure
set(findobj(gcf,'Tag','name_progressbar'),'Text','Display the SLC coverage...'); drawnow; pause(0.01);
axmain = gcf;
axiprogress = findobj(gcf,'Tag','progressbar');
fig_ext_burst = figure('name','Coverage of SLCs','numbertitle','off'); fig_ext_burst.OuterPosition = [200 100 1080 700];

if contains(struct2array(ver), 'Mapping Toolbox')
    gxi = geoaxes;
else
    gxi = axes;
end

% Display and save in the dumpy matrice to progress the DEM download
box_burst.IW1=[];

for i1 = 1 : length(burst_extension)

    if isempty(burst_extension(i1).Date) == 0
        box_burst.IW1.lat{i1,1}=[min(burst_extension(i1).Ext.burst_coordinates.latitude),max(burst_extension(i1).Ext.burst_coordinates.latitude)];
        box_burst.IW1.lon{i1,1}=[min(burst_extension(i1).Ext.burst_coordinates.longitude),max(burst_extension(i1).Ext.burst_coordinates.longitude)];
        hold(gxi,'on')

        if contains(struct2array(ver), 'Mapping Toolbox')
            geoplot(gxi,burst_extension(i1).Ext.burst_coordinates.latitude,burst_extension(i1).Ext.burst_coordinates.longitude,'-','Color',colori(i1,:)); hold(gxi,'on')
        else
            plot(gxi,burst_extension(i1).Ext.burst_coordinates.longitude,burst_extension(i1).Ext.burst_coordinates.latitude,'-','Color',colori(i1,:)); hold(gxi,'on')
        end

    end
    update_progressbar_MIESAR(i1./length(list{1}),axiprogress,miesar_para,'defaut'); drawnow; pause(0.01);

end
save([miesar_para.WK,'/parmsSLC.mat'],'box_burst','-append');


[lonta,lata] = read_kml([miesar_para.WK,'/area.kml']);
[lont,latt] = read_kml([miesar_para.WK,'/target.kml']);

if contains(struct2array(ver), 'Mapping Toolbox')
    hold(gxi,'on')
    geoplot(gxi,latt,lont,'--','Color','black'); hold(gxi,'on')
    hold(gxi,'on')
    geoplot(gxi,lata,lonta,'--','Color','green'); hold(gxi,'on')

    hold(gxi,'off')
    geobasemap(gxi,'satellite');

else
    hold(gxi,'on')
    plot(gxi,lont,latt,'--','Color','black'); hold(gxi,'on')
    hold(gxi,'on')
    plot(gxi,lont,latt,'--','Color','green'); hold(gxi,'on')
    hold(gxi,'off')

end
