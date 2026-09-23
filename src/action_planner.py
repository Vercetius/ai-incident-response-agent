import json

from openai import OpenAI

from src.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


def historical_action_fallback(
    retrieval_context,
):
    historical = retrieval_context[
        "historical_incidents"
    ]

    if not historical:
        return {
            "immediate_actions": [],
            "investigation_actions": [],
            "recovery_actions": [],
            "verification_actions": [],
            "method": "no_context",
        }

    best = historical[0]

    return {
        "immediate_actions": [
            best["resolution"]
        ],
        "investigation_actions": [
            (
                "Validate whether the current "
                "incident matches the retrieved "
                "historical failure pattern."
            )
        ],
        "recovery_actions": [
            best["resolution"]
        ],
        "verification_actions": [
            (
                "Verify service health and "
                "confirm affected metrics return "
                "to normal."
            )
        ],
        "method": "historical_fallback",
    }


def generate_action_plan(
    incident,
    triage_result,
    anomaly_result,
    retrieval_context,
    root_cause_result,
):
    fallback = historical_action_fallback(
        retrieval_context
    )

    if not OPENAI_API_KEY:
        return fallback

    runbooks = retrieval_context[
        "runbooks"
    ]

    historical = retrieval_context[
        "historical_incidents"
    ]

    context = {
        "incident_id": (
            incident.incident_id
        ),
        "title": incident.title,
        "service": incident.service,
        "severity": triage_result[
            "severity"
        ],
        "priority": triage_result[
            "priority"
        ],
        "root_cause": {
            "hypothesis": (
                root_cause_result[
                    "hypothesis"
                ]
            ),
            "confidence": (
                root_cause_result[
                    "confidence"
                ]
            ),
        },
        "anomalies": anomaly_result[
            "anomalies"
        ],
        "runbooks": [
            {
                "name": item["name"],
                "content": item[
                    "content"
                ],
            }
            for item in runbooks[:2]
        ],
        "historical_incidents": [
            {
                "incident_id": item[
                    "incident_id"
                ],
                "root_cause": item[
                    "root_cause"
                ],
                "resolution": item[
                    "resolution"
                ],
            }
            for item in historical[:2]
        ],
    }

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    prompt = f"""
You are an AI incident-response assistant.

Create a conservative operational action plan using ONLY
the supplied evidence.

Do not invent commands, infrastructure names, credentials,
or destructive actions.

Return valid JSON with exactly these fields:

{{
  "immediate_actions": ["action"],
  "investigation_actions": ["action"],
  "recovery_actions": ["action"],
  "verification_actions": ["action"]
}}

Rules:
- Immediate actions should reduce impact.
- Investigation actions should validate the hypothesis.
- Recovery actions should restore service.
- Verification actions should confirm recovery.
- Prefer reversible actions.
- Do not automatically execute anything.
- Human approval is required for operational changes.

CONTEXT:
{json.dumps(context, indent=2)}
"""

    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
        )
    except Exception:
        return fallback

    raw = response.output_text.strip()

    if raw.startswith("```"):
        raw = raw.strip("`")

        if raw.startswith("json"):
            raw = raw[4:].strip()

    try:
        parsed = json.loads(raw)

        return {
            "immediate_actions": parsed.get(
                "immediate_actions",
                [],
            ),
            "investigation_actions": parsed.get(
                "investigation_actions",
                [],
            ),
            "recovery_actions": parsed.get(
                "recovery_actions",
                [],
            ),
            "verification_actions": parsed.get(
                "verification_actions",
                [],
            ),
            "method": "llm_grounded",
        }

    except json.JSONDecodeError:
        return fallback
