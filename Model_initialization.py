# pylint: disable=C0103,R0912,R0913,R0914,R0915,R1711
"""
Python script "Model_initialization.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2019-2021 by Matthew Garcia
"""


import numpy as np
from WRFgrids_class import WRFgrids
from Geography import setup_topo_map, setup_lc_map, setup_defoliation_map
from Radar_class import Radar
from Flier_class import Flier
from Flier_setup import read_flier_locations_attributes
from Flier_setup import generate_flier_locations, generate_flier_attributes
from Flier_setup import calc_circadian_from_WRF_T, assign_circadian
from Flier_summary import summarize_locations
from Solar_calculations import update_suntimes


def command_line_args(sim, args):
    """Process command line arguments.
       TO DO: convert to argparse usage."""
    if len(args) > 2:
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
            if var_name == 'wingbeat_eff':
                print('initial setup : ignoring %s value' % var_name)
                print('initial setup : (change sim.flight_speed if you want to use it)')
        if sim.flight_speed == 'param':
            if var_name in ['w_horizontal', 'w_alpha']:
                print('initial setup : ignoring %s value' % var_name)
                print('initial setup : (change sim.flight_speed if you want to use it)')
            if var_name == 'wingbeat_eff':
                sim.wingbeat_eff = var_value
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


def load_initial_WRF_grids(sim):
    """Load initial WRF grids."""
    last_time = sim.start_time
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


def setup_fliers(sim, sbw, last_wrf_grids, topography, landcover, defoliation):
    """Initialize and define collection of fliers."""
    if sim.use_defoliation:
        # assign flier locations and attributes using defoliation map and empirical eqns
        print('initial setup : assigning defoliation-based flier locations and attributes')
        flier_locations = generate_flier_locations(last_wrf_grids, landcover, defoliation)
        flier_attributes = generate_flier_attributes(sbw, flier_locations)
    else:
        # read flier locations and attributes from BioSIM output CSV file
        print('initial setup : obtaining BioSIM output flier locations and attributes')
        flier_locations, flier_attributes = read_flier_locations_attributes(sim)
    #
    # select n_fliers from available pool
    n_fliers_available = len(flier_locations)
    selected_fliers = np.random.randint(low=0, high=n_fliers_available, size=sim.n_fliers)
    #
    # initialize individual Flier objects
    print('initial setup : initializing %d Fliers' % sim.n_fliers)
    fliers = dict()
    for f, f_available_idx in enumerate(selected_fliers):
        flier_idx = sim.simulation_number * sim.n_fliers * 10 + f
        flier_id = '%d%s%s_%s' % (sim.start_time.year, str(sim.start_time.month).zfill(2),
                                  str(sim.start_time.day).zfill(2), str(flier_idx).zfill(9))
        fliers[flier_id] = Flier(sim, sbw, flier_id, flier_locations[f_available_idx],
                                 flier_attributes[f_available_idx])
        update_suntimes(sim, fliers[flier_id])
    n_female = sum(flier.sex for flier in fliers.values())
    n_male = sim.n_fliers - n_female
    print('initial setup : %d Flier objects initialized (%d F, %d M)' %
            (sim.n_fliers, n_female, n_male))
    #
    # summarize flier locations
    flier_locations = summarize_locations(fliers, 'initial setup')
    #
    # calculate/assign flier circadian attributes
    if sim.calculate_circadian_from_WRF:
        calc_circadian_from_WRF_T(sim, sbw, fliers, flier_locations,
                                  topography, landcover)
    else:
        assign_circadian(sim, sbw, fliers)
    return fliers  # dict

# end Model_initialization.py
