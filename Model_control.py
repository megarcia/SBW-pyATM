# pylint: disable=C0103,R0912,R0913,R0914,R0915,R1711
"""
Python script "Model_control.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2019, 2020 by Matthew Garcia
"""


import sys
from message_fn import message
from Simulation_specifications import Simulation
from SBW_empirical import SBW
from Model_initialization import command_line_args, setup_fliers
from Model_initialization import load_initial_WRF_grids, setup_maps, setup_radar
from Temporal_operations import advance_clock, count_active_fliers, remove_fliers
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
    message()
    message('initial setup : all imports loaded successfully')
    #
    sim = Simulation()
    message('initial setup : Simulation object initialized')
    message('initial setup : simulation name is %s' % sim.simulation_name)
    #
    command_line_args(sim, sys.argv)
    #
    sbw = SBW()
    message('initial setup : SBW empirical object initialized')
    #
    # simulation start/end times
    message('initial setup : specified start time %s UTC' % str(sim.start_time.isoformat()))
    message('initial setup : specified end time %s UTC' % str(sim.end_time.isoformat()))
    message('initial setup : specified internal time step %d sec' % sim.dt)
    #
    # simulation use of WRF output
    message('initial setup : using WRF file path %s' % sim.WRF_input_path)
    message('initial setup : specified WRF grid %s' % sim.WRF_grid)
    message('initial setup : specified WRF input interval %d min' % sim.WRF_input_interval)
    #
    # load initial WRF grids
    last_wrf_time, last_wrf_grids = load_initial_WRF_grids(sim)
    #
    # initialize map objects as provided
    topography, landcover, defoliation = setup_maps(sim)
    #
    # initialize radar object as provided
    radar = setup_radar(sim)
    #
    # initialize and define collection of fliers
    all_fliers = setup_fliers(sim, sbw, last_wrf_grids, topography,
                              landcover, defoliation)
    #
    # summarize flier locations
    flier_locations = summarize_locations(all_fliers, 'initial setup')
    #
    # set up various data structures
    all_fliers_flight_status = dict()
    trajectories = dict()
    liftoff_locations = dict()
    landing_locations = dict()
    egg_deposition = dict()
    dt_str = '%s UTC' % str(sim.start_time.isoformat())
    #
    # get flier initial environment variables
    flier_environments_last = \
        query_flier_environments(sim, last_wrf_time, last_wrf_grids,
                                 flier_locations, topography, landcover, dt_str)
    update_flier_environments(all_fliers, flier_environments_last, dt_str)
    update_flier_status(sim, all_fliers, sim.start_time)
    #
    # write out flier location and motion summary
    flier_locations = summarize_motion(all_fliers, flier_locations)
    report_flier_locations(sim, radar, flier_locations, sim.start_time)
    #
    # pre-load next WRF grids
    next_wrf_time, next_wrf_grids = load_next_WRF_grids(sim, sim.start_time, dt_str)
    flier_environments_next = \
        query_flier_environments(sim, next_wrf_time, next_wrf_grids,
                                 flier_locations, topography, landcover, dt_str)
    #
    # simulation time steps
    message('%s : starting model time steps' % dt_str)
    date_time = advance_clock(sim, sim.start_time)  # datetime object in UTC
    message()
    #
    # *** temporal loop begins here ***
    #
    while date_time <= sim.end_time:  # datetime objects in UTC
        dt_str = '%s UTC' % str(date_time.isoformat())
        #
        # if 5h elapsed and no active fliers left, break simulation
        if end_sim_no_flights(sim, all_fliers, date_time, dt_str):
            break
        #
        # shuffle and update WRF grids if needed
        wrf_grids_updated = False
        if date_time > next_wrf_time:  # datetime objects in UTC
            last_wrf_time, last_wrf_grids, next_wrf_time, next_wrf_grids = \
                shuffle_WRF_grids(sim, next_wrf_time, next_wrf_grids, dt_str)
            wrf_grids_updated = True
        #
        # update and summarize all active flier locations
        n_moving_fliers = update_flier_locations(sim, all_fliers, dt_str)
        flier_locations = summarize_locations(all_fliers, dt_str)
        #
        # update flier environments
        if date_time == next_wrf_time:  # datetime objects in UTC
            if n_moving_fliers or wrf_grids_updated:
                flier_environments_next = \
                    query_flier_environments(sim, next_wrf_time, next_wrf_grids,
                                             flier_locations, topography, landcover,
                                             dt_str)
            update_flier_environments(all_fliers, flier_environments_next, dt_str)
        else:
            if n_moving_fliers or wrf_grids_updated:
                flier_environments_last = \
                    query_flier_environments(sim, last_wrf_time, last_wrf_grids,
                                             flier_locations, topography, landcover,
                                             dt_str)
                flier_environments_next = \
                    query_flier_environments(sim, next_wrf_time, next_wrf_grids,
                                             flier_locations, topography, landcover,
                                             dt_str)
            interpolate_flier_environments(all_fliers, flier_environments_last,
                                           flier_environments_next, last_wrf_time,
                                           next_wrf_time, date_time)
        #
        # write out flier location and motion summary
        flier_locations = summarize_motion(all_fliers, flier_locations)
        report_flier_locations(sim, radar, flier_locations, date_time)
        #
        # loop through all_fliers, update state as needed and append to status record
        liftoff_locations, landing_locations, to_remove = \
            update_flier_states(sim, sbw, defoliation, radar, all_fliers, date_time,
                                liftoff_locations, landing_locations, dt_str)
        #
        # diagnostic summary of flier activity
        summarize_activity(all_fliers, dt_str)
        #
        # remove lost/dead fliers
        if to_remove:
            all_fliers, all_fliers_flight_status, trajectories, egg_deposition = \
                remove_fliers(sim, all_fliers, date_time, all_fliers_flight_status,
                              trajectories, egg_deposition, to_remove, dt_str)
        #
        # advance simulation clock
        if date_time < sim.end_time:  # datetime objects in UTC
            date_time = advance_clock(sim, date_time)  # datetime object in UTC
        else:
            message('%s : end of simulation, wrapping up' % dt_str)
            break
        message()
    #
    # *** temporal loop ends here ***
    #
    # end-of-simulation report on remaining activity
    n_active_fliers = count_active_fliers(sim, all_fliers, dt_str, output=False)
    message('%s : simulation ended with %d active fliers (of %d specified)' %
            (dt_str, n_active_fliers, sim.n_fliers))
    message()
    if n_active_fliers:
        trajectories, egg_deposition = \
            report_remaining_fliers(sim, all_fliers, trajectories, egg_deposition)
    #
    # end-of-simulation flight statistics, trajectories, location reports, grids
    report_statistics(sim, all_fliers_flight_status, liftoff_locations)
    report_trajectories(sim, next_wrf_grids, trajectories)
    report_summary_grids(sim, liftoff_locations, landing_locations, egg_deposition)
    #
    message()
    message('simulation %s completed' % sim.simulation_name)
    return


if __name__ == '__main__':
    ATM_main()

# end Model_control.py
