function isce_switch_stackfunctions(src,evt,action,miesar_para)
%   isce_switch_stackfunctions(src,evt,action,miesar_para)
%       [src]           : callback value
%       [evt]           : callback value
%       [action]        : name of the action to perform (string value)
%       [miesar_para]   : user parameters (struct.)
%
%       Function to switch the directory of ISCE functions (between TopSAR and StripMap)
%
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also conversionstacks_SI_IW, isce_switch_stackfunctions, conversionstacks_SI_SM, parallelizationstepISCE, dem_box_cal, iscedisplayifg, removewatermask_ISCEprocessing_SM, isce_preprocessing_S1_IW, runISCEallstep, isce_preprocessing_SM, selectionofstack, isceprocessing.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.0.0 Beta
%   Date: 11/07/2022
%
%   -------------------------------------------------------
%   Version history:
%           2.0.0 Alpha: Initial (unreleased)

paramslc = load([miesar_para.WK,'/parmsSLC.mat']);
% For security test of path ISCE
[a,pathisce] = system('which stackSentinel.py'); pathisce = strip(pathisce);
[a,pathvalue] =  system('echo $PATH'); pathvalue = strip(pathvalue);

if isempty(strfind(pathisce,'/contrib/stack/topsStack/')) == 0
    if strcmp(paramslc.mode,'S1_IW') == 0
        pathvalue = strrep(pathvalue,'/contrib/stack/topsStack','/contrib/stack/stripmapStack');
    end
else
    if strcmp(paramslc.mode,'S1_IW') == 1
        pathvalue = strrep(pathvalue,'/contrib/stack/stripmapStack','/contrib/stack/topsStack');
    end
end
setenv('PATH',pathvalue)