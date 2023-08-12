#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib.pyplot as plt
from pyintdem.core import Band, RGB
from pyintdem.data import Sentinel2
from tqdm import tqdm

# Input setting
input_dir='/run/media/khan/Backup KE Maxelev'
data_dir = os.path.join(input_dir, 'Data')

# Directory of saving unzipped data
output_dir = '/run/media/khan/Backup KE Maxelev/Analysis_v3' # Output
save_dir = os.path.join(output_dir, 'Masks') 

for idir in [output_dir, save_dir]:
    if not os.path.exists(idir):
        os.mkdir(idir)

# Actual computation
zones = os.listdir(data_dir) # or select by passing a list ['T45QWF', 'T45QXF', 'T45QYF']
nmask = 0.5 # Threshold

if __name__=='__main__':
    for zone in zones:
        zone_dir = os.path.join(data_dir, zone)
        snaps = os.listdir(zone_dir)
        snap_files = [Sentinel2(loc=os.path.join(zone_dir, snap)) for snap in snaps]
        
        # Nan-averaged merging of B11
        for i, snap_file in enumerate(tqdm(snap_files, desc=zone)):
            if i == 0:
                b = Band()
                b.read(fname=snap_file.files['FRE_B11'], band=1)
                b.set_missing(value=-10000, to=np.nan)
                count_band = np.logical_not(np.isnan(b.data)).astype(int)
                b = b/10000
            else:
                other = Band()
                other.read(fname=snap_file.files['FRE_B11'], band=1)
                other.set_missing(value=-10000, to=np.nan)
                count_band = count_band + np.logical_not(np.isnan(other.data))
                other = other/10000
                count_band = count_band + np.logical_not(np.isnan(other.data))
                b = b.nan_sum(other)

        count_band = Band(data=count_band, geotransform=b.geotransform, projection=b.projection)
        # count_band.to_geotiff(fname=os.path.join(save_dir, f'{zone}_count.tif')) # uncomment to sava valid image/pixel
        b = b / count_band # Averaging
        
        # b.to_geotiff(fname=os.path.join(save_dir, f'{zone}_noth.tif')) # uncomment to save before threshold
        b = b < nmask*b.std # Applying the Threshold
        b.upscale(factor=2)
        b.to_geotiff(fname=os.path.join(save_dir, f"{zone}.tif"))