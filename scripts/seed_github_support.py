#!/usr/bin/env python3
"""Seed synthetic support tickets as GitHub Issues in a public fixture repo."""
import argparse
import csv
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "generated"


def gh(*args, input_text=None):
    return subprocess.check_output(["gh", *args], input=input_text, text=True).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="aymen-mouelhi/northstar-labs-support-fixture")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    with (DATA / "tickets.csv").open(newline="", encoding="utf-8") as stream:
        tickets = list(csv.DictReader(stream))
    if args.dry_run:
        print(json.dumps({"repo": args.repo, "issues": len(tickets)}, indent=2))
        return

    existing = json.loads(gh("issue", "list", "--repo", args.repo, "--state", "all", "--limit", "100",
                             "--json", "title,number"))
    existing_titles = {issue["title"] for issue in existing}
    created = []
    for ticket in tickets:
        title = f"[{ticket['ticket_id']}] {ticket['subject']}"
        if title in existing_titles:
            continue
        body = "\n".join([
            "Synthetic support fixture for the DataAgents vs MCP benchmark.", "",
            f"- Account: `{ticket['account_id']}`",
            f"- Requester: `{ticket['requester_email']}`",
            f"- Category: `{ticket['category']}`",
            f"- Priority: `{ticket['priority']}`",
            f"- Fixture created at: `{ticket['created_at']}`",
            f"- Canonical ticket ID: `{ticket['ticket_id']}`",
        ])
        url = gh("issue", "create", "--repo", args.repo, "--title", title, "--body", body,
                 "--label", f"priority:{ticket['priority']}", "--label", f"category:{ticket['category']}")
        created.append(url)
    print(json.dumps({"repo": args.repo, "created": len(created), "total_fixture_tickets": len(tickets)}, indent=2))


if __name__ == "__main__":
    main()
