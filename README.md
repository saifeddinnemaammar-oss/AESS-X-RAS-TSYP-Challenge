# Project Nabad (نبض): Autonomous USAR Swarm

A decentralized, hardware-native robotics architecture designed for GPS-denied Urban Search and Rescue (USAR) operations. Built for collapsed infrastructure and electronic warfare zones, this system utilizes a dual-robot deployment strategy paired with a resilient LoRa mesh network to map hazards and locate human targets.

## System Architecture

The architecture is partitioned across four physical nodes to eliminate dependency conflicts and maintain lean microcontroller execution:

### 1. `/Writer_Robot` (Dual-Board: Pi 4 + ESP32)
* **Raspberry Pi 4 (`pi_src/`):** Runs ROS 2 Humble and BreezySLAM. Hosts an INT8 quantized YOLOv8 Nano model to visually identify victims and fire hazards.
* **ESP32-WROOM (`esp32_src/`):** Dedicated RTOS actuator. Polls MLX90640 Thermal and MQ-2/MQ-7 gas sensors to corroborate visual data via sensor fusion. Manages servo-actuated beacon deployment.

### 2. `/ONA_Gateway` (Air-Gapped Translator)
* Raspberry Pi 4B paired with a direct SPI SX1276 LoRa transceiver and a u-blox NEO-M9N GNSS anchor. 
* Intercepts local ENU telemetry, validates CRC-16 checksums, and performs tangent-plane mathematical translation into global WGS84 coordinates.
* **Security:** Linux `iptables` strictly blocks IP forwarding. Data reaches the 4G/LTE cellular network exclusively through a custom Python translation daemon.

### 3. `/Executor_Robot` (Monolithic ESP32)
* Bare-metal ESP32 configured for navigating tight physical clearances.
* Combines RPLiDAR A1 obstacle avoidance with LoRa RSSI gradient homing to follow the deployed beacon trail.
* Equipped with a servo MedKit release, water pump relay, and a PAM8403 3W audio amplifier for broadcasting pre-recorded extraction instructions.

### 4. `/Beacon_Node` (Standalone RF Memory)
* 18650 Li-ion powered nodes utilizing a zero-draw magnetic reed-switch wake-up circuit.
* Transmits a unified 20-byte `BeaconPacket` (Type, Coordinates, TTL, Confidence, CRC-16) every 3 seconds using ALOHA-based temporal randomization.
* Integrated hardware watchdog triggers a piezoelectric SOS alarm if the Time-To-Live expires prior to Executor arrival.

## Communication Protocol
All nodes communicate via 868MHz LoRa using a strict 20-byte Little-Endian C-struct. The ONA Gateway acts as the central firewall, dropping malformed or jammed packets before they bridge to the Command Post dashboard.

## Deployment Instructions (Writer Robot)
On the Writer Robot's Raspberry Pi 4 (Ubuntu 22.04), execute the automated installation script to download ROS 2 Humble and the RPLiDAR dependencies:
```bash
chmod +x install_ros2_pi.sh
./install_ros2_pi.sh