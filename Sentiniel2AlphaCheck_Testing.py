import time,matplotlib,numpy as np,gc,sys,matplotlib.pyplot as plt,os
from osgeo import gdal
from Sentiniel2Logger import TiffReader,TiffWritter,ViewData,Info
class Test_Processor(object):
    '''
        Process the Hue and Value channel to construct a binary waterMap
    '''
    def __init__(self,Directory):
        __InfoObj=Info(Directory)
        self.__InputFolder=__InfoObj.OutputDir('TIFF')
        
        self.OUTdir=__InfoObj.OutputDir('PNG')

        self.DataViewer=ViewData(Directory)
        self.Directory=Directory
        self.TiffReader=TiffReader(Directory)
        self.TiffWritter=TiffWritter(Directory)
       
     ##Saving Necessary Results

    def __SaveChannelData(self,Data,Identifier,SaveGeoTiff=False,SaveDIR=None):
        '''
            Save's the Channel data as TIFF and PNG
        '''
        if SaveDIR is None:
            self.DataViewer.PlotWithGeoRef(Data,str(Identifier))
        else:
            self.DataViewer.PlotWithGeoRef(Data,str(Identifier),TestSaveDir=str(SaveDIR))
        
        if(SaveGeoTiff==True):
            self.TiffWritter.SaveArrayToGeotiff(Data,str(Identifier))

    def __PlotHistogramOfAlpha(self):
        print('Getting Alpha Channel')
        __File=self.__InputFolder+"1.1.3 Alpha Band N.tiff"
        
        Alpha=self.TiffReader.GetTiffData(__File)
        
        
        
        Value,Count= np.unique(Alpha, return_counts=True)
        
        Vl=np.nanmin(Value)
        
        Vh=np.nanmax(Value)
        
        V=np.linspace(Vl,Vh,10,endpoint=True)

        Cl=np.nanmin(Count)

        Ch=np.nanmax(Count)
        
        C=np.linspace(Cl,Ch,10,endpoint=True)

        plt.figure('Alpha Histogram of values')
            
        plt.title('Alpha Histogram of values')
        
        plt.grid(True)

        plt.xticks(V)

        plt.yticks(C)
        
        plt.xlabel('Normalized Values')
        
        plt.ylabel('Value Count')
        
        plt.plot(Value,Count)

        plt.savefig(self.OUTdir+'Test_0_CompleteAlphaHistogram.png')

        #clear memory
        plt.clf()
        
        plt.close()

        STD=np.nanstd(Alpha)
        iSTD=(Value<=1.1*STD) & ~np.isnan(Value)
        Count=Count[iSTD]
        Value=Value[iSTD]

        V=np.linspace(0,1.1*STD,11,endpoint=True)
        Cl=np.nanmin(Count)
        Ch=np.nanmax(Count)
        C=np.linspace(Cl,Ch,10,endpoint=True)

        Vlbl=[]
        Vlbl.append('0')
        for i in range(1,10):
            vstr='0.'+str(i)+' S'
            Vlbl.append(str(vstr))
        Vlbl.append('S')

        plt.figure('Alpha Histogram of STD values')
            
        plt.title('Alpha Histogram of STD values')
        
        plt.grid(True)

        plt.xticks(V,Vlbl)

        plt.yticks(C)
        
        plt.xlabel('Normalized STD Values')
        
        plt.ylabel('Value Count (STD)')
        
        plt.plot(Value,Count)

        plt.savefig(self.OUTdir+'Test_0_STDAlphaHistogram.png')

        #clear memory
        plt.clf()
        
        plt.close()

    def __LoadHueValue(self):
        '''
            Reading Saved data and forming a data mask from Alpha Data
        '''
        
        print('Getting Value Data')
        __File=self.__InputFolder+"2.2.2 Value Normalized Pekel.tiff"
        self.Value=self.TiffReader.GetTiffData(__File)
        
        print('Getting Hue Data')
        __File=self.__InputFolder+"2.2.1_HUE_Normalized_Pekel.tiff"
        self.Hue=self.TiffReader.GetTiffData(__File)
        
    def __CreateWaterMask(self,Div): 
        '''
            A thresh hold is selected for which Alpha is clipped to 0 to form a water mask
        '''   
        print('Getting Alpha Channel')
        __File=self.__InputFolder+"1.1.3 Alpha Band N.tiff"
        Alpha=self.TiffReader.GetTiffData(__File)
        
        
        print('Creating WaterMask')
        self.iNan=np.isnan(Alpha)

        self.WaterMask=np.zeros(Alpha.shape)
        
        self.WaterMask[Alpha<(np.nanstd(Alpha)*Div)]=1  ##Changeable
        
        self.WaterMask[self.iNan]=np.nan
        
        self.DIVStd=Div

        self.TestSavePNGDir=self.OUTdir+'STD_Scale_'+str(self.DIVStd)+'/'
        
        if not os.path.exists(self.TestSavePNGDir):
            os.mkdir(self.TestSavePNGDir)

        self.__SaveChannelData(self.WaterMask,'Test__STD_'+str(self.DIVStd)+'_3.1.0 Water Mask__ThreshValue='+str((np.nanstd(Alpha)*Div)),SaveDIR=self.TestSavePNGDir)

       



    def __MaskHueValue(self):
        print('Masking Value Channel with water mask')
        self.Value[self.WaterMask==0]=np.nan
        self.__SaveChannelData(self.Value,'Test__STD_'+str(self.DIVStd)+'_3.1.1 Masked Value Channel',SaveDIR=self.TestSavePNGDir)

        print('Inverse Masking Value Channel with water mask')
        self.Hue[self.WaterMask==1]=np.nan
        self.__SaveChannelData(self.Hue,'Test__STD_'+str(self.DIVStd)+'_3.1.3 Inversed Masked Hue Channel',SaveDIR=self.TestSavePNGDir)

    
    
    def __FormBinaryWaterValueChannel(self):
        '''
            BW_value is formed as:
            
            BW_value=(I_value (i, j) < T value + n value . σ value ) ∧ (I value (i, j) > T value − n value . σ value )

            Here I_value= Water Mask applied Value channel
               T_value is Median of I_value 
               S_value is standard deviation of I_value
        '''
        print('Calculating Binary Water Value Channel')
        T=np.nanmedian(self.Value)     #Median 
        S=np.nanstd(self.Value)      #standard deviation
        
        n=5                            #Scaling Factor

        #Value channel conditional constant 
        c1=T+n*S
        c2=T-n*S

        print('T='+str(T)+'   S='+str(S)+'     n='+str(n)+'     c1='+str(c1)+'        c2='+str(c2))

        self.BW_Value=np.zeros(self.Value.shape)
        self.BW_Value[(self.Value<c1) & (self.Value>c2) ]=1
        
        self.BW_Value=self.BW_Value.astype(np.float)
        self.BW_Value[self.iNan]=np.nan
        
        self.__SaveChannelData(self.BW_Value,'Test__STD_'+str(self.DIVStd)+'_3.1.2 Binary Water Value Channel_SF='+str(n),SaveDIR=self.TestSavePNGDir)
    
    
    
    def __FormBinaryWaterHueChannel(self,SF):
        
        '''
            BW_hue is formed as:
            
            BW_hue=¬((I hue (i, j) < T hue + n hue . σ hue ) ∧ (I hue (i, j) > T hue − n hue . σ hue ))

            Here I hue= Inverse Water Mask applied Hue channel
               T hue is Median of I Hue 
               S hue is standard deviation of I HUe
        '''
        print('Calculating Binary Water Hue Channel')
        T=np.nanmedian(self.Hue)       #Median 
        S=np.nanstd(self.Hue)          #standard deviation
        
        n=SF 
        self.SFn=SF                           #Scaling Factor

        #Value channel conditional constant 
        c1=T+n*S
        c2=T-n*S

        print('T='+str(T)+'   S='+str(S)+'     n='+str(n)+'     c1='+str(c1)+'        c2='+str(c2))

        self.BW_Hue=np.ones(self.Hue.shape)
        self.BW_Hue[(self.Hue<c1) & (self.Hue>c2) ]=0
        
        self.BW_Hue=self.BW_Hue.astype(np.float)
        self.BW_Hue[self.iNan]=np.nan
        
        self.__SaveChannelData(self.BW_Hue,'Test__STD_'+str(self.DIVStd)+'__SF='+str(n)+'_3.1.4 Binary Water Hue Channel',SaveDIR=self.TestSavePNGDir)
        
    def __AndOperationWaterMap(self):
        IsWater=np.zeros(self.BW_Hue.shape)

        IsWater[(self.BW_Hue==1) & (self.BW_Value==1)]=1
        IsWater=IsWater.astype(np.float)
        IsWater[self.iNan]=np.nan
        
        self.__SaveChannelData(IsWater,'Test__STD_'+str(self.DIVStd)+'__SF='+str(self.SFn)+'_3.1.5 Binary Water Map',SaveDIR=self.TestSavePNGDir)        
        
        
    def GetBinaryWaterMap(self):
        '''
            Produce the binary water map as follows
            > Load Hue and Value Channel Data
            > Create Water Map from Alpha Channel
            > Mask Value Inverse Mask Hue
            > Binary Value Water 
            > Birany Hue Water
            > And operation
        '''
        #self.__PlotHistogramOfAlpha()
        
        self.__LoadHueValue()
        WSF=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]
        for sc in WSF:
            self.__CreateWaterMask(sc)
            self.__MaskHueValue()
            self.__FormBinaryWaterValueChannel()
            SF=[0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.1,1.2,1.3,1.4,1.5]
            for sf in SF: 
                self.__FormBinaryWaterHueChannel(sf)
                self.__AndOperationWaterMap()
        