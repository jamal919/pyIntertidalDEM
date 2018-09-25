import time,os,simplekml,shapefile,matplotlib.pyplot as plt,numpy as np,sys,gc,csv,scipy.misc,matplotlib 
from osgeo import gdal,osr

class Info(object):
    '''
        The purpose of this class is to collect useable data from the input data
    '''


    def __init__(self,directory):
        self.directory=directory                                           #The directory that contains the files(MASKS and Band Files)

        #SECTION: Creation of output Log for the data
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
        
        
        #SECTION: Information of the data
        #The existance of EDG_R1 file is necessary in data folder for the program to work properly

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
        '''
            Returns output directory based on file type
            The structre of Output directory is as follows:

                            Output_log
                                |
                                |
                     ------------------------
                     |          |           |
                    PNG        CSV         TIFF
                     |          |           |
                    Zones      Zones       Zones
                     |          |           |
                DataString   DataString   DataString
                     |          |           |
            Stepwise Results  Final      Stepwise Results
                             Lat Lon
            
            *A sample Zone looks like: T45QYE

            *A sample Data string look like: SENTINEL2B_20171103-043722-293_L2A_T45QYG_D_V1-4
        '''
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

    
    def __DisplayProductInformation(self):
        '''
            Displays information about the data
        '''
        
        print('    Satelite Name  :'+ self.__IdentifierStrings[0])
        
        print('             Date  :'+ self.__DateTimeStamp [0][6:]+'-'+self.__DateTimeStamp[0][4:6]+'-'+self.__DateTimeStamp[0][0:4])
        
        print('             Time  :'+ self.__DateTimeStamp[1][0:2]+':'+self.__DateTimeStamp[1][2:4]+':'+self.__DateTimeStamp[1][4:]+':'+self.__DateTimeStamp[2])
        
        print('     Product Type  :'+ self.__IdentifierStrings[2])
        
        print('Geographical Zone  :'+ self.__IdentifierStrings[3])
        
        print('    Metadata Type  :'+ self.__IdentifierStrings[4]+' Version:'+self.__IdentifierStrings[5])
        
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
            | B12     | SWIR | 2190nm     |         20 |
            |---------+------+------------+------------+

            The two Cloud masks contains cloud information for 10m and 20m resolutions 
        '''
        BlueBandFile=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B2.tif'
        
        RedBandFile=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B4.tif'

        GreenBandFile=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B8.tif'

        SWIRBandB11=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B11.tif'

        SWIRBandB12=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B12.tif'

        CloudMask10m=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_CLM_R1.tif'
        
        CloudMask20m=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_CLM_R2.tif'
        
        

        self.__Files=[RedBandFile,GreenBandFile,BlueBandFile,SWIRBandB11,SWIRBandB12,CloudMask10m,CloudMask20m]

    
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
    def __init__(self,Directory):
        self.Directory=Directory
    
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


class TiffWritter(object):

    '''
        The purpose of this class is to write Array data as Geotiff
    '''

    def __init__(self,Directory):
        self.Directory=Directory

        InfoObj=Info(self.Directory)
        self.OutputDir=InfoObj.OutputDir('TIFF')   #Gets the Tiff data output directory creates by Info class
        
        self.GeoTiffDir=InfoObj.EdgeMask           #Gets the edgemask file
    
    def __ProjectionAndTransfromData(self):
        '''
            GeoTiff mainly consists of three parts:
            >Projection Data
            >Geo Transformation Data
            >Raster Data(Array data/ values )
            
            According to the given datafolder, the edge mask is used to collect the Projection and geotransformation data   
        '''
        TiffReaderObj=TiffReader(self.Directory)
        DataSet=TiffReaderObj.ReadTiffData(self.GeoTiffDir)
        self.__Projection=DataSet.GetProjection()
        self.__GeoTransform=DataSet.GetGeoTransform()
        DataSet=None
    
    def SaveArrayToGeotiff(self,Array,Identifier):
        '''
            Saving array Data as geotiff
        '''

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

class ViewData(object):

    '''
        The purpose of this class is to view specific data as Plot or Print the data
    '''

    def __init__(self,Directory):
       
        __InfoObj=Info(Directory)
       
        Reader=TiffReader(Directory)
       
        self.OUTdir=__InfoObj.OutputDir('PNG')
       
       ##The following section is used to collect the Lat Lon of Plot axis from pixel
       ##----------------------------------------------------------------------------
        __NoDataFile=__InfoObj.EdgeMask
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
        ##--------------------------------------------------------------------------------------------------------------------------------------------


    def DebugPrint(self,Variable,VariableIdentifier):
        '''
            Prints a varible as respect to indentification
        '''
        print('DEBUG OBJECT:'+VariableIdentifier)
        print('*********************************************************************************************')
        print(Variable)
        print('*********************************************************************************************')
    
 

    def PlotWithGeoRef(self,Variable,VariableIdentifier,PlotImdt=False,TestSaveDir=None):
        
        '''
            Plots the data with Geo reference
        '''


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

        if TestSaveDir is None:
            plt.savefig(self.OUTdir+VariableIdentifier+'.png')
        else:
            plt.savefig(str(TestSaveDir)+VariableIdentifier+'.png')

        if (PlotImdt==True):
            plt.show() 
        
        #clear memory
        plt.clf()
        
        plt.close()
            
class SaveData(object):
    '''
        The purpose of this class is to save the Lat Lon data as KML and CSV
    '''

    def __init__(self,Directory):
        InfoObj=Info(Directory)
        self.OutputDir=InfoObj.OutputDir('CSV')
        self.DateTime=InfoObj.DateTime
        self.SateliteName=InfoObj.SateliteName
        self.Zone=InfoObj.Zone

    def SaveDataAsCSV(self,Identifier,Data):
        '''
            Saves Lat Lon Data as CSV in a Given Format
        '''
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
    
    def SaveDataAsKML(self,Identifier,Data):
        '''
            Saves Lat Lon Data as KML 
        '''

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
    