# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np
import os
from glob import glob
from scipy.spatial import distance
import csv
from pyproj import Proj

class Dem(object):
    def __init__(self,wkdir,waterleveldir,vertrefdir):
       self.__csvdir=wkdir 
       self.__wldir=waterleveldir
       self.__outdir=vertrefdir

    def listStation(self,zone):
        
        lats=[]
        lons=[]
        stationfiledir=os.path.join(self.__wldir,str(zone),str(zone)+'.dat')
        with open(str(stationfiledir)) as f:
            lines=f.readlines()
            for line in lines:
                lat=line.split(' ')[0]
                lon=line.split(' ')[1]
                lon=str(lon).replace('\n','')
                lats.append(float(lat))
                lons.append(float(lon))
            nodes=np.column_stack((lats,lons))

        return nodes

    def __GetPoints(self,csvfile):

        lats=[]
        lons=[]
        with open(csvfile) as f:
            reader=csv.reader(f)
            for row in reader:
                lat=float(row[0])
                lon=float(row[1])
                lats.append(lat)
                lons.append(lon)
        points=np.column_stack((lats,lons))

        return points

    def __GetInformation(self,point,nodes):
        btm = Proj('+proj=tmerc +lat_0=0 +lon_0=90 +k=0.9996 +x_0=500000 +y_0=0 +a=6377276.345 +b=6356075.41314024 +units=m +no_defs')
        x=point[0]
        y=point[1]
        x_btm, y_btm = btm(x, y) # find position in BTM
        node=[x_btm,y_btm]
        
        xs=nodes[:,0]
        ys=nodes[:,1]
        
        xs_btm,ys_btm=btm(xs,ys)
        
        nodes_btm=np.column_stack((xs_btm,ys_btm))
       
        dist_mat = distance.cdist([node], nodes_btm)
        
        closest_dist = dist_mat.min()
        
        closest_ind = dist_mat.argmin()
       
        
        timeInfo=self.__time
        latInfo=x
        lonInfo=y
        nnlatInfo=nodes[closest_ind][0]
        nnlonInfo=nodes[closest_ind][1]
        distanceInfo=closest_dist
        heightInfo=self.heightdata[closest_ind]

        Information=[timeInfo,latInfo,lonInfo,nnlatInfo,nnlonInfo,distanceInfo,heightInfo]
        return Information


    def findClosest(self,nodes,csvfile):
        
        outcsvfile=os.path.join(self.OutCsvdir,self.__FILEIdent+'.csv')
        print('Saving information to:'+outcsvfile)

        points=self.__GetPoints(csvfile)
        
        with open(outcsvfile,"w") as output:

            writer=csv.writer(output,lineterminator='\n')

            for point in points:

                Information=self.__GetInformation(point,nodes)
               
                writer.writerow(Information)

        print('Done saving Information!(time, lon, lat, nnlon, nnlat, distance, height)')
        
    def __FinddatFile(self,Path,zone):
        pathstr=str(Path).split('/')
        identifier=str(pathstr[-1]).replace('.csv','')
        identifier=str(identifier).replace('5.0.','')
        date=str(identifier).split('_')[0]
        time=str(identifier).split('_')[1]
        self.__FILEIdent=identifier
        day=date.split('-')[0]
        month=date.split('-')[1]
        year=date.split('-')[2]

        hour=time.split('-')[0]
        minute=time.split('-')[1]
        seconds=time.split('-')[2]
        
        datIdentifier=year+hour+month+day+minute+seconds  #name of dat file
        datfile=os.path.join(self.__wldir,str(zone),str(datIdentifier)+'.dat')
        return datfile

    def __findHeights(self,datfile):
        with open(str(datfile)) as f:
            lines=f.readlines()
            data=lines[2]
                
        data=str(data).split()
        del data[0] #Date
        self.__time=data[0]
        del data[0] #time
        heightdata=[float(i) for i in data] #Height data for all given points
        
        return heightdata

    def __createOutdir(self,zone):
        self.OutCsvdir=os.path.join(self.__outdir,zone,'')   #final output csv
            
        if not os.path.exists(self.OutCsvdir):
            os.mkdir(self.OutCsvdir)


    def setVertRef(self):
        Zones=os.listdir(self.__csvdir)
        for zone in Zones:
            
            self.__createOutdir(zone)

            nodes=self.listStation(zone)
            
            for Path in glob(os.path.join(self.__csvdir,str(zone), '*.csv')):
                
                datfile=self.__FinddatFile(Path,zone)
                
                self.heightdata=self.__findHeights(datfile)
                
                self.findClosest(nodes,Path)
                
                