#!/usr/bin/env python3
from DataList import ListTrainingData
import numpy as np
import cv2
import matplotlib.pyplot as plt

    
def test(TDF):
    JPGPath='/home/ansary/Sentiniel2/Data/'+str(TDF)+'/'+str(TDF)+'_QKL_ALL.jpg'
    img = cv2.imread(JPGPath,cv2.IMREAD_GRAYSCALE) # reads image as grayscale
    plt.imshow(img, cmap='gray')
    plt.show()
def main():
    TrainData=ListTrainingData()
    test(TrainData[0])

if __name__=='__main__':
    main()
