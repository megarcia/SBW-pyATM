# pylint: disable=C0103,C0413,R1711
"""
Python script "plot_flight_distance_histograms.py"
by Matthew Garcia, Post-doctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2020-2021 by Matthew Garcia
"""


import sys
import numpy as np
import pandas as pd
from Experiment_class import gen_experiments
from message_fn import message
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


message()
date = sys.argv[1]
sim_name = sys.argv[2]
if sim_name == 'default':
    sim_num = 0
else:
    sim_num = sim_name.split('_')[-1]
path = '%s_collected' % sim_name
#
experiments = gen_experiments()
#
overall_fname = '%s/%s_flight_dist_histogram.csv' % (path, sim_name)
overall_df = pd.read_csv(overall_fname, index_col=False)
x_vals = np.array(overall_df.columns).astype(int)
overall_y_vals = np.array(overall_df.sum(axis=0).astype(float))
#
female_fname = '%s/%s_flight_dist_female_histogram.csv' % (path, sim_name)
female_df = pd.read_csv(female_fname, index_col=False)
female_y_vals = np.array(female_df.sum(axis=0).astype(float))
#
male_fname = '%s/%s_flight_dist_male_histogram.csv' % (path, sim_name)
male_df = pd.read_csv(male_fname, index_col=False)
male_y_vals = np.array(male_df.sum(axis=0).astype(float))
#
female_y_vals = female_y_vals / np.sum(overall_y_vals)
male_y_vals = male_y_vals / np.sum(overall_y_vals)
overall_y_vals = overall_y_vals / np.sum(overall_y_vals)
#
fig_fname = '%s/%s_flight_dist_histogram.png' % (path, sim_name)
plt.figure(figsize=(6, 4))
plt.plot(x_vals, female_y_vals, color='r', label='females')
plt.plot(x_vals, male_y_vals, color='b', label='males')
plt.plot(x_vals, overall_y_vals, color='k', label='all fliers')
plt.xlim([0, 400])  # 500])
plt.ylim([0.0, 0.05])  # 0.07])
plt.xticks(fontsize=8)
plt.yticks(fontsize=8)
plt.legend(loc='upper right', fontsize=9)
plt.xlabel('overall flight distance (km)', fontsize=10)
plt.ylabel('fraction of all fliers', fontsize=10)
if sim_num:
    plt.title('%s %s (%s = %.2f)' % (date, sim_name, experiments[sim_num].variable,
                                     experiments[sim_num].value), fontsize=10)
else:
    plt.title('%s %s' % (date, sim_name), fontsize=10)
plt.tight_layout()
plt.savefig(fig_fname, dpi=300, bbox_inches='tight')
message('saved figure %s' % fig_fname)
plt.close()
message()

# end plot_flight_distance_histogram.py
