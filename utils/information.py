# -*- coding: utf-8 -*-
import os
import sys
class Info(object):
    '''
        The purpose of this class is to collect useable data from the input data
    '''


    def __init__(self,directory):
        self.directory=directory                                           #The directory that contains the files(MASKS and Band Files)
        
        self.__DirectoryStrings=str(self.directory).split('/')             #split the directory to extract specific folder
        
        self.__DirectoryStrings=list(filter(bool,self.__DirectoryStrings))
        
        self.__IdentifierStrings=self.__DirectoryStrings[-1].split('_')    #split the specific folder data identifiers
       
        self.__DateTimeStamp=self.__IdentifierStrings[1].split('-')        #Time stamp data 

        __Date=self.__DateTimeStamp [0][6:]+'-'+self.__DateTimeStamp[0][4:6]+'-'+self.__DateTimeStamp[0][0:4]
        
        __Time=self.__DateTimeStamp[1][0:2]+'-'+self.__DateTimeStamp[1][2:4]+'-'+self.__DateTimeStamp[1][4:]
        
        self.DateTime=__Date+'_'+__Time
        
        self.SateliteName=self.__IdentifierStrings[0]
        
        self.Zone=self.__IdentifierStrings[3]
        
        
       

    
    
    def __DisplayProductInformation(self):
        '''
            Displays information about the data
        '''
        
        print('    Satelite Name  :'+ self.__IdentifierStrings[0])
        
        print('             Date  :'+ self.__DateTimeStamp [0][6:]+'-'+self.__DateTimeStamp[0][4:6]+'-'+self.__DateTimeStamp[0][0:4])
        
        print('             Time  :'+ self.__DateTimeStamp[1][0:2]+':'+self.__DateTimeStamp[1][2:4]+':'+self.__DateTimeStamp[1][4:]+':'+self.__DateTimeStamp[2])
        
        print('     Product Type  :'+ self.__IdentifierStrings[2])
        
        print('Geographical Zone  :'+ self.__IdentifierStrings[3])
        
        print('    Metadata Type  :'+ self.__IdentifierStrings[4]+' Version:'+self.__IdentifierStrings[5])
        
    def __DataFileList(self):

        '''
            Lists the files to be used for processing
            For our purposes 4 bands and 2 masks are used:

            |---------+------+------------+------------+
            | Band No | Type | Wavelength | Resolution |
            |---------+------+------------+------------+
            | B2      | Blue | 490nm      |         10 |
            | B4      | Red  | 665nm      |         10 |
            | B8      | NIR  | 842nm      |         10 |
            | B11     | SWIR | 1610nm     |         20 |
            |---------+------+------------+------------+

            The two Cloud masks contains cloud information for 10m and 20m resolutions 
        '''
        BlueBandFile=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B2.tif'
        
        RedBandFile=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B4.tif'

        GreenBandFile=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B8.tif'

        SWIRBandB11=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B11.tif'

        CloudMask10m=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_CLM_R1.tif'
        
        CloudMask20m=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_CLM_R2.tif'
        
        

        self.__Files=[RedBandFile,GreenBandFile,BlueBandFile,SWIRBandB11,CloudMask10m,CloudMask20m]

    
    def DefineDiectoriesAndReferences(self,ProcessedDataPath,PreprocessedDataPath,png=False):
        MASKDIR=os.path.join(PreprocessedDataPath,'WaterMask','')
        if not os.path.exists(PreprocessedDataPath):
            print('Water Mask Directory Not Found!')
            print('Preprocess the data to create WaterMap for the zone')
            sys.exit(1)

        MASKFILE=str(os.path.join(MASKDIR,self.Zone+'.tiff'))
        
        if not os.path.isfile(MASKFILE):
            print('Water Mask File  Not Found for zone:'+self.Zone)
            sys.exit(1)
        
        
        self.__OD=ProcessedDataPath

        self.ReferenceGeotiff=MASKFILE         #For TiffSaving And Plotting

        self.MainDir=os.path.join(ProcessedDataPath,self.Zone,self.DateTime+'_'+self.SateliteName,'')
        
        self.PNGOutDir=os.path.join(self.MainDir,'QucikLookPngFiles','')

        ODZ=os.path.join(self.__OD,self.Zone,'')
        if not os.path.exists(ODZ):
            os.mkdir(ODZ)
        ODZI=os.path.join(ODZ,self.DateTime+'_'+self.SateliteName,'')
        if not os.path.exists(ODZI):
            os.mkdir(ODZI)
        if png:
            ODZIP=os.path.join(ODZI,'QucikLookPngFiles','')
            if not os.path.exists(ODZIP):
                os.mkdir(ODZIP)
   
    
    def DisplayFileList(self):
        '''
            Display's data information

            Creates the List of files to be used

            Returns the file List
        '''
        self.__DisplayProductInformation()        
        
        self.__DataFileList()
        
        return self.__Files 