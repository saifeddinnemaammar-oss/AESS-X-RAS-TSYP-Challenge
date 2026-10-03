# Wiring Guide

## Writer Robot (Dual-Board)
**Raspberry Pi 4:**
- USB: RPLiDAR A1
- MIPI CSI-2: Pi Camera V2
- USB (ttyUSB0): Serial bridge to ESP32

**ESP32-WROOM:**
- SPI (Pins 18, 19, 23, NSS 5): SX1276 LoRa
- I2C (Pins 21, 22): MLX90640 Thermal Array & INA219 Power Monitor
- ADC (Pins 34, 35): MQ-2 & MQ-7 Gas Sensors
- PWM (Pin 13): SG90 Drop Servo

## Executor Robot (Monolithic ESP32)
**ESP32-WROOM:**
- SPI (Pins 18, 19, 23, NSS 5): SX1276 LoRa
- UART2 (Pins 16, 17): RPLiDAR A1
- I2C (Pins 21, 22): MPU-9250 IMU
- GPIO (Pins 14, 27, 26, 32, 25, 33): BTS7960 Motor Drivers
- GPIO (Pin 18): MedKit Servo
- GPIO (Pin 19): Water Pump Relay
- DAC/GPIO (Pin 22): PAM8403 3W Audio Amplifier

## ONA Gateway (Air-Gapped)
**Raspberry Pi 4:**
- USB: 4G/LTE Modem
- UART (ttyAMA0): u-blox NEO-M9N GNSS
- USB (ttyUSB0): Serial link to ESP32 Firewall

**ESP32-WROOM (Firewall):**
- SPI (Pins 18, 19, 23, NSS 5): SX1276 LoRa

## Beacon Node
**ESP32-WROOM:**
- SPI (Pins 18, 19, 23, NSS 5): SX1276 LoRa
- GPIO (Pin 4): WS2812B NeoPixel Data-In
- GPIO (Pin 12): Piezoelectric SOS Buzzer
- EN/3V3: Magnetic Reed Switch Wake-Up Circuit