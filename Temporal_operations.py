# pylint: disable=C0103,R0912,R0913,R0914,R0915,R1711
"""
Python script "Temporal_operations.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2019-2021 by Matthew Garcia
"""


import copy
from datetime import timedelta
from message_fn import message
from WRFgrids_class import WRFgrids
from Interpolate import interpolate_time


def advance_clock(sim, date_time):
    """Advance simulation time by dt, in seconds.
       Input and output are datetime objects in UTC."""
    dt_str = '%s UTC' % str(date_time.isoformat())
    message('%s : advancing clock, dt = %d seconds' % (dt_str, sim.dt))
    date_time_new = date_time + timedelta(seconds=sim.dt)
    return date_time_new  # datetime object


def count_active_fliers(sim, fliers, dt_str, output=True):
    """Report count of active fliers in simulation."""
    n_active = sum(flier.active for flier in fliers.values())
    if output:
        message('%s : %d active fliers (of %d specified)' %
                (dt_str, n_active, sim.n_fliers))
    return n_active  # int


def end_sim_no_flights(sim, fliers, date_time, dt_str):
    """If no flights occur by 5 hours into simulation, end simulation."""
    end_sim = False
    elapsed_time = date_time - sim.start_time  # timedelta/datetime objects in UTC
    if elapsed_time.seconds >= (5 * 60 * 60):
        n_active = count_active_fliers(sim, fliers, dt_str, output=False)
        if not n_active:
            message('%s : no active fliers remain' % dt_str)
            message('%s : ending simulation' % dt_str)
            end_sim = True
    return end_sim  # bool


def end_sim_no_fliers(fliers, dt_str):
    """If no flier objects remain, end simulation."""
    end_sim = False
    n_fliers = 0
    for flier in fliers.values():
        if flier.state in ['LIFTOFF', 'FLIGHT', 'LANDING_S', 'LANDING_W',
                           'LANDING_T', 'LANDING_P', 'SUNRISE', 'SPENT',
                           'SPLASHED', 'EXIT', 'MAXFLIGHTS', 'EXHAUSTED']:
            n_fliers += 1
    if not n_fliers:
        message('%s : no fliers remain' % dt_str)
        message('%s : ending simulation' % dt_str)
        end_sim = True
    return end_sim  # bool


def query_flier_environments(sim, wrf_time, wrf_grids, flier_locations,
                             topography, landcover, dt_str):
    """Get environmental variables for all fliers."""
    message('%s : querying flier environments using %s WRF grids' %
            (dt_str, str(wrf_time.isoformat())))
    flier_environments = \
        wrf_grids.get_flier_environments(sim, flier_locations,
                                         topography, landcover)
    return flier_environments  # dict


def update_flier_environments(fliers, environments, dt_str):
    """Update flier accounts of environmental variables."""
    message('%s : updating flier environments' % dt_str)
    for flier_id, flier in fliers.items():
        env = environments[flier_id]
        flier.update_environment(env[3:])
    return


def interpolate_flier_environments(fliers, environments_last, environments_next,
                                   last_wrf_time, next_wrf_time, date_time):
    """Interpolate between two sets of WRF grids for flier environments."""
    message('%s UTC : interpolating flier environments' % str(date_time.isoformat()))
    for flier_id, flier in fliers.items():
        last_env = environments_last[flier_id]
        next_env = environments_next[flier_id]
        flier_env = list()
        flier_env.append(last_env[3])  # surface elevation
        flier_env.append(last_env[4])  # landcover index
        for i in range(5, 11):
            flier_env.append(interpolate_time(last_env[i], last_wrf_time,
                                              next_env[i], next_wrf_time,
                                              date_time))
        flier.update_environment(flier_env)
    return


def update_flier_locations(sim, fliers, dt_str):
    """Update locations of all fliers (using flier motion)."""
    message('%s : updating flier locations' % dt_str)
    n_moving = 0
    for flier in fliers.values():
        if flier.active:
            flier.update_location(sim)
            if flier.state in ['LIFTOFF', 'FLIGHT', 'LANDING_S',
                               'LANDING_W', 'LANDING_T', 'LANDING_P']:
                n_moving += 1
    return n_moving  # int


def update_flier_states(sim, sbw, defoliation, radar, fliers, date_time,
                        liftoff_locs, landing_locs, dt_str):
    """Update operating states of all fliers."""
    message('%s : updating states of active fliers' % dt_str)
    to_remove = list()
    for flier_id, flier in fliers.items():
        remove, liftoff_locs, landing_locs = \
            flier.state_decisions(sim, sbw, defoliation, radar, date_time,
                                  liftoff_locs, landing_locs)
        if remove:
            message('%s : flier %s indicated for removal' %
                    (dt_str, flier.flier_id))
            to_remove.append(flier_id)
    return liftoff_locs, landing_locs, to_remove  # 2 * dict + list


def update_flier_status(sim, fliers, date_time):
    """Update status accounts for all fliers."""
    for flier in fliers.values():
        flier.update_status(sim, date_time)
    return


def remove_fliers(sim, fliers, date_time, flight_status,
                  trajectories, egg_deposition, to_remove, dt_str):
    """Remove lost/dead fliers (record egg deposition history first)."""
    for flier_id in to_remove:
        flier = fliers[flier_id]
        flight_status[flier_id] = flier.flight_status
        trajectories = flier.report_status(sim, trajectories, date_time)
        if flier.sex and flier.eggs_laid:
            for eggs_id, egg_location in flier.eggs_laid.items():
                egg_deposition[eggs_id] = egg_location
        del fliers[flier_id]
        message('%s : removed %s Flier object' % (dt_str, flier_id))
    return fliers, flight_status, trajectories, egg_deposition  # 4 * dict


def load_next_WRF_grids(sim, date_time, dt_str):
    """Load next WRF grids in temporal sequence."""
    next_time = date_time + timedelta(minutes=sim.WRF_input_interval)
    next_grids = WRFgrids(next_time, sim.WRF_input_path, sim.WRF_grid, dt_str)
    message('%s : WRF %s grids object initialized' % (dt_str, str(next_time.isoformat())))
    return next_time, next_grids  # datetime + WRFgrids objects


def shuffle_WRF_grids(sim, next_time, next_grids, dt_str):
    """Shuffle next WRF grids to last, load new grids."""
    message('%s : updating WRF grids' % dt_str)
    last_time = copy.deepcopy(next_time)  # datetime objects in UTC
    last_grids = copy.deepcopy(next_grids)  # WRFgrids object
    next_time, next_grids = load_next_WRF_grids(sim, last_time, dt_str)
    return last_time, last_grids, next_time, next_grids  # 2 * (datetime + WRFgrids objects)

# end Temporal_operations.py
