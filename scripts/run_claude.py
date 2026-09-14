#!/usr/bin/env python3
"""Run one frozen task in Claude Code and preserve raw JSON telemetry."""
import argparse
import json
import os
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def load_task(task_id):
    tasks = yaml.safe_load((ROOT / "protocol" / "tasks.yaml").read_text())["tasks"]
    return next((task for task in tasks if task["id"] == task_id), None)


def runner_environment():
    """Resolve the existing GitHub CLI credential without persisting it."""
    env = os.environ.copy()
    if not env.get("GITHUB_TOKEN") and shutil.which("gh"):
        try:
            env["GITHUB_TOKEN"] = subprocess.check_output(
                ["gh", "auth", "token"], text=True, stderr=subprocess.DEVNULL
            ).strip()
        except subprocess.CalledProcessError:
            pass
    if not env.get("GITHUB_TOKEN"):
        raise SystemExit("GITHUB_TOKEN is required (or authenticate the GitHub CLI with `gh auth login`)")
    return env


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id")
    parser.add_argument("--model", required=True, help="Exact model ID; aliases are forbidden for scored runs")
    parser.add_argument("--temperature", choices=("cold", "warm"), required=True)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    task = load_task(args.task_id)
    if not task or not task.get("prompt"):
        raise SystemExit(f"Task {args.task_id!r} is missing or is not interactive")

    run_id = str(uuid.uuid4())
    out_dir = ROOT / "runs" / "raw" / "cc_raw" / args.task_id
    out_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "claude", "-p", task["prompt"], "--model", args.model,
        "--mcp-config", str(ROOT / ".mcp.json"), "--strict-mcp-config",
        "--output-format", "stream-json", "--verbose",
    ]
    if args.dry_run:
        print(json.dumps({"run_id": run_id, "command": command, "task": task}, indent=2))
        return

    started_at = utc_now()
    start = time.monotonic_ns()
    status, error = "ok", None
    try:
        completed = subprocess.run(
            command, cwd=ROOT, text=True, capture_output=True,
            timeout=args.timeout, env=runner_environment(),
        )
        if completed.returncode:
            status, error = "error", completed.stderr[-4000:]
    except subprocess.TimeoutExpired as exc:
        completed, status, error = exc, "timeout", "timeout"
    elapsed_ms = (time.monotonic_ns() - start) // 1_000_000
    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    (out_dir / f"{run_id}.jsonl").write_text(stdout, encoding="utf-8")
    (out_dir / f"{run_id}.stderr.txt").write_text(stderr, encoding="utf-8")
    summary = {
        "run_id": run_id, "system_id": "cc_raw", "task_id": args.task_id,
        "session_temperature": args.temperature, "started_at": started_at,
        "finished_at": utc_now(), "status": status, "model": args.model,
        "wall_clock_ms": elapsed_ms, "raw_event_file": f"{run_id}.jsonl", "error": error,
    }
    (out_dir / f"{run_id}.summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
