# Communication Protocol

The communication layer is built on a resilient LoRa mesh network utilizing 868MHz. To ensure high reliability and low latency under severe bandwidth constraints, the protocol uses a highly optimized C-struct layout.

## BeaconPacket Specification

All nodes communicate using a rigid 20-byte Little-Endian C-struct. 

### Structure Definition

```c
struct __attribute__((packed)) BeaconPacket {
    uint16_t header;       // 0xAA55
    uint8_t  type;         // 1=Beacon, 2=WriterTelemetry, 3=Command
    uint8_t  flags;        // Bit0: Fire, Bit1: Gas, Bit2: Human
    int16_t  x_cm;         // Local X coordinate in cm
    int16_t  y_cm;         // Local Y coordinate in cm
    int8_t   z_m;          // Local Z altitude in meters
    uint32_t timestamp;    // Epoch time
    uint16_t ttl_s;        // Time-to-live in seconds
    uint8_t  confidence;   // AI/Sensor confidence (0-255)
    uint16_t crc16;        // CRC-16 CCITT-FALSE
};
```

### Checksum details
- **Algorithm**: CRC-16 CCITT-FALSE
- **Polynomial**: `0x11021`
- **Initial Value**: `0xFFFF`
- **Verification**: The ESP32 ONA Firewall independently calculates the CRC before passing the packet over serial to the Raspberry Pi.

## Transmission Scheme
The Beacon Nodes transmit their `BeaconPacket` using an ALOHA-based temporal randomization algorithm. They send data every 3 seconds with a ±500ms jitter window to significantly reduce packet collision probability in multi-beacon deployments.
