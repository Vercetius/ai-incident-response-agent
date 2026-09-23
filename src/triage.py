from src.models import NormalizedIncident


SEVERITY_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


def get_metric_max(
    incident: NormalizedIncident,
    metric_name: str,
):
    values = incident.metrics.get(
        metric_name,
        [],
    )

    if not values:
        return None

    return max(values)


def classify_severity(
    incident: NormalizedIncident,
):
    reasons = []

    http_401_rate = get_metric_max(
        incident,
        "http_401_rate",
    )

    failure_rate = get_metric_max(
        incident,
        "failure_rate_percent",
    )

    connection_pool = get_metric_max(
        incident,
        "connection_pool_percent",
    )

    provider_latency = get_metric_max(
        incident,
        "provider_latency_ms",
    )

    http_500_rate = get_metric_max(
        incident,
        "http_500_rate",
    )

    queue_depth = get_metric_max(
        incident,
        "queue_depth",
    )

    memory_percent = get_metric_max(
        incident,
        "memory_percent",
    )

    if (
        http_401_rate is not None
        and http_401_rate >= 70
    ):
        reasons.append(
            f"Authentication failure rate reached "
            f"{http_401_rate:.0f}%."
        )

        severity = "critical"

    elif (
        failure_rate is not None
        and failure_rate >= 70
    ):
        reasons.append(
            f"Service failure rate reached "
            f"{failure_rate:.0f}%."
        )

        severity = "critical"

    elif (
        "deployment"
        in incident.title.lower()
        and incident.error_count >= 3
    ):
        reasons.append(
            "Multiple errors appeared immediately "
            "after a deployment."
        )

        severity = "critical"

    elif (
        connection_pool is not None
        and connection_pool >= 95
    ):
        reasons.append(
            f"Database connection pool reached "
            f"{connection_pool:.0f}% utilization."
        )

        severity = "high"

    elif (
        provider_latency is not None
        and provider_latency >= 5000
    ):
        reasons.append(
            f"External provider latency reached "
            f"{provider_latency:.0f} ms."
        )

        severity = "high"

    elif (
        http_500_rate is not None
        and http_500_rate >= 30
    ):
        reasons.append(
            f"HTTP 500 rate reached "
            f"{http_500_rate:.0f}%."
        )

        severity = "high"

    elif (
        incident.error_count >= 2
        and incident.warning_count >= 1
    ):
        reasons.append(
            "Multiple errors and warnings "
            "were detected."
        )

        severity = "high"

    elif (
        queue_depth is not None
        and queue_depth >= 10000
    ):
        reasons.append(
            f"Queue depth reached "
            f"{queue_depth:.0f} messages."
        )

        severity = "medium"

    elif (
        memory_percent is not None
        and memory_percent >= 85
    ):
        reasons.append(
            f"Memory utilization reached "
            f"{memory_percent:.0f}%."
        )

        severity = "medium"

    elif incident.error_count >= 1:
        reasons.append(
            "At least one service error "
            "was detected."
        )

        severity = "medium"

    else:
        reasons.append(
            "No severe service failure signal "
            "was detected."
        )

        severity = "low"

    if incident.error_count:
        reasons.append(
            f"{incident.error_count} ERROR "
            f"log(s) detected."
        )

    if len(
        incident.services_affected
    ) > 1:
        reasons.append(
            f"{len(incident.services_affected)} "
            f"services are involved."
        )

    return {
        "severity": severity,
        "reasons": reasons,
    }


def triage_incident(
    incident: NormalizedIncident,
):
    result = classify_severity(
        incident
    )

    severity = result["severity"]

    if severity == "critical":
        priority = "P1"
        response = "Immediate response required"

    elif severity == "high":
        priority = "P2"
        response = "Urgent investigation required"

    elif severity == "medium":
        priority = "P3"
        response = "Investigation required"

    else:
        priority = "P4"
        response = "Monitor and review"

    return {
        "incident_id": incident.incident_id,
        "severity": severity,
        "priority": priority,
        "response": response,
        "reasons": result["reasons"],
    }
