# Database Connection Pool Saturation

## Symptoms

- Database connection timeouts
- Failed connection acquisition
- Connection pool utilization above 90%
- Increased application latency
- Requests waiting for database access

## Investigation

1. Check connection pool utilization.
2. Inspect active and idle database connections.
3. Look for leaked or long-running connections.
4. Review recent application deployments.
5. Inspect database latency and resource pressure.

## Mitigation

- Increase the connection pool temporarily if capacity allows.
- Restart affected application workers if connections are stuck.
- Investigate connection leaks.
- Reduce long-running database operations.

## Escalation

Escalate to the database or platform team if pool saturation persists after mitigation.
