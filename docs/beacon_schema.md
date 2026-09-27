# Beacon Message Schema

All RF communication uses a strict 20-byte binary struct to maximize LoRa throughput and reliability.

## Byte-Level Layout

| Bytes | Field          | Type       | Range        | Description                                      |
|-------|----------------|------------|--------------|--------------------------------------------------|
| 0-1   | Beacon ID      | uint16_le  | 0-65535      | Unique ID of the beacon.                         |
| 2     | Writer ID      | uint8      | 0-255        | ID of the deploying robot.                       |
| 3     | Event Type     | uint8      | 0-3          | 0=Checkpoint, 1=Victim, 2=Fire, 3=Gas            |
| 4-5   | Local X        | int16_le   | +/- 32767    | ENU East coordinate in cm.                       |
| 6-7   | Local Y        | int16_le   | +/- 32767    | ENU North coordinate in cm.                      |
| 8     | Local Z        | int8       | +/- 127      | Floor or vertical coordinate in cm.              |
| 9-12  | Timestamp      | uint32_le  | Epoch        | Unix time of event detection.                    |
| 13-14 | TTL            | uint16_le  | 0-65535      | Validity window in seconds.                      |
| 15    | Confidence     | uint8      | 0-255        | Sensor certainty (mapped to 0.0-1.0).            |
| 16-17 | Next Beacon ID | uint16_le  | 0-65535      | Chain pointer to next beacon (0 = none).         |
| 18-19 | CRC-16         | uint16_le  | 0-65535      | CRC-16/MODBUS checksum for error verification.   |

**Total Size:** 20 bytes.

## Python Struct Format
To pack and unpack this struct in Python, use the following `struct` format string:
```python
FORMAT_STRING = '<H B B h h b I H B H H'
```

## CRC-16/MODBUS Algorithm
The final 2 bytes contain a CRC-16 checksum using the MODBUS polynomial (`0xA001`). This ensures payload integrity over the noisy LoRa link. Packets failing the CRC check are dropped immediately by the ONA firewall.

## ACK Packet Format
Acknowledgments (ACKs) are minimal 4-byte packets:
- `Bytes 0-1`: Beacon ID (uint16_le)
- `Byte 2`: ACK Status (0x01 = Success, 0x00 = Fail)
- `Byte 3`: Checksum (XOR of bytes 0-2)

## Example Hex Dump
```text
01 00 05 02 C8 00 90 01 00 60 C3 5E 65 3C 00 FF 02 00 A1 3F
```
*Annotation:*
- `01 00`: Beacon ID = 1
- `05`: Writer ID = 5
- `02`: Event = Fire
- `C8 00`: Local X = 200 cm
- `90 01`: Local Y = 400 cm
- `00`: Local Z = 0
- `60 C3 5E 65`: Timestamp = 1699999990
- `3C 00`: TTL = 60s
- `FF`: Confidence = 255 (1.0)
- `02 00`: Next Beacon = 2
- `A1 3F`: CRC = 0x3FA1

## Data Aging and Confidence Decay
To prevent executors from responding to stale data, confidence decays exponentially based on age:
$C_{eff} = C_0 \cdot e^{-\text{age}/\tau}$

Where:
- $C_0$ is the initial confidence (0.0 - 1.0).
- $\text{age} = \text{now} - \text{timestamp}$.
- $\tau$ is the decay constant for the event type.

If $\text{age} > \text{TTL}$, the beacon is ignored completely.
