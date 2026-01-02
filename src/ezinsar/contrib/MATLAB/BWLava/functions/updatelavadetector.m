function updatelavadetector(src,evt,figmain,action)
%   updatelavadetector(src,evt,action,miesar_para)
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

switch action
    case 'init'

        if ~ishandle(figmain.UserData.Displayer)
            uialert(figmain,"Please open the BWLava Displayer","Error");
            error('Please open the BWLava Displayer');
        end

        if isempty(figmain.UserData.Data.maskraw) == 1
            uialert(figmain,"Please run the segmentation","Error");
            error('Please run the segmentation');
        end

        if ishandle(figmain.UserData.LavaDetector)
            close(figmain.UserData.LavaDetector)
        end
        figmain.UserData.LavaDetector = lavaplugin(figmain);
        updatelavadetector(src,evt,figmain,'update')

    case 'update'

        if length(figmain.UserData.partmask(1).x) == 0
            set(findobj(figmain.UserData.LavaDetector,'Tag','maskinglistlavaplugin'),'Items',{});
            set(findobj(figmain.UserData.LavaDetector,'Tag','maskingbtdeletelavaplugin'),'Enable','off');
        else
            set(findobj(figmain.UserData.LavaDetector,'Tag','maskingbtdeletelavaplugin'),'Enable','on');

            items = {''};
            for i1 = 1 : length(figmain.UserData.partmask)
                items{i1} = sprintf('Mask %d',i1);
            end
            set(findobj(figmain.UserData.LavaDetector,'Tag','maskinglistlavaplugin'),'Items',items);

        end

        if length(figmain.UserData.partlava(1).x) == 0
            set(findobj(figmain.UserData.LavaDetector,'Tag','lavalistlavaplugin'),'Items',{});
            set(findobj(figmain.UserData.LavaDetector,'Tag','lavabtdeletelavaplugin'),'Enable','off');
            set(findobj(figmain.UserData.LavaDetector,'Tag','btrunlavaplugin'),'Enable','off');
        else
            set(findobj(figmain.UserData.LavaDetector,'Tag','lavabtnewlavaplugin'),'Enable','on');
            set(findobj(figmain.UserData.LavaDetector,'Tag','lavabtdeletelavaplugin'),'Enable','on');
            set(findobj(figmain.UserData.LavaDetector,'Tag','btrunlavaplugin'),'Enable','on');

            items = {''};
            for i1 = 1 : length(figmain.UserData.partlava)
                items{i1} = sprintf('Part-lava %d',i1);
            end
            set(findobj(figmain.UserData.LavaDetector,'Tag','lavalistlavaplugin'),'Items',items);
        end

        updatedisplayer(src,evt,figmain)
        updatelavadetector(src,evt,figmain,'updateplot')

    case 'updateplot'

        axitag = findobj(figmain.UserData.Displayer,'Tag','axesdisplayer');
        figure(figmain.UserData.Displayer)

        hold on;

        h = 1;
        p = [];
        strlg = {};
        for i1 = 1 : size(figmain.UserData.partmask,2)
            if isempty(figmain.UserData.partmask(i1).x) == 0
                p = [p; patch(axitag, ...
                    figmain.UserData.partmask(i1).x, ...
                    figmain.UserData.partmask(i1).y,rand(1,3),'FaceAlpha',0.25)];
                strlg{h} = ['Mask ',num2str(i1)];
                h = h + 1;
            end
        end

        for i1 = 1 : size(figmain.UserData.partlava,2)
            if isempty(figmain.UserData.partlava(i1).x) == 0
                p = [p; plot(axitag, ...
                    figmain.UserData.partlava(i1).x, ...
                    figmain.UserData.partlava(i1).y,'-')];
                strlg{h} = ['Lava-part ',num2str(i1)];
                h = h + 1;
            end
        end

        hold off;
        lg = legend(p,strlg); lg.Color = [1 1 1];
        drawnow; pause(0.01)

    case 'vectormask'

        updatedisplayer([],[],figmain)
        [file,location] = uigetfile({'*.shp'}, ...
                           'MultiSelect', 'off', ... 
                          'Select the shapefile for masking'); 

        d = uiprogressdlg(figmain,'Title','Please Wait',...
            'Message','Please confirm the mask area');

        if length(figmain.UserData.partmask(1).x) == 0
            h = 1;
        else
            h = length(figmain.UserData.partmask) + 1;
        end

        S = shaperead([location,filesep,file]); 
        
        xtmp = [S(1).X(1:end-1)'; S(1).X(1)]; 
        ytmp = [S(1).Y(1:end-1)'; S(1).Y(1)]; 

        roi = drawpolygon('Position',[xtmp ytmp],'Label','Masking','Color',[0 0 1]);
        rect = customWait(roi);
        delete(roi);
        delete(d);
        
        figmain.UserData.partmask(h).x = [rect(:,1); rect(1,1)];
        figmain.UserData.partmask(h).y = [rect(:,2); rect(1,2')];

        updatelavadetector(src,evt,figmain,'update')

    case 'tracemask'

        set(findobj(figmain.UserData.Displayer,'Tag','bgdisplayer'),'Value','Filtered coherence');
        updatedisplayer([],[],figmain)

        d = uiprogressdlg(figmain,'Title','Please Wait',...
            'Message','Please select the mask area');

        figure(figmain.UserData.Displayer)

        xmin = min(figmain.UserData.Data.Xcrop(:));
        xmax = max(figmain.UserData.Data.Xcrop(:));
        ymin = min(figmain.UserData.Data.Ycrop(:));
        ymax = max(figmain.UserData.Data.Ycrop(:));

        roi = drawpolygon('Label','Masking','Color',[0 0 1]);
        rect = customWait(roi);
        delete(roi);
        delete(d);

        if length(figmain.UserData.partmask(1).x) == 0
            h = 1;
        else
            h = length(figmain.UserData.partmask) + 1;
        end

        figmain.UserData.partmask(h).x = [rect(:,1); rect(1,1)];
        figmain.UserData.partmask(h).y = [rect(:,2); rect(1,2')];

        updatelavadetector(src,evt,figmain,'update')

    case 'tracelavepart'

        set(findobj(figmain.UserData.Displayer,'Tag','bgdisplayer'),'Value','Filtered coherence');
        updatedisplayer([],[],figmain)

        d = uiprogressdlg(figmain,'Title','Please Wait',...
            'Message','Please select the lava-part area');

        figure(figmain.UserData.Displayer)

        xmin = min(figmain.UserData.Data.Xcrop(:));
        xmax = max(figmain.UserData.Data.Xcrop(:));
        ymin = min(figmain.UserData.Data.Ycrop(:));
        ymax = max(figmain.UserData.Data.Ycrop(:));

        roi = drawrectangle('Label','Lava','Color',[0 0 1]);
        rect = customWait(roi);
        delete(roi);
        delete(d);

        if length(figmain.UserData.partlava(1).x) == 0
            h = 1;
        else
            h = length(figmain.UserData.partlava) + 1;
        end

        figmain.UserData.partlava(h).x = [rect(1); rect(1)+rect(3); rect(1)+rect(3); rect(1); rect(1)];
        figmain.UserData.partlava(h).y = [rect(2); rect(2); rect(2)+rect(4); rect(2)+rect(4); rect(2)];

        updatelavadetector(src,evt,figmain,'update')

    case 'deletemask'

        idx = get(findobj(figmain.UserData.LavaDetector,'Tag','maskinglistlavaplugin'),'Value')
        if isempty(idx) == 0
            idx = strsplit(idx,' '); idx = str2num(idx{2});
            figmain.UserData.partmask(idx) = [];

            if isempty(figmain.UserData.partmask) == 1
                figmain.UserData.partmask = struct('x',[],'y',[],'nl1',[],'nl2',[],'nc1',[],'nc2',[]);
            end

            updatelavadetector(src,evt,figmain,'update')
        end

    case 'deletelavapart'
        idx = get(findobj(figmain.UserData.LavaDetector,'Tag','lavalistlavaplugin'),'Value')
        if isempty(idx) == 0
            idx = strsplit(idx,' '); idx = str2num(idx{2});
            figmain.UserData.partlava(idx) = [];

            if isempty(figmain.UserData.partlava) == 1
                figmain.UserData.partlava = struct('x',[],'y',[],'nl1',[],'nl2',[],'nc1',[],'nc2',[]);
            end

            updatelavadetector(src,evt,figmain,'update')
        end

    case 'runcomputation'
        d = uiprogressdlg(figmain,'Title','Correction of the lava mask',...
            'Message','Computation');

        % Nolava mask
        nolavamask = ones(size(figmain.UserData.Data.Xcrop));
        if length(figmain.UserData.partmask(1).x) ~= 0
            for i1 = 1 : size(figmain.UserData.partmask,2)
                if isempty(figmain.UserData.partmask(i1).x) == 0
                    nolavamask = nolavamask - inpolygon(figmain.UserData.Data.Xcrop,figmain.UserData.Data.Ycrop,figmain.UserData.partmask(i1).x,figmain.UserData.partmask(i1).y);
                end
            end
        end
        nolavamask(nolavamask<1)=0;

        for i1 = 1 : size(figmain.UserData.Data.maskraw,3)
            nolavamaskit = nolavamask;
            nolavamaskit(isnan(figmain.UserData.Data.coherencecrop(:,:,i1))==1) = 0;

            mask = abs(figmain.UserData.Data.maskraw(:,:,i1)-1) .* nolavamaskit;
            masklava = zeros(size(figmain.UserData.Data.coherencecrop(:,:,i1)));

            BWl = bwlabel(mask,4);
            for i2 = 1 : size(figmain.UserData.partlava,2)
                if isempty(figmain.UserData.partlava(i2).x) == 0
                    mi = inpolygon(figmain.UserData.Data.Xcrop,figmain.UserData.Data.Ycrop,figmain.UserData.partlava(i2).x,figmain.UserData.partlava(i2).y);
                    [n,m] = find(mi==1);
                    indi = searchindex(BWl,min(n),max(n),min(m),max(m),100);
                    masklava(BWl==indi)=1;

                end
            end

            % Cleaning
            if strcmp(get(findobj(figmain.UserData.LavaDetector,'Tag','ppswitchlavaplugin'),'Value'),'Enabled')
                kernel = fix(get(findobj(figmain.UserData.LavaDetector,'Tag','pperodthreslavaplugin'),'Value'));

                se = offsetstrel('ball',kernel,kernel);
                b = imerode(masklava,se);
                b(b==max(b(:)))=1;
                b(b~=1)=0;
                mask = b;

                masklava = zeros(size(mask));
                BWl = bwlabel(mask,4);
                for i2 = 1 : size(figmain.UserData.partlava,2)
                    if isempty(figmain.UserData.partlava(i2).x) == 0
                        mi = inpolygon(figmain.UserData.Data.Xcrop,figmain.UserData.Data.Ycrop,figmain.UserData.partlava(i2).x,figmain.UserData.partlava(i2).y);
                        [n,m] = find(mi==1);
                        indi = searchindex(BWl,min(n),max(n),min(m),max(m),100);
                        masklava(BWl==indi)=1;
                    end
                end

                b = imdilate(masklava,se);
                b(b==min(b(:)))=1;
                b(b~=1)=0;
                mask = b;

                masklava = zeros(size(mask));
                BWl = bwlabel(mask,4);
                for i2 = 1 : size(figmain.UserData.partlava,2)
                    if isempty(figmain.UserData.partlava(i2).x) == 0
                        mi = inpolygon(figmain.UserData.Data.Xcrop,figmain.UserData.Data.Ycrop,figmain.UserData.partlava(i2).x,figmain.UserData.partlava(i2).y);
                        [n,m] = find(mi==1);
                        indi = searchindex(BWl,min(n),max(n),min(m),max(m),100);
                        masklava(BWl==indi)=1;
                    end
                end

                masklava = masklava .* nolavamaskit;

            end

            BWl = bwlabel(abs(masklava-1));
            N = hist(BWl(:),[1:max(unique(BWl(:)))]);
            th = fix(get(findobj(figmain.UserData.LavaDetector,'Tag','ppkipukathreslavaplugin'),'Value'));
            idx = find(N<th);
            masklava(ismember(BWl,idx)) = 1;

            figmain.UserData.Data.mask(:,:,i1) = masklava;

            % Pixel centres
            lim = bwboundaries(masklava);
            outlines = cell(1);
            for i = 1 : length(lim)
                indx = lim{i}(:,2);
                indy = lim{i}(:,1);

                xoutlines = [];
                youtlines = [];
                for j = 1 : length(indx)
                    xoutlines=[xoutlines; figmain.UserData.Data.Xcrop(indy(j),indx(j))];
                    youtlines=[youtlines; figmain.UserData.Data.Ycrop(indy(j),indx(j))];
                end
                outlines{i} = [xoutlines youtlines];
            end
            figmain.UserData.Data.outlines{i1,1} = outlines;

            % Pixel edges
            lim = bwboundaries(masklava,'TraceStyle','pixeledge');

            h = 1;
            for i = 1 : length(lim)
                indx = lim{i}(:,2);
                indy = lim{i}(:,1);
                if numel(indx)>3 & numel(indy)>3
                    xi = interp1([1:size(figmain.UserData.Data.Xcrop,2)]',figmain.UserData.Data.Xcrop(1,:)',indx);
                    yi = interp1([1:size(figmain.UserData.Data.Xcrop,1)]',figmain.UserData.Data.Ycrop(:,1)',indy);

                    if h == 1
                        p = polyshape(xi,yi);
                    else
                        ptmp = polyshape(xi,yi);

                        polytest = intersect(p,ptmp); 
                        if isempty(polytest.Vertices(:,1)) == 1
                            p = union(p,ptmp);
                        else
                            p = subtract(p,ptmp);
                        end
                    end
                    h = h + 1;
                end
            end
            figmain.UserData.Data.outlines{i1,2} = p;

            d.Value = i1./size(figmain.UserData.Data.coherence,3);
            pause(0.01);
        end

        delete(d);

        set(findobj(figmain.UserData.Displayer,'Tag','bgdisplayer'),'Value','Corrected Binary image');
        updatedisplayer([],[],figmain)

end

end

function pos = customWait(hROI)
l = addlistener(hROI,'ROIClicked',@clickCallback);
uiwait;
delete(l);
pos = hROI.Position;
end

function clickCallback(~,evt)
if strcmp(evt.SelectionType,'double')
    uiresume;
end
end
