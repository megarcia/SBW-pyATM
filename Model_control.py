# pylint: disable=C0103,R0912,R0913,R0914,R0915,R1711
"""
Python script "Model_control.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


import sys
from Simulation_specifications import Simulation
from Clock import Clock
from SBW_empirical import SBW
from Model_initialization import command_line_args, setup_fliers
from Model_initialization import load_initial_WRF_grids, setup_maps, setup_radar
from Oviposition_calculations import oviposition
from Temporal_operations import count_active_fliers, remove_fliers
from Temporal_operations import end_sim_no_flights
from Temporal_operations import update_flier_states, update_flier_status
from Temporal_operations import query_flier_environments, interpolate_flier_environments
from Temporal_operations import update_flier_locations, update_flier_environments
from Temporal_operations import load_next_WRF_grids, shuffle_WRF_grids
from Flier_summary import summarize_locations, report_flier_locations
from Flier_summary import summarize_motion, summarize_activity
from Model_wrapup import report_remaining_fliers, report_statistics
from Model_wrapup import report_trajectories, report_summary_grids


def ATM_main():
    """Simulation initialization and loop control."""
    print()
    print('initial setup : all imports loaded successfully')
    #
    sim = Simulation()
    print('initial setup : Simulation object initialized')
    print('initial setup : simulation name is %s' % sim.simulation_name)
    #
    clock = Clock(sim)
    print('initial setup : simulation clock initialized')
    print('initial setup : simulation start datetime is %s' % clock.start_dt_str)
    print('initial setup : simulation end datetime is %s' % clock.end_dt_str)
    print('initial setup : simulation time step is %s seconds' % clock.dt_interval)
    #
    # process any command-line arguments (e.g. changed parameter values)
    command_line_args(sim, sys.argv)
    #
    # get SBW empirical data and calculations
    sbw = SBW()
    print('initial setup : SBW empirical object initialized')
    #
    # simulation use of WRF output
    print('initial setup : using WRF file path %s' % sim.WRF_input_path)
    print('initial setup : specified WRF grid %s' % sim.WRF_grid)
    print('initial setup : specified WRF input interval %d min' % sim.WRF_input_interval)
    #
    # load initial WRF grids
    last_wrf_time, last_wrf_grids = load_initial_WRF_grids(sim, clock)
    #
    # initialize map objects as provided
    topography, landcover, defoliation = setup_maps(sim)
    #
    # initialize radar object as provided
    radar = setup_radar(sim)
    #
    # initialize and define collection of fliers
    all_fliers, flier_locations = setup_fliers(sim, clock, sbw, last_wrf_grids,
                                               topography, landcover, defoliation)
    #
    # set up various data structures
    all_fliers_flight_status = dict()
    trajectories = dict()
    liftoff_locations = dict()
    landing_locations = dict()
    egg_deposition = dict()
    #
    # get flier initial environment variables
    flier_environments_last = \
        query_flier_environments(sim, clock, last_wrf_time, last_wrf_grids,
                                 flier_locations, topography, landcover)
    update_flier_environments(clock, all_fliers, flier_environments_last)
    update_flier_status(clock, all_fliers)
    #
    # write out flier location and motion summary
    flier_locations = summarize_motion(all_fliers, flier_locations)
    report_flier_locations(sim, clock, radar, flier_locations)
    #
    # pre-load next WRF grids
    next_wrf_time, next_wrf_grids = load_next_WRF_grids(sim, clock)
    flier_environments_next = \
        query_flier_environments(sim, clock, next_wrf_time, next_wrf_grids,
                                 flier_locations, topography, landcover)
    #
    # natal site oviposition
    oviposition(sim, sbw, all_fliers)
    #
    # simulation time steps
    print('%s : starting model time steps' % clock.start_dt_str)
    clock.advance_clock()
    print()
    #
    # *** temporal loop begins here ***
    #
    while clock.current_dt <= clock.end_dt:  # datetime objects in UTC
        #
        # if 5h elapsed and no active fliers left, break simulation
        if end_sim_no_flights(sim, clock, all_fliers):
            break
        #
        # shuffle and update WRF grids if needed
        wrf_grids_updated = False
        if clock.current_dt == next_wrf_time:  # datetime objects in UTC
            last_wrf_time, last_wrf_grids, next_wrf_time, next_wrf_grids = \
                shuffle_WRF_grids(sim, clock, next_wrf_time, next_wrf_grids)
            wrf_grids_updated = True
        #
        # update and summarize all active flier locations
        n_moving_fliers = update_flier_locations(clock, all_fliers)
        flier_locations = summarize_locations(clock, all_fliers)
        #
        # update flier environments
        if clock.current_dt == next_wrf_time:  # datetime objects in UTC
            if n_moving_fliers or wrf_grids_updated:
                flier_environments_next = \
                    query_flier_environments(sim, clock, next_wrf_time, next_wrf_grids,
                                             flier_locations, topography, landcover)
            update_flier_environments(clock, all_fliers, flier_environments_next)
        else:
            if n_moving_fliers or wrf_grids_updated:
                flier_environments_last = \
                    query_flier_environments(sim, clock, last_wrf_time, last_wrf_grids,
                                             flier_locations, topography, landcover)
                flier_environments_next = \
                    query_flier_environments(sim, clock, next_wrf_time, next_wrf_grids,
                                             flier_locations, topography, landcover)
            interpolate_flier_environments(clock, all_fliers, flier_environments_last,
                                           flier_environments_next, last_wrf_time,
                                           next_wrf_time)
        #
        # write out flier location and motion summary
        flier_locations = summarize_motion(all_fliers, flier_locations)
        report_flier_locations(sim, clock, radar, flier_locations)
        #
        # loop through all_fliers, update state as needed and append to status record
        liftoff_locations, landing_locations, to_remove = \
            update_flier_states(sim, clock, sbw, defoliation, radar, all_fliers,
                                liftoff_locations, landing_locations)
        #
        # diagnostic summary of flier activity
        summarize_activity(clock, all_fliers)
        #
        # remove lost/dead fliers
        if to_remove:
            all_fliers, all_fliers_flight_status, trajectories, egg_deposition = \
                remove_fliers(sim, clock, all_fliers, all_fliers_flight_status,
                              trajectories, egg_deposition, to_remove)
        #
        # advance simulation clock
        if clock.current_dt < clock.end_dt:  # datetime objects in UTC
            clock.advance_clock()
        else:
            print('%s : end of simulation, wrapping up' % clock.current_dt_str)
            break
        print()
    #
    # *** temporal loop ends here ***
    #
    # end-of-simulation report on remaining activity
    n_active_fliers = count_active_fliers(sim, clock, all_fliers, output=False)
    print('%s : simulation ended with %d active fliers (of %d specified)' %
          (clock.current_dt_str, n_active_fliers, sim.n_fliers))
    print()
    if n_active_fliers:
        trajectories, egg_deposition = \
            report_remaining_fliers(sim, clock, all_fliers, trajectories, egg_deposition)
    #
    # end-of-simulation flight statistics, trajectories, location reports, grids
    report_statistics(sim, clock, all_fliers_flight_status, liftoff_locations)
    report_trajectories(sim, next_wrf_grids, trajectories)
    report_summary_grids(sim, liftoff_locations, landing_locations, egg_deposition)
    #
    print()
    print('simulation %s completed' % sim.simulation_name)
    return


if __name__ == '__main__':
    ATM_main()

# end Model_control.py
