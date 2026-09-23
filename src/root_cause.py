import json

from openai import OpenAI

from src.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


def build_root_cause_evidence(
    incident,
    triage_result,
    anomaly_result,
    retrieval_context,
):
    historical = retrieval_context[
        "historical_incidents"
    ]

    runbooks = retrieval_context[
        "runbooks"
    ]

    evidence = {
        "incident_id": incident.incident_id,
        "title": incident.title,
        "service": incident.service,
        "severity": triage_result[
            "severity"
        ],
        "triage_reasons": triage_result[
            "reasons"
        ],
        "anomalies": anomaly_result[
            "anomalies"
        ],
        "logs": [
            {
                "service": log.service,
                "level": log.level,
                "message": log.message,
                "metric": log.metric,
                "value": log.value,
            }
            for log in incident.logs
        ],
        "historical_incidents": [
            {
                "incident_id": item[
                    "incident_id"
                ],
                "title": item["title"],
                "root_cause": item[
                    "root_cause"
                ],
                "resolution": item[
                    "resolution"
                ],
                "similarity": item[
                    "score"
                ],
            }
            for item in historical[:3]
        ],
        "runbooks": [
            {
                "name": item["name"],
                "similarity": item[
                    "score"
                ],
            }
            for item in runbooks[:3]
        ],
    }

    return evidence


def heuristic_root_cause(
    retrieval_context,
):
    historical = retrieval_context[
        "historical_incidents"
    ]

    if not historical:
        return {
            "hypothesis": "insufficient evidence",
            "confidence": 0.0,
            "source": "none",
        }

    best = historical[0]

    confidence = min(
        max(
            best["score"],
            0.0,
        ),
        1.0,
    )

    return {
        "hypothesis": best[
            "root_cause"
        ],
        "confidence": round(
            confidence,
            3,
        ),
        "source": best[
            "incident_id"
        ],
    }


def analyze_root_cause(
    incident,
    triage_result,
    anomaly_result,
    retrieval_context,
):
    evidence = build_root_cause_evidence(
        incident,
        triage_result,
        anomaly_result,
        retrieval_context,
    )

    fallback = heuristic_root_cause(
        retrieval_context
    )

    if not OPENAI_API_KEY:
        return {
            **fallback,
            "reasoning": (
                "LLM analysis unavailable. "
                "Using the most similar "
                "historical incident."
            ),
            "evidence": evidence,
            "method": "historical_fallback",
        }

    try:
        client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        prompt = f"""
You are an incident-response root-cause analyst.

Analyze the incident using ONLY the evidence supplied below.

Do not invent infrastructure, events, metrics, deployments,
or causal relationships that are not supported by the evidence.

Return valid JSON with exactly these fields:

{{
  "hypothesis": "short root cause hypothesis",
  "confidence": 0.0,
  "reasoning": "concise explanation grounded in the evidence"
}}

Confidence must be between 0 and 1.

EVIDENCE:
{json.dumps(evidence, indent=2)}
"""

        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
        )

        raw = response.output_text.strip()

        if raw.startswith("```"):
            raw = raw.strip("`")

            if raw.startswith("json"):
                raw = raw[4:].strip()

        parsed = json.loads(raw)

        confidence = float(
            parsed.get(
                "confidence",
                fallback["confidence"],
            )
        )

        confidence = min(
            max(confidence, 0.0),
            1.0,
        )

        return {
            "hypothesis": parsed.get(
                "hypothesis",
                fallback["hypothesis"],
            ),
            "confidence": round(
                confidence,
                3,
            ),
            "reasoning": parsed.get(
                "reasoning",
                "",
            ),
            "evidence": evidence,
            "method": "llm_grounded",
        }

    except Exception as error:
        return {
            **fallback,
            "reasoning": (
                "LLM analysis unavailable. "
                "Historical retrieval fallback used. "
                f"Reason: {type(error).__name__}."
            ),
            "evidence": evidence,
            "method": "historical_fallback",
        }
