import sys
import time
import math

sys.path.append('../common')
from beacon_schema import unpack_beacon

def evaluate_beacon(packet: bytes):
    data = unpack_beacon(packet)
    if not data:
        return
        
    b_id, w_id, b_type, lx, ly, lz, tstamp, ttl, conf, next_id, crc = data
    age = int(time.time()) - tstamp
    
    if age > ttl:
        print(f"[EXECUTOR] Beacon {b_id} TTL expired. Purging from local costmap.")
        return
        
    effective_conf = conf * math.exp(-age / 3600.0)
    print(f"[EXECUTOR] Beacon {b_id} Verified | Age: {age}s | Effective Confidence: {effective_conf:.1f}/255")
