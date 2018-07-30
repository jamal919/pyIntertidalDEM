import time,os,simplekml,shapefile,matplotlib.pyplot as plt,numpy as np,sys,gc 
from termcolor import colored
from osgeo import gdal
    
class Log(object):

    def __init__(self,Directory):
        
        self.Directory=Directory
        self.OutputDir=str(os.getcwd())+'/Output_log/'+str(self.Directory).split('/')[-1]+'/'
        self.GeoTiffDir=str(self.Directory)+'/MASKS/'+str(self.Directory).split('/')[-1]+'_EDG_R1.tif'
        if not os.path.exists(self.OutputDir):
            os.mkdir(self.OutputDir)
    
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
        DataSet=None
    
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

'''
##output formats---later process    

    csvfile=str(os.getcwd())+'/Output_log/'+str(directory_strings[-1])+'.csv'

    with open(csvfile,"w") as output:
        writer=csv.writer(output,lineterminator='\n')
        for index in range(0,np.shape(latitude_longitude)[0]):
            writer.writerow(latitude_longitude[index].tolist())
    

def kml_output(latitude_longitude,unzipped_directory):
    
    start_time = time.time()

    directory_strings=str(unzipped_directory).split('/')

    outputfile=str(os.getcwd())+'/Output_log/'+str(directory_strings[-1])+'.kml'

    kml=simplekml.Kml()

    for index in range(0,np.shape(latitude_longitude)[0]):
        lat=latitude_longitude[index,0]
        lon=latitude_longitude[index,1]
        kml.newpoint(coords=[(lat,lon)])
    
    kml.save(outputfile)

    print('')
    print(colored('*Saved to kml file ','cyan'))
    
    print('')
    print(colored("Elapsed Time: %s seconds " % (time.time() - start_time),'green'))




def shape_point_output(latitude_longitude,unzipped_directory):
    
    start_time=time.time()

    directory_strings=str(unzipped_directory).split('/')

    outputfile=str(os.getcwd())+'/Output_log/'+str(directory_strings[-1])+'__point.shp'

    lat=latitude_longitude[:,0]
    lon=latitude_longitude[:,1]

    Writer_SHP=shapefile.Writer(shapefile.POINT)
    
    Writer_SHP.field('Latitude')
    Writer_SHP.field('Longitude')

    Writer_SHP.record(lat,lon)
    Writer_SHP.save(outputfile)

    print('')
    print(colored('*Saved to .shp file ','cyan'))
    
    print('')
    print(colored("Elapsed Time: %s seconds " % (time.time() - start_time),'green'))
'''
