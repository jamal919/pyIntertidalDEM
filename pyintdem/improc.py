# -*- coding: utf-8 -*-
'''
Image processing steps

Author: khan
Email: jamal.khan@legos.obs-mip.fr
'''
from __future__ import print_function
import numpy as np
import scipy.ndimage.measurements
import scipy.signal
from osgeo import gdal,osr
import gc 
import csv
import time
import os

from .utilities import TiffWriter
from .utilities import TiffReader
from .utilities import DataPlotter
from .utilities import Info

np.seterr(all='ignore') # set to 'warn' for debugging

class BandData(object):
    '''
        The purpose of this class is to Preprocess the individual Band data
    '''
    def __init__(self, directory, improcdir, preprocdir,png=False):
        
        self.__InfoObj = Info(directory)
        Files=self.__InfoObj.DisplayFileList()
        self.__InfoObj.DefineDiectoriesAndReferences(improcdir,preprocdir,png=png)
        
        self.__pngFlag=png
        
        if self.__pngFlag:
            self.__DataViewer=DataPlotter(self.__InfoObj.ReferenceGeotiff,self.__InfoObj.PNGOutDir)
            
        
        #Files to be used
        self.__RedBandFile = Files[0]
        self.__GreenBandFile = Files[1]
        self.__BlueBandFile = Files[2]
        self.__SWIRB11 = Files[3]
        self.__CloudMask10mFile = Files[4]
        self.__CloudMask20mFile = Files[5]
       
        self.TiffReader = TiffReader()
        self.TiffWritter = TiffWriter()
    
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
        
        __Decimals=self.__GetDecimalsWithEndBit(np.amax(MaskData))

        for v in range(0,len(__Decimals)):
            BandData[MaskData==__Decimals[v]]=-10000 # NaN values
        
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
        
    #Section- Preprocessing

    def __NanConversion(self,Data):
        '''
            Converts negative Relfectance values(Cloud and No data values) to Nan
        '''
        Data = Data.astype(np.float)
        Data[Data==-10000] = np.nan
        return Data

    def __NormalizeData(self,Data):
        '''
            Normalizes the data as follows:
                    
                                Data - Min
            > Data Normalized=-------------
                                Max - Min
        '''        
        Data = (Data-np.nanmin(Data))/(np.nanmax(Data)-np.nanmin(Data))
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
        Data = self.__CloudMaskCorrection(Data,__CloudMask20m,'SWIR Band 20m')
        Data = self.__NanConversion(Data)
        Data = self.__NormalizeData(Data)
        Data = np.array(Data.repeat(2,axis=0).repeat(2,axis=1))

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

    def __SaveChannelData(self, Data, Identifier, SaveGeoTiff=False):
        '''
            Save's the Channel data as TIFF and PNG
        '''
        if self.__pngFlag:
            self.__DataViewer.plotInMap(Data, Identifier)
        if(SaveGeoTiff==True):
            self.TiffWritter.SaveArrayToGeotiff(
                Data,str(Identifier),
                self.__InfoObj.ReferenceGeotiff,
                self.__InfoObj.MainDir
            )
        
        __DATA=None

    def __CreateAlphaChannel(self):
        '''
            Combine SWIR bands to create Alpha channel
        '''
        B11=self.TiffReader.GetTiffData(self.__SWIRB11)
       
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
        print('\t|- Preparing Alpha channel')
        self.__CreateAlphaChannel()
        print('\t|- Preparing Red channel')
        self.__ProcessRedChannel()
        print('\t|- Preparing Green channel')
        self.__ProcessGreenChannel()
        print('\t|- Preparing Blue channel')
        self.__ProcessBlueChannel()


class HSVData(object):
    '''
        The purpose of this class is to compute Hue and Value channel Data from RGB
    '''
    def __init__(self,directory,improcdir,preprocdir,png=False):
        self.__InfoObj=Info(directory)
        self.__InfoObj.DefineDiectoriesAndReferences(improcdir,preprocdir,png=png)

        InputFolder=self.__InfoObj.MainDir
        #INPUT RGB
        self.RedDataFile=InputFolder+'1.2.2 Red A.tiff'
        self.GreenDataFile=InputFolder+'1.3.2 Green A.tiff'
        self.BlueDataFile=InputFolder+'1.4.2 Blue A.tiff'
        
        self.TiffReader=TiffReader()
        self.TiffWritter=TiffWriter()
        
        self.__pngFlag=png
        if self.__pngFlag:
            self.__DataViewer=DataPlotter(self.__InfoObj.ReferenceGeotiff,self.__InfoObj.PNGOutDir)

    def HueValueRGB(self):
        '''
            Hue and Value Channel Data Are computed by Pekel et al. (2014) as follows:
            
            Value=max(R,G,B)
            
                | =0                           ; if R=G=B
                |
                |           G-B
                | =(60x-------------)mod 360   ; if V=R
                |       V-min(R,G,B)
                |
                |           B-R
            Hue=| =(60x-------------)+120      ; if V=G
                |       V-min(R,G,B)
                |           
                |           R-G
                | =(60x-------------)+240      ; if V=B
                |       V-min(R,G,B)

        '''

        print('\t|- Computing Hue and Value channel from RGB data')
        
        R=self.TiffReader.GetTiffData(self.RedDataFile)
        G=self.TiffReader.GetTiffData(self.GreenDataFile)
        B=self.TiffReader.GetTiffData(self.BlueDataFile)
        
        
        if self.__pngFlag:
            [row,col]=R.shape
            
            RGB=np.empty([row,col,3])
            
            RGB[:,:,0]=R
            RGB[:,:,1]=G
            RGB[:,:,2]=B

            #2.1.1 RGB
            
            self.__DataViewer.plotInMap(data=RGB, Identifier='2.1.1 RGB', rgb=True)
        
        # inan = np.isnan(R)
        # max_rgb = np.maximum(np.maximum(R, G), B)
        # min_rgb = np.maximum(np.maximum(R, G), B)
        # value = max_rgb
        # saturation = (value - min_rgb)/value
        
        # hue = np.empty(np.shape(R))
        # hue[np.where(value==min_rgb)] = 0
        # hue[np.where(value==R)] = (60*((G[np.where(value==R)]-B[np.where(value==R)])/(value[np.where(value==R)]-min_rgb[np.where(value==R)]))+360)%360
        # hue[np.where(value==G)] = 60*(B[np.where(value==G)]-R[np.where(value==G)])/(value[np.where(value==G)]-min_rgb[np.where(value==G)])+120
        # hue[np.where(value==B)] = 60*(R[np.where(value==B)]-G[np.where(value==B)])/(value[np.where(value==B)]-min_rgb[np.where(value==B)])+240
        # hue[inan] = np.nan
        # value[inan] = np.nan
        # saturation[inan] = np.nan
        # hue = (hue-np.nanmin(hue))/(np.nanmax(hue)-np.nanmin(hue))
        # value = (value-np.nanmin(value))/(np.nanmax(value)-np.nanmin(value))

        iN=np.isnan(R)
        Hue=np.empty(np.shape(R))

        Max=np.maximum(np.maximum(R,G),B) ##Val
        Max[iN]=np.nan

        Min=np.minimum(np.minimum(R,G),B) ##min
        Min[iN]=np.nan 
        
        #Max==Min segment
        Chroma=Max-Min
        Chroma[iN]=np.nan
        iZ=(Chroma==0)
        Hue[iZ]=0

        iV=(Chroma>0)

        #Max=Red
        iR=(R==Max) & iV
        Hue[iR]=((60*((G[iR]-B[iR])/(Max[iR]-Min[iR])))+360) % 360

        #Max=Green
        iG=(G==Max) & iV
        Hue[iG]=(60*((B[iG]-R[iG])/(Max[iG]-Min[iG])))+120

        #Max=Blue
        iB=(B==Max) & iV
        Hue[iB]=(60*((B[iB]-R[iB])/(Max[iB]-Min[iB])))+240
        Hue[iN]=np.nan
        Hue=(Hue-np.nanmin(Hue))/(np.nanmax(Hue)-np.nanmin(Hue))
        
        Max = (Max-np.nanmin(Max))/(np.nanmax(Max)-np.nanmin(Max)) #norm

        #2.2.1 HUE Normalized Pekel
        self.TiffWritter.SaveArrayToGeotiff(Hue,'2.2.1_HUE_Normalized_Pekel',self.__InfoObj.ReferenceGeotiff,self.__InfoObj.MainDir)
        
        #2.2.2 Value Normalized Pekel
        self.TiffWritter.SaveArrayToGeotiff(Max,'2.2.2 Value Normalized Pekel',self.__InfoObj.ReferenceGeotiff,self.__InfoObj.MainDir)
        if self.__pngFlag:
            self.__DataViewer.plotInMap(Hue,'2.2.1_HUE_Normalized_Pekel')
            self.__DataViewer.plotInMap(Max,'2.2.2 Value Normalized Pekel')

class WaterMap(object):
    '''
        Process the Hue and Value channel to construct a binary WaterMap
    '''
    def __init__(self,directory,improcdir,preprocdir,nhue,nvalue,png=False):
        self.__InfoObj=Info(directory)
        self.__InfoObj.DefineDiectoriesAndReferences(improcdir,preprocdir,png=png)
        
        self.__pngFlag=png
        if self.__pngFlag:
            self.__DataViewer=DataPlotter(self.__InfoObj.ReferenceGeotiff,self.__InfoObj.PNGOutDir)
        
        self.InputFolder=self.__InfoObj.MainDir
        
        self.WMdir=self.__InfoObj.ReferenceGeotiff

        self.__NHUE=nhue
        self.__NVALUE=nvalue
        
        self.TiffReader=TiffReader()
        self.TiffWritter=TiffWriter()
        


     ##Saving Necessary Results

    def __SaveChannelData(self,Data,Identifier,SaveGeoTiff=False):
        '''
            Save's the Channel data as TIFF and PNG
        '''
        if self.__pngFlag:
            self.__DataViewer.plotInMap(Data,str(Identifier))
        
        if(SaveGeoTiff==True):
            self.TiffWritter.SaveArrayToGeotiff(Data,str(Identifier),self.__InfoObj.ReferenceGeotiff,self.__InfoObj.MainDir)
        
        __Data=None

    def __LoadHueValue(self):
        '''
            Reading Saved data and forming a data mask from Alpha Data
        '''
        __File=self.InputFolder+"2.2.2 Value Normalized Pekel.tiff"
        self.Value=self.TiffReader.GetTiffData(__File)
        
        __File=self.InputFolder+"2.2.1_HUE_Normalized_Pekel.tiff"
        self.Hue=self.TiffReader.GetTiffData(__File)
    
    def __CreateWaterMask(self): 
        '''
            A thresh hold is selected for which Alpha is clipped to 0 to form a water mask
        '''
        __File=self.InputFolder+"1.1.2 Alpha Band N.tiff"
        Alpha=self.TiffReader.GetTiffData(__File)
        
        self.iNan=np.isnan(Alpha)
        self.WaterMask=self.TiffReader.GetTiffData(self.WMdir)
        self.WaterMask[self.iNan]=np.nan
    
    def __MaskHueValue(self):
        MasKedValue=np.copy(self.Value)
        MasKedValue[self.WaterMask==0]=np.nan
        self.__SaveChannelData(MasKedValue,'3.1.1 Masked Value Channel')
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
        T=np.nanmedian(self.Value[self.WaterMask==1])     #Median 
        S=np.nanstd(self.Value[self.WaterMask==1])      #standard deviation
        
        n=float(self.__NVALUE)                            #Scaling Factor

        #Value channel conditional constant 
        c1=T+n*S
        c2=T-n*S

        print('\t|\t|- Hue channel: T = {:.3f}, S = {:.3f}, n = {:.3f}, c1 = {:.3f}, c2 = {:.3f}'.format(T, S, n, c1, c2))

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
        T=np.nanmedian(self.Hue[self.WaterMask==0])       #Median 
        S=np.nanstd(self.Hue[self.WaterMask==0])          #standard deviation
        
        n=float(self.__NHUE)                            #Scaling Factor

        #Value channel conditional constant 
        c1=T+n*S
        c2=T-n*S

        print('\t|\t|- Value Channel : T = {:.3f}, S = {:.3f}, n = {:.3f}, c1 = {:.3f}, c2 = {:.3f}'.format(T, S, n, c1, c2))

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
        print('\t|- Binary water map')
        self.__LoadHueValue()
        self.__CreateWaterMask()
        self.__MaskHueValue()
        self.__FormBinaryWaterValueChannel()
        self.__FormBinaryWaterHueChannel()
        self.__AndOperationWaterMap()

class FeatureFilter(object):
    '''
        This class is designed to only consider filtering those regions which are near the ocean
        i.e-- Regions where Major connected water body exists 

        THIS CLASS IS SPECIFICLY DESIGNED FOR DEM
    '''
    def __init__(self,directory,improcdir,preprocdir,nwater=50000,nland=10000,png=False):
        self.__InfoObj=Info(directory)
        self.__InfoObj.DefineDiectoriesAndReferences(improcdir,preprocdir,png=png)
        
        self.__pngFlag=png
        if self.__pngFlag:
            self.__DataViewer=DataPlotter(self.__InfoObj.ReferenceGeotiff,self.__InfoObj.PNGOutDir)
        
        self.__InputFolder=self.__InfoObj.MainDir
        __IsWaterFile=self.__InputFolder+'/3.1.5 Binary Water Map.tiff'
        Reader=TiffReader()
        self.TiffWritter=TiffWriter()
        self.Data=Reader.GetTiffData(__IsWaterFile)
        self.__Inan=np.isnan(self.Data)
        self.__NWATER=int(nwater)
        self.__NLAND=int(nland)

        
    def __FilterLandFeatures(self,MAP):
        Features=1-MAP
        Thresh=self.__NLAND
        __SignificantData=np.zeros(np.shape(self.Data))
        __Labeled,_=scipy.ndimage.measurements.label(Features)
        _, __CountsOfFeature = np.unique(__Labeled, return_counts=True)
        __SignificantFeatures=np.argwhere(__CountsOfFeature>=Thresh).ravel()
        __SignificantFeatures=__SignificantFeatures[__SignificantFeatures>0]
        for sigF in __SignificantFeatures:
            __SignificantData[__Labeled==sigF]=1
        return __SignificantData
    
    def __DetectWaterFixed(self):
        WF=np.zeros(self.Data.shape)
        
        LabeledData,_=scipy.ndimage.measurements.label(self.Data)
        _,PixelCount=np.unique(LabeledData,return_counts=True)
        Thresh=self.__NWATER
        __SignificantFeatures=np.argwhere(PixelCount>=Thresh).ravel()
        __SignificantFeatures=__SignificantFeatures[__SignificantFeatures>0]
        for sigF in __SignificantFeatures:
            WF[LabeledData==sigF]=1
        
        WaterMap=self.__FilterLandFeatures(WF)

        return WaterMap
    
    def FilterWaterMap(self):
        print('\t|- Filtering water map')
        MapWater=self.__DetectWaterFixed()
        MapWater=1-MapWater
        MapWater[self.__Inan]=np.nan
        
        self.TiffWritter.SaveArrayToGeotiff(MapWater,'4.1.1_WaterMap',self.__InfoObj.ReferenceGeotiff,self.__InfoObj.MainDir)
        if self.__pngFlag:
            self.__DataViewer.plotInMap(MapWater,'4.1.1_WaterMap_Fixed_Thresh')
        
class Shoreline(object):
    def __init__(self,directory,improcdir,preprocdir):
        self.__InfoObj=Info(directory)
        self.__InfoObj.DefineDiectoriesAndReferences(improcdir,preprocdir)
       
        __InputFolder=self.__InfoObj.MainDir
        __WaterMapFile=__InputFolder+'/4.1.1_WaterMap.tiff'
        Reader=TiffReader()
        self.DateTime=self.__InfoObj.DateTime
       
        self.MapWater=Reader.GetTiffData(__WaterMapFile)

        __NoDataFile=self.__InfoObj.ReferenceGeotiff
        __DataSet=Reader.ReadTiffData(__NoDataFile)
        self.GeoTransForm=__DataSet.GetGeoTransform()
        self.Projection=__DataSet.GetProjection()
        __DataSet=None

    def __ConvolutedMap(self):
        [self.__row,self.__col]=np.shape(self.MapWater)
        __Kernel=np.array([[0,-1,0],[-1,4,-1],[0,-1,0]])
        __ConvolutedData=scipy.signal.convolve2d(self.MapWater[1:self.__row-1,1:self.__col-1],__Kernel)
        __ConvolutedData[__ConvolutedData<=0]=np.nan
        __ConvolutedData[__ConvolutedData>0]=1

        self.__Map_ShoreLine=np.argwhere(__ConvolutedData==1) #change this condition for testing
        self.__TotalDataPoints=np.shape(self.__Map_ShoreLine)[0]
        
        #Cleanup
        __ConvolutedData=None
        gc.collect()
    
    def __PixelToSpaceCoordinate(self):
        [__x_offset,__pixel_width,__rotation_1,__y_offset,__rotation_2,__pixel_height]=self.GeoTransForm
        __pixel_Coordinate_X=self.__Map_ShoreLine[:,1]
        __pixel_Coordinate_y=self.__Map_ShoreLine[:,0]
        self.__Space_coordinate_X= __pixel_width * __pixel_Coordinate_X +   __rotation_1 * __pixel_Coordinate_y + __x_offset
        self.__Space_coordinate_Y= __rotation_2* __pixel_Coordinate_X +    __pixel_height* __pixel_Coordinate_y + __y_offset
        
        #shift to the center of the pixel
        self.__Space_coordinate_X +=__pixel_width  / 2.0
        self.__Space_coordinate_Y +=__pixel_height / 2.0
    
    def __SpaceCoordinateToLatLon(self):
        ##get CRS from dataset
        __Coordinate_Reference_System=osr.SpatialReference() #Get Co-ordinate reference
        __Coordinate_Reference_System.ImportFromWkt(self.Projection) #projection reference

        ## create lat/long CRS with WGS84 datum<GDALINFO for details>
        __Coordinate_Reference_System_GEO=osr.SpatialReference()
        __Coordinate_Reference_System_GEO.ImportFromEPSG(4326)                   # 4326 is the EPSG id of lat/long CRS

        __Transform_term = osr.CoordinateTransformation(__Coordinate_Reference_System, __Coordinate_Reference_System_GEO)
        self.__LatitudeData=np.zeros(self.__TotalDataPoints)
        self.__LongitudeData=np.zeros(self.__TotalDataPoints)
        for indice in range(0,self.__TotalDataPoints):
            (__latitude_point, __longitude_point, _ ) = __Transform_term.TransformPoint(self.__Space_coordinate_X[indice], self.__Space_coordinate_Y[indice])
            
            self.__LatitudeData[indice]=__latitude_point
            self.__LongitudeData[indice]=__longitude_point

    def __SaveDataAsCSV(self,Data):
        '''
            Saves Lat Lon Data as CSV in a Given Format
        '''
        Identifier=self.__InfoObj.DateTime
        csvfile=self.__InfoObj.MainDir+'5.0.'+str(Identifier)+'.csv'
        with open(csvfile,"w") as output:
            writer=csv.writer(output,lineterminator='\n')
            for index in range(0,np.shape(Data)[0]):
                __Information=Data[index].tolist()
                writer.writerow(__Information)

    def generate(self):
        print('\t|- Mapping ShoreLine')
        self.__ConvolutedMap()
        self.__PixelToSpaceCoordinate()
        self.__SpaceCoordinateToLatLon()
        self.__SaveDataAsCSV(np.column_stack((self.__LatitudeData,self.__LongitudeData)))