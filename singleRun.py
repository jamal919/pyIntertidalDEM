#!/usr/bin/env python3

from initializer import Program_initializer
from dataExtractor import RGB_Data_extractor,Shoreline_data_extractor
import numpy as np

def module_run():

    unzipped_directory="/home/ansary/Sentiniel2/Data/20171130/SENTINEL2B_20171130-042157-149_L2A_T46QCK_D_V1-4"
    prog=Program_initializer(unzipped_directory)  #program object
    
    prog.print_banner()
    
    data_files=prog.list_files_sentiniel()

    data_to_extract=RGB_Data_extractor(data_files)    #data object

    rgb_data=data_to_extract.RGB_Construction()  
    
    shoreLine_data_obj=Shoreline_data_extractor(rgb_data)


    Map_Shore=shoreLine_data_obj.Shoreline_extraction()

    latitude_longitude=shoreLine_data_obj.pixel_Coordinate_to_latitude_longitude(Map_Shore,unzipped_directory)

    
    
#Main 
if __name__=='__main__':
    module_run()    
