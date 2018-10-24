# -*- coding: utf-8 -*-
from .band_processor import BandData
from .HSV_processor import HSVData
from .binarymap_processor import Processor
from .filter import DataFilter
import sys
import os
def construct_channels(directory,improcdir,preprocdir,png=False):
    try:
        BandDataObj=BandData(directory,improcdir,preprocdir,png=png)
        HSVDataObj=HSVData(directory,improcdir,preprocdir,png=png)
        BandDataObj.Data()
        HSVDataObj.HueValueRGB()
    except:
        print('Channel Construction Failed!')    

def make_watermap(directory,improcdir,preprocdir,nhue=0.4,nvalue=5.0,png=False):
    try:
        ProcessorObj=Processor(directory,improcdir,preprocdir,nhue,nvalue,png=png)
        ProcessorObj.GetBinaryWaterMap()
    except:
        print('WaterMap creation Failed')

def remove_blob(directory,improcdir,preprocdir,nwater=50000,nland=10000,png=True):
    try:
        DataFilterObj=DataFilter(directory,improcdir,preprocdir,nwater=50000,nland=10000,png=True)
        DataFilterObj.FilterWaterMap()
    except:
        print('Filtering Failed')
    