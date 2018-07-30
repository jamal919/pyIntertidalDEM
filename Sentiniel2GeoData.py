'''    
class Shoreline_data_extractor(object):


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
    '''