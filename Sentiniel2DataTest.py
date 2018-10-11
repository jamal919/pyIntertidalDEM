#!/usr/bin/env python3
from Sentiniel2Logger import TiffReader,ViewData
import matplotlib.pyplot as plt,numpy as np,argparse,time,sys
parser = argparse.ArgumentParser()
parser.add_argument("Dir", help="Directory of Uncompressed Data",type=str)
args = parser.parse_args()
directory=args.Dir

def GetTiffData(DataSet,Num):
    try:
        __RasterBandData=DataSet.GetRasterBand(int(Num))
        
        __data=__RasterBandData.ReadAsArray()
        
    except RuntimeError as e_arr:                                   #Error handling
        print('Error while data extraction file!')
        print('Error Details:')
        print(e_arr)
        sys.exit(1)
    return __data

def main(directory):
    DirectoryStrings=str(directory).split('/')             #split the directory to extract specific folder
    DirectoryStrings=list(filter(bool,DirectoryStrings))
    DFile=str(directory)+str(DirectoryStrings[-1])+'_ATB_R1.tif'
    TiffR=TiffReader(directory)
    DataSet=TiffR.ReadTiffData(DFile)
    WVC=GetTiffData(DataSet,1)
    AOT=GetTiffData(DataSet,2)
    WVC=(WVC-np.nanmin(WVC))/(np.nanmax(WVC)-np.nanmin(WVC))
    AOT=(AOT-np.nanmin(AOT))/(np.nanmax(AOT)-np.nanmin(AOT))
    DataViewer=ViewData(directory)
    DataViewer.PlotWithGeoRef(WVC,'Water Vapour Content (Normalized)')
    DataViewer.PlotWithGeoRef(AOT,'Aerosol Optical Thickness (Normalized)')

    
    
    



if __name__=='__main__':
    main(directory)