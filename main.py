# -*- coding: utf-8 -*-
import os
import preprep
import utils
import improc

##-----------------------------------------------------------------------------------------------------------
indatadir = '/media/ansary/PMAISONGDE/none at the moment/'          # Directoty of Zipped Data
wkdir = '/media/ansary/PMAISONGDE/Data/'                            # Directory of saving unzipped data
prepdir='/media/ansary/PMAISONGDE/'                                 # Directory of saving preprocessed data   
improcdir='/media/ansary/PMAISONGDE/'                               # Directory of saving processed data 

#Preprocessing Optional Params
stdfactor=0.5                                                       # Threshold for watermask , data[data>factor*std]=Land (Float) 
MaskWater=10000                                                     # Water Mask creation water blob removal threshold 
MaskLand=5000                                                       # Water Mask creation land blob removal threshold
additionalDirectory=None                                            # Specialized testing Directory for watermask

#processing Optional params
hue_channel_scaling_factor=0.4                                      # Scaling Factor of hue for median thresholding
value_channel_scaling_factor=5.0                                    # Scaling Factor of Value for median thresholding
blob_removal_land=10000                                             # Binary water map blob removal size for land features
blob_removal_Water=50000                                            # Binary water map blob removal size for water features

#Boolean Params of png saving
prepWmaskPNGflag=True                                               # Save png for Water mask creation  (True/False)

procChannelPNGflag=False                                            # Save png while channel construction (True/False)
procWaterMapPngFlag=False                                           # Save png while binary water map creation (True/False)
procblobRemovalpngFlag=False                                        # Save png while filtering water maps

##---------------------------------------------------------------------------------------------------------------------------------




# Preprocessing directory creation
prepdir = os.path.join(prepdir, 'PreProcessed','')
if not os.path.exists(prepdir):
    os.mkdir(prepdir)
#ImageProcessing directory creation
improcdir = os.path.join(improcdir, 'ProcessedData')
if not os.path.exists(improcdir):
    os.mkdir(improcdir)


def preprocessing():
    #preprep.ingest(indatadir, wkdir)
    #preprep.genstat(...)
    preprep.genmask(wkdir,prepdir,dir=additionalDirectory,nstd=stdfactor,water=MaskWater,land=MaskLand,png=prepWmaskPNGflag)
    
def processing():
    DataPath=wkdir
    Zones=os.listdir(wkdir)
    Zones=['T45QXE','T45QWE']
    for zone in Zones:
        DataPath=str(os.path.join(wkdir,zone,''))
        DataFolders=os.listdir(DataPath)
        for df in DataFolders:
            directory=str(os.path.join(DataPath,df,''))

            improc.construct_channels(directory,improcdir,prepdir,png=procChannelPNGflag)
            improc.make_watermap(directory,improcdir,prepdir,nhue=hue_channel_scaling_factor,nvalue=value_channel_scaling_factor,png=procWaterMapPngFlag)
            improc.remove_blob(directory,improcdir,prepdir,nwater=blob_removal_Water,nland=blob_removal_land,png=procblobRemovalpngFlag)
            improc.extract_shoreline(directory,improcdir,prepdir)

if __name__=='__main__':
    preprocessing()
    #processing()








