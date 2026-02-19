from datetime import datetime
from typing import Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TrafficFeatures(BaseModel):
    duration: float
    protocol: str
    service: str
    flag: str
    src_bytes: int
    dst_bytes: int
    wrong_fragment: int
    urgent: int
    count: int
    srv_count: int


class DeviceMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    device_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    src_ip: str
    dst_ip: str
    features: TrafficFeatures


class AAAEvent(BaseModel):
    message_id: str
    device_id: str
    status: Literal["authorized", "blocked"]
    reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: DeviceMessage


class IDAEvent(BaseModel):
    message_id: str
    device_id: str
    prediction: Literal["normal", "attack"]
    score: Optional[float] = None
    ts: datetime = Field(default_factory=datetime.utcnow)


class VMAEvent(BaseModel):
    message_id: str
    device_id: str
    risk_score: int
    factors: list[str]
    ts: datetime = Field(default_factory=datetime.utcnow)
