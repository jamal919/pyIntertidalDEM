import time,os,simplekml,shapefile,matplotlib.pyplot as plt,numpy as np,sys,gc,csv,scipy.misc 
from osgeo import gdal
from mpl_toolkits.basemap import Basemap

class Info(object):

    def __init__(self,directory):
        
        self.directory=directory                                           #The directory that contains the files(MASKS and Band Files)

        self.__OutputFolder=str(os.getcwd())+'/Output_log/'

        if not os.path.exists(self.__OutputFolder):

            os.mkdir(self.__OutputFolder)

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
    
    def OutputDir(self):
        __OutputDir=self.__OutputFolder+self.__DirectoryStrings[-1]+'/'
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
        
        print('    Metadata Type  :'+ self.__IdentifierStrings[4]+' Version:'+self.__IdentifierStrings[5][1])
        
    def __DataFileList(self):
        
        BandFileB2=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B2.tif'
        
        BandFileB4=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B4.tif'
        
        BandFileB8=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B8.tif'
        
        BandFileB11=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B11.tif'

        CloudMask10m=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_CLM_R1.tif'
        
        CloudMask20m=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_CLM_R2.tif'

        
        self.__Files=[BandFileB2,BandFileB4,BandFileB8,BandFileB11,CloudMask10m,CloudMask20m]

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
        self.OutputDir=InfoObj.OutputDir()
        self.GeoTiffDir=InfoObj.EdgeMaskDir() #Generall Case--ReadCase
        #self.GeoTiffDir=str(self.Directory)+'/EDG.tif'

    
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
        self.Directory=Directory
        
    def DebugPrint(self,Variable,VariableIdentifier):
        print('DEBUG OBJECT:'+VariableIdentifier)
        print('*********************************************************************************************')
        print(Variable)
        print('*********************************************************************************************')
        
    def DebugPlot(self,Variable,VariableIdentifier):
        
        print('plotting data:'+VariableIdentifier)
        
        plt.figure(VariableIdentifier)
        
        plt.imshow(Variable)
        
        plt.title(VariableIdentifier)
        
        plt.grid(True)
        
class SaveData(object):
    def __init__(self,Directory):
        InfoObj=Info(Directory)
        self.OutputDir=InfoObj.OutputDir()
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
        __RGBImageFile=self.OutputDir+str(Identifier)+'.jpg'
        scipy.misc.imsave(__RGBImageFile,Data)
        print('')
        print("Elapsed Time(JPG Saving): %s seconds " % (time.time() - start_time))
