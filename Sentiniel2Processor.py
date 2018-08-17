import time,matplotlib,numpy as np,gc,sys
from osgeo import gdal
from Sentiniel2Logger import Log

class Processor(object):
    
    def __init__(self,Directory):
        self.Logger=Log(Directory)
        self.Directory=Directory
        
    def __ReadDataFromFile(self,File):
        try:
            __DataSet=gdal.Open(File,gdal.GA_ReadOnly)        #taking readonly data
        
        except RuntimeError as e_Read:                             #Error handling
            print('Error while opening file!')
            print('Error Details:')
            print(e_Read)
            sys.exit(1)
        return __DataSet

    def __GetData(self,File):

        __DataSet=self.__ReadDataFromFile(File)
   
        if(__DataSet.RasterCount==1):                          
            try:
                __RasterBandData=__DataSet.GetRasterBand(1)
                
                __data=__RasterBandData.ReadAsArray()

                #manual cleanup
                __DataSet=None
                __RasterBandData=None
                gc.collect()
                
            except RuntimeError as e_arr:                                   #Error handling
                print('Error while data extraction file!')
                print('Error Details:')
                print(e_arr)
                sys.exit(1)
            return __data
        else:
            print('The file contains multiple bands')
            sys.exit(1)
    
    def __ReadHUEData(self):
        self.Logger.PrintLogStatus('Getting Hue Data')
        __File=str(self.Directory)+"Hue Channel Data.tiff"
        __HueData=self.__GetData(__File)
        return __HueData

    def __ReadValueData(self):
        self.Logger.PrintLogStatus('Getting Value Data')
        __File=str(self.Directory)+"Value Channel Data.tiff"
        __ValData=self.__GetData(__File)
        return __ValData

    def __ProcessHUEData(self):
        __HueData=self.__ReadHUEData()
        self.Logger.DebugPlot(__HueData,'Hue Data')
        #hue channel constants
        __n_hue=0.5                      #scaling factor
        __T_hue=np.median(__HueData)     #Median
        self.Logger.DebugPrint(__T_hue,'Median Hue')
        __sig_hue=np.std(__HueData)      #standard deviation
        self.Logger.DebugPrint(__sig_hue,'Standard Deviation Hue')
        
        #HUE channel conditional constant 
        __c1_hue=__T_hue+__n_hue*__sig_hue
        self.Logger.DebugPrint(__c1_hue,'Conditional Constant 1 Hue')
        __c2_hue=__T_hue-__n_hue*__sig_hue
        self.Logger.DebugPrint(__c2_hue,'Conditional Constant 2 Hue')

        __IsWater_hue=np.empty(np.shape(__HueData))
        __IsWater_hue[:]=0                              
        __IsWater_hue[(__HueData<__c1_hue) & (__HueData>__c2_hue)]=1
        return __IsWater_hue   

    def __ProcessValData(self):
        __ValData=self.__ReadValueData()
        self.Logger.DebugPlot(__ValData,'Val Data')
        #value channel constants
        __n_val=0.5                           #scaling factor(question)
        __T_val=np.median(__ValData)     #Median 
        self.Logger.DebugPrint(__T_val,'Median Val')
        __sig_val=np.std(__ValData)      #standard deviation
        self.Logger.DebugPrint(__sig_val,'Standard Deviation Val')
        #Value channel conditional constant 
        __c1_val=__T_val+__n_val*__sig_val
        self.Logger.DebugPrint(__c1_val,'Conditional Constant 1 Val')
        __c2_val=__T_val-__n_val*__sig_val
        self.Logger.DebugPrint(__c2_val,'Conditional Constant 2 Val')

        __IsWater_val=np.empty(np.shape(__ValData))
        __IsWater_val[:]=0                              
        __IsWater_val[(__ValData<__c1_val) & (__ValData>__c2_val)]=1  
        return __IsWater_val   

    def __MapWater(self):
       
        __IsWater_hue=self.__ProcessHUEData()
        __IsWater_val=self.__ProcessValData()
        __Map_Water=np.empty(np.shape(__IsWater_hue))
        __Map_Water[:]=0
        __Map_Water[(__IsWater_val==1) & (__IsWater_hue==1) ]=1
        return __Map_Water

    def GetWaterMap(self):
        gdal.UseExceptions()
        return self.__MapWater() 
