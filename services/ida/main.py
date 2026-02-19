import logging
import os
import signal
import sys
import time
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from common.log import configure_logging
from common.mqtt_client import MqttServiceClient
from common.schema import REQUIRED_FEATURES, utc_now_iso, validate_device_message
from common.topics import IDA_OUT, TMA_TO_IDA

ARTIFACT_DIR = Path("/app/artifacts")
MODEL_PATH = ARTIFACT_DIR / "ida_model.joblib"
FEATURES_PATH = ARTIFACT_DIR / "feature_list.joblib"
DATA_PATH = Path("/app/data/nsl_kdd_sample.csv")

CATEGORICAL = ["protocol_type", "service", "flag"]
NUMERIC = [
    "duration",
    "src_bytes",
    "dst_bytes",
    "wrong_fragment",
    "urgent",
    "count",
    "srv_count",
]


def load_or_train_model() -> tuple[Pipeline, list[str]]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    if MODEL_PATH.exists() and FEATURES_PATH.exists():
        logging.info("Loading existing IDA model artifacts")
        model = joblib.load(MODEL_PATH)
        features = joblib.load(FEATURES_PATH)
        return model, features

    logging.info("Training IDA model from %s", DATA_PATH)
    df = pd.read_csv(DATA_PATH)

    X = df[REQUIRED_FEATURES]
    y = df["label"].map(lambda x: 1 if str(x).lower() in {"attack", "anomaly", "malicious", "1"} else 0)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("clf", LogisticRegression(max_iter=300, solver="lbfgs")),
        ]
    )
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(REQUIRED_FEATURES, FEATURES_PATH)
    logging.info("Saved IDA artifacts to %s", ARTIFACT_DIR)

    return model, REQUIRED_FEATURES


def main() -> None:
    configure_logging("ida")
    threshold = float(os.getenv("IDA_THRESH", "0.6"))
    model, feature_list = load_or_train_model()

    mqtt = MqttServiceClient("ida-agent")
    mqtt.start()

    def handle(payload: dict) -> None:
        if not validate_device_message(payload):
            return

        row = {k: payload["features"][k] for k in feature_list}
        x = pd.DataFrame([row])
        proba_attack = float(model.predict_proba(x)[0][1])
        label = "attack" if proba_attack >= threshold else "normal"

        event = {
            "message_id": payload["message_id"],
            "device_id": payload["device_id"],
            "timestamp": utc_now_iso(),
            "ida": {
                "label": label,
                "attack_probability": round(proba_attack, 4),
                "threshold": threshold,
            },
        }
        mqtt.publish_json(IDA_OUT, event)

    mqtt.subscribe_json(TMA_TO_IDA, handle)

    def shutdown(_sig, _frame):
        mqtt.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
