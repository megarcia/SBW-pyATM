# pylint: disable=C0103,C0413,R0913,R0914,R0915,R1711,W0621
"""
Python script "combine_dvel_grids.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2020-2021 by Matthew Garcia
"""


import os
import sys
from glob import glob
import numpy as np
import pandas as pd
from plot_combined_grids import plot_grid


fields = {'dens': 9, 'dvel': 4}


UTM_zone = 19
sw_east = 481000.0
sw_north = 5249000.0
ne_east = 726000.0
ne_north = 5493000.0
dx = 1000.0
dy = 1000.0


print()
field = 'dvel'
experiment = sys.argv[2]
date = sys.argv[1]
#
print('gathering file list for %s field' % field)
if experiment == 'default':
    inpath = '%s/WRF-NARR_d03_%s_simulation_000??_summary' % (experiment, date)
else:
    inpath = 'sensitivity_%s/WRF-NARR_d03_%s_simulation_%s_000??_summary' % \
        (str(int(experiment)).zfill(2), date, str(int(experiment)).zfill(2))
minute = fields[field]
if experiment == 'default':
    dens_fname_list = sorted(glob('%s/dens_*%d:00+00:00_000??_XAM_grid.npy' % (inpath, minute)))
    dvel_fname_list = sorted(glob('%s/dvel_*%d:00+00:00_000??_XAM_grid.npy' % (inpath, minute)))
else:
    dens_fname_list = sorted(glob('%s/dens_*%d:00+00:00_%s_000??_XAM_grid.npy' %
                                  (inpath, minute, str(int(experiment)).zfill(2))))
    dvel_fname_list = sorted(glob('%s/dvel_*%d:00+00:00_%s_000??_XAM_grid.npy' %
                                  (inpath, minute, str(int(experiment)).zfill(2))))
print('- found %d files to process' % len(dvel_fname_list))
files_df = pd.DataFrame({'dens_fname': dens_fname_list,
                         'dvel_fname': dvel_fname_list})
# 'dens_2013-07-15T23/54/00+00:00_10_00000_XAM_grid.npy'
# 'dvel_2013-07-15T23/54/00+00:00_10_00000_XAM_grid.npy'
times = [f.split('/')[-1].split('_')[1] for f in dvel_fname_list]
files_df['time'] = times
if experiment == 'default':
    iteration = [f.split('/')[-1].split('_')[2] for f in dvel_fname_list]
else:
    iteration = [f.split('/')[-1].split('_')[3] for f in dvel_fname_list]
files_df['iteration'] = iteration
times = sorted(list(set(times)))
times_df = pd.DataFrame({'%s_time' % field: times})
print('- found %d times to process' % len(times))
print()
#
print('building 1-km target grid according to radar coverage area')
print('- UTM zone = %d' % UTM_zone)
print('- SW corner easting = %.0f' % sw_east)
print('- NE corner easting = %.0f' % ne_east)
print('- dx = %.0f' % dx)
ncols = int((ne_east - sw_east) / dx)
print('- ncols = %d' % ncols)
print('- SW corner northing = %.0f' % sw_north)
print('- NE corner northing = %.0f' % ne_north)
print('- dy = %.0f' % dy)
nrows = int((ne_north - sw_north) / dy)
print('- nrows = %d' % nrows)
print()
#
if experiment == 'default':
    # if not os.path.exists('%s_collected' % (experiment)):
    #     os.mkdir('%s_collected' % (experiment))
    outpath = '%s_collected/dvel_grids' % experiment
else:
    # if not os.path.exists('sensitivity_%s_collected' % (experiment)):
    #     os.mkdir('sensitivity_%s_collected' % (experiment))
    outpath = 'sensitivity_%s_collected/dvel_grids' % experiment
file_dens_nmoths = list()
time_dens_nmoths = list()
time_max_dens_nmoths = list()
time_min_dvel = list()
time_max_dvel = list()
for timestr in times:
    print('processing %s' % timestr)
    time_df = files_df[files_df['time'] == timestr]
    dens_fname_list = list(time_df['dens_fname'])
    dvel_fname_list = list(time_df['dvel_fname'])
    iteration_list = list(time_df['iteration'])
    print('- %d files' % len(dvel_fname_list))
    #
    dens_combined_grid = np.zeros((nrows, ncols))
    dvel_combined_grid = np.zeros((nrows, ncols))
    for dens_fname, dvel_fname, iteration in zip(dens_fname_list,
                                                 dvel_fname_list,
                                                 iteration_list):
        if not os.path.isfile(dens_fname):
            print('%s not found, skipping' % dens_fname)
            continue
        if not os.path.isfile(dvel_fname):
            print('%s not found, skipping' % dvel_fname)
            continue
        dens_grid = np.load(dens_fname)
        nmoths = int(np.sum(dens_grid))
        file_dens_nmoths.append(nmoths)
        print('- %s (%d moths)' % (iteration, nmoths))
        dens_combined_grid += dens_grid
        dvel_grid = np.load(dvel_fname)
        dvel_combined_grid += dens_grid * dvel_grid
    #
    nmoths = int(np.sum(dens_combined_grid))
    time_dens_nmoths.append(nmoths)
    max_nmoths = int(np.max(dens_combined_grid))
    time_max_dens_nmoths.append(int(np.max(dens_combined_grid)))
    print('gridded %d flying moths' % nmoths)
    if nmoths:
        dvel_weighted_grid = dvel_combined_grid / dens_combined_grid
        min_dvel = np.nanmin(dvel_weighted_grid)
        time_min_dvel.append(min_dvel)
        max_dvel = np.nanmax(dvel_weighted_grid)
        time_max_dvel.append(max_dvel)
        print('- min = %.2f, max = %.2f' % (min_dvel, max_dvel))
        outfname = '%s/%s_%s_collected_XAM_grid.npy' % (outpath, field, timestr)
        np.save(outfname, dvel_weighted_grid)
        print('- saved %s' % outfname)
        title = '%s moth velocity (n = %d)' % (timestr, nmoths)
        outfname = '%s.png' % outfname[:-4]
        plot_grid(sw_east, sw_north, ne_east, ne_north, UTM_zone,
                  dvel_weighted_grid, -20, 20, 'RdYlGn', title, outfname)
    else:
        print('- no flight locations for saving/plotting')
        time_min_dvel.append(0.0)
        time_max_dvel.append(0.0)
    print()
#
files_df['nmoths'] = file_dens_nmoths
if experiment == 'default':
    outfname = '%s/%s_%s_%s_fileinfo.csv' % (outpath, field, date, experiment)
else:
    outfname = '%s/%s_%s_sensitivity_%s_fileinfo.csv' % \
        (outpath, field, date, str(int(experiment)).zfill(2))
files_df.to_csv(outfname, index=False)
print('saved %s' % outfname)
#
times_df['nmoths'] = time_dens_nmoths
times_df['max_nmoths'] = time_max_dens_nmoths
times_df['min_dvel'] = time_min_dvel
times_df['max_dvel'] = time_max_dvel
if experiment == 'default':
    outfname = '%s/%s_%s_%s_timeinfo.csv' % (outpath, field, date, experiment)
else:
    outfname = '%s/%s_%s_sensitivity_%s_timeinfo.csv' % \
        (outpath, field, date, str(int(experiment)).zfill(2))
times_df.to_csv(outfname, index=False)
print('saved %s' % outfname)
#
print()
print('done!')
print()

# end combine_dvel_grids.py
