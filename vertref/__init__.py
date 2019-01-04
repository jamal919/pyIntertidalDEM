# -*- coding: utf-8 -*-
from __future__ import print_function
from .dem import Dem
import os
from glob import glob

def set_water_levels(shorelinedir, waterleveldir, vertrefdir):
        DemObj = Dem(shorelinedir, waterleveldir, vertrefdir)
        DemObj.setVertRef()
