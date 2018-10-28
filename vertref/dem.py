# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np



class Predictor(object):
    def __init__(self,dem_input_dir):
        self.__indir=dem_input_dir

    def listStation(self):
        pass

    def findClosest(self):
        # Find closest station correspods to a given lat long
        pass

    def calcWL(self):
        # Load closest station constituent values
        # calculate WL for a given time
        # return WL
        pass
class Dem(object):
    def __init__(self):
        pass

    def setVertRef(self):
        pass