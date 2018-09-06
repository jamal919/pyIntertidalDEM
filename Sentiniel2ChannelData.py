from Sentiniel2Logger import Info,TiffReader,TiffWritter,ViewData,SaveData
import numpy as np,sys 

class BandData(object):
    def __init__(self,Directory):
        InfoObj=Info(Directory)
        Files=InfoObj.DisplayFileList()
        self.__RedBandFile=Files[2]
        self.__GreenBandFile=Files[1]
        self.__BlueBandFile=Files[0]
        self.__NIRBandFile=Files[3]
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
        Data=Data.astype(np.float)
        Data[Data==-10000]=np.nan
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
        
        self.TiffWritter.SaveArrayToGeotiff(__RedBand,'Red Channel')
        self.DataViewer.PlotWithGeoRef(__RedBand,'Red')
        
    def __ProcessGreenChannel(self):
        __GreenBand=self.TiffReader.GetTiffData(self.__GreenBandFile)  #Read

        __CloudMask10m=self.TiffReader.GetTiffData(self.__CloudMask10mFile) #CloudMask
        
        __GreenBand=self.__CloudMaskCorrection(__GreenBand,__CloudMask10m,'Green Band 10m')
        
        __GreenBand=self.__NormalizeData(__GreenBand)

        __GreenBand=(1-self.__AlphaBand)+(self.__AlphaBand*__GreenBand)

        self.TiffWritter.SaveArrayToGeotiff(__GreenBand,'Green Channel')
        self.DataViewer.PlotWithGeoRef(__GreenBand,'Green')

    def __ProcessBlueChannel(self):
        __BlueBand=self.TiffReader.GetTiffData(self.__BlueBandFile)  #Read

        __CloudMask10m=self.TiffReader.GetTiffData(self.__CloudMask10mFile) #CloudMask
        
        __BlueBand=self.__CloudMaskCorrection(__BlueBand,__CloudMask10m,'Blue Band 10m')
        
        __BlueBand=self.__NormalizeData(__BlueBand)

        __BlueBand=(1-self.__AlphaBand)+(self.__AlphaBand*__BlueBand)

        self.TiffWritter.SaveArrayToGeotiff(__BlueBand,'Blue Channel')
        self.DataViewer.PlotWithGeoRef(__BlueBand,'Blue')

    def __modifiedGreen(self):
        Green=self.TiffReader.GetTiffData(self.__GreenBandFile)  #Read
        NIR=self.TiffReader.GetTiffData(self.__NIRBandFile)
        Green=self.__NormalizeData(Green)
        NIR=self.__NormalizeData(NIR)
        GreenNew=(Green-NIR)/(Green+NIR)
        self.DataViewer.PlotWithGeoRef(GreenNew,'Green New')
        GreenPos=np.zeros(np.shape(GreenNew))
        GreenPos[GreenNew>0]=GreenNew[GreenNew>0]
        
        self.DataViewer.PlotWithGeoRef(GreenPos,'Green Positive')

        Data=GreenPos
        stdtest=np.zeros(np.shape(Data))
        
        mean=np.nanmean(Data)
        
        std=np.nanstd(Data)
        
        ig1=(Data<mean+1*std) & (Data>mean-1*std)
        stdtest[ig1]=Data[ig1]
        stdtest[np.isnan(Data)]=np.nan
        stdtest[stdtest==0]=np.nan
        
       
        self.DataViewer.PlotWithGeoRef(stdtest,'DATA:1st std')
        
        ig2=(Data<mean+2*std) & (Data>mean-2*std)
        stdtest[ig2]=Data[ig2]
        stdtest[ig1]=np.nan

        self.DataViewer.PlotWithGeoRef(stdtest,'DATA:2nd std')

        ig3=(Data<mean+3*std) & (Data>mean-3*std)
        stdtest[ig3]=Data[ig3]
        stdtest[ig2]=np.nan

        self.DataViewer.PlotWithGeoRef(stdtest,'DATA:3rd std')

        ig4=(Data<mean+4*std) & (Data>mean-4*std)
        stdtest[ig4]=Data[ig4]
        stdtest[ig3]=np.nan
        
        self.DataViewer.PlotWithGeoRef(stdtest,'DATA:4th std')
        
        ig5=(Data<mean+5*std) & (Data>mean-5*std)
        stdtest[ig5]=Data[ig5]
        stdtest[ig4]=np.nan
        
        self.DataViewer.PlotWithGeoRef(stdtest,'DATA:5th std')     
        

        
    def Data(self):
        self.__ProcessAlphaChannel()
        self.__ProcessRedChannel()
        self.__ProcessGreenChannel()
        self.__ProcessBlueChannel()
        #self.__modifiedGreen()
    