function openstack(src,evt,figmain)
%   openstack(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [figmain]       : main figure of BWLava applicaiton
%
%       Script to open the coherence stack
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.0.0 Beta
%   Date: 21/11/2024
%
%   -------------------------------------------------------
%   Modified:
%
%   -------------------------------------------------------
%   Version history:
%           2.0.0 Beta: Initial (unreleased)

%% Initialisation of the data stack 
stack = cohstack;

%% Request the files
[file,location] = uigetfile({'*.tif';'*.tiff';'*.r4'}, ...
                           'MultiSelect', 'on', ... 
                          'Select the coherence image(s)'); 

if iscell(file)==0
    file = {file}; 
end 

file = sort(file); 

%% Read the images
for i1 = 1 : length(file)
     
    % For the .tif format
    if endsWith(file{i1},'.tif','IgnoreCase',true) | endsWith(file{i1},'.tiff','IgnoreCase',true)
        [cohi,color,R] = geotiffread([location,file{i1}]);
        if i1 == 1
            warning('The .tif data are considered as having the Metadata AREA_OR_POINT = point')
            x = linspace(R.LongitudeLimits(1),R.LongitudeLimits(2),R.RasterSize(2));
            y = linspace(R.LatitudeLimits(2),R.LatitudeLimits(1),R.RasterSize(1));
            [stack.X, stack.Y] = meshgrid(x,y); 
            figmain.UserData.CoordinatesInfo{1} = R; 
            figmain.UserData.CoordinatesInfo{2} = geotiffinfo([location,file{i1}]); 
        end 
    end 

    % Correction 
    if isinteger(cohi)
        cohi = double(cohi)./255;
    else
        cohi = double(cohi)
    end 
    cohi(cohi==0) = NaN; 
    stack.coherence(:,:,i1) = cohi;

    % Extract the names
    stack.files{i1} = file{i1}; 

    % Extract the dates
    namesplit = strsplit(file{i1},'.'); namesplit = strsplit(namesplit{1},'_'); 
    d1 = NaT; 
    d2 = NaT; 
    for i2 = 1 : length(namesplit)
        try
            di = datetime(namesplit{i2},'InputFormat','yyyyMMdd'); 
            if isnat(d1)
                d1 = di; 
            else
                d2 = di; 
            end 
        catch 
            a = 'dummy'; 
        end 
    end 

    % Store the variables
    stack.date1(i1) = d1; 
    stack.date2(i1) = d2; 
    stack.kernelfilt(i1) = 1; 
    stack.thesholdvalue(i1) = NaN; 
        
end 

%% Storing 
figmain.UserData.Data = stack; 
updatetable(src,evt,figmain)

%% Change the button states
set(findobj(figmain,'Tag','btdisplayer'),'Enable','on'); 
set(findobj(figmain,'Tag','btroi'),'Enable','on'); 
set(findobj(figmain,'Tag','btseg'),'Enable','on'); 
set(findobj(figmain,'Tag','btld'),'Enable','on'); 
set(findobj(figmain,'Tag','btsave'),'Enable','on'); 


