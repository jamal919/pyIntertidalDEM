#!/usr/bin/env python3

import time
from termcolor import colored
import sys
from osgeo import gdal,osr
import numpy as np
import gc
import matplotlib                      
import scipy.signal                    

class RGB_Data_extractor(object):

    def __init__(self,data_files):

        self.data_files=data_files
    #extracting band data 
    def file_data_validation(self,given_file):
        start_time = time.time()
        
        print('')
        print(colored('Validating data File:'+colored(given_file,'blue'),'red'))

        data_array=None
        
        try:
            data_set=gdal.Open(given_file,gdal.GA_ReadOnly)   #taking readonly data
        
        except RuntimeError as e_Read:                       #Error handling
            print(colored('Error while opening file!','red'))
            print(colored('Error Details:','blue'))
            print(e_Read)
            sys.exit(1)
        
        #Mostly single band files are needed for construction 
        if(data_set.RasterCount==1):                          
            try:
                raster_band_data=data_set.GetRasterBand(1)
                data_array=raster_band_data.ReadAsArray()
                #debug_print_value(data_array,'data_array')
            except RuntimeError as e_arr:                      #Error handling
                print(colored('Error while data extraction file!','red'))
                print(colored('Error Details:','blue'))
                print(e_arr)
                sys.exit(1)
        else:
            print('The file contains multiple bands','red')
            sys.exit(1)
        
        
        #Mannual cleanup
        data_set=None
        raster_band_data=None
        
        print(colored('Data Validation Done!','cyan'))
        
        print(colored("Elapsed Time: %s seconds " % (time.time() - start_time),'yellow'))
        
        return data_array
    #Section--Mask Processing       
    def Decimals_with_end_Bit_detection(self,max_value):
        result=[]

        for i in range(0,max_value+1):
            bin_str=format(i,'08b')
            if(bin_str[-1]=='1'):
                result.append(i)
        return result
    def CLOUD_MASK_CORRECTION(self,Cloud_mask_data,Band_data,Data_Identifier):
        start_time = time.time()
        #process 
            #detect max value of array(<=255)
            #get vaules whose binary ends with 1 and change band_data
        print('')
        print(colored('processing cloud mask with:'+colored(Data_Identifier,'blue'),'green'))

        value_decimals=self.Decimals_with_end_Bit_detection(np.amax(Cloud_mask_data))

        for v in range(0,len(value_decimals)):
            Band_data[Cloud_mask_data==value_decimals[v]]=-10000            #Exclude data point Identifier= - Reflectance value

        print(colored("Elapsed Time: %s seconds " % (time.time() - start_time),'yellow'))
        
        return Band_data
    #Section--RGBConstruction 
    def RGB_Construction(self):

        gdal.UseExceptions()                                     #Throw any exception while processing with GDAL  


        start_time = time.time()

        band_files=self.data_files[0:4]                               #B2,B4,B8
        
        mask_files=self.data_files[4:]                                #Cloud,Cloud_20m
        
        
        
        #File data extraction
        #B2==Blue band
        B2_band_data=self.file_data_validation(band_files[0])
        
        #B4==Red band
        B4_band_data=self.file_data_validation(band_files[1])
        
        #B8=NIR band
        B8_band_data=self.file_data_validation(band_files[2])
        
        #B11=SWIR band
        B11_band_data=self.file_data_validation(band_files[3])
        
        #CLM
        Cloud_mask_data=self.file_data_validation(mask_files[0])
        
        #CLM_R2
        Cloud_mask_data_20m=self.file_data_validation(mask_files[1])

        #EDG
        #Edge_mask_data=file_data_validation(mask_files[2])
        
        #cloud masking correction(bit 1)
    
        B2_band_data=self.CLOUD_MASK_CORRECTION(Cloud_mask_data,B2_band_data,'Edge_corrected_B2')
        
        B4_band_data=self.CLOUD_MASK_CORRECTION(Cloud_mask_data,B4_band_data,'Edge_corrected_B4')
        
        B8_band_data=self.CLOUD_MASK_CORRECTION(Cloud_mask_data,B8_band_data,'Edge_corrected_B8')


        #B11 with 20m CLM
        B11_band_data=self.CLOUD_MASK_CORRECTION(Cloud_mask_data_20m,B11_band_data,'Edge_corrected_B11')


        # Repeating rows and coloumns to increase data points(discuss)
        B11_band_data=np.array(B11_band_data.repeat(2,axis=0).repeat(2,axis=1))


        
        #No data correction(-10000(REFLECTANCE_QUANTIFICATION_VALUE) value removal)
        B2_band_data[B2_band_data== -10000]=0

        B4_band_data[B4_band_data== -10000]=0

        B8_band_data[B8_band_data== -10000]=0
        
        B11_band_data[B11_band_data== -10000]=0
        
        
        print('')
        print(colored('*Normalizing data ','cyan'))
        #data normalization
        
        Blue_norm=B2_band_data/np.amax(B2_band_data)
        
        Red_norm =B4_band_data/np.amax(B4_band_data)

        NIR_norm =B8_band_data/np.amax(B8_band_data)

        SWIR_norm=B11_band_data/np.amax(B11_band_data)
        
        print('')
        print(colored('*Constructing RGB ','cyan'))
        
        #RGB Image construction from RGBa ---Equation 1
        Red_new  =(1- SWIR_norm)+(SWIR_norm*Red_norm)
        
        Green_new=(1- SWIR_norm)+(SWIR_norm*NIR_norm)
        
        Blue_new=(1- SWIR_norm)+(SWIR_norm*Blue_norm)


        [row,col]=np.shape(SWIR_norm)               #Row Col of the image
        
        dim=3                                       #RGB 
        
        RGB_data=np.zeros([row,col,dim])            #Black Background
        
        #RGB Data
        RGB_data[:,:,0]=Red_new
        RGB_data[:,:,1]=Green_new
        RGB_data[:,:,2]=Blue_new
        
        print('')
        print(colored('Cleanning Unnecessary Data','yellow'))
        
        #Data variables
        
        band_files=None
        mask_files=None

        B2_band_data=None
        B4_band_data=None
        B8_band_data=None
        B11_band_data=None

        Cloud_mask_data=None
        Cloud_mask_data_20m=None

        #Edge_mask_data=None

        Blue_norm=None
        Red_norm=None
        NIR_norm=None
        SWIR_norm=None

        Red_new=None
        Blue_new=None
        Green_new=None

        gc.collect()    
    
        print('')
        print(colored("Total Elapsed Time: %s seconds " % (time.time() - start_time),'green'))

        return RGB_data    

class Shoreline_data_extractor(object):

    def __init__(self,rgb_data):
        self.rgb_data=rgb_data
    
    def Shoreline_extraction(self):

        start_time = time.time()
        kernel_shore_base= np.array([[0,-1,0],[-1,4,-1],[0,-1,0]])

        print('')
        print(colored('*Reading RGB data ','cyan'))
        
        [row,col,_]=np.shape(self.rgb_data)

        #hsv conversion
        print('')
        print(colored('*Converting RGB to HSV ','cyan'))
        
        hsv_data=matplotlib.colors.rgb_to_hsv(self.rgb_data)

        #--1
        self.rgb_data=None    
        
        print('')
        print(colored("Total Elapsed Time: %s seconds " % (time.time() - start_time),'green'))

        #hue,Saturation and value channel separation
        print('')
        print(colored('*Extracting Hue and Val data ','cyan'))
        
        
        hue_data=hsv_data[:,:,0]
        val_data=hsv_data[:,:,2]


        #--1
        hsv_data=None 

        
        print('')
        print(colored('*Calculating Constraints ','cyan'))
        
        #hue channel constants
        n_hue=0.5                     #scaling factor(question)
        T_hue=np.median(hue_data)     #Median
        sig_hue=np.std(hue_data)      #standard deviation
        
        #value channel constants
        n_val=0.5                     #scaling factor(question)
        T_val=np.median(val_data)     #Median 
        sig_val=np.std(val_data)      #standard deviation

        #HUE channel conditional constant 
        c1_hue=T_hue+n_hue*sig_hue
        c2_hue=T_hue-n_hue*sig_hue

        #Value channel conditional constant 
        c1_val=T_val+n_val*sig_val
        c2_val=T_val-n_val*sig_val


        
        #binary mapping as per equation 2 & 3
        print('')
        print(colored('*Mapping Water hue binary Data ','cyan'))

        IsWater_hue=np.ones([row,col])                              
        IsWater_hue[(hue_data<c1_hue) & (hue_data>c2_hue)]=0        

        print('')
        print(colored('*Mapping Water val binary Data ','cyan'))
        
        IsWater_val=np.zeros([row,col])
        IsWater_val[(val_data<c1_val) & (val_data>c2_val)]=1            

        
        #MapWater data
        Map_Water=np.zeros([row,col])
        Map_Water[(IsWater_val==1) & (IsWater_hue==1) ]=1
        
        #--1
        IsWater_hue=None
        IsWater_val=None
        #--1
        hue_data=None
        val_data=None

        

        print('')
        print(colored('*Calculating Convoluted Data ','cyan'))

        convoluted_data=scipy.signal.convolve2d(Map_Water[1:row-1,1:col-1],kernel_shore_base)
        
        print('')    
        print(colored("Total Elapsed Time: %s seconds " % (time.time() - start_time),'green'))

        
        Map_Shore=np.argwhere(convoluted_data>0)
        
        #--1
        convoluted_data=None
        Map_Water=None

        return Map_Shore

    def pixel_Coordinate_to_latitude_longitude(self,data_array,unzipped_directory):
        print('')
        print(colored('*Latitude Longitude Determination ','cyan'))
        
        start_time=time.time()

        Total_data_points=np.shape(data_array)[0]
        #Read Geo Transform data from Geotiff

        directory_strings=str(unzipped_directory).split('/')
        
        GeoTiff_file=str(unzipped_directory)+'/MASKS/'+directory_strings[-1]+'_EDG_R1.tif'

        try:
            data_set=gdal.Open(GeoTiff_file,gdal.GA_ReadOnly)   #taking readonly data
        
        except RuntimeError as e_Read:                       #Error handling
            print(colored('Error while opening file!','red'))
            print(colored('Error Details:','blue'))
            print(e_Read)
            sys.exit(1)

        [x_offset,pixel_width,rotation_1,y_offset,pixel_height,rotation_2]=data_set.GetGeoTransform()

        #pixel-coordinate to space-coordinate

        pixel_Coordinate_X=data_array[:,0]
        pixel_Coordinate_y=data_array[:,1]

        Space_coordinate_X= pixel_width * pixel_Coordinate_X +   rotation_1 * pixel_Coordinate_y + x_offset
        Space_coordinate_Y= rotation_2  * pixel_Coordinate_X + pixel_height * pixel_Coordinate_y + y_offset


        #shift to the center of the pixel
        Space_coordinate_X += pixel_width  / 2.0
        Space_coordinate_Y += pixel_height / 2.0

        ##get CRS from dataset
        Coordinate_Reference_System=osr.SpatialReference()                     #Get Co-ordinate reference
        Coordinate_Reference_System.ImportFromWkt(data_set.GetProjectionRef()) #projection reference

        ## create lat/long CRS with WGS84 datum<GDALINFO for details>
        Coordinate_Reference_System_GEO=osr.SpatialReference()
        Coordinate_Reference_System_GEO.ImportFromEPSG(4326)                   # 4326 is the EPSG id of lat/long CRS

        Transform_term = osr.CoordinateTransformation(Coordinate_Reference_System, Coordinate_Reference_System_GEO)

        
        
        latitude_data=np.zeros(Total_data_points)
        longitude_data=np.zeros(Total_data_points)
        
        

        for indice in range(0,Total_data_points):
            (latitude_point, longitude_point, _ ) = Transform_term.TransformPoint(Space_coordinate_X[indice], Space_coordinate_Y[indice])
            
            latitude_data[indice]=latitude_point
            longitude_data[indice]=longitude_point
            


        print('')
        print(colored("Total Elapsed Time: %s seconds " % (time.time() - start_time),'green'))

        return np.column_stack((latitude_data,longitude_data))
