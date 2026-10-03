# Hardware Manifests (BOM)

## Writer Robot BOM
| Component | Description |
|-----------|-------------|
| Chassis | 4WD differential-drive mobile chassis with DC motors |
| Compute (AI) | Raspberry Pi 4B (4GB) |
| Compute (RTOS)| ESP32-WROOM-32 |
| Nav Sensors | RPLIDAR A1 |
| Event Sensors | Pi Camera V2, MLX90640 (Thermal), MQ-2 (Smoke), MQ-7 (CO) |
| Comms | SX1276 LoRa module (SPI to ESP32) |
| Payload | Servo-actuated beacon deployment magazine (SG90) |
| Power | 3S LiPo battery, INA219 (Power Monitor), Dual 5V Buck Converters |

## Executor Robot BOM
| Component | Description |
|-----------|-------------|
| Chassis | Agile wheeled chassis with BTS7960 high-current drivers |
| Compute | Monolithic ESP32-WROOM-32 |
| Nav Sensors | RPLIDAR A1, MPU-9250 (IMU) |
| Comms | SX1276 LoRa module (SPI for RSSI Homing) |
| Payload | Servo MedKit release, 5V Water Pump Relay, PAM8403 3W Audio Amp & Speaker |
| Power | 3S LiPo battery, INA219, 5V/3A Buck Converter |

## ONA Gateway BOM
| Component | Description |
|-----------|-------------|
| Compute | Raspberry Pi 4B (Core translation & routing) |
| Firewall/Comms| ESP32-WROOM-32 paired with SX1276 LoRa Transceiver |
| Comms (Uplink) | 4G/LTE USB Cellular Modem |
| Location | u-blox NEO-M9N GNSS Module (UART) |
| Power | 12V LiFePO4 battery with 5V/5A Regulated Converter |

## Beacon BOM
| Component | Description |
|-----------|-------------|
| Compute | ESP32-WROOM-32 module |
| Comms | SX1276 LoRa module |
| Visual/Audio | WS2812B NeoPixel RGB Ring (8 pixels), Piezoelectric Buzzer (SOS) |
| Power | 18650 Li-ion cell |
| Wake Mechanism | Reed switch, P-Channel MOSFET, Neodymium Magnet |
| Enclosure | Custom 3D-printed ABS impact-resistant shell |