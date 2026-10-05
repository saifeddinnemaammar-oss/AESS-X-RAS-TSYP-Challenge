# Deployment and Failure Management

## Running the System

### Simulation (Software-Only)
You can test the translation and ingest pipelines without physical sensor inputs using the provided unit tests:
```bash
pytest tests/
```

### Physical Hardware Deployment
To launch the actual robotic nodes once hardware is configured:

**ONA Gateway:**
Runs the LoRa ingest, translation, and forwarding daemon.
```bash
cd ONA_Gateway/pi_src
python3 ona_gateway.py
```

**Writer Robot:**
Initializes the ROS2 SLAM nodes, Vision AI, and ESP32 bridge.
```bash
cd Writer_Robot/pi_src
python3 writer_node.py
```

## Failure Cases and Mitigations

| Failure | Mitigation |
|---------|------------|
| Writer loses power | Beacons persist critical info; ONA stores data. |
| Beacon battery dies | Redundant beacons; Executor skips to next. |
| ONA uplink drops | Store-and-forward queue; resend when link returns. |
| False positive event | Multi-sensor confirmation; confidence threshold. |
| Executor cannot find beacon | Search pattern; return to last known. |
| RF interference | LoRa sub-GHz; ALOHA retries; multiple beacons. |
| Map drift | Loop closure; anchor beacons. |
| CRC errors | ONA firewall drops invalid packets; beacon resends. |
