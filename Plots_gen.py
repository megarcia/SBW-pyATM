# pylint: disable=C0103,C0412,C0413,R0914,R0915,R1711
"""
Python script "Plots_gen.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2019 by Matthew Garcia
"""


import warnings
import iso8601
import numpy as np
import matplotlib as mpl
from matplotlib import gridspec
from matplotlib.cm import get_cmap
from matplotlib.collections import LineCollection
from mpl_toolkits.basemap import Basemap
mpl.use('Agg')
import matplotlib.pyplot as plt


def setup_basemap(sim):
    """Set up common basemap for various plots."""
    mid_lat = (sim.plot_bottom_lat + sim.plot_top_lat) / 2.0
    mid_lon = (sim.plot_left_lon + sim.plot_right_lon) / 2.0
    bmap = Basemap(projection='tmerc', lon_0=mid_lon, lat_0=mid_lat, lat_ts=mid_lat,
                   llcrnrlat=sim.plot_bottom_lat, llcrnrlon=sim.plot_left_lon,
                   urcrnrlat=sim.plot_top_lat, urcrnrlon=sim.plot_right_lon,
                   resolution='h', area_thresh=500)
    bmap.drawcoastlines()
    bmap.drawstates()
    bmap.drawcountries()
    #
    # draw map references
    bmap.drawmapscale(lon=sim.plot_left_lon+0.75, lat=sim.plot_top_lat-0.5,
                      lon0=mid_lon, lat0=mid_lat, length=100.0, barstyle='fancy')
    parallels = np.arange(30., 60., 1.)
    bmap.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
    meridians = np.arange(270., 360., 1.)
    bmap.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)
    return bmap


def plot_single_flight(sim, status_df, outfname):
    """2-panel figure of flight map and profile, with temperature colored."""
    warnings.filterwarnings("ignore", message="Tight layout not applied")
    #
    date_time_all = list(status_df['date_time'])
    lat_all = np.array(status_df['lat'])
    lon_all = np.array(status_df['lon'])
    alt_all = np.array(status_df['alt_MSL'])
    sfc_all = np.array(status_df['sfc_elev'])
    T_all = np.array(status_df['T'])
    #
    if np.sum(alt_all - sfc_all) == 0:
        return False
    idx1 = 0
    for idx, alt in enumerate(alt_all):
        if alt > sfc_all[idx]:
            idx1 = idx - 1
            break
    idx2 = -1
    for idx in range(len(alt_all)-1, -1, -1):
        if alt_all[idx] > sfc_all[idx]:
            idx2 = idx + 2
            break
    date_time = date_time_all[idx1:idx2]
    lat = lat_all[idx1:idx2]
    lon = lon_all[idx1:idx2]
    alt = alt_all[idx1:idx2]
    sfc = sfc_all[idx1:idx2]
    T = T_all[idx1:idx2]
    #
    init_time = iso8601.parse_date(date_time[0])
    elapsed_time = []
    for tt in date_time:
        tdiff = iso8601.parse_date(tt) - init_time
        elapsed_time.append(tdiff.seconds / 60.0)
    #
    # set up figure
    plt.figure(figsize=(8, 12))
    gs = gridspec.GridSpec(24, 16)
    #
    # plot flight map
    plt.subplot(gs[:14, :])
    b = setup_basemap(sim)
    #
    # plot flight map trajectory
    b.plot(lon[0], lat[0], '+', markersize=12, color='k', latlon=True)
    b.plot(lon[-1], lat[-1], 'x', markersize=10, color='k', latlon=True)
    b.plot(lon, lat, linewidth=5, color='r', latlon=True)
    #
    # plot flight vertical profile
    plt.subplot(gs[15:, 2:])
    points = np.array([elapsed_time, alt]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    norm = plt.Normalize(T.min(), T.max())
    lc = LineCollection(segments, cmap='jet', norm=norm)
    lc.set_array(T)
    lc.set_linewidth(5)
    line = plt.gca().add_collection(lc)
    cbar = plt.colorbar(line, shrink=0.9)
    cbar.set_label('Temperature [C]')
    plt.plot(elapsed_time, sfc, color='k', label='ground')
    plt.xlabel('Flight time [mins]', fontsize=10)
    plt.ylabel('Altitude [m AMSL]', fontsize=10)
    #
    # save and close figure
    plt.tight_layout()
    plt.savefig(outfname, dpi=300, bbox_inches='tight')
    plt.close()
    return True


def plot_all_flights(sim, wrf_grids, trajectories, outfname):
    """Map of all flight trajectories, with topography."""
    #
    # set up figure
    plt.figure(figsize=(8, 8))
    b = setup_basemap(sim)
    #
    # plot topography from WRF grid
    lons, lats = b(wrf_grids.map_lons, wrf_grids.map_lats)
    b.contourf(lons, lats, wrf_grids.map_topography, 48, cmap=get_cmap('terrain'))
    cbar = plt.colorbar(pad=0.02, shrink=0.75)
    cbar.ax.set_ylabel('surface elevation [m AMSL]')
    #
    # plot flight trajectories
    n_flights = 0
    for _, trajectory in trajectories.items():
        lats_all, lons_all, alt_AGL = trajectory
        if np.any(alt_AGL > 0.0):
            idx1 = 0
            for idx, alt in enumerate(alt_AGL):
                if alt > 0.0:
                    idx1 = idx - 1
                    break
            idx2 = -1
            for idx in range(len(alt_AGL)-1, -1, -1):
                if alt_AGL[idx] > 0.0:
                    idx2 = idx + 1
                    break
            lats = lats_all[idx1:idx2]
            lons = lons_all[idx1:idx2]
            npts = len(lats)
            if npts > 2:
                b.plot(lons[0], lats[0], '+', markersize=10, color='k', latlon=True)
                b.plot(lons[-1], lats[-1], 'x', markersize=8, color='k', latlon=True)
                b.plot(lons, lats, linewidth=1, color='r', latlon=True)
                n_flights += 1
    #
    sim_name = sim.simulation_name
    if sim.experiment_number:
        sim_name += ' exp. %s' % str(sim.experiment_number).zfill(2)
    titlestr = '%s simulation %s (%d of %d moths)' % \
        (sim_name, str(sim.simulation_number).zfill(5),
         n_flights, sim.n_fliers)
    plt.title(titlestr, fontsize=12)
    #
    # save and close figure
    plt.tight_layout()
    plt.savefig(outfname, dpi=300, bbox_inches='tight')
    plt.close()
    return


# end Plots_gen.py
