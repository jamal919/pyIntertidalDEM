from Sentiniel2Logger import TiffReader,ViewData
import gc,sys
class AtmTest(object):
    def __init__(self,Directory):
        DirectoryStrings=str(Directory).split('/')             #split the directory to extract specific folder
        DirectoryStrings=list(filter(bool,DirectoryStrings))
        self.ATBFile=str(Directory)+DirectoryStrings[-1]+'_ATB_R1.tif'
        self.IAOMask=str(Directory)+'/MASKS/'+DirectoryStrings[-1]+'_IAO_R1.tif'
        self.TiffReader=TiffReader(Directory)
        self.DataViewer=ViewData(Directory)

    def IAOdata(self):
        Data=self.TiffReader.GetTiffData(self.IAOMask)
        #self.DataViewer.PlotWithGeoRef(Data,'IAO Mask')
        return Data

    def ATBdata(self):
        __DataSet=self.TiffReader.ReadTiffData(self.ATBFile)
        try:
            __RasterBandData=__DataSet.GetRasterBand(2)      
            __data=__RasterBandData.ReadAsArray()
            #manual cleanup
            __DataSet=None
            __RasterBandData=None
            gc.collect()
                
        except RuntimeError as e_arr:                                   #Error handling
            print('Error while data extraction file!')
            print('Error Details:')
            print(e_arr)
            sys.exit(1)
        self.DataViewer.PlotWithGeoRef(__data,'AOT')
