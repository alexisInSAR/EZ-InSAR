function [index] = searchindex(BWl,indnl1,indnl2,indnc1,indnc2,nbrand) 
    index = []; 
    indexnlin = fix(rand(nbrand,1).*(indnl2-indnl1)+indnl1);
    indexncol = fix(rand(nbrand,1).*(indnc2-indnc1)+indnc1);

    for j1 = 1 : length(indexnlin)
        index=[index; BWl(indexnlin(j1),indexncol(j1))];
    end
    index=mode(index);
end 