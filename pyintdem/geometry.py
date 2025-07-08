# -*- coding: utf-8 -*-
# Extracted from pycaz/utils/geometry.py
# https://github.com/jamal919/pycaz
import cartopy.crs as ccrs
from pyproj import CRS
import numpy as np


def buffer_extent(extent, buffer, xmin=0, ymin=-90, xmax=360, ymax=90):
    """
    Apply a buffer to a given extent

    :param extent: Extent as [west, east, south, north]
    :param buffer: Buffer to be applied
    :param xmin: Maximum west
    :param ymin: Maximum south
    :param xmax: Maximum east
    :param ymax: Maximum north
    :return: Buffered extent [west, east, south, north]
    """
    w, e, s, n = extent
    buffered = [
        xmin if w - buffer < xmin else w - buffer,
        xmax if e + buffer > xmax else e + buffer,
        ymin if s - buffer < ymin else s - buffer,
        ymax if n + buffer > ymax else n + buffer
    ]

    return buffered


def bounds2extent(bounds):
    """
    Get the extent [w, e, s, n] from a bound [w, s, e, n] of a geometry

    :param bounds: Bounds in [west, south, east, north] or shape.bounds or gdf.GeoDataFrame.total_bounds
    :return: Extent in [west, east, south, north]
    """
    return [
        bounds[0],
        bounds[2],
        bounds[1],
        bounds[3]
    ]


def extent2geojson(extent):
    """
    Create a geojson from an extent [west, east, south, north]

    :param extent: Extent in [west, east, south, north]
    :return: GeoJSON object representing the extent
    """
    west, east, south, north = extent
    geojson = [
        {
            'type': 'Polygon',
            'coordinates': [[
                [west, south],
                [east, south],
                [east, north],
                [west, north],
                [west, south]
            ]]
        }
    ]

    return geojson


def geojson2geometries(geojson):
    """
    Convert a geojson object into a list of geometries

    :param geojson: Input geojson object
    :return:
    """
    from shapely.geometry import shape

    geometries = list(map(shape, geojson))

    return geometries


def extent2geometries(extent):
    """
    Create shapely geometries list from an extent definition

    :param extent: Extent in [west, east, south, north]
    :return: shapely geometries
    """
    geojson = extent2geojson(extent)
    geometries = geojson2geometries(geojson)
    return geometries


def get_utm_code_manual(lon, lat):
    """
    Get UTM code for a given longitude and latitude

    :param lon: target longitude
    :param lat: target latitude
    :return: UTM as epsg code
    """
    # https://stackoverflow.com/a/40140326
    utm_band = str((np.floor((lon + 180) / 6) % 60) + 1)
    if len(utm_band) == 1:
        utm_band = '0' + utm_band
    if lat >= 0:
        epsg_code = '326' + utm_band
    else:
        epsg_code = '327' + utm_band
    return epsg_code


def get_utm_code(extent, datum_name='WGS 84'):
    """
    Get UTM code suitable for a given extent

    Requires pyproj > 3

    :param extent: Extent in [west, east, south, north]
    :param datum_name: Default to "WGS 84"
    :return: utm code
    """
    from pyproj.aoi import AreaOfInterest
    from pyproj.database import query_utm_crs_info

    geometries = geojson2geometries(extent2geojson(extent))

    # inside rioxarray
    x_centroid, y_centroid = geometries[0].centroid.x, geometries[0].centroid.y

    utm_crs_list = query_utm_crs_info(
        datum_name=datum_name,
        area_of_interest=AreaOfInterest(
            west_lon_degree=x_centroid,
            south_lat_degree=y_centroid,
            east_lon_degree=x_centroid,
            north_lat_degree=y_centroid
        ),
    )
    utm_code = utm_crs_list[0].code
    return utm_code


def cartopy_utm_projection(utm_code):
    """
    Get the corresponding cartopy projection for given UTM code. In cartopy, this is used  in the `transform` command

    The resulting projection looks like something directly taken from the pyproj.

    TODO: Check if pyproj projection can be used directly.

    :param utm_code: UTM code
    :return: Corresponding cartopy UTM projection projection
    """
    utm_zone = CRS.from_epsg(utm_code).utm_zone
    zone = int(utm_zone[0:-1])

    if utm_zone[-1] == 'S':
        southern_hemisphere = True
    else:
        southern_hemisphere = False

    return ccrs.UTM(zone=zone, southern_hemisphere=southern_hemisphere)
