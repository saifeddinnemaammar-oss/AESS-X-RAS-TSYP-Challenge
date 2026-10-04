"""
ONA Gateway Configuration (ESP32 UART Firewall Edition)
"""

# ESP32 RF Firewall settings (Matches lora_ingest.py)
ESP32_PORT = "/dev/ttyUSB0"
ESP32_BAUDRATE = 115200

# GPS settings
GPS_UART_PORT = "/dev/ttyAMA0"
GPS_BAUDRATE = 9600

# MQTT settings
MQTT_HOST = "127.0.0.1" 
MQTT_PORT = 1883
MQTT_TOPIC_BEACONS = "nabad/beacons"
MQTT_TOPIC_TELEMETRY = "nabad/telemetry"
MQTT_TOPIC_MISSIONS = "nabad/missions"

# Uplink Mode
UPLINK_MODE = "MQTT" # or "HTTP"
HTTP_UPLINK_URL = "http://localhost:8080/api/ingest"

# Default anchor (Used if GPS fails)
DEFAULT_LAT0 = 34.7398
DEFAULT_LON0 = 10.7600
DEFAULT_ALT0 = 15.0

R_EARTH = 6378137.0
MAX_PACKETS_PER_SEC = 10

STORE_FORWARD_DB = "/var/lib/nabad/queue.db"
MISSION_STORAGE = "/var/lib/nabad/missions"
LOG_FILE = "/var/log/nabad/ona_gateway.log"