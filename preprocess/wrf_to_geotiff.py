# pylint: disable=C0103
"""
Python script "wrf_to_geotiff.py"
by Matthew Garcia, Ph.D.
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2018 by Matthew Garcia
"""


import sys
import numpy as np
import xarray as xr
from scipy.interpolate import griddata
from netCDF4 import Dataset
from osgeo import gdal
from wrf import to_np, getvar, latlon_coords


all_vars = [['LU_INDEX', 'MODIS/IGBP LC'],
            ['LAI', 'MODIS LAI'],
            ['LAI12M', 'MODIS LAI'],
            ['GREENFRAC', 'MODIS Greenness Fraction'],
            ['ALBEDO12M', 'MODIS Albedo'],
            ['HGT_M', 'Sfc Elev (m)'],
            ['GHT', 'Geopotential Hgt (m)'],
            ['T2', '$T_{sfc}$ (K)'],
            ['U10', '$U_{sfc}$ (m s$^{-1}$)'],
            ['V10', '$V_{sfc}$ (m s$^{-1}$)'],
            ['sfcwind', '$sfc wind$ (m s$^{-1}$)']]


def message(char_string=''):
    """Print a string to the terminal and flush the buffer."""
    print char_string
    sys.stdout.flush()
    return


ncfname = sys.argv[1]
var_req = sys.argv[2]
found = 0
for var in all_vars:
    if var_req == var[0]:
        varname = var
        found = 1
        continue
if not found:
    message('requested variable %s not implemented yet' % var_req)
    sys.exit(0)
if ncfname.split('/')[-1][:6] == 'wrfout':
    grid_num = int(ncfname.split('/')[-1].split('.')[0].split('_')[1][-1])
    date_str = ncfname.split('/')[-1].split('.')[0].split('_')[2]
    time_str = ncfname.split('/')[-1].split('.')[0].split('_')[3][:-3]
elif ncfname.split('/')[-1][:6] == 'met_em':
    grid_num = int(ncfname.split('/')[-1].split('.')[1][-1])
    date_str = ncfname.split('/')[-1].split('.')[2].split('_')[0]
    time_str = ncfname.split('/')[-1].split('.')[2].split('_')[1][:-3]
message('grid number %d' % grid_num)
#
# Open the NetCDF file
message('reading %s' % ncfname)
ncfile = Dataset(ncfname, 'r')
#
# Get (and/or calculate) requested variable
message('getting variable %s' % varname[0])
if varname[0] == 'sfcwind':
    wind = lambda x, y: np.sqrt(x**2 + y**2)
    uvar = getvar(ncfile, 'U10')
    vvar = getvar(ncfile, 'V10')
    var = xr.apply_ufunc(wind, uvar, vvar)
    var.attrs['projection'] = uvar.attrs['projection']
elif varname[0] in ['LAI12M', 'GREENFRAC', 'ALBEDO12M', 'GHT']:
    var = getvar(ncfile, varname[0])
    var = var[0, :, :]
else:
    var = getvar(ncfile, varname[0])
#
arr_in = np.flipud(to_np(var))  # numpy datatype
message('array min = %.3f' % np.min(arr_in))
message('array max = %.3f' % np.max(arr_in))
lats, lons = latlon_coords(var)  # xarray datatype
lats = np.flipud(np.array(lats))
lons = np.flipud(np.array(lons))
min_lon = np.max(lons[:, 0])
message('min lon = %.8f' % min_lon)
max_lon = np.min(lons[:, -1])
message('max lon = %.8f' % max_lon)
dx = 0.012704865963664  # 1 km at 45 degrees latitude
if grid_num == 3:
    dx = 3 * dx
message('dx = %.12f' % dx)
ndx = int((max_lon - min_lon) / dx) + 1
adj_max_lon = min_lon + (ndx - 1) * dx
message('adjusted max lon = %.8f' % adj_max_lon)
xlon, xstep = np.linspace(min_lon, adj_max_lon, ndx, retstep=True)
message('xlon has %d elements' % len(xlon))
message('dxlon = %.12f' % xstep)
min_lat = np.max(lats[-1, :])
message('min lat = %.8f' % min_lat)
max_lat = np.min(lats[0, :])
message('max lat = %.8f' % max_lat)
dy = 0.012704865963664  # 1 km at 45 degrees latitude
if grid_num == 3:
    dy = 3 * dy
message('dy = %.12f' % dy)
ndy = int((max_lat - min_lat) / dy) + 1
adj_min_lat = max_lat - (ndy - 1) * dy
message('adjusted min lat = %.8f' % adj_min_lat)
ylat, ystep = np.linspace(max_lat, adj_min_lat, ndy, retstep=True)
message('ylat has %d elements' % len(ylat))
message('dylat = %.12f' % ystep)
#
message('lons shape = %s' % str(np.shape(lons)))
message('lats shape = %s' % str(np.shape(lats)))
message('arr_in shape = %s' % str(np.shape(arr_in)))
message('regridding %s data' % var_req)
arr_out = griddata((lons.flatten(), lats.flatten()), arr_in.flatten(),
                   (xlon[None,:], ylat[:,None]), method='nearest') #, fill_value=-9999)
nrows, ncols = np.shape(arr_out)
message('arr_out shape = %s' % str(np.shape(arr_out)))
message('arr_out min = %.3f' % np.min(arr_out))
message('arr_out max = %.3f' % np.max(arr_out))
#
# create output GeoTIFF file
outfname = '%s_%s.tif' % (ncfname[:-3], varname[0])
driver = gdal.GetDriverByName("GTiff")
nbands = 1
outdata = driver.Create(outfname, ysize=nrows, xsize=ncols, bands=nbands, eType=gdal.GDT_Float64)
outdata.SetGeoTransform((min_lon, dx, 0.0, max_lat, 0.0, -dy))
proj_str = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]'
outdata.SetProjection(proj_str)
outdata.GetRasterBand(1).WriteArray(arr_out)
outdata.GetRasterBand(1).SetNoDataValue(-9999)
outdata.FlushCache() # saves to disk!!
message('wrote %s' % outfname)

# end wrf_to_geotiff.py
