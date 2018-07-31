#!/usr/bin/env python3

from Sentiniel2Info import displayInfo
from Sentiniel2Logger import Log,DebugLog
from Sentiniel2Preprocessor import Preprocessor
from Sentiniel2RGBProcessor import RGBProcessor
from Sentiniel2GeoData import GeoData
import matplotlib.pyplot as plt,numpy as np,argparse,time
from termcolor import colored
testCase1="/home/ansary/Sentiniel2/Data/20171130/SENTINEL2B_20171130-042157-149_L2A_T46QCK_D_V1-4"
testCase2="/home/ansary/Sentiniel2/Data/20180224/SENTINEL2B_20180224-045147-074_L2A_T45QYE_D/SENTINEL2B_20180224-045147-074_L2A_T45QYE_D_V1-5"  
directory=testCase1

def ModuleInfoSentiniel(directory):
    info=displayInfo(directory)
    info.Banner()
    return info.DisplayFileList()
'''
def GetDirectory():
    parser = argparse.ArgumentParser()
    parser.add_argument("unzipped_directory", help="Directory of unzipped Sentiniel2 product",type=str)
    args = parser.parse_args()
    return args.unzipped_directory
'''
def ModuleRun():
    start_time=time.time()

    Logger=Log(directory)            #Logger Object

    Files=ModuleInfoSentiniel(directory)
    
    preprocess=Preprocessor(Files,directory)      #Preprocessor Object

    RGBData=preprocess.GetRGBData()

    #Logger.SaveRGBAsImage('QKL_RGB',RGBData)

    ProcessRGB=RGBProcessor(RGBData,directory)    #RGBprocessor Object

    MapWater=ProcessRGB.GetWaterMap()

    NoData=Logger.GetNoDataCorrection()

    MapWater[NoData==1]=0

    #Logger.DebugPlot(MapWater,'MapWater')

    #Logger.SaveArrayToGeotiff(MapWater,'WaterMap')
    
    GeoObj=GeoData(directory,MapWater)
    
    LatLon=GeoObj.GetShoreLineGeoData()
    
    #Logger.DebugPrint(LatLon,'Latitude Longitude')

    #Identifier='ShoreLine_LatLon'
    
    #Logger.SaveDataAsCSV(Identifier,LatLon)
    
    #Logger.SaveDataAsKML(Identifier,LatLon)
    
    #Logger.SaveDataAsSHPPoint(Identifier,LatLon)

    print(colored("Total Elapsed Time: %s seconds " % (time.time() - start_time),'green'))

    plt.show()
    
def DebugRun():
    Logger=Log(directory)
    
    DebugLogger=DebugLog(directory) 
    
    DataFile=Logger.OutputDir+'WaterMap.tiff'
    
    Data=DebugLogger.GetFileData(DataFile)

    GeoObj=GeoData(directory,Data)
    
    LatLon=GeoObj.GetShoreLineGeoData()
    
    Logger.DebugPrint(LatLon,'Latitude Longitude')

    Identifier='ShoreLine_LatLon'
    
    #Logger.SaveDataAsCSV(Identifier,LatLon)
    
    Logger.SaveDataAsKML(Identifier,LatLon)
    
    #Logger.SaveDataAsSHPPoint(Identifier,LatLon)
    


if __name__=='__main__':
    DebugRun()    
   