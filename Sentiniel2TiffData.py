from osgeo import gdal
import sys,gc,os,time,numpy as np

class TiffReader(object):
    def __init__(self,Directory):
        self.Directory=Directory
    
    def __ReadData(self,File):
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
        __DataSet=self.__ReadData(File)
   
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
    
class TiffWritter(object):
    def __init__(self,Directory):
        self.Directory=Directory
        self.OutputDir=str(os.getcwd())+'/Output_log/'+str(self.Directory).split('/')[-1]+'/'
        if not os.path.exists(self.OutputDir):
            os.mkdir(self.OutputDir)
        #self.GeoTiffDir=str(self.Directory)+'/MASKS/'+str(self.Directory).split('/')[-1]+'_EDG_R1.tif' #Generall Case
        self.GeoTiffDir=str(self.Directory)+'/EDG.tif'
    def __ProjectionAndTransfromData(self):
        #Projection,Geotransform
        try:
            DataSet=gdal.Open(self.GeoTiffDir,gdal.GA_ReadOnly)        #taking readonly data
        
        except RuntimeError as e_Read:                                        #Error handling
            print('Error while opening file!')
            print('Error Details:')
            print(e_Read)
            sys.exit(1)
    
        self.__Projection=DataSet.GetProjection()
        self.__GeoTransform=DataSet.GetGeoTransform()
        DataSet=None
    
    def SaveArrayToGeotiff(self,Array,Identifier):
        self.__ProjectionAndTransfromData()
        print('*Saving '+str(Identifier)+'.tiff')
        start_time=time.time()
        GeoTiffFileName = str(Identifier)+'.tiff'
        Driver = gdal.GetDriverByName('GTiff')
        OutputDataset = Driver.Create(self.OutputDir+GeoTiffFileName,np.shape(Array)[0],np.shape(Array)[1], 1,gdal.GDT_Float32)
        OutputDataset.GetRasterBand(1).WriteArray(Array)
        OutputDataset.SetGeoTransform(self.__GeoTransform)
        OutputDataset.SetProjection(self.__Projection)
        OutputDataset.FlushCache()
        OutputDataset=None
        print("Elapsed Time(GeoTiff Saving): %s seconds " % (time.time() - start_time))

#No Data Values
class NoData(object):
    def __init__(self,Directory):
        self.Directory=Directory
        self.GeoTiffDir=str(self.Directory)+'/MASKS/'+str(self.Directory).split('/')[-1]+'_EDG_R1.tif'
    
    def GetNoData(self):
        gdal.UseExceptions()
        try:
            DataSet=gdal.Open(self.GeoTiffDir,gdal.GA_ReadOnly)        #taking readonly data
        
        except RuntimeError as e_Read:                                        #Error handling
            print('Error while opening file!')
            print('Error Details:')
            print(e_Read)
            sys.exit(1)
    
        if(DataSet.RasterCount==1):                          
            try:
                __RasterBandData=DataSet.GetRasterBand(1)
                
                __NoData=__RasterBandData.ReadAsArray()

                #manual cleanup
                __RasterBandData=None
                gc.collect()
                
            except RuntimeError as e_arr:                                   #Error handling
                print('Error while data extraction file!')
                print('Error Details:')
                print(e_arr)
                sys.exit(1)
        else:
            print('The file contains multiple bands')
            sys.exit(1)
        DataSet=None
        return __NoData

       