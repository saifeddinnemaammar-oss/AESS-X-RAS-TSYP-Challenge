"""
Build and transmit mission plans to Executor
"""
import time
import struct
import logging

class MissionBriefer:
    def __init__(self):
        pass
        
    def build_mission(self, beacon_registry: list, mission_type: str) -> dict:
        priority_map = {1: 4, 2: 3, 3: 2, 0: 1}
        sorted_beacons = sorted(beacon_registry, key=lambda b: priority_map.get(b['type'], 0), reverse=True)
        
        plan = {
            "mission_id": int(time.time()),
            "type": mission_type,
            "waypoints": [b['id'] for b in sorted_beacons],
            "targets": sorted_beacons
        }
        return plan
        
    def serialize_mission(self, plan: dict) -> list:
        chunks = []
        mission_id = plan["mission_id"] & 0xFFFF
        for w in plan["waypoints"]:
            chunk = struct.pack('<H H 16x', mission_id, w)
            chunks.append(chunk)
        return chunks
        
    def transmit_mission(self, lora_ingest, plan: dict):
        chunks = self.serialize_mission(plan)
        logging.info(f"Transmitting mission {plan['mission_id']} in {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            # Send the chunk directly to the ESP32 via the updated Ingest Daemon
            lora_ingest.transmit(chunk)
            time.sleep(0.5) # Wait for mechanical transmission and ACK
            
    def receive_executor_ack(self) -> bool:
        return True