class Point:
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def __str__(self) -> str:
        return '({}, {})'.format(self.lat, self.lon)


class Area:
    def __init__(self, nw: Point, se: Point):
        self.southwest_lat = nw.lat
        self.southwest_lon = nw.lon
        self.northeast_lat = se.lat
        self.northeast_lon = se.lon

    def __str__(self) -> str:
        """Allows to unpack data this way: *area"""
        return '{}, {}, {}, {}'.format(self.southwest_lat, self.southwest_lon,
                                       self.northeast_lat, self.northeast_lon)

    def __iter__(self):
        return (coord for coord in (self.southwest_lat,
                                    self.northeast_lat, self.southwest_lon, self.northeast_lon))


class Waypoint:
    """Class for collecting aircraft checkins on the map."""
    def __init__(self, latitude, longitude, altitude, speed, heading, timestamp):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.speed = speed
        self.heading = heading
        self.timestamp = timestamp

    def __str__(self) -> str:
        return '{} {}'.format(self.latitude, self.longitude)

    def __eq__(self, other):
        if self.latitude != other.latitude \
                or self.longitude != other.longitude \
                or self.altitude != other.altitude \
                or self.speed != other.speed \
                or self.heading != other.heading:
            return False
        return True
