from datetime import datetime, timedelta, timezone as tz
import numpy as np
from Solar_calculations import Sun


circadian_p1_mean = -3.8  # [h]
circadian_p1_stdv = 0.7  # [h]
circadian_p2_mean = 0.145  # [h/C]
circadian_p2_stdv = 0.031  # [h/C]
circadian_p3_mean = -1.267  # [h]
circadian_p3_stdv = 0.146  # [h]
circadian_p4_mean = -0.397  # [-]
circadian_p4_stdv = 0.187  # [-]
circadian_p5_mean = -2.465  # [-]
circadian_p5_stdv = 0.152  # [-]
circadian_kf_mean = 1.35  # [-]
circadian_kf_stdv = 0.025  # [-]


def calc_circadian_deltas(T_ref):
    """Regniere et al. [2019]."""
    circadian_p1 = np.random.normal(loc=circadian_p1_mean, scale=circadian_p1_stdv)
    circadian_p2 = np.random.normal(loc=circadian_p2_mean, scale=circadian_p2_stdv)
    circadian_p3 = np.random.normal(loc=circadian_p3_mean, scale=circadian_p3_stdv)
    circadian_p4 = np.random.normal(loc=circadian_p4_mean, scale=circadian_p4_stdv)
    circadian_p5 = np.random.normal(loc=circadian_p5_mean, scale=circadian_p5_stdv)
    circadian_kf = np.random.normal(loc=circadian_kf_mean, scale=circadian_kf_stdv)
    delta_s = circadian_p1 + circadian_p2 * T_ref
    delta_0 = circadian_p3 + circadian_p4 * delta_s
    delta_f = circadian_p5 * delta_0
    delta_f_potential = circadian_kf * delta_f
    return delta_s, delta_0, delta_f, delta_f_potential  # 4 * float


def update_suntimes(lat, lon, UTC_offset, start_time):
    """Update sunset/sunrise times based on location."""
    sun = Sun(lat=lat, lon=lon, UTC_offset=UTC_offset)
    local_sunset_time = sun.sunset(when=start_time) + timedelta(hours=UTC_offset)
    utc_sunset_time = local_sunset_time - timedelta(hours=UTC_offset)
    utc_sunset_time = utc_sunset_time.replace(tzinfo=tz.utc)
    return local_sunset_time, utc_sunset_time


def initialize_circadian_attributes(delta_s, delta_0, delta_f,
                                    delta_f_potential, local_sunset_time):
    """Calculate liftoff circadian rhythm offsets and times; Regniere et al. [2019]"""
    local_t_c = local_sunset_time + timedelta(hours=delta_s)
    local_t_0 = local_t_c + timedelta(hours=delta_0)
    if delta_f_potential:
        local_t_m = local_t_0 + timedelta(hours=delta_f_potential)
    else:
        local_t_m = local_t_0 + timedelta(hours=delta_f)
    utc_t_c = local_t_c - timedelta(hours=UTC_offset)
    utc_t_c = utc_t_c.replace(tzinfo=tz.utc)
    utc_t_0 = local_t_0 - timedelta(hours=UTC_offset)
    utc_t_0 = utc_t_0.replace(tzinfo=tz.utc)
    utc_t_m = local_t_m - timedelta(hours=UTC_offset)
    utc_t_m = utc_t_m.replace(tzinfo=tz.utc)
    return utc_t_0, utc_t_c, utc_t_m


def calc_circadian_p(date_time, utc_t_0, utc_t_c, utc_t_m):
    """Regniere et al. [2019]; date_time is an offset-aware datetime object in UTC."""
    C = 1.0 - (2.0 / 3.0) + (1.0 / 5.0)
    if date_time < utc_t_0:
        circadian_p = 0.0
    elif date_time > utc_t_m:
        circadian_p = 1.0
    else:
        if date_time <= utc_t_c:
            num_t_diff = utc_t_c - date_time
            tau_num = -1 * num_t_diff.seconds / 3600.0
            denom_t_diff = utc_t_c - utc_t_0
        else:
            num_t_diff = date_time - utc_t_c
            tau_num = num_t_diff.seconds / 3600.0
            denom_t_diff = utc_t_m - utc_t_c
        tau_denom = denom_t_diff.seconds / 3600.0
        # print('    tau_num = %.3f' % tau_num)
        # print('    tau_denom = %.3f' % tau_denom)
        tau = tau_num / tau_denom
        # print('    tau = %.3f' % tau)
        term2 = (2.0 / 3.0) * tau**3
        term3 = (1.0 / 5.0) * tau**5
        circadian_p = (C + tau - term2 + term3) / (2 * C)
    return circadian_p


print()
flier_lat = 49.0851
flier_lon = -72.6678
flier_T_ref = 25.3166
UTC_offset = -4.0
start_time = datetime(2013, 7, 15, 21, 0, 0, tzinfo=tz.utc)
end_time = datetime(2013, 7, 16, 10, 0, 0, tzinfo=tz.utc)
dt = 120
#
print('Flier location:')
print('lat = %.4f' % flier_lat)
print('lon = %.4f' % flier_lon)
print()
local_sunset_time, utc_sunset_time = update_suntimes(flier_lat, flier_lon, UTC_offset,
                                                     start_time)
print('sunset = %s EDT' % local_sunset_time)
print('sunset = %s UTC' % utc_sunset_time)
print()
#
delta_s, delta_0, delta_f, delta_f_potential = calc_circadian_deltas(flier_T_ref)
print('delta_s = %.2f h' % delta_s)
print('delta_0 = %.2f h' % delta_0)
print('delta_f = %.2f h' % delta_f)
print('delta_f_potential = %.2f h' % delta_f_potential)
print()
#
utc_t_0, utc_t_c, utc_t_m = initialize_circadian_attributes(delta_s, delta_0, delta_f,
                                                            delta_f_potential,
                                                            local_sunset_time)
print('t_0 = %s UTC' % utc_t_0)
print('t_c = %s UTC' % utc_t_c)
print('t_m = %s UTC' % utc_t_m)
print()
#
date_time = start_time
while date_time <= end_time:
    circadian_p = calc_circadian_p(date_time, utc_t_0, utc_t_c, utc_t_m)
    print('%s : circadian_p = %.3f' % (date_time, circadian_p))
    date_time = date_time + timedelta(seconds=dt)
print()
