import logging
import os
import random
import signal
import sys
import time

from common.log import configure_logging
from common.mqtt_client import MqttServiceClient
from common.schema import validate_device_message
from common.topics import AAA_AUTHORIZED, AAA_BLOCKED, DEVICE_DATA


def main() -> None:
    configure_logging("aaa")
    auth_rate = float(os.getenv("AUTH_RATE", "0.7"))
    mqtt = MqttServiceClient("aaa-agent")
    mqtt.start()

    def handle(payload: dict) -> None:
        if not validate_device_message(payload):
            logging.warning("Dropped invalid payload")
            return

        if random.random() <= auth_rate:
            mqtt.publish_json(AAA_AUTHORIZED, payload)
        else:
            mqtt.publish_json(AAA_BLOCKED, payload)

    mqtt.subscribe_json(DEVICE_DATA, handle)
    logging.info("AAA agent running with AUTH_RATE=%s", auth_rate)

    def shutdown(_sig, _frame):
        mqtt.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
