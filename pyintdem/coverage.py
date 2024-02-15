#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import warnings
from pathlib import Path

import cartopy
import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

import requests
from shapely.geometry import Polygon, shape


logger = logging.getLogger(__name__)

data_source = {
    'Theia':{
        'url':'https://raw.githubusercontent.com/jamal919/pyIntertidalDEM/master/resources/sentinel2_tiles_theia.geojson',
        'source':'https://umap.openstreetmap.fr/en/datalayer/154585/2949043/',
        'fname':'sentinel2_tiles_theia.geojson'
    },
    'Copernicus':{
        'url':'https://raw.githubusercontent.com/jamal919/pyIntertidalDEM/master/resources/sentinel2_tiles_global.geojson',
        'source':'https://github.com/justinelliotmeyers/Sentinel-2-Shapefile-Index',
        'fname':'sentinel2_tiles_global.geojson'
    }
}

class Coverage:
    def __init__(
            self,
            bbox=[-180, 180, -90, 90],
            shoreline=False,
            source='Theia',
            cachedir='./cache'):
        """Filter list of tiles for a target `bbox`, over `shoreline` if needed

        Args:
            bbox (array, optional): Bounding box in [w, e, s, n]. Defaults to [-180, 180, -90, 90].
            shoreline (bool, optional): Keep only the tiles crossing GSHHG shoreline. Defaults to False.
            source (str, optional): Choose either 'Theia' or 'Copernicus'
        """
        self.source = source
        self.cachedir = Path(cachedir)
        if not self.cachedir.exists():
            self.cachedir.mkdir()
        
        self.fname = self.cachedir / data_source[source]['fname']
        self.url = data_source[source]['url']
        self.coverage = get_coverage_from_geojson(url=self.url, fname=self.fname)
        

        logger.info(f'Get the {source} Sentinel-2 coverage at {self.url}')
        
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

    def to_file(self, fname):
        """Save the coverage to a file, geojson, shapefile

        Uses the to_file feature of the underlying geopandas format

        Args:
            fname (path): path to the file
        """
        self.coverage.to_file(fname)

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

def get_coverage_from_geojson(url, fname, kw_map={'name':'name', 'features':'features'}):
    """Get a geodataframe from a online geojson dataset

    Args:
        url (str, optional): Layer URL to download. Expected in geojson
        fname (str, optional): Local filename to save.
        kw_map (dict, optional): Name of the variable for 'name' and 'features'

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

    var_name = kw_map['name']
    var_feature = kw_map['features']


    tile_names = []
    geometries = []

    for feature in geojson[var_feature]:
        tile_names.append(feature['properties'][var_name])
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