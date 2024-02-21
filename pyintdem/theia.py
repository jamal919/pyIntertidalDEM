#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import copy
import json
import logging
from pathlib import Path

import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from shapely.geometry import Polygon, shape
from tqdm.auto import tqdm

logger = logging.getLogger(__name__)

class TheiaAPI:
    def __init__(self, collection='SENTINEL2', server="https://theia.cnes.fr/atdistrib", proxies={}):
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
        cloudCover=3,
        productType='REFLECTANCE', 
        processingLevel='LEVEL2A',
        maxRecords=500,
        **kwargs):
        """Search in the THEIA repository for a list of tiles

        Args:
            tiles (list): List of tiles. Can be generated from TheiaCoverage, with prefix 'T', e.g., 'TXXYYY' format.
            startDate (str, optional): Start date of the data. Defaults to '2016-01-01'.
            completionDate (str, optional): End date of the data. Defaults to '2023-01-01'.
            cloudCover (float, optional): Maximum cloud cover. Defaults to 3.
            productType (str, optional): Product type. Defaults to 'REFLECTANCE' for SENTINEL-2.
            processingLevel (str, optional): Processing level. Defaults to 'LEVEL2A'.
            maxRecords (int, optional): Maximum number of records to query. Hard limit is 500, set by Theia.
        """
        tiles = np.atleast_1d(tiles)
        results = {}

        logger.info(f'Searching copernicus server for {len(tiles)} tiles')
        for tile in tiles:
            result = self._search(
                location=tile,
                startDate=startDate,
                completionDate=completionDate,
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
        cloudCover=3,
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
            cloudCover (float, optional): Maximum cloud cover, defauls to 3.
            productType (str, optional): Product type. Defaults to 'REFLECTANCE' for SENTINEL-2.
            processingLevel (str, optional): Processing level. Defaults to 'LEVEL2A'.
            maxRecords (int, optional): Maximum number of records to query. Hard limit is 500, set by Theia.
        """

        user_params = locals()
        user_params['cloudCover'] = f"[0,{user_params['cloudCover']}]"
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
            params=request_params,
            proxies=self.proxies
        )

        if res.ok:
            logger.debug('Ok response received')
            result = res.json()
            [(_, res_type), (_, res_props), (_, res_features)] = result.items()

            # sorting with date
            res_features.sort(key=lambda item: pd.to_datetime(item['properties']['startDate'][:-1]))
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

    def save(self, fname, summary=False):
        """Save search result to file `fname` if `summary=False`, or save the summary to `file` 

        Args:
            fname (str): Path to file, can be geojson for full result, or geojson/shapefile for summary
        """
        if summary:
            self.summary.to_file(fname)
        else:
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

    def download(self, savedir, ext='zip'):
        """Download the current search result to the `savedir` directory

        The routine will automatically create folder for each individual tile

        Args:
            savedir (str): Path to directory where the files will be saved
        """
        savedir = Path(savedir)
        for tile in tqdm(self.results, desc='Tiles'):
            tiledir = savedir / tile
            
            if not tiledir.exists():
                tiledir.mkdir()

            for feature in tqdm(self.results[tile], desc=f'Features in {tile}'):
                token = self.token # Creating a token before each file download
                download(feature, tiledir, token=token, ext=ext, 
                         server=self.server, 
                         collection=self.collection, 
                         proxies=self.proxies)


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

def download(feature, savedir, token, ext='zip', server="https://theia.cnes.fr/atdistrib", collection='SENTINEL2', proxies={}):
    """Download a THEIA data record `feature`

    Args:
        feature (datarecord): Theia datarecord
        savedir (str): Path of directory where the file will be saved
        token (str): Server token, see TheiaAPI().token
        server (str, optional): Theia server. Defaults to "https://theia.cnes.fr/atdistrib".
        collection (str, optional): Collection to download. Defaults to 'SENTINEL2'.
    """
    featureid = feature['id'] # to download
    productid = feature['properties']['productIdentifier']
    fname = f'{productid}.{ext}'
    fpath = Path(savedir)/ fname
    url=f'{server}/resto2/collections/{collection}/{featureid}/download/'
    header = { 'Authorization':f'Bearer {token}' }
    params = { 'issuerId':'theia' }

    with requests.get(url=url, headers=header, params=params, stream=True, proxies=proxies) as res:
        logger.info(fpath)
        logger.info(url)

        try:
            total_size = int(res.headers.get('content-length'))
            logger.info(f'Size of the file {total_size} bytes')
        except:
            total_size = 0
            logger.info(f'No Size info received, progress bar will not be shown')

        res.raise_for_status()
        
        # Check existing file and if download is needed or not
        download_needed = True
        if fpath.exists():
            logger.info(f'File {fname} already exists')
            fpath_size = fpath.stat().st_size
            
            if fpath_size == total_size:
                download_needed = False
                logger.info(f'Full file {fname} already downloaded')
            else:
                logger.info(f'Partial file {fname} found')
                logger.info(f'Online size {total_size} vs local size {fpath_size}')
                logger.info(f'{fname} will be redownloaded')

        # Actual download
        if download_needed:
            with open(fpath, 'wb') as f, tqdm(desc=fname, total=total_size, unit='iB', unit_scale=True, unit_divisor=1024) as bar:
                for chunk in res.iter_content(chunk_size=8192):
                    size = f.write(chunk)
                    bar.update(size)


