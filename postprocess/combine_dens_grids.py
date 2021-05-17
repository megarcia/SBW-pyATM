# pylint: disable=C0103,C0413,R0913,R0914,R0915,R1711,W0621
"""
Python script "combine_dens_grids.py"
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
from message_fn import message


fields = {'dens': 9, 'dvel': 4}


UTM_zone = 19
sw_east = 481000.0
sw_north = 5249000.0
ne_east = 726000.0
ne_north = 5493000.0
dx = 1000.0
dy = 1000.0


message()
field = 'dens'
experiment = sys.argv[2]
date = sys.argv[1]
#
message('gathering file list for %s field' % field)
if experiment == 'default':
    inpath = '%s/WRF-NARR_d03_%s_simulation_000??_summary' % (experiment, date)
else:
    inpath = 'sensitivity_%s/WRF-NARR_d03_%s_simulation_%s_000??_summary' % \
        (str(int(experiment)).zfill(2), date, str(int(experiment)).zfill(2))
minute = fields[field]
if experiment == 'default':
    fname_list = sorted(glob('%s/%s_*%d:00+00:00_000??_XAM_grid.npy' % (inpath, field, minute)))
else:
    fname_list = sorted(glob('%s/%s_*%d:00+00:00_%s_000??_XAM_grid.npy' %
                             (inpath, field, minute, str(int(experiment)).zfill(2))))
message('- found %d files to process' % len(fname_list))
files_df = pd.DataFrame({'%s_fname' % field: fname_list})
# 'dens_2013-07-15T23/59/00+00:00_10_00000_XAM_grid.npy'
times = [f.split('/')[-1].split('_')[1] for f in fname_list]
files_df['time'] = times
if experiment == 'default':
    iteration = [f.split('/')[-1].split('_')[2] for f in fname_list]
else:
    iteration = [f.split('/')[-1].split('_')[3] for f in fname_list]
files_df['iteration'] = iteration
times = sorted(list(set(times)))
times_df = pd.DataFrame({'%s_time' % field: times})
message('- found %d times to process' % len(times))
message()
#
message('building 1-km target grid according to radar coverage area')
message('- UTM zone = %d' % UTM_zone)
message('- SW corner easting = %.0f' % sw_east)
message('- NE corner easting = %.0f' % ne_east)
message('- dx = %.0f' % dx)
ncols = int((ne_east - sw_east) / dx)
message('- ncols = %d' % ncols)
message('- SW corner northing = %.0f' % sw_north)
message('- NE corner northing = %.0f' % ne_north)
message('- dy = %.0f' % dy)
nrows = int((ne_north - sw_north) / dy)
message('- nrows = %d' % nrows)
message()
#
if experiment == 'default':
    # if not os.path.exists('%s_collected' % (experiment)):
    #     os.mkdir('%s_collected' % (experiment))
    outpath = '%s_collected/dens_grids' % experiment
else:
    # if not os.path.exists('sensitivity_%s_collected' % (experiment)):
    #     os.mkdir('sensitivity_%s_collected' % (experiment))
    outpath = 'sensitivity_%s_collected/dens_grids' % experiment
file_dens_nmoths = list()
time_dens_nmoths = list()
time_max_dens_nmoths = list()
for timestr in times:
    message('processing %s' % timestr)
    time_df = files_df[files_df['time'] == timestr]
    fname_list = list(time_df['%s_fname' % field])
    iteration_list = list(time_df['iteration'])
    message('- %d files' % len(fname_list))
    #
    combined_grid = np.zeros((nrows, ncols))
    for fname, iteration in zip(fname_list, iteration_list):
        if not os.path.isfile(fname):
            message('%s not found, skipping' % fname)
            continue
        grid = np.load(fname)
        nmoths = int(np.sum(grid))
        file_dens_nmoths.append(nmoths)
        message('- %s (%d moths)' % (iteration, nmoths))
        combined_grid += grid
    nmoths = int(np.sum(combined_grid))
    time_dens_nmoths.append(nmoths)
    max_nmoths = int(np.max(combined_grid))
    time_max_dens_nmoths.append(max_nmoths)
    message('gridded %d flying moths (max = %d)' % (nmoths, max_nmoths))
    outfname = '%s/%s_%s_collected_XAM_grid.npy' % (outpath, field, timestr)
    np.save(outfname, combined_grid)
    message('- saved %s' % outfname)
    if nmoths:
        title = '%s moth density (n = %d)' % (timestr, nmoths)
        outfname = '%s.png' % outfname[:-4]
        plot_grid(sw_east, sw_north, ne_east, ne_north, UTM_zone,
                  combined_grid, 1, 10, 'viridis', title, outfname)
    else:
        message('- no flight locations for plotting')
    message()
#
files_df['nmoths'] = file_dens_nmoths
if experiment == 'default':
    outfname = '%s/%s_%s_%s_fileinfo.csv' % (outpath, field, date, experiment)
else:
    outfname = '%s/%s_%s_sensitivity_%s_fileinfo.csv' % \
        (outpath, field, date, str(int(experiment)).zfill(2))
files_df.to_csv(outfname, index=False)
message('saved %s' % outfname)
#
times_df['nmoths'] = time_dens_nmoths
times_df['max_nmoths'] = time_max_dens_nmoths
if experiment == 'default':
    outfname = '%s/%s_%s_%s_timeinfo.csv' % (outpath, field, date, experiment)
else:
    outfname = '%s/%s_%s_sensitivity_%s_timeinfo.csv' % \
        (outpath, field, date, str(int(experiment)).zfill(2))
times_df.to_csv(outfname, index=False)
message('saved %s' % outfname)
#
message()
message('done!')
message()

# end combine_dens_grids.py
