#!/usr/bin/env python3
import csv
import hashlib
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dataset" / "generated"
SEED = 20260914
BASE = datetime(2026, 7, 1, tzinfo=timezone.utc)


def write_csv(name, rows):
    path = OUT / name
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def main():
    random.seed(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    accounts = []
    events = []
    contacts = []
    deals = []
    subscriptions = []
    invoices = []
    tickets = []
    segments = ["SMB", "Mid-market", "Enterprise"]
    countries = ["FR", "DE", "GB", "US", "ES"]
    for i in range(1, 121):
        account_id = f"acct_{i:04d}"
        segment = segments[(i - 1) % len(segments)]
        accounts.append({
            "account_id": account_id,
            "company_name": f"Northstar Customer {i:04d}",
            "segment": segment,
            "country_code": countries[(i - 1) % len(countries)],
            "crm_company_id": f"hs_{100000 + i}",
            "billing_customer_id": f"cus_bench_{100000 + i}",
            "created_at": (BASE - timedelta(days=120 - i)).isoformat(),
        })
        domain = f"customer-{i}.example"
        contacts.append({
            "contact_id": f"contact_{i:04d}",
            "email": f"finance@{domain}",
            "first_name": "Alex",
            "last_name": f"Customer{i:04d}",
            "crm_company_id": f"hs_{100000 + i}",
            "account_id": account_id,
        })
        plan = {"SMB": "starter", "Mid-market": "growth", "Enterprise": "scale"}[segment]
        mrr = {"SMB": 29900, "Mid-market": 49900, "Enterprise": 89900}[segment]
        deals.append({
            "deal_id": f"deal_{i:04d}",
            "crm_company_id": f"hs_{100000 + i}",
            "account_id": account_id,
            "stage": "closedwon",
            "amount_cents": mrr * 12,
            "expected_mrr_cents": mrr,
            "closed_at": (BASE - timedelta(days=30 - (i % 20))).isoformat(),
        })
        # Three deliberate CRM/billing mismatches for task X02.
        if i not in (17, 53, 101):
            subscriptions.append({
                "subscription_id": f"sub_bench_{100000 + i}",
                "billing_customer_id": f"cus_bench_{100000 + i}",
                "account_id": account_id,
                "plan": plan,
                "status": "active",
                "mrr_cents": mrr,
                "started_at": (BASE - timedelta(days=30 - (i % 20))).isoformat(),
            })
        for month in (7, 8):
            refunded = month == 8 and segment == "Enterprise" and i % 4 == 0
            invoices.append({
                "invoice_id": f"in_bench_{i:04d}_{month:02d}",
                "billing_customer_id": f"cus_bench_{100000 + i}",
                "account_id": account_id,
                "period_start": datetime(2026, month, 1, tzinfo=timezone.utc).isoformat(),
                "amount_paid_cents": mrr,
                "refunded_cents": mrr if refunded else 0,
                "status": "paid",
            })
        ticket_count = 3 if i % 12 == 0 else (1 if i % 12 == 1 else 0)
        for ticket_no in range(ticket_count):
            tickets.append({
                "ticket_id": f"ticket_{i:04d}_{ticket_no:02d}",
                "requester_email": f"finance@{domain}",
                "account_id": account_id,
                "subject": "Bulk export fails" if i % 12 == 0 else "How to configure alerts",
                "category": "bulk_export" if i % 12 == 0 else "configuration",
                "priority": "high" if i % 12 == 0 else "normal",
                "status": "open" if ticket_no % 2 == 0 else "solved",
                "created_at": (BASE + timedelta(days=34 + ticket_no, hours=i % 12)).isoformat(),
            })
        daily_events = {"SMB": 3, "Mid-market": 7, "Enterprise": 14}[segment]
        for day in range(45):
            count = daily_events
            # Incident window: stable billing population but Enterprise usage collapse.
            if segment == "Enterprise" and day >= 35 and i % 4 == 0:
                count = max(1, daily_events // 7)
            for n in range(count):
                occurred = BASE + timedelta(days=day, hours=(i + n) % 24, minutes=(i * n) % 60)
                received = occurred + timedelta(minutes=(i + n) % 9)
                events.append({
                    "event_id": f"evt_{i:04d}_{day:02d}_{n:02d}",
                    "account_id": account_id,
                    "event_name": "session_started" if n % 3 == 0 else "feature_used",
                    "feature": "bulk_export" if i % 4 == 0 else ["dashboard", "alerts", "reports"][n % 3],
                    "occurred_at": occurred.isoformat(),
                    "received_at": received.isoformat(),
                    "properties": json.dumps({"user_id": f"usr_{i:04d}_{n % 6:02d}"}, separators=(",", ":")),
                })
    files = [
        write_csv("accounts.csv", accounts),
        write_csv("contacts.csv", contacts),
        write_csv("deals.csv", deals),
        write_csv("subscriptions.csv", subscriptions),
        write_csv("invoices.csv", invoices),
        write_csv("tickets.csv", tickets),
        write_csv("product_events.csv", events),
    ]
    incidents = {
        "dataset_version": "0.1.0",
        "seed": SEED,
        "incidents": [{
            "id": "incident_usage_collapse",
            "starts_at": (BASE + timedelta(days=35)).isoformat(),
            "affected_segment": "Enterprise",
            "affected_condition": "account ordinal divisible by 4",
            "expected_root_cause": "bulk_export cohort product usage collapse",
        }],
    }
    incident_path = OUT / "incidents.json"
    incident_path.write_text(json.dumps(incidents, indent=2) + "\n", encoding="utf-8")
    files.append(incident_path)
    manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (OUT / "manifest.sha256.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"generated {len(accounts)} accounts, {len(events)} product events, and cross-source fixtures in {OUT}")


if __name__ == "__main__":
    main()
