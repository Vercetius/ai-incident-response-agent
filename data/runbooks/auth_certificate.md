# Authentication Certificate Failure

## Symptoms

- JWT validation failures
- Authentication requests returning 401
- Signing certificate expiration errors
- Sudden widespread login failures

## Investigation

1. Check the active signing certificate.
2. Verify certificate expiration time.
3. Validate certificate distribution across authentication workers.
4. Check whether recent certificate rotation failed.

## Mitigation

- Rotate the expired signing certificate.
- Restart authentication workers if necessary.
- Verify new tokens are signed and validated correctly.

## Escalation

Treat widespread authentication failure as a critical incident.
