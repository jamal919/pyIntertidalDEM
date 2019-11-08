#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from pyintdem.util import Extractor

data_dir = '/run/media/khan/Sentinel2/RawData'
out_dir='/run/media/khan/Backup KE Maxelev/Data'

extractor = Extractor(input_dir=data_dir, output_dir=out_dir)
extractor.list_zones(debug=True)
for zone in extractor.zones:
    extractor.extract(zone=zone)