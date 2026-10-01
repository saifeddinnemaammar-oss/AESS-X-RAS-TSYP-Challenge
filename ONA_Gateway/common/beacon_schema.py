import struct
import logging

def unpack_beacon(raw_bytes: bytes):
    """
    Unpacks the 20-byte LoRa packet struct from the Writer/Executor.
    Format matches: <H B B h h b I H B H H
    """
    if len(raw_bytes) != 20:
        logging.error(f"Schema mismatch: Expected 20 bytes, got {len(raw_bytes)}")
        return None
        
    try:
        # Unpack the little-endian C-struct
        unpacked = struct.unpack('<HBBhhbIHBHH', raw_bytes)
        return unpacked
    except struct.error as e:
        logging.error(f"Struct unpack failed: {e}")
        return None