"""
System-wide constants shared by Writer, Executor, and ONA for the Living Map USAR project.
"""

# LoRa Radio Configuration
LORA_FREQ = 868.0  # MHz
LORA_SF = 7
LORA_BW = 125000  # Hz
LORA_CR = "4/5"
LORA_TX_POWER = 14  # dBm
LORA_PREAMBLE_LEN = 8

# Event Types
EVENT_CHECKPOINT = 0
EVENT_VICTIM = 1
EVENT_FIRE = 2
EVENT_GAS = 3

# Default TTL values per event type (in seconds)
TTL_VICTIM = 7200      # 2 hours
TTL_FIRE = 1800        # 30 mins
TTL_GAS = 3600         # 1 hour
TTL_CHECKPOINT = 14400 # 4 hours

# Confidence settings
CONFIDENCE_THRESHOLD = 50  # Out of 255
DECAY_TAU = 3600.0         # Decay time constant

# SPI pins for SX1276 on Pi
PI_SPI_CE0 = 8
PI_SPI_RST = 22
PI_SPI_DIO0 = 25
