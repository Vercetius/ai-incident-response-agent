import pytest

from src.log_ingestion import load_and_normalize
from src.retrieval import IncidentRetriever


@pytest.fixture(scope="module")
def retriever():
    return IncidentRetriever()


@pytest.fixture(scope="module")
def incidents():
    return load_and_normalize(
        "data/generated/incidents.json"
    )


def test_database_runbook_retrieval(
    retriever,
    incidents,
):
    results = retriever.retrieve_runbooks(
        incidents[0],
        top_k=3,
    )

    names = {
        item["name"]
        for item in results
    }

    assert "database_connection_pool" in names


def test_auth_runbook_retrieval(
    retriever,
    incidents,
):
    results = retriever.retrieve_runbooks(
        incidents[1],
        top_k=3,
    )

    names = {
        item["name"]
        for item in results
    }

    assert "auth_certificate" in names


def test_database_history_retrieval(
    retriever,
    incidents,
):
    results = retriever.retrieve_historical(
        incidents[0],
        top_k=3,
    )

    ids = {
        item["incident_id"]
        for item in results
    }

    assert "HIST-001" in ids


def test_auth_history_retrieval(
    retriever,
    incidents,
):
    results = retriever.retrieve_historical(
        incidents[1],
        top_k=3,
    )

    ids = {
        item["incident_id"]
        for item in results
    }

    assert "HIST-002" in ids
