from pydantic import ValidationError

from services.common.log import get_logger
from services.common.mqtt_client import MQTTService
from services.common.schema import DeviceMessage
from services.common.topics import METRICS_EVENTS, TMA_IN, TMA_TO_IDA, TMA_TO_VMA

logger = get_logger("tma")


def main():
    mqtt = MQTTService("tma")

    def handle(_topic: str, payload: dict):
        try:
            msg = DeviceMessage.model_validate(payload)
        except ValidationError as exc:
            logger.error("Invalid TMA payload: %s", exc)
            return

        body = msg.model_dump(mode="json")
        mqtt.publish(TMA_TO_IDA, body)
        mqtt.publish(TMA_TO_VMA, body)
        mqtt.publish(METRICS_EVENTS, {"type": "tma_fanout", "message_id": msg.message_id, "device_id": msg.device_id})

    mqtt.add_handler(TMA_IN, handle)
    logger.info("TMA started")
    mqtt.start()


if __name__ == "__main__":
    main()
