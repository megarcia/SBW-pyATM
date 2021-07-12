# pylint: disable=C0103,R0912,R0913,R0914,R0915,R1711
"""
Python script "Model_wrapup.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


from Flier_summary import plot_trajectories, report_flier_statistics
from Flier_grids import grid_liftoff_locations, grid_landing_locations
from Flier_grids import grid_egg_deposition


def report_remaining_fliers(sim, clock, fliers, trajectories, egg_deposition):
    """Report status of any remaining fliers at end of simulation."""
    print('simulation wrapup : reporting status of remaining active fliers')
    for flier in fliers.values():
        if flier.active:
            trajectories = flier.report_status(sim, clock, trajectories)
        if flier.sex and flier.eggs_laid:
            for eggs_id, egg_location in flier.eggs_laid.items():
                egg_deposition[eggs_id] = egg_location
    return trajectories, egg_deposition


def report_statistics(sim, clock, flight_status, liftoff_locs):
    """Report flight statistics for all flights."""
    print('simulation wrapup : processing flight statistics')
    report_flier_statistics(sim, clock, flight_status, liftoff_locs)
    return


def report_trajectories(sim, next_grids, trajectories):
    """Plot trajectories for all flights."""
    if trajectories:
        plot_trajectories(sim, next_grids, trajectories)
    return


def report_summary_grids(sim, liftoff_locs, landing_locs, egg_dep):
    """Plot summary grids for all flights."""
    if liftoff_locs:
        grid_liftoff_locations(sim, liftoff_locs)
    if landing_locs:
        grid_landing_locations(sim, landing_locs)
    if egg_dep:
        grid_egg_deposition(sim, egg_dep)
    return

# end Model_wrapup.py
