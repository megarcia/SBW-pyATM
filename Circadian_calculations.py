# pylint: disable=C0103,R0205,R0902,R0914,R0915,R1711
"""
Python script "Circadian_calculations.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


from datetime import datetime, timedelta
from datetime import timezone as tz
import numpy as np
from Interpolation import interpolate_time
from WRFgrids_class import check_for_WRF_file, WRFgrids


def calc_circadian_deltas(sbw, T_ref):
    """Regniere et al. [2019]."""
    circadian_p1 = np.random.normal(loc=sbw.circadian['p1_mean'],
                                    scale=sbw.circadian['p1_stdv'])
    circadian_p2 = np.random.normal(loc=sbw.circadian['p2_mean'],
                                    scale=sbw.circadian['p2_stdv'])
    circadian_p3 = np.random.normal(loc=sbw.circadian['p3_mean'],
                                    scale=sbw.circadian['p3_stdv'])
    circadian_p4 = np.random.normal(loc=sbw.circadian['p4_mean'],
                                    scale=sbw.circadian['p4_stdv'])
    circadian_p5 = np.random.normal(loc=sbw.circadian['p5_mean'],
                                    scale=sbw.circadian['p5_stdv'])
    circadian_kf = np.random.normal(loc=sbw.circadian['kf_mean'],
                                    scale=sbw.circadian['kf_stdv'])
    delta_s = circadian_p1 + circadian_p2 * T_ref
    delta_0 = circadian_p3 + circadian_p4 * delta_s
    delta_f = circadian_p5 * delta_0
    delta_f_potential = circadian_kf * delta_f
    deltas = [delta_s, delta_0, delta_f, delta_f_potential]
    return deltas  # list of 4 * float


def initialize_circadian_attributes(sim, sbw, flier):
    """Calculate liftoff circadian rhythm offsets and times; Regniere et al. [2019]"""
    if sim.calculate_circadian_from_WRF:
        deltas = calc_circadian_deltas(sbw, flier.circadian_T_ref)
        flier.circadian_delta_s = deltas[0]
        flier.circadian_delta_0 = deltas[1]
        flier.circadian_delta_f = deltas[2]
        flier.circadian_delta_f_potential = deltas[3]
    else:
        flier.circadian_delta_s = sbw.circadian['delta_s']
        flier.circadian_delta_0 = 0.5 * sbw.circadian['delta_f']
        flier.circadian_delta_f = sbw.circadian['delta_f']
        flier.circadian_delta_f_potential = 0.0
    flier.local_t_c = \
        flier.local_sunset_time + timedelta(hours=flier.circadian_delta_s)
    flier.local_t_0 = \
        flier.local_t_c + timedelta(hours=flier.circadian_delta_0)
    if flier.circadian_delta_f_potential:
        flier.local_t_m = \
            flier.local_t_0 + timedelta(hours=flier.circadian_delta_f_potential)
    else:
        flier.local_t_m = \
            flier.local_t_0 + timedelta(hours=flier.circadian_delta_f)
    flier.utc_t_c = flier.local_t_c - timedelta(hours=sim.UTC_offset)
    flier.utc_t_c = flier.utc_t_c.replace(tzinfo=tz.utc)
    flier.utc_t_0 = flier.local_t_0 - timedelta(hours=sim.UTC_offset)
    flier.utc_t_0 = flier.utc_t_0.replace(tzinfo=tz.utc)
    flier.utc_t_m = flier.local_t_m - timedelta(hours=sim.UTC_offset)
    flier.utc_t_m = flier.utc_t_m.replace(tzinfo=tz.utc)
    return


def get_flier_environments(sim, locations, topography, landcover, ref_time):
    """Get WRF-based environments of all Fliers."""
    dt_str = 'initial setup'
    grids = WRFgrids(ref_time, sim.WRF_input_path, sim.WRF_grid, dt_str)
    print('%s : WRF %s grids object initialized' %
          (dt_str, str(ref_time.isoformat())))
    print('%s : querying potential flier environments' % dt_str)
    flier_environments = \
        grids.get_flier_environments(sim, locations, topography, landcover)
    return flier_environments


def calc_circadian_from_WRF_T(sim, sbw, fliers, locations, topography, landcover):
    """Calculate flier circadian attributes using WRF-based temperatures."""
    dt_str = 'initial setup'
    print('%s : calculating flier circadian attributes' % dt_str)
    circadian_ref_hh = int(sbw.circadian['ref_time'])
    circadian_ref_mm = int(60 * (sbw.circadian['ref_time'] - circadian_ref_hh))
    local_circadian_ref_time = datetime(sim.start_year, sim.start_month, sim.start_day,
                                        circadian_ref_hh, circadian_ref_mm, 0)
    circadian_ref_time = local_circadian_ref_time - timedelta(hours=sim.UTC_offset)  # UTC
    print('%s : circadian reference time %s UTC' %
          (dt_str, str(circadian_ref_time.isoformat())))
    file_exists, _ = check_for_WRF_file(circadian_ref_time, sim.WRF_input_path, sim.WRF_grid)
    if file_exists:
        flier_environments = get_flier_environments(sim, locations, topography, landcover,
                                                    circadian_ref_time)
        print('%s : updating flier circadian reference temperatures' % dt_str)
        for flier_id, flier in fliers.items():
            flier.circadian_T_ref = flier_environments[flier_id][5]
    else:
        circadian_ref_mm1 = (circadian_ref_mm // sim.WRF_input_interval) * sim.WRF_input_interval
        local_circadian_ref_time1 = datetime(sim.start_year, sim.start_month, sim.start_day,
                                             circadian_ref_hh, circadian_ref_mm1, 0)
        circadian_ref_time1 = local_circadian_ref_time1 - timedelta(hours=sim.UTC_offset)  # UTC
        flier_environments1 = get_flier_environments(sim, locations, topography, landcover,
                                                     circadian_ref_time1)
        circadian_ref_time2 = circadian_ref_time1 + timedelta(minutes=sim.WRF_input_interval)  # UTC
        flier_environments2 = get_flier_environments(sim, locations, topography, landcover,
                                                     circadian_ref_time2)
        print('%s : updating flier circadian reference temperatures' % dt_str)
        for flier_id, flier in fliers.items():
            flier.circadian_T_ref = \
                interpolate_time(flier_environments1[flier_id][5], circadian_ref_time1,
                                 flier_environments2[flier_id][5], circadian_ref_time2,
                                 circadian_ref_time)
    for flier in fliers.values():
        initialize_circadian_attributes(sim, sbw, flier)
    return


def assign_circadian(sim, sbw, fliers):
    """Assign flier circadian attributes with user-specified values."""
    print('initial setup : assigning specified flier circadian attributes')
    for flier in fliers.values():
        initialize_circadian_attributes(sim, sbw, flier)
    return


def calc_circadian_p(clock, flier):
    """Regniere et al. [2019]; clock contains an offset-aware datetime object in UTC."""
    C = 1.0 - (2.0 / 3.0) + (1.0 / 5.0)
    if clock.current_dt < flier.utc_t_0:
        flier.circadian_p = 0.0
    elif clock.current_dt > flier.utc_t_m:
        flier.circadian_p = 1.0
    else:
        if clock.current_dt <= flier.utc_t_c:
            num_t_diff = flier.utc_t_c - clock.current_dt
            tau_num = -1 * num_t_diff.seconds / 3600.0
            denom_t_diff = flier.utc_t_c - flier.utc_t_0
        else:
            num_t_diff = clock.current_dt - flier.utc_t_c
            tau_num = num_t_diff.seconds / 3600.0
            denom_t_diff = flier.utc_t_m - flier.utc_t_c
        tau_denom = denom_t_diff.seconds / 3600.0
        tau = tau_num / tau_denom
        term2 = (2.0 / 3.0) * tau**3
        term3 = (1.0 / 5.0) * tau**5
        flier.circadian_p = (C + tau - term2 + term3) / (2 * C)
    return

# end Circadian_calculations.py
