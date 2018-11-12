# -*- coding: utf-8 -*-
from __future__ import print_function

from .rivermap import RiverLineGen
def create_rivermaps(wkdir,improcdir,preprocdir):
    
    RiverLineGenObj=RiverLineGen(wkdir,improcdir,preprocdir)
    RiverLineGenObj.CombineBinaryWaterMaps()
    