function hash = string2hash(string)
persistent md
if isempty(md)
    md = java.security.MessageDigest.getInstance('MD5');
end
hash = sprintf('%2.2x', typecast(md.digest(uint8(string)), 'uint8')');
end