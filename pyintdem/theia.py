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
            bbox=[-180, 180, -90, 90],
            shoreline=False,
            fname='theia_sentinel2.geojson', 
            url='https://umap.openstreetmap.fr/en/datalayer/154585/2949043/'):
        """Filter list of tiles for a target `bbox`, over `shoreline` if needed

        Args:
            bbox (array, optional): Bounding box in [w, e, s, n]. Defaults to [-180, 180, -90, 90].
            shoreline (bool, optional): Keep only the tiles crossing GSHHG shoreline. Defaults to False.
            fname (str, optional): Local file to store the full geojson for future use. Defaults to 'theia_sentinel2.geojson'.
            url (str, optional): Online source of the coverage. Defaults to 'https://umap.openstreetmap.fr/en/datalayer/154585/2949043/'.
        """
        
        self.fname = fname
        self.url = url
        self.coverage = get_theia_coverage(url=self.url, fname=self.fname)

        logger.info(f'Visit the Theia Sentinel-2 coverage at {self.url}')
        
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
        """Clear further selection and relaod with initial criteria
        """
        self.coverage = self._get_coverage()

    def as_list(self, prefix='T'):
        """Get a list of the selected tiles, with `prefix` if necessary.

        Args:
            prefix (str, optional): Prefix to add to each tilename. Useful for TheiaAPI. Defaults to 'T'.

        Returns:
            list: List of selected tiles
        """
        tiles_list = [f'{prefix}{tile}' for tile in self.coverage.index]
        return tiles_list
    
    def filter_by_bbox(self, bbox_poly):
        """Filter the coverage by a bbox_polygon

        Args:
            bbox_poly (shapely.Polygon): Polygon to filter the tiles in current coverage
        """
        is_within = [tile.intersects(bbox_poly) for tile in self.coverage.geometry]
        self.coverage = self.coverage.loc[is_within]

    def filter_by_shoreline(self):
        """Filter the coverage by keeping only over the shoreline

        For shoreline, currently the cartopy.feature shoreline is used, which is GSHHG shoreline downloaded by cartopy's
        internal downloader.
        """
        goems_shorelines = self._shorelines_within_bbox()

        does_intersects = np.any(
            [[geom.intersects(shoreline) for shoreline in goems_shorelines.geometry] for geom in self.coverage.geometry],
            axis=1)

        self.coverage = self.coverage.loc[does_intersects]

    def _shorelines_within_bbox(self):
        """Get a GeoDataFrame of the shorelines linestrings for the bbox defined in class

        Returns:
            GeoDataFrame: GeoDataFrame of the shorelines linestring within self.bbox
        """
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
        """Plot the current coverage

        Args:
            ax (cartopy.GeoAxes, optional): An axis to plot the map. Defaults to None.
            coastline (bool, optional): Plot coastline or not. Defaults to True.
            geom_kw (dict, optional): keywarded arguments to control geometry plotting. 
                Defaults to {'facecolor':'red', 'edgecolor':'black', 'alpha':0.5, }.
            text_kw (dict, optional): keywarded arguments to control the text. 
                Defaults to {'ha':'center', 'color':'black', 'bbox':{'facecolor':'white', 'edgecolor':'black', 'alpha':0.75}}.

        Returns:
            cartopy.GeoAxes: Axes with plots of the selected tiles
        """
        
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
    """Get the tiles available in theia

    Args:
        url (str, optional): Layer URL. Defaults to 'https://umap.openstreetmap.fr/en/datalayer/154585/2949043/'.
        fname (str, optional): Local filename to save. Defaults to 'theia_sentinel2.geojson'.

    Returns:
        GeoDataFrame: GeoDataFrame with tile name as index and tile geometry
    """
    
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
    """Converts a [w, e, s, n] bbox to a shapely.Polygon

    Args:
        bbox (shapely.Polygon): Polygon corresponding to the bbox
    """
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
    def __init__(self, collection='SENTINEL2', server="https://theia.cnes.fr/atdistrib"):
        """A simple API to query and download the SENTINEL2 collection from Theia server

        Args:
            collection (str, optional): Theia collection name. For now only SENTINEL2 is tested. Defaults to 'SENTINEL2'.
            server (str, optional): Server url of the Theia Distribution center. Defaults to "https://theia.cnes.fr/atdistrib".
        """
        self.server = server
        self.collection = collection
        self.results = {}

    @property
    def token(self):
        """Returns the token from the server given the username and password

        The username and password is stored at `home`/.pyintdemsecrets. 
        
        The file should contain the following - 
        ```
        [THEIA]
        USER = your_theia_username
        PASS = your_theia_password
        ```

        Go to https://theia.cnes.fr/atdistrib/rocket/#/home to create your account, if you do not have one. 
        """
        config = configparser.ConfigParser()

        secret_file = Path.home() / '.pyintdemsecrets'
        
        if secret_file.exists():
            logger.info('.pyintdemsecrets found!')
        else:
            logger.info('.pyintdemsecrets not found!')
            raise Exception(f'Secret file {secret_file.as_posix()} not found!')

        config.read(secret_file)

        try:
            user = config['THEIA']['USER']
        except KeyError:
            raise Exception(f'.pyintdemsecrets must contain USER = <your_theia_username> in [THEIA] block')

        try:
            password = config['THEIA']['PASS']
        except KeyError:
            raise Exception(f'.pyintdemsecrets must contain PASS = <your_theia_password> in [THEIA] block')

        try:
            res = requests.post(
                url=f'{self.server}/services/authenticate/', 
                data={'ident':user, 'pass':password})
            
            res.raise_for_status()
        except Exception as e:
            raise Exception(f'Access token creation failed. Reponse from the server was: {res.json()}')
        
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
        """Search in the THEIA repository for a list of tiles

        Args:
            tiles (list): List of tiles. Can be generated from TheiaCoverage, with prefix 'T', e.g., 'TXXYYY' format.
            startDate (str, optional): Start date of the data. Defaults to '2016-01-01'.
            completionDate (str, optional): End date of the data. Defaults to '2023-01-01'.
            cloudCover (str, optional): Cloud cover range, needs to be in string. Defaults to '[0,3]'.
            productType (str, optional): Product type. Defaults to 'REFLECTANCE' for SENTINEL-2.
            processingLevel (str, optional): Processing level. Defaults to 'LEVEL2A'.
            maxRecords (int, optional): Maximum number of records to query. Hard limit is 500, set by Theia.
        """
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
        """Search in the THEIA repository for a list of tiles

        Args:
            tiles (list): List of tiles. Can be generated from TheiaCoverage, with prefix 'T', e.g., 'TXXYYY' format.
            startDate (str, optional): Start date of the data. Defaults to '2016-01-01'.
            completionDate (str, optional): End date of the data. Defaults to '2023-01-01'.
            cloudCover (str, optional): Cloud cover range, needs to be in string. Defaults to '[0,3]'.
            productType (str, optional): Product type. Defaults to 'REFLECTANCE' for SENTINEL-2.
            processingLevel (str, optional): Processing level. Defaults to 'LEVEL2A'.
            maxRecords (int, optional): Maximum number of records to query. Hard limit is 500, set by Theia.
        """

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
        """Create a summary GeoDataFrame with the count of acquistions for each tile

        Returns:
            GeoDataFrame: Summary of the tiles
        """
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
        """Extent of the current search result and selections

        Returns:
            bbox: Extent in the form of [w, e, s, n]
        """
        geom_extents = np.vstack([geom.bounds for geom in self.summary.geometry])
        results_extent = [
            np.min(geom_extents[:, 0]),
            np.max(geom_extents[:, 2]),
            np.min(geom_extents[:, 1]),
            np.max(geom_extents[:, 3])
        ]

        return results_extent

    def head(self, count=10):
        """Returns a subset of selection with `count` number of acquisitions for each tile from the top of the list

        Args:
            count (int, optional): Tiles to keep. Defaults to 10.

        Returns:
            TheiaAPI: Selected results
        """
        results = {}
        for tile in self.results:
            results[tile] = self.results[tile][0:count]

        self_object = self.copy()
        self_object.results = results

        return(self_object)

    def tail(self, count=10):
        """Returns a subset of selection with `count` number of acquisitions for each tile from the bottom of the list

        Args:
            count (int, optional): Tiles to keep. Defaults to 10.

        Returns:
            TheiaAPI: Selected results
        """
        results = {}
        for tile in self.results:
            results[tile] = self.results[tile][-count:]

        self_object = self.copy()
        self_object.results = results

        return(self_object)

    def drop_empty(self):
        """Drop tiles that does not have any acquisions

        Returns:
            TheiaAPI: Selected results
        """
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
        """Filter using the `filter_func`

        `filter_func` must receive only one argument, which is a data-record dictionary

        Args:
            filter_func (function): Arbitrary filter function
        """
        results = {}
        for tile in self.results:
            results[tile] = list(filter(filter_func, self.results[tile]))

        self_object = self.copy()
        self_object.results = results

        return(self_object)

    def filter_date_range(self, start_date, end_date):
        """Filter the search result with a date range from `start_date` to `end_date`

        Args:
            start_date (str): Date string in 'yyyy-mm-dd HH:MM:SS', or datetime object
            end_date (str): Date string in 'yyyy-mm-dd HH:MM:SS', or datetime object
        """
        filter_func = lambda result: is_within_date_range(result, start_date=start_date, end_date=end_date)
        filtered_object = self.filter(filter_func)
        
        return(filtered_object)

    def filter_less_than(self, property_name, target_value):
        """Filter with arbitrary `property_name` from the data record when the value is less than `target_value`

        Args:
            property_name (str): A property name available in the data record
            target_value (any): The target highest value of of the property
        """
        filter_func = lambda result: less_than(result, name=property_name, target=target_value)
        filtered_object = self.filter(filter_func)
        
        return(filtered_object)

    def plot(self, 
        ax=None, 
        coastline=True,
        geom_kw={'facecolor':'red', 'edgecolor':'black', 'alpha':0.5, }, 
        text_kw={'ha':'center', 'color':'black', 'bbox':{'facecolor':'white', 'edgecolor':'black', 'alpha':0.75}}):
        """Plot the current search result summary

        Args:
            ax (cartopy.GeoAxes, optional): An axis to plot the map. Defaults to None.
            coastline (bool, optional): Plot coastline or not. Defaults to True.
            geom_kw (dict, optional): keywarded arguments to control geometry plotting. 
                Defaults to {'facecolor':'red', 'edgecolor':'black', 'alpha':0.5, }.
            text_kw (dict, optional): keywarded arguments to control the text. 
                Defaults to {'ha':'center', 'color':'black', 'bbox':{'facecolor':'white', 'edgecolor':'black', 'alpha':0.75}}.

        Returns:
            cartopy.GeoAxes: Axes with plots of the selected tiles
        """
        
        summary = self.summary

        if ax is None:
            fig, ax = plt.subplots(figsize=(5, 8), subplot_kw={'projection':ccrs.PlateCarree()})
        else:
            pass

        ax.add_geometries(summary.geometry, crs=ccrs.PlateCarree(), **geom_kw)

        for (i, row) in summary.iterrows():
            xy = [row.geometry.centroid.x, row.geometry.centroid.y]
            count = row['count']

            ax.annotate(text=count, xy=xy, **text_kw)

        if coastline:
            ax.coastlines()
        
        ax.set_extent(self.extent)

        return ax

    def save(self, fname):
        """Save search result to file `fname`

        Args:
            fname (str): Path to file
        """
        with open(fname, 'w') as f:
            res_str = json.dumps(self.results)
            f.write(res_str)

    def load(self, fname):
        """Load search result from file `fname`

        Args:
            fname (str): Path to file
        """
        with open(fname, 'r') as f:
            res_data = json.load(f)

        self.results = res_data

    def download(self, savedir):
        """Download the current search result to the `savedir` directory

        The routine will automatically create folder for each individual tile

        Args:
            savedir (str): Path to directory where the files will be saved
        """
        savedir = Path(savedir)
        for tile in self.results:
            tiledir = savedir / tile
            
            if not tiledir.exists():
                tiledir.mkdir()

            for feature in self.results[tile]:
                token = self.token # Creating a token before each file download
                download(feature, tiledir, token=token, server=self.server, collection=self.collection)


    def __repr__(self):
        return str(self.summary)

def is_within_date_range(result, start_date, end_date):
    """Test if the date in the `result` is within the `start_date` and `end_date`

    Args:
        result (datarecord): Tile data record received from Theia
        start_date (str): Date in 'yyyy-mm-dd HH:MM:SS' for datetime object
        end_date (str): Date in 'yyyy-mm-dd HH:MM:SS' for datetime object

    Returns:
        array: Boolean array
    """

    filter_start_date = pd.to_datetime(start_date)
    filter_end_date = pd.to_datetime(end_date)

    result_start_date = pd.to_datetime(result['properties']['startDate'][:-1])
    result_end_date = pd.to_datetime(result['properties']['startDate'][:-1])

    within = (result_start_date >= filter_start_date) & (result_end_date <= filter_end_date)

    return within

def less_than(result, name, target):
    """Test if the property with `name` is less than `target` value

    Args:
        result (datarecord): Tile data record received from Theia
        name (str): Name of the property
        target (any): Target value of the property

    Returns:
        array: Boolean array
    """
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
    """Download a THEIA data record `feature`

    Args:
        feature (datarecord): Theia datarecord
        savedir (str): Path of directory where the file will be saved
        token (str): Server token, see TheiaAPI().token
        server (str, optional): Theia server. Defaults to "https://theia.cnes.fr/atdistrib".
        collection (str, optional): Collection to download. Defaults to 'SENTINEL2'.
    """
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

