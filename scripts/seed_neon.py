#!/usr/bin/env python3
import csv
import json
import os
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "generated"


def read_csv(name):
    with (DATA / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    database_url = os.environ.get("BENCHMARK_DATABASE_URL")
    if not database_url:
        raise SystemExit("BENCHMARK_DATABASE_URL is required")
    accounts = read_csv("accounts.csv")
    events = read_csv("product_events.csv")
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute((ROOT / "sql" / "neon_schema.sql").read_text(encoding="utf-8"))
            cur.executemany(
                """INSERT INTO benchmark.accounts
                (account_id, company_name, segment, country_code, crm_company_id, billing_customer_id, created_at)
                VALUES (%(account_id)s, %(company_name)s, %(segment)s, %(country_code)s, %(crm_company_id)s,
                        %(billing_customer_id)s, %(created_at)s)
                ON CONFLICT (account_id) DO UPDATE SET
                  company_name=EXCLUDED.company_name, segment=EXCLUDED.segment,
                  country_code=EXCLUDED.country_code, crm_company_id=EXCLUDED.crm_company_id,
                  billing_customer_id=EXCLUDED.billing_customer_id, created_at=EXCLUDED.created_at""",
                accounts,
            )
            cur.executemany(
                """INSERT INTO benchmark.identity_map
                (account_id, normalized_domain, crm_company_id, billing_customer_id)
                VALUES (%(account_id)s, %(normalized_domain)s, %(crm_company_id)s, %(billing_customer_id)s)
                ON CONFLICT (account_id) DO UPDATE SET
                  normalized_domain=EXCLUDED.normalized_domain,
                  crm_company_id=EXCLUDED.crm_company_id,
                  billing_customer_id=EXCLUDED.billing_customer_id""",
                [{**a, "normalized_domain": f"customer-{int(a['account_id'].split('_')[1])}.example"} for a in accounts],
            )
            cur.executemany(
                """INSERT INTO benchmark.product_events
                (event_id, account_id, event_name, feature, occurred_at, received_at, properties)
                VALUES (%(event_id)s, %(account_id)s, %(event_name)s, %(feature)s,
                        %(occurred_at)s, %(received_at)s, %(properties)s::jsonb)
                ON CONFLICT (event_id) DO UPDATE SET
                  account_id=EXCLUDED.account_id, event_name=EXCLUDED.event_name,
                  feature=EXCLUDED.feature, occurred_at=EXCLUDED.occurred_at,
                  received_at=EXCLUDED.received_at, properties=EXCLUDED.properties""",
                events,
            )
        conn.commit()
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM benchmark.accounts")
            account_count = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM benchmark.product_events")
            event_count = cur.fetchone()[0]
    print(json.dumps({"accounts": account_count, "product_events": event_count}))


if __name__ == "__main__":
    main()
