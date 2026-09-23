from src.log_ingestion import (
    load_and_normalize,
)


def test_incident_loading():
    incidents = load_and_normalize(
        "data/generated/incidents.json"
    )

    assert len(incidents) == 8


def test_checkout_incident_normalization():
    incidents = load_and_normalize(
        "data/generated/incidents.json"
    )

    incident = incidents[0]

    assert (
        incident.incident_id
        == "INC-001"
    )

    assert incident.error_count == 2

    assert incident.warning_count == 2

    assert (
        "checkout-api"
        in incident.services_affected
    )

    assert (
        "postgres-primary"
        in incident.services_affected
    )

    assert (
        incident.metrics[
            "connection_pool_percent"
        ][0]
        == 97
    )
