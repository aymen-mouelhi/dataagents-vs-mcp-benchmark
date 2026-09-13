#!/usr/bin/env python3
"""Seed Stripe test mode from canonical fixtures.

The script refuses live keys and writes the created Stripe IDs to a private run
artifact. Canonical benchmark IDs are stored as Stripe metadata so exports can
be reconciled without relying on provider-generated identifiers.
"""
import csv
import json
import os
from pathlib import Path

import stripe

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "generated"


def read_csv(name):
    with (DATA / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    key = os.environ.get("STRIPE_SECRET_KEY", "")
    if not key.startswith(("sk_test_", "rk_test_")):
        raise SystemExit("STRIPE_SECRET_KEY must be a Stripe test-mode key")
    stripe.api_key = key
    accounts = {r["account_id"]: r for r in read_csv("accounts.csv")}
    contacts = {r["account_id"]: r for r in read_csv("contacts.csv")}
    created = []
    for sub in read_csv("subscriptions.csv"):
        account = accounts[sub["account_id"]]
        contact = contacts[sub["account_id"]]
        customer = stripe.Customer.create(
            name=account["company_name"],
            email=contact["email"],
            metadata={"benchmark_account_id": sub["account_id"], "fixture_version": "0.1.0"},
        )
        product = stripe.Product.create(
            name=f"Northstar {sub['plan'].title()}",
            metadata={"benchmark_plan": sub["plan"], "fixture_version": "0.1.0"},
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(sub["mrr_cents"]),
            currency="eur",
            recurring={"interval": "month"},
        )
        created.append({"account_id": sub["account_id"], "customer_id": customer.id,
                        "product_id": product.id, "price_id": price.id})
    out = ROOT / "artifacts" / "private"
    out.mkdir(parents=True, exist_ok=True)
    (out / "stripe_seed_map.json").write_text(json.dumps(created, indent=2) + "\n")
    print(json.dumps({"customers": len(created), "mode": "test"}))


if __name__ == "__main__":
    main()
