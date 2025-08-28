function col = datemodlist(col)
tmpvec = [];
for itx = 1 : length(col)
    if contains(col{itx,1},'.') == 0
        tmp = strrep(strrep(col{itx,1},'Z','.000000Z'),'Z','');
    else
        tmp = strrep(col{itx,1},'Z','');
    end
    tmpvec = [tmpvec; datetime(tmp,'InputFormat','yyyy-MM-dd''T''HH:mm:ss.SSSSSS','Format','yyyy-MM-dd''T''HH:mm:ss.SSS')];
end
col = tmpvec;
end