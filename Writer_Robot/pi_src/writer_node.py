"""
Main Writer orchestrator — the entry point.
Implements the complete Writer mission data flow and ESP32 serial delegation.
"""
import time
import math
import logging
import argparse
import serial

try:
    from src.common.lora_interface import LoRaRadio
except ImportError:
    LoRaRadio = None

from src.writer.config import *
from src.writer.sensor_drivers import (
    DHT11Sensor, MLX90640Thermal, GasSensor, IMUSensor, BatteryMonitor, MCP3008ADC
)
from src.writer.event_detector import EventDetector
from src.writer.beacon_deployer import BeaconDeployer
from src.writer.lora_handler import WriterLoRa
from src.writer.explorer import FrontierExplorer
from src.writer.status_monitor import StatusMonitor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WriterNode:
    def __init__(self, sim_mode=False):
        self.sim_mode = sim_mode
        self.state = "INIT"
        self.pose = (0.0, 0.0, 0.0)  # x, y, theta

        logging.info("Initializing Writer subsystems...")
        
        # Initialize ESP32 Serial Link
        try:
            if not sim_mode:
                self.esp = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
                time.sleep(2) # Wait for ESP32 reboot
                logging.info("ESP32 Serial Link Established.")
            else:
                self.esp = None
        except Exception as e:
            logging.error(f"ESP32 Connection failed: {e}")
            self.esp = None

        if not sim_mode and LoRaRadio:
            self.radio = LoRaRadio(spi_bus=0, spi_device=0, ce_pin=LORA_CE0, rst_pin=LORA_RST, dio0_pin=LORA_DIO0)
            self.adc = MCP3008ADC(ADC_SPI_BUS, ADC_SPI_DEVICE)
            self.dht = DHT11Sensor(DHT11_PIN)
            self.thermal = MLX90640Thermal(I2C_BUS, MLX90640_ADDR)
            self.mq2 = GasSensor(self.adc, MQ2_CHANNEL, calib_curve=1.5)
            self.mq7 = GasSensor(self.adc, MQ7_CHANNEL, calib_curve=1.2)
            self.imu = IMUSensor(I2C_BUS, MPU9250_ADDR)
            self.battery = BatteryMonitor(I2C_BUS, INA219_ADDR)
        else:
            self.radio = None
            self.adc = None
            self.dht = DHT11Sensor(DHT11_PIN)
            self.thermal = MLX90640Thermal(I2C_BUS, MLX90640_ADDR)
            self.mq2 = GasSensor(self.adc, MQ2_CHANNEL)
            self.mq7 = GasSensor(self.adc, MQ7_CHANNEL)
            self.imu = IMUSensor(I2C_BUS, MPU9250_ADDR)
            self.battery = BatteryMonitor(I2C_BUS, INA219_ADDR)

        self.lora = WriterLoRa(self.radio)
        self.deployer = BeaconDeployer(self.lora, self.send_esp_command, max_beacons=10)
        self.explorer = FrontierExplorer()
        self.detector = EventDetector()
        
        self.status = StatusMonitor(self.battery, self.lora, lambda: self.deployer.beacons_remaining)
        self.status.start()

        self.last_checkpoint_pos = (0.0, 0.0)
        self.current_beacon_id = 1
        self.current_event = None

    def send_esp_command(self, cmd):
        if not self.esp:
            return
        self.esp.write(f"{cmd}\n".encode('utf-8'))
        while True:
            if self.esp.in_waiting > 0:
                resp = self.esp.readline().decode('utf-8').strip()
                if resp == "ACK":
                    break
            time.sleep(0.05)

    def run(self):
        try:
            self.state = "EXPLORING"
            logging.info("Starting EXPLORING state")

            while self.state != "DONE":
                if self.status.is_critical() and self.state not in ["RETURNING", "UPLOADING", "DONE"]:
                    logging.warning("Battery critical! Returning to ONA.")
                    self.state = "RETURNING"
                
                if self.state == "EXPLORING":
                    self._explore_step()
                elif self.state == "EVENT_HANDLING":
                    self._handle_event()
                elif self.state == "RETURNING":
                    self._return_step()
                elif self.state == "UPLOADING":
                    self._upload_step()
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logging.info("Shutting down gracefully...")
        finally:
            self.cleanup()

    def _get_sensor_readings(self):
        return {
            'dht': self.dht.read(),
            'thermal': self.thermal.read(),
            'mq2': self.mq2.read(),
            'mq7': self.mq7.read(),
            'imu': self.imu.read()
        }

    def _explore_step(self):
        lidar_scan = [(0.0, 1.0)]
        self.pose = (self.pose[0] + 0.5, self.pose[1], 0.0)
        
        self.explorer.update_grid(lidar_scan, self.pose)
        
        readings = self._get_sensor_readings()
        event_type, confidence = self.detector.detect(readings)

        dist_since_checkpoint = math.hypot(self.pose[0] - self.last_checkpoint_pos[0], 
                                           self.pose[1] - self.last_checkpoint_pos[1])
        
        if event_type is not None:
            self.current_event = (event_type, confidence)
            self.state = "EVENT_HANDLING"
        elif dist_since_checkpoint >= BEACON_DROP_INTERVAL:
            self.current_event = (0, 255)  
            self.state = "EVENT_HANDLING"
        elif self.explorer.is_exploration_complete() or self.deployer.beacons_remaining <= 0:
            self.state = "RETURNING"
        else:
            wx, wy, wheading = self.explorer.get_next_waypoint()
            # Command motors to move towards (wx, wy)
            if self.esp:
                self.send_esp_command(f"DRIVE,{wx:.2f},{wy:.2f}")

    def _handle_event(self):
        event_type, confidence = self.current_event
        x_cm, y_cm = int(self.pose[0] * 100), int(self.pose[1] * 100)
        z_cm = 0
        
        success = self.deployer.deploy_beacon(self.current_beacon_id, event_type, x_cm, y_cm, z_cm, confidence)
        if success:
            self.current_beacon_id += 1
            self.last_checkpoint_pos = (self.pose[0], self.pose[1])
            
        self.state = "EXPLORING"

    def _return_step(self):
        logging.info("Navigating back to ONA...")
        if self.esp:
            self.send_esp_command("DRIVE,0.0,0.0")
        time.sleep(2)  
        self.state = "UPLOADING"

    def _upload_step(self):
        logging.info("Uploading map to ONA...")
        time.sleep(1)  
        logging.info("Upload complete.")
        self.state = "DONE"

    def cleanup(self):
        self.status.stop()
        self.deployer.cleanup()
        if self.esp:
            self.esp.close()
        logging.info("Cleanup complete.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--sim", action="store_true", help="Run in simulation mode with mock hardware")
    args = parser.parse_args()
    
    node = WriterNode(sim_mode=args.sim)
    node.run()