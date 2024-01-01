function GUIpathdirectory(src,evt,action,miesar_para,mode,fig)
%   GUIpathdirectory(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to open a GUI to select the data directories
%
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also createlistSLC, GUIpathdirectory, displayextensionS1, initparmslc, readxmlannotationS1, displayextensionTSXPAZ, manageparamaterSLC, downloaderSLC, manageSLC.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.0.0 Beta
%   Date: 07/07/2022
%
%   -------------------------------------------------------
%   Version history:
%           2.0.0 Beta: Initial (unreleased)

parmsSLC = load([miesar_para.WK,'/parmsSLC.mat']);

switch action
    case 'open'
        hfig = uifigure('Position',[442 388 815 416],'Name','Directories of data','HandleVisibility','on');
%         figure(hfig)
        hfig.UserData = miesar_para; 

        gridhfig = uigridlayout(hfig,[3,10]);

        labelSLCpath = uilabel(gridhfig,'Text','SLC path','HorizontalAlignment','center','VerticalAlignment','center','FontSize',20,'FontWeight','bold');
        labelSLCpath.Layout.Row = [1];
        labelSLCpath.Layout.Column = [1 2];

        labelorbitpath = uilabel(gridhfig,'Text','Orbit path','HorizontalAlignment','center','VerticalAlignment','center','FontSize',20,'FontWeight','bold');
        labelorbitpath.Layout.Row = [2];
        labelorbitpath.Layout.Column = [1 2];

        labelauxpath = uilabel(gridhfig,'Text','Aux. file path','HorizontalAlignment','center','VerticalAlignment','center','FontSize',20,'FontWeight','bold');
        labelauxpath.Layout.Row = [3];
        labelauxpath.Layout.Column = [1 2];

        textSLCpath = uieditfield(gridhfig,'text','Tag','textSLCpath');
        textSLCpath.Layout.Row = [1];
        textSLCpath.Layout.Column = [3 9];
        if iscell(parmsSLC.pathSLC) == 1
            parmsSLC.pathSLC = parmsSLC.pathSLC{1};
        end
        textSLCpath.Value = parmsSLC.pathSLC;
        textSLCpath.ValueChangedFcn = @(src,evt,arg1,arg2,arg3,arg4) GUIpathdirectory(src,evt,'update',miesar_para,[],hfig);

        textorbitpath = uieditfield(gridhfig,'text','Tag','textorbitpath');
         textorbitpath.Layout.Row = [2];
        textorbitpath.Layout.Column = [3 9];
        if iscell(parmsSLC.pathorbit) == 1
            parmsSLC.pathorbit = parmsSLC.pathorbit{1};
        end
        textorbitpath.Value = parmsSLC.pathorbit;
        textorbitpath.ValueChangedFcn = @(src,evt,arg1,arg2,arg3,arg4) GUIpathdirectory(src,evt,'update',miesar_para,[],hfig);

        textauxpath = uieditfield(gridhfig,'text','Tag','textauxpath');
        textauxpath.Layout.Row = [3];
        textauxpath.Layout.Column = [3 9];
        if iscell(parmsSLC.pathaux) == 1
            parmsSLC.pathaux = parmsSLC.pathaux{1};
        end
        textauxpath.Value = parmsSLC.pathaux;
        textauxpath.ValueChangedFcn = @(src,evt,arg1,arg2,arg3,arg4) GUIpathdirectory(src,evt,'update',miesar_para,[],hfig);

        buttonSLCpath = uibutton(gridhfig,'Text','Select')  ;
        buttonSLCpath.ButtonPushedFcn = @(src,evt,arg1,arg2,arg3,arg4) GUIpathdirectory(src,evt,'gui',miesar_para,'slc',hfig);
        buttonSLCpath.Layout.Row = [1];
        buttonSLCpath.Layout.Column = [10];
        buttonSLCpath.Tooltip = 'Click to select the path';

        buttonorbitspath = uibutton(gridhfig,'Text','Select')  ;
        buttonorbitspath.ButtonPushedFcn = @(src,evt,arg1,arg2,arg3,arg4) GUIpathdirectory(src,evt,'gui',miesar_para,'orbits',hfig);
        buttonorbitspath.Layout.Row = [2];
        buttonorbitspath.Layout.Column = [10];
        buttonorbitspath.Tooltip = 'Click to select the path';

        buttonauxpath = uibutton(gridhfig,'Text','Select')  ;
        buttonauxpath.ButtonPushedFcn = @(src,evt,arg1,arg2,arg3,arg4) GUIpathdirectory(src,evt,'gui',miesar_para,'aux',hfig);
        buttonauxpath.Layout.Row = [3];
        buttonauxpath.Layout.Column = [10];
        buttonauxpath.Tooltip = 'Click to select the path';

        GUIpathdirectory(src,evt,'update',miesar_para,[],hfig);

    case 'update'

        if exist(get(findobj(fig,'Tag','textSLCpath'),'Value')) == 7
            set(findobj(fig,'Tag','textSLCpath'),'FontColor','green','FontWeight','bold');
        else
            set(findobj(fig,'Tag','textSLCpath'),'FontColor','red','FontWeight','bold');
        end 

        if exist(get(findobj(fig,'Tag','textorbitpath'),'Value')) == 7
            set(findobj(fig,'Tag','textorbitpath'),'FontColor','green','FontWeight','bold');
        else
            set(findobj(fig,'Tag','textorbitpath'),'FontColor','red','FontWeight','bold');
        end 

        if exist(get(findobj(fig,'Tag','textauxpath'),'Value')) == 7
            set(findobj(fig,'Tag','textauxpath'),'FontColor','green','FontWeight','bold');
        else
            set(findobj(fig,'Tag','textauxpath'),'FontColor','red','FontWeight','bold');
        end 
            
        pathSLC = get(findobj(fig,'Tag','textSLCpath'),'Value');
        pathorbit = get(findobj(fig,'Tag','textorbitpath'),'Value');
        pathaux = get(findobj(fig,'Tag','textauxpath'),'Value');

        save([miesar_para.WK,'/parmsSLC.mat'],'pathSLC','pathorbit','pathaux','-append');

    case 'gui'
        tmppath = uigetdir(miesar_para.WK); 
        switch mode 
            case 'slc'
                set(findobj(fig,'Tag','textSLCpath'),'Value',tmppath);
            case 'orbits'
                set(findobj(fig,'Tag','textorbitpath'),'Value',tmppath);
            case 'aux'
                set(findobj(fig,'Tag','textauxpath'),'Value',tmppath);
        end 
        GUIpathdirectory(src,evt,'update',miesar_para,[],fig);

end 