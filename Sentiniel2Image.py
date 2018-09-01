#!/usr/bin/env python3
from Sentiniel2Logger import TiffReader,ViewData,SaveData
import os,numpy as np
class ConstructImage(object):
    def __init__(self,Directory):
        self.directory=Directory                                           #The directory that contains the files(MASKS and Band Files)

        self.__OutputFolder=str(os.getcwd())+'/Output_log/'

        if not os.path.exists(self.__OutputFolder):

            os.mkdir(self.__OutputFolder)

        self.__DirectoryStrings=str(self.directory).split('/')             #split the directory to extract specific folder
        
        self.__DirectoryStrings=list(filter(bool,self.__DirectoryStrings))
        
        self.BandFileB2=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B2.tif'
        
        self.BandFileB3=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B3.tif'
        
        self.BandFileB4=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B4.tif'
        
        self.TiffReader=TiffReader(Directory)

        self.DataViewer=ViewData(Directory)

        self.DataSaver=SaveData(Directory)

    def RGBImage(self):
        Blue=self.TiffReader.GetTiffData(self.BandFileB2)
        Green=self.TiffReader.GetTiffData(self.BandFileB3)
        Red=self.TiffReader.GetTiffData(self.BandFileB4)
        
        Blue[Blue==-10000]=0
        Green[Green==-10000]=0
        Red[Red==-10000]=0
        
        Blue=Blue/np.amax(Blue)
        Green=Green/np.amax(Green)
        Red=Red/np.amax(Red)
        [__row,__col]=np.shape(Blue)         #Row Col of the image
        __dim=3                                         #RGB 
        RGBData=np.zeros([__row,__col,__dim])   #Black Background
        RGBData[:,:,0]=Red
        RGBData[:,:,1]=Green
        RGBData[:,:,2]=Blue
        self.DataSaver.SaveRGBAsImage('RGBData',RGBData)

if __name__=='__main__':
    DataPath='/home/ansary/Sentiniel2/Data/'
    DataFolders=os.listdir(path=DataPath)
    for df in DataFolders:
        directory=DataPath+df+'/'
        ImObj=ConstructImage(directory)
        ImObj.RGBImage()
