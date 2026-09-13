# DataAgents vs Claude Code + MCP Benchmark

An open, preregistered benchmark for measuring the operational value of a continuously synced and transformed data layer against direct, agent-driven access to source systems through MCP.

This repository deliberately separates:

1. **Canonical truth** - deterministic business entities and injected incidents.
2. **Source state** - the same entities distributed across Stripe, HubSpot, Neon PostgreSQL, and a support source.
3. **System runs** - DataAgents, Claude Code with raw MCP, and an optional Claude Code + prepared warehouse control.
4. **Evaluation** - correctness, traceability, latency, token use, tool calls, transferred records, setup effort, freshness, and total cost.

The benchmark does not assume DataAgents wins. All tasks, tolerances, exclusions, and scoring rules are frozen before scored runs.

## Quick start

```bash
python3 scripts/generate_dataset.py
python3 scripts/validate_dataset.py
```

To seed Neon:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
export BENCHMARK_DATABASE_URL='postgresql://...'
.venv/bin/python scripts/seed_neon.py
```

Credentials are never committed. Copy `.env.example` to a private `.env` file if desired.

## Current status

- [x] Protocol and fairness rules
- [x] Deterministic canonical dataset generator
- [x] Incident manifest and answer-key structure
- [x] Neon schema and idempotent seeder
- [x] Event injection design
- [x] Unified run telemetry schema
- [x] Neon project provisioned in Frankfurt and seeded (project `solitary-credit-82809008`)
- [ ] HubSpot developer/test account
- [ ] Stripe test-mode account
- [ ] Support-system selection and account
- [ ] DataAgents adapter
- [ ] Claude Code MCP configuration and runner
- [ ] Pilot runs and protocol freeze
- [ ] Scored runs and report

See [METHODOLOGY.md](METHODOLOGY.md) and [protocol/preregistration.yaml](protocol/preregistration.yaml).

## Provisioned reference environment

The first reference Neon environment uses PostgreSQL 18 in AWS Europe Central 1
(Frankfurt). Its production branch contains 120 accounts, 120 identity mappings,
and 42,000 product events. Credentials remain private and are not committed.
