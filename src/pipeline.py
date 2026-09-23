from src.action_planner import (
    generate_action_plan,
)
from src.anomaly_detection import (
    detect_anomalies,
)
from src.retrieval import (
    IncidentRetriever,
)
from src.risk import (
    assess_operational_risk,
    calculate_confidence,
)
from src.root_cause import (
    analyze_root_cause,
)
from src.triage import (
    triage_incident,
)


class IncidentResponsePipeline:
    def __init__(self):
        self.retriever = (
            IncidentRetriever()
        )

    def analyze(
        self,
        incident,
    ):
        triage = triage_incident(
            incident
        )

        anomalies = detect_anomalies(
            incident
        )

        retrieval = (
            self.retriever
            .retrieve_context(
                incident
            )
        )

        root_cause = (
            analyze_root_cause(
                incident,
                triage,
                anomalies,
                retrieval,
            )
        )

        action_plan = (
            generate_action_plan(
                incident,
                triage,
                anomalies,
                retrieval,
                root_cause,
            )
        )

        confidence = (
            calculate_confidence(
                triage,
                root_cause,
                retrieval,
            )
        )

        operational_risk = (
            assess_operational_risk(
                triage,
                action_plan,
            )
        )

        escalation_reasons = []

        if confidence < 0.60:
            escalation_reasons.append(
                "Low analysis confidence"
            )

        if (
            triage["severity"]
            == "critical"
        ):
            escalation_reasons.append(
                "Critical severity incident"
            )

        if (
            operational_risk[
                "risk_level"
            ]
            == "high"
        ):
            escalation_reasons.append(
                "High operational risk"
            )

        if (
            root_cause["method"]
            == "historical_fallback"
        ):
            escalation_reasons.append(
                "LLM unavailable; fallback analysis used"
            )

        escalation_required = bool(
            escalation_reasons
        )

        human_approval_required = (
            operational_risk[
                "risk_level"
            ]
            in {
                "medium",
                "high",
            }
            or triage[
                "severity"
            ]
            in {
                "high",
                "critical",
            }
        )

        return {
            "incident_id": (
                incident.incident_id
            ),
            "triage": triage,
            "anomalies": anomalies,
            "retrieval": retrieval,
            "root_cause": root_cause,
            "action_plan": action_plan,
            "confidence": confidence,
            "operational_risk": (
                operational_risk
            ),
            "escalation_required": (
                escalation_required
            ),
            "escalation_reasons": (
                escalation_reasons
            ),
            "human_approval_required": (
                human_approval_required
            ),
        }
