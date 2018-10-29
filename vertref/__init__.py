# -*- coding: utf-8 -*-
from __future__ import print_function
from .dem import Dem
import os
from glob import glob
def set_water_levels(wkdir,waterleveldir,vertrefdir):
        DemObj=Dem(wkdir,waterleveldir,vertrefdir)
        DemObj.setVertRef()
