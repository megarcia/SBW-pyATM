# pylint: disable=C0103,C0413,R0912,R0914,R0915,R1711
"""
Python script "summarize_experiment_stats.py"
by Matthew Garcia, Post-doctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


import sys
from datetime import timedelta
import iso8601
import numpy as np
import pandas as pd


def parse_time_values(values):  # list of str
    """Parse ISO8601 time values to python time objects."""
    values_out = list()
    for v in values:
        if v in ['0', 'None']:
            values_out.append('None')
        else:
            values_out.append(iso8601.parse_date(v))
    return values_out  # list of datetime objects


def get_weighted_mean(weights, values, time=False):  # lists of float + bool
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
        weighted_mean = weighted_mean.isoformat().split('.')[0]
    return weighted_mean  # float or str


def get_weighted_stdv(weights, stdv_values):  # lists of float
    """Calculate weighted mean of given values."""
    weights = [w for w in weights if w not in ['0', 'None']]
    stdv_values = [v for v in stdv_values if v not in ['0', 'None']]
    weights = [w - 1 for w in weights]
    var_values = [s**2 for s in stdv_values]
    sum_weights = np.sum(weights)
    sum_product = np.sum([w * v for w, v in zip(weights, var_values)])
    weighted_stdv = np.sqrt(sum_product / sum_weights)
    return weighted_stdv  # float


def list_all_time_stats(var, weights, stats_df, outf):  # str + list of datetime + DataFrame + outfile
    """Get min, weighted mean, weighted stdv, and max of selected time variable."""
    min_val = min(parse_time_values(list(stats_df['%s_min' % var])))
    outf.write('    min = %s UTC \n' % min_val.isoformat().split('+')[0])
    mean_val = get_weighted_mean(weights, list(stats_df['%s_mean' % var]), time=True)
    outf.write('    mean = %s UTC \n' % mean_val)
    stdv_val = get_weighted_stdv(weights, list(stats_df['%s_stdv' % var]))
    outf.write('    stdv = %.1f mins \n' % stdv_val)
    max_val = max(parse_time_values(list(stats_df['%s_max' % var])))
    outf.write('    max = %s UTC \n' % max_val.isoformat().split('+')[0])
    outf.write('\n')
    return


def list_mean_stdv_stats(var, weights, stats_df, units, outf, newline=True):  # str + list of float + DataFrame + outfile
    """Get min, weighted mean, weighted stdv, and max of selected variable."""
    mean_val = get_weighted_mean(weights, list(stats_df['%s_mean' % var]))
    outf.write('    mean = %.1f %s \n' % (mean_val, units))
    stdv_val = get_weighted_stdv(weights, list(stats_df['%s_stdv' % var]))
    outf.write('    stdv = %.1f %s \n' % (stdv_val, units))
    if newline:
        outf.write('\n')
    return


def list_all_stats(var, weights, stats_df, units, outf):  # str + list of float + DataFrame + outfile
    """Get min, weighted mean, weighted stdv, and max of selected variable."""
    outf.write('    min = %.1f %s \n' % (min(list(stats_df['%s_min' % var])), units))
    list_mean_stdv_stats(var, weights, stats_df, units, outf, newline=False)
    outf.write('    max = %.1f %s \n' % (max(list(stats_df['%s_max' % var])), units))
    outf.write('\n')
    return


def main(simdate, exp_name):
    """Summarize stats for a collection of experimental iterations."""
    path = '%s_collected' % exp_name
    infname = '%s/%s_collected_stats.csv' % (path, exp_name)
    stats_df = pd.read_csv(infname, index_col=False)
    outfname = '%s/%s_stats_summary.txt' % (path, exp_name)
    with open(outfname, 'w') as outfile:
        outfile.write('summarizing %d viable %s %s simulation reports \n' % (len(stats_df), simdate, exp_name))
        outfile.write('\n')
        #
        outfile.write('total moths: %d \n' % stats_df['n_total'].sum())
        outfile.write('    female = %d \n' % stats_df['n_female'].sum())
        outfile.write('    male = %d \n' % stats_df['n_male'].sum())
        outfile.write('\n')
        #
        outfile.write('non-fliers: %d \n' % stats_df['n_nonfliers_total'].sum())
        outfile.write('    female = %d \n' % stats_df['n_nonfliers_female'].sum())
        outfile.write('    male = %d \n' % stats_df['n_nonfliers_male'].sum())
        outfile.write('\n')
        #
        n_fliers_total = list(stats_df['n_fliers_total'])
        n_fliers_female = list(stats_df['n_fliers_female'])
        n_fliers_male = list(stats_df['n_fliers_male'])
        #
        outfile.write('fliers: %d \n' % np.sum(n_fliers_total))
        outfile.write('    female = %d \n' % np.sum(n_fliers_female))
        outfile.write('    male = %d \n' % np.sum(n_fliers_male))
        outfile.write('\n')
        #
        outfile.write('overall flight start: \n')
        list_all_time_stats('flight_start', n_fliers_total, stats_df, outfile)
        outfile.write('female flight start: \n')
        list_all_time_stats('flight_start_female', n_fliers_female, stats_df, outfile)
        outfile.write('male flight start: \n')
        list_all_time_stats('flight_start_male', n_fliers_male, stats_df, outfile)
        #
        outfile.write('overall flight duration: \n')
        list_all_stats('flight_duration', n_fliers_total, stats_df, 'mins', outfile)
        outfile.write('female flight duration: \n')
        list_all_stats('flight_duration_female', n_fliers_female, stats_df, 'mins', outfile)
        outfile.write('male flight duration: \n')
        list_all_stats('flight_duration_male', n_fliers_male, stats_df, 'mins', outfile)
        #
        outfile.write('overall flight distance: \n')
        list_all_stats('flight_dist', n_fliers_total, stats_df, 'km', outfile)
        outfile.write('female flight distance: \n')
        list_all_stats('flight_dist_female', n_fliers_female, stats_df, 'km', outfile)
        outfile.write('male flight distance: \n')
        list_all_stats('flight_dist_male', n_fliers_male, stats_df, 'km', outfile)
        #
        outfile.write('overall flight speed: \n')
        list_mean_stdv_stats('flight_speed', n_fliers_total, stats_df, 'm/s', outfile)
        outfile.write('female flight speed: \n')
        list_mean_stdv_stats('flight_speed_female', n_fliers_female, stats_df, 'm/s', outfile)
        outfile.write('male flight speed: \n')
        list_mean_stdv_stats('flight_speed_male', n_fliers_male, stats_df, 'm/s', outfile)
        #
        mean_val = get_weighted_mean(n_fliers_total, list(stats_df['flight_wind_speed_mean']))
        outfile.write('mean wind speed = %.1f m/s \n' % mean_val)
        outfile.write('\n')
        #
        outfile.write('overall flight airspeed: \n')
        list_mean_stdv_stats('flight_airspeed', n_fliers_total, stats_df, 'm/s', outfile)
        outfile.write('female flight airspeed: \n')
        list_mean_stdv_stats('flight_airspeed_female', n_fliers_female, stats_df, 'm/s', outfile)
        outfile.write('male flight airspeed: \n')
        list_mean_stdv_stats('flight_airspeed_male', n_fliers_male, stats_df, 'm/s', outfile)
        #
        outfile.write('overall flight altitude AGL: \n')
        list_mean_stdv_stats('flight_meanAGL', n_fliers_total, stats_df, 'm', outfile)
        outfile.write('female flight altitude AGL: \n')
        list_mean_stdv_stats('flight_meanAGL_female', n_fliers_female, stats_df, 'm', outfile)
        outfile.write('male flight altitude AGL: \n')
        list_mean_stdv_stats('flight_meanAGL_male', n_fliers_male, stats_df, 'm', outfile)
        #
        outfile.write('overall maximum flight altitude AGL: \n')
        list_mean_stdv_stats('flight_maxAGL', n_fliers_total, stats_df, 'm', outfile)
        outfile.write('female maximum flight altitude AGL: \n')
        list_mean_stdv_stats('flight_maxAGL_female', n_fliers_female, stats_df, 'm', outfile)
        outfile.write('male maximum flight altitude AGL: \n')
        list_mean_stdv_stats('flight_maxAGL_male', n_fliers_male, stats_df, 'm', outfile)
        #
        outfile.write('overall maximum flight altitude AMSL: \n')
        list_mean_stdv_stats('flight_maxAMSL', n_fliers_total, stats_df, 'm', outfile)
        outfile.write('female maximum flight altitude AMSL: \n')
        list_mean_stdv_stats('flight_maxAMSL_female', n_fliers_female, stats_df, 'm', outfile)
        outfile.write('male maximum flight altitude AMSL: \n')
        list_mean_stdv_stats('flight_maxAMSL_male', n_fliers_male, stats_df, 'm', outfile)
    #
    print('wrote %s' % outfname)


if __name__ == "__main__":
    print()
    date = sys.argv[1]
    exp_name = sys.argv[2]
    main(date, exp_name)
    print()

# end summarize_experiment_stats.py
