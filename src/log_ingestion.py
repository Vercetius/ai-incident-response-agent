import json
from pathlib import Path

from src.models import (
    Incident,
    NormalizedIncident,
)


def load_incidents(path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Incident file not found: {path}"
        )

    raw_data = json.loads(
        path.read_text()
    )

    return [
        Incident.model_validate(item)
        for item in raw_data
    ]


def normalize_incident(
    incident: Incident,
) -> NormalizedIncident:

    error_count = sum(
        1
        for log in incident.logs
        if log.level.upper() == "ERROR"
    )

    warning_count = sum(
        1
        for log in incident.logs
        if log.level.upper() == "WARNING"
    )

    info_count = sum(
        1
        for log in incident.logs
        if log.level.upper() == "INFO"
    )

    services_affected = sorted(
        {
            log.service
            for log in incident.logs
        }
    )

    metrics = {}

    for log in incident.logs:
        if (
            log.metric is not None
            and log.value is not None
        ):
            metrics.setdefault(
                log.metric,
                [],
            ).append(
                log.value
            )

    log_messages = [
        log.message
        for log in incident.logs
    ]

    return NormalizedIncident(
        incident_id=incident.incident_id,
        title=incident.title,
        service=incident.service,
        started_at=incident.started_at,
        logs=incident.logs,
        error_count=error_count,
        warning_count=warning_count,
        info_count=info_count,
        services_affected=services_affected,
        metrics=metrics,
        log_messages=log_messages,
    )


def load_and_normalize(path):
    incidents = load_incidents(
        path
    )

    return [
        normalize_incident(incident)
        for incident in incidents
    ]
