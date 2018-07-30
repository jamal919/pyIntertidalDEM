#!/usr/bin/env python3

from Sentiniel2Info import displayInfo
from Sentiniel2Logger import Log
from Sentiniel2Preprocessor import Preprocessor
from Sentiniel2RGBProcessor import RGBProcessor

import matplotlib.pyplot as plt,numpy as np



##globals
testCase1="/home/ansary/Sentiniel2/Data/20171130/SENTINEL2B_20171130-042157-149_L2A_T46QCK_D_V1-4"
    
directory=testCase1


#directory_strings=str(directory).split('/')           #user for output purposes


#------------------------------------------------------------------------------------------------------------------------

def ModuleInfoSentiniel(directory):
    info=displayInfo(directory)
    info.Banner()
    return info.DisplayFileList()




def ModuleRun():

    Logger=Log('Module Run')            #Logger Object

    Files=ModuleInfoSentiniel(directory)

    preprocess=Preprocessor(Files)      #Preprocessor Object

    RGBData=preprocess.GetRGBData()

    ProcessRGB=RGBProcessor(RGBData)    #RGBprocessor Object

    ShoreLine=ProcessRGB.GetShoreLine()

    Logger.DebugPrint(ShoreLine,'ShoreLine')

    #Logger.DebugPlot(maping,'maping')



    plt.show()
    
    
    
    
    
    
    
    
    '''
    data_to_extract=RGB_Data_extractor(data_files)    #data object

    rgb_data=data_to_extract.RGB_Construction()  
    
    shoreLine_data_obj=Shoreline_data_extractor(rgb_data)


    Map_Shore=shoreLine_data_obj.Shoreline_extraction()

    latitude_longitude=shoreLine_data_obj.pixel_Coordinate_to_latitude_longitude(Map_Shore,unzipped_directory)

    print(np.shape(latitude_longitude))
    '''
    '''
    csvfile=str(os.getcwd())+'/Output_log/'+str(directory_strings[-1])+'.csv'

    with open(csvfile,"w") as output:
        writer=csv.writer(output,lineterminator='\n')
        for index in range(0,np.shape(latitude_longitude)[0]):
            writer.writerow(latitude_longitude[index].tolist())
    '''
    
 
if __name__=='__main__':
    ModuleRun()    
