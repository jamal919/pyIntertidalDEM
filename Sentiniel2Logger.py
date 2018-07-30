import time,os,simplekml,shapefile
import numpy as np
from termcolor import colored
import matplotlib.pyplot as plt 

    
#Plotting
    
    

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


class Log(object):

    def __init__(self,Identifier):
        
        self.Identifier=Identifier

    def PrintLogStatus(self,Status):
        print('')
        print(colored('*Status:'+colored(Status,'red'),'cyan'))
        print('')

    def DebugPrint(self,Variable,VariableIdentifier):
        print('')
        print(colored('DEBUG OBJECT:'+colored(self.Identifier+':'+VariableIdentifier,'blue'),'cyan'))
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
