#!/usr/bin/env python3
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dataset" / "generated"


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
    manifest = json.loads((OUT / "manifest.sha256.json").read_text())
    for name, expected in manifest.items():
        actual = hashlib.sha256((OUT / name).read_bytes()).hexdigest()
        assert actual == expected, f"hash mismatch for {name}"
    print(f"validated {len(accounts)} accounts, {len(events)} events, cross-source incidents, and {len(manifest)} hashes")


if __name__ == "__main__":
    main()
