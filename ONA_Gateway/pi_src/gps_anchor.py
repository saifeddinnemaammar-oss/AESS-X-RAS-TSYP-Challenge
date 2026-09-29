"""
UART GNSS reader for the u-blox NEO-M9N
"""
import serial
import threading
import time
import logging

class GPSAnchor:
    def __init__(self, port="/dev/ttyAMA0", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.lat = None
        self.lon = None
        self.alt = None
        self.fix_quality = 0
        self.num_sats = 0
        self.hdop = 99.99
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        
    def _parse_nmea_coord(self, val: str, dir: str) -> float:
        if not val or not dir:
            return 0.0
        # Format: ddmm.mmmm
        dot_idx = val.find('.')
        if dot_idx == -1: return 0.0
        deg = float(val[:dot_idx-2])
        mins = float(val[dot_idx-2:])
        dec = deg + (mins / 60.0)
        if dir in ['S', 'W']:
            dec = -dec
        return dec
        
    def _loop(self):
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=1)
        except Exception as e:
            logging.error(f"Failed to open GPS port {self.port}: {e}")
            return
            
        while self.running:
            try:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if not line:
                    continue
                parts = line.split(',')
                if line.startswith('$GPGGA') or line.startswith('$GNGGA'):
                    if len(parts) >= 15:
                        lat_val = parts[2]
                        lat_dir = parts[3]
                        lon_val = parts[4]
                        lon_dir = parts[5]
                        fix_q = int(parts[6]) if parts[6] else 0
                        sats = int(parts[7]) if parts[7] else 0
                        hdop_val = float(parts[8]) if parts[8] else 99.99
                        alt_val = float(parts[9]) if parts[9] else 0.0
                        
                        with self.lock:
                            self.fix_quality = fix_q
                            self.num_sats = sats
                            self.hdop = hdop_val
                            if fix_q > 0:
                                self.lat = self._parse_nmea_coord(lat_val, lat_dir)
                                self.lon = self._parse_nmea_coord(lon_val, lon_dir)
                                self.alt = alt_val
            except Exception as e:
                logging.error(f"GPS read error: {e}")
                time.sleep(1)
        ser.close()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            
    def get_anchor(self):
        with self.lock:
            return self.lat, self.lon, self.alt
            
    def get_fix_quality(self) -> int:
        with self.lock:
            return self.fix_quality
            
    def is_valid(self) -> bool:
        with self.lock:
            return self.fix_quality > 0 and self.lat is not None and self.lon is not None
