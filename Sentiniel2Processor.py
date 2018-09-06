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
        #self.DataViewer.PlotWithGeoRef(__HueData,'hue')
        mean=np.nanmedian(__HueData)
        std=np.nanstd(__HueData)
        stdtest=np.empty(np.shape(__HueData))
        ig=(__HueData<mean+1*std) & (__HueData>mean-1*std)
        stdtest[ig]=__HueData[ig]
        stdtest[np.isnan(__HueData)]=np.nan 
        stdtest[stdtest==0]=np.nan
        self.DataViewer.PlotWithGeoRef(stdtest,'1st std')
        ig1=(__HueData<mean+2*std) & (__HueData>mean-2*std)
        stdtest[ig1]=__HueData[ig1]
        stdtest[ig]=np.nan
        self.DataViewer.PlotWithGeoRef(stdtest,'2nd std')
        ig2=(__HueData<mean+3*std) & (__HueData>mean-3*std)
        stdtest[ig2]=__HueData[ig2]
        stdtest[ig1]=np.nan
        self.DataViewer.PlotWithGeoRef(stdtest,'3rd std')
        ig3=(__HueData<mean+4*std) & (__HueData>mean-4*std)
        stdtest[ig3]=__HueData[ig3]
        stdtest[ig2]=np.nan
        self.DataViewer.PlotWithGeoRef(stdtest,'4th std')
        ig4=(__HueData<mean+5*std) & (__HueData>mean-5*std)
        stdtest[ig4]=__HueData[ig4]
        stdtest[ig3]=np.nan
        self.DataViewer.PlotWithGeoRef(stdtest,'5th std')
        
        
        '''
        #hue channel constants
        __n_hue=1                      #scaling factor
         
        __T_hue=np.nanmedian(__HueData)     #Median
        __sig_hue=np.nanstd(__HueData)      #standard deviation
        
        self.DataViewer.DebugPrint(__T_hue,'Thue')
        self.DataViewer.DebugPrint(__sig_hue,'Shue')
        
        #HUE channel conditional constant 
        __c1_hue=__T_hue+__n_hue*__sig_hue
        __c2_hue=__T_hue-__n_hue*__sig_hue
        self.DataViewer.DebugPrint(__c1_hue,'c1hue')
        self.DataViewer.DebugPrint(__c2_hue,'c2hue')
        
        
        self.__IsWater_hue=np.empty(np.shape(__HueData))
        self.__IsWater_hue[:]=0
        self.__IsWater_hue[(__HueData>__c1_hue) | (__HueData<__c2_hue)]=1  ##Change in condition
        self.DataViewer.PlotWithGeoRef(self.__IsWater_hue,'self.__IsWater_hue')
        '''
    def __ProcessValData(self):
        print('Getting Value Data')
        __File=self.__InputFolder+"/Value Data.tiff"
        __ValData=self.TiffReader.GetTiffData(__File)
        self.DataViewer.PlotWithGeoRef(__ValData,'val')
        '''
        #value channel constants
        __n_val=1                           #scaling factor(question)
        
        __T_val=np.nanmedian(__ValData)     #Median 
        __sig_val=np.nanstd(__ValData)      #standard deviation
        
        self.DataViewer.DebugPrint(__T_val,'Tval')
        self.DataViewer.DebugPrint(__sig_val,'Sval')
        
        #Value channel conditional constant 
        __c1_val=__T_val+__n_val*__sig_val
        __c2_val=__T_val-__n_val*__sig_val
        self.DataViewer.DebugPrint(__c1_val,'c1hue')
        self.DataViewer.DebugPrint(__c2_val,'c2hue')
        
        
        self.__IsWater_val=np.empty(np.shape(__ValData))
        self.__IsWater_val[:]=0
        self.__IsWater_val[(__ValData<__c1_val) & (__ValData>__c2_val)]=1
        self.DataViewer.PlotWithGeoRef(self.__IsWater_val,'self.__IsWater_val')
        '''
    def GetIsWater(self):
        self.__ProcessHUEData()
        #self.__ProcessValData()
        '''
        IsWater=np.empty(np.shape(self.__IsWater_val))
        IsWater[:]=0
        IsWater[(self.__IsWater_hue==1) & (self.__IsWater_val==1)]=1
        self.DataViewer.PlotWithGeoRef(IsWater,'IsWater')
        self.TiffWritter.SaveArrayToGeotiff(IsWater,'Iswater')
        '''