import json
import logging
import os
import time
from typing import Callable

import paho.mqtt.client as mqtt


class MqttServiceClient:
    def __init__(self, client_id: str):
        self.host = os.getenv("BROKER_HOST", "broker")
        self.port = int(os.getenv("BROKER_PORT", "1883"))
        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

    def connect_with_retry(self) -> None:
        while True:
            try:
                self.client.connect(self.host, self.port, keepalive=60)
                logging.info("Connected to MQTT broker %s:%s", self.host, self.port)
                return
            except Exception as exc:
                logging.warning("MQTT connection failed: %s. Retrying in 2s...", exc)
                time.sleep(2)

    def start(self) -> None:
        self.connect_with_retry()
        self.client.loop_start()

    def stop(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()

    def publish_json(self, topic: str, payload: dict) -> None:
        data = json.dumps(payload)
        self.client.publish(topic, data)

    def subscribe_json(self, topic: str, handler: Callable[[dict], None]) -> None:
        def on_message(_client, _userdata, msg):
            try:
                payload = json.loads(msg.payload.decode("utf-8"))
                handler(payload)
            except Exception as exc:
                logging.exception("Failed to process message on %s: %s", msg.topic, exc)

        self.client.subscribe(topic)
        self.client.message_callback_add(topic, on_message)
        logging.info("Subscribed to %s", topic)
