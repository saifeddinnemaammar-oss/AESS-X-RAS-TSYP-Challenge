"""
Writer-specific configuration parameters.
Defines IDs, SPI/GPIO pins, thresholds, and operational constraints.
"""

WRITER_ID = 1

# LoRa SX1276 (SPI0)
LORA_CE0 = 8
LORA_RST = 22
LORA_DIO0 = 25

# I2C Addresses
I2C_BUS = 1
INA219_ADDR = 0x40
MPU9250_ADDR = 0x68
MLX90640_ADDR = 0x33

# GPIO Pins
DHT11_PIN = 4
SERVO_PIN = 18

# SPI ADC (MCP3008)
ADC_SPI_BUS = 0
ADC_SPI_DEVICE = 1
MQ2_CHANNEL = 0
MQ7_CHANNEL = 1

# Sensor Thresholds
THERMAL_VICTIM = 34.0
THERMAL_FIRE = 55.0
CO2_VICTIM = 1000.0
GAS_HAZARD = 500.0

# Exploration Params
MAX_FRONTIER_DIST = 10.0  # meters
BEACON_DROP_INTERVAL = 5.0  # meters

# Battery Thresholds
BATT_LOW = 20.0
BATT_CRITICAL = 10.0
