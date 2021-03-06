# pylint: disable=C0103
"""
Python script "Clock.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


from datetime import datetime, timedelta, timezone


class Clock:
    """Simulation clock in UTC."""

    def __init__(self, sim):
        self.start_dt = datetime(sim.start_year, sim.start_month, sim.start_day,
                                 sim.start_hour, sim.start_minute, 0,
                                 tzinfo=timezone.utc)
        self.start_dt_str = self.start_dt.isoformat()
        #
        self.end_dt = datetime(sim.end_year, sim.end_month, sim.end_day,
                               sim.end_hour, sim.end_minute, 0,
                               tzinfo=timezone.utc)
        self.end_dt_str = self.end_dt.isoformat()
        #
        self.UTC_offset = sim.UTC_offset
        self.start_dt_local = self.start_dt + timedelta(hours=self.UTC_offset)
        self.end_dt_local = self.end_dt + timedelta(hours=self.UTC_offset)
        #
        self.dt_interval = sim.dt
        #
        self.current_dt = self.start_dt
        self.current_dt_str = self.current_dt.isoformat()
        self.current_dt_local = self.current_dt + timedelta(hours=self.UTC_offset)
        #
        self.elapsed_time = self.current_dt - self.start_dt

    def advance_clock(self):
        """Advance simulation time by dt_interval, in seconds."""
        print('%s : advancing clock, dt = %d seconds' % (self.current_dt_str, self.dt_interval))
        self.current_dt += timedelta(seconds=self.dt_interval)
        self.current_dt_str = self.current_dt.isoformat()
        self.current_dt_local = self.current_dt + timedelta(hours=self.UTC_offset)
        self.elapsed_time = self.current_dt - self.start_dt

# end Clock.py
