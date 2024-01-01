function hash = string2hash(string)
%   string2hash(string)
%
%       Function to generate an unique user id. 
%          
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 1.0.0 Beta
%   Date: 06/07/2022
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)

persistent md
if isempty(md)
    md = java.security.MessageDigest.getInstance('MD5');
end
hash = sprintf('%2.2x', typecast(md.digest(uint8(string)), 'uint8')');
end
