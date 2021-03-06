# pylint: disable=C0103,R0912,R0913,R0914,R0915,R1711
"""
Python script "Model_initialization.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


import numpy as np
from WRFgrids_class import WRFgrids
from Map_class import setup_topo_map, setup_lc_map, setup_defoliation_map
from Radar_class import Radar
from Flier_class import Flier
from Flier_setup import read_survivor_locations_attributes
from Flier_setup import read_flier_locations_attributes
from Flier_setup import generate_flier_locations, generate_flier_attributes
from Circadian_calculations import calc_circadian_from_WRF_T, assign_circadian
from Flier_summary import summarize_locations
from Solar_calculations import update_suntimes


def command_line_args(sim, args):
    """Process command line arguments.
       TO DO: convert to argparse usage."""
    sim.sequential = False
    sim.sequential_prev_fname = None
    sim.sequential_use_prev_survivors = False
    if len(args) > 2:
        if args[2] == 'seq':
            print('initial setup : simulation number %s in experiment collection' %
                  args[1].zfill(5))
            sim.simulation_number = int(args[1])
            sim.sequential = True
            print('initial setup : simulations in sequential date mode')
            print('initial setup : list of simulation surviving moths will be generated')
            if len(args) == 4:
                sim.sequential_use_prev_survivors = True
                sim.sequential_prev_fname = '%s_survivor_attributes.csv' % args[3]
                print('initial setup : using previous survivor moths from %s' %
                      sim.sequential_prev_fname)
        else:
            print('initial setup : experiment number %s' % args[1])
            sim.experiment_number = int(args[1])
            var_name = args[2]
            var_value = float(args[3])
            if var_name == 'max_precip':
                sim.max_precip = var_value
                print('initial setup : using %s = %.2f' % (var_name, var_value))
            if var_name == 'min_windspeed':
                sim.min_windspeed = var_value
                print('initial setup : using %s = %.2f' % (var_name, var_value))
            if sim.flight_speed == 'const':
                if var_name == 'w_horizontal':
                    sim.w_horizontal = var_value
                    print('initial setup : using %s = %.2f' % (var_name, var_value))
                if var_name == 'w_alpha':
                    sim.w_alpha = var_value
                    print('initial setup : using %s = %.2f' % (var_name, var_value))
                if var_name == 'wingbeat_coeff':
                    print('initial setup : ignoring %s value' % var_name)
                    print('initial setup : (change sim.flight_speed if you want to use it)')
            if sim.flight_speed == 'param':
                if var_name in ['w_horizontal', 'w_alpha']:
                    print('initial setup : ignoring %s value' % var_name)
                    print('initial setup : (change sim.flight_speed if you want to use it)')
                if var_name == 'wingbeat_coeff':
                    sim.wingbeat_coeff = var_value
                    print('initial setup : using %s = %.2f' % (var_name, var_value))
            if var_name == 'delta_nu':
                sim.delta_nu = var_value
                print('initial setup : using %s = %.2f' % (var_name, var_value))
            print('initial setup : simulation number %s in experiment collection' %
                  args[4].zfill(5))
            sim.simulation_number = int(args[4])
    else:
        print('initial setup : using default values for all parameters')
        print('initial setup : simulation number %s in experiment collection' %
              args[1].zfill(5))
        sim.simulation_number = int(args[1])
    return


def load_initial_WRF_grids(sim, clock):
    """Load initial WRF grids."""
    last_time = clock.start_dt
    last_grids = WRFgrids(last_time, sim.WRF_input_path, sim.WRF_grid, 'initial setup')
    print('initial setup : WRF %s grids object initialized' % str(last_time.isoformat()))
    return last_time, last_grids  # datetime + WRFgrids objects


def setup_maps(sim):
    """initialize topography, landcover, defoliation map objects as provided."""
    topography = setup_topo_map(sim)
    landcover = setup_lc_map(sim)
    defoliation = setup_defoliation_map(sim)
    return topography, landcover, defoliation  # 3 * Map object


def setup_radar(sim):
    """Initialize radar object as indicated.
       TO-DO: expand to allow multiple radars."""
    if sim.use_radar:
        radar = Radar(sim)
        print('initial setup : radar location %s initialized' % sim.radar_name)
    else:
        radar = None
    return radar  # Map object


def setup_fliers(sim, clock, sbw, last_wrf_grids, topography, landcover, defoliation):
    """Initialize and define collection of fliers."""
    if sim.use_defoliation:
        # assign flier locations and attributes using defoliation map and empirical eqns
        print('initial setup : assigning defoliation-based flier locations and attributes')
        flier_locations = generate_flier_locations(last_wrf_grids, landcover, defoliation)
        flier_attributes = generate_flier_attributes(sbw, flier_locations)
    else:
        if sim.sequential_use_prev_survivors:
            # read survivor locations and attributes from specified previous output CSV file
            print('initial setup : obtaining surviving flier locations and attributes')
            survivors_df = read_survivor_locations_attributes(sim, clock)
        else:
            survivors_df = None
        # read flier locations and attributes from BioSIM output CSV file
        print('initial setup : obtaining BioSIM output flier locations and attributes')
        flier_locations, flier_attributes = \
            read_flier_locations_attributes(sim, clock, survivors_df)
    #
    # select n_fliers from available pool
    n_fliers_available = len(flier_locations)
    if n_fliers_available > sim.n_fliers:
        selected_fliers = np.random.randint(low=0, high=n_fliers_available, size=sim.n_fliers)
    else:
        selected_fliers = list(range(n_fliers_available))
    sim.n_fliers = len(selected_fliers)
    #
    # initialize individual Flier objects
    print('initial setup : initializing %d Fliers' % sim.n_fliers)
    fliers = dict()
    for f, f_available_idx in enumerate(selected_fliers):
        flier_idx = sim.simulation_number * sim.n_fliers * 10 + f
        flier_id = '%d%s%s_%s' % (sim.start_year, str(sim.start_month).zfill(2),
                                  str(sim.start_day).zfill(2), str(flier_idx).zfill(9))
        fliers[flier_id] = Flier(sim, sbw, flier_id, flier_locations[f_available_idx],
                                 flier_attributes[f_available_idx])
        update_suntimes(clock, fliers[flier_id])
    n_female = sum(flier.sex for flier in fliers.values())
    n_male = sim.n_fliers - n_female
    print('initial setup : %d Flier objects initialized (%d F, %d M)' %
          (sim.n_fliers, n_female, n_male))
    #
    # summarize flier locations
    flier_locations = summarize_locations(clock, fliers)
    #
    # calculate/assign flier circadian attributes
    if sim.calculate_circadian_from_WRF:
        calc_circadian_from_WRF_T(sim, sbw, fliers, flier_locations,
                                  topography, landcover)
    else:
        assign_circadian(sim, sbw, fliers)
    return fliers, flier_locations  # 2 * dict

# end Model_initialization.py
