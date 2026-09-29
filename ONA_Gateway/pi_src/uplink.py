"""
Command post communication (UplinkManager)
"""
import json
import logging
import time
import threading
import requests

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

class UplinkManager:
    def __init__(self, mode="MQTT", mqtt_host="localhost", mqtt_port=1883, http_url=""):
        self.mode = mode
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.http_url = http_url
        self.connected = False
        self.client = None
        self.store_forward = None
        
        if self.mode == "MQTT" and mqtt:
            self.client = mqtt.Client()
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            
    def set_store_forward(self, sf_queue):
        self.store_forward = sf_queue
            
    def start(self):
        if self.mode == "MQTT" and self.client:
            threading.Thread(target=self._mqtt_loop, daemon=True).start()
        elif self.mode == "HTTP":
            self.connected = True
            
    def _mqtt_loop(self):
        while True:
            try:
                self.client.connect(self.mqtt_host, self.mqtt_port, 60)
                self.client.loop_forever()
            except Exception as e:
                logging.error(f"MQTT connect error: {e}")
                self.connected = False
                time.sleep(5)
                
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logging.info("MQTT connected")
            if self.store_forward:
                self.store_forward.drain(self)
        else:
            self.connected = False
            
    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        logging.warning("MQTT disconnected")
        
    def is_connected(self) -> bool:
        return self.connected
        
    def _publish(self, topic: str, payload: dict):
        if not self.connected:
            if self.store_forward:
                self.store_forward.enqueue(topic, json.dumps(payload), 0)
            return False
            
        try:
            if self.mode == "MQTT":
                self.client.publish(topic, json.dumps(payload), qos=1)
                return True
            elif self.mode == "HTTP":
                resp = requests.post(f"{self.http_url}/{topic}", json=payload, timeout=2)
                if resp.status_code == 200:
                    return True
                else:
                    if self.store_forward:
                        self.store_forward.enqueue(topic, json.dumps(payload), 0)
                    return False
        except Exception as e:
            logging.error(f"Publish failed: {e}")
            if self.store_forward:
                self.store_forward.enqueue(topic, json.dumps(payload), 0)
            return False

    def publish_beacon(self, beacon_json: dict):
        self._publish("living_map/beacons", beacon_json)

    def publish_telemetry(self, telemetry_json: dict):
        self._publish("living_map/telemetry", telemetry_json)

    def publish_mission_status(self, status_json: dict):
        self._publish("living_map/missions", status_json)
