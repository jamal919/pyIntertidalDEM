# -*- coding: utf-8 -*-
from utils.tiffwriter import TiffWriter
from utils.tiffreader import TiffReader
from utils.dataplotter import DataPlotter
from utils.information import Info

import numpy as np 
import os


class BandData(object):
    '''
        The purpose of this class is to Process the Band data
    '''
    def __init__(self,directory,improcdir,preprocdir,png=False):
        
        self.__InfoObj=Info(directory)
        Files=self.__InfoObj.DisplayFileList()
        self.__InfoObj.DefineDiectoriesAndReferences(improcdir,preprocdir,png=png)
        
        self.__pngFlag=png
        if self.__pngFlag:
            self.__DataViewer=DataPlotter(self.__InfoObj.ReferenceGeotiff,self.__InfoObj.PNGOutDir)
            
        
        #Files to be used
        self.__RedBandFile=Files[0]
        self.__GreenBandFile=Files[1]
        self.__BlueBandFile=Files[2]
        
        self.__SWIRB11=Files[3]
        
        self.__CloudMask10mFile=Files[4]
        self.__CloudMask20mFile=Files[5]
       
        self.TiffReader=TiffReader()
        self.TiffWritter=TiffWriter()

        

   #-----------------------------------------------------------------------------------------------------------------     
   ##Section-- Cloud masking
    
    def __CloudMaskCorrection(self,BandData,MaskData,Identifier):
        
        
        '''
            A cloud mask for each resolution (CLM_R1.tif ou CLM_R2.tif) contains the following 8 Bit data
                - bit 0 (1) : all clouds except the thinnest and all shadows
                - bit 1 (2) : all clouds (except the thinnest)
                - bit 2 (4) : clouds detected via mono-temporal thresholds
                - bit 3 (8) : clouds detected via multi-temporal thresholds
                - bit 4 (16) : thinnest clouds
                - bit 5 (32) : cloud shadows cast by a detected cloud
                - bit 6 (64) : cloud shadows cast by a cloud outside image
                - bit 7 (128) : high clouds detected by 1.38 µm
            
            An aggresive cloud masking is done based on the bit 0 (all clouds except the thinnest and all shadows)
            
            The algorithm for cloud detecting all clouds except the thinnest and all shadows is as follows:
            > Get the maximum value of CLM File
            > Get the decimal numbers that ends with 1 upto the maximum value
            > Set the pixels contains these decimals to negative Reflectance and return the data file  
        
        '''
        print('Processing Cloud Mask With:'+Identifier)                                                                               
        
        __Decimals=self.__GetDecimalsWithEndBit(np.amax(MaskData))

        for v in range(0,len(__Decimals)):
            BandData[MaskData==__Decimals[v]]=-10000                #Exclude data point Identifier= - Reflectance value
        
        return BandData 
    
    
    def __GetDecimalsWithEndBit(self,MaxValue):
        '''
            Detects all the values that contains endbit set to 1
        '''
        __results=[]
        
        for i in range(0,MaxValue+1):
        
            __BinaryString=format(i,'08b')
        
            if(__BinaryString[-1]=='1'):
        
                __results.append(i)
        
        return __results
        
    #-------------------------------------------------------------------------------------------------------------------
    #Section- Preprocessing

    def __NanConversion(self,Data):
        '''
            Converts negative Relfectance values(Cloud and No data values) to Nan
        '''
        Data=Data.astype(np.float)
        Data[Data==-10000]=np.nan
        return Data

    def __NormalizeData(self,Data):
        '''
            Normalizes the data as follows:
                    
                                Data - Min
            > Data Normalized=-------------
                                Max - Min
        '''        
        Data=(Data-np.nanmin(Data))/(np.nanmax(Data)-np.nanmin(Data))
        return Data
    

    def __PreprocessAlpha(self,Data):
        '''
            Preprocess SWIR Band Data as follows:
            > Apply cloud mask
            > Nan convert negative reflectance values
            > Normalize Data
            > Upsample Data
        '''
        __CloudMask20m=self.TiffReader.GetTiffData(self.__CloudMask20mFile) #CloudMask        
        Data=self.__CloudMaskCorrection(Data,__CloudMask20m,'SWIR Band 20m')

        Data=self.__NanConversion(Data)

        Data=self.__NormalizeData(Data)

        Data=np.array(Data.repeat(2,axis=0).repeat(2,axis=1))

        return Data


    def __PreprocessChannel(self,Data):
        '''
            Preprocess RGB Band Data as follows:
            > Apply cloud mask
            > Nan convert negative reflectance values
            > Normalize Data
        '''
        __CloudMask10m=self.TiffReader.GetTiffData(self.__CloudMask10mFile) #CloudMask       
        Data=self.__CloudMaskCorrection(Data,__CloudMask10m,'RGB Band 10m')

        Data=self.__NanConversion(Data)

        Data=self.__NormalizeData(Data)

        return Data

    ##Saving Necessary Results

    def __SaveChannelData(self,Data,Identifier,SaveGeoTiff=False):
        '''
            Save's the Channel data as TIFF and PNG
        '''
        if self.__pngFlag:
            self.__DataViewer.PlotWithGeoRef(Data,str(Identifier))
        
        if(SaveGeoTiff==True):
            self.TiffWritter.SaveArrayToGeotiff(Data,str(Identifier),self.__InfoObj.ReferenceGeotiff,self.__InfoObj.MainDir)
        
        __DATA=None
    




    #Section Main

    def __CreateAlphaChannel(self):
        '''
            Combine SWIR bands to create Alpha channel
        '''
        B11=self.TiffReader.GetTiffData(self.__SWIRB11) #Read
       
        B11=self.__PreprocessAlpha(B11)
        
        self.__SaveChannelData(B11,'1.1.1 B11 Band C-U-N')
        
        self.Alpha=B11
        self.Alpha=self.__NormalizeData(self.Alpha)
        self.__SaveChannelData(self.Alpha,'1.1.2 Alpha Band N',SaveGeoTiff=True)
        
            
    def __ProcessRedChannel(self):
        RED=self.TiffReader.GetTiffData(self.__RedBandFile)
       
        RED=self.__PreprocessChannel(RED) 
        self.__SaveChannelData(RED,'1.2.1 Red C-N')
        
        RED=(1-self.Alpha)+(RED*self.Alpha)
        self.__SaveChannelData(RED,'1.2.2 Red A',SaveGeoTiff=True)
        
    def __ProcessGreenChannel(self):
        GREEN=self.TiffReader.GetTiffData(self.__GreenBandFile)
       
        GREEN=self.__PreprocessChannel(GREEN) 
        self.__SaveChannelData(GREEN,'1.3.1 Green C-N')
        
        GREEN=(1-self.Alpha)+(GREEN*self.Alpha)
        self.__SaveChannelData(GREEN,'1.3.2 Green A',SaveGeoTiff=True)
    
    def __ProcessBlueChannel(self):
        BLUE=self.TiffReader.GetTiffData(self.__BlueBandFile)
       
        BLUE=self.__PreprocessChannel(BLUE) 
        self.__SaveChannelData(BLUE,'1.4.1 Blue C-N')
        
        BLUE=(1-self.Alpha)+(BLUE*self.Alpha)
        self.__SaveChannelData(BLUE,'1.4.2 Blue A',SaveGeoTiff=True)
    


    def Data(self):
        '''
            Processing all the channel data step by step and saving the following:
            
            List of PNG

            1.1-Alpha
                --1.1.1 B11 Band C-U-N
                
                --1.1.2 Alpha Band N
                
            
            1.2-Red
                --1.2.1 Red C-N
                --1.2.2 Red A
            
            1.3-Green
                --1.3.1 Green C-N
                --1.3.2 Green A
                
            1.4-Blue
                --1.4.1 Blue C-N
                --1.4.2 Blue A
            
            List of TIFF
            1.1-Alpha
                --1.1.3 Alpha Band N
            1.2-Red
                --1.2.2 Red A
            
            1.3-Green
                --1.3.2 Green A
                
            1.4-Blue
                --1.4.2 Blue A
             
            **
            Notations:

                C= Cloud Mask Applied
                U= Upsampled
                N= Normalized
                A= Alpha Applied
                 
            **
                
        '''
        self.__CreateAlphaChannel()
        self.__ProcessRedChannel()
        self.__ProcessGreenChannel()
        self.__ProcessBlueChannel()