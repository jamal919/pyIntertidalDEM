# -*- coding: utf-8 -*-
from .band_processor import BandData
from .HSV_processor import HSVData
from .binarymap_processor import Processor
import sys
import os
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
    

def make_watermap(directory,OUTDIR,prepdir,zone,nhue=0.4,nvalue=5.0,png=False):
    SavePNG=False
    if png:
        SavePNG=True
    BandDataObj=BandData(directory,OUTDIR,PNGFLAG=SavePNG)  #For getting directories
    
    MASKDIR=os.path.join(prepdir,'WaterMask','')
    if not os.path.exists(prepdir):
        print('Water Mask Directory Not Found!')
        sys.exit(1)

    MASKFILE=str(os.path.join(MASKDIR,str(zone)+'.tiff'))
    if not os.path.isfile(MASKFILE):
        print('Water Mask File  Not Found for zone:'+str(zone))
        sys.exit(1)

    BWINDATA=BandDataObj.TIFFSAVEDIR
    if png:
        PNGDIRBW=BandDataObj.PNGDIR_FINAL
        ProcessorOBJ=Processor(BWINDATA,MASKFILE,nhue,nvalue,PNGDIR=PNGDIRBW)
    else:
        ProcessorOBJ=Processor(BWINDATA,MASKFILE,nhue,nvalue)
    ProcessorOBJ.GetBinaryWaterMap()