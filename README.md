# Living Map - War-Zone Urban SAR

**IEEE RAS x AESS Tunisia TSYPI4 Technical Challenge**

## Problem
In war-zone urban search and rescue, robots must explore GPS-denied, communication-denied collapsed buildings. When a robot fails, its knowledge is lost. We build a resilient spatial memory system using radio beacons and an Outside Network Area (ONA) to enable mission continuity.

## System Overview
- **Writer Robot:** Autonomous ground robot. Explores, detects events, drops beacons.
- **Beacons:** Checkpoint and event beacons. Store what, where, when, TTL, confidence, next beacon ID.
- **ONA:** Outside Network Area. Receives, translates local to GPS, carries to command post, briefs Executor.
- **Executor Robot:** Ground robot. Receives mission from ONA, follows beacon chain, avoids hazards.
- **Command Post:** Live map. Commander decides.

## Event Types
1. Human distress - thermal + audio + CO2.
2. Fire/gas hazard - temperature + smoke + CO/VOC.

## Architecture
See docs/architecture.md for details.

## Simulation
Built with ROS2 Humble + Gazebo Classic.

## Repository Structure
- src/ - ROS2 packages for Writer, Executor, Beacons, ONA.
- simulation/ - Gazebo worlds, models, launch files.
- command_post/ - Dashboard for live map.
- docs/ - Architecture, beacon schema, failure cases, implementation plan.
- report/ - Technical report for Phase 1.

## Team
- [Name] - Project Lead
- [Name] - ROS/Simulation
- [Name] - SLAM/Navigation
- [Name] - Sensors/Events
- [Name] - Comms/Beacons
- [Name] - ONA/Backend
- [Name] - Documentation

## License
MIT
