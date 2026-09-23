# Worker Queue Backlog

## Symptoms

- Queue depth increasing rapidly
- Processing delays
- Workers continuously busy
- Delayed asynchronous jobs

## Investigation

1. Check current queue depth.
2. Inspect worker concurrency.
3. Compare workload with normal traffic.
4. Look for slow or failing tasks.

## Mitigation

- Scale worker capacity.
- Reduce expensive background tasks.
- Retry failed jobs where appropriate.
- Monitor queue depth after scaling.
