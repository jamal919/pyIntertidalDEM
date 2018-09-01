#!/usr/bin/env python3
import os

Zones=[]
Dates=[]
TrainDataIdx=[]


def ZoneTime(DataFolders):
    for dirs in DataFolders:
        IdentifierStrings=dirs.split('_')    
        DateTimeStamp=IdentifierStrings[1].split('-') 
        Date=DateTimeStamp [0][6:]+'-'+DateTimeStamp[0][4:6]+'-'+DateTimeStamp[0][0:4]
        Zone=IdentifierStrings[3]
        Zones.append(Zone)
        Dates.append(Date)    

def ListDates(UniqueZones):
    print('-------------List of Dates for specific Zones----------------------')
    for Uzone in UniqueZones:
        idx=[i for i,e in enumerate(Zones) if e==Uzone ]
        DatesString=''
        TrainDataIdx.append(idx[0])
        for i in idx:
            
            d=Dates[int(i)]
            DatesString=DatesString+' '+d+' '
        print(Uzone+':'+DatesString)
            

def ListTrainingData():
    DataPath='/home/ansary/Sentiniel2/Data/'
    DataFolders=os.listdir(path=DataPath)
    ZoneTime(DataFolders)
    UniqueZones=list(set(Zones))
    ListDates(UniqueZones)
    TrainData=[]
    for idx in TrainDataIdx:
        TrainData.append(DataFolders[int(idx)])
    print('-----List of training data ------ ')
    for td in TrainData:
        print(td)
    return TrainData
    
TD=ListTrainingData()