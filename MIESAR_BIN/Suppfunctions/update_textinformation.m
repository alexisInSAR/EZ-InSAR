function update_textinformation(src,evt,miesar_para,message,type)
%   update_progressbar_MIESAR(src,evt,miesar_para,action)
%       [src]           : callback value
%       [evt]           : callback value
%       [message]       : message to be displayed
%       [type]          : type of message [information, sucess, error]
%
%       Function to display some information
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 18/07/2021
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)

set(findobj(gcf,'Tag','maintextoutput'),'Value',message);
switch type 
    case 'error'
        set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
    case 'sucess'
        set(findobj(gcf,'Tag','maintextoutput'),'FontColor','green');
    case 'information'
        set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');
    case 'progress'
        set(findobj(gcf,'Tag','maintextoutput'),'FontColor','blue');
end 

pause(0.001); 
