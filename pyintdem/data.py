#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data and Metadata holder for different satellites
"""
import copy

import rasterio
from datetime import datetime
from glob import glob
import os
from pathlib import Path
import pandas as pd
import re
from .core import Band
import numpy as np
import json
from zipfile import ZipFile


class Sentinel2(object):
    def __init__(self, loc, datefmt='%Y%m%d-%H%M%S-%f'):
        """
        File information holder for unpacked Sentinel-2 images.

        arguments:
            loc: string
                Location of the unpacked tile of a single Sentinel-2 image
            datefmt: string
                Format string to extract the datetime

        returns:
            object: Sentinel2
        """
        self.loc = loc
        self.file_prefix = os.path.basename(self.loc)
        _metadata = self.file_prefix.split('_')
        self.files = dict()

        for floc in glob(os.path.join(self.loc, '*.*')):
            fname = os.path.basename(floc)
            fname = fname.split(sep=self.file_prefix)[-1][1:].split('.')[0]
            self.files[fname] = floc

        for subdir in glob(os.path.join(self.loc, '*/')):
            subdir_name = os.path.basename(subdir[:-1])  # Avoiding trailing sep
            self.files[subdir_name] = dict()
            for floc in glob(os.path.join(subdir, '*.*')):
                fname = os.path.basename(floc)
                fname = fname.split(sep=self.file_prefix)[-1][1:].split('.')[0]
                self.files[subdir_name][fname] = floc

        self.info = dict(
            dir=self.loc,
            file_prefix=self.file_prefix,
            satellite=_metadata[0],
            date_time=datetime.strptime(_metadata[1], datefmt),
            level=_metadata[2],
            zone=_metadata[3],
            meta=_metadata[4],
            version=_metadata[5]
        )

    def watermask(self, loc, id=['zone'], fmt='tif'):
        """
        Return the location of the water mask based on the id and format fmt.
        The id can be nested for a nested setup. The last element of the id will
        be used to infer the name of the file itself.

        arguments:
            loc: string
                Location of the mask files
            id: array of string
                organization of the mask file in folders. id[-1] is the name of
                the mask file.
            fmt: string
                file format extension without preceding dot

        returns:
            Mask file location: string
        """
        _maskfile = loc
        if len(id) > 1:
            for i in id[:-1]:
                _maskfile = os.path.join(_maskfile, self.info[i])

            _maskfile = os.path.join(_maskfile, '{:s}.{:s}'.format(self.info[id[-1]], fmt))
        elif len(id) == 1:
            _maskfile = os.path.join(loc, '{:s}.{:s}'.format(self.info[id[0]], fmt))

        return _maskfile

    def __repr__(self):
        repr_str = ''.join('{:<15s} : {:s}\n'.format(i, self.info[i].__repr__()) for i in self.info)
        return repr_str


def format_band_name(band_name):
    band_number = re.findall(r'\d+', band_name)

    if len(band_number) == 1:
        band_name = band_name.replace(band_number[0], str(int(band_number[0])))

    return band_name


def parse_copernicus(fpath):
    """Reads the Sentinel2 filename from theia and extract the relevant information

    # MMM_MSIXXX_YYYYMMDDHHMMSS_Nxxyy_ROOO_Txxxxx_<Product Discriminator>.SAFE
    # The products contain two dates.

    # The first date (YYYYMMDDHHMMSS) is the datatake sensing time.
    # The second date is the "<Product Discriminator>" field, which is 15 characters in length, and is used to distinguish 
    # between different end user products from the same datatake. Depending on the instance, the time in this field can be 
    # earlier or slightly later than the datatake sensing time.
    # The other components of the filename are:

    # MMM: is the mission ID(S2A/S2B)
    # MSIXXX: MSIL1C denotes the Level-1C product level/ MSIL2A denotes the Level-2A product level
    # YYYYMMDDHHMMSS: the datatake sensing start time
    # Nxxyy: the Processing Baseline number (e.g. N0204)
    # ROOO: Relative Orbit number (R001 - R143)
    # Txxxxx: Tile Number field
    # SAFE: Product Format (Standard Archive Format for Europe) / Equivalent to zip

    Referenec:
        https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi/naming-convention

    Args:
        fpath (path): Path to the file, for theia it is a zip file

    Returns:
        dict: A dictionary with filetype, fpath, mission, product, version, time, tile
    """
    fpath = Path(fpath)
    fname = fpath.name.split('.')[0]
    mission, product, sensing_date, baseline, relative_orbit, tileid, version = fname.split('_')

    return {
        'filetype': 'copernicus',
        'fpath': fpath,
        'mission': mission,
        'product': product,
        'version': version,
        'time': pd.to_datetime(sensing_date, format='%Y%m%dT%H%M%S'),
        'tile': tileid
    }


def parse_theia(fpath):
    """Reads the Sentinel2 filename from theia and extract the relevant information

    The data downloaded from Theia has following structure - 

        SENTINEL2A_20091211-165909-000_L2A_T14SLE_C_V1-0
         SATELLITE_YYYYMMDD-HHMMSS-SSS_LEV_TILE_META_VERSION 

    Reference:
        https://www.theia-land.fr/wp-content/uploads/2018/12/SENTINEL-2A_L2A_Products_Description.pdf

    Args:
        fpath (path): Path to the file, for theia it is a zip file

    Returns:
        dict: A dictionary with filetype, fpath, mission, product, version, time, tile
    """
    fpath = Path(fpath)
    fname = fpath.name.split('.')[0]
    mission, sensing_date, product, tile, meta_version, version = fname.split('_')

    return {
        'filetype': 'theia',
        'fpath': fpath.absolute().as_posix(),
        'mission': mission,
        'product': product,
        'version': version,
        'time': pd.to_datetime(sensing_date, format='%Y%m%d-%H%M%S-%f'),
        'tile': tile
    }


def map_theia_bands(fpath):
    fpath = Path(fpath)
    ds = {}
    with ZipFile(fpath) as f:
        fnames = list(filter(lambda x: x.split('_')[-2] == 'FRE', f.namelist()))
        bands = list(map(lambda x: x.split('_')[-1].split('.tif')[0], fnames))
        for band, fname in zip(bands, fnames):
            bandpath = f'/vsizip/{fpath.as_posix()}/{fname}'
            ds[band] = bandpath

    return ds


def map_copernicus_bands(fpath):
    ds = {}
    with rasterio.open(fpath) as f:
        for subds in f.subdatasets:
            with rasterio.open(subds) as f:
                band_files = list(filter(lambda x: x.split('.')[-1] == 'jp2', f.files))
                band_names = list(map(lambda x: x.split('_')[-2], band_files))

                for band_name, band_file in zip(band_names, band_files):
                    ds[format_band_name(band_name)] = band_file

    return ds


def preprocess_none(band):
    return band


def preprocess_theia(band):
    band.set_missing(-10000)
    band = band / 10000
    return band


def preprocess_copernicus(band):
    band.set_missing(0)
    band = band / 10000
    return band


available_parsers = [parse_theia, parse_copernicus]

data_mappers = {
    'theia': map_theia_bands,
    'copernicus': map_copernicus_bands
}

band_preprocessors = {
    'theia': preprocess_theia,
    'copernicus': preprocess_copernicus
}


class DataFile(dict):
    def __init__(self, mapper=None, **kwargs):
        super().__init__(self)
        self.update(kwargs)

        self['bands'] = map_bands(self, mapper=mapper)

    def get_band(self, name, number=1, preprocess=True):
        if callable(preprocess):
            preprocessor = preprocess
        else:
            if preprocess:
                preprocessor = band_preprocessors[self['filetype']]
            else:
                preprocessor = preprocess_none

        band_fname = self['bands'][name]
        ds = rasterio.open(band_fname)
        band = Band(
            data=ds.read(number).astype(float),
            geotransform=ds.get_transform(),
            projection=ds.crs.to_wkt()
        )

        return preprocessor(band)

    def get_mask(self, mask_dir, ext='.tif'):
        mask_dir = Path(mask_dir)
        tile_name = self['tile']
        mask_fname = tile_name + ext
        mask_fpath = mask_dir / mask_fname
        ds = rasterio.open(mask_fpath)
        band = Band(
            data=ds.read(1),
            geotransform=ds.get_transform(),
            projection=ds.crs.to_wkt()
        )
        return band

    @property
    def computed(self):
        pyintdem = self.get('pyintdem', None)

        if pyintdem is None:
            return False

        computed_state = pyintdem.get('computed', None)
        if computed_state is None:
            return False
        else:
            return computed_state

def map_bands(datafile, mapper=None):
    if mapper is None:
        # use predefined mappers from data_mappers
        mapper = data_mappers[datafile['filetype']]
    else:
        mapper = mapper
        try:
            assert callable(mapper)
        except:
            raise Exception('mapper must be a callable which can map the internal file structure')

    ds = mapper(datafile['fpath'])
    return ds


class Database(dict):
    def __init__(self, fdir, patterns=['**/*.zip*', '**/*.SAFE'], nameparsers=available_parsers):

        super().__init__(self)

        self.fdir = fdir
        self.patterns = patterns
        self.nameparsers = nameparsers

        _datafiles = list_datafiles(
            fnames=listfiles(self.fdir, patterns=self.patterns),
            parsers=self.nameparsers)

        # convert to DataFile from dictionary
        _datafiles = [DataFile(**datafile) for datafile in _datafiles]

        self.update(sort_datafiles_by_tiles(_datafiles))

    @property
    def tiles(self):
        return list(self.keys())

    def sel(self, tiles):
        # Keep only the selected tiles
        self_copy = copy.deepcopy(self)
        for tile in self_copy:
            if tile not in tiles:
                self_copy.pop(tile)

        return self_copy

    def to_file(self, fname):
        # serialize the time
        database = self.copy()
        for tile in database:
            for datafile in database[tile]:
                datafile['time'] = datafile['time'].strftime('%Y-%m-%d %H:%M:%S.%f')

        with open(fname, 'w') as fp:
            json.dump(database, fp=fp, indent=2)

    def from_file(self, fname):
        with open(fname, 'r') as fp:
            database = json.load(fp)
            for tile in database:
                for datafile in database[tile]:
                    datafile['time'] = pd.to_datetime(datafile['time'], format='%Y-%m-%d %H:%M:%S.%f')

        self.update(database)

    def clear(self):
        for key in self:
            self.pop(key)

    def map_output(self, fdir):
        checker = get_output_checker(fdir)
        for tile in self:
            self[tile] = list(map(checker, self[tile]))

    def split_by_compute_status(self):
        return self.filter_out_noncomputed(), self.filter_out_computed()

    def filter_out_noncomputed(self):
        self_copy = copy.deepcopy(self)
        for tile in self_copy:
            self_copy[tile] = list(filter(lambda data: data.computed, self_copy[tile]))

        return self_copy

    def filter_out_computed(self):
        self_copy = copy.deepcopy(self)
        for tile in self_copy:
            self_copy[tile] = list(filter(lambda data: not data.computed, self_copy[tile]))

        return self_copy

    @property
    def ntiles(self):
        return len(self)

    def tabulate(self):
        df = {}
        for tile in self:
            nimage = len(self[tile])
            ncomputed = np.sum([image.computed for image in self[tile]])
            df[tile] = {
                'nimage':nimage,
                'ncomputed':ncomputed
            }

        df = pd.DataFrame(df).T

        return df

    def __repr__(self):
        df = self.tabulate()
        nimage = df.nimage.sum()
        ncomputed = df.ncomputed.sum()

        return f"Database: {self.ntiles:0.0f} tiles, {nimage:0.0f} images, {ncomputed:0.0f} computed"

def listfiles(fdir, patterns=['*/*.zip', '*/*.SAFE']):
    filelist = []

    if isinstance(patterns, list):
        patterns = patterns
    elif isinstance(patterns, str):
        patterns = [patterns]
    else:
        raise Exception('patterns must be a list of string or a string')

    fdir = Path(fdir)

    for pattern in patterns:
        for afile in fdir.glob(pattern=pattern):
            filelist.append(afile)

    return filelist


def parse_file(fname, parsers=[parse_theia, parse_copernicus]):
    if callable(parsers):
        parsers = [parsers]
    elif isinstance(parsers, list):
        # nothing to do here
        pass
    else:
        raise Exception('name parsers must be a callable/function or list of functions')

    try:
        assert np.all([callable(parser) for parser in parsers])
    except:
        Exception('all name parsers must be a callable/function')

    is_parseable = False
    info = {}

    for parser in parsers:
        try:
            info = parser(fname)
        except:
            is_parseable = False
        else:
            is_parseable = True
            break

    return is_parseable, info


def list_datafiles(fnames, parsers=[parse_theia, parse_copernicus]):
    parsed_files = []
    for fname in fnames:
        is_parseable, info = parse_file(fname, parsers=parsers)
        if is_parseable:
            parsed_files.append(info)

    return parsed_files


def sort_datafiles_by_tiles(datafiles):
    database = {}
    for datafile in datafiles:
        tile = datafile['tile']
        if tile in database:
            database[tile].append(datafile)
        else:
            database[tile] = []
            database[tile].append(datafile)
    return database

def get_output_checker(output_dir):
    output_dir = Path(output_dir)

    def checker(data):
        acqisition_time = data['time']
        tile_id = data['tile']
        image_dir_name = acqisition_time.strftime("%Y%m%d%H%M%S")
        image_dir_path = output_dir / tile_id / image_dir_name
        output_exists = image_dir_path.exists() and len(list(image_dir_path.glob("shoreline_*.csv"))) > 0
        data_updated = copy.deepcopy(data)
        data_updated['pyintdem'] = {
            'computed': output_exists,
            'fpath': image_dir_path
        }
        return data_updated

    return checker
