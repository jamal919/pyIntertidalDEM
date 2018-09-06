from Sentiniel2Logger import TiffReader,TiffWritter,Info,ViewData
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
        self.DataViewer=ViewData(Directory)

    def HueValueRGB(self): 
        print('Computing Hue and Value channel')
        __RedData=self.TiffReader.GetTiffData(self.RedDataFile)
        __GreenData=self.TiffReader.GetTiffData(self.GreenDataFile)
        __BlueData=self.TiffReader.GetTiffData(self.BlueDataFile)
       
        __Inan=np.isnan(__RedData)

        
        __Max=np.maximum(np.maximum(__RedData,__GreenData),__BlueData) ##Val
        __Max[__Inan]=np.nan

        
        __Min=np.minimum(np.minimum(__RedData,__GreenData),__BlueData)
        __Min[__Inan]=np.nan
        

        __Chroma=__Max-__Min
        __Chroma[__Inan]=0
        '''
        __RedData[__Inan]=np.nan
        __BlueData[__Inan]=np.nan
        __GreenData[__Inan]=np.nan
        '''
        __Ipos= __Chroma>0

        __Hue=np.empty(np.shape(__Max))        
        __Hue[:]=0

        idx = (__RedData== __Max) & __Ipos 
        __Hue[idx] = (__GreenData[idx] - __BlueData[idx]) / __Chroma[idx]

        idx = (__GreenData == __Max) & __Ipos 
        __Hue[idx] = 2. + (__BlueData[idx] - __RedData[idx]) / __Chroma[idx]

        idx = (__BlueData == __Max) & __Ipos 
        __Hue[idx] = 4. + (__RedData[idx] - __GreenData[idx]) / __Chroma[idx]
        
        __Hue= (__Hue / 6.0) % 1.0

        __Hue=__Hue/np.amax(__Hue)
        __Hue[__Inan]=np.nan
        
        self.TiffWritter.SaveArrayToGeotiff(__Hue,'Hue Data')
        self.DataViewer.PlotWithGeoRef(__Hue,'Hue')
        self.TiffWritter.SaveArrayToGeotiff(__Max,'Value Data')
        self.DataViewer.PlotWithGeoRef(__Max,'Value')
        
    
    def HueValueRGBspherical(self):
        print('Computing Hue and Value channel')
        Red=self.TiffReader.GetTiffData(self.RedDataFile)
        Green=self.TiffReader.GetTiffData(self.GreenDataFile)
        Blue=self.TiffReader.GetTiffData(self.BlueDataFile)

        Hue=np.empty(np.shape(Red))
        iPosOrange= (Red>=Green) & (Green>=Blue)
        iPosChartreuseGreen=(Green>Red) & (Red>=Blue)
        iPosSpringGreen=(Green>=Blue) & (Blue>Red)
        iPosAzure=(Blue>Green) & (Green>Red)
        iPosViolet=(Blue>Red) & (Red>=Green)
        iPosRose=(Red>=Blue) & (Blue>Green)
        
        Hue[iPosOrange]=(Green[iPosOrange]-Blue[iPosOrange])/(Red[iPosOrange]-Blue[iPosOrange])
        Hue[iPosChartreuseGreen]=2-((Red[iPosChartreuseGreen]-Blue[iPosChartreuseGreen])/(Green[iPosChartreuseGreen]-Blue[iPosChartreuseGreen]))
        Hue[iPosSpringGreen]=2+((Blue[iPosSpringGreen]-Red[iPosSpringGreen])/(Green[iPosSpringGreen]-Red[iPosSpringGreen]))
        Hue[iPosAzure]=4-((Green[iPosAzure]-Red[iPosAzure])/(Blue[iPosAzure]-Red[iPosAzure]))
        Hue[iPosViolet]=4+((Red[iPosViolet]-Green[iPosViolet])/(Blue[iPosViolet]-Green[iPosViolet]))
        Hue[iPosRose]=6-((Blue[iPosRose]-Green[iPosRose])/(Red[iPosRose]-Green[iPosRose]))

        #self.TiffWritter.SaveArrayToGeotiff(Hue,'Hue Data--sp')
        self.DataViewer.PlotWithGeoRef(Hue,'Hue--sp')