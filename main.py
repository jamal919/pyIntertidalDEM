# -*- coding: utf-8 -*-
import os
import preprep
import utils
import improc

indatadir = '/media/ansary/PMAISONGDE/none at the moment/'
wkdir = '/media/ansary/PMAISONGDE/Data/'
prepdir='/media/ansary/PMAISONGDE/'
improcdir='/media/ansary/PMAISONGDE/'


# Preprocessing
#prepdir = os.path.join(prepdir, 'PreProcessed','')
#if not os.path.exists(prepdir):
#    os.mkdir(prepdir)

#preprep.ingest(indatadir, wkdir)
#preprep.genstat(...)
#preprep.genmask(wkdir,prepdir,dir='DEMISTD_10k_5K',nstd=0.5,water=10000,land=5000,png=True)

#ImageProcessing
improcdir = os.path.join(improcdir, 'ProcessedData')
if not os.path.exists(improcdir):
    os.mkdir(improcdir)

DataPath=wkdir
Zones=os.listdir(wkdir)
Zones=['T45QXE','T45QWE']
for zone in Zones:
    DataPath=str(os.path.join(wkdir,zone,''))
    DataFolders=os.listdir(DataPath)
    for df in DataFolders:
        directory=str(os.path.join(DataPath,df,''))

        improc.construct_channels(directory,improcdir, png=True)
        #improc.make_watermap(nhue=0.4,nvalue=5.0,png=True)
        #improc.remove_blob(nwater=50000,nland=10000,png=True)
        #improc.extract_shoreline()










#utils testing
#dirc='/media/ansary/PMAISONGDE/Data/T45QYE/SENTINEL2B_20180512-043429-820_L2A_T45QYE_D_V1-7/' 
#Dfile='/media/ansary/PMAISONGDE/Data/T45QYE/SENTINEL2B_20180512-043429-820_L2A_T45QYE_D_V1-7/SENTINEL2B_20180512-043429-820_L2A_T45QYE_D_V1-7_FRE_B8.tif'

#utils.infotest(dirc)
#utils.TiffReaderTest(Dfile)
#utils.TiffWriterTest()
#utils.PlottingTest()