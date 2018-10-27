# -*- coding: utf-8 -*-
from .rivermap import RiverLineGen
def create_rivermaps(wkdir,improcdir,preprocdir):
    
    RiverLineGenObj=RiverLineGen(wkdir,improcdir,preprocdir)
    RiverLineGenObj.CombineBinaryWaterMaps()
    