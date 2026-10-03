"""
LoRa Packet Ingestion Daemon for ONA Gateway (Serial to ESP32 Firewall)
"""
import threading
import queue
import time
import logging
from typing import Dict, Optional
import serial

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Shared_Protocols'))
try:
    from beacon_schema import unpack_beacon
except ImportError:
    pass

class LoRaIngestDaemon:
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.packet_queue = queue.Queue()
        self.running = False
        self.thread = None
        self.esp_serial = None
        self.stats = {
            'received': 0,
            'valid': 0,
            'invalid_len': 0,
            'invalid_crc': 0,
            'rate_limited': 0
        }
        self.source_rates: Dict[int, list] = {}
        
    def setup_hardware(self):
        try:
            self.esp_serial = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2) # Wait for ESP32 to reboot
            logging.info("Connected to ESP32 RF Firewall.")
        except Exception as e:
            logging.error(f"ESP32 Serial setup failed: {e}")

    def _check_rate_limit(self, source_id: int) -> bool:
        now = time.time()
        if source_id not in self.source_rates:
            self.source_rates[source_id] = []
        self.source_rates[source_id] = [t for t in self.source_rates[source_id] if now - t < 1.0]
        
        if len(self.source_rates[source_id]) >= 10: 
            return False
        self.source_rates[source_id].append(now)
        return True

    def _loop(self):
        self.setup_hardware()
        logging.info("LoRa Ingest Daemon started")
        while self.running:
            if self.esp_serial and self.esp_serial.in_waiting > 0:
                try:
                    line = self.esp_serial.readline().decode('utf-8').strip()
                    if line.startswith("VALID_PKT:"):
                        self.stats['received'] += 1
                        hex_data = line.split(":")[1]
                        packet = bytes.fromhex(hex_data)
                        
                        # Forward to the firewall queue
                        self.packet_queue.put(packet)
                        self.stats['valid'] += 1
                    elif line.startswith("WARN"):
                        logging.debug(f"[ESP32 Firewall] {line}")
                except Exception as e:
                    logging.error(f"Serial read error: {e}")
            time.sleep(0.01)

    def transmit(self, payload_bytes: bytes):
        """Sends data out via the ESP32 LoRa transmitter."""
        if self.esp_serial:
            hex_str = payload_bytes.hex()
            self.esp_serial.write(f"TX:{hex_str}\n".encode('utf-8'))
            logging.info(f"Delegated transmission to ESP32: {len(payload_bytes)} bytes")
            
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.esp_serial:
            self.esp_serial.close()
            
    def get_stats(self) -> Dict[str, int]:
        return self.stats