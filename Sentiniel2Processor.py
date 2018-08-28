import time,matplotlib,numpy as np,gc,sys
from osgeo import gdal
from Sentiniel2Logger import TiffReader,TiffWritter,ViewData,Info

class Processor(object):
    
    def __init__(self,Directory):
        __InfoObj=Info(Directory)
        self.__InputFolder=__InfoObj.OutputDir()
        self.DataViewer=ViewData(Directory)
        self.Directory=Directory
        self.TiffReader=TiffReader(Directory)
        self.TiffWritter=TiffWritter(Directory)

    def __ProcessHUEData(self):
        print('Getting Hue Data')
        __File=self.__InputFolder+"/Hue Data.tiff"
        __HueData=self.TiffReader.GetTiffData(__File)
        __HueData=__HueData/np.amax(__HueData)
        
        #hue channel constants
        __n_hue=1                      #scaling factor
        idx=__HueData>0
        __T_hue=np.median(__HueData[idx])     #Median
        __sig_hue=np.std(__HueData[idx])      #standard deviation
        
        #HUE channel conditional constant 
        __c1_hue=__T_hue+__n_hue*__sig_hue
        __c2_hue=__T_hue-__n_hue*__sig_hue
        
        self.__IsWater_hue=np.empty(np.shape(__HueData))
        self.__IsWater_hue[:]=0                              
        self.__IsWater_hue[(__HueData>__c1_hue) | (__HueData<__c2_hue)]=1  ##Change in condition
        #self.DataViewer.DebugPlot(self.__IsWater_hue,'self.__IsWater_hue')

    def __ProcessValData(self):
        print('Getting Value Data')
        __File=self.__InputFolder+"/Value Data.tiff"
        __ValData=self.TiffReader.GetTiffData(__File)
        __ValData=__ValData/np.amax(__ValData)
        #value channel constants
        __n_val=1                           #scaling factor(question)
        idx=__ValData<1
        __T_val=np.median(__ValData[idx])     #Median 
        __sig_val=np.std(__ValData[idx])      #standard deviation
        #Value channel conditional constant 
        __c1_val=__T_val+__n_val*__sig_val
        __c2_val=__T_val-__n_val*__sig_val
        
        self.__IsWater_val=np.empty(np.shape(__ValData))
        self.__IsWater_val[:]=1                              
        self.__IsWater_val[(__ValData<__c1_val) & (__ValData>__c2_val)]=0
        #self.DataViewer.DebugPlot(self.__IsWater_val,'self.__IsWater_val')

    def GetIsWater(self):
        self.__ProcessHUEData()
        self.__ProcessValData()
        IsWater=np.empty(np.shape(self.__IsWater_val))
        IsWater[:]=0
        IsWater[(self.__IsWater_hue==1) & (self.__IsWater_val==1)]=1
        self.DataViewer.PlotWithGeoRef(IsWater,'IsWater')
        self.TiffWritter.SaveArrayToGeotiff(IsWater,'Iswater')