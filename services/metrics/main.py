import os
import threading
from collections import deque
from datetime import datetime
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from common.log import configure_logging
from common.mqtt_client import MqttServiceClient
from common.topics import AAA_AUTHORIZED, AAA_BLOCKED, IDA_OUT, VMA_OUT

configure_logging("metrics")

app = FastAPI(title="IoT MAS Metrics API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

state_lock = threading.Lock()
EVENTS_MAX = int(os.getenv("EVENTS_MAX", "50"))

metrics: dict[str, int] = {
    "total_received": 0,
    "authorized": 0,
    "blocked": 0,
    "ida_attack": 0,
    "ida_normal": 0,
    "vma_high_risk": 0,
}
recent_events: deque[dict[str, Any]] = deque(maxlen=EVENTS_MAX)

mqtt = MqttServiceClient("metrics-service")


def append_event(event_type: str, payload: dict) -> None:
    event = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "payload": payload,
    }
    with state_lock:
        recent_events.appendleft(event)


def on_authorized(payload: dict) -> None:
    with state_lock:
        metrics["total_received"] += 1
        metrics["authorized"] += 1
    append_event("aaa_authorized", payload)


def on_blocked(payload: dict) -> None:
    with state_lock:
        metrics["total_received"] += 1
        metrics["blocked"] += 1
    append_event("aaa_blocked", payload)


def on_ida(payload: dict) -> None:
    label = payload.get("ida", {}).get("label", "normal")
    with state_lock:
        if label == "attack":
            metrics["ida_attack"] += 1
        else:
            metrics["ida_normal"] += 1
    append_event("ida_out", payload)


def on_vma(payload: dict) -> None:
    risk = payload.get("vma", {}).get("risk_score", 0)
    with state_lock:
        if risk >= 70:
            metrics["vma_high_risk"] += 1
    append_event("vma_out", payload)


@app.on_event("startup")
def startup_event() -> None:
    mqtt.start()
    mqtt.subscribe_json(AAA_AUTHORIZED, on_authorized)
    mqtt.subscribe_json(AAA_BLOCKED, on_blocked)
    mqtt.subscribe_json(IDA_OUT, on_ida)
    mqtt.subscribe_json(VMA_OUT, on_vma)


@app.on_event("shutdown")
def shutdown_event() -> None:
    mqtt.stop()


@app.get("/api/metrics")
def get_metrics() -> dict:
    with state_lock:
        return dict(metrics)


@app.get("/api/events")
def get_events() -> dict:
    with state_lock:
        return {"items": list(recent_events)}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
