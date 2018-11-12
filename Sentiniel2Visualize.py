from Sentiniel2Logger import Info,TiffReader,ViewData
import argparse,os,numpy as np,matplotlib.pyplot as plt 
parser = argparse.ArgumentParser()
parser.add_argument("Dir", help="Directory of Uncompressed Data",type=str)
args = parser.parse_args()
directory=args.Dir
def main(dirc):

    InfoOBJ=Info(dirc)
    TDIR=InfoOBJ.OutputDir('TIFF')
    CFILE=TDIR+'/5.0.1_MAP_SHORE.tiff'
    TRDR=TiffReader(dirc)
    Data=TRDR.GetTiffData(CFILE)
    
    return Data 

if __name__=='__main__':
    DataPath=directory
    Zones=[ 'T46QCK','T45QWE', 'T45QXE', 'T45QYE', 'T46QBK', 'T46QBL']
    for zone in Zones:
        DataPath=DataPath+str(zone)+'/'
        print('Executing Module for zone:'+str(zone))
        DataFolders=os.listdir(path=DataPath)
        
        TRDR=TiffReader(directory)
        ZFILE=str(os.getcwd())+'/DataPreprocess/Zone/'+str(zone)+'__Zone.tiff'
        ZoneData=TRDR.GetTiffData(ZFILE)
        v=1
        for df in DataFolders:
            
            dirc=DataPath+df+'/'
            print(dirc)
            data=main(dirc)
            ZoneData[data==1]=v+1
            v=v+1
        
        DataPath=directory
        plt.figure('SHORELINES:'+str(zone))
        plt.title('SHORELINES:'+str(zone))
        plt.imshow(ZoneData)
        plt.show()
        plt.clf()
        plt.close()
    