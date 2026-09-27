# Wiring Guide

## Writer Pi GPIO Table
| Pin # | GPIO | Function | Connected To |
|-------|------|----------|--------------|
| 24    | 8    | SPI0 CE0 | SX1276 NSS   |
| 15    | 22   | GPIO     | SX1276 RST   |
| 22    | 25   | GPIO     | SX1276 DIO0  |
| 3     | 2    | I2C1 SDA | I2C Bus      |
| 5     | 3    | I2C1 SCL | I2C Bus      |
| 7     | 4    | GPIO     | DHT11 Data   |
| 12    | 18   | PWM      | Servo Signal |

## Executor Pi GPIO Table
| Pin # | GPIO | Function | Connected To |
|-------|------|----------|--------------|
| 24    | 8    | SPI0 CE0 | SX1276 NSS   |
| 15    | 22   | GPIO     | SX1276 RST   |
| 22    | 25   | GPIO     | SX1276 DIO0  |
| 3     | 2    | I2C1 SDA | I2C Bus      |
| 5     | 3    | I2C1 SCL | I2C Bus      |

## ONA Pi GPIO Table
| Pin # | GPIO | Function | Connected To |
|-------|------|----------|--------------|
| 24    | 8    | SPI0 CE0 | SX1302 HAT   |
| 19    | 10   | SPI0 MOSI| SX1302 HAT   |
| 21    | 9    | SPI0 MISO| SX1302 HAT   |
| 23    | 11   | SPI0 SCLK| SX1302 HAT   |
| 8     | 14   | UART TX  | NEO-M9N RX   |
| 10    | 15   | UART RX  | NEO-M9N TX   |

## Beacon ESP32 GPIO Table
| GPIO | Function | Connected To |
|------|----------|--------------|
| 18   | SPI SCK  | SX1276 SCK   |
| 23   | SPI MOSI | SX1276 MOSI  |
| 19   | SPI MISO | SX1276 MISO  |
| 5    | SPI NSS  | SX1276 NSS   |
| 14   | GPIO     | SX1276 RST   |
| 26   | GPIO     | SX1276 DIO0  |

## Bus Assignments
### I2C Bus (Writer/Executor)
- 0x40: INA219 Power Monitor
- 0x68: MPU9250 IMU
- 0x33: MLX90640 Thermal Camera (Writer only)

### UART
- `/dev/ttyAMA0` (9600 baud) -> NEO-M9N GPS on ONA

## Power Distribution
- **Robots:** 3S LiPo -> INA219 (V/I monitor) -> 5V/3A Buck Converter -> Raspberry Pi & USB Peripherals.
- **Beacons:** 18650 Cell -> P-MOSFET (switched by Reed) -> AP2112K 3.3V LDO -> ESP32 & SX1276.

## Wire Color Conventions
- **Red:** VCC (5V / 3.3V)
- **Black:** GND
- **Yellow:** SCL / RX / SCK
- **Blue:** SDA / TX / MOSI
- **Green:** MISO / Signals
