# Measurement plan

This plan separates one-time setup, continuous data operations, interactive
analysis, and autonomous monitoring. That separation is essential: query
latency alone would not measure the value claimed for managed syncing and
transformations.

## Compared configurations

| ID | Configuration | Included work |
| --- | --- | --- |
| `da` | DataAgents | Native connectors, managed sync, transformations, semantic mappings, saved monitors, and investigations |
| `cc_raw` | Claude Code + source MCPs | Direct read-only access to Pipedrive, Stripe, Neon, and GitHub; no unpublished joins or cached answers |
| `cc_wh` | Claude Code + prepared warehouse | Optional engineering control; transformation build, scheduler, hosting, and maintenance are charged to this arm |

The headline comparison is `da` versus `cc_raw`. `cc_wh` shows whether any
observed advantage comes from a prepared data layer rather than the agent UI.

## Clocks and boundaries

- **Setup clock:** first connector/configuration action to a validated ready
  state. Record wall time and hands-on human time separately.
- **Freshness clock:** source mutation acknowledgement to the first correct
  transformed answer. Poll on the frozen schedule; do not continuously probe.
- **Investigation clock:** prompt submission to final answer. Also capture first
  useful output and first source/tool call.
- **Monitoring clock:** source mutation acknowledgement to an actionable alert.
- Provider throttling, retries, failures, and manual intervention remain in the
  measured result.

All timestamps use UTC from the runner host. Before a scored block, record clock
offset against an external time source and abort if absolute drift exceeds two
seconds.

## Phase A — setup and baseline readiness

For every source and system, record:

- elapsed setup time and active human minutes;
- authentication and connector steps;
- custom code/configuration lines changed;
- initial records and bytes transferred;
- time to schema discovery, first successful sync, transformation completion,
  and answer-key validation;
- failed attempts and recovery time;
- recurring infrastructure and required subscription tier.

The baseline is ready only when all canonical entity counts and frozen source
hashes reconcile. A visually successful connector is not sufficient.

## Phase B — interactive tasks

Run every frozen task ten times per system: five cold sessions and five warm
sessions. Randomize task order with the preregistered seed and alternate system
order. Preserve the full event stream and score:

- conclusion correctness and numerical accuracy;
- evidence precision/recall and source traceability;
- wall time, first useful output, and first tool-call latency;
- tokens, turns, tool calls, API requests, returned rows, and returned bytes;
- model, infrastructure, and allocated subscription cost;
- intervention, retry, timeout, and refusal rate.

Warm runs may reuse normal product caches and saved transformations, but never a
cached final answer. Cold runs start a fresh conversation and clear only caches
that the product documents as user-controllable.

## Phase C — continuous change

Replay `protocol/mutations.yaml` in order. For each mutation, capture the source
acknowledgement time and probe at 15 seconds, 1 minute, 5 minutes, 15 minutes,
and 60 minutes until the answer is correct. If a system documents a slower sync
cadence, keep the same observations and report that cadence rather than changing
the schedule.

This phase measures assets created by syncing and transformation directly:

- source-to-raw freshness;
- raw-to-transformed freshness;
- cross-source identity resolution accuracy;
- transformation reuse across later questions;
- correction/deletion propagation;
- schema-change recovery time and human intervention;
- query-time source work avoided by prepared data.

## Phase D — autonomous monitoring

Inject the frozen incident without an investigative prompt. DataAgents uses its
native monitor. `cc_raw` uses a disclosed scheduled Claude invocation at the
same nominal cadence. Charge every scheduled run, including runs that find
nothing. Score detection recall, false positives, alert latency, alert quality,
and cost per monitored day.

## Cost equations

For run `r`:

`marginal_cost(r) = model_tokens + source_API + compute + storage + egress`

For a monthly volume `n`:

`fully_loaded(n) = marginal_cost_per_run*n + subscription_allocation + maintenance + setup_cost/n`

Setup cost uses the published loaded hourly rate multiplied by measured active
human hours. Report break-even at 10, 100, 500, and 2,000 investigations per
month and show sensitivity at three labor rates. Never treat a free trial as a
zero long-run platform price.

## Readiness and exclusion rules

- Freeze prompts, answers, tolerances, model IDs, software versions, MCP server
  identities, prices, and source hashes before scored runs.
- Run a small unscored pilot only to repair the harness and ambiguous prompts.
- Exclude a run only for a preregistered infrastructure invalidation; publish it
  with the exclusion reason. Product failures remain scored failures.
- Blind-grade answers against structured keys. Adjudicators receive randomized
  system labels.
- Publish raw redacted telemetry, per-run scores, analysis code, and confidence
  intervals. Report distributions and failures, not just averages.

