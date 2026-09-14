# Benchmark provisioning run — 2026-09-14

## Metadata

- Tester: Codex, supervised by benchmark sponsor
- Scope: reference data-estate provisioning and evidence checks
- Browser: Codex in-app browser
- Workspace: `dataagents-vs-mcp-benchmark`
- Decision: in progress

## Authorized mutations

- Create benchmark-only cloud accounts and test workspaces.
- Seed deterministic benchmark fixtures into those workspaces.
- Create the public GitHub support fixture repository and its issues.
- No live Stripe payments, email campaigns, invitations, or production-data edits.

## Results

### Neon PostgreSQL — passed

- Project: `dataagents-mcp-benchmark`
- Project ID: `solitary-credit-82809008`
- Region: AWS Europe Central 1 (Frankfurt)
- Branch/database: `production` / `neondb`
- Verified rows: 120 accounts, 120 identity mappings, 42,000 product events
- Provider-reported bootstrap query time: 43 ms

### GitHub Issues support fixture — passed

- Public source: `aymen-mouelhi/northstar-labs-support-fixture`
- Canonical open corpus: 40 issues (30 incidents, 10 controls)
- Cleanup: 19 duplicates from an interrupted seed attempt were closed and are excluded by the frozen `state=open` filter.

### Stripe sandbox — passed

- Existing test account: `Revydo sandbox` (`acct_1UBaBvDhuRdfwuUP`)
- Created a benchmark-only restricted test credential with write access limited
  to Customers, Products, Prices, Subscriptions, and Invoices.
- The seeder rejected live keys by construction and created no live-mode objects.
- Verified through the authoritative list API: 3 products, 3 prices, 120
  customers, 117 subscriptions, and 240 paid historical invoices.
- Stripe search indexing exposed 237 and then 238 invoices immediately after the
  seed while the authoritative list endpoint already returned all 240. This is
  recorded as provider search-readiness lag, not fixture loss.
- An idempotency defect discovered during the first pass was fixed: the seeder
  now retrieves thin search results, resumes draft invoices, and pays only when
  invoice status is not already `paid`.

### CRM — passed

- HubSpot developer environment creation requires physical passkey/2FA interaction.
- Pipedrive trial registration was submitted for the sponsor's work email.
- Pipedrive recognizes the address at login, but Google login returns to the login page and no activation/reset email is visible in the work mailbox, including spam/all-mail search.
- The sponsor explicitly authorized using their personal Google identity after the
  work-email authentication block.
- Created workspace: `Northstar Labs Benchmark`.
- Company domain: `northstarlabsbenchmark`.
- Verified that the workspace contains no sample deals.
- Seeded through the idempotent API harness without exposing or committing the token.
- Verified through the API: 120 organizations, 120 people, and 120 deals.
- Verified through the refreshed Pipedrive UI: 120 people.
- Pipedrive native MCP is available in workspace settings; Claude authorization
  remains intentionally separate from fixture seeding.

## Defects

None filed. The CRM result is an external authentication/provisioning block, not a DataAgents product regression.

## Cleanup and side effects

- Closed 19 duplicate GitHub fixture issues.
- Created 120 Stripe sandbox customers, 117 trialing subscriptions, 3 products,
  3 prices, and 240 paid-out-of-band historical invoices.
- No live payment, invitation, external send, or production mutation occurred.

## Console/network evidence

- No relevant browser console errors were captured.
- Pipedrive work-account OAuth returned to the login route without a visible error.
- Pipedrive personal-account OAuth and account creation completed successfully in
  the sponsor's normal Chrome profile.
- One non-blocking Pipedrive console warning was observed:
  `tracking-utilities: Sesheta is not a proper object`.
- The contact-list UI initially displayed a stale zero count immediately after
  API seeding, then displayed 120 after a page refresh. The direct API already
  reported all three 120-record collections during the stale UI interval.
- Stripe API search indexing lagged the list API immediately after seeding; no
  browser console failure was observed during key creation.

## Performance telemetry

No scored agent conversations ran during this provisioning pass.
