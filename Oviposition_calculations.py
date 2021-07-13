# pylint: disable=C0103
"""
Python script "Oviposition_calculations.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


def update_flier_morphology(sbw, flier):
    """Lay eggs and update moth fecundity, gravidity, and mass.
       F_frac_per_brood to be replaced with detailed calculation of
       n_eggs laid according to daytime temperature formulation."""
    n_eggs = int(flier.fecundity * sbw.F_frac_per_brood)
    eggs_laid_str = '%s_%d' % (flier.flier_id, flier.nflights)
    flier.eggs_laid[eggs_laid_str] = [flier.lat, flier.lon, flier.UTM_zone,
                                      flier.easting, flier.northing, n_eggs]
    flier.fecundity -= n_eggs
    flier.gravidity = flier.fecundity / flier.fecundity_0
    flier.mass = sbw.calc_mass_from_gravidity(flier.forewing_A, flier.gravidity,
                                              flier.mass_err)
    flier.calc_AM_ratio()


def oviposition(sim, sbw, fliers):
    """Determine if oviposition occurs and update moth status accordingly."""
    for flier in fliers.values():
        if flier.sex:
            if flier.lc_type == 'null':
                flier.update_state('EXIT')
            elif flier.lc_type == 'HOST_FOREST':
                flier.update_state('OVIPOSITION')
                update_flier_morphology(sbw, flier)
                if flier.gravidity <= 0.01:
                    flier.update_state('SPENT')
                else:
                    flier.update_empirical_values(sim, sbw)
            elif flier.lc_type == 'OTHER_FOREST':
                flier.prev_state = 'FOREST'
            elif flier.lc_type == 'NONFOREST':
                flier.prev_state = 'NONFOREST'

# end Oviposition_calculations.py
