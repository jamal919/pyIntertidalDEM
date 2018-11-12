# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from osgeo import gdal
import gc 

class TiffReader(object):

    '''
        The purpose of this class is to contain necessary functions to Read GeoTiff data
    '''
    def __init__(self):
        __DataSet=None
    
    def ReadTiffData(self,File):
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
    
    
    def GetTiffData(self,File):
        '''
            Returns single Raster data as array
        '''
        __DataSet=self.ReadTiffData(File)
   
        if(__DataSet.RasterCount==1):                          
            try:
                __RasterBandData=__DataSet.GetRasterBand(1)
                
                __data=__RasterBandData.ReadAsArray()

                #manual cleanup
                __DataSet=None
                __RasterBandData=None
                gc.collect()
                
            except RuntimeError as e_arr:                                   #Error handling
                print('Error while data extraction file!')
                print('Error Details:')
                print(e_arr)
                sys.exit(1)
            return __data
        else:
            print('The file contains Multiple bands')
            sys.exit(1)
