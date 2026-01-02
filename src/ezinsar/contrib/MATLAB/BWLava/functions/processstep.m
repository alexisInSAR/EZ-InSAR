function processstep(src,evt,figmain,action)
%   processstep(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : action name
%       [figmain]       : main figure of BWLava applicaiton
%
%       Script to process the processing steps
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

if ~ishandle(figmain.UserData.Displayer)
    uialert(figmain,"Please open the BWLava Displayer","Error");
    error('Please open the BWLava Displayer');
end

switch action

    case 'ROIselection'

        uimsg = uiconfirm(figmain,'Please select the Region of Interest on the Displayer. When you are okay, double-click on the rectangle.','Selection of the Region of Interest');

        if strcmp(uimsg,'Cancel') == 0

            set(findobj(figmain.UserData.Displayer,'Tag','bgdisplayer'),'Value','Raw coherence');
            updatedisplayer([],[],figmain);

            d = uiprogressdlg(figmain,'Title','Please Wait',...
                'Message','Please select the Region of Interest');

            figure(figmain.UserData.Displayer);
            xmin = min(figmain.UserData.Data.X(:));
            xmax = max(figmain.UserData.Data.X(:));
            ymin = min(figmain.UserData.Data.Y(:));
            ymax = max(figmain.UserData.Data.Y(:));

            roi = drawrectangle('Position',[xmin + (xmax-xmin).*0.25,ymin + (ymax-ymin).*0.25,(xmax-xmin).*0.5,(ymax-ymin).*0.5],'Label','Region of Interest','Color',[1 0 0]);
            rect = customWait(roi);
            delete(roi);

            d.Message = 'Cropping...';

            % Cropping
            mi = inpolygon(figmain.UserData.Data.X, ...
                figmain.UserData.Data.Y, ...
                [rect(1) rect(1)+rect(3) rect(1)+rect(3) rect(1) rect(1)], ...
                [rect(2) rect(2) rect(2)+rect(4) rect(2)+rect(4) rect(2)]);

            [nl,nc] = find(mi==1);
            nl1 = min(nl);
            nl2 = max(nl);
            nc1 = min(nc);
            nc2 = max(nc);

            figmain.UserData.Data.coherencecrop = [];
            figmain.UserData.Data.coherencefilt = [];

            for i1 = 1 : size(figmain.UserData.Data.coherence,3)
                figmain.UserData.Data.coherencecrop(:,:,i1) = figmain.UserData.Data.coherence(nl1:nl2,nc1:nc2,i1);
                figmain.UserData.Data.coherencefilt(:,:,i1) = medfilt2(figmain.UserData.Data.coherencecrop(:,:,i1),[figmain.UserData.Data.kernelfilt(i1),figmain.UserData.Data.kernelfilt(i1)]);
                d.Value = i1./size(figmain.UserData.Data.coherence,3);
                pause(0.01)
            end
            figmain.UserData.Data.Xcrop = figmain.UserData.Data.X(nl1:nl2,nc1:nc2);
            figmain.UserData.Data.Ycrop = figmain.UserData.Data.Y(nl1:nl2,nc1:nc2);

            delete(d);
        end

        set(findobj(figmain.UserData.Displayer,'Tag','bgdisplayer'),'Value','Cropped coherence');
        updatedisplayer([],[],figmain);

    case 'segmentation'


        uimsg = uiconfirm(figmain,'Please select the segmentation region on the Displayer. When you are okay, double-click on the rectangle.','Selection of the Region of Segmentation');

        if strcmp(uimsg,'Cancel') == 0

            set(findobj(figmain.UserData.Displayer,'Tag','bgdisplayer'),'Value','Filtered coherence');
            updatedisplayer([],[],figmain);

            d = uiprogressdlg(figmain,'Title','Please Wait',...
                'Message','Please select the Region of Segmentation');

            figure(figmain.UserData.Displayer);
            xmin = min(figmain.UserData.Data.Xcrop(:));
            xmax = max(figmain.UserData.Data.Xcrop(:));
            ymin = min(figmain.UserData.Data.Ycrop(:));
            ymax = max(figmain.UserData.Data.Ycrop(:));

            roi = drawrectangle('Position',[xmin + (xmax-xmin).*0.25,ymin + (ymax-ymin).*0.25,(xmax-xmin).*0.5,(ymax-ymin).*0.5],'Label','Region of Segmentation','Color',[0 0 1]);
            rect = customWait(roi);
            delete(roi);

            d.Message = 'Computation of the threshold...';

            % Cropping
            mi = inpolygon(figmain.UserData.Data.Xcrop, ...
                figmain.UserData.Data.Ycrop, ...
                [rect(1) rect(1)+rect(3) rect(1)+rect(3) rect(1) rect(1)], ...
                [rect(2) rect(2) rect(2)+rect(4) rect(2)+rect(4) rect(2)]);

            [nl,nc] = find(mi==1);
            nl1 = min(nl);
            nl2 = max(nl);
            nc1 = min(nc);
            nc2 = max(nc);

            figmain.UserData.Data.maskraw = [];

            for i1 = 1 : size(figmain.UserData.Data.coherencefilt,3)
                level = graythresh(figmain.UserData.Data.coherencefilt(nl1:nl2,nc1:nc2,i1));
                figmain.UserData.Data.thesholdvalue(i1) = level;
                figmain.UserData.Data.maskraw(:,:,i1) = double(im2bw(figmain.UserData.Data.coherencefilt(:,:,i1),level));

                d.Value = i1./size(figmain.UserData.Data.coherencefilt,3);
                pause(0.01)
            end

            delete(d);
        end

        updatetable([],[],figmain);

        set(findobj(figmain.UserData.Displayer,'Tag','bgdisplayer'),'Value','Raw Binary image');
        updatedisplayer([],[],figmain);

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
