# pylint: disable=C0103,R0205,R0902,R0912,R0913,R0914,R0915,R1702,R1711
"""
Python script "Flier_class.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


import numpy as np
import pandas as pd
from Geography import lat_lon_to_utm, utm_to_lat_lon, inside_grid, calc_GpH
from Map_class import lc_category
from Flier_summary import flight_status_columns
from Plots_gen import plot_single_flight


class Flier:
    """Initialize, define, and manipulate an individual flier (SBW moth)."""

    def __init__(self, sim, sbw, flier_id, flier_location, flier_attributes):
        self.flier_id = flier_id
        #
        # status attributes
        self.active = 0
        self.output_written = 0
        self.prev_state = 'NONE'
        self.state = 'INITIALIZED'
        self.nflights = 0
        self.max_nflights = sim.max_nflights
        self.flight_status = dict()
        self.flight_status_idx = 0
        #
        # location-based attributes
        self.lat = flier_location[0]
        self.lon = flier_location[1]
        self.easting, self.northing, self.UTM_zone = lat_lon_to_utm(self.lat, self.lon)
        self.sfc_elev = 0.0
        self.alt_AGL = 0.0
        self.alt_MSL = self.sfc_elev + self.alt_AGL
        self.GpH = calc_GpH(self.lat, self.alt_MSL)
        if sim.use_defoliation:
            self.landcover_index = flier_location[2]
            self.lc_type = lc_category(self.landcover_index)
            self.defoliation_level = flier_location[3]
        else:
            self.landcover_index = -9999
            self.lc_type = 'null'
            self.defoliation_level = 0
        #
        # solar time attributes (to be initialized elsewhere)
        self.utc_sunset_time = None
        self.local_sunset_time = None
        self.utc_sunrise_time = None
        self.local_sunrise_time = None
        #
        # circadian rhythm attributes (to be initialized elsewhere)
        self.circadian_T_ref = 0.0
        self.circadian_delta_s = 0.0
        self.circadian_delta_0 = 0.0
        self.circadian_delta_f = 0.0
        self.circadian_delta_f_potential = 0.0
        self.utc_t_c = None
        self.local_t_c = None
        self.utc_t_0 = None
        self.local_t_0 = None
        self.utc_t_m = None
        self.local_t_m = None
        self.circadian_p = 0.0
        self.circadian_p_threshold = np.random.uniform()
        #
        # environmental attributes (to be provided by WRF data)
        self.P = 0.0
        self.T = 0.0
        self.Precip = 0.0
        self.U = 0.0
        self.V = 0.0
        self.W = 0.0
        #
        # eclosion date (via BioSIM)
        self.eclosion_YY = flier_attributes[0]
        self.eclosion_MM = flier_attributes[1]
        self.eclosion_DD = flier_attributes[2]
        #
        # morphological attributes
        self.sex = flier_attributes[3]
        self.forewing_A = flier_attributes[4]  # cm^2
        self.mass = flier_attributes[5]  # kg
        self.mass_err = 1.0
        if self.sex:
            self.fecundity = int(round(flier_attributes[6], 0))
            self.fecundity_0 = int(round(flier_attributes[7], 0))
            self.gravidity = self.fecundity / self.fecundity_0
            self.eggs_laid = dict()
        else:
            self.fecundity = 0.0
            self.fecundity_0 = 0.0
            self.gravidity = 0.0
            self.eggs_laid = 0
        #
        # flight attributes
        self.nu_L = sbw.calc_nu_L(self.forewing_A, self.mass)
        self.nu = 0.0
        self.Ts = 0.0
        self.nu_L_Ts = 0.0
        self.calc_AM_ratio()  # introduced by MG (July 2020)
        self.liftoff_angle = np.deg2rad(60)  # introduced by MG (July 2020)
        self.v_h = 0.0
        self.v_x = 0.0
        self.v_y = 0.0
        self.v_z = 0.0
        self.bearing = 0.0
        self.flight_range = 0.0
        self.flight_distance = 0.0
        #
        # doppler (radar-relative) motion
        self.v_radial = 0.0
        self.v_azimuthal = 0.0
        return

    def calc_AM_ratio(self):
        """Flight strength ratio, introduced by MG (July 2020)"""
        self.AMratio = self.forewing_A / (self.mass * 1000.0)  # cm^2 per g
        return

    def update_state(self, new_state):
        """Update Flier to indicated state.
           Possible states: 'INITIALIZED' (from 1st record to oviposition or circadian readiness),
                            'OVIPOSITION' (females only, of course)
                            'READY' (within allowed circadian liftoff period),
                            'LIFTOFF' (when nu_T > nu_L, while nflights <= max_nflights),
                            'FLIGHT' (above decision altitude),
                            'LANDING_W' (due to weak winds at decision altitude)
                            'LANDING_T' (due to low temperature),
                            'LANDING_P' (due to precipitation),
                            'LANDING_S' (due to sunrise),
                            'CRASH' (flight motion intersects ground, not a T/P/S landing)
                            'SPLASHED' (in the event of a water landing, your seat
                                        cushion may be used as a flotation device),
                            'SUNRISE' (if already on the ground at sunrise),
                            'HOST' (allows oviposition and/or reflight),
                            'FOREST' (non-host, no egg-laying but allows reflight),
                            'NONFOREST' (no egg-laying but allows reflight),
                            'SPENT' (for females, at G < 0.01),
                            'EXIT' (flew beyond simulation domain),
                            'MAXFLIGHTS' (eventually to be replaced with exhaustion)
                            'EXHAUSTED' (mass <= min_mass)"""
        self.prev_state = self.state
        self.state = new_state
        if new_state in ['READY', 'OVIPOSITION', 'HOST', 'FOREST', 'NONFOREST',
                         'LIFTOFF', 'FLIGHT', 'CRASH', 'LANDING_W', 'LANDING_T',
                         'LANDING_P', 'LANDING_S']:
            self.active = 1
        return

    def update_location(self, clock):
        """Update Flier location using ground-relative motion."""
        if self.state in ['LIFTOFF', 'FLIGHT', 'LANDING_W', 'LANDING_T',
                          'LANDING_P', 'LANDING_S', 'EXHAUSTED']:
            x_dist = (self.v_x + self.U) * clock.dt_interval
            y_dist = (self.v_y + self.V) * clock.dt_interval
            z_dist = (self.v_z + self.W) * clock.dt_interval
            self.flight_range += np.sqrt(x_dist**2 + y_dist**2)
            self.flight_distance += np.sqrt(x_dist**2 + y_dist**2 + z_dist**2)
            self.easting += x_dist
            self.northing += y_dist
            self.lat, self.lon = utm_to_lat_lon(self.easting, self.northing, self.UTM_zone)
            self.alt_MSL += z_dist
            self.GpH = calc_GpH(self.lat, self.alt_MSL)
        return

    def inside_grid(self, sim):
        """Check if Flier is still within the simulation boundaries."""
        return inside_grid(sim, self.lat, self.lon)

    def update_nu(self, sim, sbw):
        """Calculate Flier wingbeat frequency."""
        self.nu = sbw.calc_nu_T(self.T) * sim.delta_nu
        return

    def update_v_h_components(self, speed):
        """Calculate Flier horizontal velocity components."""
        self.v_x = speed * np.sin(self.bearing)
        self.v_y = speed * np.cos(self.bearing)
        return

    def update_motion(self, sim, sbw, radar):
        """Update Flier wingbeat frequency and wind-relative motion (velocity)."""
        if self.state in ['LIFTOFF', 'FLIGHT']:
            self.update_nu(sim, sbw)
            if (self.U != 0.0) and (self.V != 0.0):
                self.bearing = np.arctan2(self.U, self.V)
            # else if entering calm area (no wind), don't change the flight bearing
            if sim.flight_speed == 'const':
                # w_horizontal specified by user input
                if self.state == 'LIFTOFF':
                    self.update_v_h_components(-sim.w_horizontal)  # into the wind
                    self.v_z = 0.6  # [m/s] from Greenbank et al. (1980)
                elif self.state == 'FLIGHT':
                    self.update_v_h_components(sim.w_horizontal)  # with the wind
                    self.v_z = sim.w_alpha * (self.nu - self.nu_L_Ts)  # [m/s]
            elif sim.flight_speed == 'param':
                # new flight velocity parameterization
                # introduced August 2020 (MG)
                # revised February 2021 (MG)
                if self.state == 'LIFTOFF':
                    # horizontal speed [m/s]
                    self.v_h = -1 * sim.wingbeat_coeff * self.AMratio * \
                               self.nu * np.cos(self.liftoff_angle)
                    # vertical speed [m/s]
                    self.v_z = sim.wingbeat_coeff * self.AMratio * \
                               (self.nu - self.nu_L) * np.sin(self.liftoff_angle)
                elif self.state == 'FLIGHT':
                    # horizontal speed [m/s]
                    self.v_h = -1 * sim.wingbeat_coeff * self.AMratio * self.nu
                    # horizontal speed [m/s] in calm winds
                    V_h = np.sqrt(self.U**2 + self.V**2)
                    if (self.v_h + V_h) < sim.min_flight_speed:
                        self.v_h = sim.min_flight_speed - V_h
                    # vertical speed [m/s]
                    self.v_z = sim.wingbeat_coeff * self.AMratio * (self.nu - self.nu_L)
                self.update_v_h_components(self.v_h)
        elif self.state in ['LANDING_S', 'LANDING_W', 'LANDING_T', 'LANDING_P', 'EXHAUSTED']:
            # drifting on wind, wings folded
            self.nu = 0.0
            self.v_h = 0.0
            self.v_x = 0.0
            self.v_y = 0.0
            self.v_z = np.random.normal(loc=sim.w_descent_mean,
                                        scale=sim.w_descent_stdv)
            self.v_z = np.min([self.v_z, 0.0])
        else:
            self.zero_motion(sim)
        if sim.use_radar and (self.alt_AGL > radar.min_alt_AGL):
            self.v_radial, self.v_azimuthal = \
                radar.doppler_vel(self.UTM_zone, self.easting, self.northing,
                                  (self.U + self.v_x), (self.V + self.v_y))
        else:
            self.v_radial = 0.0
            self.v_azimuthal = 0.0
        return

    def zero_motion(self, sim):
        """Set motion variable values for stationary Flier."""
        self.nu = 0.0
        self.v_h = 0.0
        self.v_x = 0.0
        self.v_y = 0.0
        self.v_z = 0.0
        self.bearing = 0.0
        if sim.use_radar:
            self.v_radial = 0.0
            self.v_azimuthal = 0.0
        return

    def update_empirical_values(self, sim, sbw):
        """Update empirical flight parameters."""
        self.nu_L = sbw.calc_nu_L(self.forewing_A, self.mass)
        self.Ts = sbw.calc_Ts(self.nu_L, sim.delta_nu)
        self.nu_L_Ts = sbw.calc_nu_L_Ts(self.Ts, sim.delta_nu)
        return

    def update_environment(self, environment):
        """Update Flier environment using WRF-derived values."""
        self.sfc_elev = environment[0]         # [m]
        self.landcover_index = environment[1]  # [-]
        self.lc_type = lc_category(self.landcover_index)
        self.T = environment[2]                # [C]
        self.P = environment[3]                # [hPa]
        self.Precip = environment[4]           # [mm/h]
        self.U = environment[5]                # [m/s]
        self.V = environment[6]                # [m/s]
        self.W = environment[7]                # [m/s]
        if self.sfc_elev == -9999:
            self.update_state('EXIT')
        else:
            if self.alt_MSL < self.sfc_elev:
                self.alt_MSL = self.sfc_elev
                self.GpH = calc_GpH(self.lat, self.alt_MSL)
            self.alt_AGL = self.alt_MSL - self.sfc_elev
        return

    def liftoff_conditions(self, sim, sbw):
        """Evaluate Flier liftoff conditions and triggers."""
        if self.Precip >= sim.max_precip:  # no liftoff in heavy rain
            return False
        if self.W < 0.0:  # no liftoff in a downdraft (for later)
            return False
        if self.T > sbw.threshold_T:  # no liftoff if T too high (torpor)
            return False
        windspeed = np.sqrt(self.U**2 + self.V**2)
        if windspeed < sim.min_windspeed:  # no liftoff in calm wind
            return False
        if self.nu < self.nu_L:  # no liftoff if T too low (wingbeat)
            return False
        return True

    def liftoff_loc_info(self, clock):
        """Concatenate info on Flier liftoff location and conditions."""
        loc_info = [self.lat, self.lon, self.UTM_zone, self.easting, self.northing,
                    self.sfc_elev, self.lc_type, self.defoliation_level, self.sex,
                    self.mass, self.forewing_A, self.AMratio, self.fecundity, self.nu,
                    self.nu_L, clock.current_dt_str, self.utc_sunset_time.isoformat(),
                    self.circadian_T_ref, self.utc_t_0.isoformat(), self.utc_t_c.isoformat(),
                    self.utc_t_m.isoformat(), self.circadian_p, self.v_h, self.v_z, self.T,
                    self.P, self.U, self.V, self.W]
        return loc_info

    def landing_loc_info(self):
        """Concatenate info on Flier landing location and conditions."""
        loc_info = [self.lat, self.lon, self.UTM_zone, self.easting, self.northing,
                    self.sfc_elev, self.lc_type, self.defoliation_level, self.sex,
                    self.mass, self.fecundity]
        return loc_info

    def survivor_info(self):
        """Concatenate info on surviving Flier attributes."""
        attributes = [self.lat, self.lon, self.eclosion_YY, self.eclosion_MM,
                      self.eclosion_DD, self.sex, self.forewing_A, self.mass,
                      self.fecundity, self.fecundity_0]
        return attributes

    def update_state_motion(self, sim, sbw, radar, new_state):
        """Update Flier state and motion."""
        self.update_state(new_state)
        if new_state in ['CRASH', 'EXIT']:
            self.zero_motion(sim)
        else:
            self.update_motion(sim, sbw, radar)
        return

    def state_decisions(self, sim, clock, sbw, defoliation, radar,
                        liftoff_locations, landing_locations, survivors):
        """The main decision-making block."""
        self.update_nu(sim, sbw)
        remove = False
        #
        if self.state in ['INITIALIZED', 'OVIPOSITION']:
            if self.circadian_p >= self.circadian_p_threshold:
                self.update_state('READY')
        elif self.state in ['READY', 'HOST', 'FOREST', 'NONFOREST']:
            # sunrise
            if clock.current_dt > self.utc_sunrise_time:
                self.update_state('SUNRISE')
            # liftoff
            if self.state not in ['SUNRISE', 'SPENT']:
                if self.liftoff_conditions(sim, sbw):
                    if self.nflights == self.max_nflights:
                        self.update_state('MAXFLIGHTS')
                    else:
                        liftoff_id_str = '%s_%d' % (self.flier_id, self.nflights)
                        liftoff_locations[liftoff_id_str] = \
                            self.liftoff_loc_info(clock)
                        self.update_state_motion(sim, sbw, radar, 'LIFTOFF')
                        self.nflights += 1
        elif self.state in ['LIFTOFF', 'FLIGHT']:
            if not self.inside_grid(sim):
                self.update_state_motion(sim, sbw, radar, 'EXIT')
            elif clock.current_dt > self.utc_sunrise_time:
                self.update_state_motion(sim, sbw, radar, 'LANDING_S')
            elif self.Precip >= sim.max_precip:
                self.update_state_motion(sim, sbw, radar, 'LANDING_P')
            else:
                self.update_empirical_values(sim, sbw)
                if self.nu == 0.0:
                    self.update_state_motion(sim, sbw, radar, 'LANDING_T')
                else:
                    if self.state == 'LIFTOFF':
                        if self.alt_AGL >= sim.climb_decision_hgt:
                            windspeed = np.sqrt(self.U ** 2 + self.V ** 2)
                            if windspeed < sim.min_windspeed:
                                self.update_state_motion(sim, sbw, radar, 'LANDING_W')
                            else:
                                self.update_state_motion(sim, sbw, radar, 'FLIGHT')
                    elif (self.state == 'FLIGHT') and (self.alt_AGL <= 0.0):
                        self.update_state_motion(sim, sbw, radar, 'CRASH')
                    else:
                        self.update_motion(sim, sbw, radar)
        elif self.state in ['CRASH', 'LANDING_W', 'LANDING_T', 'LANDING_P', 'LANDING_S']:
            if not self.inside_grid(sim):
                self.update_state('EXIT')
            elif self.alt_AGL > 0.0:
                if self.state == 'LANDING_T':
                    # allow moth to resume normal flight if it falls into a warm enough layer
                    if self.nu > 0.0:
                        self.update_state('FLIGHT')
                self.update_motion(sim, sbw, radar)
            else:
                self.nu = 0.0
                self.zero_motion(sim)  # a landed moth is stationary
                landing_id_str = '%s_%d' % (self.flier_id, self.nflights)
                landing_locations[landing_id_str] = self.landing_loc_info()
                if self.lc_type == 'null':
                    self.update_state('EXIT')
                elif self.lc_type == 'WATER':
                    self.update_state('SPLASHED')
                elif self.lc_type == 'HOST_FOREST':
                    self.update_state('HOST')
                    if sim.use_defoliation:
                        self.defoliation_level = defoliation.get_value(self.lon, self.lat)
                elif self.lc_type == 'OTHER_FOREST':
                    self.update_state('FOREST')
                elif self.lc_type == 'NONFOREST':
                    self.update_state('NONFOREST')
        elif self.state in ['SPENT', 'SPLASHED', 'EXIT', 'MAXFLIGHTS', 'EXHAUSTED']:
            self.zero_motion(sim)  # a spent/lost/dead moth is stationary
            self.alt_AGL = 0.0  # a spent/lost/dead moth is on the ground
            if self.sfc_elev == -9999:
                self.update_state('EXIT')
                self.sfc_elev = 0.0
            self.alt_MSL = self.sfc_elev
        self.update_status(clock)
        if self.state == 'SUNRISE':
            if sim.sequential:
                survivors[self.flier_id] = self.survivor_info()
            remove = True
        elif self.state in ['SPENT', 'SPLASHED', 'EXIT', 'MAXFLIGHTS', 'EXHAUSTED']:
            self.active = 0
            remove = True
        return remove, liftoff_locations, landing_locations, survivors  # bool + 3 * dict

    def flight_status_info(self, clock):
        """Concatenate info on Flier location, status, and conditions."""
        status_info = [self.flight_status_idx, clock.current_dt_str, self.prev_state,
                       self.state, self.northing, self.easting, self.UTM_zone, self.lat,
                       self.lon, self.sfc_elev, self.alt_AGL, self.alt_MSL,
                       self.defoliation_level, self.sex, self.mass, self.forewing_A,
                       self.fecundity_0, self.fecundity, self.gravidity, self.nu,
                       self.nu_L, self.v_h, self.v_x, self.v_y, self.v_z, self.v_radial,
                       self.v_azimuthal, self.bearing, self.flight_range, self.P, self.T,
                       self.Precip, self.GpH, self.U, self.V, self.W]
        return status_info

    def update_status(self, clock):
        """Record Flier status for output."""
        flight_status_str = '%s_%s' % (self.flier_id,
                                       str(self.flight_status_idx).zfill(7))
        self.flight_status[flight_status_str] = self.flight_status_info(clock)
        self.flight_status_idx += 1
        return

    def report_status(self, sim, clock, trajectories):
        """Write out full listing of Flier status and plot trajectory."""
        if sim.experiment_number:
            outpath = '%s_simulation_%s_%s_output' % \
                      (sim.simulation_name, str(sim.experiment_number).zfill(2),
                       str(sim.simulation_number).zfill(5))
        else:
            outpath = '%s_simulation_%s_output' % \
                      (sim.simulation_name, str(sim.simulation_number).zfill(5))
        status_df = pd.DataFrame.from_dict(self.flight_status, orient='index')
        status_df.columns = flight_status_columns()
        status_df = status_df.sort_values(by=['flight_status'])
        if sim.experiment_number:
            outfname = '%s/flier_%s_%s_%s_report.csv' % \
                       (outpath, str(sim.experiment_number).zfill(2),
                        str(sim.simulation_number).zfill(5), self.flier_id)
        else:
            outfname = '%s/flier_%s_%s_report.csv' % \
                       (outpath, str(sim.simulation_number).zfill(5), self.flier_id)
        status_df.to_csv(outfname)
        print('%s UTC : wrote %s' % (clock.current_dt_str, outfname.split('/')[-1]))
        self.output_written = 1
        #
        if sim.experiment_number:
            outfname = '%s/flier_%s_%s_%s_trajectory.png' % \
                       (outpath, str(sim.experiment_number).zfill(2),
                        str(sim.simulation_number).zfill(5), self.flier_id)
        else:
            outfname = '%s/flier_%s_%s_trajectory.png' % \
                       (outpath, str(sim.simulation_number).zfill(5), self.flier_id)
        if plot_single_flight(sim, status_df, outfname):
            print('%s UTC : wrote %s' % (clock.current_dt_str, outfname.split('/')[-1]))
            lats = np.array(status_df['lat'])
            lons = np.array(status_df['lon'])
            alts = np.array(status_df['alt_AGL'])
            trajectories[self.flier_id] = [lats, lons, alts]
        return trajectories

# end Flier_class.py
