# Root Cause
Database connection pool exhausted due to unclosed socket connections in legacy auth middleware.

# Remediation
1. Increase max_connections pool size.
2. Apply connection recycling timeout.
