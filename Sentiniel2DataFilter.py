import numpy as np,scipy.signal,scipy.ndimage,time 
from Sentiniel2Logger import TiffReader,Info,TiffWritter
class DataFilter(object):
    
    def __init__(self,Directory):
        __InfoObj=Info(Directory)
        __InputFolder=__InfoObj.OutputDir('TIFF')
        __IsWaterFile=__InputFolder+'/3.1.3_IsWater.tiff'
        Reader=TiffReader(Directory)
        self.TiffWritter=TiffWritter(Directory)
        self.Data=Reader.GetTiffData(__IsWaterFile)
        
    def __SegmentFeatures(self,Features,Thresh):
        __SignificantData=np.zeros(np.shape(self.Data))
        __Labeled,_=scipy.ndimage.measurements.label(Features)
        _, __CountsOfFeature = np.unique(__Labeled, return_counts=True)
        __SignificantFeatures=np.argwhere(__CountsOfFeature>=Thresh).ravel()
        __SignificantFeatures=__SignificantFeatures[__SignificantFeatures>0]
        for sigF in __SignificantFeatures:
            __SignificantData[__Labeled==sigF]=1
        return __SignificantData

    def __DetectWater(self):
        
        __SignificantWaterData=self.__SegmentFeatures(self.Data,100000) #Water Data
        __LabeledWater,_=scipy.ndimage.measurements.label(__SignificantWaterData)
        __LandData=np.ones(np.shape(self.Data))
        __LandData[__LabeledWater>0]=0
        __SignificantLandData=self.__SegmentFeatures(__LandData,10000)  #Land Data
        
        self.__MapWater=np.zeros(np.shape(self.Data))
        self.__MapWater[__SignificantLandData==0]=1
        
    def FilterWaterMap(self):
        start_time=time.time()
        print('Filtering Water Map')
        self.__DetectWater()
        self.TiffWritter.SaveArrayToGeotiff(self.__MapWater,'WaterMap')
        print("Total Elapsed Time(Segmentation): %s seconds " % (time.time() - start_time))
        