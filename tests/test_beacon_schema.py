"""
Unit tests for Shared_Protocols/beacon_schema.py.

These tests check the Python side of the 20-byte beacon packet against a
direct Python port of the calculateCRC() function used in the ESP32 firmware
(Writer_Robot/esp32_src/writer_esp32.ino, Beacon_node/beacon_core.ino,
Executor_Robot/executor_core.ino, ONA_Gateway/esp32_src/ona_esp32.ino).

They do NOT test radio transmission or the firmware itself.

Run from the repository root:
    pip install crcmod==1.7
    python -m unittest discover -s tests -v
"""
import os
import random
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Shared_Protocols"))
import beacon_schema  # noqa: E402


def firmware_crc16(data: bytes) -> int:
    """Line-by-line port of calculateCRC() from the .ino files."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if (crc & 0x8000) else (crc << 1)
            crc &= 0xFFFF  # uint16_t overflow in C
    return crc


class TestBeaconSchema(unittest.TestCase):

    def test_crcmod_installed(self):
        # Without crcmod, beacon_schema silently falls back to CRC = 0x0000.
        self.assertIsNotNone(beacon_schema.crcmod,
                             "crcmod is missing: CRC would always be 0x0000")

    def test_payload_and_packet_size(self):
        self.assertEqual(struct.calcsize(beacon_schema.BEACON_FMT), 18)
        pkt = beacon_schema.pack_beacon(1, 1, 0, 0, 0, 0, 60, 255, 0)
        self.assertEqual(len(pkt), 20)

    def test_crc_standard_check_value(self):
        # CRC-16/CCITT-FALSE check value for b"123456789" is 0x29B1.
        self.assertEqual(firmware_crc16(b"123456789"), 0x29B1)
        self.assertEqual(beacon_schema.calc_crc16(b"123456789"), 0x29B1)

    def test_python_crc_matches_firmware_crc(self):
        rng = random.Random(0)
        for _ in range(500):
            payload = bytes(rng.getrandbits(8) for _ in range(18))
            self.assertEqual(beacon_schema.calc_crc16(payload), firmware_crc16(payload))

    def test_round_trip(self):
        pkt = beacon_schema.pack_beacon(b_id=101, w_id=1, b_type=1, x=1500, y=-3200,
                                        z=0, ttl=3600, conf=200, next_id=100)
        out = beacon_schema.unpack_beacon(pkt)
        self.assertIsNotNone(out)
        b_id, w_id, b_type, x, y, z, ts, ttl, conf, next_id, crc = out
        self.assertEqual((b_id, w_id, b_type, x, y, z, ttl, conf, next_id),
                         (101, 1, 1, 1500, -3200, 0, 3600, 200, 100))

    def test_crc_is_little_endian_after_payload(self):
        pkt = beacon_schema.pack_beacon(7, 1, 2, 10, 20, 0, 60, 128, 6)
        self.assertEqual(struct.unpack("<H", pkt[18:20])[0], firmware_crc16(pkt[:18]))

    def test_single_bit_error_is_rejected(self):
        pkt = bytearray(beacon_schema.pack_beacon(5, 1, 3, 100, 200, 1, 60, 99, 4))
        for i in range(20):
            for bit in range(8):
                corrupted = bytearray(pkt)
                corrupted[i] ^= 1 << bit
                self.assertIsNone(beacon_schema.unpack_beacon(bytes(corrupted)),
                                  f"bit flip at byte {i}, bit {bit} not detected")

    def test_wrong_length_is_rejected(self):
        pkt = beacon_schema.pack_beacon(5, 1, 3, 100, 200, 1, 60, 99, 4)
        self.assertIsNone(beacon_schema.unpack_beacon(pkt[:19]))
        self.assertIsNone(beacon_schema.unpack_beacon(pkt + b"\x00"))


if __name__ == "__main__":
    unittest.main()
