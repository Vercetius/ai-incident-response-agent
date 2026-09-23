import json
from pathlib import Path


OUTPUT = Path(
    "data/generated/incidents.json"
)


INCIDENTS = [
    {
        "incident_id": "INC-001",
        "title": "Checkout API latency spike",
        "service": "checkout-api",
        "started_at": "2026-09-20T10:02:00Z",
        "expected_severity": "high",
        "expected_root_cause": "database connection pool exhaustion",
        "expected_action": "increase database connection pool and investigate leaked connections",
        "logs": [
            {
                "timestamp": "2026-09-20T10:02:01Z",
                "service": "checkout-api",
                "level": "WARNING",
                "message": "Request latency exceeded 2500ms",
                "metric": "latency_ms",
                "value": 2680
            },
            {
                "timestamp": "2026-09-20T10:02:05Z",
                "service": "checkout-api",
                "level": "ERROR",
                "message": "Database connection timeout"
            },
            {
                "timestamp": "2026-09-20T10:02:06Z",
                "service": "postgres-primary",
                "level": "WARNING",
                "message": "Connection pool usage above 95%",
                "metric": "connection_pool_percent",
                "value": 97
            },
            {
                "timestamp": "2026-09-20T10:02:10Z",
                "service": "checkout-api",
                "level": "ERROR",
                "message": "Failed to acquire database connection"
            }
        ]
    },
    {
        "incident_id": "INC-002",
        "title": "Authentication failures",
        "service": "auth-service",
        "started_at": "2026-09-20T13:15:00Z",
        "expected_severity": "critical",
        "expected_root_cause": "expired signing certificate",
        "expected_action": "rotate signing certificate and restart authentication workers",
        "logs": [
            {
                "timestamp": "2026-09-20T13:15:01Z",
                "service": "auth-service",
                "level": "ERROR",
                "message": "JWT validation failed"
            },
            {
                "timestamp": "2026-09-20T13:15:03Z",
                "service": "auth-service",
                "level": "ERROR",
                "message": "Signing certificate expired"
            },
            {
                "timestamp": "2026-09-20T13:15:04Z",
                "service": "api-gateway",
                "level": "ERROR",
                "message": "401 response rate increased sharply",
                "metric": "http_401_rate",
                "value": 82
            },
            {
                "timestamp": "2026-09-20T13:15:08Z",
                "service": "auth-service",
                "level": "ERROR",
                "message": "Unable to verify authentication token"
            }
        ]
    },
    {
        "incident_id": "INC-003",
        "title": "Worker queue backlog",
        "service": "email-worker",
        "started_at": "2026-09-21T08:45:00Z",
        "expected_severity": "medium",
        "expected_root_cause": "worker capacity insufficient for traffic spike",
        "expected_action": "scale email workers and monitor queue depth",
        "logs": [
            {
                "timestamp": "2026-09-21T08:45:01Z",
                "service": "email-worker",
                "level": "WARNING",
                "message": "Queue depth exceeded threshold",
                "metric": "queue_depth",
                "value": 12500
            },
            {
                "timestamp": "2026-09-21T08:45:05Z",
                "service": "email-worker",
                "level": "WARNING",
                "message": "Message processing delay above 120 seconds"
            },
            {
                "timestamp": "2026-09-21T08:45:09Z",
                "service": "email-worker",
                "level": "INFO",
                "message": "All workers currently busy"
            }
        ]
    },
    {
        "incident_id": "INC-004",
        "title": "Payment provider intermittent timeout",
        "service": "payment-service",
        "started_at": "2026-09-21T17:30:00Z",
        "expected_severity": "high",
        "expected_root_cause": "external payment provider degradation",
        "expected_action": "enable retry policy and fail over to secondary payment provider",
        "logs": [
            {
                "timestamp": "2026-09-21T17:30:01Z",
                "service": "payment-service",
                "level": "ERROR",
                "message": "Payment provider request timed out"
            },
            {
                "timestamp": "2026-09-21T17:30:04Z",
                "service": "payment-service",
                "level": "ERROR",
                "message": "External API latency exceeded 6000ms",
                "metric": "provider_latency_ms",
                "value": 6420
            },
            {
                "timestamp": "2026-09-21T17:30:10Z",
                "service": "payment-service",
                "level": "WARNING",
                "message": "Payment retry rate increased",
                "metric": "retry_rate_percent",
                "value": 41
            }
        ]
    },
    {
        "incident_id": "INC-005",
        "title": "Analytics database disk warning",
        "service": "analytics-db",
        "started_at": "2026-09-22T06:10:00Z",
        "expected_severity": "low",
        "expected_root_cause": "log retention growth",
        "expected_action": "archive old logs and review retention policy",
        "logs": [
            {
                "timestamp": "2026-09-22T06:10:01Z",
                "service": "analytics-db",
                "level": "WARNING",
                "message": "Disk usage reached 78%",
                "metric": "disk_usage_percent",
                "value": 78
            },
            {
                "timestamp": "2026-09-22T06:10:10Z",
                "service": "analytics-db",
                "level": "INFO",
                "message": "Database queries operating normally"
            }
        ]
    },
    {
        "incident_id": "INC-006",
        "title": "Recommendation service memory pressure",
        "service": "recommendation-api",
        "started_at": "2026-09-22T11:20:00Z",
        "expected_severity": "medium",
        "expected_root_cause": "memory leak in recommendation worker",
        "expected_action": "restart affected worker and inspect memory allocation growth",
        "logs": [
            {
                "timestamp": "2026-09-22T11:20:01Z",
                "service": "recommendation-api",
                "level": "WARNING",
                "message": "Memory usage exceeded 85%",
                "metric": "memory_percent",
                "value": 88
            },
            {
                "timestamp": "2026-09-22T11:20:05Z",
                "service": "recommendation-api",
                "level": "WARNING",
                "message": "Garbage collection frequency increased"
            },
            {
                "timestamp": "2026-09-22T11:20:09Z",
                "service": "recommendation-api",
                "level": "ERROR",
                "message": "Worker terminated due to out-of-memory condition"
            }
        ]
    },
    {
        "incident_id": "INC-007",
        "title": "Product API elevated 500 errors",
        "service": "product-api",
        "started_at": "2026-09-22T15:40:00Z",
        "expected_severity": "high",
        "expected_root_cause": "invalid cache configuration",
        "expected_action": "rollback cache configuration and restore previous deployment settings",
        "logs": [
            {
                "timestamp": "2026-09-22T15:40:01Z",
                "service": "product-api",
                "level": "ERROR",
                "message": "Redis connection refused"
            },
            {
                "timestamp": "2026-09-22T15:40:02Z",
                "service": "api-gateway",
                "level": "WARNING",
                "message": "HTTP 500 rate exceeded threshold",
                "metric": "http_500_rate",
                "value": 37
            },
            {
                "timestamp": "2026-09-22T15:40:04Z",
                "service": "product-api",
                "level": "ERROR",
                "message": "Cache backend unavailable"
            }
        ]
    },
    {
        "incident_id": "INC-008",
        "title": "Order service failures after deployment",
        "service": "order-service",
        "started_at": "2026-09-22T19:05:00Z",
        "expected_severity": "critical",
        "expected_root_cause": "faulty application deployment",
        "expected_action": "rollback deployment to previous stable version",
        "logs": [
            {
                "timestamp": "2026-09-22T19:05:01Z",
                "service": "order-service",
                "level": "INFO",
                "message": "Deployment version 4.8.2 completed"
            },
            {
                "timestamp": "2026-09-22T19:05:12Z",
                "service": "order-service",
                "level": "ERROR",
                "message": "Unhandled exception in order creation"
            },
            {
                "timestamp": "2026-09-22T19:05:14Z",
                "service": "order-service",
                "level": "ERROR",
                "message": "Order creation failed"
            },
            {
                "timestamp": "2026-09-22T19:05:16Z",
                "service": "api-gateway",
                "level": "ERROR",
                "message": "Order endpoint failure rate above 70%",
                "metric": "failure_rate_percent",
                "value": 74
            }
        ]
    }
]


def main():
    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            INCIDENTS,
            indent=2,
        )
    )

    print(
        f"Generated {len(INCIDENTS)} incidents."
    )

    print(
        f"Saved to: {OUTPUT}"
    )


if __name__ == "__main__":
    main()
