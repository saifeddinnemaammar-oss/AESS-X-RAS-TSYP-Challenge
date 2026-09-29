"""
Live Hardware Sensor Polling for Writer Robot.
Extracts real-time data from the DHT11, INA219, and analog gas sensors (via ADC).
Dependencies: pip install adafruit-circuitpython-ina219 adafruit-circuitpython-dht smbus2
"""
import time
import board
import busio
import adafruit_dht
from adafruit_ina219 import INA219
import logging

logger = logging.getLogger(__name__)

class HardwareSensors:
    def __init__(self):
        self.i2c_bus = busio.I2C(board.SCL, board.SDA)
        
        # Initialize INA219 Battery Monitor[cite: 18]
        try:
            self.ina219 = INA219(self.i2c_bus)
            logger.info("INA219 Battery Monitor initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize INA219: {e}")
            self.ina219 = None

        # Initialize DHT11 Temperature Sensor on GPIO 4[cite: 18]
        try:
            self.dht11 = adafruit_dht.DHT11(board.D4)
            logger.info("DHT11 Sensor initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize DHT11: {e}")
            self.dht11 = None

        # NOTE: Raspberry Pi lacks analog pins. 
        # MQ Gas Sensors must be routed through an I2C ADC (e.g., ADS1115).
        # We will assume an ADS1115 is present at I2C address 0x48.
        import smbus2
        self.smbus = smbus2.SMBus(1)
        self.adc_address = 0x48

    def read_gas_adc(self, channel):
        """Reads analog voltage from MQ sensors via I2C ADC."""
        try:
            # 0x40 is the command for single-ended read on channel 0
            command = 0x40 | (channel & 0x03)
            self.smbus.write_byte(self.adc_address, command)
            time.sleep(0.1)
            return self.smbus.read_byte(self.adc_address)
        except Exception as e:
            return 0

    def get_all_readings(self):
        """Returns a comprehensive dictionary of all live sensor states."""
        readings = {
            'thermal': {'max_temp': 0.0},
            'mq7': {'ppm': 0},
            'battery': {'voltage': 0.0, 'percent': 0.0}
        }

        if self.dht11:
            try:
                temp = self.dht11.temperature
                if temp is not None:
                    readings['thermal']['max_temp'] = float(temp)
            except RuntimeError as e:
                pass # DHT11 frequently throws read errors, pass and retry next loop

        if self.ina219:
            voltage = self.ina219.bus_voltage
            readings['battery']['voltage'] = voltage
            # 3S LiPo is 12.6V fully charged, ~9.6V depleted[cite: 18]
            percent = max(0, min(100, (voltage - 9.6) / (12.6 - 9.6) * 100))
            readings['battery']['percent'] = percent

        # Read MQ-7 (CO) and MQ-2 (Smoke) analog values mapped to channels 0 and 1
        raw_mq7 = self.read_gas_adc(0)
        readings['mq7']['ppm'] = raw_mq7 * 10 # Rough mapping scalar

        return readings