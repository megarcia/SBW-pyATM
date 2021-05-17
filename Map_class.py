# pylint: disable=C0103,R0205,R0902,R1711
"""
Python script "Map_class.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2019, 2020 by Matthew Garcia
"""


import sys
import numpy as np
from osgeo import gdal
from message_fn import message


def lc_category(idx):
    """Landcover mappings based on
       Table 2: IGBP-Modified MODIS 20-category Land Use Categories at
       http://www2.mmm.ucar.edu/wrf/users/docs/user_guide_V3.9/users_guide_chap3.html#_Land_Use_and"""
    if idx in [17, 21]:  # water, inland lakes
        lc = 'WATER'
    elif idx in [1, 5]:  # evergreen needleleaf forest, mixed forest
        lc = 'HOST_FOREST'
    elif idx in [2, 3, 4]:  # other forest types
        lc = 'OTHER_FOREST'
    else:
        lc = 'NONFOREST'
    return lc


def lc_categories(idxs):
    """Get landcover names for list of indexes."""
    return [lc_category(idx) for idx in idxs]


class Map(object):
    """Read, subset, query a GeoTIFF map file."""

    def __init__(self, sim, fname):
        if '.tif' in fname:
            message('initial setup : reading map file %s' % fname)
            ds = gdal.Open(fname)
            if ds.RasterCount > 1:
                message('initial setup : found >1 raster in this GeoTIFF file')
            # flip to proper viewing orientation
            self.map_grid = np.flipud(ds.ReadAsArray())
            self.nrows = ds.RasterYSize
            self.ncols = ds.RasterXSize
            gt = ds.GetGeoTransform()
            self.SW_lon = gt[0]
            self.dx = gt[1]
            self.NE_lat = gt[3]
            self.dy = -gt[5]
            self.SW_lat = self.NE_lat + self.ncols * gt[4] - self.nrows * self.dy
            self.NE_lon = self.SW_lon + self.ncols * self.dx + self.nrows * gt[2]
        else:
            message('ERROR: map type %s is not yet supported' % fname)
            message('       --> exiting simulation set-up')
            sys.exit(1)
        self.map_bounds = [self.SW_lat, self.SW_lon, self.NE_lat, self.NE_lon]
        self.subset = self.check_map_boundaries(sim)
        if self.subset == -1:
            message('ERROR: the provided map %s is not' % fname)
            message('       large enough to cover the simulation area')
            message('       map SW_lat = %.16f must be <=' % self.SW_lat)
            message('       sim SW_lat = %.16f' % sim.grid_min_lat)
            message('       map SW_lon = %.16f must be <=' % self.SW_lon)
            message('       sim SW_lon = %.16f' % sim.grid_min_lon)
            message('       map NE_lat = %.16f must be >=' % self.NE_lat)
            message('       sim NE_lat = %.16f' % sim.grid_max_lat)
            message('       map NE_lat = %.16f must be >=' % self.NE_lon)
            message('       sim NE_lat = %.16f' % sim.grid_max_lon)
            message('       --> exiting simulation set-up')
            sys.exit(1)
        elif self.subset == 0:
            self.map = self.map_grid
            message('initial setup : resulting map dimensions: %s' %
                    str(np.shape(self.map)))
        elif self.subset == 1:
            message('initial setup : subsetting map to specified simulation boundaries')
            self.map = self.subset_grid(sim.grid_bounds)
            message('initial setup : resulting map dimensions: %s' %
                    str(np.shape(self.map)))
            self.SW_lat = sim.grid_bounds[0]
            self.SW_lon = sim.grid_bounds[1]
            self.NE_lat = sim.grid_bounds[2]
            self.NE_lon = sim.grid_bounds[3]
        self.nrows, self.ncols = np.shape(self.map)
        self.dy = (self.NE_lat - self.SW_lat) / float(self.nrows - 1)
        self.dx = (self.NE_lon - self.SW_lon) / float(self.ncols - 1)
        return

    def check_map_boundaries(self, sim):
        """Check boundaries of input map against simulation bounds.
           map_bounds list order: [SW_lat, SW_lon, NE_lat, NE_lon]"""
        boundaries = [0, 0, 0, 0]
        if self.SW_lat <= sim.grid_min_lat:
            boundaries[0] = 1
        elif self.SW_lat > sim.grid_min_lat:
            boundaries[0] = -1
        if self.SW_lon <= sim.grid_min_lon:
            boundaries[1] = 1
        elif self.SW_lon > sim.grid_min_lon:
            boundaries[1] = -1
        if self.NE_lat >= sim.grid_max_lat:
            boundaries[2] = 1
        elif self.NE_lat < sim.grid_max_lat:
            boundaries[2] = -1
        if self.NE_lon >= sim.grid_max_lon:
            boundaries[3] = 1
        elif self.NE_lon < sim.grid_max_lon:
            boundaries[3] = -1
        if min(boundaries) == -1:
            subset = -1
        elif max(boundaries) == 1:
            subset = 1
        elif sum(boundaries) == 0:
            subset = 0
        return subset  # int

    def subset_grid(self, grid_bounds):
        """Trim map to simulation domain."""
        min_row = np.max([0, int((grid_bounds[0] - self.SW_lat) // self.dy)])
        min_col = np.max([0, int((grid_bounds[1] - self.SW_lon) // self.dx)])
        max_row = np.min([self.nrows, int((grid_bounds[2] - self.SW_lat) // self.dy)])
        max_col = np.min([self.ncols, int((grid_bounds[3] - self.SW_lon) // self.dx)])
        grid_subset = self.map_grid[min_row:max_row, min_col:max_col]
        return grid_subset  # numpy 2D array

    def get_value(self, lon, lat):
        """Get single map data point value, e.g. topography or landcover category."""
        row = int((lat - self.SW_lat) // self.dy)
        col = int((lon - self.SW_lon) // self.dx)
        if (row < 0) or (row >= self.nrows) or (col < 0) or (col >= self.ncols):
            value = -9999
        else:
            value = self.map[row, col]
        return value  # int or float

    @staticmethod
    def get_values(map_id, lons, lats):
        """Get list of map data point values, e.g. topography or landcover categories."""
        return [map_id.get_value(lon, lat) for lon, lat in zip(lons, lats)]

# end Map_class.py
