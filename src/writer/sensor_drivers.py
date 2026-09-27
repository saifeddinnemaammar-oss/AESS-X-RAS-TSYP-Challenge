"""
Hardware abstraction for all Writer sensors.
"""
import time
import math
import logging

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

try:
    from smbus2 import SMBus
except ImportError:
    SMBus = None

try:
    import spidev
except ImportError:
    spidev = None

class DHT11Sensor:
    def __init__(self, pin):
        self.pin = pin
        if GPIO:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN)

    def read(self):
        try:
            if not GPIO:
                raise Exception("No RPi.GPIO")
            # Simulated timing protocol reading for DHT11
            return {"temp": 25.0, "humidity": 50.0, "ok": True}
        except Exception as e:
            logging.error(f"DHT11 read failed: {e}")
            return {"temp": 0.0, "humidity": 0.0, "ok": False}

class MLX90640Thermal:
    def __init__(self, bus, address):
        self.bus_id = bus
        self.address = address
        self.bus = SMBus(bus) if SMBus else None

    def read(self):
        try:
            if not self.bus:
                raise Exception("No I2C")
            # Simulated 24x32 array processing
            max_temp = 36.5
            return {"max_temp": max_temp, "ok": True}
        except Exception as e:
            logging.error(f"MLX90640 read failed: {e}")
            return {"max_temp": 0.0, "ok": False}

class MCP3008ADC:
    def __init__(self, bus, device):
        self.spi = spidev.SpiDev() if spidev else None
        if self.spi:
            try:
                self.spi.open(bus, device)
                self.spi.max_speed_hz = 1350000
            except Exception as e:
                logging.error(f"SPI init failed: {e}")
                self.spi = None

    def read_channel(self, channel):
        if not self.spi:
            return 0
        if 0 <= channel <= 7:
            r = self.spi.xfer2([1, (8 + channel) << 4, 0])
            return ((r[1] & 3) << 8) + r[2]
        return 0

class GasSensor:
    def __init__(self, adc, channel, calib_curve=1.0):
        self.adc = adc
        self.channel = channel
        self.calib_curve = calib_curve

    def read(self):
        try:
            val = self.adc.read_channel(self.channel)
            ppm = val * self.calib_curve
            return {"ppm": ppm, "ok": True}
        except Exception as e:
            logging.error(f"GasSensor read failed: {e}")
            return {"ppm": 0.0, "ok": False}

class IMUSensor:
    def __init__(self, bus, address):
        self.bus_id = bus
        self.address = address
        self.bus = SMBus(bus) if SMBus else None

    def read(self):
        try:
            if not self.bus:
                raise Exception("No I2C")
            return {"heading": 90.0, "ok": True}
        except Exception as e:
            logging.error(f"IMU read failed: {e}")
            return {"heading": 0.0, "ok": False}

class BatteryMonitor:
    def __init__(self, bus, address):
        self.bus_id = bus
        self.address = address
        self.bus = SMBus(bus) if SMBus else None

    def read(self):
        try:
            if not self.bus:
                raise Exception("No I2C")
            voltage = 11.1
            percentage = min(100.0, max(0.0, (voltage - 9.0) / (12.6 - 9.0) * 100))
            return {"voltage": voltage, "percentage": percentage, "ok": True}
        except Exception as e:
            logging.error(f"Battery read failed: {e}")
            return {"voltage": 0.0, "percentage": 0.0, "ok": False}
