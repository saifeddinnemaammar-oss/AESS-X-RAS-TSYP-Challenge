"""
Main ONA Gateway Daemon
"""
import argparse
import time
import logging
import signal
import sys
import os

from config import *
from lora_ingest import LoRaIngestDaemon
from gps_anchor import GPSAnchor
from translator import CoordinateTranslator
from firewall import PacketFirewall
from uplink import UplinkManager
from store_forward import StoreForwardQueue
from mission_briefer import MissionBriefer

class ONAGateway:
    def __init__(self):
        self.running = False
        
        self.lora = LoRaIngestDaemon(bus=LORA_SPI_BUS, device=LORA_SPI_DEVICE, rst_pin=LORA_RST, dio0_pin=LORA_DIO0)
        self.gps = GPSAnchor(port=GPS_UART_PORT, baudrate=GPS_BAUDRATE)
        self.translator = CoordinateTranslator(r_earth=R_EARTH)
        self.firewall = PacketFirewall()
        self.sf_queue = StoreForwardQueue(db_path=STORE_FORWARD_DB)
        self.uplink = UplinkManager(mode=UPLINK_MODE, mqtt_host=MQTT_HOST, mqtt_port=MQTT_PORT, http_url=HTTP_UPLINK_URL)
        self.uplink.set_store_forward(self.sf_queue)
        self.briefer = MissionBriefer()
        
    def start(self):
        logging.info("Starting ONA Gateway...")
        self.running = True
        
        self.lora.start()
        self.gps.start()
        self.uplink.start()
        
        # Wait for GPS fix or timeout
        logging.info("Waiting for GPS fix...")
        timeout = time.time() + 10
        while time.time() < timeout:
            if self.gps.is_valid():
                break
            time.sleep(1)
            
        if self.gps.is_valid():
            lat, lon, alt = self.gps.get_anchor()
            logging.info(f"Obtained GPS fix: {lat}, {lon}, {alt}")
        else:
            lat, lon, alt = DEFAULT_LAT0, DEFAULT_LON0, DEFAULT_ALT0
            logging.warning(f"No GPS fix, using default anchor: {lat}, {lon}, {alt}")
            
        self.translator.set_anchor(lat, lon, alt)
        
        self._run_loop()
        
    def _run_loop(self):
        last_prune = time.time()
        
        while self.running:
            try:
                # Update anchor if GPS moves
                if self.gps.is_valid():
                    lat, lon, alt = self.gps.get_anchor()
                    self.translator.set_anchor(lat, lon, alt)
                    
                # Process packets
                try:
                    packet = self.lora.packet_queue.get_nowait()
                except:
                    packet = None
                    
                if packet:
                    valid, parsed, reason = self.firewall.validate_packet(packet)
                    if valid:
                        b_id, w_id, b_type, x, y, z, ts, ttl, conf, next_id, crc = parsed
                        
                        try:
                            wgs_lat, wgs_lon, wgs_alt = self.translator.translate(x, y, z)
                            
                            payload = {
                                "beacon_id": b_id,
                                "writer_id": w_id,
                                "type": b_type,
                                "lat": wgs_lat,
                                "lon": wgs_lon,
                                "alt": wgs_alt,
                                "timestamp": ts,
                                "confidence": conf
                            }
                            
                            self.uplink.publish_beacon(payload)
                            logging.info(f"Published beacon {b_id} from writer {w_id}")
                        except Exception as e:
                            logging.error(f"Translation/Publish failed: {e}")
                    else:
                        logging.debug(f"Packet rejected: {reason}")
                        
                # Prune queue periodically
                if time.time() - last_prune > 3600:
                    self.sf_queue.prune_expired()
                    last_prune = time.time()
                    
                time.sleep(0.01)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error(f"Main loop error: {e}")
                time.sleep(1)
                
    def stop(self):
        logging.info("Stopping ONA Gateway...")
        self.running = False
        self.lora.stop()
        self.gps.stop()
        logging.info("Stopped.")

def main():
    parser = argparse.ArgumentParser(description="ONA Gateway Daemon")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--sim", action="store_true", help="Run in simulation mode")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level")
    args = parser.parse_args()
    
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {args.log_level}")
        
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    gateway = ONAGateway()
    
    def signal_handler(sig, frame):
        gateway.stop()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    gateway.start()

if __name__ == "__main__":
    main()
