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
        
        self.BandFileB3=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B2.tif'
        
        self.IAOMask=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_IAO_R1.tif'

        self.TiffReader=TiffReader(Directory)

        self.DataViewer=ViewData(Directory)

        self.DataSaver=SaveData(Directory)

        self.SaveTiff=TiffWritter(Directory)

    
    def RGBImage(self):
        Data=self.TiffReader.GetTiffData(self.BandFileB3)
        Data=Data.astype(np.float)
        Data[Data==-10000]=np.nan
        self.DataViewer.PlotWithGeoRef(Data,'Data')
        
        
        stdtest=np.zeros(np.shape(Data))
        
        mean=np.nanmean(Data)
        
        std=np.nanstd(Data)
        
        ig1=(Data<mean+1*std) & (Data>mean-1*std)
        stdtest[ig1]=Data[ig1]
        stdtest[np.isnan(Data)]=np.nan
        stdtest[stdtest==0]=np.nan
        
       
        self.DataViewer.PlotWithGeoRef(stdtest,'DATA:1st std')
        
        ig2=(Data<mean+2*std) & (Data>mean-2*std)
        stdtest[ig2]=Data[ig2]
        stdtest[ig1]=np.nan

        self.DataViewer.PlotWithGeoRef(stdtest,'DATA:2nd std')

        ig3=(Data<mean+3*std) & (Data>mean-3*std)
        stdtest[ig3]=Data[ig3]
        stdtest[ig2]=np.nan

        self.DataViewer.PlotWithGeoRef(stdtest,'DATA:3rd std')

        ig4=(Data<mean+4*std) & (Data>mean-4*std)
        stdtest[ig4]=Data[ig4]
        stdtest[ig3]=np.nan
        
        self.DataViewer.PlotWithGeoRef(stdtest,'DATA:4th std')
        
        ig5=(Data<mean+5*std) & (Data>mean-5*std)
        stdtest[ig5]=Data[ig5]
        stdtest[ig4]=np.nan
        
        self.DataViewer.PlotWithGeoRef(stdtest,'DATA:5th std')         
        
    

if __name__=='__main__':
    #DataPath='/home/ansary/Sentiniel2/Data/'
    #DataFolders=os.listdir(path=DataPath)
    
    DataPath='/home/ansary/Sentiniel2/Data/SENTINEL2B_20171223-043613-607_L2A_T45QYE_D_V1-4/'
    ImObj=ConstructImage(DataPath)
    ImObj.RGBImage()
    #plt.show()
    
    '''
    for df in DataFolders:
        directory=DataPath+df+'/'
        ImObj=ConstructImage(directory)
        ImObj.RGBImage()
    '''