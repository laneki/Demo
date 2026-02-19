from datetime import datetime
from typing import Any, Dict

REQUIRED_FEATURES = [
    "duration",
    "protocol_type",
    "service",
    "flag",
    "src_bytes",
    "dst_bytes",
    "wrong_fragment",
    "urgent",
    "count",
    "srv_count",
]


def validate_device_message(payload: Dict[str, Any]) -> bool:
    if not all(key in payload for key in ["message_id", "device_id", "timestamp", "features"]):
        return False

    features = payload.get("features")
    if not isinstance(features, dict):
        return False

    return all(key in features for key in REQUIRED_FEATURES)


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"
