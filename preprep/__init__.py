# -*- coding: utf-8 -*-
from __future__ import print_function
from .extractor import DataExtractor
from .watermask_generator import WaterMaskCreator 

import os 
def ingest(indatadir, wkdir):
    try:
        extobj = DataExtractor(indatadir, wkdir)
        extobj.StartExtracting()
    except:
        print('Extraction failed!')

def genmask(wkdir,prepdir,dir=None,nstd=0.5,water=10000,land=5000,png=False):
    try:
        OutDir=os.path.join(prepdir,'WaterMask','')
        if not os.path.exists(OutDir):
                os.mkdir(OutDir)
        if dir:
            OutDir=os.path.join(OutDir, str(dir),'')
            if not os.path.exists(OutDir):
                os.mkdir(OutDir)
        if png:
            PNGdir=os.path.join(OutDir,'QucikLookPNGs','')
            if not os.path.exists(PNGdir):
                os.mkdir(PNGdir)
            WaterMaskCreatorObj=WaterMaskCreator(wkdir,OutDir,nstd,water,land,PNGDir=PNGdir)
        else:
            WaterMaskCreatorObj=WaterMaskCreator(wkdir,OutDir,nstd,water,land)

        WaterMaskCreatorObj.CreateWaterMask()
    except:
        print('WaterMask Generation Failed')