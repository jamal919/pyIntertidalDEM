from Sentiniel2TiffData import TiffReader,TiffWritter,NoData
import numpy as np,sys 

class BandData(object):
    def __init__(self,Files,Directory):
        self.__RedBandFile=Files[1]
        self.__GreenBandFile=Files[2]
        self.__BlueBandFile=Files[0]
        self.__AlphaBandFile=Files[3]
        self.__CloudMask10mFile=Files[4]
        self.__CloudMask20mFile=Files[5]
        self.Directory=Directory
        self.TiffReader=TiffReader(self.Directory)
        self.TiffWritter=TiffWritter(self.Directory)
    
    def __GetDecimalsWithEndBit(self,MaxValue):
        
        __results=[]
        
        for i in range(0,MaxValue+1):
        
            __BinaryString=format(i,'08b')
        
            if(__BinaryString[-1]=='1'):
        
                __results.append(i)
        
        return __results
        
    def __CloudMaskCorrection(self,BandData,MaskData,Identifier):
        
        print('Processing Cloud Mask With:'+Identifier)                                                                               
        
        __Decimals=self.__GetDecimalsWithEndBit(np.amax(MaskData))

        for v in range(0,len(__Decimals)):
            BandData[MaskData==__Decimals[v]]=-10000                #Exclude data point Identifier= - Reflectance value
        
        return BandData 
    
    def __AlphaUpSampling(self):
        self.__AlphaBand=np.array(self.__AlphaBand.repeat(2,axis=0).repeat(2,axis=1))

    def __ProcessAlphaChannel(self):
        
        self.__AlphaBand=self.TiffReader.GetTiffData(self.__AlphaBandFile) #Read
        
        __CloudMask20m=self.TiffReader.GetTiffData(self.__CloudMask20mFile) #CloudMask
        
        self.__AlphaBand=self.__CloudMaskCorrection(self.__AlphaBand,__CloudMask20m,'Alpha Band 20m')
        
        self.__AlphaBand[self.__AlphaBand==-10000]=0                       #No Data Correction
        
        self.__AlphaBand=(self.__AlphaBand/np.amax(self.__AlphaBand))*255  #0-255 
        
        self.__AlphaBand=self.__AlphaBand.astype(np.uint8)                 #8 bit integer
        
        
        self.__AlphaUpSampling()
        
        print(sys.getsizeof(self.__AlphaBand)/(2**30))
        
    def __ProcessRedChannel(self):
        __RedBand=self.TiffReader.GetTiffData(self.__RedBandFile)  #Read

        __CloudMask10m=self.TiffReader.GetTiffData(self.__CloudMask10mFile) #CloudMask
        
        __RedBand=self.__CloudMaskCorrection(__RedBand,__CloudMask10m,'Red Band 10m')
        
        __RedBand[__RedBand==-10000]=0                       #No Data Correction
        
        __RedBand=(__RedBand/np.amax(__RedBand))*255  #0-255 
        
        __RedBand=__RedBand.astype(np.uint8)                 #8 bit integer

        __RedBand=(255-self.__AlphaBand)+(self.__AlphaBand*__RedBand)
        
        self.TiffWritter.SaveArrayToGeotiff(__RedBand,'Red Channel')

        print(sys.getsizeof(__RedBand)/(2**30))
              
    def __ProcessGreenChannel(self):
        __GreenBand=self.TiffReader.GetTiffData(self.__GreenBandFile)  #Read

        __CloudMask10m=self.TiffReader.GetTiffData(self.__CloudMask10mFile) #CloudMask
        
        __GreenBand=self.__CloudMaskCorrection(__GreenBand,__CloudMask10m,'Green Band 10m')
        
        __GreenBand[__GreenBand==-10000]=0                       #No Data Correction
        
        __GreenBand=(__GreenBand/np.amax(__GreenBand))*255  #0-255 
        
        __GreenBand=__GreenBand.astype(np.uint8)                 #8 bit integer

        __GreenBand=(255-self.__AlphaBand)+(self.__AlphaBand*__GreenBand)
        
        self.TiffWritter.SaveArrayToGeotiff(__GreenBand,'Green Channel')

        print(sys.getsizeof(__GreenBand)/(2**30))
        
    def __ProcessBlueChannel(self):
        __BlueBand=self.TiffReader.GetTiffData(self.__BlueBandFile)  #Read

        __CloudMask10m=self.TiffReader.GetTiffData(self.__CloudMask10mFile) #CloudMask
        
        __BlueBand=self.__CloudMaskCorrection(__BlueBand,__CloudMask10m,'Blue Band 10m')
        
        __BlueBand[__BlueBand==-10000]=0                       #No Data Correction
        
        __BlueBand=(__BlueBand/np.amax(__BlueBand))*255  #0-255 
        
        __BlueBand=__BlueBand.astype(np.uint8)                 #8 bit integer

        __BlueBand=(255-self.__AlphaBand)+(self.__AlphaBand*__BlueBand)
        
        self.TiffWritter.SaveArrayToGeotiff(__BlueBand,'Blue Channel')

        print(sys.getsizeof(__BlueBand)/(2**30))
        
    def Data(self):
        self.__ProcessAlphaChannel()
        self.__ProcessRedChannel()
        self.__ProcessGreenChannel()
        self.__ProcessBlueChannel()

    