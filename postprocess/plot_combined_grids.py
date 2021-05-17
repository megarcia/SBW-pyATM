# pylint: disable=C0103
"""
Python script "plot_combined_grids.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


import numpy as np
from message_fn import message
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


def plot_grid(sw_e, sw_n, ne_e, ne_n, UTMz, grid, cmin, cmax, cmap, title, fname):
    """Plot combined grid."""
    sw_e = sw_e / 1000.0
    sw_n = sw_n / 1000.0
    ne_e = ne_e / 1000.0
    ne_n = ne_n / 1000.0
    fig, _ = plt.subplots()
    fig.set_size_inches(6, 6)
    grid_nan = np.where(grid == 0, np.nan, grid)
    stretch = (ne_e - sw_e) / (ne_n - sw_n)
    plt.imshow(grid_nan, extent=(sw_e, ne_e, sw_n, ne_n), aspect=stretch,
               interpolation='nearest', origin='lower', cmap=plt.get_cmap(cmap))
    plt.clim(cmin, cmax)
    cbar = plt.colorbar(shrink=0.9)
    cbar.ax.tick_params(labelsize=8)
    plt.xlim([sw_e, ne_e])
    plt.ylim([sw_n, ne_n])
    plt.xticks(fontsize=10)
    plt.yticks(rotation='vertical', va='center', fontsize=10)
    plt.xlabel('UTM %dN easting (km)' % UTMz, fontsize=10)
    plt.ylabel('UTM %sN northing (km)' % UTMz, fontsize=10)
    plt.title(title, fontsize=10)
    plt.savefig(fname, dpi=300, bbox_inches='tight')
    message('- saved figure %s' % fname)
    plt.close()
    return

# end plot_combined_grids.py
