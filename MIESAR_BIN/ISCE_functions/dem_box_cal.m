function dem_region=dem_box_cal(lonta,lata,box_burst)
%   Function to calculate the overlap region between AOI box and the S1 burst footprints 
%   Copyright 2022 Xiaowen Wang, UCD
%   Date: 23/02/2022
%
poly_aoi=polyshape([min(lonta) max(lonta) max(lonta) min(lonta)],[min(lata) min(lata) max(lata) max(lata)]);
burst_overlap=[];
%% IW1
for i1 = 1 : size(box_burst.IW1.lat,1)     
   for j1 = 1 : size(box_burst.IW1.lat,2)    
          lat_limit=cell2mat(box_burst.IW1.lat(i1,j1));
          lon_limit=cell2mat(box_burst.IW1.lon(i1,j1));  
       if isempty(lat_limit) == 0 && isempty(lon_limit) == 0                  
          poly_burst=polyshape([lon_limit(1) lon_limit(2) lon_limit(2) lon_limit(1)],[lat_limit(1) lat_limit(1) lat_limit(2) lat_limit(2)]);             
          flg_polyout = intersect(poly_aoi,poly_burst);
          if isempty(flg_polyout.Vertices) == 0 
              burst_limt=[lon_limit(1) lon_limit(2) lat_limit(1) lat_limit(2)]; 
              burst_overlap=[burst_overlap;burst_limt];
          end 
       end       
   end
end 
%% IW2
for i1 = 1 : size(box_burst.IW2.lat,1)     
   for j1 = 1 : size(box_burst.IW2.lat,2)    
          lat_limit=cell2mat(box_burst.IW2.lat(i1,j1));
          lon_limit=cell2mat(box_burst.IW2.lon(i1,j1));   
       if isempty(lat_limit) == 0 && isempty(lon_limit) == 0                 
          poly_burst=polyshape([lon_limit(1) lon_limit(2) lon_limit(2) lon_limit(1)],[lat_limit(1) lat_limit(1) lat_limit(2) lat_limit(2)]);             
          flg_polyout = intersect(poly_aoi,poly_burst);
          if isempty(flg_polyout.Vertices) == 0 
              burst_limt=[lon_limit(1) lon_limit(2) lat_limit(1) lat_limit(2)]; 
              burst_overlap=[burst_overlap;burst_limt];
          end  
       end              
   end
end    
%% IW3                 
for i1 = 1 : size(box_burst.IW3.lat,1)     
   for j1 = 1 : size(box_burst.IW3.lat,2)    
          lat_limit=cell2mat(box_burst.IW3.lat(i1,j1));
          lon_limit=cell2mat(box_burst.IW3.lon(i1,j1)); 
       if isempty(lat_limit) == 0 && isempty(lon_limit) == 0                   
          poly_burst=polyshape([lon_limit(1) lon_limit(2) lon_limit(2) lon_limit(1)],[lat_limit(1) lat_limit(1) lat_limit(2) lat_limit(2)]);             
          flg_polyout = intersect(poly_aoi,poly_burst);
          if isempty(flg_polyout.Vertices) == 0 
              burst_limt=[lon_limit(1) lon_limit(2) lat_limit(1) lat_limit(2)]; 
              burst_overlap=[burst_overlap;burst_limt];
          end 
       end        
   end
end 

  dem_region=[min(burst_overlap(:,1)),max(burst_overlap(:,2)),min(burst_overlap(:,3)),max(burst_overlap(:,4))];
end

