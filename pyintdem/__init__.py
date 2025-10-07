#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""pyIntertidalDEM Processing toolbox

pyIntertidalDEM is a set of libraries and procedures written in python to extract 
shorelines from spectral images using  a sophisticated shoreline extraction algorithm.
These modules are developed in Python v3 environment.
"""
from pathlib import Path
from pyintdem.core import Band

__version__ = '1.8'


def read_file(fn, band=1) -> Band:
    """
    Read a tif file and return a Band object
    Args:
        fn: path to tiff file
        band: the band number to read

    Returns: Band object

    """
    fn = Path(fn).as_posix()
    da_band = Band()
    da_band.read(fname=fn, band=band)
    return da_band
