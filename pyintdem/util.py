#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np
import zipfile
import time
from datetime import datetime
from glob import glob
import os

class Extractor(object):
    def __init__(self, input_dir, output_dir):
        '''
        DataExtractor Class implements the functionality to discover data in 
        a directory and extract them to a target directory arranged by the tiles.

        arguments:
            input_dir: string
                Location of the zip data directory, the subdirectories are searched
                automatically.
            output_dir: string
                Location to save the extracted data. If the directory does not
                exist, it will be created. 
        '''
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.zones = dict()
        
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

    def list_zones(self, debug=False):
        '''
        List the zones available in the data files and store them to self.zones

        arguments:
            debug: boolean
                prints useful debug information
        '''
        for fname in glob(os.path.join(self.input_dir, '**', '*.zip'), recursive=True):
            basename = os.path.basename(fname).replace('.zip', '')
            zone = basename.split('_')[3]
            
            try:
                assert zone in self.zones
            except AssertionError:
                self.zones[zone] = []
            finally:
                self.zones[zone].append(fname)
        
        if debug:
            # Number of zones
            if len(self.zones) <= 1:
                print('We have found {:d} zone'.format(len(self.zones)))
            else:
                print('We have found {:d} zone(s)'.format(len(self.zones)))

            # Zone wise tile number
            for zone in self.zones:
                print('- {:s} : {:d} tiles'.format(zone, len(self.zones[zone])))
            
    def extract(self, zone):
        '''
        Extract the zip files for a particular zone listed using list_zones()

        arguments:
            zone: string
                zone id to be extracted
        '''

        try:
            assert zone in self.zones
        except AssertionError:
            print('{:s} - Not found! Use list_zones method to list all tiles.'.format(zone))
        else:
            zone_dir = os.path.join(self.output_dir, zone)
            print('|- Extracting {:d} {:s} tiles to - {:s}'.format(len(self.zones[zone]), zone, zone_dir))
            
            if not os.path.exists(zone_dir):
                os.mkdir(zone_dir)

            for fname in self.zones[zone]:
                start_time = time.time()
                zfile = zipfile.ZipFile(file=fname)
                zfile.extractall(zone_dir)
                zfile.close()
                print('\t|- Extracted : {zone_name:s} - {file_name:s} in {te:s}'.format(
                    zone_name=zone,
                    file_name=os.path.basename(fname),
                    te=str(time.time()-start_time)
                ))