# pylint: disable=C0103,R0205,R0902,R1711
"""
Python script "Geography.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


from pyproj import Proj


def get_utm_zone(lon):
    """Calculate UTM zone number."""
    zone = int(1 + (lon + 180.0) / 6.0)
    return zone


def lat_lon_to_utm(lat, lon):
    """Convert coordinates from geographic to UTM."""
    UTM_zone = get_utm_zone(lon)
    proj = Proj(proj="utm", zone=UTM_zone, ellps="WGS84", south=bool(lat < 0))
    easting, northing = proj(lon, lat)
    return easting, northing, UTM_zone


def utm_to_lat_lon(easting, northing, UTM_zone):
    """Convert coordinates from UTM to geographic."""
    proj = Proj(proj="utm", zone=UTM_zone, ellps="WGS84", south=bool(northing < 0))
    lon, lat = proj(easting, northing, inverse=True)
    return lat, lon


def inside_grid(sim, lat, lon):
    """Check if moth is still within the simulation boundaries."""
    if sim.grid_min_lat <= lat <= sim.grid_max_lat:
        return True
    if sim.grid_min_lon <= lon <= sim.grid_max_lon:
        return True
    return False


def inside_init_box(sim, lat, lon):
    """Check if moth is within the desired initialization box."""
    if sim.init_flier_min_lat <= lat <= sim.init_flier_max_lat:
        return True
    if sim.init_flier_min_lon <= lon <= sim.init_flier_max_lon:
        return True
    return False

# end Geography.py
