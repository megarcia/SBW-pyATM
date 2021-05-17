# pylint: disable=C0103,C0413,R1711
"""
Python script "plot_liftoff_time_histograms.py"
by Matthew Garcia, Post-doctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2020-2021 by Matthew Garcia
"""


import sys
from datetime import datetime, timedelta, timezone
import iso8601
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from Experiment_class import gen_experiments
from message_fn import message
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


def parse_time_values(values):  # list of str
    """Parse ISO8601 time values to python time objects."""
    values_out = list()
    for v in values:
        if v in ['0', 'None']:
            values_out.append('None')
        else:
            values_out.append(iso8601.parse_date(v))
    return values_out  # list of datetime objects


def get_weighted_mean(weights, values, time=False):  # lists of float and bool
    """Calculate weighted mean of given values."""
    weights = [w for w in weights if w not in ['0', 'None']]
    values = [v for v in values if v not in ['0', 'None']]
    if time:
        values = parse_time_values(values)  # list of str --> list of datetime objects
        min_time = min(values)
        values = [(value - min_time).seconds for value in values]
    sum_weights = np.sum(weights)
    sum_product = np.sum([w * v for w, v in zip(weights, values)])
    weighted_mean = sum_product / sum_weights
    if time:
        weighted_mean = min_time + timedelta(seconds=weighted_mean)
        # weighted_mean = weighted_mean.isoformat()
    return weighted_mean  # float or datetime object


def calc_circadian_p(t_c, t_0, t_m, date_time):
    """Regniere et al. [2019]; date_time is a datetime object in UTC."""
    C = 1.0 - (2.0 / 3.0) + (1.0 / 5.0)
    if date_time > t_m:
        circadian_p = 1.0
    elif date_time >= t_0:
        if date_time <= t_c:
            tau_denom = t_c - t_0
        else:
            tau_denom = t_m - t_c
        tau = (date_time - t_c) / tau_denom
        term2 = (2.0 / 3.0) * tau**3
        term3 = (1.0 / 5.0) * tau**5
        circadian_p = (C + tau - term2 + term3) / (2 * C)
        if circadian_p < 0.0:
            circadian_p = 0.0
    else:
        circadian_p = 0.0
    return circadian_p  # float


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
summary_fname = '%s/%s_collected_stats.csv' % (path, sim_name)
summary_df = pd.read_csv(summary_fname, index_col=False)
summary_df.columns = [col.lstrip() for col in summary_df.columns]
nmoths = np.array(summary_df['n_total'])
nfemales = np.array(summary_df['n_female'])
nmales = np.array(summary_df['n_male'])
all_fliers = np.array(summary_df['n_fliers_total'])
female_fliers = np.array(summary_df['n_fliers_female'])
male_fliers = np.array(summary_df['n_fliers_male'])
message('flier total fractions:')
message('    female: %.3f' % (np.sum(female_fliers) / np.sum(nfemales)))
message('    male: %.3f' % (np.sum(male_fliers) / np.sum(nmales)))
message('    overall: %.3f' % (np.sum(all_fliers) / np.sum(nmoths)))
#
overall_fname = '%s/%s_liftoff_times_histogram.csv' % (path, sim_name)
overall_df = pd.read_csv(overall_fname, index_col=False)
x_vals = np.array(overall_df.columns).astype(int)
nvals = len(x_vals)
overall_y_vals = np.array(overall_df.sum(axis=0).astype(float))
#
female_fname = '%s/%s_liftoff_times_female_histogram.csv' % (path, sim_name)
female_df = pd.read_csv(female_fname, index_col=False)
female_y_vals = np.array(female_df.sum(axis=0).astype(float))
#
male_fname = '%s/%s_liftoff_times_male_histogram.csv' % (path, sim_name)
male_df = pd.read_csv(male_fname, index_col=False)
male_y_vals = np.array(male_df.sum(axis=0).astype(float))
#
female_y_vals = female_y_vals / np.sum(female_y_vals)
male_y_vals = male_y_vals / np.sum(male_y_vals)
overall_y_vals = overall_y_vals / np.sum(overall_y_vals)
#
female_accum_y_vals = [female_y_vals[0]]
male_accum_y_vals = [male_y_vals[0]]
overall_accum_y_vals = [overall_y_vals[0]]
for i in range(1, nvals):
    female_accum_y_vals.append(np.sum(female_y_vals[0:i+1]))
    male_accum_y_vals.append(np.sum(male_y_vals[0:i+1]))
    overall_accum_y_vals.append(np.sum(overall_y_vals[0:i+1]))
#
# calculate optimum likelihood line according to weighted mean Tref
summary_fname = '%s/%s_collected_stats.csv' % (path, sim_name)
summary_df = pd.read_csv(summary_fname, index_col=False)
summary_df.columns = [col.strip() for col in list(summary_df.columns)]
n_fliers = np.array(summary_df['n_fliers_total'])
sunsets = list(summary_df['sunset_mean'])
sunset_mean = get_weighted_mean(n_fliers, sunsets, time=True)
Trefs = np.array(summary_df['Tref_mean'])
Tref_mean = get_weighted_mean(n_fliers, Trefs, time=False)
circadian_p1 = -3.8    # [h]
circadian_p2 = 0.145   # [h/C]
circadian_p3 = -1.267  # [h]
circadian_p4 = -0.397  # [-]
circadian_p5 = -2.465  # [-]
circadian_kf = 1.35    # [-]
delta_s = circadian_p1 + circadian_p2 * Tref_mean
delta_0 = circadian_p3 + circadian_p4 * delta_s
delta_f = circadian_p5 * delta_0
delta_f_potential = circadian_kf * delta_f
t_c = sunset_mean + timedelta(hours=delta_s)
t_0 = t_c + timedelta(hours=delta_0)
if delta_f_potential:
    t_m = t_0 + timedelta(hours=delta_f_potential)
else:
    t_m = t_0 + timedelta(hours=delta_f)
yyyy = int(date[:4])
mm = int(date[4:6])
dd = int(date[6:])
start_time = datetime(yyyy, mm, dd, 21, 0, 0, tzinfo=timezone.utc)
optimum_y_vals = list()
for t in x_vals:
    date_time = start_time + timedelta(seconds=t*60.0)
    likelihood = calc_circadian_p(t_c, t_0, t_m, date_time)
    optimum_y_vals.append(likelihood)
sunset_mean_mins = (sunset_mean - start_time).seconds / 60.0
#
corr, _ = pearsonr(overall_accum_y_vals, optimum_y_vals)
mean_actual = np.sum(overall_accum_y_vals * x_vals) / np.sum(overall_accum_y_vals)
mean_optimum = np.sum(optimum_y_vals * x_vals) / np.sum(optimum_y_vals)
bias = mean_actual - mean_optimum
message('liftoff time distribution')
message('    corr = %.4f' % corr)
message('    bias = %.1f mins' % bias)
#
fig_fname = '%s/%s_liftoff_times_histogram.png' % (path, sim_name)
plt.figure(figsize=(6, 4))
plt.plot(x_vals, female_accum_y_vals, color='r', label='females')
plt.plot(x_vals, male_accum_y_vals, color='b', label='males')
plt.plot(x_vals, overall_accum_y_vals, color='k', label='all fliers')
plt.plot(x_vals, optimum_y_vals, 'g--', label='theoretical')
plt.plot([sunset_mean_mins, sunset_mean_mins], [0.0, 1.0], 'k--', label='sunset')
plt.xlim([0, 420])
plt.ylim([0.0, 1.0])
plt.xticks(fontsize=8)
plt.yticks(fontsize=8)
plt.legend(loc='upper left', fontsize=9)
plt.xlabel('liftoff time (mins after 2100 UTC)', fontsize=10)
plt.ylabel('fraction of fliers lifted off', fontsize=10)
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

# end plot_liftoff_time_histograms.py
