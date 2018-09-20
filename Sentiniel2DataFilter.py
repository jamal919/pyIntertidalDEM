import numpy as np,scipy.signal,scipy.ndimage,time 
from Sentiniel2Logger import TiffReader,Info,TiffWritter,ViewData
class DataFilter(object):
    
    def __init__(self,Directory):
        __InfoObj=Info(Directory)
        __InputFolder=__InfoObj.OutputDir('TIFF')
        __IsWaterFile=__InputFolder+'/3.1.3_IsWater.tiff'
        Reader=TiffReader(Directory)
        self.TiffWritter=TiffWritter(Directory)
        self.Data=Reader.GetTiffData(__IsWaterFile)
        self.__Inan=np.isnan(self.Data)
        self.DataViewer=ViewData(Directory)
        
    def __SegmentFeatures(self,Features,Thresh):
        __SignificantData=np.zeros(np.shape(self.Data))
        __Labeled,_=scipy.ndimage.measurements.label(Features)
        _, __CountsOfFeature = np.unique(__Labeled, return_counts=True)
        __SignificantFeatures=np.argwhere(__CountsOfFeature>=Thresh).ravel()
        __SignificantFeatures=__SignificantFeatures[__SignificantFeatures>0]
        for sigF in __SignificantFeatures:
            __SignificantData[__Labeled==sigF]=1
        return __SignificantData

    def __PercentThresh(self,Value):
        [row,col]=self.Data.shape
        Thresh=(row*col*Value)/100
        return Thresh

    def __DetectWater(self,Thresh):
        __SignificantWaterData=self.__SegmentFeatures(self.Data,Thresh) #Water Data
        __LabeledWater,_=scipy.ndimage.measurements.label(__SignificantWaterData)
        __LandData=np.ones(np.shape(self.Data))
        __LandData[__LabeledWater>0]=0
        __SignificantLandData=self.__SegmentFeatures(__LandData,Thresh)  #Land Data
        
        __MapWater=np.zeros(np.shape(self.Data))
        __MapWater[__SignificantLandData==0]=1
        return __MapWater
    
    def __DetectWaterFixed(self):
        __SignificantWaterData=self.__SegmentFeatures(self.Data,50000) #Water Data
        __LabeledWater,_=scipy.ndimage.measurements.label(__SignificantWaterData)
        __LandData=np.ones(np.shape(self.Data))
        __LandData[__LabeledWater>0]=0
        __SignificantLandData=self.__SegmentFeatures(__LandData,10000)  #Land Data
        
        __MapWater=np.zeros(np.shape(self.Data))
        __MapWater[__SignificantLandData==0]=1
        return __MapWater
    
    def FilterWaterMap(self):
        start_time=time.time()
        print('Filtering Water Map')
        '''
        for i in range(1,10):
            Thresh=self.__PercentThresh(i)
            MapWater=self.__DetectWater(Thresh)
            #self.TiffWritter.SaveArrayToGeotiff(MapWater,'4.1.1_WaterMap')
            self.DataViewer.PlotWithGeoRef(MapWater,'4.1.1_WaterMap_ '+str(i)+' %Thresh')
        '''
        MapWater=self.__DetectWaterFixed()
        MapWater[self.__Inan]=np.nan
        #self.TiffWritter.SaveArrayToGeotiff(MapWater,'4.1.1_WaterMap')
        self.DataViewer.PlotWithGeoRef(MapWater,'4.1.1_WaterMap_Fixed_Thresh')
        print("Total Elapsed Time(Segmentation): %s seconds " % (time.time() - start_time))
        