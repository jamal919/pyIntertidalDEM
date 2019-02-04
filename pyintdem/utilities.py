#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np
from osgeo import osr, gdal
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import time
from datetime import datetime, timedelta
import gc
import sys
import os

class Info(object):
    '''
        The purpose of this class is to collect useable data from the input data
    '''

    def __init__(self,directory):
        self.directory=directory #The directory that contains the files(MASKS and Band Files)        
        self.__DirectoryStrings=str(self.directory).split('/') #split the directory to extract specific folder
        self.__DirectoryStrings=list(filter(bool,self.__DirectoryStrings))
        self.__IdentifierStrings=self.__DirectoryStrings[-1].split('_') #split the specific folder data identifiers
        self.__DateTimeStamp=self.__IdentifierStrings[1].split('-') #Time stamp data 

        __Date=self.__DateTimeStamp [0][6:]+'-'+self.__DateTimeStamp[0][4:6]+'-'+self.__DateTimeStamp[0][0:4]
        __Time=self.__DateTimeStamp[1][0:2]+'-'+self.__DateTimeStamp[1][2:4]+'-'+self.__DateTimeStamp[1][4:]
        self.DateTime=__Date+'_'+__Time
        self.SateliteName=self.__IdentifierStrings[0]
        self.Zone=self.__IdentifierStrings[3]
    
    
    def __DisplayProductInformation(self):
        '''
            Displays information about the data
        '''
        _satellite = self.__IdentifierStrings[0]
        _date = self.__DateTimeStamp [0][6:]+'-'+self.__DateTimeStamp[0][4:6]+'-'+self.__DateTimeStamp[0][0:4]
        _time = self.__DateTimeStamp[1][0:2]+':'+self.__DateTimeStamp[1][2:4]+':'+self.__DateTimeStamp[1][4:]+':'+self.__DateTimeStamp[2]
        _product = self.__IdentifierStrings[2]
        _zone = self.__IdentifierStrings[3]
        _version = self.__IdentifierStrings[5]+self.__IdentifierStrings[4]
        print('* {:s} {:s} {:s} {:s} : {:s} {:s}'.format(_satellite, _zone, _product, _version, _date, _time,))
        
        # print('    Satelite Name  :'+ self.__IdentifierStrings[0])
        # print('             Date  :'+ self.__DateTimeStamp [0][6:]+'-'+self.__DateTimeStamp[0][4:6]+'-'+self.__DateTimeStamp[0][0:4])
        # print('             Time  :'+ self.__DateTimeStamp[1][0:2]+':'+self.__DateTimeStamp[1][2:4]+':'+self.__DateTimeStamp[1][4:]+':'+self.__DateTimeStamp[2])
        # print('     Product Type  :'+ self.__IdentifierStrings[2])
        # print('Geographical Zone  :'+ self.__IdentifierStrings[3])
        # print('    Metadata Type  :'+ self.__IdentifierStrings[5]+self.__IdentifierStrings[4])
        
    def __DataFileList(self):

        '''
            Lists the files to be used for processing
            For our purposes 4 bands and 2 masks are used:

            |---------+------+------------+------------+
            | Band No | Type | Wavelength | Resolution |
            |---------+------+------------+------------+
            | B2      | Blue | 490nm      |         10 |
            | B4      | Red  | 665nm      |         10 |
            | B8      | NIR  | 842nm      |         10 |
            | B11     | SWIR | 1610nm     |         20 |
            |---------+------+------------+------------+

            The two Cloud masks contains cloud information for 10m and 20m resolutions 
        '''
        BlueBandFile=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B2.tif'
        RedBandFile=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B4.tif'
        GreenBandFile=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B8.tif'
        SWIRBandB11=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B11.tif'
        CloudMask10m=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_CLM_R1.tif'
        CloudMask20m=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_CLM_R2.tif'
        
        self.__Files=[RedBandFile,GreenBandFile,BlueBandFile,SWIRBandB11,CloudMask10m,CloudMask20m]

    
    def DefineDiectoriesAndReferences(self,ProcessedDataPath,PreprocessedDataPath,png=False):
        MASKDIR=os.path.join(PreprocessedDataPath,'Masks','')
        if not os.path.exists(PreprocessedDataPath):
            print('Water Mask Directory Not Found!')
            print('Preprocess the data to create WaterMap for the zone')
            sys.exit(1)

        MASKFILE=str(os.path.join(MASKDIR,self.Zone+'.tiff'))
        
        if not os.path.isfile(MASKFILE):
            print('Water Mask File  Not Found for zone:'+self.Zone)
            sys.exit(1)
        
        
        self.__OD=ProcessedDataPath

        self.ReferenceGeotiff=MASKFILE         #For TiffSaving And Plotting

        self.MainDir=os.path.join(ProcessedDataPath,self.Zone,self.DateTime+'_'+self.SateliteName,'')
        
        self.PNGOutDir=os.path.join(self.MainDir,'QucikLookPngFiles','')

        ODZ=os.path.join(self.__OD,self.Zone,'')
        if not os.path.exists(ODZ):
            os.mkdir(ODZ)
        ODZI=os.path.join(ODZ,self.DateTime+'_'+self.SateliteName,'')
        if not os.path.exists(ODZI):
            os.mkdir(ODZI)
        if png:
            ODZIP=os.path.join(ODZI,'QucikLookPngFiles','')
            if not os.path.exists(ODZIP):
                os.mkdir(ODZIP)
   
    
    def DisplayFileList(self):
        '''
            Display's data information

            Creates the List of files to be used

            Returns the file List
        '''
        self.__DisplayProductInformation()        
        
        self.__DataFileList()
        
        return self.__Files 

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
            __DataSet=gdal.Open(File,gdal.GA_ReadOnly)
        except RuntimeError as e_Read:
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
                
            except RuntimeError as e_arr:
                print('Error while data extraction file!')
                print('Error Details:')
                print(e_arr)
                sys.exit(1)
            return __data
        else:
            print('The file contains Multiple bands')
            sys.exit(1)


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
    
    def SaveArrayToGeotiff(self, Array, Identifier, ReferenceGeoTiffDir, OutputDirectory):
        '''
            Saving array Data as geotiff
        '''
        self.OutputDir=str(OutputDirectory)+'/'                 
        
        self.GeoTiffDir=ReferenceGeoTiffDir
        self.__ProjectionAndTransfromData() # Gets projection and geotransform
        GeoTiffFileName = str(Identifier)+'.tiff' # Output geotiff file name according to identifier
        Driver = gdal.GetDriverByName('GTiff')
        OutputDataset = Driver.Create(self.OutputDir+GeoTiffFileName,np.shape(Array)[0],np.shape(Array)[1], 1,gdal.GDT_Float32)
        OutputDataset.GetRasterBand(1).WriteArray(Array)
        OutputDataset.SetGeoTransform(self.__GeoTransform)
        OutputDataset.SetProjection(self.__Projection)
        OutputDataset.FlushCache()
        OutputDataset=None

class DataPlotter(object):

    '''
        The purpose of this class is to view specific data as Plot or Print the data
    '''

    def __init__(self,ReferenceGeoTiffDir,OutputDir):
        __NoDataFile = ReferenceGeoTiffDir #Reference 
        Reader = TiffReader()
        self.OUTdir = OutputDir
       
        __DataSet = Reader.ReadTiffData(__NoDataFile)
        GeoTransForm = __DataSet.GetGeoTransform()
        Projection = __DataSet.GetProjection()
        __DataSet = Reader.GetTiffData(__NoDataFile)
        [row,col] = np.shape(__DataSet)
        __DataSet = None

        xdiff=1000
        ydiff=1000
        ceilx=-(-row//xdiff)
        ceily=-(-col//ydiff)
        xps=np.arange(0,ceilx*xdiff,xdiff)
        yps=np.arange(0,ceily*ydiff,ydiff)
        
        [__x_offset, __pixel_width, __rotation_1, __y_offset, __rotation_2, __pixel_height] = GeoTransForm
        __pixel_Coordinate_X = xps
        __pixel_Coordinate_y = yps
        __Space_coordinate_X = __pixel_width*__pixel_Coordinate_X+__rotation_1*__pixel_Coordinate_y+__x_offset
        __Space_coordinate_Y = __rotation_2*__pixel_Coordinate_X + __pixel_height*__pixel_Coordinate_y+__y_offset
        
        ## get CRS from dataset
        # Get Co-ordinate reference
        __Coordinate_Reference_System = osr.SpatialReference()
        # projection reference
        __Coordinate_Reference_System.ImportFromWkt(Projection)                  

        ## create lat/long CRS with WGS84 datum<GDALINFO for details>
        __Coordinate_Reference_System_GEO = osr.SpatialReference()
        # 4326 is the EPSG id of lat/long CRS
        __Coordinate_Reference_System_GEO.ImportFromEPSG(4326) 

        __Transform_term = osr.CoordinateTransformation(
            __Coordinate_Reference_System, 
            __Coordinate_Reference_System_GEO
        )
        Latitude = np.zeros(np.shape(yps)[0])
        Longitude = np.zeros(np.shape(xps)[0])
        for idx in range(0,np.shape(yps)[0]):
            (__latitude_point, __longitude_point, _ ) = __Transform_term.TransformPoint(
                __Space_coordinate_X[idx],
                __Space_coordinate_Y[idx]
            )
            Latitude[idx] = __latitude_point
            Longitude[idx] = __longitude_point
        self.__XPS = xps
        self.__YPS = yps
        self.__Lats = np.round(Latitude, decimals=4) 
        self.__Lons = np.round(Longitude, decimals=4)

    
    def PlotWithGeoRef(self, Variable, VariableIdentifier, pltshow=False):
        '''
            Plots the data with Geo reference
        '''
        gdal.UseExceptions()
        low = np.nanmin(Variable)
        high = np.nanmax(Variable)
        V = np.linspace(low, high, 10, endpoint=True)
        plt.figure(VariableIdentifier)
        plt.title(VariableIdentifier)
        plt.grid(True)
        plt.xticks(self.__XPS, self.__Lats)
        plt.yticks(self.__YPS, self.__Lons)
        plt.imshow(Variable)
        plt.colorbar(ticks=V)
        
        savename = os.path.join(self.OUTdir, '{:s}.png'.format(VariableIdentifier))
        plt.savefig(savename)
        
        if (pltshow==True):
            plt.show()
        
        # clear memory
        plt.clf()
        plt.close()

    def plotInMap(self, data, Identifier, cmap='binary', rgb=False, colorbar=False, pltshow=False):
        cmap = cmap
        LatMax = np.amax(self.__Lats)
        LatMin = np.amin(self.__Lats)
        LonMax = np.amax(self.__Lons)
        LonMin = np.amin(self.__Lons)
        extent = [LatMin,LatMax,LonMin,LonMax] #LL=0,2 UR=1,3
        
        savename = os.path.join(self.OUTdir, '{:s}.png'.format(str(Identifier)))

        plotbound = extent
        fig, ax = plt.subplots(figsize=(9, 9))
        m = Basemap(
            llcrnrlon=plotbound[0], 
            llcrnrlat=plotbound[2], 
            urcrnrlon=plotbound[1],
            urcrnrlat=plotbound[3], 
            projection='merc', 
            resolution='c',
            ax=ax
        )
        if rgb:
            img = m.imshow(data, extent=extent, origin='upper')
        else:
            img = m.imshow(data, extent=extent, origin='upper', cmap=cmap)
        m.drawparallels(
            circles=np.arange(np.round(plotbound[2], 1), np.round(plotbound[3], 2), 0.2), 
            labels=[True, False, False, True], 
            dashes=[2, 2]
        )
        m.drawmeridians(
            meridians=np.arange(np.round(plotbound[0], 1), np.round(plotbound[1], 2), 0.2), 
            labels=[True, False, False, True], 
            dashes=[2, 2]
        )

        if colorbar:
            m.colorbar(img, location='right')
        
        plt.savefig(savename)
        
        if (pltshow==True):
            plt.show()
        plt.clf()
        plt.close()

class WaterBodyMap(object):
    def __init__(self,wkdir,improcdir,prepdir):
        row=10980
        col=10980
        self.__DataPath=wkdir
        self.__Zones=os.listdir(wkdir)
        self.__improcdir=improcdir
        self.__prepdir=prepdir
        self.__TiffReader=TiffReader()
        self.__TiffWriter=TiffWriter()
        self.__ALLData=np.empty((row,col))
        self.__OutDir=os.path.join(self.__improcdir,'RiverMaps','')
        if not os.path.exists(self.__OutDir):
            os.mkdir(self.__OutDir)



    def CombineBinaryWaterMaps(self): 
        for zone in self.__Zones:
            print('Calculating for zone:'+str(zone))
            DataPath=str(os.path.join(self.__DataPath,zone,''))
            DataFolders=os.listdir(DataPath)
            self.__ALLData=np.zeros(self.__ALLData.shape)
            for df in DataFolders:
                directory=str(os.path.join(DataPath,df,''))
                InfoObj=Info(directory)
                InfoObj.DefineDiectoriesAndReferences(self.__improcdir,self.__prepdir,png=True)
                DataFile=InfoObj.MainDir+'3.1.5 Binary Water Map.tiff'
                print('Reading Data:'+str(DataFile))
                Data=self.__TiffReader.GetTiffData(DataFile)
                iNan=np.isnan(Data)
                Data[iNan]=0
                self.__ALLData+=Data
            DataViewer=DataPlotter(InfoObj.ReferenceGeotiff,self.__OutDir)
            DataViewer.PlotWithGeoRef(self.__ALLData,'RiverMap:'+str(zone))
            self.__TiffWriter.SaveArrayToGeotiff(self.__ALLData,'RiverMap:'+str(zone),InfoObj.ReferenceGeotiff,self.__OutDir)