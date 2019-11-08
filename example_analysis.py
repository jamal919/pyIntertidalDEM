#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import gc
import time
import numpy as np
import matplotlib.pyplot as plt
from pyintdem.core import Band, RGB
from pyintdem.data import Sentinel2

# Directory Settings
raw_data_dir = '/run/media/khan/Sentinel2/RawData' # Zip Data
input_dir='/run/media/khan/Backup KE Maxelev'
output_dir = '/run/media/khan/Backup KE Maxelev/Analysis_v3' # Output

# Directory of saving unzipped data
data_dir = os.path.join(input_dir, 'Data')
mask_dir = os.path.join(output_dir, 'Masks') 
improc_dir = os.path.join(output_dir, 'Shorelines') 
vertref_dir = os.path.join(output_dir, 'Referencing') 
waterlevel_dir = os.path.join(output_dir, 'WaterLevels')
dem_dir = os.path.join(output_dir, 'DEM')

zones = ['T45QWE', 'T45QXE', 'T45QYE', 'T46QBK', 'T46QCK', 'T46QBL', 'T46QCL']

if __name__=='__main__':
    for zone in zones:
        zone_dir = os.path.join(data_dir, zone)
        snaps = os.listdir(zone_dir)
        for snap_dir in snaps:
            print(snap_dir)
            snap_file = Sentinel2(loc=os.path.join(zone_dir, snap_dir))
            snap_save = os.path.join(improc_dir, snap_file.info['zone'])
            if not os.path.exists(snap_save):
                os.mkdir(snap_save)
            snap_save = os.path.join(
                snap_save, 
                snap_file.info['date_time'].strftime('%Y%m%d%H%M%S')
                )
            if not os.path.exists(snap_save):
                os.mkdir(snap_save)

            # Alpha band
            alpha = Band()
            alpha.read(fname=snap_file.files['FRE_B11'], band=1)
            alpha.set_missing(value=-10000, to=np.nan)
            alpha = alpha/10000
            alpha.upscale(factor=2, method='nearest')
            print('Max = {:.2f}, Std = {:.2f}, Mean = {:.2f}, Cut = {:.2f}'.format(alpha.max, alpha.std, alpha.mean, alpha.mean+alpha.std))
            alpha.normalize(method='std', std_factor=1, std_correction='high')
            alpha.plot('Upscaled Normalized Alpha', cmap='binary_r', saveto=os.path.join(snap_save, 'alpha.png'))
            alpha.to_geotiff(fname=os.path.join(snap_save, 'alpha.tif'))

            # Red
            red = Band()
            red.read(fname=snap_file.files['FRE_B4'], band=1)
            red.set_missing(value=-10000, to=np.nan)
            red = red/10000
            red.normalize(method='minmax')
            red.plot('Normalized Red', cmap='binary_r', saveto=os.path.join(snap_save, 'red_norm.png'))
            red = (red*alpha) + (alpha*-1+1)
            red.plot('Synthetic Red', cmap='binary_r', saveto=os.path.join(snap_save, 'red_synthetic.png'))
            red.to_geotiff(fname=os.path.join(snap_save, 'red_synthetic.tif'))

            # Green
            green = Band()
            green.read(fname=snap_file.files['FRE_B8'], band=1)
            green.set_missing(value=-10000, to=np.nan)
            green = green/10000
            green.normalize(method='minmax')
            green.plot('Normalized Green', cmap='binary_r', saveto=os.path.join(snap_save, 'green_norm.png'))
            green = (alpha*-1+1) + (green*alpha)
            green.plot('Synthetic Green', cmap='binary_r', saveto=os.path.join(snap_save, 'green_synthetic.png'))
            green.to_geotiff(fname=os.path.join(snap_save, 'green_synthetic.tif'))

            # Blue
            blue = Band()
            blue.read(fname=snap_file.files['FRE_B2'], band=1)
            blue.set_missing(value=-10000, to=np.nan)
            blue = blue/10000
            blue.normalize(method='minmax')
            blue.plot('Normalized Blue', cmap='binary_r', saveto=os.path.join(snap_save, 'blue_norm.png'))
            blue = (alpha*-1+1) + (blue*alpha)
            blue.plot('Synthetic Blue', 'binary_r', saveto=os.path.join(snap_save, 'blue_synthetic.png'))
            blue.to_geotiff(fname=os.path.join(snap_save, 'green_synthetic.tif'))

            # RGB HSV Conversion
            rgb = RGB(red=red, green=green, blue=blue)
            del red, green, blue, alpha
            rgb.plot(title='RGB', saveto=os.path.join(snap_save, 'rgb.png'))
            hue, _, value = rgb.to_hsv(method='matplotlib')
            del rgb
            hue.plot('Hue', cmap='binary_r', saveto=os.path.join(snap_save, 'hue.png'))
            value.plot('Value', cmap='binary_r', saveto=os.path.join(snap_save, 'value.png'))
            hue.to_geotiff(fname=os.path.join(snap_save, 'hue.tif'))
            value.to_geotiff(fname=os.path.join(snap_save, 'value.tif'))

            # Water masks
            watermask = Band()
            watermask.read(
                fname=snap_file.watermask(loc=mask_dir),
                band=1
                )
            watermask.plot('Water Mask', cmap='binary_r', saveto=os.path.join(snap_save, 'watermask.png'))

            # Masking and calculating thresholds
            hue_mask = hue.mask(by=watermask, inverse=True)
            hue_mask.plot('Inversed masked hue', saveto=os.path.join(snap_save, 'hue_masked.png'))
            value_mask = value.mask(by=watermask)
            value_mask.plot('Masked value', saveto=os.path.join(snap_save, 'value_masked.png'))
            
            hue_median = hue_mask.median
            hue_std = hue_mask.std
            value_median = value_mask.median
            value_std = value_mask.std
            
            del watermask, hue_mask, value_mask

            # Threholding
            nhues = [0.5]
            nvalues = [3.0]
            nhues, nvalues = np.meshgrid(nhues, nvalues)
            
            for nhue, nvalue in zip(nhues.flatten(), nvalues.flatten()):
                # nhue = 1.0
                hue_bw = (
                    (hue<(hue_median+nhue*hue_std)).logical_and(
                        hue>(hue_median-nhue*hue_std)
                    )
                ).logical_not()
                hue_bw.plot('Hue BW', saveto=os.path.join(snap_save, 'hue_bw_{:.1f}.png'.format(nhue)))
                hue_bw.to_geotiff(fname=os.path.join(snap_save, 'hue_bw_{:.1f}.tif'.format(nhue)))
                
                # nvalue = 1.5
                value_bw = (value<(value_median+nvalue*value_std)).logical_and(
                    value>(value_median-nvalue*value_std)
                )
                value_bw.plot('Value BW', saveto=os.path.join(snap_save, 'value_bw_{:.1f}.png'.format(nvalue)))
                value_bw.to_geotiff(fname=os.path.join(snap_save, 'value_bw_{:.1f}.tif'.format(nvalue)))

                bw = value_bw.logical_and(hue_bw)
                del value_bw, hue_bw
                
                bw.plot('BW', cmap='binary', saveto=os.path.join(snap_save, 'bw_{:.1f}_{:.1f}.png'.format(nhue, nvalue)))
                bw.to_geotiff(fname=os.path.join(snap_save, 'bw_{:.1f}_{:.1f}.tif'.format(nhue, nvalue)))

                bw = bw.clean(npixel=10000, fillvalue=0, background=False) # Water
                bw = bw.clean(npixel=10000, fillvalue=1, background=True) # Land
                bw.plot('BW Clean', cmap='binary', saveto=os.path.join(snap_save, 'bw_clean_{:.1f}_{:.1f}.png'.format(nhue, nvalue)))
                bw.to_geotiff(fname=os.path.join(snap_save, 'bw_clean_{:.1f}_{:.1f}.tif'.format(nhue, nvalue)))

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
                    saveto=os.path.join(snap_save, 'shoreline_{:.1f}_{:.1f}.csv'.format(nhue, nvalue))
                )

                del bw
                gc.collect()