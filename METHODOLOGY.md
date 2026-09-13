# Methodology

## Research question

For a small SaaS business whose operational data changes continuously across four systems, how do DataAgents and Claude Code with source-native MCP access compare on answer quality, traceability, speed, token consumption, total cost, freshness, setup effort, and autonomous incident detection?

## Tested systems

- **DA**: DataAgents with managed connectors, continuous sync, transformations, semantic mapping, monitoring, and investigation.
- **CC-RAW**: Claude Code with direct, read-only MCP access to each source. No precomputed joins or derived business tables.
- **CC-WH**: Optional engineering control: Claude Code querying a documented, transformed warehouse maintained by deterministic jobs. Its build and maintenance effort are charged to this configuration.

Where the underlying model differs, conclusions are end-to-end. An architecture-only comparison is reported only if the same model and prompt can be used on both sides.

## Workload

The canonical fictional company, Northstar Labs, sells three subscription plans. Customer, billing, product-usage, and support facts are distributed across four sources. Entity identifiers intentionally differ between systems and must be reconciled through stable keys such as normalized email and explicit mapping records.

Scenarios include:

- single-source reporting;
- cross-source joins;
- root-cause investigations;
- corrections and late-arriving records;
- schema evolution;
- unprompted anomaly detection.

## Experimental phases

### 1. Onboarding

Record elapsed time and active human minutes for account creation, connector authorization, schema discovery, mapping, transformation, monitoring configuration, and validation.

### 2. Baseline synchronization

Seed identical source state, wait for each system's documented ready condition, and verify row counts plus source hashes. Measure initial synchronization latency and transformation readiness.

### 3. Interactive investigations

Run frozen prompts in randomized order. Execute each prompt ten times per system: five cold-session and five warm-session runs. Alternate system order to reduce time-of-day effects.

### 4. Continuous-change experiment

Replay the public event timeline. Events include new records, updates, deletions where supported, late events, and corrections. Query at fixed offsets after each injection to estimate freshness.

### 5. Autonomous monitoring

Inject incidents without sending an investigative prompt. DataAgents uses its native monitoring. CC-RAW uses a disclosed scheduled Claude Code invocation with the same allowed source access. Measure time from source commit to actionable alert.

## Primary outcomes

1. Correct actionable conclusion rate.
2. Median end-to-end latency among valid runs.
3. Total marginal cost per valid investigation.
4. Autonomous incident detection recall within the declared service window.

## Secondary outcomes

- numerical accuracy;
- evidence precision and recall;
- source traceability;
- input/output/cache tokens;
- agent turns and MCP calls;
- source API requests, rows, and bytes returned;
- initial and steady-state freshness;
- false positive rate;
- setup and maintenance effort.

## Cost accounting

Report both marginal and fully loaded cost. Fully loaded cost includes model usage, DataAgents subscription allocation, sync/compute/storage, MCP hosting, scheduled-run usage, and human engineering time. One-time setup is shown separately and amortized over 10, 100, 500, and 2,000 monthly investigations.

## Validity protections

- Freeze protocol before scored runs.
- Pin model IDs, Claude Code version, MCP server versions, source schemas, and prices.
- Equal read-only source permissions.
- No hidden prompts or unpublished helper tools.
- Preserve timeouts, errors, retries, and excluded runs.
- Blind answer grading against a structured key.
- Publish raw evidence with secrets and test-account identifiers redacted.
- Report confidence intervals and full distributions, not only averages.
