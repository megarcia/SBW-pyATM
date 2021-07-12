# pylint: disable=C0103,R0205,R0902,R0914,W0621
"""
Calculation of solar noon, sunrise, sunset

from
http://michelanders.blogspot.ru/2010/12/calulating-sunrise-and-sunset-in-python.html

modified slightly by
Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com
"""


from datetime import datetime, time, timedelta, timezone as tz
from numpy import cos, sin, arccos, arcsin, tan
from numpy import rad2deg as deg
from numpy import deg2rad as rad


class Sun(object):
    """
    Calculate sunrise and sunset based on equations from NOAA
    http://www.srrb.noaa.gov/highlights/sunrise/calcdetails.html
    typical use, calculating the sunrise on the present day:
        import datetime
        from Sun_Times import Sun
        s = Sun(lat=49, lon=3)
        print('sunrise is at ',s.sunrise(when=datetime.datetime.now())
    """

    def __init__(self, lat=0.0, lon=0.0, UTC_offset=0.0):
        self.lat = lat
        self.lon = lon
        self.UTC_offset = UTC_offset
        self.day = None
        self.date = None
        self.time_frac = None
        self.timezone = UTC_offset
        self.solarnoon_t = None
        self.sunset_t = None
        self.sunrise_t = None

    def sunrise(self, when=None):
        """
        return the time of local sunrise as a datetime.time object
        when is a datetime.datetime object.
        """
        if when is None:
            when = datetime.now()
        self.__preptime(when)
        self.__calc()
        sunrise_time, day_offset = Sun.__timefromdecimalday(self.sunrise_t)
        sunrise_time = datetime.combine(self.date, sunrise_time) + timedelta(days=day_offset)
        return sunrise_time

    def sunset(self, when=None):
        """
        return the time of local sunset as a datetime.time object
        when is a datetime.datetime object.
        """
        if when is None:
            when = datetime.now()
        self.__preptime(when)
        self.__calc()
        sunset_time, day_offset = Sun.__timefromdecimalday(self.sunset_t)
        sunset_time = datetime.combine(self.date, sunset_time) + timedelta(days=day_offset)
        return sunset_time

    def solarnoon(self, when=None):
        """
        return the time of local solar noon as a datetime.time object
        when is a datetime.datetime object.
        """
        if when is None:
            when = datetime.now()
        self.__preptime(when)
        self.__calc()
        solarnoon_time, day_offset = Sun.__timefromdecimalday(self.solarnoon_t)
        solarnoon_time = datetime.combine(self.date, solarnoon_time) + timedelta(days=day_offset)
        return solarnoon_time

    @staticmethod
    def __timefromdecimalday(day):
        """
        returns a datetime.time object.
        day is a decimal day between 0.0 and 1.0, e.g. noon = 0.5
        """
        day_offset = 0
        if day < 0.0:
            day_offset = -1.0
        if day >= 1.0:
            day_offset = 1.0
        day -= day_offset
        hours = 24.0 * day
        h = int(hours)
        minutes = (hours - h) * 60.0
        m = int(minutes)
        seconds = (minutes - m) * 60.0
        s = int(seconds)
        return time(hour=h, minute=m, second=s), day_offset

    def __preptime(self, when):
        """
        Extract information in a suitable format from when,
        a datetime.datetime object.
        """
        # datetime days are numbered in the Gregorian calendar
        # while the calculations from NOAA are distributed as
        # OpenOffice spreadsheets with days numbered from
        # 1/1/1900. The difference are those numbers taken for
        # 18/12/2010
        self.day = when.toordinal() - (734124.0 - 40529.0)
        t = when.time()
        self.date = when.date()
        self.time_frac = (t.hour + t.minute / 60.0 + t.second / 3600.0) / 24.0
        offset = when.utcoffset()
        if offset is not None:
            self.timezone = offset.seconds / 3600.0 + (offset.days * 24.0)

    def __calc(self):
        """
        Perform the actual calculations for solar noon, sunrise, and sunset.
        """
        timezone = self.timezone    # in hours, east is positive
        longitude = self.lon        # in decimal degrees, east is positive
        latitude = self.lat         # in decimal degrees, north is positive
        time_frac = self.time_frac  # percentage past midnight, i.e. noon is 0.5
        day = self.day              # daynumber 1 = 1 Jan 1900
        Jday = day + 2415018.5 + time_frac - timezone / 24.0  # Julian day
        Jcent = (Jday - 2451545.0) / 36525.0                  # Julian century
        Manom = 357.52911 + Jcent * (35999.05029 - 0.0001537 * Jcent)
        Mlong = 280.46646 + Jcent * (36000.76983 + Jcent * 0.0003032) % 360.0
        Eccent = 0.016708634 - Jcent * (0.000042037 + 0.0001537 * Jcent)
        Mobliq = 23.0 + (26.0 + (21.448 - Jcent *
                                 (46.815 + Jcent * (0.00059 - Jcent * 0.001813))) / 60.0) / 60.0
        obliq = Mobliq + 0.00256 * cos(rad(125.04 - 1934.136 * Jcent))
        vary = tan(rad(obliq / 2.0)) * tan(rad(obliq / 2.0))
        Seqcent = sin(rad(Manom)) * (1.914602 - Jcent * (0.004817 + 0.000014 * Jcent)) \
            + sin(rad(2.0 * Manom)) * (0.019993 - 0.000101 * Jcent) + sin(rad(3.0 * Manom)) \
            * 0.000289
        Struelong = Mlong + Seqcent
        Sapplong = Struelong - 0.00569 - 0.00478 * sin(rad(125.04 - 1934.136 * Jcent))
        declination = deg(arcsin(sin(rad(obliq)) * sin(rad(Sapplong))))
        eqtime = 4.0 * deg(vary * sin(2.0 * rad(Mlong)) - 2.0 * Eccent * sin(rad(Manom)) +
                           4.0 * Eccent * vary * sin(rad(Manom)) * cos(2.0 * rad(Mlong)) -
                           0.5 * vary * vary * sin(4.0 * rad(Mlong)) -
                           1.25 * Eccent * Eccent * sin(2.0 * rad(Manom)))
        hourangle = deg(arccos(cos(rad(90.833)) / (cos(rad(latitude)) * cos(rad(declination))) -
                               tan(rad(latitude)) * tan(rad(declination))))
        self.solarnoon_t = (720.0 - 4.0 * longitude - eqtime + timezone * 60.0) / 1440.0
        self.sunrise_t = self.solarnoon_t - hourangle * 4.0 / 1440.0
        self.sunset_t = self.solarnoon_t + hourangle * 4.0 / 1440.0


def update_suntimes(clock, flier):
    """Update sunset/sunrise times based on location."""
    sun = Sun(lat=flier.lat, lon=flier.lon, UTC_offset=clock.UTC_offset)
    flier.local_sunset_time = sun.sunset(when=clock.start_dt) + \
        timedelta(hours=clock.UTC_offset)
    flier.utc_sunset_time = flier.local_sunset_time - \
        timedelta(hours=clock.UTC_offset)
    flier.utc_sunset_time = flier.utc_sunset_time.replace(tzinfo=tz.utc)
    flier.local_sunrise_time = sun.sunrise(when=clock.end_dt) + \
        timedelta(hours=clock.UTC_offset)
    flier.utc_sunrise_time = flier.local_sunrise_time - \
        timedelta(hours=clock.UTC_offset)
    flier.utc_sunrise_time = flier.utc_sunrise_time.replace(tzinfo=tz.utc)


def test():
    """Run a quick test for sunset/sunrise times at the specified radar location."""
    from Simulation_specifications import Simulation
    from Clock import Clock
    sim = Simulation()
    clock = Clock(sim)
    print()
    print('at XAM radar location:')
    print()
    sun = Sun(lat=sim.radar_lat, lon=sim.radar_lon, UTC_offset=clock.UTC_offset)
    print('start =', clock.start_dt_str)
    local_sunset_time = sun.sunset(when=clock.start_dt) + timedelta(hours=clock.UTC_offset)
    print('local sunset = ', local_sunset_time)
    utc_sunset_time = local_sunset_time - timedelta(hours=clock.UTC_offset)
    print('UTC sunset = ', utc_sunset_time)
    print()
    print('end =', clock.end_dt_str)
    local_sunrise_time = sun.sunrise(when=clock.end_dt) + timedelta(hours=clock.UTC_offset)
    print('local sunrise = ', local_sunrise_time)
    utc_sunrise_time = local_sunrise_time - timedelta(hours=clock.UTC_offset)
    print('UTC sunrise = ', utc_sunrise_time)
    print()


if __name__ == "__main__":
    test()
    #
    # s = Sun(lat=43.058923, lon=-89.502096, UTC_offset=-5.0)  # Madison, WI
    # print 'today is %s' % datetime.today()
    # print 'sunrise at %s local time' % s.sunrise()
    # print 'solar noon at %s local time' % s.solarnoon()
    # print 'sunset at %s local time' % s.sunset()
    # print s.sunrise() < s.sunset()
    # print s.sunset() < s.solarnoon()

# end Solar_calculations.py
