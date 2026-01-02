#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module for geodetic functions

    
    (From `ezinsar` package)

Changelog:
        * 3.1.0: Initial version, Feb. 2025

Note: 
        FORK FROM snap-engine-master/snap-engine-utilities/src/main/java/org/esa/snap/engine_utilities/eo/GeoUtils.java
"""

################################################################################
## Python packages
################################################################################
import numpy as np  
from typing import Optional

################################################################################
## Constants
################################################################################
class WGS84:
        '''WGS84 information
        '''
        def __init__(self):
                self.a = 6378137.0
                self.b = 6356752.3142451794975639665996337
                self.earthFlatCoef = 1.0 / ((self.a - self.b) / self.a)
                self.e2 = 2.0 / self.earthFlatCoef - 1.0 / (self.earthFlatCoef * self.earthFlatCoef)
                self.e2inv = 1 - self.e2
                self.ep2 = self.e2 / (1 - self.e2)

class GRS80:
        '''GRS80 information
        '''
        def __init__(self):
                self.a = 6378137.0
                self.b = 6356752.314140
                self.earthFlatCoef = 1.0 / ((self.a - self.b) / self.a)
                self.e2 = 2.0 / self.earthFlatCoef - 1.0 / (self.earthFlatCoef * self.earthFlatCoef)
                self.e2inv = 1 - self.e2
                self.ep2 = self.e2 / (1 - self.e2)

################################################################################
## Functions 
################################################################################
def get_distanceheading(lat1,lon1,lat2,lon2, 
                ell: Optional[any] = 'WGS84'):
        """Compute the headings and distance from two latitude and longitude points 

        Args:
                lat1: latitude of the point 1 
                lon1: longitude of the point 1 
                lat1: latitude of the point 2
                lon1: longitude of the point 2
                ell (str, Optional): Ellipsoid name [Default: WGS84]

        Returns:
                (float): heading 1
                (float): heading 2
                (float): distance in meters

        """  

        if ell == 'WGS84':
                ell = WGS84()
        elif ell == 'GRS80':
                ell = GRS80()

        lat1 = np.deg2rad(lat1)
        lat2 = np.deg2rad(lat2)
        lon1 = np.deg2rad(lon1)
        lon2 = np.deg2rad(lon2)

        F=1/ell.earthFlatCoef
        R = 1 - F
        TU1 = R * np.tan(lat1)
        TU2 = R * np.tan(lat2)

        CU1 = 1.0 / np.sqrt(TU1 * TU1 + 1.0)
        SU1 = CU1 * TU1
        CU2 = 1.0 / np.sqrt(TU2 * TU2 + 1.0)
        S = CU1 * CU2
        BAZ = S * TU2
        FAZ = BAZ * TU1
        X = lon2 - lon1

        SX = np.sin(X)
        CX = np.cos(X)
        TU1 = CU2 * SX
        TU2 = BAZ - SU1 * CU2 * CX
        SY = np.sqrt(TU1 * TU1 + TU2 * TU2)
        CY = S * CX + FAZ
        Y = np.arctan2(SY, CY)
        SA = S * SX / SY
        C2A = -SA * SA + 1.
        CZ = FAZ + FAZ
        if (C2A > 0.):   
                CZ = -CZ / C2A + CY
        E = CZ * CZ * 2. - 1.
        C = ((-3. * C2A + 4.) * F + 4.) * C2A * F / 16.
        D = X
        X = ((E * CY * C + CZ) * SY * C + Y) * SA
        X = (1. - C) * X * F + lon2 - lon1

        FAZ = np.arctan2(TU1, TU2)
        BAZ = np.arctan2(CU1 * SX, BAZ * CX - SU1 * CU2) + np.pi

        X = np.sqrt((1. / R / R - 1.) * C2A + 1.) + 1.
        X = (X - 2.) / X
        C = 1. - X
        C = (X * X / 4. + 1.) / C
        D = (0.375 * X * X - 1.) * X
        X = E * CY
        S = 1. - E - E
        S = ((((SY * SY * 4. - 3.) * S * CZ * D / 6. - X) * D / 4. + CZ) * SY * D + Y) * C * ell.a * R

        if np.rad2deg(FAZ) < 0:
                FAZ = FAZ + 2*np.pi
        if np.rad2deg(BAZ) < 0:
                BAZ = BAZ + 2*np.pi

        return FAZ, BAZ, S











# def geo2xyzWGS84(longitude,latitude,altitude):

#         a = 6378137.0
#         b = 6356752.3142451794975639665996337
#         earthFlatCoef = 1.0 / ((a - b) / a)
#         e2 = 2.0 / earthFlatCoef - 1.0 / (earthFlatCoef * earthFlatCoef)
#         e2inv = 1 - e2
#         ep2 = e2 / (1 - e2)

#         lat = np.deg2rad(np.array(latitude))
#         lon = np.deg2rad(np.array(longitude))

#         sinLat = np.sin(lat)
#         N = (a / np.sqrt(1.0 - e2 * sinLat * sinLat))
#         NcosLat = (N + altitude) * np.cos(lat)

#         x = NcosLat * np.cos(lon)
#         y = NcosLat * np.sin(lon)
#         z = (N + altitude - e2 * N) * sinLat

#         return x.tolist(), y.tolist(), z.tolist()