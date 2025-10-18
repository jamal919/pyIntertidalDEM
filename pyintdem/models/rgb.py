#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

import matplotlib.colors as mcl
import matplotlib.pyplot as plt
import numpy as np
from osgeo import gdal

from .band import Band


class RGB(object):
    def __init__(self, red, green, blue):
        """
        RGB band using in the red-green-blue band.

        argument:
            red: Band
                Red band to construct RGB
            green: Band
                Green band to construct RGB
            blue: Band
                Blue band to construct RGB
        """
        try:
            # Type checking
            assert np.all(
                [
                    isinstance(red, Band),
                    isinstance(green, Band),
                    isinstance(blue, Band)
                ]
            )
        except:
            raise AssertionError('In RGB: Not an instance of Band data')
        try:
            # Shape checking
            assert np.all(
                [
                    np.all(red.data.shape == green.data.shape),
                    np.all(green.data.shape == blue.data.shape)
                ]
            )
        except:
            raise AssertionError('In RGB: Bands are not of equal size')
        else:
            # Projection information
            self.geotransform = red.geotransform
            self.projection = red.projection

            # Build the RGB
            row, col = red.data.shape[0:2]
            self.rgb = np.empty(shape=[row, col, 3])
            self.rgb[:, :, 0] = red.data
            self.rgb[:, :, 1] = green.data
            self.rgb[:, :, 2] = blue.data

    @staticmethod
    def rgb2hsv(r, g, b):
        """
        Local Implementation of RGB to HSV.
        Arguments:
            r: double, red value
            g: double, green value
            b: double, blue value

        returns:
            (hue, saturation, value)
        """
        if np.any([np.isnan(r), np.isnan(g), np.isnan(b)]):
            h = np.nan
            s = np.nan
            v = np.nan
        else:
            mx = np.max([r, g, b])
            mn = np.min([r, g, b])
            df = mx - mn

            if mx == mn:
                h = 0
            elif mx == r:
                h = (60 * ((g - b) / df) + 360) % 360
            elif mx == g:
                h = (60 * ((b - r) / df) + 120) % 360
            elif mx == b:
                h = (60 * ((r - g) / df) + 240) % 360

            h = h / 360.0

            if mx == 0:
                s = 0
            else:
                s = df / mx

            v = mx

        return h, s, v

    def to_hsv(self, method='matplotlib'):
        """
        Convert the red-green-blue space to hue-saturation-value space and
        return the individual bands.

        argument:
            method: string
                method to be used to convert RGB to HSV.
                    `matplotlib` uses the matplotlib routines
                    `local` uses the local routine
                default is `matplotlib` and the fastest option
        """
        if method == 'matplotlib':
            # TODO rgb values must be normalized
            inan = np.where(np.isnan(self.rgb[:, :, 0]))
            hsv = mcl.rgb_to_hsv(self.rgb)
            hsv[:, :, 0][inan] = np.nan
            hsv[:, :, 1][inan] = np.nan
            hsv[:, :, 2][inan] = np.nan
        elif method == 'local':
            f = lambda x: self.rgb2hsv(r=x[0], g=x[1], b=x[2])
            hsv = np.apply_along_axis(func1d=f, axis=2, arr=self.rgb)
        else:
            raise NotImplementedError('In RGB : hsv method {:s} not implemented'.format(method))

        # Finally
        hue = Band(
            data=hsv[:, :, 0],
            geotransform=self.geotransform,
            projection=self.projection
        )
        saturation = Band(
            data=hsv[:, :, 1],
            geotransform=self.geotransform,
            projection=self.projection
        )
        value = Band(
            data=hsv[:, :, 2],
            geotransform=self.geotransform,
            projection=self.projection
        )

        # And
        return hue, saturation, value

    def to_value(self):
        """
        Return the value part of the hue-saturation-value composition. Value is
        simply the maximum of the red-green-blue component.
        """
        value = Band(
            data=np.nanmax(self.rgb, axis=2),
            geotransform=self.geotransform,
            projection=self.projection
        )
        return value

    def plot(self, title='RGB', saveto=None):
        """
        Plot RGB data using title and saveto a locaiton

        argument:
            title: string
                The title to be used in plotting
            saveto: string
                Save to the locaiton
        """
        plt.figure()
        plt.imshow(self.rgb)
        plt.colorbar()
        plt.title(title)
        if saveto is None:
            plt.show()
        else:
            plt.savefig(saveto)
            plt.close()

    def to_geotiff(self, fname, dtype=gdal.GDT_Float32, epsg='auto'):
        """
        Save band data to geotiff to location passed by `to` with datatype
        defined by `dtype`

        argument:
            fname: string
                The filename to be saved
            dtype: gdal data type
                Gdal datatype to be used for saving, default `gdal.GDT_Float32`
            epsg: epsg code
                epsg code to reproject the data. `auto` saves the data to
                original projection. Default `auto` (only option)

        """
        fname = Path(fname).as_posix()
        row, col, nband = self.rgb.shape

        if epsg == 'auto':
            driver = gdal.GetDriverByName('GTiff')
            gtiff = driver.Create(fname, row, col, nband, dtype)
            gtiff.GetRasterBand(1).WriteArray(self.rgb[:, :, 0])
            gtiff.GetRasterBand(2).WriteArray(self.rgb[:, :, 1])
            gtiff.GetRasterBand(3).WriteArray(self.rgb[:, :, 2])
            gtiff.SetGeoTransform(self.geotransform)
            gtiff.SetProjection(self.projection)
            gtiff.FlushCache()
            gtiff = None
        else:
            raise NotImplementedError
