function updatedisplayer(src,evt,figmain)
%   updatedisplayer(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [figmain]       : main figure of BWLava applicaiton
%
%       Script to update the displayer
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

checkerror = false;

valuecoh = get(findobj(figmain.UserData.Displayer,'Tag','listdisplayer'),'Value');
axitag = findobj(figmain.UserData.Displayer,'Tag','axesdisplayer');
set(axitag,'Color','black');

idx = find(ismember(figmain.UserData.Data.files, valuecoh)); 

try 
    a = axitag.Children(1).CData;
    mode = 'update'; 
catch 
    a = 'dummy'; 
    mode = 'new'; 
end  

switch get(findobj(figmain.UserData.Displayer,'Tag','bgdisplayer'),'Value')
    case 'Raw coherence'
        x = figmain.UserData.Data.X(1,:); 
        y = figmain.UserData.Data.Y(:,1); 
        data = figmain.UserData.Data.coherence(:,:,idx); 
    case 'Cropped coherence'
        if isempty(figmain.UserData.Data.Xcrop) == 0
            x = figmain.UserData.Data.Xcrop(1,:); 
            y = figmain.UserData.Data.Ycrop(:,1); 
            data = figmain.UserData.Data.coherencecrop(:,:,idx); 
        else
            uialert(figmain,"Please open the Region of Interest","Error");
            checkerror=true; 
            set(findobj(figmain.UserData.Displayer,'Tag','bgdisplayer'),'Value','Raw coherence');
        end 
    case 'Filtered coherence'
        if isempty(figmain.UserData.Data.coherencefilt) == 0
            x = figmain.UserData.Data.Xcrop(1,:); 
            y = figmain.UserData.Data.Ycrop(:,1); 
            data = figmain.UserData.Data.coherencefilt(:,:,idx); 
        else
            uialert(figmain,"Please open the Region of Interest because the filtering is done at this step.","Error");
            checkerror=true; 
            set(findobj(figmain.UserData.Displayer,'Tag','bgdisplayer'),'Value','Raw coherence');
        end 
    case 'Raw Binary image'
        if isempty(figmain.UserData.Data.maskraw) == 0
            x = figmain.UserData.Data.Xcrop(1,:); 
            y = figmain.UserData.Data.Ycrop(:,1); 
            data = figmain.UserData.Data.maskraw(:,:,idx);
        else
            uialert(figmain,"Please run the segmentation","Error");
            checkerror=true; 
            set(findobj(figmain.UserData.Displayer,'Tag','bgdisplayer'),'Value','Filtered coherence');
        end 
    case 'Corrected Binary image'
        if isempty(figmain.UserData.Data.mask) == 0
            x = figmain.UserData.Data.Xcrop(1,:); 
            y = figmain.UserData.Data.Ycrop(:,1); 
            data = figmain.UserData.Data.mask(:,:,idx);
        else
            uialert(figmain,"Please run the lava detector","Error");
            checkerror=true; 
            set(findobj(figmain.UserData.Displayer,'Tag','bgdisplayer'),'Value','Raw Binary image');
        end 
end 

if checkerror == false
    xtmp = axitag.XLim; 
    ytmp = axitag.YLim; 
    
    imagesc(axitag,x,y, ...
        data); 
    set(axitag,'Ydir','normal'); 
    colormap("gray")
    axis equal; 
    caxis([0 1]); grid on; grid minor; 
    
    
    ci = colorbar; 
    if contains(get(findobj(figmain.UserData.Displayer,'Tag','bgdisplayer'),'Value'),'coherence')
        ylabel(ci,'Coherence'); 
    else
        ylabel(ci,'Masking'); 
    end 
    
    if strcmp(get(findobj(figmain.UserData.Displayer,'Tag','listoutlinesdisplayer'),'Value'),'Pixel centres')==1
            C(:,:,1) = axitag.Children(1).CData;
            C(:,:,2) = axitag.Children(1).CData;
            C(:,:,3) = axitag.Children(1).CData;
            try
                for i1 = 1 : length(figmain.UserData.Data.outlines{idx,1})
                    xc = figmain.UserData.Data.outlines{idx,1}{i1}(:,1);
                    yc = figmain.UserData.Data.outlines{idx,1}{i1}(:,2);
                    for i2 = 1 : length(xc)
                        nc = find(xc(i2)==figmain.UserData.Data.Xcrop(1,:));
                        nl = find(yc(i2)==figmain.UserData.Data.Ycrop(:,1));
                        C(nl,nc,1) = 1;
                        C(nl,nc,2) = 0;
                        C(nl,nc,3) = 0;
                    end
                end 
                checkerror2=false; 
            catch 
                checkerror2=true; 
            end 
        if sum(C(:,:,1),'all','omitnan') ~= sum(axitag.Children(1).CData,'all','omitnan') | checkerror2==false
            axitag.Children(1).CData = C; 
        else 
            uialert(figmain,"Please run the lava detector","Error");
            set(findobj(figmain.UserData.Displayer,'Tag','listoutlinesdisplayer'),'Value','None');  
        end
    
    elseif strcmp(get(findobj(figmain.UserData.Displayer,'Tag','listoutlinesdisplayer'),'Value'),'Pixel edges')==1
        try
            hold on; plot(axitag,figmain.UserData.Data.outlines{idx,2},'FaceColor','red','FaceAlpha',0.5,'LineStyle','-'); hold off; 
        catch
            uialert(figmain,"Please run the lava detector","Error");
            set(findobj(figmain.UserData.Displayer,'Tag','listoutlinesdisplayer'),'Value','None'); 
        end
    end 
else
    updatedisplayer([],[],figmain);
end  

switch mode
    case 'update'
        axitag.XLim = xtmp; 
        axitag.YLim = ytmp;
end 

if ishghandle(figmain.UserData.LavaDetector)
    updatelavadetector(src,evt,figmain,'updateplot')
end 
drawnow;pause(0.1)

end 


