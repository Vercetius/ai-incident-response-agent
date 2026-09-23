SEVERITY_RISK = {
    "low": 10,
    "medium": 30,
    "high": 60,
    "critical": 85,
}


RISKY_ACTION_KEYWORDS = {
    "restart": 10,
    "rollback": 20,
    "fail over": 20,
    "failover": 20,
    "rotate": 15,
    "increase": 10,
    "scale": 10,
    "disable": 25,
    "delete": 40,
    "drop": 50,
}


def calculate_confidence(
    triage_result,
    root_cause_result,
    retrieval_context,
):
    severity = triage_result[
        "severity"
    ]

    root_confidence = float(
        root_cause_result.get(
            "confidence",
            0.0,
        )
    )

    history = retrieval_context[
        "historical_incidents"
    ]

    runbooks = retrieval_context[
        "runbooks"
    ]

    history_score = (
        history[0]["score"]
        if history
        else 0.0
    )

    runbook_score = (
        runbooks[0]["score"]
        if runbooks
        else 0.0
    )

    score = (
        root_confidence * 0.5
        + history_score * 0.3
        + runbook_score * 0.2
    )

    if severity == "critical":
        score = min(
            score,
            0.95,
        )

    return round(
        max(
            0.0,
            min(score, 1.0),
        ),
        3,
    )


def action_risk_score(
    action_plan,
):
    score = 0
    findings = []

    actions = []

    for key in (
        "immediate_actions",
        "investigation_actions",
        "recovery_actions",
        "verification_actions",
    ):
        actions.extend(
            action_plan.get(
                key,
                []
            )
        )

    for action in actions:
        text = action.lower()

        for keyword, points in (
            RISKY_ACTION_KEYWORDS.items()
        ):
            if keyword in text:
                score += points

                findings.append(
                    {
                        "keyword": keyword,
                        "points": points,
                        "action": action,
                    }
                )

    return {
        "score": min(
            score,
            100,
        ),
        "findings": findings,
    }


def assess_operational_risk(
    triage_result,
    action_plan,
):
    severity = triage_result[
        "severity"
    ]

    base = SEVERITY_RISK.get(
        severity,
        20,
    )

    action_risk = action_risk_score(
        action_plan
    )

    score = min(
        base + action_risk["score"],
        100,
    )

    if score >= 75:
        level = "high"

    elif score >= 40:
        level = "medium"

    else:
        level = "low"

    return {
        "risk_score": score,
        "risk_level": level,
        "action_risk": action_risk,
    }
