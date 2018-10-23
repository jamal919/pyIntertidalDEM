# -*- coding: utf-8 -*-
from utils.tiffwriter import TiffWriter
from utils.tiffreader import TiffReader
from utils.dataplotter import DataPlotter

import numpy as np
class Processor(object):
    '''
        Process the Hue and Value channel to construct a binary waterMap
    '''
    def __init__(self,DataDir,MaskDir,nhue,nvalue,PNGDIR=None):
        

        self.__NHUE=nhue

        self.__NVALUE=nvalue
        
        self.InputFolder=DataDir
        
        self.WMdir=MaskDir
        
        self.TiffReader=TiffReader()
        self.TiffWritter=TiffWriter()
        self.__REFGTIFF=self.InputFolder+"2.2.1_HUE_Normalized_Pekel.tiff"
        self.PNGFLAG=False
        if PNGDIR!=None:
            self.PNGFLAG=True
            self.DataViewer=DataPlotter(self.__REFGTIFF,PNGDIR)
     ##Saving Necessary Results

    def __SaveChannelData(self,Data,Identifier,SaveGeoTiff=False):
        '''
            Save's the Channel data as TIFF and PNG
        '''
        if self.PNGFLAG:
            self.DataViewer.PlotWithGeoRef(Data,str(Identifier))
        
        if(SaveGeoTiff==True):
            self.TiffWritter.SaveArrayToGeotiff(Data,str(Identifier),self.__REFGTIFF,self.InputFolder)
        
        __Data=None

    def __LoadHueValue(self):
        '''
            Reading Saved data and forming a data mask from Alpha Data
        '''
        
        print('Getting Value Data')
        __File=self.InputFolder+"2.2.2 Value Normalized Pekel.tiff"
        self.Value=self.TiffReader.GetTiffData(__File)
        
        print('Getting Hue Data')
        __File=self.InputFolder+"2.2.1_HUE_Normalized_Pekel.tiff"
        self.Hue=self.TiffReader.GetTiffData(__File)
    
    def __CreateWaterMask(self): 
        '''
            A thresh hold is selected for which Alpha is clipped to 0 to form a water mask
        '''   
        print('Getting Alpha Channel')
        __File=self.InputFolder+"1.1.2 Alpha Band N.tiff"
        Alpha=self.TiffReader.GetTiffData(__File)
        
        
        print('Creating WaterMask')
        self.iNan=np.isnan(Alpha)

        self.WaterMask=self.TiffReader.GetTiffData(self.WMdir)  
        
        self.WaterMask[self.iNan]=np.nan
    
    def __MaskHueValue(self):
        print('Masking Value Channel with water mask')
        MasKedValue=np.copy(self.Value)
        MasKedValue[self.WaterMask==0]=np.nan
        self.__SaveChannelData(MasKedValue,'3.1.1 Masked Value Channel')

        print('Inverse Masking Value Channel with water mask')
        MasKedHue=np.copy(self.Hue)
        MasKedHue[self.WaterMask==1]=np.nan
        self.__SaveChannelData(MasKedHue,'3.1.3 Inversed Masked Hue Channel')

    def __FormBinaryWaterValueChannel(self):
        '''
            BW_value is formed as:
            
            BW_value=(I_value (i, j) < T value + n value . σ value ) ∧ (I value (i, j) > T value − n value . σ value )

            Here I_value= Water Mask applied Value channel
               T_value is Median of I_value 
               S_value is standard deviation of I_value
        '''
        print('Calculating Binary Water Value Channel')
        T=np.nanmedian(self.Value[self.WaterMask==1])     #Median 
        S=np.nanstd(self.Value[self.WaterMask==1])      #standard deviation
        
        n=float(self.__NVALUE)                            #Scaling Factor

        #Value channel conditional constant 
        c1=T+n*S
        c2=T-n*S

        print('T='+str(T)+'   S='+str(S)+'     n='+str(n)+'     c1='+str(c1)+'        c2='+str(c2))

        self.BW_Value=np.zeros(self.Value.shape)
        self.BW_Value[(self.Value<c1) & (self.Value>c2) ]=1
        
        self.BW_Value=self.BW_Value.astype(np.float)
        self.BW_Value[self.iNan]=np.nan
        
        self.__SaveChannelData(self.BW_Value,'3.1.2 Binary Water Value Channel')
    
    def __FormBinaryWaterHueChannel(self):
        
        '''
            BW_hue is formed as:
            
            BW_hue=¬((I hue (i, j) < T hue + n hue . σ hue ) ∧ (I hue (i, j) > T hue − n hue . σ hue ))

            Here I hue= Inverse Water Mask applied Hue channel
               T hue is Median of I Hue 
               S hue is standard deviation of I HUe
        '''
        print('Calculating Binary Water Hue Channel')
        T=np.nanmedian(self.Hue[self.WaterMask==0])       #Median 
        S=np.nanstd(self.Hue[self.WaterMask==0])          #standard deviation
        
        n=float(self.__NHUE)                            #Scaling Factor

        #Value channel conditional constant 
        c1=T+n*S
        c2=T-n*S

        print('T='+str(T)+'   S='+str(S)+'     n='+str(n)+'     c1='+str(c1)+'        c2='+str(c2))

        self.BW_Hue=np.ones(self.Hue.shape)
        self.BW_Hue[(self.Hue<c1) & (self.Hue>c2) ]=0
        
        self.BW_Hue=self.BW_Hue.astype(np.float)
        self.BW_Hue[self.iNan]=np.nan
        
        self.__SaveChannelData(self.BW_Hue,'3.1.4 Binary Water Hue Channel')
        
    def __AndOperationWaterMap(self):
        IsWater=np.zeros(self.BW_Hue.shape)

        IsWater[(self.BW_Hue==1) & (self.BW_Value==1)]=1
        IsWater=IsWater.astype(np.float)
        IsWater[self.iNan]=np.nan
        
        self.__SaveChannelData(IsWater,'3.1.5 Binary Water Map',SaveGeoTiff=True)        
        
        
    def GetBinaryWaterMap(self):
        '''
            Produce the binary water map as follows
            > Load Hue and Value Channel Data
            > Create Water Map from Alpha Channel
            > Mask Value Inverse Mask Hue
            > Binary Value Water 
            > Birany Hue Water
            > And operation
        '''
        self.__LoadHueValue()
        self.__CreateWaterMask()
        self.__MaskHueValue()
        self.__FormBinaryWaterValueChannel()
        self.__FormBinaryWaterHueChannel()
        self.__AndOperationWaterMap()
        