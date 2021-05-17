# pylint: disable=C0103
"""
Python script "map_wrf_io_T_wind_upa.py"
by Matthew Garcia, Ph.D.
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2018 by Matthew Garcia
basic structure borrowed from wrf-python documentation
"""


import sys
import glob
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from mpl_toolkits.basemap import Basemap
from wrf import to_np, getvar, interplevel, smooth2d, latlon_coords  #, get_basemap
from Simulation_specifications import Simulation


def message(char_string=''):
    """Print a string to the terminal and flush the buffer."""
    print char_string
    sys.stdout.flush()
    return

simulation_name = sys.argv[1]
path = sys.argv[2]
sim = Simulation()
flist = sorted(glob.glob('%s/*.nc' % path))
#
for ncfname in flist:
    if ncfname.split('/')[-1][:6] == 'wrfout':
        grid_num = int(ncfname.split('/')[-1].split('.')[0].split('_')[2][-1:])
        date_str = ncfname.split('/')[-1].split('.')[0].split('_')[3]
        time_str = ncfname.split('/')[-1].split('.')[0].split('_')[4][:-3]
    elif ncfname.split('/')[-1][:6] == 'met_em':
        grid_num = int(ncfname.split('/')[-1].split('.')[1][-1:])
        date_str = ncfname.split('/')[-1].split('.')[2].split('_')[0]
        time_str = ncfname.split('/')[-1].split('.')[2].split('_')[1][:-3]
    ncfile = Dataset(ncfname, 'r')
    #
    # Get variables
    P = getvar(ncfile, 'pressure')
    T = getvar(ncfile, 'temperature')
    U = getvar(ncfile, 'u_unstaggered')
    V = getvar(ncfile, 'v_unstaggered')
    #
    # get coordinate information
    lats, lons = latlon_coords(T)
    #
    for prs in [950, 900, 850]:
        #
        # start map
        plt.figure(figsize=(8, 8))
        mid_lat = (sim.grid_bounds[0] + sim.grid_bounds[2]) / 2.0
        mid_lon = (sim.grid_bounds[1] + sim.grid_bounds[3]) / 2.0
        if grid_num == 3:
            b = Basemap(projection='tmerc', lon_0=mid_lon, lat_0=mid_lat, lat_ts=mid_lat,
                        llcrnrlat=sim.grid_bounds[0], llcrnrlon=sim.grid_bounds[1]+2.0,
                        urcrnrlat=sim.grid_bounds[2], urcrnrlon=sim.grid_bounds[3],
                        resolution='h', area_thresh=500)
        elif grid_num == 4:
            b = Basemap(projection='tmerc', lon_0=mid_lon, lat_0=mid_lat, lat_ts=mid_lat,
                        llcrnrlat=sim.grid_bounds[0], llcrnrlon=sim.grid_bounds[1]+1.0,
                        urcrnrlat=sim.grid_bounds[2], urcrnrlon=sim.grid_bounds[3],
                        resolution='h', area_thresh=500)
        b.drawcoastlines()
        b.drawstates()
        b.drawcountries()
        #
        # interpolate to desired pressure level
        T_prs = interplevel(T, P, prs)
        U_prs = interplevel(U, P, prs)
        V_prs = interplevel(V, P, prs)
        #
        # draw T with filled contours
        x, y = b(to_np(lons), to_np(lats))
        smooth_T_prs = smooth2d(T_prs, 3)
        clevs = np.arange(4, 35)
        T_prs_contours = b.contourf(x, y, to_np(smooth_T_prs), levels=clevs, cmap=get_cmap('jet'))
        cbar = plt.colorbar(T_prs_contours, pad=0.02, shrink=0.5)
        cbar.ax.set_ylabel(r'$T_{%d}$ [$^{\circ}$C]' % prs)
        #
        parallels = np.arange(30., 60., 2.)
        b.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
        meridians = np.arange(270., 360., 2.)
        b.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)
        #
        # draw wind barbs
        if grid_num == 3:
            interval = 30
            barb_len = 5
        elif grid_num == 4:
            interval = 40
            barb_len = 4
        b.barbs(x[::interval, ::interval], y[::interval, ::interval],
                to_np(U_prs[::interval, ::interval]), to_np(V_prs[::interval, ::interval]),
                length=barb_len)
        #
        plt.title('%s grid %d %s %s %s UTC' %
                  (simulation_name, grid_num, r'$T_{%d}$ [$^{\circ}$C]' % prs, date_str, time_str))
        filename = '%s/T_wind_upa/%s_grid_%d_%s_%s_%s.png' % \
            (path, simulation_name, grid_num, 'T_wind_%dhPa' % prs, date_str, time_str)
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        message('saved %s' % filename)
        plt.close()

# end map_wrf_io_T_wind_upa.py
