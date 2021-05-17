# pylint: disable=C0103
"""
Python script "plot_radar_sim_comparison_nolags.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


import sys
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


def message(char_string=''):
    """Print a string to the terminal and flush the buffer."""
    print(char_string)
    sys.stdout.flush()
    return


def plot_scores(scores, rtimes, cmax, title, fname):
    """Plot composite scores through time."""
    plt.figure(figsize=(6, 4.5))
    ax = plt.gca()
    plt.plot(scores)
    plt.xlim(0, len(rtimes))
    plt.ylim(0, cmax)
    rtimes = [rt.split('T')[1] for rt in rtimes]
    plt.xticks(ticks=range(len(rtimes)), labels=rtimes, rotation=90, fontsize=6)
    for label in ax.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)
    plt.yticks(fontsize=6)
    plt.xlabel('radar time (UTC = EDT + 4)', fontsize=8)
    plt.ylabel('modified Fractions Skill Score', fontsize=8)
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
mfss_df = accuracy_df[accuracy_df['sim_lag'] == 0]
rdatetimes = list(mfss_df['radar_datetime'])
rtimes = sorted(list(set(rdatetimes)))
fss_series = np.array(mfss_df['FSS_sum'])
fss_max = np.max(fss_series)
fss_total = np.sum(fss_series)
#
message('plotting fractions skill scores for no-lag comparisons')
plot_title = '%s %s no-lag MFSS (max = %.2f, total = %.1f)' % (date, sim_name, fss_max, fss_total)
plot_fname = '%s/%s_radar_sim_MFSS_nolags.png' % (sim_path, sim_name)
plot_scores(fss_series, rtimes, 5.0, plot_title, plot_fname)
message()

# end plot_radar_sim_comparison_nolags.py
