#!/usr/bin/env python3

from termcolor import colored 

class Program_initializer(object):


    def __init__(self,unzipped_directory):
        self.unzipped_directory=unzipped_directory

    #Banner
    def print_banner(self):
        print('')
        print(colored('*********************************************************************************************','blue'))
        print(colored('****************************'+colored('        SENTINIEL2        ','red')+colored('***************************************','green'),'green'))
        print(colored('*********************************************************************************************','blue'))
        print('')
    

    #list all files needed for processing
    def list_files_sentiniel(self):
    
        directory_strings=str(self.unzipped_directory).split('/')  #split the directory to extract specific folder
        identifier_strings=directory_strings[-1].split('_')   #split the specific folder data identifiers
        date_time_stamp=identifier_strings[1].split('-')      #Time stamp data 

        #display product information
        print(colored('    Satelite Name  :','green')+ colored(identifier_strings[0],'blue'))
        print(colored('             Date  :','green')+ colored(date_time_stamp[0][6:]+'-'+date_time_stamp[0][4:6]+'-'+date_time_stamp[0][0:4],'blue'))
        print(colored('             Time  :','green')+ colored(date_time_stamp[1][0:2]+':'+date_time_stamp[1][2:4]+':'+date_time_stamp[1][4:]+':'+date_time_stamp[2]+'(ms)','blue'))
        print(colored('     Product Type  :','green')+ colored(identifier_strings[2]+colored('(See Handbook for description)','red'),'blue'))
        print(colored('Geographical Zone  :','green')+ colored(identifier_strings[3]+colored('(Zone,Tile,OrbitNumber)','red'),'blue'))
        print(colored('    Metadata Type  :','green')+ colored(identifier_strings[4]+' Version:'+identifier_strings[5][1]+colored('(See Handbook for description)','red'),'blue'))
        #------------------------------------------------------------------------------------------------------------------------
        
        #Files to take data from --Customized for now
    
        Band_file_no_1=str(self.unzipped_directory)+'/'+directory_strings[-1]+'_FRE_B2.tif'
        Band_file_no_2=str(self.unzipped_directory)+'/'+directory_strings[-1]+'_FRE_B4.tif'
        Band_file_no_3=str(self.unzipped_directory)+'/'+directory_strings[-1]+'_FRE_B8.tif'
        Band_file_no_4=str(self.unzipped_directory)+'/'+directory_strings[-1]+'_FRE_B11.tif'

        Cloud_mask_file=str(self.unzipped_directory)+'/MASKS/'+directory_strings[-1]+'_CLM_R1.tif'
        Cloud_mask_file_20m=str(self.unzipped_directory)+'/MASKS/'+directory_strings[-1]+'_CLM_R2.tif'

        Edge_mask_file=str(self.unzipped_directory)+'/MASKS/'+directory_strings[-1]+'_EDG_R1.tif'

        list_of_file_to_read=[Band_file_no_1,Band_file_no_2,Band_file_no_3,Band_file_no_4,Cloud_mask_file,Cloud_mask_file_20m,Edge_mask_file]

        print('')
        print(colored('***Files to be used for processing***','cyan'))

        print('')
        for file_to_read in list_of_file_to_read:
            print(colored(file_to_read,'green'))
            print('')
        
        return list_of_file_to_read 
