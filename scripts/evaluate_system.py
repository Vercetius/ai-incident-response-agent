import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import time

from src.anomaly_detection import detect_anomalies
from src.log_ingestion import (
    load_incidents,
    normalize_incident,
)
from src.retrieval import IncidentRetriever
from src.root_cause import heuristic_root_cause
from src.triage import triage_incident


EXPECTED_RUNBOOKS = {
    "INC-001": "database_connection_pool",
    "INC-002": "auth_certificate",
    "INC-003": "queue_backlog",
    "INC-004": "external_provider",
    "INC-005": "resource_pressure",
    "INC-006": "resource_pressure",
    "INC-007": "application_failure",
    "INC-008": "application_failure",
}


EXPECTED_HISTORY = {
    "INC-001": "HIST-001",
    "INC-002": "HIST-002",
    "INC-003": "HIST-003",
    "INC-004": "HIST-004",
    "INC-006": "HIST-005",
    "INC-007": "HIST-006",
    "INC-008": "HIST-007",
}


def main():
    raw_incidents = load_incidents(
        "data/generated/incidents.json"
    )

    retriever = IncidentRetriever()

    severity_correct = 0
    runbook_correct = 0
    history_correct = 0
    history_total = 0
    root_cause_supported = 0
    anomaly_incidents = 0

    start = time.perf_counter()

    for raw in raw_incidents:
        incident = normalize_incident(
            raw
        )

        triage = triage_incident(
            incident
        )

        if (
            triage["severity"]
            == raw.expected_severity
        ):
            severity_correct += 1

        anomalies = detect_anomalies(
            incident
        )

        if anomalies[
            "anomaly_count"
        ] > 0:
            anomaly_incidents += 1

        runbooks = (
            retriever.retrieve_runbooks(
                incident,
                top_k=1,
            )
        )

        predicted_runbook = (
            runbooks[0]["name"]
        )

        if (
            predicted_runbook
            == EXPECTED_RUNBOOKS[
                raw.incident_id
            ]
        ):
            runbook_correct += 1

        history = (
            retriever.retrieve_historical(
                incident,
                top_k=1,
            )
        )

        if (
            raw.incident_id
            in EXPECTED_HISTORY
        ):
            history_total += 1

            if (
                history[0]["incident_id"]
                == EXPECTED_HISTORY[
                    raw.incident_id
                ]
            ):
                history_correct += 1

        context = {
            "runbooks": runbooks,
            "historical_incidents": (
                history
            ),
        }

        root = heuristic_root_cause(
            context
        )

        if (
            root["hypothesis"]
            and root["confidence"] > 0
        ):
            root_cause_supported += 1

    elapsed = (
        time.perf_counter()
        - start
    )

    total = len(
        raw_incidents
    )

    print()
    print(
        "AI INCIDENT RESPONSE AGENT EVALUATION"
    )

    print("=" * 60)

    print(
        "Severity accuracy:",
        f"{severity_correct}/{total}",
        f"({severity_correct / total:.1%})",
    )

    print(
        "Runbook Top-1:",
        f"{runbook_correct}/{total}",
        f"({runbook_correct / total:.1%})",
    )

    print(
        "Historical Top-1:",
        f"{history_correct}/{history_total}",
        f"({history_correct / history_total:.1%})",
    )

    print(
        "Incidents with detected anomalies:",
        f"{anomaly_incidents}/{total}",
    )

    print(
        "Root causes with retrieved support:",
        f"{root_cause_supported}/{total}",
    )

    print(
        "Evaluation processing time:",
        f"{elapsed:.3f}s",
    )

    print("=" * 60)

    all_pass = (
        severity_correct == total
        and runbook_correct == total
        and history_correct == history_total
        and root_cause_supported == total
    )

    print(
        "SYSTEM EVALUATION:",
        "PASS"
        if all_pass
        else "REVIEW REQUIRED",
    )


if __name__ == "__main__":
    main()
