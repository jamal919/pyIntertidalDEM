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
        self.IAOData=self.TiffReader.GetTiffData(__InfoObj.IAO)

    def __ProcessValData(self):
        print('Getting Value Data')
        __File=self.__InputFolder+"/Value Data.tiff"
        __ValData=self.TiffReader.GetTiffData(__File)
        Water=__ValData*self.IAOData

        self.DataViewer.PlotWithGeoRef(Water,'Water val')
        
        #value channel constants
        
        __T_val=np.nanmedian(Water[Water>0])     #Median 
        __sig_val=np.nanstd(Water[Water>0])      #standard deviation
        
        __n_val=1
        self.DataViewer.DebugPrint(__n_val,'nval')
        self.DataViewer.DebugPrint(__T_val,'Tval')
        self.DataViewer.DebugPrint(__sig_val,'Sval')
        
        #Value channel conditional constant 
        __c1_val=__T_val+__n_val*__sig_val
        __c2_val=__T_val-__n_val*__sig_val
        self.DataViewer.DebugPrint(__c1_val,'c1hue')
        self.DataViewer.DebugPrint(__c2_val,'c2hue')
        
        
        self.__IsWater_val=np.empty(np.shape(__ValData))
        self.__IsWater_val[:]=0
        self.__IsWater_val[(__ValData<__c1_val) & (__ValData>__c2_val) ]=1
        self.DataViewer.PlotWithGeoRef(self.__IsWater_val,'self.__IsWater_val')
        self.TiffWritter.SaveArrayToGeotiff(self.__IsWater_val,'Water+problametic data')
    def __ProcessHUEData(self):
        print('Getting Hue Data')
        __File=self.__InputFolder+"/Hue Data.tiff"
        __HueData=self.TiffReader.GetTiffData(__File)
        Water=__HueData*(1-self.IAOData) 
        self.DataViewer.PlotWithGeoRef(Water,'Water hue')
        self.DataViewer.PlotWithGeoRef(__HueData,'pure hue')
        
        
        __T_hue=np.nanmedian(Water[Water>0])     #Median
        __sig_hue=np.nanstd(Water[Water>0])      #standard deviation
        
        __n_hue=1
        self.DataViewer.DebugPrint(__n_hue,'nhue')
        self.DataViewer.DebugPrint(__T_hue,'Thue')
        self.DataViewer.DebugPrint(__sig_hue,'Shue')
        
        #HUE channel conditional constant 
        __c1_hue=__T_hue+__sig_hue*__n_hue
        __c2_hue=__T_hue-__sig_hue*__n_hue
        
        self.DataViewer.DebugPrint(__c1_hue,'c1hue')
        self.DataViewer.DebugPrint(__c2_hue,'c2hue')
        
        
        self.__IsWater_hue=np.empty(np.shape(__HueData))
        self.__IsWater_hue[:]=1
        self.__IsWater_hue[(__HueData<__c1_hue) & (__HueData>__c2_hue) ]=0  ##Change in condition
        self.__IsWater_hue[__HueData==0]=1
        self.DataViewer.PlotWithGeoRef(self.__IsWater_hue,'self.__IsWater_hue')
        
    
        
    def GetIsWater(self):
        
        self.__ProcessValData()
        
        #self.__ProcessHUEData()
        '''
        IsWater=np.empty(np.shape(self.__IsWater_val))
        IsWater[:]=0
        IsWater[(self.__IsWater_hue==1) & (self.__IsWater_val==1)]=1
        self.DataViewer.PlotWithGeoRef(IsWater,'IsWater')
        self.TiffWritter.SaveArrayToGeotiff(IsWater,'Iswater')
        '''