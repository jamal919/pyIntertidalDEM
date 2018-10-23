# -*- coding: utf-8 -*-
import time
import numpy as np 
import time
from osgeo import gdal
from .tiffreader import TiffReader

class TiffWriter(object):

    '''
        The purpose of this class is to write Array data as Geotiff
    '''

    def __init__(self):
        __Data=None
        
    def __ProjectionAndTransfromData(self):
        '''
            GeoTiff mainly consists of three parts:
            >Projection Data
            >Geo Transformation Data
            >Raster Data(Array data/ values )
            
            According to the given datafolder, the edge mask is used to collect the Projection and geotransformation data   
        '''
        TiffReaderObj=TiffReader()
        DataSet=TiffReaderObj.ReadTiffData(self.GeoTiffDir)
        self.__Projection=DataSet.GetProjection()
        self.__GeoTransform=DataSet.GetGeoTransform()
        DataSet=None
    
    def SaveArrayToGeotiff(self,Array,Identifier,ReferenceGeoTiffDir,OutputDirectory):
        '''
            Saving array Data as geotiff
        '''
        self.OutputDir=str(OutputDirectory)+'/'                 
        
        self.GeoTiffDir=ReferenceGeoTiffDir           
    
        self.__ProjectionAndTransfromData()        # Gets projection and geotransform

        print('*Saving '+str(Identifier)+'.tiff')
        start_time=time.time()
        
        GeoTiffFileName = str(Identifier)+'.tiff'   # Output geotiff file name according to identifier
        
        Driver = gdal.GetDriverByName('GTiff')
        OutputDataset = Driver.Create(self.OutputDir+GeoTiffFileName,np.shape(Array)[0],np.shape(Array)[1], 1,gdal.GDT_Float32)
        OutputDataset.GetRasterBand(1).WriteArray(Array)
        OutputDataset.SetGeoTransform(self.__GeoTransform)
        OutputDataset.SetProjection(self.__Projection)
        OutputDataset.FlushCache()
        OutputDataset=None
        print("Elapsed Time(GeoTiff Saving): %s seconds " % (time.time() - start_time))
