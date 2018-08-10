from Sentiniel2Logger import Log

import numpy as np 

class HueVal(object):

    def __init__(self,RED,GREEN,BLUE):
        self.MaxRG=np.maximum(RED,GREEN)
        self.Max=np.maximum(self.MaxRG,BLUE) 
        self.Value=self.Max/np.amax(self.Max)
        self.MinRG=np.minimum(RED,GREEN)
        self.Min=np.minimum(self.MinRG,BLUE)
        self.Chroma=self.Max-self.Min
        self.Chroma[self.Chroma==0]=-10000
        self.__HueR=(abs(GREEN-BLUE)/self.Chroma)%6
        self.__HueG=(abs(BLUE-RED)/self.Chroma)+2
        self.__HueB=(abs(GREEN-RED)/self.Chroma)+4
        self.Hue=np.zeros(np.shape(RED))
        self.Hue[np.where(self.Max==RED)]=self.__HueR[np.where(self.Max==RED)]
        self.Hue[np.where(self.Max==BLUE)]=self.__HueB[np.where(self.Max==BLUE)]
        self.Hue[np.where(self.Max==GREEN)]=self.__HueG[np.where(self.Max==GREEN)]
        self.Hue=self.Hue/np.amax(self.Hue)
    
    def GetHUE(self):
        return self.Hue
    def GetVal(self):
        return self.Value