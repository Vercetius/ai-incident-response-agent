from src.anomaly_detection import (
    detect_anomalies,
)
from src.log_ingestion import (
    load_incidents,
    load_and_normalize,
    normalize_incident,
)
from src.triage import (
    triage_incident,
)


def test_all_expected_severities():
    incidents = load_incidents(
        "data/generated/incidents.json"
    )

    for raw in incidents:
        normalized = normalize_incident(
            raw
        )

        result = triage_incident(
            normalized
        )

        assert (
            result["severity"]
            == raw.expected_severity
        )


def test_auth_incident_is_critical():
    incidents = load_and_normalize(
        "data/generated/incidents.json"
    )

    incident = incidents[1]

    result = triage_incident(
        incident
    )

    assert (
        result["severity"]
        == "critical"
    )

    assert result["priority"] == "P1"


def test_disk_warning_is_low():
    incidents = load_and_normalize(
        "data/generated/incidents.json"
    )

    incident = incidents[4]

    result = triage_incident(
        incident
    )

    assert result["severity"] == "low"

    assert result["priority"] == "P4"


def test_auth_anomalies_detected():
    incidents = load_and_normalize(
        "data/generated/incidents.json"
    )

    incident = incidents[1]

    result = detect_anomalies(
        incident
    )

    messages = {
        anomaly["message"]
        for anomaly in result[
            "anomalies"
        ]
    }

    assert (
        "Authentication failure spike"
        in messages
    )

    assert (
        "Expired certificate detected"
        in messages
    )


def test_checkout_database_anomalies():
    incidents = load_and_normalize(
        "data/generated/incidents.json"
    )

    incident = incidents[0]

    result = detect_anomalies(
        incident
    )

    messages = {
        anomaly["message"]
        for anomaly in result[
            "anomalies"
        ]
    }

    assert (
        "Database connection pool saturation"
        in messages
    )

    assert (
        "Database connectivity failure"
        in messages
    )
