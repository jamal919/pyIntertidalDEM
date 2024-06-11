#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zipfile
import time
from glob import glob
import os
import numpy as np
import tqdm
import logging

from .core import Band

logger = logging.getLogger(__name__)


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

    def list_zones(self):
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

        # Number of zones
        if len(self.zones) <= 1:
            logger.debug('We have found {:d} zone'.format(len(self.zones)))
        else:
            logger.debug('We have found {:d} zone(s)'.format(len(self.zones)))

        # Zone wise tile number
        for zone in self.zones:
            logger.debug('- {:s} : {:d} tiles'.format(zone, len(self.zones[zone])))

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
            logger.error('{:s} - Not found! Use list_zones method to list all tiles.'.format(zone))
        else:
            zone_dir = os.path.join(self.output_dir, zone)
            logger.info('|- Extracting {:d} {:s} tiles to - {:s}'.format(len(self.zones[zone]), zone, zone_dir))

            if not os.path.exists(zone_dir):
                os.mkdir(zone_dir)

            for fname in tqdm.tqdm(self.zones[zone], desc=zone):
                start_time = time.time()
                zfile = zipfile.ZipFile(file=fname)
                zfile.extractall(zone_dir)
                zfile.close()
                logger.info('\t|- Extracted : {zone_name:s} - {file_name:s} in {te:s}'.format(
                    zone_name=zone,
                    file_name=os.path.basename(fname),
                    te=str(time.time() - start_time)
                ))


def create_mask(database, maskdir, nmask=0.5, ext='tif', band='B11', normalize=True):
    for tile in database:
        fname = maskdir / f'{tile}.{ext}'
        datafiles = database[tile]
        for i, datafile in enumerate(datafiles):
            img_band = datafile.get_band(band, preprocess=True)

            if normalize:
                img_band.normalize(method='std', std_factor=1, std_correction='high')

            if i == 0:
                count_band = np.logical_not(np.isnan(img_band.data)).astype(int)
                mask = img_band
            else:
                count_band = count_band + np.logical_not(np.isnan(img_band.data)).astype(int)
                mask = mask.nan_sum(img_band)

        count_band = Band(data=count_band, geotransform=mask.geotransform, projection=mask.projection)
        mask = mask / count_band
        mask = mask < nmask * mask.std
        mask.to_geotiff(fname=fname.as_posix())
