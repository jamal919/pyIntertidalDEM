#!/usr/bin/env python3
import os,zipfile,time


def ListZones(Directory):
    AllZones=[]
   
    for _,_,Files in os.walk(Directory):
        for dFile in Files:
            if str(dFile).endswith(('.zip')):
                dFile=str(dFile).replace('.zip','')
                DirectoryStrings=str(dFile).split('/')             #split the directory to extract specific folder
                DirectoryStrings=list(filter(bool,DirectoryStrings))
                IdentifierStrings=DirectoryStrings[-1].split('_')    #split the specific folder data identifiers
                Zone=IdentifierStrings[3] 
                AllZones.append(Zone)
    
    ZoneSet=set(AllZones)
    
    Zones=list(ZoneSet)
    
    return Zones

def CreateDirectories(Zones):
    directory=input('Enter The Directory You want to Unzip The Data#')
    directory=directory+'Unzipped Data/'
    if not os.path.exists(directory):
            os.mkdir(directory)
    ZoneDirs=[]
    for zone in Zones:
        DirFolder=directory+str(zone)+'/'
        if not os.path.exists(DirFolder):
            os.mkdir(DirFolder)
        ZoneDirs.append(DirFolder)
    return ZoneDirs

def UnzipToZoneDirs(ZoneDirs,Directory,Zones):
    print('Data Extraction Can Take some time.Please Wait patiently')
    print('For Our Testing: Extracting Data From one portable HDD to another portable HDD took 160 seconds average')
    print('Test PC Config:')
    print('--OS: Ubuntu 18.04 LTS/ Bionic Beaver')
    print('--Processor: Intel® Core™ i5-8250U CPU @ 1.60GHz × 8 ')
    print('--Ram: 8GB (DDR 4)')
    for i in range(0,len(Zones)):
        print('Extracting All Data for Zone-'+str(Zones[i]))
        
        for dirpath,_,Files in os.walk(Directory):
        
            for dFile in Files:
                if str(dFile).endswith(('.zip')) and (dFile.find(str(Zones[i])) != -1):
                    start_time=time.time()
                    ZipFileUnex=zipfile.ZipFile(str(os.path.abspath(os.path.join(dirpath, dFile))),'r')
                    print('Unzipping :',str(ZipFileUnex))
                    ZipFileUnex.extractall(str(ZoneDirs[i]))
                    ZipFileUnex.close()
                    print('Time Taken:'+str(time.time()-start_time))

    print('**Complete Data Extraction Completed') 
    print('Proceed To create WaterMask with Sentiniel2WaterMask.py')


def main():
    Directory=input('Enter The Directory To The zipped Data #')
    Zones=ListZones(Directory)
    print('**The zipped Data contains following zones**')
    print(Zones)
    
    ZoneDirs=CreateDirectories(Zones)
    UnzipToZoneDirs(ZoneDirs,Directory,Zones)
    
if __name__=='__main__':
    main()
