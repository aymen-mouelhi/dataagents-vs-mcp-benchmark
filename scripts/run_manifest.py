#!/usr/bin/env python3
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def version(command):
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"unavailable: {exc}"


manifest = {
    "captured_at": datetime.now(timezone.utc).isoformat(),
    "platform": platform.platform(),
    "python": platform.python_version(),
    "claude_code": version(["claude", "--version"]),
    "git_commit": version(["git", "rev-parse", "HEAD"]),
    "git_status": version(["git", "status", "--porcelain"]),
}
print(json.dumps(manifest, indent=2))
