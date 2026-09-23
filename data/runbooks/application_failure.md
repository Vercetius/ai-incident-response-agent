# Application Failure After Deployment

## Symptoms

- HTTP 500 errors
- Unhandled exceptions
- Failure rate increasing after deployment
- Dependency connection failures
- Service instability after configuration changes

## Investigation

1. Compare incident start time with deployment events.
2. Inspect application logs.
3. Review configuration changes.
4. Check dependent services such as caches and databases.

## Mitigation

- Roll back the most recent deployment when strongly correlated.
- Restore the previous stable configuration.
- Validate service health after rollback.
