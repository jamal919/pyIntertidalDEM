import os,argparse
import numpy as np,matplotlib.pyplot as plt 
import calendar
parser = argparse.ArgumentParser()
parser.add_argument("Dir", help="Directory of Uncompressed Data",type=str)
args = parser.parse_args()
directory=args.Dir

def CreateRange():
    Y2017=[]
    Y2018=[] 
    for i in range(1,13):
        if(i<10):
            Y2017.append(int('20170'+str(i)))
            Y2018.append(int('20180'+str(i)))
        else:
            Y2017.append(int('2017'+str(i)))
            Y2018.append(int('2018'+str(i)))
    Y=Y2017+Y2018
    Ystr=[]
    for i in range(0,len(Y)):
        if (i==0 or i==12):
            YS=str(Y[i])
            year=YS[0:4]
            month=int(YS[4:])
            month=calendar.month_abbr[month]
            stamp=year+'-'+str(month)
            Ystr.append(stamp)
        else:
            YS=str(Y[i])
            month=int(YS[4:])
            month=calendar.month_abbr[month]
            stamp=str(month)
            Ystr.append(stamp)
    return {'Y':Y,'STRY':Ystr}


 
def PlotMonthlyData(directory):
    BINLST=np.array(CreateRange()['Y'])
    TICKS=CreateRange()['STRY']
   
    OutDir=str(os.getcwd())+'/DataAcquisition/'
    if not os.path.exists(OutDir):
        os.mkdir(OutDir)
    
    


    DATASTAMPS=[]
    DataPath=directory
    Zones=os.listdir(directory)
    for zone in Zones:
        DataPath=DataPath+str(zone)+'/'
        print('Counting Data for zone:'+str(zone))
        DataFolders=os.listdir(path=DataPath)
        for df in DataFolders:
            Identifier=str(df).split('_')
            DateTime=Identifier[1].split('-')
            Month=DateTime[0][4:6]
            Year=DateTime[0][0:4]
            YMSTAMP=int(str(Year)+str(Month))
            DATASTAMPS.append(YMSTAMP)
        DataPath=directory
        DATASTAMPS=sorted(DATASTAMPS,key=int)
        DATASTAMPS=np.array(DATASTAMPS)
        DATES,COUNTS=np.unique(DATASTAMPS,return_counts=True)
        DATACOUNTS=np.zeros(len(BINLST))
        for i in range (0,len(DATES)):
            DATACOUNTS[BINLST==DATES[i]]=COUNTS[i]
    

        
        
        
        y_pos = np.arange(len(BINLST))
        
        plt.figure('Data Count for:'+str(zone))
        plt.title('Histogram of Monthly data acquisition:'+str(zone))
        plt.bar(y_pos, DATACOUNTS, align='center', alpha=1)
        plt.xticks(y_pos, TICKS)
        plt.xlabel('Time')
        plt.ylabel('No of Data Sets')
        manager = plt.get_current_fig_manager()
        manager.resize(*manager.window.maxsize())

        plt.savefig(OutDir+str(zone)+'.png')
        plt.clf()
        plt.close()


        DATASTAMPS=[]

if __name__=='__main__':
    PlotMonthlyData(directory)
    