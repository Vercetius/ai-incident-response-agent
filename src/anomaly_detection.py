from src.models import NormalizedIncident


METRIC_RULES = {
    "latency_ms": {
        "threshold": 2000,
        "severity": "high",
        "label": "Elevated request latency",
    },
    "connection_pool_percent": {
        "threshold": 90,
        "severity": "high",
        "label": "Database connection pool saturation",
    },
    "http_401_rate": {
        "threshold": 20,
        "severity": "critical",
        "label": "Authentication failure spike",
    },
    "queue_depth": {
        "threshold": 5000,
        "severity": "medium",
        "label": "Queue backlog",
    },
    "provider_latency_ms": {
        "threshold": 3000,
        "severity": "high",
        "label": "External provider latency",
    },
    "retry_rate_percent": {
        "threshold": 20,
        "severity": "medium",
        "label": "Elevated retry rate",
    },
    "disk_usage_percent": {
        "threshold": 75,
        "severity": "low",
        "label": "Disk utilization warning",
    },
    "memory_percent": {
        "threshold": 80,
        "severity": "medium",
        "label": "Memory pressure",
    },
    "http_500_rate": {
        "threshold": 10,
        "severity": "high",
        "label": "HTTP 500 error spike",
    },
    "failure_rate_percent": {
        "threshold": 20,
        "severity": "critical",
        "label": "Service failure spike",
    },
}


LOG_PATTERNS = {
    "certificate expired": {
        "label": "Expired certificate detected",
        "severity": "critical",
    },
    "out-of-memory": {
        "label": "Out-of-memory event detected",
        "severity": "high",
    },
    "connection refused": {
        "label": "Dependency connection failure",
        "severity": "high",
    },
    "database connection timeout": {
        "label": "Database connectivity failure",
        "severity": "high",
    },
    "request timed out": {
        "label": "External request timeout",
        "severity": "high",
    },
    "unhandled exception": {
        "label": "Unhandled application exception",
        "severity": "high",
    },
}


def detect_metric_anomalies(
    incident: NormalizedIncident,
):
    anomalies = []

    for metric_name, values in (
        incident.metrics.items()
    ):
        rule = METRIC_RULES.get(
            metric_name
        )

        if rule is None:
            continue

        for value in values:
            if value >= rule["threshold"]:
                anomalies.append(
                    {
                        "type": "metric",
                        "metric": metric_name,
                        "value": value,
                        "threshold": rule[
                            "threshold"
                        ],
                        "severity": rule[
                            "severity"
                        ],
                        "message": rule[
                            "label"
                        ],
                    }
                )

    return anomalies


def detect_log_anomalies(
    incident: NormalizedIncident,
):
    anomalies = []

    for log in incident.logs:
        message = log.message.lower()

        for pattern, rule in (
            LOG_PATTERNS.items()
        ):
            if pattern in message:
                anomalies.append(
                    {
                        "type": "log_pattern",
                        "service": log.service,
                        "severity": rule[
                            "severity"
                        ],
                        "message": rule[
                            "label"
                        ],
                        "evidence": log.message,
                    }
                )

    return anomalies


def detect_anomalies(
    incident: NormalizedIncident,
):
    anomalies = []

    anomalies.extend(
        detect_metric_anomalies(
            incident
        )
    )

    anomalies.extend(
        detect_log_anomalies(
            incident
        )
    )

    return {
        "incident_id": incident.incident_id,
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
    }
