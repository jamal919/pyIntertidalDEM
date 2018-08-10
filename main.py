#!/usr/bin/env python3

from Sentiniel2Info import displayInfo
from Sentiniel2Logger import Log,DebugLog
from Sentiniel2Preprocessor import Preprocessor
from Sentiniel2RGBProcessor import RGBProcessor
from Sentiniel2GeoData import GeoData
from Sentiniel2DataTesting import DataTester
from Sentiniel2GeoMask import MaskClass


import matplotlib.pyplot as plt,numpy as np,argparse,time
from termcolor import colored
import os

testCase1="/home/ansary/Sentiniel2/Data/20171130/SENTINEL2B_20171130-042157-149_L2A_T46QCK_D_V1-4"
testCase2="/home/ansary/Sentiniel2/Data/20180224/SENTINEL2B_20180224-045147-074_L2A_T45QYE_D/SENTINEL2B_20180224-045147-074_L2A_T45QYE_D_V1-5"  
#testFolder="/home/ansary/Sentiniel2/Data/20180412/"

directory=testCase2

'''
parser = argparse.ArgumentParser()
parser.add_argument("unzipped_directory", help="Directory of unzipped Sentiniel2 product",type=str)
args = parser.parse_args()
'''

def ModuleInfoSentiniel(directory):
    info=displayInfo(directory)
    info.Banner()
    return info.DisplayFileList()


def ModuleRun(directory):
    start_time=time.time()

    Logger=Log(directory)            #Logger Object

    Files=ModuleInfoSentiniel(directory)
    
    preprocess=Preprocessor(Files,directory)      #Preprocessor Object

    RGBData=preprocess.GetRGBData()

    Logger.DebugPlot(RGBData,'QKL_RGB')

    ProcessRGB=RGBProcessor(RGBData,directory)    #RGBprocessor Object

    MapWater=ProcessRGB.GetWaterMap()

    NoData=Logger.GetNoDataCorrection()

    MapWater[NoData==1]=0

    Logger.DebugPlot(MapWater,'MapWater')

    #Test=DataTester(directory,MapWater)           #Data tester object

    #Test.SegmentationWaterMap()

    #Logger.SaveArrayToGeotiff(MapWater,'WaterMap')
    
    #GeoObj=GeoData(directory,MapWater)
    
    #LatLon=GeoObj.GetShoreLineGeoData()
    
    #Logger.DebugPrint(LatLon,'Lat Lon')

    #Identifier='ShoreLine_LatLon'
    
    #Logger.SaveDataAsCSV(Identifier,LatLon)
    
    #Logger.SaveDataAsKML(Identifier,LatLon)
    
    #Logger.SaveDataAsSHPPoint(Identifier,LatLon)
    
    print(colored("Total Elapsed Time: %s seconds " % (time.time() - start_time),'green'))

    plt.show()
    
def DebugRun(directory):
    Logger=Log(directory)
    
    MaskOBJ=MaskClass(directory)

    Logger.DebugPlot(MaskOBJ.ApplyMask(7),'Mask')

    #DebugLogger=DebugLog(directory) 
    
    #DataFile=Logger.OutputDir+'WaterMap.tiff'
    
    #Data=DebugLogger.GetFileData(DataFile)

    #Test=DataTester(directory,Data)

    #Test.SegmentationWaterMap()

    plt.show()
    
    #Logger.SaveArrayToGeotiff(Data,'Hole Filled Map')

    #GeoObj=GeoData(directory,Data)
    
    #LatLon=GeoObj.GetShoreLineGeoData()
    
    #Logger.DebugPrint(LatLon,'Latitude Longitude')

    #Identifier='ShoreLine_LatLon'
    
    #Logger.SaveDataAsCSV(Identifier,LatLon)
    
    #Logger.SaveDataAsKML(Identifier,LatLon)
    
    #Logger.SaveDataAsSHPPoint(Identifier,LatLon)
    


if __name__=='__main__':
    '''
    Dirs=os.listdir(path=testFolder)
    Dirs.remove('20180412.meta4')
    for d in Dirs:
        directory=testFolder+d
        #print(directory)
        ModuleRun(directory) 
    '''
    DebugRun(directory)