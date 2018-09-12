import time,matplotlib,numpy as np,gc,sys
from osgeo import gdal
from Sentiniel2Logger import TiffReader,TiffWritter,ViewData,Info
class Processor(object):
    
    def __init__(self,Directory):
        __InfoObj=Info(Directory)
        self.__InputFolder=__InfoObj.OutputDir('TIFF')
        self.DataViewer=ViewData(Directory)
        self.Directory=Directory
        self.TiffReader=TiffReader(Directory)
        self.TiffWritter=TiffWritter(Directory)
       
    def __SaveChannelData(self,Data,Identifier):
        self.DataViewer.PlotWithGeoRef(Data,str(Identifier))
        self.TiffWritter.SaveArrayToGeotiff(Data,str(Identifier))


    def __LoadHueValue(self):
        
        print('Getting Value Data')
        __File=self.__InputFolder+"/2.2.2 Value Normalized Pekel.tiff"
        self.__ValData=self.TiffReader.GetTiffData(__File)
        
        print('Getting Hue Data')
        __File=self.__InputFolder+"/2.2.1_HUE_Normalized_Pekel.tiff"
        self.__HueData=self.TiffReader.GetTiffData(__File)
        

    def __ProcessValData(self):
        print('Processing Value Channel')

        __T_val=np.nanmedian(self.__ValData)     #Median 
        __sig_val=np.nanstd(self.__ValData)      #standard deviation
        __n_val=0.5

        self.DataViewer.DebugPrint(__n_val,'nval')
        self.DataViewer.DebugPrint(__T_val,'Tval')
        self.DataViewer.DebugPrint(__sig_val,'Sval')
        
        #Value channel conditional constant 
        __c1_val=__T_val+__n_val*__sig_val
        __c2_val=__T_val-__n_val*__sig_val
        self.DataViewer.DebugPrint(__c1_val,'c1hue')
        self.DataViewer.DebugPrint(__c2_val,'c2hue')
        
        
        self.__IsWater_val=np.empty(np.shape(self.__ValData))
        self.__IsWater_val[:]=0
        self.__IsWater_val[(self.__ValData<__c1_val) & (self.__ValData>__c2_val) ]=1
        
        #3.1.1_Is_Water_Val_SF-'+str(__n_val)
        self.__SaveChannelData(self.__IsWater_val,'3.1.1_Is_Water_Val_SF-'+str(__n_val))
       
    def __ProcessHUEData(self):
        
        __T_hue=np.nanmedian(self.__HueData)     #Median
        __sig_hue=np.nanstd(self.__HueData)      #standard deviation
        __n_hue=0.5
        
        self.DataViewer.DebugPrint(__n_hue,'nhue')
        self.DataViewer.DebugPrint(__T_hue,'Thue')
        self.DataViewer.DebugPrint(__sig_hue,'Shue')
        
        #HUE channel conditional constant 
        __c1_hue=__T_hue+__sig_hue*__n_hue
        __c2_hue=__T_hue-__sig_hue*__n_hue
        
        self.DataViewer.DebugPrint(__c1_hue,'c1hue')
        self.DataViewer.DebugPrint(__c2_hue,'c2hue')
        
        
        self.__IsWater_hue=np.empty(np.shape(self.__HueData))
        self.__IsWater_hue[:]=0
        self.__IsWater_hue[(self.__HueData<__c1_hue) & (self.__HueData>__c2_hue) ]=1  ##Change in condition
        
        #3.1.2_Is_Water_Hue_SF-'+str(__n_hue)
        self.__SaveChannelData(self.__IsWater_hue,'3.1.2_Is_Water_Hue_SF-'+str(__n_hue))
       
        
    
        
    def GetIsWater(self):
        self.__LoadHueValue()
        self.__ProcessValData()
        self.__ProcessHUEData()
        IsWater=np.empty(np.shape(self.__IsWater_val))
        IsWater[:]=0
        IsWater[(self.__IsWater_hue==1) & (self.__IsWater_val==1)]=1
        #3.1.3_IsWater_nhue-str(nHue)_nVal-(nVal)
        self.__SaveChannelData(IsWater,'3.1.3_IsWater')        
