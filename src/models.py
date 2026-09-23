from typing import List, Optional

from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    timestamp: str
    service: str
    level: str
    message: str
    metric: Optional[str] = None
    value: Optional[float] = None


class Incident(BaseModel):
    incident_id: str
    title: str
    service: str
    started_at: str
    logs: List[LogEntry]

    expected_severity: Optional[str] = None
    expected_root_cause: Optional[str] = None
    expected_action: Optional[str] = None


class NormalizedIncident(BaseModel):
    incident_id: str
    title: str
    service: str
    started_at: str
    logs: List[LogEntry]

    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0

    services_affected: List[str] = Field(
        default_factory=list
    )

    metrics: dict = Field(
        default_factory=dict
    )

    log_messages: List[str] = Field(
        default_factory=list
    )
