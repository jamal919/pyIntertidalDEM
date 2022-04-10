#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyintdem.util import Extractor
import os

data_dir = '/run/media/khan/Sentinel2/RawData'
out_dir='/run/media/khan/Backup KE Maxelev/Data'

if not os.path.exists(out_dir):
    os.mkdir(out_dir)

extractor = Extractor(input_dir=data_dir, output_dir=out_dir)
extractor.list_zones(debug=True)
for zone in extractor.zones:
    extractor.extract(zone=zone)