#!/usr/bin/env python3

from Sentiniel2Info import displayInfo
from Sentiniel2Logger import Log,DebugLog
from Sentiniel2Preprocessor import Preprocessor
from Sentiniel2RGBProcessor import RGBProcessor
from Sentiniel2GeoData import GeoData
import matplotlib.pyplot as plt,numpy as np



##globals
testCase1="/home/ansary/Sentiniel2/Data/20171130/SENTINEL2B_20171130-042157-149_L2A_T46QCK_D_V1-4"
    
directory=testCase1

def ModuleInfoSentiniel(directory):
    info=displayInfo(directory)
    info.Banner()
    return info.DisplayFileList()




def ModuleRun():

    Logger=Log(directory)            #Logger Object

    Files=ModuleInfoSentiniel(directory)
    '''
    preprocess=Preprocessor(Files,directory)      #Preprocessor Object

    RGBData=preprocess.GetRGBData()

    ProcessRGB=RGBProcessor(RGBData,directory)    #RGBprocessor Object

    MapWater=ProcessRGB.GetWaterMap()

    Logger.DebugPlot(MapWater,'MapWater')

    Logger.SaveArrayToGeotiff(MapWater,'WaterMap')
    
    plt.show()
    '''
def DebugRun():
    Logger=Log(directory)
    
    DebugLogger=DebugLog(directory) 
    
    DataFile=Logger.OutputDir+'WaterMap.tiff'
    
    Data=DebugLogger.GetFileData(DataFile)
    
    GeoObj=GeoData(directory,Data)
    
    LatLon=GeoObj.GetShoreLineGeoData()
    
    Identifier='ShoreLine_LatLon'
    
    Logger.SaveDataAsCSV(Identifier,LatLon)
    Logger.SaveDataAsKML(Identifier,LatLon)
    Logger.SaveDataAsSHPPoint(Identifier,LatLon)
    


if __name__=='__main__':
    DebugRun()    
   