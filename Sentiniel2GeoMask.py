from termcolor import colored
from osgeo import gdal
import sys,gc,numpy as np
from Sentiniel2Logger import Log
'''
A geophysical mask MG2 :
   - bit 0 (1) : Water mask
   - bit 1 (2) : All clouds (except the thinnests)
   - bit 2 (4) : Snow Mask
   - bit 3 (8) : all shadows ("OU" des bits 5 et 6 du masque de nuages)
   - bit 4 (16) : Topographic shadows
   - bit 5 (32) : Unseen pixels due to topography
   - bit 6 (64) : Sun too low for a correct terrain correction
   - bit 7 (128) : Sun direction tangent to slope (inaccurate terrain 
correction)
'''





class MaskClass(object):
    def __init__(self,Directory):
        self.Directory=Directory
        self.MaskDir=str(self.Directory)+'/MASKS/'+str(self.Directory).split('/')[-1]+'_MG2_R1.tif'
        self.Logger=Log(self.Directory)

    def __ReadDataFromMG2MASK(self):
        #height,Width,Projection,Geotransform
        try:
            DataSet=gdal.Open(self.MaskDir,gdal.GA_ReadOnly)        #taking readonly data
        
        except RuntimeError as e_Read:                                        #Error handling
            print(colored('Error while opening file!','red'))
            print(colored('Error Details:','blue'))
            print(e_Read)
            sys.exit(1)
    
        if(DataSet.RasterCount==1):                          
            try:
                self.__RasterBandData=DataSet.GetRasterBand(1)
                
                self.__Data=self.__RasterBandData.ReadAsArray()

                #manual cleanup
                self.__RasterBandData=None
                gc.collect()
                
            except RuntimeError as e_arr:                                   #Error handling
                print(colored('Error while data extraction file!','red'))
                print(colored('Error Details:','blue'))
                print(e_arr)
                sys.exit(1)
        else:
            print('The file contains multiple bands','red')
            sys.exit(1)
        
        DataSet=None

    def __GetDecimals(self,MaxValue,Bit):
        
        __results=[]
        
        for i in range(0,MaxValue+1):
        
            __BinaryString=format(i,'08b')
        
            if(__BinaryString[7-int(Bit)]=='1'):
        
                __results.append(i)
        
        return __results
        
    def ApplyMask(self,Bit):
        self.__ReadDataFromMG2MASK()
        self.Logger.PrintLogStatus('Getting Mask Data')                                                                               
        
        __Decimals=self.__GetDecimals(np.amax(self.__Data),int(Bit))

        MaskData=np.zeros(np.shape(self.__Data))
       
        for v in range(0,len(__Decimals)):
            MaskData[self.__Data==__Decimals[v]]=1               
        
        return MaskData        
    