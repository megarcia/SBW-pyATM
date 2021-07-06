# pylint: disable=C0103
"""
Python script "Clock.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


from datetime import timedelta


class Clock():
    """Simulation clock in UTC."""

    def __init__(self, sim):
        self.start_dt = sim.start_time
        self.start_dt_str = self.start_dt.isoformat()
        self.end_dt = sim.end_time
        self.end_dt_str = self.end_dt.isoformat()
        self.dt_interval = sim.dt
        self.current_dt = sim.start_time
        self.current_dt_str = self.current_dt.isoformat()

    def advance_clock(self):
        """Advance simulation time by dt_interval, in seconds."""
        print('%s : advancing clock, dt = %d seconds' % (self.current_dt_str, self.dt_interval))
        self.current_dt += timedelta(seconds=self.dt_interval)
        self.current_dt_str = self.current_dt.isoformat()

# end Clock.py
