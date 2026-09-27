# Hardware Manifests (BOM)

## Writer Robot BOM
| Component | Description |
|-----------|-------------|
| Chassis | Tracked mobile chassis with DC motors and encoders |
| Compute | Raspberry Pi 4B (2GB) |
| Nav Sensors | RPLIDAR A1, MPU9250 (IMU) |
| Event Sensors | Pi Camera, USB Microphone, MLX90640 (Thermal), MQ-2 (Smoke), MQ-7 (CO), DHT11 |
| Comms | SX1276 LoRa module (SPI) |
| Payload | Servo-actuated beacon deployment rack |
| Power | 3S LiPo battery, INA219 (Power Monitor), 5V/3A Buck Converter |

## Executor Robot BOM
| Component | Description |
|-----------|-------------|
| Chassis | Small wheeled chassis |
| Compute | Raspberry Pi 4B (2GB) |
| Nav Sensors | RPLIDAR A1, MPU9250 (IMU) |
| Verification Sensors | Pi Camera, USB Microphone, MQ-2, MQ-7 |
| Comms | SX1276 LoRa module (SPI) |
| Payload | Medical/Supply drop bay |
| Power | 3S LiPo battery, INA219, 5V/3A Buck Converter |

## ONA Gateway BOM
| Component | Description |
|-----------|-------------|
| Compute | Raspberry Pi 4B (4GB) |
| Comms (LoRa) | SX1302 LoRa HAT |
| Comms (Uplink) | 4G LTE USB Modem or Wi-Fi Router |
| Location | NEO-M9N GPS Module (UART) |
| Power | High-capacity power bank or 12V SLA battery with buck converter |

## Beacon BOM
| Component | Description |
|-----------|-------------|
| Compute | ESP32-WROOM-32 module |
| Comms | SX1276 LoRa module |
| Power | 18650 Li-ion cell |
| Power Regulation | AP2112K 3.3V LDO |
| Wake Mechanism | Reed switch, IRLML6402 P-Channel MOSFET, Neodymium Magnet |
| Enclosure | 3D printed rugged shell |

## Total System Cost Estimate
- Writer Robot: ~$350
- Executor Robot: ~$250
- ONA Gateway: ~$150
- Beacons (x10): ~$100 ($10/each)
- **Total Estimated Cost:** ~$850
