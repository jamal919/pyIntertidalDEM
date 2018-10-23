# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import zipfile
import time
from glob import glob
import improc
class DataExtractor(object):
    def __init__(self, indir, outdir):
        self.InputDir = indir
        self.DataDir = os.path.join(outdir, 'Data')
        
        if not os.path.exists(self.DataDir):
            os.mkdir(self.DataDir)
    
    def __ListZones(self):
        AllZones=[]
        for Path in glob(os.path.join(self.InputDir, '**/*.zip'),recursive=True):
            File = os.path.basename(Path).replace('.zip', '')
            Zones = File.split('_')[3]
            AllZones.append(Zones)
            
        ZoneSet=set(AllZones)
        self.Zones=list(ZoneSet)
        
    
    def __CreateZoneDirectories(self):
        self.ZoneDirs=[]
        for zone in self.Zones:
            DirFolder=os.path.join(self.DataDir, str(zone))
            if not os.path.exists(DirFolder):
                os.mkdir(DirFolder)
            self.ZoneDirs.append(DirFolder)
        self.ZoneDirs
    
    def __UnzipToZoneDirs(self):
        for i in range(0,len(self.Zones)):
            print('Extracting All Data for Zone-'+str(self.Zones[i]))
            for Path in glob(os.path.join(self.InputDir, '**/*.zip'),recursive=True):
                start_time=time.time()
                ZipFileUnex=zipfile.ZipFile(str(Path),'r')
                print('Unzipping :', str(Path))
                ZipFileUnex.extractall(str(self.ZoneDirs[i]))
                ZipFileUnex.close()
                print('Time Taken:' + str(time.time()-start_time))

                        
    def StartExtracting(self):
        self.__ListZones()
        self.__CreateZoneDirectories()
        self.__UnzipToZoneDirs()    

