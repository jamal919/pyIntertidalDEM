# -*- coding: utf-8 -*-
from .tide import Analyzer
import os

def save_constituents(dem_data_dir,dem_output_dir):
    dem_data_dir=os.path.join(dem_data_dir,'Chandpur')
    print('Saving constituents:',str(dem_data_dir))
    AnalyzerObj=Analyzer(dem_data_dir)
    AnalyzerObj.analyze()    