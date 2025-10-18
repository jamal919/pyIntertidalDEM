# -*- encoding: utf-8 -*-
import gc
import logging
from pathlib import Path

import numpy as np
from skimage import measure
import geopandas as gpd
from shapely import LineString
from rioxarray.exceptions import NoDataInBounds
from tqdm.autonotebook import tqdm

from pyintdem import read_file
from pyintdem.models.band import Band, RGB

logger = logging.getLogger(__name__)

KERNEL_LAPLACE = np.array(
    [
        [0, -1, 0],
        [-1, 4, -1],
        [0, -1, 0]
    ])

def create_mask(database, maskdir,
                nmask=0.5,
                ext='tif', band='B11',
                normalize=True, clip_kw=None):
    """
    Create mask from the database for all the tiles

    Args:
        database: Database of Sentinel-2 files
        maskdir: Location of the mask directory
        nmask: Thresholding values, typically 0.5 to 0.75
        ext: Extension for the saved mask file
        band: The band to use for thresholding, B11
        normalize: To normalize or not, normally True
        clip_kw: A dictionary of one or all components {'bbox', 'geoms'} for clipping

    Returns: None

    """

    maskdir = Path(maskdir)
    if not maskdir.exists():
        maskdir.mkdir(parents=True)

    to_clip = False
    if clip_kw is not None:
        print("The images will be clipped")
        to_clip = True

    for tile in tqdm(database):
        fname = maskdir / f'{tile}.{ext}'
        datafiles = database[tile]
        for i, datafile in enumerate(datafiles):
            img_band = datafile.get_band(band, preprocess=True)

            if to_clip:
                try:
                    img_band = img_band.clip(**clip_kw)
                except NoDataInBounds:
                    print("Data not found for the clipped zone")

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


def prepare_bands(datafile, clip_kw=None):
    """
    Auxiliary function to be used in the extract_shoreline to prepare bands
    Args:
        datafile: datafile to be processed
        clip_kw: Dictionary of one or all components {'bbox', 'geoms'} for clipping

    Returns: red, green, blue, alpha bands

    """
    to_clip = False
    if clip_kw is not None:
        print("The images will be clipped")
        to_clip = True

    # Loading data
    alpha = datafile.get_band('B11', preprocess=True)
    red = datafile.get_band('B4', preprocess=True)
    green = datafile.get_band('B8', preprocess=True)
    blue = datafile.get_band('B2', preprocess=True)

    # Upscale alpha to match others
    alpha = alpha.reproject_match(red)

    # Apply clipping
    if to_clip:
        alpha = alpha.clip(**clip_kw)
        red = red.clip(**clip_kw)
        green = green.clip(**clip_kw)
        blue = blue.clip(**clip_kw)

    # Normalize bands
    alpha.normalize(method='std', std_factor=1, std_correction='high')
    red.normalize(method='minmax')
    green.normalize(method='minmax')
    blue.normalize(method='minmax')

    return red, green, blue, alpha

def prepare_mask(datafile: pyintdem.Data.DataFile, clip_kw=None):
    pass


def create_synthetic_rgb(red: Band, green: Band, blue:Band, alpha:Band) -> [Band, Band, Band]:
    """
    Create synthetic red, green and blue bands using the alpha bands

    Returns: red, green, blue

    """
    red = (red * alpha) + (alpha * -1 + 1)
    green = (alpha * -1 + 1) + (green * alpha)
    blue = (alpha * -1 + 1) + (blue * alpha)

    return red, green, blue




def compute_hue_value(datafile, datafiledir,
                      savetifs=False, saveplots=False,
                      clip_kw=None):
    """
    Compute hue and value for the given datafile
    Args:
        datafile: datafile to be processed
        datafiledir: directory to save the output
        savetifs: if the tifs should be saved
        saveplots: if the plots should be saved
        clip_kw: Dictionary of one or all components {'bbox', 'geoms'} for clipping

    Returns: hue, value

    """
    red, green, blue, alpha = prepare_bands(datafile, clip_kw=clip_kw)

    if savetifs:
        red.to_geotiff(fname=datafiledir / 'red_norm.tif')
        green.to_geotiff(fname=datafiledir / 'green_norm.tif')
        blue.to_geotiff(fname=datafiledir / 'blue_norm.tif')
        alpha.to_geotiff(fname=datafiledir / 'alpha_norm.tif')

    if saveplots:
        alpha.plot('Upscaled Normalized Alpha', cmap='binary_r', saveto=datafiledir / 'alpha_norm.png')
        red.plot('Normalized Red', cmap='binary_r', saveto=datafiledir / 'red_norm.png')
        green.plot('Normalized Green', cmap='binary_r', saveto=datafiledir / 'green_norm.png')
        blue.plot('Normalized Blue', cmap='binary_r', saveto=datafiledir / 'blue_norm.png')

    red, green, blue = create_synthetic_rgb(red, green, blue, alpha)

    if savetifs:
        red.to_geotiff(fname=datafiledir / 'red_synthetic.tif')
        green.to_geotiff(fname=datafiledir / 'green_synthetic.tif')
        blue.to_geotiff(fname=datafiledir / 'blue_synthetic.tif')

    if saveplots:
        red.plot('Normalized Red', cmap='binary_r', saveto=datafiledir / 'red_synthetic.png')
        green.plot('Normalized Green', cmap='binary_r', saveto=datafiledir / 'green_synthetic.png')
        blue.plot('Normalized Blue', cmap='binary_r', saveto=datafiledir / 'blue_synthetic.png')

    # RGB HSV Conversion
    rgb = RGB(red=red, green=green, blue=blue)
    del red, green, blue, alpha
    rgb.plot(title='RGB', saveto=datafiledir / 'rgb.png')
    hue, _, value = rgb.to_hsv(method='matplotlib')
    del rgb

    if saveplots:
        hue.plot('Hue', cmap='binary_r', saveto=datafiledir / 'hue.png')
        value.plot('Value', cmap='binary_r', saveto=datafiledir / 'value.png')

    # Hue and value tifs are always saved
    hue.to_geotiff(fname=datafiledir / 'hue.tif')
    value.to_geotiff(fname=datafiledir / 'value.tif')

    return hue, value

def apply_thresholding_hue(ds: Band, mask: Band, nhue:float=0.5) -> Band:
    pass

def apply_thresholding_value(ds: Band, mask: Band, nvalue:float=3.0) -> Band:
    pass

def apply_cleaning(ds: Band, waterblob=10000, landblob=1000) -> Band:
    pass

def extract_waterline_points_with_kernel(
        ds: Band,
        kernel: np.ndarray = KERNEL_LAPLACE,
        replacenan:bool=False,
        replacevalue:float=4,
        fillvalue:float=4,
        nanmask:bool=True,
        cleanedge:bool=True):
    pass

def extract_waterlines(ds: Band, level:float=0.5, epsg:int=4326) -> gpd.GeoDataFrame:
    """
    Extract waterline linestring from the sagmented band dataset

    Args:
        ds: binary sagmented water/land dataset
        level: default to 0.5, i.e., the line will be extracted at the middle
        epsg: target projection, default to 4326 (lon-lat)

    Returns: GeoDataFrame

    """
    contours = measure.find_contours(ds.data, level=level)
    contours_latlon = [ds.position(contour.T, epsg=epsg, center=True) for contour in contours]
    linestrings_contours_latlon = [LineString(contour[:, [1, 0]]) for contour in contours_latlon]
    gdf_shorelines = gpd.GeoDataFrame(geometry=linestrings_contours_latlon)
    gdf_shorelines = gdf_shorelines.set_crs(epsg=epsg)

    return gdf_shorelines

def get_waterline_points(method="marching_square", kernel_kw=None) -> gpd.GeoDataFrame:
    # method: kernel
    # method: marching_square
    pass

def extract_shoreline(datafile, datafiledir, maskdir,
                      nhue=0.5, nvalue=3.0,
                      waterblob=10000, landblob=10000,
                      savetifs=False, saveplots=False,
                      clip_kw=None, recompute=True):
    """
    Extract shorelines using dataset

    Args:
        datafile: datafile to be processed
        datafiledir: path to where outputs will be saved
        maskdir: path to mask directory
        nhue: threshold multiplier for hue, default 0.5
        nvalue: threshold multiplier for value, default 3.0
        waterblob: minimum size of water body over land
        landblob: minimum size of land body over ocean/water
        savetifs: if the intermediate tifs should be saved, set False for faster processing
        saveplots: if the intermediate plots should be saved, set False for faster processing
        clip_kw: Dictionary of one or all components {'bbox', 'geoms'} for clipping
        recompute: Force recompute hue and value files, True

    Returns: Processed dataset are saved in the datafiledir

    """
    logger = logging.getLogger(__name__)
    datafiledir = Path(datafiledir)

    hue_value_is_computed = False
    fname_hue = datafiledir / 'hue.tif'
    fname_value = datafiledir / 'value.tif'

    if fname_hue.exists() and fname_value.exists():
        hue_value_is_computed = True

    if recompute or not hue_value_is_computed:
        # compute is requested or needed
        hue, value = compute_hue_value(
            datafile=datafile, datafiledir=datafiledir,
            savetifs=savetifs, saveplots=saveplots,
            clip_kw=clip_kw)
    else:
        # load the existing dataset
        hue = read_file(fname_hue, band=1)
        value = read_file(fname_value, band=1)

    # Load water mask
    watermask = datafile.get_mask(mask_dir=maskdir)
    watermask = watermask.reproject_match(hue)

    if saveplots:
        watermask.plot('Water Mask', cmap='binary_r', saveto=datafiledir / 'watermask.png')

    # Masking and calculating thresholds
    hue_mask = hue.mask(by=watermask, inverse=True)
    if saveplots:
        hue_mask.plot('Inversed masked hue', saveto=datafiledir / 'hue_masked.png')
    value_mask = value.mask(by=watermask)
    if saveplots:
        value_mask.plot('Masked value', saveto=datafiledir / 'value_masked.png')

    hue_median = hue_mask.median
    hue_std = hue_mask.std
    value_median = value_mask.median
    value_std = value_mask.std

    del watermask, hue_mask, value_mask

    # Thresholding
    hue_bw = (
        (hue < (hue_median + nhue * hue_std)).logical_and(
            hue > (hue_median - nhue * hue_std)
        )
    ).logical_not()
    if saveplots:
        hue_bw.plot('Hue BW', saveto=datafiledir / f'hue_bw_{nhue:.1f}.png')
    if savetifs:
        hue_bw.to_geotiff(fname=datafiledir / f'hue_bw_{nhue:.1f}.tif')

    value_bw = (value < (value_median + nvalue * value_std)).logical_and(
        value > (value_median - nvalue * value_std)
    )
    if saveplots:
        value_bw.plot('Value BW', saveto=datafiledir / f'value_bw_{nvalue:.1f}.png')
    if savetifs:
        value_bw.to_geotiff(fname=datafiledir / f'value_bw_{nvalue:.1f}.tif')

    bw = value_bw.logical_and(hue_bw)
    del value_bw, hue_bw
    if saveplots:
        bw.plot('BW', cmap='binary', saveto=datafiledir / f'bw_{nhue:.1f}_{nvalue:.1f}.png')
    if savetifs:
        bw.to_geotiff(fname=datafiledir / f'bw_{nhue:.1f}_{nvalue:.1f}.tif')

    bw = bw.clean(npixel=waterblob, fillvalue=0, background=False)  # Water
    bw = bw.clean(npixel=landblob, fillvalue=1, background=True)  # Land
    if saveplots:
        bw.plot('BW Clean', cmap='binary', saveto=datafiledir / f'bw_clean_{nhue:.1f}_{nvalue:.1f}.png')

    bw.to_geotiff(fname=datafiledir / f'bw_clean_{nhue:.1f}_{nvalue:.1f}.tif')

    # Shoreline mapping
    shoreline = bw.convolute(
        kernel=[[0, -1, 0], [-1, 4, -1], [0, -1, 0]],
        replacenan=False,
        replacevalue=4,
        fillvalue=4,
        nanmask=True,
        cleanedge=True
    )
    shoreline.position(
        xyloc=np.where(shoreline.data == 1),
        epsg=4326,
        center=True,
        saveto=datafiledir / f'shoreline_{nhue:.1f}_{nvalue:.1f}.csv'
    )

    del bw
    gc.collect()


def process_database(database, out_dir, mask_dir,
                     nhue=0.5, nvalue=3.0,
                     waterblob=10000, landblob=10000,
                     savetifs=False, saveplots=True,
                     clip_kw=None, recompute=False):
    """
    Process the dataset using the shoreline processing scheme
    Args:
        database: database to process
        out_dir: output directory
        mask_dir: mask directory
        nhue: threshold multiplier for hue, default 0.5
        nvalue: threshold multiplier for value, default 3.0
        waterblob: minimum size of water body over land
        landblob: minimum size of land body over ocean/water
        savetifs: if the intermediate tifs should be saved, set False for faster processing
        saveplots: if the intermediate plots should be saved, set False for faster processing
        clip_kw: Dictionary of one or all components {'bbox', 'geoms'} for clipping
        recompute: recompute hue and value files

    Returns: results are saved in the out_dir

    """
    out_dir = Path(out_dir)
    if not out_dir.exists():
        out_dir.mkdir()

    for tile in database:
        tile_dir = out_dir / tile
        if not tile_dir.exists():
            tile_dir.mkdir()

        for datafile in tqdm(database[tile], desc=tile):
            datafile_dir = tile_dir / datafile['time'].strftime('%Y%m%d%H%M%S')
            logger.info(f"Tile: {tile} for {datafile_dir.name} now processing")
            if not datafile_dir.exists():
                datafile_dir.mkdir()

            try:
                extract_shoreline(
                    datafile=datafile,
                    datafiledir=datafile_dir,
                    maskdir=mask_dir,
                    nhue=nhue, nvalue=nvalue,
                    waterblob=waterblob, landblob=landblob,
                    savetifs=savetifs, saveplots=saveplots,
                    clip_kw=clip_kw, recompute=recompute)
                logger.info(f"Tile: {tile} for {datafile_dir.name} is processed")
            except Exception as e:
                logger.error(f"Tile: {tile} for {datafile_dir.name} error: {e}")

            gc.collect()
