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
| Beacon missing or moved | Re-verify with local sensors; fallback to map. |
| Beacon stale (TTL expired) | Ignore beacon; decay confidence to 0. |
| LoRa module dies | Fallback to dead-reckoning and IMU. |
| LiDAR dies | Fallback to IMU and visual odometry (camera). |
| IMU dies | Rely on LiDAR SLAM exclusively. |
| Robot battery low | Abort mission; return to base immediately. |
| Verification fails | Mark event as invalid; send update via LoRa. |
| Hazard too close | Engage obstacle avoidance; re-path around hazard. |
| ONA unreachable | Store data locally; re-attempt comms periodically. |
| Motor stall | Reverse briefly; attempt alternate path. |
| Magnetic wake-up fails | Pre-mission physical check of reed switch. |
| CRC errors | ONA firewall drops invalid packets; beacon resends. |
| ONA SPI errors | Hardware watchdog restarts SPI interface. |
| ONA queue overflow | Drop oldest packets first (FIFO). |
