# Beacon Message Schema

| Field | Size | Description |
|-------|------|-------------|
| Beacon ID | 2 B | Unique ID |
| Writer ID | 1 B | Which robot wrote it |
| Event Type | 1 B | 0=checkpoint, 1=victim, 2=fire, 3=gas |
| Local X | 2 B | cm |
| Local Y | 2 B | cm |
| Local Z | 1 B | floor |
| Timestamp | 4 B | Unix time |
| TTL | 2 B | seconds |
| Confidence | 1 B | 0-255 mapped to 0.0-1.0 |
| Next Beacon ID | 2 B | 0 = none |
| CRC | 2 B | Error check |

Total: ~20 bytes.

## Aging
- Executor computes age = now - timestamp.
- If age > TTL, ignore beacon.
- Effective confidence = confidence * exp(-age / tau).
