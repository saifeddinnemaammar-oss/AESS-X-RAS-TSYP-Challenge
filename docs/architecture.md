# System Architecture

## Overview
Project Nabad uses a decentralized architecture composed of four distinct nodes designed to operate in GPS-denied and communication-restricted environments.

## Node Roles

1. **Writer Robot**: An autonomous explorer equipped with a Raspberry Pi 4 (for ROS2, SLAM, and YOLOv8 inference) and an ESP32 for hardware management (thermal, gas sensors, servos). It maps the environment and drops Beacon Nodes when it detects victims or hazards.
2. **Beacon Nodes**: ESP32-based devices deployed by the Writer Robot. They act as RF breadcrumbs, transmitting localized coordinates and event data via LoRa.
3. **Executor Robot**: An ESP32-based autonomous vehicle that navigates using RPLiDAR and LoRa RSSI to follow the breadcrumb trail and deliver medical payloads.
4. **ONA Gateway**: The central telemetry hub. An ESP32 handles LoRa reception as a hardware firewall, forwarding validated packets to a Raspberry Pi 4, which translates local coordinates to global WGS84 coordinates and pushes them to the command post.

## Data Flow

```mermaid
flowchart TD
    W_Drop[Writer drops beacon] --> B_Pulse[Beacon pulses LoRa]
    B_Pulse --> O_Ingest[ONA ingests packet]
    O_Ingest --> O_Translate[ONA translates ENU to WGS84]
    O_Translate --> CP_Display[Command Post displays on map]
    CP_Display --> CP_Plan[Commander plans mission]
    CP_Plan --> O_Brief[ONA briefs Executor]
    O_Brief --> E_Act[Executor acts]
```

## ONA Processing Pipeline

```mermaid
flowchart LR
    RF_Ingest[RF Ingest] --> Firewall[Firewall CRC check]
    Firewall --> Translate[Translate ENU to GPS]
    Translate --> Uplink{Link Up?}
    Uplink -->|Yes| Push[Push to Command Post]
    Uplink -->|No| Store[Store & Forward Queue]
    Store --> Push
```
