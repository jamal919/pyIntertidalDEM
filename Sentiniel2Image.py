#!/usr/bin/env python3
from Sentiniel2Logger import TiffReader,ViewData,SaveData,TiffWritter
import os,numpy as np,matplotlib.pyplot as plt,scipy.ndimage
class ConstructImage(object):
    def __init__(self,Directory):
        self.directory=Directory                                           #The directory that contains the files(MASKS and Band Files)

        self.__OutputFolder=str(os.getcwd())+'/Output_log/'

        if not os.path.exists(self.__OutputFolder):

            os.mkdir(self.__OutputFolder)

        self.__DirectoryStrings=str(self.directory).split('/')             #split the directory to extract specific folder
        
        self.__DirectoryStrings=list(filter(bool,self.__DirectoryStrings))
        
        self.BandFileB12=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B12.tif'
        
        self.IAOMask=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_IAO_R1.tif'

        self.TiffReader=TiffReader(Directory)

        self.DataViewer=ViewData(Directory)

        self.DataSaver=SaveData(Directory)

        self.SaveTiff=TiffWritter(Directory)

    
    def RGBImage(self):
        IAO=self.TiffReader.GetTiffData(self.IAOMask)
        
        B12=self.TiffReader.GetTiffData(self.BandFileB12)
        B12=np.array(B12.repeat(2,axis=0).repeat(2,axis=1))
        
        IAO[B12==-10000]=0
        Labeled,_=scipy.ndimage.measurements.label(IAO)
        Feature,CountsOfFeature = np.unique(Labeled, return_counts=True)
        Max=np.amax(CountsOfFeature[Feature>0])
        POS=np.argwhere(CountsOfFeature==Max)
        Data=np.zeros(np.shape(IAO))
        Data[Labeled==POS]=1
        Labeled[Data==1]=0
        #self.DataViewer.PlotWithGeoRef(Labeled,'Label')

        B12[B12==-10000]=0
        B12[Data==1]=0
        B12=B12/np.amax(B12)
        B12[Labeled>0]=1
        
        self.DataViewer.PlotWithGeoRef(B12,'B12')

        
        #self.SaveTiff.SaveArrayToGeotiff(Data,'Data')         
        
if __name__=='__main__':
    #DataPath='/home/ansary/Sentiniel2/Data/'
    #DataFolders=os.listdir(path=DataPath)
    
    DataPath='/home/ansary/Sentiniel2/Data/SENTINEL2B_20171223-043613-607_L2A_T45QYE_D_V1-4/'
    ImObj=ConstructImage(DataPath)
    ImObj.RGBImage()
    plt.show()
    
    '''
    for df in DataFolders:
        directory=DataPath+df+'/'
        ImObj=ConstructImage(directory)
        ImObj.RGBImage()
    '''