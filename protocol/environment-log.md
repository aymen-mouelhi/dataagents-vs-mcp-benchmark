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
- Seeding pending a new restricted sandbox credential or Stripe MCP OAuth grant

## 2026-09-14 - Support source

- Provider: GitHub Issues
- Repository: `aymen-mouelhi/northstar-labs-support-fixture`
- Visibility: public
- Canonical open issues: 40
- Incident/control split: 30 bulk-export incident tickets, 10 configuration controls
- Canonical identifiers and source timestamps are embedded in every issue body
- Nineteen duplicate issues caused by an interrupted first seeding pass were
  closed immediately and are excluded by the frozen `state=open` source filter

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
- Workspace was verified empty; deterministic CRM seeding is pending an API
  credential or MCP write authorization
