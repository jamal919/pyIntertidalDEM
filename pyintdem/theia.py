#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import copy
import json
import logging
import os
import warnings
from pathlib import Path

import cartopy
import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from shapely.geometry import Polygon, shape
from tqdm import tqdm

logger = logging.getLogger(__name__)

class TheiaCoverage:
    def __init__(
            self,
            bbox=None,
            shoreline=False,
            fname='theia_sentinel2.geojson', 
            url='https://umap.openstreetmap.fr/en/datalayer/154585/2949043/'):
        
        self.fname = fname
        self.url = url
        self.coverage = get_theia_coverage(url=self.url, fname=self.fname)
        
        # Apply bbox filtering
        if bbox is not None:
            try:
                self.bbox = bbox2polygon(bbox)
            except:
                warnings.warn('Bbox is probably not correct, expected format [w, e, s, n]')
                self.bbox = bbox2polygon([-180, 180, -90, 90])
            finally:
                self.filter_by_bbox(self.bbox)

        # Apply shoreline filtering
        if shoreline:
            self.filter_by_shoreline()

    def clear(self):
        self.coverage = self._get_coverage()

    def as_list(self, prefix='T'):
        tiles_list = [f'{prefix}{tile}' for tile in self.coverage.index]
        return tiles_list
    
    def filter_by_bbox(self, bbox_poly):
        is_within = [tile.intersects(bbox_poly) for tile in self.coverage.geometry]
        self.coverage = self.coverage.loc[is_within]

    def filter_by_shoreline(self):
        goems_shorelines = self._shorelines_within_bbox()

        does_intersects = np.any(
            [[geom.intersects(shoreline) for shoreline in goems_shorelines.geometry] for geom in self.coverage.geometry],
            axis=1)

        self.coverage = self.coverage.loc[does_intersects]

    def _shorelines_within_bbox(self):
        coastline = list(cartopy.feature.COASTLINE.geometries())
        coastline_gdf = gpd.GeoDataFrame(geometry=coastline)
        is_within = [line.intersects(self.bbox) for line in coastline_gdf.geometry]
        
        return coastline_gdf.loc[is_within]

    def plot(
            self,
            ax=None, 
            coastline=True,
            geom_kw={'facecolor':'red', 'edgecolor':'black', 'alpha':0.5, }, 
            text_kw={'ha':'center', 'color':'black', 'bbox':{'facecolor':'white', 'edgecolor':'black', 'alpha':0.75}}):
        
        if ax is None:
            fig, ax = plt.subplots(subplot_kw={'projection':ccrs.PlateCarree()})

        self.coverage.plot(ax=ax, **geom_kw)
        
        # Annotation
        for tile_name, geometry in zip(self.coverage.index, self.coverage.geometry):
            ax.annotate(
                text=tile_name,
                xy=[geometry.centroid.x, geometry.centroid.y],
                **text_kw
            )
        
        # Add coastline
        if coastline:
            ax.coastlines()
        
        return ax

def get_theia_coverage(
        url='https://umap.openstreetmap.fr/en/datalayer/154585/2949043/', 
        fname='theia_sentinel2.geojson'
    ):
    
    fname = Path(fname)
    
    if fname.exists():
        logger.info('Loading Sentinel-2 coverage from file')
        with open(fname, 'r') as f:
            geojson = json.load(f)
    else:
        logger.info('Loading Sentinel-2 tiles from the url')
        res = requests.get(url)
        geojson = res.json()

        with open(fname, 'w') as f:
            f.write(json.dumps(geojson))


    tile_names = []
    geometries = []

    for feature in geojson['features']:
        tile_names.append(feature['properties']['name'])
        geometries.append(shape(feature['geometry']))

    gdf = gpd.GeoDataFrame({'name': tile_names}, geometry=geometries).set_index('name')

    return gdf

def bbox2polygon(bbox):
    w, e, s, n = bbox
    points = np.array([
        [w, s],
        [e, s],
        [e, n],
        [w, n],
        [w, s]
    ])

    polygon = Polygon(points)

    return(polygon)


class TheiaAPI:
    def __init__(self, collection='SENTINEL2'):
        self.server = "https://theia.cnes.fr/atdistrib"
        self.collection = collection
        self.results = {}
        self.locations = {}

    @property
    def token(self):
        config = configparser.ConfigParser()

        secret_file = Path.home() / '.pyintdemsecrets'
        
        if secret_file.exists():
            logger.info('.pyintdemsecrets found!')
        else:
            logger.info('.pyintdemsecrets not found!')
            raise Exception(f'Secret file {secret_file.as_posix()} not found!')

        config.read()

        try:
            user = config['THEIA']['USER']
        except KeyError:
            raise Exception(f'.pyintdemsecrets must contain USER = <your_theia_username> in [THEIA] block')

        try:
            password = config['THEIA']['PASS']
        except KeyError:
            raise Exception(f'.pyintdemsecrets must contain PASS = <your_theia_password> in [THEIA] block')

        res = requests.post(
            url=f'{self.server}/services/authenticate/', 
            data={'ident':user, 'pass':password})
        
        if res.ok:
            logger.debug("Response received from authenticate service")
        else:
            raise res.error
        
        if len(res.text) == 36:
            return(res.text)
        else:
            logger.debug("Wrong response from authenticate service, check user/pass")
            raise Exception(f'Got wrong token! Exiting.')

    def search(self,
        tiles, 
        startDate='2016-01-01', 
        completionDate='2023-01-01',
        cloudCover='[0,3]',
        productType='REFLECTANCE', 
        processingLevel='LEVEL2A',
        maxRecords=500,
        **kwargs):
        tiles = np.atleast_1d(tiles)
        results = {}

        for tile in tqdm(tiles):
            result = self._search(
                location=tile,
                startDate=startDate,
                cloudCover=cloudCover,
                productType=productType,
                processingLevel=processingLevel,
                maxRecords=maxRecords,
                **kwargs
            )

            results[tile] = result

        self.results = results

    def _search(self, 
        location='',
        startDate='2016-01-01', 
        completionDate='2023-01-01',
        cloudCover='[0,3]',
        productType='REFLECTANCE', 
        processingLevel='LEVEL2A',
        maxRecords=500,
        **kwargs
        ):

        user_params = locals()
        request_params = {}

        for kwarg in user_params:
            if kwarg == 'kwargs':
                for kw in kwargs:
                    request_params[kw] = kwargs[kw]

            else:
                request_params[kwarg] = user_params[kwarg]

        logger.debug('Querying search api')
        res = requests.get(
            url=f'{self.server}/resto2/api/collections/{self.collection}/search.json', 
            params=request_params
        )

        if res.ok:
            logger.debug('Ok response received')
            result = res.json()
            [(_, res_type), (_, res_props), (_, res_features)] = result.items()
        else:
            logger.info('Non 200 response received, returning empty list')
            res_features = []

        return(res_features)

    @property
    def summary(self):
        summary = {}
        geometry = []

        non_empty_tiles, dropped_tiles = self.drop_empty()

        for tile in non_empty_tiles.results:
            ntile = len(non_empty_tiles.results[tile])
            if ntile > 0:
                geometry.append(shape(non_empty_tiles.results[tile][0]['geometry']))
            else:
                geometry.append(Polygon())

            summary[tile] = {'count':ntile}

        df = pd.DataFrame(summary).T
        gdf = gpd.GeoDataFrame(df, geometry=geometry)

        return gdf

    def copy(self):
        return copy.copy(self)

    @property
    def extent(self):
        geom_extents = np.vstack([geom.bounds for geom in self.summary.geometry])
        results_extent = [
            np.min(geom_extents[:, 0]),
            np.max(geom_extents[:, 2]),
            np.min(geom_extents[:, 1]),
            np.max(geom_extents[:, 3])
        ]

        return results_extent

    def head(self, count=10):
        results = {}
        for tile in self.results:
            results[tile] = self.results[tile][0:count]

        self_object = self.copy()
        self_object.results = results

        return(self_object)

    def tail(self, count=10):
        results = {}
        for tile in self.results:
            results[tile] = self.results[tile][-count:]

        self_object = self.copy()
        self_object.results = results

        return(self_object)

    def drop_empty(self):
        results = {}
        dropped = []
        for tile in self.results:
            if len(self.results[tile]) > 0:
                results[tile] = self.results[tile]

            else:
                dropped.append(tile)

        self_object = self.copy()
        self_object.results = results

        return self_object, dropped

    def filter(self, filter_func):
        results = {}
        for tile in self.results:
            results[tile] = list(filter(filter_func, self.results[tile]))

        self_object = self.copy()
        self_object.results = results

        return(self_object)

    def filter_date_range(self, start_date, end_date):
        filter_func = lambda result: is_within_date_range(result, start_date=start_date, end_date=end_date)
        filtered_result = self.filter(filter_func)
        return(filtered_result)

    def filter_less_than(self, property_name, target_value):
        filter_func = lambda result: less_than(result, name=property_name, target=target_value)
        filtered_result = self.filter(filter_func)
        return(filtered_result)

    def plot(self, ax=None):
        summary = self.summary

        if ax is None:
            fig, ax = plt.subplots(figsize=(5, 8), subplot_kw={'projection':ccrs.PlateCarree()})
        else:
            pass

        ax.add_geometries(summary.geometry, crs=ccrs.PlateCarree(), facecolor='None')

        for (i, row) in summary.iterrows():
            xy = [row.geometry.centroid.x, row.geometry.centroid.y]
            count = row['count']

            ax.annotate(text=count, xy=xy, ha='center')

        ax.coastlines()
        ax.set_extent(self.extent)

        return ax

    def save(self, fname):
        with open(fname, 'w') as f:
            res_str = json.dumps(self.results)
            f.write(res_str)

    def load(self, fname):
        with open(fname, 'r') as f:
            res_data = json.load(f)

        self.results = res_data

    def download(self, savedir):
        savedir = Path(savedir)
        for tile in self.results:
            tiledir = savedir / tile
            
            if not tiledir.exists():
                tiledir.mkdir()

            for feature in self.results[tile]:
                download(feature, tiledir, token=self.token, server=self.server, collection=self.collection)


    def __repr__(self):
        return str(self.summary)

def is_within_date_range(result, start_date, end_date):

    filter_start_date = pd.to_datetime(start_date)
    filter_end_date = pd.to_datetime(end_date)

    result_start_date = pd.to_datetime(result['properties']['startDate'][:-1])
    result_end_date = pd.to_datetime(result['properties']['startDate'][:-1])

    within = (result_start_date >= filter_start_date) & (result_end_date <= filter_end_date)

    return within

def less_than(result, name, target):
    target_type = type(target)
    
    try: 
        property_value = result['properties'][name]
    except KeyError:
        available_keys = result['properties'].keys()
        raise(f'Property {name} not found in {available_keys}')
    else:
        property_value = target_type(property_value)
    finally:
        is_less_than = property_value < target

    return is_less_than

def download(feature, savedir, token, server="https://theia.cnes.fr/atdistrib", collection='SENTINEL2'):
    featureid = feature['id'] # to download
    productid = feature['properties']['productIdentifier'] # to save to file
    fname = Path(savedir)/f'{productid}.zip'
    url=f'{server}/resto2/collections/{collection}/{featureid}/download/'
    header = { 'Authorization':f'Bearer {token}' }
    params = { 'issuerId':'theia' }

    with requests.get(url=url, headers=header, params=params, stream=True) as res:
        logger.info(fname)
        logger.info(url)
        total_size = int(res.headers.get('content-length', 0))
        logger.info(f'total_size {total_size} bytes')
        
        res.raise_for_status()
        
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
        
        with open(fname, 'wb') as f:
            for chunk in tqdm(res.iter_content(chunk_size=8192)):
                progress_bar.update(len(chunk))
                f.write(chunk)
            
            progress_bar.close()