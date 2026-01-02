%   cohstack
%
%       Class for the BWLava application
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.0.0 Beta
%   Date: 21/11/2024
%
%   -------------------------------------------------------
%   Modified:
%
%   -------------------------------------------------------
%   Version history:
%           2.0.0 Beta: Initial (unreleased)

classdef cohstack
    properties (Access = public)
        X(:,:) double {mustBeReal, mustBeReal} = [] 
        Y(:,:) double {mustBeReal, mustBeReal} = [] 

        Xcrop(:,:) double {mustBeReal, mustBeReal} = [] 
        Ycrop(:,:) double {mustBeReal, mustBeReal} = [] 

        coherence(:,:,:) double {mustBeReal, mustBeReal} = []
        coherencecrop(:,:,:) double {mustBeReal, mustBeReal} = [] 
        coherencefilt(:,:,:) double {mustBeReal, mustBeReal} = [] 

        maskraw(:,:,:) double {mustBeReal, mustBeReal} = []

        mask(:,:,:) double {mustBeReal, mustBeReal} = []

        kernelfilt(:,1) double {mustBeReal, mustBeReal} = []

        thesholdvalue(:,1) double {mustBeReal, mustBeReal} = []

        outlines(:,2) cell = cell(1,2);

        date1(:,:) datetime {mustBeVector} = NaT(0,1)
        date2(:,:) datetime {mustBeVector} = NaT(0,1) 

        files(:,1) cell = cell(1);
    end

    methods
        %% Method to open the coherence image(s)
        function T = stack2table(obj)
            tablecell = cell(1); 

            for i1 = 1 : length(obj.date1)
                tablecell{i1,1} = obj.files{i1}; 
                tablecell{i1,2} = obj.date1(i1); 
                tablecell{i1,3} = obj.date2(i1); 
                tablecell{i1,4} = obj.kernelfilt(i1); 
                tablecell{i1,5} = obj.thesholdvalue(i1); 
            end 
            T = cell2table(tablecell, 'VariableNames',{'Filename','Date 1','Date 2','Filter Kernel','Threshold'}); 
 
        end
    end
end

