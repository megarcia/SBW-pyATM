from datetime import datetime, timedelta, timezone as tz
from Solar_calculations import Sun


XAM_lat = 48.4783
XAM_lon = -67.5822
UTC_offset = -4.0
start_time = datetime(2013, 7, 15, 21, 0, 0, tzinfo=tz.utc)
end_time = datetime(2013, 7, 16, 10, 0, 0, tzinfo=tz.utc)


print()
print('XAM radar location:')
print('lat = %.4f' % XAM_lat)
print('lon = %.4f' % XAM_lon)
print()
sun = Sun(lat=XAM_lat, lon=XAM_lon, UTC_offset=UTC_offset)
print('simulation start = %s UTC' % start_time)
local_sunset_time = sun.sunset(when=start_time) + timedelta(hours=UTC_offset)
print('sunset = %s EDT' % local_sunset_time)
utc_sunset_time = local_sunset_time - timedelta(hours=UTC_offset)
print('sunset = %s UTC' % utc_sunset_time)
print()
print('simulation end = %s UTC' % end_time)
local_sunrise_time = sun.sunrise(when=end_time) + timedelta(hours=UTC_offset)
print('sunrise = %s EDT' % local_sunrise_time)
utc_sunrise_time = local_sunrise_time - timedelta(hours=UTC_offset)
print('sunrise = %s UTC' % utc_sunrise_time)
print()
