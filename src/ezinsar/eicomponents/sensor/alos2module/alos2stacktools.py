#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to pre-process the ALOS-2 and ALOS SLC stack

The module allows to pre-process the ALOS-2 and ALOS SLC stack, directly for an `EIjob`
    
    (From `ezinsar` package)

Changelog:
        * 1.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
from typing import Optional, Union

from ezinsar.eicomponents.slcmodule import slcstacktools
from ezinsar import constants
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## Function to compute the coarse network
################################################################################
def commputecoarsenetworkSM(pathSLC,bbox,polarisation,
        DEM: Optional[Union[str,float,int]] = 500,
        figure: Optional[Union[None,str]] = None,
        preref: Optional[Union[None,str]] = None,
        verbose: Optional[bool] = True,  
        log: Optional[Union[str,None]] = None,  
        ):
        """Compute the potential best reference date for a ALOS2 (or ALOS) network, ONLY FOR SM.

        The function computes the the potential best reference date for a ALOS-2 (or ALOS) network, ONLY FOR SM.

        Args:
                pathSLC (str): Path of the SLC directory.
                bbox (any): Polygon vector of the bbox
                polarisation (str): Selected polarisation
                DEM (str): Fullpath of the DEM file [Default: None].
                figure (str): Figure file [Default: None]. If `None`, the figure will be displayed. 
                preref (str): Pre-selected reference date [Default: None],  in YYYYMMDD format. 
                verbose (bool, Optional): verbose [Default: `True`]. 
                log (str): logging [Default: `None`].

        Returns:
                best_ref (str): Best potential reference date
                dates (list): Dates of the SLCs
                Btempnorm (list): Float of the temporal baselines in days (normalised to the reference dates)
                Btempnorm (list): Float of the perpendicular baselines in metres (normalised to the reference dates)

        """
        dateref, dates, Btempnorm, Bperpnorm = slcstacktools.commputecoarsenetwork(pathSLC,bbox,polarisation,
                'ALOS2',
                DEM = DEM,
                figure = figure, 
                preref = preref,
                verbose = verbose,
                log = log,
                )

        return dateref, dates, Btempnorm, Bperpnorm