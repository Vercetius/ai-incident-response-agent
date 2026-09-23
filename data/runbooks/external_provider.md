# External Provider Degradation

## Symptoms

- External API timeouts
- Increased provider latency
- Retry rate increasing
- Requests failing outside the internal infrastructure

## Investigation

1. Check external provider status.
2. Measure provider latency and timeout rate.
3. Compare primary and secondary providers.
4. Inspect retry and circuit-breaker behavior.

## Mitigation

- Enable safe retries.
- Use circuit breakers.
- Fail over to a secondary provider where available.
- Reduce unnecessary provider traffic.
