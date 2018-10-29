# -*- coding: utf-8 -*-
from .dem import Dem
import os
from glob import glob
def set_water_levels(wkdir,waterleveldir,vertrefdir):
        DemObj=Dem(wkdir,waterleveldir,vertrefdir)
        DemObj.setVertRef()
# file creation with station name---       time lat_lon station