# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import numpy as np
import calendar
import matplotlib.pyplot as plt

class STATGen(object):
    def __init__(self,wkdir,prepdir):
        self.__DataDir=wkdir
        self.__OutDir=os.path.join(prepdir,'Statistics','')
        if not os.path.exists(self.__OutDir):
            os.mkdir(self.__OutDir)

    def PlotMonthlyData(self):
        TICKS=[]
        XT=[]
        for i in range(1,13):
            TICKS.append(str(calendar.month_abbr[i]))        
        for i in range(1,32):
            XT.append(str(i))

        OutDir=os.path.join(self.__OutDir, 'DataAcquisition','')
        if not os.path.exists(OutDir):
            os.mkdir(OutDir)
        
        
        
        Zones=os.listdir(self.__DataDir)

        for zone in Zones:
            DataMat=np.zeros((12,31))
            
            DataPath=os.path.join(self.__DataDir, str(zone))
            
            print('Counting Data for zone:'+str(zone))
            
            DataFolders=os.listdir(DataPath)
            
            NOofData=str(len(DataFolders))
            
            for df in DataFolders:
                Identifier=str(df).split('_')
                
                DateTime=Identifier[1].split('-')
                
                Month=int(DateTime[0][4:6])
                
                Date=int(DateTime[0][6:])
                
                DataMat[Month-1][Date-1] +=1
           
            y_pos = np.arange(12)
           
            fig, ax = plt.subplots(figsize=(6, 5), dpi=120, tight_layout=True)
           
            ax.set_title('Zone:'+str(zone)+'\n Total data:'+NOofData)
            im = ax.imshow(DataMat)
            fig.colorbar(im, ax=ax, orientation='horizontal')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(TICKS)
            ax.set_xticks(np.arange(31))
            ax.set_xticklabels(XT)
            
            plt.savefig(os.path.join(OutDir, str(zone)+'.png'))
            plt.clf()
            plt.close()
