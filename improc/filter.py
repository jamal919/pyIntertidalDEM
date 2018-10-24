from utils.tiffwriter import TiffWriter
from utils.tiffreader import TiffReader
from utils.dataplotter import DataPlotter
from utils.information import Info
import numpy as np
import scipy.ndimage.measurements
import time
class DataFilter(object):
    '''
        This class is designed to only consider filtering those regions which are near the ocean
        i.e-- Regions where Major connected water body exists 

        THIS CLASS IS SPECIFICLY DESIGNED FOR DEM
    '''
    def __init__(self,directory,improcdir,preprocdir,nwater=50000,nland=10000,png=True):
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
        start_time=time.time()
        print('Filtering Water Map')
        MapWater=self.__DetectWaterFixed()
        MapWater=1-MapWater
        MapWater[self.__Inan]=np.nan
        
        
        self.TiffWritter.SaveArrayToGeotiff(MapWater,'4.1.1_WaterMap',self.__InfoObj.ReferenceGeotiff,self.__InfoObj.MainDir)
        if self.__pngFlag:
            self.__DataViewer.PlotWithGeoRef(MapWater,'4.1.1_WaterMap_Fixed_Thresh')
        
        
        print("Total Elapsed Time(Segmentation): %s seconds " % (time.time() - start_time))
        