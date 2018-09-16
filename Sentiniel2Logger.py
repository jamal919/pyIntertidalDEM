import time,os,simplekml,shapefile,matplotlib.pyplot as plt,numpy as np,sys,gc,csv,scipy.misc,matplotlib 
from osgeo import gdal,osr

class Info(object):

    def __init__(self,directory):
        
        self.directory=directory                                           #The directory that contains the files(MASKS and Band Files)

        self.__OutputFolder=str(os.getcwd())+'/Output_log/'

        if not os.path.exists(self.__OutputFolder):

            os.mkdir(self.__OutputFolder)
        
        self.PNGdir=self.__OutputFolder+'PNG Files/'
        if not os.path.exists(self.PNGdir):

            os.mkdir(self.PNGdir)
        self.TIFFDir=self.__OutputFolder+'TIFF Files/'
        if not os.path.exists(self.TIFFDir):

            os.mkdir(self.TIFFDir)
        self.CSVDir=self.__OutputFolder+'CSV Files/'
        if not os.path.exists(self.CSVDir):

            os.mkdir(self.CSVDir)
        

        self.__DirectoryStrings=str(self.directory).split('/')             #split the directory to extract specific folder
        
        self.__DirectoryStrings=list(filter(bool,self.__DirectoryStrings))
        
        self.__IdentifierStrings=self.__DirectoryStrings[-1].split('_')    #split the specific folder data identifiers
       
        self.__DateTimeStamp=self.__IdentifierStrings[1].split('-')        #Time stamp data 

        self.EdgeMask=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_EDG_R1.tif'

        __Date=self.__DateTimeStamp [0][6:]+'-'+self.__DateTimeStamp[0][4:6]+'-'+self.__DateTimeStamp[0][0:4]
        
        __Time=self.__DateTimeStamp[1][0:2]+'-'+self.__DateTimeStamp[1][2:4]+'-'+self.__DateTimeStamp[1][4:]
        
        self.DateTime=__Date+' '+__Time
        self.SateliteName=self.__IdentifierStrings[0]
        self.Zone=self.__IdentifierStrings[3]    
        
       

    def OutputDir(self,Type):
        if(Type==str('PNG')):
            __OutputFolder=self.PNGdir+str(self.Zone)+'/'
            if not os.path.exists(__OutputFolder):
                os.mkdir(__OutputFolder)
        if(Type==str('TIFF')): 
            __OutputFolder=self.TIFFDir+str(self.Zone)+'/'
            if not os.path.exists(__OutputFolder):
                os.mkdir(__OutputFolder)
        if(Type==str('CSV')): 
            __OutputFolder=self.CSVDir+str(self.Zone)+'/'
            if not os.path.exists(__OutputFolder):
                os.mkdir(__OutputFolder)
        
        __OutputDir=__OutputFolder+self.__DirectoryStrings[-1]+'/'
        if not os.path.exists(__OutputDir):
            os.mkdir(__OutputDir)
        return __OutputDir

    def EdgeMaskDir(self):
        return self.EdgeMask

    def __Banner(self):
        print('')
        print('*********************************************************************************************')
        print('****************************        SENTINIEL2        ***************************************')
        print('*********************************************************************************************')
        print('')
    
    def __DisplayProductInformation(self):
        
        print('    Satelite Name  :'+ self.__IdentifierStrings[0])
        
        print('             Date  :'+ self.__DateTimeStamp [0][6:]+'-'+self.__DateTimeStamp[0][4:6]+'-'+self.__DateTimeStamp[0][0:4])
        
        print('             Time  :'+ self.__DateTimeStamp[1][0:2]+':'+self.__DateTimeStamp[1][2:4]+':'+self.__DateTimeStamp[1][4:]+':'+self.__DateTimeStamp[2])
        
        print('     Product Type  :'+ self.__IdentifierStrings[2])
        
        print('Geographical Zone  :'+ self.__IdentifierStrings[3])
        
        print('    Metadata Type  :'+ self.__IdentifierStrings[4]+' Version:'+self.__IdentifierStrings[5])
        
    def __DataFileList(self):
        
        BandFileB2=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B2.tif'
        
        BandFileB3=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B3.tif'
        
        BandFileB4=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B4.tif'

        BandFileB8=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B8.tif'
        
        BandFileB12=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B12.tif'

        CloudMask10m=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_CLM_R1.tif'
        
        CloudMask20m=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_CLM_R2.tif'

        
        self.__Files=[BandFileB2,BandFileB3,BandFileB4,BandFileB8,BandFileB12,CloudMask10m,CloudMask20m]

    def __PrintFileList(self):
        print('Listing Files To Be used')
        
        for f in self.__Files:
            print('')
            print(f)
            print('')

    def DisplayFileList(self):

        self.__Banner()
    
        self.__DisplayProductInformation()        
        
        self.__DataFileList()
    
        self.__PrintFileList()
        
        return self.__Files 

class TiffReader(object):

    def __init__(self,Directory):
        self.Directory=Directory
    
    def ReadTiffData(self,File):
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
    
class TiffWritter(object):

    def __init__(self,Directory):
        self.Directory=Directory
        InfoObj=Info(self.Directory)
        self.OutputDir=InfoObj.OutputDir('TIFF')
        self.GeoTiffDir=InfoObj.EdgeMaskDir() 
    
    def __ProjectionAndTransfromData(self):
        TiffReaderObj=TiffReader(self.Directory)
        DataSet=TiffReaderObj.ReadTiffData(self.GeoTiffDir)
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

class ViewData(object):

    def __init__(self,Directory):
        __InfoObj=Info(Directory)
        Reader=TiffReader(Directory)
        self.OUTdir=__InfoObj.OutputDir('PNG')
        __NoDataFile=__InfoObj.EdgeMaskDir()
        __DataSet=Reader.ReadTiffData(__NoDataFile)
        GeoTransForm=__DataSet.GetGeoTransform()
        Projection=__DataSet.GetProjection()
        __DataSet=Reader.GetTiffData(__NoDataFile)
        [row,col]=np.shape(__DataSet)
        __DataSet=None

        xdiff=1000
        ydiff=1000
        ceilx=-(-row//xdiff)
        ceily=-(-col//ydiff)
        xps=np.arange(0,ceilx*xdiff,xdiff)
        yps=np.arange(0,ceily*ydiff,ydiff)
        
        [__x_offset,__pixel_width,__rotation_1,__y_offset,__rotation_2,__pixel_height]=GeoTransForm
        __pixel_Coordinate_X=xps
        __pixel_Coordinate_y=yps
        __Space_coordinate_X= __pixel_width * __pixel_Coordinate_X +   __rotation_1 * __pixel_Coordinate_y + __x_offset
        __Space_coordinate_Y= __rotation_2* __pixel_Coordinate_X +    __pixel_height* __pixel_Coordinate_y + __y_offset
        
        ##get CRS from dataset
        __Coordinate_Reference_System=osr.SpatialReference()                     #Get Co-ordinate reference
        __Coordinate_Reference_System.ImportFromWkt(Projection)                  #projection reference

        ## create lat/long CRS with WGS84 datum<GDALINFO for details>
        __Coordinate_Reference_System_GEO=osr.SpatialReference()
        __Coordinate_Reference_System_GEO.ImportFromEPSG(4326)                   # 4326 is the EPSG id of lat/long CRS

        __Transform_term = osr.CoordinateTransformation(__Coordinate_Reference_System, __Coordinate_Reference_System_GEO)
        Latitude=np.zeros(np.shape(yps)[0])
        Longitude=np.zeros(np.shape(xps)[0])
        for idx in range(0,np.shape(yps)[0]):
            (__latitude_point, __longitude_point, _ ) = __Transform_term.TransformPoint(__Space_coordinate_X[idx], __Space_coordinate_Y[idx])
            Latitude[idx]=__latitude_point
            Longitude[idx]=__longitude_point
        self.__XPS=xps
        self.__YPS=yps
        self.__Lats=np.round(Latitude,decimals=4) 
        self.__Lons=np.round(Longitude,decimals=4)
        
    def DebugPrint(self,Variable,VariableIdentifier):
        print('DEBUG OBJECT:'+VariableIdentifier)
        print('*********************************************************************************************')
        print(Variable)
        print('*********************************************************************************************')
    
 

    def PlotWithGeoRef(self,Variable,VariableIdentifier,PlotImdt=False):
        
        print('plotting data:'+VariableIdentifier)
        low=np.nanmin(Variable)
        high=np.nanmax(Variable)
        
        V=np.linspace(low,high,10,endpoint=True)
        
        plt.figure(VariableIdentifier)
            
        plt.title(VariableIdentifier)
        
        plt.grid(True)

        plt.xticks(self.__XPS,self.__Lats)

        plt.yticks(self.__YPS,self.__Lons)
   
        plt.imshow(Variable)

        plt.colorbar(ticks=V)
        
        plt.savefig(self.OUTdir+VariableIdentifier+'.png')
        
        if (PlotImdt==True):
            plt.show() 
        
        #clear memory
        plt.clf()
        
        plt.close()
            
class SaveData(object):
    def __init__(self,Directory):
        InfoObj=Info(Directory)
        self.OutputDir=InfoObj.OutputDir('CSV')
        self.DateTime=InfoObj.DateTime
        self.SateliteName=InfoObj.SateliteName
        self.Zone=InfoObj.Zone

    def SaveDataAsCSV(self,Identifier,Data):
        start_time=time.time()
        __Information=[self.DateTime,self.SateliteName,self.Zone]  
        print('Saving '+str(Identifier)+'.csv')
        csvfile=self.OutputDir+str(Identifier)+'.csv'
        with open(csvfile,"w") as output:
            writer=csv.writer(output,lineterminator='\n')
            for index in range(0,np.shape(Data)[0]):
                __Information[3:]=Data[index].tolist()
                writer.writerow(__Information)
       
        print('')
        print("Elapsed Time(CSV Saving): %s seconds " % (time.time() - start_time))
    
    def SaveImageDataAsCSV(self,Identifier,Data):
        start_time=time.time()
        print('Saving '+str(Identifier)+'.csv')
        csvfile=self.OutputDir+str(Identifier)+'.csv'
        with open(csvfile,"w") as output:
            writer=csv.writer(output,lineterminator='\n')
            for index in range(0,np.shape(Data)[0]):
                writer.writerow(Data[index].tolist())
       
        print('')
        print("Elapsed Time(CSV Saving): %s seconds " % (time.time() - start_time))
    



    def SaveDataAsKML(self,Identifier,Data):
        start_time = time.time()
        outputfile=self.OutputDir+str(Identifier)+'.kml'
        kml=simplekml.Kml()
        for index in range(0,np.shape(Data)[0]):
            __lat=Data[index,0]
            __lon=Data[index,1]
            kml.newpoint(coords=[(__lat,__lon)])
        kml.save(outputfile)
        print('Saving '+str(Identifier)+'.kml')

        print('')
        print("Elapsed Time(kml Saving): %s seconds " % (time.time() - start_time))
   
    def SaveRGBAsImage(self,Identifier,Data):
        start_time=time.time()
        print('Saving RGB data As Image')
        __RGBImageFile=self.OutputDir+str(Identifier)+'.png'
        scipy.misc.imsave(__RGBImageFile,Data)
        print('')
        print("Elapsed Time(PNG Saving): %s seconds " % (time.time() - start_time))
