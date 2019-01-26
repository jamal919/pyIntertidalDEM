# -*- coding: utf-8 -*-
'''
Prepartion of Spaceborne spectral images for analysis. 

Author: khan
Email: jamal.khan@legos.obs-mip.fr
'''
import numpy as np
import scipy
import scipy.ndimage.measurements
import matplotlib.pyplot as plt
from glob import glob
import zipfile
import calendar
import time
import os

from .utilities import TiffReader
from .utilities import TiffWriter
from .utilities import DataPlotter

class DataExtractor(object):
    def __init__(self, input_dir, output_dir):
        '''
        DataExtractor Class implements the functionality to discover data in 
        a directory and extract them to a target directory arranged by the tiles.
        '''
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.zones = dict()
        
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

    def list_zones(self, debug=False):
        for fname in glob(os.path.join(self.input_dir, '**', '*.zip'), recursive=True):
            basename = os.path.basename(fname).replace('.zip', '')
            zone = basename.split('_')[3]
            
            try:
                assert zone in self.zones
            except AssertionError:
                self.zones[zone] = []
            finally:
                self.zones[zone].append(fname)
        
        if debug:
            # Number of zones
            if len(self.zones) <= 1:
                print('We have found {:d} zone'.format(len(self.zones)))
            else:
                print('We have found {:d} zone(s)'.format(len(self.zones)))

            # Zone wise tile number
            for zone in self.zones:
                print('- {:s} : {:d} tiles'.format(zone, len(self.zones[zone])))
            
    def extract(self, zone):
        try:
            assert zone in self.zones
        except AssertionError:
            print('{:s} - Not found! Use list_zones method to list all tiles.'.format(zone))
        else:
            zone_dir = os.path.join(self.output_dir, zone)
            print('|- Extracting {:d} {:s} tiles to - {:s}'.format(len(self.zones[zone]), zone, zone_dir))
            
            if not os.path.exists(zone_dir):
                os.mkdir(zone_dir)

            for fname in self.zones[zone]:
                start_time = time.time()
                zfile = zipfile.ZipFile(file=fname)
                zfile.extractall(zone_dir)
                zfile.close()
                print('\t|- Extracted : {zone_name:s} - {file_name:s} in {te:s}'.format(
                    zone_name=zone,
                    file_name=os.path.basename(fname),
                    te=str(time.time()-start_time)
                ))

class Stat(object):
    def __init__(self, data_dir, prep_dir):
        self.zone_dir = data_dir
        self.stat_dir = os.path.join(prep_dir, 'Statistics')
        
        if not os.path.exists(self.stat_dir):
            os.mkdir(self.stat_dir)

    def plot_sampling(self, zones):
        ticks = [calendar.month_abbr[i] for i in range(1, 13)]
        xt = [str(i) for i in range(1, 32)]

        _save_dir = os.path.join(self.stat_dir, 'DataAcquisition')
        if not os.path.exists(_save_dir):
            os.mkdir(_save_dir)

        for zone in zones:
            data_count = np.zeros((12,31))
            data_path = os.path.join(self.zone_dir, str(zone))
            
            print('Counting Data for zone:'+str(zone))
            
            data_tiles = os.listdir(data_path)
            data_tiles_count = str(len(data_tiles))
            
            for data_tile in data_tiles:
                tile_id = str(data_tile).split('_')
                tile_time = tile_id[1].split('-')
                tile_month = int(tile_time[0][4:6])
                tile_day=int(tile_time[0][6:])
                
                data_count[tile_month-1][tile_day-1] +=1
           
            y_pos = np.arange(12)
           
            fig, ax = plt.subplots(figsize=(6, 5), dpi=120, tight_layout=True)
           
            ax.set_title('Zone:'+str(zone)+'\n Total data:'+ data_tiles_count)
            im = ax.imshow(data_count)
            fig.colorbar(im, ax=ax, orientation='horizontal')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(ticks)
            ax.set_xticks(np.arange(31))
            ax.set_xticklabels(xt)
            
            plt.savefig(os.path.join(_save_dir, str(zone)+'.png'))
            plt.clf()
            plt.close()

class WaterMask(object):
    def __init__(self, data_dir, prep_dir, nstd_threshold, water_blob_size, land_blob_size, pngdir=None):
        self.Directory=data_dir
        self.OutPutDir=os.path.join(prep_dir, 'Masks')
        self.factor=nstd_threshold
        self.TiffReader=TiffReader()
        self.WaterSize=water_blob_size
        self.LandSize=land_blob_size
        self.TiffWriter=TiffWriter()
        self.SavePNG=False
        if pngdir !=None:
            self.SavePNG=True
            self.PNGDir=pngdir

    def __CloudMaskCorrection(self,BandData,MaskData):
        Decimals=self.__GetDecimalsWithEndBit(np.amax(MaskData))
        for v in range(0,len(Decimals)):
            BandData[MaskData==Decimals[v]]=-10000
        return BandData 

   
    def __GetDecimalsWithEndBit(self,MaxValue):
        results=[]
        for i in range(0,MaxValue+1):
            BinaryString=format(i,'08b')
            if(BinaryString[-1]=='1'):
                results.append(i)
        return results
    
    def __ProcessAlpha(self,Directory):
        DirectoryStrings=str(Directory).split('/')
        DirectoryStrings=list(filter(bool,DirectoryStrings))
        
        SWIRB11File=str(os.path.join(Directory,str(DirectoryStrings[-1])+'_FRE_B11.tif'))  
        CloudMask20m=str(os.path.join(Directory,'MASKS',str(DirectoryStrings[-1])+'_CLM_R2.tif'))
       
        print('\t|- {:s}'.format(DirectoryStrings[-1]))
        
        B11=self.TiffReader.GetTiffData(SWIRB11File)
        CLM=self.TiffReader.GetTiffData(CloudMask20m)

        B11=self.__CloudMaskCorrection(B11,CLM)
        B11=np.array(B11.repeat(2,axis=0).repeat(2,axis=1))
        B11=B11.astype(np.float)
        
        
        iPosB11=(B11==-10000)
        B11[iPosB11]=np.nan
        B11=(B11-np.nanmin(B11))/(np.nanmax(B11)-np.nanmin(B11))
        return B11

    def __CombineAlpha(self, zone):
       
        DataPath=os.path.join(self.Directory, str(zone))
      
        DataFolders=os.listdir(DataPath)
        
        self.DirGtiff=str(os.path.join(DataPath,str(DataFolders[0]),str(DataFolders[0])+'_FRE_B8.tif'))
        #10m resolution Size (10980,10980)
        Gtiff=self.TiffReader.GetTiffData(self.DirGtiff)
        All=np.empty(Gtiff.shape)
        All=All.astype(np.float)
        All[:]  = np.nan
        Holder = np.empty((Gtiff.shape[0], Gtiff.shape[1], 2), dtype=np.float)
        for df in DataFolders:
            dirc=os.path.join(DataPath,df)
            Alpha=self.__ProcessAlpha(str(dirc))
            Holder[:, :, 0] = All
            Holder[:, :, 1] = Alpha
            All = np.nanmean(Holder, axis=-1, keepdims=False)
        
        All = (All-np.nanmin(All))/(np.nanmax(All)-np.nanmin(All))

        All=All/np.nanstd(All)
        WM_STD=np.ones(All.shape)
        WM_STD[All>self.factor]=0
        return WM_STD

    def __FilterWaterMask(self,Data):
       
        WF=np.zeros(Data.shape)
        #WaterFilter
        Thresh=int(self.WaterSize)
        LabeledData,_=scipy.ndimage.measurements.label(Data)
        _,PixelCount=np.unique(LabeledData,return_counts=True)
        __SignificantFeatures=np.argwhere(PixelCount>Thresh).ravel()
        __SignificantFeatures=__SignificantFeatures[__SignificantFeatures>0]
        
        for sigF in __SignificantFeatures:
            WF[LabeledData==sigF]=1
        #LandFilter
        Land=1-WF
        Thresh=int(self.LandSize)
        LabeledData,_=scipy.ndimage.measurements.label(Land)
        _,PixelCount=np.unique(LabeledData,return_counts=True)
        __SignificantFeatures=np.argwhere(PixelCount>Thresh).ravel()
        __SignificantFeatures=__SignificantFeatures[__SignificantFeatures>0]
        for sigF in __SignificantFeatures:
            Land[LabeledData==sigF]=0
        
        WF[Land==1]=1
        self.TiffWriter.SaveArrayToGeotiff(WF,self.Identifier,self.DirGtiff,self.OutPutDir)
        
        if self.SavePNG:
            Ref = os.path.join(self.OutPutDir,str(self.Identifier)+'.tiff')
            DataPlotterOBJ = DataPlotter(str(Ref),self.PNGDir)
            DataPlotterOBJ.PlotWithGeoRef(WF,self.Identifier)
            DataPlotterOBJ.plotInMap(WF,self.Identifier)

    def generate(self, zones):
        for zone in zones:
            self.Identifier=str(zone)
            print('* Mask Generation - Zone: {:s}'.format(zone))
            Data = self.__CombineAlpha(zone)
            self.__FilterWaterMask(Data)
