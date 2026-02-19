import os
import threading
from collections import deque
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.common.log import get_logger
from services.common.mqtt_client import MQTTService
from services.common.topics import AAA_AUTHORIZED, AAA_BLOCKED, IDA_OUT, VMA_OUT

logger = get_logger("metrics")
EVENTS_MAX = int(os.getenv("EVENTS_MAX", "50"))

app = FastAPI(title="iot-mas-metrics")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

counters = {
    "total_received": 0,
    "authorized": 0,
    "blocked": 0,
    "ida_pred_attack": 0,
    "ida_pred_normal": 0,
    "vma_high_risk": 0,
}
events: deque[dict[str, Any]] = deque(maxlen=EVENTS_MAX)


def push_event(event_type: str, payload: dict):
    events.appendleft({"type": event_type, "payload": payload})


def mqtt_worker():
    mqtt = MQTTService("metrics")

    def on_auth(_topic: str, payload: dict):
        counters["total_received"] += 1
        counters["authorized"] += 1
        push_event("authorized", payload)

    def on_block(_topic: str, payload: dict):
        counters["total_received"] += 1
        counters["blocked"] += 1
        push_event("blocked", payload)

    def on_ida(_topic: str, payload: dict):
        if payload.get("prediction") == "attack":
            counters["ida_pred_attack"] += 1
        else:
            counters["ida_pred_normal"] += 1
        push_event("ida", payload)

    def on_vma(_topic: str, payload: dict):
        if int(payload.get("risk_score", 0)) >= 70:
            counters["vma_high_risk"] += 1
        push_event("vma", payload)

    mqtt.add_handler(AAA_AUTHORIZED, on_auth)
    mqtt.add_handler(AAA_BLOCKED, on_block)
    mqtt.add_handler(IDA_OUT, on_ida)
    mqtt.add_handler(VMA_OUT, on_vma)
    logger.info("Metrics MQTT worker started")
    mqtt.start()


@app.on_event("startup")
def startup_event():
    t = threading.Thread(target=mqtt_worker, daemon=True)
    t.start()


@app.get("/api/metrics")
def get_metrics():
    return counters


@app.get("/api/events")
def get_events():
    return {"events": list(events)[:20]}
