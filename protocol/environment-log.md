# Environment log

This file records externally provisioned benchmark infrastructure without secrets.

## 2026-09-14 - Neon

- Organization: benchmark sponsor's existing Neon organization
- Project name: `dataagents-mcp-benchmark`
- Project ID: `solitary-credit-82809008`
- Branch: `production`
- Database: `neondb`
- PostgreSQL: 18
- Region: AWS Europe Central 1 (Frankfurt)
- Seed method: Neon SQL editor using deterministic set-based SQL
- Verified inserts: 120 accounts, 120 identity mappings, 42,000 product events
- Query execution time reported by Neon for bootstrap batch: 43 ms

Database credentials and provider-generated passwords are excluded from git.
