#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
STATE_DIR = REPO_ROOT / 'state'


def resolve_path(env_key: str, default_rel: str) -> Path:
    raw = os.getenv(env_key, '').strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return (REPO_ROOT / default_rel).resolve()


CRON_STATE = resolve_path('CRON_ALERT_ROUTER_STATE_PATH', 'state/cron-alert-router-state.json')
CLAW_STATE = resolve_path('CLAWMETRY_MONITOR_STATE_PATH', 'state/clawmetry-monitor-state.json')


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def get_error_jobs() -> list[str]:
    try:
        proc = subprocess.run(
            ['openclaw', 'cron', 'list', '--json'],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        if proc.returncode != 0:
            return []
        data = json.loads(proc.stdout)
        jobs = data.get('jobs', []) if isinstance(data, dict) else []
        bad = []
        for j in jobs:
            if not isinstance(j, dict):
                continue
            name = j.get('name', '')
            if 'Alert Digest' in name:
                continue
            st = j.get('state', {}) or {}
            if st.get('lastStatus') == 'error' or int(st.get('consecutiveErrors', 0) or 0) >= 1:
                bad.append(name or j.get('id', 'unknown'))
        return bad
    except Exception:
        return []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--hours', type=int, default=12)
    args = ap.parse_args()

    now = datetime.now(KST)
    cutoff = now - timedelta(hours=args.hours)

    cron_state = load_json(CRON_STATE)
    claw_state = load_json(CLAW_STATE)

    sent = cron_state.get('sent', {}) if isinstance(cron_state.get('sent', {}), dict) else {}
    cron_recent = 0
    for _sig, ms in sent.items():
        try:
            dt = datetime.fromtimestamp(float(ms) / 1000.0, tz=KST)
            if dt >= cutoff:
                cron_recent += 1
        except Exception:
            continue

    last_alert = claw_state.get('last_alert_at', {}) if isinstance(claw_state.get('last_alert_at', {}), dict) else {}
    claw_recent = 0
    for _sig, sec in last_alert.items():
        try:
            dt = datetime.fromtimestamp(float(sec), tz=KST)
            if dt >= cutoff:
                claw_recent += 1
        except Exception:
            continue

    active_router = len(cron_state.get('active', {}) or {})
    active_claw = 1 if claw_state.get('incident_active') else 0
    error_jobs = get_error_jobs()

    has_anomaly = (cron_recent + claw_recent) > 0 or (active_router + active_claw) > 0 or len(error_jobs) > 0
    if not has_anomaly:
        print('')
        return

    top_jobs = ', '.join(error_jobs[:3]) if error_jobs else '-'
    msg = '\n'.join([
        f"🟡 AlertBot digest (last {args.hours}h)",
        f"events: router {cron_recent} / clawmetry {claw_recent}",
        f"active incidents: router {active_router} / clawmetry {active_claw}",
        f"error jobs: {top_jobs}",
    ])
    print(msg)


if __name__ == '__main__':
    main()
