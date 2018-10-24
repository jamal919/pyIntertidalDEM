# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from osgeo import osr
from .tiffreader import TiffReader
from mpl_toolkits.basemap import Basemap

class DataPlotter(object):

    '''
        The purpose of this class is to view specific data as Plot or Print the data
    '''

    def __init__(self,ReferenceGeoTiffDir,OutputDir):
        
        __NoDataFile=ReferenceGeoTiffDir #Reference 
        
        Reader=TiffReader()
       
        self.OUTdir=OutputDir
       
        __DataSet=Reader.ReadTiffData(__NoDataFile)
        GeoTransForm=__DataSet.GetGeoTransform()
        Projection=__DataSet.GetProjection()
        __DataSet=Reader.GetTiffData(__NoDataFile)
        [row,col]=np.shape(__DataSet)
        __DataSet=None

        xdiff=1000
        ydiff=1000
        ceilx=-(-row//xdiff)
        ceily=-(-col//ydiff)
        xps=np.arange(0,ceilx*xdiff,xdiff)
        yps=np.arange(0,ceily*ydiff,ydiff)
        
        [__x_offset,__pixel_width,__rotation_1,__y_offset,__rotation_2,__pixel_height]=GeoTransForm
        __pixel_Coordinate_X=xps
        __pixel_Coordinate_y=yps
        __Space_coordinate_X= __pixel_width * __pixel_Coordinate_X +   __rotation_1 * __pixel_Coordinate_y + __x_offset
        __Space_coordinate_Y= __rotation_2* __pixel_Coordinate_X +    __pixel_height* __pixel_Coordinate_y + __y_offset
        
        ##get CRS from dataset
        __Coordinate_Reference_System=osr.SpatialReference()                     #Get Co-ordinate reference
        __Coordinate_Reference_System.ImportFromWkt(Projection)                  #projection reference

        ## create lat/long CRS with WGS84 datum<GDALINFO for details>
        __Coordinate_Reference_System_GEO=osr.SpatialReference()
        __Coordinate_Reference_System_GEO.ImportFromEPSG(4326)                   # 4326 is the EPSG id of lat/long CRS

        __Transform_term = osr.CoordinateTransformation(__Coordinate_Reference_System, __Coordinate_Reference_System_GEO)
        Latitude=np.zeros(np.shape(yps)[0])
        Longitude=np.zeros(np.shape(xps)[0])
        for idx in range(0,np.shape(yps)[0]):
            (__latitude_point, __longitude_point, _ ) = __Transform_term.TransformPoint(__Space_coordinate_X[idx], __Space_coordinate_Y[idx])
            Latitude[idx]=__latitude_point
            Longitude[idx]=__longitude_point
        self.__XPS=xps
        self.__YPS=yps
        self.__Lats=np.round(Latitude,decimals=4) 
        self.__Lons=np.round(Longitude,decimals=4)

    def PlotWithGeoRef(self,Variable,VariableIdentifier,PlotImdt=False):
        
        '''
            Plots the data with Geo reference
        '''


        print('plotting data:'+VariableIdentifier)
        low=np.nanmin(Variable)
        high=np.nanmax(Variable)
        
        V=np.linspace(low,high,10,endpoint=True)
        
        plt.figure(VariableIdentifier)
            
        plt.title(VariableIdentifier)
        
        plt.grid(True)

        plt.xticks(self.__XPS,self.__Lats)

        plt.yticks(self.__YPS,self.__Lons)
   
        plt.imshow(Variable)

        plt.colorbar(ticks=V)

        
        plt.savefig(self.OUTdir+VariableIdentifier+'.png')
        
        if (PlotImdt==True):
            plt.show() 
        
        #clear memory
        plt.clf()
        
        plt.close()

    def plotInMap(self,data):
        print('Plotting in Map ref')
        cmap='GnBu'
        LatMax=np.amax(self.__Lats)
        LatMin=np.amin(self.__Lats)
        LonMax=np.amax(self.__Lons)
        LonMin=np.amin(self.__Lons)
        extent=[LatMin,LatMax,LonMin,LonMax] #LL=0,2 UR=1,3
        
        savename=self.OUTdir+'test.png'

        plotbound = extent
        _, ax = plt.subplots(figsize=(9, 9))
        ax = Basemap(llcrnrlon=plotbound[0], llcrnrlat=plotbound[2], urcrnrlon=plotbound[1],
                    urcrnrlat=plotbound[3], projection='merc', resolution='f')
        img = ax.imshow(data, extent=extent, origin='upper', cmap=cmap, vmax=1, vmin=0)
        ax.drawparallels(circles=np.arange(np.round(plotbound[2], 1), np.round(plotbound[3], 2), 0.2), labels=[True, False, False, True], dashes=[2, 2])
        ax.drawmeridians(meridians=np.arange(np.round(plotbound[0], 1), np.round(plotbound[1], 2), 0.2), labels=[True, False, False, True], dashes=[2, 2])
        ax.colorbar(img, location='right')
        print('Saving figure')
        plt.savefig(savename)
        plt.show()