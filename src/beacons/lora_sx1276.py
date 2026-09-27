"""
MicroPython SX1276 driver for ESP32.
"""

from machine import SPI, Pin
import time

# Registers
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
REG_PKT_RSSI_VALUE = 0x1A
REG_MODEM_CONFIG_1 = 0x1D
REG_MODEM_CONFIG_2 = 0x1E
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

class SX1276:
    def __init__(self, sck, mosi, miso, nss, rst, dio0):
        self.spi = SPI(1, baudrate=5000000, polarity=0, phase=0, sck=Pin(sck), mosi=Pin(mosi), miso=Pin(miso))
        self.nss = Pin(nss, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT)
        self.dio0 = Pin(dio0, Pin.IN)
        self.nss.value(1)
        self.on_receive = None
        
    def begin(self):
        self.rst.value(0)
        time.sleep_ms(10)
        self.rst.value(1)
        time.sleep_ms(10)
        
        version = self._read_register(REG_VERSION)
        if version != 0x12:
            return False
            
        self.configure()
        self.dio0.irq(trigger=Pin.IRQ_RISING, handler=self._handle_interrupt)
        return True
        
    def _write_register(self, reg, val):
        self.nss.value(0)
        self.spi.write(bytearray([reg | 0x80, val]))
        self.nss.value(1)
        
    def _read_register(self, reg):
        self.nss.value(0)
        self.spi.write(bytearray([reg & 0x7F]))
        val = self.spi.read(1)[0]
        self.nss.value(1)
        return val
        
    def configure(self, freq=868.0, sf=7, tx_power=14, preamble=8):
        self.set_mode(MODE_SLEEP)
        
        frf = int((freq * 1000000) / 61.03515625)
        self._write_register(REG_FRF_MSB, (frf >> 16) & 0xFF)
        self._write_register(REG_FRF_MID, (frf >> 8) & 0xFF)
        self._write_register(REG_FRF_LSB, frf & 0xFF)
        
        self._write_register(REG_PA_CONFIG, 0x80 | (tx_power - 2))
        
        bw_val = 0x70
        cr_val = 0x02
        self._write_register(REG_MODEM_CONFIG_1, bw_val | (cr_val << 1))
        self._write_register(REG_MODEM_CONFIG_2, (sf << 4) | 0x04)
        
        self._write_register(REG_PREAMBLE_MSB, (preamble >> 8) & 0xFF)
        self._write_register(REG_PREAMBLE_LSB, preamble & 0xFF)
        
        self._write_register(REG_FIFO_TX_BASE_ADDR, 0x00)
        self._write_register(REG_FIFO_RX_BASE_ADDR, 0x00)
        
        self.set_mode(MODE_STDBY)
        
    def set_mode(self, mode):
        self._write_register(REG_OP_MODE, mode)
        
    def send(self, data):
        self.set_mode(MODE_STDBY)
        self._write_register(REG_DIO_MAPPING_1, 0x40)
        self._write_register(REG_FIFO_ADDR_PTR, 0x00)
        self._write_register(REG_PAYLOAD_LENGTH, len(data))
        
        self.nss.value(0)
        self.spi.write(bytearray([REG_FIFO | 0x80]))
        self.spi.write(data)
        self.nss.value(1)
        
        self.set_mode(MODE_TX)
        
    def receive(self):
        self.set_mode(MODE_STDBY)
        self._write_register(REG_DIO_MAPPING_1, 0x00)
        self.set_mode(MODE_RX_CONT)
        
    def get_rssi(self):
        return self._read_register(REG_PKT_RSSI_VALUE) - 157
        
    def _handle_interrupt(self, pin):
        irq_flags = self._read_register(REG_IRQ_FLAGS)
        self._write_register(REG_IRQ_FLAGS, irq_flags)
        
        if irq_flags & 0x40: # RxDone
            length = self._read_register(REG_RX_NB_BYTES)
            current_addr = self._read_register(REG_FIFO_RX_CURRENT_ADDR)
            self._write_register(REG_FIFO_ADDR_PTR, current_addr)
            
            self.nss.value(0)
            self.spi.write(bytearray([REG_FIFO & 0x7F]))
            data = self.spi.read(length)
            self.nss.value(1)
            
            rssi = self.get_rssi()
            if self.on_receive:
                self.on_receive(data, rssi)
                
        elif irq_flags & 0x08: # TxDone
            self.set_mode(MODE_STDBY)
