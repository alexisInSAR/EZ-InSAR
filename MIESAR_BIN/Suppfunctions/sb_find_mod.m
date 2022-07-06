function []=sb_find_mod(rho_min,ddiff_max,bdiff_max)
%SB_FIND find small baselines
%   SB_FIND(RHO_MIN,DDIFF_MAX,BDIFF_MAX)
%
%   RHO_MIN:   minumum coherence (default=0.50)
%   DDIFF_MAX: time in days for total decorrelation (default=1500)
%   BDIFF_MAX: critical baseline in m (default=1070)
%
%   Andy Hooper, September 2006
%
%   ======================================================================
%   04/2008 AH: Criteria for selection changed to coherence basis 
%   ======================================================================
%   Script is part of StaMPS https://github.com/dbekaert/StaMPS/releases/tag/v4.1-beta
%
%   -------------------------------------------------------
%   Modified:
%           - Alexis Hrysiewicz, UCD / iCRAG: compatibility with EZ-InSAR 


if nargin<1
    rho_min=0.5
end

if nargin<2
    ddiff_max=1500
end

if nargin<3
    bdiff_max=1070
end

load psver
psname=['ps',num2str(psver)];
ps=load(psname);


sbname='small_baselines.list';

[X,Y]=meshgrid(ps.bperp',ps.bperp);
bdiff=abs(X-Y);
[X,Y]=meshgrid(ps.day',ps.day);
ddiff=abs(X-Y);
N=size(X,1);

rho=(1-bdiff/bdiff_max).*(1-ddiff/ddiff_max); % correlation
rho(bdiff>bdiff_max|ddiff>ddiff_max)=0;
rho=rho-eye(N);
ix=(rho>rho_min&~tril(ones(ps.n_ifg)));

[dummy,I]=max(rho);
best_ix=(sort([1:N;I]));
for i=1:N
    ix(best_ix(1,i),best_ix(2,i))=1;
end
[x,y]=find(ix);


%[x,y]=find((rho>rho_min|I|I2)&~tril(ones(ps.n_ifg)));
%[x,y]=find(bdiff<bdiff_max&ddiff<ddiff_max&~tril(ones(ps.n_ifg)));

no_conn_ix=find(sum(rho>rho_min)==0);



sortxy=sortrows([x,y]);
x=sortxy(:,1);
y=sortxy(:,2);

fid=fopen(sbname,'w');
for i=1:length(x)
    fprintf(fid,'%s %s\n',datestr(ps.day(x(i)),'yyyymmdd'),datestr(ps.day(y(i)),'yyyymmdd'));
end
fclose(fid);

