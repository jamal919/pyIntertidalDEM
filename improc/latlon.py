# -*- coding: utf-8 -*-
from __future__ import print_function
from utils.information import Info
from utils.tiffreader import TiffReader


from osgeo import gdal,osr
import numpy as np 
import scipy.signal
import time
import gc 
import csv
class GeoData(object):

    def __init__(self,directory,improcdir,preprocdir):
        self.__InfoObj=Info(directory)
        self.__InfoObj.DefineDiectoriesAndReferences(improcdir,preprocdir)
       
        __InputFolder=self.__InfoObj.MainDir
        __WaterMapFile=__InputFolder+'/4.1.1_WaterMap.tiff'
        Reader=TiffReader()
        self.DateTime=self.__InfoObj.DateTime
       
        self.MapWater=Reader.GetTiffData(__WaterMapFile)

        __NoDataFile=self.__InfoObj.ReferenceGeotiff
        __DataSet=Reader.ReadTiffData(__NoDataFile)
        self.GeoTransForm=__DataSet.GetGeoTransform()
        self.Projection=__DataSet.GetProjection()
        __DataSet=None
        
    
        

    def __ConvolutedMap(self):
        print('Mapping ShoreLine')
        [self.__row,self.__col]=np.shape(self.MapWater)
        start_time = time.time()
        __Kernel=np.array([[0,-1,0],[-1,4,-1],[0,-1,0]])
        __ConvolutedData=scipy.signal.convolve2d(self.MapWater[1:self.__row-1,1:self.__col-1],__Kernel)
        __ConvolutedData[__ConvolutedData<=0]=np.nan
        __ConvolutedData[__ConvolutedData>0]=1
        
        

        self.__Map_ShoreLine=np.argwhere(__ConvolutedData==1)                                              #change this condition for testing
        self.__TotalDataPoints=np.shape(self.__Map_ShoreLine)[0]
        #Cleanup
        __ConvolutedData=None
        gc.collect()
        print("Total Elapsed Time(Convolution): %s seconds " % (time.time() - start_time))
    
    def __PixelToSpaceCoordinate(self):
        [__x_offset,__pixel_width,__rotation_1,__y_offset,__rotation_2,__pixel_height]=self.GeoTransForm
        __pixel_Coordinate_X=self.__Map_ShoreLine[:,1]
        __pixel_Coordinate_y=self.__Map_ShoreLine[:,0]
        self.__Space_coordinate_X= __pixel_width * __pixel_Coordinate_X +   __rotation_1 * __pixel_Coordinate_y + __x_offset
        self.__Space_coordinate_Y= __rotation_2* __pixel_Coordinate_X +    __pixel_height* __pixel_Coordinate_y + __y_offset
        #shift to the center of the pixel
        self.__Space_coordinate_X +=__pixel_width  / 2.0
        self.__Space_coordinate_Y +=__pixel_height / 2.0
    
    def __SpaceCoordinateToLatLon(self):
        start_time=time.time()
        ##get CRS from dataset
        __Coordinate_Reference_System=osr.SpatialReference()                     #Get Co-ordinate reference
        __Coordinate_Reference_System.ImportFromWkt(self.Projection)             #projection reference

        ## create lat/long CRS with WGS84 datum<GDALINFO for details>
        __Coordinate_Reference_System_GEO=osr.SpatialReference()
        __Coordinate_Reference_System_GEO.ImportFromEPSG(4326)                   # 4326 is the EPSG id of lat/long CRS

        __Transform_term = osr.CoordinateTransformation(__Coordinate_Reference_System, __Coordinate_Reference_System_GEO)
        self.__LatitudeData=np.zeros(self.__TotalDataPoints)
        self.__LongitudeData=np.zeros(self.__TotalDataPoints)
        for indice in range(0,self.__TotalDataPoints):
            (__latitude_point, __longitude_point, _ ) = __Transform_term.TransformPoint(self.__Space_coordinate_X[indice], self.__Space_coordinate_Y[indice])
            
            self.__LatitudeData[indice]=__latitude_point
            self.__LongitudeData[indice]=__longitude_point
        print('')
        print("Total Elapsed Time(SpaceCoords to Lat Lon): %s seconds " % (time.time() - start_time))

    def __SaveDataAsCSV(self,Data):
        '''
            Saves Lat Lon Data as CSV in a Given Format
        '''
        start_time=time.time()
        Identifier=self.__InfoObj.DateTime
        print('Saving '+str(Identifier)+'.csv')
        csvfile=self.__InfoObj.MainDir+'5.0.'+str(Identifier)+'.csv'
        with open(csvfile,"w") as output:
            writer=csv.writer(output,lineterminator='\n')
            for index in range(0,np.shape(Data)[0]):
                __Information=Data[index].tolist()
                writer.writerow(__Information)
       
        print('')
        print("Elapsed Time(CSV Saving): %s seconds " % (time.time() - start_time))

    def ShoreLine(self):
        self.__ConvolutedMap()
        self.__PixelToSpaceCoordinate()
        self.__SpaceCoordinateToLatLon()
        self.__SaveDataAsCSV(np.column_stack((self.__LatitudeData,self.__LongitudeData)))
       