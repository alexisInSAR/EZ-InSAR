function [burst_coordinates, nb_burst] = readxmlannotationS1(pathxml,mode)
%   readxmlannotationS1(pathxml)
%       [pathxml]           : path of S1 .xml annotation files. 
%
%       Function to read the .xml to extract the burst coordinates. 
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
%           - Alexis Hrysiewicz, UCD / iCRAG, 07/07/2022: StripMap
%           implementation
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)
%           2.0.0 Alpha: Initial (unreleased)


%% Read the parameters
% For the lines
lines = []; 
[a,b] = system(['grep "<line>" ',pathxml]); c = strsplit(b,'\n'); 
for i1 = 1 : length(c)
    if contains(c{i1},'<line>') 
        ci = strsplit(c{i1},'<line>'); 
        ci = strsplit(ci{end},'</line>'); 
        ci = str2num(ci{1}); 
        lines = [lines; ci]; 
    end
end 

% For the pixels
pixels = []; 
[a,b] = system(['grep "<pixel>" ',pathxml]); c = strsplit(b,'\n'); 
for i1 = 1 : length(c)
    if contains(c{i1},'<pixel>') 
        ci = strsplit(c{i1},'<pixel>'); 
        ci = strsplit(ci{end},'</pixel>'); 
        ci = str2num(ci{1}); 
        pixels = [pixels; ci]; 
    end
end 

% For the latitude
latitude = []; 
[a,b] = system(['grep "<latitude>" ',pathxml]); c = strsplit(b,'\n'); 
for i1 = 1 : length(c)
    if contains(c{i1},'<latitude>') 
        ci = strsplit(c{i1},'<latitude>'); 
        ci = strsplit(ci{end},'</latitude>'); 
        ci = str2num(ci{1}); 
        latitude = [latitude; ci]; 
    end
end 

% For the longitude
longitude = []; 
[a,b] = system(['grep "<longitude>" ',pathxml]); c = strsplit(b,'\n'); 
for i1 = 1 : length(c)
    if contains(c{i1},'<longitude>') 
        ci = strsplit(c{i1},'<longitude>'); 
        ci = strsplit(ci{end},'</longitude>'); 
        ci = str2num(ci{1}); 
        longitude = [longitude; ci]; 
    end
end 

%% Extraction of coordinates 
switch mode 
    case 'S1_IW'
        burst_coordinates = struct('longitude',[],'latitude',[]); 
        unique_lines = unique(lines);
        nb_burst = length(unique_lines)-1; 
        for i1 = 1 : nb_burst
            posi1 = find(unique_lines(i1) == lines); 
            posi2 = find(unique_lines(i1+1) == lines); 
            loni = [longitude(posi1); flipud(longitude(posi2)); longitude(posi1(1))]; 
            lati = [latitude(posi1); flipud(latitude(posi2)); latitude(posi1(1))]; 
            burst_coordinates(i1).longitude = loni; 
            burst_coordinates(i1).latitude = lati; 
        end 
    case 'S1_SM'
        nb_burst = 1;  
        k = convhull(longitude,latitude); 
        burst_coordinates(1).longitude = longitude(k); 
        burst_coordinates(1).latitude = latitude(k); 
end 
