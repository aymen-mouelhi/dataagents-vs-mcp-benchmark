#!/usr/bin/env python3
"""Seed ordinary Stripe sandbox objects from canonical fixtures.

The script refuses live keys and writes the created Stripe IDs to a private run
artifact. Canonical benchmark IDs are stored as Stripe metadata so exports can
be reconciled without relying on provider-generated identifiers.

Test clocks are intentionally not used: Stripe limits each clock to three
customers and omits clock-generated invoices from unscoped list operations,
which would make MCP discovery artificially difficult.
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


def first_search(resource, query):
    result = resource.search(query=query, limit=1)
    return result.data[0] if result.data else None


def main():
    key = os.environ.get("STRIPE_SECRET_KEY", "")
    if not key.startswith(("sk_test_", "rk_test_")):
        raise SystemExit("STRIPE_SECRET_KEY must be a Stripe test-mode key")
    stripe.api_key = key
    accounts = {r["account_id"]: r for r in read_csv("accounts.csv")}
    contacts = {r["account_id"]: r for r in read_csv("contacts.csv")}
    subscriptions = {r["account_id"]: r for r in read_csv("subscriptions.csv")}
    invoices = read_csv("invoices.csv")

    prices = {}
    for plan, amount in (("starter", 29900), ("growth", 49900), ("scale", 89900)):
        product = first_search(stripe.Product, f"metadata['benchmark_plan']:'{plan}'")
        if not product:
            product = stripe.Product.create(
                name=f"Northstar {plan.title()}",
                metadata={"benchmark_plan": plan, "fixture_version": "0.1.0"},
            )
        existing_prices = stripe.Price.list(product=product.id, active=True, limit=100)
        price = next((p for p in existing_prices.data if p.unit_amount == amount and p.recurring), None)
        if not price:
            price = stripe.Price.create(
                product=product.id, unit_amount=amount, currency="eur",
                recurring={"interval": "month"},
                metadata={"benchmark_plan": plan, "fixture_version": "0.1.0"},
            )
        prices[plan] = price

    created = []
    for account_id, account in accounts.items():
        contact = contacts[account_id]
        customer = first_search(stripe.Customer, f"metadata['benchmark_account_id']:'{account_id}'")
        if not customer:
            customer = stripe.Customer.create(
                name=account["company_name"], email=contact["email"],
                metadata={"benchmark_account_id": account_id, "benchmark_segment": account["segment"],
                          "fixture_version": "0.1.0"},
            )
        sub = subscriptions.get(account_id)
        stripe_sub = None
        if sub:
            existing = stripe.Subscription.list(customer=customer.id, status="all", limit=10)
            stripe_sub = next((s for s in existing.data if s.metadata.get("benchmark_subscription_id") == sub["subscription_id"]), None)
            if not stripe_sub:
                stripe_sub = stripe.Subscription.create(
                    customer=customer.id,
                    items=[{"price": prices[sub["plan"]].id}],
                    trial_period_days=365,
                    metadata={"benchmark_subscription_id": sub["subscription_id"],
                              "benchmark_account_id": account_id, "fixture_version": "0.1.0"},
                )
        created.append({"account_id": account_id, "customer_id": customer.id,
                        "subscription_id": stripe_sub.id if stripe_sub else None})

    # Historical benchmark periods are represented by ordinary, externally-paid
    # invoices so they remain visible to unscoped list/search operations.
    customer_ids = {r["account_id"]: r["customer_id"] for r in created}
    for fixture in invoices:
        found = stripe.Invoice.search(query=f"metadata['benchmark_invoice_id']:'{fixture['invoice_id']}'", limit=1)
        if found.data:
            continue
        stripe.InvoiceItem.create(
            customer=customer_ids[fixture["account_id"]],
            amount=int(fixture["amount_paid_cents"]), currency="eur",
            description=f"Northstar subscription - {fixture['period_start'][:7]}",
            metadata={"benchmark_invoice_id": fixture["invoice_id"], "benchmark_account_id": fixture["account_id"]},
        )
        invoice = stripe.Invoice.create(
            customer=customer_ids[fixture["account_id"]], auto_advance=False,
            collection_method="send_invoice", days_until_due=30,
            metadata={"benchmark_invoice_id": fixture["invoice_id"],
                      "benchmark_account_id": fixture["account_id"],
                      "benchmark_period": fixture["period_start"][:7],
                      "benchmark_refunded_cents": fixture["refunded_cents"],
                      "fixture_version": "0.1.0"},
        )
        stripe.Invoice.finalize_invoice(invoice.id)
        stripe.Invoice.pay(invoice.id, paid_out_of_band=True)
    out = ROOT / "artifacts" / "private"
    out.mkdir(parents=True, exist_ok=True)
    (out / "stripe_seed_map.json").write_text(json.dumps(created, indent=2) + "\n")
    print(json.dumps({"customers": len(created), "invoices": len(invoices), "mode": "test"}))


if __name__ == "__main__":
    main()
