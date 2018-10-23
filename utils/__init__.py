# -*- coding: utf-8 -*-
from .information import Info
from .tiffreader import TiffReader
from .tiffwriter import TiffWriter
from .dataplotter import DataPlotter

import matplotlib.pyplot as plt
import numpy as np 


def infotest(directory):
    try:
        InfoOBJ=Info(directory)
        InfoOBJ.DisplayFileList()

        print(InfoOBJ.DateTime)
        print(InfoOBJ.directory)
        
    except:
        print('Information Test Failed')

def TiffReaderTest(FILE):
    try:
        TiffReaderObj=TiffReader()
        Data=TiffReaderObj.GetTiffData(FILE)
        plt.imshow(Data)
        plt.show()
        plt.clf()
        plt.close()
    except:
        print('Tiff Reading Test Failed')

def TiffWriterTest():
    Dfile='/media/ansary/PMAISONGDE/Data/T45QYE/SENTINEL2B_20180512-043429-820_L2A_T45QYE_D_V1-7/SENTINEL2B_20180512-043429-820_L2A_T45QYE_D_V1-7_FRE_B8.tif'
    OUT='/media/ansary/PMAISONGDE/EXXX/'

    try:
        TiffReaderObj=TiffReader()
        Data=TiffReaderObj.GetTiffData(Dfile)
        Data=Data.astype(np.float)
        Data[Data==-10000]=np.nan
        Data=(Data-np.nanmin(Data))/(np.nanmax(Data)-np.nanmin(Data))
        
        TiffWriterObj=TiffWriter()
        TiffWriterObj.SaveArrayToGeotiff(Data,'test',Dfile,OUT)
        
    
    
    except:
        print('Tiff Reading Test Failed')

def PlottingTest():
    Dfile='/media/ansary/PMAISONGDE/Data/T45QYE/SENTINEL2B_20180512-043429-820_L2A_T45QYE_D_V1-7/SENTINEL2B_20180512-043429-820_L2A_T45QYE_D_V1-7_FRE_B8.tif'
    
    OUT='/media/ansary/PMAISONGDE/EXXX/'

    try:
        TiffReaderObj=TiffReader()
        Data=TiffReaderObj.GetTiffData(Dfile)
        Data=Data.astype(np.float)
        Data[Data==-10000]=np.nan
        Data=(Data-np.nanmin(Data))/(np.nanmax(Data)-np.nanmin(Data))
        
        DataViewer=DataPlotter(Dfile,OUT)
        DataViewer.PlotWithGeoRef(Data,'test',PlotImdt=True)
    
    
    except:
        print('Data Plotting Test Failed')