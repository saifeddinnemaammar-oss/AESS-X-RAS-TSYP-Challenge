"""
Writer LoRa communication manager.
"""
import time
import logging

class WriterLoRa:
    def __init__(self, radio=None):
        self.radio = radio

    def send_beacon_config(self, packet):
        logging.info(f"Sending beacon config: {len(packet)} bytes")
        if self.radio:
            self.radio.tx(packet)
        else:
            time.sleep(0.1)

    def wait_for_ack(self, timeout=2.0):
        start = time.time()
        while time.time() - start < timeout:
            if self.radio:
                rx_data = self.radio.rx()
                if rx_data and len(rx_data) >= 4:
                    return rx_data
            else:
                time.sleep(0.5)
                return b'ACK\x00'
            time.sleep(0.1)
        return None

    def broadcast_status(self, status_data):
        logging.info(f"Broadcasting status: {status_data}")
        packet = b'STAT' + b'\x00' * 16
        if self.radio:
            self.radio.tx(packet)

    def send_to_ona(self, packet):
        logging.info("Forwarding to ONA")
        if self.radio:
            self.radio.tx(packet)
