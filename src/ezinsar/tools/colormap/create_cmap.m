%% Create the colormap based on MATLAB (part of EZ-InSAR)
clear all; close all; clc; 
   
list = {'parula','turbo','hsv','cool','hot','gray','jet'}; 

for i1 = 1: length(list)
    color = fix(colormap(list{i1}).*255); 
    fout = fopen(['cmap_',list{i1},'.csv'],'w'); 
    fprintf(fout,'%d %d %d\n',color'); 
    fclose(fout); 
end 