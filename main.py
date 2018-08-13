#!/usr/bin/env python3

from Sentiniel2Info import displayInfo
from Sentiniel2Logger import Log,DebugLog
from Sentiniel2Preprocessor import Preprocessor
from Sentiniel2RGBProcessor import RGBProcessor
from Sentiniel2DataFilter import DataFilter
import matplotlib.pyplot as plt,numpy as np,argparse,time
from termcolor import colored
import os

testCase1="/home/ansary/Sentiniel2/Data/20171130/SENTINEL2B_20171130-042157-149_L2A_T46QCK_D_V1-4"
testCase2="/home/ansary/Sentiniel2/Data/20180224/SENTINEL2B_20180224-045147-074_L2A_T45QYE_D/SENTINEL2B_20180224-045147-074_L2A_T45QYE_D_V1-5"  
directory=testCase2


def ModuleRun(directory):
    start_time=time.time()

    Logger=Log(directory)            #Logger Object

    InfoObj=displayInfo(directory)   #Info

    Files=InfoObj.DisplayFileList()
    
    preprocess=Preprocessor(Files,directory)      #Preprocessor Object

    RGBData=preprocess.GetRGBData()

    Logger.DebugPlot(RGBData,'QKL_RGB')
    
    ProcessRGB=RGBProcessor(RGBData,directory)    #RGBprocessor Object

    IsWater=ProcessRGB.GetWaterMap()

    NoData=Logger.GetNoDataCorrection()

    IsWater[NoData==1]=0
    
    Logger.SaveArrayToGeotiff(IsWater,'IsWater')
    
    #Filter=DataFilter(directory,IsWater)           #Data tester object

    #WaterMap=Filter.FilterWaterMap(5000)

    #GeoObj=GeoData(directory,MapWater)
    
    #LatLon=GeoObj.GetShoreLineGeoData()
    
    #Logger.DebugPrint(LatLon,'Lat Lon')

    #Identifier='ShoreLine_LatLon'
    
    #Logger.SaveDataAsKML(Identifier,LatLon)
    
    print(colored("Total Elapsed Time: %s seconds " % (time.time() - start_time),'green'))

    plt.show()
    
def DebugRun(directory):
    Logger=Log(directory)
    
    DebugLogger=DebugLog(directory) 
    
    DataFile=Logger.OutputDir+'IsWater.tiff'
    
    IsWater=DebugLogger.GetFileData(DataFile)

    Filter=DataFilter(directory,IsWater)

    WaterMap=Filter.FilterWaterMap()

    Logger.DebugPlot(WaterMap,'WaterMap')

    plt.show()
    
    
if __name__=='__main__':
    DebugRun(directory)