# pylint: disable=C0103
"""
Python script "map_wrf_io_T_wind_sfc.py"
by Matthew Garcia, Ph.D.
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2018 by Matthew Garcia
basic structure borrowed from wrf-python documentation
"""


import sys
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from wrf import to_np, getvar, smooth2d, get_basemap, latlon_coords


def message(char_string=''):
    """Print a string to the terminal and flush the buffer."""
    print char_string
    sys.stdout.flush()
    return


simulation_name = sys.argv[1]
ncfname = sys.argv[2]
ncfile = Dataset(ncfname, 'r')
if ncfname.split('/')[-1][:6] == 'wrfout':
    grid_num = int(ncfname.split('/')[-1].split('.')[0].split('_')[2][-1:])
    date_str = ncfname.split('/')[-1].split('.')[0].split('_')[3]
    time_str = ncfname.split('/')[-1].split('.')[0].split('_')[4][:-3]
elif ncfname.split('/')[-1][:6] == 'met_em':
    grid_num = int(ncfname.split('/')[-1].split('.')[1][-1:])
    date_str = ncfname.split('/')[-1].split('.')[2].split('_')[0]
    time_str = ncfname.split('/')[-1].split('.')[2].split('_')[1][:-3]
# message('grid %d' % grid_num)
# message('date %s' % date_str)
# message('time %s' % time_str)
#
# Get variables
T2 = getvar(ncfile, 'T2')
U10 = getvar(ncfile, 'U10')
V10 = getvar(ncfile, 'V10')
#
# start figure
fig = plt.figure(figsize=(8, 4))
# create basemap object
bm = get_basemap(T2, resolution='h', area_thresh=500)
bm.drawcoastlines(linewidth=0.5)
bm.drawstates(linewidth=0.5)
bm.drawcountries(linewidth=0.5)
# get coordinate information
lats, lons = latlon_coords(T2)
x, y = bm(to_np(lons), to_np(lats))
# smooth the T2 variable
smooth_T2 = smooth2d(T2, 5)
# draw T2 with filled contours
levels = np.arange(4, 35)
T2_contours = bm.contourf(x, y, to_np(smooth_T2), levels=levels, cmap=get_cmap('jet'))
plt.colorbar(T2_contours, shrink=0.95)
# bm.contourf(x, y, to_np(smooth_T2), 12, cmap=get_cmap('jet'))
# bm.clim([10, 34])
# draw wind barbs
bm.barbs(x[::40, ::40], y[::40, ::40], to_np(U10[::40, ::40]), to_np(V10[::40, ::40]), length=4)
#
# plt.colorbar(shrink=0.95)
plt.title('%s grid %d %s %s %s UTC' %
          (simulation_name, grid_num, r'$T_{sfc}$ [$^{\circ}$C]', date_str, time_str))
filename = 'reduced/T_wind_sfc/%s_grid_%d_%s_%s_%s.png' % \
    (simulation_name, grid_num, 'T_wind_sfc', date_str, time_str)
plt.savefig(filename, dpi=300, bbox_inches='tight')
message('saved %s' % filename)
plt.close()

# end map_wrf_io_T_wind_sfc.py
