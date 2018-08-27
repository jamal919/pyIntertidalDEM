from Sentiniel2TiffData import TiffReader,TiffWritter,NoData
from Sentiniel2Logger import Log
import numpy as np,sys 

class HSVData(object):
    def __init__(self,Directory):
        self.Logger=Log(Directory)
        self.RedDataFile=str(Directory)+'/Red Channel.tiff'
        self.GreenDataFile=str(Directory)+'/Green Channel.tiff'
        self.BlueDataFile=str(Directory)+'/Blue Channel.tiff'
        self.TiffReader=TiffReader(Directory)
        self.TiffWritter=TiffWritter(Directory)

    

    def HueValueRGB(self): 
        __RedData=self.TiffReader.GetTiffData(self.RedDataFile)
        __GreenData=self.TiffReader.GetTiffData(self.GreenDataFile)
        __BlueData=self.TiffReader.GetTiffData(self.BlueDataFile)
        
        __Max=np.maximum(np.maximum(__RedData,__GreenData),__BlueData) ##Val
        __Hue=np.empty(np.shape(__Max))
        __Hue[:]=0
        
        __Min=np.minimum(np.minimum(__RedData,__GreenData),__BlueData)
        __Chroma=__Max-__Min
        __Ipos= __Chroma>0
        
        idx = (__RedData== __Max) & __Ipos
        __Hue[idx] = (__GreenData[idx] - __BlueData[idx]) / __Chroma[idx]

        idx = (__GreenData == __Max) & __Ipos
        __Hue[idx] = 2. + (__BlueData[idx] - __RedData[idx]) / __Chroma[idx]

        idx = (__BlueData == __Max) & __Ipos
        __Hue[idx] = 4. + (__RedData[idx] - __GreenData[idx]) / __Chroma[idx]
        
        __Hue= (__Hue / 6.0) % 1.0

        #self.TiffWritter.SaveArrayToGeotiff(__Hue,'Hue Data')
        
        #self.TiffWritter.SaveArrayToGeotiff(__Max,'Value Data')
        self.Logger.DebugPlot(__Hue,'Hue Data')
        self.Logger.DebugPlot(__Max,'Value Data')
        