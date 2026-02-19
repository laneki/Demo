import logging
import os
import random
import time
import uuid

from common.log import configure_logging
from common.mqtt_client import MqttServiceClient
from common.schema import utc_now_iso
from common.topics import DEVICE_DATA

DEVICE_IDS = [f"device-{i}" for i in range(1, 8)]
PROTOCOLS = ["tcp", "udp", "icmp"]
SERVICES = ["http", "smtp", "ftp", "ssh", "dns"]
FLAGS = ["SF", "S0", "REJ", "RSTR"]


def synth_features() -> dict:
    suspicious = random.random() < 0.25
    return {
        "duration": random.randint(0, 1000),
        "protocol_type": random.choice(PROTOCOLS),
        "service": random.choice(SERVICES),
        "flag": random.choice(FLAGS),
        "src_bytes": random.randint(20, 50000 if suspicious else 20000),
        "dst_bytes": random.randint(0, 45000 if suspicious else 15000),
        "wrong_fragment": random.randint(0, 3 if suspicious else 1),
        "urgent": random.randint(0, 2 if suspicious else 1),
        "count": random.randint(1, 200),
        "srv_count": random.randint(1, 200),
    }


def main() -> None:
    configure_logging("iot_dev")
    interval = int(os.getenv("PUBLISH_INTERVAL_MS", "300")) / 1000.0

    mqtt = MqttServiceClient("iot-device-sim")
    mqtt.start()

    logging.info("Starting IoT simulator with interval %.3fs", interval)
    try:
        while True:
            payload = {
                "message_id": str(uuid.uuid4()),
                "device_id": random.choice(DEVICE_IDS),
                "timestamp": utc_now_iso(),
                "features": synth_features(),
            }
            mqtt.publish_json(DEVICE_DATA, payload)
            time.sleep(interval)
    finally:
        mqtt.stop()


if __name__ == "__main__":
    main()
