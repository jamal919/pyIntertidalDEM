#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import signal as sps
from scipy.ndimage import measurements as scm
from scipy.interpolate import RegularGridInterpolator
from osgeo import osr, gdal
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcl
from netCDF4 import Dataset
import copy
import warnings
from pathlib import Path
import xarray as xr
import rioxarray
import gc

from pyintdem.geometry import extent2geometries

gdal.UseExceptions()

class Band(object):
    def __init__(self, data=None, geotransform=None, projection=None, **kwargs):
        """
        Band data class contains the information needed for a GeoTiff file.

        arguments:
            data: array like
                2D data array, default None
            geotransform: string
                geotransform information, default None
            projection: string
                projection information, default None

        returns:
            Band data: Band
        """
        self.data = data
        self.geotransform = geotransform
        self.projection = projection
        self.attrs = kwargs

    def read(self, fname, band=1):
        """
        Read band data from a file.

        arguments:
            fname: string, file location
            band: integer, band number

        Raise an exception if data can not be read.
        """

        gdal.UseExceptions()
        try:
            dset = gdal.Open(fname, gdal.GA_ReadOnly)
            self.geotransform = dset.GetGeoTransform()
            self.projection = dset.GetProjectionRef()
            self.data = dset.GetRasterBand(band).ReadAsArray().astype(float)
        except:
            raise Exception('Band: read error!')

    def set_missing(self, value, to=np.nan):
        """
        set the missing value in data from value 

        argument:
            value: float like
                Value to be replaced
            to: float like
                Values replaced by to
        """
        if np.isnan(value):
            self.data[np.isnan(self.data)] = to
        else:
            self.data[self.data == value] = to

    def upscale(self, factor, method='nearest'):
        """
        increase the resolution with a factor.

        argument:
            factor: float like
                Multiplication factor for upscaling the data resolution
            method: string
                Method to be used for interpolation. Currently only nearest
                neighbour is available.
        """
        self.geotransform = (
                self.geotransform[0],
                self.geotransform[1]/float(factor),
                self.geotransform[2],
                self.geotransform[3],
                self.geotransform[4],
                self.geotransform[5]//float(factor)
            )
        if method=='nearest':
            self.data = np.array(self.data.repeat(factor, axis=0).repeat(factor, axis=1))
            return(True)
        elif method=='linear':
            nrows, ncols = self.data.shape
            
            # for original data
            orig_r = np.linspace(0, nrows-1, nrows)
            orig_c = np.linspace(0, ncols, ncols)

            f = RegularGridInterpolator((orig_r, orig_c), self.data)

            # for upscaled data
            upscale_r = np.linspace(0, nrows-1, nrows*factor)
            upscale_c = np.linspace(0, ncols-1, ncols*factor)

            upscale_data = f(np.meshgrid(upscale_r, upscale_c))

            self.data = upscale_data
            return True
        else:
            raise NotImplementedError

    def normalize(self, method='minmax', std_factor=0.5, std_correction='high', perc_threshold=95):
        """
        normalize the data using a given method.

        argument:
            method: string
                Method to be used for normalizing to 0 to 1 
                    minmax - minimum maximum value
                    std - mean and std removal of extreme
                    perc - percentile selection and min/max
            std_factor: float
                std_factor to be used for `std` method
            std_correction: string
                Which side of the distribution the capping will be applied
                    both - both size
                    low - lower tail
                    high - higher tail
            perc_threshold: float
                perc_threshold to be used for `perc` method
        """
        if method=='minmax':
            self.data = (self.data - np.nanmin(self.data))/(np.nanmax(self.data)-np.nanmin(self.data))
            return(True)

        elif method=='std':
            mu = np.nanmean(self.data)
            std = np.nanstd(self.data)

            if std_correction=='both':
                self.data[np.logical_and(self.data<(mu-std_factor*std), np.logical_not(np.isnan(self.data)))] = mu-std_factor*std
                self.data[np.logical_and(self.data>(mu+std_factor*std), np.logical_not(np.isnan(self.data)))] = mu+std_factor*std
            elif std_correction=='low':
                self.data[np.logical_and(self.data<(mu-std_factor*std), np.logical_not(np.isnan(self.data)))] = mu-std_factor*std
            elif std_correction=='high':
                self.data[np.logical_and(self.data>(mu+std_factor*std), np.logical_not(np.isnan(self.data)))] = mu+std_factor*std
            else:
                raise NotImplementedError

            self.data = (self.data - np.nanmin(self.data))/(np.nanmax(self.data)-np.nanmin(self.data))

        elif method=='perc':
            pth = np.nanpercentile(self.data, perc_threshold)
            self.data[np.logical_and(self.data>pth, np.logical_not(np.isnan(self.data)))] = pth
            self.data = (self.data - np.nanmin(self.data))/(np.nanmax(self.data)-np.nanmin(self.data))
        else:
            raise NotImplementedError

    def clip(self, bbox=None, geoms=None):
        """
        Args:
            bbox: bounding box as [e, w, s, n] in lon-lat cooordinates; epsg:4326
            geoms: a list of geometries, e.g., from geopandas.geometry; epsg:4326

        Returns: clipped Band
        """
        clip_geom = np.array([])

        if bbox is not None:
            bbox = extent2geometries(bbox)
            clip_geom = np.append(clip_geom, bbox)

        if geoms is not None:
            geoms = np.atleast_1d(geoms)
            clip_geom = np.append(clip_geom, geoms)

        if len(clip_geom) == 0:
            print("Neither bbox nor geom is given, returning the original Band")
            return copy.deepcopy(self)

        gdf_clip = gpd.GeoDataFrame(geometry=clip_geom, crs=4326)
        clip_geom_projected = gdf_clip.to_crs(self.projection)

        da = band_to_rio(self)
        da_clipped = da.rio.clip(clip_geom_projected.geometry, all_touched=True, drop=True)
        band_clipped = rio_to_band(da_clipped)

        return band_clipped

    def reproject_match(self, to_band):
        """
        Reproject a band object to match the resolution, projection, and region of another band object.
        Args:
            to_band: band of the target resolution and projection

        Returns: new band object reprojected to match the to_band
        """
        da_self = band_to_rio(self)
        da_to_band = band_to_rio(to_band)

        da_self_matched = da_self.rio.reproject_match(da_to_band)
        band_self_matched = rio_to_band(da_self_matched)
        return band_self_matched

    def mask(self, by, inverse=False):
        """
        Apply a mask 'by' on the band data - keeping the values presented by 1
        in mask 'by'. Set inverse to True for inverse masking.

        argument:
            by: Band
                Mask band
            inverse: boolean
                Inverse masking
        """
        _data = copy.deepcopy(self.data)
        if isinstance(by, Band):
            if inverse:
                # set what is in the mask to np.nan
                _data[by.data.astype(bool)] = np.nan
            else:
                # set what is not in the mask to np.nan
                by = by.logical_not()
                _data[by.data.astype(bool)] = np.nan

            return(
                Band(
                    data=_data,
                    geotransform=self.geotransform,
                    projection=self.projection
                )
            )
        else:
            raise NotImplementedError('In mask: mask must be a Band type')

    @property
    def min(self):
        """
        Minimum value of the band data
        """
        return np.nanmin(self.data)

    @property
    def max(self):
        """
        Maximum value of the band data
        """
        return np.nanmax(self.data)

    @property
    def mean(self):
        """
        Mean value of the band data
        """
        return np.nanmean(self.data)

    @property
    def std(self):
        """
        Standard deviation of the band data
        """
        return np.nanstd(self.data)

    @property
    def median(self):
        """
        Median of the band data
        """
        return np.nanmedian(self.data)

    def convolute(
        self, 
        kernel=[[0, -1, 0], [-1, 4, -1], [0, -1, 0]], 
        replacenan=False, 
        replacevalue=np.nan, 
        fillvalue=0, 
        nanmask=True,
        cleanedge=True):
        """
        Convolute the data with the given kernel.
        
        arguments:
            kernel: array-like
                kernel to be used for convolution
            replacenan: boolean
                if True, the nan values in the data will be replaced with 
                `replacevalue`. Default is False
            replacevalue: np.float like
                if replacenan, then nan values in the data will be replaced with
                this value. Default is np.nan
            fillvalue: np.float like
                fills the boundary of the data with `fillvalue` before doing the
                convolution. Default is 0. 
            nanmask: boolean
                masks the values lower than unity to np.nan and set the values 
                higher than 1 to unity.
            cleanedge: boolean
                set valus of two edge row and column to np.nan

        returns:
            Convoluted band: Band
        """
        kernel = np.array(kernel)

        if replacenan:
            self.set_missing(value=np.nan, to=replacevalue)

        conv = sps.convolve2d(self.data, kernel, mode='same', boundary='fill', fillvalue=0)
        
        if nanmask:
            conv[conv<1] = np.nan
            conv[conv>=1] = 1

        if cleanedge:
            conv[:, 0:2] = np.nan
            conv[:, -1] = np.nan
            conv[:, -2] = np.nan
            conv[0:2, :] = np.nan
            conv[-1, :] = np.nan
            conv[-2, :] = np.nan

        return(
            Band(
                data=conv,
                geotransform=self.geotransform,
                projection=self.projection
            )
        )

    def position(self, xyloc, epsg=4326, center=True, saveto=None):
        """
        Return the position of the given pixel location by array of x,y in xyloc
        lon lat position.

        The reason xyloc is selected is to be able to use the np.where functionality
        to output the location directly without any further modification.

        In the image sense, xyloc is actually switched position in the geographic
        sense, i.e., xyloc is in row, column model, where as geographic coordinate
        is in column row model.
        """
        # Switching from matrix to geograpic location
        yi = np.array(xyloc[0]) # row location
        xi = np.array(xyloc[1]) # column location

        try:
            crs_in = osr.SpatialReference()
            crs_in.ImportFromWkt(self.projection)
        except:
            raise RuntimeError('In Band.position(): problem with projection')

        try:
            crs_out = osr.SpatialReference()
            crs_out.ImportFromEPSG(epsg)
        except:
            raise RuntimeError('In Band.position(): problem with epsg')
        else:
            transformer = osr.CoordinateTransformation(crs_in, crs_out)

        # Position of pixel in source coordinate
        x = self.geotransform[0] + xi*self.geotransform[1] + yi*self.geotransform[2]
        if center:
            x = x + self.geotransform[1]/float(2) # Shifting half pixel for center
        
        y = self.geotransform[3] + yi*self.geotransform[5] + xi*self.geotransform[4]
        if center:
            y = y + self.geotransform[5]/float(2)

        # Transformed position of pixels
        try:
            assert zip(x, y)
        except:
            xyout = transformer.TransformPoint(x, y)[0:2]
        else:
            xyout = np.array([transformer.TransformPoint(xx, yy)[0:2] for xx,yy in zip(x, y)])
        finally:
            if saveto is None:
                return(xyout)
            else:
                np.savetxt(
                    fname=saveto, 
                    X=xyout, 
                    fmt='%f', 
                    delimiter=',',
                    comments='',
                    header='lat,lon'
                )

    def clean(self, npixel, fillvalue, background=False):
        """
        Clean the image below given pixel blob size (number of pixels) grouped
        together. If background, the data will be reversed in first step.
        Finally, it returns a clean band.

        argument:
            npixel: int like
                number of pixel to be use as the blob size
            fillvalue: float like
                value to be used on the selected blobs
            background: boolean
                if background=True, the data will be reversed at the first step
                before applying the npixel blobs and then filled with fillvalue
        """
        inan = np.isnan(self.data)
        if background:
            data = np.zeros(shape=self.data.shape)
            labels, _ = scm.label(self.data)
        else:
            data = np.ones(shape=self.data.shape)
            labels, _ = scm.label(np.nanmax(self.data)-self.data)
        
        _, count = np.unique(labels, return_counts=True)
        retained_labels = np.argwhere(count>=npixel).ravel()
        retained_labels = retained_labels[retained_labels>0]

        for label in retained_labels:
            data[labels==label] = fillvalue

        data[inan] = np.nan

        return(
            Band(
                data=data,
                geotransform=self.geotransform,
                projection=self.projection
            )
        )

    def isnan(self):
        """
        Tests if there are nan data using numpy.isnan() function.

        Returns:
            Band data with test for NaN values.
        """
        return Band(
            data=np.isnan(self.data),
            geotransform=self.geotransform,
            projection=self.projection
        )

    def astype(self, dtype):
        """
        Casts dtype to the original band data

        Args:
            dtype: dtype to cast, could be python dtype or numpy dtypes

        Returns:
            Band data with casting applied.

        """

        return Band(
            data=self.data.astype(dtype),
            geotransform=self.geotransform,
            projection=self.projection
        )

    def __repr__(self):
        """
        Print representation
        """
        return '{:d} - {:d}'.format(self.data.shape[0], self.data.shape[1])

    def __add__(self, other):
        """
        Return a modified band with another band data or value added to the
        current band data.
        """
        if isinstance(other, (int, float)):
            return(
                Band(
                    data=self.data+float(other),
                    geotransform=self.geotransform,
                    projection=self.projection
                )
            )
        elif isinstance(other, Band):
            try:
                assert np.all(self.data.shape==other.data.shape)
            except:
                raise AssertionError('In Band add: size mismatch')
            else:
                return(
                    Band(
                        data=self.data+other.data,
                        geotransform=self.geotransform,
                        projection=self.projection
                    )
                )
        else:
            raise NotImplementedError('In Band add: other datatype not implemented')

    def __radd__(self, other):
        """
        Return a modified band with another band data or value added to the
        current band data.
        """
        if isinstance(other, (int, float)):
            return Band.__add__(self, other)
        else:
            raise NotImplementedError('In Band radd: only int and float is implemented')

    def __sub__(self, other):
        """
        Return a modified band with another band data or value subtracted from
        the current band data.
        """
        if isinstance(other, (int, float)):
            return(
                Band(
                    data=self.data-float(other),
                    geotransform=self.geotransform,
                    projection=self.projection
                )
            )
        elif isinstance(other, Band):
            try:
                assert np.all(self.data.shape==other.data.shape)
            except:
                raise AssertionError('In Band sub: size mismatch')
            else:
                return(
                    Band(
                        data=self.data-other.data,
                        geotransform=self.geotransform,
                        projection=self.projection
                    )
                )
        else:
            raise NotImplementedError('In Band sub: other datatype not implemented')

    def __rsub__(self, other):
        """
        Return a modified band with another band data or value subtracted from
        the current band data.
        """
        if isinstance(other, (int, float)):
            return Band.__sub__(self, other)
        else:
            raise NotImplementedError('In Band rsub: only int and float is implemented')
    
    def __mul__(self, other):
        """
        Return a modified band with another band data or value multiplied to the
        current band data.
        """
        if isinstance(other, (int, float)):
            return(
                Band(
                    data=self.data*float(other),
                    geotransform=self.geotransform,
                    projection=self.projection
                )
            )
        elif isinstance(other, Band):
            try:
                assert np.all(self.data.shape==other.data.shape)
            except:
                raise AssertionError('In Band mul: size mismatch')
            else:
                return(
                    Band(
                        data=self.data*other.data,
                        geotransform=self.geotransform,
                        projection=self.projection
                    )
                )
        else:
            raise NotImplementedError('In Band mul: other datatype not implemented')

    def __truediv__(self, other):
        """
        Return a modified band with another band data or value dividing the
        current band data.
        """
        if isinstance(other, (int, float)):
            return(
                Band(
                    data=self.data/float(other),
                    geotransform=self.geotransform,
                    projection=self.projection
                )
            )
        elif isinstance(other, Band):
            try:
                assert np.all(self.data.shape==other.data.shape)
            except:
                raise AssertionError('In Band div: size mismatch')
            else:
                return(
                    Band(
                        data=self.data/other.data,
                        geotransform=self.geotransform,
                        projection=self.projection
                    )
                )
        else:
            raise NotImplementedError('In Band div: other datatype not implemented')

    def __gt__(self, other):
        """
        Return a modified logical band which is true if the values are greater
        than the other and false if otherwise.
        """
        if isinstance(other, (int, float)):
            _data = self.data>float(other)
            _data = _data.astype(float)
            _data[np.isnan(self.data)] = np.nan
            return(
                Band(
                    data=_data,
                    geotransform=self.geotransform,
                    projection=self.projection
                )
            )
        elif isinstance(other, Band):
            try:
                assert np.all(self.data.shape==other.data.shape)
            except:
                raise AssertionError('In Band gt: size mismatch')
            else:
                _data = self.data>other.data
                _data = _data.astype(float)
                _data[np.isnan(self.data)] = np.nan
                return(
                    Band(
                        data=_data,
                        geotransform=self.geotransform,
                        projection=self.projection
                    )
                )
        else:
            raise NotImplementedError('In Band gt: other datatype not implemented')

    def __ge__(self, other):
        """
        Return a binary band which is true if the values are greater
        than the other and false if otherwise.
        """
        if isinstance(other, (int, float)):
            _data = self.data>=float(other)
            _data = _data.astype(float)
            _data[np.isnan(self.data)] = np.nan
            return(
                Band(
                    data=_data,
                    geotransform=self.geotransform,
                    projection=self.projection
                )
            )
        elif isinstance(other, Band):
            try:
                assert np.all(self.data.shape==other.data.shape)
            except:
                raise AssertionError('In Band ge: size mismatch')
            else:
                _data = self.data>=other.data
                _data = _data.astype(float)
                _data[np.isnan(self.data)] = np.nan
                return(
                    Band(
                        data=_data,
                        geotransform=self.geotransform,
                        projection=self.projection
                    )
                )
        else:
            raise NotImplementedError('In Band ge: other datatype not implemented')

    def __lt__(self, other):
        """
        Return a binary band which is true if the values are greater
        than the other and false if otherwise.
        """
        if isinstance(other, (int, float)):
            _data = self.data<float(other)
            _data = _data.astype(float)
            _data[np.isnan(self.data)] = np.nan
            return(
                Band(
                    data=_data,
                    geotransform=self.geotransform,
                    projection=self.projection
                )
            )
        elif isinstance(other, Band):
            try:
                assert np.all(self.data.shape==other.data.shape)
            except:
                raise AssertionError('In Band lt: size mismatch')
            else:
                _data = self.data<other.data
                _data = _data.astype(float)
                _data[np.isnan(self.data)] = np.nan
                return(
                    Band(
                        data=_data,
                        geotransform=self.geotransform,
                        projection=self.projection
                    )
                )
        else:
            raise NotImplementedError('In Band lt: other datatype not implemented')

    def __le__(self, other):
        """
        Return a modified logical band which is true if the values are greater
        than the other and false if otherwise.
        """
        if isinstance(other, (int, float)):
            data = self.data<=float(other)
            data[np.isnan(self.data)] = np.nan
            return(
                Band(
                    data=data,
                    geotransform=self.geotransform,
                    projection=self.projection
                )
            )
        elif isinstance(other, Band):
            try:
                assert np.all(self.data.shape==other.data.shape)
            except:
                raise AssertionError('In Band le: size mismatch')
            else:
                data = self.data<=other.data
                data[np.isnan(self.data)] = np.nan
                return(
                    Band(
                        data=data,
                        geotransform=self.geotransform,
                        projection=self.projection
                    )
                )
        else:
            raise NotImplementedError('In Band le: other datatype not implemented')

    def logical_and(self, other):
        """
        Logical and connection of two Band data
        """
        if isinstance(other, Band):
            _data = np.logical_and(self.data, other.data)
            _data = _data.astype(float)
            _data[np.isnan(self.data)] = np.nan
            return(
                Band(
                    data=_data,
                    geotransform=self.geotransform,
                    projection=self.projection
                )
            )
        else:
            raise NotImplementedError('In Band logical_and: only Band data in implemented')

    def logical_or(self, other):
        """
        Logical or of two Band data
        """
        if isinstance(other, Band):
            _data = np.logical_or(self.data, other.data)
            _data = _data.astype(float)
            _data[np.isnan(self.data)] = np.nan
            return(
                Band(
                    data=_data,
                    geotransform=self.geotransform,
                    projection=self.projection
                )
            )
        else:
            raise NotImplementedError('In Band logical_or: only Band data is implemented')
    
    def logical_not(self):
        """
        Logical not of a Band
        """
        _data = np.logical_not(self.data)
        _data = _data.astype(float)
        _data[np.isnan(self.data)] = np.nan
        return(
            Band(
                data=_data,
                geotransform=self.geotransform,
                projection=self.projection
            )
        )

    def nan_avg(self, other):
        """
        Do a nan average with other.
        """
        if isinstance(other, Band):
            _data = np.empty((self.data.shape[0], self.data.shape[1], 2), dtype=float)
            _data[:, :, 0] = self.data
            _data[:, :, 1] = other.data
            
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                _data = np.nanmean(_data, axis=-1, keepdims=False)

            return(
                Band(
                    data=_data,
                    geotransform=self.geotransform,
                    projection=self.projection
                )
            )
        else:
            raise NotImplementedError('In Band nan_avg: only Band data is implemented')
    
    def nan_sum(self, other):
        """
        Do a nan sum with other.
        """
        if isinstance(other, Band):
            _data = np.empty((self.data.shape[0], self.data.shape[1], 2), dtype=float)
            _data[:, :, 0] = self.data
            _data[:, :, 1] = other.data
            
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                _data = np.nansum(_data, axis=-1, keepdims=False)

            return(
                Band(
                    data=_data,
                    geotransform=self.geotransform,
                    projection=self.projection
                )
            )
        else:
            raise NotImplementedError('In Band nan_avg: only Band data is implemented')

    def to_geotiff(self, fname, epsg=None, dtype='float32'):
        """
        Save band data to geotiff to location passed by `fname` with `epsg`.

        argument:
            fname: string
                The filename to be saved
            epsg: epsg code
                epsg code to reproject the data. `None` saves the data to
                original projection. Default `None`

        """
        fname = Path(fname).as_posix()
        da_self = band_to_rio(self)

        if epsg is not None:
            da_self = da_self.reproject(epsg=epsg)

        da_self.rio.to_raster(fname, dtype=dtype)

    def to_netcdf(self, fname, epsg=None):
        """
        Save band data to netCDF4 file to location passed by `fname`.

        argument:
            fname: string
                filename to be used
            epsg: epsg code
                epsg code to reproject the data, default None
        """
        fname = Path(fname).as_posix()
        da_self = band_to_rio(self)
        if epsg is not None:
            da_self = da_self.reproject(epsg=epsg)

        da_self.to_netcdf(fname)

    def plot(self, title='Band', cmap='binary', saveto=None):
        """
        Plotting function with given title, cmap

        argument:
            title: string
                Plot title
            cmap: string, cmap
                colormap name
            saveto: string
                saving location
        """
        fig, ax = plt.subplots()
        im = ax.imshow(self.data, cmap=cmap)
        plt.colorbar(im)
        plt.title(title)
        if saveto is None:
            plt.show()
        else:
            plt.savefig(saveto, dpi=300)
            plt.close()

        del fig, ax
        gc.collect()


def band_to_rio(band: Band) -> xr.DataArray:
    """
    Convert a band to a rioxarray DataArray
    Args:
        band: A core.Band dataset

    Returns: xr.DataArray

    """
    x_start, dx, _, y_start, _, dy = band.geotransform
    ny, nx = band.data.shape
    x = np.arange(x_start + dx / 2, x_start + (nx + 0.5) * dx, dx)
    y = np.arange(y_start + dy / 2, y_start + (ny + 0.5) * dy, dy)
    ds = xr.DataArray(band.data, dims=('y', 'x'), coords={'x': x, 'y': y})
    ds.rio.write_crs(band.projection, inplace=True)

    return ds

def rio_to_band(da: xr.DataArray) -> Band:
    """
    Convert a rioxarray DataArray to band data
    Args:
        da: xr.DataArray with rioxarray projection

    Returns: xr.DataArray

    """
    band = Band(
        data=da.values,
        geotransform=da.rio.transform().to_gdal(),
        projection=da.rio.crs.to_wkt()
    )

    return band

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
                h = (60*((g-b)/df) + 360) % 360
            elif mx == g:
                h = (60*((b-r)/df) + 120) % 360
            elif mx == b:
                h = (60*((r-g)/df) + 240) % 360

            h = h/360.0

            if mx == 0:
                s = 0
            else:
                s = df/mx

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
        if method=='matplotlib':
            # TODO rgb values must be normalized
            inan = np.where(np.isnan(self.rgb[:, :, 0]))
            hsv = mcl.rgb_to_hsv(self.rgb)
            hsv[:, :, 0][inan] = np.nan
            hsv[:, :, 1][inan] = np.nan
            hsv[:, :, 2][inan] = np.nan
        elif method=='local':
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
        
        if epsg=='auto':
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
