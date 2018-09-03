#!/usr/bin/env python3
#from DataList import ListTrainingData
from Sentiniel2Logger import ViewData,TiffReader,SaveData
import numpy as np
import matplotlib.pyplot as plt
    
def test(TDF):
    #Directory='/home/ansary/Sentiniel2/Data/'+TDF+'/'
    #TR=TiffReader(Directory)
    #DataFile='/home/ansary/Sentiniel2/RGBUNQ/'+TDF+'/Data.tiff'
    #Data=TR.GetTiffData(DataFile)
    #VD=ViewData(Directory)
    #VD.PlotWithGeoRef(Data,'Data')    
    #SD=SaveData(Directory)
    #Feature,CountsOfFeature = np.unique(Data, return_counts=True)
    #STORE=np.column_stack((Feature,CountsOfFeature))
    #SD.SaveDataAsCSV('Feature',STORE)
    ImagePath='/home/ansary/Sentiniel2/RGBData/'+TDF+'/'+'RGBData.jpg'
    img=plt.imread(ImagePath)
    plt.imshow(img)
    plt.show()

def main():
    #TrainData=ListTrainingData()
    test('SENTINEL2B_20171130-042157-149_L2A_T46QCK_D_V1-4')

if __name__=='__main__':
    main()
    plt.show()
    