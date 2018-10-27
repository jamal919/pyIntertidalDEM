# -*- coding: utf-8 -*-
from __future__ import print_function
from utide import solve
import numpy as np

# Time series input
# Harmonic analysis using utide.solve
# Save the amplitude and phase for the constituents
# CSV or netCDF

class Reader(object):
    def __init__(self, filepath):
        self.filepath = filepath

    def read_schism(self):
        pass

    def read_refmar(self):
        pass

class TimeSeries(object):
    def __init__(self):
        self.time = None
        self.elev = None
        self.lon = None

    def load(self, file, reader):
        self.time, self.elev, self.lon = reader.read_refmar(file)

class Analyzer(object):
    def __init__(self, ts, lat):
        self.ts = ts

    def analyze(self):
        self.ha = solve(self.ts.time, self.ts.elev, self.ts.lat)

class Predictor(object):
    def __init__(self):
        pass

    def listStation(self):
        # Listing available stations where the constituents were calculated
        pass

    def findClosest(self):
        # Find closest station correspods to a given lat long
        pass

    def calcWL(self):
        # Load closest station constituent values
        # calculate WL for a given time
        # return WL
        pass
    