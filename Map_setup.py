# pylint: disable=C0103,R0205,R0902,R1711
"""
Python script "Map_setup.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2020 by Matthew Garcia
"""


from Map_class import Map
from message_fn import message


def setup_topo_map(sim):
    """Initialize topography map object as indicated."""
    if sim.topography_fname == 'WRF':
        topo_map = 'WRF'
        message('initial setup : using WRF topography')
    else:
        topo_map = Map(sim, sim.topography_fname)
        message('initial setup : topography Map object initialized')
    return topo_map  # Map object or string


def setup_lc_map(sim):
    """Initialize landcover map object as indicated."""
    if sim.landcover_fname == 'WRF':
        lc_map = 'WRF'
        message('initial setup : using WRF landcover')
    else:
        lc_map = Map(sim, sim.landcover_fname)
        message('initial setup : landcover Map object initialized')
    return lc_map  # Map object or string


def setup_defoliation_map(sim):
    """Initialize defoliation map object if provided."""
    if sim.use_defoliation:
        defol_map = Map(sim, sim.defoliation_fname)
        message('initial setup : defoliation Map object initialized')
    else:
        defol_map = None
    return defol_map  # Map object or None

# end Map_setup.py
