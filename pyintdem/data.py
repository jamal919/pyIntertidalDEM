#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Data and Metadata holder for different satellites

TODO: 
    * merge extraction facility for individual satellite
    * streamline the file data extraction

Author: khan
Email: jamal.khan@legos.obs-mip.fr
'''

from datetime import datetime
from glob import glob
import os

class Sentinel2(object):
    def __init__(self, loc, datefmt='%Y%m%d-%H%M%S-%f'):
        '''
        File information holder for unpacked Sentinel-2 images.

        arguments:
            loc: string
                Location of the unpacked tile of a single Sentinel-2 image
            datefmt: string
                Format string to extract the datetime

        returns:
            object: Sentinel2
        '''
        self.loc = loc
        self.file_prefix = os.path.basename(self.loc)
        _metadata = self.file_prefix.split('_')
        self.files = dict()

        for floc in glob(os.path.join(self.loc, '*.*')):
            fname = os.path.basename(floc)
            fname = fname.split(sep=self.file_prefix)[-1][1:].split('.')[0]
            self.files[fname] = floc

        for subdir in glob(os.path.join(self.loc, '*/')):
            subdir_name = os.path.basename(subdir[:-1]) # Avoiding trailing sep
            self.files[subdir_name] = dict()
            for floc in glob(os.path.join(subdir, '*.*')):
                fname = os.path.basename(floc)
                fname = fname.split(sep=self.file_prefix)[-1][1:].split('.')[0]
                self.files[subdir_name][fname] = floc

        self.info = dict(
            dir = self.loc,
            file_prefix = self.file_prefix,
            satellite = _metadata[0],
            date_time = datetime.strptime(_metadata[1], datefmt),
            level = _metadata[2],
            zone = _metadata[3],
            meta = _metadata[4],
            version = _metadata[5]
        )

    def watermask(self, loc, id=['zone'], fmt='tif'):
        '''
        Return the location of the water mask based on the id and format fmt. 
        The id can be nested for a nested setup. The last element of the id will
        be used to infer the name of the file itself.

        arguments:
            loc: string
                Location of the mask files
            id: array of string
                organization of the mask file in folders. id[-1] is the name of
                the mask file.
            fmt: string
                file format extension without preceeding dot

        returns:
            Mask file location: string
        '''
        _maskfile = loc
        if len(id) > 1:
            for i in id[:-1]:
                _maskfile = os.path.join(_maskfile, self.info[i])

            _maskfile = os.path.join(_maskfile, '{:s}.{:s}'.format(self.info[id[-1]], fmt))
        elif len(id) == 1:
            _maskfile = os.path.join(loc, '{:s}.{:s}'.format(self.info[id[0]], fmt))
        
        return(_maskfile)

    def __repr__(self):
        return(''.join('{:<15s} : {:s}\n'.format(i, self.info[i].__repr__()) for i in self.info))