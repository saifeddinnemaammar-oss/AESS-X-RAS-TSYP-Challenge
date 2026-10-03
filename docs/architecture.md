## ONA Bus Isolation Diagram
```mermaid
flowchart LR
    LoRa((LoRa 868MHz)) -->|SPI| ESP32[ESP32 Hardware Firewall]
    ESP32 -->|Serial UART| Pi[Raspberry Pi 4B]
    UART[UART /dev/ttyAMA0] -->|GNSS NMEA| Pi
    Pi -->|iptables Blocked| USB[USB 4G Modem]