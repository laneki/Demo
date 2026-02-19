import json
import os
import time
from typing import Callable, Dict, Optional

import paho.mqtt.client as mqtt

from .log import get_logger


class MQTTService:
    def __init__(self, client_id: str):
        self.logger = get_logger(client_id)
        self.host = os.getenv("BROKER_HOST", "broker")
        self.port = int(os.getenv("BROKER_PORT", "1883"))
        self.client = mqtt.Client(client_id=client_id, clean_session=True)
        self.client.enable_logger(self.logger)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.handlers: Dict[str, Callable[[str, dict], None]] = {}

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("Connected to MQTT broker at %s:%s", self.host, self.port)
            for topic in self.handlers:
                client.subscribe(topic)
                self.logger.info("Subscribed topic=%s", topic)
        else:
            self.logger.error("MQTT connect failed rc=%s", rc)

    def _on_disconnect(self, client, userdata, rc):
        self.logger.warning("Disconnected from MQTT rc=%s; retrying...", rc)
        while True:
            try:
                client.reconnect()
                self.logger.info("MQTT reconnected")
                break
            except Exception as exc:
                self.logger.error("Reconnect failed: %s", exc)
                time.sleep(2)

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as exc:
            self.logger.error("Invalid JSON on %s: %s", msg.topic, exc)
            return

        handler = self.handlers.get(msg.topic)
        if handler:
            handler(msg.topic, payload)

    def add_handler(self, topic: str, handler: Callable[[str, dict], None]):
        self.handlers[topic] = handler

    def connect(self):
        self.client.connect(self.host, self.port, keepalive=60)

    def publish(self, topic: str, payload: dict):
        self.client.publish(topic, json.dumps(payload), qos=0, retain=False)

    def start(self):
        self.connect()
        self.client.loop_forever()

    def loop_start(self):
        self.connect()
        self.client.loop_start()
