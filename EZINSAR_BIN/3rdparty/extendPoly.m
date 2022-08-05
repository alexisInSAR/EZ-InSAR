function [extendedPolyCell] =  extendPoly(Polygon,varargin)
% Extends a polygon by the specified range and calculates the resulting 
% polygon with the specified resolution. Requires basic Matlab and no 
% additional toolboxes.
% 
% Usage: 
%  extendedPolygon = extendPoly ( originalPolygon , range, resolution )
%
%  mandatory:
%  ----------
%  originalPolygon =   <Nx2 double> array that represent the polygons 
%                      which are defined either CW or CCW
%  range           =   radius with which the polygon is to be extended 
%  extendedPolygon =   cellarray with CW or CCW corresponding with the input
%                      polygon
%
%  optional:
%  ---------
%  resolution      =   sets the resultion with which the circular parts of
%                      the extension are drawns. Default pi/50.
%
% Limitations:
%  - Polygon is not allowed to have crossing line sections
%    (selfintersections)
%  - Only 2D Polygons allowed
%  - Unpredictable results when negative range is specified
%
% Example:
%  Polygon = [0,0;4,0;2,6;0,4];
%  extendedPolygon = extendPoly(Polygon,0.4);
%  figure(1); clf; patch(Polygon(:,1),Polygon(:,2),'r');
%  for i=1:length(extendedPolygon)
%    toPlot=extendedPolygon{i};
%    line(toPlot(:,1),toPlot(:,2),'Color','b');
%  end
%
% -------------------------------------------------------------------------
% Version: 1.5 Date: 10-11-2008 
% Tested on Matlab 7.6.0 (R2008b)
%
% Lt. Krispijn A. Scholte
% CAMS-Force Vision, Den Helder (The Netherlands)
% email: krispijn_s@hotmail.com
% 
% Makes use of NS "InterX" algorithm for curve intersection (embedded)
% http://www.mathworks.com/matlabcentral/fileexchange/22441
% -------------------------------------------------------------------------
%
% Version history:
%  1.0  Initial (unreleased)
%  1.1  Multiple small bug fixes
%  1.2  Fixed CW/CCW detection bug
%  1.3  Added error and warning messages, automatically closes polygon if 
%       input polygon is not closed.
%  1.4  New faster CW/CCW detection method. Old method prevented returning 
%       results when the polygon has only negative x-values. 
%  1.5  Replaced selfintersection algorithm because it yielded inaccurate
%       results; added user definable resolution parameter for drawing the
%       circle pieces of the resulting polygon.
%% Verify input and generate error and warning messages if needed
%test number of input arguments; error if incorrect
if nargin < 2 || nargin > 3
    error('extendPoly:InputFormating',['Wrong number of input arguments: ',num2str(nargin),' given; 2 required.']);
end
if nargin == 2
    range = varargin{1};
    res = pi/50; % use default
    warning('extendPoly:InputFormating','No drawing resolution specified. Reverting to default (pi/50).');
else
    range = varargin{1};
    res = varargin{2};
end
%test if a negative range is specified; generate warning if so
if range < 0
    warning('extendPoly:InputFormating','Negative range specified. Results may not be correct.');
end
 
%test if the input polygon is a real polygon; error if not.
if size(unique(Polygon,'rows'),1) < 3
    error('extendPoly:InputFormating',['Specified input polygon is not a polygon (number of unique points is ',num2str(length(unique(Polygon))),').']);
end
%test input polygon is closed; if not generate warning and close polygon
if sum(single(Polygon(end,:)) == single(Polygon(1,:))) < 2 % test with single precision
    Polygon(end+1,:)=Polygon(1,:);
    warning('extendPoly:InputFormating','Input polygon is not closed.');
end
%test input polygon for self intersections (NOT ALLOWED)
P = InterX(Polygon');
SegPoints = P';
if ~isempty(SegPoints)
    
    %if one self intersection occurs it needs to be tested because this is 
    %often occurs where the polygon is closed. If the self intersection
    %point is a polygon point, then it is allowed. If it is not, then
    %generate an error
    
    if size(SegPoints,1) > 1 
       error('extendPoly:InputFormating','Input polygon has self intersections.'); 
    else
        pointMatched = false;
        
        for i=1:size(Polygon(1,:))
            if sum(single(Polygon(i,:)) == single(SegPoints(1,:))) == 2
                %x and y coordinates match, so this intersection is part of
                %the polygon (probably due to closing the polygon
                pointMatched = true;
                break
            end
        end
        
        if ~pointMatched 
            error('extendPoly:InputFormating','Input polygon has self intersections.'); 
        end
    end
end
%% Set configuration
% These numbers can be modified to improve precision or speed. Current
% values have yielded good, stable results on a wide variety of polygons,
% but feel free to adjust them if the initial results are less than
% satisfactory.
global stepSize;                    %stepsize used for defining a test circle around points to be tested
global polySize;                    %number of datapoints in the original polygon
CCW = false;                        %assumes the polygon is defined CW, which will be tested below 
extendedPoly=zeros(1,2);            %create an empty matrix for the extended polygon
j=1;                                %extendedPolygon node counter
pointTestTolerance = .997;           %tolerance for the point test
                       %resolution with which the radius around polygon points are drawn
polySize = length(Polygon(:,1));  
%determine circleTest stepsize (used very very frequently)
xscale = max(Polygon(:,1))-min(Polygon(:,1));
yscale = max(Polygon(:,2))-min(Polygon(:,2));
scaler = (sqrt(xscale^2+yscale^2))/range; %scaler is used to decrease stepSize if the range increases
if scaler < 2
    scaler = 2;
end
stepSize =.25/scaler;
%% Determine if input polygon is specified CW/CCW
% first point is drawn; test if point is in polygon and range specified
% is positive, if so -> polygon is defined CCW (program default assumes CW)
if polySize > 4
    i=round(polySize./2);
else
    i=2;
end
p0=Polygon(i,:); p1=Polygon(i-1,:); p2=Polygon(i+1,:);
Vector1=(p0-p1); Vector2=(p0-p2);
ZeroVec = zeros(size(Vector1));
while isequal(Vector1,Vector2) || isequal(Vector1,ZeroVec) || isequal(Vector2,ZeroVec);
    i=i+1;
    p1=Polygon(i-1,:); p2=Polygon(i+1,:);
    Vector1=(p0-p1); Vector2=(p0-p2);
end
% determine normals and normalise
NV1=rotateVector(Vector1, pi./2); NV2=rotateVector(Vector2, -pi./2);
NormV1=normaliseVector(NV1); NormV2=normaliseVector(NV2);
% test point is based on the two normals
pointToTest=p0+((1-pointTestTolerance)*1e-5.*normaliseVector(NormV1+NormV2));
IN = pointInPolygon (pointToTest,Polygon);
if range > 0 && IN == 1
   % Reverse point order
   CCW = true;
   Polygon = Polygon(end:-1:1,:);
else
   if range < 0 && IN == 0
      % Reverse point order
      CCW = true;
      Polygon = Polygon(end:-1:1,:);
   end
end
%% Extend the polygon by the specified range
% First test if it is a fully closed polygon (eg. first and last 
% coordinates are identical. If such is the case, remove the last entry and
% reduce the polySize
if isequal(single(Polygon(end,:)),single(Polygon(1,:)))
   Polygon = Polygon(1:1:end-1,:);
   polySize = polySize-1;    
end
for i=1:polySize
   % find the two vectors needed
   if i~=1
       if i<polySize
        p0=Polygon(i,:); p1=Polygon(i-1,:); p2=Polygon(i+1,:);   
       else
        p0=Polygon(i,:); p1=Polygon(i-1,:); p2=Polygon(1,:); %special case for i=polySize
       end
   else
        p0=Polygon(i,:); p1=Polygon(polySize,:); p2=Polygon(i+1,:); %special case for i=1
   end
   
   Vector1=(p0-p1); Vector2=(p0-p2);
   
   if ~(isequal(Vector1,Vector2) || isequal(Vector1,ZeroVec) || isequal(Vector2,ZeroVec));
   
       %determine normals and normalise and
       NV1=rotateVector(Vector1, pi./2); NV2=rotateVector(Vector2, -pi./2);
       NormV1=normaliseVector(NV1); NormV2=normaliseVector(NV2);
       %determine rotation by means of the atan2 (because sign matters!)
       
       totalRotation = vectorAngle(NormV2, NormV1);
       rotateVectors = totalRotation:-res:0;
       
       if totalRotation < pi && abs(totalRotation) > res
           
           for k=rotateVectors;
               rotAngle = k;
               newPoint = rotateVector(NormV2,rotAngle);
               nnewp = normaliseVector(newPoint);
               %only add point if it is different from the previous point
               if j > 1
                   if extendedPoly(j-1,:)~=p0+(range*nnewp)
                    extendedPoly(j,:)=p0+(range.*nnewp);j=j+1;
                   end
               else
                   extendedPoly(j,:)=p0+(range.*nnewp);j=j+1;
               end
           end
       else
           % corner < 0 degrees special case or if the total rotation is
           % smaller than the rotation resolution but only if they are
           % different from the previously addes point
           extendedPoly(j,:)=p0+(range.*NormV1);j=j+1;
           extendedPoly(j,:)=p0+(range.*NormV2);j=j+1;
       end      
   end
end
extendedPoly(end+1,:)=extendedPoly(1,:);
%% Clean up the resulting polygon
% look for self intersections then comes the jedimindtrick: how to 
% determine which segpoints to keep? A circle is drawn with a radius range 
% around the segpoint. If this circle intersects with the original polygon 
% it is removed from the list. The resulting segpoints indicate where line 
% segments of the extended polygon need to be removed. Also
% indicates whether there are addition polygons within the extended
% polygon.
if length(extendedPoly(:,1)) > 3
    P = InterX(extendedPoly');
    SegPoints = P';
else
    SegPoints = [];
end
rowsDeleted = 0;
tempSegPoints = SegPoints;
for i=1:1:size(SegPoints,1)
    testResult = newHitTest(SegPoints(i,:),Polygon,range,pointTestTolerance,res);
    
    if testResult == 1
        %remove this segpoint from the list
        tempSegPoints(i-rowsDeleted,:)=[];
        rowsDeleted = rowsDeleted+1;
    end
    
end
SegPoints = tempSegPoints;
pointsAdded=0; 
%determine on which linesections the self intersection points into are 
%they are inserted into the extended Polygon
PointsLog=[];
for j=1:size(extendedPoly,1)
    
    for i=1:1:size(SegPoints,1)
           
        Q1=extendedPoly(j,:);
        
        if j ~= size(extendedPoly,1)
            Q2=extendedPoly(j+1,:);
        else
            Q2=extendedPoly(1,:);
        end
        P=SegPoints(i,:);
        %calculate the distance from the point to the line
        distance=abs(det([Q2-Q1;P-Q1]))/norm(Q2-Q1);
        %determine if the segpoint is on the line
        if distance < eps(single(1))          
            PointsLog = [PointsLog; i, j, j+1];
        end
    end
    
end
% Reorder the matrix
newPointsLog=[];
for i=1:size(SegPoints,1)
    if PointsLog((2*i)-1,1) ~= PointsLog(2*i,1)
        addIndex = find(PointsLog(:,1) == PointsLog((2*i)-1,1));
        for j=1:size(addIndex,1)
           if addIndex(j) ~=  (2*i)-1
              %reorder the matrix 
              newPointsLog = [PointsLog(1:(2*i)-1,:);...
                  PointsLog(addIndex(j),:);...
                  PointsLog((2*i):addIndex(j)-1,:);...
                  PointsLog(addIndex(j)+1:end,:)];
           end
        end
        PointsLog = newPointsLog;
    end
end
% create matrix with removal intervals
% removeIntervals = (SegPoint to be inserted, Point in extendPoly after
% which to add, Point in extendPoly before which to add)
removeIntervals=zeros(size(SegPoints,1),3);
for i=1:size(SegPoints,1)
    removeIntervals(i,1)=PointsLog((2*i)-1,1);
    removeIntervals(i,2)=PointsLog((2*i)-1,2);
    removeIntervals(i,3)=PointsLog(2*i,3-1);
end
Segments = [removeIntervals(:,2),removeIntervals(:,3)];
SegPoints = SegPoints(removeIntervals(:,1),:);
rowsDeleted = 0;
tempSegPoints = SegPoints;
tempSegments = Segments;
for i=1:1:size(SegPoints,1)
    testResult = newHitTest(SegPoints(i,:),Polygon,range,pointTestTolerance,stepSize);
    
    if testResult == 1
        %remove this segpoint from the list
        tempSegPoints(i-rowsDeleted,:)=[];
        tempSegments(i-rowsDeleted,:)=[];
        rowsDeleted = rowsDeleted+1;
    end
    
end
SegPoints = tempSegPoints;
Segments = tempSegments;
pointsAdded=0; 
%insert self intersection points into the extended Polygon
tempPoints = extendedPoly;
for i=1:1:size(SegPoints,1)
    % reuse the segments from the self intersect algorithm
    j=Segments(i,1);
    tempPoints = [tempPoints(1:j+pointsAdded,:);SegPoints(i,:);tempPoints(j+pointsAdded+1:end,:)];
	pointsAdded = pointsAdded+1;
    j=Segments(i,2);
    tempPoints = [tempPoints(1:j+pointsAdded,:);SegPoints(i,:);tempPoints(j+pointsAdded+1:end,:)];
	pointsAdded = pointsAdded+1;
end
extendedPoly = tempPoints;
% Final check to make sure no points are in the polygon that do not belong
% there.
rowsDeleted = 0;
tempPoints = extendedPoly;
for i=1:1:size(extendedPoly,1)
    testResult = newHitTest(extendedPoly(i,:),Polygon,range,pointTestTolerance,stepSize);
    
    if testResult == 1
        %remove this point from the list
        tempPoints(i-rowsDeleted,:)=[];
        rowsDeleted = rowsDeleted+1;
    end
    
end
extendedPoly = tempPoints;
% We now have an hull polygon with possibly internal polygons due to
% intersections by extending the polygon. 
subPolyList=[];
for i=1:size(extendedPoly(:,1))
    if i ~= size(extendedPoly(:,1))
        pointToTest = 0.5.*(extendedPoly(i+1,:)+extendedPoly(i,:));
        testResult = newHitTest(pointToTest,Polygon,range,pointTestTolerance,stepSize);
        
        if testResult == 1
            % after the tested point either starts or stops a new internal
            % polygon but only if this is a segpoint
            subPolyList = [subPolyList; i];
        end
    else
        %Special case for the last point
        pointToTest = 0.5.*(extendedPoly(1,:)+extendedPoly(i,:));
        testResult = newHitTest(pointToTest,Polygon,range,pointTestTolerance,stepSize);
        
        if testResult == 1
            % after the tested point either starts or stops a new internal
            % polygon but only if this is a segpoint
            subPolyList = [subPolyList; i];
        end
    end
end
subPoly=cell(1,size(subPolyList,1));
%process the subPoly's
if ~isempty(subPolyList)
    shift = 0;
    if size(subPolyList,1) > 1
        for i=1:size(subPolyList,1)
            %first add the new poly to the subpoly list
            if shift + i + 1 > size(subPolyList,1)
                break
            end
            
            polyStart = subPolyList(i+shift,1)+1;
            polyStop = subPolyList(i+shift+1,1);
            if polyStop-polyStart > 2
                theNewPoly = extendedPoly(polyStart:polyStop-1,:);
                subPoly{shift+1}=theNewPoly;
                shift = shift + 1;
            end
            
        end
    end
end
%clean up empty cells in subPoly
if ~isempty(subPoly)
    subPoly(cellfun(@isempty,subPoly)) = [];
    %remove determined subpoly points from the hull polygon
    removeIndex = zeros(size(extendedPoly,1),1);
    for i=1:length(subPoly)
        for j=1:size(subPoly{i}(:,1))
            for k=1:size(extendedPoly,1)
                if extendedPoly(k,:)==subPoly{i}(j,:)
                    removeIndex(k,1)=1;
                end
            end
        end
    end
    extendedPoly = extendedPoly(~removeIndex(:,1),:); 
end
%% Finalising the output
% Format the output cell array. The first position is the hull polygon,
% after that the sub polygons are added. All polygons are specified
% according to the input polygon.
extendedPolyCell = cell(1,length(subPoly)+1);
if ~CCW
    extendedPolyCell{1}=extendedPoly;
    % add the sub polies only if they are real Polies (3 or more points)
    if ~isempty(subPoly)
        j=2;
        for i=1:length(subPoly)
            if size(subPoly{i},1) > 3
               extendedPolyCell{j}=subPoly{i}; j=j+1;
            end
        end
    end
else
    %input polygon was CCW defined; make sure the output is too
    
    extendedPolyCell{1}=extendedPoly(end:-1:1,:);
    
    % add the sub polies
    if ~isempty(subPoly)
        j=2;
        for i=1:length(subPoly)
            if size(subPoly{i},1) > 3
               extendedPolyCell{j}=subPoly{i}(end:-1:1,:); j=j+1;
            end
        end
    end
end
%clean up empty cells
extendedPolyCell(cellfun(@isempty,extendedPolyCell)) = [];
%close all polygons if they aren't already
for i=1:length(extendedPolyCell)
    if sum(single(extendedPolyCell{i}(end,:)) == single(extendedPolyCell{i}(1,:))) < 2
        extendedPolyCell{i}(end+1,:)=extendedPolyCell{i}(1,:);
    end
end
%% Embedded Helper functions
%-[Own functions]----------------------------------------------------------
function [rotatedVec] = rotateVector(Vector, angle)
% rotate unity vectors
rotatedVec(1)= cos(angle)*Vector(1) - sin(angle)*Vector(2);
rotatedVec(2)= sin(angle)*Vector(1) + cos(angle)*Vector(2);
function [normVec] = normaliseVector(Vector)
% normalise vector to a unity vector
nv=Vector.^2;scaler=sqrt(nv(1)+nv(2)); 
normVec=(Vector./scaler);
function [angle] = vectorAngle(Vector1,Vector2)
% determine the angle from Vector1 to Vector2
x1=Vector1(1);y1=Vector1(2);
x2=Vector2(1);y2=Vector2(2);
angle = mod(atan2(x1*y2-x2*y1,x1*x2+y1*y2),2*pi); %in radians
function [oddNodes] = pointInPolygon (point,thePolygon)
% determine if a point is in the polygon (faster than matlab "inpolygon"
% command
polyPoints=size(thePolygon,1);    % number of polygon points
oddNodes = false;
j=polyPoints;
x=point(1); y=point(2);
for i=1:polyPoints
    if (thePolygon(i,2)<y && thePolygon(j,2)>=y ||  thePolygon(j,2)<y && thePolygon(i,2)>=y)
        if (thePolygon(i,1)+(y-thePolygon(i,2))/(thePolygon(j,2)-thePolygon(i,2))*(thePolygon(j,1)-thePolygon(i,1))<x)
            oddNodes=~oddNodes;
        end
    end
    j=i; 
end
function [result] = newHitTest (point,Polygon,r,tol,stepSize)
%This function calculates whether a point is allowed.
%First is a quick test is done by calculating the distance from point to 
%each point of the polygon. If that distance is smaller than range "r", 
%the point is not allowed. This will slow down the algorithm at some 
%points, but will greatly speed it up in others because less calls to the 
%circleTest routine are needed.
polySize=size(Polygon,1);
testCounter=0;
for i=1:polySize
    d = sqrt(sum((Polygon(i,:)-point).^2));
    
    if d < tol*r
        testCounter=1;
        break
    end
end
if testCounter == 0
    circleTestResult = circleTest (point,Polygon,r,tol,stepSize);
    testCounter = circleTestResult;
end
result = testCounter;
% |    
  function [result] = circleTest (point,Polygon,r,tol,stepSize)
% draws a circle around the specified point and determines if it is in the
% Polygon or not
circlePoints=0:stepSize:2*pi+stepSize;
%test circle
xs=(tol.*r.*sin(circlePoints))+point(1);
ys=(tol.*r.*cos(circlePoints))+point(2);
%curve intersect has proven to be wrong in a number of cases, so if there
%is no intersection, do a quick point-in-polygon test to check the results
breakCounter = 0;
for j=1:length(xs)
    pInPtest = pointInPolygon ([xs(j),ys(j)],Polygon);
    
    if pInPtest == 1
       breakCounter = breakCounter + 1;
    end
    if breakCounter > 1
        break
    end
   
end
if breakCounter == 0
    result = 0;
else
    result = 1;
end
%-[From Matlab File Exchange]----------------------------------------------
function P = InterX(L1,varargin)
%INTERX Intersection of curves
%   P = INTERX(L1,L2) returns the intersection points of two curves L1 
%   and L2. The curves L1,L2 can be either closed or open and are described
%   by two-row-matrices, where each row contains its x- and y- coordinates.
%   The intersection of groups of curves (e.g. contour lines, multiply 
%   connected regions etc) can also be computed by separating them with a
%   column of NaNs as for example
%
%         L  = [x11 x12 x13 ... NaN x21 x22 x23 ...;
%               y11 y12 y13 ... NaN y21 y22 y23 ...]
%
%   P has the same structure as L1 and L2, and its rows correspond to the
%   x- and y- coordinates of the intersection points of L1 and L2. If no
%   intersections are found, the returned P is empty.
%
%   P = INTERX(L1) returns the self-intersection points of L1. To keep
%   the code simple, the points at which the curve is tangent to itself are
%   not included. P = INTERX(L1,L1) returns all the points of the curve 
%   together with any self-intersection points.
%   
%   Example:
%       t = linspace(0,2*pi);
%       r1 = sin(4*t)+2;  x1 = r1.*cos(t); y1 = r1.*sin(t);
%       r2 = sin(8*t)+2;  x2 = r2.*cos(t); y2 = r2.*sin(t);
%       P = InterX([x1;y1],[x2;y2]);
%       plot(x1,y1,x2,y2,P(1,:),P(2,:),'ro')
%   Author : NS
%   Version: 1.0, 12/12/08
%   Two words about the algorithm: Most of the code is self-explanatory.
%   The only trick lies in the calculation of C1 and C2. To be brief, this
%   is essentially the two-dimensional analog of the condition that needs
%   to be satisfied by a function F(x) that has a zero in the interval
%   [a,b], namely
%           F(a)*F(b) <= 0
%   C1 and C2 exactly do this for each segment of curves 1 and 2
%   respectively. If this condition is satisfied simultaneously for two
%   segments then we know that they will cross at some point. 
%   Each factor of the 'C' arrays is essentially a matrix containing 
%   the numerators of the signed distances between points of one curve
%   and line segments of the other.
    %...Argument checks and assignment of L2
    error(nargchk(1,2,nargin));
    if nargin == 1,
        L2 = L1;    hF = @lt;   %...Avoid the inclusion of common points
    else
        L2 = varargin{1}; hF = @le;
    end
       
    %...Preliminary stuff
    x1  = L1(1,:)';  x2 = L2(1,:);
    y1  = L1(2,:)';  y2 = L2(2,:);
    dx1 = diff(x1); dy1 = diff(y1);
    dx2 = diff(x2); dy2 = diff(y2);
    
    %...Determine 'signed distances'
    S1 = repmat(dx1.*y1(1:end-1) - dy1.*x1(1:end-1),1,size(L2,2)-1);
    S2 = repmat(dx2.*y2(1:end-1) - dy2.*x2(1:end-1),size(L1,2)-1,1);
    
    C1 = feval(hF,(kron(dx1,y2(1:end-1)) - kron(dy1,x2(1:end-1)) - S1).*...
         (kron(dx1,y2(2:end))- kron(dy1,x2(2:end)) - S1),0);       
    
    C2 = feval(hF,(kron(dx2,y1(1:end-1)) - kron(dy2,x1(1:end-1)) - S2).*...
         (kron(dx2,y1(2:end)) - kron(dy2,x1(2:end)) - S2),0);
    %...Obtain the points where an intersection is expected
    [i,j] = find(C1&C2);
    x2 = x2';dx2=dx2';y2=y2';dy2=dy2';  
    L = dy2(j).*dx1(i) - dy1(i).*dx2(j);
    i = i(L~=0); j=j(L~=0); L=L(L~=0);  %...Avoid divisions by 0
    
    %...Solve system of eqs to get the common points
    P = unique([(dx2(j).*(dx1(i).*y1(i) - dy1(i).*x1(i)) ...
         + dx1(i).*(dy2(j).*x2(j) - dx2(j).*y2(j))),...
           dy1(i).*(dy2(j).*x2(j) - dx2(j).*y2(j))...
         + dy2(j).*(dx1(i).*y1(i) - dy1(i).*x1(i))]./[L L],'rows')';
%-----------------------------------------------------------------------EOF
