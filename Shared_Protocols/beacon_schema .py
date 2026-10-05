"""
Unified Beacon Packet Schema
Ensures exact 20-byte payload alignment across the Writer, ONA Gateway, and Beacons.
Dependencies: crcmod
"""
import struct
import time

try:
    import crcmod
except ImportError:
    crcmod = None

# ---------------------------------------------------------
# Struct Format: <HBBhhbIHBH
# < : Little-endian (Crucial for ESP32 C++ memory alignment)
# H : uint16 (Beacon ID)   -> 2 bytes
# B : uint8 (Writer ID)    -> 1 byte
# B : uint8 (Event Type)   -> 1 byte
# h : int16 (X cm)         -> 2 bytes
# h : int16 (Y cm)         -> 2 bytes
# b : int8  (Z cm)         -> 1 byte
# I : uint32 (Timestamp)   -> 4 bytes
# H : uint16 (TTL)         -> 2 bytes
# B : uint8 (Confidence)   -> 1 byte
# H : uint16 (Next/Prev ID)-> 2 bytes
# ---------------------------------------------------------
# Total Payload: 18 bytes
# CRC-16 Checksum: 2 bytes
# Final Packet Size: 20 bytes
# ---------------------------------------------------------
BEACON_FMT = "<HBBhhbIHBH"

if crcmod:
    # Matches the ESP32 C++ CRC-16-CCITT implementation (Poly 0x1021, Init 0xFFFF)
    crc16_func = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xFFFF, xorOut=0x0000)
else:
    crc16_func = lambda x: 0x0000

def calc_crc16(data: bytes) -> int:
    """Calculates CCITT CRC-16 checksum."""
    return crc16_func(data)

def pack_beacon(b_id: int, w_id: int, b_type: int, x: int, y: int, z: int, ttl: int, conf: int, next_id: int) -> bytes:
    """Packs local telemetry and metadata into the 20-byte LoRa format."""
    current_ts = int(time.time()) & 0xFFFFFFFF
    
    payload = struct.pack(BEACON_FMT, b_id, w_id, b_type, x, y, z, current_ts, ttl, conf, next_id)
    crc = calc_crc16(payload)
    
    # Append the CRC using Little-Endian format
    return payload + struct.pack("<H", crc)

def unpack_beacon(raw_bytes: bytes):
    """Unpacks a 20-byte payload, returning None if the CRC-16 validation fails."""
    if len(raw_bytes) != 20:
        return None
        
    payload = raw_bytes[:18]
    # Unpack the CRC using Little-Endian format
    received_crc = struct.unpack("<H", raw_bytes[18:20])[0]
    
    if received_crc != calc_crc16(payload):
        return None
        
    unpacked = struct.unpack(BEACON_FMT, payload)
    return (*unpacked, received_crc)