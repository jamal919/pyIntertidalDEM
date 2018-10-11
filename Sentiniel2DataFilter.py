import numpy as np,scipy.signal,scipy.ndimage,time 
from Sentiniel2Logger import TiffReader,Info,TiffWritter,ViewData
class DataFilter(object):
    '''
        This class is designed to only consider filtering those regions which are near the ocean
        i.e-- Regions where Major connected water body exists 

        THIS CLASS IS SPECIFICLY DESIGNED FOR DEM
    '''
    def __init__(self,Directory):
        __InfoObj=Info(Directory)
        __InputFolder=__InfoObj.OutputDir('TIFF')
        __IsWaterFile=__InputFolder+'/3.1.5 Binary Water Map.tiff'
        Reader=TiffReader(Directory)
        self.TiffWritter=TiffWritter(Directory)
        self.Data=Reader.GetTiffData(__IsWaterFile)
        self.__Inan=np.isnan(self.Data)
        self.DataViewer=ViewData(Directory)
        
    def __FilterLandFeatures(self,MAP):
        Features=1-MAP
        Thresh=10000
        __SignificantData=np.zeros(np.shape(self.Data))
        __Labeled,_=scipy.ndimage.measurements.label(Features)
        _, __CountsOfFeature = np.unique(__Labeled, return_counts=True)
        __SignificantFeatures=np.argwhere(__CountsOfFeature>=Thresh).ravel()
        __SignificantFeatures=__SignificantFeatures[__SignificantFeatures>0]
        for sigF in __SignificantFeatures:
            __SignificantData[__Labeled==sigF]=1
        return __SignificantData

    

    
    def __DetectWaterFixed(self):
        LabeledData,_=scipy.ndimage.measurements.label(self.Data)
        Value,PixelCount=np.unique(LabeledData,return_counts=True)
        MaxPixel=np.amax(PixelCount[Value>0])
        MaxVal=Value[PixelCount==MaxPixel]
        WF=np.zeros(self.Data.shape)
        WF[LabeledData==MaxVal[0]]=1
        
        WaterMap=self.__FilterLandFeatures(WF)

        return WaterMap
    
    def FilterWaterMap(self):
        start_time=time.time()
        print('Filtering Water Map')
        MapWater=self.__DetectWaterFixed()
        MapWater=1-MapWater
        MapWater[self.__Inan]=np.nan
        
        
        self.TiffWritter.SaveArrayToGeotiff(MapWater,'4.1.1_WaterMap')
        self.DataViewer.PlotWithGeoRef(MapWater,'4.1.1_WaterMap_Fixed_Thresh')
        
        
        print("Total Elapsed Time(Segmentation): %s seconds " % (time.time() - start_time))
        