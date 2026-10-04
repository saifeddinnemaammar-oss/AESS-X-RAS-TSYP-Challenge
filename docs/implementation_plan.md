# Implementation Plan

## Phase 1 (due 05/10/2026)
- Simulation.
- GitHub repo with code and docs.
- 6-page technical report.
- Failure cases.
- Implementation plan.

## Phase 2 (due 01/12/2026)
- Physical prototype: Writer + Executor robots.
- Beacons with LoRa.
- ONA with 4G uplink.
- Command post dashboard.
- User manual.
- 5-min pitch + 2-min Q&A.

## Hardware BOM Summary
- 2x Raspberry Pi 4B (Writer AI & ONA Translation)
- 6x ESP32-WROOM-32 (1 Writer RTOS, 1 ONA Firewall, 1 Executor Core, 10 Beacons)
- 6x SX1276 LoRa Transceivers
- 2x RPLIDAR A1 (Writer & Executor)
- 1x MPU-9250 IMU (Executor)
- 1x u-blox NEO-M9N GNSS (ONA Gateway)
- 1x 4G/LTE USB modem
- 1x MLX90640 Thermal camera array
- MQ-2 & MQ-7 Gas sensors
- PAM8403 3W Audio Amplifier & Speaker
- 10x Piezoelectric SOS Buzzers
- 18650 & 3S LiPo batteries
- Robot chassis & custom 3D printed enclosures