# -*- coding: utf-8 -*-
from .band_processor import BandData
 
def construct_channels(directory,improcdir, tiff=True, png=True):
    
    BandDataObj=BandData(directory,improcdir)
