# -*- coding: utf-8 -*-
'''
Vertical referencing using simulated or observed water levels. This module 
provides classes to make water level predictions using utide, vertically
reference the shorelines using predicted water levels, and production of final
merged DEM product. 

Author: khan
Email: jamal.khan@legos.obs-mip.fr
'''
from __future__ import print_function
import numpy as np
from scipy.spatial import distance
from pyproj import Proj
from glob import glob
import csv
import os

class Dem(object):
    def __init__(self, improc_dir, waterlevel_dir, vertref_dir):
        '''
        The Dem object is expected to load the shorelines, vertically reference
        with proper water level and finally return the Dem developed from the 
        consjunction of water level and shoreline information.

        Currently the implementation loads the water level, vertically reference
        it and store the single vertically referenced file. 
        '''
        self.__csvdir = improc_dir 
        self.__wldir = waterlevel_dir
        self.__outdir = vertref_dir

    def __create_out_dir(self,zone):
        '''
        Creates the output directory for each zone at outdir location. 
        '''
        self.outcsvdir = os.path.join(self.__outdir, zone) 
            
        if not os.path.exists(self.outcsvdir):
            os.mkdir(self.outcsvdir)

    def __list_wl_nodes(self,zone):
        '''
        Given the zone name, this function looks for a <zone>.dat file in water
        level directory and loads the corresponding node points where the water
        level was extracted.

        Currently the <zone>.dat file has a header indicating the number of points
        in the following lines - so skip_header=1 was used. 
        '''
        stationfileloc = os.path.join(self.__wldir, str(zone), str(zone)+'.dat')
        nodes = np.genfromtxt(fname=stationfileloc, dtype=float, skip_header=1)
        return nodes

    def __find_dat_file(self, fname, zone):
        '''
        Given the fname of the original shoreline csv file and, tile it belongs 
        to, this function finds the corresponding file with waterlevel information.
        Currently, the waterlevel are expected to be in yyyymmddhhmmss.csv format.
        '''
        pathstr = os.path.basename(fname)
        identifier = pathstr.replace('.csv','')
        identifier = str(identifier).replace('5.0.','')
        date = str(identifier).split('_')[0]
        time = str(identifier).split('_')[1]
        self.__file_identifier = identifier
        day = date.split('-')[0]
        month = date.split('-')[1]
        year = date.split('-')[2]

        hour = time.split('-')[0]
        minute = time.split('-')[1]
        seconds = time.split('-')[2]
        
        datidentifier = year + month + day + hour + minute + seconds #name of dat file
        datfile = os.path.join(self.__wldir,str(zone),str(datidentifier)+'.dat')
        return datfile

    def __find_heights(self, datfile):
        '''
        Return the corresponding water level information only from a comodo
        produced water level file. 
        '''
        with open(str(datfile)) as f:
            lines = f.readlines()
            data = lines[2]
                
        data = str(data).split()
        self.__time = data[0] + ' ' + data[1]
        del data[0] #Date
        del data[0] #time
        
        heightdata = np.array([float(i) for i in data]) #Height data for all given points
        return heightdata

    def __get_shoreline_points(self, csvfile):
        '''
        Reads shoreline csv files, without headers, comma delimited.
        Returns the lon, lat variables
        '''
        points = np.genfromtxt(fname=csvfile, delimiter=',')
        return points

    def __get_information(self, point, nodes):
        '''
        Calculate various informaiton regarding a given point and nodes from where
        the depth value will be interpolated.
        The output information is an array of time, lon, lat, nearest lon, nearest lat, distance, height. 
        '''
        btm = Proj('+proj=tmerc +lat_0=0 +lon_0=90 +k=0.9996 +x_0=500000 +y_0=0 +a=6377276.345 +b=6356075.41314024 +units=m +no_defs')
        x = point[0]
        y = point[1]
        x_btm, y_btm = btm(x, y) # find position in BTM
        node = [x_btm,y_btm]
        
        xs = nodes[:,0]
        ys = nodes[:,1]
        
        xs_btm,ys_btm = btm(xs,ys)
        nodes_btm = np.column_stack((xs_btm,ys_btm))
        dist_mat = distance.cdist([node], nodes_btm)
        
        closest_dist = dist_mat.min()
        closest_ind = dist_mat.argmin()
        
        time_info = self.__time
        lon_info = x
        lat_info = y
        nn_lon_info = nodes[closest_ind][0]
        nn_lat_info = nodes[closest_ind][1]
        distance_info = closest_dist
        height_info = self.heightdata[closest_ind]

        information = [time_info, lon_info, lat_info, nn_lon_info, nn_lat_info, distance_info, height_info]
        return information


    def __find_closest(self, nodes, csvfile):
        '''
        __find_closest finds the nearest lon,lat point from wl nodes for all the points
        given in csvfile generated by shoreline generation algorithm.
        '''

        outcsvfile = os.path.join(self.outcsvdir, self.__file_identifier+'.csv')

        points = self.__get_shoreline_points(csvfile)
        
        with open(outcsvfile,"w") as output:
            writer = csv.writer(output, lineterminator='\n')

            for point in points:
                information = self.__get_information(point,nodes)
                writer.writerow(information)

    def set_vetical_heights(self, zone):
        '''
        set_vetical_heights assembles a dem out of the given shoreline directory and water 
        level information. 
        '''
        self.__create_out_dir(zone)
        nodes = self.__list_wl_nodes(zone)
        
        for fname in glob(os.path.join(self.__csvdir, str(zone), '*', '*.csv')):
            datfile = self.__find_dat_file(fname, zone)
            print(zone, os.path.basename(datfile))
            self.heightdata = self.__find_heights(datfile)
            self.__find_closest(nodes, fname)