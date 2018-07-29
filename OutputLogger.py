import time,os,simplekml,shapefile
import numpy as np
from termcolor import colored
import matplotlib.pyplot as plt 
#Debugger
def debug_print_value(debug_object,Debug_Identifier):
    print('')
    print(colored('DEBUG OBJECT:'+colored(Debug_Identifier,'blue'),'cyan'))
    print(colored('*********************************************************************************************','red'))
    print(colored(debug_object,'green'))
    print(colored('*********************************************************************************************','red'))
    print('')
    
#Plotting
def Plot_with_Geo_ref(data_array,Data_Identifier):
    
    start_time = time.time()
    
    print(colored('plotting data:'+Data_Identifier,'blue'))
    
    plt.figure(Data_Identifier)
    
    plt.imshow(data_array)
    
    plt.title(Data_Identifier)
    
    plt.grid(True)
    
    print(colored("Elapsed Time: "+Data_Identifier+ " %s seconds " % (time.time() - start_time),'yellow'))


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
