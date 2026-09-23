from src.action_planner import (
    historical_action_fallback,
)
from src.log_ingestion import (
    load_and_normalize,
)
from src.pipeline import (
    IncidentResponsePipeline,
)
from src.risk import (
    action_risk_score,
)


def test_risky_action_detection():
    plan = {
        "immediate_actions": [
            "Restart affected workers"
        ],
        "investigation_actions": [],
        "recovery_actions": [
            "Rollback deployment"
        ],
        "verification_actions": [],
    }

    result = action_risk_score(
        plan
    )

    assert result["score"] >= 30


def test_critical_incident_requires_approval():
    incidents = load_and_normalize(
        "data/generated/incidents.json"
    )

    pipeline = (
        IncidentResponsePipeline()
    )

    result = pipeline.analyze(
        incidents[1]
    )

    assert (
        result["triage"]["severity"]
        == "critical"
    )

    assert (
        result[
            "human_approval_required"
        ]
        is True
    )

    assert (
        result[
            "escalation_required"
        ]
        is True
    )


def test_high_incident_requires_approval():
    incidents = load_and_normalize(
        "data/generated/incidents.json"
    )

    pipeline = (
        IncidentResponsePipeline()
    )

    result = pipeline.analyze(
        incidents[0]
    )

    assert (
        result["triage"]["severity"]
        == "high"
    )

    assert (
        result[
            "human_approval_required"
        ]
        is True
    )


def test_fallback_plan_has_actions():
    incidents = load_and_normalize(
        "data/generated/incidents.json"
    )

    pipeline = (
        IncidentResponsePipeline()
    )

    context = (
        pipeline.retriever
        .retrieve_context(
            incidents[0]
        )
    )

    plan = (
        historical_action_fallback(
            context
        )
    )

    assert len(
        plan["immediate_actions"]
    ) >= 1


def test_low_severity_is_not_automatically_high_risk():
    incidents = load_and_normalize(
        "data/generated/incidents.json"
    )

    pipeline = (
        IncidentResponsePipeline()
    )

    result = pipeline.analyze(
        incidents[4]
    )

    assert (
        result["triage"]["severity"]
        == "low"
    )

    assert (
        result[
            "operational_risk"
        ]["risk_level"]
        != "high"
    )
