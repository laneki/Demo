# IoT MAS Simulator (MQTT + FastAPI + Dashboard)

A runnable, Dockerized simulation of a distributed IoT cybersecurity Multi-Agent System inspired by layered MAS architectures (AAA, TMA, IDA, VMA).

## What it does

1. Device simulator publishes synthetic NSL-KDD-like traffic records.
2. AAA authorizes/blocks each record (randomized by `AUTH_RATE`).
3. TMA fans out each authorized record **in parallel** to IDA and VMA.
4. IDA trains once on startup (if no saved model), persists model to disk, then predicts `normal` vs `attack` for each message.
5. VMA computes a heuristic vulnerability risk score (`0..100`) and emits factors.
6. Metrics API aggregates live counters/events and serves dashboard data.
7. Dashboard (nginx static site) polls metrics endpoints every second.

## Run

```bash
docker compose up --build
```

Open dashboard:

- http://localhost:8080

## Configurable environment variables

Configured in `docker-compose.yml`:

- `BROKER_HOST=broker`
- `BROKER_PORT=1883`
- `AUTH_RATE=0.7`
- `PUBLISH_INTERVAL_MS=300`
- `IDA_THRESH=0.6`
- `EVENTS_MAX=50`

## Project layout

- `services/common`: shared MQTT, schemas, logging, topics
- `services/device_sim`: synthetic device publisher
- `services/aaa`: authorization agent
- `services/tma`: traffic management fan-out agent
- `services/ida`: intrusion detection agent (train/load + predict)
- `services/vma`: vulnerability management/risk scoring agent
- `services/metrics`: FastAPI metrics/event collector
- `dashboard`: HTML/CSS/JS static frontend
- `data/nsl_kdd_sample.csv`: synthetic train data shaped like NSL-KDD subset

## Replace synthetic CSV with real NSL-KDD later

1. Put your cleaned NSL-KDD CSV at `data/nsl_kdd_sample.csv` (or update `IDA_TRAIN_CSV` env var in compose and IDA).
2. Ensure columns include:
   - `duration, protocol, service, flag, src_bytes, dst_bytes, wrong_fragment, urgent, count, srv_count, label`
3. Remove old model artifacts to force retraining:

```bash
rm -rf artifacts/ida/*
```

4. Restart IDA service:

```bash
docker compose up --build ida
```

## Add a new agent later

1. Create `services/<new_agent>/main.py` and `Dockerfile`.
2. Import shared helpers from `services/common`.
3. Define new topics in `services/common/topics.py`.
4. Subscribe/publish with `MQTTService` helper.
5. Add service entry in `docker-compose.yml`.
6. (Optional) publish compact events to `iotmas/metrics/events` for dashboard visibility.
