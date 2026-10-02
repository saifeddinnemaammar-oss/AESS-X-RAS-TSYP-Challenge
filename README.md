# The Living Map: Autonomous Multi-Node Emergency Response

"The Living Map" is a decentralized, hardware-native robotics architecture designed for GPS-denied hazard environments. The system utilizes a dual-robot deployment strategy combined with a LoRa mesh network to map, verify, and neutralize environmental threats.

## Repository Structure

The architecture is divided into distinct, hardware-specific environments to ensure lean microcontroller flashing and eliminate dependency conflicts.

* **`/Writer_Robot`**: Dual-board (Raspberry Pi + ESP32) SLAM explorer. Maps the physical environment and physically deploys RF beacon breadcrumbs.
* **`/ONA_Gateway`**: Dual-board (Raspberry Pi + ESP32) translation firewall. Validates incoming LoRa telemetry via CRC-16, translates local offsets to WGS84 coordinates, and briefs the Executor.
* **`/Executor_Robot`**: Monolithic ESP32 actuator. Relies entirely on LiDAR obstacle avoidance, priority queuing, and RSSI homing to navigate to hazards and deploy physical countermeasures.
* **`/Beacon_Node`**: Standalone ESP32 RF nodes. Provide visual RGB status indication and broadcast periodic homing pings for Executor navigation.
* **`/Shared_Protocols`**: The unified 20-byte payload schemas and CCITT CRC-16 cryptographic logic ensuring cross-node synchronization.

## Communication Protocol
All nodes communicate via 868MHz LoRa using a strict 20-byte packet structure. The ONA Gateway acts as the central firewall, dropping any packets that fail the CRC-16 checksum before they reach the Command Post dashboard.

## Deployment Instructions (Writer Robot)

This repository contains our custom ROS 2 `core` package for odometry-to-ESP32 bridging. 

**1. Install Dependencies**
On the Writer Robot's Raspberry Pi 4 (Ubuntu 22.04), run the automated installation script to download ROS 2 Humble and the RPLiDAR drivers:
```bash
chmod +x install_ros2_pi.sh
./install_ros2_pi.sh
