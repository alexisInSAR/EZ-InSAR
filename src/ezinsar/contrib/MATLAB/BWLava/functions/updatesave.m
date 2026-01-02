function updatesave(src,evt,figmain,action)
%   updatesave(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [figmain]       : main figure of BWLava applicaiton
%
%       Script to update the save plugin
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

switch action
    case 'init'

        if isempty(figmain.UserData.Data.mask) == 1
            uialert(figmain,"Please run the lava detection","Error");
            error('Please run the segmentation');
        end

        if ishandle(figmain.UserData.Save)
            close(figmain.UserData.Save)
        end
        figmain.UserData.Save = saveplugin(figmain);

    case 'geotiffmask'
        selpath = uigetdir('Select a directory to shore the lava-flow mask'); 

        R = figmain.UserData.CoordinatesInfo{1};
        info = figmain.UserData.CoordinatesInfo{2}; 

        for i1 = 1 : size(figmain.UserData.Data.mask,3)
            if mod(figmain.UserData.Data.Xcrop(1,end)-figmain.UserData.Data.Xcrop(1,1),360) < 1
                
                R.LatitudeLimits = [min(figmain.UserData.Data.Ycrop(:,1)) max(figmain.UserData.Data.Ycrop(:,1))];
                R.LongitudeLimits = [min(figmain.UserData.Data.Xcrop(1,:)) max(figmain.UserData.Data.Xcrop(1,:))];
                R.RasterSize = size(figmain.UserData.Data.Xcrop);
                % R.RasterExtentInLatitude = abs(figmain.UserData.Data.Ycrop(end,1)-figmain.UserData.Data.Ycrop(1,1)); 
                % R.RasterExtentInLongitude = abs(figmain.UserData.Data.Xcrop(1,end)-figmain.UserData.Data.Xcrop(1,1)); 

                name = figmain.UserData.Data.files{i1}; name = strsplit(name,'.'); name = name{1}; 
                geotiffwrite([selpath,filesep,name,'_masklava.tif'],figmain.UserData.Data.mask(:,:,i1),R); 
            end 

        end 

    case 'outlines'
        selpath = uigetdir('Select a directory to shore the lava-flow outlines')
        
        mode = get(findobj(figmain.UserData.Save,'Tag','outlineselectsaveplugin'),'Value'); 
        format = get(findobj(figmain.UserData.Save,'Tag','outlineformatsaveplugin'),'Value'); 
        
        for i1 = 1 : size(figmain.UserData.Data.mask,3)
            
            switch mode

                case 'Pixel edges'
                    name = figmain.UserData.Data.files{i1}; name = strsplit(name,'.'); name = name{1}; 

                    if mod(figmain.UserData.Data.Xcrop(1,end)-figmain.UserData.Data.Xcrop(1,1),360) < 1
                        p = geoshape(figmain.UserData.Data.outlines{i1,2}.Vertices(:,2),figmain.UserData.Data.outlines{i1,2}.Vertices(:,1),'Geometry','Polygon');
                    else
                        p = mapshape(figmain.UserData.Data.outlines{i1,2}.Vertices(:,1),figmain.UserData.Data.outlines{i1,2}.Vertices(:,2),'Geometry','Polygon');
                    end 

                    switch format
                        case '.shp file'
                            shapewrite(p,[selpath,filesep,name,'_lavaoutlines.shp'])
                        case '.kml file'
                            kmlwrite([selpath,filesep,name,'_lavaoutlines.kml'],p)
                    end 
            end 

        end   
end

end
