# pylint: disable=C0103,R0913,R0914,R1711
"""
Python script "Flier_setup.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


from datetime import datetime, timedelta, timezone as tz
import numpy as np
import pandas as pd
from Interpolation import get_interp_vals_2D
from Geography import inside_grid, inside_init_box
from Map_class import lc_category


def read_flier_locations_attributes(sim, clock):
    """Read BioSIM CSV output file with moth emergence dates, locations, attributes.
       Filter to desired moth age (2-14 days) and location in simulation domain/box."""
    print('initial setup : reading and processing %s' % sim.biosim_fname)
    attributes_df = pd.read_csv(sim.biosim_fname, low_memory=False)
    n_attributes = len(attributes_df)
    print('initial setup : %d total fliers are listed' % n_attributes)
    lats = np.array(attributes_df['Latitude']).astype(np.float)
    lons = np.array(attributes_df['Longitude']).astype(np.float)
    inside = list()
    for i in range(n_attributes):
        inside.append(inside_grid(sim, lats[i], lons[i]))
    attributes_df['inside_grid'] = inside
    if sim.use_initial_flier_polygon:
        inside = list()
        for i in range(n_attributes):
            inside.append(inside_init_box(sim, lats[i], lons[i]))
        attributes_df['inside_init_box'] = inside
    YY = np.array(attributes_df['Year']).astype(np.int)
    MM = np.array(attributes_df['Month']).astype(np.int)
    DD = np.array(attributes_df['Day']).astype(np.int)
    TDelta = list()
    for i in range(n_attributes):
        DT = datetime(YY[i], MM[i], DD[i], 0, 0, 0, tzinfo=tz.utc)
        TDelta.append(clock.start_dt - DT)
    attributes_df['timedelta'] = TDelta
    # select moths that became available within n days of the start date
    maxdays = sim.biosim_ndays_max
    young_df = attributes_df[attributes_df['timedelta'] <= timedelta(days=maxdays)]
    print('initial setup : %d total fliers have been ready <= %d days' %
          (len(young_df), maxdays))
    # select moths that are fertilized on or before the start date
    mindays = sim.biosim_ndays_min
    ready_df = young_df[young_df['timedelta'] >= timedelta(days=mindays)]
    print('initial setup : %d total fliers are ready before the start date' %
          len(ready_df))
    # select moths that are within the specified initialization/simulation area
    if sim.use_initial_flier_polygon:
        available_df = ready_df[ready_df['inside_init_box']]
        print('initial setup : selecting only ready fliers in the specified area')
    else:
        available_df = ready_df[ready_df['inside_grid']]
    n_available = len(available_df)
    print('initial setup : %d ready fliers are available in the simulation domain' %
          n_available)
    # lat/lon based on BioSIM assignment and availability
    lats = np.array(available_df['Latitude']).astype(np.float)
    lons = np.array(available_df['Longitude']).astype(np.float)
    # morphological attributes based on BioSIM assignment (for now)
    sex = np.array(available_df['Sex']).astype(np.int)
    A = np.array(available_df['A']).astype(np.float)
    M = np.array(available_df['M']).astype(np.float)
    F = np.array(available_df['F']).astype(np.float) * sex
    F_0 = np.array(available_df['F_0']).astype(np.float) * sex
    # export locations
    locations = list()
    for i in range(n_available):
        locations.append([lats[i], lons[i]])
    # export attributes
    attributes = list()
    for i in range(n_available):
        attributes.append([sex[i], A[i], M[i], F_0[i], F[i]])
    return locations, attributes  # 2 * lists


def generate_flier_locations(wrf_grids, landcover, defoliation):
    """Generate flier lat/lon locations using given defoliation map.
       TO-DO: update with initial locations box/polygon."""
    grid_orig = np.copy(defoliation.map_grid)
    grid = np.where(grid_orig == -9999.0, 0, grid_orig)
    grid = np.where(grid == 30.0, 1, grid)
    grid = np.where(grid == 60.0, 2, grid)
    grid = np.where(grid == 90.0, 3, grid)
    rs, cs = np.where(grid > 0)
    rows = list()
    cols = list()
    dlevels = list()
    for r, c in zip(rs, cs):
        for i in range(grid[r, c]):
            rows.append(r)
            cols.append(c)
            dlevels.append(grid[r, c])
    max_dev_lat = defoliation.dy / 2.0
    max_dev_lon = defoliation.dx / 2.0
    lats = defoliation.SW_lat + rows * defoliation.dy + \
        np.random.uniform(low=-max_dev_lat, high=max_dev_lat)
    lons = defoliation.SW_lon + cols * defoliation.dx + \
        np.random.uniform(low=-max_dev_lon, high=max_dev_lon)
    #
    # check candidate locations against provided landcover
    locations = list()
    if landcover == 'WRF':
        lc_idxs = get_interp_vals_2D(wrf_grids.lons, wrf_grids.lats,
                                     wrf_grids.landcover, 'nearest',
                                     lons, lats)
    else:
        lc_idxs = landcover.get_values(lons, lats)
    #
    # accept only locations in HOST_FOREST landcover
    for i, lc_idx in enumerate(lc_idxs):
        if lc_category(lc_idx) == 'HOST_FOREST':
            locations.append([lats[i], lons[i], lc_idx, dlevels[i]])
    return locations  # list


def generate_flier_attributes(sbw, locations):
    """Select sex, assign forewing_A, and calculate mass & fecundity.
       Empirical distributions are specified in SBW_empirical.py"""
    n_fliers = len(locations)
    sex = np.random.uniform(size=n_fliers)
    sex = np.where(sex >= 0.5, 1, 0)
    n_females = np.sum(sex)
    n_males = n_fliers - n_females
    #
    # assign male wing areas by random sample from normal empirical distribution
    A_males = np.random.normal(loc=sbw.A_mean[0], scale=sbw.A_stdv[0], size=n_males)
    A_males = np.where(A_males < sbw.A_min[0], sbw.A_min[0], A_males)
    A_males = np.where(A_males > sbw.A_max[0], sbw.A_max[0], A_males)
    #
    # assign female wing areas by random sample from normal empirical distribution
    A_females = np.random.normal(loc=sbw.A_mean[1], scale=sbw.A_stdv[1], size=n_females)
    A_females = np.where(A_females < sbw.A_min[1], sbw.A_min[1], A_females)
    A_females = np.where(A_females > sbw.A_max[1], sbw.A_max[1], A_females)
    #
    # calculate male mass from empirical relation to wing area
    M_err_males = np.random.normal(loc=sbw.M_err_mean[0], scale=sbw.M_err_stdv[0], size=n_males)
    M_males = sbw.calculate_mass_from_wing_area(0, A_males, M_err_males)
    #
    # calculate female fecundity from empirical relation to wing area
    F_err = np.random.normal(loc=sbw.F_err_mean, scale=sbw.F_err_stdv, size=n_females)
    F = list()
    F_0 = list()
    f_idx = 0
    for i in range(n_fliers):
        if sex[i]:
            F.append(sbw.calculate_fecundity(A_females[f_idx], F_err[f_idx]))
            D = locations[i][3] * 0.30  # effects of defoliation
            F_0.append(sbw.calculate_fecundity_0(F[f_idx], D))
            f_idx += 1
    #
    # calculate female mass from empirical relation to gravidity and wing area
    G = [(f / f_0) for f, f_0 in zip(F, F_0)]
    M_err_females = np.random.normal(loc=sbw.M_F_err_mean, scale=sbw.M_F_err_stdv, size=n_females)
    M_females = sbw.calculate_mass_from_gravidity(A_females, G, M_err_females)
    #
    # build attributes list of lists
    attributes = list()
    m_idx = 0
    f_idx = 0
    for i in range(n_fliers):
        if sex[i] == 0:
            attributes.append([sex[i], A_males[m_idx], M_males[m_idx], 0.0, 0.0])
            m_idx += 1
        else:
            attributes.append([sex[i], A_females[f_idx], M_females[f_idx],
                               F[f_idx], F_0[f_idx]])
            f_idx += 1
    return attributes  # list

# end Flier_setup.py
