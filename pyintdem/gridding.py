# -*- coding: utf-8 -*-
import numpy as np
import geopandas as gpd

from pyintdem.geometry import bounds2extent, extent2geometries


def create_tiles_layout(extent, dx=1, dy=1, rounding=True, extent_convension='cartopy'):
    """Compute a GeoDataframe with specified tile layout

    Args:
        extent (array): [w, e, s, n] for cartopy or [w, s, e, n] for shapely
        dx (float, optional): size for x. Defaults to 1.
        dy (float, optional): size for y. Defaults to 1.
        rounding (bool, optional): Rounds the given extent with dx and dy. Defaults to True.
        extent_convension (str, optional): cartopy or shapely. Defaults to 'cartopy'.

    Raises:
        ValueError: extent_convention needs to be `cartopy` or `shapely`

    Returns:
        GeoDataframe: GeoDataframe containing the tiles
    """
    if extent_convension == 'cartopy':
        w, e, s, n = extent
    elif extent_convension == 'shapely':
        w, s, e, n = extent
    else:
        raise ValueError('extent_convention must be one of `cartopy` or `shapely`')

    # Do rounding
    if rounding:
        w = np.floor(w)
        e = np.ceil(e)
        s = np.floor(s)
        n = np.ceil(n)

    extent_ = [w, e, s, n]

    # create tiles
    dx_, dy_ = dx, dy
    x = np.arange(extent_[0], extent_[1] + dx_, dx_)
    y = np.arange(extent_[2], extent_[3] + dy_, dy_)

    tiles = []
    for x1, x2 in zip(x[:-1], x[1:]):
        for y1, y2 in zip(y[:-1], y[1:]):
            tile = extent2geometries([x1, x2, y1, y2])[0]
            tiles.append(tile)

    tiles_gdf = gpd.GeoDataFrame(geometry=tiles)
    return tiles_gdf


def create_mapping_grid(bbox, res, bbox_type='cartopy'):
    """    Mapping grid, which is shifted to the right by res/2 to have the center on the ordinate

    +----+----+
    |         |
    |    +    |
    |         |
    +---------+

    Args:
        bbox (array): [w, e, s, n] for cartopy or [w, s, e, n] for shapely
        res (float): resolution of the grid
        bbox_type (str, optional): cartopy or shapely. Defaults to 'cartopy'.

    Raises:
        ValueError: extent_convention needs to be `cartopy` or `shapely`

    Returns:
        [array, array]: Array of X and Y
    """
    if bbox_type == 'cartopy':
        w, e, s, n = bbox
    elif bbox_type == 'shapely':
        w, s, e, n = bbox
    else:
        raise ValueError('bbox_type can be only of `cartopy` or `shapely` convention')

    x = np.arange(w + res / 2, e + res / 2, res)
    y = np.arange(s + res / 2, n + res / 2, res)

    X, Y = np.meshgrid(x, y)

    return X, Y