#!/usr/bin/env python3
"""Report the Codex CLI 5-hour / weekly rate-limit remaining from local rollout logs.

Codex records account-level rate limits in each rollout's `token_count` events
(`payload.rate_limits.primary` = 5-hour window, `secondary` = weekly window).
The agent cannot run `/status`, so this reads the newest record from disk.

Usage:
  python3 codex_rate_limit.py            # human-readable
  python3 codex_rate_limit.py --json     # machine-readable
  python3 codex_rate_limit.py --guard 15 # exit 0 if 5h remaining > 15%, 3 if <= 15%, 2 if unknown

Read-only. Does not print tokens, credentials, or conversation content.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))
TAIL_BYTES = 4 * 1024 * 1024  # rate_limits appear every turn; the tail is enough
MAX_FILES = 8


def newest_rollouts(sessions: Path) -> list[Path]:
    files = [p for p in sessions.rglob("rollout-*.jsonl") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:MAX_FILES]


def latest_record(path: Path) -> tuple[str, dict] | None:
    size = path.stat().st_size
    with path.open("rb") as f:
        if size > TAIL_BYTES:
            f.seek(size - TAIL_BYTES)
            f.readline()  # drop partial line
        best = None
        for raw in f:
            if b'"rate_limits"' not in raw:
                continue
            try:
                d = json.loads(raw)
            except ValueError:
                continue
            p = d.get("payload") or {}
            rl = p.get("rate_limits")
            if p.get("type") == "token_count" and rl and rl.get("primary"):
                ts = d.get("timestamp", "")
                if best is None or ts >= best[0]:
                    best = (ts, rl)
        return best


def window(w: dict | None, now: float) -> dict | None:
    if not w:
        return None
    used = float(w.get("used_percent", 0.0))
    resets_at = w.get("resets_at")
    expired = resets_at is not None and resets_at <= now
    return {
        "used_percent": used,
        "remaining_percent": 100.0 if expired else round(100.0 - used, 1),
        "window_minutes": w.get("window_minutes"),
        "resets_at_jst": datetime.fromtimestamp(resets_at, JST).strftime("%Y-%m-%d %H:%M") if resets_at else None,
        "reset_passed_since_record": expired,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--guard", type=float, metavar="PCT",
                    help="exit 3 if 5h remaining <= PCT, 2 if unknown, else 0")
    ap.add_argument("--max-age-min", type=float, default=30.0,
                    help="treat a record older than this as unknown (default 30)")
    args = ap.parse_args()

    home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    found = None
    for f in newest_rollouts(home / "sessions"):
        rec = latest_record(f)
        if rec and (found is None or rec[0] > found[0]):
            found = rec

    now = time.time()
    if found is None:
        result = {"status": "unknown", "reason": f"no rate_limits record under {home / 'sessions'}"}
    else:
        ts, rl = found
        rec_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        age_min = (now - rec_time.timestamp()) / 60
        five = window(rl.get("primary"), now)
        result = {
            "status": "ok",
            "recorded_at_jst": rec_time.astimezone(JST).strftime("%Y-%m-%d %H:%M:%S"),
            "record_age_min": round(age_min, 1),
            "five_hour": five,
            "weekly": window(rl.get("secondary"), now),
            "rate_limit_reached_type": rl.get("rate_limit_reached_type"),
        }
        if age_min > args.max_age_min and not (five and five["reset_passed_since_record"]):
            result["status"] = "stale"
            result["reason"] = f"newest record is {age_min:.0f} min old (> {args.max_age_min:.0f})"

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    elif result["status"] == "unknown":
        print(f"5h remaining: unknown ({result['reason']})")
    else:
        f5, wk = result["five_hour"], result["weekly"]
        line = f"5h remaining: {f5['remaining_percent']:.0f}% (used {f5['used_percent']:.0f}%, resets {f5['resets_at_jst']} JST)"
        if f5["reset_passed_since_record"]:
            line += " [window already reset]"
        print(line)
        if wk:
            print(f"weekly remaining: {wk['remaining_percent']:.0f}% (resets {wk['resets_at_jst']} JST)")
        print(f"recorded {result['recorded_at_jst']} JST ({result['record_age_min']} min ago), status={result['status']}")

    if args.guard is not None:
        if result["status"] != "ok":
            return 2
        return 3 if result["five_hour"]["remaining_percent"] <= args.guard else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
