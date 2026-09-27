"""
Message protocol layer on top of beacon_schema for the Living Map USAR project.
"""

import struct
from . import beacon_schema

# Message Types
MSG_BEACON_PULSE = 0x01
MSG_BEACON_ACK = 0x02
MSG_MISSION_PLAN = 0x03
MSG_STATUS_REPORT = 0x04
MSG_TELEMETRY = 0x05

# Rate Limiting (seconds)
RL_BEACON_PULSE = 3.0
RL_TELEMETRY = 1.0

def pack_ack(beacon_id, status=0):
    """
    ACK packet format: 4 bytes
    Byte 0: Type (0x02)
    Byte 1-2: Beacon ID (uint16_le)
    Byte 3: Status (0=OK, 1=FAIL)
    """
    return struct.pack('<B H B', MSG_BEACON_ACK, beacon_id, status)

def unpack_ack(packet):
    if len(packet) != 4:
        return None
    msg_type, beacon_id, status = struct.unpack('<B H B', packet)
    if msg_type != MSG_BEACON_ACK:
        return None
    return {'beacon_id': beacon_id, 'status': status}

def serialize_mission_plan(plan_data):
    """
    Mission plan serialization (variable length).
    Format:
    Byte 0: Type (0x03)
    Byte 1: Num Checkpoints (N)
    Following N * 4 bytes: X, Y (int16_le, int16_le)
    """
    encoded = struct.pack('<B B', MSG_MISSION_PLAN, len(plan_data))
    for x, y in plan_data:
        encoded += struct.pack('<h h', x, y)
    return encoded

def deserialize_mission_plan(packet):
    if len(packet) < 2 or packet[0] != MSG_MISSION_PLAN:
        return None
    num_pts = packet[1]
    if len(packet) != 2 + (num_pts * 4):
        return None
    
    plan = []
    for i in range(num_pts):
        offset = 2 + (i * 4)
        x, y = struct.unpack('<h h', packet[offset:offset+4])
        plan.append((x, y))
    return plan

def route_packet(packet):
    """
    Packet routing by message type.
    """
    if not packet:
        return None, None
        
    if len(packet) == 20: # 20-byte beacon pulse is implicit by length + valid CRC
        beacon = beacon_schema.unpack_beacon(packet)
        if beacon:
            return MSG_BEACON_PULSE, beacon
            
    if packet[0] == MSG_BEACON_ACK:
        return MSG_BEACON_ACK, unpack_ack(packet)
    elif packet[0] == MSG_MISSION_PLAN:
        return MSG_MISSION_PLAN, deserialize_mission_plan(packet)
        
    # Add other routing as needed
    return None, None
