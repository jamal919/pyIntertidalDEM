import time,matplotlib,numpy as np,gc,sys
from osgeo import gdal
from Sentiniel2Logger import TiffReader,TiffWritter

class Processor(object):
    
    def __init__(self,Directory):
        self.Directory=Directory
        self.TiffReader=TiffReader(Directory)
        self.TiffWritter=TiffWritter(Directory)

    def __ProcessHUEData(self):
        print('Getting Hue Data')
        __File=str(self.Directory)+"/Hue Data.tiff"
        __HueData=self.TiffReader.GetTiffData(__File)
        __HueData=__HueData/np.amax(__HueData)
        #self.Logger.DebugPlot(__HueData,'Hue Data')
        #hue channel constants
        __n_hue=1                      #scaling factor
        idx=__HueData>0
        __T_hue=np.median(__HueData[idx])     #Median
        #self.Logger.DebugPrint(__T_hue,'Median Hue')
        __sig_hue=np.std(__HueData[idx])      #standard deviation
        #self.Logger.DebugPrint(__sig_hue,'Standard Deviation Hue')
        
        #HUE channel conditional constant 
        __c1_hue=__T_hue+__n_hue*__sig_hue
        #self.Logger.DebugPrint(__c1_hue,'Conditional Constant 1 Hue')
        __c2_hue=__T_hue-__n_hue*__sig_hue
        #self.Logger.DebugPrint(__c2_hue,'Conditional Constant 2 Hue')

        self.__IsWater_hue=np.empty(np.shape(__HueData))
        self.__IsWater_hue[:]=0                              
        self.__IsWater_hue[(__HueData>__c1_hue) | (__HueData<__c2_hue)]=1  ##Change in condition
        
    def __ProcessValData(self):
        print('Getting Value Data')
        __File=str(self.Directory)+"/Value Data.tiff"
        __ValData=self.TiffReader.GetTiffData(__File)
        __ValData=__ValData/np.amax(__ValData)
        #self.Logger.DebugPlot(__ValData,'Val Data')
        #value channel constants
        __n_val=1                           #scaling factor(question)
        idx=__ValData<1
        __T_val=np.median(__ValData[idx])     #Median 
        #self.Logger.DebugPrint(__T_val,'Median Val')
        __sig_val=np.std(__ValData[idx])      #standard deviation
        #self.Logger.DebugPrint(__sig_val,'Standard Deviation Val')
        #Value channel conditional constant 
        __c1_val=__T_val+__n_val*__sig_val
        #self.Logger.DebugPrint(__c1_val,'Conditional Constant 1 Val')
        __c2_val=__T_val-__n_val*__sig_val
        #self.Logger.DebugPrint(__c2_val,'Conditional Constant 2 Val')

        self.__IsWater_val=np.empty(np.shape(__ValData))
        self.__IsWater_val[:]=1                              
        self.__IsWater_val[(__ValData<__c1_val) & (__ValData>__c2_val)]=0
        
    def GetIsWater(self):
        self.__ProcessHUEData()
        self.__ProcessValData()
        IsWater=np.empty(np.shape(self.__IsWater_val))
        IsWater[:]=0
        IsWater[(self.__IsWater_hue==1) & (self.__IsWater_val==1)]=1
        #self.Logger.DebugPlot(IsWater,'Water')
        #self.TiffWritter.SaveArrayToGeotiff(IsWater,'Iswater_1_1')