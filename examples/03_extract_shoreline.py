# uncomment the following if you had not installed the package
# import sys
# sys.path.append('/home/khan/Documents/developments/pyIntertidalDEM')

from pyintdem.core import RGB
from pyintdem.data import Database, DataFile
from pathlib import Path
import logging
from tqdm.autonotebook import tqdm
import gc
import numpy as np

def workflow_khan2019(
        datafile,
        datafiledir,
        maskdir,
        nhue=0.5, nvalue=3.0,
        waterblob=10000, landblob=10000,
        savetifs=False, saveplots=False):
    # Alpha band
    alpha = datafile.get_band('B11', preprocess=True)
    alpha.upscale(factor=2, method='nearest')
    logging.info('Max = {:.2f}, Std = {:.2f}, Mean = {:.2f}, Cut = {:.2f}'.format(alpha.max, alpha.std, alpha.mean, alpha.mean+alpha.std))
    alpha.normalize(method='std', std_factor=1, std_correction='high')
    if saveplots:
        alpha.plot('Upscaled Normalized Alpha', cmap='binary_r', saveto=datafiledir/'alpha.png')
    if savetifs:
        alpha.to_geotiff(fname=datafiledir/'alpha.tif')

    # Red band
    red = datafile.get_band('B4', preprocess=True)
    red.normalize(method='minmax')
    red.plot('Normalized Red', cmap='binary_r', saveto=datafiledir/'red_norm.png')
    red = (red*alpha) + (alpha*-1+1)
    if saveplots:
        red.plot('Synthetic Red', cmap='binary_r', saveto=datafiledir/'red_synthetic.png')
    if savetifs:
        red.to_geotiff(fname=datafiledir/'red_synthetic.tif')

    # Green
    green = datafile.get_band('B8', preprocess=True)
    green.normalize(method='minmax')
    green.plot('Normalized Green', cmap='binary_r', saveto=datafiledir/'green_norm.png')
    green = (alpha*-1+1) + (green*alpha)
    if saveplots:
        green.plot('Synthetic Green', cmap='binary_r', saveto=datafiledir/'green_synthetic.png')
    if savetifs:
        green.to_geotiff(fname=datafiledir/'green_synthetic.tif')

    # Blue
    blue = datafile.get_band('B2', preprocess=True)
    blue.normalize(method='minmax')
    blue.plot('Normalized Blue', cmap='binary_r', saveto=datafiledir/'blue_norm.png')
    blue = (alpha*-1+1) + (blue*alpha)
    if saveplots:
        blue.plot('Synthetic Blue', 'binary_r', saveto=datafiledir/'blue_synthetic.png')
    if savetifs:
        blue.to_geotiff(fname=datafiledir/'blue_synthetic.tif')

    # RGB HSV Conversion
    rgb = RGB(red=red, green=green, blue=blue)
    del red, green, blue, alpha
    rgb.plot(title='RGB', saveto=datafiledir/'rgb.png')
    hue, _, value = rgb.to_hsv(method='matplotlib')
    del rgb
    if saveplots:
        hue.plot('Hue', cmap='binary_r', saveto=datafiledir/'hue.png')
        value.plot('Value', cmap='binary_r', saveto=datafiledir/'value.png')
    if savetifs:
        hue.to_geotiff(fname=datafiledir/'hue.tif')
        value.to_geotiff(fname=datafiledir/'value.tif')

    # Water masks
    watermask = datafile.get_mask(mask_dir=maskdir)
    watermask.upscale(factor=2)
    if saveplots:
        watermask.plot('Water Mask', cmap='binary_r', saveto=datafiledir/'watermask.png')

    # Masking and calculating thresholds
    hue_mask = hue.mask(by=watermask, inverse=True)
    if saveplots:
        hue_mask.plot('Inversed masked hue', saveto=datafiledir/'hue_masked.png')
    value_mask = value.mask(by=watermask)
    if saveplots:
        value_mask.plot('Masked value', saveto=datafiledir/'value_masked.png')

    hue_median = hue_mask.median
    hue_std = hue_mask.std
    value_median = value_mask.median
    value_std = value_mask.std

    del watermask, hue_mask, value_mask

    # Thresholding
    hue_bw = (
        (hue<(hue_median+nhue*hue_std)).logical_and(
            hue>(hue_median-nhue*hue_std)
        )
    ).logical_not()
    if saveplots:
        hue_bw.plot('Hue BW', saveto=datafiledir/'hue_bw_{:.1f}.png'.format(nhue))
    if savetifs:
        hue_bw.to_geotiff(fname=datafiledir/'hue_bw_{:.1f}.tif'.format(nhue))

    value_bw = (value<(value_median+nvalue*value_std)).logical_and(
        value>(value_median-nvalue*value_std)
    )
    if saveplots:
        value_bw.plot('Value BW', saveto=datafiledir/'value_bw_{:.1f}.png'.format(nvalue))
    if savetifs:
        value_bw.to_geotiff(fname=datafiledir/'value_bw_{:.1f}.tif'.format(nvalue))

    bw = value_bw.logical_and(hue_bw)
    del value_bw, hue_bw
    if saveplots:
        bw.plot('BW', cmap='binary', saveto=datafiledir/'bw_{:.1f}_{:.1f}.png'.format(nhue, nvalue))
    if savetifs:
        bw.to_geotiff(fname=datafiledir/'bw_{:.1f}_{:.1f}.tif'.format(nhue, nvalue))

    bw = bw.clean(npixel=waterblob, fillvalue=0, background=False) # Water
    bw = bw.clean(npixel=landblob, fillvalue=1, background=True) # Land
    if saveplots:
        bw.plot('BW Clean', cmap='binary', saveto=datafiledir/'bw_clean_{:.1f}_{:.1f}.png'.format(nhue, nvalue))
    if savetifs:
        bw.to_geotiff(fname=datafiledir/'bw_clean_{:.1f}_{:.1f}.tif'.format(nhue, nvalue))

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
        xyloc=np.where(shoreline.data==1),
        epsg=4326,
        center=True,
        saveto=datafiledir/'shoreline_{:.1f}_{:.1f}.csv'.format(nhue, nvalue)
    )

    del bw
    gc.collect()

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, filename='03_extract_shoreline.log', filemode='w')
    logging.captureWarnings(True)

    rootdir = Path('F:/Sentinel2')
    datadir = rootdir / 'Data'
    maskdir = rootdir / 'Masks'
    shorelinedir = Path('E:') / 'Shorelines'

    database = Database(datadir)

    # Parameters
    nhue = 0.5  # Thresholding parameter for Hue band
    nvalue = 3.0  # Thresholding parameter for Value band

    waterblob = 10000  # Remove water blob smaller than 10000 pixels
    landblob = 10000  # Remove land blobs smaller than 10000 pixels

    # Running the algorithm over the database
    for tile in database:
        tiledir = shorelinedir / tile
        if not tiledir.exists():
            tiledir.mkdir()
        for datafile in tqdm(database[tile], desc=tile):
            datafiledir = tiledir / datafile['time'].strftime('%Y%m%d%H%M%S')
            if not datafiledir.exists():
                datafiledir.mkdir()

            workflow_khan2019(datafile=datafile,
                              datafiledir=datafiledir,
                              maskdir=maskdir,
                              nhue=nhue, nvalue=nvalue,
                              waterblob=waterblob, landblob=landblob,
                              savetifs=False, saveplots=True)

