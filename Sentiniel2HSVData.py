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
        __Ipos= __Chroma>0

        __Hue=np.empty(np.shape(__Max))        
        __Hue[:]=0

        idx = (__RedData== __Max) & __Ipos 
        __Hue[idx] = (__GreenData[idx] - __BlueData[idx]) / __Chroma[idx]

        idx = (__GreenData == __Max) & __Ipos 
        __Hue[idx] = 2.0 + (__BlueData[idx] - __RedData[idx]) / __Chroma[idx]

        idx = (__BlueData == __Max) & __Ipos 
        __Hue[idx] = 4.0 + (__RedData[idx] - __GreenData[idx]) / __Chroma[idx]
        
        __Hue= (__Hue / 6.0) % 1.0
        
        __Hue[__Inan]=np.nan
        
        Mean=np.nanmean(__Hue)
        Std=np.nanstd(__Hue)
        __Hue=(__Hue-Mean)/Std
        Min=(np.nanmin(__Hue))
        __Hue=__Hue+((-1)*(Min))
        __Hue=__Hue/np.nanmax(__Hue)
        
        self.TiffWritter.SaveArrayToGeotiff(__Hue,'Hue Data')
        self.DataViewer.PlotWithGeoRef(__Hue,'Hue')
        self.TiffWritter.SaveArrayToGeotiff(__Max,'Value Data')
        self.DataViewer.PlotWithGeoRef(__Max,'Value')
        
    
    def HueValueRGBspherical(self):
        print('Computing Hue and Value channel')
        R=self.TiffReader.GetTiffData(self.RedDataFile)
        G=self.TiffReader.GetTiffData(self.GreenDataFile)
        B=self.TiffReader.GetTiffData(self.BlueDataFile)
        iN=np.isnan(R)
        Max=np.maximum(np.maximum(R,G),B) ##Val
        Max[iN]=np.nan
        Hue=np.empty(np.shape(R))
        iO=(R>=G) & (G> B) #infinite =
        iC=(G> R) & (R>=B) #zero
        iS=(G>=B) & (B> R) #
        iA=(B> G) & (G> R) #
        iV=(B> R) & (R>=G) #zero
        iR=(R>=B) & (B> G) #
        Hue[iO]=  ((G[iO]-B[iO])/(R[iO]-B[iO]))
        Hue[iC]=2-((R[iC]-B[iC])/(G[iC]-B[iC]))
        Hue[iS]=2+((B[iS]-R[iS])/(G[iS]-R[iS]))
        Hue[iA]=4-((G[iA]-R[iA])/(B[iA]-R[iA]))
        Hue[iV]=4+((R[iV]-G[iV])/(B[iV]-G[iV]))
        Hue[iR]=6-((B[iR]-G[iR])/(R[iR]-G[iR]))
        Hue[iN]=np.nan
        Mean=np.nanmean(Hue)
        Std=np.nanstd(Hue)
        Hue=(Hue-Mean)/Std
        Min=(np.nanmin(Hue))
        Hue=Hue+((-1)*(Min))
        Hue=Hue/np.nanmax(Hue)
        
        self.TiffWritter.SaveArrayToGeotiff(Hue,'Hue Data')
        self.DataViewer.PlotWithGeoRef(Hue,'Hue--sp')
        self.TiffWritter.SaveArrayToGeotiff(Max,'Value Data')
        self.DataViewer.PlotWithGeoRef(Max,'Value')