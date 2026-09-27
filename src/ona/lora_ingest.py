"""
LoRa Packet Ingestion Daemon for ONA Gateway
"""
import threading
import queue
import time
import logging
from typing import Dict, Optional
import spidev

try:
    import RPi.GPIO as GPIO
except ImportError:
    pass

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
try:
    from beacon_schema import unpack_beacon, BEACON_FMT, calc_crc16
except ImportError:
    pass

class LoRaIngestDaemon:
    def __init__(self, bus: int = 0, device: int = 0, rst_pin: int = 22, dio0_pin: int = 25):
        self.bus = bus
        self.device = device
        self.rst_pin = rst_pin
        self.dio0_pin = dio0_pin
        
        self.packet_queue = queue.Queue()
        self.running = False
        self.thread = None
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
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.rst_pin, GPIO.OUT)
            GPIO.output(self.rst_pin, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(self.rst_pin, GPIO.LOW)
            time.sleep(0.1)
            GPIO.output(self.rst_pin, GPIO.HIGH)
            
            GPIO.setup(self.dio0_pin, GPIO.IN)
            
            self.spi = spidev.SpiDev()
            self.spi.open(self.bus, self.device)
            self.spi.max_speed_hz = 5000000
        except Exception as e:
            logging.error(f"LoRa HW setup failed: {e}")

    def _read_packet(self) -> Optional[bytes]:
        # Stub for actually reading from SX1302/1276 via SPI
        # This requires reading FIFO.
        return b''
        
    def _check_rate_limit(self, source_id: int) -> bool:
        now = time.time()
        if source_id not in self.source_rates:
            self.source_rates[source_id] = []
        
        # Keep only timestamps from last 1 second
        self.source_rates[source_id] = [t for t in self.source_rates[source_id] if now - t < 1.0]
        
        if len(self.source_rates[source_id]) >= 10:  # MAX_PACKETS_PER_SEC
            return False
            
        self.source_rates[source_id].append(now)
        return True

    def _loop(self):
        self.setup_hardware()
        logging.info("LoRa Ingest Daemon started")
        while self.running:
            try:
                # Polling DIO0 or block
                # if GPIO.input(self.dio0_pin) == GPIO.HIGH:
                packet = self._read_packet()
                if packet:
                    self.stats['received'] += 1
                    
                    if len(packet) != 20:
                        self.stats['invalid_len'] += 1
                        continue
                        
                    parsed = unpack_beacon(packet)
                    if not parsed:
                        self.stats['invalid_crc'] += 1
                        continue
                        
                    beacon_id, writer_id = parsed[0], parsed[1]
                    source_id = (writer_id << 16) | beacon_id
                    
                    if not self._check_rate_limit(source_id):
                        self.stats['rate_limited'] += 1
                        continue
                        
                    self.stats['valid'] += 1
                    self.packet_queue.put(packet)
            except Exception as e:
                logging.error(f"LoRa read error: {e}")
            time.sleep(0.01)
            
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        try:
            self.spi.close()
        except:
            pass
            
    def get_stats(self) -> Dict[str, int]:
        return self.stats
