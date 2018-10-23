# -*- coding: utf-8 -*-
from .band_processor import BandData
from .HSV_processor import HSVData

def construct_channels(directory,OUTDIR,png=False):
    SavePNG=False
    if png:
        SavePNG=True

    BandDataObj=BandData(directory,OUTDIR,PNGFLAG=SavePNG)
    BandDataObj.Data()
    
    HSVIN=BandDataObj.TIFFSAVEDIR
    if png:
        PNGDIRHSV=BandDataObj.PNGDIR_FINAL
        HSVDataObj=HSVData(HSVIN,PNGdir=PNGDIRHSV)
    else:
        HSVDataObj=HSVData(HSVIN)
    HSVDataObj.HueValueRGB()