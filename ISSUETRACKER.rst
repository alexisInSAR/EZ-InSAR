Issue tracker
=============

GDAL => 3.11
------------

This version currently is not compatible with EZ-InSAR.

Multi-InSAR operator of SNAP
----------------------------

The operator *Multi-InSAR* does not work with the version 11 and 12 of SNAP, i.e., only the stack mode *StaMPS_PS* can be used. 

* Alexis Hrysiewicz, 27 May. 2025

Incompatibility with Shapely 2.0.X, Numpy 2.0.X
-----------------------------------------------

* If new version of shapely is used, it requires any new version of numpy. However, old version of numpy can be required for GDAL. In addition, new version of shapely is required for other packages. 

* Alexis Hrysiewicz, 15 Mar. 2025

