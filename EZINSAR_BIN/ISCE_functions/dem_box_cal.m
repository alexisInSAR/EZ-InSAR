function dem_region=dem_box_cal(lonta,lata,box_burst)
%   dem_box_cal(lonta,lata,box_burst)
%
%       Function to calculate the overlap region between AOI box and the S1 burst footprints
%
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also conversionstacks_SI_IW, isce_switch_stackfunctions, conversionstacks_SI_SM, parallelizationstepISCE, dem_box_cal, iscedisplayifg, removewatermask_ISCEprocessing_SM, isce_preprocessing_S1_IW, runISCEallstep, isce_preprocessing_SM, selectionofstack, isceprocessing.
%
%   -------------------------------------------------------
%   Xiaowen Wang, UCD
%   Version: 2.0.0 Beta
%   Date: 23/02/2022
%
%   -------------------------------------------------------
%   Modified:
%           - Alexis Hrysiewicz, UCD / iCRAG, 07/07/2022: StripMap
%           implementation
%
%   -------------------------------------------------------
%   Version history:
%           1.0.0 Beta: Initial (unreleased)
%           2.0.0 Beta: Initial (unreleased)

poly_aoi=polyshape([min(lonta) max(lonta) max(lonta) min(lonta)],[min(lata) min(lata) max(lata) max(lata)]);
burst_overlap=[];
%% IW1
if isfield(box_burst,'IW1')
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
end

%% IW2
if isfield(box_burst,'IW2')
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
end

%% IW3
if isfield(box_burst,'IW3')
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
end

dem_region=[min(burst_overlap(:,1)),max(burst_overlap(:,2)),min(burst_overlap(:,3)),max(burst_overlap(:,4))];
end

