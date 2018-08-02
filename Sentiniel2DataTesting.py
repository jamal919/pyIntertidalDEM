import numpy as np,scipy.signal,scipy.ndimage 
from Sentiniel2Logger import Log

class DataTester(object):
    def __init__(self,Directory,Data):
        self.Directory=Directory
        self.Data=Data
        self.__Logger=Log(self.Directory)
        self.__kernel=np.ones((3,3),np.uint8)

    def SegmentationWaterMap(self):
        __Labeled_array, _ =scipy.ndimage.measurements.label(self.Data)
        _, __CountsOfFeature = np.unique(__Labeled_array, return_counts=True)
        __SortedByFeature=np.argsort(__CountsOfFeature)
        __BackGround=np.zeros(np.shape(self.Data))
        for i in range(2,7):
            
            PointValueToConsider=__SortedByFeature[-i] #based on highest number of occuerence
            __BackGround[__Labeled_array==PointValueToConsider]=i-1+5
        self.__Logger.DebugPlot(__BackGround,'Segment:1-5 top data points')
