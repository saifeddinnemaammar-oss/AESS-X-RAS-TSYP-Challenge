# The Living Map: Writer Robot Subsystem

The Writer Robot is an autonomous exploration rover responsible for mapping GPS-denied hazard zones and deploying a physical LoRa mesh network. 

## System Architecture
This node utilizes a dual-board architecture:
*   **Raspberry Pi (High-Level Brain):** Handles pathfinding logic, SPI communication with the LoRa module, CRC-16 packet generation, and serial delegation.
*   **ESP32 (Low-Level Actuator):** Dedicated to real-time PWM generation for the L298N motor drivers and beacon-drop servos, ensuring OS-level interrupts on the Pi do not affect driving kinematics.

## Wiring Schematics

### 1. Raspberry Pi to LoRa (SX1276) via SPI
| LoRa Pin | Pi Pin | Function |
| :--- | :--- | :--- |
| VCC | 3.3V | Power |
| GND | GND | Ground |
| MISO | Pin 21 (GPIO 9) | Master In Slave Out |
| MOSI | Pin 19 (GPIO 10) | Master Out Slave In |
| SCK | Pin 23 (GPIO 11) | Serial Clock |
| NSS | Pin 24 (GPIO 8) | Chip Select (CE0) |

### 2. Pi to ESP32 (UART)
*   Connect Pi **USB** to ESP32 **Micro-USB/USB-C** using a standard data cable. The Pi recognizes this as `/dev/ttyUSB0`.

### 3. ESP32 to L298N Motor Driver
| ESP32 GPIO | L298N Pin | Function |
| :--- | :--- | :--- |
| GPIO 14 | ENA | Left Motor PWM (Speed) |
| GPIO 27 | IN1 | Left Motor FWD |
| GPIO 26 | IN2 | Left Motor REV |
| GPIO 32 | ENB | Right Motor PWM (Speed) |
| GPIO 25 | IN3 | Right Motor FWD |
| GPIO 33 | IN4 | Right Motor REV |

## Setup Instructions
1. Flash `writer_esp32.ino` to the ESP32 using the Arduino IDE.
2. Connect the ESP32 to the Raspberry Pi via USB.
3. Install dependencies on the Pi: `pip install -r requirements.txt`
4. Execute the main program: `python3 writer_pi.py`