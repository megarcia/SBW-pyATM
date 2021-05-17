# pylint: disable=C0103
"""
Python script "plot_radar_sim_comparison_lags.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


import sys
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


def message(char_string=''):
    """Print a string to the terminal and flush the buffer."""
    print(char_string)
    sys.stdout.flush()
    return


def plot_scores(scores, rtimes, lags, cmax, title, fname):
    """Plot composite scores through time."""
    plt.figure(figsize=(6, 4.5))
    ax = plt.gca()
    scores = np.where(scores == 0.0, np.nan, scores)
    stretch = 0.5
    plt.imshow(scores, cmap='plasma', aspect=stretch, interpolation='nearest')
    plt.clim(0, cmax)
    cbar = plt.colorbar(pad=0.02, shrink=0.67)
    cbar.ax.tick_params(labelsize=6)
    plt.plot((lags.index(0), lags.index(0)), (0, len(rtimes)-1), 'k--', linewidth=1)
    plt.text(lags.index(0), len(rtimes)-2, 'early   ', fontsize=8, horizontalalignment='right')
    plt.text(lags.index(0), len(rtimes)-2, '   late', fontsize=8, horizontalalignment='left')
    plt.xticks(ticks=range(len(lags)), labels=lags, fontsize=6)
    for label in ax.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)
    rtimes = [rt.split('T')[1] for rt in rtimes]
    plt.yticks(ticks=range(len(rtimes)), labels=rtimes, fontsize=6)
    for label in ax.yaxis.get_ticklabels()[::2]:
        label.set_visible(False)
    plt.xlabel('simulation lag [minutes]', fontsize=8)
    plt.ylabel('radar time (UTC = EDT + 4)', fontsize=8)
    plt.title(title, fontsize=8)
    #
    plt.savefig(fname, dpi=300, bbox_inches='tight')
    message('- saved figure %s' % fname)
    plt.close()
    return


message()
date = sys.argv[1]
exp_name = sys.argv[2]
if sim_name == 'default':
    sim_num = 0
    path = 'ATM_default'
else:
    sim_num = sim_name.split('_')[-1]
    path = 'ATM_indiv_sensitivity'
#
sim_path = '%s/%s/%s/%s_collected' % (path, date, exp_name, sim_name)
inf = '%s/%s_radar_sim_MFSS.csv' % (sim_path, sim_name)
message('reading %s' % inf)
accuracy_df = pd.read_csv(inf, index_col=False)
message()
#
min_lag = -90
max_lag = 90
lags = range(min_lag, max_lag + 10, 10)
rdatetimes = list(accuracy_df['radar_datetime'])
x = np.arange(-9, 10)
weights = stats.norm.pdf(x, loc=0, scale=2.9)
rtimes = sorted(list(set(rdatetimes)))
ntimes = len(rtimes)
nlags = len(lags)
scores_arr = np.zeros((ntimes, nlags))
fss_total = 0.0
for j, radar_dt in enumerate(rtimes):
    this_rtime_df = accuracy_df[accuracy_df['radar_datetime'] == radar_dt]
    this_rtime_lags = list(this_rtime_df['sim_lag'])
    this_rtime_scores = list(this_rtime_df['FSS_sum'])
    for ii, lag in enumerate(this_rtime_lags):
        i = lags.index(lag)
        scores_arr[j, i] = this_rtime_scores[ii]
        fss_total += scores_arr[j, i] * weights[i]
#
message('plotting fractions skill scores for lagged comparisons')
plot_title = '%s %s MFSS (total = %.1f)' % (date, sim_name, fss_total)
plot_fname = '%s/%s_radar_sim_MFSS.png' % (sim_path, sim_name)
plot_scores(scores_arr, rtimes, lags, 5.0, plot_title, plot_fname)
message()

# end plot_radar_sim_comparison_lags.py
