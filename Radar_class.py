# pylint: disable=C0103,R0205,R0902,R0903,R0913,R1711
"""
Python script "Radar_class.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2019, 2020 by Matthew Garcia
"""


import warnings
import numpy as np
from pyproj import Proj
from Geography import get_utm_zone, is_south


class Radar(object):
    """Initialize and define an individual radar location and coverage grid."""

    def __init__(self, sim):
        self.radar_id = sim.radar_name
        #
        # radar location information
        self.lat = sim.radar_lat
        self.lon = sim.radar_lon
        self.UTM_zone = get_utm_zone(self.lon)
        proj = Proj(proj="utm", zone=self.UTM_zone, ellps="WGS84",
                    south=is_south(self.lat))
        self.easting, self.northing = proj(self.lon, self.lat)
        #
        # coverage grid definition
        self.grid_sw_east = sim.radar_grid_sw_east
        self.grid_sw_north = sim.radar_grid_sw_north
        self.grid_ne_east = sim.radar_grid_ne_east
        self.grid_ne_north = sim.radar_grid_ne_north
        self.grid_dx = sim.radar_grid_dx
        self.grid_dy = sim.radar_grid_dy
        self.grid_nrows = int((self.grid_ne_north - self.grid_sw_north) / self.grid_dy)
        self.grid_ncols = int((self.grid_ne_east - self.grid_sw_east) / self.grid_dx)
        #
        # empty radar grid
        self.empty_grid = np.zeros((self.grid_nrows, self.grid_ncols))
        #
        # minimum altitude (AGL) for radar detection
        self.min_alt_AGL = 20.0
        return

    def doppler_vel(self, UTM_zone, easting, northing, V_x, V_y):
        """Convert Flier motion to polar components centered on radar."""
        if UTM_zone != self.UTM_zone:
            proj1 = Proj(proj="utm", zone=UTM_zone, ellps="WGS84",
                         south=is_south(self.lat))
            lon, lat = proj1(easting, northing, inverse=True)
            proj2 = Proj(proj="utm", zone=self.UTM_zone, ellps="WGS84",
                         south=is_south(self.lat))
            easting, northing = proj2(lon, lat)
        x_dist = easting - self.easting
        y_dist = northing - self.northing
        r_dist = np.sqrt(x_dist**2 + y_dist**2)
        V_r = ((x_dist * V_x) + (y_dist * V_y)) / r_dist
        V_a = np.sqrt(V_x**2 + V_y**2 - V_r**2)
        return V_r, V_a  # 2 * float

    def count_grid(self, norths, easts):
        """Count values on radar grid according to location."""
        grid = np.copy(self.empty_grid)
        for north, east in zip(norths, easts):
            r = int(round((north - self.grid_sw_north) / self.grid_dy))
            c = int(round((east - self.grid_sw_east) / self.grid_dx))
            if 0 <= r < self.grid_nrows:
                if 0 <= c < self.grid_ncols:
                    grid[r, c] += 1
        return grid

    def accumulate_grid(self, norths, easts, vals):
        """Accumulate values on radar grid according to location."""
        grid = np.copy(self.empty_grid)
        for north, east, val in zip(norths, easts, vals):
            r = int(round((north - self.grid_sw_north) / self.grid_dy))
            c = int(round((east - self.grid_sw_east) / self.grid_dx))
            if 0 <= r < self.grid_nrows:
                if 0 <= c < self.grid_ncols:
                    grid[r, c] += val
        return grid

    def average_grid(self, norths, easts, vals):
        """Get average values on radar grid according to location."""
        warnings.filterwarnings("ignore", message="invalid value encountered")
        accumulated_grid = self.accumulate_grid(norths, easts, vals)
        counted_grid = self.count_grid(norths, easts)
        grid = np.where(counted_grid > 0, accumulated_grid / counted_grid, 0)
        return grid

# end Radar_class.py
