#!/usr/bin/env python3

from Sentiniel2Info import displayInfo
from Sentiniel2Logger import Log,DebugLog
from Sentiniel2Processor import Processor
from Sentiniel2DataFilter import DataFilter
from Sentiniel2GeoData import GeoData
import matplotlib.pyplot as plt,numpy as np,argparse,time
import os

parser = argparse.ArgumentParser()
parser.add_argument("Dir", help="Directory of HUE and Value Data",type=str)
args = parser.parse_args()
directory=args.Dir


def ModuleRun(directory):
    start_time=time.time()

    Logger=Log(directory)            #Logger Object

    ProcessorOBJ=Processor(directory)

    IsWater=ProcessorOBJ.GetWaterMap()

    #NoData=Logger.GetNoDataCorrection()

    #IsWater[NoData==1]=0
    
    Logger.DebugPlot(IsWater,'Iswater')
    #Filter=DataFilter(directory,IsWater)

    #WaterMap=Filter.FilterWaterMap()

    #Logger.DebugPlot(WaterMap,'WaterMap')

    #Geo=GeoData(directory,WaterMap)
    
    #LatLon=Geo.GetShoreLineGeoData()
    
    #Logger.DebugPrint(LatLon,'Lat Lon')

    #Identifier='ShoreLine_LatLon'
    
    #Logger.SaveDataAsKML(Identifier,LatLon)
    
    print("Total Elapsed Time: %s seconds " % (time.time() - start_time))

    plt.show()
    
if __name__=='__main__':
    ModuleRun(directory)