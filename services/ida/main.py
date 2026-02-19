import os
from pathlib import Path

import joblib
import pandas as pd
from pydantic import ValidationError
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from services.common.log import get_logger
from services.common.mqtt_client import MQTTService
from services.common.schema import DeviceMessage
from services.common.topics import IDA_OUT, METRICS_EVENTS, TMA_TO_IDA

logger = get_logger("ida")
MODEL_PATH = Path("/app/artifacts/ida_model.joblib")
FEATURES_PATH = Path("/app/artifacts/ida_features.joblib")
TRAIN_CSV = Path("/app/data/nsl_kdd_sample.csv")
THRESH = float(os.getenv("IDA_THRESH", "0.6"))

NUMERIC = ["duration", "src_bytes", "dst_bytes", "wrong_fragment", "urgent", "count", "srv_count"]
CATEGORICAL = ["protocol", "service", "flag"]
FEATURES = NUMERIC + CATEGORICAL


def train_and_save() -> Pipeline:
    df = pd.read_csv(TRAIN_CSV)
    X = df[FEATURES]
    y = (df["label"].astype(str).str.lower() == "attack").astype(int)

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
            ("num", "passthrough", NUMERIC),
        ]
    )

    model = Pipeline(
        steps=[
            ("pre", preprocessor),
            ("clf", RandomForestClassifier(n_estimators=120, random_state=42)),
        ]
    )
    model.fit(X, y)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(FEATURES, FEATURES_PATH)
    logger.info("trained_first_time=true model_saved=%s", MODEL_PATH)
    return model


def load_or_train() -> Pipeline:
    if MODEL_PATH.exists() and FEATURES_PATH.exists():
        logger.info("Loading persisted model from disk")
        return joblib.load(MODEL_PATH)
    return train_and_save()


def build_row(msg: DeviceMessage) -> pd.DataFrame:
    f = msg.features
    row = {
        "duration": f.duration,
        "protocol": f.protocol,
        "service": f.service,
        "flag": f.flag,
        "src_bytes": f.src_bytes,
        "dst_bytes": f.dst_bytes,
        "wrong_fragment": f.wrong_fragment,
        "urgent": f.urgent,
        "count": f.count,
        "srv_count": f.srv_count,
    }
    return pd.DataFrame([row], columns=FEATURES)


def main():
    model = load_or_train()
    mqtt = MQTTService("ida")

    def handle(_topic: str, payload: dict):
        try:
            msg = DeviceMessage.model_validate(payload)
        except ValidationError as exc:
            logger.error("Invalid IDA payload: %s", exc)
            return

        X = build_row(msg)
        proba = None
        if hasattr(model, "predict_proba"):
            proba = float(model.predict_proba(X)[0][1])
            pred = "attack" if proba >= THRESH else "normal"
        else:
            pred_i = int(model.predict(X)[0])
            pred = "attack" if pred_i == 1 else "normal"

        out = {
            "message_id": msg.message_id,
            "device_id": msg.device_id,
            "prediction": pred,
            "score": proba,
            "ts": msg.timestamp.isoformat(),
        }
        mqtt.publish(IDA_OUT, out)
        mqtt.publish(METRICS_EVENTS, {"type": "ida_prediction", **out})

    mqtt.add_handler(TMA_TO_IDA, handle)
    logger.info("IDA started threshold=%s", THRESH)
    mqtt.start()


if __name__ == "__main__":
    main()
