from Sentiniel2Logger import TiffReader,TiffWritter,Info,ViewData
import numpy as np,sys 

class HSVData(object):
    def __init__(self,Directory):

        __InfoObj=Info(Directory)
        __InputFolder=__InfoObj.OutputDir('TIFF')
        self.RedDataFile=__InputFolder+'/1.2.3_Red_Alpha_Applied.tiff'
        self.GreenDataFile=__InputFolder+'/1.3.3_Green_Alpha_Applied.tiff'
        self.BlueDataFile=__InputFolder+'/1.4.3_Blue_Alpha_Applied.tiff'
        self.TiffReader=TiffReader(Directory)
        self.TiffWritter=TiffWritter(Directory)
        self.DataViewer=ViewData(Directory)


    def HueValueRGB(self):
    
        print('Computing Hue and Value channel from RGB data')
        R=self.TiffReader.GetTiffData(self.RedDataFile)
        G=self.TiffReader.GetTiffData(self.GreenDataFile)
        B=self.TiffReader.GetTiffData(self.BlueDataFile)
        [row,col]=R.shape
        RGB=np.empty([row,col,3])
        RGB[:,:,0]=R
        RGB[:,:,1]=G
        RGB[:,:,2]=B

        #2.1.1 RGB
        self.DataViewer.PlotWithGeoRef(RGB,'2.1.1_RGB')
        


        iN=np.isnan(R)
        Hue=np.empty(np.shape(R))

        Max=np.maximum(np.maximum(R,G),B) ##Val
        Max[iN]=np.nan
        Min=np.minimum(np.minimum(R,G),B) ##min
        Min[iN]=np.nan
        
        #Max==Min segment
        Chroma=Max-Min
        Chroma[iN]=np.nan
        iZ=(Chroma==0)
        Hue[iZ]=0

        iV=(Chroma>0)
        #Max=Red
        iR=(R==Max) & iV
        Hue[iR]=((60*((G[iR]-B[iR])/(Max[iR]-Min[iR])))+360) % 360
        #Max=Green
        iG=(G==Max) & iV
        Hue[iG]=(60*((B[iG]-R[iG])/(Max[iG]-Min[iG])))+120
        #Max=Blue
        iB=(B==Max) & iV
        Hue[iB]=(60*((B[iB]-R[iB])/(Max[iB]-Min[iB])))+240

        Hue[iN]=np.nan
        
        Hue=Hue/np.nanmax(Hue)
        
        #2.2.1 HUE Normalized Pekel
        self.TiffWritter.SaveArrayToGeotiff(Hue,'2.2.1_HUE_Normalized_Pekel')
        self.DataViewer.PlotWithGeoRef(Hue,'2.2.1_HUE_Normalized_Pekel')
        #2.2.2 Value Normalized Pekel
        self.TiffWritter.SaveArrayToGeotiff(Max,'2.2.2 Value Normalized Pekel')
        self.DataViewer.PlotWithGeoRef(Max,'2.2.2 Value Normalized Pekel')
        