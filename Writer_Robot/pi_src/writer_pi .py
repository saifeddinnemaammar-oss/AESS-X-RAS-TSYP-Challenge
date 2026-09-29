"""
Writer Robot: Main Computational Node
Handles SLAM exploration logic, LoRa mesh networking, and delegates hardware actuation to ESP32.
"""

import time
import struct
import serial
import spidev
import crcmod

# --- CONFIGURATION ---
ESP32_PORT = '/dev/ttyUSB0'  
BAUD_RATE = 115200
LORA_SPI_BUS = 0
LORA_SPI_DEVICE = 0

# Hazard Signatures
HAZARD_ANCHOR = 0x01
HAZARD_VICTIM = 0x02
HAZARD_GAS    = 0x03
HAZARD_FIRE   = 0x04

class WriterPi:
    def __init__(self):
        self.current_x = 0.0
        self.current_y = 0.0
        
        # 1. Initialize ESP32 Serial Link
        try:
            self.esp = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1)
            time.sleep(2) # Allow ESP32 to reboot on serial connect
            print("[SYS] ESP32 Serial Link Established.")
        except serial.SerialException:
            raise SystemExit("[ERR] ESP32 not found. Check USB connection.")

        # 2. Initialize LoRa SPI
        self.spi = spidev.SpiDev()
        self.spi.open(LORA_SPI_BUS, LORA_SPI_DEVICE)
        self.spi.max_speed_hz = 5000000
        self.spi.mode = 0
        
        # 3. Initialize CRC-16 (CCITT) for network security
        self.crc16 = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xFFFF, xorOut=0x0000)

    def send_esp_command(self, cmd):
        """Dispatches string commands to the ESP32 and blocks until acknowledged."""
        self.esp.write(f"{cmd}\n".encode('utf-8'))
        
        while True:
            if self.esp.in_waiting > 0:
                response = self.esp.readline().decode('utf-8').strip()
                if response == "ACK":
                    break
            time.sleep(0.05)

    def transmit_mesh_packet(self, hazard_type):
        """Constructs and transmits a 20-byte LoRa payload."""
        header = 0xAA55
        node_id = 0x01 # Writer ID
        
        # Pack 18 bytes: Header(2), Node(1), X(4), Y(4), Hazard(1), Pad(6)
        payload = struct.pack('>HBffB6s', header, node_id, self.current_x, self.current_y, hazard_type, b'\x00'*6)
        
        # Append 2-byte CRC
        full_packet = payload + struct.pack('>H', self.crc16(payload))
        
        self.spi.xfer2(list(full_packet))
        print(f"[LoRa TX] Node: {node_id} | Hazard: {hazard_type} | X:{self.current_x:.1f} Y:{self.current_y:.1f}")

    def execute_beacon_drop(self, hazard_type, x, y):
        """Sequence to lock coordinates, drop hardware, and broadcast data."""
        self.current_x = x
        self.current_y = y
        
        print(f"\n[ACTION] Target Reached (X:{x}, Y:{y}). Deploying Beacon...")
        self.send_esp_command("DROP_BEACON")
        self.transmit_mesh_packet(hazard_type)

    def run_exploration(self):
        """Main SLAM navigation and deployment loop."""
        print("[SYS] Boot complete. Commencing exploration phase.\n")
        
        # Waypoints mirroring the IEEE simulation
        mission_waypoints = [
            (2.0, 0.0, HAZARD_ANCHOR),
            (7.0, 3.5, HAZARD_VICTIM),
            (11.5, 3.0, HAZARD_GAS),
            (10.5, 7.0, HAZARD_FIRE)
        ]

        for x, y, hazard in mission_waypoints:
            print(f"[NAV] Routing to X:{x}, Y:{y}...")
            self.send_esp_command(f"DRIVE,{x},{y}")
            self.execute_beacon_drop(hazard, x, y)
            time.sleep(1) # Stabilization pause

        print("\n[NAV] Mission complete. Returning to ONA Gateway.")
        self.send_esp_command("DRIVE,0.0,0.0")

    def cleanup(self):
        self.esp.close()
        self.spi.close()

if __name__ == '__main__':
    writer = WriterPi()
    try:
        writer.run_exploration()
    except KeyboardInterrupt:
        print("\n[SYS] Emergency Stop Triggered.")
    finally:
        writer.cleanup()