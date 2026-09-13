#!/usr/bin/env python3
"""Seed a HubSpot developer/test account using private-app credentials."""
import csv
import json
import os
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "generated"
BASE_URL = "https://api.hubapi.com"


def read_csv(name):
    with (DATA / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def post(path, token, payload):
    response = requests.post(BASE_URL + path, headers={"Authorization": f"Bearer {token}"}, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def main():
    token = os.environ.get("HUBSPOT_ACCESS_TOKEN")
    if not token:
        raise SystemExit("HUBSPOT_ACCESS_TOKEN is required")
    companies = []
    for account in read_csv("accounts.csv"):
        obj = post("/crm/v3/objects/companies", token, {"properties": {
            "name": account["company_name"],
            "domain": f"customer-{int(account['account_id'].split('_')[1])}.example",
            "description": f"benchmark_account_id={account['account_id']}; fixture_version=0.1.0",
        }})
        companies.append({"account_id": account["account_id"], "hubspot_company_id": obj["id"]})
        time.sleep(0.11)
    out = ROOT / "artifacts" / "private"
    out.mkdir(parents=True, exist_ok=True)
    (out / "hubspot_seed_map.json").write_text(json.dumps(companies, indent=2) + "\n")
    print(json.dumps({"companies": len(companies)}))


if __name__ == "__main__":
    main()
