# pylint: disable=C0103,C0411,C0412,C0413,E0611,R0914,R0915,R1711
"""
Python script "map_locations_hexbin.py"
by Matthew Garcia, Post-doctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


import sys
from glob import glob
import numpy as np
import pandas as pd
from matplotlib.cm import get_cmap
from mpl_toolkits.basemap import Basemap
from Simulation_specifications import Simulation
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


def setup_map_fig(sim):
    plt.figure(figsize=(8, 8))
    bottom_lat = sim.plot_bottom_lat
    top_lat = sim.plot_top_lat
    left_lon = sim.plot_left_lon
    right_lon = sim.plot_right_lon
    mid_lat = (bottom_lat + top_lat) / 2.0
    mid_lon = (left_lon + right_lon) / 2.0
    bmap = Basemap(projection='tmerc', lon_0=mid_lon, lat_0=mid_lat,
                   lat_ts=mid_lat, llcrnrlat=bottom_lat, llcrnrlon=left_lon,
                   urcrnrlat=top_lat, urcrnrlon=right_lon, resolution='h',
                   area_thresh=500)
    bmap.drawcoastlines()
    bmap.drawstates()
    bmap.drawcountries()
    bmap.drawmapscale(lon=left_lon+0.75, lat=top_lat-0.5,
                      lon0=mid_lon, lat0=mid_lat, length=100.0,
                      barstyle='fancy')
    parallels = np.arange(30., 60., 1.)
    bmap.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
    meridians = np.arange(270., 360., 1.)
    bmap.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)
    return plt, bmap


def main(simdate, exp_name, sex, action):
    """Get and plot activity counts at indicated locations."""
    path = '%s_collected' % exp_name
    infnames = sorted(glob('%s/%s_locs/%s_locs_*.csv' % (path, action, action)))
    print('found %d input location files' % len(infnames))
    #
    infname = infnames[0]
    print('reading locations from %s' % infname)
    locations_df = pd.read_csv(infname, index_col=False, low_memory=False)
    for infname in infnames[1:]:
        print('reading locations from %s' % infname)
        temp_df = pd.read_csv(infname, index_col=False)
        locations_df = pd.concat([locations_df, temp_df], axis=0)
    print('found %d data rows' % len(locations_df))
    #
    if sex == 'male':
        locations_df = locations_df[locations_df['sex'] == 0]
    elif sex == 'female':
        locations_df = locations_df[locations_df['sex'] == 1]
    print('filtered to %d data rows' % len(locations_df))
    #
    lons = np.array(locations_df['longitude'])
    lats = np.array(locations_df['latitude'])
    if sex in ['female', 'all']:
        eggs = np.array(locations_df['F'])
    #
    sim = Simulation()
    print('plotting %s %s by location' % (sex, action))
    plt, bmap = setup_map_fig(sim)
    x, y = bmap(lons, lats)
    x_min, y_min = bmap(sim.plot_left_lon, sim.plot_bottom_lat)
    x_max, y_max = bmap(sim.plot_right_lon, sim.plot_top_lat)
    hbin = bmap.hexbin(x, y, extent=(x_min, x_max, y_min, y_max),
                       gridsize=100, mincnt=1, cmap=get_cmap('viridis'))
    cbar = plt.colorbar(pad=0.02, shrink=0.75)
    count_clevs = cbar.get_ticks().astype(int)
    cbar.set_ticks(count_clevs)
    cbar.ax.set_yticklabels(count_clevs, rotation=90, va='center')
    plt.tight_layout()
    title = '%s SBW adult %s %s (count)' % (simdate, sex, action)
    plt.title(title, fontsize=12)
    plot_fname = '%s/%s_%s_%s_%s_map.png' % (path, simdate, exp_name, sex, action)
    plt.savefig(plot_fname, dpi=300, bbox_inches='tight')
    plt.close()
    print('- saved %s' % plot_fname)
    #
    if sex == 'male':
        return
    #
    print('plotting %s %s fecundity by location' % (sex, action))
    plt, bmap = setup_map_fig(sim)
    x, y = bmap(lons, lats)
    hbin = bmap.hexbin(x, y, C=eggs, extent=(x_min, x_max, y_min, y_max),
                       gridsize=100, mincnt=1, cmap=get_cmap('viridis'),
                       reduce_C_function=np.sum)
    cbar = plt.colorbar(pad=0.02, shrink=0.75)
    count_clevs = cbar.get_ticks().astype(int)
    cbar.set_ticks(count_clevs)
    cbar.ax.set_yticklabels(count_clevs, rotation=90, va='center')
    plt.tight_layout()
    title = '%s SBW adult %s %s (fecundity)' % (simdate, sex, action)
    plt.title(title, fontsize=12)
    plot_fname = '%s/%s_%s_%s_%s_fecundity_map.png' % \
        (path, simdate, exp_name, sex, action)
    plt.savefig(plot_fname, dpi=300, bbox_inches='tight')
    plt.close()
    print('- saved %s' % plot_fname)


if __name__ == "__main__":
    print()
    simdate = sys.argv[1]
    exp_name = sys.argv[2]
    sex = sys.argv[3]
    action = sys.argv[4]
    main(simdate, exp_name, sex, action)
    print()

# end map_locations_hexbin.py
