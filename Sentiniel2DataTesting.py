import numpy as np,scipy.signal,scipy.ndimage 
from Sentiniel2Logger import Log

class DataTester(object):
    def __init__(self,Directory,Data):
        self.Directory=Directory
        self.Data=Data
        self.__Logger=Log(self.Directory)
        self.__kernel=np.ones((5,5),np.uint8)

    def __HoleFillWaterMap(self):
        self.Data=scipy.ndimage.morphology.binary_fill_holes(self.Data)
        self.__Logger.DebugPlot(self.Data,'HoleFillData')

    def NoiseRemovalKernel(self):
        self.__HoleFillWaterMap()
        self.__NoiseData=scipy.signal.convolve2d(self.Data,self.__kernel)
        self.__Logger.DebugPlot(self.__NoiseData,'Noise Data')
        self.__Logger.DebugPrint(self.__NoiseData,'Noise Data')
