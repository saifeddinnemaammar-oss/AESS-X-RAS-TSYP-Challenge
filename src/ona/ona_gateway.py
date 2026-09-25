import sys
import math
import json
import time

sys.path.append('../common')
from beacon_schema import unpack_beacon

R_EARTH = 6378137.0
LAT0, LON0, ALT0 = 34.7398, 10.7600, 15.0  

def translate_enu_to_wgs84(x_cm, y_cm, z_cm):
    x_e, y_n, z_u = x_cm / 100.0, y_cm / 100.0, z_cm / 100.0
    lat = LAT0 + (y_n / R_EARTH) * (180 / math.pi)
    lon = LON0 + (x_e / (R_EARTH * math.cos(math.radians(LAT0)))) * (180 / math.pi)
    return lat, lon, ALT0 + z_u

def process_incoming_rf(packet: bytes):
    data = unpack_beacon(packet)
    if not data:
        print("[FIREWALL] Packet dropped. Invalid length or CRC mismatch.")
        return
        
    b_id, w_id, b_type, lx, ly, lz, tstamp, ttl, conf, next_id, crc = data
    lat, lon, alt = translate_enu_to_wgs84(lx, ly, lz)
    
    payload = {
        "beacon_id": b_id,
        "type": b_type,
        "wgs84": {"lat": round(lat, 6), "lon": round(lon, 6), "alt": round(alt, 1)},
        "confidence": conf
    }
    print(f"[ONA UPLINK] Forwarding to Command Post: {json.dumps(payload)}")
