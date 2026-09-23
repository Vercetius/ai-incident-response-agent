from src.action_planner import historical_action_fallback
from src.log_ingestion import load_and_normalize
from src.retrieval import IncidentRetriever
from src.root_cause import heuristic_root_cause


def test_database_root_cause():
    incidents = load_and_normalize(
        "data/generated/incidents.json"
    )

    retriever = IncidentRetriever()

    context = retriever.retrieve_context(
        incidents[0]
    )

    result = heuristic_root_cause(
        context
    )

    assert (
        "connection pool"
        in result["hypothesis"].lower()
    )

    assert result["confidence"] > 0.5


def test_auth_root_cause():
    incidents = load_and_normalize(
        "data/generated/incidents.json"
    )

    retriever = IncidentRetriever()

    context = retriever.retrieve_context(
        incidents[1]
    )

    result = heuristic_root_cause(
        context
    )

    assert (
        "certificate"
        in result["hypothesis"].lower()
    )


def test_action_fallback():
    incidents = load_and_normalize(
        "data/generated/incidents.json"
    )

    retriever = IncidentRetriever()

    context = retriever.retrieve_context(
        incidents[1]
    )

    result = historical_action_fallback(
        context
    )

    assert len(
        result["immediate_actions"]
    ) >= 1

    assert len(
        result["verification_actions"]
    ) >= 1
