# pylint: disable=C0103,R0912,R0913,R0914,R0915,R1711
"""
Python script "Temporal_operations.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


import copy
from datetime import timedelta
from WRFgrids_class import WRFgrids
from Interpolate import interpolate_time
from Solar_calculations import update_suntimes


def count_active_fliers(sim, clock, fliers, output=True):
    """Report count of active fliers in simulation."""
    n_active = sum(flier.active for flier in fliers.values())
    if output:
        print('%s : %d active fliers (of %d specified)' %
              (clock.current_dt_str, n_active, sim.n_fliers))
    return n_active  # int


def end_sim_no_flights(sim, clock, fliers):
    """If no flights occur by 5 hours into simulation, end simulation."""
    end_sim = False
    if clock.elapsed_time.seconds >= (5 * 60 * 60):
        n_active = count_active_fliers(sim, clock, fliers, output=False)
        if not n_active:
            print('%s : no active fliers remain' % clock.current_dt_str)
            print('%s : ending simulation' % clock.current_dt_str)
            end_sim = True
    return end_sim  # bool


def end_sim_no_fliers(fliers, clock):
    """If no flier objects remain, end simulation."""
    end_sim = False
    n_fliers = 0
    for flier in fliers.values():
        if flier.state in ['LIFTOFF', 'FLIGHT', 'LANDING_S', 'LANDING_W',
                           'LANDING_T', 'LANDING_P', 'SUNRISE', 'SPENT',
                           'SPLASHED', 'EXIT', 'MAXFLIGHTS', 'EXHAUSTED']:
            n_fliers += 1
    if not n_fliers:
        print('%s : no fliers remain' % clock.current_dt_str)
        print('%s : ending simulation' % clock.current_dt_str)
        end_sim = True
    return end_sim  # bool


def query_flier_environments(sim, clock, wrf_time, wrf_grids, flier_locations,
                             topography, landcover):
    """Get environmental variables for all fliers."""
    print('%s : querying flier environments using %s WRF grids' %
          (clock.current_dt_str, str(wrf_time.isoformat())))
    flier_environments = \
        wrf_grids.get_flier_environments(sim, flier_locations,
                                         topography, landcover)
    return flier_environments  # dict


def update_flier_environments(clock, fliers, environments):
    """Update flier accounts of environmental variables."""
    print('%s : updating flier environments' % clock.current_dt_str)
    for flier_id, flier in fliers.items():
        env = environments[flier_id]
        flier.update_environment(env[3:])
    return


def interpolate_flier_environments(clock, fliers, environments_last,
                                   environments_next, last_wrf_time, next_wrf_time):
    """Interpolate between two sets of WRF grids for flier environments."""
    print('%s UTC : interpolating flier environments' % clock.current_dt_str)
    for flier_id, flier in fliers.items():
        last_env = environments_last[flier_id]
        next_env = environments_next[flier_id]
        flier_env = list()
        flier_env.append(last_env[3])  # surface elevation
        flier_env.append(last_env[4])  # landcover index
        for i in range(5, 11):
            flier_env.append(interpolate_time(last_env[i], last_wrf_time,
                                              next_env[i], next_wrf_time,
                                              clock.current_dt))
        flier.update_environment(flier_env)
    return


def update_flier_locations(clock, fliers):
    """Update locations of all fliers (using flier motion)."""
    print('%s : updating flier locations' % clock.current_dt_str)
    n_moving = 0
    for flier in fliers.values():
        if flier.active:
            flier.update_location(clock)
            update_suntimes(clock, flier)
            if flier.state in ['LIFTOFF', 'FLIGHT', 'LANDING_S',
                               'LANDING_W', 'LANDING_T', 'LANDING_P']:
                n_moving += 1
    return n_moving  # int


def update_flier_states(sim, clock, sbw, defoliation, radar, fliers,
                        liftoff_locs, landing_locs):
    """Update operating states of all fliers."""
    print('%s : updating states of active fliers' % clock.current_dt_str)
    to_remove = list()
    for flier_id, flier in fliers.items():
        remove, liftoff_locs, landing_locs = \
            flier.state_decisions(sim, sbw, defoliation, radar,
                                  liftoff_locs, landing_locs)
        if remove:
            print('%s : flier %s indicated for removal' %
                  (clock.current_dt_str, flier.flier_id))
            to_remove.append(flier_id)
    return liftoff_locs, landing_locs, to_remove  # 2 * dict + list


def update_flier_status(sim, clock, fliers):
    """Update status accounts for all fliers."""
    for flier in fliers.values():
        flier.update_status(sim, clock)
    return


def remove_fliers(sim, clock, fliers, flight_status, trajectories,
                  egg_deposition, to_remove):
    """Remove lost/dead fliers (record egg deposition history first)."""
    for flier_id in to_remove:
        flier = fliers[flier_id]
        flight_status[flier_id] = flier.flight_status
        trajectories = flier.report_status(sim, clock, trajectories)
        if flier.sex and flier.eggs_laid:
            for eggs_id, egg_location in flier.eggs_laid.items():
                egg_deposition[eggs_id] = egg_location
        del fliers[flier_id]
        print('%s : removed %s Flier object' % (clock.current_dt_str, flier_id))
    return fliers, flight_status, trajectories, egg_deposition  # 4 * dict


def load_next_WRF_grids(sim, clock):
    """Load next WRF grids in temporal sequence."""
    next_time = clock.current_dt + timedelta(minutes=sim.WRF_input_interval)
    next_grids = WRFgrids(clock, next_time, sim.WRF_input_path, sim.WRF_grid)
    print('%s : WRF %s grids object initialized' % (clock.current_dt_str,
                                                    str(next_time.isoformat())))
    return next_time, next_grids  # datetime + WRFgrids objects


def shuffle_WRF_grids(sim, clock, next_time, next_grids):
    """Shuffle next WRF grids to last, load new grids."""
    print('%s : updating WRF grids' % clock.current_dt_str)
    last_time = copy.deepcopy(next_time)  # datetime objects in UTC
    last_grids = copy.deepcopy(next_grids)  # WRFgrids object
    next_time, next_grids = load_next_WRF_grids(sim, clock)
    return last_time, last_grids, next_time, next_grids  # 2 * (datetime + WRFgrids objects)

# end Temporal_operations.py
