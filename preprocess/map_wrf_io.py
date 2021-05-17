# pylint: disable=C0103
"""
Python script "map_wrf_io.py"
by Matthew Garcia, Ph.D.
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2018 by Matthew Garcia
basic structure borrowed from wrf library documentation
"""


import sys
import numpy as np
import xarray as xr
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from mpl_toolkits.basemap import Basemap
from wrf import to_np, getvar, smooth2d, get_basemap, latlon_coords


all_vars = [['LU_INDEX', 'MODIS/IGBP LC'],
            ['LAI', 'MODIS LAI'],
            ['HGT', 'Sfc Elev (m)'],
            ['GHT', 'Geopotential Hgt (m)'],
            ['T2', '$T_{sfc}$ (K)'],
            ['U10', '$U_{sfc}$ (m s$^{-1}$)'],
            ['V10', '$V_{sfc}$ (m s$^{-1}$)'],
            ['sfcwind', '$sfc wind$ (m s$^{-1}$)']]
no_smooth_vars = ['LU_INDEX', 'LAI']


def message(char_string=''):
    """Print a string to the terminal and flush the buffer."""
    print char_string
    sys.stdout.flush()
    return


simulation_name = sys.argv[1]
ncfname = sys.argv[2]
var_req = sys.argv[3]
found = 0
for var in all_vars:
    if var_req == var[0]:
        varname = var
        found = 1
        continue
if not found:
    message('requested variable %s not implemented yet' % var_req)
    sys.exit(0)
#
# Open the NetCDF file
ncfile = Dataset(ncfname, 'r')
if ncfname[:6] == 'wrfout':
    grid_num = int(ncfname.split('.')[0].split('_')[1][-1:])
    date_str = ncfname.split('.')[0].split('_')[2]
    time_str = ncfname.split('.')[0].split('_')[3][:-3]
elif ncfname[:6] == 'met_em':
    grid_num = int(ncfname.split('.')[1][-1:])
    date_str = ncfname.split('.')[2].split('_')[0]
    time_str = ncfname.split('.')[2].split('_')[1][:-3]
#
# Get (and/or calculate) requested variable
if varname[0] == 'sfcwind':
    wind = lambda x, y: np.sqrt(x**2 + y**2)
    uvar = getvar(ncfile, 'U10')
    vvar = getvar(ncfile, 'V10')
    var = xr.apply_ufunc(wind, uvar, vvar)
    var.attrs['projection'] = uvar.attrs['projection']
elif varname[0] == 'GHT':
    var = getvar(ncfile, varname[0])
    var = var[0, :, :]
else:
    var = getvar(ncfile, varname[0])
#
# start figure
fig = plt.figure(figsize=(8, 4))
#
# create basemap object
bm = get_basemap(var, resolution='h', area_thresh=500)
bm.drawcoastlines(linewidth=0.5)
bm.drawstates(linewidth=0.5)
bm.drawcountries(linewidth=0.5)
#
# draw the mapped variable
if varname[0] == 'LU_INDEX':
    bm.imshow(to_np(var), interpolation='nearest', cmap=get_cmap('jet_r'))  ## placeholder for the moment
elif varname[0] == 'LAI':
    bm.imshow(to_np(var), interpolation='nearest', cmap=get_cmap('YlGn'))
elif varname[0] in ['HGT', 'GHT']:
    bm.imshow(to_np(var), interpolation='nearest', cmap=get_cmap('terrain'))
else:
    # convert lats/lons to x/y, making sure to convert to numpy arrays via to_np
    #   or basemap will crash with an undefined RuntimeError
    lats, lons = latlon_coords(var)
    x, y = bm(to_np(lons), to_np(lats))
    # Smooth the variable
    smooth_var = smooth2d(var, 3)
    # draw filled contours
    bm.contourf(x, y, to_np(smooth_var), 16, cmap=get_cmap('jet'))
#
plt.colorbar(shrink=0.95)
plt.title('%s grid %d %s %s %s UTC' %
          (simulation_name, grid_num, varname[1], date_str, time_str))
filename = '%s_grid_%d_%s_%s_%s.png' % \
    (simulation_name, grid_num, varname[0], date_str, time_str)
plt.savefig(filename, dpi=150, bbox_inches='tight')
message('saved %s' % filename)
plt.close()

# end map_wrf_io.py
