import signal
import sys
import time

from common.log import configure_logging
from common.mqtt_client import MqttServiceClient
from common.topics import AAA_AUTHORIZED, TMA_TO_IDA, TMA_TO_VMA


def main() -> None:
    configure_logging("tma")
    mqtt = MqttServiceClient("tma-agent")
    mqtt.start()

    def handle(payload: dict) -> None:
        mqtt.publish_json(TMA_TO_IDA, payload)
        mqtt.publish_json(TMA_TO_VMA, payload)

    mqtt.subscribe_json(AAA_AUTHORIZED, handle)

    def shutdown(_sig, _frame):
        mqtt.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
