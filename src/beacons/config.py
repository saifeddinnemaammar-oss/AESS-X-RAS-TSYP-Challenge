"""
Beacon-specific constants for ESP32 MicroPython.
"""

# SPI pins for SX1276
SPI_SCK = 18
SPI_MOSI = 23
SPI_MISO = 19
SPI_NSS = 5
SPI_RST = 14
SPI_DIO0 = 26

# LoRa Radio Configuration
LORA_FREQ = 868.0  # MHz
LORA_SF = 7
LORA_BW = 125000  # Hz

# Timings
DEEP_SLEEP_MS = 3000        # 3 seconds
TX_TIMEOUT_MS = 100
RX_BOOT_TIMEOUT_MS = 5000   # wait 5s for config from Writer

# Hardware
LED_PIN = 2  # Onboard LED
