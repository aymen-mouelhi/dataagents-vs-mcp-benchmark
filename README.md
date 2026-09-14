# DataAgents vs Claude Code + MCP Benchmark

An open, preregistered benchmark for measuring the operational value of a continuously synced and transformed data layer against direct, agent-driven access to source systems through MCP.

This repository deliberately separates:

1. **Canonical truth** - deterministic business entities and injected incidents.
2. **Source state** - the same entities distributed across Stripe, Pipedrive, Neon PostgreSQL, and a support source.
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

Claude Code source MCP endpoints are declared in `.mcp.json`. Each scored run
uses `--strict-mcp-config`, an exact model ID, verbose stream-JSON output, and a
fresh immutable run ID. Test the harness without contacting a model:

```bash
.venv/bin/python scripts/run_claude.py S01 --model EXACT_MODEL_ID --temperature cold --dry-run
```

## Current status

- [x] Protocol and fairness rules
- [x] Deterministic canonical dataset generator
- [x] Incident manifest and answer-key structure
- [x] Neon schema and idempotent seeder
- [x] Event injection design
- [x] Unified run telemetry schema
- [x] Neon project provisioned in Frankfurt and seeded (project `solitary-credit-82809008`)
- [x] Pipedrive trial seeded and verified (120 organizations, people, and deals)
- [ ] Stripe test-mode account
- [x] Support source selected: public GitHub Issues fixture
- [ ] DataAgents adapter
- [x] Claude Code MCP configuration and raw-event runner
- [ ] Pilot runs and protocol freeze
- [ ] Scored runs and report

See [METHODOLOGY.md](METHODOLOGY.md) and [protocol/preregistration.yaml](protocol/preregistration.yaml).

## Provisioned reference environment

The first reference Neon environment uses PostgreSQL 18 in AWS Europe Central 1
(Frankfurt). Its production branch contains 120 accounts, 120 identity mappings,
and 42,000 product events. Credentials remain private and are not committed.

The support fixture is publicly inspectable at
[`aymen-mouelhi/northstar-labs-support-fixture`](https://github.com/aymen-mouelhi/northstar-labs-support-fixture).
Only open issues belong to the scored corpus.
