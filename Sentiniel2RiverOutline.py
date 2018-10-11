#!/usr/bin/env python3
from Sentiniel2Logger import TiffReader,ViewData,Info
import matplotlib.pyplot as plt,numpy as np,argparse,time,sys,os
from osgeo import gdal
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
##Save Geotiff
def SaveArrayToGeotiff(Array,DIRGTIFF,Identifier):
   
    OutDir=str(os.getcwd())+'/'+'RiverOutLine/'
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

def main(directory,ALLDATA):
    TiffRDR=TiffReader(directory)

    InfoObj=Info(directory)
    InputDir=InfoObj.OutputDir('TIFF')
    dfile=InputDir+'3.1.5 Binary Water Map.tiff'
    print('Reading:'+str(dfile))
    Data=TiffRDR.GetTiffData(dfile)
    ALLDATA[Data==0]=0

    


if __name__=='__main__':
    TiffRDR=TiffReader(directory)
    DataPath=directory
    Zones=os.listdir(directory)
    for zone in Zones:
        DataPath=DataPath+str(zone)+'/'
        
        print('Executing River OutLine Module for zone:'+str(zone))
        
        DataFolders=os.listdir(path=DataPath)
        DirGtiff=DataPath+str(DataFolders[0])+'/'+str(DataFolders[0])+'_FRE_B8.tif'#10m resolution Size (10980,10980)
        Gtiff=TiffRDR.GetTiffData(DirGtiff)
        ALLDATA=np.ones(Gtiff.shape)
        
        for df in DataFolders:
            dirc=DataPath+df+'/'
            main(dirc,ALLDATA)

        DataPath=directory
        print('plotting data for zone:'+str(zone))
        
        plt.figure(str(zone))
        plt.title(str(zone))
        plt.imshow(ALLDATA)
        plt.show()
        plt.clf()
        plt.close()
        
        #SaveArrayToGeotiff(ALLDATA,DirGtiff,str(zone))