# pylint: disable=C0103,R0205,R0902,R0903,R0915
"""
Python script "Simulation_specifications_WRF-NARR_d03_20130715.py"
by Matthew Garcia, Post-doctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


from datetime import datetime, timezone as tz


class Simulation(object):
    """Declare simulation boundaries, settings, parameters, etc."""

    def __init__(self):
        #
        # simulation management
        self.simulation_name = 'WRF-NARR_d03_20130715'
        self.experiment_number = 0  # if there are multiple experiments, changed by user input
        self.simulation_number = 0  # if there are multiple simulations, changed by user input
        self.n_fliers = 1000        # recommended max 1000 per simulation
        self.full_physics = 0       # using parameterized flight physics (for now)
        #
        # simulation spatial domain
        self.grid_min_lat, self.grid_max_lat = 42.0415, 51.3277
        self.grid_min_lon, self.grid_max_lon = -80.1780, -53.2079
        self.grid_bounds = [self.grid_min_lat, self.grid_min_lon,
                            self.grid_max_lat, self.grid_max_lon]
        self.grid_UTM_zone = 19
        self.grid_dx, self.grid_dy = 1000.0, 1000.0  # [m]
        #
        # simulation times (in UTC)
        self.start_time = datetime(2013, 7, 15, 21, 0, 0, tzinfo=tz.utc)  # Y, M, D, h, m, s
        self.end_time = datetime(2013, 7, 16, 10, 0, 0, tzinfo=tz.utc)  # Y, M, D, h, m, s
        #
        # other simulation time specifications
        self.dt = 60                  # [s]
        self.UTC_offset = -4.0        # [h] --> Eastern Daylight Time
        #
        # ancillary maps
        self.topography_fname = 'WRF'  # 'WRF' or GeoTIFF file name
        self.landcover_fname = 'WRF'   # 'WRF' or GeoTIFF file name
        #
        # defoliation options: True requires defoliation_fname, False requires biosim_fname
        self.use_defoliation = False
        self.defoliation_fname = ''   # for flier setup, required if use_defoliation = True
        #
        # BioSIM-derived moth morphological information, if provided
        self.biosim_fname = '2013_BioSIM_SBW_output.csv'  # for now
        self.use_initial_flier_polygon = False
        self.init_flier_min_lat, self.init_flier_max_lat = 48.5, 50.5
        self.init_flier_min_lon, self.init_flier_max_lon = -70.0, -67.0
        #
        # WRF input options
        self.WRF_input_path = '%s_grids' % self.simulation_name
        self.WRF_grid = 'd03'
        self.WRF_input_interval = 60  # [min]
        # vinterp options: 'nearest', 'linear', 'quadratic' (splines), 'cubic' (splines), etc.
        self.WRF_vinterp = 'linear'
        # hinterp options: 'nearest', 'linear', 'cubic' (splines)
        self.WRF_hinterp = 'nearest'
        #
        # circadian options: True uses ref_time, False uses delta_s and delta_f
        self.calculate_circadian_from_WRF = True
        #
        # calibration flight parameters
        # maximum precipitation rate for liftoff
        self.max_precip = 2.5        # maximum precipitation rate before washout [mm/h]
        self.max_cloudlwc = 0.16     # maximum cloud liquid water content before washout [g/m3]
        # minimum wind speed for liftoff
        self.min_windspeed = 1.5     # minimum wind required for liftoff [m/s]
        # flight speed
        self.flight_speed = 'param'  # 'const' for constant flight speed, 'param' for parameterized
        self.w_horizontal = 2.0      # constant flight speed [m/s] from Greenbank et al. (1980)
        self.w_alpha = 0.11          # vertical flight speed conversion factor [m/s/Hz]
        self.wingbeat_eff = 1.58     # wingbeat efficiency for parameterization
        # energy conservation
        self.delta_nu = 1.0          # cruising altitude adjustment factor
        #
        # non-calibration flight parameters
        self.climb_decision_hgt = 60.0  # [m AGL] from Greenbank (1980)
        self.min_flight_speed = 1.0     # minimum ground-relative flight speed [m/s]
        self.w_descent_mean, self.w_descent_stdv = -2.0, 1.0  # [m/s]
        #
        # substitute for future calculation of energy stores and eventual exhaustion
        self.max_nflights = 3
        #
        # for radar coverage location and doppler velocity calculations/maps
        self.use_radar = True
        self.radar_name = 'XAM'
        self.radar_lat, self.radar_lon = 48.4783, -67.5822
        self.radar_UTM_zone = 19
        self.radar_grid_sw_east, self.radar_grid_ne_east = 481000.0, 726000.0
        self.radar_grid_sw_north, self.radar_grid_ne_north = 5249000.0, 5493000.0
        self.radar_grid_dx, self.radar_grid_dy = 1000.0, 1000.0
        #
        # for output grids
        self.npy_grids = False
        #
        # for output maps
        self.plot_bottom_lat, self.plot_top_lat = 44.0, 51.0
        self.plot_left_lon, self.plot_right_lon = -73.0, -64.0

# end Simulation_specifications_WRF-NARR_d03_20130715.py
