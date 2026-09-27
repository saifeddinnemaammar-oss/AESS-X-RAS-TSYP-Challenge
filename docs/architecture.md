# System Architecture

The Living Map USAR (Urban Search and Rescue) system is divided into three distinct zones to ensure reliable operation in disconnected and hazardous environments.

## Zone Architecture

```mermaid
flowchart TD
    subgraph Zone_A [Zone A: Disaster Area / Indoors]
        W[Writer Robot]
        E[Executor Robot]
        B1((Beacon 1))
        B2((Beacon 2))
        W -->|Deploys| B1
        W -->|Deploys| B2
        B1 -.->|LoRa| B2
        E -.->|Homing / LoRa| B1
    end

    subgraph Zone_B [Zone B: Outside Network Area]
        ONA[ONA Gateway]
    end

    subgraph Zone_C [Zone C: Safe Zone]
        CP[Command Post]
    end

    B1 ==LoRa==> ONA
    B2 ==LoRa==> ONA
    ONA ==4G / Wi-Fi==> CP
    CP ==4G / Wi-Fi==> ONA
    ONA ==LoRa==> E
```

## Data Flow: LoRa → ONA → 4G/Wi-Fi → Command Post
1. **Writer Robot** drops beacons at points of interest (hazards, victims).
2. **Beacons** pulse out their 20-byte data packets via LoRa (868 MHz).
3. **ONA Gateway** ingests LoRa packets, translates local coordinates to global GPS coordinates, and pushes the data to the Command Post via 4G or Wi-Fi.
4. **Command Post** receives telemetry and map data, allowing commanders to plan missions.
5. **ONA Gateway** relays mission briefings back to the **Executor Robot** via LoRa before it enters the hazardous zone.

## ONA Bus Isolation Diagram
```mermaid
flowchart LR
    SPI[SPI0 Bus] -->|LoRa Packets| Pi[Raspberry Pi 4B]
    UART[UART /dev/ttyAMA0] -->|NMEA Data| Pi
    Pi -->|Firewall| USB[USB 4G Modem]
```

## Software Architecture
- **Writer Pi**: `writer_node.py` (exploration, event detection, beacon deployment)
- **Executor Pi**: `executor_node.py` (mission planning, homing, verification)
- **ONA Pi**: `ona_gateway.py` (LoRa ingest, translation, uplink, firewall)
- **Beacon ESP32**: MicroPython `main.py` (deep sleep, lock-in, periodic pulse)

## Sequence Diagrams

### a) Writer Beacon Deployment Handshake
```mermaid
sequenceDiagram
    participant W as Writer Node
    participant D as Deployer Servo
    participant B as Beacon (ESP32)
    participant L as LoRa TX
    W->>D: Trigger drop
    D-->>B: Magnetic switch released (Wake)
    B->>B: Boot & initialize
    W->>L: Send Beacon Config
    L->>B: RX Config Packet
    B-->>W: ACK Config
    W->>W: Mark successful deployment
```

### b) ONA Packet Processing Pipeline
```mermaid
sequenceDiagram
    participant B as Beacon
    participant L as LoRa Ingest
    participant F as Firewall
    participant T as Translator
    participant U as Uplink
    B->>L: LoRa Packet
    L->>F: Validate CRC & Format
    F->>T: Valid Packet
    T->>T: Local ENU -> GPS WGS84
    T->>U: Enqueue JSON
    U->>U: MQTT Publish
```

### c) Executor Mission Briefing
```mermaid
sequenceDiagram
    participant CP as Command Post
    participant O as ONA
    participant E as Executor Robot
    CP->>O: Send Mission Plan (JSON)
    O->>O: Parse & queue
    E->>O: Request Briefing (LoRa)
    O-->>E: Transmit Mission Waypoints
    E->>E: Acknowledge & Execute
```

### d) Executor Beacon Homing
```mermaid
sequenceDiagram
    participant E as Executor Robot
    participant B as Beacon
    loop Homing Phase
        B->>E: LoRa Pulse (RSSI)
        E->>E: Estimate Distance & Bearing
        E->>E: Adjust velocity
    end
    E->>E: Arrival at target
```
