# -*- coding: utf-8 -*-
from .tide import Analyzer
import os
from glob import glob
def compute_waterlavels(dem_data_dir,vertrefdir):
    #dem_data_dir=os.path.join(dem_data_dir,'Chandpur')
    print('Saving constituents:',str(dem_data_dir))
    files=glob(os.path.join(dem_data_dir, '*'))
    for dfile in files: 
        AnalyzerObj=Analyzer(dfile,vertrefdir)
        AnalyzerObj.analyze()    

# file creation with station name---       time lat_lon station