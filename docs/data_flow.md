# System Data Flow

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

## Writer Mission Flow
```mermaid
flowchart LR
    START --> Init
    Init --> Explore
    Explore --> Detect
    Detect --> Deploy
    Deploy --> CheckBatt{Battery Low?}
    CheckBatt -->|No| Explore
    CheckBatt -->|Yes| Return
    Return --> Upload
    Upload --> END
```

## Executor Mission Flow
```mermaid
flowchart LR
    Briefing --> Entry
    Entry --> Navigation
    Navigation --> Arrival
    Arrival --> Verification
    Verification --> Action
    Action --> Return
```

## Beacon Lifecycle
```mermaid
stateDiagram-v2
    Stored: Stored (0mA)
    Deployed: Deployed (Boot)
    Listen: Listen for Config
    LockIn: Lock-in Config
    Pulsing: Pulsing LoRa
    Expired: Expired (Deep Sleep)

    Stored --> Deployed : Magnet Removed
    Deployed --> Listen
    Listen --> LockIn : RX Config
    LockIn --> Pulsing
    Pulsing --> Expired : TTL Exceeded
```

## ONA Processing Pipeline
```mermaid
flowchart LR
    RF_Ingest[RF Ingest] --> Firewall[Firewall (CRC check)]
    Firewall --> Translate[Translate (ENU to GPS)]
    Translate --> Uplink{Link Up?}
    Uplink -->|Yes| Push[Push to Command Post]
    Uplink -->|No| Store[Store & Forward Queue]
    Store --> Push
```
