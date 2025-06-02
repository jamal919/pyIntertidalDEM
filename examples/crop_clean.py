# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 16:31:47 2024

@author: LoesLGLG
"""

#%% IMPORTS

import rasterio
from rasterio.mask import mask
from shapely.geometry import Polygon, box
from pyproj import Transformer
import json
import glob2
import os
import shutil
import math

#%% FUNCTIONS

def crop_tif(input_tif, square_polygon):
    """
    Crop a TIF file according to a given polygon (already transformed into an even 10m pixel square) and replace the original one.

    Arguments :
        input_tif (str) :  Path of input (and output) TIF file.
        square_polygon (shapely.geometry.Polygon) : Square polygon in TIF CRS.
    """
    geojson_polygon = [json.loads(json.dumps(square_polygon.__geo_interface__))]
    temp_output = input_tif + ".tmp"

    with rasterio.open(input_tif) as src:
        out_image, out_transform = mask(src, geojson_polygon, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })
        with rasterio.open(temp_output, "w", **out_meta) as dest:
            dest.write(out_image)
    os.replace(temp_output, input_tif)

    print(f"The TIF file has been cropped and saved as : {input_tif}")


def transform_polygon(polygon_coords, from_crs, to_crs):
    """
    Transforms the coordinates of a polygon from one CRS to another.

    Arguments :
        polygon_coords (list) : Coordinates of the polygon (list of (x,y)).
        from_crs (str) : EPSG code of initial CRS.
        to_crs (str) : EPSG code of target CRS.

    Returns :
        shapely.geometry.Polygon : Polygon transformed into the new CRS.
    """
    transformer = Transformer.from_crs(from_crs, to_crs, always_xy=True)
    transformed_coords = [transformer.transform(lon, lat) for lon, lat in polygon_coords]
    return Polygon(transformed_coords)


def validate_polygon_inclusion(polygon, raster_bounds):
    """
    Check if the polygon (already transformed into a square with an even 10m pixel side) is strictly included within the boundaries of the original tile.

    Arguments:
        polygon (shapely.geometry.Polygon): Polygon to be checked.
        raster_bounds (tuple): TIF boundaries (xmin, ymin, xmax, ymax).

    Raise :
        ValueError: If the polygon is not strictly included.
    """
    tif_bounds = box(*raster_bounds)
    if not tif_bounds.contains(polygon):
        raise ValueError("The polygon supplied is not strictly included within the tile boundaries.")


def adjust_to_square(polygon, pixel_size=10):
    """
    Transform a polygon into a square containing the polygon and adjust the size to have an even number of 10m pixels (beware!)

    Arguments:
        polygon (shapely.geometry.Polygon): Input polygon.
        pixel_size (int): Size of a pixel (in meters). Defaults to 10 m.

    Returns :
        shapely.geometry.Polygon: Adjusted square polygon.
    """
    bounds = polygon.bounds  # (xmin, ymin, xmax, ymax)
    xmin, ymin, xmax, ymax = bounds
    width = xmax - xmin
    height = ymax - ymin

    side = int(max(width, height))
    side = math.ceil(side / pixel_size) * pixel_size
    if (side / pixel_size) % 2 == 0:
        side += pixel_size
    center_x = (xmin + xmax) / 2
    center_y = (ymin + ymax) / 2
    new_xmin = center_x - side / 2
    new_xmax = center_x + side / 2
    new_ymin = center_y - side / 2
    new_ymax = center_y + side / 2
    return box(new_xmin, new_ymin, new_xmax, new_ymax)


def clean_directory(directory_path,keep_keywords):
    """
    Cleans up the directory by deleting unnecessary files/folders.

    Arguments:
        directory_path (str) : Directory path.
        keep_keywords (list) : Files to keep.
    """
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)

        # Delete folders
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
            print(f"Deleted folder : {item_path}")

        # Delete all other files
        elif os.path.isfile(item_path):
            if not any(keyword in item for keyword in keep_keywords):
                os.remove(item_path)
                print(f"Deleted file : {item_path}")
            else:
                print(f"Retained file : {item_path}")

#%% PATHS 

directory = "F:/Data_sat/Sentinel_2/temp/"
keep_keywords = ['FRE_B2', 'FRE_B4', 'FRE_B8.tif', 'FRE_B11', '.jpg'] 

# Coordinates of the polygon to be preserved (EPSG:4326)
polygon_coords_wgs84 = [
    [-1.220184, 46.229367],
    [-1.098190, 46.229367],
    [-1.098190, 46.334909],
    [-1.220184, 46.334909],
    [-1.220184, 46.229367]
]


#%% MAIN

# Pre-processing: Transformation and adjustment of the polygon into a square with an even number of pixels for 10m strips.
with rasterio.open(glob2.glob(directory + '*/*FRE_B2.tif')[0]) as src:
    coord_tif = src.crs
    transformed_polygon = transform_polygon(polygon_coords_wgs84, "EPSG:4326", coord_tif)
    square_polygon = adjust_to_square(transformed_polygon)
    validate_polygon_inclusion(square_polygon, src.bounds)

# Loop over TIF files for crop following square and clean directories
for paths in glob2.glob(directory + '*'):
    clean_directory(paths,keep_keywords)
    print(paths)
    for file in glob2.glob(paths + '/*.tif'):
        crop_tif(file, square_polygon)




