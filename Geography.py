# pylint: disable=C0103,R0205,R0902,R1711
"""
Python script "Geography.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2020-2021 by Matthew Garcia
"""


from pyproj import Proj
from Map_class import Map


def get_utm_zone(lon):
    """Calculate UTM zone number."""
    zone = int(1 + (lon + 180.0) / 6.0)
    return zone


def lat_lon_to_utm(lat, lon):
    """Convert coordinates from geographic to UTM."""
    UTM_zone = get_utm_zone(lon)
    proj = Proj(proj="utm", zone=UTM_zone, ellps="WGS84", south=bool(lat < 0))
    easting, northing = proj(lon, lat)
    return easting, northing


def utm_to_lat_lon(easting, northing, UTM_zone):
    """Convert coordinates from UTM to geographic."""
    proj = Proj(proj="utm", zone=UTM_zone, ellps="WGS84", south=bool(northing < 0))
    lon, lat = proj(easting, northing, inverse=True)
    return lat, lon


def setup_topo_map(sim):
    """Initialize topography map object as indicated."""
    if sim.topography_fname == 'WRF':
        topo_map = 'WRF'
        print('initial setup : using WRF topography')
    else:
        topo_map = Map(sim, sim.topography_fname)
        print('initial setup : topography Map object initialized')
    return topo_map  # Map object or string


def setup_lc_map(sim):
    """Initialize landcover map object as indicated."""
    if sim.landcover_fname == 'WRF':
        lc_map = 'WRF'
        print('initial setup : using WRF landcover')
    else:
        lc_map = Map(sim, sim.landcover_fname)
        print('initial setup : landcover Map object initialized')
    return lc_map  # Map object or string


def setup_defoliation_map(sim):
    """Initialize defoliation map object if provided."""
    if sim.use_defoliation:
        defol_map = Map(sim, sim.defoliation_fname)
        print('initial setup : defoliation Map object initialized')
    else:
        defol_map = None
    return defol_map  # Map object or None

# end Geography.py
