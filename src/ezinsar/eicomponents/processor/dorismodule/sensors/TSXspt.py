#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to support TSX SPT data with Doris processor 

The module allows to support TSX SPT data with Doris processor from an ``ezinsar.coregistration`` job. 
    
    (From `ezinsar` package)

Changelog:
    * 1.1.0: Initial version, Feb. 2025

"""

################################################################################
## Python packages
################################################################################
import os 
from typing import Optional
import zipfile
import datetime
import xml.etree.ElementTree as ET
import numpy as np
from scipy.interpolate import LinearNDInterpolator
from shapely.wkt import loads
from scipy import interpolate
import shutil
import glob 

from ezinsar.eicomponents.sensor.s1module import s1slctools
from ezinsar.eicomponents.processor.dorismodule import doristools
from ezinsar import usermessage
from ezinsar import constants

__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""
################################################################################
## Import a Sentinel-1 Stripmap image
################################################################################
def computefrqmatrixTSXSPT(leaderfile,
    outputfile,
    nb_lines,
    nb_pixels,
    log: Optional[bool] = None,
    verbose: Optional[bool] = None):
    """Compute the frequency matrix for TSX SPT-like imagery

    The function computes the frequency matrix for TSX SPT-like imagery. It requires for the cc6p_SP algorithm.   

    Args:
        leaderfile (str): path of the leader file
        outputfile (str): path of the output raw file
        nb_lines (int): Number of lines
        nb_pixels (int): Number of pixels
        log (bool): log [Default: `None`].
        verbose (bool): verbose [Default: `None`].

    """
    usermessage.openingmsg(__name__,computefrqmatrixTSXSPT.__name__,__file__,__copyright__,'Compute the frequency matrix for TSX SPT-like imagery',log,verbose)

    xmlfileslc = ET.parse(leaderfile)

    INTnumberOfDopplerRecords = int(xmlfileslc.findall('.//processing/doppler/dopplerCentroid/numberOfDopplerRecords')[0].text)

    # double db_dCdEtimeUTC(256);
    db_dCdEtimeUTC = []
    for nodes in xmlfileslc.findall('.//processing/doppler/dopplerCentroid/dopplerEstimate/timeUTC'):
        p1 = nodes.text.split('T')[-1].split('Z')[0].split(':')
        ti = float(p1[0])*3600 + float(p1[1])*60 + float(p1[2])
        db_dCdEtimeUTC.append(ti)
    db_dCdEtimeUTC = np.array(db_dCdEtimeUTC)

    # double db_GdRtimeUTC(256);
    db_GdRtimeUTC = []
    for nodes in xmlfileslc.findall('.//processing/geometry/dopplerRate/timeUTC'):
        p1 = nodes.text.split('T')[-1].split('Z')[0].split(':')
        ti = float(p1[0])*3600 + float(p1[1])*60 + float(p1[2])
        db_GdRtimeUTC.append(ti)
    db_GdRtimeUTC = np.array(db_GdRtimeUTC)

    # double db_startTimeUTC;
    p1 = xmlfileslc.findall('.//productInfo/sceneInfo/start/timeUTC')[0].text.split('T')[-1].split('Z')[0].split(':')
    db_startTimeUTC = float(p1[0])*3600 + float(p1[1])*60 + float(p1[2])

    # double db_stopTimeUTC;
    p1 = xmlfileslc.findall('.//productInfo/sceneInfo/stop/timeUTC')[0].text.split('T')[-1].split('Z')[0].split(':')
    db_stopTimeUTC = float(p1[0])*3600 + float(p1[1])*60 + float(p1[2])

    # double db_DopplerRateCoeff0(1);
    db_DopplerRateCoeff0 = []
    for nodes in xmlfileslc.findall('.//processing/geometry/dopplerRate/dopplerRatePolynomial/coefficient[@exponent="0"]'):
        db_DopplerRateCoeff0.append(float(nodes.text))
    db_DopplerRateCoeff0 = np.array(db_DopplerRateCoeff0)

    # double db_coeff0(256);
    db_coeff0 = []
    for nodes in xmlfileslc.findall('.//processing/doppler/dopplerCentroid/dopplerEstimate/combinedDoppler/coefficient[@exponent="0"]'):
        db_coeff0.append(float(nodes.text))
    db_coeff0 = np.array(db_coeff0)

    # double db_coeff1(256);
    db_coeff1 = []
    for nodes in xmlfileslc.findall('.//processing/doppler/dopplerCentroid/dopplerEstimate/combinedDoppler/coefficient[@exponent="1"]'):
        db_coeff1.append(float(nodes.text))
    db_coeff1 = np.array(db_coeff1)

    # double db_validityRangeMin(256);
    db_validityRangeMin = []
    for nodes in xmlfileslc.findall('.//processing/doppler/dopplerCentroid/dopplerEstimate/combinedDoppler/validityRangeMin'):
        db_validityRangeMin.append(float(nodes.text))
    db_validityRangeMin = np.array(db_validityRangeMin)

    # double db_validityRangeMax(256);
    db_validityRangeMax = []
    for nodes in xmlfileslc.findall('.//processing/doppler/dopplerCentroid/dopplerEstimate/combinedDoppler/validityRangeMax'):
        db_validityRangeMax.append(float(nodes.text))
    db_validityRangeMax = np.array(db_validityRangeMax)

    # double db_referencePoint(256);
    db_referencePoint = []
    for nodes in xmlfileslc.findall('.//processing/doppler/dopplerCentroid/dopplerEstimate/combinedDoppler/referencePoint'):
        db_referencePoint.append(float(nodes.text))
    db_referencePoint = np.array(db_referencePoint)

    # double db_t_ra_firstPixel;
    db_t_ra_firstPixel = float(xmlfileslc.findall('.//productInfo/sceneInfo/rangeTime/firstPixel')[0].text)

    # double db_commonRSF;
    db_commonRSF = float(xmlfileslc.findall('.//productSpecific/complexImageInfo/commonRSF')[0].text)

    # Computation 
    FMrate = (db_DopplerRateCoeff0[0] + db_DopplerRateCoeff0[1]) / 2

    spotlightphase2 = np.empty([nb_lines, nb_pixels])

    i = 0

    usermessage.ezprint('Computation:',log,verbose)

    while i <= nb_pixels - 1:

        freq = [];#zeros(INTnumberOfDopplerRecords-1,1);
        tssc = [];#zeros(INTnumberOfDopplerRecords-1,1);
        xi =  [];#zeros(lines-1,1);
        yi = [];#zeros(lines-1,1);

        j1 = 0
        while j1 <= nb_lines - 1:
            xi.append(((db_stopTimeUTC - db_startTimeUTC) / nb_lines) * j1)
            j1 = j1 + 1 

        P_pixel = db_t_ra_firstPixel + (i - 1.0)/db_commonRSF
        freq = (db_coeff0 * (P_pixel - db_referencePoint)**0) + (db_coeff1 * (P_pixel - db_referencePoint)**1)
        tssc = (db_dCdEtimeUTC-(freq / FMrate)) - db_startTimeUTC

        x = tssc
        y = freq

        f = interpolate.interp1d(x, y, kind='linear')
        yi = f(xi) 

        spotlightphase2[:,i] = yi

        if np.fix(i/1000) == (i/(1000)):
            usermessage.ezprint('\tProgress %d pixels of %d' % (i+1,(nb_pixels)),log,verbose)

        i = i + 1
        
    # Save
    with open(outputfile, 'wb') as fi:
        spotlightphase2.astype(dtype=np.float32).tofile(fi)
    usermessage.ezprint('\tFile: %s' % (outputfile),log,verbose)
    usermessage.ezprint('\tdone.',log,verbose)
