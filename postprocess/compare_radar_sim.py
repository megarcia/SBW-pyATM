# pylint: disable=C0103,C0413,R0912,R0913,R0914,R0915,R1711,W0621
"""
Python script "compare_radar_sim.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2020-2021 by Matthew Garcia
"""


import sys
import glob
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy import ndimage


def message(char_string=''):
    """Print a string to the terminal and flush the buffer."""
    print(char_string)
    sys.stdout.flush()
    return


def calc_frac_grid(binary_grid, neighborhood_size):
    """Obtain the fractions grid by mean image filter."""
    frac_grid = ndimage.uniform_filter(binary_grid, size=neighborhood_size,
                                       mode='constant')
    return frac_grid


def calc_frac_skill_score(obs_grid, sim_grid, neighborhood_size):
    """Calculate the fractions skill score (Roberts and Lean, 2008)."""
    obs_frac_grid = calc_frac_grid(obs_grid, neighborhood_size)
    sim_frac_grid = calc_frac_grid(sim_grid, neighborhood_size)
    MSE = np.sum((obs_frac_grid - sim_frac_grid)**2)
    MSE_ref = np.sum(obs_frac_grid**2 + sim_frac_grid**2)
    frac_skill_score = 1.0 - (MSE / MSE_ref)
    if np.isnan(frac_skill_score):
        frac_skill_score = 0.0
    return frac_skill_score


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
sim_count_grids = sorted(glob.glob('%s/dens_*_grid.npy' % sim_path))
message('found %d simulation count grid files' % len(sim_count_grids))
#
radar_path = 'Radar/%s_XAM_radar/grids' % date
radar_refl_grids = sorted(glob.glob('%s/*_refl.npy' % radar_path))
message('found %d radar reflectivity grid files' % len(radar_refl_grids))
#
UTM_zone = 19
sw_east = 481000.0
sw_north = 5249000.0
ne_east = 726000.0
ne_north = 5493000.0
dx = 1000.0
dy = 1000.0
#
XAM_east = (sw_east + ne_east) / 2.0
XAM_north = (sw_north + ne_north) / 2.0
ne_east = XAM_east  # for W half
sw_north = XAM_north  # for N half
#
ncols = int((ne_east - sw_east) / dx) + 1
nrows = int((ne_north - sw_north) / dy) + 1
#
UTC_offset = 0  # radar grids are on UTC, *not* EDT = UTC - 4
min_lag = -90
max_lag = 90
n_quantiles = 15
max_range = 11
neighborhoods = range(1, max_range+2, 2)
#
refl_grid_pairs = []
lags = range(min_lag, max_lag + 10, 10)
for radarf in radar_refl_grids:
    rdatestr = radarf.split('/')[-1].split('.')[0].split('_')[0]
    ry = int(rdatestr[:4])
    rm = int(rdatestr[4:6])
    rd = int(rdatestr[6:])
    rtimestr = radarf.split('/')[-1].split('.')[0].split('_')[1]
    rh = int(rtimestr[:2])
    rmm = int(rtimestr[2:])
    radar_date_time = datetime(ry, rm, rd, rh, rmm, 0, 0)
    radar_date_time_UTC = radar_date_time - timedelta(hours=UTC_offset)
    # 20130715_2209_refl.npy
    rdatestr = '%s%s%s' % (str(ry), str(rm).zfill(2), str(rd).zfill(2))
    rtimestr = '%s%s' % (str(rh).zfill(2), str(rmm).zfill(2))
    rdatetime = [rdatestr, rtimestr]
    for lag in lags:
        sim_date_time_UTC = radar_date_time_UTC + timedelta(minutes=lag)
        sy = sim_date_time_UTC.year
        sm = sim_date_time_UTC.month
        sd = sim_date_time_UTC.day
        sh = sim_date_time_UTC.hour
        smm = sim_date_time_UTC.minute
        # dens_2013-07-15T22:09:00_collected_XAM_grid.npy
        sdatestr = '%s-%s-%s' % (str(sy), str(sm).zfill(2), str(sd).zfill(2))
        stimestr = '%s:%s:00+00:00' % (str(sh).zfill(2), str(smm).zfill(2))
        simf = '%s/dens_%sT%s_collected_XAM_grid.npy' % (sim_path, sdatestr, stimestr)
        sdatestr = '%s%s%s' % (str(sy), str(sm).zfill(2), str(sd).zfill(2))
        stimestr = '%s%s' % (str(sh).zfill(2), str(smm).zfill(2))
        sdatetime = [sdatestr, stimestr]
        # check file availability for pairing
        if simf in sim_count_grids:
            message('paired %s with %s (lag = %d mins)' %
                    (radarf.split('/')[-1], simf.split('/')[-1], lag))
            refl_grid_pairs.append([radarf, simf, rdatetime, lag, sdatetime])
message('found %d corresponding pairs of radar reflectivity and sim count grids' %
        len(refl_grid_pairs))
message()
#
rdatetimes = list()
sdatetimes = list()
sim_maxs = list()
sim_lags = list()
frac_skill_scores = np.zeros((len(refl_grid_pairs), n_quantiles))
#
for i, fpair in enumerate(refl_grid_pairs):
    radarf, simf, rdatetime, lag, sdatetime = fpair
    message('examining results for')
    message('- radar time %s %s' % (rdatetime[0], rdatetime[1]))
    rdatetimes.append('%sT%s' % (rdatetime[0], rdatetime[1]))
    radar_grid_full = np.load(radarf)
    radar_grid = radar_grid_full[nrows-1:, :ncols]  # get NW quadrant
    message('- sim time   %s %s' % (sdatetime[0], sdatetime[1]))
    sdatetimes.append('%sT%s' % (sdatetime[0], sdatetime[1]))
    sim_grid_full = np.load(simf)
    sim_grid = sim_grid_full[nrows-1:, :ncols]  # get NW quadrant
    sim_maxs.append(int(np.max(sim_grid)))
    message('- sim lag = %d mins' % lag)
    sim_lags.append(lag)
    #
    radar_min = -6
    radar_max = 24
    radar_increment = (radar_max - radar_min) / n_quantiles
    sim_min = 1
    sim_max = np.max(sim_maxs)
    sim_increment = (sim_max - sim_min) / n_quantiles
    #
    message('- calculating fractions skill scores')
    for q in range(n_quantiles):
        radar_low = radar_min + q * radar_increment
        radar_mask_lower = np.where(radar_grid < radar_low, 0, 1)
        # radar_high = radar_low + radar_increment
        # radar_mask_upper = np.where(radar_grid > radar_high, 0, 1)
        radar_mask_upper = np.where(radar_grid > radar_max, 0, 1)
        radar_binary_grid = radar_mask_lower * radar_mask_upper
        sim_low = sim_min + q * sim_increment
        sim_mask_lower = np.where(sim_grid < sim_low, 0, 1)
        # sim_high = sim_low + sim_increment
        # sim_mask_upper = np.where(sim_grid > sim_high, 0, 1)
        sim_mask_upper = np.where(sim_grid > sim_max, 0, 1)
        sim_binary_grid = sim_mask_lower * sim_mask_upper
        fss_by_q = 0
        for n in neighborhoods:
            fss_by_q += calc_frac_skill_score(radar_binary_grid, sim_binary_grid, n)
        frac_skill_scores[i, q] = fss_by_q
    message()
#
accuracy_df = pd.DataFrame({'radar_datetime': rdatetimes,
                            'sim_datetime': sdatetimes,
                            'sim_lag': sim_lags,
                            'sim_max': sim_maxs})
for q in range(n_quantiles):
    accuracy_df['FSS_q%d' % (q+1)] = frac_skill_scores[:, q]
accuracy_df['FSS_sum'] = np.sum(frac_skill_scores, axis=1)
outf = '%s/../%s_radar_sim_MFSS.csv' % (sim_path, sim_name)
accuracy_df.to_csv(outf, index=False)
message('wrote %s' % outf)
message()

# end compare_radar_sim.py
