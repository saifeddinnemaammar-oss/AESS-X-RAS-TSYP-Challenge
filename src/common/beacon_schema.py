import struct
import time
import math

BEACON_FMT = '<H B B h h b I H B H H'

def calc_crc16(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def pack_beacon(b_id, w_id, b_type, x, y, z, ttl, conf, next_id):
    timestamp = int(time.time())
    payload = struct.pack(BEACON_FMT[:-2], b_id, w_id, b_type, x, y, z, timestamp, ttl, conf, next_id)
    crc = calc_crc16(payload)
    return payload + struct.pack('<H', crc)

def unpack_beacon(packet: bytes):
    if len(packet) != 20:
        return None
    payload = packet[:-2]
    received_crc = struct.unpack('<H', packet[-2:])[0]
    if calc_crc16(payload) != received_crc:
        return None
    return struct.unpack(BEACON_FMT, packet)
