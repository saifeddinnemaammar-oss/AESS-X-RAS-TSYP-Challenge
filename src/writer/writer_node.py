import sys
import time

sys.path.append('../common')
from beacon_schema import pack_beacon

beacon_id = 1

def sensor_fusion_pipeline(thermal_c, co2_ppm):
    if thermal_c > 34.0 and co2_ppm > 1000:
        return 1 
    elif thermal_c > 55.0:
        return 2 
    return 0 

def trigger_drop(local_x_cm, local_y_cm, event_type):
    global beacon_id
    ttl = 7200 if event_type == 1 else 1800
    conf = 240 
    
    packet = pack_beacon(beacon_id, 1, event_type, local_x_cm, local_y_cm, 0, ttl, conf, 0)
    print(f"[WRITER] Dropped Beacon ID {beacon_id} | Type: {event_type} | Packet size: {len(packet)} bytes")
    beacon_id += 1
    return packet
