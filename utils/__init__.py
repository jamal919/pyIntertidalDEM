# -*- coding: utf-8 -*-
from utils.dataplotter import DataPlotter
from utils.tiffreader import TiffReader
def mapPlotTest():
    Reader=TiffReader()
    
    RefTiff='/media/ansary/My Passport/OUTPUT/PreProcessed/WaterMask/T45QWE.tiff'
    OutDir='/media/ansary/My Passport/'
    data=Reader.GetTiffData(RefTiff)

    DataViewer=DataPlotter(RefTiff,OutDir)
    DataViewer.plotInMap(data)