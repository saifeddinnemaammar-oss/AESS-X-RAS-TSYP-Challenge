# The Living Map: Autonomous Multi-Node Emergency Response

A decentralized, hardware-native robotics architecture designed for GPS-denied hazard environments. This system utilizes a dual-robot deployment strategy combined with a custom LoRa mesh network to map, verify, and neutralize environmental threats.

## Repository Structure

The architecture is divided into distinct, hardware-specific environments to ensure lean microcontroller flashing and eliminate dependency conflicts.

* **`/Writer_Robot`** (Dual-Board: Pi 4 + ESP32)
  * **Raspberry Pi (`pi_src/`):** Executes frontier SLAM exploration, thermal anomaly detection, and YOLOv8 visual validation of targets before triggering deployment.
  * **ESP32 (`esp32_src/`):** Dedicated real-time actuator managing L298N drive motors and the beacon-drop servo.
* **`/ONA_Gateway`** (Dual-Board: Pi 4 + ESP32)
  * **ESP32 (`esp32_src/`):** High-speed RF firewall running direct SPI to the LoRa transceiver, strictly validating incoming 20-byte CRC-16 packets.
  * **Raspberry Pi (`pi_src/`):** ENU-to-WGS84 coordinate translation engine, SQLite store-and-forward queue, and MQTT uplink to the external Command Post.
* **`/Executor_Robot`** (Monolithic ESP32)
  * Single-board microcontroller running `executor_core.ino`.
  * Interprets LoRa mission briefings from the ONA Gateway, maps local obstacles via RPLiDAR on `Serial2`, tracks beacon signals via RSSI gradient navigation, and controls the payload servo and water pump relay directly.
* **`/Beacon_Node`** (Standalone ESP32)
  * Standalone deployable RF breadcrumbs running `beacon_core.ino`.
  * Processes 20-byte configuration packets with CRC-16 validation, drives WS2812B NeoPixel hazard indicators, and broadcasts 1.5-second homing pings.
* **`/Shared_Protocols`**
  * Centralized `beacon_schema.py` defining the 20-byte binary packet standard (`>HBBhhhIHBB`) and CCITT-False CRC-16 cryptographic logic.

## Communication Protocol
All nodes communicate via 868MHz LoRa using a strict 20-byte packet structure. The ONA Gateway acts as the central firewall, dropping any packets that fail the CRC-16 checksum before they reach the Command Post dashboard.

## AI & Vision Pipeline
Visual validation is processed on the **Writer Robot**'s Raspberry Pi using an optimized `YOLOv8` (TFLite) model. The camera only activates upon detecting a thermal anomaly, verifying the presence of a human target before declaring a Priority 1 Victim Event and dropping a cyan rescue beacon.
