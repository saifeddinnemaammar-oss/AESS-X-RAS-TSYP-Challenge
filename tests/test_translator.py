"""
Unit tests for ONA_Gateway/pi_src/translator.py (local ENU -> WGS84).

The translator uses a flat-earth (tangent-plane) approximation. These tests
only check the arithmetic of that approximation; they do not measure
real-world localisation accuracy.

Run from the repository root:
    python -m unittest discover -s tests -v
"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ONA_Gateway", "pi_src"))
from translator import CoordinateTranslator  # noqa: E402

R = 6378137.0


class TestTranslator(unittest.TestCase):

    def setUp(self):
        self.t = CoordinateTranslator(r_earth=R)
        self.t.set_anchor(34.7398, 10.7600, 15.0)  # DEFAULT_LAT0/LON0/ALT0 in config.py

    def test_origin_maps_to_anchor(self):
        self.assertEqual(self.t.translate(0, 0, 0), (34.7398, 10.7600, 15.0))

    def test_anchor_required(self):
        with self.assertRaises(ValueError):
            CoordinateTranslator().translate(0, 0, 0)

    def test_north_offset_changes_latitude_only(self):
        lat, lon, _ = self.t.translate(0, 10000, 0)  # 100 m north
        self.assertAlmostEqual(lat - 34.7398, math.degrees(100.0 / R), places=12)
        self.assertEqual(lon, 10.7600)

    def test_east_offset_changes_longitude_only(self):
        lat, lon, _ = self.t.translate(10000, 0, 0)  # 100 m east
        expected = math.degrees(100.0 / (R * math.cos(math.radians(34.7398))))
        self.assertAlmostEqual(lon - 10.7600, expected, places=12)
        self.assertEqual(lat, 34.7398)

    def test_z_is_added_in_metres(self):
        _, _, alt = self.t.translate(0, 0, 100)  # 100 cm up
        self.assertAlmostEqual(alt, 16.0, places=9)

    def test_int16_extremes(self):
        # Packet x/y are int16 centimetres -> max offset is +/-327.67 m.
        lat, lon, _ = self.t.translate(32767, -32768, 0)
        self.assertTrue(-90 <= lat <= 90 and -180 <= lon <= 180)


if __name__ == "__main__":
    unittest.main()
