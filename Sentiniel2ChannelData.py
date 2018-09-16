from Sentiniel2Logger import Info,TiffReader,TiffWritter,ViewData,SaveData
import numpy as np,sys 

class BandData(object):
    def __init__(self,Directory):
        InfoObj=Info(Directory)
        Files=InfoObj.DisplayFileList()
        self.__RedBandFile=Files[3]
        self.__GreenBandFile=Files[2]
        self.__BlueBandFile=Files[0]
        self.__VegBandFile=Files[1]
        self.__AlphaBandFile=Files[4]
        self.__CloudMask10mFile=Files[5]
        self.__CloudMask20mFile=Files[6]
        self.TiffReader=TiffReader(Directory)
        self.TiffWritter=TiffWritter(Directory)
        self.DataViewer=ViewData(Directory)
        self.DataSaver=SaveData(Directory)

    def __GetDecimalsWithEndBit(self,MaxValue):
        
        __results=[]
        
        for i in range(0,MaxValue+1):
        
            __BinaryString=format(i,'08b')
        
            if(__BinaryString[-1]=='1'):
        
                __results.append(i)
        
        return __results
        
    def __CloudMaskCorrection(self,BandData,MaskData,Identifier):
        
        print('Processing Cloud Mask With:'+Identifier)                                                                               
        
        __Decimals=self.__GetDecimalsWithEndBit(np.amax(MaskData))

        for v in range(0,len(__Decimals)):
            BandData[MaskData==__Decimals[v]]=-10000                #Exclude data point Identifier= - Reflectance value
        
        return BandData 
    
    def __AlphaUpSampling(self):
        self.__AlphaBand=np.array(self.__AlphaBand.repeat(2,axis=0).repeat(2,axis=1))

    def __NormalizeData(self,Data):
        Mean=np.nanmean(Data)
        Std=np.nanstd(Data)
      
        Data[Data>Mean+3*Std]=Mean+3*Std
        Data[Data<Mean-3*Std]=Mean-3*Std
        Mean=np.nanmean(Data)
        Std=np.nanstd(Data)
        
        Data=(Data-Mean)/Std
        Min=(np.nanmin(Data))
        Data=Data+((-1)*(Min))
        Data=Data/np.nanmax(Data)
        return Data

    def __SaveChannelData(self,Data,Identifier):
        self.DataViewer.PlotWithGeoRef(Data,str(Identifier))
        self.TiffWritter.SaveArrayToGeotiff(Data,str(Identifier))

    def __NanConversion(self,Data):
        Data=Data.astype(np.float)
        Data[Data==-10000]=np.nan
        return Data

    def __ProcessAlphaChannel(self):
        
        self.__AlphaBand=self.TiffReader.GetTiffData(self.__AlphaBandFile) #Read

        __CloudMask20m=self.TiffReader.GetTiffData(self.__CloudMask20mFile) #CloudMask
        
        self.__AlphaBand=self.__CloudMaskCorrection(self.__AlphaBand,__CloudMask20m,'Alpha Band 20m')
        
        self.__AlphaUpSampling()

        self.__AlphaBand=self.__NanConversion(self.__AlphaBand)

        ##1.1.1 Alpha CLOUD
        self.__SaveChannelData(self.__AlphaBand,'1.1.1_Alpha_CLM_Upsampled')

        self.__AlphaBand=self.__NormalizeData(self.__AlphaBand)
        
        self.__AlphaBand=np.around(self.__AlphaBand,decimals=2)
        ##1.1.2 Alpha NORM
        self.__SaveChannelData(self.__AlphaBand,'1.1.2_Alpha_NORM')
        
        self.__AlphaBand[self.__AlphaBand<0.1]=0
        ##1.1.3 Alpha Modified
        self.__SaveChannelData(self.__AlphaBand,'1.1.3 Alpha Modified')
        
        
            
    def __ProcessRedChannel(self):
        __RedBand=self.TiffReader.GetTiffData(self.__RedBandFile)  #Read

        __CloudMask10m=self.TiffReader.GetTiffData(self.__CloudMask10mFile) #CloudMask
        
        __RedBand=self.__CloudMaskCorrection(__RedBand,__CloudMask10m,'Red Band 10m')
        
        __RedBand=self.__NanConversion(__RedBand)

        #1.2.1 Red CLM
        self.__SaveChannelData(__RedBand,'1.2.1_RED_CLM')

        __RedBand=self.__NormalizeData(__RedBand)

        #1.2.2 Red NORM
        self.__SaveChannelData(__RedBand,'1.2.2_RED_NORM')

        __RedBand=(1-self.__AlphaBand)+(self.__AlphaBand*__RedBand)

        #1.2.3 Red Alpha Applied
        self.__SaveChannelData(__RedBand,'1.2.3_Red_Alpha_Applied')
 
    def __ProcessGreenChannel(self):
        __GreenBand=self.TiffReader.GetTiffData(self.__GreenBandFile)  #Read

        __CloudMask10m=self.TiffReader.GetTiffData(self.__CloudMask10mFile) #CloudMask
        
        __GreenBand=self.__CloudMaskCorrection(__GreenBand,__CloudMask10m,'Green Band 10m')
        
        __GreenBand=self.__NanConversion(__GreenBand)

        #1.3.1 Green CLM
        self.__SaveChannelData(__GreenBand,'1.3.1_Green_CLM')

        __GreenBand=self.__NormalizeData(__GreenBand)

        #1.3.2 Green NORM
        self.__SaveChannelData(__GreenBand,'1.3.2_Green_NORM')

        __GreenBand=(1-self.__AlphaBand)+(self.__AlphaBand*__GreenBand)

        #1.3.3 Green Alpha Applied
        self.__SaveChannelData(__GreenBand,'1.3.3_Green_Alpha_Applied')


    def __ProcessBlueChannel(self):
        __BlueBand=self.TiffReader.GetTiffData(self.__BlueBandFile)  #Read

        __CloudMask10m=self.TiffReader.GetTiffData(self.__CloudMask10mFile) #CloudMask
        
        __BlueBand=self.__CloudMaskCorrection(__BlueBand,__CloudMask10m,'Blue Band 10m')
        
        __BlueBand=self.__NanConversion(__BlueBand)

        #1.4.1 Blue CLM
        self.__SaveChannelData(__BlueBand,'1.4.1_Blue_CLM')

        __BlueBand=self.__NormalizeData(__BlueBand)

        #1.4.2 Blue NORM
        self.__SaveChannelData(__BlueBand,'1.4.2_Blue_NORM')

        __BlueBand=(1-self.__AlphaBand)+(self.__AlphaBand*__BlueBand)

        #1.4.3 Blue Alpha Applied
        self.__SaveChannelData(__BlueBand,'1.4.3_Blue_Alpha_Applied')
        
    def Data(self):
        self.__ProcessAlphaChannel()
        self.__ProcessRedChannel()
        self.__ProcessGreenChannel()
        self.__ProcessBlueChannel()
       