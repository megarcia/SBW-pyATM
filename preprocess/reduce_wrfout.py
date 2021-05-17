# pylint: disable=C0103
"""
Python script "reduce_wrfout.py"
by Matthew Garcia, Ph.D.
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2018 by Matthew Garcia

Extract/derive specific variables from a WRF output NetCDF file
    1. Geopotential height [m]
    2. Air temperature [C]
    3. Atmospheric pressure [hPa]
    4. W [m/s]
    5. Precipitation [kg/m^2 h] is equivalent to [mm/h]
    6. U [m/s] converted to Earth-relative value
    7. V [m/s] converted to Earth-relative value
    8. Land use category
    9. Surface elevation [m]

Uses the 'wrfcube' library by Max Heikenfeld under GNU license
http://github.com/mheikenfeld/wrfcube, mailto:max.heikenfeld@physics.ox.ac.uk

Wind component rotation to Earth-relative values follows an example by
David Ovens, Department of Atmospheric Sciences, University of Washington
https://atmos.washington.edu/~ovens/wrfwinds.html, mailto:ovens@uw.edu

Get everything on an unstaggered grid for conformity.
Subset to the lowest ~1.5 km
Subset to the XAM radar coverage area (or another area) (if desired)
"""


import os
import sys
import glob
import iris
import numpy as np
import wrfcube


def message(char_string=''):
    """Print a string to the terminal and flush the buffer."""
    print char_string
    sys.stdout.flush()
    return


path = sys.argv[1]
file_idx = int(sys.argv[2])
dt = float(sys.argv[3])
ncfiles = sorted(glob.glob('%s/wrfout_d0?_*.nc' % path))
infname = ncfiles[file_idx]
os.system('cp %s .' % infname)
infname = infname.split('/')[-1]
message()
#
max_level = 10
#
# XAM radar coverage area
# min_lat = 47.396
# max_lat = 49.555
# min_lon = -69.255
# max_lon = -65.947
#
# eastern half of WRF d04
# min_lat = 44.37058258
# max_lat = 50.82014084
# min_lon = -71.76272583
# max_lon = -63.80361938
#
# read derived variables into iris.Cube
message('reading %s and calculating derived variables' % infname)
var_names = ['geopotential_height', 'temperature', 'pressure', 'w_unstaggered']
var_cubes = wrfcube.derivewrfcubelist(infname, var_names)
var_cubes[1].rename('temperature')
var_cubes[1].convert_units('celsius')
var_cubes[2].convert_units('hPa')
var_cubes[3].rename('w_unstaggered')
#
# get grid-relative U and V winds and their rotation factors
U = wrfcube.derivewrfcube(infname, 'u_unstaggered')
V = wrfcube.derivewrfcube(infname, 'v_unstaggered')
COSALPHA = wrfcube.loadwrfcube(infname, 'COSALPHA')
SINALPHA = wrfcube.loadwrfcube(infname, 'SINALPHA')
#
# calculate and append Earth-relative U and V winds
message('calculating Earth-relative winds')
U_e = U.data * COSALPHA.data - V.data * SINALPHA.data
V_e = V.data * COSALPHA.data + U.data * SINALPHA.data
U.data = U_e
U.rename('ue_unstaggered')
var_cubes.append(U)
V.data = V_e
V.rename('ve_unstaggered')
var_cubes.append(V)
#
# calculate and append upper air precipitation rate
message('calculating and adding upper air rain rate')
PRESSURE = var_cubes[2].data * 100.0
TEMPERATURE = var_cubes[1].data + 273.15
R = 287.058  # [J kg-1 K-1]
DENSITY = PRESSURE / TEMPERATURE / R
QRAIN = wrfcube.loadwrfcube(infname, 'QRAIN')
qrain_rate = QRAIN.data * DENSITY / dt
QRAIN_rate = QRAIN
QRAIN_rate.data = qrain_rate
QRAIN_rate.rename('rain')
QRAIN_rate.units = 'mm/h'
var_cubes.append(QRAIN_rate)
#
# define the height levels subset
lev_constraint = iris.Constraint(bottom_top=lambda idx: idx <= max_level)
#
# extract the subset levels
message('extracting desired levels')
var_cubes_lev_subset = iris.cube.CubeList()
for var_cube in var_cubes:
    var_cube_lev_subset = var_cube.extract(lev_constraint)
    var_cubes_lev_subset.append(var_cube_lev_subset)
#
# calculate and append surface precipitation rate
message('calculating and adding surface precipitation rate')
RAINNC = wrfcube.loadwrfcube(infname, 'RAINNC')
rainnc_rate = RAINNC.data / dt
RAINNC_rate = RAINNC
RAINNC_rate.data = rainnc_rate
RAINNC_rate.rename('precipitation')
RAINNC_rate.units = 'mm/h'
var_cubes_lev_subset.append(RAINNC_rate)
#
# copy RAINNC metadata attributes to upper air variables
# for i in range(len(var_names) + 2):
#     var_cubes_lev_subset[i].attributes = RAINNC.attributes
#
# append surface temperature
message('adding surface temperature')
T2 = wrfcube.loadwrfcube(infname, 'T2')
T2.convert_units('celsius')
var_cubes_lev_subset.append(T2)
#
# append surface pressure
message('adding surface pressure')
PSFC = wrfcube.loadwrfcube(infname, 'PSFC')
PSFC.convert_units('hPa')
var_cubes_lev_subset.append(PSFC)
#
# get grid-relative surface U and V winds
U10 = wrfcube.loadwrfcube(infname, 'U10')
V10 = wrfcube.loadwrfcube(infname, 'V10')
#
# calculate and append Earth-relative surface U and V wind
message('calculating Earth-relative surface winds')
U10_e = U10.data * COSALPHA.data - V10.data * SINALPHA.data
V10_e = V10.data * COSALPHA.data + U10.data * SINALPHA.data
U10.data = U10_e
U10.rename('U10_e')
var_cubes_lev_subset.append(U10)
V10.data = V10_e
V10.rename('V10_e')
var_cubes_lev_subset.append(V10)
#
# append surface elevation
message('adding surface elevation')
HGT = wrfcube.loadwrfcube(infname, 'HGT')
var_cubes_lev_subset.append(HGT)
#
# append land use
message('adding land use')
LU_INDEX = wrfcube.loadwrfcube(infname, 'LU_INDEX')
var_cubes_lev_subset.append(LU_INDEX)
#
# define a subset area in terms of the grid coordinates (rows and columns)
"""
message('defining subset area')
lat = var_cubes_lev_subset[0].coord('latitude').points[0]
lat_subset = np.where(lat <= min_lat, -9999, lat)
lat_subset = np.where(lat_subset >= max_lat, -9999, lat_subset)
idxs = np.where(lat_subset != -9999)
min_sn_idx = np.min(idxs[0])
max_sn_idx = np.max(idxs[0])
lat_constraint = iris.Constraint(south_north=lambda idx: min_sn_idx <= idx <= max_sn_idx)
#
lon = var_cubes_lev_subset[0].coord('longitude').points[0]
lon_subset = np.where(lon <= min_lon, -9999, lon)
lon_subset = np.where(lon_subset >= max_lon, -9999, lon_subset)
idxs = np.where(lon_subset != -9999)
min_we_idx = np.min(idxs[1])
max_we_idx = np.max(idxs[1])
lon_constraint = iris.Constraint(west_east=lambda idx: min_we_idx <= idx <= max_we_idx)
#
# extract the subset area
message('extracting subset area')
var_cubes_lev_lat_lon_subset = iris.cube.CubeList()
for var_cube in var_cubes_lev_subset:
    var_cube_lat_subset = var_cube.extract(lat_constraint)
    var_cube_lat_lon_subset = var_cube_lat_subset.extract(lon_constraint)
    var_cubes_lev_lat_lon_subset.append(var_cube_lat_lon_subset)
"""
#
# write the output NetCDF file
outfname = 'wrfout_subset_%s' % ('_'.join(infname.split('_')[1:]))
message('saving data to %s' % outfname)
# iris.save(var_cubes_lev_lat_lon_subset, outfname)
iris.save(var_cubes_lev_subset, outfname)
message()
#
# clean up around the place
os.system('cp %s %s/reduced/' % (outfname, path))
os.system('rm %s' % infname)
os.system('rm %s' % outfname)
message('done!')
#
sys.exit(0)
