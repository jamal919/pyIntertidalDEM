import time,matplotlib,numpy as np,gc,sys
from osgeo import gdal
from Sentiniel2Logger import Log
from Sentiniel2TiffData import TiffReader,TiffWritter

class Processor(object):
    
    def __init__(self,Directory):
        self.Logger=Log(Directory)
        self.Directory=Directory
        self.TiffReader=TiffReader(Directory)
        self.TiffWritter=TiffWritter(Directory)

    def __ProcessHUEData(self):
        print('Getting Hue Data')
        __File=str(self.Directory)+"/Hue Data.tiff"
        __HueData=self.TiffReader.GetTiffData(__File)
        __HueData=__HueData/np.amax(__HueData)
        #hue channel constants
        __n_hue=1                      #scaling factor
        idx=__HueData>0
        __T_hue=np.median(__HueData[idx])     #Median
        self.Logger.DebugPrint(__T_hue,'Median Hue')
        __sig_hue=np.std(__HueData[idx])      #standard deviation
        self.Logger.DebugPrint(__sig_hue,'Standard Deviation Hue')
        
        #HUE channel conditional constant 
        __c1_hue=__T_hue+__n_hue*__sig_hue
        self.Logger.DebugPrint(__c1_hue,'Conditional Constant 1 Hue')
        __c2_hue=__T_hue-__n_hue*__sig_hue
        self.Logger.DebugPrint(__c2_hue,'Conditional Constant 2 Hue')

        __IsWater_hue=np.empty(np.shape(__HueData))
        __IsWater_hue[:]=0                              
        __IsWater_hue[(__HueData>__c1_hue) | (__HueData<__c2_hue)]=1  ##Change in condition
        self.TiffWritter.SaveArrayToGeotiff(__IsWater_hue,'IsWaterHue')

    def __ProcessValData(self):
        print('Getting Value Data')
        __File=str(self.Directory)+"/Value Data.tiff"
        __ValData=self.TiffReader.GetTiffData(__File)
        __ValData=__ValData/np.amax(__ValData)
        #value channel constants
        __n_val=1                           #scaling factor(question)
        idx=__ValData<1
        __T_val=np.median(__ValData[idx])     #Median 
        self.Logger.DebugPrint(__T_val,'Median Val')
        __sig_val=np.std(__ValData[idx])      #standard deviation
        self.Logger.DebugPrint(__sig_val,'Standard Deviation Val')
        #Value channel conditional constant 
        __c1_val=__T_val+__n_val*__sig_val
        self.Logger.DebugPrint(__c1_val,'Conditional Constant 1 Val')
        __c2_val=__T_val-__n_val*__sig_val
        self.Logger.DebugPrint(__c2_val,'Conditional Constant 2 Val')

        __IsWater_val=np.empty(np.shape(__ValData))
        __IsWater_val[:]=1                              
        __IsWater_val[(__ValData<__c1_val) & (__ValData>__c2_val)]=0  
        self.TiffWritter.SaveArrayToGeotiff(__IsWater_val,'IsWaterVal')
        
    def GetIsWater(self):
        self.__ProcessHUEData()
        self.__ProcessValData()
        