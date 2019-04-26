#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import numpy as np
from scipy import signal as sps
from scipy.ndimage import measurements as scm
from osgeo import osr, gdal
import matplotlib.pyplot as plt
import matplotlib.colors as mcl
from mpl_toolkits.basemap import Basemap
import netCDF4
import copy
import os

gdal.UseExceptions()

class Band(object):
    def __init__(self, data=None, geotransform=None, projection=None, **kwargs):
        '''
        Band data class contains the information needed for a GeoTiff file. 
        '''
        self.data = data
        self.geotransform = geotransform
        self.projection = projection

    def read(self, fname, band=1):
        gdal.UseExceptions()
        try:
            dset = gdal.Open(fname, gdal.GA_ReadOnly)
            self.geotransform = dset.GetGeoTransform()
            self.projection = dset.GetProjectionRef()
            self.data = dset.GetRasterBand(band).ReadAsArray().astype(np.float)
        except:
            raise Exception('Band: read error!')

    def set_missing(self, value, to=np.nan):
        '''
        set the missing value in data from value 
        '''
        if np.isnan(value):
            self.data[np.isnan(self.data)] = to
        else:
            self.data[self.data == value] = to

    def upscale(self, factor, method='nearest'):
        if method=='nearest':
            self.geotransform = (
                self.geotransform[0],
                self.geotransform[1]/float(factor),
                self.geotransform[2],
                self.geotransform[3],
                self.geotransform[4],
                self.geotransform[5]//float(factor)
            )
            self.data = np.array(self.data.repeat(factor, axis=0).repeat(factor, axis=1))
            return(True)
        else:
            raise NotImplementedError

    def normalize(self, method='minmax', std_factor=0.5, perc_threshold=95):
        if method=='minmax':
            self.data = (self.data - np.nanmin(self.data))/(np.nanmax(self.data)-np.nanmin(self.data))
            return(True)

        elif method=='std':
            mu = np.nanmean(self.data)
            std = np.nanstd(self.data)
            self.data[np.logical_and(self.data<(mu-std_factor*std), np.logical_not(np.isnan(self.data)))] = mu-std_factor*std
            self.data[np.logical_and(self.data<(mu+std_factor*std), np.logical_not(np.isnan(self.data)))] = mu+std_factor*std
            self.data = (self.data - np.nanmin(self.data))/(np.nanmax(self.data)-np.nanmin(self.data))

        elif method=='perc':
            pth = np.nanpercentile(self.data, perc_threshold)
            self.data[np.logical_and(self.data>pth, np.logical_not(np.isnan(self.data)))] = pth
            self.data = (self.data - np.nanmin(self.data))/(np.nanmax(self.data)-np.nanmin(self.data))
        else:
            raise NotImplementedError

    def mask(self, by, inverse=False):
        '''
        Apply a mask 'by' on the band data - keeping the values presented by 1
        in mask 'by'. Set inverse to True for inversing masking.

        # TODO: size check
        '''
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
    def std(self):
        '''
        Standard deviation of the band data
        '''
        return(np.nanstd(self.data))

    @property
    def median(self):
        '''
        Median of the band data
        '''
        return(np.nanmedian(self.data))

    def convolute(
        self, 
        kernel=[[0, -1, 0], [-1, 4, -1], [0, -1, 0]], 
        replacenan=False, 
        replacevalue=np.nan, 
        fillvalue=0, 
        nanmask=True,
        cleanedge=True):
        '''
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
        '''
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
        '''
        Return the position of the given pixel location by array of x,y in xyloc
        lon lat position.

        The reason xyloc is selected is to able to use the np.where functionality
        to output the location directly without any further modification.

        In the image sense, xyloc is actually switched position in the geographic
        sense, i.e., xyloc is in row, column model, where as geographic coordinate
        is in column row model.
        '''
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
                    header='lon,lat'
                )

    def clean(self, npixel, fillvalue, background=False):
        '''
        Clean the image below given pixel blob size (number of pixels) grouped
        together. If reversed, the data will be reversed in first step.
        Finally it returns a clean band.
        '''
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
        print(retained_labels)

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


    def __repr__(self):
        '''
        Print representation
        '''
        return('{:d} - {:d}'.format(self.data.shape[0], self.data.shape[1]))

    def __add__(self, other):
        '''
        Return a modified band with another band data or value added to the
        current band data.
        '''
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
        '''
        Return a modified band with another band data or value added to the
        current band data.
        '''
        if isinstance(other, (int, float)):
            return(Band.__add__(self, other))
        else:
            raise NotImplementedError('In Band radd: only int and float is implemented')


    def __sub__(self, other):
        '''
        Return a modified band with another band data or value subtracted from
        the current band data.
        '''
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
        '''
        Return a modified band with another band data or value subtracted from
        the current band data.
        '''
        if isinstance(other, (int, float)):
            return(Band.__sub__(self, other))
        else:
            raise NotImplementedError('In Band rsub: only int and float is implemented')
    
    def __mul__(self, other):
        '''
        Return a modified band with another band data or value multiplied to the
        current band data.
        '''
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
        '''
        Return a modified band with another band data or value dividing the
        current band data.
        '''
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
        '''
        Return a modified logical band which is true if the values are greater
        than the other and false if otherwise.
        '''
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
        '''
        Return a binary band which is true if the values are greater
        than the other and false if otherwise.
        '''
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
        '''
        Return a binary band which is true if the values are greater
        than the other and false if otherwise.
        '''
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
        '''
        Return a modified logical band which is true if the values are greater
        than the other and false if otherwise.
        '''
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

    def to_geotiff(self, fname, dtype=gdal.GDT_Float32, epsg='auto'):
        '''
        Save band data to geotiff to location passed by `to` with datatype
        defined by `dtype`
        '''
        row, col = self.data.shape
        
        if epsg=='auto':
            driver = gdal.GetDriverByName('GTiff')
            gtiff = driver.Create(fname, row, col, 1, dtype)
            gtiff.GetRasterBand(1).WriteArray(self.data)
            gtiff.SetGeoTransform(self.geotransform)
            gtiff.SetProjection(self.projection)
            gtiff.FlushCache()
            gtiff = None
        else:
            try:
                in_proj = osr.SpatialReference()
                in_proj.ImportFromWkt(self.projection)
                out_proj = osr.SpatialReference()
                out_proj.ImportFromEPSG(epsg)
            except:
                raise Exception('Problem with EPSG code!')
            else:
                mdriver = gdal.GetDriverByName('MEM')
                fdriver = gdal.GetDriverByName('GTiff')
                src = mdriver.Create('Memory', row, col, 1, dtype)
                src.SetGeoTransform(self.geotransform)
                src.SetProjection(self.projection)
                src.GetRasterBand(1).WriteArray(self.data)
                trans_coord = osr.CoordinateTransformation(
                    in_proj, 
                    out_proj
                )
                print(self.geotransform)
                (ulx, uly, ulz) = trans_coord.TransformPoint(
                    self.geotransform[0], 
                    self.geotransform[3]
                )
                (lrx, lry, lrz) = trans_coord.TransformPoint(
                    self.geotransform[0]+self.geotransform[1]*row,
                    self.geotransform[3]+self.geotransform[5]*col
                )
                pixelx, pixely, _ = np.array(trans_coord.TransformPoint(
                    self.geotransform[0]+self.geotransform[1],
                    self.geotransform[3]+self.geotransform[5]
                ))- np.array(trans_coord.TransformPoint(
                    self.geotransform[0],
                    self.geotransform[3]
                ))
                xsize = int(np.abs((ulx-lrx)//pixelx))
                ysize = int(np.abs((uly-lry)//pixely))
                geotransform = (ulx, pixelx, self.geotransform[2], uly, self.geotransform[4], pixely)

                gtiff = fdriver.Create(fname, xsize, ysize, 1, dtype)
                gtiff.SetGeoTransform(geotransform)
                gtiff.SetProjection(out_proj.ExportToWkt())
                gdal.ReprojectImage(
                    src, 
                    gtiff, 
                    self.projection, 
                    out_proj.ExportToWkt(), 
                    gdal.GRA_Bilinear
                )
                gtiff.FlushCache()
                gtiff = None
                src = None
                del gtiff, src

    def to_netcdf(self, fname, epsg=4326):
        '''
        Save band data to netCDF4 file to location passed by `to`.
        '''
        row, col = self.data.shape

        # Setting up coordinate transformation
        try:
            in_proj = osr.SpatialReference()
            in_proj.ImportFromWkt(self.projection)
            out_proj = osr.SpatialReference()
            out_proj.ImportFromEPSG(epsg)
        except:
            raise Exception('Problem with EPSG code!')
        else:
            trans_coord = osr.CoordinateTransformation(in_proj, out_proj)
            x = np.array([self.geotransform[0]+i*self.geotransform[1] for i in np.arange(row)])
            y = np.array([self.geotransform[3]+i*self.geotransform[5] for i in np.arange(col)])

            meshx, meshy = np.meshgrid(x, y)
            meshxy = zip(meshx.flatten(), meshy.flatten())
            lonlat = np.array([trans_coord.TransformPoint(xy[0], xy[1])[0:2] for xy in meshxy])
            lon = np.reshape(lonlat[:, 0], meshx.shape)
            lat = np.reshape(lonlat[:, 1], meshx.shape)
            del lonlat, meshxy, meshx, meshy
            
        try:
            nc = netCDF4.Dataset(
                filename=fname, 
                mode='w', 
                clobber=True,
                format='NETCDF4_CLASSIC'
            )
        except:
            raise Exception('netCDF Error!')
        else:
            # Dimensitons
            dx = nc.createDimension(dimname='x', size=len(x))
            dy = nc.createDimension(dimname='y', size=len(y))

            # Variables
            vx = nc.createVariable(varname='x', datatype=float, dimensions=(dx))
            vx.long_name = 'x coordinate'
            vx.wkt = self.projection
            vx[:] = x

            vy = nc.createVariable(varname='y', datatype=float, dimensions=(dy))
            vy.long_name = 'y coordinate'
            vy.wkt = self.projection
            vy[:] = y

            lon = nc.createVariable(varname='lon', datatype=float, dimensions=(dx, dy))
            lon.long_name = 'Longitude'
            lon.units = 'degrees_east'
            lon[:] = lon

            lat = nc.createVariable(varname='lat', datatype=float, dimensions=(dx, dy))
            lat.long_name = 'Latitude'
            lat.units = 'degrees_north'
            lat[:] = lat

            value = nc.createVariable(varname='value', datatype=float, dimensions=(dx, dy))
            value.long_name = 'Pixel value'
            value[:] = self.data
        finally:
            nc.sync()
            nc.close()

    def to_csv(self, to, crs='auto', drop_nan=False):
        '''
        Save band data to csv file
        '''
        raise NotImplementedError()

    def plot(self, title='Band', cmap='binary', saveto=None):
        '''
        Plotting function with given title, cmap. If saveto loction is given
        '''
        plt.figure()
        plt.imshow(self.data, cmap=cmap)
        plt.colorbar()
        plt.title(title)
        if saveto is None:
            plt.show()
        else:
            plt.savefig(saveto, dpi=300)
            plt.close()

class RGB(object):
    def __init__(self, red, green, blue):
        '''
        RGB band using band using in the red-green-blue band.
        '''
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

        return(h, s, v)

    def to_hsv(self, method='matplotlib'):
        '''
        Convert the red-green-blue space to hue-saturation-value space and 
        return the individual bands. 
        '''
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
        return(hue, saturation, value)

    def to_value(self):
        '''
        Return the value part of the hue-saturation-value composition. Value is 
        simply the maximum of the red-green-blue component.
        '''
        value = Band(
            data=np.nanmax(self.rgb, axis=2),
            geotransform=self.geotransform,
            projection=self.projection
        )
        return(value)

    def plot(self, title='RGB', saveto=None):
        plt.figure()
        plt.imshow(self.rgb)
        plt.colorbar()
        plt.title(title)
        if saveto is None:
            plt.show()
        else:
            plt.savefig(saveto)
            plt.close()