import numpy as np,scipy.signal,scipy.ndimage,time 
from Sentiniel2Logger import Log

class DataTester(object):
    def __init__(self,Directory,Data):
        self.Directory=Directory
        self.Data=Data
        self.__Logger=Log(self.Directory)
        
    def __PlotUpToSegments(self,num):
        __BackGround=np.zeros(np.shape(self.Data))
        for i in range(2,num):
            PointValueToConsider=self.__SortedByFeature[-i] #based on highest number of occuerence
            if i%5==0:
                __val=1
            else :
                __val=i%5
            __BackGround[self.__Labeled_array==PointValueToConsider]=__val
        self.__Logger.DebugPlot(__BackGround,'Segment:1-'+str(num)+' top data points')
        
    def __FilterUpToPixelCount(self,ThreshHold):
        __FeatureListCount=np.shape(np.where(self.__CountsOfFeature<=ThreshHold))[1]
        __FeatureValues=np.column_stack(np.where(self.__CountsOfFeature<=ThreshHold))
        __SignificantFeatureCount=self.__TotalFeatures - __FeatureListCount
        self.__PlotUpToSegments(__SignificantFeatureCount)
    
    def SegmentationWaterMap(self):
        start_time=time.time()
        self.__Labeled_array, _ =scipy.ndimage.measurements.label(self.Data)
        __FeatureNumber, self.__CountsOfFeature = np.unique(self.__Labeled_array, return_counts=True)
        self.__SortedByFeature=np.argsort(self.__CountsOfFeature)
        self.__TotalFeatures=np.shape(self.__CountsOfFeature)[0]
        self.__Logger.SaveDataAsCSV('FeatureData',np.column_stack([__FeatureNumber,self.__CountsOfFeature]))
        print("Total Elapsed Time(Segmentation): %s seconds " % (time.time() - start_time))
