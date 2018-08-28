from Sentiniel2Logger import TiffReader,TiffWritter,Info
import numpy as np,sys 

class HSVData(object):
    def __init__(self,Directory):

        __InfoObj=Info(Directory)
        __InputFolder=__InfoObj.OutputDir()
        self.RedDataFile=__InputFolder+'/Red Channel.tiff'
        self.GreenDataFile=__InputFolder+'/Green Channel.tiff'
        self.BlueDataFile=__InputFolder+'/Blue Channel.tiff'
        self.TiffReader=TiffReader(Directory)
        self.TiffWritter=TiffWritter(Directory)

    def HueValueRGB(self): 
        print('Computing Hue and Value channel')
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

        self.TiffWritter.SaveArrayToGeotiff(__Hue,'Hue Data')
        
        self.TiffWritter.SaveArrayToGeotiff(__Max,'Value Data')
        