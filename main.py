#!/usr/bin/env python3
from Sentiniel2ChannelData import BandData
from Sentiniel2HSVData import HSVData
from Sentiniel2Processor import Processor
from Sentiniel2DataFilter import DataFilter
from Sentiniel2GeoData import GeoData
import matplotlib.pyplot as plt,numpy as np,argparse,time
import os,psutil,sys,gc    

parser = argparse.ArgumentParser()
parser.add_argument("Dir", help="Directory of HUE and Value Data",type=str)
args = parser.parse_args()
directory=args.Dir

def SaveRGB(directory):
    BandDataObj=BandData(directory)
    BandDataObj.Data()

def SaveHUEVALUE(directory):
    HSVDataObj=HSVData(directory)
    HSVDataObj.HueValueRGB()

def SaveIsWater(directory):
    ProcessorObj=Processor(directory)
    ProcessorObj.GetIsWater()

def SaveWaterMap(directory):
    DataFilterObj=DataFilter(directory)
    DataFilterObj.FilterWaterMap()

def SaveLatLon(directory):
    GeoDataObj=GeoData(directory)
    GeoDataObj.ShoreLine()
    
def ModuleRun(directory):
    start_time=time.time()

    
    SaveRGB(directory)
    SaveHUEVALUE(directory)
    SaveIsWater(directory)
    #SaveWaterMap(directory)
    #SaveLatLon(directory)
    print("Total Elapsed Time: %s seconds " % (time.time() - start_time))
    
    pid = os.getpid()
    
    py = psutil.Process(pid)
    
    memoryUse = py.memory_info()[0]/(2**30)  # memory use in GB

    print('memory use(in GB):', memoryUse)
    
    #plt.show()
    
if __name__=='__main__':
    if sys.version_info[1] < 3.6:
        raise Exception("Must be using Python 3")
    else:
        ModuleRun(directory)
        '''
        DataPath='/home/ansary/Sentiniel2/Data/'
        DataFolders=os.listdir(path=DataPath)
        for df in DataFolders:
            directory=DataPath+df+'/'
            ModuleRun(directory)
            gc.collect()
        '''