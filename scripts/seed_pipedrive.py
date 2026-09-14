#!/usr/bin/env python3
"""Idempotently seed Pipedrive organizations, people, and deals."""
import csv
import json
import os
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "generated"


def read_csv(name):
    with (DATA / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


class Client:
    def __init__(self, domain, token):
        self.base = f"https://{domain}.pipedrive.com/api/v1"
        self.headers = {"x-api-token": token}

    def request(self, method, path, **kwargs):
        extra_params = kwargs.pop("params", {})
        response = requests.request(method, self.base + path,
                                    params=extra_params, headers=self.headers,
                                    timeout=30, **kwargs)
        response.raise_for_status()
        payload = response.json()
        if not payload.get("success"):
            raise RuntimeError(payload)
        time.sleep(0.06)
        return payload.get("data")

    def exact_search(self, item_type, term, field):
        data = self.request("GET", "/itemSearch", params={"term": term,
                            "item_types": item_type, "fields": field,
                            "exact_match": "true", "limit": 10})
        return data.get("items", []) if data else []


def main():
    token = os.environ.get("PIPEDRIVE_API_TOKEN")
    domain = os.environ.get("PIPEDRIVE_COMPANY_DOMAIN")
    if not token or not domain:
        raise SystemExit("PIPEDRIVE_API_TOKEN and PIPEDRIVE_COMPANY_DOMAIN are required")
    client = Client(domain, token)
    accounts = read_csv("accounts.csv")
    contacts = {row["account_id"]: row for row in read_csv("contacts.csv")}
    deals = {row["account_id"]: row for row in read_csv("deals.csv")}
    mapping = []

    for account in accounts:
        account_id = account["account_id"]
        org_name = account["company_name"]
        org_hits = client.exact_search("organization", org_name, "name")
        if org_hits:
            org_id = org_hits[0]["item"]["id"]
        else:
            org = client.request("POST", "/organizations", json={
                "name": org_name,
                "visible_to": 3,
            })
            org_id = org["id"]

        contact = contacts[account_id]
        person_hits = client.exact_search("person", contact["email"], "email")
        if person_hits:
            person_id = person_hits[0]["item"]["id"]
        else:
            person = client.request("POST", "/persons", json={
                "name": f"{contact['first_name']} {contact['last_name']}",
                "email": [{"value": contact["email"], "primary": True, "label": "work"}],
                "org_id": org_id,
                "visible_to": 3,
            })
            person_id = person["id"]

        deal_fixture = deals[account_id]
        deal_title = f"Northstar subscription - {account_id}"
        deal_hits = client.exact_search("deal", deal_title, "title")
        if deal_hits:
            deal_id = deal_hits[0]["item"]["id"]
        else:
            deal = client.request("POST", "/deals", json={
                "title": deal_title,
                "value": int(deal_fixture["amount_cents"]) / 100,
                "currency": "EUR",
                "org_id": org_id,
                "person_id": person_id,
                "status": "won",
                "visible_to": 3,
            })
            deal_id = deal["id"]
        mapping.append({"account_id": account_id, "organization_id": org_id,
                        "person_id": person_id, "deal_id": deal_id})

    out = ROOT / "artifacts" / "private"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pipedrive_seed_map.json").write_text(json.dumps(mapping, indent=2) + "\n")
    print(json.dumps({"organizations": len(mapping), "people": len(mapping), "deals": len(mapping)}))


if __name__ == "__main__":
    main()
