# pylint: disable=C0103,R0913
"""
Python script "Interpolation.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2019, 2020 by Matthew Garcia
"""


import numpy as np
from scipy.interpolate import interp1d, griddata


def interpolate_time(value1, date_time1, value2, date_time2, date_time):
    """Linear interpolation of meteorological values in time."""
    t1 = date_time - date_time1  # datetime objects
    t_interval = date_time2 - date_time1  # datetime objects
    t_frac = float(t1.seconds) / float(t_interval.seconds)
    value = value1 + (value2 - value1) * t_frac
    return value  # float


def get_vals_1D(GpH_columns, var_columns, interp_method, locs_GpH):
    """Interpolate (linear) values to specified GpH within 1D columns."""
    var_vals = np.zeros((len(locs_GpH)))
    for i, GpH in enumerate(locs_GpH):
        fn = interp1d(GpH_columns[:, i], var_columns[:, i],
                      kind=interp_method, fill_value='extrapolate')
        var_vals[i] = fn(GpH)
    return var_vals


def get_nearest_vals_2D(var, locs_row, locs_col):
    """Query values at specified row/col locations in known 2D grid."""
    return [var[r, c] for r, c in zip(locs_row, locs_col)]


def get_nearest_columns(var, locs_row, locs_col):
    """Extract 1D columns at specified row/col locations in known 3D grid."""
    nlayers = np.shape(var)[0]
    var_columns = np.zeros((nlayers, len(locs_row)))
    for k in range(nlayers):
        var_layer = var[k, :, :]
        var_columns[k, :] = get_nearest_vals_2D(var_layer, locs_row, locs_col)
    return var_columns


def get_interp_vals_2D(lons, lats, var, interp_method, locs_lon, locs_lat):
    """Interpolate values at specified locations from irregular 2D grid."""
    var_vals = griddata((lons.flatten(), lats.flatten()), var.flatten(),
                        (locs_lon, locs_lat), method=interp_method)
    return var_vals

# end Interpolation.py
