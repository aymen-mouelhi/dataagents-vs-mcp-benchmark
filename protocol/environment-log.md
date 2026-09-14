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

## 2026-09-14 - Stripe

- Existing sandbox located: `Revydo sandbox`
- Dashboard account ID: `acct_1UBaBvDhuRdfwuUP`
- No live-mode operations are permitted by the seeder
- Test clocks excluded from the primary corpus because they cap simulations at
  three customers and omit generated invoices from ordinary unscoped lists
- Created a benchmark-only restricted test key with write access limited to
  Customers, Products, Prices, Subscriptions, and Invoices
- Seeded and verified through the authoritative list API: 3 products, 3 prices,
  120 customers, 117 subscriptions, and 240 paid invoices
- Stripe search indexing briefly lagged the authoritative list API after the
  seed; this was treated as readiness/freshness evidence rather than a missing row
- Restricted credentials and provider object mappings remain private and are
  excluded from git

## 2026-09-14 - Support source

- Provider: GitHub Issues
- Repository: `aymen-mouelhi/northstar-labs-support-fixture`
- Visibility: public
- Canonical open issues: 40
- Incident/control split: 30 bulk-export incident tickets, 10 configuration controls
- Canonical identifiers and source timestamps are embedded in every issue body
- Nineteen duplicate issues caused by an interrupted first seeding pass were
  closed immediately and are excluded by the frozen `state=open` source filter
- Claude Code uses GitHub's official `/mcp/readonly` endpoint with only the
  `repos,issues` toolsets and an existing GitHub CLI credential resolved in memory
- Claude Code MCP health check: connected

## 2026-09-14 - CRM

- HubSpot was attempted first but its existing account requires passkey/2FA
  interaction before a developer environment can be created
- Frozen fallback: Pipedrive trial with native MCP
- Native MCP endpoint: `https://mcp.pipedrive.ai/mcp`
- Trial signup submitted for the benchmark sponsor's work email
- Work-email signup was blocked by the provider's authentication flow
- Trial created with the benchmark sponsor's explicitly authorized Google identity
- Workspace: `Northstar Labs Benchmark`
- Company domain: `northstarlabsbenchmark`
- No sample data or marketing opt-in was enabled
- Seed method: idempotent Pipedrive API seeder using a non-exported user token
- Verified via API: 120 organizations, 120 people, 120 deals
- Verified in UI after refresh: 120 people
- Native MCP is available in the workspace and explicitly states that it can
  query company data and create or update CRM records; Claude OAuth is pending
