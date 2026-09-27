"""
ONA Gateway Configuration
"""

# GPS settings
GPS_UART_PORT = "/dev/ttyAMA0"
GPS_BAUDRATE = 9600

# LoRa settings
LORA_SPI_BUS = 0
LORA_SPI_DEVICE = 0
LORA_RST = 22
LORA_DIO0 = 25
LORA_FREQ = 868.0

# MQTT settings
MQTT_HOST = "127.0.0.1" # Default to localhost if not set
MQTT_PORT = 1883
MQTT_TOPIC_BEACONS = "living_map/beacons"
MQTT_TOPIC_TELEMETRY = "living_map/telemetry"
MQTT_TOPIC_MISSIONS = "living_map/missions"

# Uplink Mode
UPLINK_MODE = "MQTT" # or "HTTP"
HTTP_UPLINK_URL = "http://localhost:8080/api/ingest"

# Default anchor
DEFAULT_LAT0 = 34.7398
DEFAULT_LON0 = 10.7600
DEFAULT_ALT0 = 15.0

# Earth radius in meters
R_EARTH = 6378137.0

# Rate limiting
MAX_PACKETS_PER_SEC = 10

# Storage paths
STORE_FORWARD_DB = "/var/lib/living_map/queue.db"
MISSION_STORAGE = "/var/lib/living_map/missions"
LOG_FILE = "/var/log/living_map/ona_gateway.log"
