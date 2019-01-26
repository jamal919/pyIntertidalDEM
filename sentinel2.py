#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
from pyintdem import preprep
from pyintdem import improc
from pyintdem import vertref

# Directory Settings
raw_data_dir = '/run/media/khan/Sentinel2/RawData' # Zip Data
input_dir='/run/media/khan/PMAISONGDE/Analysis'
output_dir = '/run/media/khan/Sentinel2/Analysis' # Output

# Directory of saving unzipped data
data_dir = os.path.join(input_dir, 'Data') 
prep_dir = os.path.join(output_dir, 'Preprocess') 
improc_dir = os.path.join(output_dir, 'Shorelines') 
vertref_dir = os.path.join(output_dir, 'Referencing') 
waterlevel_dir = os.path.join(output_dir, 'WaterLevels')

for dloc in [input_dir, output_dir, data_dir, prep_dir, improc_dir, vertref_dir, waterlevel_dir]:
    if not os.path.exists(dloc):
        os.mkdir(dloc)

if __name__=='__main__':
    # list of zones
    zones = ['T45QWE', 'T45QXE', 'T45QYE', 'T46QBK', 'T46QCK', 'T46QBL', 'T46QCL']
    zones = ['T46QBL', 'T46QCL']
    zones = ['T46QCK']

    # # Data Extraction
    # zip_extractor = preprep.DataExtractor(input_dir=raw_data_dir, output_dir=data_dir)
    # zip_extractor.list_zones(debug=False)
    # for zone in zones:
    #     zip_extractor.extract(zone)

    # Tile Statistics
    zip_stat = preprep.Stat(data_dir=data_dir, prep_dir=prep_dir)
    zip_stat.plot_sampling(zones=zones)

    # Generate Water mask
    mask_generator = preprep.WaterMask(
        data_dir=data_dir,
        prep_dir=prep_dir,
        nstd_threshold=0.5,
        water_blob_size=10000,
        land_blob_size=5000
    )
    mask_generator.generate(zones)

    # Image Processing
    for zone in zones:
        zone_path = os.path.join(data_dir, zone)
        for zone_snap in os.listdir(zone_path):
            snap_dir = os.path.join(zone_path, zone_snap)
            
            # Process RGB data
            rgb_processor = improc.BandData(
                directory=snap_dir, 
                improcdir=improc_dir, 
                preprocdir=prep_dir, 
                png=True
            )
            rgb_processor.Data()
            
            # RGB to HSV Conversion
            hsv_processor = improc.HSVData(
                directory=snap_dir,
                improcdir=improc_dir,
                preprocdir=prep_dir,
                png=True
            )
            hsv_processor.HueValueRGB()
            
            # Water Map generation
            water_map = improc.WaterMap(
                directory=snap_dir, 
                improcdir=improc_dir, 
                preprocdir=prep_dir,
                nhue = 0.5,
                nvalue = 5.0,
                png=True
            )
            water_map.GetBinaryWaterMap()
            
            # Filter blob in the water map
            feature_filter = improc.FeatureFilter(
                directory=snap_dir,
                improcdir=improc_dir,
                preprocdir=prep_dir,
                nwater=50000,
                nland=10000,
                png=True
            )
            feature_filter.FilterWaterMap()
            
            # Shoereline generation
            shoreline_generator = improc.Shoreline(
                directory=snap_dir,
                improcdir=improc_dir,
                preprocdir=prep_dir
            )
            shoreline_generator.generate()
    
    # # Vertical referencing
    # for zone in zones:
    #     dem_generator = vertref.Dem(
    #         improc_dir=improc_dir,
    #         waterlevel_dir=waterlevel_dir,
    #         vertref_dir=vertref_dir
    #     )
    #     dem_generator.set_vetical_heights(zone=zone)