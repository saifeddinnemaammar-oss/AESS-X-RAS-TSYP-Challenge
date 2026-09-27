"""
SX1276 LoRa driver for Raspberry Pi using spidev + RPi.GPIO.
"""

import spidev
import RPi.GPIO as GPIO
import time
import threading
import logging

logger = logging.getLogger(__name__)

# SX1276 Registers
REG_FIFO = 0x00
REG_OP_MODE = 0x01
REG_FRF_MSB = 0x06
REG_FRF_MID = 0x07
REG_FRF_LSB = 0x08
REG_PA_CONFIG = 0x09
REG_FIFO_ADDR_PTR = 0x0D
REG_FIFO_TX_BASE_ADDR = 0x0E
REG_FIFO_RX_BASE_ADDR = 0x0F
REG_FIFO_RX_CURRENT_ADDR = 0x10
REG_IRQ_FLAGS = 0x12
REG_RX_NB_BYTES = 0x13
REG_PKT_SNR_VALUE = 0x19
REG_PKT_RSSI_VALUE = 0x1A
REG_MODEM_CONFIG_1 = 0x1D
REG_MODEM_CONFIG_2 = 0x1E
REG_SYMB_TIMEOUT_LSB = 0x1F
REG_PREAMBLE_MSB = 0x20
REG_PREAMBLE_LSB = 0x21
REG_PAYLOAD_LENGTH = 0x22
REG_DIO_MAPPING_1 = 0x40
REG_VERSION = 0x42

# Modes
MODE_SLEEP = 0x80
MODE_STDBY = 0x81
MODE_TX = 0x83
MODE_RX_CONT = 0x85

class LoRaRadio:
    def __init__(self, spi_bus=0, spi_device=0, ce_pin=8, rst_pin=22, dio0_pin=25):
        self.spi = spidev.SpiDev()
        self.spi_bus = spi_bus
        self.spi_device = spi_device
        self.ce_pin = ce_pin
        self.rst_pin = rst_pin
        self.dio0_pin = dio0_pin
        self.lock = threading.Lock()
        self.on_receive = None
        self._running = False
        
    def init(self):
        logger.info("Initializing LoRa SX1276...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.setup(self.dio0_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # Reset radio
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.01)
        
        self.spi.open(self.spi_bus, self.spi_device)
        self.spi.max_speed_hz = 5000000
        
        version = self._read_register(REG_VERSION)
        if version != 0x12:
            raise RuntimeError(f"SX1276 not found. Version: 0x{version:02x}")
            
        self.configure()
        self._running = True
        GPIO.add_event_detect(self.dio0_pin, GPIO.RISING, callback=self._handle_interrupt)
        
    def _write_register(self, reg, value):
        with self.lock:
            self.spi.xfer2([reg | 0x80, value])
            
    def _read_register(self, reg):
        with self.lock:
            return self.spi.xfer2([reg & 0x7F, 0x00])[1]
            
    def configure(self, freq=868.0, sf=7, bw=125, tx_power=14, preamble=8):
        self.set_mode(MODE_SLEEP)
        
        # Set frequency (frf = int(868e6 / 61.035))
        frf = int((freq * 1000000) / 61.03515625)
        self._write_register(REG_FRF_MSB, (frf >> 16) & 0xFF)
        self._write_register(REG_FRF_MID, (frf >> 8) & 0xFF)
        self._write_register(REG_FRF_LSB, frf & 0xFF)
        
        # PA Config (assuming PA_BOOST)
        self._write_register(REG_PA_CONFIG, 0x80 | (tx_power - 2))
        
        # Modem config
        bw_val = 0x70 # 125kHz
        cr_val = 0x02 # 4/5
        self._write_register(REG_MODEM_CONFIG_1, bw_val | (cr_val << 1))
        self._write_register(REG_MODEM_CONFIG_2, (sf << 4) | 0x04) # RX payload CRC ON
        
        # Preamble
        self._write_register(REG_PREAMBLE_MSB, (preamble >> 8) & 0xFF)
        self._write_register(REG_PREAMBLE_LSB, preamble & 0xFF)
        
        self._write_register(REG_FIFO_TX_BASE_ADDR, 0x00)
        self._write_register(REG_FIFO_RX_BASE_ADDR, 0x00)
        
        self.set_mode(MODE_STDBY)
        
    def set_mode(self, mode):
        self._write_register(REG_OP_MODE, mode)
        
    def send_packet(self, data):
        self.set_mode(MODE_STDBY)
        self._write_register(REG_DIO_MAPPING_1, 0x40) # DIO0 = TxDone
        self._write_register(REG_FIFO_ADDR_PTR, 0x00)
        self._write_register(REG_PAYLOAD_LENGTH, len(data))
        
        with self.lock:
            self.spi.xfer2([REG_FIFO | 0x80] + list(data))
            
        self.set_mode(MODE_TX)
        # Interrupt will handle TX_DONE
        
    def receive_packet(self):
        self.set_mode(MODE_STDBY)
        self._write_register(REG_DIO_MAPPING_1, 0x00) # DIO0 = RxDone
        self.set_mode(MODE_RX_CONT)
        
    def get_rssi(self):
        return self._read_register(REG_PKT_RSSI_VALUE) - 157
        
    def _handle_interrupt(self, channel):
        if not self._running:
            return
        irq_flags = self._read_register(REG_IRQ_FLAGS)
        self._write_register(REG_IRQ_FLAGS, irq_flags) # Clear flags
        
        if irq_flags & 0x40: # RxDone
            length = self._read_register(REG_RX_NB_BYTES)
            current_addr = self._read_register(REG_FIFO_RX_CURRENT_ADDR)
            self._write_register(REG_FIFO_ADDR_PTR, current_addr)
            with self.lock:
                data = self.spi.xfer2([REG_FIFO & 0x7F] + [0x00] * length)[1:]
            rssi = self.get_rssi()
            if self.on_receive:
                self.on_receive(bytes(data), rssi)
                
        elif irq_flags & 0x08: # TxDone
            logger.debug("TX Done")
            self.set_mode(MODE_STDBY)
            
    def cleanup(self):
        logger.info("Cleaning up LoRa Radio...")
        self._running = False
        self.set_mode(MODE_SLEEP)
        GPIO.remove_event_detect(self.dio0_pin)
        self.spi.close()
        # Do not cleanup GPIO globally if others are using it, but ok for now.

