#!/usr/bin/env python3

from Sentiniel2Info import displayInfo
from Sentiniel2Logger import Log,DebugLog
from Sentiniel2Preprocessor import Preprocessor
from Sentiniel2RGBProcessor import RGBProcessor
from Sentiniel2DataFilter import DataFilter
from Sentiniel2GeoData import GeoData
import matplotlib.pyplot as plt,numpy as np,argparse,time
from termcolor import colored
import os

testCase1="/home/ansary/Sentiniel2/Data/20171130/SENTINEL2B_20171130-042157-149_L2A_T46QCK_D_V1-4"
testCase2="/home/ansary/Sentiniel2/Data/20180224/SENTINEL2B_20180224-045147-074_L2A_T45QYE_D/SENTINEL2B_20180224-045147-074_L2A_T45QYE_D_V1-5"  
directory=testCase1


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
    
    Filter=DataFilter(directory,IsWater)

    WaterMap=Filter.FilterWaterMap()

    Logger.DebugPlot(WaterMap,'WaterMap')

    Geo=GeoData(directory,WaterMap)
    
    LatLon=Geo.GetShoreLineGeoData()
    
    #Logger.DebugPrint(LatLon,'Lat Lon')

    #Identifier='ShoreLine_LatLon'
    
    #Logger.SaveDataAsKML(Identifier,LatLon)
    
    print(colored("Total Elapsed Time: %s seconds " % (time.time() - start_time),'green'))

    plt.show()
    
if __name__=='__main__':
    ModuleRun(directory)