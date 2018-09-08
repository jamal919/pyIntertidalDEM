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
        
        self.B1f=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_ATB_R1.tif'
        self.B2f=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B2.tif'
        self.B3f=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B3.tif'
        self.B4f=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B4.tif'
        self.B5f=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B5.tif'
        self.B6f=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B6.tif'
        self.B7f=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B7.tif'
        self.B8f=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B8.tif'
        self.B8Af=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B8A.tif'
        self.B11f=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B11.tif'
        self.B12f=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B12.tif'
        self.dat='/home/ansary/Sentiniel2/prb/dat.tiff'
        
        self.IAOMask=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_IAO_R1.tif'

        self.TiffReader=TiffReader(Directory)

        self.DataViewer=ViewData(Directory)

        self.DataSaver=SaveData(Directory)

        self.TiffWritter=TiffWritter(Directory)

    def __NormalizeData(self,Data):
        
        Mean=np.nanmean(Data)
        Std=np.nanstd(Data)
        Data[Data>Mean+3*Std]=Mean+3*Std
        Data[Data<Mean-3*Std]=Mean-3*Std
        Mean=np.nanmean(Data)
        Std=np.nanstd(Data)
        
        Data=(Data-Mean)/Std
        Min=(np.nanmin(Data))
        Data=Data+((-1)*(Min))
        Data=Data/np.nanmax(Data)
        return Data

    def __CleaData(self,Data):
        Data=Data.astype(np.float)
        Data[Data==-10000]=np.nan
        return Data

    def __UpSample(self,Data):
        return  np.array(Data.repeat(2,axis=0).repeat(2,axis=1))

    def RGBImage(self):
        data=self.TiffReader.GetTiffData(self.dat)
        ##Read
        B2=self.TiffReader.GetTiffData(self.B2f)
        B3=self.TiffReader.GetTiffData(self.B3f)
        B4=self.TiffReader.GetTiffData(self.B4f)
        B5=self.TiffReader.GetTiffData(self.B5f)
        B6=self.TiffReader.GetTiffData(self.B6f)
        B7=self.TiffReader.GetTiffData(self.B7f)
        B8=self.TiffReader.GetTiffData(self.B8f)
        B8A=self.TiffReader.GetTiffData(self.B8Af)
        B11=self.TiffReader.GetTiffData(self.B11f)
        B12=self.TiffReader.GetTiffData(self.B12f)
        ##Upsample---5,6,7,8A,11,12
        B5=self.__UpSample(B5)
        B6=self.__UpSample(B6)
        B7=self.__UpSample(B7)
        B8A=self.__UpSample(B8A)
        B11=self.__UpSample(B11)
        B12=self.__UpSample(B12)

        #for clarity
        B2=self.__CleaData(B2)
        B3=self.__CleaData(B3)
        B4=self.__CleaData(B4)
        B5=self.__CleaData(B5)
        B6=self.__CleaData(B6)
        B7=self.__CleaData(B7)
        B8=self.__CleaData(B8)
        B8A=self.__CleaData(B8A)
        B11=self.__CleaData(B11)
        B12=self.__CleaData(B12)

        ##non norm
        ##Saving fig 
        '''
        self.TiffWritter.SaveArrayToGeotiff(B2*data,'B2_prb')
        self.TiffWritter.SaveArrayToGeotiff(B3*data,'B3_prb')
        self.TiffWritter.SaveArrayToGeotiff(B4*data,'B4_prb')
        self.TiffWritter.SaveArrayToGeotiff(B5*data,'B5_prb')
        self.TiffWritter.SaveArrayToGeotiff(B6*data,'B6_prb')
        self.TiffWritter.SaveArrayToGeotiff(B7*data,'B7_prb')
        self.TiffWritter.SaveArrayToGeotiff(B8*data,'B8_prb')
        self.TiffWritter.SaveArrayToGeotiff(B8A*data,'B8A_prb')
        '''
        self.TiffWritter.SaveArrayToGeotiff(B11*data,'B11_prb')
        self.TiffWritter.SaveArrayToGeotiff(B12*data,'B12_prb')


        ##Normalize---
        B2=self.__NormalizeData(B2)
        B3=self.__NormalizeData(B3)
        B4=self.__NormalizeData(B4)
        B5=self.__NormalizeData(B5)
        B6=self.__NormalizeData(B6)
        B7=self.__NormalizeData(B7)
        B8=self.__NormalizeData(B8)
        B8A=self.__NormalizeData(B8A)
        B11=self.__NormalizeData(B11)
        B12=self.__NormalizeData(B12)
        
        ##Saving fig
        ''' 
        self.TiffWritter.SaveArrayToGeotiff(B2*data,'B2_norm_prb')
        self.TiffWritter.SaveArrayToGeotiff(B3*data,'B3_norm_prb')
        self.TiffWritter.SaveArrayToGeotiff(B4*data,'B4_norm_prb')
        self.TiffWritter.SaveArrayToGeotiff(B5*data,'B5_norm_prb')
        self.TiffWritter.SaveArrayToGeotiff(B6*data,'B6_norm_prb')
        self.TiffWritter.SaveArrayToGeotiff(B7*data,'B7_norm_prb')
        self.TiffWritter.SaveArrayToGeotiff(B8*data,'B8_norm_prb')
        self.TiffWritter.SaveArrayToGeotiff(B8A*data,'B8A_norm_prb')
        '''
        self.TiffWritter.SaveArrayToGeotiff(B11*data,'B11_norm_prb')
        self.TiffWritter.SaveArrayToGeotiff(B12*data,'B12_norm_prb')

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