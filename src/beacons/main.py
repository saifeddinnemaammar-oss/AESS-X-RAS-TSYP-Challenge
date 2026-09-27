"""
Main beacon firmware implementing the 3-state duty cycle.
ESP32 MicroPython.
"""

import machine
import time
import struct
import config
from lora_sx1276 import SX1276

def calc_crc16(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def blink_led(led, times, delay_ms):
    for _ in range(times):
        led.value(1)
        time.sleep_ms(delay_ms)
        led.value(0)
        time.sleep_ms(delay_ms)

def main():
    led = machine.Pin(config.LED_PIN, machine.Pin.OUT)
    rtc = machine.RTC()
    reset_cause = machine.reset_cause()
    
    lora = SX1276(
        sck=config.SPI_SCK,
        mosi=config.SPI_MOSI,
        miso=config.SPI_MISO,
        nss=config.SPI_NSS,
        rst=config.SPI_RST,
        dio0=config.SPI_DIO0
    )
    
    if not lora.begin():
        print("LoRa init failed")
        machine.deepsleep(config.DEEP_SLEEP_MS)
        
    is_deep_sleep_wake = (reset_cause == machine.DEEPSLEEP_RESET)
    
    if not is_deep_sleep_wake:
        # State 1: BOOT & LISTEN
        blink_led(led, 5, 100)
        
        payload = None
        def rx_callback(data, rssi):
            nonlocal payload
            if len(data) == 20:
                payload_data = data[:-2]
                crc = struct.unpack('<H', data[-2:])[0]
                if calc_crc16(payload_data) == crc:
                    payload = data
                    
        lora.on_receive = rx_callback
        lora.receive()
        
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < config.RX_BOOT_TIMEOUT_MS:
            if payload:
                break
            time.sleep_ms(10)
            
        if payload:
            # State 2: DATA LOCK-IN
            rtc.memory(payload)
            
            # Send ACK (Type 0x02, beacon_id, status 0=OK)
            # Extracted from payload: beacon_id is bytes 0-1
            beacon_id = struct.unpack('<H', payload[0:2])[0]
            ack_packet = struct.pack('<B H B', 0x02, beacon_id, 0)
            lora.send(ack_packet)
            time.sleep_ms(config.TX_TIMEOUT_MS) # Wait for TX
            blink_led(led, 2, 500)
        else:
            # Failed to get payload, go to sleep and try again
            machine.deepsleep(config.DEEP_SLEEP_MS)
            
    # State 3: CONTINUOUS PULSING
    memory_data = rtc.memory()
    if memory_data and len(memory_data) == 20:
        # TX the payload
        lora.send(memory_data)
        time.sleep_ms(config.TX_TIMEOUT_MS)
        led.value(1)
        time.sleep_ms(50)
        led.value(0)
        
    # Deep sleep
    machine.deepsleep(config.DEEP_SLEEP_MS)

if __name__ == "__main__":
    main()
