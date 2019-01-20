# -*- coding: utf-8 -*-

#!/usr/bin/env python3

from __future__ import print_function
import os
import preprep
import utils
import improc
import vertref
import time 
from memory_profiler import profile


# Paramters
## Vertref
indatadir = '/run/media/khan/Sentinel2/RawData' # Directoty of Zipped Data
outputdir = '/run/media/khan/Sentinel2/Analysis' # Directory Containing outputs
wkdir = os.path.join(outputdir, 'Data') # Directory of saving unzipped data
prepdir = os.path.join(outputdir, 'PreProcessing') # Directory of saving preprocessed data   
improcdir = os.path.join(outputdir, 'ShorelineExtraction') # Directory of saving processed data 
vertrefdir = os.path.join(outputdir, 'VerticalReferencing') # Saving Intermediate data for vertical referencing
waterleveldir = os.path.join(outputdir, 'WaterLevels') # Directory of water level dat files

## Preprocessing Optional Params
stdfactor = 0.5 # Threshold for watermask , data[data>factor*std]=Land (Float) 
MaskWater = 10000 # Water Mask creation water blob removal threshold 
MaskLand = 5000 # Water Mask creation land blob removal threshold
additionalDirectory = None # Specialized testing Directory for watermask

## processing Optional params
hue_channel_scaling_factor = 0.4 # Scaling Factor of hue for median thresholding
value_channel_scaling_factor = 5.0 # Scaling Factor of Value for median thresholding
blob_removal_land = 10000 # Binary water map blob removal size for land features
blob_removal_Water = 50000 # Binary water map blob removal size for water features

## Boolean Params of png saving
prepWmaskPNGflag = False                                              # Save png for Water mask creation  (True/False)
procChannelPNGflag = False                                            # Save png while channel construction (True/False)
procWaterMapPngFlag = False                                           # Save png while binary water map creation (True/False)
procblobRemovalpngFlag = False                                        # Save png while filtering water maps

# Selections of files to be used
DeltaicZones = ['T45QWE', 'T45QXE', 'T45QYE', 'T46QBK', 'T46QCK','T46QBL', 'T46QCL']

# Worker functions
def CreateOuputDirs(prepdir,improcdir,vertrefdir):
    for dloc in [prepdir, improcdir, vertrefdir]:
        if not os.path.exists(dloc):
            os.mkdir(dloc)

def Preprocessing():
    start_time = time.time()
    preprep.ingest(indatadir, wkdir)
    preprep.genstat(wkdir,prepdir)
    preprep.genmask(wkdir,prepdir,dir=additionalDirectory,nstd=stdfactor,water=MaskWater,land=MaskLand,png=prepWmaskPNGflag)
    print('Total elapsed time:', str(time.time()-start_time))

def ShorelineProcessing():
    DataPath = wkdir
    Zones=os.listdir(wkdir)
    
    for zone in Zones:
        DataPath=str(os.path.join(wkdir,zone,''))
        DataFolders=os.listdir(DataPath)

        for df in DataFolders:
            directory=str(os.path.join(DataPath,df,''))

            if zone in DeltaicZones:
                improc.remove_blob(directory,improcdir,prepdir,nwater=blob_removal_Water,nland=blob_removal_land,png=procblobRemovalpngFlag)
                improc.extract_shoreline(directory,improcdir,prepdir)
                improc.construct_channels(directory,improcdir,prepdir,png=procChannelPNGflag)
                improc.make_watermap(directory,improcdir,prepdir,nhue=hue_channel_scaling_factor,nvalue=value_channel_scaling_factor,png=procWaterMapPngFlag)

def SingleDataProcess(directory,improcdir,prepdir):
    start_time=time.time()
    improc.construct_channels(directory,improcdir,prepdir,png=procChannelPNGflag)
    improc.make_watermap(directory,improcdir,prepdir,nhue=hue_channel_scaling_factor,nvalue=value_channel_scaling_factor,png=procWaterMapPngFlag)
    improc.remove_blob(directory,improcdir,prepdir,nwater=blob_removal_Water,nland=blob_removal_land,png=procblobRemovalpngFlag)
    improc.extract_shoreline(directory,improcdir,prepdir)
    print('Total elapsed time:',str(time.time()-start_time))


def VerticalReferencing():
    vertref.set_water_levels(shorelinedir=improcdir, waterleveldir=waterleveldir, vertrefdir=vertref)

if __name__=='__main__':
    CreateOuputDirs(prepdir, improcdir, vertrefdir)
    Preprocessing()
    ShorelineProcessing()
    VerticalReferencing()
    