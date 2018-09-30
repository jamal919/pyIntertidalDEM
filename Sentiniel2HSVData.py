from Sentiniel2Logger import TiffReader,TiffWritter,Info,ViewData

import numpy as np,sys 

class HSVData(object):
    '''
        The purpose of this class is to compute Hue and Value channel Data from RGB
    '''
    def __init__(self,Directory):

        __InfoObj=Info(Directory)
        __InputFolder=__InfoObj.OutputDir('TIFF')
        
        #INPUT RGB
        self.RedDataFile=__InputFolder+'1.2.2 Red A.tiff'
        self.GreenDataFile=__InputFolder+'1.3.2 Green A.tiff'
        self.BlueDataFile=__InputFolder+'1.4.2 Blue A.tiff'
        
        self.TiffReader=TiffReader(Directory)
        self.TiffWritter=TiffWritter(Directory)
        self.DataViewer=ViewData(Directory)
       
    def HueValueRGB(self):
        '''
            Hue and Value Channel Data Are computed by Pekel et al. (2014) as follows:
            
            Value=max(R,G,B)
            
                | =0                           ; if R=G=B
                |
                |           G-B
                | =(60x-------------)mod 360   ; if V=R
                |       V-min(R,G,B)
                |
                |           B-R
            Hue=| =(60x-------------)+120      ; if V=G
                |       V-min(R,G,B)
                |           
                |           R-G
                | =(60x-------------)+240      ; if V=B
                |       V-min(R,G,B)

        '''

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
        self.DataViewer.PlotWithGeoRef(RGB,'2.1.1 RGB')
        
        
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
        
        Hue=(Hue-np.nanmin(Hue))/(np.nanmax(Hue)-np.nanmin(Hue))
        
        Max=(Max-np.nanmin(Max))/(np.nanmax(Max)-np.nanmin(Max)) #norm

        #2.2.1 HUE Normalized Pekel
        self.TiffWritter.SaveArrayToGeotiff(Hue,'2.2.1_HUE_Normalized_Pekel')
        self.DataViewer.PlotWithGeoRef(Hue,'2.2.1_HUE_Normalized_Pekel')
        #2.2.2 Value Normalized Pekel
        self.TiffWritter.SaveArrayToGeotiff(Max,'2.2.2 Value Normalized Pekel')
        self.DataViewer.PlotWithGeoRef(Max,'2.2.2 Value Normalized Pekel')
        