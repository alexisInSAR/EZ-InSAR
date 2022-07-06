function update_progressbar_MIESAR(src,evt,miesar_para,action)
%   update_progressbar_MIESAR(src,evt,miesar_para,action)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to manage the progress bar of EZ-InSAR.
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 30/11/2021
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)

switch action
    case 'isce'
        fi = fopen([miesar_para.WK,'/stackstepisce.log'],'r'); logstack = textscan(fi,'%s %s'); fclose(fi);
        IndexC = cell2mat(strfind(logstack{2},['RUN']));
        a = sum(IndexC);
        b = length(logstack{2});

        set(findobj(gcf,'Tag','name_progressbar'),'Text','ISCE Processing');

        % Read the log
        if a./b == 1
            si = sprintf('It seems that the ISCE processing is done.');
        elseif a./b == 0
            si = sprintf('No already ISCE processing detected.');
        else
            si = sprintf('ISCE processing detected: %d/%d.\nThe last done step is: %s. Please continue the processing with %s',a,b,logstack{1}{a},logstack{1}{a+1});
        end
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si,'FontColor','blue');

    case 'MintPy'
        fi = fopen([miesar_para.WK,'/stepmintpy.log'],'r'); logstack = textscan(fi,'%s %s'); fclose(fi);
        IndexC = strfind(logstack{2},['RUN']);
        idx1 = find(not(cellfun('isempty',IndexC)));
        IndexC = strfind(logstack{2},['OPT']);
        idx2 = find(not(cellfun('isempty',IndexC)));

        a = numel(idx1);
        b = length(logstack{2})-numel(idx2);

        set(findobj(gcf,'Tag','name_progressbar'),'Text','MintPy Processing');

        % Read the log
        if a./b == 1
            si = sprintf('It seems that the MintPy processing is done.');
        elseif a./b == 0
            si = sprintf('No already MintPy processing detected.');
        else
            si = sprintf('MintPy processing detected: %d/%d.\nThe last done step is: %s. Please continue the processing with %s',a,b,logstack{1}{idx1(a)},logstack{1}{idx1(a)+1});
        end
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si,'FontColor','blue');

    case 'stampsPS'
        fi = fopen([miesar_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{1};

        fi = fopen([pathstampsprocessing,'/PSprocess.log'],'r'); logstack = textscan(fi,'%s %s'); fclose(fi);
        IndexC = cell2mat(strfind(logstack{2},['RUN']));
        a = sum(IndexC);
        b = length(logstack{2})-2;

        set(findobj(gcf,'Tag','name_progressbar'),'Text','StaMPS Processing: PS');

        % Read the log
        if a./b == 1
            si = sprintf('It seems that the StaMPS PS processing is done.');
        elseif a./b == 0
            si = sprintf('No already StaMPS PS processing detected.');
        else
            si = sprintf('StaMPS PS processing detected: %d/%d.\nThe last done step is: %s. Please continue the processing with %s',a,b,logstack{1}{a+2},logstack{1}{a+2+1});
        end
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si,'FontColor','blue');

    case 'stampsSBAS'
        fi = fopen([miesar_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{1};

        fi = fopen([pathstampsprocessing,'/SBASprocess.log'],'r'); logstack = textscan(fi,'%s %s'); fclose(fi);
        IndexC = cell2mat(strfind(logstack{2},['RUN']));
        a = sum(IndexC);
        b = length(logstack{2})-4;

        set(findobj(gcf,'Tag','name_progressbar'),'Text','StaMPS Processing: SBAS');

        % Read the log
        if a./b == 1
            si = sprintf('It seems that the StaMPS SBAS processing is done.');
        elseif a./b == 0
            si = sprintf('No already StaMPS SBAS processing detected.');
        else
            si = sprintf('StaMPS SBAS processing detected: %d/%d.\nThe last done step is: %s. Please continue the processing with %s',a,b,logstack{1}{a+4},logstack{1}{a+4+1});
        end
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si,'FontColor','blue');

   case 'stampsMERGED'
        fi = fopen([miesar_para.WK,'/stampsdirectory.log'],'r');
        pathstampsprocessing = textscan(fi,'%s'); fclose(fi); pathstampsprocessing = pathstampsprocessing{1}{1};

        fi = fopen([pathstampsprocessing,'/Mergedprocess.log'],'r'); logstack = textscan(fi,'%s %s'); fclose(fi);
        IndexC = cell2mat(strfind(logstack{2},['RUN']));
        a = sum(IndexC);
        b = length(logstack{2})-2;

        set(findobj(gcf,'Tag','name_progressbar'),'Text','StaMPS Processing: MERGED');

        % Read the log
        if a./b == 1
            si = sprintf('It seems that the StaMPS MERGED processing is done.');
        elseif a./b == 0
            si = sprintf('No already StaMPS MERGED processing detected.');
        else
            si = sprintf('StaMPS MERGED processing detected: %d/%d.\nThe last done step is: %s. Please continue the processing with %s',a,b,logstack{1}{(a+2)},logstack{1}{(a)+2+1});
        end
        set(findobj(gcf,'Tag','maintextoutput'),'Value',si,'FontColor','blue');
       
       case 'defaut'
       	ratio = src;
       	b = 1; 
       	a = ratio;      
end

%% Update the progress bar
if strcmp(action,'defaut')
    axitmp = evt;
else
    axitmp = findobj(gcf,'Tag','progressbar');
end 
cla(axitmp)
axitmp.XLim = [0 100];
axitmp.YLim = [0 1];
plot(axitmp,[0 100 100 0 0],[0 0 1 1 0],'-k','LineWidth',2)
axitmp.YTick = [];

if a./b == 1
    axitmp.XTick = [0 a./b].*100;
    axitmp.XTickLabel = {'0 %', [num2str([a./b].*100,'%.1f'), '%']};
    patchcolor = 'green';
elseif a./b == 0
    axitmp.XTick = [a./b 1].*100;
    axitmp.XTickLabel = {[num2str([a./b].*100,'%.1f'), '%'], '100 %'};
    patchcolor = 'blue';
else
    axitmp.XTick = [0 a./b 1].*100;
    axitmp.XTickLabel = {'0 %', [num2str([a./b].*100,'%.1f'), '%'],'100 %'};
    patchcolor = 'blue';
end

hold on; patch(axitmp,[0 a./b a./b 0 0].*100 ,[0 0 1 1 0],patchcolor,'FaceAlpha',0.75,'EdgeColor','none'); hold off;
