#!/usr/bin/env python3

from Sentiniel2Info import displayInfo
from Sentiniel2ChannelData import BandData
from Sentiniel2HSVData import HSVData
from Sentiniel2Processor import Processor
from Sentiniel2Logger import Log
import matplotlib.pyplot as plt,numpy as np,argparse,time
import os,psutil

parser = argparse.ArgumentParser()
parser.add_argument("Dir", help="Directory of HUE and Value Data",type=str)
args = parser.parse_args()
directory=args.Dir

def SaveRGB(directory):
    Info=displayInfo(directory)
    Files=Info.DisplayFileList()
    BandDataObj=BandData(Files,directory)
    BandDataObj.Data()

def SaveHUEVALUE(directory):
    HSVDataObj=HSVData(directory)
    HSVDataObj.HueValueRGB()

def SaveIsWater(directory):
    ProcessorObj=Processor(directory)
    ProcessorObj.GetIsWater()

def SaveWaterMap(directory):
    pass

def ModuleRun(directory):
    start_time=time.time()

    #SaveRGB(directory)
    #SaveHUEVALUE(directory)
    #SaveIsWater(directory)

    print("Total Elapsed Time: %s seconds " % (time.time() - start_time))
    
    pid = os.getpid()
    
    py = psutil.Process(pid)
    
    memoryUse = py.memory_info()[0]/(2**30)  # memory use in GB

    print('memory use:', memoryUse)
    
    plt.show()
    
if __name__=='__main__':
    ModuleRun(directory)