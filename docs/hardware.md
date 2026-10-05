# Hardware Specifications and Wiring

## BOM and Component Roles

### Writer Robot
*   **Compute**: Raspberry Pi 4B (ROS2, AI) + ESP32-WROOM-32 (RTOS actuator control)
*   **Navigation**: RPLiDAR A1
*   **Perception**: Pi Camera V2, MLX90640 (Thermal), MQ-2 (Smoke), MQ-7 (CO)
*   **Communication**: SX1276 LoRa module
*   **Payload**: Servo-actuated beacon deployment magazine (SG90)

### Executor Robot
*   **Compute**: Monolithic ESP32-WROOM-32
*   **Navigation**: RPLiDAR A1, MPU-9250 (IMU)
*   **Communication**: SX1276 LoRa module
*   **Payload**: Servo MedKit release, 5V Water Pump Relay, PAM8403 3W Audio Amp & Speaker
*   **Drive**: Agile wheeled chassis with BTS7960 high-current drivers

### ONA Gateway
*   **Compute**: Raspberry Pi 4B (Translation & routing)
*   **Firewall**: ESP32-WROOM-32 with SX1276 LoRa Transceiver
*   **Uplink**: 4G/LTE USB Cellular Modem
*   **Location**: u-blox NEO-M9N GNSS Module

### Beacon Node
*   **Compute**: ESP32-WROOM-32
*   **Communication**: SX1276 LoRa module
*   **Indicators**: WS2812B NeoPixel RGB Ring, Piezoelectric Buzzer
*   **Power**: 18650 Li-ion cell, Magnetic Reed Switch Wake-Up Circuit

## Wiring Guide

### Writer Robot (Dual-Board)
**ESP32-WROOM:**
*   SPI (Pins 18, 19, 23, NSS 5): SX1276 LoRa
*   I2C (Pins 21, 22): MLX90640 Thermal Array & INA219 Power Monitor
*   ADC (Pins 34, 35): MQ-2 & MQ-7 Gas Sensors
*   PWM (Pin 13): SG90 Drop Servo

### Executor Robot
*   SPI (Pins 18, 19, 23, NSS 5): SX1276 LoRa
*   UART2 (Pins 16, 17): RPLiDAR A1
*   I2C (Pins 21, 22): MPU-9250 IMU
*   GPIO (Pins 14, 27, 26, 32, 25, 33): BTS7960 Motor Drivers
*   GPIO (Pin 18, 19): MedKit Servo, Water Pump Relay
*   DAC (Pin 22): PAM8403 Audio Amp

### ONA Gateway
**ESP32-WROOM (Firewall):**
*   SPI (Pins 18, 19, 23, NSS 5): SX1276 LoRa

**Raspberry Pi 4:**
*   UART (ttyAMA0): u-blox NEO-M9N GNSS
