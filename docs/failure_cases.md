# Failure Cases and Mitigations

| Failure | Mitigation |
|---------|------------|
| Writer loses power | Beacons persist critical info; ONA stores data. |
| Beacon battery dies | Redundant beacons; Executor skips to next. |
| ONA uplink drops | Store-and-forward queue; resend when link returns. |
| GPS unavailable at ONA | Use surveyed entry coordinates. |
| False positive event | Multi-sensor confirmation; confidence threshold. |
| Executor cannot find beacon | Search pattern; return to last known. |
| RF interference | LoRa sub-GHz; retries; multiple beacons. |
| Map drift | Loop closure; anchor beacons. |
