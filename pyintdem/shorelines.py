#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.interpolate import NearestNDInterpolator

class Shorelines:
    def __init__(self, fdir, pattern='*/shoreline*.csv'):
        self.fdir = Path(fdir)
        self.pattern = pattern
        self.shorelines = list_shorelines(self.fdir, self.pattern)

    def timestamps(self, buffer='0H'):
        _timestamps = get_timestamps(self.shorelines)
        if buffer=='0H':
            return _timestamps
        else:
            return buffer_timestamps(_timestamps)
        
    def extent(self, buffer=0):
        _extent = get_extent(self.shorelines)
        if buffer==0:
            return _extent
        else:
            return buffer_extent(_extent, buffer=buffer)
        
    def reference(self, ds):
        add_reference(shorelines=self.shorelines, ds=ds)

    def combine(self, fname=None, elev=True):
        if elev:
            varnames = ['lon', 'lat', 'elev']
        else:
            varnames = ['lon', 'lat']
        df_combined = pd.DataFrame()
        for shoreline in self.shorelines:
            df = read_shoreline(shoreline=shoreline)
            df_combined = pd.concat(
                [df_combined, df.loc[:, varnames]], 
                axis=0, 
                ignore_index=True)
            
        if fname is not None:
            df_combined.to_csv(fname, index=False)

        return df_combined

def list_shorelines(fdir, pattern='*/shoreline*.csv'):
    shorelines = list(fdir.rglob(pattern))
    return shorelines

def get_timestamp(shoreline):
    timestamp = shoreline.parent.name # taking from the filename
    timestamp = pd.to_datetime(timestamp, format='%Y%m%d%H%M%S')
    return timestamp

def get_timestamps(shorelines):
    timestamps = pd.to_datetime([get_timestamp(shoreline) for shoreline in shorelines])
    timestamps = np.unique(timestamps) # sorts and gives the unique values
    return timestamps

def buffer_timestamps(timestamps, buffer='1H'):
    temp = [timestamps[0] - pd.Timedelta(buffer)]
    for timestamp in timestamps:
        temp.append(timestamp)
        
    temp.append(timestamps[-1] + pd.Timedelta(buffer))
    return pd.to_datetime(temp).values

def read_shoreline(shoreline):
    df = pd.read_csv(shoreline, header=0)
    return df

def get_extent(shorelines):
    for i, shoreline in enumerate(shorelines):
        df = read_shoreline(shoreline)
        if i == 0:
            extent = [df.lon.min(), df.lon.max(), df.lat.min(), df.lat.max()]
        else:
            this_extent = [df.lon.min(), df.lon.max(), df.lat.min(), df.lat.max()]
            extent = [
                np.min([extent[0], this_extent[0]]),
                np.max([extent[1], this_extent[1]]),
                np.min([extent[2], this_extent[2]]),
                np.max([extent[3], this_extent[3]]),
            ]

    return extent

def buffer_extent(extent, buffer):
    buffered_extent = [
        extent[0] - buffer,
        extent[1] + buffer,
        extent[2] - buffer,
        extent[3] + buffer
    ]

    return buffered_extent

def add_reference(shorelines, ds):
    shorelines = np.atleast_1d(shorelines)
    for shoreline in shorelines:
        timestamp = get_timestamp(shoreline)
        elev_ds = ds.interp(time=timestamp)
        shoreline_df = read_shoreline(shoreline)
        X, Y = np.meshgrid(elev_ds['lon'], elev_ds['lat'])
        elev_df = pd.DataFrame({
            'lon':X.flatten(),
            'lat':Y.flatten(),
            'elev':elev_ds['elev'].values.flatten()
        })

        elev_df = elev_df.dropna()
        f = NearestNDInterpolator(elev_df.loc[:, ['lon', 'lat']].values, elev_df.loc[:, 'elev'].values)
        elev_shoreline = f(shoreline_df.loc[:, ['lon', 'lat']])
        shoreline_df.loc[:, 'elev'] = elev_shoreline
        shoreline_df.to_csv(shoreline)