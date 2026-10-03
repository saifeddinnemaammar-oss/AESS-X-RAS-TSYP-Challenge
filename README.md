# Project Nabad: The Living Map Architecture

A decentralized, hardware-native robotics architecture designed for GPS-denied USAR (Urban Search and Rescue) operations. Built for collapsed infrastructure and electronic warfare zones, this system utilizes a dual-robot deployment strategy paired with a resilient LoRa mesh network to map hazards and find human life under the rubble.

## Architectural Overview

*Nabad* (نبض) means "pulse" or "heartbeat." In total communication blackouts, the core of this system is a trail of disposable LoRa beacons that pulse a 20-byte coordinate signal through the darkness, keeping the network alive until extraction arrives.

The architecture is strictly segmented across four physical nodes:

### 1. `/Writer_Robot` (Dual-Board: Pi 4 + ESP32)
The vanguard of the system.
* **Raspberry Pi 4 (`pi_src/`):** Runs ROS 2 Humble and BreezySLAM for exploration. It hosts an INT8 quantized **YOLOv8 Nano** model to visually identify victims and fire hazards in the rubble.
* **ESP32-WROOM (`esp32_src/`):** A dedicated real-time actuator. It polls the **MLX90640 Thermal Array** and **MQ-2/MQ-7** gas sensors to corroborate YOLOv8's visual data. Upon sensor fusion lock, it triggers a servo to drop a physical beacon.

### 2. `/ONA_Gateway` (Air-Gapped Translator)
The perimeter firewall.
* A Raspberry Pi 4B paired with a direct SPI **SX1276 LoRa transceiver** and a **u-blox NEO-M9N GNSS** anchor. 
* It intercepts the local ENU telemetry from the rubble, validates the CRC-16 checksums to reject jammed packets, and performs a tangent-plane mathematical translation into global WGS84 coordinates.
* **Air-Gap Security:** Linux `iptables` strictly blocks IP forwarding. Data can only reach the external 4G/LTE cellular network by passing through the custom Python translation daemon.

### 3. `/Executor_Robot` (Monolithic ESP32)
The agile intervention unit.
* Relies on a single, bare-metal ESP32 to navigate tight clearances.
* Utilizes a combination of **RPLiDAR A1** obstacle avoidance and LoRa RSSI gradient homing to follow the beacon breadcrumb trail left by the Writer.
* Equipped with physical payloads (servo MedKit release, water pump relay) and a **PAM8403 3W audio amplifier** to broadcast pre-recorded voice commands to trapped victims.

### 4. `/Beacon_Node` (Standalone RF Memory)
The physical breadcrumbs.
* Powered by an 18650 Li-ion cell with a zero-draw magnetic reed-switch wake-up.
* Transmits the unified 20-byte `BeaconPacket` (Type, Coordinates, TTL, Confidence, CRC-16) every 3 seconds using ALOHA-based temporal randomization to prevent packet collision.
* Features a hardware watchdog that triggers a piezoelectric SOS alarm if the Executor fails to arrive before the Time-To-Live expires.