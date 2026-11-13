#!/usr/bin/env python3
"""Report the Claude Code 5-hour / weekly rate-limit remaining from the statusline record.

Claude Code passes account-level rate limits only to the statusline script.
`~/.claude/statusline-rate-limits.py` saves the newest values to
`~/.claude/rate-limits.json`; this reads that file. Same interface as
`codex_rate_limit.py`.

Usage:
  python3 claude_rate_limit.py            # human-readable
  python3 claude_rate_limit.py --json     # machine-readable
  python3 claude_rate_limit.py --guard 15 # exit 0 if 5h remaining > 15%, 3 if <= 15%, 2 if unknown

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


def window(w: dict | None, now: float) -> dict | None:
    if not w or w.get("used_percentage") is None:
        return None
    used = float(w["used_percentage"])
    resets_at = w.get("resets_at")
    expired = resets_at is not None and resets_at <= now
    return {
        "used_percent": used,
        "remaining_percent": 100.0 if expired else round(100.0 - used, 1),
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

    path = Path(os.environ.get("CLAUDE_RATE_LIMITS_FILE", Path.home() / ".claude" / "rate-limits.json"))
    now = time.time()
    try:
        rec = json.loads(path.read_text())
    except (OSError, ValueError):
        rec = None

    if not rec or not (rec.get("rate_limits") or {}).get("five_hour"):
        result = {"status": "unknown", "reason": f"no rate_limits record in {path}"}
    else:
        rl = rec["rate_limits"]
        age_min = (now - float(rec["recorded_at"])) / 60
        five = window(rl.get("five_hour"), now)
        result = {
            "status": "ok",
            "recorded_at_jst": datetime.fromtimestamp(rec["recorded_at"], JST).strftime("%Y-%m-%d %H:%M:%S"),
            "record_age_min": round(age_min, 1),
            "five_hour": five,
            "weekly": window(rl.get("seven_day"), now),
        }
        if five is None:
            result["status"] = "unknown"
            result["reason"] = "five_hour used_percentage missing"
        elif age_min > args.max_age_min and not five["reset_passed_since_record"]:
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
