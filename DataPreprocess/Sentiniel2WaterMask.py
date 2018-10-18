#!/usr/bin/env python3
import time
import matplotlib
import numpy as np
import sys
import matplotlib.pyplot as plt
import os
import scipy.ndimage
from osgeo import gdal,osr
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("Dir", help="Directory of Uncompressed Data",type=str)
args = parser.parse_args()
directory=args.Dir


##Read DataSet
def ReadTiffData(File):
    '''
        Reads the Dataset
    '''
    gdal.UseExceptions()
    try:
        __DataSet=gdal.Open(File,gdal.GA_ReadOnly)        #taking readonly data
    
    except RuntimeError as e_Read:                             #Error handling
        print('Error while opening file!')
        print('Error Details:')
        print(e_Read)
        sys.exit(1)
    return __DataSet
##Read Raster Data
def GetTiffData(File):
    '''
        Returns single Raster data as array
    '''
    __DataSet=ReadTiffData(File)

    if(__DataSet.RasterCount==1):                          
        try:
            __RasterBandData=__DataSet.GetRasterBand(1)
            
            __data=__RasterBandData.ReadAsArray()
            
        except RuntimeError as e_arr:                                   #Error handling
            print('Error while data extraction file!')
            print('Error Details:')
            print(e_arr)
            sys.exit(1)
        return __data
    else:
        print('The file contains Multiple bands')
        sys.exit(1)

##Save Geotiff
def SaveArrayToGeotiff(Array,DIRGTIFF,Identifier):
    OutDir=str(os.getcwd())+'/'
    if str(Identifier).find('Zone')!=-1:
        OutDir=OutDir+'Zone/'
        if not os.path.exists(OutDir):
            os.mkdir(OutDir)
            
    if str(Identifier).find('WaterMask__FIXED')!=-1:
        OutDir=OutDir+'WaterMask__FIXED/'
        if not os.path.exists(OutDir):
            os.mkdir(OutDir)

    if str(Identifier).find('WaterMask__demistd')!=-1:
        OutDir=OutDir+'WaterMask__demistd/'
        if not os.path.exists(OutDir):
            os.mkdir(OutDir)
    
    if str(Identifier).find('Filtered')!=-1:
        OutDir=OutDir+'FinalWaterMasks/'
        if not os.path.exists(OutDir):
            os.mkdir(OutDir)
    

    print('Saving:'+str(Identifier))
    DataSet=ReadTiffData(DIRGTIFF)
    Projection=DataSet.GetProjection()
    GeoTransform=DataSet.GetGeoTransform()    
    
    GeoTiffFileName =OutDir+str(Identifier)+'.tiff'   # Output geotiff file name according to identifier
    
    Driver = gdal.GetDriverByName('GTiff')
    OutputDataset = Driver.Create(GeoTiffFileName,np.shape(Array)[0],np.shape(Array)[1], 1,gdal.GDT_Float32)
    OutputDataset.GetRasterBand(1).WriteArray(Array)
    OutputDataset.SetGeoTransform(GeoTransform)
    OutputDataset.SetProjection(Projection)
    OutputDataset.FlushCache()
    print('Saved:'+str(Identifier))

##CloudMask
def CloudMaskCorrection(BandData,MaskData):
    Decimals=GetDecimalsWithEndBit(np.amax(MaskData))
    for v in range(0,len(Decimals)):
        BandData[MaskData==Decimals[v]]=-10000                #Exclude data point Identifier= - Reflectance value
    return BandData 

def GetDecimalsWithEndBit(MaxValue):
    results=[]
    for i in range(0,MaxValue+1):
        BinaryString=format(i,'08b')
        if(BinaryString[-1]=='1'):
            results.append(i)
    return results



def ProcessAlpha(Directory):
    DirectoryStrings=str(Directory).split('/')             #split the directory to extract specific folder
        
    DirectoryStrings=list(filter(bool,DirectoryStrings))

    SWIRB11File=str(Directory)+str(DirectoryStrings[-1])+'_FRE_B11.tif'
    CloudMask20m=str(Directory)+'/MASKS/'+str(DirectoryStrings[-1])+'_CLM_R2.tif'
    print('Processing Alpha Data:'+str(DirectoryStrings[-1]))
    B11=GetTiffData(SWIRB11File)
    CLM=GetTiffData(CloudMask20m)

    B11=CloudMaskCorrection(B11,CLM)
    
    B11=np.array(B11.repeat(2,axis=0).repeat(2,axis=1))
    
    B11=B11.astype(np.float)
    
    
    iPosB11=(B11==-10000)
    
    B11[iPosB11]=np.nan
    
    B11=(B11-np.nanmin(B11))/(np.nanmax(B11)-np.nanmin(B11))
    
    
    return B11
    
def CombineZoneData(directory,Zones):    

    DataPath=directory
    
    for zone in Zones:
        DataPath=DataPath+str(zone)+'/'
        print('Executing Module for zone:'+str(zone))
        DataFolders=os.listdir(path=DataPath)
        DirGtiff=DataPath+str(DataFolders[0])+'/'+str(DataFolders[0])+'_FRE_B8.tif'#10m resolution Size (10980,10980)
        Gtiff=GetTiffData(DirGtiff)
       
        All=np.empty(Gtiff.shape)
        All=All.astype(np.float)
        All[:]  = np.nan

        Holder = np.empty((Gtiff.shape[0], Gtiff.shape[1], 2), dtype=np.float)

        for df in DataFolders:
            dirc=DataPath+df+'/'
            Alpha=ProcessAlpha(dirc)
            Holder[:, :, 0] = All
            Holder[:, :, 1] = Alpha
            All = np.nanmean(Holder, axis=-1, keepdims=False)
        
        All = (All-np.nanmin(All))/(np.nanmax(All)-np.nanmin(All))
        DataPath=directory
        SaveArrayToGeotiff(All,DirGtiff,str(zone)+'__Zone')
        
        
def FilterWaterMasks(Zones):
    Png_Dir=str(os.getcwd())+'/Analysis/Filtered/'
    if not os.path.exists(Png_Dir):
        os.mkdir(Png_Dir)
    for zone in Zones:
        print('*Executing for Zone:'+str(zone))
        ZFile=str(os.getcwd())+'/WaterMask__demistd/'+str(zone)+'__WaterMask__demistd.tiff'
        Data=GetTiffData(ZFile)
        Land=1-Data
        Thresh=5000
        LabeledData,_=scipy.ndimage.measurements.label(Land)
        _,PixelCount=np.unique(LabeledData,return_counts=True)
        __SignificantFeatures=np.argwhere(PixelCount>Thresh).ravel()
        __SignificantFeatures=__SignificantFeatures[__SignificantFeatures>0]
        for sigF in __SignificantFeatures:
            Land[LabeledData==sigF]=0
        Data[Land==1]=1
        plt.figure('0.5*STD threshold WaterMask FILTERED:'+str(zone))
        plt.title('0.5*STD threshold WaterMask FILTERED:'+str(zone))
        plt.imshow(Data)
        #plt.show()
        plt.savefig(Png_Dir+str(zone)+'__0.5STD.png')
        plt.clf()
        plt.close()
        SaveArrayToGeotiff(Data,ZFile,str(zone)+'__Filtered')
        
def CreateWaterMask(Zones,Manual_check=False,PlotHist=False):
    Png_Dir=str(os.getcwd())+'/Analysis/'
    if not os.path.exists(Png_Dir):
        os.mkdir(Png_Dir)    
    
    
    
    for zone in Zones:
        print('*Executing for Zone:'+str(zone))
        ZFile=str(os.getcwd())+'/Zone/'+str(zone)+'__Zone.tiff'
        Data=GetTiffData(ZFile)
        STDthresh=0.5*np.nanstd(Data)
        print('0.5*STD='+str(STDthresh))
        Data=Data/np.nanstd(Data)
        WM_STD=np.ones(Data.shape)
        WM_STD[Data>0.5]=0
        plt.figure('0.5*STD threshold WaterMask:'+str(zone))
        plt.title('0.5*STD threshold WaterMask:'+str(zone))
        plt.imshow(WM_STD)
        #plt.show()
        plt.savefig(Png_Dir+str(zone)+'__0.5STD.png')
        plt.clf()
        plt.close()
        if PlotHist:
            
            DrawData=GetTiffData(ZFile)
            plt.figure('Histogram of:'+str(zone))
            plt.title('Histogram of:'+str(zone))
            Value,Count=np.unique(DrawData,return_counts=True)
            Count=Count[Value<=2*np.nanmean(DrawData)]
            Value=Value[Value<=2*np.nanmean(DrawData)]
            plt.plot(Value,Count)
            plt.axvline(x=0.5*np.nanstd(DrawData))
            plt.axvline(x=np.nanmean(DrawData))
            plt.xlabel('Values')
            plt.ylabel('Count of pixels')
            plt.xticks((0.5*np.nanstd(DrawData),np.nanmean(DrawData),2*np.nanmean(DrawData),np.nanstd(DrawData)),('0.5STD','MEAN',str(2*np.nanmean(DrawData)),str(np.nanstd(DrawData))))
            plt.savefig(Png_Dir+str(zone)+'__Histogram_DPLOT.png')
            plt.clf()
            plt.close()
            
            plt.figure('Histogram of:'+str(zone))
            plt.title('Histogram of:'+str(zone))
            Value,Count=np.unique(Data,return_counts=True)
            plt.plot(Value,Count)
            
            plt.axvspan(0, 0.5*np.nanstd(Data), facecolor='#2ca02c', alpha=0.5)
            plt.xlabel('Values')
            plt.ylabel('Count of pixels')
            plt.savefig(Png_Dir+str(zone)+'__Histogram.png')
            plt.clf()
            plt.close()
            

        if Manual_check==True:
            textfile_path=str(os.getcwd())+'/Analysis/Analysis.txt'
    
            with open(textfile_path, 'a') as textfile:
                textfile.write("|ZONE            Fixed                 0.5*STD\n")
                textfile.write("|------------------------------------------------------\n")
            HData=GetTiffData(ZFile)
            sFlag='n'
            while True:
                
                WM_FIXED=np.zeros(HData.shape)
                
                fixedThresh=float(input('Max thresh for watermasking:'))
                
                WM_FIXED[HData<=fixedThresh]=1
                
                plt.figure('Fixed threshold WaterMask of Zone:'+str(zone))
                plt.title('Full Water Region:'+str(zone)+':'+str(fixedThresh))
                plt.imshow(WM_FIXED)
                plt.show()
                plt.clf()
                plt.close() 
                
                sFlag=str(input('Finalize WaterMask?(y/n)'))

                if(sFlag=='y'):
                    plt.figure('Fixed threshold WaterMask of Zone:'+str(zone))
                    plt.title('Full Water Region:'+str(zone)+':'+str(fixedThresh))
                    plt.imshow(WM_FIXED)
                    plt.savefig(Png_Dir+str(zone)+'__Final.png',bbox_inches='tight')
                    plt.clf()
                    plt.close() 
                    break
            print('Saving Fixed threshold WaterMask For:'+str(zone))
            SaveArrayToGeotiff(WM_FIXED,ZFile,str(zone)+'__WaterMask__FIXED')
            
            with open(textfile_path, 'a') as textfile:
                textfile.write('|'+str(zone)+'          '+str(fixedThresh)+'          '+str(STDthresh)+"\n")
        
        else:
            SaveArrayToGeotiff(WM_STD,ZFile,str(zone)+'__WaterMask__demistd')



if __name__=='__main__':
    Zones=os.listdir(directory)
    CombineZoneData(directory,Zones)
    CreateWaterMask(Zones)
    FilterWaterMasks(Zones)