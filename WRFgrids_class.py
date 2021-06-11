# pylint: disable=C0103,R0205,R0902,R0912,R0913,R0914,R0915,R1711
"""
Python script "WRFgrids_class.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2019, 2020 by Matthew Garcia
"""


import os
import sys
import numpy as np
from netCDF4 import Dataset
from wrf import to_np, getvar, smooth2d, latlon_coords
from Interpolate import get_vals_1D
from Interpolate import get_nearest_vals_2D, get_nearest_columns
from Interpolate import get_interp_vals_2D


def check_for_WRF_file(file_date_time, path, wrf_grid):
    """Check given path for file with desired timestamp."""
    fname_colons = 'wrfout_subset_%s_%s:00.nc' % \
        (wrf_grid, file_date_time.strftime("%Y-%m-%d_%H:%M"))
    fpath_colons = '%s/%s' % (path, fname_colons)
    fname_underscores = 'wrfout_subset_%s_%s_00.nc' % \
        (wrf_grid, file_date_time.strftime("%Y-%m-%d_%H_%M"))
    fpath_underscores = '%s/%s' % (path, fname_underscores)
    if os.path.exists(fpath_colons):
        file_exists = True
        fname = fname_colons
    elif os.path.exists(fpath_underscores):
        file_exists = True
        fname = fname_underscores
    else:
        file_exists = False
        fname = fname_colons
    return file_exists, fname  # bool, str


class WRFgrids(object):
    """Read and interpolate WRF output data."""

    def __init__(self, file_date_time, path, wrf_grid, dt_str):
        self.date_time = file_date_time
        file_exists, self.fname = check_for_WRF_file(file_date_time, path, wrf_grid)
        if file_exists:
            print('%s : reading %s' % (dt_str, self.fname))
            ncfile = Dataset('%s/%s' % (path, self.fname), 'r')
            # get lat/lon coordinate grids
            T2_var = getvar(ncfile, 'T2')
            lats, lons = latlon_coords(T2_var)  # xarray datatype
            self.lats = np.array(lats)
            self.lons = np.array(lons)
            # get surface variables
            self.T2 = to_np(T2_var)
            self.PSFC = to_np(getvar(ncfile, 'PSFC'))
            self.precip = to_np(getvar(ncfile, 'precipitation'))
            self.U10 = to_np(getvar(ncfile, 'u10_e'))
            self.V10 = to_np(getvar(ncfile, 'v10_e'))
            self.landcover = to_np(getvar(ncfile, 'LU_INDEX'))
            self.topography = to_np(getvar(ncfile, 'HGT'))
            # get upper air variables
            self.GpH = to_np(getvar(ncfile, 'geopotential_height'))
            self.temperature = to_np(getvar(ncfile, 'temperature'))
            self.pressure = to_np(getvar(ncfile, 'pressure'))
            self.rain = to_np(getvar(ncfile, 'rain'))
            self.uwind = to_np(getvar(ncfile, 'ue_unstaggered'))
            self.vwind = to_np(getvar(ncfile, 've_unstaggered'))
            self.wwind = to_np(getvar(ncfile, 'w_unstaggered'))
            # variables for mapping
            self.map_lats = to_np(lats)
            self.map_lons = to_np(lons)
            self.map_topography = to_np(smooth2d(getvar(ncfile, 'HGT'), 3))
            #
            ncfile.close()
        else:
            print('ERROR: WRF file %s does not exist!' % self.fname)
            sys.exit()
        return

    def get_WRF_grid_by_name(self, grid_name):
        """Isolate WRF grid by name."""
        if grid_name == 'topography':
            grid = self.topography
        elif grid_name == 'landcover':
            grid = self.landcover
        elif grid_name == 'T2':
            grid = self.T2
        elif grid_name == 'PSFC':
            grid = self.PSFC
        elif grid_name == 'PRCP':
            grid = self.precip
        elif grid_name == 'U10':
            grid = self.U10
        elif grid_name == 'V10':
            grid = self.V10
        elif grid_name == 'GpH':
            grid = self.GpH
        elif grid_name == 'temperature':
            grid = self.temperature
        elif grid_name == 'pressure':
            grid = self.pressure
        elif grid_name == 'rain':
            grid = self.rain
        elif grid_name == 'uwind':
            grid = self.uwind
        elif grid_name == 'vwind':
            grid = self.vwind
        elif grid_name == 'wwind':
            grid = self.wwind
        return grid

    def get_vals_2D(self, sim, grid_name, lons, lats):
        """Get values by specified 2D (horizontal) interpolation method."""
        grid = self.get_WRF_grid_by_name(grid_name)
        if sim.WRF_hinterp == 'nearest':
            rows, cols = self.get_nearest_locs(lons, lats)
            vals = get_nearest_vals_2D(grid, rows, cols)
        else:
            if grid_name == 'landcover':
                vals = get_interp_vals_2D(self.lons, self.lats, grid,
                                          'nearest', lons, lats)
            else:
                vals = get_interp_vals_2D(self.lons, self.lats, grid,
                                          sim.WRF_hinterp, lons, lats)
        return vals

    def get_col_3D(self, sim, grid_name, lons, lats):
        """Get values by specified 2D (horizontal) interpolation method."""
        grid = self.get_WRF_grid_by_name(grid_name)
        if sim.WRF_hinterp == 'nearest':
            rows, cols = self.get_nearest_locs(lons, lats)
            value_col = get_nearest_columns(grid, rows, cols)
        else:
            value_col = self.get_interp_columns(grid, sim.WRF_hinterp, lons, lats)
        return value_col

    def interpolate_space(self, sim, locations):
        """Get WRF variable values at the given locations for a specific time."""
        use_sfc_grids = dict()
        use_upa_grids = dict()
        for flier_id, loc in locations.items():
            alt_AGL = loc[2]
            if alt_AGL <= 20.0:
                use_sfc_grids[flier_id] = loc
            else:
                use_upa_grids[flier_id] = loc
        values = dict()
        #
        # get values where use_sfc_grids is indicated
        n_sfc_fliers = len(use_sfc_grids)
        if n_sfc_fliers:
            ids = use_sfc_grids.keys()
            locs_lon = [loc[1] for loc in use_sfc_grids.values()]
            locs_lat = [loc[0] for loc in use_sfc_grids.values()]
            SFCelev_vals = self.get_vals_2D(sim, 'topography', locs_lon, locs_lat)
            LCidx_vals = self.get_vals_2D(sim, 'landcover', locs_lon, locs_lat)
            T2_vals = self.get_vals_2D(sim, 'T2', locs_lon, locs_lat)
            PSFC_vals = self.get_vals_2D(sim, 'PSFC', locs_lon, locs_lat)
            PRCP_vals = self.get_vals_2D(sim, 'PRCP', locs_lon, locs_lat)
            U10_vals = self.get_vals_2D(sim, 'U10', locs_lon, locs_lat)
            V10_vals = self.get_vals_2D(sim, 'V10', locs_lon, locs_lat)
            #
            for i, flier_id in enumerate(ids):
                lat = locations[flier_id][0]
                lon = locations[flier_id][1]
                GpH = locations[flier_id][4]
                values[flier_id] = [lat, lon, GpH, SFCelev_vals[i], LCidx_vals[i],
                                    T2_vals[i], PSFC_vals[i], PRCP_vals[i], U10_vals[i],
                                    V10_vals[i], 0.0]
        #
        # get values where use_upa_grids is indicated
        n_upa_fliers = len(use_upa_grids)
        if n_upa_fliers:
            ids = use_upa_grids.keys()
            locs_lon = [loc[1] for loc in use_upa_grids.values()]
            locs_lat = [loc[0] for loc in use_upa_grids.values()]
            locs_GpH = [loc[4] for loc in use_upa_grids.values()]
            SFCelev_vals = self.get_vals_2D(sim, 'topography', locs_lon, locs_lat)
            LCidx_vals = self.get_vals_2D(sim, 'landcover', locs_lon, locs_lat)
            GpH_columns = self.get_col_3D(sim, 'GpH', locs_lon, locs_lat)
            T_columns = self.get_col_3D(sim, 'temperature', locs_lon, locs_lat)
            T_vals = get_vals_1D(GpH_columns, T_columns, sim.WRF_vinterp, locs_GpH)
            P_columns = self.get_col_3D(sim, 'pressure', locs_lon, locs_lat)
            P_vals = get_vals_1D(GpH_columns, P_columns, sim.WRF_vinterp, locs_GpH)
            R_columns = self.get_col_3D(sim, 'rain', locs_lon, locs_lat)
            R_vals = get_vals_1D(GpH_columns, R_columns, sim.WRF_vinterp, locs_GpH)
            U_columns = self.get_col_3D(sim, 'uwind', locs_lon, locs_lat)
            U_vals = get_vals_1D(GpH_columns, U_columns, sim.WRF_vinterp, locs_GpH)
            V_columns = self.get_col_3D(sim, 'vwind', locs_lon, locs_lat)
            V_vals = get_vals_1D(GpH_columns, V_columns, sim.WRF_vinterp, locs_GpH)
            W_columns = self.get_col_3D(sim, 'wwind', locs_lon, locs_lat)
            W_vals = get_vals_1D(GpH_columns, W_columns, sim.WRF_vinterp, locs_GpH)
            #
            for i, flier_id in enumerate(ids):
                lat = locations[flier_id][0]
                lon = locations[flier_id][1]
                GpH = locations[flier_id][4]
                values[flier_id] = [lat, lon, GpH, SFCelev_vals[i], LCidx_vals[i],
                                    T_vals[i], P_vals[i], R_vals[i], U_vals[i],
                                    V_vals[i], W_vals[i]]
        return values  # dict

    def get_flier_environments(self, sim, locations, topography, landcover):
        """Interpolate WRF grids to get environmental variables at Flier locations."""
        environments = self.interpolate_space(sim, locations)
        if topography != 'WRF':
            lats = list()
            lons = list()
            for flier_id, flier in locations.items():
                lats.append(flier[0])
                lons.append(flier[1])
            elevs = topography.get_values(lons, lats)
            for i, flier_id in enumerate(locations.keys()):
                environments[flier_id][3] = elevs[i]
        if landcover != 'WRF':
            lats = list()
            lons = list()
            for flier_id, flier in locations.items():
                lats.append(flier[0])
                lons.append(flier[1])
            lc_idxs = landcover.get_values(lons, lats)
            for i, flier_id in enumerate(locations.keys()):
                environments[flier_id][4] = lc_idxs[i]
        return environments  # dict

    def get_interp_columns(self, var, interp_method, locs_lon, locs_lat):
        """Extract 1D columns at specified locations from irregular 3D grid."""
        nlayers = np.shape(var)[0]
        var_columns = np.zeros((nlayers, len(locs_lon)))
        for k in range(nlayers):
            var_layer = var[k, :, :]
            var_columns[k, :] = get_interp_vals_2D(self.lons, self.lats, var_layer,
                                                   interp_method, locs_lon, locs_lat)
        return var_columns

    def get_nearest_locs(self, locs_lon, locs_lat):
        """Get nearest row/col indexes from lat/lon values."""
        nrows, ncols = np.shape(self.lats)
        rows = np.zeros((nrows, ncols)).astype(int)
        for j in range(nrows):
            rows[j, :] = j
        cols = np.zeros((nrows, ncols)).astype(int)
        for i in range(ncols):
            cols[:, i] = i
        locs_row = get_interp_vals_2D(self.lons, self.lats, rows,
                                      'nearest', locs_lon, locs_lat)
        locs_col = get_interp_vals_2D(self.lons, self.lats, cols,
                                      'nearest', locs_lon, locs_lat)
        return locs_row, locs_col

# end WRFgrids_class.py
