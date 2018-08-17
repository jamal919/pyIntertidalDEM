import time,matplotlib,numpy as np,gc
from Sentiniel2Logger import Log

class RGBProcessor(object):
    
    def __init__(self,RGBData,Directory):
        self.RGBData=RGBData
        self.Logger=Log(Directory)
        
    def __HSVConversion(self):
        start_time=time.time()
        self.Logger.PrintLogStatus('Converting RGB to HSV')
        self.__HSVData=matplotlib.colors.rgb_to_hsv(self.RGBData)
        self.RGBData=None
        [self.__row,self.__col,_]=np.shape(self.__HSVData)
        self.__HueData=self.__HSVData[:,:,0]
        self.__ValData=self.__HSVData[:,:,2]
        self.__HSVData=None

        #Debug --------------------------------------------HUE,VALUE
        #self.Logger.DebugPlot(self.__HueData,'Hue Channel Data')
        #self.Logger.DebugPlot(self.__ValData,'Value Channel Data')
        

        print('')
        print("Total Elapsed Time(HSVConversion): %s seconds " % (time.time() - start_time))
    
    def __MapWater(self):
        self.Logger.PrintLogStatus('Mapping Water')
        #hue channel constants
        __n_hue=0.5                           #scaling factor(question)
        __T_hue=np.median(self.__HueData)     #Median
        __sig_hue=np.std(self.__HueData)      #standard deviation
        #value channel constants
        __n_val=0.5                           #scaling factor(question)
        __T_val=np.median(self.__ValData)     #Median 
        __sig_val=np.std(self.__ValData)      #standard deviation
        #HUE channel conditional constant 
        __c1_hue=__T_hue+__n_hue*__sig_hue
        __c2_hue=__T_hue-__n_hue*__sig_hue
        #Value channel conditional constant 
        __c1_val=__T_val+__n_val*__sig_val
        __c2_val=__T_val-__n_val*__sig_val
        #binary mapping as per equation 2 & 3
        __IsWater_hue=np.zeros([self.__row,self.__col])                              
        __IsWater_hue[(self.__HueData<__c1_hue) & (self.__HueData>__c2_hue)]=1        
        __IsWater_val=np.zeros([self.__row,self.__col])
        __IsWater_val[(self.__ValData<__c1_val) & (self.__ValData>__c2_val)]=1            
        #MapWater data
        self.__Map_Water=np.zeros([self.__row,self.__col])
        self.__Map_Water[(__IsWater_val==1) & (__IsWater_hue==1) ]=1
        
        #Debug ---------------------------------------- IsWaterHue,IsWaterVal,MapWater
        #self.Logger.DebugPlot(__IsWater_hue,'Is Water Hue Data')
        #self.Logger.DebugPlot(__IsWater_val,'Is Water Val Data')
        #self.Logger.DebugPlot(self.__Map_Water,' Water Map')
        
        
        
        #CleanUp
        __IsWater_hue=None
        __IsWater_val=None
        self.__HueData=None
        self.__ValData=None

    def GetWaterMap(self):
        self.__HSVConversion()
        self.__MapWater()
        return self.__Map_Water
