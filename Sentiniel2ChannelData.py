from Sentiniel2Logger import Info,TiffReader,TiffWritter,ViewData
import numpy as np,sys 

class BandData(object):
    def __init__(self,Directory):
        InfoObj=Info(Directory)
        Files=InfoObj.DisplayFileList()
        self.__RedBandFile=Files[2]
        self.__GreenBandFile=Files[1]
        self.__BlueBandFile=Files[0]
        self.__AlphaBandFile=Files[3]
        self.__CloudMask10mFile=Files[4]
        self.__CloudMask20mFile=Files[5]
        self.TiffReader=TiffReader(Directory)
        self.TiffWritter=TiffWritter(Directory)
        self.DataViewer=ViewData(Directory)

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
        Data=Data.astype(np.float)
        Data[Data==-10000]=np.nan
        Mean=np.nanmean(Data)
        self.DataViewer.DebugPrint(Mean,'Mean')
        Std=np.nanstd(Data)
        self.DataViewer.DebugPrint(Std,'STD')
        Data=(Data-Mean)
        Data=Data/Std
        Min=(np.nanmin(Data))
        self.DataViewer.DebugPrint(Min,'Minimum')
        Data=Data+((-1)*(Min))
        self.DataViewer.DebugPrint(np.nanmax(Data),'Max')
        Data=Data/np.nanmax(Data)
        
        return Data

    def __ProcessAlphaChannel(self):
        
        self.__AlphaBand=self.TiffReader.GetTiffData(self.__AlphaBandFile) #Read
        
        __CloudMask20m=self.TiffReader.GetTiffData(self.__CloudMask20mFile) #CloudMask
        
        self.__AlphaBand=self.__CloudMaskCorrection(self.__AlphaBand,__CloudMask20m,'Alpha Band 20m')
        
        self.__AlphaUpSampling()
        
        self.__AlphaBand=self.__NormalizeData(self.__AlphaBand)

        self.DataViewer.PlotWithGeoRef(self.__AlphaBand,'Alpha')
        
            
    def __ProcessRedChannel(self):
        __RedBand=self.TiffReader.GetTiffData(self.__RedBandFile)  #Read

        __CloudMask10m=self.TiffReader.GetTiffData(self.__CloudMask10mFile) #CloudMask
        
        __RedBand=self.__CloudMaskCorrection(__RedBand,__CloudMask10m,'Red Band 10m')
        
        
        __RedBand=self.__NormalizeData(__RedBand)

        __RedBand=(1-self.__AlphaBand)+(self.__AlphaBand*__RedBand)
        
        #__RedBand=__RedBand*255

        #__RedBand=__RedBand.astype(np.uint8)                 #8 bit integer

        self.TiffWritter.SaveArrayToGeotiff(__RedBand,'Red Channel')

        self.DataViewer.PlotWithGeoRef(__RedBand,'RedBand')

    def __ProcessGreenChannel(self):
        __GreenBand=self.TiffReader.GetTiffData(self.__GreenBandFile)  #Read

        __CloudMask10m=self.TiffReader.GetTiffData(self.__CloudMask10mFile) #CloudMask
        
        __GreenBand=self.__CloudMaskCorrection(__GreenBand,__CloudMask10m,'Green Band 10m')
        
        __GreenBand=self.__NormalizeData(__GreenBand)

        __GreenBand=(1-self.__AlphaBand)+(self.__AlphaBand*__GreenBand)

        #__GreenBand=__GreenBand*255

        #__GreenBand=__GreenBand.astype(np.uint8)                 #8 bit integer

        self.TiffWritter.SaveArrayToGeotiff(__GreenBand,'Green Channel')

        self.DataViewer.PlotWithGeoRef(__GreenBand,'GreenBand')
        
    def __ProcessBlueChannel(self):
        __BlueBand=self.TiffReader.GetTiffData(self.__BlueBandFile)  #Read

        __CloudMask10m=self.TiffReader.GetTiffData(self.__CloudMask10mFile) #CloudMask
        
        __BlueBand=self.__CloudMaskCorrection(__BlueBand,__CloudMask10m,'Blue Band 10m')
        
        __BlueBand=self.__NormalizeData(__BlueBand)
        
        __BlueBand=(1-self.__AlphaBand)+(self.__AlphaBand*__BlueBand)
        
        #__BlueBand=__BlueBand*255

        #__BlueBand=__BlueBand.astype(np.uint8)                 #8 bit integer

        self.TiffWritter.SaveArrayToGeotiff(__BlueBand,'Blue Channel')

        self.DataViewer.PlotWithGeoRef(__BlueBand,'BlueBand')

        
    def Data(self):
        self.__ProcessAlphaChannel()
        self.__ProcessRedChannel()
        self.__ProcessGreenChannel()
        self.__ProcessBlueChannel()
    