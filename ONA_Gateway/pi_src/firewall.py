"""
Packet validation and filtering (Firewall)
"""
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Shared_Protocols'))
try:
    from beacon_schema import unpack_beacon
except ImportError:
    pass

class PacketFirewall:
    def __init__(self):
        self.stats = {
            'accepted': 0,
            'rejected': 0,
            'duplicates': 0,
            'rate_limited': 0
        }
        self.recent_hashes = set()
        self.recent_hashes_times = []
        self.blacklist = set()
        self.whitelist = set() # empty means all allowed if not blacklisted
        
    def validate_packet(self, raw_bytes: bytes):
        if len(raw_bytes) != 20:
            self.stats['rejected'] += 1
            return False, None, "Invalid length"
            
        parsed = unpack_beacon(raw_bytes)
        if not parsed:
            self.stats['rejected'] += 1
            return False, None, "Invalid CRC"
            
        b_id, w_id, b_type, x, y, z, ts, ttl, conf, next_id, crc = parsed
        
        if b_id in self.blacklist or (self.whitelist and b_id not in self.whitelist):
            self.stats['rejected'] += 1
            return False, None, "Beacon ID blacklisted/not whitelisted"
            
        if b_type > 3:
            self.stats['rejected'] += 1
            return False, None, "Invalid event type"
            
        now = int(time.time())
        if ts > now + 3600 or ts < now - (48 * 3600):
            self.stats['rejected'] += 1
            return False, None, "Timestamp out of sanity range"
            
        # Dup check
        if crc in self.recent_hashes:
            self.stats['duplicates'] += 1
            return False, None, "Duplicate packet"
            
        self.recent_hashes.add(crc)
        self.recent_hashes_times.append((time.time(), crc))
        self._prune_hashes()
        
        self.stats['accepted'] += 1
        return True, parsed, "OK"
        
    def _prune_hashes(self):
        now = time.time()
        while self.recent_hashes_times and now - self.recent_hashes_times[0][0] > 60:
            _, old_crc = self.recent_hashes_times.pop(0)
            if old_crc in self.recent_hashes:
                self.recent_hashes.remove(old_crc)
