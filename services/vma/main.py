import signal
import sys
import time

from common.log import configure_logging
from common.mqtt_client import MqttServiceClient
from common.schema import utc_now_iso, validate_device_message
from common.topics import TMA_TO_VMA, VMA_OUT


def compute_risk(features: dict) -> tuple[int, list[str]]:
    score = 10
    factors: list[str] = []

    if features["src_bytes"] > 30000:
        score += 25
        factors.append("high_src_bytes")
    if features["dst_bytes"] > 20000:
        score += 20
        factors.append("high_dst_bytes")
    if features["wrong_fragment"] > 0:
        score += 15
        factors.append("wrong_fragment_present")
    if features["urgent"] > 0:
        score += 10
        factors.append("urgent_packets")
    if features["count"] > 120 or features["srv_count"] > 120:
        score += 20
        factors.append("high_connection_rate")
    if features["flag"] in {"REJ", "RSTR"}:
        score += 10
        factors.append("suspicious_flag")

    return min(score, 100), factors


def main() -> None:
    configure_logging("vma")
    mqtt = MqttServiceClient("vma-agent")
    mqtt.start()

    def handle(payload: dict) -> None:
        if not validate_device_message(payload):
            return

        risk_score, factors = compute_risk(payload["features"])
        event = {
            "message_id": payload["message_id"],
            "device_id": payload["device_id"],
            "timestamp": utc_now_iso(),
            "vma": {
                "risk_score": risk_score,
                "risk_level": "high" if risk_score >= 70 else "medium" if risk_score >= 40 else "low",
                "factors": factors,
            },
        }
        mqtt.publish_json(VMA_OUT, event)

    mqtt.subscribe_json(TMA_TO_VMA, handle)

    def shutdown(_sig, _frame):
        mqtt.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
