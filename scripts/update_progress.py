#!/usr/bin/env python3
"""Refresh dashboard data from the manual learning journal and two public repos.

This script never scrapes TryHackMe. The journal's data/progress.json remains
the source of truth for paths, rooms, and daily learning records.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JOURNAL_DATA_URL = (
    "https://raw.githubusercontent.com/"
    "JayeshChabukswar/cybersecurity.path/main/data/progress.json"
)
TRACKED_REPOSITORIES = (
    "JayeshChabukswar/JayeshChabukswar.github.io",
    "JayeshChabukswar/cybersecurity.path",
)
OUTPUT = Path("data/progress.json")
USER_AGENT = "JayeshCybersecurityDashboard/1.0"


def get_json(url: str) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    # Public endpoints work unauthenticated; use GITHUB_TOKEN if available to
    # increase API rate limits without requiring a separately stored secret.
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"GET failed for {url}: {exc}") from exc


def collect_recent_commits() -> list[dict[str, str]]:
    commits: list[dict[str, str]] = []
    for repository in TRACKED_REPOSITORIES:
        url = f"https://api.github.com/repos/{repository}/commits?per_page=100"
        response = get_json(url)
        if not isinstance(response, list):
            raise RuntimeError(f"Unexpected commits response for {repository}")
        for item in response:
            commit = item.get("commit") or {}
            author = commit.get("author") or {}
            message = (commit.get("message") or "").splitlines()[0].strip()
            # Ignore this workflow's own data-only commit, otherwise each run
            # would observe yesterday's commit and manufacture a new change.
            if message == "Refresh cybersecurity dashboard data":
                continue
            commits.append({
                "repository": repository,
                "sha": (item.get("sha") or "")[:7],
                "message": message,
                "date": author.get("date") or "",
                "url": item.get("html_url") or "",
            })
    # Stable ordering and de-duplication make repeated runs deterministic.
    unique: dict[tuple[str, str], dict[str, str]] = {}
    for item in commits:
        unique[(item["repository"], item["sha"])] = item
    return sorted(
        unique.values(),
        key=lambda item: (item["date"], item["repository"], item["sha"]),
        reverse=True,
    )[:10]


def main() -> int:
    try:
        source = get_json(JOURNAL_DATA_URL)
        if not isinstance(source, dict):
            raise RuntimeError("Journal progress file must contain a JSON object.")
        # Validate expected sections before using the source as the dashboard base.
        for key in ("profile", "tryhackme", "learning_log"):
            if key not in source:
                raise RuntimeError(f"Journal progress file is missing '{key}'.")
        if not isinstance(source.get("tryhackme", {}).get("paths"), list):
            raise RuntimeError("tryhackme.paths must be a list.")
        if not isinstance(source.get("learning_log"), list):
            raise RuntimeError("learning_log must be a list.")

        data = dict(source)
        activity = dict(data.get("github_activity") or {})
        activity["tracking_mode"] = "selected_repositories"
        activity["repositories"] = list(TRACKED_REPOSITORIES)
        activity["latest_commits"] = collect_recent_commits()
        data["github_activity"] = activity

        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else None
        if current == serialized:
            print("Dashboard data is already current; no file change needed.")
            return 0
        OUTPUT.write_text(serialized, encoding="utf-8")
        print(f"Updated {OUTPUT}; {len(activity['latest_commits'])} recent commits tracked.")
        return 0
    except Exception as exc:  # fail loudly so Actions marks the run as failed
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
