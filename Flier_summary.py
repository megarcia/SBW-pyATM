# pylint: disable=C0103,R0913,R0912,R0914,R0915,R1711
"""
Python script "Flier_summary.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2019-2021 by Matthew Garcia
"""


from datetime import timedelta
import iso8601
import numpy as np
import pandas as pd
from Flier_grids import grid_flier_locations, grid_flier_dvels
from Plots_gen import plot_all_flights


def summarize_locations(fliers, dt_str):  # dict, str
    """Collect location information for all Flier objects."""
    print('%s : summarizing flier locations' % dt_str)
    locations = dict()
    for flier_id, flier in fliers.items():
        if (flier.state in ['INITIALIZED', 'OVIPOSITION']) or flier.active:
            locations[flier_id] = [flier.lat, flier.lon, flier.alt_AGL,
                                   flier.alt_MSL, flier.GpH, flier.UTM_zone,
                                   flier.easting, flier.northing]
    return locations  # dict


def summarize_motion(fliers, locations):  # 2 * dict
    """Append Flier motion to location information."""
    for flier_id, flier in fliers.items():
        if (flier.state in ['INITIALIZED', 'OVIPOSITION']) or flier.active:
            if flier.alt_AGL > 0.0:
                locations[flier_id].append(flier.v_x + flier.U)
                locations[flier_id].append(flier.v_y + flier.V)
                locations[flier_id].append(flier.v_z + flier.W)
            else:
                locations[flier_id].append(flier.v_x)
                locations[flier_id].append(flier.v_y)
                locations[flier_id].append(flier.v_z)
            locations[flier_id].append(flier.v_radial)
            locations[flier_id].append(flier.v_azimuthal)
    return locations  # dict


def summarize_activity(fliers, dt_str):  # dict, str
    """In-simulation summary of flier activity."""
    print('%s : flier summary:' % dt_str)
    summary = np.zeros(8)
    for flier in fliers.values():
        if flier.state == 'INITIALIZED':
            summary[0] += 1
        elif flier.state == 'OVIPOSITION':
            summary[1] += 1
        elif flier.state == 'READY':
            summary[2] += 1
        elif flier.state == 'LIFTOFF':
            summary[3] += 1
        elif flier.state == 'FLIGHT':
            summary[4] += 1
        elif flier.state in ['LANDING_T', 'LANDING_P', 'LANDING_S']:
            summary[5] += 1
        elif flier.state in ['CRASH', 'HOST', 'FOREST', 'NONFOREST']:
            summary[6] += 1
        elif flier.state in ['SPENT', 'SPLASHED', 'EXIT', 'MAXFLIGHTS', 'EXHAUSTED']:
            summary[7] += 1
    print('%s :   %d inactive' % (dt_str, summary[0]))
    print('%s :   %d laying eggs' % (dt_str, summary[1]))
    print('%s :   %d ready' % (dt_str, summary[2]))
    print('%s :   %d lifting off' % (dt_str, summary[3]))
    print('%s :   %d flying' % (dt_str, summary[4]))
    print('%s :   %d landing' % (dt_str, summary[5]))
    print('%s :   %d landed' % (dt_str, summary[6]))
    print('%s :   %d lost' % (dt_str, summary[7]))
    print('%s :   %d total' % (dt_str, sum(summary)))
    return


def report_flier_locations(sim, radar, locations, date_time):
    """Write location and motion of all Fliers as CSV."""
    location_df = pd.DataFrame.from_dict(locations, orient='index')
    columns = ['lat', 'lon', 'alt_AGL', 'alt_MSL', 'GpH',
               'UTM_zone', 'easting', 'northing',
               'v_x', 'v_y', 'v_z', 'v_r', 'v_a']
    location_df.columns = columns
    dt_str = str(date_time.isoformat())
    if sim.experiment_number:
        outfname = '%s_simulation_%s_%s_summary/locs_%s_%s_%s.csv' % \
            (sim.simulation_name, str(sim.experiment_number).zfill(2),
             str(sim.simulation_number).zfill(5), dt_str,
             str(sim.experiment_number).zfill(2),
             str(sim.simulation_number).zfill(5))
    else:
        outfname = '%s_simulation_%s_summary/locs_%s_%s.csv' % \
            (sim.simulation_name, str(sim.simulation_number).zfill(5),
             dt_str, str(sim.simulation_number).zfill(5))
    location_df.to_csv(outfname)
    print('%s UTC : wrote %s' % (dt_str, outfname.split('/')[-1]))
    if sim.use_radar and sim.npy_grids:
        grid_flier_locations(sim, radar, locations, date_time)
        grid_flier_dvels(sim, radar, locations, date_time)
    return


def get_time_mean_stdv(vals):
    """Find the mean for list of datatime objects."""
    min_val = min(vals)
    deltas = [(start - min_val).seconds for start in vals]
    mean_delta = np.round(np.mean(deltas), 0)
    mean_val = min_val + timedelta(seconds=mean_delta)
    stdv_val = np.std(deltas) / 60.0
    return mean_val, stdv_val  # datetime object + float


def report_time_stats(outf, sum_str, vals):
    """Report stats for list of datetime objects."""
    if len(vals):
        min_val = min(vals)
        outf.write('    min = %s UTC \n' % min_val.isoformat())
        sum_str += min_val.isoformat() + ','
        mean_val, stdv_val = get_time_mean_stdv(vals)
        outf.write('    mean = %s UTC \n' % mean_val.isoformat())
        sum_str += mean_val.isoformat() + ','
        outf.write('    stdv = %.1f mins \n' % stdv_val)
        sum_str += '%.1f,' % stdv_val
        max_val = max(vals)
        outf.write('    max = %s UTC \n' % max_val.isoformat())
        sum_str += max_val.isoformat() + ','
    else:
        outf.write('    min = None\n')
        outf.write('    mean = None\n')
        outf.write('    stdv = None\n')
        outf.write('    max = None\n')
        sum_str += '0,0,0,0,'
    return sum_str


def report_stats(outf, sum_str, vals, units):
    """Report stats for list of float values."""
    if len(vals):
        min_val = np.min(vals)
        outf.write('    min = %.1f %s \n' % (min_val, units))
        sum_str += '%.1f,' % min_val
        mean_val = np.mean(vals)
        outf.write('    mean = %.1f %s \n' % (mean_val, units))
        sum_str += '%.1f,' % mean_val
        stdv_val = np.std(vals)
        outf.write('    stdv = %.1f %s \n' % (stdv_val, units))
        sum_str += '%.1f,' % stdv_val
        max_val = np.max(vals)
        outf.write('    max = %.1f %s \n' % (max_val, units))
        sum_str += '%.1f,' % max_val
    else:
        outf.write('    min = None\n')
        outf.write('    mean = None\n')
        outf.write('    stdv = None\n')
        outf.write('    max = None\n')
        sum_str += '0.0,0.0,0.0,0.0,'
    return sum_str


def report_mean(outf, sum_str, vals, label, units):
    """Report mean value for list of float values."""
    if len(vals):
        mean_val = np.mean(vals)
        outf.write('    %s = %.1f %s \n' % (label, mean_val, units))
        sum_str += '%.1f,' % mean_val
    else:
        outf.write('    %s = None \n' % label)
        sum_str += '0.0,'
    return sum_str


def report_mean_stdv(outf, sum_str, vals, label, units):
    """Report mean and stdv values for list of float values."""
    if len(vals):
        mean_val = np.mean(vals)
        outf.write('    %s mean = %.1f %s \n' % (label, mean_val, units))
        sum_str += '%.1f,' % mean_val
        stdv_val = np.std(vals)
        outf.write('    %s stdv = %.1f %s \n' % (label, stdv_val, units))
        sum_str += '%.1f,' % stdv_val
    else:
        outf.write('    %s mean = None \n' % label)
        outf.write('    %s stdv = None \n' % label)
        sum_str += '0.0,0.0,'
    return sum_str


def report_mean_stdv_pooled(outf, sum_str, mean_vals, stdv_vals, size_vals, label, units):
    """Report mean and stdv values for pooled lists of float values."""
    if len(mean_vals):
        sum_size = np.sum(size_vals)
        size_mean_vals = [(s * m) for s, m in zip(size_vals, mean_vals)]
        mean_val = np.sum(size_mean_vals) / sum_size
        outf.write('    %s mean = %.1f %s \n' % (label, mean_val, units))
        sum_str += '%.1f,' % mean_val
        var_vals = [(s**2) for s in stdv_vals]
        devs_sq = [(m - mean_val)**2 for m in mean_vals]
        var_devs_sq = [(v + dsq) for v, dsq in zip(var_vals, devs_sq)]
        size_var_devs_sq = [(s * v) for s, v in zip(size_vals, var_devs_sq)]
        var_val = np.sum(size_var_devs_sq) / sum_size
        stdv_val = np.sqrt(var_val)
        outf.write('    %s stdv = %.1f %s \n' % (label, stdv_val, units))
        sum_str += '%.1f,' % stdv_val
    else:
        outf.write('    %s mean = None \n' % label)
        outf.write('    %s stdv = None \n' % label)
        sum_str += '0.0,0.0,'
    return sum_str


def get_time_histogram(times, ref_time):
    """Get histogram of liftoff times."""
    min_time = 0       # minutes
    max_time = 7 * 60  # 7 hours from reference time, should be 2100 through 0400
    interval = 5       # minutes
    bins = range(min_time, max_time+interval, interval)
    nbins = len(bins)
    if len(times):
        time_deltas = [(start_time - ref_time).seconds for start_time in times]
        deltas_mins = [d / 60.0 for d in time_deltas]
        counts, bins = np.histogram(deltas_mins, bins=bins)
    else:
        counts = np.zeros((nbins-1), dtype=int)
    return counts, bins


def get_dist_histogram(dists):
    """Get histogram of flight distances."""
    min_dist = 0    # km
    max_dist = 600  # km
    interval = 5    # km
    bins = range(min_dist, max_dist+interval, interval)
    nbins = len(bins)
    if len(dists):
        counts, bins = np.histogram(dists, bins=bins)
    else:
        counts = np.zeros((nbins-1), dtype=int)
    return counts, bins


def get_horizontal_speed_histogram(speeds):
    """Get histogram of horizontal flight speeds."""
    min_speed = -5.0  # m/s
    max_speed = 5.0   # m/s
    interval = 0.1    # m/s
    bins = np.arange(min_speed, max_speed+interval, interval)
    nbins = len(bins)
    if len(speeds):
        counts, bins = np.histogram(speeds, bins=bins)
    else:
        counts = np.zeros((nbins-1), dtype=int)
    return counts, bins


def get_liftoff_speed_histogram(speeds):
    """Get histogram of liftoff (horizontal and vertical) flight speeds."""
    min_speed = 0.0  # m/s
    max_speed = 2.0  # m/s
    interval = 0.1   # m/s
    bins = np.arange(min_speed, max_speed+interval, interval)
    nbins = len(bins)
    if len(speeds):
        counts, bins = np.histogram(speeds, bins=bins)
    else:
        counts = np.zeros((nbins-1), dtype=int)
    return counts, bins


def get_alt_histogram(alts):
    """Get histogram of flight altitudes."""
    min_alt = 0     # meters
    max_alt = 2000  # meters
    interval = 20   # meters
    bins = range(min_alt, max_alt+interval, interval)
    nbins = len(bins)
    if len(alts):
        counts, bins = np.histogram(alts, bins=bins)
    else:
        counts = np.zeros((nbins-1), dtype=int)
    return counts, bins


def get_time_stats_histogram(outf, sum_str, var, df, ref_datetime):
    times = [iso8601.parse_date(d) for d in list(df[var])]
    sum_str = report_time_stats(outf, sum_str, times)
    time_counts, time_bins = get_time_histogram(times, ref_datetime)
    return sum_str, [time_counts, time_bins]


def get_speed_stats_histogram(outf, sum_str, var, df, label, units):
    vals = list(df[var])
    sum_str = report_mean_stdv(outf, sum_str, vals, label, units)
    counts, bins = get_liftoff_speed_histogram(vals)
    return sum_str, [counts, bins]


def report_liftoff_stats(outf, sum_str, liftoff_locs, ref_datetime):
    """Report liftoff-oriented statistics across all Fliers in simulation."""
    #
    liftoff_df = pd.DataFrame.from_dict(liftoff_locs, orient='index')
    liftoff_df.columns = ['latitude', 'longitude', 'UTM_zone', 'easting', 'northing',
                          'sfc_elev', 'lc_type', 'defoliation', 'sex', 'M', 'A',
                          'AMratio', 'F', 'nu', 'nu_L', 'liftoff_time', 'sunset_time',
                          'T_ref', 't_0', 't_c', 't_m', 'circadian_p', 'v_h', 'v_z',
                          'T', 'P', 'U', 'V', 'W']
    sunset_times = [iso8601.parse_date(d) for d in list(liftoff_df['sunset_time'])]
    outf.write('sunset: \n')
    sum_str = report_time_stats(outf, sum_str, sunset_times)
    outf.write('\n')
    #
    T_refs = np.array(liftoff_df['T_ref'])
    outf.write('reference T: \n')
    sum_str = report_stats(outf, sum_str, T_refs, 'ºC')
    outf.write('\n')
    #
    liftoff_df_female = liftoff_df[liftoff_df['sex'] == 1]
    liftoff_df_male = liftoff_df[liftoff_df['sex'] == 0]
    histograms = list()
    #
    var = 'liftoff_time'
    outf.write('overall flight start: \n')
    sum_str, liftoff_times_histo = get_time_stats_histogram(outf, sum_str, var,
                                                            liftoff_df, ref_datetime)
    histograms.append(liftoff_times_histo)
    outf.write('\n')
    outf.write('female flight start: \n')
    sum_str, liftoff_times_histo = get_time_stats_histogram(outf, sum_str, var,
                                                            liftoff_df_female, ref_datetime)
    histograms.append(liftoff_times_histo)
    outf.write('\n')
    outf.write('male flight start: \n')
    sum_str, liftoff_times_histo = get_time_stats_histogram(outf, sum_str, var,
                                                            liftoff_df_male, ref_datetime)
    histograms.append(liftoff_times_histo)
    outf.write('\n')
    #
    var = 'v_z'
    outf.write('liftoff vertical speed: \n')
    sum_str, liftoff_v_z_histo = get_speed_stats_histogram(outf, sum_str, var,
                                                           liftoff_df, 'overall', 'm/s')
    histograms.append(liftoff_v_z_histo)
    sum_str, liftoff_v_z_histo = get_speed_stats_histogram(outf, sum_str, var,
                                                           liftoff_df_female, 'female', 'm/s')
    histograms.append(liftoff_v_z_histo)
    sum_str, liftoff_v_z_histo = get_speed_stats_histogram(outf, sum_str, var,
                                                           liftoff_df_male, 'male', 'm/s')
    histograms.append(liftoff_v_z_histo)
    outf.write('\n')
    #
    var = 'v_h'
    outf.write('liftoff horizontal speed: \n')
    sum_str, liftoff_v_h_histo = get_speed_stats_histogram(outf, sum_str, var,
                                                           liftoff_df, 'overall', 'm/s')
    histograms.append(liftoff_v_h_histo)
    sum_str, liftoff_v_h_histo = get_speed_stats_histogram(outf, sum_str, var,
                                                           liftoff_df_female, 'female', 'm/s')
    histograms.append(liftoff_v_h_histo)
    sum_str, liftoff_v_h_histo = get_speed_stats_histogram(outf, sum_str, var,
                                                           liftoff_df_male, 'male', 'm/s')
    histograms.append(liftoff_v_h_histo)
    outf.write('\n')
    #
    return sum_str, histograms  # 1 str + 1 list of lists of lists


def report_flier_statistics(sim, all_fliers_flight_status, liftoff_locations):
    """Calculate and report various statistics across all Fliers in simulation."""
    #
    n_fliers_male = 0
    n_fliers_female = 0
    n_nonfliers_male = 0
    n_nonfliers_female = 0
    flight_start = list()
    flight_start_male = list()
    flight_start_female = list()
    flight_duration = list()
    flight_duration_male = list()
    flight_duration_female = list()
    flight_dist = list()
    flight_dist_male = list()
    flight_dist_female = list()
    flight_meanspeed = list()
    flight_meanspeed_male = list()
    flight_meanspeed_female = list()
    flight_meanairspeed = list()
    flight_stdvairspeed = list()
    flight_sizeairspeed = list()
    flight_meanairspeed_male = list()
    flight_stdvairspeed_male = list()
    flight_sizeairspeed_male = list()
    flight_meanairspeed_female = list()
    flight_stdvairspeed_female = list()
    flight_sizeairspeed_female = list()
    flight_meanwind = list()
    flight_meanAGL = list()
    flight_meanAGL_male = list()
    flight_meanAGL_female = list()
    flight_maxAGL = list()
    flight_maxAGL_male = list()
    flight_maxAGL_female = list()
    flight_maxAMSL = list()
    flight_maxAMSL_male = list()
    flight_maxAMSL_female = list()
    #
    # put each flier's status data into a DataFrame for ease of processing
    for flight_status in all_fliers_flight_status.values():
        status_df = pd.DataFrame.from_dict(flight_status, orient='index')
        if sim.full_physics:
            columns = ['flight_status', 'date_time', 'prev_state', 'state',
                       'northing', 'easting', 'UTM_zone', 'lat', 'lon', 'sfc_elev',
                       'alt_AGL', 'alt_MSL', 'defoliation', 'sex', 'M', 'A', 'F_0',
                       'F', 'gravidity', 'nu', 'nu_L', 'weight', 'lift', 'drag',
                       'thrust', 'body_angle', 'a_x', 'a_y', 'a_z', 'v_x', 'v_y',
                       'v_z', 'v_r', 'v_a', 'bearing', 'range', 'P', 'T', 'Precip',
                       'GpH', 'U', 'V', 'W']
        else:
            columns = ['flight_status', 'date_time', 'prev_state', 'state',
                       'northing', 'easting', 'UTM_zone', 'lat', 'lon', 'sfc_elev',
                       'alt_AGL', 'alt_MSL', 'defoliation', 'sex', 'M', 'A', 'F_0',
                       'F', 'gravidity', 'nu', 'nu_L', 'v_h', 'v_x', 'v_y', 'v_z',
                       'v_r', 'v_a', 'bearing', 'range', 'P', 'T', 'Precip', 'GpH',
                       'U', 'V', 'W']
        status_df.columns = columns
        status_df = status_df.sort_values(by=['date_time'])
        #
        date_time_all = [iso8601.parse_date(d) for d in list(status_df['date_time'])]
        sfc_all = np.array(status_df['sfc_elev'])
        alt_all = np.array(status_df['alt_MSL'])
        alt_AGL = alt_all - sfc_all
        female = list(status_df['sex'])[0]
        if np.sum(alt_AGL) == 0:
            if female:
                n_nonfliers_female += 1
            else:
                n_nonfliers_male += 1
        else:
            if female:
                n_fliers_female += 1
            else:
                n_fliers_male += 1
            idx1 = 0
            for idx, alt in enumerate(alt_AGL):
                if alt > 0.0:
                    idx1 = idx - 1
                    break
            start_datetime = date_time_all[idx1]
            flight_start.append(start_datetime)
            if female:
                flight_start_female.append(start_datetime)
            else:
                flight_start_male.append(start_datetime)
            idx2 = -1
            if alt_AGL[-1] > 0.0:
                idx2 = len(alt_AGL) - 1
            else:
                for idx in range(len(alt_AGL)-1, -1, -1):
                    if alt_AGL[idx] > 0.0:
                        idx2 = idx + 1
                        break
            end_datetime = date_time_all[idx2]
            duration = end_datetime - start_datetime
            flight_duration.append(duration.seconds / 60.0)
            if female:
                flight_duration_female.append(duration.seconds / 60.0)
            else:
                flight_duration_male.append(duration.seconds / 60.0)
            dist = np.array(status_df['range'])[idx2]
            flight_dist.append(dist / 1000.0)
            if female:
                flight_dist_female.append(dist / 1000.0)
            else:
                flight_dist_male.append(dist / 1000.0)
            flight_meanspeed.append(dist / duration.seconds)
            if female:
                flight_meanspeed_female.append(dist / duration.seconds)
            else:
                flight_meanspeed_male.append(dist / duration.seconds)
            v_h = np.array(status_df['v_h'])[idx1:idx2]
            flight_meanairspeed.append(np.mean(v_h))
            flight_stdvairspeed.append(np.std(v_h))
            flight_sizeairspeed.append(len(v_h))
            if female:
                flight_meanairspeed_female.append(np.mean(v_h))
                flight_stdvairspeed_female.append(np.std(v_h))
                flight_sizeairspeed_female.append(len(v_h))
            else:
                flight_meanairspeed_male.append(np.mean(v_h))
                flight_stdvairspeed_male.append(np.std(v_h))
                flight_sizeairspeed_male.append(len(v_h))
            U = np.array(status_df['U'])[idx1:idx2]
            V = np.array(status_df['V'])[idx1:idx2]
            flight_meanwind.append(np.mean(np.sqrt(U**2 + V**2)))
            flight_meanAGL.append(np.mean(alt_AGL[idx1:idx2]))
            if female:
                flight_meanAGL_female.append(np.mean(alt_AGL[idx1:idx2]))
            else:
                flight_meanAGL_male.append(np.mean(alt_AGL[idx1:idx2]))
            flight_maxAGL.append(np.max(alt_AGL[idx1:idx2]))
            if female:
                flight_maxAGL_female.append(np.max(alt_AGL[idx1:idx2]))
            else:
                flight_maxAGL_male.append(np.max(alt_AGL[idx1:idx2]))
            flight_maxAMSL.append(np.max(alt_all[idx1:idx2]))
            if female:
                flight_maxAMSL_female.append(np.max(alt_all[idx1:idx2]))
            else:
                flight_maxAMSL_male.append(np.max(alt_all[idx1:idx2]))
    #
    if sim.experiment_number:
        outfname = '%s_simulation_%s_%s_summary/%s_%s_%s_flights_summary.txt' % \
            (sim.simulation_name, str(sim.experiment_number).zfill(2),
             str(sim.simulation_number).zfill(5), sim.simulation_name,
             str(sim.experiment_number).zfill(2), str(sim.simulation_number).zfill(5))
    else:
        outfname = '%s_simulation_%s_summary/%s_%s_flights_summary.txt' % \
            (sim.simulation_name, str(sim.simulation_number).zfill(5), sim.simulation_name,
             str(sim.simulation_number).zfill(5))
    #
    with open(outfname, 'w') as outfile:
        if sim.experiment_number == 0:
            outfile.write('simulation %s output\n' % str(sim.simulation_number).zfill(5))
            summary_string = 'simulation_%s,' % str(sim.simulation_number).zfill(5)
        else:
            outfile.write('simulation %s_%s output\n' % (str(sim.experiment_number).zfill(2),
                                                         str(sim.simulation_number).zfill(5)))
            summary_string = 'simulation_%s_%s,' % (str(sim.experiment_number).zfill(2),
                                                    str(sim.simulation_number).zfill(5))
        outfile.write('\n')
        outfile.write('summarizing %d viable flight reports \n' % sim.n_fliers)
        outfile.write('\n')
        #
        n_female_total = n_nonfliers_female + n_fliers_female
        n_male_total = n_nonfliers_male + n_fliers_male
        n_nonfliers_total = n_nonfliers_male + n_nonfliers_female
        n_fliers_total = n_fliers_male + n_fliers_female
        #
        outfile.write('total moths: %d \n' % sim.n_fliers)
        outfile.write('    female = %d \n' % n_female_total)
        outfile.write('    male = %d \n' % n_male_total)
        summary_string += '%d,%d,%d,' % (sim.n_fliers, n_female_total, n_male_total)
        outfile.write('\n')
        #
        outfile.write('non-fliers: %d \n' % n_nonfliers_total)
        outfile.write('    female = %d \n' % n_nonfliers_female)
        outfile.write('    male = %d \n' % n_nonfliers_male)
        summary_string += '%d,%d,%d,' % (n_nonfliers_total, n_nonfliers_female, n_nonfliers_male)
        outfile.write('\n')
        #
        outfile.write('fliers: %d \n' % n_fliers_total)
        outfile.write('    female = %d \n' % n_fliers_female)
        outfile.write('    male = %d \n' % n_fliers_male)
        summary_string += '%d,%d,%d,' % (n_fliers_total, n_fliers_female, n_fliers_male)
        outfile.write('\n')
        #
        summary_string, histograms = \
            report_liftoff_stats(outfile, summary_string, liftoff_locations, sim.start_time)
        liftoff_time_counts, liftoff_time_bins = histograms[0]
        liftoff_time_counts_female, liftoff_time_bins_female = histograms[1]
        liftoff_time_counts_male, liftoff_time_bins_male = histograms[2]
        liftoff_v_z_counts, liftoff_v_z_bins = histograms[3]
        liftoff_v_z_counts_female, liftoff_v_z_bins_female = histograms[4]
        liftoff_v_z_counts_male, liftoff_v_z_bins_male = histograms[5]
        liftoff_v_h_counts, liftoff_v_h_bins = histograms[6]
        liftoff_v_h_counts_female, liftoff_v_h_bins_female = histograms[7]
        liftoff_v_h_counts_male, liftoff_v_h_bins_male = histograms[8]
        #
        outfile.write('overall flight duration: \n')
        summary_string = report_stats(outfile, summary_string, flight_duration, 'mins')
        outfile.write('\n')
        #
        outfile.write('female flight duration: \n')
        summary_string = report_stats(outfile, summary_string, flight_duration_female, 'mins')
        outfile.write('\n')
        #
        outfile.write('male flight duration: \n')
        summary_string = report_stats(outfile, summary_string, flight_duration_male, 'mins')
        outfile.write('\n')
        #
        outfile.write('overall flight distance: \n')
        summary_string = report_stats(outfile, summary_string, flight_dist, 'km')
        flight_dist_counts, flight_dist_bins = get_dist_histogram(flight_dist)
        outfile.write('\n')
        #
        outfile.write('female flight distance: \n')
        summary_string = report_stats(outfile, summary_string, flight_dist_female, 'km')
        flight_dist_counts_female, flight_dist_bins_female = \
            get_dist_histogram(flight_dist_female)
        outfile.write('\n')
        #
        outfile.write('male flight distance: \n')
        summary_string = report_stats(outfile, summary_string, flight_dist_male, 'km')
        flight_dist_counts_male, flight_dist_bins_male = \
            get_dist_histogram(flight_dist_male)
        outfile.write('\n')
        #
        outfile.write('flight speed: \n')
        summary_string = report_mean_stdv(outfile, summary_string, flight_meanspeed,
                                          'overall', 'm/s')
        summary_string = report_mean_stdv(outfile, summary_string, flight_meanspeed_female,
                                          'female', 'm/s')
        summary_string = report_mean_stdv(outfile, summary_string, flight_meanspeed_male,
                                          'male', 'm/s')
        outfile.write('\n')
        #
        if flight_meanwind:
            overall_flight_meanwind = np.mean(flight_meanwind)
            outfile.write('mean wind speed = %.1f m/s \n' % overall_flight_meanwind)
            summary_string += '%.1f,' % overall_flight_meanwind
        else:
            outfile.write('mean wind speed = None \n')
            summary_string += '0.0,'
        outfile.write('\n')
        #
        outfile.write('flight airspeed: \n')
        summary_string = report_mean_stdv_pooled(outfile, summary_string,
                                                 flight_meanairspeed,
                                                 flight_stdvairspeed,
                                                 flight_sizeairspeed,
                                                 'overall', 'm/s')
        flight_airspeed_counts, flight_airspeed_bins = \
            get_horizontal_speed_histogram(flight_meanairspeed)
        summary_string = report_mean_stdv_pooled(outfile, summary_string,
                                                 flight_meanairspeed_female,
                                                 flight_stdvairspeed_female,
                                                 flight_sizeairspeed_female,
                                                 'female', 'm/s')
        flight_airspeed_counts_female, flight_airspeed_bins_female = \
            get_horizontal_speed_histogram(flight_meanairspeed_female)
        summary_string = report_mean_stdv_pooled(outfile, summary_string,
                                                 flight_meanairspeed_male,
                                                 flight_stdvairspeed_male,
                                                 flight_sizeairspeed_male,
                                                 'male', 'm/s')
        flight_airspeed_counts_male, flight_airspeed_bins_male = \
            get_horizontal_speed_histogram(flight_meanairspeed_male)
        outfile.write('\n')
        #
        outfile.write('flight altitude AGL: \n')
        summary_string = report_mean_stdv(outfile, summary_string, flight_meanAGL,
                                          'overall', 'm')
        flight_alt_counts, flight_alt_bins = get_alt_histogram(flight_meanAGL)
        summary_string = report_mean_stdv(outfile, summary_string, flight_meanAGL_female,
                                          'female', 'm')
        flight_alt_counts_female, flight_alt_bins_female = \
            get_alt_histogram(flight_meanAGL_female)
        summary_string = report_mean_stdv(outfile, summary_string, flight_meanAGL_male,
                                          'male', 'm')
        flight_alt_counts_male, flight_alt_bins_male = \
            get_alt_histogram(flight_meanAGL_male)
        outfile.write('\n')
        #
        outfile.write('max flight altitude AGL: \n')
        summary_string = report_mean_stdv(outfile, summary_string, flight_maxAGL,
                                          'overall', 'm')
        summary_string = report_mean_stdv(outfile, summary_string, flight_maxAGL_female,
                                          'female', 'm')
        summary_string = report_mean_stdv(outfile, summary_string, flight_maxAGL_male,
                                          'male', 'm')
        outfile.write('\n')
        #
        outfile.write('max flight altitude AMSL: \n')
        summary_string = report_mean_stdv(outfile, summary_string, flight_maxAMSL,
                                          'overall', 'm')
        summary_string = report_mean_stdv(outfile, summary_string, flight_maxAMSL_female,
                                          'female', 'm')
        summary_string = report_mean_stdv(outfile, summary_string, flight_maxAMSL_male,
                                          'male', 'm')
        outfile.write('\n')
        #
        outfile.write('diagnostic information strings follow: \n')
        outfile.write('\n')
        outfile.write(summary_string + '\n')
        outfile.write(','.join([str(x) for x in liftoff_time_bins]) + '\n')
        outfile.write(','.join([str(x) for x in liftoff_time_counts]) + '\n')
        outfile.write(','.join([str(x) for x in liftoff_time_bins_female]) + '\n')
        outfile.write(','.join([str(x) for x in liftoff_time_counts_female]) + '\n')
        outfile.write(','.join([str(x) for x in liftoff_time_bins_male]) + '\n')
        outfile.write(','.join([str(x) for x in liftoff_time_counts_male]) + '\n')
        outfile.write(','.join(['%.1f' % x for x in liftoff_v_z_bins]) + '\n')
        outfile.write(','.join([str(x) for x in liftoff_v_z_counts]) + '\n')
        outfile.write(','.join(['%.1f' % x for x in liftoff_v_z_bins_female]) + '\n')
        outfile.write(','.join([str(x) for x in liftoff_v_z_counts_female]) + '\n')
        outfile.write(','.join(['%.1f' % x for x in liftoff_v_z_bins_male]) + '\n')
        outfile.write(','.join([str(x) for x in liftoff_v_z_counts_male]) + '\n')
        outfile.write(','.join(['%.1f' % x for x in liftoff_v_h_bins]) + '\n')
        outfile.write(','.join([str(x) for x in liftoff_v_h_counts]) + '\n')
        outfile.write(','.join(['%.1f' % x for x in liftoff_v_h_bins_female]) + '\n')
        outfile.write(','.join([str(x) for x in liftoff_v_h_counts_female]) + '\n')
        outfile.write(','.join(['%.1f' % x for x in liftoff_v_h_bins_male]) + '\n')
        outfile.write(','.join([str(x) for x in liftoff_v_h_counts_male]) + '\n')
        outfile.write(','.join([str(x) for x in flight_dist_bins]) + '\n')
        outfile.write(','.join([str(x) for x in flight_dist_counts]) + '\n')
        outfile.write(','.join([str(x) for x in flight_dist_bins_female]) + '\n')
        outfile.write(','.join([str(x) for x in flight_dist_counts_female]) + '\n')
        outfile.write(','.join([str(x) for x in flight_dist_bins_male]) + '\n')
        outfile.write(','.join([str(x) for x in flight_dist_counts_male]) + '\n')
        outfile.write(','.join(['%.1f' % x for x in flight_airspeed_bins]) + '\n')
        outfile.write(','.join([str(x) for x in flight_airspeed_counts]) + '\n')
        outfile.write(','.join(['%.1f' % x for x in flight_airspeed_bins_female]) + '\n')
        outfile.write(','.join([str(x) for x in flight_airspeed_counts_female]) + '\n')
        outfile.write(','.join(['%.1f' % x for x in flight_airspeed_bins_male]) + '\n')
        outfile.write(','.join([str(x) for x in flight_airspeed_counts_male]) + '\n')
        outfile.write(','.join([str(x) for x in flight_alt_bins]) + '\n')
        outfile.write(','.join([str(x) for x in flight_alt_counts]) + '\n')
        outfile.write(','.join([str(x) for x in flight_alt_bins_female]) + '\n')
        outfile.write(','.join([str(x) for x in flight_alt_counts_female]) + '\n')
        outfile.write(','.join([str(x) for x in flight_alt_bins_male]) + '\n')
        outfile.write(','.join([str(x) for x in flight_alt_counts_male]) + '\n')
    print('simulation wrapup : wrote %s' % outfname.split('/')[-1])
    return


def plot_trajectories(sim, next_wrf_grids, trajectories):
    """Generate topo plot with all flight trajectories."""
    if sim.experiment_number:
        outfname = '%s_simulation_%s_%s_summary/%s_%s_%s_flights_topo_map.png' % \
                (sim.simulation_name, str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5), sim.simulation_name,
                 str(sim.experiment_number).zfill(2), str(sim.simulation_number).zfill(5))
    else:
        outfname = '%s_simulation_%s_summary/%s_%s_flights_topo_map.png' % \
                (sim.simulation_name, str(sim.simulation_number).zfill(5),
                 sim.simulation_name, str(sim.simulation_number).zfill(5))
    plot_all_flights(sim, next_wrf_grids, trajectories, outfname)
    print('simulation wrapup : wrote %s' % outfname.split('/')[-1])
    return

# end Flier_summary.py
