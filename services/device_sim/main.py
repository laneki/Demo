import os
import random
import time
from datetime import datetime
from uuid import uuid4

from services.common.log import get_logger
from services.common.mqtt_client import MQTTService
from services.common.topics import AAA_IN, DEVICES_DATA, METRICS_EVENTS

logger = get_logger("device_sim")
INTERVAL_MS = int(os.getenv("PUBLISH_INTERVAL_MS", "300"))

PROTOCOLS = ["tcp", "udp", "icmp"]
SERVICES = ["http", "https", "ssh", "dns", "smtp", "ftp", "other"]
FLAGS = ["SF", "S0", "REJ", "RSTR", "RSTO"]


def random_ip() -> str:
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def generate_message() -> dict:
    return {
        "message_id": str(uuid4()),
        "device_id": f"dev-{random.randint(1, 12):03d}",
        "timestamp": datetime.utcnow().isoformat(),
        "src_ip": random_ip(),
        "dst_ip": random_ip(),
        "features": {
            "duration": round(random.random() * 10, 3),
            "protocol": random.choice(PROTOCOLS),
            "service": random.choice(SERVICES),
            "flag": random.choice(FLAGS),
            "src_bytes": random.randint(10, 50000),
            "dst_bytes": random.randint(10, 50000),
            "wrong_fragment": random.randint(0, 2),
            "urgent": random.randint(0, 1),
            "count": random.randint(1, 100),
            "srv_count": random.randint(1, 100),
        },
    }


def main():
    mqtt = MQTTService("device_sim")
    mqtt.loop_start()
    logger.info("Device simulator started interval_ms=%s", INTERVAL_MS)

    while True:
        msg = generate_message()
        mqtt.publish(DEVICES_DATA, msg)
        mqtt.publish(AAA_IN, msg)
        mqtt.publish(METRICS_EVENTS, {"type": "device_generated", "message_id": msg["message_id"], "ts": msg["timestamp"]})
        time.sleep(INTERVAL_MS / 1000)


if __name__ == "__main__":
    main()
