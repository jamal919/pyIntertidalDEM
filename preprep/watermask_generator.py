# -*- coding: utf-8 -*-
from __future__ import print_function

from utils.tiffreader import TiffReader
from utils.dataplotter import DataPlotter
from utils.tiffwriter import TiffWriter

import numpy as np
import os
import scipy.ndimage.measurements
import matplotlib.pyplot as plt

class WaterMaskCreator(object):
    def __init__(self,DataDir,OutPutDir,nstd,water,land,PNGDir=None):
        self.Directory=DataDir
        self.OutPutDir=str(OutPutDir)
        self.factor=nstd
        self.TiffReader=TiffReader()
        self.WaterSize=water
        self.LandSize=land
        self.TiffWriter=TiffWriter()
        self.SavePNG=False
        if PNGDir !=None:
            self.SavePNG=True
            self.PNGDir=PNGDir

    def __CloudMaskCorrection(self,BandData,MaskData):
        Decimals=self.__GetDecimalsWithEndBit(np.amax(MaskData))
        for v in range(0,len(Decimals)):
            BandData[MaskData==Decimals[v]]=-10000                #Exclude data point Identifier= - Reflectance value
        return BandData 

   
    def __GetDecimalsWithEndBit(self,MaxValue):
        results=[]
        for i in range(0,MaxValue+1):
            BinaryString=format(i,'08b')
            if(BinaryString[-1]=='1'):
                results.append(i)
        return results
    
    def __ProcessAlpha(self,Directory):
        DirectoryStrings=str(Directory).split('/')             #split the directory to extract specific folder
        DirectoryStrings=list(filter(bool,DirectoryStrings))
        
        SWIRB11File=str(os.path.join(Directory,str(DirectoryStrings[-1])+'_FRE_B11.tif'))  
        
        CloudMask20m=str(os.path.join(Directory,'MASKS',str(DirectoryStrings[-1])+'_CLM_R2.tif'))
       
        
        print('Processing Alpha Data:'+str(DirectoryStrings[-1]))
        
        B11=self.TiffReader.GetTiffData(SWIRB11File)
        CLM=self.TiffReader.GetTiffData(CloudMask20m)

        B11=self.__CloudMaskCorrection(B11,CLM)
        
        B11=np.array(B11.repeat(2,axis=0).repeat(2,axis=1))
        
        B11=B11.astype(np.float)
        
        
        iPosB11=(B11==-10000)
        
        B11[iPosB11]=np.nan
        
        B11=(B11-np.nanmin(B11))/(np.nanmax(B11)-np.nanmin(B11))
        
        
        return B11

    def __CombineAlpha(self,zone):
       
        DataPath=os.path.join(self.Directory, str(zone))
      
        DataFolders=os.listdir(path=DataPath)
        
        self.DirGtiff=str(os.path.join(DataPath,str(DataFolders[0]),str(DataFolders[0])+'_FRE_B8.tif'))
        #10m resolution Size (10980,10980)
        Gtiff=self.TiffReader.GetTiffData(self.DirGtiff)
        All=np.empty(Gtiff.shape)
        All=All.astype(np.float)
        All[:]  = np.nan
        Holder = np.empty((Gtiff.shape[0], Gtiff.shape[1], 2), dtype=np.float)
        for df in DataFolders:
            dirc=os.path.join(DataPath,df)
            Alpha=self.__ProcessAlpha(str(dirc))
            Holder[:, :, 0] = All
            Holder[:, :, 1] = Alpha
            All = np.nanmean(Holder, axis=-1, keepdims=False)
        
        All = (All-np.nanmin(All))/(np.nanmax(All)-np.nanmin(All))

        All=All/np.nanstd(All)
        WM_STD=np.ones(All.shape)
        WM_STD[All>self.factor]=0
        return WM_STD

    def __FilterWaterMask(self,Data):
       
        WF=np.zeros(Data.shape)
        #WaterFilter
        Thresh=int(self.WaterSize)
        LabeledData,_=scipy.ndimage.measurements.label(Data)
        _,PixelCount=np.unique(LabeledData,return_counts=True)
        __SignificantFeatures=np.argwhere(PixelCount>Thresh).ravel()
        __SignificantFeatures=__SignificantFeatures[__SignificantFeatures>0]
        
        for sigF in __SignificantFeatures:
            WF[LabeledData==sigF]=1
        #LandFilter
        Land=1-WF
        Thresh=int(self.LandSize)
        LabeledData,_=scipy.ndimage.measurements.label(Land)
        _,PixelCount=np.unique(LabeledData,return_counts=True)
        __SignificantFeatures=np.argwhere(PixelCount>Thresh).ravel()
        __SignificantFeatures=__SignificantFeatures[__SignificantFeatures>0]
        for sigF in __SignificantFeatures:
            Land[LabeledData==sigF]=0
        
        WF[Land==1]=1
        self.TiffWriter.SaveArrayToGeotiff(WF,self.Identifier,self.DirGtiff,self.OutPutDir)
        
        if self.SavePNG:
            Ref=os.path.join(self.OutPutDir,str(self.Identifier)+'.tiff')
            DataPlotterOBJ=DataPlotter(str(Ref),self.PNGDir)
            DataPlotterOBJ.PlotWithGeoRef(WF,self.Identifier)
            DataPlotterOBJ.plotInMap(WF,self.Identifier)

    def CreateWaterMask(self):
    
        Zones=os.listdir(self.Directory)
        Zones=['T46QCK']
        for zone in Zones:
            self.Identifier=str(zone)
            print('*Executing for Zone:'+str(zone))
            Data=self.__CombineAlpha(zone)
            self.__FilterWaterMask(Data)  
    