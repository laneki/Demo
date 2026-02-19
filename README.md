# IoT Cybersecurity Multi-Agent Simulation

A complete distributed simulation of an IoT cybersecurity multi-agent pipeline built with Python 3.11, MQTT, Docker Compose, FastAPI, and a live HTML/CSS/JS dashboard.

## Quick Start

```bash
docker compose up --build
```

Then open:

- Dashboard: http://localhost:8080
- Metrics API: http://localhost:8000/api/metrics
- Events API: http://localhost:8000/api/events

No extra setup is required.

---

## Architecture

Services:

- `iot_dev`: IoT traffic simulator (NSL-KDD-like records)
- `aaa`: Authentication & Authorization Agent
- `tma`: Traffic Management Agent (fan-out dispatcher)
- `ida`: Intrusion Detection Agent (scikit-learn model, train once)
- `vma`: Vulnerability Management Agent (risk scoring)
- `metrics`: FastAPI metrics/event collector + API
- `dashboard`: Static dashboard UI (polling metrics API)
- `broker`: Eclipse Mosquitto MQTT broker

### Data Flow Diagram (ASCII)

```text
+----------------+
|  IoT Devices   |
|   (iot_dev)    |
+--------+-------+
         |
         | iotmas/devices/data
         v
+----------------+
|      AAA       |
| authz filter   |
+---+--------+---+
    |        |
    |        +------------------> iotmas/aaa/blocked ---> Metrics
    |
    +---------------------------> iotmas/aaa/authorized ---> Metrics + TMA
                                              |
                                              v
                                      +---------------+
                                      |      TMA      |
                                      | fan-out       |
                                      +---+-------+---+
                                          |       |
                               to_ida ----+       +---- to_vma
                                          v       v
                                        +---+   +---+
                                        |IDA|   |VMA|
                                        +---+   +---+
                                          |       |
                                          +---+---+
                                              |
                                              v
                                          Metrics API
                                              |
                                              v
                                           Dashboard
```

---

## Topic Map

- `iotmas/devices/data` : `iot_dev -> aaa`
- `iotmas/aaa/authorized` : `aaa -> tma + metrics`
- `iotmas/aaa/blocked` : `aaa -> metrics`
- `iotmas/tma/to_ida` : `tma -> ida`
- `iotmas/tma/to_vma` : `tma -> vma`
- `iotmas/ida/out` : `ida -> metrics`
- `iotmas/vma/out` : `vma -> metrics`

---

## IDA Train-Once Logic

The IDA service uses a persisted artifact volume mounted at `/app/artifacts`.

- On startup:
  - If `/app/artifacts/ida_model.joblib` and `/app/artifacts/feature_list.joblib` exist, it loads them.
  - Otherwise, it trains a scikit-learn pipeline using `data/nsl_kdd_sample.csv`, then saves both artifacts.
- This ensures no retraining on subsequent restarts unless artifacts are removed.

---

## Configuration (Environment Variables)

Defaults are defined in `docker-compose.yml`.

- `BROKER_HOST=broker`
- `BROKER_PORT=1883`
- `AUTH_RATE=0.7`
- `PUBLISH_INTERVAL_MS=300`
- `IDA_THRESH=0.6`
- `EVENTS_MAX=50`

---

## Extensibility: Adding a New Agent

1. Define one or more new MQTT topics in `services/common/topics.py`.
2. Create a new folder under `services/<new_agent>/` with:
   - `main.py`
   - `requirements.txt`
   - `Dockerfile`
3. Subscribe/publish using `services/common/mqtt_client.py`.
4. Add service definition to `docker-compose.yml`.
5. Optionally subscribe in `metrics` and update counter/event logic.

This plug-in pattern allows easy horizontal expansion of new defensive/analytic agents.

---

## Dataset Notes

The project includes a synthetic local dataset at:

- `data/nsl_kdd_sample.csv`

To replace with real NSL-KDD:

1. Keep the same feature column names:
   - `duration, protocol_type, service, flag, src_bytes, dst_bytes, wrong_fragment, urgent, count, srv_count, label`
2. Replace file contents with real records.
3. Remove old IDA artifacts so retraining can occur:
   ```bash
   docker compose down -v
   docker compose up --build
   ```

---

## Production-Style Notes

- Decoupled services communicate via MQTT topics.
- Shared message schema and topic constants in `services/common`.
- Logging and validation helpers are centralized.
- Metrics API is isolated from MQTT ingestion logic.
- Dashboard never connects directly to MQTT (API-only).
