"""
ENU to WGS84 translation engine
"""
import math

class CoordinateTranslator:
    def __init__(self, r_earth=6378137.0):
        self.r_earth = r_earth
        self.lat0 = None
        self.lon0 = None
        self.alt0 = None
        
    def set_anchor(self, lat0: float, lon0: float, alt0: float):
        self.lat0 = lat0
        self.lon0 = lon0
        self.alt0 = alt0
        
    def translate(self, x_cm: float, y_cm: float, z_cm: float):
        if self.lat0 is None or self.lon0 is None or self.alt0 is None:
            raise ValueError("Anchor not set")
            
        x_e = x_cm / 100.0
        y_n = y_cm / 100.0
        z_u = z_cm / 100.0
        
        delta_lat = (y_n / self.r_earth) * (180.0 / math.pi)
        delta_lon = (x_e / (self.r_earth * math.cos(math.radians(self.lat0)))) * (180.0 / math.pi)
        
        lat = self.lat0 + delta_lat
        lon = self.lon0 + delta_lon
        alt = self.alt0 + z_u
        
        return lat, lon, alt
        
    def translate_batch(self, beacons: list):
        # beacons is list of dicts with x_cm, y_cm, z_cm
        res = []
        for b in beacons:
            lat, lon, alt = self.translate(b['x_cm'], b['y_cm'], b['z_cm'])
            res.append({'lat': lat, 'lon': lon, 'alt': alt})
        return res
