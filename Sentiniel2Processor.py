import sys,time,gc,numpy as np

from termcolor import colored

from osgeo import gdal

from Sentiniel2Logger import Log

from Sentiniel2HueVal import HueVal

class Processor(object):

    def __init__(self,Files,Directory):

        self.Files=Files
        self.Logger=Log(Directory)

    def __ReadDataFromFile(self):
        try:
            self.__DataSet=gdal.Open(self.__Filename,gdal.GA_ReadOnly)        #taking readonly data
        
        except RuntimeError as e_Read:                                        #Error handling
            print(colored('Error while opening file!','red'))
            print(colored('Error Details:','blue'))
            print(e_Read)
            sys.exit(1)

    def __ReturnData(self):

        self.__ReadDataFromFile()
   
        if(self.__DataSet.RasterCount==1):                          
            try:
                self.__RasterBandData=self.__DataSet.GetRasterBand(1)
                
                self.__data=self.__RasterBandData.ReadAsArray()

                #manual cleanup
                self.__DataSet=None
                self.__RasterBandData=None
                gc.collect()
                
            except RuntimeError as e_arr:                                   #Error handling
                print(colored('Error while data extraction file!','red'))
                print(colored('Error Details:','blue'))
                print(e_arr)
                sys.exit(1)
        else:
            print('The file contains multiple bands','red')
            sys.exit(1)

    def __GetFileData(self,FileName):
        
        self.Logger.PrintLogStatus('Getting data from file:'+colored(FileName,'blue'))
        
        self.__Filename=FileName

        self.__ReturnData()

        return self.__data
    
    def __GetBandData(self):
        self.__B2BandData=self.__GetFileData(self.Files[0])
        self.__B4BandData=self.__GetFileData(self.Files[1])
        self.__B8BandData=self.__GetFileData(self.Files[2])
        self.__B11BandData=self.__GetFileData(self.Files[3])
                
    def __GetMaskData(self):
        self.__CloudMask10m=self.__GetFileData(self.Files[4])
        self.__CloudMask20m=self.__GetFileData(self.Files[5])
        self.__EdgeMask=self.__GetFileData(self.Files[6])
        
    def __GetDecimalsWithEndBit(self,MaxValue):
        
        __results=[]
        
        for i in range(0,MaxValue+1):
        
            __BinaryString=format(i,'08b')
        
            if(__BinaryString[-1]=='1'):
        
                __results.append(i)
        
        return __results
        
    def __CloudMaskCorrection(self,BandData,MaskData,Identifier):
        
        self.Logger.PrintLogStatus('Processing Cloud Mask With:'+colored(Identifier,'blue'))                                                                               
        
        __Decimals=self.__GetDecimalsWithEndBit(np.amax(MaskData))

        for v in range(0,len(__Decimals)):
            BandData[MaskData==__Decimals[v]]=-10000                #Exclude data point Identifier= - Reflectance value
        
        return BandData        

    def __GetMaskAppliedData(self):
        self.__B2BandData=self.__CloudMaskCorrection(self.__B2BandData,self.__CloudMask10m,'EDGE Corrected B2')
        self.__B4BandData=self.__CloudMaskCorrection(self.__B4BandData,self.__CloudMask10m,'EDGE Corrected B4')
        self.__B8BandData=self.__CloudMaskCorrection(self.__B8BandData,self.__CloudMask10m,'EDGE Corrected B8')
        self.__B11BandData=self.__CloudMaskCorrection(self.__B11BandData,self.__CloudMask20m,'EDGE Corrected B11')

        #Debug ----------------------------------------------------------------Every Segment
        #self.Logger.SaveArrayToGeotiff(self.__B2BandData,'Cloud Mask Applied B2')
        #self.Logger.SaveArrayToGeotiff(self.__B4BandData,'Cloud Mask Applied B4')
        #self.Logger.SaveArrayToGeotiff(self.__B8BandData,'Cloud Mask Applied B8')
        #self.Logger.SaveArrayToGeotiff(self.__B11BandData,'Cloud Mask Applied B11')

    def __B11UpSampling(self):
        self.__B11BandData=np.array(self.__B11BandData.repeat(2,axis=0).repeat(2,axis=1))

    def __NoDataCorrection(self):
        self.__B2BandData[self.__B2BandData== -10000]=0
        self.__B4BandData[self.__B4BandData== -10000]=0
        self.__B8BandData[self.__B8BandData== -10000]=0
        self.__B11BandData[self.__B11BandData== -10000]=0

    def __DataNormalization(self):
        self.Logger.PrintLogStatus('Normalizing data')
        self.__BlueNorm=self.__B2BandData/np.amax(self.__B2BandData)
        self.__RedNorm =self.__B4BandData/np.amax(self.__B4BandData)
        self.__GreenNorm =self.__B8BandData/np.amax(self.__B8BandData)
        self.__SWIRNorm=self.__B11BandData/np.amax(self.__B11BandData)
        
    def __RGBaToRGB(self): #RGB Image construction from RGBa ---Equation 1
        self.Logger.PrintLogStatus('Converting RGBa to RGB')
        self.__RedNew  =(1- self.__SWIRNorm)+(self.__SWIRNorm*self.__RedNorm)
        self.__GreenNew=(1- self.__SWIRNorm)+(self.__SWIRNorm*self.__GreenNorm)
        self.__BlueNew=(1- self.__SWIRNorm)+(self.__SWIRNorm*self.__BlueNorm)

        #Debug -------------------------------------------------------Red,Blue,Green
        #self.Logger.SaveArrayToGeotiff(self.__RedNew,'Red Channel')
        #self.Logger.SaveArrayToGeotiff(self.__GreenNew,'Green Channel')
        #self.Logger.SaveArrayToGeotiff(self.__BlueNew,'Blue Channel')
        
    def __RGBToHueVal(self):
        HueValOBJ=HueVal(self.__RedNew,self.__GreenNew,self.__BlueNew)
        self.__HueData=HueValOBJ.GetHUE()
        self.__ValData=HueValOBJ.GetVal()
        #Debug --------------------------------------------HUE,VALUE
        self.Logger.DebugPlot(self.__HueData,'Hue Channel Data')
        self.Logger.DebugPlot(self.__ValData,'Value Channel Data')
        
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
        __IsWater_hue=np.ones(np.shape(self.__HueData))                              
        __IsWater_hue[(self.__HueData<__c1_hue) & (self.__HueData>__c2_hue)]=0        
        __IsWater_val=np.zeros(np.shape(self.__ValData))
        __IsWater_val[(self.__ValData<__c1_val) & (self.__ValData>__c2_val)]=1            
        #MapWater data
        self.__Map_Water=np.zeros(np.shape(__IsWater_hue))
        self.__Map_Water[(__IsWater_val==1) & (__IsWater_hue==1) ]=1
          
    def __CleanUp(self):
        self.__B2BandData=None
        self.__B4BandData=None
        self.__B8BandData=None
        self.__B11BandData=None
        self.__CloudMask10m=None
        self.__CloudMask20m=None
        self.__EdgeMask=None
        self.__RedNorm=None
        self.__BlueNorm=None
        self.__SWIRNorm=None
        self.__NIRNorm=None
        self.__RedNew=None
        self.__GreenNew=None
        self.__BlueNew=None
        self.__data=None
        self.__DataSet=None
        self.__RasterBandData=None
        self.__Filename=None
        __IsWater_hue=None
        __IsWater_val=None
        self.__HueData=None
        self.__ValData=None
        gc.collect()

    def GetWaterData(self):
        start_time = time.time()
        gdal.UseExceptions()                                     #Throw any exception while processing with GDAL 
        self.__GetBandData()
        self.__GetMaskData()
        self.__GetMaskAppliedData()
        self.__B11UpSampling()
        self.__NoDataCorrection()
        self.__DataNormalization()
        self.__RGBaToRGB()
        self.__RGBToHueVal()
        self.__MapWater()
        self.__CleanUp()
        print('')
        print(colored("Total Elapsed Time(Preprocessing): %s seconds " % (time.time() - start_time),'green'))
        return self.__Map_Water