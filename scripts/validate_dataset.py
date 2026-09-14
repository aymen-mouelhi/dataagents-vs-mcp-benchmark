#!/usr/bin/env python3
import csv
import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dataset" / "generated"
ANSWERS = ROOT / "protocol" / "answers"


def rows(name):
    with (OUT / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    accounts = rows("accounts.csv")
    events = rows("product_events.csv")
    deals = rows("deals.csv")
    subscriptions = rows("subscriptions.csv")
    invoices = rows("invoices.csv")
    tickets = rows("tickets.csv")
    assert len(accounts) == 120
    assert len({r["account_id"] for r in accounts}) == 120
    account_ids = {r["account_id"] for r in accounts}
    assert all(r["account_id"] in account_ids for r in events)
    assert len(deals) == 120
    assert len(subscriptions) == 117
    assert len(invoices) == 240
    assert len(tickets) == 40
    subscribed = {r["account_id"] for r in subscriptions}
    assert {r["account_id"] for r in deals} - subscribed == {"acct_0017", "acct_0053", "acct_0101"}
    refund_accounts = {r["account_id"] for r in invoices if int(r["refunded_cents"]) > 0}
    assert len(refund_accounts) == 10

    # Recompute frozen answer-key facts from canonical rows so protocol edits
    # cannot silently drift away from the public fixture.
    answer = lambda task_id: json.loads((ANSWERS / f"{task_id}.json").read_text())
    july_revenue = sum(
        int(r["amount_paid_cents"]) - int(r["refunded_cents"])
        for r in invoices if r["period_start"].startswith("2026-07")
    )
    assert answer("S01")["recognized_revenue_cents"] == july_revenue
    august_refunds = sum(
        int(r["refunded_cents"]) for r in invoices
        if r["period_start"].startswith("2026-08") and r["account_id"] in refund_accounts
    )
    assert answer("X01")["august_refunded_cents"] == august_refunds
    assert answer("X01")["affected_accounts"] == len(refund_accounts)
    missing = sorted({r["account_id"] for r in deals} - subscribed)
    missing_deals = [r for r in deals if r["account_id"] in missing]
    assert answer("X02")["account_ids"] == missing
    assert answer("X02")["expected_mrr_cents"] == sum(int(r["expected_mrr_cents"]) for r in missing_deals)

    account_by_id = {r["account_id"]: r for r in accounts}
    baseline_start, baseline_end = date(2026, 7, 29), date(2026, 8, 4)
    incident_start, incident_end = date(2026, 8, 5), date(2026, 8, 14)
    daily = {}
    for event in events:
        day = date.fromisoformat(event["occurred_at"][:10])
        daily[(event["account_id"], day)] = daily.get((event["account_id"], day), 0) + 1
    affected = []
    for account_id in subscribed:
        if account_by_id[account_id]["segment"] != "Enterprise":
            continue
        baseline = sum(daily.get((account_id, date.fromordinal(n)), 0)
                       for n in range(baseline_start.toordinal(), baseline_end.toordinal() + 1)) / 7
        incident = sum(daily.get((account_id, date.fromordinal(n)), 0)
                       for n in range(incident_start.toordinal(), incident_end.toordinal() + 1)) / 10
        if baseline and 1 - incident / baseline >= 0.8:
            affected.append(account_id)
    assert len(affected) == answer("F01")["affected_active_enterprise_customers"] == 10
    assert answer("R01")["affected_accounts"] == len(affected)
    assert answer("A01")["incident_id"] == "incident_usage_collapse"
    manifest = json.loads((OUT / "manifest.sha256.json").read_text())
    for name, expected in manifest.items():
        actual = hashlib.sha256((OUT / name).read_bytes()).hexdigest()
        assert actual == expected, f"hash mismatch for {name}"
    print(f"validated {len(accounts)} accounts, {len(events)} events, answer keys, cross-source incidents, and {len(manifest)} hashes")


if __name__ == "__main__":
    main()
