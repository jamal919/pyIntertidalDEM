# -*- coding: utf-8 -*-
from __future__ import print_function
from utils.tiffreader import TiffReader
from utils.tiffwriter import TiffWriter
from utils.information import Info
from utils.dataplotter import DataPlotter
import os
import numpy as np
class RiverLineGen(object):
    def __init__(self,wkdir,improcdir,prepdir):
        row=10980
        col=10980
        self.__DataPath=wkdir
        self.__Zones=os.listdir(wkdir)
        self.__improcdir=improcdir
        self.__prepdir=prepdir
        self.__TiffReader=TiffReader()
        self.__TiffWriter=TiffWriter()
        self.__ALLData=np.empty((row,col))
        self.__OutDir=os.path.join(self.__improcdir,'RiverMaps','')
        if not os.path.exists(self.__OutDir):
            os.mkdir(self.__OutDir)



    def CombineBinaryWaterMaps(self): 
        for zone in self.__Zones:
            print('Calculating for zone:'+str(zone))
            DataPath=str(os.path.join(self.__DataPath,zone,''))
            DataFolders=os.listdir(DataPath)
            self.__ALLData=np.zeros(self.__ALLData.shape)
            for df in DataFolders:
                directory=str(os.path.join(DataPath,df,''))
                InfoObj=Info(directory)
                InfoObj.DefineDiectoriesAndReferences(self.__improcdir,self.__prepdir,png=True)
                DataFile=InfoObj.MainDir+'3.1.5 Binary Water Map.tiff'
                print('Reading Data:'+str(DataFile))
                Data=self.__TiffReader.GetTiffData(DataFile)
                iNan=np.isnan(Data)
                Data[iNan]=0
                self.__ALLData+=Data
            DataViewer=DataPlotter(InfoObj.ReferenceGeotiff,self.__OutDir)
            DataViewer.PlotWithGeoRef(self.__ALLData,'RiverMap:'+str(zone))
            self.__TiffWriter.SaveArrayToGeotiff(self.__ALLData,'RiverMap:'+str(zone),InfoObj.ReferenceGeotiff,self.__OutDir)