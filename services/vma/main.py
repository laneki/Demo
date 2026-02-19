from pydantic import ValidationError

from services.common.log import get_logger
from services.common.mqtt_client import MQTTService
from services.common.schema import DeviceMessage
from services.common.topics import METRICS_EVENTS, TMA_TO_VMA, VMA_OUT

logger = get_logger("vma")


def compute_risk(msg: DeviceMessage) -> tuple[int, list[str]]:
    f = msg.features
    score = 10
    factors: list[str] = []

    if f.service in {"ftp", "smtp", "other"}:
        score += 20
        factors.append("unusual_service")
    if f.src_bytes + f.dst_bytes > 60000:
        score += 25
        factors.append("high_traffic_bytes")
    if f.count > 75 or f.srv_count > 75:
        score += 25
        factors.append("repeated_connections")
    if f.flag in {"REJ", "RSTO", "RSTR"}:
        score += 20
        factors.append("suspicious_flag")

    return min(score, 100), factors


def main():
    mqtt = MQTTService("vma")

    def handle(_topic: str, payload: dict):
        try:
            msg = DeviceMessage.model_validate(payload)
        except ValidationError as exc:
            logger.error("Invalid VMA payload: %s", exc)
            return

        risk, factors = compute_risk(msg)
        out = {
            "message_id": msg.message_id,
            "device_id": msg.device_id,
            "risk_score": risk,
            "factors": factors,
            "ts": msg.timestamp.isoformat(),
        }
        mqtt.publish(VMA_OUT, out)
        mqtt.publish(METRICS_EVENTS, {"type": "vma_risk", **out})

    mqtt.add_handler(TMA_TO_VMA, handle)
    logger.info("VMA started")
    mqtt.start()


if __name__ == "__main__":
    main()
