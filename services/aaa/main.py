import os
import random

from pydantic import ValidationError

from services.common.log import get_logger
from services.common.mqtt_client import MQTTService
from services.common.schema import DeviceMessage
from services.common.topics import AAA_AUTHORIZED, AAA_BLOCKED, AAA_IN, METRICS_EVENTS, TMA_IN

logger = get_logger("aaa")
AUTH_RATE = float(os.getenv("AUTH_RATE", "0.7"))


def main():
    mqtt = MQTTService("aaa")

    def handle(_topic: str, payload: dict):
        try:
            message = DeviceMessage.model_validate(payload)
        except ValidationError as exc:
            logger.error("Invalid payload: %s", exc)
            return

        authorized = random.random() < AUTH_RATE
        if authorized:
            out = {"status": "authorized", "payload": message.model_dump(mode="json")}
            mqtt.publish(AAA_AUTHORIZED, out)
            mqtt.publish(TMA_IN, message.model_dump(mode="json"))
            mqtt.publish(METRICS_EVENTS, {"type": "aaa_authorized", "message_id": message.message_id, "device_id": message.device_id})
        else:
            out = {
                "status": "blocked",
                "reason": "not_authorized",
                "payload": message.model_dump(mode="json"),
            }
            mqtt.publish(AAA_BLOCKED, out)
            mqtt.publish(METRICS_EVENTS, {"type": "aaa_blocked", "message_id": message.message_id, "device_id": message.device_id})

    mqtt.add_handler(AAA_IN, handle)
    logger.info("AAA started AUTH_RATE=%.2f", AUTH_RATE)
    mqtt.start()


if __name__ == "__main__":
    main()
