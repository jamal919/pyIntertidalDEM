import time,os,simplekml,shapefile,matplotlib.pyplot as plt,numpy as np,sys,gc,csv,scipy.misc 
from termcolor import colored
from osgeo import gdal
    
class Log(object):

    def __init__(self,Directory):
        
        self.Directory=Directory
        self.OutputDir=str(os.getcwd())+'/Output_log/'+str(self.Directory).split('/')[-1]+'/'
        if not os.path.exists(self.OutputDir):
            os.mkdir(self.OutputDir)
        self.GeoTiffDir=str(self.Directory)+'/MASKS/'+str(self.Directory).split('/')[-1]+'_EDG_R1.tif'
        
    
    def PrintLogStatus(self,Status):
        print('')
        print(colored('*Status:'+colored(Status,'red'),'cyan'))
        print('')

    def DebugPrint(self,Variable,VariableIdentifier):
        print('')
        print(colored('DEBUG OBJECT:'+colored(VariableIdentifier,'blue'),'cyan'))
        print(colored('*********************************************************************************************','red'))
        print(colored(Variable,'green'))
        print(colored('*********************************************************************************************','red'))
        print('')

    def DebugPlot(self,Variable,VariableIdentifier):
        
        print(colored('plotting data:'+VariableIdentifier,'blue'))
        
        plt.figure(VariableIdentifier)
        
        plt.imshow(Variable)
        
        plt.title(VariableIdentifier)
        
        plt.grid(True)
    
    def __ReadDataFromGTIFF(self):
        #height,Width,Projection,Geotransform
        try:
            DataSet=gdal.Open(self.GeoTiffDir,gdal.GA_ReadOnly)        #taking readonly data
        
        except RuntimeError as e_Read:                                        #Error handling
            print(colored('Error while opening file!','red'))
            print(colored('Error Details:','blue'))
            print(e_Read)
            sys.exit(1)
    
        self.__Projection=DataSet.GetProjection()
        self.__GeoTransform=DataSet.GetGeoTransform()
        if(DataSet.RasterCount==1):                          
            try:
                self.__RasterBandData=DataSet.GetRasterBand(1)
                
                self.__NoData=self.__RasterBandData.ReadAsArray()

                #manual cleanup
                self.__RasterBandData=None
                gc.collect()
                
            except RuntimeError as e_arr:                                   #Error handling
                print(colored('Error while data extraction file!','red'))
                print(colored('Error Details:','blue'))
                print(e_arr)
                sys.exit(1)
        else:
            print('The file contains multiple bands','red')
            sys.exit(1)
        
        DataSet=None
    
    def GetNoDataCorrection(self):
        self.__ReadDataFromGTIFF()
        return self.__NoData
            
    def GetGeoTransformData(self):
        self.__ReadDataFromGTIFF()
        return self.__GeoTransform
    
    def GetProjectionData(self):
        self.__ReadDataFromGTIFF()
        return self.__Projection

    def SaveArrayToGeotiff(self,Array,Identifier):
        self.__ReadDataFromGTIFF()
        self.PrintLogStatus('Saving '+str(Identifier)+'.tiff')
        start_time=time.time()
        GeoTiffFileName = str(Identifier)+'.tiff'
        Driver = gdal.GetDriverByName('GTiff')
        OutputDataset = Driver.Create(self.OutputDir+GeoTiffFileName,np.shape(Array)[0],np.shape(Array)[1], 1,gdal.GDT_Float32)
        OutputDataset.GetRasterBand(1).WriteArray(Array)
        OutputDataset.SetGeoTransform(self.__GeoTransform)
        OutputDataset.SetProjection(self.__Projection)
        OutputDataset.FlushCache()
        OutputDataset=None
        print('')
        print(colored("Elapsed Time(GeoTiff Saving): %s seconds " % (time.time() - start_time),'green'))

    def SaveDataAsCSV(self,Identifier,Data):
        start_time=time.time()  
        csvfile=self.OutputDir+str(Identifier)+'.csv'
        with open(csvfile,"w") as output:
            writer=csv.writer(output,lineterminator='\n')
            for index in range(0,np.shape(Data)[0]):
                writer.writerow(Data[index].tolist())
        self.PrintLogStatus('Saving '+str(Identifier)+'.csv')

        print('')
        print(colored("Elapsed Time(CSV Saving): %s seconds " % (time.time() - start_time),'green'))
    
    def SaveDataAsKML(self,Identifier,Data):
        start_time = time.time()
        outputfile=self.OutputDir+str(Identifier)+'.kml'
        kml=simplekml.Kml()
        for index in range(0,np.shape(Data)[0]):
            __lat=Data[index,0]
            __lon=Data[index,1]
            kml.newpoint(coords=[(__lat,__lon)])
        kml.save(outputfile)
        self.PrintLogStatus('Saving '+str(Identifier)+'.kml')

        print('')
        print(colored("Elapsed Time(kml Saving): %s seconds " % (time.time() - start_time),'green'))
   
    def SaveRGBAsImage(self,Identifier,Data):
        start_time=time.time()
        self.PrintLogStatus('Saving RGB data As Image')
        __RGBImageFile=self.OutputDir+str(Identifier)+'.jpg'
        scipy.misc.imsave(__RGBImageFile,Data)
        print('')
        print(colored("Elapsed Time(JPG Saving): %s seconds " % (time.time() - start_time),'green'))



###single runner

class DebugLog(object):
    def __init__(self,Directory):
        self.Directory=Directory
        self.Logger=Log(Directory)
    
    def __ReadDataFromFile(self):
        try:
            self.__DataSet=gdal.Open(self.__Filename,gdal.GA_ReadOnly)        #taking readonly data
        
        except RuntimeError as e_Read:                                        #Error handling
            print(colored('Error while opening file!','red'))
            print(colored('Error Details:','blue'))
            print(e_Read)
            sys.exit(1)

    def __ReturnData(self):

        self.__ReadDataFromFile()
   
        if(self.__DataSet.RasterCount==1):                          
            try:
                self.__RasterBandData=self.__DataSet.GetRasterBand(1)
                
                self.__data=self.__RasterBandData.ReadAsArray()

                #manual cleanup
                self.__DataSet=None
                self.__RasterBandData=None
                gc.collect()
                
            except RuntimeError as e_arr:                                   #Error handling
                print(colored('Error while data extraction file!','red'))
                print(colored('Error Details:','blue'))
                print(e_arr)
                sys.exit(1)
        else:
            print('The file contains multiple bands','red')
            sys.exit(1)

    def GetFileData(self,FileName):
        
        self.Logger.PrintLogStatus('Getting data from file:'+colored(FileName,'blue'))
        
        self.__Filename=FileName

        self.__ReturnData()

        return self.__data