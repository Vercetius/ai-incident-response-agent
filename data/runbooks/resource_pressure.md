# Resource Pressure

## Symptoms

- High memory usage
- Out-of-memory worker termination
- High disk utilization
- Garbage collection frequency increasing

## Investigation

1. Inspect resource utilization over time.
2. Identify processes consuming abnormal resources.
3. Check recent deployments.
4. Look for memory leaks or excessive log growth.

## Mitigation

- Restart affected workers when safe.
- Scale capacity temporarily.
- Archive unnecessary logs.
- Investigate memory allocation or storage growth.
