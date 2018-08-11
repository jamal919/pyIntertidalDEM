from termcolor import colored
from Sentiniel2Logger import Log 

class displayInfo(object):


    def __init__(self,directory):
        
        self.directory=directory                                           #The directory that contains the files(MASKS and Band Files)

        self.__DirectoryStrings=str(self.directory).split('/')             #split the directory to extract specific folder
        
        self.__IdentifierStrings=self.__DirectoryStrings[-1].split('_')    #split the specific folder data identifiers
        
        self.__DateTimeStamp=self.__IdentifierStrings[1].split('-')        #Time stamp data 

    def Banner(self):
        print('')
        print(colored('*********************************************************************************************','blue'))
        print(colored('****************************'+colored('        SENTINIEL2        ','red')+colored('***************************************','green'),'green'))
        print(colored('*********************************************************************************************','blue'))
        print('')
    
    def __DisplayProductInformation(self):
        
        print(colored('    Satelite Name  :','green')+ colored(self.__IdentifierStrings[0],'blue'))
        
        print(colored('             Date  :','green')+ colored(self.__DateTimeStamp [0][6:]+'-'+self.__DateTimeStamp[0][4:6]+'-'+self.__DateTimeStamp[0][0:4],'blue'))
        
        print(colored('             Time  :','green')+ colored(self.__DateTimeStamp[1][0:2]+':'+self.__DateTimeStamp[1][2:4]+':'+self.__DateTimeStamp[1][4:]+':'+self.__DateTimeStamp[2]+'(ms)','blue'))
        
        print(colored('     Product Type  :','green')+ colored(self.__IdentifierStrings[2]+colored('(See Handbook for description)','red'),'blue'))
        
        print(colored('Geographical Zone  :','green')+ colored(self.__IdentifierStrings[3]+colored('(Zone,Tile,OrbitNumber)','red'),'blue'))
        
        print(colored('    Metadata Type  :','green')+ colored(self.__IdentifierStrings[4]+' Version:'+self.__IdentifierStrings[5][1]+colored('(See Handbook for description)','red'),'blue'))
        
    def __DataFileList(self):
        
        BandFileB2=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B2.tif'
        
        BandFileB4=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B4.tif'
        
        BandFileB8=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B8.tif'
        
        BandFileB11=str(self.directory)+'/'+self.__DirectoryStrings[-1]+'_FRE_B11.tif'

        CloudMask10m=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_CLM_R1.tif'
        
        CloudMask20m=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_CLM_R2.tif'

        EdgeMask=str(self.directory)+'/MASKS/'+self.__DirectoryStrings[-1]+'_EDG_R1.tif'

        self.__Files=[BandFileB2,BandFileB4,BandFileB8,BandFileB11,CloudMask10m,CloudMask20m,EdgeMask]

    def __PrintFileList(self):
        
        self.__Logger=Log(self.directory)

        self.__Logger.PrintLogStatus('Listing Files To Be used')
        
        for f in self.__Files:
            print('')
            print(colored(f,'green'))
            print('')

    def DisplayFileList(self):
    
        self.__DisplayProductInformation()        
        
        self.__DataFileList()
    
        self.__PrintFileList()
        
        return self.__Files 
