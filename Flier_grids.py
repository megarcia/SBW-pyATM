# pylint: disable=C0103,R0913,R0912,R0914,R0915,R1711
"""
Python script "Flier_grids.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2019, 2020 by Matthew Garcia
"""


import numpy as np
import pandas as pd
from pyproj import Proj


def get_utm_zone(lon):
    """Calculate UTM zone number."""
    return int(1 + (lon + 180.0) / 6.0)


def is_south(lat):
    """Is location in southern hemisphere?"""
    return bool(lat < 0.0)


def grid_flier_locations(sim, radar, locations, date_time):
    """Count Fliers and generate/save radar-relative grid."""
    north_upa = list()
    east_upa = list()
    for location in locations.values():
        if location[2] > radar.min_alt_AGL:
            north_upa.append(location[7])
            east_upa.append(location[6])
    if north_upa:
        upa_grid = radar.count_grid(north_upa, east_upa)
        dt_str = str(date_time.isoformat())
        if sim.experiment_number:
            outfname = '%s_simulation_%s_%s_summary/dens_%s_%s_%s_%s_grid.npy' % \
                (sim.simulation_name, str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5), dt_str,
                 str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5), radar.radar_id)
        else:
            outfname = '%s_simulation_%s_summary/dens_%s_%s_%s_grid.npy' % \
                (sim.simulation_name, str(sim.simulation_number).zfill(5),
                 dt_str, str(sim.simulation_number).zfill(5), radar.radar_id)
        np.save(outfname, upa_grid)
        print('%s UTC : wrote %s' % (dt_str, outfname.split('/')[-1]))
    return


def grid_flier_dvels(sim, radar, locations, date_time):
    """Average Flier doppler velocity and generate/save radar-relative grid."""
    north_upa = list()
    east_upa = list()
    dvel_upa = list()
    for location in locations.values():
        if location[2] > radar.min_alt_AGL:
            north_upa.append(location[7])
            east_upa.append(location[6])
            dvel_upa.append(location[11])
    if north_upa:
        upa_grid = radar.average_grid(north_upa, east_upa, dvel_upa)
        dt_str = str(date_time.isoformat())
        if sim.experiment_number:
            outfname = '%s_simulation_%s_%s_summary/dvel_%s_%s_%s_%s_grid.npy' % \
                (sim.simulation_name, str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5), dt_str,
                 str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5), radar.radar_id)
        else:
            outfname = '%s_simulation_%s_summary/dvel_%s_%s_%s_grid.npy' % \
                (sim.simulation_name, str(sim.simulation_number).zfill(5),
                 dt_str, str(sim.simulation_number).zfill(5), radar.radar_id)
        np.save(outfname, upa_grid)
        print('%s UTC : wrote %s' % (dt_str, outfname.split('/')[-1]))
    return


def create_fill_grids(sim, df):
    """Generate and fill liftoff/landing grids."""
    proj = Proj(proj="utm", zone=sim.grid_UTM_zone, ellps="WGS84",
                south=is_south(sim.grid_min_lat))
    grid_sw_east, grid_sw_north = proj(sim.grid_min_lon, sim.grid_min_lat)
    grid_ne_east, grid_ne_north = proj(sim.grid_max_lon, sim.grid_max_lat)
    grid_nrows = int((grid_ne_north - grid_sw_north) / sim.grid_dy)
    grid_ncols = int((grid_ne_east - grid_sw_east) / sim.grid_dx)
    #
    grid = np.zeros((grid_nrows, grid_ncols))
    females_grid = np.zeros((grid_nrows, grid_ncols))
    fecundity_grid = np.zeros((grid_nrows, grid_ncols))
    males_grid = np.zeros((grid_nrows, grid_ncols))
    #
    UTM_zone = list(df['UTM_zone'])
    east = list(df['easting'])
    north = list(df['northing'])
    sex = list(df['sex'])
    fecundity = list(df['F'])
    #
    for i, female in enumerate(sex):
        if UTM_zone[i] != sim.grid_UTM_zone:
            proj1 = Proj(proj="utm", zone=UTM_zone[i], ellps="WGS84",
                         south=is_south(sim.grid_min_lat))
            lon, lat = proj1(east[i], north[i], inverse=True)
            proj2 = Proj(proj="utm", zone=sim.grid_UTM_zone, ellps="WGS84",
                         south=is_south(sim.grid_min_lat))
            east[i], north[i] = proj2(lon, lat)
        r = int(round((north[i] - grid_sw_north) / sim.grid_dy))
        c = int(round((east[i] - grid_sw_east) / sim.grid_dx))
        if 0 <= r < grid_nrows:
            if 0 <= c < grid_ncols:
                grid[r, c] += 1
                if female:
                    females_grid[r, c] += 1
                    fecundity_grid[r, c] += fecundity[i]
                else:
                    males_grid[r, c] += 1
    return grid, females_grid, fecundity_grid, males_grid


def grid_liftoff_locations(sim, liftoff_locations):
    """Save Flier liftoff locations and generate domain-wide grid."""
    liftoff_df = pd.DataFrame.from_dict(liftoff_locations, orient='index')
    liftoff_df.columns = ['latitude', 'longitude', 'UTM_zone', 'easting', 'northing',
                          'sfc_elev', 'lc_type', 'defoliation', 'sex', 'M', 'A',
                          'AMratio', 'F', 'nu', 'nu_L', 'liftoff_time', 'sunset_time',
                          'T_ref', 't_c', 't_0', 't_m', 'circadian_p', 'v_h', 'v_z',
                          'T', 'P', 'U', 'V', 'W']
    if sim.experiment_number:
        outfname = '%s_simulation_%s_%s_summary/liftoff_locs_times_%s_%s.csv' % \
            (sim.simulation_name, str(sim.experiment_number).zfill(2),
             str(sim.simulation_number).zfill(5), str(sim.experiment_number).zfill(2),
             str(sim.simulation_number).zfill(5))
    else:
        outfname = '%s_simulation_%s_summary/liftoff_locs_times_%s.csv' % \
            (sim.simulation_name, str(sim.simulation_number).zfill(5),
             str(sim.simulation_number).zfill(5))
    liftoff_df.to_csv(outfname)
    print('simulation wrapup : wrote %s' % outfname.split('/')[-1])
    #
    if sim.npy_grids:
        liftoff_grid, liftoff_females_grid, liftoff_fecundity_grid, liftoff_males_grid = \
            create_fill_grids(sim, liftoff_df)
        #
        if sim.experiment_number:
            outfname = '%s_simulation_%s_%s_summary/liftoff_all_locs_%s_%s.npy' % \
                (sim.simulation_name, str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5), str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5))
        else:
            outfname = '%s_simulation_%s_summary/liftoff_all_locs_%s.npy' % \
                (sim.simulation_name, str(sim.simulation_number).zfill(5),
                 str(sim.simulation_number).zfill(5))
        np.save(outfname, liftoff_grid)
        print('simulation wrapup : wrote %s' % outfname.split('/')[-1])
        #
        if sim.experiment_number:
            outfname = '%s_simulation_%s_%s_summary/liftoff_female_locs_%s_%s.npy' % \
                (sim.simulation_name, str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5), str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5))
        else:
            outfname = '%s_simulation_%s_summary/liftoff_female_locs_%s.npy' % \
                (sim.simulation_name, str(sim.simulation_number).zfill(5),
                 str(sim.simulation_number).zfill(5))
        np.save(outfname, liftoff_females_grid)
        print('simulation wrapup : wrote %s' % outfname.split('/')[-1])
        #
        if sim.experiment_number:
            outfname = '%s_simulation_%s_%s_summary/liftoff_fecundity_locs_%s_%s.npy' % \
                (sim.simulation_name, str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5), str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5))
        else:
            outfname = '%s_simulation_%s_summary/liftoff_fecundity_locs_%s.npy' % \
                (sim.simulation_name, str(sim.simulation_number).zfill(5),
                 str(sim.simulation_number).zfill(5))
        np.save(outfname, liftoff_fecundity_grid)
        print('simulation wrapup : wrote %s' % outfname.split('/')[-1])
        #
        if sim.experiment_number:
            outfname = '%s_simulation_%s_%s_summary/liftoff_male_locs_%s_%s.npy' % \
                (sim.simulation_name, str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5), str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5))
        else:
            outfname = '%s_simulation_%s_summary/liftoff_male_locs_%s.npy' % \
                (sim.simulation_name, str(sim.simulation_number).zfill(5),
                 str(sim.simulation_number).zfill(5))
        np.save(outfname, liftoff_males_grid)
        print('simulation wrapup : wrote %s' % outfname.split('/')[-1])
    return


def grid_landing_locations(sim, landing_locations):
    """Save Flier landing locations and generate domain-wide grid."""
    landing_df = pd.DataFrame.from_dict(landing_locations, orient='index')
    landing_df.columns = ['latitude', 'longitude', 'UTM_zone', 'easting',
                          'northing', 'sfc_elev', 'lc_type', 'defoliation',
                          'sex', 'M', 'F']
    landing_df.sort_index(inplace=True)
    if sim.experiment_number:
        outfname = '%s_simulation_%s_%s_summary/landing_locs_%s_%s.csv' % \
            (sim.simulation_name, str(sim.experiment_number).zfill(2),
             str(sim.simulation_number).zfill(5), str(sim.experiment_number).zfill(2),
             str(sim.simulation_number).zfill(5))
    else:
        outfname = '%s_simulation_%s_summary/landing_locs_%s.csv' % \
            (sim.simulation_name, str(sim.simulation_number).zfill(5),
             str(sim.simulation_number).zfill(5))
    landing_df.to_csv(outfname)
    print('simulation wrapup : wrote %s' % outfname.split('/')[-1])
    #
    if sim.npy_grids:
        landing_grid, landing_females_grid, landing_fecundity_grid, landing_males_grid = \
            create_fill_grids(sim, landing_df)
        #
        if sim.experiment_number:
            outfname = '%s_simulation_%s_%s_summary/landing_all_locs_%s_%s.npy' % \
                (sim.simulation_name, str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5), str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5))
        else:
            outfname = '%s_simulation_%s_summary/landing_all_locs_%s.npy' % \
                (sim.simulation_name, str(sim.simulation_number).zfill(5),
                 str(sim.simulation_number).zfill(5))
        np.save(outfname, landing_grid)
        print('simulation wrapup : wrote %s' % outfname.split('/')[-1])
        #
        if sim.experiment_number:
            outfname = '%s_simulation_%s_%s_summary/landing_female_locs_%s_%s.npy' % \
                (sim.simulation_name, str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5), str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5))
        else:
            outfname = '%s_simulation_%s_summary/landing_female_locs_%s.npy' % \
                (sim.simulation_name, str(sim.simulation_number).zfill(5),
                 str(sim.simulation_number).zfill(5))
        np.save(outfname, landing_females_grid)
        print('simulation wrapup : wrote %s' % outfname.split('/')[-1])
        #
        if sim.experiment_number:
            outfname = '%s_simulation_%s_%s_summary/landing_fecundity_locs_%s_%s.npy' % \
                (sim.simulation_name, str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5), str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5))
        else:
            outfname = '%s_simulation_%s_summary/landing_fecundity_locs_%s.npy' % \
                (sim.simulation_name, str(sim.simulation_number).zfill(5),
                 str(sim.simulation_number).zfill(5))
        np.save(outfname, landing_fecundity_grid)
        print('simulation wrapup : wrote %s' % outfname.split('/')[-1])
        #
        if sim.experiment_number:
            outfname = '%s_simulation_%s_%s_summary/landing_male_locs_%s_%s.npy' % \
                (sim.simulation_name, str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5), str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5))
        else:
            outfname = '%s_simulation_%s_summary/landing_male_locs_%s.npy' % \
                (sim.simulation_name, str(sim.simulation_number).zfill(5),
                 str(sim.simulation_number).zfill(5))
        np.save(outfname, landing_males_grid)
        print('simulation wrapup : wrote %s' % outfname.split('/')[-1])
    return


def grid_egg_deposition(sim, egg_deposition):
    """Save Flier egg deposition locations and generate domain-wide grid."""
    eggs_df = pd.DataFrame.from_dict(egg_deposition, orient='index')
    eggs_df.columns = ['latitude', 'longitude', 'UTM_zone',
                       'easting', 'northing', 'n_eggs']
    eggs_df.sort_index(inplace=True)
    if sim.experiment_number:
        outfname = '%s_simulation_%s_%s_summary/egg_deposition_%s_%s.csv' % \
            (sim.simulation_name, str(sim.experiment_number).zfill(2),
             str(sim.simulation_number).zfill(5), str(sim.experiment_number).zfill(2),
             str(sim.simulation_number).zfill(5))
    else:
        outfname = '%s_simulation_%s_summary/egg_deposition_%s.csv' % \
            (sim.simulation_name, str(sim.simulation_number).zfill(5),
             str(sim.simulation_number).zfill(5))
    eggs_df.to_csv(outfname)
    print('simulation wrapup : wrote %s' % outfname.split('/')[-1])
    #
    if sim.npy_grids:
        proj = Proj(proj="utm", zone=sim.grid_UTM_zone, ellps="WGS84", south=is_south(sim.grid_min_lat))
        grid_sw_east, grid_sw_north = proj(sim.grid_min_lon, sim.grid_min_lat)
        grid_ne_east, grid_ne_north = proj(sim.grid_max_lon, sim.grid_max_lat)
        grid_nrows = int((grid_ne_north - grid_sw_north) / sim.grid_dy)
        grid_ncols = int((grid_ne_east - grid_sw_east) / sim.grid_dx)
        eggs_grid = np.zeros((grid_nrows, grid_ncols))
        for location in egg_deposition.values():
            if location[2] != sim.grid_UTM_zone:
                proj1 = Proj(proj="utm", zone=location[2], ellps="WGS84", south=is_south(sim.grid_min_lat))
                lon, lat = proj1(location[3], location[4], inverse=True)
                proj2 = Proj(proj="utm", zone=sim.grid_UTM_zone, ellps="WGS84", south=is_south(sim.grid_min_lat))
                location[3], location[4] = proj2(lon, lat)
            r = int(round((location[4] - grid_sw_north) / sim.grid_dy))
            c = int(round((location[3] - grid_sw_east) / sim.grid_dx))
            if 0 <= r < grid_nrows:
                if 0 <= c < grid_ncols:
                    eggs_grid[r, c] += location[5]
        if sim.experiment_number:
            outfname = '%s_simulation_%s_%s_summary/egg_deposition_%s_%s.npy' % \
                (sim.simulation_name, str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5), str(sim.experiment_number).zfill(2),
                 str(sim.simulation_number).zfill(5))
        else:
            outfname = '%s_simulation_%s_summary/egg_deposition_%s.npy' % \
                (sim.simulation_name, str(sim.simulation_number).zfill(5),
                 str(sim.simulation_number).zfill(5))
        np.save(outfname, eggs_grid)
        print('simulation wrapup : wrote %s' % outfname.split('/')[-1])
    return

# end Flier_grids.py
